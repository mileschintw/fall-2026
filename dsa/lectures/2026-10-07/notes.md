# DSA Class 3 — 2026-10-07（週三，Mod 1 Linked Lists/Arrays：用 array 和 linked list 實作 stack、unittest、PyCharm debugger）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，1066 cues，00:05:57–01:54:14；Panopto 標示 114 分鐘，但前約 6 分鐘沒有字幕）、slides：**無專屬投影片**（老師在 [00:10:01] 說今天沒有投影片，只拿上週的一張 stack 圖出來看）。背景參考：`dsa/lectures/2026-10-05/slides.txt`（Mod1_LInkedListsArrays_Monday.pdf 手寫筆記 OCR，雜訊多，只用來對照概念）。課堂程式碼：GitHub `uw-python-fall2026/in-class-code` commit `2caa2ad`（"First commit"，2026-10-08T02:48:44Z，也就是 10/7 7:48 PM PDT 下課後），檔案 `Mod1/stack.py`、`Mod1/test_stack.py`、`Mod1/__init__.py`。閱讀：Grokking Algorithms Ch2（arrays vs linked lists）、Ch3（call stack），依 Grokking Algorithms 常見版本章節推定，未核對目錄與課程閱讀清單。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：Ray Stack / Maray Stack → `array_stack`；Bush → push；Lm / LM → `elem`；pi term → PyCharm；ISON → Python；pump / staff / stock / stuck → pop / stack；Crayed in → create new；subscriptivable → subscriptable；Phrases Index error → `assertRaises(IndexError)`；Inquals line of → `== len(`；mod one → `Mod1`。
>
> 錄影注意：[00:59:10] 休息 10 分鐘（老師說 5:35 回來），休息時錄影有暫停，同一分鐘內就接到 "welcome back"。[01:45:00] 以後是下課後老師留下來和幾位同學 debug。

## 重點摘要

1. **複習週一（Class 2）**
   - O(1) 和 O(n) 是在量一個操作要跑多少指令。下週會更深入講 Big-O（[00:06:18]）。
   - Array 的 insert／delete 要搬移元素，bookkeeping 比較多。Linked list 只要加減 node。
   - Array 要事先知道型別和數量，元素必須同型別。Linked list 比較容易放不同型別（看實作）。
2. **今天的實際內容和 Panopto 標題不同**
   - 標題是「Linked Lists/Arrays」，但整堂其實是把一個 **stack**（LIFO）實作兩次：一次用 array，一次用 linked list。
   - 順帶介紹：Python dict、`range`、`raise IndexError`、`unittest`（先寫 test）、`__init__.py` 與 package import、PyCharm 的 Python console 和 debugger。
   - 老師說這堂是為 A2 打底（實作 array 和 linked list 並做分析）。
3. **Stack 的概念**（餅乾罐比喻）
   - 只能看到、拿走最上面那一個。push 放到最上面，pop 拿走最上面那一個。
   - Last In First Out：最後放進去的最先拿出來。
4. **Array-based stack**（`stack.py`）
   - 用 dict 當輕量的 struct：`{'data': [None] * capacity, 'size': 0}`。
   - `[None] * capacity` 在 Python 裡其實是 list，課堂上「假裝」它是固定大小的 array。
   - `size` 是 metadata，同時也是下一個可以放東西的 index。
   - push：先檢查 `size == len(data)`（滿了就 `raise IndexError('Stack is full')`），放進 `data[size]`，再 `size += 1`。
   - pop：先檢查 `size == 0`（空的就 raise IndexError），取 `data[size - 1]`，`size -= 1`，回傳元素。
   - 有同學發現一開始 `create_array_stack` 把 capacity 寫死成 5，沒用到參數，後來改成用 `capacity`（[00:54:07]）。
