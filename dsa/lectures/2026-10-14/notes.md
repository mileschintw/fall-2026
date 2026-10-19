# DSA Class 5 — 2026-10-14（週三，Mod 2 Stacks/Queues：stack 實作比較、amortized cost、Python list / deque、queue 入門）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，980 cues，00:03:53–01:52:36，錄影約 113 分鐘）、slides（`EE 590a Class outline, wrapping up stacks, queues and runtimes.pdf`，Canvas file 154547849，11 頁，p11 只有頁尾）、閱讀：Grokking Algorithms（課程沒有指定本堂章節，下面的對照是自行整理的，不是課程指定）。逐字稿是自動產生，專有名詞可能聽錯。
>
> **這份「投影片」其實是課後整理的講義，不是上課時播放的內容。** 老師在 [00:05:15] 說她這堂沒有 slides，下課後會把手上的筆記整理好放到 Canvas。PDF 頁尾的列印日期是 10/17。所以講義裡有些內容上課沒講到，例如 ring buffer、two-stack queue、deque 的 64-slot block、`queue.Queue`、其他語言比較。這些在下面標成（講義 pN），沒有逐字稿時間戳。Piazza @44 說 benchmark 程式碼放在 `in-class-code`。
>
> 常見誤聽對照：Hooray → array；oven / Oven → O(n)；PO → pop；deck / Dec / duck → deque；Q / Cube(s) / RQs → queue(s)；NQ / DQ / EQ → enqueue / dequeue；deaf / death / Death → `def`；dot top left / dot top of zero → `.popleft()` / `.pop(0)`；Self-doubt search equal → `self.assertEqual`；a static → a stack；acute → a queue；M.Ortized → amortized；peak → peek；Evie → Eevee；"create late stacked" → create stack。

## 重點摘要

1. **複習：Python list 到底是什麼**（[00:11:01]–[00:19:13]）
   - Python list 是 dynamic array of references（pointers）。背後是一塊連續記憶體，每格存的是指向物件的 pointer，物件本身放在別的地方。
   - 每個 pointer 一樣大（64-bit 上是 8 bytes），所以 list 可以混放不同型別，`lst[i]` 仍然是 O(1)：位址 = 起點 + 8·i（講義 p5）。
   - list 會在背後自動 resize（也可能 shrink），用的是類似上週的 doubling 策略。
   - Python 有 `array` 模組，但實務上很少人用。大量數值運算用 NumPy。
   - 前幾週要求「把 list 當 array 用」，是為了看清楚 array 的限制。
2. **為什麼要看同一個 ADT 的多種實作？**（[00:19:13]–[00:21:00]，講義 p1）
   - Stack 是 ADT（abstract data type）：它承諾 push、pop、peek、is_empty，以及 LIFO 行為。
   - Array 和 linked list 是兩種兌現這個承諾的方式。只透過 interface 使用的程式分不出底層是哪一種，所以同一套 test suite 可以跑在兩種 stack 上。
   - 每種實作都是讓某些操作變便宜、另一些變貴。你的程式最常做哪種操作，就決定誰比較好。
3. **三種 stack 的 runtime 表**（[00:21:00]–[00:41:15]，講義 p4）
   - Fixed-capacity array：push、pop 都是 O(1)，但滿了就 raise error。find 是 O(n)。
   - Resizing array（doubling）：push 是 **amortized O(1)**，觸發 resize 的那一次是 O(n)。pop O(1)、find O(n)。
   - Linked stack（在 head push / pop）：push、pop 都是 O(1)，而且永遠不會停頓。find O(n)。
4. **Amortized cost**（[00:25:02]–[00:39:03]，講義 p2、p10）
   - 一次昂貴的 resize（O(n)）換來後面 n 次便宜的 push（O(1)），平均攤下來每次 push 是 O(1)。
   - 老師用 capacity 5 → 10 → 20、push 20 個元素的例子逐步推導（[00:35:01]–[00:39:03]）。
   - 講義補充：doubling 讓 n 次 push 總共最多約 2n 次 copy。Amortized 是對一整串操作的總量保證，**不是**對隨機輸入取平均（講義 p2，這是常見的混淆）。
   - 講義也區分 worst case、average case、amortized 三種說法（p2）。
