# DSA Class 6 — 2026-10-19（週一，Mod 3 Trees/Traversals：從 linear 到 tree、binary tree 的 recursive 定義、用 dict 建樹、tree_size / tree_height、depth-first traversal 預告）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，1091 cues，00:08:54–01:51:00，錄影 1:51:09，DeliveryID `6e8bef14-3722-4b1d-94b4-b4e9001f6e1d`）、slides（`EE590a_Class_trees_and_traversals_students.pdf`，Canvas file 154647952，Module 3 item 27579742「Class 6 outline, Introducing Trees and Traversals」，10 頁）、閱讀：Grokking Algorithms（課程沒有指定本堂章節，下面的對照是自行整理的：Ch 3 Recursion、Ch 6 Breadth-first search；2nd ed 的 Trees 章節，章號未核對）。逐字稿是自動產生，專有名詞可能聽錯。
>
> **這份講義也是課後整理的，不是上課時播放的內容。** PDF 頁尾列印時間是 10/19 7:54 PM（下課後）；老師在 [00:22:02] 說會把凌亂的筆記整理好再分享，[01:50:05] 說會拿掉「你們不需要的部分」、把 code push 到 repo、白板的樹圖也會放上去。
>
> **上課只講到講義的前半。** 講義的 leaves（`count_leaves`）、三種 depth-first 順序的正式定義、expression tree、level order（deque）、stack 版 preorder、runtime 表、recursion limit 都**沒有在課堂上講**，老師說留到週三（[01:42:02]、[01:44:00]、[01:49:01]）。下面這些內容標成（講義 pN），沒有逐字稿時間戳。
>
> 常見誤聽對照：deck / Duck → deque；O . → O(n)；archery → our tree；Poultry analysis → fault tree analysis；She hate, tree hate → tree_height；death / Death → depth（[01:22:00]「We have Death」= depth）；treat → tree；addiction → a dictionary；Brent → print；South → size；Dom → DOM；531 → 5:31（break 的時間）；import arith → import array；circular waffle → circular buffer。

## 重點摘要

1. **開場 Q&A：Python 裡要用什麼當 array**（[00:11:04]–[00:14:01]）
   - 一般情況就用 Python `list`（dynamic array of references，連續記憶體裡放 pointer）。`pop()` 尾端便宜，`pop(0)` 很貴，因為要把後面全部往前挪。
   - 老師說她**從來不會**在 Python 用 `import array`，那只是示範「Python 也有 array」。要 circular buffer 就用 `list` 或 `deque`；要做大量數值運算的高效能 array 就用 NumPy。

2. **implementation detail 要懂到什麼程度**（[00:16:00]–[00:20:06]）
   - 小專案只要會用 interface；要做專業、高效的程式或準備面試，就要知道底層實作（例如何時用 `list`、何時用 `deque`）。
   - **考試**：要懂 Python list 怎麼運作（dynamic array of references、pop 頭貴、pop 尾和 append 便宜）；`deque` 的內部算加分項（[00:19:04]）。
   - ADT（abstract data type）vs implementation：stack 是 LIFO、queue 是 FIFO，這是行為上的約定；底下可以用 array、linked list 或 deque 實作（[00:19:04]–[00:20:06]）。

3. **從 linear 到 tree：為什麼要分岔**（[00:21:01]–[00:25:02]；講義 p1–p2）
   - array、linked list、stack、queue 都是 linear data structure（資料排成一列）。linked list 在頭端插入／刪除便宜，但搜尋要 O(n)。
   - 引子：一百萬筆資料，如果每一步能丟掉一半，要幾步？約 20 步（log₂ n；2²⁰ = 1,048,576）。一百萬 vs 20 的差距，就是後面 binary search tree 要追的目標。
   - 生活中的 tree：檔案系統、fault tree analysis（同學分享航太的 vehicle → subsystem → box → component 安全分析）、autocomplete／predictive text、HTML 的 DOM（[00:26:07]–[00:30:11]）。講義另外列了 org chart、家譜、賽程表、Python expression `(8 - 3) * (2 + 4)` 會被轉成 tree（講義 p2）。