5. **Linked-list-based stack**
   - Stack：`{'head': None, 'size': 0}`。Node：`{'payload': value, 'next': None}`。
   - 不需要 capacity，可以一直加，這是和 array 的 trade-off。
   - 課堂討論要從 head 還是 tail 加：從 head 加是 O(1)，從 tail 加要走完整個 list，是 O(n)。Stack 永遠只動最前面，所以 push／pop 都在 head。
   - push：建 node → `node['next'] = head` → `head = node` → `size += 1`。
   - pop：先檢查空 → 取 head → `head = head['next']` → `size -= 1` → 回傳 payload。
   - 下課前測試出現 `'NoneType' object is not subscriptable`：linked pop 沒檢查空 stack，`head` 是 `None`。補上 `size == 0` 的檢查後通過。
6. **Testing（unittest）**
   - 先寫 test 再寫實作，迫使自己先想清楚預期行為。
   - Test 名稱要長、要描述行為，例如 `test_push_then_pop_returns_values_newest_first`。
   - 結構：set up（建 stack、push）→ assert。`assertEqual(expected, actual)`，第一個參數是預期值。
   - 預期會丟 exception 的情境用 `with self.assertRaises(IndexError):`。
   - 有趣的 bug：「push 到滿的 array stack 要丟 IndexError」的 test 在還沒寫檢查時就通過了，因為 Python list 自己在 `data[3] = ...` 時丟了 IndexError（list assignment index out of range）。老師之後還是加上明確檢查。
7. **Python 細節**
   - dict 用 `stack['data']` 取值，不是 `stack.data`。
   - `range(4)` 從 0 開始、不含 4；`range(0, 4, 1)` 一樣；`range(4, -1, -1)` 倒數 4 到 0。
   - `raise IndexError('message')` 丟 exception。
   - `def`、參數、冒號、`pass`（還沒實作的佔位）。
   - 有兩個底線的名稱（dunder）是 Python 自己定義的。
   - `Mod1/__init__.py`（空檔）讓 `Mod1` 成為 package，test 才能 `from Mod1.stack import ...`。
8. **PyCharm debugger**
   - 點行號設 breakpoint → 右鍵「Debug Python test」→ resume 跑到下一個 breakpoint，step over 一行一行走，同時看變數。
   - 在 `assertRaises` 包住的 test 裡，exception 被 test 接走了，debugger 不會顯示錯誤。

## 名詞解釋

| 名詞 | 說明 |
|---|---|
| Stack | LIFO 資料結構。只能從頂端 push 和 pop，看不到底下的東西。 |
| LIFO | Last In First Out，最後放進去的最先拿出來。 |
| push / pop | 放到頂端／從頂端拿走並回傳。課堂上是自己實作的函式，不是 Python list 內建的 `pop`。 |
| capacity / size | capacity 是 array 能放幾個（建立時決定）；size 是目前實際放了幾個。Array stack 的 size 同時是下一個空位的 index。 |
| metadata | 關於資料本身的資訊，例如 size。多存一份可以讓「有幾個元素」這種查詢變快。 |
| resize（array） | Array 不能長大，要開一個新的（通常兩倍大），把舊的全部複製過去，O(n)。 |
| node / head | Linked list 的節點有 payload（資料）和 next（指向下一個 node）。head 指向第一個 node。 |
| `None` | Python 的「沒有東西」，類似 C 的 NULL。 |
| dict | Python 的 key-value 集合（`{}`）。這堂把它當成輕量的 class／C struct，用來把 data 和 size 綁在一起。 |
| dunder | double underscore，例如 `__init__.py`、`__name__`，是 Python 自己定義的特殊名稱。 |
| package / `__init__.py` | 資料夾裡放 `__init__.py`，Python 就把它當成 package，可以用 `from Mod1.stack import ...` 匯入。 |
| `range(start, stop, step)` | 產生整數序列，stop 不包含在內，step 可以是負數。 |
| `IndexError` | Index 超出範圍時的 exception。課堂上 stack 空或滿都丟這個。 |
| unittest / `TestCase` | Python 內建的測試框架。test method 名稱以 `test_` 開頭。 |
| `assertEqual(expected, actual)` | 預期值放前面，實際呼叫結果放後面。不相等就 fail 並指出位置。 |
| `assertRaises` | `with self.assertRaises(IndexError):` 包住的程式必須丟出該 exception，test 才算通過。 |
| test-first | 先寫 test 描述預期行為，再寫實作讓它通過。 |
| `NoneType object is not subscriptable` | 對 `None` 用 `[...]` 取值時的錯誤，通常代表某個以為是 dict／list 的變數其實是 `None`。 |
| linting | 檢查程式格式和風格的工具，IDE 裡的波浪底線常來自這裡。 |
| breakpoint / step over / resume | Debugger 的基本操作：停在某行／執行一行但不進入函式／繼續跑到下一個 breakpoint。 |

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

