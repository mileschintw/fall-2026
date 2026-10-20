# 換 claude.ai 帳號時的遷移步驟

> 對象：換帳號之後，在**新帳號**的 Claude desktop app 開一個 session，工作目錄設為 `D:\Repos\fall-2026`，權限模式選 **Bypass permissions**（排程任務會沿用建立時 session 的模式）。然後說「照 automation/MIGRATION.md 遷移」。
> 綁帳號的設定只有一處：`courses.yaml` 的 `hub` 段。讀取用 `python scripts/hub_config.py <key>`。

## 哪些東西會跟著換帳號、哪些不會

| 東西 | 存在哪裡 | 換帳號後 |
|---|---|---|
| repo（筆記、逐字稿、報告、state、腳本、prompt） | `D:\Repos\fall-2026` + GitHub `mileschintw/fall-2026` | 不受影響 |
| `.env`（ICS 網址） | 本機，gitignore | 不受影響 |
| `gh` 登入 | 本機 | 不受影響（和 claude.ai 帳號無關） |
| 記憶檔 | `~/.claude/projects/D--Repos-fall-2026/memory/` | 不受影響 |
| 排程的 prompt 檔 | `~/.claude/scheduled-tasks/<taskId>/SKILL.md`（只有一行，指向 `automation/<prompt>`） | 檔案還在，但新帳號的排程表看不到 |
| **排程表**（cron、開關、cwd、權限模式） | `%APPDATA%\Claude\claude-code-sessions\<帳號 ID>\<組織 ID>\scheduled-tasks.json` | **要重建**（第 1 步） |
| **dashboard**（claude.ai artifact） | 舊帳號名下，網址記在 `hub.dashboard_url` | **要重建**（第 2 步）；資料和頁面原始碼都在 repo |
| 內建瀏覽器的 UW / Microsoft / Piazza 登入 | desktop app 的瀏覽器 profile | 未查證；可能要重新登入（第 3 步） |
| 舊的 session 紀錄 | 舊帳號 | 留在舊帳號，不遷移 |

## 第 1 步：重建四個排程任務

1. 列出要建的任務：`python scripts/hub_config.py scheduled_tasks`。每一筆有 `id`、`title`、`cron`、`prompt`、`description`。
2. 舊的 `~/.claude/scheduled-tasks/<id>/` 資料夾可能讓同名 taskId 建立失敗。先整個移到 `~/.claude/scheduled-tasks-old/`（**移動，不要刪除**）。
3. 每一筆用 `mcp__scheduled-tasks__create_scheduled_task` 建立：`taskId` = `id`、`title`、`cronExpression` = `cron`、`description`，`prompt` 用下面的範本。`<prompt>` 換成該筆的檔名，`<任務名>` 換成晨報、週規劃、截止提醒或上課筆記：
   ```
   工作目錄 D:\Repos\fall-2026。讀 D:\Repos\fall-2026\automation\<prompt>，照它的內容執行（這是 Fall 2026 學期中樞的<任務名>任務；prompt 的正本放在 repo 裡）。檔案讀不到就停下，回報「automation/<prompt> 不存在」。
   ```
   截止提醒的最後一句改成：「檔案讀不到就用 PushNotification 推播『automation/deadline-alert.md 不存在』。」
4. 確認建立結果有寫「saved in Bypass permissions mode」。這台電腦的時區是 Pacific，cron 用本機時間，所以不用換算。
5. 驗證：`run_scheduled_task` 跑一次 `fall-2026-deadline-alert`。完成後檢查兩件事：
   - `digests/INDEX.md` 最上面多一列。
   - 用 `mcp__ccd_session_mgmt__get_session` 看那次 run，`cwd` 要是 `D:\Repos\fall-2026`。

   dashboard 還沒重建的話，這一列會是 ⚠️「dashboard 沒更新」，這是正常的。做完第 2 步再跑一次。

## 第 2 步：重建 dashboard

1. 用 Artifact 工具建立：`action: "publish"`、`type_url` = `python scripts/hub_config.py dashboard_type_url` 的值、`title: "Fall 2026 學期中樞"`、`auto_open: "after_first_write"`。記下回傳的新網址。
   - 如果 type_url 失效，先跑 `action: "quickstart"`、`intent: "other"`，用它推薦的 Dashboard type。
