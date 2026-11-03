# DSA A4：Bug Hunt（Help desk bug hunt）

> 原文：[spec.md](spec.md)（[Canvas assignment 11814804](https://canvas.uw.edu/courses/1917417/assignments/11814804)，Canvas 說明是空白；starter repo README：`uw-python-fall2026/assignment-4-mileschintw`，blob 5e06266，標題「Assignment 4: Help desk bug hunt (60 points)」；repo 其他檔案存在 [repo/](repo/)）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-11-01（日）11:59 PM PST**（Canvas `due_at` 2026-11-02T07:59:59Z，和 `assignments.md` 一致；原本是 10/30（五））。截止後才交：Canvas 在 2026-11-03 晨報時已變成 `submitted`；Piazza @65 申請一次性免罰延期，待回覆 |
| 分數 | Canvas 100 分；README 寫 60 分（autograder 24 + 截止後老師評 36，見「還不確定的地方」） |
| 繳交方式 | push 到 `uw-python-fall2026/assignment-4-mileschintw`，**再到 Canvas 交 repo URL**；每次 push 都會跑 autograder（repo 的 **Actions** 分頁） |
| 要交的東西 | 只有這 3 個檔案會被評分：<br>1. `help_desk.py`（修好的版本）<br>2. `test_regressions.py`（你的 test，至少 3 個）<br>3. `FINDINGS.md`（嫌疑表格至少 4 列 + 3 題 reflection）<br>其他檔案改了也會被忽略 |

本機工作 clone：`D:\Repos\assignment-4-mileschintw`（branch `main`；`gh` 確認你有 push 權限）。

> **[repo/](repo/) 存的是 repo 目前的內容**。從 2026-11-03 起，`help_desk.py`、`test_regressions.py`、`FINDINGS.md` 是你自己 push 的版本，不是 starter。老師的原版還是 [repo/help_desk_original.py](repo/help_desk_original.py)（blob 44a44ce），下面的函式規格都取自 docstring，兩份的 docstring 一樣。

## 學習目標
（README 開頭）
- 練習和 AI assistant 合作的基本功：AI（或同學、自己的眼睛）提出的問題都只是**嫌疑（suspicion）**，要用 test 證明才算數。
- 找出 bug、證明它是真的、修好它，並留下 regression test，讓 bug 不會悄悄回來。
- 分辨「看起來錯」和「真的錯」：AI 會報不存在的問題，也會漏掉真的問題。

## 要做什麼

### 程式（README「The code」）
`help_desk.py` 用課堂上的元件組成：dynamic array、stack、queue，加上一組 help desk 函式和一個括號檢查器。ticket 送進 queue、依序處理、處理完移到 closed list；最近一次關閉的 ticket 可以用 `undo_close` 重新打開。

- **唯一的「正確」定義是每個函式的 docstring**。code 和 docstring 不一致就是 bug。
- bug 不只一種：**答案錯**、**不該 crash 卻 crash**、**速度太慢**。

### 函式規格（來自 [repo/help_desk.py](repo/help_desk.py) 的 docstring）
資料格式：dynamic array = `{'slots': [...], 'size': n}`；stack = Python list；queue = `{'items': [...], 'head': i}`（`head` 之前的是已經 dequeue 掉的）；desk = `{'open': queue, 'undo': stack, 'closed': dynamic array, 'next_id': n}`；ticket = `{'id': n, 'text': text}`。

| 函式 | docstring 規定的行為 |
|---|---|
| `da_create()` | 回傳空的 dynamic array，起始容量 4 |
| `da_append(arr, value)` | 加到尾端；滿了就**容量加倍**，元素全部保留。append n 個總共 **O(n)** |
| `da_get(arr, index)` | 回傳 index 的元素，`0 <= index < size`；其他 index（含負數）raise `IndexError` |
| `da_remove_last(arr)` | 移除並回傳最後一個元素；空的時候 raise `IndexError` |
| `da_to_list(arr)` | 依序回傳所有元素，一般 list |
| `stack_create()` | 回傳空 stack |
| `stack_push(s, value)` | 放到 top |
| `stack_pop(s)` | 移除並回傳 top；**空 stack 回傳 `None`** |
| `stack_is_empty(s)` | 沒有東西時回傳 True |
| `queue_create()` | 回傳空 queue |
| `queue_enqueue(q, value)` | 加到 queue 尾端 |
| `queue_dequeue(q)` | 移除並回傳最前面；空的回傳 `None`。每次 **O(1)**，n 次共 O(n) |
| `queue_peek(q)` | 回傳最前面但不移除；空的回傳 `None` |
| `queue_size(q)` | 回傳還在等的數量 |
| `queue_push_front(q, value)` | 放到 queue 的**最前面**，下一個被 dequeue 的就是它 |
| `desk_create()` | 回傳空的 help desk |
| `submit(desk, text)` | 把 ticket 加到 open queue 尾端並回傳；id 從 1 開始、2、3…，**不重複使用** |
| `work_next(desk)` | 取 open queue 最前面的 ticket 關閉：加到 closed list 尾端，回傳它；沒有 open ticket 回傳 `None` |
| `undo_close(desk)` | 重新打開「最近關閉、還沒被重新打開過」的 ticket：**離開 closed list**、回到 open queue 的**最前面**（下一個被處理）；回傳它，沒東西可 undo 回傳 `None` |
| `next_ticket(desk)` | 回傳 `work_next` 會關閉的那張，不關閉；沒有就 `None` |
| `open_count(desk)` | open ticket 數 |
| `closed_count(desk)` | closed ticket 數 |
| `closed_ids(desk)` | closed ticket 的 id，依關閉順序 |
| `brackets_balanced(text)` | 每個 `(`、`[`、`{` 都被對應的括號依正確順序關閉才回傳 True；其他字元忽略；空字串算 balanced |

### 步驟（README「What to do」）
1. **Hunt**：讀 code、執行、亂試，也可以請 AI 列嫌疑。
2. **Prove**：每個嫌疑都在 `test_regressions.py` 寫一個 test。
   - 認為是 **bug**：test 在 `help_desk_original.py` 上 **FAIL**，修好的 `help_desk.py` 上 **PASS**。
   - 查過發現**沒問題**：test 在兩份上都 **PASS**。
3. **Fix**：修 `help_desk.py`，函式名稱和 docstring 契約都不能變。**不要改 `help_desk_original.py`**。
4. **Record**：填 `FINDINGS.md`（見下）並回答 3 題 reflection。

### `FINDINGS.md`（[repo/FINDINGS.md](repo/FINDINGS.md)）
表格欄位：`#`｜`Function`｜`What I think is wrong`｜`Idea came from (me / AI / other)`｜`Status`｜`Test name`，至少 4 列。

| Status | 意思 |
|---|---|
| `confirmed` | Test name 欄寫的 test 在 original 上 FAIL、在修好的版本上 PASS |
| `refuted` | test 在兩份上都 PASS，證明 code 沒問題 |
| `unproven` | 判斷不出來；Test name 欄留空 |

Reflection（每題寫在「Answer:」那行，刪掉「(write here)」，**每題至少 8 個字**，checker 會檢查）：
1. 哪個嫌疑最後不是 bug，或和你一開始想的不一樣？怎麼發現的？
2. 在改 code 之前，是什麼讓你相信某個 bug 是真的？
3. 有用 AI 嗎？有：它做得好的一件事、做錯或漏掉的一件事。沒有：你希望有人幫忙的一件事。

### 本機檢查（README + [repo/check_hunt.py](repo/check_hunt.py)）
```
python3 -m unittest test_regressions -v      # 你的 test，跑在修好的 code 上
python3 -m unittest test_already_correct -v  # 本來就對、必須維持的行為
python3 check_hunt.py                        # 全部檢查 + 摘要
python3 check_hunt.py own|already|findings|reflection   # 單項，和 autograder 一樣
```
`check_hunt.py` 會自己把 `help_desk_original.py` 複製成 `help_desk.py` 放到暫存資料夾去跑，不用手動換檔。2026-11-02 在 starter 上跑的結果：四項都是 `NOT YET`（只有 1 個範例 test；`help_desk.py` 和 original 一樣所以 already 不計；表格 0 列；reflection 空白）。2026-11-03 抓到的提交版本：`test_regressions.py` 有 3 個 test（範例 1 個 + 你寫的 2 個）、`FINDINGS.md` 表格填了 1 列（至少要 4 列）、reflection 還是空白、`help_desk.py` 改了 1 處。這次排程沒有跑 checker，請到 repo 的 Actions 分頁看 autograder 的結果。

### 配分（README「Points」+ [repo/.github/workflows/classroom.yml](repo/.github/workflows/classroom.yml)）

| 項目 | 分數 | push 後看得到？ | autograder 指令 |
|---|---:|---|---|
| 你的 test 在修好的 code 上全過（至少 3 個） | 4 | 是 | `check_hunt.py own` |
| 本來就對的行為仍然正確（`test_already_correct.py`；`help_desk.py` 至少要改一處才計分） | 8 | 是 | `check_hunt.py already` |
| `FINDINGS.md` 表格至少 4 列，每列的 test 表現和寫的一致 | 6 | 是 | `check_hunt.py findings` |
| Reflection 有回答 | 6 | 是 | `check_hunt.py reflection` |
| 每個真 bug 有修好 | 每個 3 | 截止後 | 老師評 |
| 每個真 bug 有你寫的 regression test，在「只有那一個 bug」的版本上會 fail | 每個 3 | 截止後 | 老師評 |

push 後 GitHub 顯示前 24 分；其餘 36 分老師截止後補上，並列出漏掉的項目。autograder 用 Python 3.11，每項 timeout 120 秒。

`test_already_correct.py` 檢查的行為：空 array、append 後讀回、array 越界 raise、stack LIFO、queue FIFO、空 queue 回 None、大量 item 依序出來且最後 queue 是空的、ticket id 從 1 遞增、ticket 依序處理、沒東西可處理、幾個 balanced／unbalanced 字串。

## 注意事項
- **Test 只能 import**：`unittest`、`random`、`time`、`copy`、`itertools`、`math`、`string`、`collections`，以及 `help_desk` 裡的東西（README「Rules for the tests」）。
- **Test 不能用**：讀檔、`inspect`、`os`、`sys`、`eval`／`exec`、`sleep`、任何雙底線名稱（如 `__code__`）。要測行為，不是測 code 怎麼寫（README「Rules for the tests」）。checker 的 lint 另外禁止 `open`、`compile`、`globals`、`locals`、`vars`、**`dir`**、`getattr`、`setattr`、`delattr`、`__import__`、`input`、`breakpoint`，字串常數裡也不能出現 `__`（[repo/check_hunt.py](repo/check_hunt.py) `BANNED_NAMES`、`lint()`）。
- 懷疑速度問題時，test 可以用 `time.time()` 量自己的時間（README「Rules for the tests」）。
- 亂數一律用 `random.Random(seed)`，不要用未設種子的 `random`（README「Rules for the tests」）。
- **不要「修」沒壞的函式**：會讓 already-correct 的 test fail，也可能破壞你的修正（README「Points」）。
- 修的時候函式名稱和 docstring 契約都要保留（README「What to do」第 3 步）。
- **保留 AI 對話紀錄**直到課程成績確定。不用交、不影響分數，萬一有 academic integrity 疑問時用來保護自己（README「IMPORTANT」；10/26 課堂 [00:11:00]–[00:13:00]）。
- Reflection 依「完整、誠實」評分，不看你有沒有用 AI（README「Points」）。
- 遲交：syllabus 每學季可免一次（事先告知、最多晚 1 週），其他每天 -25%；投影片寫超過 4 天不收（`dsa/assignments.md`）。

## 和上課內容的關聯
- **Dynamic array 的 growth strategy、amortized O(1)**：`da_append` 要求加倍、n 次 append 總共 O(n)。Class 4（10/12）比較 add one／add 10／double 的總複製量，見 [`dsa/lectures/2026-10-12/notes.md`](../../lectures/2026-10-12/notes.md) 重點摘要第 37–54 行；Class 5（10/14）講義 p2、p10 的 amortized 推導，見 [`dsa/lectures/2026-10-14/notes.md`](../../lectures/2026-10-14/notes.md)「Amortized cost」。
- **size / capacity、resize**：Class 2（10/5），[`dsa/lectures/2026-10-05/notes.md`](../../lectures/2026-10-05/notes.md)「名詞解釋」。
- **Stack ADT（LIFO、空 stack pop）**：Class 3（10/7）用 array／linked list 實作 stack；Class 4 提到 test 要涵蓋「空 stack pop」等邊界（[`2026-10-12/notes.md`](../../lectures/2026-10-12/notes.md)「和作業 / 考試的關聯」）。
- **Queue 與 `pop(0)` 為什麼慢**：Class 5（10/14）講義 p6–p8，用 head index 或 deque 讓 dequeue O(1)。
- **unittest、先寫 test 再修 code**：Class 3（10/7）、Class 4（10/12）。
- **AI 政策**：A4 是第一個允許用 AI 的作業（10/21 課堂 [00:28:08]；10/26 課堂 [00:10:00]–[00:13:00]）。

## 還不確定的地方
1. **分數**：README 寫 60 分（24 + 36），Canvas 是 100 分。可能 Canvas 會等比例換算，沒有公告。
2. **分支**：README「Submit」說 push 到 `master`，但這個 repo 的預設分支是 **`main`**（`gh api` 和本機 clone 都是 `main`，沒有 `master`）。autograder 會在任何分支 push 時執行。推測 README 的 `master` 是從舊作業複製來的，push 到 `main` 應該就可以；不放心的話在 Piazza 確認。
3. **真 bug 有幾個**：README 只說「several」，沒有給數量；漏掉的會在截止後由老師列出。
4. **延期**：已過 11/1 截止，Piazza @65（申請重寄 repo 邀請 + 使用一次免罰延期）到 2026-11-02 晚上還沒有回覆。11/2 用 `gh` 查，你已經有這個 repo 的 push 權限，所以邀請的問題應該已經解決。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-11-02 | 第一次整理 |
| 2026-11-03 | repo 檔案 FINDINGS.md、help_desk.py、test_regressions.py 改了（是你自己 push 的作業；Canvas spec 和 README 都沒變）。更新截止列的繳交狀態，註明 repo/ 現在是提交版本，補上提交版本的進度 |

DSA 課用了 AI 要附 chat session 或註明。
