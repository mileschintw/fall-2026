# Fall 2026 學期中樞

UW Autumn 2026 兩門課的資料整理 repo：

- **GPU**：EE P 524 A Applied High-Performance GPU Computing（Prof Reinhardt）
- **DSA**：EE P 590 A Data Structures, Algorithms & Python（Adrienne Slaughter）

Canvas、Piazza、Teams/SharePoint、Panopto、GitHub 上的東西散在五六個地方。這個 repo 把它們收進同一個地方：作業時程、公告、Piazza 重點、每堂課的逐字稿和筆記，還有每天早上的晨報。大部分內容是 Claude desktop app 的排程任務自動抓、自動寫的，所以每天都會有新的 commit。

時間一律是 Pacific。11/1 之前是 PDT，之後是 PST。

## 從哪裡開始看

| 想知道 | 看這裡 |
|---|---|
| 最近有什麼事、哪個作業快到期 | [`digests/INDEX.md`](digests/INDEX.md)。最上面是每個排程任務最近一次的結果，點進去就是當天晨報。 |
| 某一天的晨報 | `digests/<日期>.md`，例如 [`digests/2026-10-19.md`](digests/2026-10-19.md) |
| 這週要做什麼 | `digests/<週日日期>-weekly.md` |
| 全學期作業、考試時程 | [`gpu/assignments.md`](gpu/assignments.md)、[`dsa/assignments.md`](dsa/assignments.md)，或是 [`digests/semester-to-date/2026-10-18-deadlines.md`](digests/semester-to-date/2026-10-18-deadlines.md) 總表 |
| 某堂課在講什麼 | `<課>/lectures/<上課日期>/notes.md`。索引在 [`gpu/lectures/README.md`](gpu/lectures/README.md)、[`dsa/lectures/README.md`](dsa/lectures/README.md) |
| 開學到 10/18 的整體狀況 | [`digests/semester-to-date/`](digests/semester-to-date/)：完整晨報（brief）、學期規劃（plan）、截止總表（deadlines） |
| 課程基本資料（教室、OH、TA、平台） | [`courses.yaml`](courses.yaml) |

上課筆記是這個 repo 最有用的部分。每份 `notes.md` 都是用老師講課的逐字稿加投影片寫的。重點後面附了 `[hh:mm:ss]` 時間戳，可以回錄影對照。逐字稿是自動字幕，專有名詞常常聽錯，所以筆記開頭有一份「常見誤聽對照」，例如 Panopto 會把 deque 聽成 deck。

## 目錄

```
fall-2026/
├── README.md            ← 這份
├── courses.yaml         ← 兩門課的設定：Canvas id、上課時段、OH、TA、Piazza、GitHub org、SharePoint
├── BOOTSTRAP.md         ← 建置這個 repo 時的完整背景：每個平台怎麼抓、查證過的課程事實、資料可信度規則
├── CLAUDE.md            ← 給 Claude 的工作規則（精簡版）
│
├── digests/             ← 產出的報告
│   ├── INDEX.md         ← 所有排程執行的總覽，自動產生，不要手改
│   ├── <日期>.md         ← 每天的晨報
│   ├── <日期>-weekly.md  ← 週日晚上的下週規劃
│   └── semester-to-date/ ← 一次性的「開學到某天」完整版
│
├── gpu/
│   ├── assignments.md   ← 作業與專題時程、分數、繳交狀態
│   ├── announcements/   ← Canvas 公告與 Teams 貼文摘要
│   └── lectures/<日期>/  ← transcript.vtt（Teams 逐字稿原檔）、slides.txt（投影片文字）、notes.md（筆記）
│
├── dsa/
│   ├── assignments.md
│   ├── repos.md         ← GitHub Classroom 的 assignment repo 清單
│   ├── piazza/          ← Piazza 貼文摘要
│   └── lectures/<日期>/  ← transcript.srt（Panopto 自動字幕）、slides.txt、notes.md
│
├── automation/          ← 排程任務的 prompt（見下一節）
│   ├── morning-brief.md、weekly-plan.md、deadline-alert.md、lecture-notes.md
│   ├── _finish.md       ← 每個任務共同的收尾：登記、更新 dashboard、推播、commit
│   ├── dashboard/       ← 手機看的 dashboard 頁面原始碼
│   └── MIGRATION.md     ← 換 claude.ai 帳號時怎麼搬
│
├── scripts/             ← 抓資料、算時區、寫報告用的小工具
│   ├── ics_fetch.py     ← 抓 Canvas 行事曆 ICS（不用登入），濾掉往年項目
│   ├── digest_base.py   ← 晨報裡不用登入的部分：48h 內截止、今天的課、新 repo
│   ├── log_run.py       ← 登記一次排程執行，重新產生 digests/INDEX.md
│   ├── tz.py            ← 時區換算（一定要 tz-aware，不能寫死 -7/-8）
│   ├── condense_transcript.py、write_transcripts.py ← 逐字稿處理
│   ├── github_assignments.ps1 ← 列 DSA 的 assignment repo
│   ├── pw_run.py        ← 用 Playwright 在已登入的頁面跑 browser/*.js，結果直接寫成檔案
│   └── browser/*.js     ← 在瀏覽器裡跑的片段：Canvas、Piazza、Panopto、SharePoint
│
└── state/               ← 排程用來判斷「什麼是新的」的紀錄
    ├── deadlines.json   ← 全部截止項目和繳交狀態（dashboard 的資料來源）
    ├── runs.json        ← 每次排程執行的結果（INDEX.md 的資料來源）
    └── *_seen.json 等   ← 已經看過的公告、貼文、檔案、repo，說明在 state/README.md
```

