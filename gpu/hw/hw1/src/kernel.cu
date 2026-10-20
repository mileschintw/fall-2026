// HW1 - SAXPY, 2D & 3D matrix addition (Au26 GPU Computing)
// Starts from the default VS "CUDA Runtime" template (addKernel / addWithCuda),
// with every cudaError_t call wrapped in checkCuda (cuda_check.h).
//
// Usage:
//   hw1                      run everything except the 1e9-point 3D case
//   hw1 all --big            also run the 3D 1000x1000x1000 case (Release build, ~12 GB host RAM)
//   hw1 addvec | printf | saxpy | mat2d | grid3d [--big]
//   hw1 printf <grid> <block> [reps]     one printf exec cfg, e.g. hw1 printf 4 8 10

#include "cuda_runtime.h"
#include "device_launch_parameters.h"
#include "cuda_check.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

cudaError_t addWithCuda(int* c, const int* a, const int* b, unsigned int size);

static unsigned int ceilDiv(size_t n, unsigned int d) { return (unsigned int)((n + d - 1) / d); }

// ---------------------------------------------------------------- kernels

__global__ void addKernel(int* c, const int* a, const int* b)
{
    int i = threadIdx.x;
    c[i] = a[i] + b[i];
}

// GTID for a 1D grid of 1D blocks
__global__ void printfKernel()
{
    int tid = threadIdx.x;
    int bid = blockIdx.x;
    int gtid = bid * blockDim.x + tid;
    printf("threadIdx.x=%2d  blockIdx.x=%2d  GTID=%2d\n", tid, bid, gtid);
}

// y = a*x + y
__global__ void saxpyKernel(int n, float a, const float* x, float* y)
{
    size_t i = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
    if (i < (size_t)n)
        y[i] = a * x[i] + y[i];
}

// C = A + B, M rows x N cols, row-major: idx = row*N + col
__global__ void matAdd2DKernel(float* C, const float* A, const float* B, int M, int N)
{
    int col = blockIdx.x * blockDim.x + threadIdx.x;  // x -> columns (fastest)
    int row = blockIdx.y * blockDim.y + threadIdx.y;  // y -> rows
    if (row < M && col < N) {
        size_t idx = (size_t)row * N + col;
        C[idx] = A[idx] + B[idx];
    }
}

// C = A + B, M rows x N cols x P slices, row-major: idx = (z*M + y)*N + x
__global__ void gridAdd3DKernel(float* C, const float* A, const float* B, int M, int N, int P)
{
    int x = blockIdx.x * blockDim.x + threadIdx.x;  // columns, 0..N-1
    int y = blockIdx.y * blockDim.y + threadIdx.y;  // rows,    0..M-1
    int z = blockIdx.z * blockDim.z + threadIdx.z;  // slices,  0..P-1
    if (x < N && y < M && z < P) {
        size_t idx = ((size_t)z * M + y) * N + x;
        C[idx] = A[idx] + B[idx];
    }
}

// ---------------------------------------------------------------- CPU reference

static void saxpyCPU(size_t n, float a, const float* x, float* y)
{
    for (size_t i = 0; i < n; i++)
        y[i] = a * x[i] + y[i];
}

// Same loop for 2D (P=1) and 3D: element-wise add over a flattened array
static void addCPU(size_t n, float* C, const float* A, const float* B)
{
    for (size_t i = 0; i < n; i++)
        C[i] = A[i] + B[i];
}

// ---------------------------------------------------------------- helpers

static float* hostAlloc(size_t n)
{
    float* p = (float*)malloc(n * sizeof(float));
    if (!p) {
        fprintf(stderr, "malloc of %zu floats (%.2f GB) failed\n", n, n * 4.0 / 1e9);
        exit(EXIT_FAILURE);
    }
    return p;
}

