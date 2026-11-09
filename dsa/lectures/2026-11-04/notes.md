# DSA Class 11 — 2026-11-04（週三，Heaps, Midterm Review：priority queue 用 list / sorted list / AVL / heap 比較、heap 的 shape 與 order、陣列表示法、bubble up / down 預告；後半 midterm 複習與題型）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，945 cues，00:03:49–01:46:08，約 102 分鐘，session `63942a74-515a-4069-9dc0-b4f90039f2f3`，Canvas Module 7 item 27659735「Heaps, Midterm Review [Wed, Class 11]」）。slides：**沒有抓到**。Module 7 唯一的檔案是 `class_scribbles.pdf`（file 155795267，約 37 MB），但 Canvas files API 回傳的 `url` 是空的（11/5 試兩次 `pdf_text.js`，都是 `FILE_ERROR`），可能還鎖著或沒發布給學生。看名稱應該是老師課堂手寫板書的匯出檔（[00:56:09] 說要把 scribbles 放上 Canvas），不是平常那種 notes 講義。老師說平常的 notes 會「今晚」再放（[01:44:12]），11/5 10 AM PT 時 Module 7 還沒有。所以下面全部根據逐字稿，沒有「講義 pN」。
>
> 閱讀：課程沒有指定章節。下面是自行對照的：Grokking Algorithms Ch 1（Big O）、Ch 2（arrays vs linked lists）、Ch 6（BFS 與 queue）；第 2 版 Ch 8 有 balanced trees / AVL。Grokking 沒有 heap 專章，heap 要等 midterm 後的 Module 7 再補（自行對照）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 字幕從 00:03:49 開始，第一句是 Panopto 塞進來的「該逐字稿自動產生…」。前半講 heap 到 [00:55:05]，休息到 [00:56:09]，老師說「Break back at 532」，也就是 5:32 PM 回來（4:30 開課）。[01:46:08] 結束。
>
> 常見誤聽對照：VST → BST；ABL / ALV → AVL；EEP / heat → heap；trait → tree（complete binary tree）；Daru → the root；bidterm → midterm；assorted list → a sorted list；top left / pop left → `popleft`；deck → deque（`collections.deque`）；acute → a queue；NQ / DQ → enqueue / dequeue；PassionList → Python list；cyclist → circular list（環狀 buffer）；Ed minus one → `head - 1`；Inters → pointers；fixed eyes → fixed size；Oh VIN → O(n)；sea → C；n not → n₀；「3n squared plus for an + 3」→ 3n² + 4n + 3；Moments factor → balance factor；Path for O → （聽不出來）。人名：Gus（開場、[00:19:00] 提醒 sorted list 的方向）、Ethan（[00:18:03] 說 pop leftmost）、Luke（[00:57:04] 問 midterm 題型）、Shaoqing（[01:19:02]，用 list + head 指標做 queue）。

## 重點摘要

1. **開場：下週一 midterm**（[00:04:00]）
   - **11/9（一）midterm，在教室、實體紙筆**，自己帶筆。
   - 今天前半講一點新內容（heap），後半做 midterm 複習。
   - [00:29:04]、[00:54:01] 兩次強調：**heap 不考**。今天先介紹，是為了把前面學過的東西串起來，midterm 後接著講。

2. **回顧整學期的資料結構**（[00:06:00]–[00:10:02]）
   - array：連續記憶體、同型別、依序存放；有 dynamic array 和 Python list。
   - linked list：node 散在記憶體各處，可以存不同型別，一個接一個串起來。
   - tree（BST、AVL）：像 linked list，但每個 node 有兩個 child。它們的用途是 **search**。
   - stack（LIFO）、queue（FIFO）。
   - 新概念 **priority queue**：每次都拿「最重要 / 最高優先」的那一個。例子：急診 triage（[00:11:08]）、車內訊息（安全相關的訊息優先，heartbeat 訊息次要，[00:12:05]–[00:13:00]）。

