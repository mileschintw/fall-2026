# DSA Class 8 — 2026-10-26（週一，Mod 3 Trees/BST：fault tree 用 post-order 算失效機率、binary search tree 規則、search / insert（iterative）、min / max / successor、delete 三種情況、search 成本 O(h)）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，1151 cues，00:04:01–01:50:08，約 110 分鐘，DeliveryID `a75e4b14-f311-4938-9c21-b4f00023a332`，Canvas Module 3 item 27612053「Mod 3 Trees/BST [Mon, Class 8]」）、slides（`EE590a_Class_Mon_fault_trees_and_BSTs_student_copy.pdf`，file 155028144，Canvas Module 3 item 27611371，10 頁；文字在 `slides.txt`，抽出來的字元之間有空格，是 PDF 排版造成的）。這份是老師的上課 outline / notes，不是投影片，老師說講課就是照這份（[00:08:06]）。閱讀：Grokking Algorithms 第 1 版（Canvas 模組寫「Chapter 5, Hashtables」「Chapter 7, Djikstra's Algorithm」，章號對得上第 1 版）。課程沒有指定本堂章節，下面的對照是自行整理的：Ch 1 Binary search 的 log₂ n 與「每步丟掉一半」、Ch 1 Big O notation 的成長表、Ch 3 Recursion 的 call stack；Grokking 沒有專門講 BST 的章節，Ch 11 "Where to go next" 只簡短提到 binary search tree）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 錄影前 4 分鐘沒有字幕（第一句在 00:04:01），開場是老師在設定螢幕分享。
>
> 常見誤聽對照：VST / BSC / PST / VST Monday → BST（`bst_…`、檔名 BST Monday）；Wi-Fi research → binary search（tree）；Her node / Kernode / Pranode / per node / Curd note / Crud → cur node（目前的 node）；Root of payload / Route of payload → `node['payload']`；Elves → else；Lesson → less than；Slide equals left → `side = 'left'`；node outside → `node[side]`；Friends PST search → print `bst_search_…`；Sheffield / Shuffle B → `shuffled`；Change → `chain`；time.berf Ontario → `time.perf_counter`；Range.sample → `rng.sample`；Century → subtree；Men of Right → min of right（child）；Sit with predators → predecessor；of age → O(h)；Anne → n；Element → （應該是 O(n)）；hiding tree → height of the tree；EMIT / admit / knit → emit；Pompe A → pump A；Mikey Euro Astro people → mechE / aero / astro 的人；R6 / R7 → 「emit 6」「emit 7」；the truth → the tree。人名：Joan Marie / Joan / Jean（同學，提出 aeronautics 的 fault tree）、Seth、Alec、Brent、William、Ethan（同學）、Luna（老師問有沒有 sample midterm 時叫的名字，可能是助教或同學）。

## 重點摘要

1. **開場公告**（[00:06:02]–[00:13:00]）
   - **Midterm 兩週後，11/9（一），實體、在教室、紙筆**（[00:06:02]、[00:11:00]）。題型：會有好改的題目（例如選擇題），因為全部要手改又要準時發回；**不會要求寫語法完全正確的 code**，可能要寫 pseudocode 或填空，程度大概是「上課用 Python 寫的那種 code」，不會因為語法扣分（[00:07:00]）。
   - 讀書材料：老師放在 Canvas 的每份 outline / notes 最後幾乎都有 check-your-knowledge 題目和答案，是很好的複習來源（[00:08:06]）。她不確定有沒有 sample midterm，會去查；可能拿舊的期末考題當範例，但那涵蓋整學期，有些還沒教到（[00:08:06]–[00:09:10]）。**下週（11/2 那週）會講哪些是 midterm 範圍、哪些不是**（[00:09:10]）。
   - **11/11（三）Veterans Day 停課，不補課**；midterm 刻意排在放假前一天（[00:09:10]–[00:10:00]）。
   - **A4 已經發布**：一週的時程，是第一個可以用 AI 的作業（[00:10:00]–[00:11:00]）。**請保留你的 AI 對話紀錄（transcripts）**：這次不用交，但之後所有作業都請保留，萬一學期末有 academic integrity 的疑問可以保護自己；學期結束後要刪就刪（[00:11:00]–[00:13:00]）。
   - **A5 會提早發布**：分兩部分，截止在 midterm 之後；但老師建議**先做 Part 1，當作 midterm 準備**（[00:13:00]）。講義也說 A5 Part 1 就是建今天這棵 BST（loop 或 recursion 都可以），delete 也要自己在 A5 Part 1 實作（講義 p1、p5）。

