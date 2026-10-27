"""Short written answers for HW2_Answers_data.docx (run after fill_data_docx.py; edits the file in place).

python fill_answers_docx.py <HW2_Answers_data.docx>
"""
import sys

import docx

from fill_data_docx import box_after, put_lines

MCQ = [
    ("b.  1,000", [
        "A __shared__ variable gets one copy per thread block. The 512 threads of a block share it, and it is freed "
        "when the block finishes, so 1000 blocks create 1000 copies."]),
    ("c.  1/32 of the original usage", [
        "Without tiling, every thread reads its own row of A and column of B from global memory, so each element is "
        "loaded N times. With 32×32 tiles, a block loads each A and B element into shared memory once per phase and "
        "32 threads reuse it, so global reads drop by a factor of TILE_WIDTH = 32."]),
    ("b.  32", [
        "One A tile is 32 × 32 floats × 4 B = 4096 B. Each tile row is 32 consecutive floats = 128 B, which is one "
        "burst when the row is aligned and the warp's loads are coalesced. 32 rows give 4096 / 128 = 32 bursts."]),
]

BOXES = {
    "DEBUG vs RELEASE comparison": [
        "Debug kernels (T2) are about 13 to 37 times slower than Release; for image 4 it is 144.5 ms vs 4.17 ms. The Debug "
        "build compiles device code with -G, which turns off device optimizations and keeps variables in memory for "
        "the debugger (nvcc --resource-usage for sm_75: the shared-memory kernel uses 56 registers per thread in "
        "Debug and 38 in Release).",
        "The host CPU blur is about 1.7× slower in Debug (/Od). For the small images, T1 is mostly the fixed "
        "cudaMalloc/cudaMemcpy cost (about 0.5 ms in Release), so T1 changes much less than T2."],
    "QUESTION: How many warps": [
        "Measured on this PC's RTX 3050 (not a T4), Warp Info showed 640 warps (Viewing 640/640). A 16×16 block is "
        "256 threads = 8 warps, and image 1 needs "
        "15 × 15 = 225 blocks = 1800 warps, more than the GPU can hold at once.",
        "The debugger was stopped in the global-memory kernel. Its Debug sm_86 code, which the RTX 3050 runs, uses 56 "
        "registers per thread, so a warp takes 56 × 32 = 1792 registers and a block of 8 warps takes 14,336 of an "
        "SM's 65,536. That limits each SM to 4 blocks = 32 warps (the 1536-thread limit would allow 6). The RTX 3050 "
        "has 20 SMs: 20 × 32 = 640.",
        "For the Tesla T4 (computed from its specs, not observed): 40 SMs, each with at most 1024 threads (32 warps) "
        "and 64K registers. The sm_75 Debug code uses 49 registers, which rounds up to the same 1792 per warp "
        "(registers are allocated in units of 256), so both limits give 4 blocks per SM and a T4 would run "
        "40 × 32 = 1280 warps at once, finishing the remaining 65 blocks in a second wave."],
    "HW Q: Why does kernel execution time differ": [
        "The static shared-memory kernel is 4.6 to 6.6% faster on every image (image 4: 3.87 ms vs 4.12 ms). Each output "
        "pixel reads all 81 filter coefficients. In the global version each of those reads is a global load that "
        "goes through L1/L2. In the shared version the block copies the 324 B once, and every later read comes from "
        "on-chip shared memory, which has lower latency and does not compete with the pixel loads for L1.",
        "The gap is small because all 32 threads of a warp read the same coefficient, so the global version mostly "
        "hits in L1 anyway, and most of the time goes to the 81 pixel loads and the arithmetic."],
    "HW Q: Reason about observed differences": [
        "Instruction counts are close (516 M vs 493 M for image 4), so the difference is memory traffic: DRAM bytes "
        "drop from 80.3 MB to 45.8 MB and instruction intensity rises from 6.4 to 10.8 inst/B.",
        "Both kernels execute many instructions per DRAM byte and use only 19.5 GB/s (global) and 11.8 GB/s (shared) "
        "of the RTX 3050's 224 GB/s, so neither is bandwidth bound. That is why moving only the coefficients into "
        "shared memory gives a small speedup. Tiling the input pixels into shared memory would cut global pixel "
        "loads from 81 per output to about (24×24)/(16×16) = 2.25.",
        "For images 1 and 2 the whole output stays in the 3050's 1.5 MB L2 (almost no DRAM writes), image 3 writes "
        "only part of it back, and the DRAM counters vary between runs, so only image 4's instruction intensity is a "
        "reliable comparison."],
}

EXTRA_CREDIT = [
    "FLOPs per interior pixel: each of the 81 taps does one multiply (weight × pixel) and one add (weight sum), plus "
    "one divide for normalization, about 163 FLOP. Integer adds and the float-to-int rounding are not counted.",
    "Without caching, the global kernel reads 81 pixel bytes and 81 four-byte coefficients per output pixel and "
    "writes 1 byte (406 B). The shared kernel reads the 324 B of coefficients once per 256-thread block (≈83.3 B).",
    "Measured on image 4 (163 × 12.19 M ≈ 1.99 GFLOP over the NCU DRAM bytes): about 25 FLOP/B for global and "
    "43 FLOP/B for shared, because L1/L2 absorb most of the repeated pixel reads."]


def main(path):
    d = docx.Document(path)
    answers = iter(MCQ)
    reasoning_boxes = []
    body = list(d.element.body)
    for i, el in enumerate(body):
        if not el.tag.endswith("}p"):
            continue
        text = "".join(el.itertext())
        if text.startswith("Answer: ________"):
            ans, why = next(answers)
            p = docx.text.paragraph.Paragraph(el, d._body)
            p.runs[1].text = " " + ans
        elif text.startswith("Work / Reasoning"):
            reasoning_boxes.append(docx.table.Table(body[i + 1], d._body).rows[0].cells[0])
    for cell, (_, why) in zip(reasoning_boxes[:3], MCQ):
        put_lines(cell, why, size=10)
    put_lines(reasoning_boxes[3], EXTRA_CREDIT, size=10)
    for label, lines in BOXES.items():
        put_lines(box_after(d, label), lines, size=10)
    d.save(path)


if __name__ == "__main__":
    main(sys.argv[1])
