# DSA A2：Lists, lists and more lists

> 原文：[spec.md](spec.md)（[Canvas assignment 11814777](https://canvas.uw.edu/courses/1917417/assignments/11814777)；starter repo README：`uw-python-fall2026/assignment-2-mileschintw`，blob 602c986，標題「Programming Assignment 2: Arrays vs. Linked Lists」）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | 2026-10-18（日）11:59 PM PDT（Canvas `due_at`，和 `assignments.md` 一致）；狀態 **submitted**（10/19 晨報確認） |
| 分數 | Canvas 150 分；README Grading Criteria 合計只有 100 分（見「還不確定的地方」） |
| 繳交方式 | commit 並 push 到 `uw-python-fall2026/assignment-2-mileschintw`（預設分支 `master`），**再到 Canvas 交 repo URL** |
| 要交的東西 | 1. `array_list.py`（6 個 TODO 函式）<br>2. `linked_list.py`（6 個 TODO 函式）<br>3. `student_tests.py`（2 個自己寫的 test）<br>4. `analysis.md`（A1–A4、P1–P3、T1、`timing.py` 全部輸出、Q1–Q7）<br>5. `my_timing.py`（2 個 TODO）<br>6. 至少 3 個 commit |

## 學習目標
（Canvas「Objectives」＋ README「Objectives」）
- 熟悉 Python 的 `unittest` 和計時工具
- 用統一的介面實作資料結構，並分析、比較不同實作
- 實作會自動變大的 array，並計算它做了多少工作
- 實作 linked list，維持 link 和 size 正確
- 跑 unit test、讀輸出、用它找 bug；自己寫 test
- 量執行時間，把數字和 Big-O 連起來
- 解釋 Python 內建結構為什麼表現成那樣

## 要做什麼
同一件事（一個存值的 list）用兩種方式做，再和內建的 `list`、`array.array`、`deque` 比速度（README「Overview」）：
- **array list**：值放在固定大小的 slot 區塊裡，滿了要自己做「變大」
- **singly linked list**：每個值一個 node，node 指向下一個

### 檔案一覽（README「The Files」）

| 檔案 | 用途 | 要改嗎 |
|---|---|---|
| `array_list.py` | Part B | **要**，寫 6 個函式 |
| `linked_list.py` | Part C | **要**，寫 6 個函式 |
| `array_list_test.py`、`linked_list_test.py` | Part B、C 的測試 | 不要 |
| `shared_list_tests.py` | 兩種結構共用的測試 | 不要 |
| `list_checks.py` | 檢查 list 內部是否正確的 helper | 不要 |
| `student_tests.py` | Part E，自己寫 2 個 test | **要** |
| `analysis.md` | Part A、D 的書面回答 | **要** |
| `my_timing.py` | Part D，自己計時（2 個 TODO） | **要** |
| `timing.py` | Part D 的計時實驗，只要跑 | 不要 |
| `analysis_test.py` | 檢查 `analysis.md` 和 `my_timing.py` 有沒有填 | 不要 |
| `part_e_checks.py` | 檢查 Part E 的 test 是真的、會過 | 不要 |

### Part A：紙上作業（`analysis.md`）
寫 code 之前先回答 A1–A4，畫出 array 和 linked list。

### Part B：array list（`array_list.py`）
- 寫 6 個標 `TODO` 的函式。先讀檔案開頭的註解：它說明資料表示法和**規則**。
- 維護 `'moves'` 計數：複製或位移了多少個值。用來「不用碼表就量出工作量」；計數正確的話，在大 list 開頭插入會有很多 moves，append 幾乎沒有。
- 建議順序：TODO 1–3（length、get、grow），再 TODO 4–6（insert、remove、to_python_list），後者最難（README「A suggested week」）。

### Part C：linked list（`linked_list.py`）
- 寫 6 個 `TODO` 函式，名稱和意義與 array list 相同，所以**同一套 test** 檢查兩者。
- `linked_list_reverse` 最難，先畫圖。

### Part D：計時（`my_timing.py`、`timing.py`、`analysis.md`）
1. **跑任何計時程式之前**先回答 P1–P3（預測）。
2. 完成 `my_timing.py` 的 2 個 TODO，回答 T1：同一個操作分別用碼表（`time.perf_counter`）和 `timeit` 計時。
3. 執行 `python3 timing.py`（Windows 用 `python`），把**全部**輸出貼進 `analysis.md`，用自己的數字回答 Q1–Q7。

### Part E：自己的 test（`student_tests.py`）
array list 和 linked list 各寫 1 個 test，要檢查既有 test 沒檢查到的東西，而且要通過。

### 評分標準（README「Grading Criteria」）

| 分數 | 項目 |
|---|---|
| 30 | Array list：`array_list_test.py` 通過（autograder 依群組給部分分數，例如 insert、remove） |
| 30 | Linked list：`linked_list_test.py` 通過（依群組給部分分數，例如 insert、reverse） |
| 10 | Part E：兩個自己寫、會過、有意義的 test，各 5 分；autograder 確認存在、通過、真的有測到 code，人工確認有意義 |
| 25 | `analysis.md` 和 `my_timing.py`：10 分自動（每題都答、結果有貼、兩個 `my_timing.py` 函式能跑），15 分人工看答案；要具體、用自己的數字，不用長 |
| 5 | GitHub 和 Canvas 都準時交，而且至少 3 個 commit |

## 注意事項
- array 上**不能用 `append`、`insert`、`pop` 或 slicing**，要自己一個一個搬值；test 會檢查這些規則（README「Part B」、「Rules」）。
- 只能用 Python standard library（README「Rules」）。
- **不可以把這份作業的任何 code 貼給 ChatGPT 或其他 AI assistant 求助**；分析要是自己的計時數字、自己的話（README「Rules」）。
- A2、A3 期間要關掉編輯器的 code suggestion（`dsa/lectures/2026-10-07/notes.md`，[00:37:05]）。
- P1–P3 一定要在跑計時之前回答（README「Part D」）。
- `timing.py` 輸出要**全部**貼上；不要拿自己的數字和同學比，要看自己的數字隨 list 變大怎麼變；跑之前關掉其他程式、跑兩次看波動（README「A Quick Guide To Timing」）。
- `list_checks.py` 的 `assert_array_list_valid`、`assert_linked_list_valid` 可以在自己的 test 裡呼叫（README「What are the "invariant" checks?」）。
- 沒有 push 到 GitHub 而且在截止前把連結交到 Canvas，就不算繳交（Canvas「Submission」）。
- 作業有更新或澄清會寫在 README 和課程論壇；更新時要自己解衝突（README「Rules」、「Updates to the assignment」）。
- 遲交：syllabus 是每學季可免一次（事先告知、最多晚 1 週），其他每天 -25%；投影片是每天 -25%、超過 4 天不收（`assignments.md`）。

## 和上課內容的關聯
- **Array 與 linked list 的結構和 Big-O**：Class 1 投影片 p24–p42（`dsa/lectures/2026-09-30/notes.md`「和作業 / 考試的關聯」）；Class 2（10/5）的 Big-O 總表和常見錯誤清單（`dsa/lectures/2026-10-05/notes.md`「和作業 / 考試的關聯」A2 段：更新 size、改 pointer 前先存 next、off-by-one、存取前比對 size、array 插入從尾端 shift、滿了先 resize、tail 的更新）。
- **unittest、test 先行、size／capacity 管理**：Class 3（10/7）在 `in-class-code` 的 `Mod1/stack.py`、`test_stack.py`（`dsa/lectures/2026-10-07/notes.md`，[00:34:04]、[01:44:04]）。老師說這堂就是 A2 的基礎：實作 array 和 linked list 並做分析（[00:10:01]）。
- **resize 的寫法**：Class 4（10/12）array stack 的 `[None] * (2*len)` 加逐一複製，不用 slicing（`dsa/lectures/2026-10-12/notes.md`「和作業 / 考試的關聯」）。
- **`array.array`、`deque`**：Class 5（10/14）講義 p9 提到 `array.array` 比 list 省記憶體、list 與 deque 的 queue 寫法（`dsa/lectures/2026-10-14/notes.md`「和作業 / 考試的關聯」）。

## 還不確定的地方
- **配分對不上**：README Grading Criteria 合計 30+30+10+25+5 = 100 分，Canvas 是 150 分。A3 也有同樣問題（Piazza @51，見 `digests/2026-10-20.md`），老師還沒回覆。
- **Class 2 notes 的待釐清問題可以結案**：A2 兩者都要實作（array list 和 linked list），「analysis」是 `analysis.md` 的 A1–A4、P1–P3、T1、Q1–Q7；unit testing 在 A2 就開始用（Part E 要自己寫 test），不是只有 A3。
- `analysis.md` 裡各題的實際題目不在 spec.md（只在 repo 的 `analysis.md`），這份摘要沒有列出題目內容。
- 已經交了；這份摘要主要給之後查閱和期中複習。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-10-20 | 第一次整理 |

DSA 課用了 AI 要附 chat session 或註明
