# DSA Class 13 — 2026-11-18（週三，Module 7 Heaps 收尾：heap sort、Python `heapq`；Module 5 Hashtables 開頭：direct addressing、hash function、chaining、load factor 與 resize）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，944 cues，00:07:27–01:47:52，約 108 分鐘；session `b6779590-a8a5-4d8b-9d98-b507003b7050`，Panopto 標題「Heaps, Hashtable Intro [Wed, Class 13]」，掛在 Canvas 的 Module 5: Hashtables 底下）。slides：**講義尚未發布**。Canvas Module 5 目前只有 Overview page 和這支錄影；Module 7 裡最新的檔案是 11/16 的 `EE590a_Class_2026-11-16_Mon_heaps_code_build_heapsort_student_copy.pdf`（156443404），屬於上一堂課，這份筆記沒有用。這堂課是線上（Zoom），老師用手寫板畫圖，程式碼在 GitHub（[00:19:03]）。
>
> 閱讀：Canvas Module 5 標了「Reading: Chapter 5, Hashtables」，對應 Grokking Algorithms Ch 5（Hash Tables）。heap sort 和 `heapq` 在 Grokking 沒有專章，可以參考 CLRS Ch 6.4（自行對照）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：heat / Keep → heap；Keep sort / heat sort / the sword → heap sort；HeatQ / EQ / heat cube / Keep Q → `heapq`；keep push / heap top → `heapq.heappush` / `heapq.heappop`；AICON → Python；num list / none list / numb → `num_list` / `num`；deck → `deque`；maxi / MIN heap → max heap / min heap；login / log in → log n；O of N / OF one → O(n) / O(1)；Vidu Algo / Visu Algo → VisuAlgo（visualgo.net）；link list → linked list；BOD7 → mod 7；Cash of → hash of；Mrs. Book → 這個 node 放 "book"（推測）；Little Effie → a little iffy（推測）；Steven、Rudy → 同學的名字。

## 重點摘要

1. **Heap 回顧**（[00:09:08]–[00:13:03]）
   - heap 是用來實作 priority queue 的一種有效率的方法；priority queue 不一定要用 heap，用一般 list 每次排序再取最小值也可以，只是比較慢。
   - heap 是 complete binary tree，最底層由左到右填，可以直接存在 list 裡。
   - heap property：每個 node 都比它的 children 重要；左右 child 之間沒有順序，這是它和 BST 不同的地方。
   - insert：放到最底層下一個空位，再 bubble up，O(log n)。
   - pop：拿走 root，把最後一個元素補到 root，再 bubble down，O(log n)。兩者都受樹高 log n 限制。
   - build heap（週一內容）：leaves 不用動，從中間往前，逐個 bubble down（[00:14:08]）。

2. **Heap sort**（[00:16:01]–[00:24:00]）
   - 最容易理解的版本：把 list 的每個元素 insert 進 heap，再一個一個 pop 出來，出來的順序就是排好的。min heap 得到由小到大，max heap 得到由大到小。
   - 老師現場寫的版本（用週一自己寫的 `heap_insert` / `heap_pop`）：

     ```python
     def heap_sort(num_list):
         heap = []
         for x in num_list:
             heap_insert(heap, x)
         sorted_list = []
         while len(heap) > 0:
             sorted_list.append(heap_pop(heap))
         return sorted_list
     ```

     （依逐字稿 [00:20:05]–[00:22:02] 重建，變數名稱可能和 GitHub 上的不同。）
   - 全部 insert 完之後，heap 這個 list **本身不是排序好的**，只保證 root 最重要（[00:23:00]）。老師畫出來驗證：`[1, 3, 2, 4, 8, 7, 6, 9, 5]` 是合法的 min heap（[00:28:14]–[00:29:21]）。

3. **現場除錯：`bubble_down` 的 off-by-one**（[00:24:00]–[00:51:06]）
   - 跑出來的結果沒有完全排好（8 和 7 的位置反了）。
   - 老師的除錯步驟：先確認 build 出來的 heap 是對的，排除 insert；再在每次 bubble down 之後 print，手動畫圖逐步 pop，和程式輸出對照（[00:29:21]–[00:38:05]）。
   - 找到出錯的地方：heap 剩 `[6, 8, 7, 9]`，pop 掉 6 之後 9 補到 root，應該和較小的 child 7 交換，程式卻和 8 交換（[00:38:05]–[00:39:04]）。也就是 heap 變小、right child 剛好是最後一個元素時，right child 沒有被比較到。
   - 同學 Steven 指出是 `bubble_down` 裡邊界判斷多了一個 `- 1`，改掉之後輸出 1–9 正確（[00:51:06]）。老師說這種 off-by-one 是大家在 bubble down 都會犯的錯。

