# GPU Lecture 3 — 2026-10-20（SIMD／SIMT 與 warp、平行效能理論（speedup、Amdahl、arithmetic intensity、roofline）、naive 與 tiled MMULT、CUDA 記憶體階層、HW2）

> 來源：transcript（Teams 自動逐字稿 `transcript.vtt`，2446 cues，00:01:05–03:35:51，約 3 小時 35 分）、slides（Au26_GPU-Compute_Lecture3.pdf，Canvas file 154698067，76 頁；另有 10/22 上傳的手寫註解版 `Au26_GPU-Compute_Lecture3_w_notes.pdf`，file 154778212，76 頁。註解是壓平的筆跡，不在文字層裡，是逐頁轉成圖片再和原版比對讀出來的，見「講義手寫註解」一節，標成（註解 pN））、閱讀章節：Reading Set #2 = PMPP 4th ed. Ch3 §1–4、Ch4 §1–4（對應 L2、L3）；Reading Set #3 = PMPP Ch5 全章（10/19 起，對應 L3–L5、HW2–3）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：sam's → SMs；Cindy → SIMD；SYSD → SISD；Matt Mall / MMALT → MMult（matrix multiplication）；Cublast / Kublas / KuBlast → cuBLAS；blast → BLAS；gem V / Gem V → GEMV；SIAS → SASS；Kuobj dump → cuobjdump；Omdal / Mom dolls law → Amdahl's law；Gustafson Barsi → Gustafson-Barsis；Week scaling → weak scaling；big O micron → big-Omicron；rich point / bridge point → ridge point；ECE sheet → spec sheet；Coop Pilot → Copilot；Colonel → kernel；Team in → GMEM；Shared, man → shared mem；Tse → C（GEMM 的輸出）；"Court concurrent workers" → P concurrent workers；"100 gigabit per second" → 投影片 p24 寫 100 GB/s；Devika、Diya 是兩位 TA。
>
> 錄影注意：錄影檔 18:27 開始，[00:02:54] 才正式上課（約 6:30 PM）。[01:57:06]–[02:07:45] 是 pop quiz 加休息（約 10 分鐘空白），[02:53:05]–[02:58:38] 是第二次 5 分鐘休息。

## 重點摘要

1. **SIMD vs SIMT 與 Flynn's taxonomy**（p4–p7）
   - Von Neumann model：processing unit（ALU + register file）、control unit（PC、IR）、記憶體同時放資料和指令。GPU 和整個 CPU+GPU 異質系統都能套進這個模型。
   - Flynn's taxonomy 依 instruction stream × data stream 分成 SISD、SIMD、MISD、MIMD。MISD 少見，可以想成 pipeline 填滿時多道指令同時處理一份資料。
   - CPU SIMD：vector 是程式設計的單位，programmer（或 compiler）要自己處理寬度、masking、data layout（SSE／AVX 這類固定寬度指令集）。
   - NVIDIA SIMT：scalar thread 是程式設計的單位。寫 kernel 等於宣告各 thread 互相獨立，硬體自動把 32 個 thread 組成 warp 在 SIMD lane 上跑，masking、divergence、per-lane addressing、latency hiding 都由硬體和 compiler 處理。
   - SIMT 的好處：同一份 kernel 可以在不同 NVIDIA 裝置上跑（未必最佳）。
2. **Warp 是排程單位**（p8–p10）
   - Block 被分配到 SM 之後切成 32-thread warp，依 thread index 遞增的順序：warp0 = 0–31、warp1 = 32–63。2D／3D block 先以 row-major 攤平再切。
   - Warp 大小 32 是實作細節，不屬於 CUDA programming model，未來可能改變。
   - 不滿 32 的 warp 用 inactive thread 補齊，所以 block 大小要取 32 的倍數。
   - 例：3 個 block × 256 threads → 每 block 8 warps，共 24 warps。
   - 例：Z×Y×X = 2×8×4 的 3D block（64 threads）→ warp0 = T(0,0,0)…T(0,7,3)，warp1 = T(1,0,0)…T(1,7,3)。
   - Zero-overhead warp scheduling：每個 warp slot 都保有完整 context，切換 warp 不需要像 CPU 那樣做 context switch。運算元備妥的 warp 才 eligible，依優先順序挑選發出。
   - Warp-level primitives（vote／match／reduce／shuffle／`__sync`）讓 warp 成為 block 和 thread 之間多一層的軟體階層，之後會用到。
3. **效能理論的基本量**（p11–p13）
   - Latency（時間，越低越好）、throughput（work/time，越高越好）、bandwidth（通常指記憶體傳輸率 bytes/s，有時指硬體峰值）。
   - p12：各種技術的 BW 相差約 10⁶、latency 相差約 10⁷；bandwidth 可以花錢買（加 lane／channel），latency 受物理限制。
   - Analysis-driven optimization：建立 baseline → 訂目標 → 反覆修改 → 每次修改都驗證正確性（不必逐 bit 相同，用 tolerance）→ 量效能。
   - Analytical 指標用來事先看出 scaling 上限和瓶頸原因；empirical 量測才看得到 bank conflict 這類真實世界的額外成本。
4. **Speedup、efficiency、scaling**（p14–p15）
   - Speedup S_P = T₁ / T_P；efficiency = S_P / P。Efficiency = 1 是 linear speedup，> 1 是 superlinear（少見）。
   - Relative speedup：baseline 是平行演算法的序列化版本。Absolute speedup：baseline 是更好的序列演算法。兩者都必須解**完全相同**的計算問題。
   - Strong scaling：問題大小固定、P 變動 → Amdahl's law；每個 processor 的記憶體是 M/P。
   - Weak scaling：問題大小隨 P 成長 → Gustafson-Barsis' law；每個 processor 的記憶體維持 M。
5. **Growth of functions 與 asymptotic 分析**（p16–p19）
   - Big-O（上界）、Big-Ω（下界）、Big-Θ（上下界）。p17 示範 3x² + 8x log x 是 Θ(x²)（c₁=1、c₂=11、n₀=1）。
   - 例：兩個長度 N 的向量做 dot product，P 個 worker 各算 N/P，再用高度 log₂P 的 tree reduction 加總。T_P = Θ(N/P + log₂P)；N ≫ log₂P 時 asymptotic speedup ≈ Θ(P)；asymptotic efficiency ≈ Θ(1)。
6. **Amdahl's law 與 Gustafson-Barsis' law**（p20–p23）
   - T₁ = W_ser + W_par，T_P ≥ W_ser + W_par/P（平行化一定有額外成本，所以是 ≥）。
   - 令 f 為 serial fraction：S_P ≤ 1 / (f + (1−f)/P)；P → ∞ 時 S_∞ ≤ 1/f。
   - 例：f = 0.1% 時最多 1000×；P = 2048 只拿到約 672×，efficiency 隨 P 增加持續下滑。
   - Gustafson：問題大小隨機器成長，serial 部分固定、parallel 部分線性成長，serial 比例越來越小，speedup 接近 linear。
