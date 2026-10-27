| kernel | FLOPs | Mem bytes | AI (FLOP/B) |
|---|---|---|---|
| transpose N=4096 | 0 | 1.342e+08 | 0 |
| softmax N=4096, 1024 rows | 3.355e+07 | 8.389e+07 | 0.4 |
| conv N=32,C=3,224x224,K=3 | 2.601e+08 | 3.854e+07 | 6.75 |
| conv N=32,C=16,224x224,K=3 | 7.399e+09 | 2.055e+08 | 36 |
| conv N=32,C=64,224x224,K=3 | 1.184e+11 | 8.222e+08 | 144 |

**Quadro RTX 6000 (TU102)**: peak 16.3 TFLOP/s, BW 672 GB/s, ridge 24.26 FLOP/B (4608 FP32 cores x 2 x 1.77 GHz boost; 384-bit GDDR6 @ 14 Gbps)
- transpose N=4096: AI 0 -> memory-bound, attainable 0 TFLOP/s
- softmax N=4096, 1024 rows: AI 0.4 -> memory-bound, attainable 0.269 TFLOP/s
- conv N=32,C=3,224x224,K=3: AI 6.75 -> memory-bound, attainable 4.54 TFLOP/s
- conv N=32,C=16,224x224,K=3: AI 36 -> transitional, attainable 16.3 TFLOP/s
- conv N=32,C=64,224x224,K=3: AI 144 -> compute-bound, attainable 16.3 TFLOP/s
- plot: roofline_quadro.png

**H100 SXM5**: peak 67.0 TFLOP/s, BW 3350 GB/s, ridge 20.00 FLOP/B (FP32 (non-Tensor) 67 TFLOPS; HBM3 3.35 TB/s)
- transpose N=4096: AI 0 -> memory-bound, attainable 0 TFLOP/s
- softmax N=4096, 1024 rows: AI 0.4 -> memory-bound, attainable 1.34 TFLOP/s
- conv N=32,C=3,224x224,K=3: AI 6.75 -> memory-bound, attainable 22.6 TFLOP/s
- conv N=32,C=16,224x224,K=3: AI 36 -> transitional, attainable 67 TFLOP/s
- conv N=32,C=64,224x224,K=3: AI 144 -> compute-bound, attainable 67 TFLOP/s
- plot: roofline_h100.png
