# DSA Class 4 — 2026-10-12（一）（Mod 2 Stacks/Queues, Dynamic Arrays：linked stack 收尾、array resize 策略、Python list 的真面目）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，1007 cues，00:02:27–01:45:34，錄影約 106 分鐘）、slides：這堂沒有專屬投影片。重疊的部分參考 Class 5 講義 `dsa/lectures/2026-10-14/slides.txt`（"EE 590a Class outline, wrapping up stacks, queues and runtimes"，Canvas file 154547849，11 頁），引用時標成「10/14 講義 pX」，那是**下一堂**的內容。閱讀：Grokking Algorithms Ch1（Big O）、Ch2（arrays vs linked lists）、Ch3（call stack）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：83 → A3；Hi Charm → PyCharm；stat / staff / stuck / step → stack；8 length Stack / Link stack → linked stack；Marie styles → array style；copies for pence / copy for a pens → `copies_for_appends`（老師示範的函式）；per node / Third node → `cur_node`；summit 1 → assignment 1；the pen → append。
>
> 錄影注意：開頭 [00:07:05] 前老師忘了分享螢幕，線上看不到程式碼。[00:36:34]–[00:47:15] 老師改用平板畫圖解說 linked list，逐字稿只有口述、沒有圖。休息時錄影暫停（[00:49:32] 宣布休息 → [00:51:25] 回來）。

## 重點摘要

1. **課務**
   - A1 成績已發。A2 本週日午夜截止（[00:04:14]）。A3 是 A2 的後續作業，「明天早上」（10/13）發布（[00:04:36]）。
   - 老師在 repo 裡開了一個 `notes.md`，上課時邊講邊打筆記（[00:05:13]）。
2. **Abstract data type vs implementation**（[00:10:03]–[00:12:15]；10/14 講義 p1–p3）
   - Stack 是 abstract data type（ADT）：大家預期它能 push、pop，而且 LIFO。
   - 底層可以用 array 或 linked list 實作。介面相同，但效能特性不同，所以還是要在意底層實作。
   - 有同學問「為什麼要做兩種實作」，老師說先擱著，這堂最後也沒回答，延到 10/14（[00:13:00]、[01:44:28]）。10/14 講義 p1 的答案：每種實作都是讓某些操作便宜、其他操作變貴，程式最常做哪種操作決定贏家。
3. **Linked stack 的 `find`：走訪 linked list 的標準 pattern**（[00:13:50]–[00:18:04]）
   - `cur_node = stack["head"]`、`index = 0`，`while cur_node is not None:` 比對 `payload`，找到就回傳 index，否則 `cur_node = cur_node["next"]`。
   - 走到底沒找到就回傳 `-1`。
   - 第一版忘了 `index += 1`，被測試抓到（[00:24:37]–[00:25:22]）。
   - 時間複雜度 O(n)（10/14 講義 p4 的 `find(value)` 列）。
4. **用 unittest 先寫測試**（[00:17:55]–[00:27:06]）
   - `find` 的測試案例：找開頭、找結尾、找中間、找不存在的值。先寫「找不存在」：push A、B、C，找 D，`self.assertEqual(-1, ...)`。
   - 因為是 stack，最後 push 的在 head，所以 push A、B、C 後找 B 應該得到 index 1。
   - 測試第一次失敗時要問：是程式錯還是測試錯？
   - 修好後重跑受影響的測試（或全部）。
5. **`push_v2` 的 bug 與畫圖除錯**（[00:28:03]–[00:48:07]）
   - 錯誤版本：先把 `head` 指向新 node，再設 `node["next"] = stack["head"]`，結果新 node 指向自己。
   - 症狀：size 一直加，但 list 裡永遠只有一個 node。pop 一直回傳同一個值，測試報 "B does not equal A"（[00:32:00]）。
   - 修法：兩行對調。先 `node["next"] = stack["head"]`，再 `stack["head"] = node`。
   - 老師用平板畫 node 和箭頭，一步步追 head 指到哪裡（[00:37:25]–[00:46:02]）。
