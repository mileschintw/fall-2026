你是 Fall 2026 學期中樞的作業說明任務。工作目錄 D:\Repos\fall-2026（本機時區 America/Los_Angeles）。先讀 CLAUDE.md 並遵守。

這個任務把兩門課每份作業的說明原文存進 `<course>/hw/<slug>/`，再為每份寫一份結構化摘要 `README.md`。抓取、比對、存原文都由 `scripts/assignment_specs.py` 做，你負責寫摘要。

1. 執行 `python scripts/assignment_specs.py`。它會透過 `pw_run.py` 讀 Canvas，透過 `gh` 讀 DSA repo 的 README，然後印出一份 JSON 報告。
   - exit 3：Canvas 登入過期。status warn，summary「需要重新登入：Canvas」，直接跳到共同收尾。不開登入視窗、不輸入密碼、不按授權。
   - exit 1：同一個指令重跑一次。還是 exit 1：status fail，summary 寫 stdout JSON 的 `canvas_error`（沒有 JSON 時寫 stderr 的最後一行），直接跳到共同收尾。
   - exit 0：照報告往下做。報告裡各欄位的意思：
     - `pending`：要寫或改寫 README.md 的作業。`changes` 列出從上次寫完摘要到現在的變動，`new` 代表第一次存。
     - `unchanged`：摘要已經是最新的。
     - `no_spec`：Canvas 和 repo 都還沒有說明，例如 DSA 還沒發的作業。
     - `errors`：這份作業這次沒抓成，下次會自動重抓。
2. 照 `pending` 的順序，一份一份照下面的「摘要格式」寫 `<dir>/README.md`。寫完一份就執行 `python scripts/assignment_specs.py --done <spec>`（例如 `--done gpu/hw1`），exit 0 才算這份完成，再做下一份。`--done` exit 1 時照它的訊息補好 README.md 再跑一次。
   - DSA 的 starter repo 檔案（stub 的 docstring、測試、`.github/workflows` 的 autograder）存在 `<dir>/repo/`，函式簽名、規格和配分以這些為準，摘要要涵蓋。
   - 內容取自 `<dir>/spec.md` 和 `<dir>/repo/`，加上 repo 裡已有的資料：`<course>/assignments.md`、`<course>/lectures/*/notes.md`、`digests/` 裡老師或 TA 對這份作業的澄清。
   - `<dir>/README.md` 已經存在（改版）：先讀它，再對照新的 spec.md 改寫，並在「改版紀錄」加一列，寫日期和 `changes` 列的變動。不存在：照格式新寫。
   - 這一步的完成條件：`pending` 裡每一份的 `--done` 都 exit 0。沒做到的那幾份留在 state 裡，下次執行會再出現在 `pending`。
3. 登記 status，依序判斷，用第一個符合的：
   - `errors` 不是空的，或有 `pending` 沒完成：status warn，summary 先寫完成的（同下一條的格式），再加「；抓取失敗：<spec>」或「；摘要未完成：<spec>」。
   - `pending` 不是空的：status new，summary 列出作業代號和「新」或「改版」（`changes` 含 `new` 就是新），例如「新：gpu/hw1、dsa/a3；改版：dsa/a2」。
   - 其他：status ok，summary「沒有新東西」。
   - output：這次有寫 GPU 的摘要就填 `gpu/hw/README.md`，只寫了 DSA 的就填 `dsa/hw/README.md`，都沒寫就留空。

## 摘要格式（README.md）
摘要整理「這份作業要交什麼、怎麼評分、有什麼限制」，寫成寫作業時隨手查的版本。只整理題目，答案和程式碼留給使用者自己寫。

```
# <COURSE> <代號>：<作業名稱>

> 原文：[spec.md](spec.md)（<原檔連結，如果有>）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | <Pacific，和 assignments.md 一致；不一致時兩個都寫，並註明採信哪個> |
| 分數 | |
| 繳交方式 | <Canvas online upload／push 到 repo 再到 Canvas 交 URL…> |
| 要交的東西 | <逐項列出，例如檔案類型、報告、截圖> |

## 學習目標
## 要做什麼
<依原文的段落和順序，每個題目或 part 一小節：題目在問什麼、輸入輸出、測資或規格（表格）、標成 HW Q 或要回答的問題>
## 注意事項
<原文明講的限制和提醒，例如 Release build、不能用的函式、檔案命名、遲交規則。每一條後面標出處（spec.md 的段落名、投影片頁碼或逐字稿時間戳）>
## 和上課內容的關聯
<這份作業會用到的上課內容，連到 notes.md 的段落或投影片頁碼。repo 裡找不到就寫「無」>
## 還不確定的地方
<原文和其他來源不一致，或原文沒講清楚的地方。沒有就寫「無」>
## 改版紀錄
| 日期 | 變動 |
|---|---|
| <YYYY-MM-DD> | 第一次整理 |
```

課程 AI 政策的提醒（照 CLAUDE.md）放在摘要最後一行：GPU 寫「GPU 課禁止用 AI 產生作業解答」；DSA 寫「DSA 課用了 AI 要附 chat session 或註明」。

這次執行可能改的檔案：`gpu/hw/`、`dsa/hw/` 底下的檔案，以及 `state/assignment_specs.json`。

每一條路最後都照 `automation/_finish.md` 做共同收尾：用 `scripts/log_run.py --task 作業說明` 登記、更新 dashboard、有新東西就推播、commit 並 push。不發文。最後一句回報這次整理了哪幾份，或跳過的原因。