3. **用學過的工具做 priority queue：三種做法比較**（[00:14:02]–[00:29:04]）
   約定：數字越小，優先度越高；「拿最重要的」= 拿最小的。

   | 做法 | 取出最小值 | 插入 |
   |---|---|---|
   | unsorted list | Θ(n)：每個都要看過，才能確定沒有更小的（[00:17:02]） | O(1)：`append` 到尾端（[00:26:04]） |
   | sorted list | O(1)：用 `deque.popleft()`，或由大到小排序後用 `list.pop()`（[00:19:00]–[00:20:02]） | O(n)：要找位置，還要搬動元素；list 或 deque 都一樣（[00:24:00]–[00:25:04]） |
   | AVL tree | O(h) = O(log n)：一路往左走到底（[00:21:02]） | O(log n)（[00:25:04]、[00:28:00]） |
   | **heap**（新） | O(log n) | O(log n)（[00:29:04]） |

   - unsorted list 插入快、取出慢；sorted list 取出快、插入慢。老師說「all of engineering, it's a trade-off」（[00:28:00]）。
   - 學生問 heap 跟 AVL 複雜度一樣，為什麼還要 heap？老師說等一下比較兩者的異同（[00:29:04]）。這堂沒講完，midterm 後才會講。

4. **Heap 的兩條規則**（[00:30:07]–[00:33:00]）
   - **Shape：complete binary tree**。每個 node 有 0、1 或 2 個 child；除了最後一層，每一層都是滿的；最後一層**從左往右**填。
   - **Order（min-heap）：每個 node ≤ 它的 children**，所以 root 一定最小。
   - 這**不是** BST。BST 要求左子樹全部比 root 小、右子樹全部比 root 大；heap 只要求 parent ≤ child，兩個 sibling 誰大都可以。例：5 底下接 10 和 15，是 heap 但不是 BST（[00:33:00]）。

5. **範例 heap 與陣列表示法**（[00:34:08]–[00:47:00]）
   - 範例樹：root 2；第二層 5、3；第三層 9、6、8、4；第四層 12、10（12、10 是 9 的 children）。
   - 檢查 order：2 < 5、3；3 < 8、4；5 < 9、6；9 < 12、10。8 比 4 大沒關係，因為它們是 sibling（[00:34:08]–[00:35:02]）。
   - 下一個插入的位置是最後一層的下一個空位（6 的左 child），從左往右填（[00:35:02]–[00:36:01]）。
   - 因為形狀固定，可以不用 node（dict 加 left / right），改用 **array** 存。按層、由左到右排：`[2, 5, 3, 9, 6, 8, 4, 12, 10]`，index 0–8（[00:38:00]–[00:40:00]）。
   - 為什麼用 array（[00:41:04]–[00:44:04]）：
     - 學生說：這就是 BFS 的走訪順序。
     - 學生說：可以用 index 取代 pointer。知道 index 就是 O(1) access，不用像 linked list 那樣一個 node 一個 node 走。
   - **Index 公式**（[00:44:04]–[00:47:00]）：
     - node i 的 children：`2i + 1`、`2i + 2`
     - node i 的 parent：`floor((i - 1) / 2)`
     - 驗算：i = 2，children 是 5 和 6；i = 6，parent 是 (6 − 1) / 2 = 2.5，取 floor 得 2。

6. **預告：取出與插入**（[00:48:09]–[00:55:05]，老師說會很快帶過）
   - **取出最小值**：拿走 root；把**最後一個元素**搬到 root；跟 children 比較並往下交換（**bubble down**），直到又是 heap（[00:49:03]–[00:52:02]）。範例取出 2 之後 root 變 3。老師邊畫邊說可能畫錯（[00:51:01]）。
   - **插入**：放到下一個空位（最後一層最左的空位）；跟 parent 比較並往上交換（**bubble up**）。範例插入 1，接在 9 底下：1 < 9 交換，1 < 5 交換，1 < 3 交換，1 到達 root（[00:52:02]–[00:54:01]）。
   - 小結（[00:54:01]）：heap 只追蹤「最重要的那一個」；用 array 存，所以有 O(1) access；取出從 root 拿，再 bubble down；插入放空位，再 bubble up。