**複習與課程安排**
- [00:06:18] O(1)、O(n) 是衡量一個操作要跑多少指令；下週會再深入講 Big-O。
- [00:08:14] Array 做 insert／delete 時要搬移元素，有很多 bookkeeping。
- [00:09:03] Array 要事先知道型別和要放幾個，元素同型別；linked list 比較有可能放不同型別，但要看實作。
- [00:10:01] 今天用 Python 實際寫 array 和 linked list，目的是幫大家準備 A2：實作 array 和 linked list，並做分析。今天沒有投影片。
- [00:20:07] 這週是第一個完整的週，老師刻意多花時間講 Python 的專有詞彙，讓大家用語一致。

**Stack 概念**
- [00:11:04] [00:12:07] Stack 是 LIFO。老師說真正該想的是：我們不知道底下有什麼，只知道、只能動最上面那一個。
- [00:14:00] 目標是用 array 和 linked list 各實作一次 stack。

**Python list 假裝成 array、dict 當 struct**
- [00:16:23] [00:17:09] `[None] * 5` 在 Python 是 list，但今天「假裝」它是 array：capacity 5，另外用 size 記錄實際放了幾個（metadata）。
- [00:21:00] [00:22:03] 有同學問 list 和 array 差在哪：老師說沒辦法簡短回答，Python 其實沒有真正的 array，所以談資料結構時很麻煩；下週一會詳細講 Python list 和 array、linked list 的關係。
- [00:23:03] 右邊的變數視窗顯示 stack 是 dict、data 是 list，那是 Python 的認知；我們概念上把 data 當 array。
- [00:24:05] [00:25:08] Dict 除了「查名字得年齡」這種用途，也常被當成輕量的 class；對熟 C 的人來說就像 struct，一個欄位放 array、一個欄位放 size。
- [00:26:05] 取值寫 `stack['data']`，不是 `stack.data`。
- [00:49:02] 如果真的當 Python list 用就能動態長大，但我們假裝它是 array，所以不能；要變大就得開新 array（通常兩倍）、把東西全部複製過去。

**`range` 和 exception**
- [00:30:08] [00:31:04] `range(4)` 從 0 開始，到 4 之前停；`range(0, 4, 1)` 是同樣的事，只是把起點、終點、步長寫明。之後走訪 stack 的 data 時會用到。
- [00:32:06] `range(4, -1, -1)` 可以倒數，印到 0 就停，不會印 -1。
- [00:33:10] [00:34:04] 用 `raise IndexError('...')` 丟 exception，訊息會出現在錯誤輸出裡，等一下 stack 會用到。

**測試先行與 AI 程式碼建議**
- [00:34:04] A2 會用 unit test 確認實作是對的；老師今天選擇先寫 test。
- [00:37:05] **老師要求接下來兩份作業（A2、A3）把 PyCharm 或其他編輯器的 code suggestion 關掉**，因為這階段要自己手寫程式、培養手感。老師自己也一直在關她編輯器裡的 AI assistant（[00:52:01]、[01:00:05]）。
- [00:40:00] Test 名稱刻意寫得很長，描述預期行為；先 set up（建 stack、push A、B），再 assert。
- [00:41:00] 每個 assert 都有預期值和實際值：第一個參數是預期值，第二個是實際呼叫的結果；fail 時會指出哪裡錯。
- [00:43:05] 回答同學：A、B 只是隨便選的測試資料，換成 1、2 也一樣。
- [00:44:02] 先寫 test 的目的是讓我們事先想清楚預期行為；第一次跑會出 NameError，因為函式還沒定義。

