# GPU Lecture 8 — 2026-11-24（Thread coarsening 與 register tiling：SGEMM Kernel 4 的 1-D blocktiling、Kernel 5 的 2-D blocktiling；Nsight Compute 看 MIO throttle、假的 bank conflict、occupancy；Final Project 更新）

> 來源：transcript（Teams 自動逐字稿 `transcript.vtt`，1753 cues，約 00:00:12–02:43:42，約 2 小時 44 分；錄影檔 `Weekly Live Lecture-20261124_183040-Meeting Recording.mp4`）、slides（Au64_GPU-Compute_L8_1D-2D-regtiling-gemmj_w_notes.pdf，Canvas file 156695872，58 頁，文字在 `slides.txt`；另有不含 notes 的版本 Au64_GPU-Compute_L8_1D-2D-regtiling-gemm.pdf，file 156687750。檔名的「Au64」和「gemmj」是原檔名的錯字，照抄）。投影片內容大多改寫自 S. Boehm〈How to Optimize a CUDA Matmul Kernel for cuBLAS-like Performance〉（2022）的 Kernel 4、5，數字都是 RTX A6000、4096² FP32。閱讀章節：Reading Set #6 = PMPP 4th ed. Ch10（reduction）＋ Ch11（prefix sum / scan），11/24 起，但 Canvas 頁面說它是給 L10（FlashAttention、Mamba selective scan）用的；本講的 thread coarsening 對應 PMPP Ch6 §6.3（Reading Set #4，自行對照）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：Carsoning → coarsening；Kublas → cuBLAS；Kuobs dump → cuobjdump；insight compute / N site compute / end site → Nsight Compute；SAS → SASS；gem / G gem / S gem → GEMM / SGEMM；GMAM → GMEM；in to call / into call → im2col；into row / in to row → im2row；colonel → kernel；res index / dot index → `resIdx` / `dotIdx`；Kaytlin → BK；Tse（單獨出現）→ C；Red Ross → thread rows；Eden → eight；`A&amp;B` → A & B（字幕的 HTML 跳脫）；Sof / Soh → So（語助詞）。
>
> 錄影注意：錄影 18:30:40 開始，[00:00:12] 就開始上課。[01:29]–[01:45] **pop quiz（最後一次）＋休息**，逐字稿空白。[00:12]–[00:15] 老師示範打開發表 sign-up 頁面時被要求登入，有一段零碎的對話。[02:43:42] 結束，比平常早。

## 重點摘要

1. **Final Project 更新**（[00:06]–[00:21]；講義 p3–p4）
   - **Leaderboard 上線**：24 組裡有 19 組交了 T0 smoke test（[00:07:01]；講義 p3）。有兩個網址：COMBINED `https://faculty.washington.edu/colinrei/au26-leaderboard/board.html`、BY TIER `.../board_by_tier.html`（講義 p3，投影片文字有多餘空格，這裡已去掉）。
   - **T0 的分數沒有意義**：大家都是原封不動的 starter，但老師分兩批跑（11/21 和之後），AWS 第二批不知為何比較快，所以數字有差。T0 只是確認會 build、會交（[00:08:01]–[00:09:01]）。
   - **每次提交只放一個 tier**：有 T1 和 T2 就分兩次交，各自標 tier；同一包裡不要同時放兩個 kernel，不然會搞混、可能跑不起來（[00:09:01]–[00:10:01]）。
   - 每個 tier 在 AWS 跑一次約 5–6 分鐘，全部跑完要幾小時，自動化還沒做好。**至少每週五、週日更新 leaderboard**，之後盡量更頻繁（[00:10:01]–[00:11:00]；講義 p3）。
   - 一直用同一個 Canvas 作業「Final Project Tier Submissions」交，註明 tier；一人交，全組都算（[00:11:00]、[00:17:00]）。
   - **AWS T4 新 image**：已預裝 `C:\resnet18\resnet18_pack`，不用再下載，可自己跑 checksum 確認；也裝了 Git，可以把程式放 repo 再 clone（[00:11:00]–[00:12:00]；講義 p3）。
   - **發表 sign-up 已開**：Google Sheet，要先用 UW SSO 登入才看得到（老師現場示範也被要求登入）。講義 p3 寫「by Fri 11/27 or auto」（沒選就自動分配）。很多組已經登記了（[00:12:00]–[00:14:18]）。
   - **發表每天 8 組，6:30–8:45 PM**，中間有休息；其他人可以旁聽，老師會貼連結（[00:14:18]–[00:15:03]）。
   - **Proposal 都收到了**，有大問題才會聯絡，否則都拿到分數（[00:15:03]）。
   - **Design Spec 延到 12/4（五）**，Canvas 作業當晚 9:30 開（[00:15:03]–[00:16:00]、[00:19:04]）。要求見下面第 2 點。
   - **T1 以上現在開放提交，到 12/15 5 PM**；之後程式碼凍結，以那時為止的提交評分。12/17（四）交 final report（[00:16:00]–[00:18:02]；講義 p3）。
   - 有問題貼在 Teams 的 final project thread（[00:18:02]）。

