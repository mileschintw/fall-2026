你是 Fall 2026 學期中樞的週規劃任務。工作目錄 D:\Repos\fall-2026（本機時區 America/Los_Angeles）。先讀 CLAUDE.md 並遵守（繁體中文、術語英文、時間標 Pacific）。
1. 執行 `python scripts/ics_fetch.py --days 8 --json state/ics.json`，再讀 gpu/assignments.md、dsa/assignments.md、dsa/repos.md。
2. 寫 digests/<今天日期>-weekly.md：下週（週一到週日）每天的課與截止項目；每個作業給建議開始時間（GPU HW 至少提前 4 天，記得 AWS WorkSpaces 每週 15 小時、單次 4 小時上限；DSA 作業至少提前 3 天，push 之後還要到 Canvas 交 repo URL）；列出 7 天內的固定提醒（11/9 DSA 期中實體 Moore 220、11/17 GPU Proposal、12/1 Design Spec、12/9 DSA 期末實體、12/15–17 發表、12/17 Final Report 不能延期）。
3. 若 ICS 失敗，寫明原因，不要把空結果當成沒有作業。不 commit、不 push、不發文。最後一句回報檔案路徑。

最後照 `automation/_finish.md` 做共同收尾：用 `scripts/log_run.py` 登記、更新 dashboard、有新東西就推播。
