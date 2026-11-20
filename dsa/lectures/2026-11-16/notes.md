# DSA Class 12 — 2026-11-16（週一，Module 7 Heaps：heap `pop` / bubble down 的常見錯誤、build heap 的方向、只從一半開始做到 O(n)、heapify 預告）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，622 cues，**只有 00:52:07–01:46:26**；錄影本身約 106 分鐘，session `67a9552d-b891-4cf3-9627-b50500303882`，Panopto 標題還是預設的「EEP 590A: Class Meeting」）。**前 52 分鐘沒有字幕**，可能是那段沒錄到聲音，也可能是 Panopto 還在處理；從後半的話推測，前半在發還 midterm 考卷，並現場寫 heap 的 `pop`（移除 root → 最後一個元素補到 root → bubble down）。slides：`EE590a_Class_2026-11-16_Mon_heaps_code_build_heapsort_student_copy.pdf`（Canvas file 156443404，7 頁，文字在 `slides.txt`；PDF 頁尾的列印時間是 11/18 8:51 PM，是課後才放上 Canvas 的）。**11/20 補**：寫這份筆記時（11/17）講義還沒發布，下面「講義補充」一節是之後依講義加的，前面各節的時間戳內容沒有改。老師說程式碼會 push 到 GitHub，連結放在 Canvas 的 resources（[01:43:02]），build heap 是 O(n) 的推導也會放 notes 到 Canvas。
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

## 講義補充（11/20 補，講義 p1–p7）

這一節全部來自講義，不是逐字稿。它補上前 52 分鐘沒有字幕的部分（recap、bubble up、bubble down 的程式），也確認了前面幾個原本是推測的地方。講義排的進度比實際上課多：heapsort 和 `heapq` 是 11/18 才講的，見 `../2026-11-18/notes.md`。

1. **Recap 與兩題暖身**（講義 p1–p2、p6）
   - 兩條規則：shape（complete binary tree，最後一層由左填起）和 order（min heap：每個 node ≤ children）。index 公式：children `2i+1`、`2i+2`，parent `(i-1)//2`。
   - 11/4 的 heap：`[2, 5, 3, 9, 6, 8, 4, 12, 10]`。
   - insert 7：放在 index 9，parent 是 index 4 的 6，6 ≤ 7，**一次都不用換**。bubble up 有時完全不 swap。
   - 從原本的 heap 連續 remove-min 兩次：依序拿出 2、3，剩 `[4, 5, 8, 9, 6, 12, 10]`。

2. **`bubble_up` / `heap_insert`**（講義 p2）

   ```python
   def bubble_up(a, i):
       while i > 0:
           parent = (i - 1) // 2
           if a[parent] <= a[i]:
               return              # in order: done
           a[i], a[parent] = a[parent], a[i]
           i = parent

   def heap_insert(a, x):
       a.append(x)                 # keeps the shape rule
       bubble_up(a, len(a) - 1)    # fixes the order rule
   ```

   - `while i > 0`：root 沒有 parent。少了這個檢查，index 0 的「parent」是 `(0-1)//2 = -1`，Python 會把它讀成最後一個元素，不會報錯。
   - `<=`：相等就停，省掉不必要的 swap。
   - 例：insert 1 到 11/4 的 heap，1 依序和 6、5、2 交換。每層最多一次比較、一次 swap，所以是 O(log n)。

3. **`bubble_down` / `heap_remove_min`**（講義 p3）

   ```python
   def bubble_down(a, i, n=None):
       if n is None:
           n = len(a)
       while True:
           left, right = 2 * i + 1, 2 * i + 2
           smallest = i
           if left < n and a[left] < a[smallest]:
               smallest = left
           if right < n and a[right] < a[smallest]:
               smallest = right
           if smallest == i:
               return              # no child is smaller: done
           a[i], a[smallest] = a[smallest], a[i]
           i = smallest

   def heap_remove_min(a):
       if not a:
           raise IndexError('remove from an empty heap')
       top = a[0]
       last = a.pop()              # shrink first, so the shape stays complete
       if a:
           a[0] = last
           bubble_down(a, 0)
       return top
   ```

   - 邊界條件是 `left < n` 和 `right < n`，**沒有 `- 1`**。11/18 課堂上 heap sort 排錯，就是現場那份 `bubble_down` 的邊界多減了 1（見 11/18 筆記）；講義這份是對的。
   - `n` 參數讓 bubble down 只作用在 list 的前段，in-place heapsort 會用到。
   - `smallest` 從自己開始，同一串比較就處理了「沒有 child」「只有 left」「兩個 child」三種情況。
   - 講義列的 common bugs 和上面重點摘要第 1 點的四個一樣；多一個細節：少了 `right < n` 的檢查，除了 `IndexError`，更糟的是會比到 heap 範圍外的值（heapsort 已排好的那段）。
   - 例：從 11/4 的 heap remove-min，10 移到 root，先和 3 換，再和 4 換。

