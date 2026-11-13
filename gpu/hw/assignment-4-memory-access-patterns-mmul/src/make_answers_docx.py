"""Blank HW4 answer sheet in the same style as HW1-HW3 (helpers reused from hw2/src and hw3/src).

python make_answers_docx.py <HW1_Answers.docx (style base)> <out HW4_Answers.docx>
"""
import importlib.util
import os
import sys

from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("hw3_sheet", os.path.join(HERE, "..", "..", "hw3", "src",
                                                                         "make_answers_docx.py"))
hw3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hw3)  # also puts hw2/src on sys.path and imports its Sheet

WT = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"


def _retitle(s):
    # Sheet() rewrites the HW1 header/footer to "HW2"; this sheet is HW4
    for sec in s.d.sections:
        for part in (sec.header, sec.footer, sec.first_page_header, sec.first_page_footer):
            for t in part._element.iter(WT):
                if t.text and "HW2" in t.text:
                    t.text = t.text.replace("HW2", "HW4")


def code(s, text):
    """kernel source from the spec, one paragraph with line breaks"""
    para = s.d.add_paragraph()
    lines = text.strip("\n").split("\n")
    for i, line in enumerate(lines):
        r = para.add_run(line)
        r.font.name = "Consolas"
        r.font.size = Pt(9)
        if i < len(lines) - 1:
            r.add_break()


PICTURE_KERNEL = """
__global__ void PictureKernel(float* d_Pin, float* d_Pout, int n, int m) {
    // Calculate the row # of the d_Pin and d_Pout element to process
    int Row = blockIdx.y*blockDim.y + threadIdx.y;
    // Calculate the column # of the d_Pin and d_Pout element to process
    int Col = blockIdx.x*blockDim.x + threadIdx.x;
    // each thread computes one element of d_Pout if in range
    if ((Row < m) && (Col < n)) {
        d_Pout[Row*n+Col] = 2*d_Pin[Row*n+Col];
    }
}"""

MATMUL_KERNEL = """
__global__ void MatrixMulKernel(float* M, float* N, float* P, int Width)
{
    int Row = blockIdx.y*blockDim.y+threadIdx.y;
    int Col = blockIdx.x*blockDim.x+threadIdx.x;
    if ((Row < Width) && (Col < Width)) {
        float Pvalue = 0;
        for (int k = 0; k < Width; ++k) {
            Pvalue += M[Row*Width+k] * N[k*Width+Col];}
        P[Row*Width+Col] = Pvalue;
    }
}"""

CONFIGS = ["v0 8×8", "v0 16×16", "v0 32×32", "v1 8×8", "v1 16×16", "v1 32×32"]