// Deterministic pseudo-random floats in [lo, hi); not exactly representable sums/products,
// so CPU vs GPU rounding differences can show up.
static void fillRandom(float* p, size_t n, unsigned int seed, float lo, float hi)
{
    unsigned int s = seed;
    for (size_t i = 0; i < n; i++) {
        s = s * 1664525u + 1013904223u;
        p[i] = lo + (hi - lo) * ((s >> 8) * (1.0f / 16777216.0f));
    }
}

// L2 p37: |cpu - gpu| <= max(aTol, rTol * max(|cpu|, |gpu|))
static size_t countMismatches(const float* cpu, const float* gpu, size_t n, float rTol, float aTol)
{
    size_t bad = 0;
    for (size_t i = 0; i < n; i++) {
        float diff = fabsf(cpu[i] - gpu[i]);
        float tol = fmaxf(aTol, rTol * fmaxf(fabsf(cpu[i]), fabsf(gpu[i])));
        if (diff > tol)
            bad++;
    }
    return bad;
}

// Prints max errors, then a tolerance sweep, so the "at what tolerance does it fail" HW Q
// can be read straight off the output.
static bool verify(const char* name, const float* cpu, const float* gpu, size_t n)
{
    double maxAbs = 0, maxRel = 0;
    size_t notIdentical = 0, worst = 0;
    for (size_t i = 0; i < n; i++) {
        double d = fabs((double)cpu[i] - (double)gpu[i]);
        if (d != 0) notIdentical++;
        double m = fmax(fabs((double)cpu[i]), fabs((double)gpu[i]));
        double r = m > 0 ? d / m : 0;
        if (d > maxAbs) maxAbs = d;
        if (r > maxRel) { maxRel = r; worst = i; }
    }
    printf("  [%s] n=%zu  not bit-identical=%zu (%.4f%%)  max|diff|=%.3e  max rel=%.3e\n",
           name, n, notIdentical, 100.0 * notIdentical / n, maxAbs, maxRel);
    if (notIdentical)
        printf("  [%s] worst at i=%zu: cpu=%.9g gpu=%.9g\n", name, worst, cpu[worst], gpu[worst]);

    const float rTols[] = { 1e-5f, 1e-6f, 1e-7f, 5e-8f, 1e-8f, 0.0f };
    printf("  [%s] sweep (aTol=0):", name);
    for (float rt : rTols) {
        size_t bad = countMismatches(cpu, gpu, n, rt, 0.0f);
        printf("  rTol=%.0e:%s", rt, bad ? "FAIL" : "pass");
        if (bad) printf("(%zu)", bad);
    }
    printf("\n");

    size_t bad = countMismatches(cpu, gpu, n, 1e-5f, 1e-6f);  // course default for FP32
    printf("  [%s] rTol=1e-5 aTol=1e-6 -> %s\n", name, bad ? "FAILED" : "PASSED");
    return bad == 0;
}

// ---------------------------------------------------------------- tests

static void runAddVec()
{
    printf("\n=== default template: addWithCuda ===\n");
    const int arraySize = 5;
    const int a[arraySize] = { 1, 2, 3, 4, 5 };
    const int b[arraySize] = { 10, 20, 30, 40, 50 };
    int c[arraySize] = { 0 };

    if (checkCuda(addWithCuda(c, a, b, arraySize), "addWithCuda") != cudaSuccess)
        exit(EXIT_FAILURE);
    printf("{1,2,3,4,5} + {10,20,30,40,50} = {%d,%d,%d,%d,%d}\n", c[0], c[1], c[2], c[3], c[4]);
}

static void runPrintf(int grid, int block, int reps)
{
    for (int r = 0; r < reps; r++) {
        printf("\n--- printfKernel<<<%d,%d>>> run %d ---\n", grid, block, r + 1);
        fflush(stdout);
        printfKernel<<<grid, block>>>();
        CHECK_KERNEL("printfKernel");  // synchronize flushes the device printf buffer
    }
}