7. **Arithmetic intensity（AI）**（p24–p28）
   - AI = 計算量 W（FLOPs）/ 記憶體流量 Q（bytes），單位 FLOP/byte。本課的「AI」預設指 arithmetic intensity。
   - 裝置需要的 AI = peak FLOP/s ÷ peak bandwidth。例：625 GFLOP/s ÷ 100 GB/s = 6.25 FLOP/B。
   - 常見演算法的 AI 大多落在 0.1 到幾百之間。BLAS 1／2 是 O(1)、FFT 是 O(log N)、BLAS 3（GEMM）與 dense linear algebra 是 O(N)。
   - BLAS：Level 1（1979，O(n)，SAXPY／DAXPY）、Level 2（1988，O(n²)，GEMV）、Level 3（1990，O(n³)，GEMM）。cuBLAS 是 NVIDIA 對每個架構手調（到 SASS 層級）的實作，「能打敗 cuBLAS 就贏了」。
   - 計算步驟：先算 W，再算 Q = Q_r + Q_w，初步用 perfect cache 假設（每個值只從記憶體讀一次）。
   - FLOP 指 FP32 的乘、加、減、比較；除法、開根號等走 SFU，要另外算；FP64 通常慢一倍以上，FP16／FP8 可以快很多。
   - 老師現場算：FP32 方陣 GEMM（C = AB）W = 2N³，Q = 12N²，AI = N/6 = O(N)；SGEMV 的 AI ≈ 1/2，DGEMV ≈ 1/4，都是 O(1)。
8. **Roofline model**（p29–p31）
   - 橫軸 AI、縱軸可達 FLOP/s，log-log 圖。可達效能 P = min(peak compute, β × AI)，β 是 peak memory bandwidth。
   - 斜線和水平線的交點是 ridge point（machine balance point）。左邊是 memory-bound，右邊是 compute-bound。
   - log P = log AI + log β，所以 memory-bound 那段在 log-log 圖上斜率永遠是 1。
   - 每張 roofline 只對應一個系統。理論 roofline 通常過於樂觀，要搭配 empirical 量測（用專門的 micro-benchmark kernel 量真實的 compute 和 bandwidth 上限）。
9. **Matrix multiplication（MMULT）為什麼重要**（p33–p36）
   - Dense Transformer 訓練的 FLOPs 約 99% 是矩陣乘法；訓練成本估算 6ND 本身就是 GEMM 的 FLOPs（p34）。
   - C = AB：A 是 M×P、B 是 P×N、C 是 M×N；每個輸出元素是一列和一行的 dot product，是「inner product 構成的 outer product」。
10. **Naive MMULT v0（全用 GMEM）**（p37–p42）
    - 先寫 CPU 三層迴圈 serial reference，用來驗證和當時間 baseline。
    - v0 把外面兩層迴圈對應到 2D grid，每個 thread 算一個輸出元素，`row = blockIdx.y*blockDim.y + threadIdx.y`、`col = blockIdx.x*blockDim.x + threadIdx.x`，累加放在 register `pval`，最後寫回一次。
    - 原則是 K.I.S.S.：先求正確，當作之後優化版本的 baseline。缺點是 DRAM 最慢，而且 memory access pattern 可能更糟（coalescing，之後講）。
    - 這個 kernel 的 effective AI：每個 thread 2·width FLOPs、讀 2·4·width bytes → 約 0.25 FLOP/B。
    - T4：40 SMs × 64 FP32 cores = 2560 cores，1.59 GHz，FMA ×2 → 8.14 TFLOPS；GDDR6 5.001 GHz × 32 bytes × 2（DDR）= 320 GB/s；需要 AI ≈ 25.4 FLOP/B。v0 只有約 1% 的效率。
    - T4 硬體上限：每 block 最多 1024 threads、block 最大 (1024,1024,64)、grid 最大 (2³¹, 65535, 65535)。2D grid 理論上可到 2⁴² 個元素（FP32 約 17 TB），實際受 DRAM 大小限制。
11. **CUDA 記憶體階層**（p43–p48）
    - 可見性：grid 層看得到 global 和 constant；block 內多了 shared memory；thread 層多了 register。Host 只能存取 global 和 constant。
    - 宣告方式（p45）：一般 automatic variable → register；per-thread array → local memory（實際在 global memory 裡）；`__shared__` → shared（scope 和 lifetime 都是 block）；`__device__` → global（grid，lifetime 是整個 application）；`__constant__` → constant（唯讀、較小）。
    - Shared memory：每個 SM 一份，on-chip SRAM，latency 和 throughput 都遠比 global 好；是 programmer 自己管理的 scratchpad，不是自動的 cache。
    - Shared memory 的兩種配置（p47）：在 kernel 內靜態宣告 `__shared__ float ds_in[TILE_WIDTH][TILE_WIDTH];`（大小必須是編譯期常數，可以用 template 參數繞過）；或 kernel 內 `extern __shared__ float s_filter[];`，由 host 在 launch 第三個參數給大小 `<<<grid, block, shared_mem_size, 0>>>`（第四個是 stream）。
    - p47 範例：block 裡的 thread 以 block-striding 迴圈合作把濾波器係數從 global 搬到 shared。
    - 要不要讓 host 存取決定宣告位置（p48）：要 → 宣告在函式外的 global／constant；不要 → kernel 內的 register／shared。
12. **Tiled MMULT v1（shared memory + tiling）**（p49–p74）
    - 關鍵觀察：每列 M、每行 N 在一個 block 內被重複讀 TILE_WIDTH 次，有空間和時間上的 reuse，適合放 shared memory。
    - 把 dot product 拆成多個 phase，每個 phase 分兩個 sub-phase：LOAD（每個 thread 從 DRAM 搬一個 M 元素和一個 N 元素進 shared）和 USE（用 shared 裡的 tile 算 partial dot product，迴圈 TILE_WIDTH 次）。
    - 每個 phase 需要兩次 `__syncthreads()`：LOAD 後一次（read-after-write），USE 後一次（write-after-read，避免下個 phase 覆寫還在用的 tile）。
    - Phase p 的 index：`M[Row*Width + p*TILE_WIDTH + tx]`、`N[(p*TILE_WIDTH + ty)*Width + Col]`。因為 M、N 是從 host 傳來的 linear array，kernel 裡要用 1D 攤平的 index；shared 陣列因為是靜態宣告，可以用 2D 寫法。
    - 所有 phase 做完才把 `Pvalue`（register）寫回 GMEM 一次。
    - GMEM 存取減少 TILE_WIDTH 倍，AI = TILE_WIDTH/4：16 → 4、32 → 8、128 → 32（但每個 SM 的 shared memory 容量會先卡住）。H100 FP32：66.9 TFLOPS ÷ 3.35 TB/s ≈ 20 FLOP/B。