2. **Design Spec 要交什麼**（[00:18:02]–[00:20:02]；講義 p4）
   - 每個打算做的 kernel 變體寫一段摘要：資料型別、用到的 GPU 記憶體資源、架構特性、課堂教過的設計模式（naive/global、shared memory、phased tiling、privatization、coarsening、register tiling、tensor core）。
   - **Tuning / optimization matrix**：要測的組態，例如 grid/block 大小、各層 tile 大小（SMEM、register）、register 和 shared memory 用量、其他可調參數（係數放哪種記憶體、L1/L2 用法）。
   - **Baseline 計時表**：每種 kernel 的初始效能，包含 CPU reference 版本；host 端用 Windows high-performance timer 或 `std::chrono`，device 端用 CUDA Events 和 Nsight Compute。
   - **對 starter 的 `conv_direct.cu`、`conv_im2col.cu` 做 Nsight Compute profiling**：列出 NCU 自動給的主要建議和預估加速，講義寫「STRONGLY recommended」從 NCU 建議最高的項目開始改。
   - 老師口頭的說法：盡量先規劃好，附 pseudo code，說明打算怎麼做出各個 kernel 等級（[00:19:04]）。

3. **本講路線與為什麼要 register tiling**（[00:00]–[00:06]、[00:21]–[00:26]；講義 p2、p5–p6）
   - L8、L9 的內容可以拿來衝更高的 tier；L10 講 FlashAttention 和 Mamba selective scan，final project 用不到（[00:00:12]–[00:01:04]）。
   - 回顧 Boehm 的系列：K1 naive 309 GFLOP/s → K2 GMEM coalescing 1,987 → K3 SMEM caching 2,980 → **K4 1-D blocktiling 8,475** → **K5 2-D blocktiling 15,972**；cuBLAS 23,250（講義 p6、p28、p55）。絕對數字因機器而異，相對倍數比較通用（[00:23:00]）。
   - Starter kit 跟 K1 差不多：T0 約 16–18 images/s，但 roofline 算 FP32 上限超過 2,000 images/s，FP16 更高，空間很大。**每個 tier 都可以交 FP32 或 FP16**（[00:24:02]–[00:25:05]）。
   - 兩個新概念：**thread coarsening**（每個 thread 做更多工作）和 **register tiling**（在 shared memory tiling 之下再多一層、放在 register 的 tiling）。coarsening 會**刻意降低 occupancy**，是「懂了規則才能打破規則」的例子（[00:02:01]–[00:05:01]）。

4. **K3 卡在哪：每個 FMA 要 2 次 shared memory load**（[00:25]–[00:33]；講義 p7）
   - K3 內層迴圈每次要從 `As`、`Bs` 各讀一個值才能做一次 FMA。FMA 大約 2–4 cycles，shared load 至少慢 5–6 倍，所以被記憶體卡住（[00:26:00]）。
   - NCU 的 warp state statistics 顯示 **Stall MIO Throttle 平均約 24 cycles**，是 K3 的主要瓶頸（[00:31:00]–[00:32:03]）。
   - NCU 在 K3 回報 shared store bank conflict，但那是**假的**，見第 9 點。