static void runSaxpy(size_t n)
{
    printf("\n=== SAXPY  N=%zu ===\n", n);
    const float a = 3.14159f;
    size_t bytes = n * sizeof(float);
    float* x = hostAlloc(n);
    float* y = hostAlloc(n);
    float* yCpu = hostAlloc(n);
    float* yGpu = hostAlloc(n);
    fillRandom(x, n, 1, -10.0f, 10.0f);
    fillRandom(y, n, 2, -10.0f, 10.0f);
    memcpy(yCpu, y, bytes);

    float *dX = nullptr, *dY = nullptr;
    CHECK_CUDA(cudaMalloc(&dX, bytes));
    CHECK_CUDA(cudaMalloc(&dY, bytes));
    CHECK_CUDA(cudaMemcpy(dX, x, bytes, cudaMemcpyHostToDevice));
    CHECK_CUDA(cudaMemcpy(dY, y, bytes, cudaMemcpyHostToDevice));

    const unsigned int threads = 256;
    unsigned int blocks = ceilDiv(n, threads);
    printf("  exec cfg <<<%u, %u>>>\n", blocks, threads);
    saxpyKernel<<<blocks, threads>>>((int)n, a, dX, dY);
    CHECK_KERNEL("saxpyKernel");
    CHECK_CUDA(cudaMemcpy(yGpu, dY, bytes, cudaMemcpyDeviceToHost));

    saxpyCPU(n, a, x, yCpu);
    verify("saxpy", yCpu, yGpu, n);

    CHECK_CUDA(cudaFree(dX));
    CHECK_CUDA(cudaFree(dY));
    free(x); free(y); free(yCpu); free(yGpu);
}

static void runMat2D(int M, int N)
{
    printf("\n=== 2D matrix add  MxN=%dx%d ===\n", M, N);
    size_t n = (size_t)M * N, bytes = n * sizeof(float);
    float* A = hostAlloc(n);
    float* B = hostAlloc(n);
    float* cCpu = hostAlloc(n);
    float* cGpu = hostAlloc(n);
    fillRandom(A, n, 3, -100.0f, 100.0f);
    fillRandom(B, n, 4, -100.0f, 100.0f);

    float *dA = nullptr, *dB = nullptr, *dC = nullptr;
    CHECK_CUDA(cudaMalloc(&dA, bytes));
    CHECK_CUDA(cudaMalloc(&dB, bytes));
    CHECK_CUDA(cudaMalloc(&dC, bytes));
    CHECK_CUDA(cudaMemcpy(dA, A, bytes, cudaMemcpyHostToDevice));
    CHECK_CUDA(cudaMemcpy(dB, B, bytes, cudaMemcpyHostToDevice));

    dim3 block(16, 16, 1);
    dim3 grid(ceilDiv(N, block.x), ceilDiv(M, block.y), 1);  // x covers columns, y covers rows
    printf("  exec cfg grid(%u,%u,%u) block(%u,%u,%u)\n", grid.x, grid.y, grid.z, block.x, block.y, block.z);
    matAdd2DKernel<<<grid, block>>>(dC, dA, dB, M, N);
    CHECK_KERNEL("matAdd2DKernel");
    CHECK_CUDA(cudaMemcpy(cGpu, dC, bytes, cudaMemcpyDeviceToHost));

    addCPU(n, cCpu, A, B);
    verify("mat2d", cCpu, cGpu, n);

    CHECK_CUDA(cudaFree(dA));
    CHECK_CUDA(cudaFree(dB));
    CHECK_CUDA(cudaFree(dC));
    free(A); free(B); free(cCpu); free(cGpu);
}