4. **Python 的 `heapq`**（[00:41:01]–[00:46:06]、[00:53:02]–[00:54:06]）
   - `import heapq`，heap 就是一個普通的 list：
     - `heapq.heappush(heap, value)`：放進去。
     - `heapq.heappop(heap)`：拿出最小值並修好 heap。
     - `heapq.heapify(lst)`：把一個 list 原地變成 heap（就是週一最後做的 build heap）。
     - 最小值永遠在 `heap[0]`，可以直接看。
   - 用 `heapq` 重寫的 heap sort，結果正確：

     ```python
     import heapq

     def heap_sort_with_heapq(num_list):
         heap = []
         for x in num_list:
             heapq.heappush(heap, x)
         sorted_list = []
         while len(heap) > 0:
             sorted_list.append(heapq.heappop(heap))
         return sorted_list
     ```

   - 對照前面學過的：queue 用 `collections.deque`，stack 用 list，heap 用 `heapq`。實務上不需要每次都自己手寫 heap。
   - heap 比 BST / AVL tree 輕量，只需要「最重要的那個」時用 heap 比較便宜（[00:54:06]）。
   - VisuAlgo 的 heap sort 用的是 max heap，由大到小取出，和課堂上的 min heap 版本方向相反（[00:49:00]）。

5. **Hash table 的動機：用 key 查紀錄**（[00:58:02]–[01:04:01]）
   問題：用 NetID / 學號查學生紀錄。目前學過的結構：

   | 結構 | lookup | insert |
   |---|---|---|
   | unsorted list | O(n) | O(1)（放最後） |
   | sorted list | O(log n)（binary search） | O(n)（找位置、後面的往後移） |
   | AVL tree | O(log n) | O(log n)（往下找位置、插入、rotate） |
   | **hash table** | **O(1) 平均** | **O(1) 平均** |

   hash table 的 O(1) 是平均，不是每次都剛好 O(1)（[01:04:01]）。

6. **Direct addressing**（[01:05:01]–[01:07:05]）
   - 最簡單的做法：開一個 array，key 就是 index（0, 1, 2, …, 999），直接到那個記憶體位置拿紀錄，O(1)。
   - 限制和 array 一樣：要事先知道會存多少東西，容量固定，而且 key 只能是數字。

7. **Python `dict` 就是 hash table**（[01:08:05]–[01:10:10]、[01:46:01]）
   - 同學問為什麼不直接用 dictionary。老師：對，dictionary 背後就是 hash table，這個單元要看的是它為什麼能有 O(1) 的 lookup。
   - 先分清楚 behavior（ADT / contract）和 implementation（[01:12:03]）：dictionary 的行為我們知道，要學的是底下怎麼做。

8. **Hash table 的結構：buckets + hash function + chaining**（[01:13:03]–[01:23:08]）
   - 一個 array 當作 list of buckets，每個 bucket 是一個 list（linked list）。
   - hash function 把任何 key（數字、字串、圖片都可以）對應成一個數字。例：`hash(42) = 42`、`hash("book") = 174`、`hash("xyz123") = 6`（老師舉例用的數字，不是真的 Python 輸出）。
   - hash function 的要求：
     - deterministic：同樣的 input 永遠得到同樣的 output（[01:16:02]）。
     - 要快，否則整體不會是 O(1)（[01:32:00]）。
   - 用 `hash(key) % num_buckets` 把數字縮到 bucket 的範圍。例：7 個 buckets，174 mod 7 = 6，"book" 放 bucket 6；`hash("xyz123") = 6`，6 mod 7 = 6，也放 bucket 6，接在同一條 linked list 後面。
   - linked list 的 node 要同時存 **key 和 value**，之後 lookup 才能在 chain 裡比對 key（同學提問後老師補充，[01:22:05]–[01:23:08]）。

9. **手動範例：7 個 buckets，依序 insert 42, 6, 15, 12, 84, 3**（[01:24:04]–[01:31:05]）
   - 簡化：key = value；Python 裡小整數的 hash 就是它自己（[01:27:06]）。
   - `bucket = hash(key) % 7`：

     | key | bucket |
     |---|---|
     | 42 | 0 |
     | 6 | 6 |
     | 15 | 1 |
     | 12 | 5 |
     | 84 | 0（**collision**，和 42 同一個 bucket） |
     | 3 | 3 |

   - collision 的處理：這裡先用 linked list 把同一個 bucket 的東西串起來（chaining）。老師說還有其他處理方式，這堂沒講（[01:30:02]）。
   - insert 的 runtime：算 bucket 是 O(1)，到那個位置放進去是 O(1)（[01:32:00]）。

