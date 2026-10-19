# 截止總表（學期至今版，2026-10-18 9:16 PM PDT）

> 這份是「截止提醒」的全學期版：從開學第一天（9/30）到期末，每一個要交或要到場的項目都列出來，附目前的繳交狀態。
> 來源：Canvas `assignments?include[]=submission`（10/18 9:16 PM 用瀏覽器重抓）、Canvas ICS（GPU 採用 2 筆、DSA 採用 41 筆）、`gh api`、syllabus / BOOTSTRAP §2。
> 可信度依 CLAUDE.md：課堂口述 > Piazza/Teams 老師回覆 > Canvas `due_at` > syllabus > 投影片。時間一律 Pacific，11/1 起是 PST。

## 🔴 已過期或今晚到期，還沒交的

| 課 | 項目 | 截止 | 狀態 | 要做什麼 |
|---|---|---|---|---|
| DSA | **A2 Lists, lists and more lists**（150 分，作業中最高分之一） | **今晚 10/18（日）11:59 PM PDT**，剩約 2.7 小時 | Canvas **unsubmitted**；`assignment-2-mileschintw` 只有老師 10/7 的 Initial commit | push → 到 Canvas 交 repo URL。來不及的話：syllabus 允許**每學季一次免罰遲交（最多 1 週）**，但要**事先告知**老師，所以要在 11:59 PM 前去 Piazza 私訊。其他遲交每天 -25%，投影片寫超過 4 天不收 |
| GPU | Task 0 - self introductions（0 分） | 10/9（五）11:59 PM PDT | Canvas unsubmitted，lock 12/18 | **不計分**（Canvas `omit_from_final_grade: true`）。Canvas 說明是「在 Teams 頻道貼自我介紹」；L1 課堂上老師說 task zero 就是 HW0、不用交 [00:57:05]，看起來是把兩者混在一起。結論：不影響成績，有空在 Teams 的 Task 0 貼文回覆自介就好 |

## ✅ 已完成

| 課 | 項目 | 截止 | 結果 |
|---|---|---|---|
| DSA | Intro Survey（Canvas quiz） | 開學第一週 | 有填（A1 repo 有建立，代表老師已經跑過邀請腳本） |
| DSA | A1 My First Python Assignment | 10/4（日）11:59 PM | **graded 50/50**。10/7 才交（submitted_at 10/7 11:10 PM PDT），晚了 3 天，但成績是滿分，看起來沒有被扣分 |
| GPU | First Class Survey（PollEv） | 10/8 EOD | 不在 Canvas 上，看不到狀態。TA 說要填完才拿得到 AWS credentials，如果你已經能登入 AWS WorkSpaces 就代表填過了 |
| GPU | HW0（環境設定，說明 PDF 10/6 上傳） | — | Canvas 沒有對應的作業項目，不計分，看起來只是 AWS VDE 登入練習 |

## 📅 接下來全部的截止日

| 日期（Pacific） | 距今 | 課 | 項目 | 分數 | 繳交方式 / 備註 |
|---|---|---|---|---|---|
| **10/20（二）5:59 PM PDT** | 2 天 | GPU | **HW1 SAXPY, 2D & 3D Matrix addition** | 11 | Canvas 上傳（online_upload）。Canvas unsubmitted。L1 投影片 p55 的 error-checking macro 有錯，要看 updated 版。遲交每天 -1 |
| **10/23（五）11:59 PM PDT** | 5 天 | DSA | **A3 Stacks, Queues and Testing** | 150 | repo `assignment-3-mileschintw` 已建立（只有 Initial commit）→ push → Canvas 交 URL。Piazza @36：用 Python primitives，list 當 stack |
| 10/27（二）5:59 PM PDT | 9 天 | GPU | HW2（**Canvas 未發布**） | 12 | 去年題目 Gaussian Blur（僅預告；L2 老師也提到 blur） |
| 10/30（五）11:59 PM PDT | 12 天 | DSA | A4 Bug Hunt | 100 | repo 還沒建立 |
| 11/3（二）5:59 PM **PST** | 16 天 | GPU | HW3（未發布） | 12 | 11/1 換冬令時間後的第一個截止 |
| 11/6（五）11:59 PM PST | 19 天 | DSA | A5 BSTs and AVLs | 100 | `due_at` 2026-11-07T07:59:59Z |
| **11/9（一）4:30–6:30 PM PST** | 22 天 | DSA | **Midterm（15%）** | 100 | **實體紙筆，Moore 220**。Canvas 的 Classic Quiz 只代表時段 |
| 11/10（二） | 23 天 | GPU | HW4（未發布） | 15 | syllabus 11:59 PM，投影片 5:59 PM；以 syllabus 為準，但建議 5:59 PM 前交 |
| **11/17（二）** | 30 天 | GPU | **Project Proposal**（專題 10%） | — | syllabus 11:59 PM，投影片 5:59 PM |
| 11/30（一）11:59 PM PST | 43 天 | DSA | A6 Heaps | 100 | |
| **12/1（二）5:59 PM PST** | 44 天 | GPU | **Project Design Spec**（專題 30%） | — | |
| **12/9（三）4:30 PM PST** | 52 天 | DSA | **Final Exam（20%）** | 120 | **實體紙筆，要到校**。老師說「十二月不要來跟我要求改時間」 |
| 12/11（五）11:59 PM PST | 54 天 | DSA | A7 Surprise | 100 | **不能遲交** |
| 12/15（二）–12/17（四） | 58 天 | GPU | Project 發表 | — | 線上 |
| **12/17（四）11:59 PM PST** | 60 天 | GPU | **Project Final Report + Code**（專題 60%） | — | **不能延期** |

## 成績結構（判斷輕重用）
- **GPU**：HW 50%（HW1–4 共 50 分）+ Final Project 50%，沒有考試。專題的 Proposal → Design Spec → Final 是 10/30/60。
- **DSA**：作業 65%（A1 50、A2 150、A3 150、A4–A7 各 100，共 750 分）+ 期中 15% + 期末 20%。**A2、A3 各佔作業總分的 20%**，是整學期最重的兩份作業，而且剛好連在一起（10/18、10/23）。

## 提醒機制
- 排程「截止提醒」每天 08:00、18:00 檢查 48h / 24h 內到期的項目，各推播一次。
- 第一次自動推播會是 10/19 08:00 的 GPU HW1（剩約 34 小時，48h 門檻）。
