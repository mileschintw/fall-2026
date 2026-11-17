# DSA Class 12 — 2026-11-16（週一，Module 7 Heaps：heap `pop` / bubble down 的常見錯誤、build heap 的方向、只從一半開始做到 O(n)、heapify 預告）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，622 cues，**只有 00:52:07–01:46:26**；錄影本身約 106 分鐘，session `67a9552d-b891-4cf3-9627-b50500303882`，Panopto 標題還是預設的「EEP 590A: Class Meeting」）。**前 52 分鐘沒有字幕**，可能是那段沒錄到聲音，也可能是 Panopto 還在處理；從後半的話推測，前半在發還 midterm 考卷，並現場寫 heap 的 `pop`（移除 root → 最後一個元素補到 root → bubble down）。slides：**講義尚未發布**。Canvas Module 7（Week of Nov 16）只有 Class 11 的 `class_scribbles.pdf`（155795267）和 11/04 的 student copy，沒有這堂課的檔案。老師說程式碼會 push 到 GitHub，連結放在 Canvas 的 resources（[01:43:02]），build heap 是 O(n) 的推導也會放 notes 到 Canvas。
>
> 閱讀：課程沒有指定章節。下面是自行對照的：Grokking Algorithms 沒有 heap 專章；Ch 7（Dijkstra）會用到 priority queue 的概念，下下週 Module 8 Graphs 會接上。build heap 是 O(n) 的嚴格證明可以參考 CLRS Ch 6.3（自行對照）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：heat / He → heap；HEPA 5 / Keepify → heapify；minheap / menu / minute → min heap；maxi → max heap；Bill deep / build heath → `build_heap`；Ape → `def`（定義 build_heap 的那行，推測）；beep, pop → `heap.pop`（推測）；Log in → log n；OVEN / O n → O(n)；links of the list → length of the list；on campus → on Canvas；visual algo → VisuAlgo（visualgo.net）；double bubble down → bubble down。

## 重點摘要

1. **heap `pop` 的三個常見錯誤**（[00:53:02]–[01:02:01]）
   老師先把前半寫好的 `pop` 拿出來，逐一檢查常見的錯：
   - **一直跟左 child 換**：應該跟**較小的那個 child** 換。程式裡用 `smallest` index，先跟 left 比、再跟 right 比，最後才 swap（[00:54:10]–[00:55:10]）。
   - **沒檢查 child 存不存在**：算出 `left = 2i+1`、`right = 2i+2` 之後，要先確認 index 小於 list 長度（[00:55:10]）。
   - **只有一個元素的 heap**：原本的寫法是「`pop()` 最後一個 → 放到 `heap[0]`」。如果只有一個元素，`pop()` 之後 list 是空的，`heap[0] = …` 會丟 `IndexError`。現場跑給大家看（[00:57:02]–[00:58:01]）。修法是：先 `last = heap.pop()`，**如果 heap 還有東西**，才 `heap[0] = last` 再 bubble down；空了就直接回傳（[00:58:01]–[00:59:02]）。
   - **root 跟最後一個換了，list 卻沒縮短**：沒 `pop()` 的話，舊資料會留在 list 尾巴，之後出問題。`pop()` 很重要，因為它會把 list 縮短（[01:00:03]–[01:02:01]）。

2. **heap 可以直接從圖讀成 list**（[01:03:00]）
   heap 底層是 list，所以不必一個一個 `insert`。把樹**一層一層、由左到右**讀下來就是 list 的順序，也就是 BFS（breadth-first）順序。老師用這種方式建了一個新 heap，再 `pop` 一次，看最後一個元素 10 被搬到 root、再 bubble down 回到下層（[01:04:01]–[01:05:00]）。
   - 推薦用 **VisuAlgo** 自己玩 heap 的 insert / remove（[01:05:00]）。

