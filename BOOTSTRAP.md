# Fall 2026 學期中樞：啟動文件（Bootstrap）

> 版本：2026-10-18。取代 `fall-2026-hub-plan.md`。
> 這份文件是交給新的 agent，一次性把學期中樞建起來用的。
> 裡面的事實是 2026-09-30 到 10-18 之間，實際登入 Canvas、Teams/SharePoint、Piazza、Panopto、GitHub 查證過的。查證不了的標 **【未驗證】**。
> Repo 位置：`D:\Repos\fall-2026`（目前是空資料夾，還沒 `git init`）。

---

## 0. 開場 prompt（貼到新 session）

```
請讀 repo 根目錄的 BOOTSTRAP.md，照第 9 節「建置步驟」把學期中樞一次建好。
規則：
- 第 1–5 節是已查證的事實與做法，直接採用。資料互相衝突時，用第 3 節的可信度規則判斷。
- 需要我本人做的事（UW NetID 登入、OAuth 授權）不要代做。碰到就停在那一步，把它列進最後的待辦清單，然後繼續做其他不受影響的步驟。
- 不用每一步都等我確認。全部做完後給我一份驗收報告：哪些通了、哪些因為缺我的動作而跳過。
- 回覆用繁體中文，術語保留英文。
```

---

## 1. 範圍、環境與限制（已查證）

**只追蹤兩門課**（以 Canvas 為主）：

| 簡稱 | Canvas ID | 課名 | 其他管道 |
|---|---|---|---|
| **GPU** | `1917398` | EE P 524 A Au 26: Applied High-Performance GPU Computing | MS Teams（含 SharePoint 上的錄影與逐字稿） |
| **DSA** | `1917417` | EE P 590 A Au 26: Advanced Topics In Digital Computers（實際內容是 Data Structures, Algorithms & Python） | Piazza、GitHub、Panopto |

Canvas 選課清單裡還有 Graduate Seminar、舊課、非課程項目，**全部忽略**，只處理上面兩個 ID。

| 項目 | 值 |
|---|---|
| 學校 | University of Washington（UW），Autumn 2026（Canvas term id `4608`） |
| Canvas | `https://canvas.uw.edu` |
| 時區 | `America/Los_Angeles`。**2026-11-01 夏令時間結束**，UTC 偏移從 -7 變成 -8。一律用 tz-aware 轉換，不要寫死偏移量 |
| 電腦 | Windows 11。已有 Python 3.13、git、GitHub CLI 2.102（已登入，帳號 `mileschintw`） |
| 瀏覽器 | **Playwright CLI**（`playwright-cli -s=uw`，用系統的 Chrome），透過 `scripts/pw_run.py` 執行。登入狀態放在 `~/.fall-2026/`（repo 外面）。2026-10-20 起，Claude app 的內建瀏覽器（`mcp__Claude_Browser__*`）會擋 `idp.u.washington.edu`（直接打網址沒反應，轉址過去則顯示 `ERR_FAILED`；同一台電腦的 Chrome 和 curl 都正常，所以不是 UW 封鎖），**不要用** |
| 適用範圍 | 以上「已驗證」只對這台 PC 和這個 Claude app 成立。換電腦就要重新驗證第 1、4 節 |

### 已確認**不能用**的路線
- **Canvas access token**：UW 對學生鎖住了 New Access Token，**不能用 token 打 Canvas API**
- **Microsoft 365 connector**：UW 租戶要求 admin consent（「M365 MCP Client for Claude needs permission … only an admin can grant」），**不能用**
- **Piazza 內部 API** `/logic/api`：回「Request not valid」

### 因此資料取得只有三條路
1. **Playwright + 使用者的登入 cookie**：`scripts/pw_run.py` 在頁面裡執行 `scripts/browser/*.js`，片段再呼叫同源 API（用 CDP REPL mode，語意和 `javascript_tool` 相同）。適用 Canvas、SharePoint、Panopto、Piazza、Teams。這是主要管道
2. **Canvas 行事曆 ICS（不用登入）**：只有截止日與事件，但純 HTTP 就能抓，最適合排程
3. **`gh` CLI**：DSA 的作業 repo