10. **Lookup 為什麼不一定是 O(1)；load factor 與 resize**（[01:33:05]–[01:41:06]）
    - lookup：用同樣的算式找到 bucket，再到 bucket 裡找。
    - 如果再 insert 14, 21, 28, 35, 49（都是 7 的倍數），全部落在 bucket 0，那條 chain 很長，找 49 要一個一個比，接近 O(n)（[01:36:08]–[01:37:03]）。
    - **load factor = items 數 ÷ buckets 數**，也就是每個 bucket 平均有幾個元素。要讓它保持很小。
    - 做法：每次 insert 之後算 load factor；太大就 resize：`num_buckets *= 2`，把舊 table 的所有東西拿出來，重新放進 buckets 數加倍的新 table。平均每個 bucket 的元素變少，lookup 不會被長 chain 拖慢。
    - 同學 Rudy 的類比：和 dynamic array 滿了要 double 類似（[01:35:00]）。
    - VisuAlgo 的 hash table 示範：7 個 buckets、11 個 items，α = 11/7 ≈ 1.6；再多放幾個也不會自動 resize（[01:42:08]–[01:44:03]）。

11. **下一堂**（[01:44:03]–[01:47:03]）
    - 週一（11/23）繼續 hash table：看程式碼實作（array 放 buckets、linked list 當 chain），以及 resize 時加倍 buckets、重新分配的過程。
    - **11/25（三）感恩節週不上課；11/23（一）照常實體上課。**

## 名詞解釋

- **Priority queue**：一種 ADT，每次取出的是「最重要」的元素。heap 是它常見的實作。
- **Heap property**：每個 node 都比它的 children 重要（min heap 是比較小，max heap 是比較大）；左右 child 之間不排序。
- **Heap sort**：把所有元素放進 heap，再全部 pop 出來，得到排序結果。每次 insert / pop 是 O(log n)，n 個元素共 O(n log n)（O(n log n) 這個總結老師這堂沒有明說，是由每次操作 O(log n) 推出來的）。
- **`heapq`**：Python 標準函式庫的 min heap，直接操作 list。`heappush`、`heappop`、`heapify`。
- **Off-by-one error**：邊界條件差 1 的錯。這裡是 `bubble_down` 判斷 child index 是否在範圍內時多減了 1。
- **Hash table**：用 hash function 把 key 對應到 array 的 index，平均 O(1) 的 insert 和 lookup。Python 的 `dict` 就是。
- **Direct addressing**：key 直接當 array index。只適用於 key 是範圍已知的小整數。
- **Hash function**：把任意 key 變成一個數字的函式；要 deterministic，而且要快。
- **Bucket**：hash table 底層 array 的一格；`bucket = hash(key) % num_buckets`。
- **Collision**：兩個不同的 key 落在同一個 bucket。
- **Chaining**：每個 bucket 放一條 linked list，collision 的元素都串在上面；node 存 key 和 value。（chaining 這個詞老師這堂用的是 chains，[01:45:00]。）
- **Load factor（α）**：items 數 ÷ buckets 數 = 每個 bucket 的平均元素數。
- **Resize / rehash**：load factor 太大時把 buckets 數加倍，所有元素重新算 bucket 放進新 table。

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

- priority queue 不一定要用 heap 實作，heap 只是剛好很有效率（[00:09:08]）。
- heap 裡左右 child 沒有大小順序，這是它和 BST 的差別（[00:11:03]）。
- insert 和 pop 都是 O(log n)，因為樹高永遠是 log n（[00:13:03]）。
- heap sort 是老師最喜歡的排序演算法之一，老師的說法是「sort by data structure」（[00:17:03]）：資料結構本身替你完成排序。
- 全部放進 heap 之後，那個 list 不是排序好的，只有 root 保證最重要（[00:23:00]–[00:24:00]）。
- 除錯的方法：先畫圖確認 heap 建對了，再逐步 pop、每一步和程式 print 的結果對照，找出第一個不一致的步驟（[00:27:01]–[00:38:05]）。
- bubble down 要和**較小的** child 交換（min heap）（[00:33:04]）。
- bubble down 的 off-by-one 是大家都會犯的錯（[00:51:06]）。
- 「magic laundry basket」的比喻：衣服全丟進去，拿出來時就摺好了（[00:52:03]–[00:53:02]）。
- 這段最重要的是 `heapq`：以後用 Python 內建的，不要每次手寫 heap（[00:53:02]–[00:54:06]）。
- hash table 的 lookup 和 insert 是 O(1) **on average**，不是每次都 O(1)（[01:04:01]）。
- Python dictionary 背後就是 hash table（[01:09:03]、[01:46:01]）。
- 資料結構要分開看 behavior（ADT）和 implementation（[01:12:03]）。
- hash function 必須 deterministic（[01:16:02]），而且必須快（[01:32:00]）。
- array 知道 index 就是 O(1) 存取，hash table 就是靠這個（[01:17:08]–[01:18:01]）。
- chain 裡要同時存 key 和 value（[01:23:08]）。
- 兩個 key 落在同一個 bucket 叫 collision；處理方式不只一種，這堂先用 linked list（[01:30:02]）。
- lookup 說是 O(1) 是「wave my hands」：chain 很長時會接近 O(n)（[01:34:01]–[01:37:03]）。
- 要讓每個 bucket 的平均元素數保持很小；insert 後檢查 load factor，太大就把 buckets 數加倍並重新放（[01:38:00]–[01:40:05]）。
- 11/25（三）不上課，11/23（一）照常實體上課（[01:47:03]）。
- 老師覺得前半堂講得不順，請大家在 Piazza 或私下回饋哪裡不清楚（[00:58:02]、[01:47:03]）。

