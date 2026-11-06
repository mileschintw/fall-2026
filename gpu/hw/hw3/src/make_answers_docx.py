"""Blank HW3 answer sheet in the same style as HW1/HW2 (layout helpers reused from hw2/src/make_answers_docx.py).

python make_answers_docx.py <HW1_Answers.docx (style base)> <out HW3_Answers.docx>
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "hw2", "src"))
from make_answers_docx import Sheet  # noqa: E402
import docx  # noqa: E402
from docx.oxml import parse_xml  # noqa: E402

WT = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"


def _retitle(s):
    # Sheet() rewrites the HW1 header/footer to "HW2"; this sheet is HW3
    for sec in s.d.sections:
        for part in (sec.header, sec.footer, sec.first_page_header, sec.first_page_footer):
            for t in part._element.iter(WT):
                if t.text and "HW2" in t.text:
                    t.text = t.text.replace("HW2", "HW3")


def mcq(s, title, q, opts):
    s.h(title, 2)
    s.p(q)
    for letter, o in zip("ABCD", opts):
        s.option(letter, o)
    s.label_value("Answer:")
    s.p("Work / Reasoning:", bold=True)
    s.box(1.4)


def keep_together(d):
    """no heading or label left alone at a page bottom; short tables (up to 8 rows) stay on one page (as in HW2)"""
    body = list(d.element.body)
    for i, el in enumerate(body[:-1]):
        if not el.tag.endswith("}p"):
            continue
        para = docx.text.paragraph.Paragraph(el, d._body)
        heading = para.style is not None and para.style.name.startswith("Heading")
        para.paragraph_format.keep_together = True
        if heading or (para.text.strip() and (body[i + 1].tag.endswith("}tbl") or
                                              body[i + 1].tag.endswith("}p"))):
            para.paragraph_format.keep_with_next = True
    for t in d.tables:
        if 1 < len(t.rows) <= 8:
            for row in t.rows[:-1]:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        p.paragraph_format.keep_with_next = True
    # the spacer paragraph after the last box can spill onto a blank final page
    body = d.element.body
    while body[-2].tag.endswith("}p") and not "".join(body[-2].itertext()).strip():
        body.remove(body[-2])
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    body.insert(len(body) - 1, parse_xml(
        f'<w:p xmlns:w="{W}"><w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>'
        f'<w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>'))


def build(base, out):
    s = Sheet(base)
    _retitle(s)
    s.p("Homework #3 (HW3)", bold=True, size=18)
    s.p("Control Divergence & Tiled MMULT improvements & NCU profiling", size=13)
    s.p("Autumn 2026 – GPU Computing", size=11)
    s.table(["Field", ""], [["Name"], ["UW NetID"], ["Build environment"]], widths=[2400, 6960])

    # ---------------- Questions ----------------
    s.h("Part 1 – Questions", 1)
    mcq(s, "Question I",
        "If the SM of a CUDA device can take up to 1536 threads and up to 4 thread blocks. Which of the following "
        "block configurations would result in the largest number of threads in the SM?",
        ["128 threads per block", "256 threads per block", "512 threads per block", "1024 threads per block"])
    mcq(s, "Question II",
        "For a vector addition, assume that the vector length is 2000, each thread calculates one output element, "
        "and the thread block size is 512 threads. How many threads will be in the grid?",
        ["2000", "2024", "2048", "2096"])
    mcq(s, "Question III",
        "With reference to the previous question, how many warps do you expect to have divergence due to the "
        "boundary check on vector length?",
        ["1", "2", "3", "6"])

    s.h("Question IV", 2)
    s.p("Assume a device that allows up to 64 blocks per SM and 2048 threads per SM. Indicate which of the following "
        "assignments per SM are possible. In the cases in which it is possible, indicate the occupancy level.")
    s.table(["Assignment per SM", "Possible?", "Occupancy"],
            [["A. 8 blocks with 128 threads each"], ["B. 16 blocks with 64 threads each"],
             ["C. 32 blocks with 32 threads each"], ["D. 64 blocks with 32 threads each"],
             ["E. 32 blocks with 64 threads each"]], widths=[4560, 2400, 2400])
    s.p("Work / Reasoning:", bold=True)
    s.box(1.6)

    s.h("Question V", 2)
    s.p("Consider a GPU with the following hardware limits: 2048 threads per SM, 32 blocks per SM, and 64K (65,536) "
        "registers per SM. For each of the following kernel characteristics, specify whether the kernel can achieve "
        "full occupancy. If not, specify the limiting factor, and the maximum occupancy % achieved.")
    s.table(["Kernel", "Full occupancy?", "Limiting factor", "Max occupancy %"],
            [["A. 128 threads/block, 30 registers/thread"], ["B. 32 threads/block, 29 registers/thread"],
             ["C. 256 threads/block, 34 registers/thread"]], widths=[3660, 1900, 2000, 1800])
    s.p("Work / Reasoning:", bold=True)
    s.box(1.6)

    # ---------------- Analysis ----------------
    s.h("Part 2 – Analysis", 1)
    s.h("Control Divergence", 2)
    s.p("Impact of control divergence for the N tiles in the tiled MMULT algorithm (same method as Lecture 4 for the "
        "M tiles; PMPP section 4.5).")
    s.table(["Block type", "Warp phases with divergence", "Expected performance impact %"],
            [["Type 1"], ["Type 2"], ["Total"]], widths=[2400, 3480, 3480])
    s.p("Work / Reasoning (behavior of the Type 1 and Type 2 blocks):", bold=True)
    s.box(2.4)
    s.h("Q: When will the warp divergence impact become minimal?", 3)
    s.box(1.2)
    s.h("Q: How does varying tile size affect arithmetic intensity?", 3)
    s.box(1.2)

    # ---------------- Programming ----------------
    s.h("Part 3 – Programming Exercises", 1)
    s.h("3.1 Control Divergence Kernels", 2)
    s.table(["Section", "Metric", "Single branch: no divergence", "Single branch: divergence",
             "Nested branch: no divergence", "Nested branch: divergence"],
            [["Occupancy", "Theoretical Occupancy"], ["Occupancy", "Achieved Occupancy"],
             ["Occupancy", "Theoretical Active Warps per SM"], ["Occupancy", "Achieved Active Warps per SM"],
             ["Warp State Statistics", "Avg. Active Threads Per Warp"],
             ["Warp State Statistics", "Avg. Not Predicated Off Threads Per Warp"]],
            widths=[1500, 2260, 1400, 1400, 1400, 1400], size=18)
    s.h("Based on the configuration of your kernels for control divergence, can you explain how the Nsight Compute "
        "metrics can capture or identify when divergence is happening?", 3)
    s.box(1.8)
    s.h("Can you find any other general GPU profiling metrics (GPU Speed of Light) which change between divergent and "
        "non-divergent runs?", 3)
    s.box(1.4)

    s.h("3.2 MMULT Variants", 2)
    s.h("What is the maximum single-element abs error fraction observed?", 3)
    s.p("absolute error fraction = abs[Pcpu(x,y) - Gpu(x,y)] / Pcpu(x,y)")
    s.table(["Case", "GPU v0 (naive, GMEM)", "GPU tiled (SMEM)"],
            [["P: 100×100, k = 100"], ["P: 1000×1000, k = 1000"], ["P: 2000×3000, k = 2500"]],
            widths=[3360, 3000, 3000])

    s.h("Nsight Compute profiling results", 3)
    s.p("Kernel execution time = smsp__cycles_elapsed.sum / smsp__cycles_elapsed.sum.per_second (s → ms); "
        "kernel instruction intensity = smsp__inst_executed.sum / dram__bytes.sum.")
    rows = []
    for case in ["100×100, k=100", "1000×1000, k=1000", "2000×3000, k=2500"]:
        rows.append([case, "v0 naive, block (__,__,1)"])
        for tw in (8, 12, 16, 32):
            rows.append([case, f"tiled TILE_WIDTH {tw}, block ({tw},{tw},1)"])
    s.table(["P, k", "Kernel / launch configuration", "Kernel execution time (ms)", "Instruction intensity (inst/B)",
             "AI (FLOP/B)", "Compute throughput (%)", "Achieved occupancy (%)"], rows,
            widths=[1300, 2060, 1200, 1200, 1200, 1200, 1200], size=16)
    for case in ["P: 100×100, k = 100", "P: 1000×1000, k = 1000", "P: 2000×3000, k = 2500"]:
        s.p(f"Roofline with baselines – {case}:", bold=True)
        s.box(3.2)
    s.p("All configurations on a single Roofline (baselines):", bold=True)
    s.box(3.2)
    s.p("Nsight Compute profile reports with the set of baselines (all configurations tested):", bold=True)
    s.box(3.2)

    s.h("Which configurations (TILE_WIDTH + thread-block size) provide the best performance?", 3)
    s.table(["Criterion", "P: 100×100, k = 100", "P: 1000×1000, k = 1000", "P: 2000×3000, k = 2500"],
            [["Highest AI"], ["Highest compute throughput"], ["Fastest execution Duration"], ["Highest Occupancy"]],
            widths=[2760, 2200, 2200, 2200])
    s.h("Under any configurations or input sizes are kernels in the compute-bound regime?", 3)
    s.box(1.2)
    s.h("Do these results vary with the size of the input/output matrices?", 3)
    s.p("Try to explain the behavior in a few sentences, referring to available device resources and other Nsight "
        "profile metrics as applicable.")
    s.box(1.8)

    s.h("FMAD option (P: 2000×3000, k = 2500)", 3)
    s.label_value("Best performing configuration:", "________________")
    s.table(["Metric", "--fmad=true (default)", "--fmad=false"],
            [["AI (FLOP/B)"], ["Execution duration (ms)"], ["Compute throughput (%)"], ["Achieved occupancy (%)"]],
            widths=[3360, 3000, 3000])
    s.h("Did the performance change?", 3)
    s.p("Consider all the metrics: AI, execution duration, compute throughput, occupancy.")
    s.box(1.4)
    s.h("When you disable fused multiply add, you force the hardware to split a single FMA into separate MUL and ADD "
        "instructions. How does it impact arithmetic intensity?", 3)
    s.box(1.4)

    s.h("Additional Questions", 2)
    s.h("What if we transpose the input matrix N, so that both the matrices are row-major in the memory, is the "
        "performance overhead required for doing the transpose worth it?", 3)
    s.box(1.6)
    s.h("If you push the TILE_WIDTH to 32, you max out the hardware limit of 1024 threads per block. Does maximizing "
        "threads per block guarantee the highest occupancy?", 3)
    s.box(1.6)

    s.h("Profiling Analysis Discussion", 2)
    s.p("Discussion of the profiling analysis for the MMULT kernels, the various launch configurations and input/output "
        "matrix sizes, and the FMAD option:", bold=True)
    s.box(3.0)

    keep_together(s.d)
    cp = s.d.core_properties
    cp.title = "Homework #3 (HW3) – Autumn 2026 GPU Computing"
    cp.subject = "HW3 answer sheet"
    s.d.save(out)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
