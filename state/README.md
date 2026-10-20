# state/
抓取狀態（給排程與晨報比對「新增」用）。不放密鑰。
- `ics.json` — 最近一次 ICS 抓取結果（已過濾 2026-09-01 之前）
- `canvas_seen.json` — 已看過的 Canvas id（兩門課的公告、作業、GPU 檔案、DSA module item、Panopto DeliveryID）和 syllabus 長度
- `seen_repos.json` — 已看過的 uw-python-fall2026 repo
- `piazza_seen.json` — 已看過的 Piazza cid
- `teams_seen.json` — GPU Teams General 已報過的 thread id → reply id（都是建立時間的 epoch ms，來自 `scripts/browser/teams_general.js`），`as_of` 是上次讀取時間
- `sharepoint_seen.json` — GPU SharePoint 檔案清單的最新 Created
- `alerts_sent.json` — 截止提醒已推播的 (項目, 門檻)
- `last_digest_base.json` — 上次晨報無需登入部分的來源狀態
- `assignment_specs.json` — 已存的作業說明：每個 Canvas 作業 id 對應的資料夾、來源指紋（說明文字 hash、檔案 updated_at、repo README sha、due_at）、`summary_done`（README.md 摘要寫好了沒）和變動紀錄。由 `scripts/assignment_specs.py` 維護