7. **Midterm 題型與作答規則**（[00:57:04]–[01:01:07]）
   - 老師說考卷還沒出，但大致是：
     - **5–10 題 true / false**
     - 幾題 multiple choice
     - 幾題填空或簡答
     - **約 3 題比較深入的題目**：可能要讀 pseudocode 或寫程式
   - 會清楚寫明要 Python 還是 pseudocode。**寫程式不要求完美的 syntax**（[00:59:13]）。
   - **把假設寫下來就有分**：例如忘記 deque 是 `popleft` 還是別的，只要寫出假設、而且假設合理，就算假設本身是錯的也給分（[00:59:13]–[01:01:07]）。

8. **複習清單**（[01:01:07]–[01:38:01]，學生喊、老師寫）
   - **Array**：連續記憶體、index、O(1) access、fixed size、同型別。滿了就 allocate 約兩倍空間，再把舊資料全部複製過去（[01:03:02]）。從前面刪除要把後面全部往前搬，不能留空格（[01:04:00]）。插入 / 刪除是 O(n)（[01:04:00]）。
   - **Linked list**：node 加 pointer；doubly linked 可以往回指；有 head 和 tail；可以在 head、tail 或中間插入 / 刪除（[01:05:01]–[01:06:00]）。
   - **ADT vs implementation**：array 和 linked list 已經很具體，但我們關心的是介面和特性（[01:06:00]–[01:07:03]）。**Python list 是 dynamic array**，不是 linked list。名字容易混淆（[01:07:03]–[01:08:04]）。
   - **Python list 的複雜度**（[01:08:04]–[01:09:00]）：`append` O(1)、`pop()` O(1)、`pop(i)` O(n)。`pop(i)` 越靠近尾端搬得越少，所以 O(n) 是 upper bound，不是 tight bound。
   - **Stack / Queue 是 ADT**（[01:10:02]–[01:12:10]）：定義的是行為（LIFO / FIFO），跟實作無關，可以用 array 或 linked list 實作。
     - **Python 的標準答案**：stack 用 **list**（`append` / `pop` 都 O(1)，[01:13:04]）；queue 用 **`collections.deque`**（[01:21:07]–[01:24:04]）。`list.pop(0)` 是 O(n)，不適合當 queue（[01:14:09]）。
     - 另一種做法：list 加一個 `head` index，dequeue 時只把 head 往後移，不真的刪除（[01:15:09]–[01:19:02]）。缺點：前面用過的空間浪費掉，要另外清理，或改成 circular buffer（[01:20:09]）。在受限、可預測的環境裡可以接受（[01:21:07]）。
     - deque 底層大致是 dynamic array，Python 幫你記 head 和 tail，`append` / `appendleft` / `pop` / `popleft` 都 O(1)（[01:22:03]–[01:24:04]）。學生問 deque 是不是就是 Python list：老師說相似但不一樣，以 Python 官方文件為準（[01:36:02]–[01:37:00]）。
     - **要會的**：stack 和 queue 的行為；Python 的 stack 用 list、queue 用 deque，以及各操作的複雜度。考試也可能出 pseudocode，用別的結構實作 stack / queue（[01:24:04]–[01:25:06]）。
   - **AVL**（[01:25:06]–[01:31:02]）：AVL 是 BST 的特例。BST 依序（或接近依序）插入會變得一邊倒，像 linked list，search 變成 O(n)。BST search 是 O(h)；AVL 用 **balance factor** 檢查哪裡不平衡，再用 **rotation**（把一個 node 拉上來、把它的 parent 放下去）修正，讓 h 保持在 log n。
   - **Big-O**（[01:31:02]–[01:35:06]）：
     - 要知道常見操作的 Big-O：O(h)、O(n)、O(1)…
     - Θ 和 Ω 介紹過，但「大概不會考」。
     - 老師說定義**不用背**（f(n) = O(g(n)) 若存在 C、n₀，使 n ≥ n₀ 時 f(n) ≤ C·g(n)）。但可能**給你定義、給 f(n) 和 g(n)**，例如 f(n) = 3n² + 4n + 3、g(n) = n³，問一個能成立的 C（[01:33:09]–[01:34:02]）。
     - 學生問會不會要從 O(1) 開始自己一路試出正確的 g？老師說不會，f 和 g 都會給（[01:34:02]）。
   - **Traversal**（[01:37:00]–[01:38:01]）：DFS、BFS；recursive 和 iterative 都要會。

