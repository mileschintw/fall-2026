# GPU（EE P 524 A）作業與專題時程

> 來源：Canvas `/courses/1917398/assignments`（2026-10-18 抓取，10-21 晨報更新）+ BOOTSTRAP §2.1（syllabus / L1 p9–10）。時間皆為 Pacific。
> 可信度：Canvas `due_at` > syllabus > 投影片。尚未在 Canvas 發布的項目以 syllabus/投影片為準，並標「未發布」。

| 項目 | 截止（Pacific） | 分數 | Canvas 狀態 | 繳交狀態 | 備註 |
|---|---|---|---|---|---|
| Task 0 - self introductions | 10/9（五）11:59 PM PDT | 0 | 已發布（id 11810624），lock 12/18 | unsubmitted | online_url；**不計分**（omit_from_final_grade）；內容是在 Teams 貼自介；L1 老師說 task zero 不用交 [00:57:05] |
| HW1 SAXPY, 2D & 3D Matrix addition | **10/20（二）5:59 PM PDT** | 11 | 已發布（id 11810625），lock 12/11 | graded（11/11 晨報確認） | online_upload；Canvas 與 §2 一致 |
| Pop Quiz - Lecture 3 - 10/20/26 | 10/20（二）8:30 PM PDT | 3 | 已發布（id 11860726，quiz 2457138），8:20–8:30 PM 開放 | graded | 課堂 pop quiz |
| HW2 Parallel performance theory, Gaussian blur kernels and more! | **10/27（二）5:59 PM PDT** | 12 | 已發布（id 11810626），lock 12/13 | graded（11/17 確認） | 10/20 發布；說明 PDF「Homework #2 (HW2) - Au26 - GPUCompute.pdf」（Canvas file 154697826） |
| Pop Quiz - Lecture 4 - 10/27 | 10/27（二）8:25 PM PDT（lock；due_at null） | 5 | 已發布（id 11860516，quiz 2457104） | graded（10/28 確認） | 課堂 pop quiz |
| HW3 Control Divergence & Tiled MMULT improvements & NCU profiling | **11/6（五）11:59 PM PST**（Canvas due_at 2026-11-07T07:59:59Z） | 12 | 已發布（id 11810628），lock 12/14 | submitted | 10/27 發布；說明 PDF「Homework #3 (HW3) - Au26 - GPU Compute .pdf」（Canvas file 155100870）；原預估 11/3，以 Canvas 為準 |
| Pop Quiz - Lecture 5 11/2/26 | 11/3（二）8:30 PM PST | 3 | 已發布（id 11881085，quiz 2460212），8:20–8:30 PM 開放 | graded（11/4 確認） | 課堂 pop quiz |
| HW4 Memory access patterns & MMULT coalesced corner turning kernel | **11/15（日）11:59 PM PST**（Canvas due_at 2026-11-16T07:59:59Z） | 15 | 已發布（id 11810623），lock 12/13 | submitted | 11/3 發布；說明 PDF「Homework #4 (HW4) - Au26 - GPUCompute.pdf」（Canvas file 155723325）；原預估 11/10，以 Canvas 為準；11/11 晨報：Canvas due_at 由 11/13 改為 11/15 |
| Final Project - Proposal | **11/20（五）11:59 PM PST**（Canvas due_at 2026-11-21T07:59:59Z） | 專題 10%（10 pts） | 已發布（id 11810636） | submitted（11/20 晨報確認） | 11/18 晨報：Canvas 發布，截止由原預估 11/17 延到 11/20；Team sign-up 重開到 11/18 11:59 PM PT，所有組別已重置，要到 People → Project Teams 重新加入（每組最多 3 人） |
| Project T0 smoke test | **11/22（日）11:59 PM PST** | — | `submit.py` 產生 ZIP，上傳到 Canvas「Final Project Tier Submissions」（id 11909772），註明「Tier0」（原文只說要註明 tier，沒指定寫在哪，寫在 submission comment 最保險）；grader 評完才上 leaderboard | submitted（11/22 9:43 PM PST，Canvas 小組提交；leaderboard 待評分） | 原封不動的 starter；`--category fp32 --batch 32 --tier 0`（proposal）；L7 講義 p53、專題 spec §8／§10（[gpu/hw/final-project-tier-submissions/](hw/final-project-tier-submissions/README.md)）；11/22 更正：之前寫「交到 leaderboard（不是 Canvas）」是錯的 |
| Project 發表 sign-up | 11/24（二）5:59 PM PST，不能用 late day | — | 未發布 | — | L7 講義 p53；spec §1 時程表、§12 仍列。11/23 4:30 PM PT 全面查過還沒有登記處：Canvas assignments／announcements／Scheduler（appointment groups）／discussions／pages／calendar／新檔案都沒有，group 只有 Project Teams 一組；Teams Final Project channel 和 General 都沒有相關貼文，也沒有取消發表的公告 |
| Popquiz Lecture 8 11/24 | 11/24（二）8:15 PM PST | 3 | 已發布（id 11919521） | graded（11/25 晨報確認） | 課堂 pop quiz；11/25 晨報才出現在 Canvas |
| Project Design Spec | **12/4（五）11:59 PM PST**（Canvas due_at 2026-12-05T07:59:59Z） | 21 pts | 已發布（id 11810630），lock 12/15 11:59 PM PST | unsubmitted | 11/25 晨報：Canvas 發布。L7 講義 p53 寫 12/2 11:59 PM，依可信度規則 Canvas due_at > 投影片，改採 12/4；原記 12/1 5:59 PM（10/6 syllabus）作廢 |
| Project leaderboard freeze＋code | **12/15（二）5:00 PM PST，不能用 late day** | 未定 | — | — | T1–Tn 提交期間 11/22–12/15；freeze 前最後一筆有效提交就是被評分的 final code（spec §8、§10）。by-tier view 依 tier 分組排名，但每隊是每個 tier 各一筆還是只留最佳一筆，L7 口述和 spec 說法不同，見 tier-submissions README |
| Final Project Tier Submissions | **12/15（二）5:00 PM PST**（Canvas due_at 2026-12-16T01:00:00Z，lock 同時） | 1 pt | 已發布（id 11909772） | unsubmitted | 11/20 晨報：Canvas 新作業，時間和上一列 leaderboard freeze 相同。11/22 依專題 spec §8 和本作業原文（「from tier0 through tier5」）確認：T0–T5 的 `submit.py` ZIP 都交這裡。Canvas 的 submitted 只代表交過某個 tier，**不代表 final code 已交**，晨報不會因此改這一列（`automation/morning-brief.md`），freeze 後手動標 |
| Project 發表 | 12/15（二）～12/17（四）6–9 PM，不能用 late day | 未定 | — | — | 線上，3 天各 8 組，每組 10 分鐘＋5 分鐘 Q&A |
| Project Final Report | **12/17（四）11:59 PM PST，不能用 late day** | 未定 | 未發布 | — | code 改在 12/15 隨 freeze 交 |

