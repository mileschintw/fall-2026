# 排程任務的共同收尾（每個任務最後都要做）

目的：使用者只要看一個地方，就知道每次排程跑了什麼、有沒有新東西。
- 電腦上看 repo 的 `digests/INDEX.md`。
- 手機或瀏覽器看 pinned dashboard。網址**不寫死**，每次都用 `python scripts/hub_config.py dashboard_url` 取得（設定在 `courses.yaml` 的 `hub.dashboard_url`）。下面寫的 `<DASHBOARD_URL>` 都是指這個值。

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
dashboard 的資料是兩個檔案：`state/runs.json` 和 `state/deadlines.json`（晨報會先把 Canvas 的變動寫進 `state/deadlines.json`）。
下面每一步對 `runs` 做一次；這次有改 `state/deadlines.json` 的話，對 `deadlines` 也做一次（兩個資料集各自上傳、各自更新、各自刪舊檔）。
1. 上傳。用 Artifact 工具：`action: "publish"`、`url: "<DASHBOARD_URL>"`、`file_path: "D:\Repos\fall-2026\state\<runs|deadlines>.json"`、`asset: true`。JSON 檔一次只能上傳一個，所以兩個要分兩次呼叫。記下回傳的 `/_blob/<id>`。
2. 用 ArtifactData（沒有載入就先用 ToolSearch 載入）指向同一個 url，`get` collection `datasets` 的 `runs`（和 `deadlines`）。記下各自的 `version`，以及舊的 `source.url`。
3. 用一個 `batch` 做 `update`，每筆都帶自己的 `if_version`，更新：`source: {kind: "file", url: "<這個資料集新的 /_blob/...>", name: "<runs|deadlines>.json"}` 和 `updated: {at: "<現在的 ISO 時間>", by: "排程：<任務名>"}`。
4. 用 Artifact 工具刪掉每個資料集舊的 asset：`action: "delete"`、`url` 同上、`path: "<舊 source.url 去掉 /_blob/ 的 id>"`。刪除失敗就略過。
5. 不要動 dashboard 的 `files/index.html` 和 `dash/meta`。
6. 如果 Artifact 或 ArtifactData 工具不存在或呼叫失敗，或者回傳 artifact 不存在／沒有權限（例如換了 claude.ai 帳號，見 `automation/MIGRATION.md`）：不重試，把第 1 步重跑一次，`--status warn`，`--summary` 寫「dashboard 沒更新：<原因>」。這一列會取代原本那列成為最新紀錄，原本那列保留。

## 3. 推播
狀態是 new、warn、fail 時，用 PushNotification 送一則：`[<任務名>] <一句話重點>`。截止提醒照它自己的規則推播，這一步不重複送。使用者正在用電腦時，推播可能送不出去，這沒關係，INDEX.md 和 dashboard 才是正本。

## 4. Commit 並 push（必做）
這一步最後做。如果第 2 步失敗、重跑過第 1 步，重跑那次的登記也要一起 commit。
1. 先跑 `git -C D:\Repos\fall-2026 branch --show-current`。如果不是 `master`，就不 commit，最後一句回報「沒有 commit：目前在 <branch>」。
2. 只 stage 這次執行**自己寫或改過**的檔案（各任務 prompt 最後列了可能改的檔案，用 `git status --short` 確認哪些真的有變動），再加上 `state/runs.json`、`digests/INDEX.md`：
   ```
   git -C D:\Repos\fall-2026 add -- <這次寫或改的檔案…> state/runs.json digests/INDEX.md
   ```
   不要用 `git add -A`、`git add .` 或 `git commit -a`。使用者可能有自己還沒 commit 的修改，別的排程任務也可能同時在跑。
3. 用 `git diff --cached --stat` 檢查一下。如果沒有 staged 的內容，就跳過 commit。staged 內容裡絕對不能有 `.env`、ICS 網址或 SharePoint tempauth 連結（見 CLAUDE.md 的「密鑰」）。
4. commit 訊息寫成一行：`<任務名> <MM/DD HH:MM> PT: <和 log_run 相同的 summary>`，例如 `晨報 10/19 07:08 PT: GPU HW1 明天 5:59 PM 到期未交`。
5. 如果 commit 失敗（例如 `index.lock` 已經存在，或被 hook 擋下）：不重試、不加 `--no-verify`、不 amend，最後一句回報失敗原因，也不要 push。檔案留在 working tree，下次執行時一起 commit，或由使用者處理。
6. commit 成功後 push：`git -C D:\Repos\fall-2026 push origin master`。之前沒推上去的 commit 也會一起推上去。
   - 被拒絕（遠端比本機新，non-fast-forward）、沒網路或驗證失敗：不重試、不 `--force`、不 pull／rebase／merge，最後一句回報「push 失敗：<原因>」。commit 留在本機，下次執行會一起推。
   - 只推 `master` 到 `origin`，不推別的 branch 或 tag。