2. 上傳兩個資料檔。JSON 一次只能傳一個，所以分兩次呼叫：`action: "publish"`、`url` = 新網址、`asset: true`，`file_path` 分別是 `D:\Repos\fall-2026\state\deadlines.json` 和 `D:\Repos\fall-2026\state\runs.json`。記下兩個 asset id，也就是 `/_blob/` 後面那 32 碼。
3. 產生 store 文件，輸出到 scratchpad（傳 id 就好，不要傳 `/_blob/...`，Git Bash 會把開頭的斜線改寫成路徑）：
   ```
   python scripts/dashboard_bundle.py --out <scratchpad>/bundle --deadlines-blob <id> --runs-blob <id> --by "Claude（遷移）"
   ```
4. 用 ArtifactData `batch` 一次寫入四份文件，全部用 `op: "set"`，新建立的文件不用帶 `if_version`：
   - `dash/meta` ← `meta.json`
   - `datasets/deadlines` ← `deadlines.json`
   - `datasets/runs` ← `runs.json`
   - `files/index.html` ← `index.html.json`
5. 把 `courses.yaml` 的 `hub.dashboard_url` 改成新網址。如果 type 換了，`hub.dashboard_type_url` 也一起改。然後跑 `python scripts/log_run.py --rebuild`，讓 INDEX.md 的連結也更新。
   接著馬上 commit 這兩個檔案：`git -C D:\Repos\fall-2026 add -- courses.yaml digests/INDEX.md`，再 commit。一定要在第 7 步之前做：排程任務收尾時會自己 commit 並 push，但只 stage 它自己的檔案和 INDEX.md。如果 `courses.yaml` 還沒 commit，GitHub 上的 INDEX.md 會是新網址，`courses.yaml` 卻還是舊網址。
6. 用 Artifact `action: "pin"` 把新 dashboard pin 到側欄，再 `action: "open"` 給使用者看一次。
7. 回到第 1 步的驗證，再跑一次截止提醒，這次應該是 ✅ 或 🆕，不會是 ⚠️。這次執行會把第 5 步的 commit 一起 push 上去。
8. 確認 repo 裡沒有其他地方寫著舊網址：`grep -rn "claude.ai/artifact/" --exclude-dir=.git .`。只有 `courses.yaml` 和自動產生的 `digests/INDEX.md` 會出現網址，其他地方都用 `hub_config.py` 讀。
9. 第 8 步如果有修改，commit 並 push（`git -C D:\Repos\fall-2026 push origin master`）。排程任務每次收尾本來就會 push master，所以不需要另外問使用者。

舊的 dashboard 留在舊帳號，要不要刪由使用者決定。

## 第 3 步：內建瀏覽器的登入

用內建瀏覽器打開以下四個網址，每個都檢查 `location.origin`：
- https://canvas.uw.edu/courses/1917398
- https://piazza.com/class/muomkq9jzdj104
- https://uwnetid.sharepoint.com/sites/og_EEP_524_A_B_-_GPU_Computing
- https://uw.hosted.panopto.com/Panopto/Pages/Home.aspx

如果跳到登入頁（`idp.u.washington.edu`、`login.microsoftonline.com`、Piazza 登入），**停下來請使用者自己登入**，不代輸入密碼。Panopto 如果出現 Canvas OAuth 確認頁，也要由使用者自己按。

## 第 4 步：驗收清單
- [ ] 新帳號的 Scheduled 頁面有四個任務，時間和 `hub.scheduled_tasks` 一致
- [ ] 截止提醒手動跑一次，INDEX.md 和 dashboard 都多了一列
- [ ] 那次執行有 commit 並 push：`git -C D:\Repos\fall-2026 status -sb` 第一行沒有 `ahead`，GitHub 上也看得到那個 commit
- [ ] dashboard 已 pin，`hub.dashboard_url` 是新網址
- [ ] 四個瀏覽器來源都能讀到資料，不在登入頁
- [ ] 隔天早上 07:00 的晨報有產生，「資料來源狀態」那一段全部是通