2. **Fault tree：post-order traversal 的真實應用**（[00:14:01]–[00:25:13]）
   - 上週同學 Joan Marie 提到航太業用 fault tree 評估飛機失效機率，老師用一棵自己編的樹示範（[00:14:01]–[00:15:05]）。
   - 樹：root（top event）=「loss of hydraulic pressure」；底下是 OR：line rupture（p = 10⁻⁷）或「兩個 pump 都壞」；「兩個 pump 都壞」是 AND：pump A 壞且 pump B 壞；每個 pump 壞又是 OR：motor 壞或 controller 壞（[00:15:05]–[00:21:00]）。
   - 規則（講義 p2）：**AND gate** 的機率 = 各 input 相乘；**OR gate** = 1 − ∏(1 − pᵢ)。pump A：1 − (0.9996)(0.9994) ≈ 0.001；兩個都壞 ≈ 10⁻⁶；整個系統 ≈ 1.0995 × 10⁻⁶，約每趟飛行 90 萬分之一。兩條規則都假設 basic events 互相獨立。（講義 p2）
   - **為什麼是 post-order**：要算 top event 之前得先算出每個 child，所以 node 必須在所有 children 之後處理，正是 post-order；pre-order 會先碰到 top gate，那時 inputs 都還沒算（[00:22:01]–[00:24:00]；講義 p2）。和上週的 `eval_postfix` / expression tree 是同一種形狀（講義 p2）。
   - fault tree 的 gate 可以有任意多個 input，所以 node 存 `children` list，不是 left/right；講義 p2–p3 有 `failure_probability(node, out)` 的完整 code。老師上課沒寫 code，說概念最重要，想玩可以自己照 notes 實作（[00:25:13]）。
   - 講義補充（上課沒講）：只有一個 pump 時機率約 10⁻³，差了約 900 倍，這就是 redundancy 的意義；走一次 n 個 node 要 n 步；如果同一個元件出現在兩處，就不再是 tree（一個 node 會有兩個 parent），天真地相乘會算錯（範例 0.0494 vs 正確 0.044）；參考 NASA 的 *Fault Tree Handbook with Aerospace Applications*（講義 p3）。

3. **in-order 得到排序結果 → binary search tree 規則**（[00:26:00]–[00:35:00]）
   - 沿用上週的範例樹（insert 順序 8, 3, 10, 1, 6, 14, 4, 7, 13）：
     ```
             8
           /   \
          3     10
         / \      \
        1   6      14
           / \    /
          4   7  13
     ```
   - 全班一起走 in-order：`1 3 4 6 7 8 10 13 14`，**是排序好的**（[00:27:08]–[00:30:01]）。
   - **BST 規則**：for every node，**left subtree 裡的每個值都比它小，right subtree 裡的每個值都比它大**（[00:32:02]–[00:34:01]）。同學先說「比 node 小就往左」，老師說那是演算法，她要的是描述這棵樹本身的性質（[00:30:01]–[00:31:02]）；另一位同學說「left child 比較小、right child 比較大」，老師把它擴充成整個 subtree（[00:32:02]）。講義也特別寫「every value in the subtree，不是 the child」（講義 p3）。
   - 有 BST 就保證 in-order 輸出是排序的（Seth 問，[00:34:01]–[00:35:00]）。

