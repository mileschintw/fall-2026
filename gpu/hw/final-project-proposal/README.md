# GPU Final Project：Proposal（ResNet-18 inference engine）

> 原文：[spec.md](spec.md)（[Canvas assignment 11810636](https://canvas.uw.edu/courses/1917398/assignments/11810636)）。專題本身的正式 spec 是 SharePoint `Final Project - ResNet18/Au26_GPUCompute_ResNet18_FinalProject_Spec.pdf`（11/16 8:53 PM PST 上傳，11/19 10:43 PM PST 更新），最新版已存在 [../final-project-tier-submissions/](../final-project-tier-submissions/Au26_GPUCompute_ResNet18_FinalProject_Spec.pdf)（文字版 [project_spec.txt](../final-project-tier-submissions/project_spec.txt)）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-11-20（五）11:59 PM PST**（Canvas `due_at` 2026-11-21T07:59:59Z；`gpu/assignments.md` 一致；ICS 全天項目也是 11/20）。Canvas lock 12/4 11:59 PM PST（`digests/2026-11-18.md`）。之前的說法 11/17（syllabus 11:59 PM／舊投影片 5:59 PM）、11/18（11/10 課堂口述）都作廢，以 Canvas `due_at` 為準 |
| 分數 | 10 pts（Canvas）；Final Project 的 10%（11/10 課堂說法見「還不確定的地方」），Final Project 佔學期 50% |
| 繳交方式 | Canvas online upload，**PDF** |
| 要交的東西 | 一份 PDF，**最多 2 頁**，包含下面 5 個部分 |

另一個今天的期限：**11/18（三）11:59 PM PT 要重新加入 Project Team**。Canvas 上所有組別已重置，之前加過也要重加：Canvas → People → Project Teams → 加入既有的組（不要自己建新組，每組最多 3 人），沒加入的會被隨機分組（TA Devika Nair 的 Canvas 公告，`digests/2026-11-18.md`）。Proposal 的第 1 部分要寫的組員就是這個名單。

## 學習目標
- 在動手寫 kernel 前先規劃整個專題：要衝到哪個 tier、誰負責哪個 kernel、用哪些 NCU metrics 判斷效能、讀哪些參考資料。
- 把「analysis-driven optimization」流程（先 profile、找瓶頸、再改 kernel）落實到專題上；老師說每個 tier 都要做 NCU profiling，數據會進 final report（`gpu/lectures/2026-10-27/notes.md` [00:16:01]；`gpu/lectures/2026-11-10/notes.md` [00:39:03]）。

## 要做什麼
專題背景（`gpu/lectures/2026-11-10/notes.md` 重點摘要第 2 點）：只做 ResNet-18 的 forward pass。給一份正確但故意很慢的 starter engine（host executor＋每層 naive kernel），工作是一層一層換成更快的 kernel。資料是 ImageNet 的 10 類子集（約 3,925 張），權重有 FP32 和 FP16（batch norm 已 fold 進去）。`check.py` 逐層比對 reference activations 當正確性 gate，`submit.py` 打包成 ZIP 交到 Canvas「Final Project Tier Submissions」，grader 一律在 AWS T4 上量、更新 leaderboard（專題 spec §8）。Starter kit：Canvas 檔案 `resnet18_pack.zip`、`resnet18_student_kit_v06.zip`（11/16 晚上發布；11/19 更新為 v07）。

Proposal 依原文的順序，必須有這些部分（spec.md「Structure」）：

| # | 部分 | 原文要求 | 補充 |
|---|---|---|---|
| 1 | Project Team Members | 應該是 **3 人**，而且已在 Canvas People／Groups 登記 | 11/10 課堂說剛好 3 人一組，不接受其他人數（[00:34]）；組別 11/18 重置後要重加 |
| 2 | Initial planned tiers | 這組打算做到哪個 tier | 之後可以隨專題進度調整（原文） |
| 3 | Work breakdown | 每個組員負責哪個 kernel 和其他專題工作 | |
| 4 | Nsight Compute profiling metrics | 列出**具體**要看的 NCU metrics，以及每個 metric 和這個演算法效能的關係 | 不是只列名字，要說為什麼相關 |
| 5 | Primary references | 實作會用或會讀的主要參考資料 | 原文舉例：open source 文獻、教科書、其他程式碼或 samples |

Tier 的大致樣子（11/10 口述，正式清單以專題 spec PDF 為準）：

| Tier | 內容 |
|---|---|
| T0 | baseline smoke test：build、跑 `check.py`、profile、`submit.py`；**11/22 11:59 PM PST 前**把 ZIP 交到 Canvas 的 Tier Submissions 作業，grader 評完會出現在 leaderboard（spec §8，見 [../final-project-tier-submissions/README.md](../final-project-tier-submissions/README.md)） |
| T1 | batched GEMM path，本質上是 SMEM tiled matrix multiply |
| 中間幾個 | conv → GEMM（L7 的 im2col、implicit／explicit GEMM）等，大約一週一個 tier |
| tensor core tier | 這時才用 FP16 |
| 最後一個 | bonus，非必要 |

## 注意事項
- 格式 **PDF**，**最多 2 頁**（spec.md「Format」）。
- 組員要已經登記在 Canvas People／Groups（spec.md「Project Team Members」）；11/18 11:59 PM PT 前重加（`digests/2026-11-18.md`，Devika Nair 公告）。
- 規劃的 tier 之後可以調整（spec.md「Initial Planned tiers」）。
- 專題 kernel **不能用現成的 CUDA 運算函式庫**（NVIDIA library、Thrust、Boost 等），checker 查到就過不了 gate；寫 references 和分工時別把這類 library 當成實作方式（`gpu/lectures/2026-11-10/notes.md` [00:07]–[00:50]）。
- Late days：每人 7 天，可以用在 final project 的各階段，但**不能用在發表和 final report**；週末（六＋日）算 1 天（`gpu/lectures/2026-10-27/notes.md` [00:10:02]）。Proposal 屬於可用 late day 的階段。

## 和上課內容的關聯
- **專題說明、tier、時程、proposal 內容**：L6（11/10），[`gpu/lectures/2026-11-10/notes.md`](../../lectures/2026-11-10/notes.md) 重點摘要第 2 點（[00:07]–[00:50]，沒有講義頁碼）。
- **NCU metrics 可以從這些地方挑**：
  - L5（10/27）analysis-driven optimization 流程、arithmetic intensity、roofline（[`gpu/lectures/2026-10-27/notes.md`](../../lectures/2026-10-27/notes.md)，講義註解 p4「use in Final Project!」）。
  - L6 的 memory chart、L1TEX／shared memory wavefront、bank conflict、Nsight Compute demo（[`gpu/lectures/2026-11-10/notes.md`](../../lectures/2026-11-10/notes.md) 重點摘要第 3–4 點，[02:51]–[03:10] demo）。
  - HW3、HW4 已經用過的 NCU profiling（[../hw3/README.md](../hw3/README.md)、[../assignment-4-memory-access-patterns-mmul/README.md](../assignment-4-memory-access-patterns-mmul/README.md)）。
- **T1 的 tiled GEMM**：HW3 的 tiled MMULT、HW4 的 coalesced corner turning kernel。
- **Conv → GEMM**：L7（11/17）投影片 `Au26_GPU-Compute_L7_conv-gemm_v3.pdf`，筆記 [`gpu/lectures/2026-11-17/notes.md`](../../lectures/2026-11-17/notes.md)。
- **References**：Reading Set #5 = PMPP 4th ed. Ch7（convolution）＋ Ch16 §16.1–16.4（deep learning），老師說對應 L6、L7 和 final project（`gpu/lectures/2026-11-10/notes.md` 開頭）。

## 還不確定的地方
1. **評分比重**：10/6 課堂說 proposal 10%、design spec 30%、final 60%；11/10 課堂說 final code、presentation、report「equally weighted」而且佔大部分，沒再提 proposal 的比例（`gpu/lectures/2026-11-10/notes.md` 還要釐清的問題第 3 點）。Canvas 上 Proposal 是 10 pts。專題 spec §1 也沒寫比重（「Grading weights and the late-day policy are announced separately by the instructor.」）。
2. **組員人數**：原文寫「should be 3」，課堂說不接受其他人數；11/18 重置後如果組裡不到 3 人怎麼處理，沒有說明。
3. **Teams 上同學在問**：final project 程式碼要保留 T0–T3 各 tier 的 kernel，還是只交最後的版本（`digests/2026-11-18.md`，「Scheduled a meeting」thread，還沒有老師或 TA 回答）。這會影響 work breakdown 怎麼寫。
4. 原文沒說 proposal 要不要每個組員各交一份，還是一組交一份（Canvas 作業是否為 group assignment 沒記錄）。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-11-18 | 第一次整理 |
| 2026-11-22 | 專題 spec PDF 已存進 repo（`../final-project-tier-submissions/`），移出「還不確定」的「spec PDF 沒存進 repo」。spec §10 對 proposal 的要求是：組員和分工、Tier 0 baseline（自己 GPU 上 dev set 的 images/s，有的話加 per-layer 時間）、到 design spec（12/2）和 freeze（12/15）的 tier 目標、batch size 和理由，已交的 v2 這幾項都有。T0 繳交方式更正為 Canvas Tier Submissions（spec §8）；評分比重補上 spec §1 的說法 |
| 2026-11-22 | 第二次 review 修正：專題背景改成「ZIP 交 Canvas」並註明 kit v07；L7 notes 已存在，改成連結 |

GPU 課禁止用 AI 產生作業解答