6. **Array stack 滿了怎麼辦**（[00:51:25]–[01:09:07]）
   - `play_with_stacks.py`：同時對 array stack（capacity 5）和 linked stack push。range 超過 5 時 array stack 丟 `IndexError`（stack full），linked stack push 到 200 也沒問題（[00:55:53]–[00:58:00]）。
   - 原因：array 是 contiguous memory、元素型別一致、容量事先決定（[00:58:41]）。
   - 投票：加倍 vs 加 1 格 vs 加 10 格。沒人選加 1 格。
   - 實作 `array_resize_double(stack)`（[01:02:36]–[01:08:00]）：
     - stack 滿時呼叫（放在原本丟 IndexError 的地方）。
     - `new_data = [None] * (len(stack["data"]) * 2)`。
     - `for index, item in enumerate(stack["data"]): new_data[index] = item`（`enumerate` 是 index 在前、item 在後）。
     - `stack["data"] = new_data`。
7. **用「複製次數」比較 resize 策略**（[01:10:12]–[01:28:26]）
   - 量時鐘時間很麻煩（機器太快，n 要很大才看得出差異），改數「複製了幾個元素」當 proxy。
   - `copies_for_appends(end, grow)`：每次 size 等於 capacity 就把 size 加進 copies，再用策略放大 capacity。策略寫成 lambda：add one、add 10、double（後來再加 triple 和放大很多倍的版本）。
   - 結果（逐字稿口述）：

     | n | add one | add 10 | double |
     |---|---|---|---|
     | 100 | 將近 5,000 | 500 | 155 |
     | 1,000 | 約 50 萬 | 50,000 | 約 1,000 |

   - n 越大，差距越到數量級（[01:26:48]）。這就是老師上週說「resize 就加倍」的根據（[01:27:41]）。
   - Triple 或更大倍數：n 小時 double 和 triple 差兩倍左右，n 大時差異就不明顯了（[01:31:47]–[01:32:02]）。
   - 10/14 講義 p2、p10 補上理論：加倍時 n 次 push 的總複製量少於 2n，所以 push 是 **O(1) amortized**，雖然觸發 resize 的那一次是 O(n)。
8. **Python list 不是 array**（[01:32:33]–[01:43:41]）
   - 前幾堂一直要大家把 list「假裝成 array」（[01:33:41]）。
   - 在 console 示範：list 可以一直 `append`，也能混放 int、字串、float（[01:34:06]–[01:35:20]）。
   - Python 以對開發者友善為設計目標，所以隱藏了底層 array 的限制（[01:36:17]）。
   - 查官方 docs 的 TimeComplexity 表：`append` O(1)、`pop` 是 O(n−k)、copy O(n)（[01:40:56]–[01:41:13]）。
   - CPython 的 list 是 variable-length array。實作是「contiguous array of references」，list head 結構存指向 array 的 pointer 和長度（[01:41:37]–[01:42:29]）。
   - 結論：Python list 是 **resizable array of pointers**（[01:43:41]）。每格是一個固定大小的 address，所以能混放型別，又保有 array 的效率。
   - 沒講完的部分延到 10/14：list of lists 的圖解、為什麼要多種實作（[01:44:50]）。

## 名詞解釋

| 名詞 | 說明 |
|---|---|
| abstract data type（ADT） | 只規定行為的「介面」或承諾。例如 stack 承諾 push、pop、peek、is_empty，而且 LIFO。不管底層怎麼做。 |
| concrete implementation | 實際實作 ADT 的資料結構，例如 array 或 linked list。效能特性由它決定。 |
| LIFO / FIFO | Last in, first out（stack）／First in, first out（queue）。 |
| array stack | 這門課用 dict 實作：`data` 欄位放一個「假裝是 array」的 list，加上 size。容量固定，滿了就丟 `IndexError` 或 resize。 |
| linked stack | 用 dict 當 node（`payload`、`next`），stack 只記 `head` 和 size。head 就是 stack 的 top。 |
| `cur_node` 走訪 pattern | 從 head 開始，`while cur_node is not None`，處理完就移到 `next`。Linked list 大部分操作都用這個模式。 |
| resize（dynamic array） | Array 滿了就配置更大的新 array，把舊元素逐一複製過去，再把參照指向新 array。 |
| growth strategy | resize 時新容量怎麼算：+1、+10、×2、×3……。加倍的總複製量最少（相對於加常數）。 |
| amortized O(1) | 把整串操作的總成本平均到每一次。加倍策略下單次 push 最壞是 O(n)，但平均每次 O(1)。這不是對隨機輸入取平均（10/14 講義 p2）。 |
| proxy metric | 不直接量時間，改數某個和時間成正比的量，這堂用的是「複製的元素數」。 |
| `enumerate` | 走訪 collection 時同時給 `(index, item)`，index 在前。 |
| unittest / `assertEqual` | Python 內建測試框架。老師在 PyCharm 裡跑單一測試或整個檔案。 |
| Python list | CPython 實作是 contiguous、resizable 的 array of pointers（references）。每格 8 bytes（64-bit），指向存在別處的物件（10/14 講義 p5）。 |
| `pop()` vs `pop(k)` | 從尾端 pop 是 O(1)。`pop(k)` 是 O(n−k)，因為 k 之後的 pointer 都要左移，`pop(0)` 最差（10/14 講義 p6）。 |

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