5. **Runtime 一樣，差別在哪？**（[00:41:15]–[00:53:03]）
   - Linked list 沒有 resize 停頓，也沒有容量上限。
   - Array 是連續記憶體，逐一走訪時 clock time 比較短。Linked list 要跳來跳去找下一個 node。
   - 記憶體：三種都是 O(n)，但 n 代表的東西不一樣：
     - fixed array 的 n 是**事先選定的 capacity**
     - resizing array 的 n 是**曾經出現過的最大元素數**，因為我們的實作不會 shrink（[00:51:05]–[00:52:02]）。這一點講義 p4 的表格沒有寫。
     - linked list 的 n 是**目前的元素數**，再加上每個 node 的 metadata（next reference）。
6. **課堂 benchmark**（[00:56:04]–[01:04:05]，講義 p4–p5、p8）
   - 程式是老師下課休息時請 Claude 寫的，她自己說還沒仔細看過（[00:57:04]）。會放到 GitHub。
   - 結果：fixed array 和 growing array 差不多，linked stack 比較慢，用 Python list 當 stack 最快。
   - 記憶體方面，linked stack 用得最多，老師自己覺得這個數字可疑（見 §還要釐清）。
   - 講義 p5 的解讀：Python list 比我們的 array stack 快 5–8 倍，因為 `append` / `pop` 在 C 裡執行，我們的是 Python function call。這就是「Big-O hides constants」。
7. **Python 官方的 list time complexity**（[01:06:07]–[01:09:04]，講義 p5–p6）
   - 最大的成本來自 resize（全部要搬），以及在開頭附近 insert / delete（後面全部要移）。
   - `pop()` 在尾端是 O(1)，`pop(0)` / `insert(0, x)` 是 O(n)。
8. **Stack / queue 在 Python 怎麼用**（[01:09:04]–[01:12:06]，講義 p6–p7）
   - Stack 用 list：`append` + `pop()`。不需要自己寫 stack class。
   - Queue（FIFO，像超市排隊）用 `collections.deque`：`append` + `popleft()`，兩端都是 O(1)。
   - List 當 queue（`append` + `pop(0)`）程式很好寫，但每次 dequeue 都要搬動整個 list。
   - 講義 p7 補充（上課沒講）：`deque(maxlen=k)` 只保留最後 k 筆；`queue.Queue`、`LifoQueue`、`SimpleQueue` 是給多執行緒用的，有 lock 成本。
9. **Live coding：兩種 queue 加 unittest**（[01:12:06]–[01:29:01]）
   - `create_queue_list` 用 dict 包住一個 list，`enqueue` 用 `append`，`dequeue` 用 `pop(0)`。
   - `create_queue_deque` 用 `deque`，`enqueue` 用 `append`，`dequeue` 用 `popleft`。
   - 測試 `test_items_in_order`：依序 enqueue Squirtle、Eevee、Pikachu，用 `assertEqual` 確認依同樣順序出來（FIFO）。兩種實作都通過。
   - 過程中出過兩個 bug：忘了 import；以及 dict 包裝後要寫 `q["data"].append`，不能寫 `q.append`。
10. **pop(0) 為什麼慢、deque 為什麼快**（[01:29:01]–[01:43:02]，講義 p8）
    - 實測把 160,000 個元素的 list 用 `pop(0)` 清空，老師口頭說約 4 秒。deque 的 `popleft` 不到 1 秒。講義 p8 寫的數字不同（見 §還要釐清）。
    - `pop(0)` 要把剩下的 pointer 全部往左移一格，n 次就是 O(n²)。
    - 老師的白板圖：deque 只移動 front 指標，空出來的格子留著。講義 p8 說這只是「第一個直覺想法」，正解是 circular array / ring buffer。**CPython 實際上**用的是 doubly linked 的 block chain，每個 block 有 64 個 pointer slot。代價是存取中間元素要走 chain，是 O(n)。
11. **下課後的提問：刪除時留 sentinel、不搬移可以嗎？**（[01:44:01]–[01:51:05]）
    - 可以，但會有空洞。走訪時要跳過空格，也會累積沒用到的記憶體。
    - 老師的結論：這是 engineering，全都是 trade-off。如果實作在自己手上，也知道使用情境，這樣做可以接受。