3. **把任意 list 變成 heap：build heap**（[01:06:02]–[01:31:01]）
   範例 list：`[9, 4, 7, 1, 8, 2, 6, 3, 5]`（推測，依 [01:06:02] 與 [01:19:04] 前後拼出來）。
   - 一眼看出它**不是** min heap：最小值 1 不在 index 0（[01:07:01]）。
   - 笨方法：一個一個 `insert` 到新 heap，但要**多一倍空間**。目標是 **in-place**，只用原本的 list（[01:11:01]–[01:12:04]）。
   - 實驗結果（老師刻意「都試試看」）：
     | 做法 | 結果 |
     |---|---|
     | 從尾到頭，每個做 **bubble up** | ❌ 結果 `1, 2, 6, 4, 8, 9, 7, 3, …`，3 比它的 parent 4 小，不是 heap（[01:18:00]–[01:20:05]） |
     | 從尾到頭，每個做 **bubble down** | ✅ 得到 `1, 3, 2, 4, 8, 7, 6, 9, 5`，是 heap（[01:21:03]–[01:22:12]） |
     | 從頭到尾，每個做 **bubble down** | ❌ 不是 heap（[01:24:06]–[01:26:04]） |
     | 從頭到尾，每個做 **bubble up** | ✅ 是 heap（[01:28:04]–[01:31:01]） |
   - **規則**：bubble up 要從頭（root）開始；bubble down 要從尾巴開始（[01:31:01]）。
   - 原因：從 root 往下做 bubble down 時，後面還沒處理的部分會「在你腳下移動」，已經走過的位置沒機會再修。從尾巴往回做時，每次 bubble down 的下面那棵子樹都已經整理好了（[01:27:00]–[01:28:04]）。

4. **runtime：從 O(n log n) 到 O(n)**（[01:32:03]–[01:43:02]）
   - bubble up / bubble down 最壞是 **O(log n)**，因為 complete binary tree 的高度不超過 log n（[01:33:00]）。
   - 對每個元素都做一次 → **O(n log n)**。老師說他不喜歡這個結果（[01:34:00]）。
   - 改進：**leaf 做 bubble down 什麼都不會發生**，所以從**最後一個非 leaf 的 node** 開始，也就是 list 大約一半的位置，往回做（[01:36:00]–[01:38:04]）。程式改成 `range(len(lst)//2 - 1, -1, -1)`，結果和之前一樣（[01:39:00]）。
   - 陷阱題：「只是 n/2，所以變 O(n)？」不對。n/2 · log n 還是 O(n log n)，那只是上界（[01:40:04]）。
   - 真正的理由：每往上一層，node 數就少一半。最多 node 的底層幾乎不用動，要走 log n 的只有 root 一個，全部加起來是 **O(n)**（[01:41:22]–[01:42:00]）。級數推導老師會放 notes 到 Canvas（[01:43:02]）。

5. **預告與行政**（[01:43:02]–[01:46:07]）
   - 週三（11/18）講 **heapify**，以及 Python 內建的 heap（`heapq`），之後就不用自己寫 heap（[01:44:00]）。本來今天要講，時間不夠。
   - 有同學補充：heapify 像是 bubble up 和 bubble down「在中間會合」，所以比較有效率（[01:44:00]，這是同學的說法，週三再確認）。
   - **midterm 解答會公布**。老師本來不公布解答，這次願意給（[01:44:00]–[01:45:09]）。
   - final：midterm 的內容**不會特別出**，但後面的東西建立在它上面，所以「fair game」（[01:45:09]）。
   - **下週一（11/23）有課；週三（11/25）感恩節停課**。問大家要不要錄非同步課，只有一個人說會看，老師說**應該不會錄**（[01:45:09]–[01:46:07]）。

## 名詞解釋

- **min heap**：complete binary tree，每個 node 都 ≤ 它的 children，所以最小值一定在 root（index 0）。**max heap** 相反。
- **list 表示法**：index `i` 的 left child 在 `2i+1`、right child 在 `2i+2`、parent 在 `(i-1)//2`。樹一層一層、由左到右讀就是 list 順序。
- **bubble up（sift up）**：新元素放在尾巴，跟 parent 比，比 parent 小就交換，一路往上。用在 `insert`。
- **bubble down（sift down）**：root 被拿掉後，最後一個元素補到 root，跟**較小的 child** 比，比 child 大就交換，一路往下。用在 `pop`。
- **build heap**：把任意 list 原地（in-place）整理成 heap。正確做法是從最後一個非 leaf node（`len//2 - 1`）往回到 0，每個做 bubble down，複雜度 O(n)。
- **leaf**：沒有 child 的 node。list 後半（大約 `len//2` 之後）全部是 leaf。
- **heapify**：Python `heapq.heapify(lst)` 會把 list 原地變成 min heap，O(n)。週三才正式介紹。
- **in-place**：不另外開一個同樣大小的資料結構，只在原本的 list 裡搬動。

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