**課務**
- [00:03:00] A1 成績已發。對成績有疑問就在 Piazza 私訊老師。A1 主要是熟悉找作業、繳交和評分的流程。
- [00:04:14] A2 週日午夜截止，到這時應該已經能自己寫了。
- [00:04:36] A3（逐字稿聽成 "83"）是 A2 的後續作業，明天早上發布。

**ADT 和實作要分開看**
- [00:10:03] 老師特別提醒這個 pattern 之後會一再出現：同一個 stack 行為，可以有 array 和 linked list 兩種實作。
- [00:11:01] Stack 是 abstract data type：一定能 push、pop，一定是 LIFO。底層用什麼都可以，只要守住這個行為。
- [00:11:56] [00:12:15] 但底層實作其實很重要，因為效能特性不同。資料結構要同時看抽象概念和具體實作。
- [00:13:00] 「為什麼要做兩種實作」先擱著，請同學提醒他回來答。結果這堂沒答，延到週三（[01:44:28]）。

**測試驅動的寫法**
- [00:14:05] 「走訪 linked list」是會一再出現的 pattern：看第一個 node，再用 while 迴圈一直取 next。
- [00:18:04] 想測試案例時，列出找開頭、找結尾、找中間、找不存在。順序不拘。
- [00:24:37] [00:24:50] 新寫的測試第一次跑就失敗，他「從不太意外」。重點是判斷錯在程式還是錯在測試。
- [00:25:45] [00:26:12] 先寫測試是為了逼自己明確寫出資料結構「應該」怎麼表現，同時也能證明它有沒有做到。
- [00:27:06] 之後改實作時，重跑全部（或受影響的）測試，確認行為沒變。
- [00:31:56] 原話："Running tests is cheap."，有疑慮就跑。
- [00:32:00] [00:33:06] 不要急著直接改 code，先讀測試輸出：哪一行失敗、預期什麼、實際拿到什麼，用它定位問題。

**Linked list 的 bug：畫圖**
- [00:35:01] [00:36:02] `push_v2` 的錯在指派順序：先改 head 會丟掉原本的 list，新 node 變成指向自己。修法是先設 `next` 再改 head。
- [00:47:09] [00:47:15] 這種指標順序的錯誤在 linked list 很常見。把預期的 node 和箭頭畫出來，是很有用的 debugging strategy。

**Array 的容量限制與 resize**
- [00:56:01] Array stack 容量設 5，push 第 6 個就丟 IndexError，這是我們自己定義的行為。
- [00:58:00] [00:58:41] Linked stack 沒有最大容量。Array 是 contiguous memory、型別一致，所以會滿，滿了就得處理。
- [01:02:36] Resize 的時機：stack 已滿、又要 push 的時候。
- [01:05:08] 老師的 resize 寫法刻意寫得直白，自己說「不 Pythonic」，是為了邊講邊跟得上。
- [01:10:46] 現在機器太快，要量時間 n 得很大，所以改數複製次數。
- [01:16:31] 複製次數是執行時間的 proxy。
- [01:26:48] n 變大後，三種策略差到好幾個數量級。
- [01:27:34] [01:27:41] 上週說「resize 就加倍，相信我」，這次的資料就是證據。
- [01:28:08] Resize 一定是昂貴的操作，所以要盡量少做。
- [01:31:47] [01:32:02] n 很大時，double 和 triple 的差異就不明顯了。
- [01:32:24] [01:32:33] 一定有 trade-off。工程師的工作就是找出 trade-off，再決定採用哪一個。

**Python list 的真面目**
- [01:33:12] [01:33:50] 老師抱怨用 Python list 教這門課很痛苦，所以前幾堂要大家「假裝它是 array」，不能無限 append。
- [01:35:11] [01:35:20] 示範 list 混放字串和 float。真正的 array 只能放一種型別，效能就是從這裡來的。
- [01:36:17] Python 是為開發者設計的，盡量友善，所以不用管底層 array。這有好處也有壞處。
- [01:38:54] [01:39:05] 用 stack、queue、list 之前要查語言的官方文件，搞清楚底層怎麼實作，才知道效率如何。
- [01:40:56] [01:41:03] Docs 表上 `append` 是 O(1)。
- [01:41:13] `pop` 是 O(n−k)，這堂沒細講。
- [01:42:29] [01:42:47] CPython list 是 contiguous array of references，也就是 array of pointers 指向其他物件。
- [01:43:17] Pointer 只是 address，在同一平台上大小固定，所以 array 能保持效率。
- [01:43:41] 這堂的 takeaway：Python list 底下是 resizable array of pointers。