9. **範例題：找出 stack push 的 bug**（[01:38:01]–[01:44:12]）
   - 老師在螢幕上寫了一段 linked-list stack 的 `push`（逐字稿看不到程式碼）。根據口述，順序是：建立 node（payload、`next = None`）→ `stack.head = node` → `node.next = stack.head` → `size += 1`。
   - 照程式畫：push A 之後，A 的 next 指向 head，也就是指向自己。push B 之後，B 的 next 也指向自己，A 就接不到了（[01:41:00]–[01:43:00]）。
   - 老師問了兩個問題：這是程式寫的行為嗎？是。這是正確的 stack 嗎？不是。考試可能這樣出：給一段 code 和輸入，請你畫出結果，再修正 code（[01:43:00]）。
   - 老師沒有公布答案，讓大家自己想（[01:44:12]）。有人猜「把這兩行對調」。我的推論是先 `node.next = stack.head`，再 `stack.head = node`（自行推論，程式碼沒看到）。

10. **收尾**（[01:44:12]–[01:46:00]）
    - 老師 notes 今晚放上 Canvas，裡面有可以拿來練習的題目（老師說不算正式的 midterm practice questions）。scribbles 也會匯出放上 Canvas。
    - 再強調：**下週一在教室考，帶筆**。整堂課的時間都可以用，但希望一小時寫得完。
    - **週六線上 office hours**；有問題也可以發 Piazza。

## 名詞解釋

- **Priority queue**：ADT，每次取出優先度最高的元素（這堂課約定數字越小越優先）。可以用 unsorted list、sorted list、AVL 或 heap 實作。
- **Heap（min-heap）**：滿足 (1) complete binary tree 和 (2) 每個 node ≤ children 的 binary tree。root 是最小值。
- **Complete binary tree**：除了最後一層都填滿，最後一層從左往右填。
- **Array representation of heap**：按層、由左到右存進陣列。children 在 `2i+1`、`2i+2`，parent 在 `floor((i-1)/2)`。
- **Bubble down（sift down）**：取出 root 後，把最後一個元素放到 root，跟 children 比較並往下交換，直到恢復 heap order。
- **Bubble up（sift up）**：插入到下一個空位後，跟 parent 比較並往上交換，直到恢復 heap order。
- **Θ（theta）**：tight bound，上下界都成立。unsorted list 找最小值是 Θ(n)。老師說不會考 Θ 和 O 的差別（[00:17:02]）。
- **ADT（abstract data type）**：只定義行為，例如 LIFO、FIFO，不管實作。
- **`collections.deque`**：Python 的 double-ended queue，兩端 append / pop 都是 O(1)。Python queue 的首選。

## 老師強調的地方