4. **build heap**（講義 p4–p5）

   ```python
   def build_heap(a):
       for i in range(len(a) // 2 - 1, -1, -1):
           bubble_down(a, i)
   ```

   - 範例 list 確認是 `[9, 4, 7, 1, 8, 2, 6, 3, 5]`（n = 9，parents 是 index 3, 2, 1, 0）：
     - index 3（1）：children 是 3、5，不用換。
     - index 2（7）：和 2 換。
     - index 1（4）：和 1 換，再和 3 換。
     - index 0（9）：和 1、3、4 各換一次。
     - 結果 `[1, 3, 2, 4, 8, 7, 6, 9, 5]`，共 0+1+2+3 = 6 次 swap，和 `heapq.heapify` 在這個 list 上的結果一樣。其他 list 上 `heapify` 可能給出不同但同樣合法的 heap，因為同一組值可以排成不只一種 heap。
   - **為什麼是 O(n)**：一半的 node 是 leaf，不用做；1/4 的 node 最多 1 次 swap；1/8 最多 2 次；1/16 最多 3 次。總和 n/4·1 + n/8·2 + n/16·3 + … 小於 n。大部分 node 靠近底層，bubble down 很短。反過來，逐一 insert 時，大部分 insert 發生在 heap 已經又大又深的時候。
   - 實測 swap 次數（輸入是遞減排列，對逐一 insert 是最壞情況）：

     | n | 逐一 insert | bottom-up |
     |---|---|---|
     | 1,000 | 7,987 | 992 |
     | 100,000 | 1,468,946 | 99,990 |
     | 1,000,000 | 17,951,445 | 999,988 |

5. **Heapsort**（講義 p5、p7；實際在 11/18 講，而且課堂上只講了「全部 insert 再全部 pop」的版本）
   - 簡單版：`build_heap`（O(n)）之後 remove-min n 次（每次 O(log n)），總共 **O(n log n)，任何輸入都是**，不只是平均。A3 的 bubble sort 是 O(n²)；Python 的 `sorted` 是 Timsort，也是 O(n log n)。
   - in-place 版（教科書的做法）：建 **max heap**；重複「root 和 heap 區段的最後一個交換 → heap 區段縮 1 → 新 root 只在 heap 區段內 bubble down」。O(n log n) 時間、O(1) 額外空間。
     - 例 `[4, 10, 3, 5, 1]`：max heap `[10, 5, 3, 4, 1]` → `[5, 4, 3, 1, 10]` → `[4, 1, 3, 5, 10]` → `[3, 1, 4, 5, 10]` → `[1, 3, 4, 5, 10]`。
   - heapsort **不是 stable**：相等的值出來的順序可能和進去時不同。排數字沒差，依某個欄位排 record 時有差。

6. **`heapq` 的進階用法**（講義 p5–p6；11/18 課堂只講到 `heappush` / `heappop` / `heapify` / `h[0]`）
   - priority 用 tuple：push `(priority, item)`，tuple 逐項比較。
   - 急診室例子：push `(2, 'flu')`、`(1, 'heart attack')`、`(3, 'sprained ankle')`、`(2, 'broken arm')`，pop 順序是 heart attack、broken arm、flu、sprained ankle。broken arm 排在 flu 前面，是因為 priority 相同時比第二項的字母順序。
   - item 不能比較（例如 dict）時，平手會丟 `TypeError: '<' not supported between instances of 'dict' and 'dict'`。解法：push `(priority, counter, item)`，counter 每次加 1，平手就先到先服務。
   - `heapq.nsmallest(3, [7, 2, 9, 4, 1, 8])` → `[1, 2, 4]`；`heapq.nlargest(2, ...)` → `[9, 8]`。
   - `heapq` 沒有 max heap，常用的做法是 push 取負號的值。

7. **總表**（講義 p6）

   | 操作 | 成本 |
   |---|---|
   | 看最小值 | O(1) |
   | insert（bubble up） | O(log n) |
   | remove-min（bubble down） | O(log n) |
   | 從 n 個值 build heap | O(n) |
   | heapsort | O(n log n)，任何輸入 |

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

- **前 52 分鐘的內容**：字幕從 00:52:07 才開始。11/20 重抓 SRT，還是 622 cues、從 00:52:07 開始，Panopto 沒有補上。前半的 `bubble_up` / `bubble_down` / remove-min 程式已由講義補上（見「講義補充」）；老師前半實際怎麼講、「4385 → 3485」那個例子是什麼，仍然不知道。
- ~~範例 list 的確切值~~：講義 p4 確認是 `[9, 4, 7, 1, 8, 2, 6, 3, 5]`，結果 `[1, 3, 2, 4, 8, 7, 6, 9, 5]`（11/20 補）。
- 從頭到尾做 bubble up 的手算過程中，老師自己說「I feel like I got something wrong」（[01:29:00]），之後才補完。結論沒錯，但中間步驟可以自己再手算一遍。
- ~~build heap 是 O(n) 的級數推導~~：講義 p4 給了逐層的算法（n/4·1 + n/8·2 + n/16·3 + … < n）和實測 swap 次數（11/20 補）。
- 老師說程式碼在 GitHub，連結在 Canvas resources。要確認是哪個 repo（`uw-python-fall2026` 底下？）。
- heapify 是不是真的像同學說的「bubble up 和 down 同時做」？Python `heapq.heapify` 其實就是今天這個「從 `n//2-1` 往回 sift down」的做法，週三上課時確認老師怎麼說。
