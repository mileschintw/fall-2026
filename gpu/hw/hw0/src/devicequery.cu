// HW0 - CUDA Host Runtime API: Device Query
// Spec field names maxThreadDim / warpsize are really maxThreadsDim / warpSize.
#include "cuda_runtime.h"
#include <stdio.h>

static int check(cudaError_t e, const char* what)
{
    if (e != cudaSuccess) {
        fprintf(stderr, "%s failed: %s\n", what, cudaGetErrorString(e));
        return 1;
    }
    return 0;
}

int main()
{
    // Initialize CUDA (cudaInitDevice(device, deviceFlags, flags), CUDA 12.0+)
    if (check(cudaInitDevice(0, 0, 0), "cudaInitDevice")) return 1;

    // Get number of CUDA devices
    int deviceCount = 0;
    if (check(cudaGetDeviceCount(&deviceCount), "cudaGetDeviceCount")) return 1;
    printf("CUDA devices: %d\n", deviceCount);

    // Loop through each device
    for (int device = 0; device < deviceCount; device++)
    {
        // Select device
        if (check(cudaSetDevice(device), "cudaSetDevice")) return 1;

        // Get driver/runtime versions (encoded as 1000*major + 10*minor)
        int driverVer = 0, runtimeVer = 0;
        check(cudaDriverGetVersion(&driverVer), "cudaDriverGetVersion");
        check(cudaRuntimeGetVersion(&runtimeVer), "cudaRuntimeGetVersion");

        // Get device properties
        cudaDeviceProp p;
        if (check(cudaGetDeviceProperties(&p, device), "cudaGetDeviceProperties")) return 1;

        // Print required device properties
        printf("\n=== Device %d: %s ===\n", device, p.name);
        printf("  Driver / Runtime version     : %d.%d / %d.%d\n",
               driverVer / 1000, (driverVer % 1000) / 10, runtimeVer / 1000, (runtimeVer % 1000) / 10);
        printf("  Compute capability           : %d.%d\n", p.major, p.minor);
        printf("  totalGlobalMem               : %zu bytes (%.2f GB)\n", p.totalGlobalMem, p.totalGlobalMem / 1e9);
        printf("  l2CacheSize                  : %d bytes\n", p.l2CacheSize);
        printf("  multiProcessorCount          : %d\n", p.multiProcessorCount);
        printf("  maxBlocksPerMultiProcessor   : %d\n", p.maxBlocksPerMultiProcessor);
        printf("  maxThreadsPerMultiProcessor  : %d\n", p.maxThreadsPerMultiProcessor);
        printf("  maxThreadsPerBlock           : %d\n", p.maxThreadsPerBlock);
        printf("  maxThreadsDim[3]             : %d x %d x %d\n", p.maxThreadsDim[0], p.maxThreadsDim[1], p.maxThreadsDim[2]);
        printf("  maxGridSize[3]               : %d x %d x %d\n", p.maxGridSize[0], p.maxGridSize[1], p.maxGridSize[2]);
        printf("  regsPerBlock                 : %d\n", p.regsPerBlock);
        printf("  regsPerMultiprocessor        : %d\n", p.regsPerMultiprocessor);
        printf("  sharedMemPerMultiprocessor   : %zu bytes\n", p.sharedMemPerMultiprocessor);
        printf("  warpSize                     : %d\n", p.warpSize);
    }
    return 0;
}
