#include "cuda_runtime.h"
#include "device_launch_parameters.h"
#include "cuda_check.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include <windows.h>
#include <profileapi.h>  // QueryPerformanceCounter / QueryPerformanceFrequency (Lecture 3)

#define STB_IMAGE_IMPLEMENTATION // this is needed
#include "../util/stb_image.h"  // download from class website files
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "../util/stb_image_write.h"  // download from class website files

// Input/output folder. Override with -DIMG_DIR=\"C:/path/\" or the --dir / --out arguments.
#ifndef IMG_DIR
#define IMG_DIR "D:/Repos/Au26_GPU/Au26_GPUCompute/HW2/dat/"
#endif

// Defaults used when the exe is run with no arguments (Ctrl+F5, ncu, debugger).
// Build one exe per case for ncu, e.g. -DIMG_IDX=3 -DKERNEL_SEL=0 -> hw2_rel_global_img3.exe
#ifndef IMG_IDX
#define IMG_IDX 1          // 1..4
#endif
#ifndef KERNEL_SEL
#define KERNEL_SEL 3       // 0 = global, 1 = static SMEM, 2 = dynamic SMEM, 3 = all three
#endif

// Nsight debugging, step 13: set to 1 to launch <<<1,1>>> instead of the full grid
#ifndef DEBUG_SINGLE_THREAD
#define DEBUG_SINGLE_THREAD 0
#endif

#define BLOCK_W 16
#define BLOCK_H 16

// global gaussian blur filter coefficients array here
#define BLUR_FILTER_WIDTH 9  // 9x9 (square) Gaussian blur filter
const float BLUR_FILT[81] = { 0.1084,0.1762,0.2494,0.3071,0.3292,0.3071,0.2494,0.1762,0.1084,0.1762,0.2865,0.4054,0.4994,0.5353,0.4994,0.4054,0.2865,0.1762,0.2494,0.4054,0.5738,0.7066,0.7575,0.7066,0.5738,0.4054,0.2494,0.3071,0.4994,0.7066,0.8703,0.9329,0.8703,0.7066,0.4994,0.3071,0.3292,0.5353,0.7575,0.9329,1.0000,0.9329,0.7575,0.5353,0.3292,0.3071,0.4994,0.7066,0.8703,0.9329,0.8703,0.7066,0.4994,0.3071,0.2494,0.4054,0.5738,0.7066,0.7575,0.7066,0.5738,0.4054,0.2494,0.1762,0.2865,0.4054,0.4994,0.5353,0.4994,0.4054,0.2865,0.1762,0.1084,0.1762,0.2494,0.3071,0.3292,0.3071,0.2494,0.1762,0.1084};

// Lecture 2 box blur (all weights 1, normalized by pixel count). Spec hint: get this working first, BLUR_SIZE = 10.
__global__ void blurKernel_box(const unsigned char* in, unsigned char* out, int w, int h, int blurSize)
{
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (col < w && row < h) {
        int pixVal = 0;
        int pixels = 0;
        for (int blurRow = -blurSize; blurRow < blurSize + 1; ++blurRow) {
            for (int blurCol = -blurSize; blurCol < blurSize + 1; ++blurCol) {
                int curRow = row + blurRow;
                int curCol = col + blurCol;
                if (curRow > -1 && curRow < h && curCol > -1 && curCol < w) {
                    pixVal += in[curRow * w + curCol];
                    ++pixels;
                }
            }
        }
        out[row * w + col] = (unsigned char)(pixVal / pixels);
    }
}

// Shared by all three Gaussian kernels: one output pixel per thread.
// Each weight*pixel product is rounded to the nearest int (__float2int_rn, not +0.5f, so nvcc can't fuse it into an FMA),
// and the int sum is normalized by the sum of the weights that actually landed inside the image.
__device__ __forceinline__ unsigned char gaussPixel(const unsigned char* in, const float* filt, int w, int h,
                                                    int filtWidth, int row, int col)
{
    int half = filtWidth / 2;
    int pixVal = 0;          // 32-bit accumulator (spec 5a.ii.1)
    float weightSum = 0.0f;
    for (int fr = -half; fr <= half; ++fr) {
        for (int fc = -half; fc <= half; ++fc) {
            int curRow = row + fr;
            int curCol = col + fc;
            if (curRow >= 0 && curRow < h && curCol >= 0 && curCol < w) {
                float wt = filt[(fr + half) * filtWidth + (fc + half)];
                pixVal += __float2int_rn(wt * (float)in[curRow * w + curCol]);
                weightSum += wt;
            }
        }
    }
    int outVal = __float2int_rn((float)pixVal / weightSum);
    return (unsigned char)min(255, max(0, outVal));
}