4. **Search（by hand → iterative code）**（[00:35:00]–[00:48:02]）
   - 找 13：8 → 右 → 10 → 右 → 14 → 左 → 13，看了 9 個 node 中的 4 個。**每一步都丟掉一整個 subtree**，跟 sorted list 上的 binary search 是同一個想法（[00:35:00]–[00:37:01]；講義 p3）。老師也點出它的 recursive 性質：每一步都在左或右 subtree 上跑同一個演算法（[00:38:02]）。
   - 老師這次**直接寫 iterative 版本**（上週一直說「能 recursive 就能 iterative」），**週三會講怎麼在兩者之間互換**（[00:39:00]–[00:40:02]）：
     ```python
     def bst_search_iterative(root, value):
         node = root
         while node is not None:
             if value == node['payload']:
                 return node
             node = node['left'] if value < node['payload'] else node['right']
         return None   # fell off the tree: not here
     ```
     上課是用 if/else 寫的（老師說「clunky way」），加 print 追蹤：找 13 → 8, 10, 14, 13；找 1 → 8, 3, 1；找 9 → 8, 10，然後掉出樹外回傳 None（[00:40:02]–[00:48:02]）。
   - 講義補充：Python 的 recursion 上限約 1,000 層，長路徑的樹會爆，所以 loop 版也要會寫；對比 `tree_size` 要兩次 recursive call，search 只走一邊，「少掉的那一次 call 就是速度的來源」（講義 p4）。重複值的 policy：這裡**忽略重複**（像 set），考試要看題目假設哪一種（講義 p4）。

5. **Insert，以及插入順序決定形狀**（[00:48:02]–[01:01:00]）
   - **insert = 先 search，掉出樹外的那個位置就是新 node 該放的地方；新值永遠變成 leaf**（[00:50:04]–[00:51:07]；講義 p4）。例：insert 9 → 10 的 left；insert 5 → 8, 3, 6, 4，放在 4 的 right（[00:49:08]–[00:52:02]）。
   - 照 8, 3, 10, 1, 6, 14, 4, 7, 13 的順序插入，就得到上面那棵範例樹（[00:52:02]–[00:54:01]）。
   - 休息後用**同樣的值、排序好的順序**（1, 3, 4, 6, 7, 8, 10, 13, 14）插入：得到一條往右的鏈，**本質上是 linked list**，但仍然符合 BST 規則（[00:57:13]–[01:01:00]）。講義：一棵 height 3、一棵 height 8（講義 p5）。
   - 下課前的 demo 才寫 `bst_insert_iterative`（[01:40:01]–[01:43:09]）：
     ```python
     def bst_insert_iterative(root, value):
         if root is None:
             return create_tree_node(value)   # empty tree: the new node is the root
         node = root
         while True:
             if value == node['payload']:
                 return root                  # duplicate: nothing to do
             side = 'left' if value < node['payload'] else 'right'
             if node[side] is None:
                 node[side] = create_tree_node(value)
                 return root
             node = node[side]
     ```

6. **min / max / successor**（[01:01:00]–[01:03:01]、[01:08:01]–[01:10:01]）
   - min：一直往左直到沒有 left child；max：一直往右（[01:01:00]–[01:02:12]）。範例樹 min = 1、max = 14（講義 p5）。
   - **successor**（下一個比它大的值）：有 right subtree 時 = **right subtree 的 min**（往右一步，再一路往左）。3 的 successor 是 4（[01:08:01]–[01:10:01]）。

