"""HW2 P1/P2: AI values and roofline plots. Run: python roofline.py <out_dir>"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

B = 4  # FP32 bytes

# ---- P1: AI expressions with the chosen values ----
def transpose(N):
    flops = 0
    mem = B * N * N + B * N * N          # read A, write A^T
    return flops, mem

def softmax_3pass(N, rows=1):
    # pass 1: m = max x_i      -> (N-1) compares, read N
    # pass 2: e_i = exp(x_i-m), s = sum e_i -> N sub + 4N exp + (N-1) add, read N, write N (e)
    # pass 3: y_i = e_i / s    -> N div, read N (e), write N (y)
    flops = rows * ((N - 1) + (N + 4 * N + (N - 1)) + N)
    mem = rows * (B * N + (B * N + B * N) + (B * N + B * N))
    return flops, mem

def conv2d(N, C, H, W, K):
    # out[n,co,h,w] = sum_{ci,kh,kw} in[n,ci,h+kh,w+kw] * w[co,ci,kh,kw]; C_in = C_out = C, stride 1, same padding
    flops = 2 * N * C * H * W * C * K * K   # one FMA (=2 FLOP) per MAC
    mem = B * N * C * H * W + B * C * C * K * K + B * N * C * H * W   # read input, read weights, write output
    return flops, mem

KERNELS = [
    ("transpose N=4096", *transpose(4096)),
    ("softmax N=4096, 1024 rows", *softmax_3pass(4096, 1024)),
    ("conv N=32,C=3,224x224,K=3", *conv2d(32, 3, 224, 224, 3)),
    ("conv N=32,C=16,224x224,K=3", *conv2d(32, 16, 224, 224, 3)),
    ("conv N=32,C=64,224x224,K=3", *conv2d(32, 64, 224, 224, 3)),
]

GPUS = {
    "Quadro RTX 6000 (TU102)": dict(peak=16.3e12, bw=672e9,
                                     note="4608 FP32 cores x 2 x 1.77 GHz boost; 384-bit GDDR6 @ 14 Gbps"),
    "H100 SXM5": dict(peak=67e12, bw=3.35e12, note="FP32 (non-Tensor) 67 TFLOPS; HBM3 3.35 TB/s"),
}

def regime(ai, ridge):
    if ai < ridge / 2:
        return "memory-bound"
    if ai > 2 * ridge:
        return "compute-bound"
    return "transitional"

def main(out):
    out.mkdir(parents=True, exist_ok=True)
    lines = ["| kernel | FLOPs | Mem bytes | AI (FLOP/B) |", "|---|---|---|---|"]
    for name, f, m in KERNELS:
        lines.append(f"| {name} | {f:.4g} | {m:.4g} | {f / m:.4g} |")
    for g, s in GPUS.items():
        ridge = s["peak"] / s["bw"]
        lines.append(f"\n**{g}**: peak {s['peak']/1e12:.1f} TFLOP/s, BW {s['bw']/1e9:.0f} GB/s, ridge {ridge:.2f} FLOP/B ({s['note']})")
        for name, f, m in KERNELS:
            ai = f / m
            att = min(s["peak"], ai * s["bw"])
            lines.append(f"- {name}: AI {ai:.3g} -> {regime(ai, ridge)}, attainable {att/1e12:.3g} TFLOP/s")

        fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=150)
        x = np.logspace(-2, 3, 400)
        ax.loglog(x, np.minimum(s["peak"], x * s["bw"]) / 1e12, color="#222", lw=2, label="roofline")
        ax.axvline(ridge, color="#888", ls="--", lw=1)
        ax.axvspan(ridge / 2, ridge * 2, color="#f2c94c", alpha=0.25, label="transitional (ridge/2 .. 2x ridge)")
        ax.text(ridge * 1.05, s["peak"] / 1e12 * 0.55, f"ridge = {ridge:.1f}", fontsize=8)
        markers = "osD^v"
        for (name, f, m), mk in zip(KERNELS, markers):
            ai = max(f / m, 0.011)  # transpose AI = 0 can't sit on a log axis: pinned to the left edge
            perf = min(s["peak"], ai * s["bw"]) / 1e12
            lbl = f"{name} (AI={f/m:.3g}, {regime(f/m, ridge)})"
            ax.plot(ai, perf, mk, ms=7, label=lbl)
        ax.set_xlabel("Arithmetic intensity (FLOP/byte)")
        ax.set_ylabel("Attainable FP32 performance (TFLOP/s)")
        ax.set_title(f"Roofline: {g}")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=7, loc="lower right")
        fig.tight_layout()
        fn = out / ("roofline_" + g.split()[0].lower() + ".png")
        fig.savefig(fn)
        plt.close(fig)
        lines.append(f"- plot: {fn.name}")
    (out / "p1_p2_values.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