def build(base, out):
    s = hw3.Sheet(base)
    _retitle(s)
    mcq = lambda title, q, opts: hw3.mcq(s, title, q, opts)  # noqa: E731

    s.p("Homework #4 (HW4)", bold=True, size=18)
    s.p("Memory access patterns & MMULT coalesced corner turning kernel", size=13)
    s.p("Autumn 2026 – GPU Computing", size=11)
    s.table(["Field", ""], [["Name"], ["UW NetID"], ["Build environment"]], widths=[2400, 6960])

    # ---------------- Questions ----------------
    s.h("Part 1 – Questions", 1)
    mcq("Question 1",
        "Assume we use a tiled matrix multiplication kernel that handles data boundary conditions only on the right "
        "edge and lower (bottom) edges. Assume that we use 32X32 tiles to process square matrices of 1,000 x 1,000. "
        "Within EACH thread block, what is the maximal number of warps that will have control divergence due to "
        "handling boundary conditions for loading input matrix M (review L1 slides 31-35) tiles throughout the "
        "kernel execution?",
        ["32", "24", "16", "8"])

    s.h("Question 2", 2)
    s.p("We are to process a 600X800 (800 pixels in the x or horizontal column direction, 600 pixels in the y or "
        "vertical row direction) image with the PictureKernel(). That is m = 600 and n = 800.")
    code(s, PICTURE_KERNEL)
    s.p("Assume that we decided to use a grid of 16X16 blocks. That is, each block is organized as a 2D 16X16 array "
        "of threads. How many warps will be generated during the execution of the kernel?")
    for letter, o in zip("ABCD", ["37*16", "38*8*50", "38*50", "38*50*2"]):
        s.option(letter, o)
    s.label_value("Answer:")
    s.p("Work / Reasoning:", bold=True)
    s.box(1.4)

    mcq("Question 3", "In Question 2, how many warps will have control divergence?",
        ["37 + 50*8", "0", "38*16", "50"])
    mcq("Question 4",
        "In Question 2, if we are to process an 800x600 picture (600 pixels in the x or horizontal direction and 800 "
        "pixels in the y or vertical direction) picture, how many warps will have control divergence?",
        ["50*8", "37+50*8", "38*16", "0"])
    mcq("Question 5",
        "In Question 2, if are to process a 799x600 picture (600 pixels in the x direction and 799 pixels in the y "
        "direction), how many warps will have control divergence?",
        ["(37+50)*8", "50*8", "37+50*8", "0"])

    s.h("Question 6", 2)
    s.p("Assume the following simple matrix multiplication kernel")
    code(s, MATMUL_KERNEL)
    s.p("If we launch the kernel with a block size of 16X16 on a 1000x1000 matrix, how many warps will have control "
        "divergence?")
    for letter, o in zip("ABCD", ["1,000", "508", "1,008", "500"]):
        s.option(letter, o)
    s.label_value("Answer:")
    s.p("Work / Reasoning:", bold=True)
    s.box(1.4)

    mcq("Question 7",
        "If a CUDA device’s SM (streaming multiprocessor) can take up to 1,536 threads and up to 8 thread blocks. "
        "Which of the following block configuration would result in the largest number of threads in each SM?",
        ["64 threads per block", "512 threads per block", "128 threads per block", "1,024 threads per block"])
    mcq("Question 8",
        "Assume that we want to use each thread to calculate two output elements of a vector addition. Assume that "
        "variable i should be initialized with the index for the first element to be processed by a thread. Which of "
        "the following should be used for such initialization to allow correct, coalesced memory accesses to these "
        "first elements in the following statement?  if(i<n) C[i] = A[i] + B[i];",
        ["int i=(blockIdx.x*blockDim.x)*2 + threadIdx;", "int i=(blockIdx.x*blockDim.x + threadIdx.x)*2;",
         "int i=(threadIdx.x*blockDim.x)*2 + blockIdx.x;", "int i=(threadIdx.x*blockDim.x + blockIdx.x)*2;"])
    mcq("Question 9",
        "Continuing from Question 8, what would be the correct statement for each thread to process the second "
        "element?",
        ["If (i<n) C[i+1] = A[i+1] + B[i+1];", "If (i+1<n) C[i+1] = A[i+1] + B[i+1];",
         "If (i+threadIdx.x < n) C[i+threadIdx.x] = A[i+threadIdx.x] + B[i+threadIdx.x];",
         "if(i+blockDim.x < n) C[i+blockDim.x] = A[i+blockDim.x] + B[i+blockDim.x];"])

    s.h("Question 10", 2)
    s.p("Assume the following simple matrix multiplication kernel")
    code(s, MATMUL_KERNEL)
    s.p("Based on the coalesced access judging criterion in Lecture 5 (slide 35), which of the following is true?")
    for letter, o in zip("ABCD", [
            "M[Row*Width+k] and N[k*Width+Col] are coalesced but P[Row*Width+Col] is not",
            "M[Row*Width+k], N[k*Width+Col] and P[Row*Width+Col] are all coalesced",
            "M[Row*Width+k] is coalesced but N[k*Width+Col] and P[Row*Width+Col] are not",
            "M[Row*Width+k] is not coalesced but N[k*Width+Col] and P[Row*Width+Col] both are"]):
        s.option(letter, o)
    s.label_value("Answer:")
    s.p("Work / Reasoning:", bold=True)
    s.box(1.4)

    # ---------------- Programming and Analysis ----------------
    s.d.add_page_break()  # keeps the 2.1 metrics table on one page
    s.h("Part 2 – Programming and Analysis Exercises", 1)
    s.h("2.1 Memory Access Patterns – Profiler Analysis", 2)
    s.p("Square matrices of 256 x 256 elements; MMULTv0: all-global memory (GMEM) – naive; MMULTv1: tiled/phased "
        "shared-memory (SMEM). 2D TILE_WIDTH = thread-block dimensions 8x8, 16x16, 32x32.")
    s.h("Nsight Compute Memory Workload Analysis (Memory Chart / Memory Tables)", 3)
    rows = []
    for level, metrics in [("Shared Memory", ["Wavefronts"]),
                           ("L1/TEX", ["Bytes", "Sectors", "Sectors/Req", "Wavefronts", "Hit Rate (%)"]),
                           ("L2", ["Bytes", "Sectors", "Sectors/Req", "Hit Rate (%)"]),
                           ("Global Memory", ["Bytes", "Sectors"])]:
        rows += [[level, m] for m in metrics]
    s.table(["Memory level", "Metric"] + CONFIGS, rows,
            widths=[1500, 1680, 1030, 1030, 1030, 1030, 1030, 1030], size=16)
    s.h("Analyze the transaction sizes and patterns between each memory level in terms of Bytes and Sectors "
        "transferred, Sectors/Req, and wavefronts. Also consider the L1 and L2 cache hit/miss performance metrics.", 3)
    s.box(2.0)

    s.h("Describe how the thread-block size relates to the warp memory access patterns and the use and efficiency "
        "of coalesced accesses and shared memory.", 3)
    s.box(2.4)
    s.h("Consider the total # bytes read from each memory level/unit for each kernel thread, based on the kernel "
        "launch configuration and input data sizes.", 3)
    s.table(["Bytes read per thread", "Shared Memory", "L1/TEX", "L2", "Global Memory"],
            [[c] for c in CONFIGS], widths=[2160, 1800, 1800, 1800, 1800])
    s.h("If you see any discrepancies or unexpected numbers in the profile report, identify those and consider if "
        "the “complicating factors” discussed in L5 (slide #28) might be contributing. Why or why not?", 3)
    s.box(2.0)

    s.h("2.2 Coalesced Corner Turning Pattern: MMULTv1b Kernel", 2)
    s.label_value("MMULTv2b full round-trip execution time:", "________________")
    s.h("Host-side verification: same input matrices M & N", 3)
    s.table(["Case", "Same (correct) results?"],
            [["a. CPU sequential reference MMULT_CPU"], ["b. GPU MMULTv0 (all-global)"],
             ["b. GPU MMULTv1 (tiled/SMEM)"], ["c. GPU MMULTv1b (corner turning, transposed M)"]],
            widths=[5360, 4000])
    s.h("Analysis of the profiling results – Coalesced Corner Turning", 3)
    s.box(2.6)

    hw3.keep_together(s.d)
    cp = s.d.core_properties
    cp.title = "Homework #4 (HW4) – Autumn 2026 GPU Computing"
    cp.subject = "HW4 answer sheet"
    s.d.save(out)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