4. **running example 與名詞**（[00:31:03]–[00:37:02]；講義 p2–p3）
   - 範例樹（9 nodes、4 leaves、height 3），整週都會用，週三還會再用：
     ```
             8
           /   \
          3     10
         / \      \
        1   6      14
           / \    /
          4   7  13
     ```
   - 課堂上補了講義沒有的兩個詞：**branch**（老師說 branch 其實就是 subtree）和 **path**（從一個 node 到另一個 node 的路線）（[00:32:00]–[00:33:01]）。

5. **binary tree 的 recursive 定義**（[00:38:04]–[00:44:02]；講義 p3）
   - **binary tree 要嘛是 empty，要嘛是一個 node 帶一棵 left tree 和一棵 right tree。** 這是用自己定義自己，也就是 recursive data structure。
   - base case 就寫在定義裡：empty tree。所以 leaf 也是 binary tree（node + 兩棵 empty tree）（[00:41:01]–[00:43:04]）。
   - **linked list 是 tree 的特例**：每個 node 只有一個 child（[00:43:04]–[00:44:02]）。講義補充這是 degenerate case，lopsided tree 會跟 linked list 一樣差，下一堂會用到（講義 p3）。

6. **用 dict 建樹**（[00:47:00]–[00:58:06]；講義 p4）
   - 不用 class，跟 linked list 一樣用 dict：
     ```python
     def create_tree_node(value, left=None, right=None):
         return {'payload': value, 'left': left, 'right': right}
     ```
     linked list 的 `next` 變成 `left` 和 `right` 兩個連結。`left=None` 是 default parameter，呼叫時可以不給（[00:49:02]）。
   - 用巢狀呼叫一次建好整棵範例樹。老師自己也承認括號很難數、很亂，平常不會這樣建，但先這樣做（[00:52:01]–[00:55:04]）。
   - empty tree 就是 `None`（相當於 null）。有同學問 `None` 會不會配置記憶體，老師說她認為不會，並請大家如果知道就糾正她（[00:55:04]–[00:56:03]）。
   - 手動走訪：`root['left']['right']['payload']` → 6；`root['right']['left']` → `None`（[00:56:03]–[00:58:06]）。講義 p4 用的例子是 `root['left']['right']['left']['payload']` → 4，並提醒對 `None` 再取 key 會 `TypeError`，所以每個函式都先檢查 node 是不是 `None`。

7. **recursion：tree_size**（[01:01:07]–[01:21:00]；講義 p4）
   - 兩個 case：empty → 0；否則 1（自己）+ 左子樹 size + 右子樹 size。
     ```python
     def tree_size(node):
         if node is None:
             return 0
         return 1 + tree_size(node['left']) + tree_size(node['right'])
     ```
   - 第一次寫成 `node.left` 出錯，改成 `node['left']`（[01:05:03]）。範例樹結果 9。
   - 老師加 print 一步一步追呼叫順序：8 → 3 → 1 → (None, None) → 6 → 4 → … → 13，最後加總 9（[01:14:08]–[01:17:02]）。
   - 有同學問「那個 1 是什麼」：是目前這個 node 本身（[01:17:02]–[01:19:08]）。用單一 node 42 驗證，size 1。

8. **recursion：tree_height 的除錯過程**（[01:22:00]–[01:43:04]；講義 p4–p5）
   - 同學提議 `1 + max(height(left), height(right))`，但 base case 照抄 size 的 `return 0`，結果範例樹算出 **4**（應該是 3），單一 node 算出 **1**（應該是 0）（[01:29:02]–[01:31:01]）。
   - 同學提議「如果 `tree_size(node) == 1` 就回傳 0」：會在每一層都重新數整棵子樹，非常沒效率，而且跑起來還是有地方不對，老師放棄這條路（[01:32:00]–[01:35:03]）。
   - 最後課堂上的版本是在某處「減 1」，用來抵消 `1 +`，跑出 3 和 0（[01:37:07]–[01:39:04]）。老師的解釋：**height = 層數（levels）− 1**，`1 + max(...)` 數的是 levels，再減 1 得到 edges 數（[01:39:04]–[01:41:00]）。
   - 有同學問這個 −1 是不是 hacky。老師說 recursive 寫法本身是 canonical，−1 算不算 hacky 看你怎麼想，但它符合「height = levels − 1」（[01:42:02]）。
   - **講義的寫法比較乾淨**：把 base case 改成 empty tree 回傳 **−1**，`1 + max(-1, -1) = 0`，不用另外減 1（講義 p5）。見下面「還要釐清的問題」第 1 點。

