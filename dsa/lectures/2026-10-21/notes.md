# DSA Class 7 — 2026-10-21（週三，Mod 3 Trees/Traversals：DFS 三種順序、各自用途與 expression tree、BFS 用 deque、把 queue 換成 stack 變成 iterative DFS、runtime 開頭）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，997 cues，00:25:40–02:08:40，DeliveryID `887324e8-5bc6-4517-895d-b4eb00222511`，Canvas Module 3 item 27590134「Mod 3 Trees/Traversals [Wed, Class 7]」）、slides：**講義尚未發布**（10/22 早上 Canvas Module 3 只有 Class 6 outline 和兩支錄影，沒有 Class 7 的檔案）。老師在 [00:33:03] 說週一的筆記已經放上 Canvas，涵蓋今天的一部分內容；那份是 `EE590a_Class_trees_and_traversals_students.pdf`（file 154647952，文字在 `../2026-10-19/slides.txt`）。下面引用它的地方都標成（Class 6 講義 pN），不是本堂的講義。閱讀：Grokking Algorithms（課程沒有指定本堂章節，下面的對照是自行整理的：Ch 3 Recursion 的 call stack、Ch 6 Breadth-first search 的 queue）。逐字稿是自動產生，專有名詞可能聽錯。
>
> **錄影前 25 分鐘沒有字幕**（第一句在 00:25:40），應該是開課前的空檔；開場公告從 [00:26:10] 開始。
>
> 常見誤聽對照：deck / duck / tech → deque；`collections.dev` → `collections.deque`；cue / Q → queue；Breath First / tradition → breadth-first / traversal；「Death The order BFS」→ preorder DFS；VFS / AFS / EFS → DFS / BFS；route → root；Note / note → node；write → right；auto → out；Vlog and / login → log n；OVAV → O(n)；Emax → Emacs；Prom stack → from stack；Admitted → emitted；RTA → our TA；horse people → （應該是「people」，人員異動）；Breeze → trees。

## 重點摘要

1. **開場公告**（[00:26:10]–[00:33:03]）
   - **A3 週日（10/25）截止**。今天就去確認自己有 A3 repo 的存取權。邀請有時重寄也不會生效，沒有權限就在 Piazza 私訊老師，附上 GitHub ID（[00:26:10]–[00:27:14]）。下課前又說：今晚 9 PM 左右還沒收到 invite，就到 Piazza 私訊（[02:07:06]）。
   - **A4 明天（10/22）發布，是第一個允許用 AI 的作業**（[00:27:14]–[00:31:05]）。要交的東西包括你用的 prompts，以及說明你怎麼在這份作業裡使用 AI。目標是「有意識地用 AI，讓自己成為更好的工程師」：能判斷 AI 產生的 code 好不好、找出可能的 bug、知道 AI 哪裡有用哪裡沒用。老師說這些是新作業，她也不確定難度和效果，歡迎回饋。
   - **TA 不能繼續擔任 TA**，之後會有新的 grader。這幾週沒人幫忙，所以批改落後；老師把**週六（10/24）**整天空下來改作業，希望下週之後恢復準時（[00:32:02]–[00:33:03]）。
   - 鼓勵在 Piazza 公開發問（可以匿名），讓全班一起討論（[00:31:05]）。

2. **複習週一 + 為什麼要練 recursive 思考**（[00:34:02]–[00:38:05]）
   - 週一講了 tree 名詞（root、node、leaf、path、parent/children、sibling、level、height、depth）、用 dict 表示 node、recursion。
   - 老師再強調一次：**能用 recursive 的方式思考問題很有價值**，即使你從來不把 recursive code 放進 production。recursive code 沒效率，但有了 recursive 的解法，就能再改寫成 iterative。tree 是用自己定義自己的 recursive data structure，所以很適合練習（[00:36:05]–[00:37:01]）。

3. **Big O 投票：週一（10/26）會深入講**（[00:38:05]–[00:40:05]）
   - 老師承認到目前為止對 Big O 的定義「講得很鬆」。舉手投票後決定**下週一花時間深入講 Big O 是什麼、不是什麼**。她說 O(1)、O(n) 比較直觀，到了 O(log n) 如果 Big O 基礎不穩就會開始混亂。