- 成績：HW 50%、Final Project 50%，沒有考試。
- **Final Project 是固定題目，不是自選專題**：全班都做 ResNet-18 inference engine（只做 forward pass），把 starter kit 的 naive kernel 一層層換成更快的版本，T0–T5 分 tier 用 `submit.py` 打包，ZIP 交到 Canvas「Final Project Tier Submissions」（id 11909772），grader 在 AWS T4 上評分後更新 leaderboard。3 人一組。Starter kit 是 Canvas Files 的 `resnet18_pack.zip`、`resnet18_student_kit_v07.zip`（11/19 起，原 v06）；spec PDF 在 SharePoint（Teams「Final Project - ResNet18」channel 的檔案），repo 存在 `gpu/hw/final-project-tier-submissions/`。時程以 L7（11/17）講義 p53 為準（`gpu/lectures/2026-11-17/notes.md` 第 14 點）。
- Final Project 各階段比重未定：10/6 說 proposal 10%／design spec 30%／final 60%，11/10 改說 code、presentation、report 比重相同。Canvas 上 Proposal 是 10 pts。
- 遲交 HW 最後期限 11/27（五）11:59 PM（L7 口述）。
- 遲交：遲 1 天 -1，之後每 24h 再 -1，第 5 天累計 -6；第 10 天再 -2，之後每 5 天 -1。
- 閱讀進度（Canvas Page `weekly-reading-sets`）：Set #1 PMPP Ch1–2（9/30 起，對應 L1、HW0）；Set #2 PMPP Ch3 §1–4、Ch4 §1–4（10/13 起，對應 L2、L3）。
- 課表註明「subject to some revision」，每週重新比對。