9. **depth-first traversal 預告**（[01:44:00]–[01:50:05]）
   - 在白板上示範兩種走法：
     - 一路往下、先走左邊、遇到就先 visit：8, 3, 1, 6, 4, 7（時間不夠，只走到 7）→ 這就是 preorder。
     - 先往左走到底，兩個 children 都 visit 完才 visit 自己：1, 4, 7, 6, 3, 13, 14, 10, 8 → 這就是 postorder。
   - 同學說出 pre-order、in-order、post-order，老師說週三正式定義（[01:49:01]）。
   - 老師說 tree_height 本質上就是一次 depth-first search：數出有幾層，再減 1（[01:49:01]–[01:50:05]）。
   - 有同學問能不能用 queue 做，老師說這是很好的銜接，週三再講（[01:43:04]）。

10. **講義後半（上課沒講，週三會講）**（講義 p5–p10）
    - `count_leaves`：第二個 base case，兩個 children 都是 `None` 時回傳 1。範例樹 4 個 leaf。
    - 三種 depth-first 順序只差「visit 那一行」放的位置：
      | 順序 | visit 放在 | 範例樹輸出 |
      |---|---|---|
      | preorder | 兩個遞迴呼叫之前（node, left, right） | 8 3 1 6 4 7 10 14 13 |
      | inorder | 兩個呼叫之間（left, node, right） | 1 3 4 6 7 8 10 13 14 |
      | postorder | 兩個呼叫之後（left, right, node） | 1 4 7 6 3 13 14 10 8 |
    - **cliffhanger**：inorder 的輸出是排序好的，不是巧合，週三的 BST 就靠這個（講義 p6）。
    - 用途：preorder 複製樹、印資料夾結構（`os.walk` 預設先給目錄再給子目錄）；postorder 先處理 children 再處理 parent（刪樹、算資料夾大小、evaluate expression）。
    - expression tree `(8 - 3) * (2 + 4)`：preorder = prefix `* - 8 3 + 2 4`；inorder = `8 - 3 * 2 + 4`（括號不見，意思變了）；postorder = postfix `8 3 - 2 4 + *`，用 stack 算出 30。`ast.parse(..., mode="eval")` 會建出同樣的樹。
    - breadth-first（level order）：用 `collections.deque` + `popleft()`，範例樹輸出 8 3 10 1 6 14 4 7 13。
    - 同一個 loop 換成 list 當 stack（`pop()`），先 push right 再 push left，就得到 preorder。**stack 走深、queue 走寬**；recursive 版本其實用的是 Python 的 call stack。
    - runtime 表見「名詞解釋」最後。
    - recursion limit：Python 預設 1,000 層（`sys.getrecursionlimit()`）。講義說 Python 3.11 上 1,000 個 node 的 chain 跑 `tree_height` 會 `RecursionError`，995 個還可以。不要調高 limit，改用 iterative 版本。
    - Java `TreeMap`、C++ `std::map` 底層通常是 tree，講 balancing 時會再提。

## 名詞解釋