12. **講義才有的延伸**（講義 p8–p10，上課沒講）
    - Ring buffer：front / back index 在固定大小的環上繞，滿了再 grow。Java 的 `ArrayDeque` 就是這種。
    - Two-stack queue：見 CYK 6。
    - 其他語言：Java `ArrayDeque`；C++ `std::stack` / `std::queue` 是 container adaptor，預設底層是 `std::deque`；Rust 用 `Vec` / `VecDeque`，官方文件建議幾乎不要用 `LinkedList`。
    - C++ `vector<int>` 和 Rust `Vec<i32>` 直接存值。Python list 和 Java `ArrayList<Integer>` 存 pointer。
    - CPython 的 list 在大尺寸時大約以 1.125 倍成長。

### Runtime cheat-sheet（講義 p10「one-page cheat sheet」，加上 p4、p6、p8 整理）

**A. 我們的三種 stack（講義 p4）**

| 操作 | Array stack（fixed） | Array stack（doubling） | Linked stack | 原因 |
|---|---|---|---|---|
| push | O(1)；滿了 raise | O(1) amortized；觸發 grow 那次 O(n) | O(1) | array 寫一格；linked 建一個 node、改兩個 reference |
| pop | O(1) | O(1) | O(1) | 頂端不需要搬移 |
| peek | O(1) | O(1) | O(1) | 讀頂端 slot 或 head node |
| is_empty / size | O(1) | O(1) | O(1) | 兩種都存了 size |
| find(value) | O(n) | O(n) | O(n) | 從一端掃；linked 每步比較貴 |
| 取第 i 個 | O(1) | O(1) | O(i) | array 用 index 直接跳，chain 要走 |
| 依位置交換兩值 | O(1) | O(1) | O(n) | chain 要走到兩個位置 |
| reverse | O(n) | O(n) | O(n) | 每個值都要動一次 |
| 會不會滿 | 會 | 不會（直到記憶體用完） | 不會 | |
| 記憶體 | n 個 slot（事先選定） | n 到 2n 個 slot；**不會 shrink，以曾經的最大 n 計**（[00:52:02]） | 每個值一個 node 加 reference | |

**B. 什麼情況用什麼（講義 p10 cheat sheet）**

| 需求 | 用什麼 | 要記住的成本 |
|---|---|---|
| Stack | `list`：`append`、`pop()` | 各 O(1)；`append` 是 amortized |
| Queue | `collections.deque`：`append`、`popleft()` | 各 O(1) |
| 用一般 list 當 queue（避免） | `append`、`pop(0)` | 每次 dequeue O(n)，清空要 O(n²) |
| 依位置存取 | `list[i]` | O(1)；deque 兩端 O(1)、中間 O(n) |
| 搜尋某值 | `x in lst` | O(n) |
| 執行緒之間分派工作 | `queue.Queue` | O(1) 加 lock 成本；用 `get()`，不要先問 `empty()` |
| 只保留最後 k 筆 | `deque(maxlen=k)` | O(1) |
| 為什麼 doubling 有效 | | 每次 push 的總 copy 數低於 2，所以 push 是 O(1) amortized |
| 為什麼 Big-O 不是全部 | 它把常數藏起來了 | 同樣 O(1)，list 比我們的 array stack 快；linked node 約 23 倍記憶體（此數字存疑，見 §還要釐清） |

**C. Python list 常用操作（講義 p5–p6，引自 Python 官方 TimeComplexity 表）**

| 操作 | 成本 |
|---|---|
| `append(x)` | O(1) amortized |
| `pop()` | O(1) |
| `lst[k]`、`lst[k] = x`、`len(lst)` | O(1) |
| `pop(k)`、`del lst[k]`、`insert(k, x)` | O(n − k) |
| `pop(0)`、`insert(0, x)` | O(n)，最壞情況 |
| `x in lst`、`min`、`max`、`copy()`、iteration | O(n) |
| `lst[i:j]` | O(j − i) |
| `extend(t)` | O(len(t)) amortized |
| `sort()` | O(n log n)；已排序的輸入 O(n) |
| `lst1 + lst2` | O(len1 + len2) |

**D. deque（講義 p8）**

| 操作 | 成本 |
|---|---|
| `append`、`appendleft`、`pop`、`popleft` | O(1) |
| `d[0]`、`d[-1]`、`len(d)` | O(1) |
| `d[i]` 在中間 | O(n) |
| `extend`、`extendleft`、`rotate(k)` | O(k) |
| `remove(x)`、`x in d`、`copy()` | O(n) |

**E. Benchmark 數字（講義 p4、p7、p8，課堂上跑的）**