5. **K4：1-D blocktiling（thread coarsening）**（[00:21]–[01:17]；講義 p5–p21）
   - 參數（4096²）：block tile `BM×BN = 64×64`、`BK = 8`、`TM = 8`（每個 thread 算 8 個輸出）；每個 block 512 threads（16 warps）；grid 64×64 = 4,096 blocks；`As`、`Bs` 各 512 floats，共 4 KB（[00:40:02]–[00:41:05]；講義 p9）。
   - Thread 對應：`threadCol = threadIdx.x % BN`（0–63，變化最快）、`threadRow = threadIdx.x / BN`（0–7）。每個 thread 負責 tile 裡**同一欄、連續 8 列**的一條 1×8 strip（[00:46:12]–[00:48:01]；講義 p11）。
   - **為什麼是直的 strip**：8 個輸出用同一欄 B，所以一個 B 值可以重複用 8 次（[00:48:01]–[00:49:08]）。
   - 載入階段：`innerColA = tid % BK`、`innerRowA = tid / BK`、`innerColB = tid % BN`、`innerRowB = tid / BN`；每個 thread 剛好各搬一個 A、一個 B。column index 用 `%`，讓相鄰 thread 讀相鄰位址，GMEM 才會 coalesce（[00:50:01]–[00:53:10]；講義 p12）。A 的一個 warp 讀 4 列各 8 個 float，B 的一個 warp 讀一整段連續 32 個 float（講義 p12）。
   - 指標：`A += cRow*BM*K`、`B += cCol*BN`、`C += cRow*BM*N + cCol*BN`；每輪外層迴圈 `A += BK`（往右）、`B += BK*N`（往下）（[00:54:03]–[00:58:07]；講義 p13）。
   - **三層迴圈**（[00:58:07]–[01:05:05]；講義 p15–p17）：
     - `bkIdx`：沿 K 每次走 BK，4096/8 = 512 輪；每輪載入 As/Bs → `__syncthreads()` → 移動指標。
     - `dotIdx`（0–7）：**先讀一個 `tmpB = Bs[dotIdx*BN + threadCol]`** 放 register。
     - `resIdx`（0–7）：讀 `As[(threadRow*TM + resIdx)*BK + dotIdx]`，做 FMA 累加到 `threadResults[resIdx]`。
     - 內層結束後再一次 `__syncthreads()`，避免快的 thread 先覆蓋 shared memory。
     - 迴圈結束後的 epilogue：`C = alpha*threadResults + beta*C`。
   - 結果：每 8 個 FMA 只要 1 + 8 = 9 次 shared load，**loads/FMA 從 2 降到 1.125**；GMEM loads per output 從 K/16 降到 K/32（[01:16:00]–[01:17:01]；講義 p15、p23）。
   - 投影片 p18–p21 有 thread 69（threadRow 1、threadCol 5，負責 C tile 的第 8–15 列、第 5 欄）的逐步追蹤表，老師說回家拿紙筆自己走一遍（[01:10:02]–[01:14:01]）。
   - 這個實作假設 M、N、K 都是 tile 的整數倍，沒有 bounds check。**Final project 也不要求 bounds check 和完整錯誤處理**，可以假設課程給的尺寸（[00:43:01]）。

6. **編譯器、loop 順序與 hoisting**（[01:20]–[01:23]；講義 p26）
   - 把 `dotIdx`、`resIdx` 兩層迴圈對調、不用 `tmpB`，量起來**完全一樣**：因為 BK、TM 是 template 常數，nvcc 會把迴圈完全展開，並自動把不變的 `Bs[...]` 搬出內層。
   - 但老師的重點是**不要依賴編譯器**：索引一旦不是編譯期常數，就展不開、也不會幫你搬，所以要自己把不變的值 hoist 出內層迴圈（[01:22:05]–[01:23:00]）。
   - 這也是 tile 大小做成 template 參數而不是 kernel 參數的原因之一（講義 p26）。