13. **HW2 總覽與 host 計時**（p75–p76）
    - HW2 10/27（二）5:59 PM 截止。學習目標：平行效能理論題、2D Gaussian blur kernel 變體、用 shared memory 放濾波器係數、Nsight VSE debugger、Nsight Compute CLI profiling、host 計時、比較理論與實測值。
    - Host 計時用 Windows `profileapi.h` 的 `QueryPerformanceCounter()` 和 `QueryPerformanceFrequency()`（解析度 < 1 µs），AppStream 上的路徑在 p76。

## 名詞解釋

| 名詞 | 說明 |
|---|---|
| Von Neumann model | Processing unit（ALU + registers）、control unit（PC、IR）、資料與指令共用同一個記憶體位址空間，加上 I/O 和外部儲存。 |
| Flynn's taxonomy | 依 instruction stream 和 data stream 是單一還是多個，把架構分成 SISD、SIMD、MISD、MIMD（Michael Flynn，Stanford，1966）。 |
| SIMD | Single Instruction, Multiple Data。CPU 上由程式明確使用固定寬度的 vector 指令。 |
| SIMT | Single Instruction, Multiple Threads（NVIDIA 用語）。程式以單一 scalar thread 撰寫，硬體把 32 個 thread 組成 warp 在 SIMD lane 上執行。 |
| warp slot | SM sub-partition 裡容納 active warp 的位置，數量有限；每個 slot 保有完整 context，所以切換 warp 不花成本。 |
| zero-overhead warp scheduling | Warp stall 時，排程器直接改發另一個 eligible warp，不需要 context switch。 |
| warp-level primitives | Warp 內的 vote、match、reduce、shuffle、`__syncwarp` 等函式，用於 warp 內交換資料與同步。 |
| latency / throughput / bandwidth | 完成單一工作的時間／單位時間完成的工作量／記憶體或通訊的傳輸率（bytes/s）。 |
| speedup / efficiency | S_P = T₁/T_P；efficiency = S_P/P。 |
| relative / absolute speedup | Baseline 分別是平行演算法的序列版本、最好的序列演算法。 |
| strong scaling / weak scaling | 問題大小固定、只增加 P／問題大小隨 P 等比例成長。 |
| Amdahl's law | 固定問題大小下，speedup ≤ 1/(f + (1−f)/P)，上限 1/f；f 是 serial fraction。 |
| Gustafson-Barsis' law | 問題大小隨機器成長時，serial 部分占比變小，speedup 可以接近 linear。 |
| Big-O / Big-Ω / Big-Θ | 漸近上界／下界／上下界。 |
| arithmetic intensity（AI） | FLOPs ÷ 記憶體流量 bytes。本課的 AI 預設指這個，不是 artificial intelligence。 |
| perfect cache assumption | 計算 Q 時假設每個值只需要從記憶體讀一次。 |
| BLAS | Basic Linear Algebra Subroutines。Level 1 向量（AXPY）、Level 2 矩陣×向量（GEMV）、Level 3 矩陣×矩陣（GEMM）。S/D 前綴代表 single/double。 |
| cuBLAS | NVIDIA 的 CUDA BLAS 函式庫，針對每個架構手調。 |
| roofline model | 以 AI 為橫軸、可達 FLOP/s 為縱軸的 log-log 圖，上限是 min(peak compute, bandwidth × AI)（Williams, 2009）。 |
| ridge point（machine balance point） | Roofline 斜線與水平線的交點；AI 在左邊是 memory-bound，在右邊是 compute-bound。 |
| FMA | Fused multiply-add，一個指令算 a×b+c，算 2 FLOPs；NVIDIA 公告的峰值通常假設 FMA。 |
| GDDR / DDR | Double data rate，時脈上升和下降緣都傳資料，所以 bandwidth 要 ×2。 |
| MMULT v0（naive） | 每個 thread 算一個輸出元素，全部從 global memory 讀，AI ≈ 0.25。 |
| global memory（GMEM） | Device 上的 DRAM，容量大但最慢；host 可存取。 |
| shared memory（SMEM） | 每個 SM 一份的 on-chip SRAM，scope 與 lifetime 都是 thread block，由 programmer 明確搬入。 |
| local memory | 每個 thread 私有、但實際存在 global memory 的區域；per-thread array 或 register 不夠（spilling）時使用，很慢。 |
| constant memory | 唯讀、容量小、grid 範圍可見，host 可寫入。 |
| scratchpad memory | 由程式明確管理的記憶體（相對於自動管理的 cache）。 |
| tiling | 把矩陣切成 tile，一次只把需要的 tile 搬進 shared memory 重複使用，減少 GMEM 流量。 |
| `__syncthreads()` | Block 範圍的 barrier intrinsic，block 裡所有 thread 都到達才能繼續；有 thread 沒執行到就會 deadlock。 |
| RAW / WAR dependency | Read-after-write（要先寫完才能讀）／write-after-read（要讀完才能覆寫）。 |
| intrinsic function | Compiler 特別處理的函式，通常直接變成一條指令，例如 `__syncthreads()` 編成一條 barrier 指令。 |
| `QueryPerformanceCounter` / `QueryPerformanceFrequency` | Windows 高解析度計時 API，在 `profileapi.h`。 |

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

**課務、AWS、office hours**
- [00:03:03] [00:04:01] 連不上 AWS 就說一聲，重寄邀請通常就好了。看到「no streaming resources available」可以 10 分鐘後再試；開新 instance 最差要等約 20 分鐘，AWS 說這是正常的啟動時間。
- [00:07:06] [00:08:02] WorkSpaces session 有 4 小時上限，到期前一定要把資料備份到 instance 外面，不然就沒了。
- [00:08:02] 正在和 UW IT 處理把 UW Google Drive／OneDrive 掛到 Windows Explorer，希望下週能好。
- [00:08:02] [00:09:01] TA office hours 已經開始：Devika 週四 11:30 AM–1 PM（逐字稿聽不清楚，註解版 p3 補上了時間），Diya 週一 6:30–8:30 PM。週四先問、週末寫、週一還卡住再去問；週末卡住就貼 Teams channel。
- [00:09:01] [00:10:02] 有同學要求某個工具預裝（逐字稿是「Get get pre-installed」，可能是 Git），老師說可以。其他工具要大家都需要才會加，因為重建 image 很麻煩。
- [00:10:02] 選擇題要拿滿分，除了答案還要附解釋；答錯但解釋合理也能拿分。
- [00:10:02] [00:11:00] Final project 要到 lecture 6 才會講，屆時還剩約五、六週做專題（原版 p3 寫 L5，註解版 p3 已改成 L6）。Reading set 每週更新，記得去 Canvas Pages 看。