7. **Delete 的三種情況**（[01:03:01]–[01:19:00]；講義 p5–p6）
   - **沒有 children（leaf）**：例 delete 1，把 parent 指向它的 link 設成 None（[01:03:01]–[01:04:00]）。
   - **一個 child**：例 delete 14（只有 left child 13），讓 parent（10）直接連到 13，13 的整個 subtree 一起帶過去。為什麼仍是 BST：13 的 subtree 原本就在 10 的右邊（都 > 10）且在 14 的左邊（都 < 14）（[01:04:00]–[01:06:05]）。
   - **兩個 children**：例 delete 3（children 1 和 6）。找 successor 4（right subtree 的 min），**把 4 的值複製到 3 的位置，不重排樹**，再從 right subtree 刪掉原本的 4；4 沒有 children，所以變回簡單情況（[01:06:05]–[01:11:00]）。
   - successor 一定是 right subtree 的最左 node，所以**沒有 left child**，刪它只會是 leaf 或 one-child 的情況：困難情況化簡成簡單情況（講義 p6）。
   - 另一種做法：用 **predecessor**（left subtree 的 max）。Ethan 問為什麼不用 left 的 max，老師說可以，不同課本做法不同，兩者都對，**選一種就要一致**；課堂用 successor 就好（[01:14:00]–[01:18:00]）。
   - 今天**沒寫 delete 的 code**，留給 A5 Part 1（[01:11:00]）。講義的提示：two-children 的情況用 recursive call 刪 successor 最短；function 要回傳剩下那棵樹的 root，因為刪掉 leaf root 或 one-child root 會改變 root（講義 p6）。
   - 講義的預測練習：delete 8（root）→ successor 10 變成 root，preorder `10 3 1 6 4 7 14 13`；delete 3 → preorder `8 4 1 6 7 10 14 13`（講義 p6、p10）。

8. **Search 的成本：數 steps、O(h)**（[01:19:00]–[01:36:11]）
   - 為什麼不用秒數：clock time 受 machine、hardware、language、同時在跑的程式影響，不能跨實作比較；所以改數 steps，**一個 step = visit 一個 node**（[01:20:02]–[01:22:02]）。
   - 在範例樹找 13 是 4 步，在鏈狀樹找 13 是 8 步。**search 每一層最多 visit 一個 node，所以步數不超過 height（+1）**：cost = **O(h)**（[01:23:00]–[01:25:02]）。
   - h 和 n 的關係取決於形狀：鏈狀時 h ≈ n（worst case）；well-behaved、每層幾乎填滿時 h ≈ log₂ n（best case），因為每一步把問題切一半（[01:26:06]–[01:34:00]）。
   - 有同學問「只有 worst case 才是 height 嗎？」老師澄清：**worst case 是 height of the tree，而 height 本身介於 log n 和 n 之間**（[01:34:00]–[01:35:02]）。
   - 要同時考慮 best / worst / average case（[01:31:04]–[01:32:08]）。講義定義：best = 同大小下最便宜的 input，worst = 最貴的，average = 在某種 input 到達方式的假設下取平均。BST search 的 best case 是 1 步（值在 root），不管 n 多大（講義 p7）。範例樹：8 要 1 步，3、10 要 2 步，1、6、14 要 3 步，4、7、13 要 4 步，平均 26 ÷ 9 ≈ 2.9（講義 p7）。

9. **Live demo：random order vs sorted order**（[01:36:11]–[01:50:05]）
   - 用 `rng.sample(range(50000), 5000)` 建兩棵樹：一棵照隨機順序插入（`shuffled`），一棵照排序順序（`chain`），各做 5,000 次 search 計時（[01:37:00]–[01:39:02]）。
   - 第一次跑：random 約 0.04 秒、sorted 約 0.08 秒（字幕寫成「0.4」「0.8」，下一句說要記住 0.04 和 0.08）；放大到 100,000 後兩邊時間幾乎一樣，老師覺得「fishy」（[01:43:09]–[01:46:02]）。
   - 同學下課時抓到 bug：**建 `chain` 時忘了 `sorted()`**，兩棵樹其實都是隨機順序（[01:47:15]）。修好後 sorted 那棵跑很久，改成 10,000 個值重跑，**sorted 版本要約 12 秒**（[01:48:04]–[01:49:04]）。
   - 講義的數字（老師自己的機器，Python 3.11）：random 約 0.005 秒、sorted 約 0.6 秒，慢 120–150 倍。100,000 個值時 random 平均 21.4 步、sorted 平均 50,000.5 步；random tree 的 height 大約是理想值的兩倍，平均步數約 1.2–1.3 × log₂ n（講義 p7–p8）。
   - 講義補充：recursive insert 在約 1,000 個 sorted 值時會 RecursionError（990 可以、1,000 不行），loop 版沒有這個限制；排序或接近排序的資料很常見（timestamp、id、字母順序的字典），只有資料事先全部到齊時 shuffle 才有用；**週三的 AVL tree 讓 worst case 也變好**（講義 p8）。