| 結構 | 1,000,000 次 push 再 pop（秒） | 100,000 個值的記憶體（MB） |
|---|---|---|
| Array stack, fixed | 0.65 | 0.80 |
| Array stack, growing | 0.57 | 1.05 |
| Linked stack（dict 當 node） | 1.35 | 18.4（老師說可疑） |
| Python list 當 stack | 0.084 | 0.80 |

清空 160,000 個元素的 queue：講義寫 list `pop(0)` 2.4 s、`deque` 0.011 s、`SimpleQueue` 0.018 s、`Queue` 0.34 s。老師上課口頭說 list 約 4 秒（[01:32:03]）。

## Check-your-knowledge 題目

> 講義在題目後面的括號裡**已經附了老師的答案**，下面標成「講義附答」並改寫成中文。「非官方解答／補充」是我自己寫的，可能有錯。p3 CYK 第 1 題講義沒有附答案，所以整題都是非官方解答。

**講義 p3 CYK**

1. **Back button 適合哪種 interface？Print spooler 呢？**
   - 講義附答：無。
   - 非官方解答：Back button 用 **stack**，因為最後瀏覽的頁面最先回去（LIFO），講義 p3 也把它列在 stack 的用途。Print spooler 用 **queue**，先送出的工作先印（FIFO）。
2. **只用 push / pop 的程式，能不能分辨 stack 底層是 array 還是 linked list？**
   - 講義附答：不能，而這正是 interface 的目的。
   - 非官方補充：功能上分不出來，但量 clock time 或記憶體就分得出來（見 benchmark）。所以「分不出來」指的是行為（正確性），不是效能。

**講義 p7 Quiz：該用哪一個？**

1. 單執行緒編輯器的 undo 歷史。講義附答：list 當 stack。
2. BFS 的 frontier。講義附答：`deque`，從後面加、從前面 `popleft`。
3. Web server，多個 thread 從同一條共用佇列拿工作。講義附答：`queue.Queue`。
4. 只保留 log 的最後 100 行。講義附答：`deque(maxlen=100)`。
5. 檢查字串的括號是否平衡。講義附答：list 當 stack。
   - 非官方補充：遇到右括號時，除了 pop，還要檢查 stack 不是空的，而且 pop 出來的左括號和右括號是同一種。講義 p3 的描述只說 pop，沒寫這兩個檢查。例如 `"(]"` 和 `")("` 都應該判定不平衡。

**講義 p10 CYK**

1. **為什麼 doubling 時 push 是 O(1) amortized？**
   - 講義附答：每次 grow 的 copy 數是 4 + 8 + … + c，總和小於 2c。c 是最後一次滿的容量，小於 n，所以 n 次 push 總共少於 2n 次 copy，平均每次 push 不到 2 次，另外再加上寫入本身。
   - 非官方補充：如果每次只加固定量，例如 +10，n 次 push 的 copy 總數約 n²/20，平均每次 O(n)。所以上週比較 +1、+10、×2、×3 時，乘法成長才是關鍵（[00:10:07]）。
2. **用 `pop(0)` 清空 1,000,000 個元素的 list，有多糟？**
   - 講義附答：O(n²)。從圖表外插，大約是 160,000 時 2.4 秒的幾十倍，也就是一分鐘以上。要講清楚這是外插，不是實測。
   - 非官方補充：n 變成 6.25 倍，O(n²) 的時間約是 39 倍，2.4 × 39 ≈ 94 秒。如果用老師口頭說的 4 秒，則約 156 秒。兩種都落在「一分鐘以上」。
3. **不能接受停頓時，選哪一種 stack？**
   - 講義附答：linked stack，或 fixed-capacity array stack。Growing array stack 偶爾會有 O(n) 的 push。
   - 非官方補充：fixed 版本的代價是有容量上限，要事先估好最大量。
4. **為什麼 deque 可以 O(1) 從左邊 pop，卻不能 O(1) 存取中間？**
   - 講義附答：deque 是 block 串成的 chain。兩端只差一跳，中間要沿著 chain 走過去。
   - 非官方補充：CPython 每個 block 有 64 格，所以走到第 i 個大約要 i/64 跳，仍然是 O(n)，只是常數小。講義 p8 的實測是 `d[500000]` 約 35 µs，list 約 0.08 µs。
5. **`grid = [[0] * 3] * 3` 為什麼會出錯？**
   - 講義附答：list 是 pointer 組成的 array，外層 list 存的是三個指向同一個內層 list 的 pointer。
   - 非官方補充：所以 `grid[0][0] = 1` 會讓三列一起變。正確寫法是 `[[0] * 3 for _ in range(3)]`。內層的 `[0] * 3` 沒問題，因為 int 是 immutable，重新指派只會換掉那一格的 pointer。