- **Heap 不在 midterm 範圍**，只是先介紹（[00:29:04]、[00:54:01]）。
- Midterm 是**下週一、實體、紙筆**，帶筆（[00:04:00]、[01:45:18]）。
- 不 sort 的 list 找最小值是 tight bound，不只是 upper bound：就算第一個就是最小的，也要看完全部才能確定（[00:17:02]）。
- `popleft` 是 O(1)，**前提是用 deque**。Python list 要拿最小的，就要由大到小排序，再從尾端 `pop()`（[00:19:00]）。老師說「I'm calling this out just because the midterm's coming up」。
- 插入到 array 中間，不管是 list 還是 deque，都要搬東西，所以是 O(n)（[00:25:04]）。
- Heap 和 BST 不一樣：heap 只看 parent ≤ child，sibling 之間沒有大小關係（[00:33:00]、[00:35:02]）。
- 用 array 存 tree 的好處是 index 可以算出來，直接 O(1) 跳過去，不用走 node（[00:43:07]–[00:44:04]）。
- 寫程式**不要求完美 syntax**；把**合理的假設寫下來就給分**，即使假設是錯的（[00:59:13]–[01:00:08]）。
- Python list 是 **dynamic array**，不是 linked list（[01:07:03]–[01:08:04]）。
- `pop(i)` 是 O(n)，但這是 **upper bound**，越靠近尾端越快（[01:09:00]）。
- **Python 的 stack 用 list，queue 用 deque**，要知道這兩個選擇和它們的複雜度（[01:24:04]–[01:25:06]）。
- Big-O 定義不用背，但要會用：給 f、g，找 C（[01:33:09]–[01:34:02]）。Θ / Ω 大概不考（[01:32:03]）。
- 考試可能出「照 code 畫圖、再修 bug」，例如今天的 stack push（[01:43:00]）。

## 和作業 / 考試的關聯

- **Midterm：11/9（一）4:30–6:30 PM PST，實體紙筆，Moore 220**（見 `dsa/assignments.md`），佔總成績 15%。Canvas 上的 Classic Quiz（2448354）只代表考試時段。範圍是 arrays、linked lists、dynamic array / Python list、stack / queue（ADT、Python 實作）、BST / AVL（balance factor、rotation）、traversal（DFS / BFS，recursive / iterative）、Big-O。**heap 不考**。
- **A5 BSTs and AVLs：11/22（日）11:59 PM PST**，跟複習裡的 AVL、balance factor、rotation 直接相關。
- 下週三 11/11 Veterans Day 停課。heap 會在 midterm 之後講，Canvas 上 Module 7 Heaps 標的是 Week of Nov 16。
- 課堂提到的練習資源：老師 notes（今晚上 Canvas，有練習題）和 `class_scribbles.pdf`（Module 7，目前 API 拿不到下載連結）。

## 還要釐清的問題

- **11/8 18:30 PT 更新（Canvas 重新登入後確認）**：老師的 notes 已經上傳，是 `EE590a_Class_2026-11-04_Wed_midterm_review_and_heaps_student_copy.pdf`（file 155891168，Module 7 item 27668750，533 KB，2026-11-07T02:41:09Z，也就是 11/6 6:41 PM PST 上傳）。`class_scribbles.pdf`（file 155795267，37 MB）也在。兩個都是 `locked_for_user: true`：**Module 7: Heaps 的 `unlock_at` 是 2026-11-16T08:00:00Z（11/16 12 AM PST）**，Canvas 顯示「This file is locked until Nov 16 at 12am」。files API 沒有 `url`，直接下載會回 403。所以 11/5 的 `FILE_ERROR` 是因為 module 上鎖，不是登入問題。考前要看就得請老師解鎖（Piazza）；11/16 解鎖後補 `slides.txt`。

- `class_scribbles.pdf` 的 files API 回傳空 `url`，是還鎖著，還是只能從網頁下載？下次跑時再試；拿到後補 `slides.txt`，並對照範例 heap 和 stack push 的程式碼。
- 老師說「今晚」要上傳的 notes（含練習題）在 11/5 早上還沒出現在 Module 7，要再看 Canvas，也可能放在 Week 6: Midterm 或別的 module。
- Stack push bug 的正確修法：逐字稿看不到程式碼，上面的修法是推論，要對照 scribbles 確認。
- Bubble down 範例畫完之後的確切狀態，老師自己說可能畫錯（[00:51:01]），要對照 scribbles。
- 學生問「heap 和 AVL 複雜度一樣，為什麼要 heap」，這堂沒回答，midterm 後應該會講（可能是 array 存放的 cache / 空間優勢、O(1) 取 min、可以 O(n) build heap 等，待老師說明）。
