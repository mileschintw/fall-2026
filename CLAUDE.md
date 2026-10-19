# Fall 2026 學期中樞

## 基本規則
- 回覆用繁體中文，術語保留英文。時間一律標成 Pacific（America/Los_Angeles；2026-11-01 結束夏令時間，用 tz-aware 轉換，見 `scripts/tz.py`）。
- 課程對照：
  - `GPU = Canvas 1917398 + Teams/SharePoint og_EEP_524_A_B_-_GPU_Computing`
  - `DSA = Canvas 1917417 + Piazza muomkq9jzdj104 + GitHub uw-python-fall2026 + Panopto`
- 只處理上面兩門課，Canvas 其他課程一律忽略。詳細設定見 `courses.yaml`，完整背景見 `BOOTSTRAP.md`。
- 資料取得：內建瀏覽器（`mcp__Claude_Browser__*`）+ 使用者 cookie；排程用 Canvas ICS（`scripts/ics_fetch.py`）；DSA repo 用 `gh`。瀏覽器片段在 `scripts/browser/`。
- 排程任務的 prompt 正本在 `automation/`（`~/.claude/scheduled-tasks/*/SKILL.md` 只是指向這裡）。學期至今版的報告放 `digests/semester-to-date/`。

## 課程 AI 政策
使用者已明確表示不在意，照常協助，包括寫作業程式碼、讀 DSA 的 starter code 和 README。只有在碰到課程明文禁止的行為時，加一行提醒：
- GPU：用 AI 產生作業解答、專題報告或專題程式碼
- DSA：把 starter code 交給 AI；用了 AI 卻沒有附上 chat session 或註明

## 不代發訊息
不在 Piazza、Teams、Canvas 發文、回覆或繳交作業。

## 登入過期的處理
遇到 UW NetID 登入頁、Microsoft 登入頁、Canvas OAuth 確認頁、Piazza 登入頁時：
- 一律停下
- 在晨報標記「需要重新登入：<來源>」
- 不輸入密碼，不按授權
- 空結果絕不寫進檔案（登入過期 ≠ 沒有資料）

## 密鑰
這是使用者的 private repo，**記得越細越好**，不需要去識別化，也不需要塗掉原始資料（人名、email、Piazza access code、Zoom 連結、逐字稿原文都可以照記）。
只有兩種東西不寫進 repo，因為它們本身就是可以直接拿來存取資料的 bearer token：
- ICS 網址（放 `.env`）
- SharePoint 的 tempauth / `temporaryDownloadUrl` 連結（反正幾分鐘就失效）

## 資料可信度規則（BOOTSTRAP §3 原文）

來源互相矛盾時，依下列順序採信：

**老師在課堂上說的（字幕／逐字稿）> Piazza / Teams 上老師或 TA 的回覆 > Canvas 作業的 `due_at` > syllabus > 投影片 > Canvas 公告與行事曆**

1. **DSA 的 Canvas 公告全是去年（Au25）複製過來的**。特徵：`posted_at: null`、`created_at` 全在同一秒（2026-09-26T23:49）、內容提到「Final Exam December 8 (Monday)」、Slack 連結是 `eep590aaut25`。**規則：`posted_at` 是 null 的公告不算數。**
2. **ICS 和 calendar_events 裡混有往年的項目**：GPU 有 2024 的 HW2–4 和 Project；DSA 有 2025 的 A2–A5、「DS: Class」，以及 Ankit、Maohua Nie 的 OH。**規則：只採用 2026-09-01 以後的項目。** 另外，DSA 2026 年的上課事件全部標成「@Zoom Online Meeting」，連週一的實體課也一樣，**地點欄不可信**。
3. DSA L1 p11 寫「Final Exam on Tuesday of Finals Week, June 10, 2025, Online in Canvas」，是舊內容，老師已口頭更正。
4. DSA 在 Canvas 上的 Midterm（Classic Quiz）和 Final Exam（New Quizzes）只代表考試時段，**實際上是實體紙筆考**。
5. GPU L1 p10 寫「Zoom」是舊文字，實際用 Teams。GPU 的歡迎公告寫 6–9 PM，後來在 Teams 上改成 6:30。
6. GPU 的課表註明「subject to some revision」，每週都要重新比對。
7. **判斷登入過期**：
   - 現象：`/api/v1/*` 回 **404**，或回傳 HTML（JSON 解析錯誤「Unexpected token '<'」），而且 `location.origin` 不是目標網站。常見的是 `idp.u.washington.edu`、`login.microsoftonline.com`，或 Canvas 的 `/login/oauth2/confirm`。
   - 這代表**登入過期，不是沒有資料**。絕對不可以把空結果寫進檔案。
   - 每次抓資料前先檢查 `location.origin`。
8. `due_at` 是 UTC。11/1 之後換算成 Pacific 要用 UTC-8。例：`2026-11-07T07:59:59Z` 是 11/6 11:59 PM PST。ICS 裡全天型的項目（`VALUE=DATE`）只有日期，時間要到 Canvas 查。