6. **面試題：用兩個 stack 做 queue，並說明成本。**
   - 講義附答：enqueue 時 push 到 inbox stack。dequeue 時，如果 outbox 是空的，就把 inbox 全部 pop 到 outbox，再從 outbox pop。每個值最多被搬兩次，所以每個操作都是 O(1) amortized。
   - 非官方補充：單次 dequeue 的 worst case 是 O(n)，也就是要倒一次 inbox 的那一次。順序是對的，因為倒的過程把 inbox 的 LIFO 反轉成 FIFO。
7. **O(1) 沒有告訴你什麼？**
   - 講義附答：常數有多大。這就是為什麼在同一個迴圈裡，Python list 會贏過我們的 array stack。
   - 非官方補充：O(1) 也沒說是不是每次都 O(1)（amortized 還是 worst case），也沒說記憶體用量。

**講義 p9 面試版兩句話**（「How would you build a queue?」、「Why not a plain array?」）
- 講義附答：用帶 head 和 tail pointer 的 linked list，或會 wrap、滿了就 grow 的 circular array，兩種都是每個操作 O(1)。不用一般 array，是因為從前面 dequeue 要搬動全部，每次 O(n)，清空要 O(n²)。

## 名詞解釋

| 名詞 | 說明 |
|---|---|
| ADT（abstract data type） | 只定義行為（有哪些操作、順序規則），不規定怎麼實作。也就是「promise」和「machinery」分開。 |
| Stack / LIFO | Last in, first out，最後放進去的最先出來。操作有 push、pop、peek、is_empty、size。 |
| Queue / FIFO | First in, first out，最早放進去的最先出來。操作有 enqueue（加到尾端）、dequeue（從前端移除）、peek（看前端）。 |
| Deque | Double-ended queue，唸作「deck」。兩端都能加入和移除，所以可以當 stack，也可以當 queue。 |
| Amortized cost | 一整串操作的總成本除以操作次數。單次可能很貴，但總量有保證。不是對隨機輸入取平均。 |
| Worst / average case | Worst 是單次呼叫最多可能花多少，average 是典型輸入下的成本。例如 dict lookup 平均 O(1)，全部碰撞時是 O(n)。 |
| Dynamic array | 會自動 resize 的 array。Python list 就是一種 dynamic array of pointers。 |
| Contiguous memory | 連續的一塊記憶體。只要知道元素個數和大小，就能用 index 算出位址。 |
| Reference / pointer | 指向物件位址的值。Python list 的每一格都存 pointer，固定 8 bytes。 |
| Circular array / ring buffer | front / back index 在固定大小的 array 上繞圈，enqueue 和 dequeue 都是 O(1)，滿了再 grow（講義 p8）。 |
| `collections.deque` | CPython 的實作是 doubly linked 的 block chain，每個 block 64 個 slot。兩端 O(1)，中間 O(n)。 |
| `queue.Queue` | Thread-safe 的 FIFO，每次 put / get 都要拿 lock。單執行緒用起來會比 deque 慢很多（講義 p7）。 |
| Sentinel value | 用一個特殊值標記「這格是空的或已刪除」（[01:45:07]）。 |
| Big-O / Θ | O 是上界，Θ 是 tight bound。日常和面試都說 O，但意思是「大約這麼快」。面試官問 tight bound 時要說 Θ（講義 p2）。 |
| `unittest` / `assertEqual` | 本堂用來測 queue 的行為（[01:19:01]）。 |

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

**課務**
- [00:05:15] 這堂沒有 slides，Canvas 上暫時沒有東西。下課後她會把筆記整理好放上去，所以上課抄不完不用慌。
- [00:57:04] [01:04:05] benchmark 程式碼會 commit 到 GitHub，給大家自己看、自己質疑。
- [01:44:01] 會在分享的筆記裡補一張比較好的 deque 示意圖。
- [01:52:00] 下一堂是週一（10/19）。

**Python list 與 array**
- [00:11:01] [00:17:00] 前幾週刻意要求「把 Python list 當 array 用」，是為了讓大家把 array 的限制想清楚。
- [00:13:09] [00:14:01] Python list 是 dynamic array of references。Array 的關鍵是連續記憶體，必須知道元素個數和大小，所以 Python 存 pointer，資料放在別處。
- [00:16:00] Python 有 array 模組，但很少有人在實務上用。大量數值運算用 NumPy。