7. **K5：2-D blocktiling（2-D register tiling）**（[01:46]–[02:25]；講義 p31–p56）
   - **對 final project 很重要**：L7 的 explicit im2col GEMM 用的基本上就是這個 kernel；implicit GEMM 以它為起點，再加上即時算出 patch 索引，不必把 patch matrix 寫進 global memory。核心的 2-D register tile 運算迴圈都一樣（[01:46:01]–[01:48:02]）。
   - 參數：`BM = BN = 128`、`BK = 8`、`TM = TN = 8`；每個 block 256 threads（8 warps），排成 16×16；grid 32×32 = 1,024 blocks；`As`、`Bs` 各 1,024 floats，共 8 KB（[01:52:01]–[01:53:03]；講義 p35–p36）。
   - Thread 對應：`threadCol = tid % (BN/TN)`、`threadRow = tid / (BN/TN)`，各 0–15；每個 thread 負責一個 8×8 方塊（64 個輸出）（[01:55:01]–[01:56:02]；講義 p37）。
   - **每個 thread 搬 4 + 4 個 float**：tile 有 1,024 個元素、只有 256 個 thread，所以用 `strideA = 256/8 = 32`、`strideB = 256/128 = 2` 跑 4 輪載入，仍保持 coalesced（[01:57:02]–[02:00:00]；講義 p38）。
   - **五層迴圈**（[02:05:02]–[02:13:11]；講義 p41–p43）：`bkIdx`（512 輪）→ 載入 → sync → `dotIdx`（8）→ **先把 8 個 A 值填進 `regM[8]`、8 個 B 值填進 `regN[8]`** → `resIdxM × resIdxN` 兩層共 64 次 FMA，**完全只用 register**（`threadResults[m*8+n] += regM[m]*regN[n]`，outer product）→ sync。
   - **loads/FMA 降到 16/64 = 0.25**；block 層級 intensity 從 16 升到 32 FLOP/B；GMEM loads per output K/64（[01:48:02]–[01:49:06]、[02:20:00]–[02:21:01]；講義 p50–p51）。老師說這讓 kernel 從被 shared memory 卡住，變成幾乎 compute bound（[01:51:04]）。
   - 「**work 隨面積成長，traffic 隨周長成長**」：thread tile 和 block tile 是同一個形狀、兩個尺度（[02:22:08]；講義 p51）。
   - 投影片 p44–p48 有 thread 37（threadRow 2、threadCol 5，負責 tile 的第 16–23 列、第 40–47 欄）的逐步追蹤（[02:15:04]–[02:19:04]）。
   - 這個版本沒有 `beta == 0` 時跳過讀 C 的優化；前幾個 kernel 有。**Final project 的 kernel 通常用不到 beta**，可以省一次 global read（[02:14:03]–[02:15:04]）。

8. **代價：register、occupancy、`__launch_bounds__`**（[02:01]–[02:03]、[02:32]–[02:37]；講義 p39、p53–p54）
   - `__launch_bounds__(256, 1)`：第一個參數是每個 block 最多幾個 thread，第二個是每個 SM 至少幾個 block。這讓編譯器可以用到每個 thread 255 個 register 而不 spill（[02:01:00]–[02:02:02]；講義 p39）。
   - 每個 thread 光 `threadResults` 就 64 個，加上 `regM`、`regN` 各 8 個，再加索引和指標，用到接近上限。**Spill 到 local memory 其實是放在 global memory**，老師說 local memory 是他最討厭的 NVIDIA 用語（[02:03:00]）。
   - 老師現場的 NCU：K4 每個 thread 48 個 register（[01:24:10]），K5 是 128 個。用 NCU 的 occupancy calculator（CC 8.9、256 threads/block、128 regs/thread、8 KB shared memory）算出 **occupancy 只有 25%**，限制來自每個 SM 的 register 數（[02:32:00]–[02:35:06]）。
   - **但 K5 還是最快**：每個 warp 每一步就有 64 個獨立的 FMA，靠 instruction-level parallelism 讓 FMA pipeline 保持忙碌，不需要靠切換 warp（[02:35:06]–[02:36:03]；講義 p53）。NCU 上最長的 stall 變成「not selected」，表示 FMA pipe 本身已經滿了；instruction statistics 裡 FFMA 佔絕大多數（[02:36:03]–[02:37:02]）。
   - Array 要留在 register，**所有索引在展開後都必須是編譯期常數**；用執行期才知道的索引，整個 array 會被丟到 local memory。要用 `ptxas -v` 看 spill，SASS 裡出現 STL/LDL 就是 spill（講義 p54）。
   - 為什麼不做 16×16：256 個 accumulator 超過 255 register 上限（講義 p53）。