// If A, B, C don't all fit in free device memory (1e9 points = 12 GB; a T4 has 16 GB,
// an 8 GB card doesn't), the volume is processed in z-slabs. Each slab is a contiguous
// M x N x Pslab sub-volume, so the same 3D kernel and bounds check apply.
static void runGrid3D(int M, int N, int P)
{
    printf("\n=== 3D grid add  MxNxP=%dx%dx%d ===\n", M, N, P);
    size_t n = (size_t)M * N * P;
    size_t planeElems = (size_t)M * N;
    float* A = hostAlloc(n);
    float* B = hostAlloc(n);
    float* cGpu = hostAlloc(n);
    fillRandom(A, n, 5, -100.0f, 100.0f);
    fillRandom(B, n, 6, -100.0f, 100.0f);

    size_t freeB = 0, totalB = 0;
    CHECK_CUDA(cudaMemGetInfo(&freeB, &totalB));
    size_t perPlane = 3 * planeElems * sizeof(float);
    size_t budget = (size_t)(freeB * 0.8);
    int slab = (int)fmin((double)P, (double)(budget / perPlane));
    if (slab < 1) {
        fprintf(stderr, "not enough device memory for even one z-plane\n");
        exit(EXIT_FAILURE);
    }
    printf("  device free %.2f / %.2f GB, need %.2f GB -> %s (slab depth %d)\n",
           freeB / 1e9, totalB / 1e9, 3.0 * n * sizeof(float) / 1e9,
           slab == P ? "single pass" : "z-slabs", slab);

    size_t slabBytes = (size_t)slab * planeElems * sizeof(float);
    float *dA = nullptr, *dB = nullptr, *dC = nullptr;
    CHECK_CUDA(cudaMalloc(&dA, slabBytes));
    CHECK_CUDA(cudaMalloc(&dB, slabBytes));
    CHECK_CUDA(cudaMalloc(&dC, slabBytes));

    dim3 block(16, 8, 4);  // 512 threads
    for (int z0 = 0; z0 < P; z0 += slab) {
        int depth = (P - z0 < slab) ? P - z0 : slab;
        size_t off = (size_t)z0 * planeElems;
        size_t bytes = (size_t)depth * planeElems * sizeof(float);
        CHECK_CUDA(cudaMemcpy(dA, A + off, bytes, cudaMemcpyHostToDevice));
        CHECK_CUDA(cudaMemcpy(dB, B + off, bytes, cudaMemcpyHostToDevice));
        dim3 grid(ceilDiv(N, block.x), ceilDiv(M, block.y), ceilDiv(depth, block.z));
        if (z0 == 0)
            printf("  exec cfg grid(%u,%u,%u) block(%u,%u,%u)\n", grid.x, grid.y, grid.z, block.x, block.y, block.z);
        gridAdd3DKernel<<<grid, block>>>(dC, dA, dB, M, N, depth);
        CHECK_KERNEL("gridAdd3DKernel");
        CHECK_CUDA(cudaMemcpy(cGpu + off, dC, bytes, cudaMemcpyDeviceToHost));
    }

    // CPU reference written over B (no longer needed): 3 host arrays instead of 4,
    // i.e. 12 GB instead of 16 GB for the 1e9-point case.
    float* cCpu = B;
    addCPU(n, cCpu, A, B);
    verify("grid3d", cCpu, cGpu, n);

    CHECK_CUDA(cudaFree(dA));
    CHECK_CUDA(cudaFree(dB));
    CHECK_CUDA(cudaFree(dC));
    free(A); free(B); free(cGpu);
}

// ---------------------------------------------------------------- main

