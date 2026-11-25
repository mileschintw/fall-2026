# GPU Final Project：Design Specifications（ResNet-18 inference engine）

> 原文：[spec.md](spec.md)（[Canvas assignment 11810630](https://canvas.uw.edu/courses/1917398/assignments/11810630)）。專題 spec §10 對 design spec 也有一段要求，見 [project_spec.txt](../final-project-tier-submissions/project_spec.txt)（PDF：[Au26_GPUCompute_ResNet18_FinalProject_Spec.pdf](../final-project-tier-submissions/Au26_GPUCompute_ResNet18_FinalProject_Spec.pdf)）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-12-04（五）11:59 PM PST**（Canvas `due_at` 2026-12-05T07:59:59Z；`gpu/assignments.md` 一致）。Canvas lock 12/15 11:59 PM PST（`digests/2026-11-25.md`）。L7 講義 p53 和專題 spec §1／§10 寫 **12/2 11:59 PM**，10/6 syllabus 寫 12/1 5:59 PM；依可信度規則採信 Canvas `due_at` 的 12/4 |
| 分數 | **21 pts**（Canvas）。佔 Final Project 多少比重未定，見「還不確定的地方」 |
| 繳交方式 | Canvas online upload |
| 要交的東西 | 一份 **PDF 或 Word Docx** 文件，內容是下面「要做什麼」的 Canvas 6 項，加上專題 spec §10 的項目。原文沒寫頁數上限 |

## 學習目標
- 在 T2 以後的 kernel 動工前，把每個要換掉的 kernel 的設計寫清楚：怎麼切 grid／block／tile、用哪些記憶體、預期落在 roofline 哪裡。
- 建立 baseline：CPU reference、starter GPU kernel 的時間，以及 Nsight Compute 對 starter kernel 的分析，之後每個 tier 的進步都拿這份數字比（final report 要有 tier → images/s 的 ablation table，spec §10）。
- 照老師說的「analysis-driven optimization」，從 NCU 自動給的最佳化建議開始調（spec.md 最後一段；`gpu/lectures/2026-10-27/notes.md` 第 10–11 點）。

## 要做什麼
依 Canvas 原文的順序（spec.md「Contents」）：

| # | 部分 | 原文要求 | 補充 |
|---|---|---|---|
| 1 | Summary＋每個 kernel variant 的 pseudocode | 簡短摘要，加上**每個**打算實作的 kernel variant 的 pseudocode | |
| 2 | 每個 kernel 的描述 | input data type、用到的 GPU memory 資源、特殊的架構功能、用到哪些**上課教過**的 design pattern 和技巧 | 原文舉例：naive／global-memory、shared memory、phased-tiled、privatization、coarsening、register tiling、tensor cores |
| 3 | Tuning／Optimization matrix（表格） | 列出所有打算評估的測試組態和變化 | 依情況列：grid／block launch 大小；各層 tile 大小（SMEM、register）；register 用量、shared memory 大小；其他可調參數（依演算法而定，例如係數放在哪種 GPU memory、L1／L2 cache 用法） |
| 4 | Baseline 效能表 | 每個要調的 kernel 的初始（baseline）時間 | |
| 5 | CPU reference 的時間 | 每種 kernel 的 CPU reference verification 版本的計時結果 | **Host 端**：Windows high performance timer API 或 `std::chrono`（`high_resolution_clock`），量不同 dataset 大小的 baseline。**GPU kernel**：CUDA Events 加 Nsight Compute profile 結果 |
| 6 | Starter kernel 的 NCU 分析 | Nsight Compute profiling 結果和分析，對象是 starter 的 `conv_direct.cu`、`conv_im2col.cu` | 列出 NCU 對每個 kernel 給的主要 tuning／optimization 建議，以及它估計的 speedup |

專題 spec §10 對 design spec 的要求（和 Canvas 原文重疊但不完全一樣，兩邊都要涵蓋）：對**每個要換掉的 kernel**寫

| 項目 | 內容 |
|---|---|
| Decomposition | grid、block、tile 大小 |
| Data layout 和 index math | 例如 NHWC、implicit GEMM 的 gather index（spec §6：tensor core kernel 會重用 gather index math、epilogue 和 launcher） |
| Epilogue plan | bias → optional residual add → optional ReLU，在 fp32 register 裡做完再 store（spec §2） |
| 預測的 arithmetic intensity 和 roofline 位置 | **每個 shape class** 都要（12 個 class 見 spec §2「Conv shape classes」表） |
| Memory plan | 每個 kernel 用哪些 buffer／記憶體 |
| Risks with fallbacks | 風險和退路 |
| Work breakdown | 和 proposal 比有變就更新 |

背景數字（寫第 4、6 部分時用得到）：
- 本組 T0（原封不動的 starter，FP32，batch 32）在 T4 上是 **18.6 images/s，0.83% roofline**，leaderboard 第 12 名（11/24 3:08 PM PST 那輪評分，`digests/2026-11-25.md`）。
- 已交的 proposal v2 規劃 **design spec 時做到 Tier 2**、freeze 時做到 Tier 4（[proposal_v2.html](../final-project-proposal/proposal_v2.html)）。
- 12 個 conv shape class：stem K = 147、downsample K = 64／128／256 不能被 tile 寬度整除，要做 bounds check；stage 4 每張圖只有 M = 49，要靠 batching 填滿 T4；每個完整 3×3 conv 都是 115.6 MMAC（spec §2）。
- 在 batch 64 下，explicit im2col 每個 stage-1 conv 的 A 矩陣約 462 MB，寫和讀回的時間跟 GEMM 本身差不多；NCU 會看到一個 bandwidth-bound kernel 旁邊一個 compute-bound kernel，這就是 implicit GEMM 的理由（spec §9）。

## 注意事項
- 格式：**PDF 或 Word Docx**（spec.md「Format」）。
- 第 2 部分要點出用了哪些「from class」的技巧（spec.md「Contents」第 2 段），名稱最好跟上課用語一致（naive、phased-tiled、privatization、coarsening、register tiling、tensor cores）。
- 第 6 部分 profile 的對象指定是 starter 的 `conv_direct.cu` 和 `conv_im2col.cu`，不是自己改過的版本（spec.md）。
- 老師強烈建議從 NCU 自動給的最高優先建議開始調（spec.md 最後一段，原文用 STRONGLY）。
- Profile starter：`--launch-count` 用 20（direct）或 40（explicit im2col 每層 2 個 kernel）；用 debug set、batch 8，**不要在 val set 上 profile**（`gpu/lectures/2026-11-17/notes.md` 第 16 點，[03:21:03]–[03:23:02]）。
- 計時：專題 harness 已經內建 CUDA event timer，要多加 timer 可以用講義 p50–p52 的 `Timer` class；不要用 disable-timing 的 flag（`gpu/lectures/2026-11-17/notes.md` 第 13 點，[03:06:03]）。Engine 的 `timing.json` 只量 compute（從第一個 normalize 到最後一個 top-k），不含 H2D／D2H（spec §6）。
- Grader 只 build sm_75：設計裡別用 T4 沒有的指令（`cp.async`、bf16、m16n8k16 fp16 MMA shape、wgmma、thread-block cluster），也不能用現成的 CUDA 運算函式庫，名字連出現在註解裡都會被擋（spec §8）。寫 design spec 時這些可以當成 risk 列出。
- `--tier` 是自己宣告的，staff 會拿 design spec 和 final report 驗證，可能改判（spec §8）。所以 design spec 寫的 kernel 設計要和實際提交的 tier 對得上。
- Late days：design spec 在時程表上**沒有**標「*」，可以用 late day（spec §1；每人 7 天，週末算 1 天，`gpu/lectures/2026-10-27/notes.md` [00:10:02]）。

## 和上課內容的關聯
- **Conv → GEMM（direct、im2col、explicit／implicit GEMM、arithmetic intensity、roofline、BN folding、epilogue fusion）**：L7（11/17），[`gpu/lectures/2026-11-17/notes.md`](../../lectures/2026-11-17/notes.md) 重點摘要第 3–12 點，講義 p6–p49。D1 direct conv 對應 `conv_direct.cu`，E1／E2＋E3 explicit GEMM 對應 `conv_im2col.cu`，I1／I2 implicit GEMM 對應 T2。
- **CUDA Events**：L7 第 13 點，講義 p50–p52。
- **Starter kit 的 NCU demo**（direct conv AI ≈ 67、load 16 sectors/request、「uncoalesced global accesses」提示；im2col transform 沒有 FMA）：L7 第 16 點，[03:24:01]–[03:28:03]。第 6 部分可以直接從這裡開始。
- **Host 計時（`QueryPerformanceCounter`／`QueryPerformanceFrequency`）**：L3（10/20），[`gpu/lectures/2026-10-20/notes.md`](../../lectures/2026-10-20/notes.md) 第 82 行附近（講義 p75–p76），HW2 用過。
- **Occupancy、launch configuration、tiled MMULT 邊界檢查、NCU GUI**：L4（10/27），[`gpu/lectures/2026-10-27/notes.md`](../../lectures/2026-10-27/notes.md) 第 2–5、10–11 點。Tuning matrix 的 block 大小、register／SMEM 用量和 occupancy 的關係在這裡。
- **Shared memory、bank conflict、L1TEX／L2、NCU memory chart**：L6（11/10），[`gpu/lectures/2026-11-10/notes.md`](../../lectures/2026-11-10/notes.md) 第 4–8、11 點。
- **Register tiling、thread coarsening（T3）**：L8（11/24）講義 `Au64_GPU-Compute_L8_1D-2D-regtiling-gemm.pdf`（Canvas Files），**筆記還沒整理**（錄影已在 SharePoint，`digests/2026-11-25.md`）。
- **Tensor cores（T4）**：L9（12/1），截止前三天才上。
- 已做過的 tiled GEMM 和 NCU 分析：[HW3](../hw3/README.md)、[HW4](../assignment-4-memory-access-patterns-mmul/README.md)。
- NCU metrics 清單：專題 spec §9「Measure as you go: the Nsight Compute checklist」，proposal 第 4 部分已經列過（[../final-project-proposal/README.md](../final-project-proposal/README.md)）。

## 還不確定的地方
1. **截止日**：Canvas 12/4（五）11:59 PM PST，L7 講義 p53 和專題 spec 都是 12/2（三）11:59 PM。依規則採信 Canvas，但老師還沒在課堂或 Teams 說過改到 12/4；保險起見可以照 12/2 規劃。
2. **兩份要求不一樣**：Canvas 原文重在 pseudocode、tuning matrix、baseline 和 CPU timing、starter 的 NCU 分析；專題 spec §10 重在 decomposition、index math、epilogue、每個 shape class 的 AI／roofline 預測、memory plan、risks。原文沒說哪份為準，兩邊都寫最保險。
3. **「CPU reference verification versions of each kernel type」**：starter kit 有 `CPU_EMULATION` build 選項，`check.py` 是拿 pack 裡的 reference activations 比對（spec §6）。原文沒說 CPU 版本要自己寫，還是用 CPU emulation build 量就可以；「various dataset sizes」指的是 debug／dev／val set 還是 batch size 也沒說。
4. **Host timer**：原文寫「windows high performance timer API」，但 grader 和 AWS T4 環境、本機 WSL 都可能不是 Windows；`std::chrono` 兩邊都能用。
5. **比重**：Canvas 上 21 pts；10/6 課堂說 design spec 佔專題 30%，11/10 改說 final code、presentation、report 比重相同且佔大部分；專題 spec §1 只寫「Grading weights and the late-day policy are announced separately by the instructor.」（`gpu/assignments.md`）。
6. **一組交一份還是每人各交**：原文沒寫（Canvas 作業是否為 group assignment 沒記錄）。T0 的 Tier Submissions 是 Canvas 小組提交（`gpu/assignments.md`），這份可能也一樣。
7. **頁數上限**：proposal 限 2 頁，design spec 原文沒寫。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-11-25 | 第一次整理 |

GPU 課禁止用 AI 產生作業解答
