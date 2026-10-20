# DSA A3：Stacks, Queues and Testing

> 原文：[spec.md](spec.md)（[Canvas assignment 11814801](https://canvas.uw.edu/courses/1917417/assignments/11814801)，Canvas 說明是空白；starter repo README：`uw-python-fall2026/assignment-3-mileschintw`，blob a169e62，標題「Assignment 3: UW-Euchre」）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-10-25（日）11:59 PM PDT**（Canvas `due_at` 2026-10-26T06:59:59Z，和 `assignments.md` 一致；原本是 10/23（五），10/19 課堂上老師確認作業都是週日截止） |
| 分數 | Canvas 150 分；README 是自動 100 + Assignment Review 25 = 125 分（見「還不確定的地方」） |
| 繳交方式 | push 到 `uw-python-fall2026/assignment-3-mileschintw`，**再到 Canvas 交 repo URL**；每次 push 都會跑 autograder（repo 的 **Actions** 分頁） |
| 要交的東西 | 1. `game_structures.py`（Part 1：deck、hand、card、node）<br>2. `game_play.py`（Part 2：遊戲函式）<br>3. 自己的 test 建議另開新檔，例如 `my_tests.py`（不是必交） |

## 學習目標
（README「Objectives」）
- 實作應用型資料結構：stack 和 doubly linked list
- 用這些結構做出能玩的東西：一個紙牌遊戲
- 寫第一個 sort 函式
- 熟悉 `unittest`
- 學會檢查自己的資料結構是否正確，而不只是「看起來能動」

## 要做什麼
做一個 2 人版 Euchre（念作「U-ker」）的核心元件。分兩部分，**先做 Part 1**：Part 2 建在 Part 1 上，Part 1 的 bug 會在 Part 2 變成莫名其妙的失敗（README「Overview」）。

### UW-Euchre 規則（README「Basic Rules Of UW-Euchre」）
- 2 人遊戲，5 個 round 後分數最多的人贏。
- 一個 round：每人發 5 張牌、選 trump（這一 round 最大的花色），然後輪流出牌比 trick；拿到最多 trick 的人贏這個 round。
- 一個 trick 由出最大牌的人贏。
- 出牌規則：
  - 第一個出牌的人可以出任何牌。
  - 第二個人必須 **follow suit**：手上有同花色就一定要出同花色（可以選哪一張）。
  - trump 花色的牌大於所有其他牌。例：Spades 是 trump 時，9♠ 大於 A♦。
  - 同花色內（包括 trump）比牌面，Ace 最大。
- **Player 1（電腦）永遠先出牌**、領第一張。
- 牌組：A、K、Q、J、10、9，四種花色（Spades、Diamonds、Hearts、Clubs），共 24 張。

### 檔案（README「Provided Starter Code」）

| 檔案 | 用途 | 要改嗎 |
|---|---|---|
| `game_structures.py` | Part 1：deck（stack）和 hand（doubly linked list） | **要** |
| `game_structures_test.py` | Part 1 的測試 | **不要** |
| `game_play.py` | Part 2：遊戲函式 | **要** |
| `game_play_test.py` | Part 2 的測試 | **不要** |
| `hand_invariants.py` | `assert_hand_valid`、`assert_cards_conserved` | **不要** |
| `uw_euchre.py` | 全部做完後在 terminal 玩遊戲 | 不用改 |

### Part 1：資料結構（`game_structures.py`）
實作 deck（stack）、hand（doubly linked list），以及放進去的 card 和 node。對應的自動評分步驟：

| 步驟 | 分數 |
|---|---:|
| Deck：create、push、peek | 7 |
| Deck：pop、is empty、LIFO | 6 |
| Card node 和 empty hand | 4 |
| Hand：add a card | 8 |
| Hand：peek at a card | 6 |
| Hand：remove a card | 12 |
| Hand：移除時維持合法 linked list | 8 |
| Hand：隨機操作結果和 Python list 一致 | 4 |
| **Part 1 小計** | **55** |

### Part 2：遊戲（`game_play.py`）
用 Part 1 的結構實作 shuffle、deal、legal moves、誰贏這個 trick、sort hand 等：

| 步驟 | 分數 |
|---|---:|
| Shuffle and deal | 8 |
| Return a hand to the deck | 6 |
| Legal moves | 5 |
| Compare cards | 8 |
| Who won the trick | 4 |
| Swap a card with the next one | 6 |
| Sort a hand | 6 |
| Play a whole round | 2 |
| **Part 2 小計** | **45** |

### Assignment Review（25 分）
人工評 code quality：命名、結構、可讀性、效率（README「Assignment Review」）。

### 怎麼跑（README「Running」）

| 目的 | 指令 |
|---|---|
| Part 1 測試 | `python3 -m unittest game_structures_test` |
| Part 2 測試 | `python3 -m unittest game_play_test` |
| 單一測試 | `python3 -m unittest game_structures_test.HandTestCase.test_add_1card_to_hand` |
| 顯示每個 test 名稱 | 加 `-v` |
| 玩遊戲（Part 1、2 完成後） | `python3 uw_euchre.py` |

這些就是 autograder 用的指令。Windows 上用 `python`。

### 自我檢查（README「Checking your own work」）
`assert_hand_valid(hand)` 檢查 hand 是合法的 doubly linked list：
- 沿 `next` 走過每張牌恰好一次並結束（沒有 cycle）
- 找到的張數等於 `hand['num_cards_in_hand']`
- 第一張的 `prev` 是 `None`
- 其他每張的 `prev` 指回前一張

`assert_cards_conserved` 檢查 deck 加兩手牌剛好是一開始那些牌：沒有遺失、重複或憑空多出。可以在自己的 test 或除錯時每個操作後呼叫。

## 注意事項
- **不要改**提供的 test 檔和 `hand_invariants.py`；自己的 test 放新檔（README「Provided Starter Code」）。
- hand 必須是用 card node 串成的**真正 doubly linked list**；test 檢查結構，用 Python list 不會過。deck 是當 stack 用的 Python list（README「Rules and notes」）。
- `sort_hand` 要拿滿分就**自己寫 sort**，不能用 `sorted()` 或 `list.sort()`；提示是 `swap_card_with_next()` 讓 bubble sort 很好寫（README「Rules and notes」）。
- 每個評分步驟要**整組 test 全過**才拿分，依組給部分分數（README「Grading」）。
- 每個步驟有時間限制，infinite loop 會讓那一步失敗而不是卡住（README「Grading」）。
- **不可以把這份作業的任何 code 貼給 ChatGPT 或其他 AI assistant 求助**（README「Rules and notes」）。
- A2、A3 期間要關掉編輯器的 code suggestion（`dsa/lectures/2026-10-07/notes.md`，[00:37:05]）。
- Piazza @36 老師答：精神是用 Python primitives 實作資料結構；deck 是 stack，用 list 當 stack 即可；大致不需要 slicing 或 list modification 之類「fancy」寫法；沒有明確的禁用清單，有具體疑問再問（`dsa/piazza/baseline-2026-10-18.md`）。
- 作業更新或澄清會寫在 README 和 Piazza；更新時要自己解衝突（README「Updates to the assignment」）。
- 沒有 push 到 GitHub 而且把連結交到 Canvas，就不算繳交（README「Submission」；A1、A2 的 Canvas 說明同樣規定）。
- 遲交：syllabus 是每學季可免一次（事先告知、最多晚 1 週），其他每天 -25%；投影片是每天 -25%、超過 4 天不收（`assignments.md`）。

## 和上課內容的關聯
- **Stack 實作與 unittest**：Class 3（10/7）`in-class-code` 的 `Mod1/stack.py`、`test_stack.py`，包括 `assertRaises` 測錯誤情境（`dsa/lectures/2026-10-07/notes.md`「和作業 / 考試的關聯」）。
- **Linked stack、測試邊界案例**：Class 4（10/12）push 時先設 `next` 再改 head（[00:36:02]）、測試要涵蓋開頭／結尾／中間／不存在／空 stack pop（`dsa/lectures/2026-10-12/notes.md`「和作業 / 考試的關聯」）。
- **List 當 stack 是 O(1)**：Class 5（10/14）講義 p6；同一套 test suite 跑在不同實作上（講義 p1）、`unittest` 行為測試 [01:17:01]–[01:29:01]（`dsa/lectures/2026-10-14/notes.md`「和作業 / 考試的關聯」）。
- **Linked list 的 pointer 順序與常見錯誤**：Class 2（10/5）的檢查清單（改 pointer 前先存 next、更新 size、tail 的更新），套用到 doubly linked list 的 `prev`／`next`（`dsa/lectures/2026-10-05/notes.md`「和作業 / 考試的關聯」）。
- **A2 的 `list_checks.py` invariant 檢查**：A3 的 `hand_invariants.py` 是同樣的概念（見 [A2 README](../a2/README.md)）。

## 還不確定的地方
- **配分對不上**：README 是 100 + 25 = 125 分，Canvas 是 150 分。Piazza @51（10/19 晚上）有同學問，老師和 TA 都還沒回覆（`digests/2026-10-20.md`）。
- **標題有 Queues，內容沒有 queue**：Canvas 標題是「Stacks, Queues and Testing」，但 README 只要求 stack（deck）和 doubly linked list（hand），沒有 queue。Class 5 講的 queue 和 `deque`（`dsa/lectures/2026-10-14/notes.md`）在 A3 裡看起來用不到。以 README 為準。
- **`find` 的疑問可以結案**：Class 5 notes 待釐清第 7 點問 A3 會不會要 stack 的 `find`；README 的 deck 只列 create、push、peek、pop、is empty，沒有 find。
- **Canvas 說明是空白**：作業內容只在 repo README。
- 10/19 Class 6 老師說作業 invite 流程會改（`dsa/lectures/2026-10-19/notes.md`，[00:15:11]），A3 repo 已經可以存取，不受影響。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-10-20 | 第一次整理 |

DSA 課用了 AI 要附 chat session 或註明