## 名詞解釋

- **fault tree**：從一個失效事件（top event，放在 root）往回拆解原因的樹。leaf 是有機率的 basic events，internal node 是 AND / OR gate。
- **AND gate / OR gate**：AND = 所有 input 都失效才失效，機率相乘；OR = 至少一個 input 失效就失效，機率 = 1 − ∏(1 − pᵢ)。都假設事件獨立。
- **post-order traversal**：先處理所有 children，最後才處理 node 本身。fault tree、expression tree（`eval_postfix`）這種「bottom-up 合併結果」的計算都要用它。
- **in-order traversal**：left → node → right。對 BST 來說輸出一定是排序好的。
- **binary search tree（BST）**：binary tree，且對每個 node，left subtree 所有值都比它小、right subtree 所有值都比它大。
- **payload**：課堂上 node（dict）裡存值的欄位，`node['payload']`；另外有 `node['left']`、`node['right']`。
- **iterative vs recursive**：iterative 用 loop（通常是 `while` 加一個 `cur node` 變數），recursive 是 function 呼叫自己。Python 預設 recursion 上限約 1,000 層。
- **successor / predecessor**：successor = 排序後下一個比它大的值（有 right subtree 時 = right subtree 的 min）；predecessor = 下一個比它小的值（left subtree 的 max）。
- **splice out**：one-child delete 時讓 parent 直接連到被刪 node 的 child。
- **duplicate policy**：插入已經存在的值時怎麼處理。課堂版本忽略（像 set），其他做法有在 node 存 count、或相等的值一律往右放。
- **step**：計算成本的單位。對 BST search 來說就是 visit 一個 node（一次比較加一次移動）。
- **height（h）**：從 root 到最深 leaf 的路徑長度。depth：從 root 到這個 node 的路徑長度，root 的 depth 是 0；找到一個 node 要 depth + 1 步。
- **best / worst / average case**：同一個演算法的三個問題：最便宜的 input、最貴的 input、在某個 input 分布假設下的平均。
- **well-behaved / balanced tree**：每層幾乎填滿，height ≈ log₂ n。反面是 chain（degenerate tree），height = n − 1。

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

- **Midterm 11/9，實體、教室、紙筆**，要提早計畫；有同學晚到問日期，老師再說一次並要大家那天到教室（[00:06:02]、[00:11:00]）。
- Midterm **不會要求語法正確的 code**，可能是 pseudocode 或填空，程度跟上課寫的 Python 差不多（[00:07:00]）。
- **Canvas notes 最後的 check-your-knowledge 題目是好的讀書材料**（[00:08:06]）。
- 11/11 Veterans Day 停課**不補**；她說常被問「放假要不要補課」（[00:10:00]）。
- **保留 AI 對話紀錄**，A4 以及之後所有作業都是；用途是萬一有 academic integrity 疑問時保護自己。她自己說這可能有點太保守（[00:11:00]–[00:13:00]）。
- **先做 A5 Part 1，當作 midterm 準備**（[00:13:00]）。
- fault tree 是 post-order 很漂亮的真實例子：要先有 children 的機率才能算 parent（[00:24:00]–[00:25:13]）。
- BST 規則要講的是**整個 subtree**，不只是 child；她要的是描述樹的性質，不是演算法（[00:30:01]–[00:33:00]）。
- search 每一步都**切掉一半的 search space**（[00:37:01]）。
- 「能 recursive 就能 iterative」，週三會講怎麼互換（[00:39:00]–[00:40:02]）。
- insert 就是 search，search 停下來的地方就是新 node 的位置（[00:50:04]–[00:51:07]）。
- **同樣的值、不同的插入順序，會得到形狀完全不同的樹**；sorted 順序會變成 linked list，而且它仍然是合法的 BST（[00:57:13]–[01:01:00]）。
- 每做完一個操作都要**回頭確認它還是 BST**，而且要能說出理由，不能只看圖（[01:06:05]、[01:13:00]）。
- **已經定義好的操作就直接用**：找 successor 就呼叫 min，不要再重寫一遍「一直往左」。她說常在作業裡看到重複實作（[01:09:04]）。
- 兩個 children 的 delete：successor 或 predecessor 都可以，**選一種就要一致**（[01:16:02]）。
- 成本要用**可比較的 metric**，不能看 clock time；step = visit 一個 node（[01:21:00]–[01:22:02]）。
- search 的 worst case 是 height，而 **height 介於 log n 和 n 之間**，由形狀決定（[01:25:02]、[01:35:02]）。
- demo 的 bug 是建 sorted 樹時漏了 `sorted()`；修好後 sorted 版要等約 12 秒（[01:47:15]–[01:49:04]）。