**Amortized cost**
- [00:27:00] 不是每次 push 都要 resize，所以要用 amortized cost 來算。
- [00:34:05] 她特別花時間逐步推導，因為這是常被問的題目。
- [00:39:03] 一次很貴的操作換來一大堆便宜的操作，這就是 amortized 的概念。她自己也說這段推導「有點 hand-wavy」。
- [00:32:02] [00:33:07] 同學問「n 一直在變，怎麼算」。她的說法是：n 就是 resize 當下 array 裡的元素數。另一位同學補充：O(1) 的次數遠多於 O(n)，所以整體以 O(1) 計。

**實作之間的差異**
- [00:42:09] [00:43:00] Linked stack 的 push 永遠 O(1)，沒有限制。Array 不是有容量上限，就是偶爾會有很貴的操作。
- [00:44:10] [00:45:06] 走訪 array 的 clock time 會比 linked list 短，但她認為差距可以忽略，所以才用 Big-O 而不是 clock time。（逐字稿原文："I'm going to argue that it's negligible"，[00:45:21]。講義 p9 反而強調常數和硬體的影響，見 §還要釐清。）
- [00:46:00] [00:47:02] 一般來說 array 只能放同一種型別。Python list 存 pointer，所以看起來能混放。
- [00:51:05] [00:52:02] **Resizing array 不會 shrink**：push 20 個再全部 pop，記憶體還是佔著。它的 O(n) 是「曾經的最大 n」。
- [00:53:03] 記憶體看起來都是 O(n)，但三種實作的 n 各自代表不同的東西（capacity、歷史最大值、目前元素數）。

**Benchmark 和 AI 的用法**
- [00:56:04] [00:57:04] 程式是休息時請 Claude 寫的，用來讓理論數字有實測可以對照。她示範把 AI 當學習工具，但也說自己還沒仔細看過程式碼。
- [01:01:04] Linked 實作大約慢兩倍。即使 Big-O 一樣，實際上還是比較慢，印證了同學的猜測。
- [01:02:08] 用 Python list 當 stack 最快。
- [01:35:02] [01:36:03] Linked stack 的記憶體數字「看起來太大」。她直說這裡有問題（逐字稿："smells a little funky"，[01:36:03]），是她會再深入查的地方，但方向應該是對的。

**Queue 與 pop(0)**
- [01:07:05] [01:08:02] Python 官方文件說，最大的成本來自 resize 和在開頭附近 insert / delete。
- [01:09:04] 要 stack 時直接用 list：一律 append 到尾端、從尾端 pop，不必自己實作 stack class。
- [01:22:01] 用 list 加 `pop(0)` 當 queue，寫低風險、不在乎效能的程式時可以，因為簡單只要三行。但高效能的程式不要用，面試也不要用。
- [01:23:15] 面試時要展現你懂 runtime，知道 `pop(0)` 沒效率，也知道 Python 有更好的 queue 寫法。
- [01:32:03] 160,000 個元素用 `pop(0)` 清空大約花 4 秒，`popleft` 不到 1 秒，差距很大。
- [01:33:04] **這就是 data structure 重要的原因**：這種差距會嚴重拖慢你寫的程式。
- [01:16:01] [01:17:01] 寫測試時要測行為。她把測試命名為「items in order」，用來驗證 FIFO。

**Trade-off**
- [01:49:12] [01:50:01] 不搬移、改留空格（sentinel）並不是錯，也不是不可能。這是 engineering，全都是 trade-off（逐字稿："this is engineering. And it's all trade-offs"，[01:49:31]）。如果實作在自己手上，也知道使用情境，可能就合理。
- [01:51:05] deque 的 `pop`（尾端）和 list 的 `pop()` 一樣是 O(1)，`popleft` 也是 O(1)，但 list 的 `pop(0)` 不是。

## 和作業 / 考試的關聯