4. **depth-first traversal 的三種順序**（[00:40:05]–[00:58:05]）
   - traversal 就是 tree 版的 iteration：linked list 是一個接一個 iterate，tree 是每個 node 都 visit 一次，但可以選擇在什麼時間點處理這個 node（[00:43:16]–[00:44:04]）。
   - depth-first：一路往下，往下走完才回頭走另一邊；breadth-first：一層一層走（[00:41:06]–[00:42:11]）。
   - 範例樹（沿用週一）：
     ```
             8
           /   \
          3     10
         / \      \
        1   6      14
           / \    /
          4   7  13
     ```
   | 順序 | 規則 | 範例樹輸出 |
   |---|---|---|
   | preorder | node → left → right | 8 3 1 6 4 7 10 14 13 |
   | inorder | left → node → right | 1 3 4 6 7 8 10 13 14 |
   | postorder | left → right → node | 1 4 7 6 3 13 14 10 8 |
   - 老師在白板上逐步走完三種順序，並讓同學在 chat 回答下一個是誰（[00:45:02]–[00:58:05]）。postorder 的提示：**root 8 一定是最後一個**（[00:54:05]）。
   - 同學問 postorder 怎麼從 1 跳到 4：3 的 left 是 1，接著進 3 的 right（以 6 為根的子樹），再往 6 的 left 走到 4（[00:58:05]–[00:59:10]）。

5. **recursive DFS 的 code**（[01:00:01]–[01:15:01]）
   - 沿用週一的 `create_tree_node`，加一個 `out` list 記錄 visit 順序：
     ```python
     def preorder_dfs(node, out):
         if node is None:          # base case：空 child，什麼都不做
             return
         out.append(node['payload'])   # visit node
         preorder_dfs(node['left'], out)
         preorder_dfs(node['right'], out)

     def inorder_dfs(node, out):
         if node is None:
             return
         inorder_dfs(node['left'], out)
         out.append(node['payload'])
         inorder_dfs(node['right'], out)

     def postorder_dfs(node, out):
         if node is None:
             return
         postorder_dfs(node['left'], out)
         postorder_dfs(node['right'], out)
         out.append(node['payload'])
     ```
     （函式名稱和 `out` 參數依逐字稿整理；老師的實際 code 還沒 push，見「還要釐清的問題」。）
   - 課堂上的小錯：第一次跑沒印出結果（忘了存 `order = ...` 再 print，[01:05:02]–[01:06:02]）；postorder 第一次跑錯是因為遞迴呼叫沒傳 node（[01:13:02]）。
   - **結構重點**（[01:14:00]–[01:15:01]）：三個版本都一樣是「base case + visit node 一行 + 兩個遞迴呼叫」，**唯一的差別是 visit 那一行相對於兩個遞迴呼叫的位置**。這個結構之後會一直出現。

6. **三種順序的用途**（[01:17:00]–[01:35:06]；同學 Ethan 在 [01:00:01] 發問）
   - 老師先回顧週一列的真實世界的 tree：file system、DOM、autocomplete / predictive text（她說這學期應該會看到一個例子），今天再加 **expression tree**（[01:18:02]–[01:19:01]）。
   - **preorder**：先處理自己再處理 children。例如列出某個資料夾底下所有檔案、或導航到某個 path：先印目前這個資料夾，再印 children，再印 children 的 children。file system 不是 binary tree，一個 node 可以有很多 children（[01:19:01]–[01:21:00]）。
   - **inorder**：輸出是**由小到大排好的**，這是其他順序沒有的特性。老師說「先記著，等一下再回來」，但這堂沒時間回來；下週的 BST 會用到（[01:22:01]）。
   - **postorder**：先處理 children 再處理 parent。例如刪除資料夾（先刪所有 children 再刪 parent）、計算資料夾在磁碟上的大小（先拿到每個 child 的大小再加總）（[01:22:01]–[01:23:06]）。
   - **expression tree** `(8 - 3) * (2 + 4)`：內部 node 是運算子，leaf 是數字（[01:24:04]–[01:25:00]）。
     - preorder → `* - 8 3 + 2 4`，也就是 **prefix notation**。老師說看到這個她只想到 Lisp（同學補 Emacs）（[01:25:00]–[01:27:07]）。
     - inorder → `8 - 3 * 2 + 4`，長得像我們平常寫的算式，但**括號不見了**，分組跟著消失，算出來的答案會不一樣（[01:27:07]–[01:28:00]）。
     - postorder → `8 3 - 2 4 + *`，也就是 **postfix notation**（[01:29:04]–[01:30:01]）。
   - **用 stack 算 postfix（同學投票要聽的「fun trick」）**（[01:30:01]–[01:34:13]）：
     - 規則：遇到數字就 push；遇到運算子就 pop 兩個數字、套用運算子、把結果 push 回去。
     - 走一遍：push 8、push 3、遇到 `-` → pop 出 8 和 3，push 5；push 2、push 4、遇到 `+` → push 6；遇到 `*` → pop 5 和 6，push 30。stack 裡剩下的最後一個值就是答案。
     - 重點：**用一個資料結構（stack）加幾條規則，就能有效率地算出 tree 表示的算式**。

