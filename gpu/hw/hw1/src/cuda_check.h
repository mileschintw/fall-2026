#pragma once
// CUDA Runtime API error checking (L1 updated slide p55).
// srcStr is const char* (the slide's char* won't accept a string literal in C++).
#include <cstdio>
#include <cstdlib>
#include <cassert>
#include "cuda_runtime.h"

inline static cudaError_t checkCuda(cudaError_t result, const char* srcStr)
{
    if (result != cudaSuccess) {
        fprintf(stderr, "CUDA Runtime Error (src: %s): %s\n", srcStr, cudaGetErrorString(result));
        assert(result == cudaSuccess);  // only fires in Debug builds
    }
    return result;
}

// Wraps checkCuda and exits on failure, so Release builds (no assert) also stop.
#define CHECK_CUDA(call)                                        \
    do {                                                        \
        if (checkCuda((call), #call) != cudaSuccess)            \
            exit(EXIT_FAILURE);                                 \
    } while (0)

// Kernels return void: check the launch with cudaGetLastError, then wait for it to finish.
#define CHECK_KERNEL(name)                                      \
    do {                                                        \
        if (checkCuda(cudaGetLastError(), name) != cudaSuccess) \
            exit(EXIT_FAILURE);                                 \
        CHECK_CUDA(cudaDeviceSynchronize());                    \
    } while (0)