| 名詞 | 意思 | 範例樹 |
|---|---|---|
| linear data structure | 資料排成一列：array、linked list、stack、queue | — |
| node | 樹裡的一格，有 payload 和指向 children 的連結 | 每個圓圈 |
| root | 最上面的 node，**唯一沒有 parent 的 node** | 8 |
| parent / child | 正上方的 node／正下方的 node | 3 和 10 是 8 的 children |
| leaf | 沒有 children 的 node | 1, 4, 7, 13 |
| subtree | 一個 node 加上它底下所有東西；老師說 branch 就是 subtree | 以 6 為根的 subtree 是 6, 4, 7 |
| path | 從一個 node 走到另一個 node 的路線 | — |
| depth（of a node） | 從 root 往下到它要走幾條 edge，也就是它在第幾層（從 0 開始） | 8 depth 0；13 depth 3 |
| height（of a tree） | 最深 node 的 depth，也就是 root 到最深 leaf 的 edge 數 = levels − 1 | 3 |
| level | 每個 depth 是一層；depth 0 是第 1 層 | 範例樹有 4 層 |
| binary tree | 每個 node 最多 2 個 children（0、1、2），叫 left 和 right | 本堂所有的樹 |
| recursive data structure | 用自己定義自己：binary tree = empty 或 node + left tree + right tree | — |
| base case | recursion 停下來的情況；tree 的 base case 是 empty tree（`None`） | — |
| degenerate tree | 每個 node 只有一個 child，等於 linked list | — |
| perfect binary tree | 每一層都滿；height h 有 2^(h+1) − 1 個 node（1, 3, 7, 15…）（講義 p3） | — |
| traversal | 每個 node 剛好 visit 一次 | — |
| depth-first（DFS） | 先一路往下走到底再回頭；preorder／inorder／postorder | — |
| breadth-first（BFS）／level order | 一層一層走；用 queue（講義 p7） | 8 3 10 1 6 14 4 7 13 |
| prefix／postfix notation | operator 放前面／後面；postfix 不需要括號（講義 p6） | — |
| ADT（abstract data type） | 行為上的約定（stack = LIFO、queue = FIFO），跟底層實作分開（[00:19:04]） | — |
| iterative | 用 loop（＋自己的 stack/queue）取代 recursion（[01:22:00]） | — |

**runtime 表**（講義 p8）

| 操作 | Time | Extra space | 原因 |
|---|---|---|---|
| size、height、count leaves | O(n) | O(h) | 每個 node 看一次；call stack 深度 = 樹高 |
| preorder／inorder／postorder（recursive） | O(n) | O(h) | 同上 |
| level order（queue） | O(n) | O(w) | queue 一次放一層，w = 最寬那層的寬度 |
| iterative depth-first（list 當 stack） | O(n) | O(h) | stack 放等待 visit 的 node |
| 在沒有排序規則的樹裡找值 | O(n) | O(h) | 不知道該往哪邊找，只能全部看 |

- h 介於約 log₂ n（塞得很滿）和 n − 1（chain）之間。一百萬筆可能是 19 層，也可能是 999,999 層，**全看形狀**，這是接下來兩堂的主題。
- perfect tree 最底層約占一半的 node，所以 level order 在很茂密的樹上很吃記憶體；DFS 只需要存一條 path。

## 老師強調的地方（附逐字稿時間戳）

- [00:13:00] 她在 Python 裡從來不用 `import array`；一般用 `list`、`deque`，數值運算用 NumPy。
- [00:14:01]–[00:15:11] 作業的 invite（GitHub Classroom 邀請）流程「變成一團亂」，她會想辦法改善，之後換更好的做法。
- [00:15:11] **作業截止日是週日**（同學問 A3 是不是改回週五，老師說是 Sunday）。她可能還沒全部更新，請同學到 Piazza 留言提醒她，下課後改。→ 10/20 1:10 AM 重抓時 Canvas 已經改成 A3 10/25（日）、A4 11/1（日）。
- [00:19:04] **考試範圍**：要知道 Python list 怎麼運作（dynamic array of references、pop 頭貴、pop 尾和 append 便宜）；`deque` 算加分。
- [00:20:06] ADT 和 implementation 要分清楚：stack／queue 是 ADT，可以用 array、linked list 或 deque 實作。
- [00:25:02] 一百萬步 vs 約 20 步，這就是我們要往 binary search 走的原因。
- [00:31:03] 這棵範例樹今天和週三都會用。
- [00:40:03]–[00:41:01] binary tree 是 recursive definition，base case 就是定義裡的 empty。
- [00:44:02] linked list 可以看成 tree 的特例，之後要記得這點。
- [00:45:06]–[00:46:01] **height 的定義不統一**：本課用 edges 數；有些書用 nodes 數。跟課外的人合作時要先對齊定義。講義 p3 也說考題會選一邊，要看題目。
- [00:55:04] 巢狀建樹很難寫，之後不會一直這樣建。
- [01:07:04] **準備面試時，遇到 tree 題（尤其 binary tree）先寫 recursive 版本**，靠定義寫出來。
- [01:08:05]–[01:09:03] recursive 很沒效率，寫進 production 的程式不要用 recursive；但它是把邏輯寫對的好起點，之後再改成 iterative（[01:21:00]–[01:22:00]）。
- [01:20:01]–[01:21:00] 寫 recursion 要有「leap of faith」：有 base case、處理目前這個 node、處理 left 和 right，然後相信遞迴呼叫。講義 p5 也說要相信較小的呼叫，不要在腦中追整棵樹。
- [01:24:07] 提示可以用 Python 內建的 `max()`。
- [01:25:08] 因為 `if node is None` 已經是 base case，呼叫 left／right 前不需要先檢查它們是不是 `None`。
- [01:35:03] 用 `tree_size == 1` 判斷 leaf 的做法，每次分岔都會走遍子樹的所有 node，很沒效率。
- [01:39:04]–[01:41:00] height = levels − 1；這個 −1 抵消 `1 +`。
- [01:49:01]–[01:50:05] tree_height 其實就是一次 depth-first search。
- [01:50:05] 講義會拿掉部分內容後再發；code 會 push 到 repo；白板圖會放到 repo。