## 怎麼運作

四個排程任務在 Claude desktop app 裡跑，時間如下（Pacific）：

| 任務 | 時間 | 做什麼 |
|---|---|---|
| 晨報 | 每天 07:00 | 檢查兩門課所有平台有沒有新公告、新貼文、新作業、新錄影，寫成 `digests/<日期>.md` |
| 截止提醒 | 每天 08:00、18:00 | 48 小時和 24 小時內到期的項目推播到手機 |
| 週規劃 | 週日 21:00 | 排下週的截止日和建議開始時間 |
| 上課筆記 | 週二、三、四 10:00 | 抓前一天的錄影逐字稿和投影片，寫 `notes.md` |

資料從三條路來：

1. **Canvas ICS 行事曆**：不用登入，排程首選。網址帶有密鑰，所以放在 `.env`，不進 repo。
2. **Playwright（`scripts/pw_run.py`）**：用使用者自己登入的狀態讀 Canvas、Piazza、Teams/SharePoint、Panopto。登入過期就停下來，在晨報上標「需要重新登入」，不會把空結果當成「沒有新東西」。
3. **`gh` CLI**：DSA 的 GitHub Classroom repo。

每個任務跑完會登記到 `state/runs.json`、重新產生 `digests/INDEX.md`、更新手機用的 dashboard，最後 commit 並 push 到 GitHub，所以 GitHub 上看到的就是最新狀態。排程只讀資料，不會在 Piazza、Teams、Canvas 發文或交作業。

## 資料可以信多少

來源互相矛盾的時候，依這個順序採信：

**老師上課講的（逐字稿）> Piazza / Teams 上老師或 TA 的回覆 > Canvas 作業的截止時間 > syllabus > 投影片 > Canvas 公告與行事曆**

幾個已知的坑（細節在 [`BOOTSTRAP.md`](BOOTSTRAP.md) §3）：

- **DSA 的 Canvas 公告全是去年複製過來的**，例如「Final Exam December 8 (Monday)」是舊的。沒有真的發布的公告不算數。
- Canvas 行事曆裡混著往年的作業。這裡只採用 2026-09-01 以後的項目。
- DSA 的上課事件全部標「Zoom」，連週一的實體課也一樣，地點欄不可信。
- DSA Canvas 上的 Midterm 和 Final 只代表考試時段，**實際上是實體紙筆考**。
- GPU L1 投影片寫 Zoom，實際用 Teams；開始時間後來改成 6:30 PM。GPU 課表註明「subject to some revision」，可能會變。

筆記和報告都盡量附上出處（逐字稿時間戳、投影片頁碼、Piazza 編號），有疑問時回去看原始來源。

## 想自己架一套

整個 repo 是照 [`BOOTSTRAP.md`](BOOTSTRAP.md) 建起來的。裡面有每個平台查證過的抓取方法，也寫了哪些路線不能用。大致需要：

- Claude desktop app（排程任務）
- Node.js 和 Playwright CLI（`npm install -g @playwright/cli@latest`，再在 repo 裡執行 `playwright-cli install --skills`）
- Python 3、`gh` CLI、PowerShell 7
- 從 Canvas 的 Calendar → Calendar Feed 取得自己的 ICS 網址，照 [`.env.example`](.env.example) 放進 `.env`
- 改 `courses.yaml` 裡的帳號、repo、dashboard 設定（`hub` 段）。換帳號的步驟在 [`automation/MIGRATION.md`](automation/MIGRATION.md)
- 課程 id、課表、`courses.yaml` 和 BOOTSTRAP 裡寫的 GitHub repo 名稱都是我的，要換成你自己的

注意兩門課的 AI 政策：GPU 不能用 AI 產生作業解答或專題內容。DSA 不能把 starter code 交給 AI，用了 AI 要附上 chat session 或註明。
