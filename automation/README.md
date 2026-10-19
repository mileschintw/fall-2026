# 排程任務的 prompt

Claude desktop app 的四個排程任務（app 的 Scheduled 頁面）都在這台電腦上、以 `D:\Repos\fall-2026` 為工作目錄執行。
任務本身登記在 `~/.claude/scheduled-tasks/<taskId>/SKILL.md`，這是 app 規定的位置，不能搬。那個檔案只剩一行，指向這裡的 prompt。**要改任務內容，改這個資料夾的檔案就好，會進 git。**排程時間和開關要在 app 裡改。

| taskId | prompt | 時間（Pacific） | 輸出 |
|---|---|---|---|
| fall-2026-morning-brief | [morning-brief.md](morning-brief.md) | 每天 07:00 | `digests/<日期>.md` |
| fall-2026-weekly-plan | [weekly-plan.md](weekly-plan.md) | 週日 21:00 | `digests/<日期>-weekly.md` |
| fall-2026-deadline-alert | [deadline-alert.md](deadline-alert.md) | 每天 08:00、18:00 | 推播 + `state/alerts_sent.json` |
| fall-2026-lecture-notes | [lecture-notes.md](lecture-notes.md) | 週二、三、四 10:00 | `<course>/lectures/<日期>/notes.md` |

## 學期至今版
排程產生的是日報和週報。要從開學到某一天的完整版本，在 session 裡說「做一份學期至今版」，輸出放在 `digests/semester-to-date/<日期>-{brief,plan,deadlines}.md`。第一份是 2026-10-18。
