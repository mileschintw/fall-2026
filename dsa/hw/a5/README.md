# DSA A5：BSTs and AVLs（Binary search trees）

> 原文：[spec.md](spec.md)（[Canvas assignment 11814818](https://canvas.uw.edu/courses/1917417/assignments/11814818)，Canvas 說明是空白；starter repo README：`uw-python-fall2026/assignment-5-mileschintw`，blob 2d037e3，標題「Assignment 5: Binary search trees (150 points)」；兩個 part 的 README 和其他檔案存在 [repo/](repo/)）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-11-22（日）11:59 PM PST**（Canvas `due_at` 2026-11-23T07:59:59Z、repo README「Due: Sunday, November 22, 11:59 pm」、`assignments.md` 一致；原本是 11/6（五），10/20 移到期中考後） |
| 分數 | repo README 寫 **150 分**（Part 1 50 + Part 2 100）；Canvas 是 100 分（見「還不確定的地方」） |
| 繳交方式 | commit 並 push 到 `uw-python-fall2026/assignment-5-mileschintw` 的 **`master`**（這個 repo 的預設分支確實是 `master`，`gh api` 2026-11-04 確認），一次 push 包含兩個 part；**以截止前最後一次 push 評分**。push 後看 repo 的 **Actions** 分頁。週規劃另外提醒要到 Canvas 交 repo URL（`digests/2026-11-01-weekly.md`；A4 也是這樣交） |
| 要交的東西 | **Part 1**：`part1/bst.py`（6 個函式）、`part1/ANALYSIS.md`（6 節）<br>**Part 2**：`part2/test_bst.py`（你的 test，至少 8 個）、`part2/AI_NOTE.md`（4 題）<br>Part 2 只有這兩個檔案計分；不要改提供的 test、helper 和 `.github` workflow，老師跑的是原檔 |

Repo 在 2026-11-04 5:13 AM PST 建立（`digests/2026-11-04.md`）。[repo/](repo/) 存的是 starter。

## 學習目標
（repo README、`part1/README.md`、`part2/README.md` 開頭）
- 自己寫一棵用 node dict 組成的 binary search tree（insert、search、min／max、delete 三種情況），再和 AVL tree 比較，看平衡為什麼重要。
- 理解樹的**形狀（height）**決定速度；sorted 輸入會讓 BST 退化。
- 練習「看一個 tree function、找出哪裡錯、寫出抓得到它的 test」（mutation testing）。
- 期中、期末是紙筆、不能用 AI，會考寫和 trace tree code（Part 1）以及找 bug 寫 test（Part 2）。老師建議**在 11/9 期中考前先做 Part 1**，是樹題目最好的練習（repo README；10/26 課堂 [00:13:00]）。

## 要做什麼

| 資料夾 | Part | 可以用 AI 嗎？ | 分數 |
|---|---|---|---:|
| `part1/` | 寫 BST，和 AVL 比較 | **不行** | 50 |
| `part2/` | Mutant hunt：寫 test 抓出有 bug 的樹 | 可以，**只限 `part2/` 的檔案** | 100 |

在 PyCharm 開整個 repo，各 part 的指令在各自資料夾裡跑；`ModuleNotFoundError` 時把 `part1`、`part2` 都設成 **Mark Directory as > Sources Root**（repo README「Working in this repo」）。

### Part 1：Binary search tree vs AVL（50 分，不能用 AI）
樹的表示法：node = `{'payload': value, 'left': node_or_None, 'right': node_or_None}`，空樹是 `None`。`tree_tools.py` 提供 `create_tree_node` 等 helper，不要改。可以從上課寫的 code 開始，但每一行都要懂；**不要抄 `part2/bst_reference.py`**（`part1/README.md`）。

#### 要寫的函式（`part1/bst.py`，規格取自 docstring 和 `part1/README.md`）
| 函式 | 規定的行為 |
|---|---|
| `bst_insert(root, value)` | 放進樹（in place）並回傳 root；`None` 進來就回傳新 node；**已經有的值忽略** |
| `bst_search(root, value)` | 回傳**存這個值的 node**（不是 True/False），沒有就 `None` |
| `bst_min(root)` | 回傳最小值的 node；空樹 `None` |
| `bst_max(root)` | 回傳最大值的 node；空樹 `None` |
| `bst_delete(root, value)` | 刪掉 value（in place），回傳**剩下那棵樹的 root**；值不在樹裡就什麼都不變；結果仍是 BST |
| `search_steps(root, value)` | 照 `bst_search` 的方式搜尋，回傳**看過幾個 node**（找到的那個也算）；空樹 0 步。也要能用在 `avl.py` 的樹上（key 相同） |

**Delete 的三種情況**（`part1/README.md`）：
- 沒有 child：直接移除。
- 一個 child：child 接替它的位置。
- 兩個 children：把 right subtree 的最小值（**successor**）複製到這個 node，再從 right subtree 刪掉那個 successor。
- root 可能改變：刪掉唯一的 node 得到 `None`；刪掉只有一個 child 的 root 回傳那個 child。

Loop 或 recursion 自己選；後面的比較會顯示這個選擇的影響。

#### Tests（`part1/bst_test.py`，不要改；autograder 每組 timeout 60 秒）
| 測試組 | 分數 | 檢查什麼 |
|---|---:|---|
| `InsertTest` | 8 | 空樹插入產生 node、範例樹的形狀、重複值被忽略 |
| `SearchTest` | 8 | 每個值都找得到、沒有的值回 `None`、空樹 search |
| `MinMaxTest` | 4 | 範例樹的 min／max、空樹 |
| `DeleteTest` | 10 | 刪 leaf、一個 child、兩個 children、刪 root、刪不存在的值、全部刪光 |
| `SearchStepsTest` | 5 | 範例樹的步數、找不到的值的步數、在 AVL 樹上的步數 |

一開始每個 test 都是 `NotImplementedError`，這是起點，不是 repo 壞了。test 通過只代表「大概是對的」，不保證每個角落都對（`part1/README.md`「Run the tests」）。

```
cd part1
python3 -m unittest bst_test -v
python3 -m unittest bst_test.SearchTest   # 只跑一組
```

#### 比較與 `ANALYSIS.md`（15 分，人工評分，看推理不看文筆）
`compare.py`（不要改）把同一組值 1..n 依 **sorted** 和 **shuffled**（`random.Random(590)`）兩種順序插入你的 BST 和 `avl.py` 的 AVL tree，n = 100、500、1,000、2,000，印出各自的 height 和平均 search 步數（用你的 `search_steps`）。某列顯示 `RecursionError` 不是 script 壞掉，那是結果，第 5 節會問。

| 節 | 要寫什麼 |
|---|---|
| 1. Predict first | **跑 `compare.py` 之前**猜 1..1,000 sorted／shuffled 時兩種樹的 height（填表）並說明理由；依理由評分，**跑完不要改** |
| 2. Results | 貼上 `python3 compare.py` 印出的表 |
| 3. BST sorted vs shuffled | 為什麼 sorted 時 BST 高很多？「BST avg steps」欄說明兩種情況下 search 是 n 的什麼量級？ |
| 4. AVL tree | AVL 的 height 和 log₂(n)、上課的上限（約 1.44 log₂(n)）比起來如何？為什麼 sorted 不會傷到它？對 AVL 來說 sorted 比 shuffled 好還是差？為什麼？ |
| 5. Recursion | 有沒有出現 `RecursionError`？有：哪個函式、多大、為什麼是那個大小。沒有：recursive `bst_insert` 在這些輸入大概多大會出事。不管哪種：為什麼 AVL 的 recursive insert 在這裡安全？ |
| 6. Sorted data | 舉一個資料會依序（或幾乎依序）到達的實際情境，那時要用什麼取代一般 BST？ |

### Part 2：Mutant hunt（100 分，可以用 AI，只限 `part2/`）
這部分**不寫樹**，是幫提供的正確樹 `bst_reference.py`（`bst_insert`、`bst_search`、`bst_min`、`bst_max`、`bst_delete`）寫 test。老師拿你的 test 去跑有 bug 的版本（**mutant**），每個 mutant 只有一個地方錯；只要你有一個 test fail、error 或 hang，那個 mutant 就算**被抓到**。分數 = 抓到幾個。

#### 規格（`part2/README.md`「The specification」+ `bst_reference.py` docstring）
每個 mutant 都違反其中某一條：

| 規則 | 內容 |
|---|---|
| Size | 五個函式都要能處理由**最多 5,000 個值、任何插入順序**建出的樹 |
| Speed | 每個函式的時間和**樹高**成正比，不是和值的數量成正比 |
| `bst_insert` | 空樹回傳新 node；否則 in place 修改並回傳 root；已有的值忽略；用 `<` 和 `==` 比較，**int、float、string 都要能用** |
| `bst_search` | 回傳存這個值的 node，沒有就 `None` |
| `bst_min`／`bst_max` | 回傳最小／最大值的 node；空樹 `None` |
| `bst_delete` | 值不在就不變；否則 in place 修改，結果是**存著其他所有值**的 BST，而且**不會比刪之前高** |

`tree_tools.py` 提供 `create_tree_node`、`inorder_values`、`tree_size`、`tree_height`（height 數 edge：單一 node 是 0，空樹是 −1）。

#### 檔案
| 檔案 | 用途 |
|---|---|
| `bst_reference.py` | 正確的樹，不要改 |
| `test_bst.py` | **你的 test 寫在這裡**，唯一要改的 code 檔；starter 有一個範例 test 和 `build(values)` helper |
| `AI_NOTE.md` | 簡短說明你怎麼做的（10 分） |
| `practice_mutants/p1.py`–`p4.py` | 四個練習用 mutant |
| `check_tests.py` | 在自己電腦上看會檢查什麼 |

```
cd part2
python3 -m unittest test_bst -v      # 你的 test，跑在正確的樹上
python3 check_tests.py               # 全部檢查 + 摘要
python3 check_tests.py mine          # 不計分：用你 part1/bst.py 的樹代替 reference
```
`mine` 在兩個 part 都完成後值得跑一次：如果某個 test 在你的 Part 1 樹上 fail、在 reference 上過，可能是找到你自己的 bug，也可能是 Part 1 允許 recursion，而你的樹處理不了 Part 2 要求的 5,000 個值（`part2/README.md`「Run your tests」）。

#### 配分（`part2/README.md`「How you are graded」+ [repo/.github/workflows/classroom.yml](repo/.github/workflows/classroom.yml)）
| 項目 | 分數 | 條件 | autograder 指令 |
|---|---:|---|---|
| Gate | 15 | 你的 test 在 reference 上**全過**，而且**至少 8 個 test**；60 秒內跑完（`check_tests.py` `MIN_TESTS = 8`） | `check_tests.py gate` |
| Practice mutants | 15 | 抓到 p1（5）、p2（4）、p3（3）、p4（3）；**gate 過了才算** | `check_tests.py mutant p1`…`p4` |
| Hidden mutants | 60 | 截止後老師用 **21 個隱藏 mutant** 跑；gate 過了才算；會附上你漏掉的規則清單 | 老師評 |
| AI note | 10 | `AI_NOTE.md` 四題都填 | `check_tests.py note` |

每個 mutant 的 time limit 是 `min(60, max(10, 5 × 你的 suite 在 reference 上的秒數))`，超過算 hang，也就是抓到（`check_tests.py` `mutant()`）。隱藏 mutant 難度不一，有些只有仔細讀規格的人才會測到（`part2/README.md`）。

#### `AI_NOTE.md`（10 分）
每題在「Answer:」那行回答（2–5 句），刪掉「(write here)」；checker 要求**每題至少 5 個字**。「I did not use AI」如果屬實也算完整答案。依完整、誠實評分，不看有沒有用 AI。
1. 這部分用了哪個 AI assistant（如果有）？
2. 你請它做什麼？摘要你的 prompt。
3. 看完它給的東西後，你改了、加了或丟掉什麼？
4. 選一個練習 mutant（p1–p4），用自己的話說明你的哪個 test 抓到它、為什麼那個 test 重要。

### 全部配分（repo README「Points」）
| 項目 | 分數 | 評分方式 |
|---|---:|---|
| Part 1 tests | 35 | push 時 GitHub |
| Part 1 `ANALYSIS.md` | 15 | 人工 |
| Part 2 gate、practice mutants、AI note | 40 | push 時 GitHub |
| Part 2 hidden mutants | 60 | 截止後 |
| **合計** | **150** | Actions 分頁顯示其中 75 分 |

autograder：GitHub Actions，Python 3.11，任何分支 push 都會跑（workflow `branches: '**'`）。

## 注意事項
- **Part 1 不能用 AI**；Part 2 可以，但只限 `part2/`。如果讓 AI assistant 或 agent 看這個 repo，要叫它**別碰 `part1/`，並自己檢查它有沒有照做**（repo README「AI, and the exams」；`part1/README.md`）。
- Part 1 不要抄 `part2/bst_reference.py`（`part1/README.md`）。
- 不要改 `bst_test.py`、`tree_tools.py`、`avl.py`、`compare.py`、`bst_reference.py`、`check_tests.py`、練習 mutant 和 `.github` workflow；老師跑原檔（repo README「Submit」；`part1/README.md`「Submit」）。
- `ANALYSIS.md` 第 1 節要在跑 `compare.py` **之前**寫，之後不要改（`ANALYSIS.md` §1）。
- **Part 2 test 只能 import**：`unittest`、`random`、`time`、`copy`、`itertools`、`math`、`string`、`collections`，`bst_reference` 的五個函式，`tree_tools` 的四個 helper（`part2/README.md`「What your tests may and may not do」）。
- **Part 2 test 不能用**：讀檔、`inspect`、`os`、`sys`、`import bst_reference`（只能 `from … import`）、雙底線名稱（如 `__code__`）、`eval`／`exec`、`sleep`（同上）。checker 的 lint 另外禁止 `open`、`compile`、`globals`、`locals`、`vars`、`dir`、`getattr` 等（[repo/part2/check_tests.py](repo/part2/check_tests.py) `BANNED_NAMES`）。要測函式**做了什麼**，不是怎麼寫的。
- Test 要**可重現**：用 `random.Random(seed)`，不要用沒設種子的 `random`（同上）。
- 整個 suite 在 reference 上要在**約 10 秒內**跑完（同上）；gate 的硬上限是 60 秒（`check_tests.py`）。
- 一個 test 在 reference 上 fail 就是錯的 test，gate 不過的話 practice 和 hidden mutant 都不計分（`part2/README.md`「How you are graded」）。
- 不管 test 是誰寫的，你都要知道它檢查哪一條規則（`part2/README.md`「AI note」）。
- 期中、期末是紙筆、不能用 AI，會考 Part 1 和 Part 2 練的東西（repo README）。
- 遲交：syllabus 每學季可免一次（事先告知、最多晚 1 週），其他每天 -25%；投影片寫超過 4 天不收（`dsa/assignments.md`）。**A4 已經用掉免罰延期**（Piazza @65，見 [../a4/README.md](../a4/README.md)「延期與 Canvas comment」），A5 遲交會直接扣分。

## 和上課內容的關聯
- **BST 規則、search／insert（iterative）、min／max／successor、delete 三種情況、O(h)**：Class 8（10/26），[`dsa/lectures/2026-10-26/notes.md`](../../lectures/2026-10-26/notes.md) 重點摘要第 38–101 行。delete 上課只畫圖沒寫 code，留給 A5 Part 1（[01:11:00]；講義 p6 的提示和 delete 8／delete 3 的 preorder 練習）。重複值上課也是忽略（講義 p4）。
- **Recursion 上限、sorted 輸入退化成 linked list**：同檔講義 p4、p8（recursive insert 在約 1,000 個 sorted 值時 RecursionError；排序資料很常見：timestamp、id、字母順序），對應 `ANALYSIS.md` §3、§5、§6。
- **平均步數、best／worst／average case**：同檔講義 p7–p8（random tree 平均步數約 1.2–1.3 × log₂ n），對應 `ANALYSIS.md` §1–§3。
- **AVL：balance factor、rotation、四種 case、height O(log n)**：Class 9（10/28），[`dsa/lectures/2026-10-28/notes.md`](../../lectures/2026-10-28/notes.md)（Visualgo 示範 BST vs AVL、講義 p3 rotation code、p5–p6 高度上限），以及 Class 10（11/2），[`dsa/lectures/2026-11-02/notes.md`](../../lectures/2026-11-02/notes.md)（height 慣例單一 node 0／空樹 −1，和 `tree_tools.tree_height` 一樣；老師說「有一份作業會大量練習 rotation」[01:38:05]），對應 `ANALYSIS.md` §4。
- **寫 test、邊界情況、用 test 證明 bug**：A4 Bug Hunt 的做法（[../a4/README.md](../a4/README.md)），Part 2 是同一套思路，改成抓 mutant。
- **期中範圍**：到 11/2 為止的 AVL 全部都考（`dsa/lectures/2026-11-02/notes.md` [01:51:04]），所以 Part 1 適合當期中準備。

## 還不確定的地方
1. **分數**：repo README 寫 150 分，Canvas 是 100 分；可能等比例換算，沒有公告（A4 也有同樣的 60 vs 100 問題）。
2. **要不要到 Canvas 交 repo URL**：A5 的 README「Submit」只說 push 到 `master`，沒提 Canvas；週規劃依 A4 的做法寫要交 URL。保險起見 push 後也到 Canvas 交。
3. **老師說 rotation 會大量練習**（11/2 [01:38:05]），但 starter 裡 Part 1 只要寫 BST，AVL（含 rotation）是提供的；rotation 的練習可能只在 `ANALYSIS.md` §4 的推理，或老師說的是別份作業。
4. **AVL 高度上限「about 1.44 log₂(n)」**：`ANALYSIS.md` §4 說是「the bound from class」，上課沒推導，在 Class 9 講義 p5–p6（`dsa/lectures/2026-10-28/notes.md` 第 9 點）。
5. **Part 2 的「Speed」規則怎麼測**：只說時間和樹高成正比，沒說測法；`time` 可以 import，但 suite 要在約 10 秒內跑完。
6. **repo 邀請**：11/3 Piazza「A5 Invites」有同學說邀請還沒發（`digests/2026-11-03.md`）；11/4 已看到你的 repo 建立，應該沒問題。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-11-04 | 第一次整理 |

DSA 課用了 AI 要附 chat session 或註明。
