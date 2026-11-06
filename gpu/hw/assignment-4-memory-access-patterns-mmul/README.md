# GPU HW4：Memory access patterns & MMULT coalesced corner turning kernel

> 原文：[spec.md](spec.md)（[Canvas assignment 11810623](https://canvas.uw.edu/courses/1917398/assignments/11810623)；PDF 原檔 [spec.pdf](spec.pdf)，Canvas file 155723325「Homework #4 (HW4) - Au26 - GPUCompute.pdf」，updated_at 2026-11-04T05:40:29Z）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-11-13（五）11:59 PM PST**（Canvas `due_at` 2026-11-14T07:59:59Z、PDF p1「DUE: 13 November 2026, 11:59 PM」、`assignments.md` 一致）；lock 12/13。原本依 syllabus 預估 11/10（週規劃 `digests/2026-11-01-weekly.md`），以 Canvas 為準 |
| 分數 | 15 分（`assignments.md`）＋ **Extra Credit 4 分**（GPU 上的 matrix transpose kernel）；原文沒寫各部分配分 |
| 繳交方式 | Canvas（原文只寫「SUBMIT」，沒寫 submission type） |
| 要交的東西 | 1. Questions 1–10 的答案，**要附過程和理由**<br>2. CUDA host application 原始碼：**只交 `.cu`、`.cpp`、`.h`**，不要交 project／solution 檔和 build 產物<br>3. CUDA kernel functions（可以和 host code 放同一個 `.cu`）<br>4. NCU profiling 報告，加一份**獨立的書面分析**，涵蓋 Memory Access Pattern Profiler Analysis 和 Coalesced Corner Turning 兩部分；Profiler Analysis 要附用到的 tile／block 大小（SUBMIT 4a 說的「question #4」） |

## 學習目標
（PDF p1「Learning Objectives」）
- 加強理解 control divergence、coalesced memory access pattern 和其他基本 CUDA 效能觀念
- 多練習用 Nsight Compute（NCU）做 profiling 和效能分析
- 在 CUDA kernel 實作 MMULT 的 coalesced corner turning pattern，並用 profile 驗證記憶體存取模式有改善
- EXTRA CREDIT（4 分）：實作 matrix transpose kernel，給 corner turning kernel 用

## 要做什麼
分兩部分：Questions（選擇題）、Programming and Analysis Exercises（Profiler 分析、Corner Turning kernel）。

### Part 1：Questions（PDF p1–p4）
書面或打字作答，**必須寫出過程或說明選擇理由才給分**。全部是四選一。

| 題 | 在問什麼 | 條件 | 選項 |
|---|---|---|---|
| 1 | 每個 thread block 裡，載入 **M** tile 時因為邊界檢查而 control divergence 的 warp **最多**有幾個（整個 kernel 執行期間） | tiled MMULT，只在右邊和下邊處理邊界；32×32 tile；1000×1000 方陣；原文要你複習「L1 slides 31–35」 | 32／24／16／8 |
| 2 | `PictureKernel()` 執行時會產生幾個 warp | 600×800 影像（m = 600 列、n = 800 行）；block 16×16 | 37*16／38*8*50／38*50／38*50*2 |
| 3 | 承 2，幾個 warp 有 control divergence | 同 2 | 37+50*8／0／38*16／50 |
| 4 | 承 2，影像改成 800×600（x 方向 600、y 方向 800），幾個 warp diverge | block 16×16 | 50*8／37+50*8／38*16／0 |
| 5 | 承 2，影像改成 799×600（x 方向 600、y 方向 799），幾個 warp diverge | block 16×16 | (37+50)*8／50*8／37+50*8／0 |
| 6 | naive `MatrixMulKernel` 的邊界檢查讓幾個 warp diverge | block 16×16；1000×1000 矩陣 | 1,000／508／1,008／500 |
| 7 | 哪種 block 大小讓每個 SM 的 thread 最多 | SM 最多 1,536 threads、8 個 block | 64／512／128／1,024 threads per block |
| 8 | 每個 thread 算向量加法的**兩個**輸出，`i` 怎麼初始化，第一個元素的存取才正確**而且 coalesced** | 敘述 `if(i<n) C[i] = A[i] + B[i];` | (A)–(D) 四種 `blockIdx`／`blockDim`／`threadIdx` 組合，見原文 p3 |
| 9 | 承 8，處理第二個元素的正確敘述 | | (A) `i+1`、`i<n`　(B) `i+1`、`i+1<n`　(C) `i+threadIdx.x`　(D) `i+blockDim.x` |
| 10 | 依 **Lecture 5 slide 35** 的 coalesced 判斷準則，naive MMULT 的 `M[Row*Width+k]`、`N[k*Width+Col]`、`P[Row*Width+Col]` 哪些是 coalesced | 同 6 的 kernel | (A)–(D) 四種組合，見原文 p4 |

`PictureKernel` 和 `MatrixMulKernel` 的完整程式碼在原文 p1–p4。

### Part 2：Programming and Analysis Exercises（PDF p4–p6）
開頭提醒：用 NCU profile 時一律用 **RELEASE（x64）build**，否則結果沒有代表性。

#### 2.1 Memory Access Patterns — Profiler Analysis（PDF p4–p5）
| 步驟 | 內容 |
|---|---|
| 1 | 用小矩陣 **256×256** |
| 2 | 用 NCU profile **MMULTv0**（全用 GMEM，naive）的 memory workload |
| 3 | 同上，profile **MMULTv1**（tiled/phased，SMEM） |
| 4 | 每個 kernel 都試三種 2D TILE_WIDTH（= thread block 維度）：**8×8、16×16、32×32** |
| 5 | 看 NCU 報告的 **Memory Workload Analysis**：Memory Chart 和 Memory Tables。分析 Shared Memory、L1/TEX、L2、Global Memory 各層之間的 transaction 大小和模式：Bytes、Sectors、Sectors/Req、wavefronts；也看 L1 和 L2 的 hit/miss |
| 6 | 說明 thread-block 大小和 warp 記憶體存取模式、coalesced access 的使用和效率、shared memory 的關係 |
| 6a | 依 launch configuration 和輸入資料大小，算每個 kernel thread 從各記憶體層讀了多少 bytes |
| 6b | 報告裡如果有不一致或意外的數字，指出來，並討論 **L5 slide #28 的「complicating factors」** 是不是原因，為什麼 |

#### 2.2 Coalesced Corner Turning Pattern：MMULTv1b kernel（PDF p5–p6）
擴充基本的 tiled/phased SMEM MMULT kernel，支援 corner turning 演算法（L5 slide 35 和原文 p5 的圖）。corner turning（轉置）的存取方式讓 GMEM 裡的 M 和 N 兩個來源矩陣都能 coalesced 存取。

- 可以用**非通用版**的 MMULT：方陣，邊長是 TILE 大小的整數倍。
- 矩陣 **M 在 device memory 裡必須是 column-major**（不是 row-major），對 M 的存取才會是正確的 coalesced 模式。

| 步驟 | 內容 |
|---|---|
| 1 | 準備 column-major 的 M：可以在 host 端轉置後再傳到 device |
| 1a | 原文建議改做下面的 Extra Credit，在 device 上轉置 |
| 2 | **EXTRA CREDIT（+4 分）**：寫一個在 GPU 上平行做 matrix transpose 的 CUDA kernel |
| 2a | GMEM 資料的 lifetime 是整個 application，所以先呼叫 Transpose kernel，再直接把轉置好的矩陣給 cornerTurning kernel 用，中間不用在 host 和 device 之間搬資料 |
| 3 | USE phase 從 SMEM tile 讀每個 thread 的資料時，要用「轉置後」的 index，inner product 才會算對 |
| 3a | 另一種做法：放進 SMEM 時就轉回 row-major |
| 4 | 用 host 端 Windows profiling API（`profileapi.h`）加 high-performance timer，量 corner-turning 版 MMULT kernel 的完整 round-trip 執行時間（原文這裡稱它 **MMULTv2b**）；API 用法參考 HW2 和 L3 |
| 5 | host 端驗證：同一組 M、N 在下列情況得到相同（正確）的結果：<br>a. CPU sequential reference `MMULT_CPU`<br>b. GPU 非 corner-turning 版 MMULTv0／v1（all-global、tiled/SMEM）<br>c. GPU corner-turning 版（用轉置的 M，MMULTv1b） |

## 注意事項
- Questions 都要附過程或理由，否則不給分（spec.md p1「Questions」；p6「SUBMIT」1）。
- NCU profiling 一律用 **Release（x64）build**（spec.md p4「Programming and Analysis Exercises」NOTE）。HW3 原文另外要求拿掉所有 `printf`；L4 也強調要開 line info（`gpu/lectures/2026-10-27/notes.md` [02:58:00]、[02:59:00]）。
- NCU 要用**系統管理員身分**執行，否則讀不到 GPU counter（`gpu/lectures/2026-10-27/notes.md` [00:59:05]、[01:00:04]）。
- Profile 時不要同時跑其他程式（`gpu/lectures/2026-10-27/notes.md` [02:54:14]）；NCU 第一次 launch 是 warm-up，正式分析跳過，output 檔名加 `%i` 避免覆蓋（同檔 [03:02:03]、[03:03:01]）。
- Corner turning 版可以只支援方陣、邊長是 TILE 大小的整數倍（spec.md p5「Coalesced Corner Turning Pattern」）。
- M 在 device 上必須是 column-major（spec.md p5）；SMEM USE phase 要用轉置後的 index，或放進 SMEM 時轉回 row-major（spec.md p6 步驟 3）。
- Tiled kernel 的 `__syncthreads()` 要放在 if 外面，否則會 deadlock（`gpu/lectures/2026-10-27/notes.md` [01:41:00]）。
- 原始碼只交 `.cu`、`.cpp`、`.h`，不要交 project／solution 和 build 產物（spec.md p6「SUBMIT」2a）。
- 分析要寫成獨立的 write-up，和 NCU 報告一起交，並列出 Profiler Analysis 用的 tile／block 大小（spec.md p6「SUBMIT」4、4a）。
- 遲交：每人 **7 個 late days**（10/27 起生效），週末（六＋日）算 1 天，沒用完的每天 +0.5 分 extra credit（`gpu/lectures/2026-10-27/notes.md`「重點摘要」1，[00:09:02]–[00:11:04]）。原本 syllabus 的扣分：遲 1 天 -1，之後每 24h 再 -1（`gpu/assignments.md`）。
- 截止是 PST（UTC−8，11/1 已結束夏令時間）。HW3 同週 11/6 到期，HW4 的 2.1 會用到 HW3 寫好的 MMULTv0／v1。

## 和上課內容的關聯
- **Q1、Q6（MMULT 邊界檢查的 divergence）**：L4 p42–p48 的 M tile Type 1／Type 2 分析（`gpu/lectures/2026-10-27/notes.md`「重點摘要」9，[02:35:01]–[02:45:00]；[02:41:05] 說明只有跨過邊界的 warp 會 diverge）。HW3 Part 2 用同樣方法分析 N tile（[../hw3/README.md](../hw3/README.md)）。
- **Q2–Q5（2D grid 的 warp 數和 divergence）**：L4 p34–p37 warp 線性化（row-major 排 thread）、p38–p41 control divergence（`gpu/lectures/2026-10-27/notes.md`「重點摘要」7–8）。
- **Q7（SM 的 thread／block 上限）**：L4 p5–p11 occupancy（同檔「重點摘要」2–4，[00:57:01]–[01:13:01]）；HW3 Question I 是同類題。
- **Q8–Q10、2.1、2.2（coalescing、記憶體階層、corner turning）**：L5（11/3），筆記 [`gpu/lectures/2026-11-03/notes.md`](../../lectures/2026-11-03/notes.md)。投影片 `Au26_GPU-Compute_Lecture5.pdf`（Canvas file 155723617）和課堂筆記版 `Au26_GPU-Compute_Lecture5_w_notes.pptx`（file 155737575），錄影在 SharePoint `General/Recordings/Weekly Live Lecture-20261103_183100-Meeting Recording.mp4`（`digests/2026-11-04.md`）。
  - **原文的 slide 編號和 PDF 頁碼對不上**（`slides.txt`）：投影片角落印的編號 = PDF 頁碼 + 2（p26 印「28」、p45 印「50」…），p27–p35 是舊 deck 的頁，沒有印編號。
    - 「slide #28」（complicating factors，2.1 步驟 6b）：印著「28」的是 **PDF p26「Caches and stores: what happens beyond L1」**（L1 每個 SM 各一份、不 coherent、store 直接送 L2；L2 write-back、partial sector；「caches are not a substitute for coalescing」）。PDF p28 是「Un-coalesced Accesses」（跨 burst section 邊界），也可能是老師指的頁。兩頁都看。
    - 「slide 35」（Q10 的 coalesced 判斷準則）：準則本身在 **PDF p29「How to judge if an access is coalesced?」**（`A[(與 threadIdx.x 無關的項) + threadIdx.x]`），用的正是 Q10 的 naive kernel；p30–p34 逐格推 A／B 的存取。PDF p35 是 Transpose Pattern。
    - 「slide 35」（2.2 corner turning）：**PDF p35「Transpose Pattern for Coalesced Access」**，對得上。
  - 課堂補充（原文沒寫）：corner-turning kernel 要和之前的 SMEM tiled kernel **一起用 NCU profile 比較**，應該看到效能提升（notes [01:42:03]）；一定要用 demo 的方法 profile，證明看到預期的行為並解釋原因（[03:10:01]）；Extra Credit 的 transpose kernel 也要驗證正確性並簡單 profile，它的 AI 是 0，全是記憶體存取，所以本身也要注意 coalescing（[03:10:01]–[03:11:02]；投影片 p49「Be sure to verify correctness and profile performance!」）。
  - NCU 指標（投影片 p45）：`l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum`、`l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum`（相除得 sectors/request，32×4 B 理想值 4、完全分散 32）、`dram__bytes_read.sum`、`dram__throughput.avg.pct_of_peak_sustained_elapsed`、`lts__t_sector_hit_rate.pct`。課堂 demo 的預測→驗證範例（4×4、32×32 矩陣的 requests／sectors 推算）在 notes [02:35:00]–[03:02:03]，2.1 的 6a 可以照同樣方法推。
- **MMULTv0／v1**：L3 p37–p42（naive）、p49–p74（tiled）（`gpu/lectures/2026-10-20/notes.md`「重點摘要」10、12）；HW3 3.2 已實作通用版。
- **NCU GUI**：L4 p49–p51 和 demo（`gpu/lectures/2026-10-27/notes.md`「重點摘要」10–11）。Memory Workload Analysis 是這次新用到的 section。
- **Windows profiling API（`profileapi.h`）**：HW2 步驟和 L3（[../hw2/README.md](../hw2/README.md)；AWS WorkSpace 上的 header 路徑也記在那裡）。

## 還不確定的地方
- **Q1 的「L1 slides 31–35」**：L1 是課程導論，M tile 邊界檢查的 divergence 分析在 L4 p42–p48；推測是筆誤，應該是 L4（或 L5 的某幾頁）。
- **Q1「maximal number of warps」的範圍**：原文說 within EACH thread block、throughout the kernel execution，但不同位置的 block 結果不同；「最多」應是取最差的那種 block。
- **Q5 的選項 a 和 c 的差別**：`(37+50)*8` 和 `37+50*8`，要注意括號。
- **kernel 名稱不一致**：2.2 標題和步驟 5c 叫 **MMULTv1b**，步驟 4 叫 **MMULTv2b**，應該是同一個 corner-turning kernel。
- **SUBMIT 4a 的「question #4」**：指的應該是 2.1 的步驟 4（TILE_WIDTH 8／16／32），不是 Questions 第 4 題。
- **2.2 要不要也用 NCU profile**：要。學習目標和 SUBMIT 4 都要求，老師課堂上也說要和 SMEM kernel 一起 profile 比較（L5 notes [01:42:03]、[03:10:01]）。還沒說清楚的是矩陣大小和 TILE_WIDTH（2.1 用 256×256，沿用最自然）。
- **原文引用的 slide 編號**：見上面「和上課內容的關聯」的對照；最好在 Teams 問一下 slide 28／35 指的是印的編號還是 PDF 頁碼。
- **round-trip 時間的範圍**：「full round-trip execution」包不包含 host↔device 傳輸、轉置 kernel（或 host 端轉置），原文沒說清楚。
- **驗證的誤差容許值**：原文說「same (correct) results」，沒給 tolerance；HW3 用 abs error fraction。
- **書面分析的格式和頁數**：HW3 指定一頁 PDF 或 Word，HW4 只說「a separate write-up」。
- **用哪個 GPU**：課程環境是 AWS WorkSpaces 的 T4（`sm_75`，HW2 原文）；L1/L2 cache 大小會影響 2.1 的 hit/miss 數字。
- **繳交方式和配分**：原文沒寫 Canvas submission type，也沒寫 Questions 和程式部分各佔幾分。
- **Late days 和原本扣分規則怎麼併用**：老師沒說（`gpu/lectures/2026-10-27/notes.md`「還要釐清的問題」3）。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-11-04 | 第一次整理 |
| 2026-11-06 | 補 L5 筆記連結、slide 編號↔PDF 頁碼對照、課堂對 profiling 和 Extra Credit 的補充要求；Canvas 原文沒有重抓（Canvas 登入過期） |

GPU 課禁止用 AI 產生作業解答