int main(int argc, char** argv)
{
    const char* mode = argc > 1 ? argv[1] : "all";
    bool big = false;
    for (int i = 1; i < argc; i++)
        if (strcmp(argv[i], "--big") == 0) big = true;
    bool all = strcmp(mode, "all") == 0;

    CHECK_CUDA(cudaSetDevice(0));
    cudaDeviceProp prop;
    CHECK_CUDA(cudaGetDeviceProperties(&prop, 0));
    printf("Device 0: %s (CC %d.%d, %.1f GB)\n", prop.name, prop.major, prop.minor, prop.totalGlobalMem / 1e9);

    if (all || strcmp(mode, "addvec") == 0)
        runAddVec();

    if (strcmp(mode, "printf") == 0 && argc >= 4) {
        runPrintf(atoi(argv[2]), atoi(argv[3]), argc >= 5 ? atoi(argv[4]) : 1);
    } else if (all || strcmp(mode, "printf") == 0) {
        runPrintf(1, 32, 1);
        runPrintf(4, 8, 1);
        runPrintf(32, 1, 1);
    }

    if (all || strcmp(mode, "saxpy") == 0) {
        runSaxpy(10);
        runSaxpy(1000);
        runSaxpy(10000000);
    }
    if (all || strcmp(mode, "mat2d") == 0) {
        runMat2D(4, 4);
        runMat2D(500, 500);
        runMat2D(3024, 4032);
    }
    if (all || strcmp(mode, "grid3d") == 0) {
        runGrid3D(3, 3, 3);
        runGrid3D(100, 100, 100);
        if (big)
            runGrid3D(1000, 1000, 1000);
        else
            printf("\n(3D 1000^3 skipped; add --big, Release build, ~12 GB free host RAM)\n");
    }

    // cudaDeviceReset must be called before exiting in order for profiling and
    // tracing tools such as Nsight and Visual Profiler to show complete traces.
    CHECK_CUDA(cudaDeviceReset());
    return 0;
}

// Helper function for using CUDA to add vectors in parallel (template code, now with checkCuda).
cudaError_t addWithCuda(int* c, const int* a, const int* b, unsigned int size)
{
    int* dev_a = 0;
    int* dev_b = 0;
    int* dev_c = 0;
    cudaError_t cudaStatus;

    // Choose which GPU to run on, change this on a multi-GPU system.
    cudaStatus = checkCuda(cudaSetDevice(0), "cudaSetDevice");
    if (cudaStatus != cudaSuccess) goto Error;

    // Allocate GPU buffers for three vectors (two input, one output).
    cudaStatus = checkCuda(cudaMalloc((void**)&dev_c, size * sizeof(int)), "cudaMalloc dev_c");
    if (cudaStatus != cudaSuccess) goto Error;
    cudaStatus = checkCuda(cudaMalloc((void**)&dev_a, size * sizeof(int)), "cudaMalloc dev_a");
    if (cudaStatus != cudaSuccess) goto Error;
    cudaStatus = checkCuda(cudaMalloc((void**)&dev_b, size * sizeof(int)), "cudaMalloc dev_b");
    if (cudaStatus != cudaSuccess) goto Error;

    // Copy input vectors from host memory to GPU buffers.
    cudaStatus = checkCuda(cudaMemcpy(dev_a, a, size * sizeof(int), cudaMemcpyHostToDevice), "cudaMemcpy a HtoD");
    if (cudaStatus != cudaSuccess) goto Error;
    cudaStatus = checkCuda(cudaMemcpy(dev_b, b, size * sizeof(int), cudaMemcpyHostToDevice), "cudaMemcpy b HtoD");
    if (cudaStatus != cudaSuccess) goto Error;

    // Launch a kernel on the GPU with one thread for each element.
    addKernel<<<1, size>>>(dev_c, dev_a, dev_b);

    // Check for any errors launching the kernel
    cudaStatus = checkCuda(cudaGetLastError(), "addKernel launch");
    if (cudaStatus != cudaSuccess) goto Error;

    // cudaDeviceSynchronize waits for the kernel to finish, and returns
    // any errors encountered during the launch.
    cudaStatus = checkCuda(cudaDeviceSynchronize(), "cudaDeviceSynchronize after addKernel");
    if (cudaStatus != cudaSuccess) goto Error;

    // Copy output vector from GPU buffer to host memory.
    cudaStatus = checkCuda(cudaMemcpy(c, dev_c, size * sizeof(int), cudaMemcpyDeviceToHost), "cudaMemcpy c DtoH");
    if (cudaStatus != cudaSuccess) goto Error;

Error:
    cudaFree(dev_c);
    cudaFree(dev_a);
    cudaFree(dev_b);

    return cudaStatus;
}
