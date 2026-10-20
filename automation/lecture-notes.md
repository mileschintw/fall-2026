你是 Fall 2026 學期中樞的上課筆記任務。工作目錄 D:\Repos\fall-2026（本機時區 America/Los_Angeles）。先讀 CLAUDE.md 與 .claude/skills/lecture-notes/SKILL.md，照 skill 執行。

1. 決定課程和日期：
   - 今天是週三：課程 = gpu，日期 = 昨天（週二上課）。
   - 今天是週二：課程 = dsa，日期 = 昨天（週一上課）。今天是週四：課程 = dsa，日期 = 昨天（週三上課）。
   - 其他天（手動執行時）：status skip，summary「今天不是筆記日」，直接跳到共同收尾。課程和日期只照上面的表決定。
2. `<course>/lectures/<date>/notes.md` 已經存在：status skip，summary「<COURSE> <date> 筆記已存在」，直接跳到共同收尾。
3. 照 skill 做。中途結束的情況：
   - 錄影或逐字稿還沒出現（Teams/Panopto 處理需時間）：status skip，summary「<COURSE> <date> 錄影尚未發布」，不寫空檔案。
   - `pw_run.py` exit 3（登入頁或 OAuth 確認頁）：status warn，summary「需要重新登入：<來源>」。不輸入密碼、不按授權。
   - 瀏覽器一律用 Playwright（`python scripts/pw_run.py`，見 CLAUDE.md），不用內建瀏覽器。
4. 完成：status new，summary 寫課程、日期和主題。這次寫的檔案（transcript、slides.txt、notes.md、`<course>/lectures/README.md`）都要 stage。

每一條路最後都照 `automation/_finish.md` 做共同收尾：用 `scripts/log_run.py` 登記、更新 dashboard、有新東西就推播、commit 並 push。不發文。最後一句回報 notes.md 路徑或跳過原因。