---

## 2. 課程事實

### 2.1 GPU：EE P 524 A（Canvas `1917398`）

**人與管道**
- 老師 Colin Reinhardt（Prof R）；TA Diya Shetty、Devika Nair
- **全程線上**。L1 投影片 p5 寫「This Class = ALL ONLINE … via MS Teams」；10/7 TA 在 Teams 回覆「the course will be run completely online」
- 上課時間是週二 6:30–9:30 PM，Teams 公告寫到 9:50。地點是 Teams 會議「Weekly Live Lecture」
- Teams 團隊 `EEP 524 A/B - GPU Computing`，頻道有 General、AWS_Info_Issues、Hw0 Discussion、Hw1 Discussion，另有隱藏頻道
- 背後的 SharePoint 站台：`https://uwnetid.sharepoint.com/sites/og_EEP_524_A_B_-_GPU_Computing`
- **上課錄影**存在 SharePoint 的 `Shared Documents/General/Recordings/`，檔名格式 `Weekly Live Lecture-YYYYMMDD_HHMMSS-*.mp4`。每支約 0.9 GB，**附 Teams 逐字稿**（en-US）
  - 已有：20261006（Lecture 1）、20261013（Lecture 2）
- TA Office Hours：Diya，週一 6:30 PM，用 Teams 會議
- 課本是 PMPP 4th ed.（Hwu, Kirk, El Hajj），可從 UW Libraries / O'Reilly 線上閱讀。每週閱讀進度在 Canvas Page `weekly-reading-sets`
- 開發環境是 AWS WorkSpaces VDE，Turing T4、VS 2026、CUDA 13.x。**每週上限 15 小時，單次 4 小時，時間到 instance 會清空**

**時程**（syllabus 與 L1 p9–10 不一致的地方兩者並列）

| 項目 | 截止（Pacific） | 備註 |
|---|---|---|
| HW1 SAXPY, 2D & 3D Matrix addition | 10/20（二）5:59 PM | 11 分 |
| HW2 | 10/27（二）5:59 PM | 12 分 |
| HW3 | 11/3（二）5:59 PM | 12 分 |
| HW4 | 11/10（二） | 15 分；syllabus 寫 11:59 PM，投影片寫 5:59 PM |
| Project Proposal | 11/17（二） | 佔專題 10%；syllabus 寫 11:59 PM，投影片寫 5:59 PM |
| Project Design Spec | 12/1（二）5:59 PM | 佔專題 30% |
| Project 發表 | 12/15（二）～ 12/17（四） | 線上 |
| Project Final Report + Code | **12/17（四）11:59 PM，不能延期** | 佔專題 60% |

- 成績：HW 50%、Final Project 50%，**沒有考試**
- 遲交罰則：遲 1 天扣 1 分，之後每 24 小時再扣 1 分，到第 5 天累計 -6。第 10 天再扣 2 分，之後每 5 天扣 1 分
- 去年（2024）的 ICS 殘留了作業標題，可以當成預告，但**不是今年的正式資訊**：
  - HW2 Gaussian Blur Kernels
  - HW3 Control Divergence & Tiled MMULT improvements & NCU profiling
  - HW4 Memory access patterns & MMULT Corner Turning
- 課程 AI 政策：不可以用 AI 產生作業解答、專題報告或程式碼（使用者已知情，見第 7 節）

### 2.2 DSA：EE P 590 A（Canvas `1917417`）