## 和作業 / 考試的關聯

- **Midterm：11/9（一）4:30–6:30 PM PST，實體紙筆，Moore 220**（`dsa/assignments.md`）。範圍下週（11/2 那週）才會公布。今天的 BST 規則、search / insert 手動追蹤、delete 三種情況、O(h) 都很可能考。講義 p9 的 6 題 check questions 和 p9–p10 的答案就是老師說的讀書材料。
- **A4 Bug Hunt：11/1（日）11:59 PM PST**（`due_at` 2026-11-02T07:59:59Z，DST 結束當天；未交）。第一個可以用 AI 的作業，**記得保留 AI 對話紀錄**。
- **A5 BSTs and AVLs：11/22（日）11:59 PM PST**（`due_at` 2026-11-23T07:59:59Z；未交）。老師說會提早發布、截止在 midterm 之後，與 Canvas 一致。**Part 1 = 實作 BST（loop 或 recursion 都可以），包含 delete**；老師建議 midterm 前先做完。
  - delete 的提示（講義 p6）：two-children 情況把 successor 的值複製進來，再對 right subtree recursive 刪掉 successor；function 回傳剩下那棵樹的 root。
  - 用 recursion 時注意 Python 約 1,000 層的上限，sorted input 很容易撞到（講義 p8）。
  - 重複值 policy 要看作業規定（講義 p4）。
- 停課：**11/11（三）Veterans Day**，不補課。

## 還要釐清的問題

- **Big O 什麼時候講完？** 上週三（10/21）投票決定「下週一深入講 Big O」，但今天只講到 O(h)、best/worst/average，老師最後說週三再從那張表延伸到 n log n、n²（[01:46:02]）；講義也說週三才給 O、Ω、Θ 精確定義（講義 p8）。另外講義 p1 說週三講 **AVL tree**，老師則說週三講 recursive ↔ iterative 的轉換（[00:40:02]）。週三的實際安排要看錄影。
- **Midterm 範圍**：下週才公布（[00:09:10]）。有沒有 sample midterm 還不確定（[00:08:06]）。
- **A5 發布了沒？** 老師說「almost going out」（[00:13:00]），要確認 Canvas / GitHub classroom 上 A5 Part 1 的實際要求，例如 duplicate policy、delete 要用 successor 還是 predecessor、要不要 recursive / iterative 兩個版本都寫。
- **demo 數字和講義對不上**：上課修好 bug 後是 10,000 個值、sorted 約 12 秒；講義是 5,000 個值、sorted 約 0.6 秒。上課改了 n、可能也改了 search 次數（老師說「I didn't update the 5,000」，[01:49:04]），所以數字不能直接比；以講義的表格為準來理解 O(log n) vs O(n)。
- [01:18:00] 老師想說「BST 的 min 和 max 有某種性質」，說到一半又說不完全對，就沒講下去。可能是指 min / max 最多只有一個 child（min 沒有 left child、max 沒有 right child），可以在 Piazza 問。
- 字幕在 [01:43:09] 寫「0.4 seconds」「0.8」，下一句說要記住「0.04 and 0.08」，判斷前者是聽錯，以 0.04 / 0.08 為準。