// blur kernel #1 - global memory only
__global__ void gaussBlurKernel_globalmem(const unsigned char* in, unsigned char* out, const float* d_filt,
                                          int w, int h, int filtWidth)
{
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (col < w && row < h)
        out[row * w + col] = gaussPixel(in, d_filt, w, h, filtWidth, row, col);
}

// blur kernel #2 - device shared memory (static alloc)
__global__ void gaussBlurKernel_sharedmem_static(const unsigned char* in, unsigned char* out, const float* d_filt,
                                                 int w, int h, int filtWidth)
{
    __shared__ float s_filt[BLUR_FILTER_WIDTH * BLUR_FILTER_WIDTH];

    // first threads of the block copy the coefficients, block-strided so <<<1,1>>> still loads all 81 (L3 p47).
    // Every thread, including ones outside the image, must reach __syncthreads(): bounds check comes after it.
    int tid = threadIdx.y * blockDim.x + threadIdx.x;
    int nCoef = filtWidth * filtWidth;
    for (int i = tid; i < nCoef; i += blockDim.x * blockDim.y)
        s_filt[i] = d_filt[i];
    __syncthreads();

    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (col < w && row < h)
        out[row * w + col] = gaussPixel(in, s_filt, w, h, filtWidth, row, col);
}

// blur kernel #3 - device shared memory (dynamic alloc, size given as the 3rd launch parameter)
__global__ void gaussBlurKernel_sharedmem_dynamic(const unsigned char* in, unsigned char* out, const float* d_filt,
                                                  int w, int h, int filtWidth)
{
    extern __shared__ float s_filtDyn[];

    int tid = threadIdx.y * blockDim.x + threadIdx.x;
    int nCoef = filtWidth * filtWidth;
    for (int i = tid; i < nCoef; i += blockDim.x * blockDim.y)
        s_filtDyn[i] = d_filt[i];
    __syncthreads();

    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    if (col < w && row < h)
        out[row * w + col] = gaussPixel(in, s_filtDyn, w, h, filtWidth, row, col);
}

// EXTRA CREDIT
// host sequential blur routine, same arithmetic as gaussPixel (nearbyintf = round-half-even like __float2int_rn)
void gaussBlurHost(const unsigned char* in, unsigned char* out, const float* filt, int w, int h, int filtWidth)
{
    int half = filtWidth / 2;
    for (int row = 0; row < h; ++row) {
        for (int col = 0; col < w; ++col) {
            int pixVal = 0;
            float weightSum = 0.0f;
            for (int fr = -half; fr <= half; ++fr) {
                for (int fc = -half; fc <= half; ++fc) {
                    int curRow = row + fr;
                    int curCol = col + fc;
                    if (curRow >= 0 && curRow < h && curCol >= 0 && curCol < w) {
                        float wt = filt[(fr + half) * filtWidth + (fc + half)];
                        float prod = wt * (float)in[curRow * w + curCol];
                        pixVal += (int)nearbyintf(prod);
                        weightSum += wt;
                    }
                }
            }
            float q = (float)pixVal / weightSum;
            int outVal = (int)nearbyintf(q);
            out[row * w + col] = (unsigned char)(outVal < 0 ? 0 : (outVal > 255 ? 255 : outVal));
        }
    }
}

static const char* KERNEL_NAMES[] = { "global", "static", "dynamic", "box" };

static double elapsedMs(LARGE_INTEGER start, LARGE_INTEGER stop, LARGE_INTEGER freq)
{
    return (double)(stop.QuadPart - start.QuadPart) * 1000.0 / (double)freq.QuadPart;
}