- **A3 Stacks, Queues and Testing**
  - 截止：10/23（五）11:59 PM PDT，150 分，Canvas id 11814801，目前 unsubmitted（依 `dsa/assignments.md`）。
  - 本堂直接相關的內容：
    - 用 `unittest` 寫行為測試，例如 `test_items_in_order` 和 `assertEqual`，見 [01:17:01]–[01:29:01]。
    - 同一套 test suite 跑在不同實作上（講義 p1）。
    - list 版和 deque 版的 queue 寫法。
    - stack / queue 各操作的 runtime 表。
  - 作業如果要求分析 runtime 或選資料結構，cheat-sheet A、B 可以直接對照。
  - 這份筆記沒有寫 A3 的解答程式碼。
  - 提醒：DSA 的 AI 政策禁止把 starter code 交給 AI，用了 AI 要附上 chat session 或註明。
- **A2 Lists, lists and more lists**
  - 截止：今天 10/18（日）11:59 PM PDT，目前 unsubmitted。
  - 講義 p9 提到 `array.array` 比 list 省記憶體，「in the assignment」看起來指的是 A2 的內容。講義 p5 的 `[[0]*3]*3` grid 陷阱是「上一堂」的內容。
- **Midterm**
  - 11/9（一）4:30–6:30 PM PST，Moore 220，實體紙筆。
  - 講義 p10 說 cheat sheet 是「for tests and interviews」，Big-O 表、amortized 推導、list 和 deque 的選擇都很可能考。
- **面試**
  - 老師兩次提到面試：不要用 `pop(0)`（[01:22:01]），以及講義 p9 的兩句話答法和 two-stack queue。
- **之後的課**
  - 講義 p3 說 DFS（stack）和 BFS（queue）下週會講。
  - 講義 p2 說 binary search（O(log n)）是之後的主題。
- **Grokking Algorithms（自行對照，非課程指定）**
  - Ch1：Big O、binary search。
  - Ch2：arrays vs linked lists，以及 insert / read 的成本比較。
  - Ch3：recursion 與 call stack，對應 stack 的用途。
  - Ch6：BFS 與 queue，對應下週。
  - 章節號以你手上的版本為準。
- **課堂程式碼**：Piazza @44 說 benchmark 在 `uw-python-fall2026/in-class-code`。

## 還要釐清的問題

1. **pop(0) 清空 160,000 個元素到底花多久？**
   - 老師上課口頭說約 4 秒（[01:31:17]–[01:32:03]）。講義 p8 寫 2.4 s（deque 0.011 s，約 200 倍）。CYK 2 也用 2.4 s 外插。
   - 依 BOOTSTRAP §3 以逐字稿為準，但這是機器和執行次數的差異（講義應該是之後重跑的），量級結論不變。考試如果問數字，以講義為參考即可，重點是 O(n²)。
2. **Linked stack 的記憶體 18.4 MB（每個值 184 bytes、約 23 倍）可信嗎？**
   - 老師在 [01:35:02]–[01:36:03] 說這個數字可疑，方向對但太大，需要再查。
   - 講義 p5 和 p10 卻直接採用這個數字，並解釋成 dict 當 node 的開銷。
   - 可以到 `in-class-code` 看 benchmark 怎麼量的，例如有沒有把 dict 本身和內容物都算進去。
3. **Linked stack 慢多少？** 老師說約兩倍（[01:01:04]），講義 p4 寫 2–3 倍（1.35 vs 0.57 / 0.65 s）。兩者大致一致。
4. **Deque 示意圖不一致**：老師白板畫的是「移動 front 指標、留空格」（[01:42:02]–[01:43:02]）。講義 p8 說這是「第一個直覺想法」，缺點是左邊的格子永遠不會再用、array 一直變大。正解是 ring buffer，CPython 實際上用 64-slot block chain。以講義為準來理解實作，老師說會補圖（[01:44:01]）。
5. **Cache 和常數到底重不重要？** 上課時老師說走訪時的跳躍成本可以忽略（[00:45:06]），講義 p9 則強調實務上 array-based 的版本在常數上勝出（引用 Java、Rust 文件）。這是強調重點不同，不算衝突。
6. **Resizing array 不會 shrink**（[00:52:02]）是指「我們自己的實作」。Python list 老師說「可能會 shrink」（[00:13:09]）。講義 p4 的記憶體欄只寫「n 到 2n 個 slot」，沒有提到這點。
7. **`find` 該不該算 stack 的操作？** 老師說她不太喜歡把 find 當成 stack 的操作（[00:21:00]），A3 會不會要求實作 find，要看作業說明。
8. **Benchmark 的 queue 比較裡另外兩項**：老師說她不完全知道是什麼（[01:33:04]），看起來是效率較差的實作。講義 p7 列出的是 `SimpleQueue` 和 `Queue`。