- [00:54:10] heap 最常見的錯：**一律跟同一邊的 child 換**，應該跟比較小的 child 換。
- [00:55:10] 算出 left / right index 之後，**先確認它在 list 範圍內**再用。
- [00:57:02] 「hitting run is cheap」：不確定會怎樣，就直接跑跑看。他示範單一元素的 heap `pop` 會報錯。
- [00:58:01]–[00:59:02] 修法：`last = heap.pop()`，heap 非空才放回 `heap[0]` 並 bubble down，空了就直接回傳。
- [01:02:01] `pop()` **非常重要**，它把 list 縮短，list 裡才不會留下多餘的資料。
- [01:03:00] heap 底層是 list，從圖直接 BFS 讀出來就能建，不用一個一個 insert。
- [01:12:04] 要原地整理，不要複製一份，因為那會多用一倍空間。
- [01:28:04] 從尾巴往回做 bubble down 時，下面的子樹「還沒被動過」，所以能各就各位。從頭做 bubble down 就像「樹在你腳下移動」。
- [01:31:01] 結論：**bubble up 從頭開始，bubble down 從尾巴開始。**
- [01:33:00] bubble up / down 最壞 O(log n)，因為 complete binary tree 高度 ≤ log n。
- [01:36:00]–[01:37:03] 從最後一個 non-leaf node 開始，leaf 不用做。
- [01:40:04] 少做一半**不等於**變成 O(n)；n/2 · log n 仍是 O(n log n)。這是陷阱題。
- [01:42:00] build heap 是 O(n)，因為每往上一層 node 數就少一半。bubble up / down 本身仍是 log n。
- [01:43:02] 對數學有興趣的人，可以把每層做的工作列出來加總。他會把 notes 放上 Canvas。

## 和作業 / 考試的關聯

- **A6 Heaps：12/6（日）11:59 PM PST 截止**（Canvas 11814820，unsubmitted）。今天講的 `pop` 三個常見錯誤（選較小的 child、檢查 child 存在、單一元素 heap、記得縮短 list）和 build heap 的方向／起點，幾乎就是 A6 會踩的坑。建議寫完用「空 heap、1 個元素、2 個元素（只有 left child）」這幾個 edge case 測一遍。
- **A5 BSTs and AVLs：11/22（日）11:59 PM PST 截止**，還沒交，這週要處理。
- **Midterm**：考卷今天發還，老師說會公布解答（[01:44:00]–[01:45:09]）。解答出來可以拿去對照 `learn/dsa/`。
- **Final：12/9（三）4:30 PM PST，實體紙筆**。heap 會是範圍內的內容。可能考的點：build heap 為什麼是 O(n)、為什麼從頭做 bubble down 不行、從 list 判斷是不是 min heap（看 index 0 是不是最小值，[01:07:01]）。
- 行事曆：**11/18（三）**講 heapify / `heapq`；**11/23（一）有課**；**11/25（三）感恩節停課，應該不會錄非同步課**。

## 還要釐清的問題

- **前 52 分鐘的內容**：字幕從 00:52:07 才開始。前半的 `pop` / bubble down 實作（包括「4385 → 3485」那個例子）要等 GitHub 上的 code，或之後 Panopto 補上字幕再看。可以晚點重抓一次 SRT 確認是不是處理中。
- 範例 list 的確切值：逐字稿聽到「9 4 7 1 8 2 6 3 5」和「47182 … 3, 5」，上面是拼出來的推測，要用 GitHub 上的 code 確認。
- 從頭到尾做 bubble up 的手算過程中，老師自己說「I feel like I got something wrong」（[01:29:00]），之後才補完。結論沒錯，但中間步驟可以自己再手算一遍。
- build heap 是 O(n) 的級數推導（Σ n/2^(h+1) · h = O(n)）：等老師的 Canvas notes。
- 老師說程式碼在 GitHub，連結在 Canvas resources。要確認是哪個 repo（`uw-python-fall2026` 底下？）。
- heapify 是不是真的像同學說的「bubble up 和 down 同時做」？Python `heapq.heapify` 其實就是今天這個「從 `n//2-1` 往回 sift down」的做法，週三上課時確認老師怎麼說。