## 和作業 / 考試的關聯

- **A2 Lists, lists and more lists**：10/18（日）11:59 PM PDT 截止（就是今天），目前 unsubmitted。本堂 [00:04:14] 的「週日午夜」與 `assignments.md` 一致。
- **A3 Stacks, Queues and Testing**：10/23（五）11:59 PM 截止，150 分，unsubmitted。本堂 [00:04:36] 說 10/13 早上發布。本堂直接相關的內容：
  - **Testing**：unittest、`assertEqual`、先寫測試再修 code。測試案例要涵蓋開頭、結尾、中間、不存在、空 stack pop 等邊界（見重點 4）。
  - **Linked stack**：push 時先設 `next` 再改 head（[00:36:02]）。`find` 記得遞增 index（[00:25:22]）。
  - **Array stack 的 resize**：`[None] * (2*len)` 加上 `enumerate` 逐一複製。這個寫法本身就沒有用 slicing。
  - **Piazza @36 老師對 A3 的說明**：
    - 精神是用 Python primitives 實作資料結構。
    - Deck 是 stack，直接用 list 當 stack 即可（`append` / `pop()`，皆 O(1)，見 10/14 講義 p6）。
    - 大致不需要 slicing 之類「fancy」寫法。
    - 這和本堂「把 list 假裝成 array」的精神一致（[01:33:41]）。
  - Queue 的部分這堂沒講，在 10/14（Class 5）。重點：用 list 的 `pop(0)` 當 dequeue 是 O(n)（10/14 講義 p6–p8）。A3 若要寫 queue，先看 Class 5 筆記和 A3 README 怎麼規定。
  - 若 A3 有用到 AI，記得依 DSA 課程政策附上 chat session 或註明。
- **A4 Bug Hunt**（10/30）：本堂示範的「讀測試輸出 → 判斷錯在 code 或 test → 畫圖追指標」流程可以直接用上。
- **Midterm 11/9（一）4:30–6:30 PM PST，實體紙筆，Moore 220**：可能考的概念包括：
  - ADT vs implementation
  - array stack 和 linked stack 各操作的複雜度（10/14 講義 p4 表）
  - 為什麼加倍、amortized O(1)
  - Python list 是 array of pointers、`pop(0)` 為什麼慢
  - 本堂沒有提到考試範圍，以上是推測。
- **閱讀**：Grokking Algorithms Ch2（arrays vs linked lists 的 insert/read 取捨）、Ch1（Big O）、Ch3（call stack，即 stack 的應用，10/14 講義 p3 也有提到）。

## 還要釐清的問題

1. **「為什麼要有兩種實作」** 這堂沒答，延到 10/14（[00:13:00]、[01:44:28]）。10/14 講義 p1 有書面答案，要看 Class 5 逐字稿確認老師的說法。
2. **複製次數表的數字**：逐字稿只有口述，沒有完整輸出。
   - n=100 時 double 是 155，剛好等於起始容量 5 時的 5+10+20+40+80，所以起始容量應該是 5。
   - 照這個推算，n=1,000 的 double 應該是 1,275。老師說「1,000」，可能只是約略數字。
   - n 的列表（100、1,000、…、可能到 1,000,000）也沒有完整唸出來。
3. **CPython list 的成長倍率**：本堂以加倍為例。10/14 講義 p9 說 CPython 大 list 約以 1.125 倍成長，還寫「as we saw」，但這堂沒有示範。可能在 10/14 講，待確認。
4. **同學問 array of pointers 的 index 0 能不能接一串 characters、index 1 接一串 integers**（[01:43:53]），老師延到週三回答。
5. **本堂的程式碼**（`play_with_stacks.py`、`copies_for_appends`、`push_v2`、上課 `notes.md`）有沒有 push 到 GitHub 或 Canvas，需要確認。逐字稿沒有說。
6. **A3 的具體要求**（要實作哪些函式、queue 能不能用 `collections.deque`、測試要寫多少）本堂沒講，請看 A3 README 和 Piazza @36。