7. **breadth-first traversal（BFS / level order）**（[01:35:06]–[01:52:02]）
   - 一層一層走，同一層的 siblings 都 visit 完才往下一層。範例樹：8, 3 10, 1 6 14, 4 7 13（[01:36:09]–[01:37:01]）。
   - BFS **沒有** pre/in/post 這種選擇，因為就是一層一層走；唯一可能要決定的是 children 先看 left 還是 right，看情境而定（[01:37:01]–[01:38:08]）。
   - BFS 不太適合用 recursive 寫，所以要用自己的資料結構記住「還沒 visit 的 node」（[01:40:03]–[01:41:03]）：
     ```python
     from collections import deque

     def bfs(root):
         out = []
         nodes_to_visit = deque()
         if root is not None:
             nodes_to_visit.append(root)
         while nodes_to_visit:              # 還有東西就繼續
             node = nodes_to_visit.popleft()  # 從前面拿（FIFO）
             out.append(node['payload'])
             if node['left'] is not None:
                 nodes_to_visit.append(node['left'])
             if node['right'] is not None:
                 nodes_to_visit.append(node['right'])
         return out
     ```
   - 為什麼用 `deque` 不用 `list`：要從一邊加、另一邊拿的時候，double-ended queue 比 list 有效率（list 只有一邊便宜）（[01:42:08]–[01:43:04]）。老師說自己寫 import 寫到忘記了，「這就是 AI 用太多的下場」（[01:42:08]）。
   - 跑出來 `8 3 10 1 6 14 4 7 13`，和預測一致（[01:50:04]–[01:51:11]）。
   - 和 expression tree 同一個概念：**用資料結構（queue / stack）幫我們記住接下來要 visit 的順序**，只是放進去和拿出來的規則不同（[01:51:11]–[01:52:02]）。

8. **mystery traversal：把 queue 換成 stack = iterative DFS**（[01:52:02]–[02:00:00]）
   - 老師把 BFS 複製一份，只改兩個地方：`deque()` 換成 `[]`、`popleft()` 換成 `pop()`。先讓大家猜會發生什麼（有同學猜「每層反過來」：8, 10, 3, 14, 6, 1…）（[01:53:00]–[01:54:01]）。
   - 答案：**在 Python 裡，這個改動就是 queue 和 stack 的差別**。queue 是 FIFO，stack 是 LIFO（[01:55:05]）。
   - 老師另外把 push 順序改成**先 push right 再 push left**，跑出 `8 3 1 6 4 7 10 14 13`，**就是 preorder**，不是 BFS（[01:56:04]–[01:57:00]）。中間一個 bug（`unsubscriptable`）是同學抓到的：在 right 的分支 append 錯了 node（[01:57:00]）。
   - 這就是週一承諾的「recursive 改寫成 iterative」：**沒有遞迴呼叫，自己用 stack 記住順序**（[01:58:03]–[01:59:08]）。
   - 同學問如果不交換 left／right 的 push 順序會怎樣：跑出 `8 10 14 13 3 6 7 4 1`，等於先走右邊的 preorder。所以要**反著 push**，pop 出來才會先 left 後 right；老師說這是用 stack 取代遞迴時「最笨拙的地方」（[01:59:08]–[02:00:00]）。

