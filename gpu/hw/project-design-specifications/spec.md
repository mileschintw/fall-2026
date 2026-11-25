# Project - Design Specifications

> 來源：Canvas assignment 11810630（https://canvas.uw.edu/courses/1917398/assignments/11810630），抓取 2026-11-25 07:43 PST。
> 這個檔案由 `scripts/assignment_specs.py` 產生，內容是原文，每次來源有變動就整份重寫，不要手改。整理過的版本在 README.md。

- 截止（Canvas `due_at`）：2026-12-04 (Fri) 11:59 PM PST

## Canvas 作業說明

Project Design Specification: Requirements

Format: PDF or Word Docx

Contents:

Provide a concise summary section and pseudocode for each kernel variant planned for implementation.
describe each planned kernel, input data types, GPU memory resources used, special architectural features and design patterns and techniques (from class) used (for example: naive/global-memory, shared memory, phased-tiled, privatization, coarsening, register tiling, tensor cores, etc).
Provide a Tuning/Optimization matrix (table) showing all the planned test configurations/variations to be evaluated, including (where relevant):
grid/block launch configuration sizes
tile sizes for various hierarchical tile levels (SMEM, register)
Register usage, shared memory sizes
Any other configurable kernel parameters (which will depend on the specific kernel algorithm/implementation), such as (possibly)
Other GPU memory locations where coefficients are stored
L1/L2 cache usage
Provide a table of initial performance timing (baseline) results for each kernel to be tuned.
Include timed performance results for CPU reference verification versions of each kernel type.
For HOST side timing: use windows high performance timer API or STDlibrary chrono classes (seehttps://en.cppreference.com/w/cpp/chrono/high_resolution_clock) toestablish baseline runtimes for various dataset sizes
For GPU device kernel timing use CUDA Events and Nsight Compute profile results.
Provide Nsight Compute profiling results and analysis for initial starter kernels {conv_direct.cu, conv_im2col.cu}
List the primary kernel tuning/optimization guidance items provided by NSightCompute for each kernel, and the estimated speedup achievable.
It is STRONGLY recommended you begin your tuning/optimization efforts by investigating the highest-recommended fixes automatically provided by Nsight Compute!
