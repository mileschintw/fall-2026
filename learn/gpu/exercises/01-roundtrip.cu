// 01-roundtrip.cu — 模組 1：vector add 的 GPU round-trip 時間都花在哪
//
// 對每個 n，量 cudaMalloc、H2D、kernel、D2H 各花多少時間，跟 CPU 迴圈比。
// 要改的地方：
//   - 第 22 行 USE_PINNED：0 = 一般 malloc（作業的寫法），1 = cudaMallocHost（pinned）。
//     預期：pinned 的 H2D/D2H 會變快，但 kernel 的占比還是很小。
//   - 第 23 行 sizes[]：加你想試的 n。
// 對照：L1 [01:43:01]（瓶頸在 PCIe 傳輸）、L3 [03:34:00]（HW2 要量 HtoD+kernel+DtoH 的 round-trip）。
//
// 編譯：見 exercises/README.md（NN-slug 換成 01-roundtrip）。

#include <cstdio>
#include <cstdlib>
#include <chrono>
#include <cuda_runtime.h>

__global__ void vecAdd(const float* a, const float* b, float* c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) c[i] = a[i] + b[i];
}

#define USE_PINNED 0
static const int sizes[] = {1000, 100000, 10000000};

#define CK(x) do { cudaError_t e = (x); if (e != cudaSuccess) { \
    printf("CUDA error %s at line %d\n", cudaGetErrorString(e), __LINE__); exit(1); } } while (0)

int main() {
    CK(cudaFree(0));  // 先建立 CUDA context，不然第一次呼叫會多出幾百 ms
    cudaEvent_t t0, t1;
    CK(cudaEventCreate(&t0)); CK(cudaEventCreate(&t1));
    printf("pinned=%d\n", USE_PINNED);
    printf("%10s %10s %10s %10s %10s %10s %10s %8s\n",
           "n", "malloc_ms", "H2D_ms", "kernel_ms", "D2H_ms", "GPU_total", "CPU_ms", "kernel%");

    for (int n : sizes) {
        size_t bytes = (size_t)n * sizeof(float);
        float *a, *b, *c;
#if USE_PINNED
        CK(cudaMallocHost(&a, bytes)); CK(cudaMallocHost(&b, bytes)); CK(cudaMallocHost(&c, bytes));
#else
        a = (float*)malloc(bytes); b = (float*)malloc(bytes); c = (float*)malloc(bytes);
#endif
        for (int i = 0; i < n; i++) { a[i] = (float)i; b[i] = 2.0f * i; }

        // CPU 版本（baseline，也拿來驗證）
        float* ref = (float*)malloc(bytes);
        auto c0 = std::chrono::high_resolution_clock::now();
        for (int i = 0; i < n; i++) ref[i] = a[i] + b[i];
        auto c1 = std::chrono::high_resolution_clock::now();
        double cpu_ms = std::chrono::duration<double, std::milli>(c1 - c0).count();

        float *da, *db, *dc;
        float ms_malloc, ms_h2d, ms_kernel, ms_d2h;

        CK(cudaEventRecord(t0));
        CK(cudaMalloc(&da, bytes)); CK(cudaMalloc(&db, bytes)); CK(cudaMalloc(&dc, bytes));
        CK(cudaEventRecord(t1)); CK(cudaEventSynchronize(t1));
        CK(cudaEventElapsedTime(&ms_malloc, t0, t1));

        CK(cudaEventRecord(t0));
        CK(cudaMemcpy(da, a, bytes, cudaMemcpyHostToDevice));
        CK(cudaMemcpy(db, b, bytes, cudaMemcpyHostToDevice));
        CK(cudaEventRecord(t1)); CK(cudaEventSynchronize(t1));
        CK(cudaEventElapsedTime(&ms_h2d, t0, t1));

        int block = 256, grid = (n + block - 1) / block;
        CK(cudaEventRecord(t0));
        vecAdd<<<grid, block>>>(da, db, dc, n);
        CK(cudaEventRecord(t1)); CK(cudaEventSynchronize(t1));
        CK(cudaGetLastError());
        CK(cudaEventElapsedTime(&ms_kernel, t0, t1));

        CK(cudaEventRecord(t0));
        CK(cudaMemcpy(c, dc, bytes, cudaMemcpyDeviceToHost));
        CK(cudaEventRecord(t1)); CK(cudaEventSynchronize(t1));
        CK(cudaEventElapsedTime(&ms_d2h, t0, t1));

        int bad = 0;
        for (int i = 0; i < n; i++) if (c[i] != ref[i]) bad++;

        float total = ms_malloc + ms_h2d + ms_kernel + ms_d2h;
        printf("%10d %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f %7.1f%%%s\n",
               n, ms_malloc, ms_h2d, ms_kernel, ms_d2h, total, cpu_ms,
               100.0f * ms_kernel / total, bad ? "  WRONG" : "");

        CK(cudaFree(da)); CK(cudaFree(db)); CK(cudaFree(dc));
#if USE_PINNED
        CK(cudaFreeHost(a)); CK(cudaFreeHost(b)); CK(cudaFreeHost(c));
#else
        free(a); free(b); free(c);
#endif
        free(ref);
    }
    return 0;
}