## 和作業 / 考試的關聯

- **A5 BSTs and AVLs**：11/22（日）11:59 PM PST 截止，Canvas 狀態 unsubmitted。這堂的 runtime 比較表（AVL 的 lookup / insert 都是 O(log n)）和 A5 直接相關。
- **A6 Heaps**：12/6（日）11:59 PM PST 截止，unsubmitted。這堂的內容幾乎都會用到：insert / bubble up、pop / bubble down、build heap、heap sort，以及 `bubble_down` 邊界的 off-by-one（寫 A6 時要特別測「right child 剛好是最後一個元素」的情況）。作業是要自己實作還是可以用 `heapq`，要看 A6 的說明。
- **Final Exam**：12/9（三）4:30 PM PST，實體紙筆。heap（手動 insert / pop 畫圖、runtime）和 hash table（手算 `hash(key) % num_buckets`、畫 chaining、算 load factor、說明 resize）都是適合紙筆考的題型。這是我的推測，老師這堂沒有提到考試範圍。
- **停課**：`dsa/assignments.md` 寫 11/25「可能改非同步」；老師這堂明說 11/25 不上課，沒有提到非同步內容（[01:47:03]）。

## 還要釐清的問題

0. （11/20 補）11/16 的講義 `EE590a_Class_2026-11-16_Mon_heaps_code_build_heapsort_student_copy.pdf` 後來放上 Canvas，裡面有這堂前半的內容：正確的 `bubble_down`（邊界是 `left < n`、`right < n`）、heapsort 的 O(n log n)、in-place 版、not stable、`heapq` 用 tuple 當 priority。整理在 `../2026-11-16/notes.md` 的「講義補充」，下面第 1、2 題可以對照那裡。
1. `bubble_down` 的 off-by-one 到底在哪一行？逐字稿只聽得到 Steven 指出兩處、老師說是「that minus one」（[00:51:06]）。要看 GitHub 上修正後的程式碼，確認是 `left < len(heap) - 1` 之類的條件改成 `left < len(heap)`。
2. heap sort 的整體 runtime 老師沒有明說。用 n 次 insert 建 heap 是 O(n log n)；改用 `heapify`（O(n)）建 heap 之後，n 次 pop 仍是 O(n log n)。另外 in-place 的 heap sort（用 max heap，把 root 換到 list 尾端）這堂沒講，VisuAlgo 示範的是那個版本。
3. collision 的其他處理方式（老師說「there are alternatives」，[01:30:02]）：應該是 open addressing（linear probing 等），下週會不會講？
4. load factor 的門檻是多少才 resize？老師只說「too big」（[01:39:04]）。Python `dict` 的實際做法（open addressing、約 2/3 滿就擴大）和課堂的 chaining 模型不同，這是我自己的補充，不是課堂內容。
5. resize 時每個元素都要重新算 bucket，單次是 O(n)，為什麼 insert 平均還是 O(1)？應該和 dynamic array 的 amortized 分析一樣，等週一看老師怎麼講。
6. 字串這類 key 的 hash function 實際怎麼算？老師這堂刻意跳過（[01:14:08]）。
7. 「Python 小整數的 hash 等於自己」（[01:27:06]）：`hash(-1)` 是 -2，是已知的例外（自己的補充）。
8. Class 13 的講義還沒放上 Canvas，放上來之後要補 `slides.txt` 並對照手寫範例。
