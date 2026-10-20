你是 Fall 2026 學期中樞的晨報任務。工作目錄是 D:\Repos\fall-2026（Windows，本機時區就是 America/Los_Angeles）。先讀 D:\Repos\fall-2026\CLAUDE.md 並遵守（繁體中文、術語保留英文、時間標 Pacific、不代發訊息、不輸入密碼、不按 OAuth 授權、密鑰不寫進 repo）。

步驟：
1. 執行 `python scripts/digest_base.py`，取得無需登入的段落（到期、今天的課、新 repo、ICS/gh 狀態）。它會改寫 `state/last_digest_base.json` 和 `state/seen_repos.json`。
2. 瀏覽器層：a–e 五個來源全部都要跑，用 Playwright（`python scripts/pw_run.py <scripts/browser/片段> state/_<名>.tmp --url <URL>`）。不用內建瀏覽器 mcp__Claude_Browser__*，它開不了 UW 登入頁。
   - pw_run.py 一次跑一個，等上一個結束再跑下一個。所有呼叫共用同一個瀏覽器分頁，同時跑會互相把頁面導走（pw_run.py 也會讓後來的呼叫排隊等）。
   - exit 3：登入過期（被導到 idp.u.washington.edu、login.microsoftonline.com、canvas.uw.edu/login/oauth2/confirm 或 Piazza 首頁的登入框）。該來源標「需要重新登入：<來源>」並跳過。排程中不開登入視窗。
   - exit 1（例如 EMPTY_FEED、NOT_LOADED、snippet error、playwright-cli not found）：同一個指令重跑一次；還是失敗就標「不通」，證據寫錯誤訊息的第一行。
   - 失敗或需要重新登入的來源，它的 `state/*_seen.json` 不動：空結果不是沒有資料，下次會補報。
   - 讀完的 state/_*.tmp 用完就刪。
   a. Canvas：`python scripts/pw_run.py scripts/browser/canvas.js state/_canvas.tmp --url https://canvas.uw.edu/courses/1917398`（一次回傳兩門課，key 是 `1917398`、`1917417`）。用 python 讀 state/_canvas.tmp，和 state/canvas_seen.json 比對並報告：
      - 新公告：`ann` 的 id 不在 `gpu_announcement_ids`／`dsa_announcement_ids`（canvas.js 已經濾掉 posted_at 是 null 的去年公告）；
      - 新作業：`asg` 的 id 不在 `gpu_assignment_ids`／`dsa_assignment_ids`。報告，並在 gpu/assignments.md 或 dsa/assignments.md 和 state/deadlines.json 各加一列；
      - due_at 變動：`asg` 的 due_at 換成 Pacific 後，和 state/deadlines.json 同 `canvas_id` 那一列的 `due` 不同。報告，並改那一列的 `due`、`due_label`，以及 assignments.md 對應的列；
      - 繳交狀態：每個作業的 `sub`（含已過截止的）和 state/deadlines.json 同 `canvas_id` 那一列比對。`submitted` / `pending_review` → `status: "已交"`、`done: true`；`graded` → `status: "已評分"`、`done: true`（原本已寫分數就保留）；`unsubmitted` 不動。以 Canvas 為準，不另外標遲交。有變動就同步改 gpu/assignments.md、dsa/assignments.md 的「繳交狀態」欄，並在晨報列出；
      - GPU 新檔案（files 的 id 不在 gpu_file_ids，例如新講義 PDF、新 HW 說明）；
      - DSA 新 module item（item_id 不在 dsa_module_item_ids；ExternalTool = 新錄影、File = 新講義/筆記、Page = 新說明頁）；
      - syllabus_len 和 `syllabus_len.gpu`／`syllabus_len.dsa` 不同 → 標「syllabus 有修改，請人工比對」。
      報告後更新 state/canvas_seen.json：新的 id 加進上面五個清單，`syllabus_len` 換成這次的值，`as_of` 改成今天日期。
   b. Piazza：`python scripts/pw_run.py scripts/browser/piazza.js state/_piazza.tmp --url https://piazza.com/class/muomkq9jzdj104` 列出 feed，和 state/piazza_seen.json 比對。新的 cid 逐篇用 `python scripts/pw_run.py scripts/browser/piazza_post.js state/_post.tmp --url https://piazza.com/class/muomkq9jzdj104/post/<cid>` 讀（一篇讀完再讀下一篇）。每篇報：編號、標題、一句話摘要；老師（Adrienne Slaughter）和 TA（Hongyu）的回覆寫出內容。報告後把新 cid 加進 state/piazza_seen.json。
   c. GPU SharePoint：`python scripts/pw_run.py scripts/browser/sharepoint_list.js state/_sp.tmp --url "https://uwnetid.sharepoint.com/sites/og_EEP_524_A_B_-_GPU_Computing/Shared%20Documents/Forms/AllItems.aspx"`。Created 晚於 state/sharepoint_seen.json 的 latest_created 就是新的：報告新錄影（Recordings/*.mp4）與頻道新活動（.loop、截圖所在頻道），再把 latest_created 改成這次最大的 Created。
   d. Panopto（DSA 錄影）：`python scripts/pw_run.py scripts/browser/panopto.js state/_panopto.tmp --pre "window.LIST_ONLY=true" --url https://uw.hosted.panopto.com/Panopto/Pages/Home.aspx`。DeliveryID 不在 state/canvas_seen.json 的 panopto_delivery_ids 就是新錄影，報告並加入。
   e. Teams GPU General：`python scripts/pw_run.py scripts/browser/teams_general.js state/_teams.tmp --url https://teams.cloud.microsoft/`（網址就用這個，teams.microsoft.com/v2/ 載入後會再轉址，執行會中斷）。和 state/teams_seen.json 比對：
      - thread `id` 不在 `threads` → 新貼文，報作者、時間、標題（沒標題就用內文第一行）、重點；
      - reply `id` 不在該 thread 的清單，而且 `at` 晚於 `as_of` → 新回覆，報作者、時間、重點。老師（Colin N Reinhardt）和 TA（Diya Shetty、Devika Nair）的回覆要寫出內容；同學的回覆只寫人數和主題；
      - 作者是空的、內文是「This message has been deleted」或「已刪除此訊息」的 reply 不報。
      報告後把這次所有的 thread id 和 reply id 加回 state/teams_seen.json，`as_of` 改成這次輸出的 `now`。Teams 只載入最近有動靜的幾個 thread，每個 thread 也只顯示最後 3 則回覆，所以如果某個 thread 的 3 則回覆全都是新的，要註明「可能還有更早的新回覆沒載入」。
3. 合併成 digests/<今天日期>.md。
   - 檔案已經存在（同一天手動重跑）：保留原檔每段的內容，把這次的新發現加在對應段落最後，前面標「（HH:MM 更新）」；「今明兩天到期」「今天的課」「資料來源狀態」三段整段換成這次的結果。
   - 下面每個段落都要寫，沒有內容就寫「無」，不要刪掉段落；來源失敗造成的空白寫「（<來源> 不通，見資料來源狀態）」，不要寫「無」。格式：
   # YYYY-MM-DD 晨報
   ## 🔴 今明兩天到期
   ## 📢 新公告（依課程）
   ## 💬 討論重點（過去 24h，含老師 / TA 的關鍵回覆）
   ## 🆕 新作業 / 新教材 / 新錄影 / 新 repo
   ## 📅 今天的課（地點 / 線上）
   ## ⚠️ 資料來源狀態（Canvas、Piazza、GPU SharePoint、Panopto、Teams、ICS GPU、ICS DSA、gh 八個來源每個都要列，標 通 / 不通 / 需要重新登入，附一行證據，例如筆數或 HTTP 狀態；**明確寫出 Playwright（pw_run.py）在這次排程執行中是否可用**）
4. 不在任何平台發文（commit 和 push 在共同收尾做）。最後一句回報：晨報路徑、各來源狀態一行摘要。

這次執行可能寫或改的檔案（共同收尾 stage 時，只加其中真的有變動的）：digests/<今天日期>.md、state/last_digest_base.json、state/seen_repos.json、state/canvas_seen.json、state/piazza_seen.json、state/sharepoint_seen.json、state/teams_seen.json、state/deadlines.json、gpu/assignments.md、dsa/assignments.md。

最後照 `automation/_finish.md` 做共同收尾：用 `scripts/log_run.py` 登記、更新 dashboard、有新東西就推播、commit 並 push。