**SIMD／SIMT 與 warp**
- [00:17:00] 老師說目前多數裝置每個 sub-partition 有 32 個 FP32 core，可以一次跑完一整個 warp（和 L2 講的 T4 不同，見「還要釐清的問題」）。
- [00:19:02] SIMD 和 SIMT 的差別「只是用語」，不影響程式怎麼寫；差在 programmer 寫什麼、硬體自動做什麼。
- [00:21:01] [00:22:01] 寫 CUDA kernel 時是以單一 thread 的角度寫 scalar code，等於隱含宣告 thread 之間互相獨立；block 之間的執行順序完全沒有保證。
- [00:24:03] [00:25:04] SIMT 靠程式、編譯期和執行期三者合作；同一份 kernel 能在各種 NVIDIA 裝置上跑，但每個裝置的 register 數、記憶體大小不同，要最佳化還是得針對裝置調。
- [00:26:00] L2 示範的 vecadd 只有 5 個 thread，仍然占用一整個 32-thread warp，很浪費。Block 至少要有 32 個 thread。
- [00:27:00] NVIDIA 官方說 warp 大小 32 不屬於 programming model，隨時可能改變；老師猜未來可能變成 64 或 128，甚至可設定。[00:38:06] 至於為什麼是 32，老師說他也答不出來。
- [00:33:16] [00:34:04] 假設每個 SM 有 8 個 warp slot，24 個 warp 就要分批執行；結果仍然正確，但換 warp 進 slot 有成本。理想是 warp 數剛好配合 slot 數，之後會深入。
- [00:35:04] [00:38:06] 現場推 2×8×4 block 的 warp 對應：x 移動最快、z 最慢；z=0 那片 8×4 = 32 個 thread 剛好是 warp 0，z=1 那片是 warp 1。
- [00:40:01] [00:41:00] Warp stall 時排程器自動換到其他 eligible warp；如果所有 warp 都在等幾百 cycle 的記憶體讀取，就會出現完全沒有運算的空轉 cycle。
- [00:41:00] [00:42:02] Warp-level primitives 比較進階，MMULT 的後續優化版本會用到。

**效能理論**
- [00:42:02] 這些效能理論會用在整門課的討論裡，作業和 final project 都要用這些指標做分析。
- [00:43:03] [00:44:04] 比喻：latency 是開車去店裡買牛奶來回的時間；throughput 像高速公路，車道越多單位時間通過的車越多；車子坐滿人就像 warp 填滿 thread（carpool）。
- [00:46:01] Register 和 global memory 的 bandwidth、latency 相差兩到三個數量級：register 一個 cycle 拿得到的東西，從 global 可能要 100 到 1000 個 cycle。
- [00:47:01] [00:48:04] 「在這門課，這非常重要」：analysis-driven optimization——先有 baseline，訂目標，每次修改後都要驗證結果還是對的，不能只是變快。浮點數不必逐 bit 相同，但要清楚自己需要的精度（FP16／FP32／FP64）。
- [00:48:04] [00:49:00] 老師希望大家做 final project 時就照這個流程。
- [00:49:00] [00:50:03] Analytical 模型會忽略 bank conflict 這類真實世界的效應，要靠 empirical 量測才看得到；之後幾堂會講。
- [00:53:01] [00:54:00] 比較 speedup 一定要公平：兩邊必須解完全相同的問題，否則數字沒有意義。
- [00:55:00] Weak scaling 「可能更貼近現實」。
- [01:01:06] 這類 Big-Θ 證明課堂上不會常做，但分析演算法複雜度時會用到。
- [01:10:01] [01:11:03] Amdahl：P → ∞ 時 speedup 上限是 1/f，例如 f = 0.5 最多 2×、f = 0.1 最多 10×。
- [01:12:00] [01:14:04] 即使 serial fraction 只有 0.1%，2048 個 worker 也只有約 672×，永遠不會超過 1000×，加更多 core 的報酬遞減。
- [01:14:04] [01:15:00] Gustafson：問題變大時 serial 部分占比變小，比較接近實際情況；但仍要盡量縮小 serial fraction，並想清楚問題能不能長大。[01:16:00] 以 ML 訓練資料為例，已經快用完整個 internet。
- [01:16:00] 老師說 arithmetic intensity「可能是我們要介紹的最重要的指標」。[01:17:00] 本課的 AI 預設指 arithmetic intensity。
- [01:18:04] AI 大多落在約 0.1 到 400 之間；算出來遠超這個範圍就該回頭檢查算法。
- [01:20:02] [01:21:06] 例：625 GFLOP/s、100 GB/s 的裝置，kernel 要有 6.25 FLOP/B 才能同時用滿 compute 和 bandwidth。
- [01:22:02] [01:23:02] cuBLAS 是 NVIDIA 針對每個裝置手寫到 SASS 的版本，用 cuobjdump 看會發現每個架構都有一份 PTX 和 SM 版本；能寫出比 cuBLAS 快的東西就能「名利雙收」。
- [01:27:01] [01:28:00] FLOP 預設指 FP32 的乘、加、減、比較；除法、開根號要另外算。有些 GPU 每 32 個 FP32 單元才一個 FP64 單元，double 可能慢很多。
- [01:28:00] [01:31:05] 現場算 FP32 方陣 GEMM：W = 2N³、Q_r = 2N²×4、Q_w = N²×4、Q = 12N²，AI = N/6 = O(N)（投影片 p36 寫 N/3D，見「還要釐清的問題」）。
- [01:31:05] N/6 比只寫 O(N) 更精確，之後可以拿來和實測值比較。
- [01:35:02] [01:36:00] 算 Q 時一定要記得乘上 4（bytes/float），「不乘就會算錯」。
- [01:37:03] SGEMV 的 AI ≈ 1/2，改成 double 會變 1/4；BLAS 1／2 都是這種很小的值，MMULT 則在 dense linear algebra 那一端。
- [01:41:03] [01:42:02] Roofline 是針對特定系統畫的；kernel 和 ceiling 之間的距離就是還能加速的空間。在 memory-bound 區可以想辦法提高 AI，把自己往右移。
- [01:47:03] Memory-bound 那段在 log-log 圖上斜率永遠是 1，log β 只是垂直位移。
- [01:49:07] [01:50:02] 作業會針對真實裝置畫 roofline，數字從 spec sheet 來（也可以問 Claude 或 Copilot，或用 device query）；有些作業可能要畫你手上沒有的裝置。
- [01:50:02] [01:51:05] 實測值幾乎一定低於理論值；如果實測比理論高，大概是哪裡算錯了。
- [01:52:01] [01:53:02] 總結：Amdahl 終究會「吃掉你的午餐」（free lunch 的玩笑），serial fraction 一定要注意。

**Pop quiz**
- [01:53:02] [01:56:07] 課中臨時開了 pop quiz：3 題、3 分，約 7 分鐘作答（約 8:21 PM 發布），答錯也有分，主要是測試能不能順利發 pop quiz。
- [02:07:45] [02:08:01] 有人分數沒記錄到也不用擔心，有出席逐字稿可以對。之後會有不定期的 pop quiz，算在 participation，不算作業；只在期末成績落在邊緣時可能幫你往上推，沒來上課的人會錯過。
- [02:09:04] 老師會檢查有沒有人來不及交完，下次可能給多一點時間；會開一個 channel 收 pop quiz 的意見。