9. **Nsight Compute 實作技巧**（[00:27]–[00:32]、[02:26]–[02:41]）
   - **分辨真假 bank conflict**：Memory Workload Analysis 的表格裡，Shared Load / Shared Store 列的 bank conflict 是 0，但「其他」列有很多，這不是你的存取模式造成的，而是 L1 cache 和 shared memory 共用同一個實體單元造成的競爭，你控制不了（[00:27:00]–[00:28:03]、[00:31:00]）。
   - 確認方法：Source 頁面的 SASS view，右鍵 → columns，加上 L1 Conflicts Shared、L1 Wavefronts Shared、L1 Wavefronts Shared Ideal、L1 Wavefronts Shared Excessive，再把顯示從百分比改成原始數字、全精度。**Excessive = 0、actual = ideal，就是沒有真的 conflict**（[00:29:00]–[00:31:00]）。老師那台機器找不到原始碼檔，所以沒辦法做 source correlation，只看 SASS。
   - 遇到這種假警告，就不要列為第一優先，往下一項看（[02:40:01]）。
   - **K5 真的有 bank conflict**：B 的 8 個連續值被編譯器自動合併成 `LDS.128`（一次讀 4 個 float），但 offset 的排法造成 **8-way bank conflict**（老師口述），可以用 L6 教的 padding 或 XOR swizzling 消掉，K5 還能更快（[02:37:02]–[02:40:01]）。
   - 工作流程：先 full profile（每個 kernel 約 45–47 passes，4096² 要幾分鐘），從 Summary 頁的建議開始看，例如 K2「每個 sector 只用到 26/32 bytes」、occupancy 不理想（[02:27:03]–[02:29:03]）。
   - MIO throttle：K3 約 24 cycles → K4 約 8 cycles，降了約三倍，速度差了將近四倍（[02:31:03]）。
   - 老師自己的結果：從 K2（已經 coalesced）115 ms 降到 K5 約 10 ms，超過 11 倍（[02:27:03]）。
   - **NCU 分析是 final report 評分的重點**，工作上 NCU 也是最重要的工具（[02:26:04]–[02:27:03]）。

10. **整體路線與之後**（[01:25]–[01:28]、[02:23]–[02:25]；講義 p29、p56）
    - 到 K4 約 cuBLAS 的 1/3，K5 超過一半（講義：36.5%、68.7%）（[01:25:01]、[02:24:00]）。
    - 之後：K6 用 `float4` / `LDS.128` 向量化 load（指令少 4 倍）；K9 autotuning；K10 warp tiling（下學期才講）；再往外是 multi-GPU、multi-node（也是下學期）（[01:27:06]–[01:28:08]）。
    - **K3–K5 降低每 FLOP 的 byte 數，K6–K10 降低每 byte 的指令數並調整形狀**；K5 的 8×8 register tile 一路沿用到 K10（講義 p56）。
    - cuBLAS 很難贏：`cuobjdump` 可以看到每個裝置家族各編一份、各自 autotune，NVIDIA 工程師還會手動看 SASS 調整（[02:23:00]–[02:24:00]）。
    - **L9 講 tensor core**（[02:43:02]）。

11. **Starter kit 的 `conv_im2col` 其實是 im2row**（[02:41:06]–[02:43:02]）
    - Starter 的兩個 kernel 是 `conv_direct` 和 `conv_im2col`。雖然叫 im2col，對照 L7 的內容，實作的其實是 **im2row** 的模式（存取模式比較好，輸入資料的 layout 要跟著配合）。老師說會在 Teams 上補充。

## 名詞解釋

- **Thread coarsening**：讓每個 thread 算多個輸出，增加每個 thread 的工作量，好讓讀進來的資料在 thread 內重複使用。代價是 register 變多、occupancy 下降。
- **Register tiling（register blocking）**：在 shared memory tile 之下再切一層，放在每個 thread 的 register 裡。K4 是 1-D（1×8 strip），K5 是 2-D（8×8 square）。
- **Hierarchical tiling**：同一個 tiling 的想法在每一層記憶體各做一次：K3 在 SMEM 層，K4/K5 在 register 層，之後還有 warp 層、多 GPU、多節點。
- **`BM`, `BN`, `BK`**：block tile 的高、寬，以及每輪搬進 shared memory 的 K 方向寬度（K-slice）。**`TM`, `TN`**：每個 thread 負責的輸出列數、欄數。
- **`bkIdx` / `dotIdx` / `resIdx`（`resIdxM`, `resIdxN`）**：外層走 K-slice、中層走 slice 內的 k、內層走 thread 自己的輸出。
- **`tmpB`**（K4）、**`regM` / `regN`**（K5）：從 shared memory 讀進 register 暫存、重複使用的 A/B 值。
- **`threadResults`**：每個 thread 在 register 裡的累加器（K4 8 個、K5 64 個）。
- **Outer product**：K5 每一步 `regM`（8 個）× `regN`（8 個）產生 64 個乘積加進累加器，也就是 rank-1 update。
- **Epilogue**：主迴圈結束後把累加結果寫回 C（`C = αAB + βC`）的那一段。
- **MIO throttle stall**：warp 在等 memory input/output 佇列（shared memory 指令就排在這裡），太多 shared load 會造成這種 stall。
- **`LDS` / `LDS.128` / `STS`**：SASS 的 shared memory load、128-bit 向量 shared load、shared memory store。
- **`__launch_bounds__(maxThreadsPerBlock, minBlocksPerMultiprocessor)`**：告訴編譯器 block 大小上限和每個 SM 至少要放幾個 block，讓它決定 register 怎麼分配。
- **Register spill / local memory**：register 不夠時，變數被放到 local memory，它實際上在 global memory（有 cache），慢很多。
- **Hoisting**：把迴圈內不會變的計算或 load 搬到迴圈外。
- **ILP（instruction-level parallelism）**：同一個 warp 內有很多互不相依的指令可以連續發出，可以補償 occupancy 低的損失。
- **Autotuning**：在不違反資源限制的前提下，把 BM/BN/BK/TM/TN 等組合全部試一遍，挑出最快的；最佳值隨裝置（compute capability）和輸入大小而變。

