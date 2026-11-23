# DSA A6：Heaps（A priority queue you can update, and a help desk that uses it）

> 原文：[spec.md](spec.md)（[Canvas assignment 11814820](https://canvas.uw.edu/courses/1917417/assignments/11814820)，Canvas 說明是空白；starter repo README：`uw-python-fall2026/assignment-6-mileschintw`，blob 81d1834，標題「Assignment 6: A priority queue you can update, and a help desk that uses it (100 points)」；stub、tests、workflow 存在 [repo/](repo/)）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-12-06（日）11:59 PM PST**（Canvas `due_at` 2026-12-07T07:59:59Z、repo README「Due: Sunday, December 6, 11:59 pm」、`assignments.md` 一致；原本是 11/30（一），10/20 改成 12/6） |
| 分數 | **100 分**（repo README 和 Canvas 一致）：Part 1 50 + Part 2 15 + Part 3 `ANALYSIS.md` 25 + `AI_NOTE.md` 10 |
| 繳交方式 | commit 並 push 到 `uw-python-fall2026/assignment-6-mileschintw` 的 **`master`**；**以截止前最後一次 push 評分**。push 後看 repo 的 **Actions** 分頁。A4、A5 的週規劃另外提醒到 Canvas 交 repo URL（見「還不確定的地方」） |
| 要交的東西 | `priority_queue.py`（Part 1，8 個函式）、`helpdesk_sim.py`（Part 2，`simulate`）、`ANALYSIS.md`（Part 3，6 節）、`AI_NOTE.md`（4 題）<br>只改這四個檔案；不要改 tests、提供的 helper、`compare.py`、`scenarios.py` 和 `.github` workflow，老師跑的是原檔 |

Repo 在 2026-11-21 6:47 PM PST 建立（`digests/2026-11-22.md`）。[repo/](repo/) 目前全是 starter，還沒有你的 push。週規劃建議 **11/28（六）開工**，最晚 12/2（三）（`digests/2026-11-22-weekly.md`）；**12/9（三）就是期末**。

## 學習目標
（repo README 開頭、「AI, and the final」）
- 上課的 heap 只會 insert 和 remove 最小值；真正的 priority queue 還要能**改一個已經在排隊的項目的優先度**（ticket 升級、Dijkstra 裡路徑變便宜、scheduler 提高等太久的 job）。
- 要改優先度得先找到它，heap 裡找東西是 O(n)。解法是用一個 **dict 記住每個 item 在 heap 裡的 index**；這份作業的重點就是**每次 swap 都讓這個 dict 保持正確**。
- 用自己的 priority queue 跑一個 help desk 模擬，看 starvation 和 aging。
- 期末紙筆：會考**手 trace heap 操作、寫短的 heap code、說明操作成本**。`ANALYSIS.md` §6 就是這種題目的練習，先在紙上做。README 原話：如果 `_sift_down` 不是自己寫的，要確定自己寫得出來。

## 要做什麼

| Part | 內容 | 要改的檔案 | 分數 |
|---|---|---|---:|
| 1 | 可以改優先度的 priority queue | `priority_queue.py` | 50 |
| 2 | 用它的 help desk 模擬 | `helpdesk_sim.py` | 15 |
| 3 | 計時、情境分析、手 trace | `ANALYSIS.md` | 25 |
| | AI note | `AI_NOTE.md` | 10 |

```
python3 -m unittest priority_queue_test -v
python3 -m unittest helpdesk_sim_test -v
python3 check_note.py
python3 compare.py
python3 scenarios.py
python3 -m unittest priority_queue_test.ChangePriorityTest   # 只跑一組
```
一開始每個 test 都是 `NotImplementedError`，是起點，不是 repo 壞了。help desk 的 test 會用到你的 priority queue，所以先讓 Part 1 過。test 通過只代表「大概是對的」（repo README「Run the tests」）。

### Part 1：priority queue（`priority_queue.py`，50 分）

**資料結構**：priority queue 是一個有三個 key 的 dict（`create_pq()` 已提供）：

| Key | 內容 |
|---|---|
| `'heap'` | 當 min-heap 用的 list，元素是 **entry** `[priority, order, item]`（常數 `PRIORITY, ORDER, ITEM = 0, 1, 2`） |
| `'position'` | dict：`item -> 這個 item 的 entry 在 'heap' 的 index` |
| `'counter'` | 總共 insert 過幾次（只增不減）；每次 insert 用它當新 entry 的 `order`，然後加 1 |

- **priority 越小越緊急**。比較用提供的 `entry_less(a, b)`：先比 priority、再比 order，**從不比 item 本身**。所以同 priority 是先來先服務；改 priority 時 **order 不變**。
- item 要 hashable 而且不重複（是 dict key）。

**每個函式 return 之後都要成立的兩條 invariant**（`pq_checks.assert_pq_valid(pq)` 會檢查並說明哪裡錯，`show_pq(pq)` 印出 queue；tests 幾乎每個操作後都呼叫它）：
1. **Heap order**：`entry_less(heap[i], heap[(i - 1) // 2])` 是 False（沒有 entry 排在 parent 前面）。
2. **Positions**：`position[item] == i` 若且唯若 `heap[i]` 存的是 `item`，而且 `position` 沒有別的東西。

**要寫的函式**（規格取自 README 表格和 docstring）：

| 函式 | 行為 | 錯誤 |
|---|---|---|
| `pq_size(pq)` | 幾個 item | |
| `pq_is_empty(pq)` | 是否沒有 item | |
| `pq_contains(pq, item)` | item 在不在，**O(1)** | |
| `pq_priority(pq, item)` | item 目前的 priority | 不在 → `KeyError` |
| `pq_insert(pq, item, priority)` | 加入；order = 目前 counter，counter + 1 | 已經在 → `ValueError` |
| `pq_peek(pq)` | 最緊急的 `(item, priority)`，不移除 | 空 → `IndexError` |
| `pq_remove_min(pq)` | 移除最緊急的，回傳 `(item, priority)` | 空 → `IndexError` |
| `pq_remove(pq, item)` | 從任何位置移除 item，回傳它的 priority，**O(log n)** | 不在 → `KeyError` |
| `pq_change_priority(pq, item, new_priority)` | 改 priority（order 不變），把 entry 移到該在的位置，**O(log n)** | 不在 → `KeyError` |

change、remove、remove_min 都要 O(log n)，有 `SpeedTest` 檢查。

**README 的提示**：
- 從上課寫的 heap code（`sift_up`、`sift_down`、insert、remove_min）開始；比較用 `entry_less`，不要用 `<`。
- 寫一個 helper `_swap(pq, i, j)`：交換兩個 entry **並且**更新兩者的 position。heap 裡每次移動都經過 `_swap`，position dict 就不會過時。
- 改 priority 之後 entry 可能要往上（變緊急）或往下（變不緊急）。先 sift up 再從它停的位置 sift down 就可以，最多只有一個會動。
- 移除 index `i` 的 entry：和最後一個 entry 交換、pop 掉尾端、刪掉它的 position，再修正搬進 `i` 的那個 entry。**那個 entry 可能要往上，不只往下**（remove_min 是 `i = 0`，不會往上）。有 test 專門測這個（`RemoveTest.test_a_remove_that_must_move_an_entry_up`）。
- entry 新增或 pop 時也要更新 position dict，不只是 swap 時。

**Tests（`priority_queue_test.py`）與配分**（[repo/.github/workflows/classroom.yml](repo/.github/workflows/classroom.yml)；每組 `timeout 60` 秒）：

| 測試組 | 分數 | 檢查什麼 |
|---|---:|---|
| `BasicsTest` | 6 | 新 queue 是空的、insert 一個、peek 不移除、四次 insert 後的 heap 長相 |
| `RemoveMinTest` | 10 | 依緊急程度取出、同 priority 先來先出、混合 priority 的 tie、insert／remove 交錯、移除後可再 insert、200 個 item |
| `LookupTest` | 4 | 每個 item 的 priority、remove 後的 contains |
| `ChangePriorityTest` | 10 | 變緊急往前、變不緊急往後、改完的 heap 長相、order 不變、改成相同 priority、大量修改 |
| `RemoveTest` | 8 | 從中間移除、移除最緊急、移除最後一個 entry、移除唯一 item、**需要往上移的 remove**、隨機順序全部移除 |
| `ErrorsTest` | 4 | 空 queue 的 `IndexError`、不存在 item 的 `KeyError`、重複 insert 的 `ValueError` |
| `RandomTest` | 4 | 上千次隨機操作，每步和簡單（慢）的 model 比對 |
| `SpeedTest` | 4 | `test_twenty_thousand_of_everything`：各 20,000 次，要在 **5 秒內**（訊息說有 position dict 的 heap 應該遠低於 1 秒） |

### Part 2：help desk（`helpdesk_sim.py`，15 分）

ticket 是 dict：`'id'`、到達的分鐘 `'arrive'`、`'priority'`（1 緊急、2 一般、3 有空再說）、`'duration'`（分鐘）。`helpdesk_tools.py`（提供）負責產生。要寫：

```
simulate(tickets, num_agents, escalations=()) -> [(ticket_id, start_minute, agent_number), ...]
```
- `tickets`：依 id 排好的 ticket list；`num_agents`：agent 編號 0..num_agents−1；`escalations`：`(minute, ticket_id, new_priority)` 的 list。
- 等待中的 ticket 放進**你自己的** priority queue，key 是 ticket id。stub 已經 import 好 `create_pq, pq_insert, pq_remove_min, pq_contains, pq_change_priority, pq_is_empty`。

**每分鐘的規則**（從第 0 分鐘開始，依這個順序）：
1. 這分鐘到達的 ticket 依 id 順序放進 queue，帶它的 priority。
2. 套用這分鐘的 escalation，依列出的順序：改**還在等**的 ticket 的 priority。ticket 還沒到、或已經有 agent 開始處理，就忽略。
3. agent 依編號（0 先）：空閒的 agent 拿最緊急的等待 ticket，這分鐘開始。在第 `m` 分鐘開始 duration `d` 的 ticket，agent 在 `m + d` 分鐘又空閒。

**所有 ticket 都開始了就停**。回傳每個 ticket 一筆紀錄，**依開始的順序**。

| 測試組（`helpdesk_sim_test.py`） | 分數 | 檢查什麼 |
|---|---:|---|
| `OneAgentTest` | 5 | 沒有 ticket、同 priority 先來先服務、最緊急的先、agent 剛好在 ticket 結束那分鐘空閒、閒置時等下一個 ticket |
| `AgentsTest` | 4 | 空閒 agent 依編號拿 ticket、一個 ticket 三個 agent、agent 0 拿最緊急的、大家都忙時到達的 ticket |
| `EscalationTest` | 3 | 升級的 ticket 插隊、ticket 到達那分鐘的 escalation 有效、不在等的 ticket 的 escalation 忽略、也可以變**不**緊急 |
| `OneDayTest` | 3 | 一整天、一整天加 aging |

`helpdesk_tools.aging_escalations(tickets, every)` 把政策轉成 escalation：ticket 每等 `every` 分鐘升一級。`scenarios.py` 跑 20 天（seed 590–609，每天 480 分鐘、約 100 張 ticket），組合是 2／3 個 agent × 不 aging／每 60 分／每 30 分，依**到達時的 priority** 印出平均等待和（括號內）20 天裡最長的等待。

### Part 3：`ANALYSIS.md`（25 分，截止後人工評分，看推理不看文筆）
`compare.py` 用同樣的工作量計時三種 priority queue：unsorted list（`list_pq.py`）、沒有 position dict、靠掃描找 item 的 heap（`scan_heap_pq.py`）、你的。每個 n（1,000、2,000、4,000、8,000；某個 size 超過 4 秒就跳過更大的）做 n 次 insert、n 次 change、n 次 remove，印出每一步的時間。整個跑不到一分鐘。

| 節 | 分數 | 要寫什麼 |
|---|---:|---|
| 1. Predict first | 3 | **跑 `compare.py` 之前**：三種 queue 各填單次 insert／change／remove_min 的 Big-O，並猜 n 加倍時整步的時間（差不多／約 2 倍／比 2 倍多一點／約 4 倍）＋理由。依理由評分，**跑完不要改** |
| 2. Results | 2 | 貼 `python3 compare.py` 印的三個表 |
| 3. Explain the times | 5 | a. 哪些猜對、哪些錯，錯的漏了什麼；b. list append 是 O(1)，為什麼 list 的 insert 步驟像 n² 成長（看 `list_insert`）；c. scan heap 三步裡哪一步慢、為什麼，position dict 讓你省掉什麼；d. position dict 的代價（記憶體、每次 swap 的工作） |
| 4. The help desk | 5 | 貼 `python3 scenarios.py` 的表；a. 2 vs 3 個 agent（不 aging），哪個 priority 為只有 2 個 agent 付出代價、多少；b. 2 agent 不 aging 那列最長的 priority-3 等待，為什麼會等那麼久（**starvation**） |
| 5. Aging | 5 | a. 2 個 agent、每 30 分 aging 對各 priority 平均和最長等待的影響，誰得誰失；b. 為什麼 aging 後 priority-1 最長等待大增（提示：舊的 priority-3 升到 1 時，tie 誰贏？）；c. 你會加 aging、加第三個 agent 還是別的，用數字說；d. 用 list 或 scan heap 時一次 escalation 是什麼 Big-O，為什麼忙的日子更重要 |
| 6. By hand | 5 | **先在紙上做，不要跑**：空 queue 依序 insert `p`6、`q`2、`r`9、`s`4、`t`7、`u`1。(1) 六次 insert 後的 heap（每個 entry 寫 `[priority, order, item]`）和 position dict；(2) 再 `pq_change_priority(pq, 's', 8)`，寫 heap 和 position；(3) 再 `pq_remove_min(pq)`：回傳什麼、heap 和 position。然後用 `show_pq` 對答案，沒對上的話是哪一步、為什麼 |

### `AI_NOTE.md`（10 分）
每題在「Answer:」那行回答（2–5 句），刪掉「(write here)」；`check_note.py` 要求 4 節都在、**每題至少 5 個字**，不看內容。「I did not use AI」如果屬實，是前三題的完整答案。
1. 用了哪個 AI assistant（如果有）、用在哪些檔案？
2. 請它做什麼？摘要你的 prompt。
3. 看完後改了、修了或丟掉什麼？舉一個它弄錯的地方，或說沒發現。
4. 用自己的話：如果 `_swap`（或任何移動 entry 的地方）忘了更新其中一個 entry 的 `position`，哪個 test 或函式會先發現？help desk 會出什麼錯？

### 全部配分（repo README「Points」）
| 項目 | 分數 | 評分方式 |
|---|---:|---|
| Basics | 6 | push 時 GitHub |
| Remove min（含 tie） | 10 | GitHub |
| Lookups | 4 | GitHub |
| Change priority | 10 | GitHub |
| Remove | 8 | GitHub |
| Errors | 4 | GitHub |
| Random operations | 4 | GitHub |
| Speed | 4 | GitHub |
| Help desk：one agent | 5 | GitHub |
| Help desk：several agents | 4 | GitHub |
| Help desk：escalations | 3 | GitHub |
| Help desk：one full day | 3 | GitHub |
| `AI_NOTE.md` 填完 | 10 | GitHub |
| `ANALYSIS.md` | 25 | 截止後人工 |
| **合計** | **100** | Actions 分頁顯示其中 75 分 |

autograder：GitHub Actions，Python 3.11，任何分支 push 都會跑（workflow `branches: '**'`）。

## 注意事項
- **只改** `priority_queue.py`、`helpdesk_sim.py`、`ANALYSIS.md`、`AI_NOTE.md`；tests、helper（`pq_checks.py`、`helpdesk_tools.py`、`list_pq.py`、`scan_heap_pq.py`、`check_note.py`）、`compare.py`、`scenarios.py`、`.github` workflow 都不要改，老師跑原檔（repo README「Submit」）。
- 比較 entry 一律用 `entry_less`，不要用 `<`；`entry_less` 從不比 item（repo README Part 1「Hints」；`priority_queue.py` docstring）。
- `pq_contains` 要 O(1)；`pq_remove`、`pq_change_priority`、`pq_remove_min` 要 O(log n)，`SpeedTest` 20,000 次要在 5 秒內（repo README Part 1；`priority_queue_test.py` 第 277–291 行）。
- 移除中間的 entry 後，搬進來的 entry **可能要往上**（repo README Part 1「Hints」）。
- insert 和 pop 時也要更新 position，不只 swap（同上）。
- 改 priority 時 order 保留（repo README Part 1；`pq_change_priority` docstring）。
- help desk 的每分鐘順序是「到達 → escalation → agent 依編號拿 ticket」；不在等的 ticket 的 escalation 忽略；紀錄依開始順序回傳（repo README Part 2「The rules」）。
- `ANALYSIS.md` §1 要在跑 `compare.py` **之前**寫，之後不要改；§6 先在紙上做（`ANALYSIS.md` §1、§6）。`ANALYSIS.md` 開頭要求答案用自己的話寫。
- 以截止前最後一次 push 評分；push 後看 Actions（repo README「Submit」）。
- 遲交：syllabus 每學季可免一次（事先告知、最多晚 1 週），其他每天 -25%；投影片寫超過 4 天不收（`dsa/assignments.md`）。**A4 已經用掉免罰延期**（Piazza @65，見 [../a4/README.md](../a4/README.md)），A6 遲交會直接扣分；而且 12/9 就是期末。

## 和上課內容的關聯
- **Priority queue ADT、用 list／sorted list／AVL／heap 實作的比較；heap 的 shape 和 order、陣列表示法（children `2i+1`、`2i+2`，parent `(i-1)//2`）**：Class 11（11/4），[`dsa/lectures/2026-11-04/notes.md`](../../lectures/2026-11-04/notes.md) 重點摘要第 3–5 點（[00:29:04]–[00:54:01]）。對應 Part 1 的 heap order invariant 和 `ANALYSIS.md` §1、§3 的 list vs heap。
- **現場寫 `heap_insert`／`bubble_up`、`heap_pop`／`bubble_down`**：Class 12（11/16），[`dsa/lectures/2026-11-16/notes.md`](../../lectures/2026-11-16/notes.md)「前半堂」第 4–5 點和「講義補充」第 2–3 點（講義 p2–p3）。這就是 README 說的「從上課寫的 heap code 開始」。
- **heap `pop` 的常見錯誤（只剩一個元素時 `pop()` 後 `heap[0] = …` 會 `IndexError`）**：同檔重點摘要第 1 點（[00:53:02]–[01:02:01]）。A6 的 `pq_remove_min`／`pq_remove`「移除唯一 item」「移除最後一個 entry」test 正好在測這個。
- **`bubble_down` 的 off-by-one 現場除錯**：Class 13（11/18），[`dsa/lectures/2026-11-18/notes.md`](../../lectures/2026-11-18/notes.md) 重點摘要第 3 點（[00:24:00]–[00:51:06]）。
- **Python `heapq`、heap sort**：同檔第 2、4 點。A6 要自己寫 heap（要維護 position dict，`heapq` 做不到）。
- **Python `dict` 就是 hash table，查詢平均 O(1)**：同檔第 7、10 點。`pq_contains` O(1) 和 `ANALYSIS.md` §3d「position dict 的代價」靠這個。
- **Dijkstra 的 decrease-key**：README 提到 graph 時會用到，屬於 Module 8 Graphs，還沒上。

## 還不確定的地方
1. **要不要到 Canvas 交 repo URL**：README「Submit」只說 push 到 `master`。A4、A5 的週規劃都提醒到 Canvas 交 URL，保險起見 push 後也交。
2. **Speed 的實際門檻**：test 的上限是 5 秒，但訊息說「well under 1」；autograder 跑在 GitHub runner 上，速度和本機不同。照 O(log n) 寫應該都過。
3. **`ANALYSIS.md` §5b 的 tie**：提示問「舊的 priority-3 升到 1 時，tie 誰贏」。依 `entry_less`，同 priority 比 order，order 小（較早 insert）的贏，而 escalation 不改 order，所以升上來的舊 ticket 會排在新來的 priority-1 前面。這是依 spec 推論的，跑 `scenarios.py` 時再對照。
4. **repo 建立時間**：`digests/2026-11-22.md` 記 11/21 18:47 PT；`digests/2026-11-22-weekly.md` 寫「repo 11/21 建立，只有 starter」，一致。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-11-23 | 第一次整理 |

DSA 課用了 AI 要附 chat session 或註明。
