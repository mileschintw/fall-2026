# 排程任務的共同收尾（每個任務最後都要做）

目的：使用者只要看一個地方，就知道每次排程跑了什麼、有沒有新東西。
- 電腦上看 repo 的 `digests/INDEX.md`。
- 手機或瀏覽器看 pinned dashboard：https://claude.ai/artifact/VaemajpQyP77JKSwxha8MG

## 1. 登記這次執行（必做）
```
python scripts/log_run.py --task <晨報|週規劃|截止提醒|上課筆記> --status <new|ok|skip|warn|fail> --summary "<一句話重點>" --output <輸出檔相對路徑或留空>
```
- `--status`：
  - `new`：有新東西，例如新公告、新作業、新錄影、新筆記、有推播的提醒
  - `ok`：正常，沒有新東西
  - `skip`：跳過，例如錄影還沒發布
  - `warn`：部分來源失敗，或需要重新登入
  - `fail`：失敗
- `--summary`：最多 60 字，寫具體內容，例如「A3 剩 24h；Piazza 新 2 篇（老師答 @47）」。沒有新東西就寫「沒有新東西」。
- 這個指令會寫進 `state/runs.json`，並重新產生 `digests/INDEX.md`。**不要手改 INDEX.md。**

## 2. 更新 dashboard（必做；失敗不影響第 1 步）
dashboard 的資料是兩個檔案：`state/runs.json` 和 `state/deadlines.json`。晨報如果從 Canvas 看到繳交狀態或 `due_at` 變了，要先用 Edit 改 `state/deadlines.json` 裡對應 `canvas_id` 那一列的 `status` / `done` / `due` / `due_label`。
1. 上傳 runs.json。用 Artifact 工具：`action: "publish"`、`url: "https://claude.ai/artifact/VaemajpQyP77JKSwxha8MG"`、`file_path: "D:\Repos\fall-2026\state\runs.json"`、`asset: true`。記下回傳的 `/_blob/<id>`。
2. 有改 deadlines.json 的話，用同樣方式上傳 `state\deadlines.json`。JSON 檔一次只能上傳一個，所以要分兩次呼叫。
3. 用 ArtifactData（沒有載入就先用 ToolSearch 載入）指向同一個 url：
   - `get` collection `datasets` 的 `runs`，必要時也 `get` `deadlines`，記下 `version`，以及舊的 `source.url`。
   - 用 `batch` 做 `update`，每筆都帶 `if_version`，更新：`source: {kind: "file", url: "<新的 /_blob/...>", name: "runs.json"}` 和 `updated: {at: "<現在的 ISO 時間>", by: "排程：<任務名>"}`。
4. 用 Artifact 工具刪掉舊的 asset：`action: "delete"`、`url` 同上、`path: "<舊 source.url 去掉 /_blob/ 的 id>"`。刪除失敗就略過。
5. 不要動 dashboard 的 `files/index.html` 和 `dash/meta`。
6. 如果 Artifact 或 ArtifactData 工具不存在或呼叫失敗：不重試，把第 1 步重跑一次，`--status warn`，`--summary` 寫「dashboard 沒更新：<原因>」。這一列會取代原本那列成為最新紀錄，原本那列保留。

## 3. 推播
狀態是 new、warn、fail 時，用 PushNotification 送一則：`[<任務名>] <一句話重點>`。截止提醒照它自己的規則推播，這一步不重複送。使用者正在用電腦時，推播可能送不出去，這沒關係，INDEX.md 和 dashboard 才是正本。

## 4. 不 commit、不 push。