**MMULT v0**
- [02:10:04] 每個演算法都會從 CPU serial reference 和 naive parallel 版本開始：「先有能動的版本再優化」，不要提早優化。
- [02:11:02] [02:12:01] 矩陣乘法占 dense Transformer 訓練 FLOPs 的 99% 以上，6ND 本身就是 GEMM；訓練要花數週，加速 MMULT 回報很大。
- [02:17:06] [02:18:01] 一定要有 CPU reference：先用很簡單的例子確認算對，再放大尺寸計時。
- [02:19:06] [02:20:03] v0 的目標只有「能動、算對」，當之後版本的 baseline（K.I.S.S. = keep it super simple）。
- [02:24:01] 每個輸出只寫到一個位置，所以所有 thread 可以完全平行，不會互相覆寫；M、N 只讀，大家一起讀沒有問題。
- [02:25:04] [02:26:03] 累加放在 register，避免反覆寫回 global memory；kernel 裡對 M、N 的讀取和對 P 的寫入都是 DRAM 存取，算 AI 時要算進去。
- [02:28:00] 2×2 block 的例子裡，每列 M、每行 N 都被讀了兩次，是多餘的記憶體存取。
- [02:29:05] 同一個演算法的不同實作會有不同的 AI；理論上演算法本身的 AI 是實作的上限（老師說「不會說絕對」）。
- [02:30:02] [02:31:03] v0 的 AI 約 0.25 FLOP/B，和 GEMV 一樣低，而且不隨尺寸變大。
- [02:31:03] [02:33:02] T4 推算：2560 cores × 1.59 GHz × 2（FMA）= 8.14 TFLOPS；5.001 GHz × 32 bytes × 2（DDR）= 320 GB/s；需要 25.4 FLOP/B，v0 差了約 100 倍。
- [02:33:02] [02:34:00] Memory access pattern、memory conflict 等問題可能讓情況更糟，後面的優化會一一處理。
- [02:35:02] [02:36:04] 可配置的 grid 遠大於 device DRAM 放得下的資料；更大的資料要靠 host → device 的串流、非同步傳輸與計算重疊，這學期末開始講，下學期深入。

**記憶體階層**
- [02:38:03] 老師說記憶體空間示意圖（p44）有錯：右邊那個 block 應該標成另一個 block（例如 block (1,0)），每個 block 看不到別的 block 的 shared memory。註解版 p44 已把右邊那個手寫改成 Block (1, 0)。
- [02:39:03] [02:40:03] Host 只能存取 global 和 constant；99% 的情況資料是放 global，因為 constant 小而且唯讀。之後要自己把資料搬到 shared，因為離 thread 比較近、快很多。
- [02:40:03] Global 和 shared／register 之間的搬移都要 programmer 明確寫，不會自動發生。
- [02:41:02] [02:42:02] Local memory 這個名字很容易誤會：它其實在 global memory 裡。Register 用完時 compiler 會自動把東西放到 local memory，程式看不出來，但會變慢；之後會教怎麼查。
- [02:42:02] 目前最重要的三種：register、global（GMEM）、shared（SMEM）。
- [02:44:03] Global 和 constant 的 lifetime 是整個 application，可以在 block 之間共用資料，代價是存取比較慢。
- [02:45:00] [02:46:00] Shared memory 是 scratchpad：宣告、初始化、從 global 搬資料都要自己寫，不像 cache 會自動填。
- [02:47:02] 靜態宣告的 shared 陣列大小必須是編譯期常數；之後會講用 template 參數繞過。
- [02:48:01] Launch configuration 其實有第三、四個參數：shared memory 大小和 stream 編號；用 dynamic shared memory 時要把 stream 補成 0。
- [02:50:04] [02:51:05] 合作搬移的模式：每個 thread 依自己的 index 搬一個值，一個 warp 一次就能把 32 個值搬進 shared memory。之後會反覆看到這個模式。

**Tiled MMULT v1**
- [02:59:01] L3 是老師所有投影片裡最長的一份（約 76 頁）；之後應該能準時在 9:30 或更早結束，留時間討論。
- [03:00:01] [03:01:00] 一個 block 內只要有重複存取，就是用 shared memory 共用資料的機會；block 常見大小 8×8、16×16、32×32，32×32 就是 32 倍的重複。
- [03:02:01] 同時有 spatial 和 temporal redundancy 是理想狀況；如果 reuse 之間隔很久，就比較難利用。
- [03:04:04] Dot product 可以拆成任意順序的部分和，最後累加得到同樣結果，所以能分 phase 計算。
- [03:06:01] 還沒載入完就開始算，會用到無效的 shared memory 資料，答案就錯了，所以 phase 之間一定要同步。
- [03:09:02] [03:10:00] `__syncthreads()` 是 block 範圍（不只是 warp）的 barrier，編譯成一條 barrier 指令；所以同一個 block 的 thread 一定在同一個 SM 上。
- [03:10:00] [03:11:03] 所有 thread 都要執行到同一個 barrier，否則會 deadlock。
- [03:11:03] 例：`if`／`else` 依 thread index 奇偶分兩邊，兩邊各有一個 `__syncthreads()`，這是兩個不同的 barrier，會 deadlock。
- [03:12:03] [03:13:02] 載入後同步是為了 read-after-write；使用後同步是為了 write-after-read。另外還有 `__syncwarp` 等其他範圍的同步，之後再講。Barrier 是 SM 上的有限硬體資源。
- [03:16:01] 第二次同步的目的：在這一輪的 USE 做完之前，不能讓下一個 phase 覆寫 shared memory。
- [03:17:03] [03:18:04] 2×2 tile 的例子讓 global memory 存取減半；tile 越大（4×4、8×8…）減少越多。
- [03:21:03] M、N 是從 host 傳來的 linear memory，kernel 裡只能用 1D index；shared 陣列因為是靜態宣告，可以用 2D 寫法。
- [03:22:01] 投影片的 index 公式假設方陣；非方陣要調整。
- [03:25:00] 範例假設矩陣大小能被 TILE_WIDTH 整除，例如 N = 128、tile 32 → 4 個 phase。
- [03:27:01] 32×32 的 block 有 1024 個 thread 同時各搬一個值進 shared memory。
- [03:30:05] [03:31:03] AI 提高到 TILE_WIDTH/4：tile 32 → 8；tile 128 → 32，足以餵飽 T4，但 shared memory 容量和 thread 數上限通常會先卡住，之後要找其他優化方式。
- [03:31:03] [03:32:04] H100 FP32 約需 20 FLOP/B；tile 32 的 AI「其實很容易達到」。
- [03:32:04] Tiled 演算法下週會繼續講，這週不用完全消化。