**實作 array stack**
- [00:45:03] [00:46:01] `def` 定義函式、括號是參數、冒號後是內容；`pass` 表示還沒實作，之後要回來補。
- [00:46:01] IDE 出現波浪底線之類的提示，就是開發者該處理的訊號，至少上 production 前要處理。
- [00:51:03] [00:52:01] Push 時，下一個空位的 index 就是 `size`。
- [00:53:06] Push 完要 `size += 1`，這樣 size 同時代表元素數和下一個 index。
- [00:55:05] 這不是 Python 內建的 pop；我們假裝 data 是 array，所以要自己實作。
- [00:56:02] 老師故意寫得很冗長（先存 `elem` 再回傳），熟 Pythonic 寫法的人可能會受不了，但這樣比較清楚。

**Package 與 import**
- [01:01:03] [01:02:04] 根目錄下有 `Mod1` 資料夾和空的 `__init__.py`，test 才能 import；自己跟著打卻 import 失敗的人先檢查這兩個東西有沒有放對。
- [01:03:08] `from Mod1.stack import ...`：`Mod1` 是資料夾（package），`.stack` 是 `stack.py`，後面列的是要匯入的函式。
- [01:04:02] 函式多了以後 import 怎麼管理，之後再講。

**錯誤情境的 test**
- [01:06:04] [01:07:00] 對空 stack pop 應該丟 exception；用 `with self.assertRaises(IndexError):` 測，選 IndexError 是因為空 array 會去存取 index -1。
- [01:08:02] [01:09:01] 修法：pop 一開始先檢查 `size == 0`，是的話 raise IndexError。
- [01:12:00] [01:13:00] 「push 到滿的 stack」的 test 在還沒寫檢查時就通過了，老師請大家想為什麼。
- [01:16:01] [01:17:06] 原因：Python list 在 `data[3] = ...` 時自己丟了 IndexError。老師偏好明確寫出檢查（`size == len(data)` 就 raise），不要依賴底層 list 的行為。

**工具：console 與 debugger**
- [01:14:03] 學期初老師刻意用 Python console，示範用輕量的方式探索、驗證 Python 在做什麼。
- [01:15:04] PyCharm 也有 debugger，可以直接用。
- [01:19:09] [01:20:05] 示範：點行號設 breakpoint，選 Debug Python test，用 resume 跑到下一次停點，用 step over 一行一行走，同時觀察 stack 內容。
- [01:21:02] 老師希望大家寫作業時多玩 debugger。
- [01:23:02] [01:24:11] 這次看不到 exception 是因為 test 本來就預期會有 exception，被 `assertRaises` 接住了；一般情況會看到更多訊息。

**Linked-list stack**
- [01:25:07] 總結 array 版：pop 前檢查不空，push 前檢查不滿。
- [01:28:00] [01:29:03] Linked list 版也用 dict：head 指向第一個 node，另外記 size（上次覺得很有用）；node 也用 dict，存 payload 和 next。
- [01:31:03] 測試可以複製 array 版改名；結果這個複製貼上埋了問題（見「還要釐清的問題」1）。
- [01:35:10] [01:36:00] 複製出兩個 `create_linked_stack`，一個有 capacity 參數：linked list 不需要事先知道 capacity，可以一直加，這是和 array 的 trade-off。
- [01:38:04] 放在開頭還是結尾會影響執行時間：放結尾要從頭走到尾，放 head 就在手邊。Stack 只需要最前面那個，所以放 head 是 O(1)。
- [01:39:02] Push 步驟：新 node 指向目前的 head → head 改指向新 node → 更新 size。
- [01:40:05] [01:41:01] Pop 步驟：取出 head node → head 改成它的 next → size 減 1 → 回傳資料。