9. **runtime 開頭（沒講完）**（[02:02:08]–[02:06:03]）
   - size、height、count leaves：都是 **O(n)**。size 要數每個 node；height 不走完每條 path 就不知道哪條最長；count leaves 不 visit 每個 node 就不知道有沒有漏掉 leaf（[02:04:03]–[02:05:06]）。
   - recursive DFS（preorder 等）：也是 **O(n)**，每個 node visit 一次（[02:05:06]–[02:06:03]）。
   - 時間到了，完整的表在 Canvas 的筆記裡（Class 6 講義 p8）。下週會回來看整張表，並補上**還沒寫的 space 那一欄**（[02:06:03]）。
   - 本來預計今天講 binary search tree，沒講到；**BST 和 runtime 改到下週一、三**（[02:07:06]–[02:08:13]）。

## 名詞解釋

| 名詞 | 意思 | 範例 |
|---|---|---|
| traversal | tree 版的 iteration：每個 node 都 visit 一次，但可以選處理的時間點 | — |
| depth-first（DFS） | 一路往下走到底，再回頭走另一邊 | preorder／inorder／postorder |
| preorder | node → left → right | 8 3 1 6 4 7 10 14 13 |
| inorder | left → node → right；binary search tree 上輸出會是排序好的 | 1 3 4 6 7 8 10 13 14 |
| postorder | left → right → node；root 一定最後 | 1 4 7 6 3 13 14 10 8 |
| breadth-first（BFS）／level order | 一層一層走，同層都 visit 完才往下 | 8 3 10 1 6 14 4 7 13 |
| base case | 遞迴停下來的情況；這裡是 `node is None`，直接 `return` | — |
| expression tree | 內部 node 是運算子、leaf 是數字的 tree | `(8 - 3) * (2 + 4)` |
| prefix notation | 運算子放前面；expression tree 的 preorder | `* - 8 3 + 2 4` |
| infix | 運算子放中間；expression tree 的 inorder，但括號會不見 | `8 - 3 * 2 + 4` |
| postfix notation | 運算子放後面；expression tree 的 postorder；用 stack 就能算，不需要括號 | `8 3 - 2 4 + *` → 30 |
| `collections.deque` | double-ended queue，兩端加入／拿出都便宜；BFS 用 `append` + `popleft` | — |
| FIFO／LIFO | queue 先進先出／stack 後進先出 | — |
| iterative DFS | 用 list 當 stack（`append` + `pop`），先 push right 再 push left，得到 preorder | — |

## 老師強調的地方（附逐字稿時間戳）

- [00:27:14] **今天就確認 A3 repo 的存取權**，不要等到最後一刻才發現沒權限、又找不到老師。
- [00:28:08]–[00:30:02] **A4 是第一個允許用 AI 的作業**，要附 prompts 和使用方式的說明。重點是有意識地用 AI：能評估 AI 寫的 code、找出 bug、知道哪裡有用。她說自己不一定分得出作業是不是 AI 做的，也不想去爭論這件事。
- [00:31:05] 有問題盡量在 Piazza 對全班發問，可以匿名。
- [00:32:02] TA 異動，批改落後，週六補改。
- [00:36:05] 能用 recursive 的方式思考問題「super powerful」，有了 recursive 解法就能改寫成 iterative。
- [00:39:00] 下週一深入講 Big O（大家舉手投票決定）。
- [00:42:11] DFS 永遠先往下，往下走完才回頭走另一邊；BFS 是同一層都走完才往下。
- [00:54:05] postorder 的提示：root（8）一定是最後一個 visit 的。
- [01:03:01]–[01:04:01] base case 是 node 為 `None`；因為建樹時沒有 child 就放 `None`，這個 base case 剛好用來表示「這裡沒有 child」。
- [01:14:00]–[01:15:01] **三種 DFS 的 code 結構一樣，只差 visit 那一行放在兩個遞迴呼叫的前、中、後**。這個結構之後會一直用到，要熟。
- [01:22:01] inorder 的輸出是排序好的，這是其他順序沒有的特性（之後 BST 會用到）。
- [01:22:01]–[01:23:06] postorder 的典型用途：先刪 children 再刪 parent、先算 children 大小再加總。
- [01:28:00] 把 expression tree 用 inorder 攤平，會失去括號和分組，答案就變了。
- [01:32:03]–[01:34:13] 用 stack 算 postfix：數字 push；運算子 pop 兩個、計算、push 結果；最後 stack 剩下的就是答案。
- [01:40:03] DFS 很適合寫成 recursive，BFS 不太適合，所以 BFS 改用 queue。
- [01:42:08]–[01:43:04] queue 要用 `deque`（兩端都有效率），不要用 list。
- [01:51:11] **用資料結構幫我們記住 visit 的順序**：expression tree 用 stack，BFS 用 queue。
- [01:55:05] 在 Python 裡，`deque` + `popleft` 換成 `list` + `pop`，就是 queue 換成 stack。
- [01:58:03] 換成 stack 之後就是**不用 recursion 的 DFS**（iterative）。
- [02:00:00] 用 stack 時 children 要反著 push，才能維持 left 先於 right；這是 iterative 版最笨拙的地方。
- [02:04:03]–[02:05:06] size、height、count leaves、recursive DFS 都是 O(n)：不 visit 每個 node 就沒辦法確定答案。
- [02:06:03] 完整 runtime 表在 Canvas 的筆記裡；下週會補上 **space** 那一欄。