**HW2 與繳交**
- [03:32:04] [03:33:02] HW2 應該已經上線：練習平行效能理論、實作 Gaussian blur kernel（延續 L2 的 blur kernel）、用 shared memory、CUDA debugger、command-line profiler、host 計時、比較理論值和實測值。老師說本堂內容加 reading 就足夠完成。
- [03:33:02] [03:34:00] 交作業只要交 source code 和 header 等必要檔案，不要交編譯產生的 lib、object 等中間檔；可以打包成 zip，但不要讓檔案從幾百 KB 膨脹到幾百 MB。
- [03:34:00] [03:35:00] Host 端計時用 `QueryPerformanceCounter`／`QueryPerformanceFrequency`，用來量 CPU serial reference，以及包含 HtoD、kernel、DtoH 的完整 round-trip 時間；和 CPU 比較時 round-trip 往往比單看 kernel 時間更有意義。

**只在投影片上、課堂沒細講的內容**
- p12 的 bandwidth／latency 代表值表（mid-2026）只有圖，課堂只帶過哪幾層重要（講義 p12）。
- p27 提到 MIPS（整數效能）和 TOPS（現在多指低精度 tensor 運算）（講義 p27）。
- p32 總結還列了降低功耗、locality、span（critical path）是設計平行演算法的考量（講義 p32）。
- p34 的數字：Llama 3.1 405B 用了 3.8×10²⁵ FLOPs；H100 Tensor Core BF16 GEMM 989 TFLOPS 對 FP32 CUDA core 67 TFLOPS（約 15×）；剩下 1% 的 softmax、LayerNorm 等若不 fuse 可能主導執行時間，所以 FlashAttention 把它們 fuse 進 GEMM（講義 p34）。
- p69–p73 的 kernel 有筆誤（自行發現，課堂沒提）：載入 N 的 index 寫成 `t*TILE_WIDTH`，應為 `p*TILE_WIDTH`；迴圈上限寫 `n/TILE_WIDTH`，參數名其實是 `Width`；第二個同步寫成 `__synchthreads()`，應為 `__syncthreads()`（講義 p69）。註解版 p69–p72 的這幾處都沒有改。
- p5 的 MIMD 括號誤寫成「Single Instruction, Multiple Data」（講義 p5）。註解版也沒改。

## 講義手寫註解（`Au26_GPU-Compute_Lecture3_w_notes.pdf`）

老師上課時在投影片上寫的紅、藍、綠、黑字和螢光筆，10/22 上傳。文字層和原版相比只有 p3 有實質修改：Devika 的 office hours 補上「Thursdays 1130-1 PM」、「HW2 procedures will be published after lecture」後面加「today」、final project 介紹從「will be in L5」改成「will be covered in L6」、「READING SET updated」改成「READING SET #3 updated」；其他頁只差在空白。其他差異都是筆跡。沒有筆跡的頁（p1–2、p4、p33–34、p43、p48–50、p56–68、p73）不列；p18（圖例 log(n)、nⁿ 旁兩個小記號）和 p40（幾條藍色底線）也不列。p69–p72 的程式筆誤（`t*TILE_WIDTH`、`n/TILE_WIDTH`、`__synchthreads()`）和 p5 的 MIMD 括號都沒有改。

**課務**
- （註解 p3）「AppStream sessions expire in 4 hrs」的「AppStream」劃掉，改寫「WorkSpaces」，對應 [00:07:06] 口頭說的 WorkSpaces 4 小時上限。
- （註解 p75）HW2 learning objective 第 6 項（host timing）畫箭頭。（註解 p76）`profileapi.h` 和兩個 learn.microsoft.com 連結畫箭頭，`QueryPerformanceCounter`、`QueryPerformanceFrequency` 前加點，也就是 HW2「Host-side Code Execution Timing」要用的東西。

**SIMD／SIMT 與 warp**
- （註解 p5）右上角畫一個 SM 切成 4 格，標「SP」，其中一格畫成小格子並寫「32 FP32」，意思是每個 SP 有 32 個 FP32 core（一般情況；T4 是 16 個，見「還要釐清的問題」第 2 點）。SIMD 那格框起來，箭頭標「GPU」。左下畫 op1、op2、op3 錯開的 pipeline 圖，下面寫「Time」，用來解釋 MISD「Computers May be Pipelined」：pipeline 填滿時，同一時間有多道指令在處理資料。
- （註解 p6）Processing Unit 旁寫「core」，整個大框左下寫「chip」，「Processing Block in SM」的 SM 框起來。
- （註解 p7）「Both models run one instruction over many ALU lanes at once」打星號，句尾補「does.」（what the hardware automatically does）。CPU SIMD 旁寫「Intel MMX →」、「4 element, 8 element」，也就是固定寬度的 vector 指令。「scalar thread is the unit of programming」和「programmer declares independence」畫箭頭，independence、masking 畫底線。
- （註解 p8）「Each Block is executed as 32-thread Warps」的 Block 上方補「Thread」（thread block）。1D 和「row-major order」畫底線。
- （註解 p9）「There are 8 * 3 = 24 Warps」後面寫「→ possible resource limitation due to the available device warp slots.」，對應 [00:33:16] 說的 warp slot 不夠時要分批。左下畫 2×8×4 block 的示意：z=0 那片 8 列 × 4 行是「W0」，後面那片 z=1 是「Warp-1」；「ZxYxX」的 Z 標「slowest」、X 標「fastest」（[00:35:04]–[00:38:06]）。
- （註解 p10）「Warp-level primitives」打星號、寫「→ CUDA prog lang.」，左邊畫一個框表示 warp 是 block 和 thread 之間多一層。

