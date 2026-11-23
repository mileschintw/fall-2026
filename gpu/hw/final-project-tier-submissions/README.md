# GPU Final Project：Tier Submissions（T0–T5 提交 ZIP）

> 原文：[spec.md](spec.md)（[Canvas assignment 11909772](https://canvas.uw.edu/courses/1917398/assignments/11909772)）。專題正式 spec 是 SharePoint `Final Project - ResNet18/Au26_GPUCompute_ResNet18_FinalProject_Spec.pdf`（11/19 10:43 PM PST 上傳），已存在同資料夾：[PDF](Au26_GPUCompute_ResNet18_FinalProject_Spec.pdf)、[文字版 project_spec.txt](project_spec.txt)（下面寫「spec §N」就是指它）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-12-15（二）5:00 PM PST**（Canvas `due_at` 2026-12-16T01:00:00Z，lock 同時，過了就交不了）；`gpu/assignments.md` 一致，也和 L7 講義 p53 的「Leaderboard freeze＋code 12/15 5 PM」相同，**不能用 late day** |
| 分數 | 1 pt（Canvas）；實際分數應在 Final Project 的 code 部分，比重見「還不確定的地方」 |
| 繳交方式 | Canvas online upload，**ZIP**（每個 tier 的 submission package）。spec §8「How to hand in the zip: Use submit.py to create submission ZIP, upload to course Canvas assignment」：leaderboard 由 grader 根據這裡的 ZIP 產生，**不是另外交到 leaderboard** |
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

### ZIP 怎麼產生（spec §8「Submitting」）
```
python tools\submit.py --team "name" --members "A, B, C" --category fp32|fp16 --batch 64 --tier 3
       --src starter --outdir submissions [--engine-args "--conv igemm"] [--notes "..."]
```
- `submit.py` 只打包 `CMakeLists.txt`、`src\`、`include\`、`third_party\`（不含 build 資料夾、執行檔、資料），再加一份 `submission.json`（team、members、category、batch、tier、engine 參數、檔案 hash）。grader 只靠這個 zip 就要能 build。
- 不一定要在 T4 上產生：`submit.py` 只是打包原始碼，速度一律由 grader 在 T4 上量。
- zip 檔名是 team＋tier＋UTC 時間戳（例 `your-team_T2_20261124T031500Z.zip`），**不要改名**。
- leaderboard 是公開網頁，**team name 不能含真名**，整個專題都用同一個名字（board 用 team name 追蹤最佳成績）。本組 proposal 用的是 `Project Team 13`。
- `--tier` 是自己宣告的，staff 會對照 design spec 和 report 驗證，可能改判。
- grader 只會傳 `--pack --set --out --batch --precision --iters --warmup`，加上 `submission.json` 裡宣告的額外參數（例如 `--conv igemm`）；預設 conv 路徑是 engine 自己決定。

### Grader 流程（spec §8，每一輪都一樣，T0 也是）
解壓 → 禁用 library 的 static scan → cmake build（只 build sm_75）→ debug set per-layer check → dev set（500 張）計時：1 次 warm-up＋3 次計時取中位數，同時用 nvidia-smi 記 SM clock → end-to-end gate。任何一關沒過就不上榜，每次提交會收到一份短報告（有效的寫測量值；無效的寫哪一關、哪一行失敗）。

Leaderboard：[overall](https://faculty.washington.edu/colinrei/au26-leaderboard/board.html)、[by tier](https://faculty.washington.edu/colinrei/au26-leaderboard/board_by_tier.html)。欄位有 images/s、% roofline、top-1/top-5 err、batch、tier、SM MHz、提交時間（UTC）。每隊以最佳有效成績代表；FP32 和 FP16 兩個 category 可以各佔一席。

### T0 smoke test（**11/22（日）11:59 PM PST**）
spec §10：把**完全沒改過的 starter** 用 `submit.py` 打包、從這個 Canvas 作業交上去，在 leaderboard 上出現一筆有效的 Tier 0。目的是驗證 toolchain 和繳交流程，不是測 kernel。本組照 proposal：`--category fp32 --batch 32 --tier 0`；proposal 分工表上 `submit.py` 的 owner 是 Miles。

L7 投影片 p56 的「Initial goals（by 22 NOV）」另外列了：starter 在自己的 GPU **和 AWS T4** 上 build 並過 `check.py`、一份最慢 kernel 的 NCU report。這些不是繳交項目，但 design spec 會用到。

### 各 tier 內容（spec §9，正式版本）
| Tier | 內容 | 對應講次 |
|---|---|---|
| T0 Baseline | build starter、過 `check.py`、profile（12 個 shape class 的時間花在哪）、選 batch size；原封不動交上去當 smoke test | L1–L6 |
| T1 Batched GEMM path | NHWC＋batching；im2col＋自己的 SMEM tiled SGEMM；無 bank conflict 的 tile；bias/ReLU fused 進 epilogue | L3–L6，11/10 |
| T2 Implicit GEMM | 拿掉 im2col buffer，gather 放進 tile load；fused residual add；per-shape launch config | L7，11/17 |
| T3 Register tiling | thread coarsening、2-D block/register tile（Boehm kernel 4–5）、`float4` load、per-shape tile 調參 | L8，11/24 |
| T4 Tensor cores | FP16 WMMA／`mma.sync`，FP32 累加；FP16 weight 和 activation；開啟 FP16 category | L9，12/1 |
| T5 Fusion and tuning | stem conv＋maxpool fused；downsample 共用 block input 的讀取；warp-shuffle avgpool 和 top-5；減少 launch；per-shape autotune | L10+，stretch |

spec 原文：「A solid team reaches Tier 3 with good Nsight Compute evidence; Tier 4 separates the top of the board.」by-tier view 依 tier 分組排名（[03:11:00]）。T1–Tn 的提交期間是 11/22–12/15；**freeze 前最後一筆有效提交就是被評分的 final code**（spec §8、§10）。

## 注意事項
- 每份提交都要標 tier（spec.md）。
- **一天最多交一次**，同一個 tier 也一樣算（spec.md「Only one submission per day please!」）。最後幾天要排好，不能 12/15 下午一次交好幾個 tier。
- 截止 12/15 5:00 PM，lock 同時；講義 p53 標 *，**不能用 late day**（`gpu/lectures/2026-11-17/notes.md` 重點摘要 14）。注意是下午 5 點，不是晚上 11:59。
- 正確性 gate（spec §7）：debug set per-layer max|err|/max|ref| ≤ 0.001（FP16 ≤ 0.02）；top-1 和 reference 一致 ≥ 99.5%；top-1/top-5 error 在 reference（dev：19.20% / 3.20%）±0.5 pp 以內；`top5.bin` 和自己的 logits 100% 一致（同分取 class index 小的）；logits 全部是有限值。任一項沒過就不上榜。
- 禁用 library（spec §8「Rules」）：cublas、cudnn、cutlass、cub/、thrust、torch、onnxruntime、nvinfer、tensorrt、任何 framework 或 vendor inference library、任何預先算好的輸出。**scan 是不分大小寫的逐行純文字搜尋**，註解和字串裡出現也會被拒，原始碼和 CMake 檔裡完全不要寫這些字（連「faster than ...」這種註解都不行）。
- Grader 只 build sm_75：T4 沒有的指令（`cp.async`、bf16、FP16 `m16n8k16` MMA shape、wgmma、thread-block cluster）在自己的 GPU 上能跑也會組譯失敗。`CMAKE_CUDA_ARCHITECTURES` 一定要保留 75，例如 `"75;86"`。
- AWS T4 instance 上的檔案不保證留到下次：engine 放在組內 private Git repo，每次開 session 先 clone，登出前 commit＋push（spec §6）。pack 已預裝在 `C:\resnet18\resnet18_pack`。
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
1. ~~T0 要不要交到這裡~~：**已確認**，spec §8 寫 T0 也是用 `submit.py` 產生 ZIP、上傳到 Canvas 作業。這個作業的 Canvas due_at 是 12/15，但 T0 本身 11/22 11:59 PM 截止（spec §1、§8、§10），11/22 前就要把 Tier0 ZIP 交到這裡並標「Tier0」。
2. **「一天一次」怎麼算**：是全隊一天一次還是每人一天一次、同一天交兩個不同 tier 算不算違規，原文沒說。另外原文沒說是一組交一份還是每個組員各交（spec 的流程是一隊一個 team name，看起來是一組交一份，由一個人交）。
3. ~~ZIP 和 leaderboard 的關係~~：**已確認**是同一套。spec §8：用 `submit.py` 產生 ZIP，上傳到 Canvas 作業，grader 每一輪評分後更新 leaderboard。之前「交到 leaderboard，不是 Canvas」的說法是錯的。
4. **分數**：Canvas 上只有 1 pt；Final Project 各部分比重，10/6 說 proposal 10%／design spec 30%／final 60%，11/10 改說 code、presentation、report 比重相同（`gpu/assignments.md`）。spec §1 也只寫「Grading weights and the late-day policy are announced separately by the instructor.」
5. ~~專題 spec PDF 沒存進 repo~~：已存（2026-11-22）。上面的 tier 表已換成 spec §9 的版本。
6. Teams 上同學問過 final code 要保留 T0–T3 各 tier 的 kernel 還是只交最後版本，還沒有老師或 TA 回答（`digests/2026-11-18.md`）。spec §8、§10 說「your last valid submission before the freeze is your final project code」，也就是只評最後一筆；但 report 要有各 tier 的 ablation（tier → images/s）和 NCU 數據（spec §10），所以各 tier 的版本還是要在 Git 裡留著。
7. **評分多久跑一輪**：spec 說「After each grading round」，沒寫一輪的頻率，所以 T0 交了之後不一定當晚就會出現在 board 上。
8. **Kit 版本**：spec 是從「MASTER kit v09」產生的；Canvas 上的 student kit 最新記錄是 v07（11/19）。兩邊的版本號不一樣，交之前先看 Canvas Files 有沒有更新的版本。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-11-20 | 第一次整理 |
| 2026-11-22 | 從 SharePoint 存入專題 spec PDF（＋文字版）；確認 T0 和各 tier 都是 `submit.py` → Canvas 這個作業；tier 表換成 spec §9；補上 submit.py 用法、grader 流程、gate 門檻、禁用字 scan、sm_75 限制 |

GPU 課禁止用 AI 產生作業解答
