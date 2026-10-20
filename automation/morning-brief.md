你是 Fall 2026 學期中樞的晨報任務。工作目錄是 D:\Repos\fall-2026（Windows，本機時區就是 America/Los_Angeles）。先讀 D:\Repos\fall-2026\CLAUDE.md 並遵守（繁體中文、術語保留英文、時間標 Pacific、不代發訊息、不輸入密碼、不按 OAuth 授權、密鑰不寫進 repo）。

步驟：
1. 執行 `python scripts/digest_base.py`，取得無需登入的段落（到期、今天的課、新 repo、ICS/gh 狀態）。
2. 瀏覽器層（內建瀏覽器 mcp__Claude_Browser__*；先載入 skill anthropic-skills:built-in-browser）。每個來源先檢查 location.origin，遇到登入頁（idp.u.washington.edu、login.microsoftonline.com、canvas.uw.edu/login/oauth2/confirm、piazza 登入頁）就停，標「需要重新登入：<來源>」，絕不把空結果當成沒有資料：
   a. Canvas：用 preview_start 開 https://canvas.uw.edu/courses/1917398 ，在該分頁用 javascript_tool 跑 scripts/browser/canvas.js 的內容（結果大時 harness 會存到 tool-results 檔，用 python 讀）。和 state/canvas_seen.json 比對並報告：
      - posted_at 在過去 24 小時內、且非 null 的公告（id 不在 gpu_announcement_ids）；
      - 新的作業 id 或 due_at 變動（和 gpu/assignments.md、dsa/assignments.md 比對；有變動就更新這兩個檔）；
      - 繳交狀態：每個作業的 `sub`（含已過截止的）和 state/deadlines.json 同 `canvas_id` 那一列比對。`submitted` / `pending_review` → `status: "已交"`、`done: true`；`graded` → `status: "已評分"`、`done: true`（原本已寫分數就保留）；`unsubmitted` 不動。以 Canvas 為準，不另外標遲交。有變動就同步改 gpu/assignments.md、dsa/assignments.md 的「繳交狀態」欄，並在晨報列出；
      - GPU 新檔案（files 的 id 不在 gpu_file_ids，例如新講義 PDF、新 HW 說明）；
      - DSA 新 module item（item_id 不在 dsa_module_item_ids；ExternalTool = 新錄影、File = 新講義/筆記、Page = 新說明頁）；
      - syllabus_len 和基準不同 → 標「syllabus 有修改，請人工比對」。
      報告後把新 id 加回 state/canvas_seen.json。
   b. Piazza：開 https://piazza.com/class/muomkq9jzdj104 ，跑 scripts/browser/piazza.js 第 1 段列出 feed，和 state/piazza_seen.json 比對，新的 cid 逐篇開 /post/<cid> 讀（等 Rendering markdown 消失），摘要老師／TA 回覆；把新 cid 加進 state/piazza_seen.json。
   c. GPU SharePoint：開 https://uwnetid.sharepoint.com/sites/og_EEP_524_A_B_-_GPU_Computing/Shared%20Documents/Forms/AllItems.aspx ，跑 scripts/browser/sharepoint_list.js，和 state/sharepoint_seen.json 的 latest_created 比對，報告新錄影（Recordings/*.mp4）與頻道新活動（.loop、截圖所在頻道），更新 state/sharepoint_seen.json。
   d. Panopto（DSA 錄影）：開 https://uw.hosted.panopto.com/Panopto/Pages/Home.aspx ，先設 window.LIST_ONLY=true 再跑 scripts/browser/panopto.js，DeliveryID 不在 state/canvas_seen.json 的 panopto_delivery_ids 就是新錄影，報告並加入。
   e. Teams General 貼文只在時間允許時讀（teams.microsoft.com/v2/ 載入 8–15 秒，虛擬捲動），與 gpu/announcements/teams-general-baseline-2026-10-18.md 比對只報新的。
3. 合併成 digests/<今天日期>.md，格式：
   # YYYY-MM-DD 晨報
   ## 🔴 今明兩天到期
   ## 📢 新公告（依課程）
   ## 💬 討論重點（過去 24h，含老師 / TA 的關鍵回覆）
   ## 🆕 新作業 / 新教材 / 新錄影 / 新 repo
   ## 📅 今天的課（地點 / 線上）
   ## ⚠️ 資料來源狀態（每個來源標 通 / 不通 / 需要重新登入，附一行證據，例如筆數或 HTTP 狀態；**明確寫出內建瀏覽器工具在這次排程執行中是否可用**）
4. 不 push、不在任何平台發文（commit 在共同收尾做）。最後一句回報：晨報路徑、各來源狀態一行摘要。

最後照 `automation/_finish.md` 做共同收尾：用 `scripts/log_run.py` 登記、更新 dashboard、有新東西就推播、commit（不 push）。