**效能理論**
- （註解 p11）latency 和 throughput 的 Units 打星號；bytes/sec 後面寫「GB/s」，memory 畫底線。
- （註解 p12）表格最上面寫「Fastest」、最下面寫「Slowest」並畫箭頭。圈出 register file（~356 TB/s、5.7×10⁻¹ ns）和 HBM3（3.35 TB/s、4.5×10² ns）兩列，對照 register 和 global memory 差了約三個數量級（[00:46:01]）。Register file、L1/shared、L2 用大括號標「on chip」；HBM3、HBM3e、DDR5 標「global」；PCIe 4.0／5.0 打星號寫「Host ↔ device」。
- （註解 p13）Analysis-Driven Optimization Process 打大星號；「Establish baseline reference」旁寫「CPU, naive kernel…」；從第 5 步畫箭頭繞回第 1 步，表示是迴圈；working、validate 畫底線。
- （註解 p14）S_P 旁寫「S₈ → cores」；Efficiency = T₁/(P·T_P) 後面寫「= 1 if T_P = T₁/P」，箭頭指向 linear speedup；「Both algorithms must solve the identical computational problem」畫箭頭。
- （註解 p15）左邊畫一個方格切成多塊（strong scaling：同一個問題切給更多 processor）和兩個空方格（weak scaling：每個 processor 一份）；weak scaling 那行打星號。例題答案：Strong scaling「M_ss = M/P」，Weak scaling「M_ws = P·M/P = M」。
- （註解 p16）O(g(n)) 旁寫「O(n²)」；Big-Θ 的 c₁g(n) 標「lower」、c₂g(n) 標「upper」。
- （註解 p17）「3x² + 8x² = 11x²」，標出 O 那段是「upper」、Ω 那段是「lower」。
- （註解 p19）「Partition vectors」前補「evenly」；右邊畫兩條向量 a、b 切成 P 段，下面畫 tree reduction。Asymptotic speedup 後面寫「~ Θ(P)」；asymptotic efficiency 劃掉 log₂P，寫「~ (N/2N) ~ Θ(1)」（N ≈ P log₂P 時）。
- （註解 p20）serial fraction 畫底線，圖上 serial work 標「W_ser」。
- （註解 p21）P → ∞ 時 (1−f)/P → 0；「f = .5、.1」→「1/(1/2) = 2、1/(1/10) = 10」（[01:10:01]–[01:11:03]）。
- （註解 p22）「program size as fixed」畫底線；serial fraction 0.1% 那條畫線拉到 2048 workers 的 672（[01:12:00]）。
- （註解 p23）Gustafson 圖的 serial work 標「fixed」；problem sizes grow、serial portion is constant 畫底線。
- （註解 p24）AI 範圍上方寫「0.1 ←→ 400」（[01:18:04]）；BLAS1,2 畫箭頭，Dense Linear Algebra 旁寫「MM」。例題「memory bandwidth」上補「Peak」，兩行規格旁寫「from spec sheet」。最下面手寫算式「AI = W/Q = 625 GFLOP/s / 100 GB/s ⇒ 6.25 FLOPs/byte」。
- （註解 p25）左邊寫「(cuBLAS)」；1979、n²、n³、matrix-vector 畫底線。GEMM 那行的「y = aAB + bC」，y 上面蓋寫「C」、最後的 C 上面蓋寫「D」，旁邊寫「A, B, D: N×N」，也就是「C = αAB + βD」。p26、p28 的表格和 p27 的手寫都是 C = αAB + βC／「A, B, C: N×N」，所以 D 大概是筆誤，重點是把左邊的 y 改成 C。
- （註解 p26）步驟 1 上方寫「PROCESS」（字跡像 PROCEST），表示下面 1、2 是算 AI 的固定步驟：先 W 再 Q；W、Q 打點，Q_r、Q_w 畫底線；perfect cache 後面補「initially」。
- （註解 p27）FLOP 後面寫「(FP32)」；SFU 那行打星號。手寫 FP32 方陣 GEMM：「C = AB, A, B, C: N×N FP32」、「W: (2N)N² = 2N³」、「Q_R = 2N²·4 bytes/float」、「Q_W = N²·4」、「Q = Q_R + Q_W = 12N²」、「AI = W/Q = 2N³/12N² = N/6 ~ O(N)」。
- （註解 p28）手寫 SGEMV：「y = αAx + βy, A: N×N, x, y: N×1, α, β: scalar fp32」；「W = (2N−1)N = Ax」、「αAx = 2N² − N + N」、「+βy = 2N」、「= 2N² + 2N」；「Q_R = (N² + 2N + 2)·4」（旁註「float bytes!」）、「Q_W = N·4」、「Q = 4N² + 12N + 8」；「AI_SGEMV = W/Q = (2N²+2N)/(4N²+12N+8) ≃ 1/2 ~ O(1)」；「DGEMV ~ 1/4」。
- （註解 p29）交點標「ridge pt = machine balance pt」，左上寫「unattainable」；斜線標「Peak memory BW」，下方「memory bound」、右方「compute bound」；橫軸標 0.1、10、100。
- （註解 p30）整頁手寫：「P(AI) = min(P_peak, β·AI)，β: memory peak BW」；「P = β·AI → AI = P_peak/β = 6.25」；「log P = log(AI) + log(β)」對應「y = mx + b」（斜率 1，log β 只是截距，[01:47:03]）；右邊「Ex: hypothetical system，P_peak = 625 GFLOPS/s，β = 100 GB/s」，下面寫「get this from spec sheet」；底下畫 log-log 軸（AI 0.1、1、10、100）和 100 GB/s 斜線、625 GFLOP/s 水平線。
- （註解 p31）measured 畫底線，箭頭指向 Theoretical GB/s 那條線。
- （註解 p32）computational work 和 communication 用大括號寫「AI?」；span／serial fraction 旁寫「Amdahl's law eat your lunch?!」（[01:52:01]–[01:53:02]）。

**MMULT v0**
- （註解 p35）c_row,col 下面寫「y, x」；c_ij 展開式下寫「P + P−1」（每個輸出元素 P 個乘法、P−1 個加法）；三個矩陣標 C、A、B。
- （註解 p36）「D: data size in bytes, 4=SP, 8=DP」上面補「2=HP」；最後一行「AI = N/3D ~ O(N)」後面寫「→ N/6」。
- （註解 p37）標題旁寫「need validation baseline!!」，往下寫「1. math correct」、「2. baseline timing」（[02:17:06]）。迴圈上限 P、`h_C[i * N + j]` 的 index 畫底線。
- （註解 p38）標題和「get the kernel working and computing correct results on GPU」打星號；「each kernel calculates」中間補「thread」；DRAM 上寫「global mem」；slowest、K.I.S.S. 畫底線；程式內迴圈用大括號指到「and computes the inner loop」。
- （註解 p39）row/col 公式用大括號連到 kernel 裡的對應行；`+= M[...] * N[...]` 和 `P[...] = pval` 標「DRAM reads」、「writes」；圖上標 x、y 軸，M 的寬標「k」，P 上畫出 block 切成的 tile 和「Block_width」。
- （註解 p41）「Effective AI for mmult_sqr_gmem kernel」旁寫「→ specific implementation」（同一演算法不同實作 AI 不同，[02:29:05]）；peak compute 和 max memory bandwidth 兩行打星號；GDDR6 的 Double Data Rate 畫箭頭指到「× 2」；「25.4 FLOPs/Byte」後面寫「→ to saturate T4 GPU FP32.」
- （註解 p42）「32*65535 = 2^21」旁寫「→ y-dim」；17 TB、F32s 畫底線。

**記憶體階層**
- （註解 p44）右邊的「Block (0, 0)」手寫改成「Block (1, 0)」，就是 [02:38:03] 口頭說的圖錯。圖上標「SMEM」、「REG」、「GMEM」，thread 下面寫「thread local」（local memory 其實在 global memory）。Grid、Block、Thread 用黃色螢光筆，Shared Memory、Registers、Global Memory、Constant Memory 用藍色螢光筆；Host 框成綠色。
- （註解 p45）「__device__ __constant__」的 `__device__` 圈起來，箭頭指到「__device__ is optional」；shared 那列畫箭頭；Lifetime 欄畫箭頭，global／constant 的 application 用大括號標。
- （註解 p46）explicit memory load/store、scratchpad 畫底線。
- （註解 p47）`__shared__ float ds_in[TILE_WIDTH][TILE_WIDTH];` 旁寫「→ TILE_WIDTH must be avail to compiler」（[02:47:02]）；launch 的 `shared_mem_size`、`0` 下面標「3」、「4」（第三、四個參數，[02:48:01]）；`s_filter[i] = d_filter[i];` 旁寫「→ explicit move GMEM → SMEM」。

