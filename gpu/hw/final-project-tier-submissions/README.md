# GPU Final Project：Tier Submissions（T0–T5 提交 ZIP）

> 原文：[spec.md](spec.md)（[Canvas assignment 11909772](https://canvas.uw.edu/courses/1917398/assignments/11909772)）。專題正式 spec 是 SharePoint `Final Project - ResNet18/Au26_GPUCompute_ResNet18_FinalProject_Spec.pdf`（11/19 10:43 PM PST 上傳），repo 裡還沒有存。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-12-15（二）5:00 PM PST**（Canvas `due_at` 2026-12-16T01:00:00Z，lock 同時，過了就交不了）；`gpu/assignments.md` 一致，也和 L7 講義 p53 的「Leaderboard freeze＋code 12/15 5 PM」相同，**不能用 late day** |
| 分數 | 1 pt（Canvas）；實際分數應在 Final Project 的 code 部分，比重見「還不確定的地方」 |
| 繳交方式 | Canvas online upload，**ZIP**（每個 tier 的 submission package） |
| 要交的東西 | 每個 tier（tier0–tier5）各一個 submission ZIP；每次提交都要**註明是哪個 tier**，例如「Tier0」「Tier2」 |

## 學習目標
- 把 ResNet-18 forward pass 的 starter engine 一層一層換成更快的 kernel，每完成一個 tier 就提交一次，留下每個最佳化階段的成果（`gpu/lectures/2026-11-17/notes.md` 重點摘要 14）。
- 每個 tier 都先 profile 再最佳化，NCU 數據之後要寫進 design spec 和 final report（`gpu/lectures/2026-11-10/notes.md` [00:39:03]）。

## 要做什麼
原文只講繳交規則（spec.md「Canvas 作業說明」）：

1. 把 final project 每個 tier 的 submission ZIP 交到這個 Canvas 作業，範圍 tier0 到 tier5。
2. 每份提交都寫上它屬於哪個 tier（例如「Tier0」）。
3. 可以交很多次，同一個 tier 也可以交好幾次。
4. **一天只交一次。**

ZIP 從哪來：照 starter kit 的 Getting Started 在 AWS T4 上跑完，會自動產生 submission zip；提交工具是 `submit.py`（`gpu/lectures/2026-11-17/notes.md` 重點摘要 15，[03:08:02]、[03:16:00]–[03:20:00]）。

各 tier 的內容（L7 講義 p55，口述 [03:09:02]–[03:11:00]；正式定義以 spec PDF 為準）：

| Tier | 內容 | 對應講次 |
|---|---|---|
| T0 | build、過 `check.py`、profile、選 batch size、拿第一筆 leaderboard；**11/22（日）11:59 PM** | 現在 |
| T1 | NHWC＋batching；explicit im2col＋自己的 SMEM tiled SGEMM；無 bank conflict 的 tile；bias/ReLU fused 進 epilogue | L3–L6 |
| T2 | implicit GEMM（拿掉 im2col buffer）、fused residual add、per-shape launch config | L7（11/17） |
| T3 | register tiling、thread coarsening、`float4`、per-shape tile 調參 | L8（11/24） |
| T4 | tensor core（FP16 WMMA／`mma.sync`，FP32 累加），開啟 FP16 類別 | L9（12/1） |
| T5 | fusion 與調參（stem conv＋maxpool、downsample、warp-shuffle avgpool、autotune） | stretch |

每個 tier 各自排 leaderboard，同一隊每個 tier 都可以有一筆（[03:11:00]）。T1–Tn 的提交期間是 11/22–12/15（講義 p53）。

## 注意事項
- 每份提交都要標 tier（spec.md）。
- **一天最多交一次**，同一個 tier 也一樣算（spec.md「Only one submission per day please!」）。最後幾天要排好，不能 12/15 下午一次交好幾個 tier。
- 截止 12/15 5:00 PM，lock 同時；講義 p53 標 *，**不能用 late day**（`gpu/lectures/2026-11-17/notes.md` 重點摘要 14）。注意是下午 5 點，不是晚上 11:59。
- 正確性 gate：`check.py` 逐層比對 reference activations，過不了不算（`gpu/lectures/2026-11-10/notes.md` 重點摘要第 2 點）。
- 不能用現成的 CUDA 運算函式庫（NVIDIA library、Thrust、Boost 等），checker 查到就過不了 gate（`gpu/lectures/2026-11-10/notes.md` [00:07]–[00:50]）。
- 開發用 dev（500 張），val 全集只在最後提交時跑；data pack 先用 SHA-256 驗證（`gpu/lectures/2026-11-17/notes.md` 重點摘要 15，[03:15:02]）。
- Starter kit 已更新到 **`resnet18_student_kit_v07.zip`**（Canvas file 156502277，11/19 10:41 PM PST），做 T0 前改用新版（`digests/2026-11-20.md`）。

## 和上課內容的關聯
- **專題時程、tier 表、starter kit 導覽**：L7（11/17）[`gpu/lectures/2026-11-17/notes.md`](../../lectures/2026-11-17/notes.md) 重點摘要 14–16（講義 p53–p57）。
- **專題背景、正確性 gate、不能用 library**：L6（11/10）[`gpu/lectures/2026-11-10/notes.md`](../../lectures/2026-11-10/notes.md) 重點摘要第 2 點。
- **T1**：HW3 tiled MMULT（[../hw3/README.md](../hw3/README.md)）、HW4 coalesced corner turning（[../assignment-4-memory-access-patterns-mmul/README.md](../assignment-4-memory-access-patterns-mmul/README.md)）、L6 bank conflict。
- **T2**：L7 conv → GEMM、implicit GEMM（L7 notes）；E3 `sgemm_tiled` 的兩層 tiling 也是 T3 的起點（L7 notes 第 81 行附近，講義 p30–p31）。
- **T3／T4**：L8（11/24）、L9（12/1），筆記還沒有。
- **Profiling**：L5（10/27）analysis-driven optimization、roofline（[`gpu/lectures/2026-10-27/notes.md`](../../lectures/2026-10-27/notes.md)）；L7 notes 重點摘要 16 NCU profiling 訣竅。
- Proposal 的 tier 規劃：[../final-project-proposal/README.md](../final-project-proposal/README.md)。

## 還不確定的地方
1. **T0 要不要交到這裡**：T0 smoke test 11/22 11:59 PM 截止，L7 時老師說繳交位置「to be announced」，大概是 Canvas（L7 notes [03:08:02]）。這個作業寫「tier0 through tier5」，看起來 T0 也交這裡，但它的 due_at 是 12/15，沒有另外標 11/22。保險做法是 11/22 前就把 Tier0 ZIP 交到這裡並標「Tier0」。
2. **「一天一次」怎麼算**：是全隊一天一次還是每人一天一次、同一天交兩個不同 tier 算不算違規，原文沒說。另外原文沒說是一組交一份還是每個組員各交。
3. **ZIP 和 leaderboard 的關係**：L7 說 `submit.py` 會交到 leaderboard、會自動產生 submission zip；這個 Canvas 作業和 leaderboard 是同一套還是兩邊都要交，原文沒說清楚。
4. **分數**：Canvas 上只有 1 pt；Final Project 各部分比重，10/6 說 proposal 10%／design spec 30%／final 60%，11/10 改說 code、presentation、report 比重相同（`gpu/assignments.md`）。
5. **專題 spec PDF 沒存進 repo**：正式 tier 定義和 ZIP 內容要求在 `Au26_GPUCompute_ResNet18_FinalProject_Spec.pdf`，上面的 tier 表是 L7 講義 p55 的版本。
6. Teams 上同學問過 final code 要保留 T0–T3 各 tier 的 kernel 還是只交最後版本，還沒有老師或 TA 回答（`digests/2026-11-18.md`）。這份作業按 tier 分別收 ZIP，可能就是答案，但沒被證實。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-11-20 | 第一次整理 |

GPU 課禁止用 AI 產生作業解答
