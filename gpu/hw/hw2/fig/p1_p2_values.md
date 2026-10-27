| kernel | chosen values | FLOPs | Mem bytes | AI (FLOP/B) |
|---|---|---|---|---|
| transpose | N = 4096 | 0 | 1.342e+08 | 0 |
| softmax | N = 4096, 1024 rows | 3.355e+07 | 8.389e+07 | 0.4 |
| conv | N = 32, C = 64, 224x224, K = 3 | 1.184e+11 | 8.222e+08 | 144 |

**Quadro RTX 6000 (TU102)**: peak 16.3 TFLOP/s, BW 672 GB/s, ridge 24.26 FLOP/B
- transpose: AI 0 -> memory-bound
- softmax: AI 0.4 -> memory-bound
- conv: AI 144 -> compute-bound
- plot: roofline_quadro.png

**H100 SXM5**: peak 67.0 TFLOP/s, BW 3350 GB/s, ridge 20.00 FLOP/B
- transpose: AI 0 -> memory-bound
- softmax: AI 0.4 -> memory-bound
- conv: AI 144 -> compute-bound
- plot: roofline_h100.png