**Tiled MMULT v1**
- （註解 p51）左邊寫「m₀n₀ + m₁n₁ + m₂n₂ + m₃n₃ + …」，前兩項標 p0、後兩項標 p1，表示 dot product 拆成 phase 的部分和（[03:04:04]）；右邊畫 M、N 的 tile 搬進「SM」、「SN」（shared memory 裡的 tile）。
- （註解 p52）Phase 0、Phase 1 的欄位上方寫「Load0、Use0、Load1、Use1」。
- （註解 p53）左邊的 M、N 標「GMEM」。
- （註解 p54）「SYNCHRONIZE! Why?」下面寫「potential RAW hazard」。
- （註解 p55）右上 timeline 標「barrier」；`__syncthreads()` 和「All threads must execute」畫箭頭；SM、deadlock 畫底線；if/else 各有一個 `__syncthreads()` 的範例旁寫「not same barrier = deadlock」（[03:11:03]）。
- （註解 p69）兩行 `__shared__` 宣告標「static SMEM」，旁寫「same as threadblock dims!」；setup 部分用大括號標「setup」；Row、Col 旁寫「location in output matrix being computed」。
- （註解 p70）for 迴圈標「enter phases」。
- （註解 p71）LOAD 的兩行標「GMEM → SMEM」，旁寫「→ using 1D indices for GMEM」（[03:21:03]）；第一個 `__syncthreads()` 畫箭頭。
- （註解 p72）第一個 `__syncthreads()` 標「RAW」、第二個標「WAR」，兩個都打星號；`Pvalue +=` 那行寫「use register acc」，內層迴圈標「USE iterations」；外層迴圈結尾標「// P Phases」；`P[Row*Width+Col] = Pvalue;` 旁寫「← write result 1 time to gmem」。
- （註解 p74）TILE_WIDTH、TILE_WIDTH / 4、0.25、AI = 32、20 FLOP/B 畫底線；TILE_WIDTH = 32（AI = 8）和 128（AI = 32）打星號，32 那行畫箭頭。

## 和作業 / 考試的關聯

- **HW2（10/27 二 5:59 PM PDT 截止，12 分，尚未繳交）**：題目直接對應本堂。
  - 選擇題 1–3：shared memory 變數的版本數、tiled MMULT 的 bandwidth 減少比例、DRAM burst 數 → 對應 §11 記憶體階層和 §12 tiled MMULT。
  - Performance Theory P1：替幾個 ML 運算算 FLOPs、mem bytes、AI → 照 [01:28:00]–[01:37:03] 的步驟（先 W 再 Q，記得乘 bytes）。
  - 程式部分：2D Gaussian blur、shared memory 放濾波器係數（p47 的 `extern __shared__` + block-striding 搬移就是範例）、Nsight VSE、Nsight Compute CLI、`QueryPerformanceCounter` 計時、理論 vs 實測。
  - 選擇題一定要附解釋 [00:10:02]；不要交中間檔 [03:33:02]。
  - 提醒：課程 AI policy 由使用者自行判斷；這份筆記整理的是課堂內容，HW2 的答案和程式請自己完成。
- **Pop Quiz - Lecture 3**（10/20 8:30 PM 截止，3 分）：Canvas 顯示 graded，算 participation。
- **HW3**（預定 11/3，未發布）：去年題目是 control divergence、tiled MMULT 和 NCU profiling，L4 會繼續講 tiled 演算法 [03:32:04]。
- **Final project**：L6 才會介紹（口頭和註解版 p3 都是 L6）；Project Proposal 預定 11/17。
- **Reading**：Reading Set #3（PMPP Ch5 全章，記憶體架構與 data locality）對應 L3–L5 和 HW2–3；HW2 說明也寫「L3 + reading set #3」就夠。
- 本課沒有考試（HW 50%、Final Project 50%）。

## 還要釐清的問題

1. **GEMM 的 AI 是 N/6 還是 N/12？** 老師在 [01:31:05] 用 W = 2N³ 算出 N/6；投影片 p36 把 W 近似成 N³，寫成 N/3D（FP32 時 D=4，等於 N/12）。差的是 W 有沒有乘 2。依逐字稿優先，以 N/6 為準；HW2 P1 寫 FLOPs 時建議明確寫出是否計入乘和加兩個 FLOP。**已解決**：註解版 p27 手寫 W = 2N³、Q = 12N²、AI = N/6，p36 在「N/3D ~ O(N)」後面也寫「→ N/6」，所以是 N/6。
2. **T4 每個 sub-partition 有幾個 FP32 core？** L3 [00:17:00] 說「多數現行裝置」每個 sub-partition 32 個，一次跑完一個 warp；L2 [03:14:01] 說 T4 每個 processing block 只有 16 個，一個 warp 要兩個 cycle。兩者不矛盾（L3 講的是一般情況），但寫 T4 相關作業時以 L2 的 16 個為準。註解版 p5 畫的 SM 示意圖每個 SP 寫「32 FP32」，也是一般情況；L4 p7 的表格是 T4 每個 SM 64 個 FP32 core，等於每個 SP 16 個。
3. **Final project 介紹在 L5 還是 L6？** 投影片 p3 寫 L5，逐字稿 [00:10:02] 說 lecture 6。依逐字稿優先，暫定 L6。**已解決**：註解版 p3 的文字層改成「will be covered in L6」。
4. **Devika 的週四 office hours 幾點？** 投影片 p3 只寫「Thursdays」，逐字稿 [00:08:02] 是「Thursdays, 1.30 to 1 P.m.」，顯然聽錯了。**已解決**：註解版 p3 的文字層寫「Devika – Thursdays 1130-1 PM」，也就是週四 11:30 AM–1 PM（「1130」沒標 AM／PM，依「1 PM」結束推斷是上午 11:30 開始）。
5. **例題裝置的 bandwidth 單位**：老師口頭說 100 gigabit/s [01:20:02]，投影片 p24 寫 100 GB/s；算出 6.25 FLOP/B 用的是 GB/s，以投影片為準。**已解決**：註解版 p24 手寫「625 GFLOP/s / 100 GB/s」，p30 也寫「β = 100 GB/s」，是 GB/s。
6. **[00:09:01] 預裝的工具是什麼？** 逐字稿「Get get pre-installed」，可能是 Git，待確認。
7. **Pop quiz 有沒有人沒記錄到？** 老師說會檢查，並開 channel 收意見 [02:09:04]；可留意 Teams。