## 和作業 / 考試的關聯

- **A3 Stacks, Queues and Testing**：10/25（日）11:59 PM PDT，150 分。老師在課堂上再次說是週日（[00:26:10]），和 Canvas 一致。**今天先確認 repo 存取權**，沒有就在 Piazza 私訊 GitHub ID（[00:27:14]、[02:07:06]）。本堂「同一個 loop 換 queue／stack」以及「用 stack 算 postfix」都是 A3 stack/queue 的好複習。
- **A4 Bug Hunt**：11/1（日）11:59 PM PST（DST 結束當天）。**10/22 發布，第一個允許用 AI 的作業**，要交 prompts 和 AI 使用說明（[00:28:08]）。之前的 AI 政策是「不能把 starter code 交給 AI、用了要附 chat session」；A4 的具體規定以作業說明為準。
- **A5 BSTs and AVLs**：11/22（日）11:59 PM PST。本堂的 traversal（尤其 inorder 排序好的性質）是 A5 的前置；BST 下週一、三講。
- **Midterm**：11/9（一）4:30–6:30 PM PST，實體紙筆，Moore 220。可能會考：
  - 給一棵樹，手寫 preorder／inorder／postorder／BFS 的輸出。
  - 手寫 recursive DFS（三種順序只差 visit 一行的位置）、用 `deque` 的 BFS、用 stack 的 iterative DFS（記得反著 push）。
  - expression tree 轉 prefix／postfix，用 stack 算 postfix。
  - size／height／count leaves／traversal 的 time 都是 O(n)；space 下週講。
  - Class 6 講義 p9 的 check questions 很像考題。
- 成績：老師週六（10/24）補改落後的作業（[00:32:02]）。
- 課程 AI 政策提醒：本筆記只整理上課內容，不涉及作業 starter code。

## 還要釐清的問題

1. **Class 7 講義還沒上 Canvas**。老師說週一的筆記已經涵蓋今天一部分（[00:33:03]），Class 6 講義 p6–p8 確實有三種順序、expression tree、level order、stack 版 preorder 和 runtime 表。之後如果出現 Class 7 的檔案，要重抓並補上 `slides.txt`。
2. **A4 的 AI 規定細節**：要附哪些 prompts、說明要寫多長、怎麼評分，課堂上沒講清楚。A4 說明明天發布，到時候對照（作業說明任務會抓）。
3. **新 grader 是誰、原 TA 為什麼不能繼續**：課堂上沒說名字。之後看 Canvas／Piazza 有沒有公告。
4. **課堂上寫的 code 還沒 push**：上面的函式名稱和參數是依逐字稿整理的（例如 `preorder_dfs(node, out)`、`nodes_to_visit`），以老師之後 push 到 repo 的版本為準。
5. **inorder 對應「排序好」**：老師說輸出 increasing，但這只在 BST 上成立（範例樹剛好是 BST）。一般的 binary tree 用 inorder 不一定排序好。老師說「等一下回來」但這堂沒回來，下週 BST 時確認。
6. **runtime 表的 space 欄**：下週才講。Class 6 講義 p8 的版本是 recursive DFS 和 iterative DFS 都是 O(h) extra space、BFS 是 O(w)，可以先看。老師開場說今天會講「為什麼 recursive code 沒效率、不適合 production」（[00:36:05]），但時間不夠沒講到，應該也是下週 space 那部分。
7. 本堂原本預計講 BST，延到下週；下週一還要深入講 Big O，進度可能再往後推。Midterm（11/9）範圍到哪裡，要留意老師之後的說明。