## 老師強調的地方（附逐字稿時間戳）

- [00:01:04] L8、L9 的內容可以直接用在 final project，幫你衝到更高的 tier；L10 不需要。
- [00:02:01]–[00:03:01] Thread coarsening 會降低 occupancy，跟之前「盡量提高 occupancy」的原則相反，這是刻意打破規則的例子。
- [00:09:01] 每次提交只放一個 tier 的 kernel，不要把兩個 tier 的 kernel 放在同一包。
- [00:11:00] 一個人交，全組都拿到分數；發表也是以組為單位。
- [00:16:00] Design spec 延到 12/4（五），T1 以上現在就可以交。
- [00:18:02] 12/15 5 PM 之後關閉提交，之前的提交就是 final project 評分的依據。
- [00:26:00] 每個 FMA 要兩次 shared load，比例不好，shared load 比 FMA 慢很多。
- [00:31:00] NCU 說有 bank conflict，但 Shared Excessive 欄是 0 的話，那不是你的程式造成的。
- [00:43:01] Final project 不要求 bounds check 和完整的錯誤處理，「not talking about production code here」。
- [01:14:01] thread 69 的追蹤表要自己拿紙筆走一遍。
- [01:22:05]–[01:23:00] 不要依賴編譯器幫你搬出不變的值，要自己明確寫出來，因為索引一旦不是常數，編譯器就做不到。
- [01:26:03] 老師口述的 tier 對應（他說「I believe」）：SMEM tiling 是 T1、1-D blocktiling 是 T2、2-D blocktiling 是 T3，vectorizing 和 tensor core 是 T4、T5。跟 spec 不完全一樣，見「還要釐清」。
- [01:46:01]–[01:48:02] K5 的 2-D register tile 是 L7 explicit/implicit im2col GEMM kernel 的基礎，**理解它才能理解 L7 那些 kernel**。
- [02:03:00] Local memory 其實在 global memory：「Again, my most hated term in NVIDIA terminology.」
- [02:10:05] 把表格的數字代進程式碼自己算一遍索引，「It's a really good exercise.」
- [02:14:03] 每輪結尾那個 `__syncthreads()` 不要忘記：「That's a common source of bugs.」
- [02:15:04] Final project 的 kernel 通常用不到 beta，`beta == 0` 時跳過讀 C 可以省很多。
- [02:25:01] 50 倍的加速對 ResNet 的 dev/val 測試是「game changer」，也會直接反映在 images/s。
- [02:26:04] **Final report 評分很看重 Nsight Compute 的效能分析**。
- [02:35:06]–[02:36:03] K5 occupancy 只有 25% 卻最快：warp 一直有計算可做、不用切換，才是理想狀況。
- [02:39:05] K5 的 8-way bank conflict 可以用 padding 或 XOR swizzling 解決，所以 K5 還不是最佳。
- [02:40:01] NCU 的 bank conflict 如果出現在「其他」那一列，不用優先處理。
- [02:42:05]–[02:43:02] Starter kit 的 `conv_im2col` 實作的其實是 im2row。
- [02:43:02] 記得報名發表時段，注意接下來的截止日；只剩兩堂課，下一堂講 tensor core。

## 和作業 / 考試的關聯

