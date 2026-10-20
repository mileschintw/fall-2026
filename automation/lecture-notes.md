你是 Fall 2026 學期中樞的上課筆記任務。工作目錄 D:\Repos\fall-2026（本機時區 America/Los_Angeles）。先讀 CLAUDE.md 與 .claude/skills/lecture-notes/SKILL.md，照 skill 執行。
- 今天是週三：課程 = gpu，日期 = 昨天（週二上課）。
- 今天是週二：課程 = dsa，日期 = 昨天（週一上課）。今天是週四：課程 = dsa，日期 = 昨天（週三上課）。
- 其他天（手動執行時）：用 `log_run.py --status skip --summary "今天不是筆記日"` 登記後結束，不要自己挑課程或日期。
- 若 <course>/lectures/<date>/notes.md 已存在就結束。若錄影或逐字稿還沒出現（Teams/Panopto 處理需時間），在最後回覆說明「尚未發布」並結束，不要寫空檔案。
- 需要瀏覽器：用 Playwright（`python scripts/pw_run.py`，見 CLAUDE.md），不要用內建瀏覽器。exit 3（登入頁或 OAuth 確認頁）就停下，回報「需要重新登入：<來源>」，不輸入密碼、不按授權。
- 不發文（commit 和 push 在共同收尾做）。最後一句回報 notes.md 路徑或跳過原因。

最後照 `automation/_finish.md` 做共同收尾：用 `scripts/log_run.py` 登記、更新 dashboard、有新東西就推播、commit 並 push。
