# DSA A1：My First Python Assignment

> 原文：[spec.md](spec.md)（[Canvas assignment 11793714](https://canvas.uw.edu/courses/1917417/assignments/11793714)；starter repo README：`uw-python-fall2026/assignment-1-mileschintw`，blob 945a91f）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | 2026-10-04（日）11:59 PM PDT（Canvas `due_at`，和 `assignments.md` 一致） |
| 分數 | 50 分（README Grading Criteria 合計 25+10+10+2+3 = 50，和 Canvas 一致）；狀態 **graded** |
| 繳交方式 | commit 並 push 到 `uw-python-fall2026/assignment-1-mileschintw`，**再到 Canvas 交 repo URL** |
| 要交的東西 | 1. repo 裡的 `HelloWorld.ipynb`（MadLib 程式）<br>2. 至少 2 個 commit<br>3. Canvas 上的 repo 連結 |

## 學習目標
（Canvas 說明「Objectives」）
- 把 Python 環境架起來
- 熟悉 GitHub
- 熟悉作業繳交流程

## 要做什麼
### 前置（README「Getting Started!」）
- 填課程 Intro Survey（[quiz 2448356](https://canvas.uw.edu/courses/1917417/quizzes/2448356)），GitHub ID 才會被加進課程，之後收到 Assignment 1 repo 的邀請。
- 安裝 PyCharm。

### 取得 repo（README「Details」）
1. 複製 repo 的 clone URL。
2. PyCharm：File → New Project from VCS → 貼上 URL，IDE 會開啟 repo。

### MadLib notebook（README「Details」、「MadLibs」）
- 打開 `HelloWorld.ipynb`，寫一個簡單的 MadLib 程式：向使用者要幾個詞，再把詞填進故事的空格印出來。
- 用 `input()` 取得使用者輸入。
- 範例互動：依序問 noun、color、city in Washington、noun，然後印出一段用到這些詞的故事。

### 評分標準（README「Grading Criteria」）

| 分數 | 條件 |
|---|---|
| 25 | 準時交，GitHub 和 Canvas 兩邊都有 |
| 10 | 程式向使用者要 **5 個詞** |
| 10 | notebook 整理得好：有 headings、text cells、code cells |
| 2 | GitHub repo 至少 2 個 commit |
| 3 | Flair：程式呈現漂亮、故事有趣、讓人會心一笑 |

## 注意事項
- **沒有 push 到 GitHub 而且在截止前把連結交到 Canvas，就不算繳交**（Canvas 說明「Submission」）。
- 成績登在 Canvas，回饋寫在 GitHub（Canvas 說明「Submission」）。
- 老師可能會更新作業內容，需要自己解決衝突；有大改會發公告（README「Updates to the assignment」）。
- 遲交：syllabus 是每學季可免一次（事先告知、最多晚 1 週），其他每天 -25%；投影片是每天 -25%、超過 4 天不收（`assignments.md`）。
- 沒收到 A1 GitHub 邀請：要先填 Intro Survey，老師是手動跑腳本邀請（`dsa/piazza/baseline-2026-10-18.md`）。

## 和上課內容的關聯
- Class 1 老師說 A1 其實是「assignment zero」：寫很少 code，主要是設定環境、熟悉繳交流程（`dsa/lectures/2026-09-30/notes.md`，[00:49:01]）。
- Class 1 [01:41:04] 說 A1 出了點狀況，會在一天內發出（同上）。
- 10/12 老師說 A1 成績已發，有疑問在 Piazza 私訊老師（`dsa/lectures/2026-10-12/notes.md`，[00:03:00]）。

## 還不確定的地方
- README 的 `input()` 範例寫成 `name = input()` 再 `print("Your name is " + adrienne)`，變數名稱對不上，照抄會出 `NameError`。看起來是範例的筆誤，不影響作業要求。
- 範例 MadLib 只問 4 個詞，但評分標準要求 5 個詞；以評分標準為準。
- 作業已經 graded，這份摘要只是存檔。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-10-20 | 第一次整理 |

DSA 課用了 AI 要附 chat session 或註明
