# 學期中樞建置驗收報告（2026-10-18）

## 🔴 先看這兩件事
1. **DSA A2 今晚 10/18（日）11:59 PM PDT 到期。** Canvas 顯示 unsubmitted，`assignment-2-mileschintw` 只有老師的 Initial commit（預設分支是 `master`，不是 `main`）。如果你寫在本機還沒 push：先 push，**再到 Canvas 交 repo URL**。
2. **GPU HW1 10/20（二）5:59 PM PDT 到期**，Canvas 顯示 unsubmitted。L2 有提到：L1 投影片 p55 的 error-checking macro 語法有錯，HW1 會用到，要看 Files 裡的「lecture 1 updated」。
- 另外：**GPU Task 0**（自我介紹，10/9 截止）在 Canvas 也是 unsubmitted，lock 日是 12/18。它是在 Teams 的 Task 0 串回覆，再到 Canvas 交連結（online_url）。

## 各來源狀態

| 來源 | 狀態 | 證據 |
|---|---|---|
| Canvas API（瀏覽器 cookie） | ✅ 通 | origin `canvas.uw.edu`；GPU 作業 2、公告 2；DSA 作業 9、quiz 2、modules 12 |
| Canvas ICS（不用登入） | ✅ 通 | 原始 GPU 8 / DSA 126 筆（和 BOOTSTRAP 一致）；過濾後 GPU 2 / DSA 41；11/1 後的換算已確認（A5 `2026-11-07T07:59:59Z` → 11/06 11:59 PM PST） |
| GitHub（gh） | ✅ 通 | 4 個 repo：in-class-code、assignment-1/2/3 |
| GPU SharePoint 逐字稿 | ✅ 通 | L1、L2 的 VTT 都抓到了：254,150 / 332,408 字元，1897 / 2554 cues，SHA-256 和瀏覽器端一致 |
| DSA Panopto 字幕 | ✅ 通（**不需要 OAuth**） | `Data.svc/GetSessions` 列出 6 個 session；5 堂課的 SRT 都存了（831–1066 cues），SHA-256 一致 |
| Piazza | ✅ 通 | feed 12 篇；已讀重點貼文，基準寫在 `dsa/piazza/` |
| Teams General | ✅ 通（只讀 UI） | 載入約 12 秒；讀到 7 則頂層貼文，基準寫在 `gpu/announcements/` |
| 排程任務 + 內建瀏覽器 | ✅ 通（有前提） | 手動觸發晨報，約 2 分鐘跑完，Canvas、Piazza、SharePoint、Teams 都讀到了，產出 `digests/2026-10-18.md` |
| GitHub private repo + push | ⏸ 等使用者 | 依 §9.10 還沒建，也還沒 push；本機已有一個 commit |

**排程的前提**：這次是在 app 開著、這個 session 也開著瀏覽器的情況下觸發的。早上 07:00 無人值守時會不會一樣，要看明天第一次自動執行的晨報，它的「資料來源狀態」那一段會寫明瀏覽器能不能用。如果不行，就退回 BOOTSTRAP §8 的兩層設計：排程只跑 ICS 和 gh（`scripts/digest_base.py` 本來就能獨立跑），瀏覽器的部分等你開 session 說「更新」時再抓。

## 和 BOOTSTRAP §2 的差異
- **GPU**：HW2 之後的作業在 Canvas 上都**還沒發布**（只有 Task 0 和 HW1）。HW1 的 `due_at` 和 §2 一致。Canvas 沒有新公告。
- **GPU L1 錄影**從 18:48 才開始錄，前面約 18 分鐘沒有逐字稿。
- **GPU L2**：老師口頭提到作業裡有 Gaussian blur，但 HW1 的標題是 SAXPY / Matrix addition，去年 blur 是 HW2。已列為待釐清。
- **DSA**：所有日期和分數都和 §2 一致。Midterm 的 Classic Quiz 開放時段是 11/9 4:30–6:30 PM PST，Final 的 `due_at` 是 12/9 6:30 PM PST，和實體考試的時段吻合，考試設定沒有變。
- **DSA Panopto** 有 5 堂錄影，比 §4.4 多了 **Class 5（10/14）**。Class 1 在 Panopto 上的 StartTime 是 10/02（上傳時間），資料夾日期依 Canvas 用 9/30。
- **DSA 新教材**：Module 2 多了「Class 5 outline … runtimes.pdf」（file `154547849`），也就是 Piazza @44 說的上課筆記和 cheat-sheet。
- **DSA Canvas 公告**：3 則的 `posted_at` 全是 null，依規則不採用（和 §3.1 一致）。
- **Piazza**：@46（今天）有同學說 A2/A3 的 GitHub 邀請過期了。你的 A2、A3 repo 用 `gh` 都看得到，所以不受影響。

## 建好的東西
- `CLAUDE.md`（§7 的規則，加上 §3 原文）、`courses.yaml`、`.env`（ICS 網址，已 gitignore）、`.env.example`、`.gitignore`
- `gpu/assignments.md`、`dsa/assignments.md`、`dsa/repos.md`、公告與 Teams／Piazza 的基準
- 逐字稿：`gpu/lectures/2026-10-06|13/transcript.vtt` + `slides.txt`；`dsa/lectures/2026-09-30…10-14/transcript.srt`
- `/lecture-notes` skill（`.claude/skills/lecture-notes/SKILL.md`），用 GPU L2 試做了一份：`gpu/lectures/2026-10-13/notes.md`（254 行、80 個時間戳，抽查都對得上 VTT）
- 腳本：`scripts/tz.py`、`ics_fetch.py`、`digest_base.py`、`condense_transcript.py`、`save_browser_result.py`、`write_transcripts.py`、`github_assignments.ps1`、`browser/{canvas,sharepoint,sharepoint_list,panopto,piazza}.js`
- 排程任務（cron 用本機時間，這台電腦本來就設 Pacific）：

| 任務 | 時間 |
|---|---|
| 晨報 | 每天 07:00 |
| 週規劃 | 週日 21:00 |
| 截止提醒 | 每天 08:00、18:00，用 48h／24h 兩個門檻推播 |
| 上課筆記 | 週二、三、四 10:00 |

  四個任務都存成 **Bypass permissions** 模式，可以在 app 的 Scheduled 裡改。

**技術備註**：瀏覽器回傳的大型結果（VTT/SRT）會被 harness 存到 `tool-results/*.txt`，再用 `save_browser_result.py` 寫進 repo，內容不經過對話，所以不會轉錄出錯。Teams 的 `temporaryDownloadUrl` 沒有寫進任何檔案。

## 使用者待辦
1. **（今晚）** DSA A2：push，然後到 Canvas 交 URL。
2. **（10/20 前）** GPU HW1。順便確認 Task 0 要不要補交。
3. 決定 GitHub private repo 的名稱（預設 `fall-2026`），確認後我再 `gh repo create --private` 並 push。
4. 晨報時間是否維持 07:00 Pacific。
5. 讓電腦不要睡眠，或打開 app 的 keep-awake；Claude app 要一直開著。
6. 內建瀏覽器的 UW NetID 或 Microsoft 登入過期時，自己重新登入。
7. 明天看第一份自動晨報的「資料來源狀態」，確認無人值守時瀏覽器能不能用。
8. 關於 credential：就算你提供，我也**不能**代你輸入密碼登入或按 OAuth 授權，這條規則不能因為你同意就放寬。登入過期時請在瀏覽器裡自己登入，登入狀態會保留，之後的 session 和排程都能沿用。請不要把密碼貼到對話裡。
