# 排程任務的 prompt

Claude desktop app 的五個排程任務（app 的 Scheduled 頁面）都在這台電腦上、以 `D:\Repos\fall-2026` 為工作目錄執行。
任務本身登記在 `~/.claude/scheduled-tasks/<taskId>/SKILL.md`，這是 app 規定的位置，不能搬。那個檔案只剩一行，指向這裡的 prompt。**要改任務內容，改這個資料夾的檔案就好，會進 git。**排程時間和開關要在 app 裡改。

排程時間的正本在 `courses.yaml` 的 `hub.scheduled_tasks`；下表是方便閱讀的副本。

| taskId | prompt | 時間（Pacific） | 輸出 |
|---|---|---|---|
| fall-2026-morning-brief | [morning-brief.md](morning-brief.md) | 每天 07:00 | `digests/<日期>.md` |
| fall-2026-weekly-plan | [weekly-plan.md](weekly-plan.md) | 週日 21:00 | `digests/<日期>-weekly.md` |
| fall-2026-deadline-alert | [deadline-alert.md](deadline-alert.md) | 每天 08:00、18:00 | 推播 + `state/alerts_sent.json` |
| fall-2026-lecture-notes | [lecture-notes.md](lecture-notes.md) | 週二、三、四 10:00 | `<course>/lectures/<日期>/notes.md` |
| fall-2026-assignment-specs | [assignment-specs.md](assignment-specs.md) | 每天 07:30 | `<course>/hw/<slug>/`（`spec.md` 原文、原始 PDF、`README.md` 摘要） |

## 看結果
每次執行都會用 `scripts/log_run.py` 登記到 `state/runs.json`，再產生 [`digests/INDEX.md`](../digests/INDEX.md)，同時更新 pinned dashboard（網址在 `courses.yaml` 的 `hub.dashboard_url`，手機也能看）。有新東西時會推播。最後在 master 上 commit 這次執行改到的檔案，並 push 到 GitHub。dashboard 頁面原始碼在 [`automation/dashboard/index.html`](dashboard/index.html)。共同收尾規則見 [_finish.md](_finish.md)。

## 學期至今版
排程產生的是日報和週報。要從開學到某一天的完整版本，在 session 裡說「做一份學期至今版」，輸出放在 `digests/semester-to-date/<日期>-{brief,plan,deadlines}.md`。第一份是 2026-10-18。

## 換 claude.ai 帳號
排程表和 dashboard 都綁在 claude.ai 帳號上，換帳號時要重建。步驟見 [MIGRATION.md](MIGRATION.md)。

## 改 dashboard 頁面
1. 改 [`dashboard/index.html`](dashboard/index.html)。
2. 跑 `python scripts/dashboard_bundle.py --out <scratchpad> --page-only`。
3. 用 ArtifactData 先 `get` `files/index.html`，記下 `version`，再用 `set` 把它換成 `<scratchpad>/index.html.json`，記得帶 `if_version`。

dashboard 的資料（`state/runs.json`、`state/deadlines.json`）由排程收尾自動上傳，不用手動處理。