**人與管道**
- 老師 Adrienne Slaughter（`ahandrew@uw.edu`，偏好用 Piazza 聯絡）；TA Hongyu（`hongyum@uw.edu`）
- 上課時間是週一、三 4:30–6:20 PM。**週一在 Moore Hall 220 實體上課，週三用 Zoom**（L1 p4 寫「Wednesdays: Zoom (unless there's a test!)」）。週一也開 Zoom
- Office Hours：老師週六 9:30–11:00，用 Zoom；TA 週二 6–8 PM
- Piazza class 是 `muomkq9jzdj104`，使用者已加入。access code 在 Canvas 的 Resources 模組，**不要寫進 repo**
- 錄影放在 Panopto，連結會加到 Canvas 對應的 Module，項目類型是 `ExternalTool`
- 教材是《Grokking Algorithms》，IDE 用 PyCharm。課堂程式碼在 `uw-python-fall2026/in-class-code`（公開 repo）

**作業機制**
- 不是 GitHub Classroom。填完 Canvas 的 Intro Survey 之後，老師用腳本直接邀請，產生 `uw-python-fall2026/assignment-<N>-mileschintw`（10/18 時已有 1–3）
- 繳交流程：push 到 GitHub，**再到 Canvas 交 repo URL**

**時程**

| 項目 | 截止（Pacific） | 分數 |
|---|---|---|
| A1 My First Python Assignment | 10/4（日）11:59 PM | 50 |
| A2 Lists, lists and more lists | 10/18（日）11:59 PM | 150 |
| A3 Stacks, Queues and Testing | 10/23（五）11:59 PM | 150 |
| A4 Bug Hunt | 10/30（五）11:59 PM | 100 |
| A5 BSTs and AVLs | 11/6（五）11:59 PM | 100 |
| **Midterm** | **11/9（一）4:30 PM，實體紙筆，Moore 220** | 100（佔總成績 15%） |
| A6 Heaps | 11/30（一）11:59 PM | 100 |
| **Final Exam** | **12/9（三）4:30 PM，實體紙筆，教室** | 120（佔總成績 20%） |
| A7 Surprise | 12/11（五）11:59 PM，**不能遲交** | 100 |

- 成績：作業 65%、期中 15%、期末 20%
- 停課：11/11（三，Veterans Day）、11/25（三，感恩節，可能改成非同步）
- 遲交（syllabus 和投影片不一致）：
  - syllabus：每學季可免一次，要事先告知、最多晚 1 週；其他每天扣 25%
  - 投影片：每天扣 25%，超過 4 天不收
- 課程 AI 政策：前 3 週禁用（已過）；之後可以用，但要附 chat session；**不可以把 starter code 貼進 AI**。使用者已知情，見第 7 節

**考試要到場的證據**（第一堂課 Panopto 自動字幕，時間是錄影中的位置）
- 51:45「The midterm is in person, in class on paper.」
- 53:05–53:18 期末考在最後一週上課，「not … during finals week … you do have to be here that last day of class.」
- 53:24–53:59「You have to be here in person.」「Do not ask me in December to move this.」
- 1:07:21–1:07:52 更正投影片：「It's actually a Wednesday … it is not online. It is not in canvas. It is on paper.」
- 1:40:55「Wednesday classes will be on zoom … except for … the last week where we have our test.」
- 12/9 這個日期老師只是順口說了一句「December 9th or whatever day that is」。實際日期是由 Canvas Final Exam 的開放時段（12/9 4:30–6:30 PM）和 L1 p7 的「Dec 7 Summary/Review, FINAL」對出來的

---

## 3. 資料可信度規則（重要）

來源互相矛盾時，依下列順序採信：

**老師在課堂上說的（字幕／逐字稿）> Piazza / Teams 上老師或 TA 的回覆 > Canvas 作業的 `due_at` > syllabus > 投影片 > Canvas 公告與行事曆**

1. **DSA 的 Canvas 公告全是去年（Au25）複製過來的**。特徵：`posted_at: null`、`created_at` 全在同一秒（2026-09-26T23:49）、內容提到「Final Exam December 8 (Monday)」、Slack 連結是 `eep590aaut25`。**規則：`posted_at` 是 null 的公告不算數。**
2. **ICS 和 calendar_events 裡混有往年的項目**：GPU 有 2024 的 HW2–4 和 Project；DSA 有 2025 的 A2–A5、「DS: Class」，以及 Ankit、Maohua Nie 的 OH。**規則：只採用 2026-09-01 以後的項目。** 另外，DSA 2026 年的上課事件全部標成「@Zoom Online Meeting」，連週一的實體課也一樣，**地點欄不可信**。
3. DSA L1 p11 寫「Final Exam on Tuesday of Finals Week, June 10, 2025, Online in Canvas」，是舊內容，老師已口頭更正。
4. DSA 在 Canvas 上的 Midterm（Classic Quiz）和 Final Exam（New Quizzes）只代表考試時段，**實際上是實體紙筆考**。
5. GPU L1 p10 寫「Zoom」是舊文字，實際用 Teams。GPU 的歡迎公告寫 6–9 PM，後來在 Teams 上改成 6:30。
6. GPU 的課表註明「subject to some revision」，每週都要重新比對。
7. **判斷登入過期**：
   - 現象：`/api/v1/*` 回 **404**，或回傳 HTML（JSON 解析錯誤「Unexpected token '<'」），而且 `location.origin` 不是目標網站。常見的是 `idp.u.washington.edu`、`login.microsoftonline.com`，或 Canvas 的 `/login/oauth2/confirm`。
   - 這代表**登入過期，不是沒有資料**。絕對不可以把空結果寫進檔案。
   - 每次抓資料前先檢查 `location.origin`。
8. `due_at` 是 UTC。11/1 之後換算成 Pacific 要用 UTC-8。例：`2026-11-07T07:59:59Z` 是 11/6 11:59 PM PST。ICS 裡全天型的項目（`VALUE=DATE`）只有日期，時間要到 Canvas 查。

---

## 4. 已驗證的取得方法

### 4.1 Canvas（瀏覽器 cookie）

在 `https://canvas.uw.edu/courses/<id>` 頁面執行（實際版本在 `scripts/browser/canvas.js`，用 `python scripts/pw_run.py scripts/browser/canvas.js <out> --url <URL>` 跑）：

```js
if (location.origin !== 'https://canvas.uw.edu') throw 'LOGIN_EXPIRED';
async function all(url){let out=[];while(url){const r=await fetch(url,{headers:{Accept:'application/json'}});
  if(!r.ok)return {err:r.status,url};out=out.concat(await r.json());
  const m=(r.headers.get('Link')||'').match(/<([^>]+)>;\s*rel="next"/);url=m?m[1]:null;}return out;}
const id=1917417, b='/api/v1/courses/'+id;
const course=await (await fetch(b+'?include[]=syllabus_body&include[]=tabs')).json();
const asg =await all(b+'/assignments?per_page=100');
const ann =await all(`/api/v1/announcements?context_codes[]=course_${id}&start_date=2026-09-01&end_date=2027-01-01&per_page=100`);
const mods=await all(b+'/modules?include[]=items&per_page=100');
const quiz=await all(b+'/quizzes?per_page=100');
const ev  =await all(`/api/v1/calendar_events?context_codes[]=course_${id}&all_events=true&start_date=2026-09-01&per_page=100`);
```

- 這些端點都測過可以用：`/courses/:id?include[]=syllabus_body`、`/tabs`、`/assignments`、`/announcements`、`/discussion_topics`、`/modules?include[]=items`、`/pages`、`/pages/:url`、`/files`、`/files/:id`、`/quizzes`、`/quizzes/:id`、`/calendar_events`、`/api/v1/courses?enrollment_state=active`
- GPU 課沒有 Modules，講義放在 Files（`/courses/1917398/files`）
- DSA 課的 `/courses/1917417/files` 會回 **403**。要先從 module items 取得檔案 ID，再用 `/api/v1/courses/1917417/files/<id>` 取得
- 已知的檔案 ID：
  - GPU：L1 `154353784`、L2 `154353786`、HW0 `154009274`、HW1 `154350654`
  - DSA：L1 `153729203`、Mod1 筆記 `153960101`。Mod1 筆記是手寫掃描，抽不太到文字

**PDF 轉文字**：在 Canvas 頁面裡載入 pdf.js（cdnjs 4.0.379）：

```js
const pdfjs=await import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs');
pdfjs.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs';
const meta=await (await fetch('/api/v1/courses/1917398/files/154353784')).json();
const doc=await pdfjs.getDocument({data:await (await fetch(meta.url)).arrayBuffer()}).promise;
```

**把資料存回 repo**：`pw_run.py` 會把片段最後一個 expression 的值直接寫成 JSON 檔，不經過聊天，再大也不用分批。

### 4.2 Canvas ICS（不用登入，排程首選）

- 每門課的 ICS 網址可以從 `/api/v1/courses?enrollment_state=active` 每筆的 `calendar.ics` 取得，格式是 `https://canvas.uw.edu/feeds/calendars/course_<uuid>.ics`
- 這個網址**帶有密鑰**。建置時用瀏覽器取得一次，存進 `.env`（`CANVAS_ICS_GPU`、`CANVAS_ICS_DSA`），**不要 commit**
- 10/18 驗證：`curl` 不帶 cookie 回 200 `text/calendar`。GPU 有 8 個事件，DSA 有 126 個
- 內容包含所有作業、考試的截止日，以及上課和 OH 事件。要套第 3 節第 2 條過濾往年項目
- 沒有公告、沒有作業說明

### 4.3 GPU 錄影與逐字稿（SharePoint，已驗證）

Teams 的錄影存在課程團隊的 SharePoint，可以用 cookie 呼叫 SharePoint REST 和 v2.1 API：

```js
// 在 https://uwnetid.sharepoint.com/sites/og_EEP_524_A_B_-_GPU_Computing/Shared%20Documents/Forms/AllItems.aspx 執行
const site='/sites/og_EEP_524_A_B_-_GPU_Computing', H={Accept:'application/json;odata=nometadata'};
// 1) 列出所有檔案（含錄影、頻道附件）
const files=await fetch(site+"/_api/web/GetListUsingPath(DecodedUrl=@a)/items?@a='"+site+"/Shared Documents'&$select=FileRef,Created,UniqueId&$top=500",{headers:H}).then(r=>r.json());
// 2) 取得 drive id 與錄影 item id
const drv=(await fetch(site+'/_api/v2.1/drives',{headers:{Accept:'application/json'}}).then(r=>r.json())).value[0].id;
const item=await fetch(site+`/_api/v2.1/drives/${drv}/root:/General/Recordings/<檔名>.mp4`,{headers:{Accept:'application/json'}}).then(r=>r.json());
// 3) 列出逐字稿，再抓內容（回傳 WEBVTT）
const tr=await fetch(site+`/_api/v2.1/drives/${drv}/items/${item.id}/media/transcripts`,{headers:{Accept:'application/json'}}).then(r=>r.json());
const vtt=await fetch(site+`/_api/v2.1/drives/${drv}/items/${item.id}/media/transcripts/${tr.value[0].id}/streamContent`).then(r=>r.text());
```

- 第 2 堂課的逐字稿約 330 KB，是 WEBVTT 格式，內容以「welcome everybody to lecture #2」開頭
- `streamContent?format=text/vtt` 會回 400，**不要加 format 參數**
- `transcripts` 回傳的 `temporaryDownloadUrl` 帶有臨時授權，**不要存進檔案或 log**
- 頻道裡的 Loop 段落（`.loop`）和截圖也在這個清單裡，可以用來偵測頻道有新活動

### 4.4 DSA 錄影與字幕（Panopto）

- 錄影在 Canvas Module 裡是 `ExternalTool` 項目，網址是 `https://uw.hosted.panopto.com/Panopto/LTI/LTI.aspx?custom_context_delivery=<id>`
- 這個 id **不是** Viewer 的 session id。例如第一堂課：LTI 是 `325acd77-…`，Viewer 是 `f8969af3-ca1a-45e7-8efb-b4d800392aba`
- 要取得 session id，就打開 LTI 項目，或打開 Canvas 的「Panopto Recordings」分頁（`/courses/1917417/external_tools/21130`），看 Viewer 網址上的 id
- 字幕（已驗證）：在 `uw.hosted.panopto.com` 的頁面上執行
  ```js
  await (await fetch('/Panopto/Pages/Transcription/GenerateSRT.ashx?id=<session-id>&language=0')).text()
  ```
  回傳 SRT（第一堂課約 98 KB），是自動字幕
- **登入**：Panopto 用 Canvas OAuth 登入，第一次會出現「Panopto is requesting access to your account」確認頁（`canvas.uw.edu/login/oauth2/confirm`）
  - **這一步要使用者自己按授權**，建議勾選 Remember my authorization
  - 10/18 時正卡在這一頁，還沒授權
- 已知錄影：Class 1（9/30）、Mod 1 週一與週三、Mod 2 週一，LTI 連結都在 modules 裡

### 4.5 Piazza（DSA 主要討論區）

- 列表頁：`https://piazza.com/class/muomkq9jzdj104`。用 `get_page_text` 可以拿到標題、摘要、日期
- 單篇：開 `…/post/<n>`，再用 `get_page_text`。貼文編號不連續，目前看到的有 @8–@12、@14、@36，有些編號打開是空白頁
- 座標點擊常因為 pane 沒繪製而逾時。改用 JS：找到標題文字所在的葉節點，往上找 `role="link"` 或 `<a>` 的祖先，再呼叫 `.click()`；也可以直接點 `[data-id="post_group_item"]`
- 截至 10/18 的內容：
  - 歡迎與課務公告
  - GitHub 邀請相關的問題
  - @10：Zoom 和 Panopto 錄影
  - Code from class（指向 in-class-code）
  - @36：Rules in hw3
- 自動化備案：在 Piazza 設定 email 通知。但信箱 connector 也被 UW 鎖住了，所以實際上只能靠瀏覽器

### 4.6 Teams 頻道貼文

- 網址 `https://teams.microsoft.com/v2/` 會轉到 `teams.cloud.microsoft`，載入要 8–15 秒。偶爾會出現「Language changes detected」橫幅，可以忽略
- 介面是虛擬捲動，`get_page_text` 只會拿到已經載入的貼文
- 討論串會摺疊成「Open N replies」，要點開再捲動。用 `find` 取得 ref 再點擊，比用座標可靠
- 頻道的「Shared」分頁是嵌在 iframe 裡的 SharePoint。檔案直接用第 4.3 節的方法讀，比較快
- 讀頻道貼文的 API **【未驗證】**，目前只能從 UI 讀

### 4.7 GitHub（已驗證）

```bash
gh repo list uw-python-fall2026 --limit 100 --json name,createdAt,url,visibility
```

出現新的 `assignment-<N>-*`，就代表有新作業。

---

## 5. 對舊計畫的修正

| 舊計畫 | 修正 |
|---|---|
| Canvas 網址 `______.instructure.com` | `https://canvas.uw.edu` |
| Canvas REST API + token | token 被鎖。改用瀏覽器 cookie，排程用 ICS |
| Microsoft 365 connector | 需要 admin 核准，不能用。GPU 的錄影和逐字稿改走 SharePoint API（4.3），貼文從 Teams UI 讀 |
| Piazza 用 email + 信箱 connector | 信箱 connector 也不能用。改從瀏覽器讀 Piazza |
| 時區例子 America/New_York | `America/Los_Angeles`，注意 11/1 結束夏令時間 |
| `~/Desktop/repos/fall-2026`、`~/.zshrc` | `D:\Repos\fall-2026`，Windows |
| GPU 作業「Teams / Canvas 待確認」 | 作業在 Canvas 上傳。公告在 Canvas 和 Teams |
| DSA 用 GitHub Classroom 的思路 | 是老師直接發邀請。repo 名稱是 `assignment-N-<帳號>`，push 之後還要到 Canvas 交 URL |
| 每一步都要確認 | 一次建完，最後交驗收報告 |

---

## 6. Repo 結構

```
D:\Repos\fall-2026\
├── BOOTSTRAP.md            ← 本文件
├── CLAUDE.md               ← 精簡規則（第 7 節）
├── courses.yaml            ← 課程 ID、管道、上課時段、SharePoint 站台、Piazza nid（不放密鑰）
├── gpu\
│   ├── assignments.md      ← 作業與專題時程、狀態
│   ├── announcements\      ← YYYY-MM-DD.md（Canvas 公告 + Teams 貼文）
│   └── lectures\YYYY-MM-DD\  transcript.vtt、notes.md
├── dsa\
│   ├── assignments.md
│   ├── repos.md            ← assignment repo 清單
│   ├── piazza\             ← 貼文摘要
│   └── lectures\YYYY-MM-DD\  transcript.srt、notes.md
├── digests\YYYY-MM-DD.md   ← 晨報
├── state\                  ← 上次抓取時間、已看過的 id
├── scripts\
│   ├── ics_fetch.py        ← 不用登入：抓兩門課的 ICS、過濾往年項目、換算時區
│   ├── browser\*.js        ← 第 4 節的瀏覽器片段（Canvas、SharePoint、Panopto、Piazza）
│   ├── github_assignments.ps1
│   └── tz.py
├── .env.example            ← 只列變數名：CANVAS_ICS_GPU、CANVAS_ICS_DSA
└── .gitignore              ← .env、大型影片檔
```

推到 GitHub 的 **private** repo。不要把 mp4 放進 repo，只放逐字稿和筆記。

---

## 7. CLAUDE.md 要寫的內容

- 語言用繁體中文，術語保留英文。時間一律標成 Pacific
- 課程對照：
  - `GPU = Canvas 1917398 + Teams/SharePoint og_EEP_524_A_B_-_GPU_Computing`
  - `DSA = Canvas 1917417 + Piazza muomkq9jzdj104 + GitHub uw-python-fall2026 + Panopto`
- 整段複製第 3 節的資料可信度規則
- **課程 AI 政策**：使用者已明確表示不在意，照常協助，包括寫作業程式碼、讀 DSA 的 starter code 和 README。只有在碰到課程明文禁止的行為時，加一行提醒：
  - GPU：用 AI 產生作業解答、專題報告或專題程式碼
  - DSA：把 starter code 交給 AI；用了 AI 卻沒有附上 chat session 或註明
- **不代發訊息**：不在 Piazza、Teams、Canvas 發文、回覆或繳交作業
- **登入過期的處理**：遇到 UW NetID 登入頁、Microsoft 登入頁、Canvas OAuth 確認頁、Piazza 登入頁時：
  - 一律停下
  - 在晨報標記「需要重新登入：<來源>」
  - 不輸入密碼，不按授權
- 密鑰類資料不寫進 repo，包括 ICS 網址、Piazza access code、含 pwd 的 Zoom 連結、SharePoint 的 tempauth 連結

---

## 8. 自動化（Claude desktop app 的排程任務）

> 用 app 的 scheduled tasks（`mcp__scheduled-tasks__*`）。電腦要醒著，Claude app 要開著。
> 瀏覽器來源改走 Playwright（`scripts/pw_run.py`），它從 shell 執行，排程任務也能用。登入狀態會在 session 過期後失效，那時晨報標「需要重新登入」，等使用者在互動 session 裡執行 `pw_run.py --login`。原本擔心排程能不能操作內建瀏覽器，這個風險因此不存在了。如果 Playwright 也不能用，就分成兩層：
> - 排程層：只跑 ICS 和 gh，產出截止日提醒
> - 互動層：使用者打開中樞 session 說「更新」時，agent 用瀏覽器抓公告、討論、逐字稿

| 任務 | 時間（Pacific） | 內容 | 來源 |
|---|---|---|---|
| 晨報 | 每天 07:00 | 過去 24 小時的新公告、Piazza 和 Teams 重點、新作業和新 repo、48 小時內到期的項目、需要重新登入的來源 | ICS、gh、瀏覽器 |
| 週規劃 | 週日 21:00 | 下週截止日、建議開始時間 | ICS、`assignments.md` |
| 截止提醒 | 截止前 48h、24h | 推播 | ICS |
| 上課筆記 | GPU：週三；DSA：週二、週四 | 抓逐字稿、對照講義，產出 `notes.md` | SharePoint（4.3）、Panopto（4.4） |

**固定提醒**
- 11/9（一）4:30 PM：DSA 期中考，實體紙筆，Moore 220
- 11/17（二）：GPU 專題 Proposal
- 12/1（二）5:59 PM：GPU 專題 Design Spec
- 12/9（三）4:30 PM：DSA 期末考，實體紙筆，**當天要到校**
- 12/15–12/17：GPU 專題發表（線上）
- 12/17（四）11:59 PM：GPU 專題報告與程式碼，不能延期

**晨報格式**

```
# YYYY-MM-DD 晨報
## 🔴 今明兩天到期
## 📢 新公告（依課程）
## 💬 討論重點（過去 24h，含老師 / TA 的關鍵回覆）
## 🆕 新作業 / 新教材 / 新錄影 / 新 repo
## 📅 今天的課（地點 / 線上）
## ⚠️ 資料來源狀態（需要重新登入的來源）
```

**上課筆記 skill**：`/lecture-notes <gpu|dsa> <日期>`
1. 抓逐字稿
2. 對照講義 PDF 和課本章節。GPU 對 PMPP（章節見 weekly-reading-sets）；DSA 對 Grokking Algorithms
3. 產出內容：重點摘要、名詞解釋、老師強調的地方、和作業或考試的關聯、還要釐清的問題

---

## 9. 建置步驟（給新 agent）

1. 在 `D:\Repos\fall-2026` 執行 `git init`，建立第 6 節的結構，以及 `CLAUDE.md`、`courses.yaml`、`.env.example`、`.gitignore`
2. 用內建瀏覽器開 Canvas，**先檢查 origin**：
   - 取得兩門課的 ICS 網址，寫進 `.env`
   - 抓兩門課的作業、公告、syllabus、modules，產生 `gpu/assignments.md` 和 `dsa/assignments.md`
   - 和第 2 節對照，有差異就列進驗收報告（例如 GPU 的 HW2 以後是否已經發布）
3. 寫 `scripts/tz.py` 和 `scripts/ics_fetch.py`，實測能抓到並正確過濾
4. 用 `gh` 列出 repo，寫進 `dsa/repos.md`
5. 用 SharePoint API（4.3）抓 GPU Lecture 1、2 的逐字稿，存成 `gpu/lectures/2026-10-06/`、`2026-10-13/` 下的 `transcript.vtt`
6. 開 DSA 的 Panopto：
   - 如果停在 OAuth 確認頁，就把它列進使用者待辦，跳過這步
   - 如果能用，抓 Class 1 到 Mod 2 的字幕
7. 讀 Piazza 列表和 Teams General 頻道，各寫一份基準摘要。之後晨報只報新增的內容
8. 建立 `/lecture-notes` skill，用 GPU Lecture 2 試做一份
9. 設定第 8 節的排程任務並手動觸發一次晨報。**這次觸發必須碰到至少一個只能靠瀏覽器取得的來源**，用來驗證第 8 節的風險；結果寫進驗收報告
10. 建 private GitHub repo，**push 前先問使用者**
11. 交出驗收報告：每個來源標明「通 / 不通 / 等使用者」，附上使用者待辦清單

---

## 10. 使用者要自己做的事

1. Playwright 的 UW NetID、Microsoft 或 Piazza 登入過期時，在 agent 執行 `python scripts/pw_run.py --login` 開出的 Chrome 視窗裡自己重新登入
2. 在 Canvas 的 Panopto OAuth 確認頁按授權（目前卡在這頁）
3. 讓電腦不要睡眠，或用 app 的 keep-awake
4. 決定晨報時間（預設 07:00 Pacific）和 GitHub repo 名稱

---

## 11. 尚未查證或待追蹤

- Playwright 的登入狀態（`~/.fall-2026/uw-state.json`）實際能撐多久才要重新登入
- Teams 頻道貼文能不能用 API 讀；「Weekly Live Lecture」的討論串只看過最後幾則
- GPU 專題的題目要求、rubric、發表排程，預計第 6–7 週公布
- DSA Piazza 有些貼文編號打不開
- DSA 的 Canvas 考試設定會不會改成符合實體紙筆
