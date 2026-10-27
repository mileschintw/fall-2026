"""HW2 P1/P2: AI values and roofline plots. Run: python roofline.py <out_dir>

Plot shows only what P2 asks for: the roofline, the ridge point, the P1 kernels' AIs, and each kernel's regime.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

B = 4  # FP32 bytes


def transpose(N):
    return 0, B * N * N + B * N * N                      # no FLOPs; read A, write A^T


def softmax_3pass(N, rows=1):
    flops = rows * ((N - 1) + (N + 4 * N + (N - 1)) + N)  # max; sub + exp + sum; divide
    mem = rows * (B * N + 2 * B * N + 2 * B * N)          # read x; read x + write e; read e + write y
    return flops, mem


def conv2d(N, C, H, W, K):
    flops = 2 * N * C * H * W * C * K * K                 # one FMA (= 2 FLOP) per MAC, C_in = C_out = C
    mem = B * N * C * H * W + B * C * C * K * K + B * N * C * H * W
    return flops, mem


KERNELS = [
    ("transpose", "N = 4096", *transpose(4096)),
    ("softmax", "N = 4096, 1024 rows", *softmax_3pass(4096, 1024)),
    ("conv", "N = 32, C = 64, 224x224, K = 3", *conv2d(32, 64, 224, 224, 3)),
]

GPUS = {
    "Quadro RTX 6000 (TU102)": dict(peak=16.3e12, bw=672e9, file="roofline_quadro.png"),
    "H100 SXM5": dict(peak=67e12, bw=3.35e12, file="roofline_h100.png"),
}


def regime(ai, ridge):
    if ai < ridge / 2:
        return "memory-bound"
    if ai > 2 * ridge:
        return "compute-bound"
    return "transitional"


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    lines = ["| kernel | chosen values | FLOPs | Mem bytes | AI (FLOP/B) |", "|---|---|---|---|---|"]
    for name, vals, f, m in KERNELS:
        lines.append(f"| {name} | {vals} | {f:.4g} | {m:.4g} | {f / m:.4g} |")
    for g, s in GPUS.items():
        ridge = s["peak"] / s["bw"]
        peak_t = s["peak"] / 1e12
        lines.append(f"\n**{g}**: peak {peak_t:.1f} TFLOP/s, BW {s['bw']/1e9:.0f} GB/s, ridge {ridge:.2f} FLOP/B")

        fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=150)
        x = np.logspace(-2, 3, 400)
        ax.loglog(x, np.minimum(s["peak"], x * s["bw"]) / 1e12, color="black", lw=1.8)
        ax.plot(ridge, peak_t, "ko", ms=5)
        ax.annotate(f"ridge point\nAI = {ridge:.1f}", (ridge, peak_t), textcoords="offset points",
                    xytext=(6, -32), fontsize=8, ha="left")
        for name, _, f, m in KERNELS:
            ai = f / m
            r = regime(ai, ridge)
            lines.append(f"- {name}: AI {ai:.3g} -> {r}")
            x_plot = max(ai, 0.01)  # transpose AI = 0 cannot sit on a log axis: drawn at the left edge
            y = min(s["peak"], x_plot * s["bw"]) / 1e12
            ax.plot(x_plot, y, "o", color="tab:blue", ms=6)
            label = f"{name} (AI = {ai:.3g})\n{r}"
            ax.annotate(label, (x_plot, y), textcoords="offset points", xytext=(10, -22) if ai == 0 else (10, -22) if ai < ridge else (0, 8),
                        fontsize=8, ha="left" if ai < ridge else "center", va="bottom" if ai >= ridge else "baseline")
        ax.set_ylim(top=peak_t * 5, bottom=s["bw"] * 0.01 / 1e12 * 0.3)
        ax.set_xlabel("Arithmetic intensity (FLOP/byte)")
        ax.set_ylabel("Performance (TFLOP/s)")
        ax.set_title(g)
        fig.tight_layout()
        fig.savefig(out / s["file"])
        plt.close(fig)
        lines.append(f"- plot: {s['file']}")
    (out / "p1_p2_values.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