- **沒有考試**，成績是 HW 50%、Final Project 50%（`gpu/assignments.md`）。這堂的 pop quiz 是**最後一次**，全部是加分，也算出席表現（[00:06:00]）；Canvas「Popquiz Lecture 8 11/24」8:05–8:15 PM 開放（[01:29:03]），11/25 晨報已確認 graded。
- **Final Project Design Spec：12/4（五）11:59 PM PST**（Canvas due_at 2026-12-05T07:59:59Z，21 pts）。老師口頭說 12/4，跟 Canvas 一致。要交的內容見重點摘要第 2 點，其中「對 `conv_direct.cu`、`conv_im2col.cu` 做 NCU profiling、列出 NCU 建議和預估加速」需要先在 GPU 上跑過，最花時間，建議先做。
- **Tier 提交**：T1 以上 11/24 起開放，到 **12/15（二）5:00 PM PST**（Canvas「Final Project Tier Submissions」，id 11909772）。這堂的 K4/K5 就是 spec 的 T3（register tiling，Boehm kernel 4–5，見 [gpu/hw/final-project-tier-submissions/README.md](../../hw/final-project-tier-submissions/README.md)）。spec 原文說一般的組能做到 T3 加上好的 NCU 證據。
- **發表 sign-up**：講義 p3 寫 11/27（五）前，沒選就自動分配；本組是否已登記不在 repo 裡，要確認。
- **遲交 HW 最後期限 11/27（五）11:59 PM**（L7 口述，這堂沒有再提）。
- **Final Report 12/17（四）**；發表 12/15–12/17。
- 下堂 L9（12/1）講 tensor core，對應 spec 的 T4。

## 還要釐清的問題

1. **發表 sign-up 的截止日**：`gpu/assignments.md` 根據 L7 講義 p53 寫 11/24 5:59 PM，這次 L8 講義 p3 寫「by Fri 11/27 or auto」。老師口頭沒有說日期，只說已經開了。以較新的 L8 講義為準應該是 11/27；`gpu/assignments.md` 那一列要不要改，留給晨報或使用者決定（這次任務只寫筆記，沒有改 assignments.md）。sign-up 是 Google Sheet，不在 Canvas，所以晨報不會自動偵測到。
2. **發表時段**：老師說每天 8 組、6:30–8:45 PM（[00:14:18]），`gpu/assignments.md` 寫 6–9 PM（spec 的說法）。依可信度規則採用老師口述的 6:30–8:45。
3. **Tier 對應**：老師口述（[01:26:03]，「I believe」）是 T1 SMEM、T2 1-D blocktiling、T3 2-D blocktiling、T4/T5 vectorizing 和 tensor core；spec（tier-submissions README）是 T1 batched GEMM + SMEM tiled SGEMM、T2 implicit GEMM、T3 register tiling（K4–5 + `float4`）、T4 tensor core、T5 fusion and tuning。兩者對 T2 和 T5 的定義不同。老師自己也不確定，提交前應以 spec 或在 Teams 上問清楚。
4. **K4 在老師 GPU 上能不能放 3 個 block**：老師說 K4 每個 thread 48 個 register、「still handle up to three blocks per SM」（[01:24:10]–[01:25:01]）。但 48 × 512 × 3 = 73,728，超過每個 SM 65,536 個 register；講義 p27 也寫要 ≤ 42 regs/thread 才放得下 3 個。照算術應該只能放 2 個 block。
5. **K5 的 occupancy 和 bank conflict 數字**：講義 p53 說 A6000 上 33%（且註明 128 regs 只是示意），老師在 CC 8.9 的機器上用 occupancy calculator 算出 25%（[02:33:01]）。兩者機器不同，不算矛盾，但要以自己 GPU 和 T4（sm_75）的 NCU 結果為準。bank conflict 部分，老師口述是 8-way（[02:39:05]），講義 p52 說純量 load 會是 4-way、`LDS.128` 按 8 lanes 一個 phase 計算，情況比純量分析好，但仍有 conflict。依可信度規則採口述的 8-way，但兩者分析的對象可能不同。
6. **發表 sign-up 頁面的登入問題**：老師示範 sign-up 時被要求登入、連結一度打不開（[00:13:05]–[00:14:18]），最後成功與否逐字稿聽不清楚。如果打不開，照老師說的先從 MyUW 用 SSO 登入再開連結。
7. **Leaderboard 更新頻率**：目前只保證週五、週日（[00:11:00]），晨報的 `scripts/leaderboard.py` 抓取時機可能要配合。