// timer #1 = device alloc + HtoD + kernel + DtoH (+ cudaFree); timer #2 = kernel launch -> cudaDeviceSynchronize()
static cudaError_t blurWithCuda(int kernelSel, const unsigned char* h_in, unsigned char* h_out, int w, int h,
                                int boxSize, double* t1Ms, double* t2Ms)
{
    cudaError_t cudaStatus = cudaSuccess;
    unsigned char* d_in = NULL;
    unsigned char* d_out = NULL;
    float* d_filt = NULL;
    size_t imgBytes = (size_t)w * h * sizeof(unsigned char);
    size_t filtBytes = BLUR_FILTER_WIDTH * BLUR_FILTER_WIDTH * sizeof(float);
    LARGE_INTEGER freq, t1Start, t1Stop, t2Start, t2Stop;

#if DEBUG_SINGLE_THREAD
    dim3 threadsPerBlock(1, 1);
    dim3 blocksPerGrid(1, 1);
#else
    dim3 threadsPerBlock(BLOCK_W, BLOCK_H);
    dim3 blocksPerGrid((w + BLOCK_W - 1) / BLOCK_W, (h + BLOCK_H - 1) / BLOCK_H);
#endif
    printf("  launch %-7s grid(%u,%u) block(%u,%u)\n", KERNEL_NAMES[kernelSel == 4 ? 3 : kernelSel],
           blocksPerGrid.x, blocksPerGrid.y, threadsPerBlock.x, threadsPerBlock.y);

    QueryPerformanceFrequency(&freq);

    // START timer #1
    QueryPerformanceCounter(&t1Start);

    // allocate device memory
    cudaStatus = checkCuda(cudaMalloc((void**)&d_in, imgBytes), "cudaMalloc d_in");
    if (cudaStatus != cudaSuccess) goto Error;
    cudaStatus = checkCuda(cudaMalloc((void**)&d_out, imgBytes), "cudaMalloc d_out");
    if (cudaStatus != cudaSuccess) goto Error;
    cudaStatus = checkCuda(cudaMalloc((void**)&d_filt, filtBytes), "cudaMalloc d_filt");
    if (cudaStatus != cudaSuccess) goto Error;

    // copy host data to device
    cudaStatus = checkCuda(cudaMemcpy(d_in, h_in, imgBytes, cudaMemcpyHostToDevice), "cudaMemcpy HtoD image");
    if (cudaStatus != cudaSuccess) goto Error;
    cudaStatus = checkCuda(cudaMemcpy(d_filt, BLUR_FILT, filtBytes, cudaMemcpyHostToDevice), "cudaMemcpy HtoD filter");
    if (cudaStatus != cudaSuccess) goto Error;

    // START timer #2
    QueryPerformanceCounter(&t2Start);
    switch (kernelSel) {
    case 0:
        gaussBlurKernel_globalmem<<<blocksPerGrid, threadsPerBlock>>>(d_in, d_out, d_filt, w, h, BLUR_FILTER_WIDTH);
        break;
    case 1:
        gaussBlurKernel_sharedmem_static<<<blocksPerGrid, threadsPerBlock>>>(d_in, d_out, d_filt, w, h, BLUR_FILTER_WIDTH);
        break;
    case 2:
        gaussBlurKernel_sharedmem_dynamic<<<blocksPerGrid, threadsPerBlock, filtBytes, 0>>>(d_in, d_out, d_filt, w, h, BLUR_FILTER_WIDTH);
        break;
    default:
        blurKernel_box<<<blocksPerGrid, threadsPerBlock>>>(d_in, d_out, w, h, boxSize);
        break;
    }

    // Check for any errors launching the kernel
    cudaStatus = checkCuda(cudaGetLastError(), "blur kernel launch");
    if (cudaStatus != cudaSuccess) goto Error;

    // wait for the kernel to finish, and return any errors encountered during the launch.
    cudaStatus = checkCuda(cudaDeviceSynchronize(), "cudaDeviceSynchronize after blur kernel");
    if (cudaStatus != cudaSuccess) goto Error;

    // STOP timer #2
    QueryPerformanceCounter(&t2Stop);

    // retrieve result data from device back to host
    cudaStatus = checkCuda(cudaMemcpy(h_out, d_out, imgBytes, cudaMemcpyDeviceToHost), "cudaMemcpy DtoH image");
    if (cudaStatus != cudaSuccess) goto Error;

    // free device memory (inside timer #1)
    cudaFree(d_in);   d_in = NULL;
    cudaFree(d_out);  d_out = NULL;
    cudaFree(d_filt); d_filt = NULL;

    // STOP timer #1
    QueryPerformanceCounter(&t1Stop);

    *t1Ms = elapsedMs(t1Start, t1Stop, freq);
    *t2Ms = elapsedMs(t2Start, t2Stop, freq);

Error:
    cudaFree(d_in);
    cudaFree(d_out);
    cudaFree(d_filt);
    return cudaStatus;
}