**收尾**
- [01:44:04] 程式碼會 push 到 in-class code repo，下週一（10/12）會把這部分收尾、確認所有 test 通過。這堂應該足以作為 A2 的基礎：程式結構、跑 test、debug、array 版和 linked list 版的差別。
- [01:45:00] 再次強調用 dict 當輕量的 structure，把東西綁在一起。
- [01:46:00] [01:47:11] 回答同學：node 的 next 預設 `None` 沒問題，`None` 就像 C 的 null；Python 不標型別，C 裡則要宣告型別。
- [01:48:09] `NoneType object is not subscriptable` 代表我們對一個 `None` 用了 `[...]` 取欄位。
- [01:51:04] [01:52:05] 用 debugger 找到原因：對空 stack pop 時 head 是 `None`。修法和 array 版一樣，pop 前先檢查 `size == 0`。
- [01:53:00] 程式碼會放上 repo，也會在 Piazza 公告；A2 有問題就貼 Piazza。
- [01:53:00] [01:54:00] 老師說這學期改了她的一些流程，遇到不如預期的狀況請告訴她，好讓她修正。

## 和作業 / 考試的關聯

- **A2 Lists, lists and more lists**
  - 截止：**今天 10/18（日）11:59 PM PDT**，150 分，Canvas id 11814777，Canvas 狀態 unsubmitted。
  - `assignment-2-mileschintw` 目前只有 Initial commit，預設分支是 `master`。繳交：push 之後，**再到 Canvas 交 repo URL**。
  - 這堂和 A2 的關係只有老師在 [00:10:01]、[01:44:04] 說的：A2 要實作 array 和 linked list 並做分析，這堂是基礎。作業細節沒在本堂講到，以 A2 repo 的 README 為準。
  - 可以直接參考的本堂內容：用 dict 表示結構、size／capacity 的管理、head 插入是 O(1)、push／pop 前的邊界檢查、unittest 的寫法、`__init__.py` 和 import 路徑、PyCharm debugger。
- **A3 Stacks, Queues and Testing**
  - 截止：10/23（五）11:59 PM PDT，150 分，Canvas id 11814801。
  - 這堂的 stack 實作加 unittest（包括 `assertRaises` 測錯誤情境）就是 A3 的直接預習。repo 之後的 commit `c3ec279`（"Adding Class 5 code"，10/15 8:19 PM PDT）又加了 `queues.py`、`test_queues.py`、`bench.py`、`play_with_stacks.py`。
- **課程對 AI 的要求**
  - 老師在 [00:37:05] 要求 A2、A3 期間關掉編輯器的 code suggestion。
  - 提醒：DSA 明文禁止把 starter code 交給 AI，也要求用了 AI 就附上 chat session 或註明。
- **期中考**：11/9（一）4:30–6:30 PM PST，Moore 220 實體紙筆。本堂沒有提到考試。
- **閱讀**：Grokking Algorithms Ch2（arrays vs linked lists 的比較、insert／delete 的成本）、Ch3（call stack，有助理解 stack 的 push／pop）。依常見版本章節推定，未核對目錄與課程閱讀清單。

## 還要釐清的問題

1. **repo 裡的 `test_linked_push_on_stack_full_throws` 應該會 fail**
   - 這個 test 是從 array 版複製來的：push a、b、c 之後再 push d，預期丟 IndexError。但 `linked_stack_push` 不會檢查容量，也不會丟 exception。
   - 課堂上 [01:50:06] 有同學指出 linked list 不會滿，老師同意這是複製貼上沒想清楚的結果，但 commit `2caa2ad` 裡這個 test 還在。
   - 最新的 commit `c3ec279`（Class 5 之後）裡這個 test 也還在。
   - 這是讀程式碼推得的結論，沒有實際執行。老師說 10/12（Class 4）會收尾，可以看 Class 4 的錄影有沒有處理。
2. **Python list 和 array 的差別**：老師在 [00:22:03] 說下週一（Class 4，10/12）會詳細講。Class 4 的筆記要對照這點。
3. **Big-O 的正式定義**：[00:06:18] 說「下週」會深入，應該也在 Class 4 以後。
4. **A2 的「analysis」要做什麼？** 老師在 [00:10:01] 只說要對實作做分析，本堂沒有說明格式或內容，要看 A2 的 README。
5. **老師改了哪些流程？** [01:53:00] 老師說這學期改了流程，但沒說是什麼。可能和 GitHub 邀請（Piazza @46 有同學說 A2／A3 邀請過期）有關，未確認。
6. **錄影前 6 分鐘沒有字幕**（00:00:00–00:05:57）：這段可能有課務公告，需要時回去看 Panopto 錄影。