## 和作業 / 考試的關聯

- **A3 Stacks, Queues and Testing**：10/25（日）11:59 PM PDT，150 分。老師在課堂上確認作業都是週日截止（[00:15:11]），和 Canvas 一致。Piazza @51 問 A3 README（100 + 25 = 125）和 Canvas（150）配分對不上，還沒有老師回覆。本堂的 tree 內容和 A3 沒有直接關係，但講義 p7 的「同一個 loop 換 stack／queue」是 A3 stack/queue 的好複習。
- **A4 Bug Hunt**：11/1（日）11:59 PM PST（DST 結束當天）。
- **A5 BSTs and AVLs**：11/22（日）11:59 PM PST。**本堂（tree 基礎、recursion、traversal）就是 A5 的前置**，週三進 BST，之後 balancing（AVL）。inorder 輸出排序好的性質是 BST 的關鍵。
- **Midterm**：11/9（一）4:30–6:30 PM PST，實體紙筆，Moore 220。可能會考：
  - Python list 的內部運作（[00:19:04] 老師明講）。
  - tree 名詞、height 用 edges 算（單一 node height 0、empty tree −1）。
  - 手寫 recursive `tree_size`／`tree_height`／`count_leaves`。
  - 三種 DFS 順序、BFS 順序（講義 p9 的 check questions 1–7 很像考題，附答案在 p9–p10）。
- 面試準備：tree 題先寫 recursive（[01:07:04]）；講義 p6 說「interview 會問」每種順序的用途。
- 課程 AI 政策提醒：DSA 禁止把 starter code 交給 AI，用了 AI 要附 chat session 或註明。本筆記只整理上課內容，不涉及作業 starter code。

## 還要釐清的問題

1. **課堂上 tree_height 的 −1 到底加在哪裡？** 逐字稿只說「this minus one counteracts this one」（[01:38:01]–[01:39:04]），看不到程式碼。可能是 base case 仍回傳 0、在最外層再減 1。若是在每一層的 `return` 都減 1，會跟 `1 +` 互相抵消，結果永遠是 0，所以應該不是那樣。**建議以講義 p5 的版本為準**（base case `return -1`），等老師 push 的 in-class code 出來再核對。
2. 講義說 Python 3.11 上 1,000 個 node 的 chain 跑 `tree_height` 會 `RecursionError`、995 還可以。本機 Python 版本不同時，邊界可能不一樣，可以自己試一次。
3. 講義 p6 說 `ast.walk` 在 CPython 3.11 的實作是 deque + `popleft`（實際上是 BFS），但 docstring 寫 "in no specified order"。這不影響考試，只是知道一下。
4. 老師說 `None` 不會配置記憶體（[00:56:03]），她自己也不確定。比較精確的說法是：`None` 是一個全域 singleton，所有 `None` 都指向同一個物件，所以 `left=None` 不會多配置新物件，只存一個 reference。
5. 老師說會發「清理過」的講義（[01:50:05]）。Canvas 上的 PDF 檔名有 `_students`，應該就是這份。如果之後出現新版要重抓。
6. 作業 invite 流程會改（[00:15:11]）。之後留意 Piazza／Canvas 有沒有新的 GitHub Classroom 做法，A3 之後的 repo 可能不同。
7. Grokking Algorithms 對應的 Trees 章節號碼還沒核對版本。