static int countMismatches(const unsigned char* a, const unsigned char* b, size_t n, int* maxDiff)
{
    int count = 0;
    *maxDiff = 0;
    for (size_t i = 0; i < n; ++i) {
        int d = abs((int)a[i] - (int)b[i]);
        if (d) {
            ++count;
            if (d > *maxDiff) *maxDiff = d;
        }
    }
    return count;
}

static void usage(void)
{
    printf("usage: hw2.exe [img 1-4|all] [global|static|dynamic|all|box] [--box N] [--nocpu] [--reps N] [--dir DIR] [--out DIR]\n"
           "  no arguments -> image %d, kernel(s) %s (compile-time IMG_IDX / KERNEL_SEL)\n",
           IMG_IDX, KERNEL_SEL == 3 ? "all" : KERNEL_NAMES[KERNEL_SEL]);
}

int main(int argc, char** argv)
{
    cudaError_t cudaStatus = cudaSuccess;
    int imgFirst = IMG_IDX, imgLast = IMG_IDX;
    int kernelSel = KERNEL_SEL;
    int boxSize = 10;
    int runCpu = 1;
    int reps = 1;
    const char* inDir = IMG_DIR;
    const char* outDir = IMG_DIR;

    for (int a = 1; a < argc; ++a) {
        const char* s = argv[a];
        if (!strcmp(s, "all") && a == 1) { imgFirst = 1; imgLast = 4; }
        else if (s[0] >= '1' && s[0] <= '4' && s[1] == 0) { imgFirst = imgLast = s[0] - '0'; }
        else if (!strcmp(s, "global")) kernelSel = 0;
        else if (!strcmp(s, "static")) kernelSel = 1;
        else if (!strcmp(s, "dynamic")) kernelSel = 2;
        else if (!strcmp(s, "all")) kernelSel = 3;
        else if (!strcmp(s, "box")) kernelSel = 4;
        else if (!strcmp(s, "--box") && a + 1 < argc) { kernelSel = 4; boxSize = atoi(argv[++a]); }
        else if (!strcmp(s, "--nocpu")) runCpu = 0;
        else if (!strcmp(s, "--reps") && a + 1 < argc) reps = atoi(argv[++a]);
        else if (!strcmp(s, "--dir") && a + 1 < argc) inDir = argv[++a];
        else if (!strcmp(s, "--out") && a + 1 < argc) outDir = argv[++a];
        else { usage(); return 1; }
    }

#ifdef _DEBUG
    const char* buildType = "Debug";
#else
    const char* buildType = "Release";
#endif
    printf("HW2 Gaussian blur  build=%s  DEBUG_SINGLE_THREAD=%d\n", buildType, DEBUG_SINGLE_THREAD);

    // create the CUDA context up front so timer #1 doesn't include context creation
    cudaStatus = checkCuda(cudaFree(0), "cudaFree(0) context init");
    if (cudaStatus != cudaSuccess) return 1;

    for (int img = imgFirst; img <= imgLast; ++img) {
        char filename[512], imgFileOut[512];
        snprintf(filename, sizeof(filename), "%shw2_testimage%d.png", inDir, img);

        // read input image from file - be aware of image pixel bit-depth and resolution (horiz x vertical)
        int x_cols = 0;
        int y_rows = 0;
        int n_pixdepth = 0;
        unsigned char* imgData = stbi_load(filename, &x_cols, &y_rows, &n_pixdepth, 1);
        if (!imgData) {
            fprintf(stderr, "stbi_load failed for %s: %s\n", filename, stbi_failure_reason());
            return 1;
        }
        size_t imgSize = (size_t)x_cols * y_rows * sizeof(unsigned char);
        printf("\n=== image %d: %s  %d x %d  channels in file=%d (loaded as 1) ===\n",
               img, filename, x_cols, y_rows, n_pixdepth);

        unsigned char* h_imgOut = (unsigned char*)malloc(imgSize);
        unsigned char* h_imgCpu = (unsigned char*)malloc(imgSize);
        if (!h_imgOut || !h_imgCpu) { fprintf(stderr, "malloc failed\n"); return 1; }

        // EXTRA CREDIT: timer #3 around the host sequential blur (also the reference for verification)
        double t3Ms = 0.0;
        if (runCpu) {
            LARGE_INTEGER freq, t3Start, t3Stop;
            QueryPerformanceFrequency(&freq);
            QueryPerformanceCounter(&t3Start);
            gaussBlurHost(imgData, h_imgCpu, BLUR_FILT, x_cols, y_rows, BLUR_FILTER_WIDTH);
            QueryPerformanceCounter(&t3Stop);
            t3Ms = elapsedMs(t3Start, t3Stop, freq);
            printf("  cpu     timer3=%10.3f ms\n", t3Ms);
            printf("RESULT build=%s img=%d w=%d h=%d kernel=cpu t3_ms=%.4f\n", buildType, img, x_cols, y_rows, t3Ms);
            snprintf(imgFileOut, sizeof(imgFileOut), "%shw2_outimage%d_cpu.png", outDir, img);
            stbi_write_png(imgFileOut, x_cols, y_rows, 1, h_imgCpu, x_cols);
        }

        int kFirst = kernelSel == 3 ? 0 : kernelSel;
        int kLast = kernelSel == 3 ? 2 : kernelSel;
        for (int k = kFirst; k <= kLast; ++k) {
            int kIdx = k == 4 ? 3 : k;
            // rep 1 of the first kernel launched also pays the one-time module load (and PTX JIT on non-sm_75 GPUs)
            for (int rep = 1; rep <= reps; ++rep) {
                double t1Ms = 0.0, t2Ms = 0.0;
                memset(h_imgOut, 0, imgSize);
                cudaStatus = blurWithCuda(k, imgData, h_imgOut, x_cols, y_rows, boxSize, &t1Ms, &t2Ms);
                if (cudaStatus != cudaSuccess) break;

                int maxDiff = 0;
                int mism = (runCpu && k != 4) ? countMismatches(h_imgCpu, h_imgOut, imgSize, &maxDiff) : -1;
                printf("  %-7s rep %d  timer1=%10.3f ms  timer2=%10.3f ms  mismatches vs CPU=%d (max diff %d)\n",
                       KERNEL_NAMES[kIdx], rep, t1Ms, t2Ms, mism, maxDiff);
                printf("RESULT build=%s img=%d w=%d h=%d kernel=%s rep=%d t1_ms=%.4f t2_ms=%.4f mismatches=%d\n",
                       buildType, img, x_cols, y_rows, KERNEL_NAMES[kIdx], rep, t1Ms, t2Ms, mism);
            }
            if (cudaStatus != cudaSuccess) break;

            // save result output image data to file
            if (k == 4)
                snprintf(imgFileOut, sizeof(imgFileOut), "%shw2_outimage%d_box%d.png", outDir, img, boxSize);
            else
                snprintf(imgFileOut, sizeof(imgFileOut), "%shw2_outimage%d_%s.png", outDir, img, KERNEL_NAMES[kIdx]);
            stbi_write_png(imgFileOut, x_cols, y_rows, 1, h_imgOut, x_cols);
        }

        // free host memory
        stbi_image_free(imgData);
        free(h_imgOut);
        free(h_imgCpu);
        if (cudaStatus != cudaSuccess) break;
    }

    // cudaDeviceReset( ) must be called in order for profiling and
    // tracing tools such as Nsight and Visual Profiler to show complete traces.
    cudaDeviceReset();
    return cudaStatus == cudaSuccess ? 0 : 1;
}
