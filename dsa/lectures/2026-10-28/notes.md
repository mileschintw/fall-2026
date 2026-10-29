# DSA Class 9 — 2026-10-28（週三，Mod 4 Trees/AVL, Big-O：為什麼 BST 需要平衡、balance factor、AVL 定義、right rotation、asymptotic analysis：O / Θ / Ω 的正式定義）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，1059 cues，00:04:32–01:54:28，約 114 分鐘，DeliveryID `2a320fb9-8082-4e68-bced-b4f200240c3c`，Canvas Module 4 item 27627622「Mod 4 Trees/AVL, Big-O [Wed, Class 9]」）、slides（兩份，文字都在 `slides.txt`，抽出來的字元之間有空格，是 PDF 排版造成的）：
> - `EE590a_Class_Wed_AVL_and_asymptotics_outline_students.pdf`（file 155413878，Module 4 item 27627620，9 頁）：老師的 class outline，頁尾列印時間是 10/28 9:01 PM，也就是**下課後補完的版本**（老師上課說 notes 目前很陽春，會補上四種 case，[01:15:06]、[01:54:03]）。下面標「講義 pN」的都是這份。
> - `EE590a_Class_Wed_AVL_and_asymptotics_students.pdf`（file 155378415，Module 4 item 27626026，4 頁）：上課用的填空講義（blanks 自己填），內容是 outline 的精簡版，下面標「填空講義 pN」。
>
> 閱讀：課程沒有指定本堂章節（Module 4 沒有 Reading 項目）。下面的對照是自行整理的：Grokking Algorithms 第 1 版 Ch 1 的 Big O notation（running time 成長表、「Big O establishes a worst-case run time」那一段，注意和老師的說法衝突，見最後一節）、Ch 1 Binary search 的 log₂ n；Grokking 沒有 AVL / rotation，Ch 11 "Where to go next" 只簡短提到 balanced tree（B-tree、red-black tree）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 錄影前 4 分半沒有字幕（第一句在 00:04:32）。上課 4:30 PM 開始，休息 5:21–5:31（[00:55:13]），老師超時約 5 分鐘。
>
> 常見誤聽對照：ABL → AVL；Subtrade / Century → subtree；OVEN → O(n)；of age / O of H → O(h)；Log in / log Basin → log n / log base 2 n；end not / n naught → n₀；Giovan / Gee → g(n)；N6 into the sixth → n⁶；bicker → bigger；sordid order → sorted order；Melissa kin / Mella / Millie → milli（second）；nut → not；love child → left child；Wise left child → Y's left child；hydro / hiding → height（of）；Rn → our n；Bryan that's right → （聽不出來，畫 rotation 時的口誤）。老師在 [01:02:06] 說「load factor」其實是指 balance factor（口誤，load factor 是 hash table / dynamic array 的詞）。人名：Rudy（同學，提出「把中間值當 root」）、Ethan（同學，問 f(n) 和 g(n) 的意思、為什麼要 Θ/Ω）、Gwen（休息後回應聽得到）、Wendy（最後點名問還有沒有問題）。

## 重點摘要

1. **回顧週一的 timing demo：插入順序決定 BST 的高度**（[00:05:00]–[00:11:08]）
   - 5,000 個值，random 順序插入後做 5,000 次 search 約 **0.009 秒**；sorted 順序插入（BST 變成 linked list）要 **超過 1 秒**（[00:06:04]）。講義寫 0.005 秒 vs 0.6 秒（講義 p1），數字不同但量級一樣；以上課跑出來的為準，差別應該只是機器和那一次的執行。
   - 老師上次的 notes 裡有實驗表（[00:08:04]–[00:10:01]）：
     | n | random 插入的高度 | random 平均 search 步數 | 理想 log₂ n | sorted 平均 search 步數 |
     |---|---|---|---|---|
     | 1,000 | 約 20 | 約 11.7 | ≈ 10 | 500.5 |
     | 10,000 | 約 30 | 約 16.5 | 13.3 | 5,000 |
   - sorted 的平均步數是 n/2，因為一半的值在 list 前半、一半在後半（[00:09:01]）。random 比理想差一點但接近；講義寫成「random 順序的高度大約是理想的兩倍」（講義 p1）。
   - **這種情況常見嗎？** 很常見：timestamp、照字母排的單字，很多資料「本來就幾乎排好」，直接倒進 BST 就會得到很差的效能（[00:11:08]–[00:12:00]）。

2. **為什麼 order of magnitude 重要**（[00:12:00]–[00:22:03]）
   - 假設每一步 1 ns：
     | n | log₂ n | n log n | n² | n² 步要多久 |
     |---|---|---|---|---|
     | 10 | 3.3 | 33 | 100 | 0.1 µs |
     | 1,000 | | | 10⁶ | 1 ms |
     | 1,000,000 | | 約 2 × 10⁷ | 10¹² | **1,000 秒 ≈ 17 分鐘** |
   - 同樣 n = 10⁶，如果只要 n 步就是 1 ms。**1 ms vs 17 分鐘**，這就是為什麼要數步數（[00:20:04]–[00:22:03]）。
   - 老師現場換算單位時講亂了（nano / micro / milli，[00:18:05]–[00:19:02]），結論是對的：10¹² × 10⁻⁹ s = 1,000 s。

3. **範例樹是不是 balanced？**（[00:23:03]–[00:28:01]）
   - 沿用 Class 7/8 的範例樹（insert 順序 8, 3, 10, 1, 6, 14, 4, 7, 13）：
     ```
             8
           /   \
          3     10
         / \      \
        1   6      14
           / \    /
          4   7  13
     ```
   - 投票結果 thumbs up 比 thumbs down 多，很多人沒投；老師說這題難，因為還沒定義「balanced」（[00:24:01]–[00:25:01]）。同學提到的判斷方式：高度是否接近 log₂ n、左右深度是否相等、能不能更好（[00:25:01]–[00:26:06]）。
   - 老師的重點：**node 10 沒有 left child，但 right child 14 底下還有 13**，至少這一塊不平衡（[00:26:06]–[00:27:05]）。

4. **讓 BST 保持平衡的三種做法**（[00:28:01]–[00:37:04]）
   - (1) **先 shuffle input 再插入**：只有資料一開始全部在手上才行，**串流進來的資料沒辦法 shuffle**；而且可能 shuffle 得很不幸（剛好變成 sorted），**沒有任何保證**（[00:34:05]–[00:36:08]）。
   - (2) **樹看起來很糟時整棵 rebuild**：rebuild 要 O(n)，很貴，和 array 滿了要 resize 是同一種問題；而且還得先定義什麼叫「糟」（[00:30:00]、[00:36:08]）。講義補充：如果常常 rebuild，花的比省的多（講義 p1）。
   - (3) **邊插入邊修（repair as we go）**：每次 insert 後檢查往上的 parents，不平衡就修 → 這就是 AVL（[00:30:00]、[00:36:08]–[00:37:04]）。
   - Rudy 的觀察：最平衡的樹 root 會是整個範圍的中間值（例如 7 或 8）（[00:33:01]–[00:34:05]），老師說要記住這點。

5. **Visualgo 示範：BST vs AVL**（[00:37:04]–[00:49:02]）
   - 用同一串值分別建 BST 和 AVL。AVL 在插入過程中**一直在換 root**，靠 rotation 把中間值往上推（[00:41:26]–[00:43:01]、[00:46:00]）。
   - BST 的第一個值永遠是 root、不會再移動；老師示範先插 1，樹就一路往右歪（[00:44:08]–[00:46:00]）。
   - Visualgo 的 pseudocode：insert → 檢查 balance factor → 依 4 種 case 做 rotate left / right（[00:46:00]–[00:47:02]）。search 成本仍然由高度決定，但 AVL 的高度接近 log n，**不可能退化成 n**（[00:48:10]）。
   - **Visualgo 連結在 Canvas 的 resources 區**，老師很推薦，每種資料結構都有視覺化（[01:15:06]）。

6. **Balance factor**（[00:49:02]–[00:58:05]）
   - 定義：**balance factor(node) = height(left subtree) − height(right subtree)**（[00:50:05]）。
   - 高度慣例：**單一 node 高度 0，空樹高度 −1**（休息後老師特別更正，[00:57:05]；講義 p2）。
   - 範例樹：8 → 0（左右高度都是 2；老師先寫成 3 再改正，[00:51:22]–[00:53:09]）；3 → −1（左 0、右 1）；14 → +1（= 0 − (−1)）；10 → **−2**（= −1 − 1）（[00:52:00]–[00:54:00]、[00:57:05]）。講義另外列 6 → 0、leaves → 0（講義 p2）。

7. **AVL tree 的定義**（[00:58:05]–[01:02:06]）
   - **AVL tree 是一種 binary search tree，每個 node 的 balance factor 都是 −1、0 或 1**（[01:00:13]）。
   - 範例樹因為 node 10 是 −2，**不是 AVL**（[01:01:02]）。
   - 講義補充：insert 之後只有「新 leaf 到 root 這條路徑上」的 node 高度可能改變，所以只要從下往上檢查這些 node（講義 p2）。

8. **Rotation：修復的動作**（[01:02:06]–[01:13:05]）
   - **Right rotation at y**（y 太偏左）：y 的 left child x 升上來當這個 subtree 的 root，y 變成 x 的 right child；x 原本的 right subtree B 沒地方放（x 的右邊已經是 y），就搬過去當 **y 的新 left subtree**（因為 y 的 left 剛好空出來）（[01:06:01]–[01:11:01]）。
     ```
           y                x
          / \              / \
         x   C    ──►     A   y
        / \                  / \
       A   B                B   C
     ```
   - **為什麼還是 BST**：由左到右讀 A, x, B, y, C，rotation 前後一樣（[01:06:01]）。逐項確認：A < x 沒變；y > x 因為 x 原本是 y 的 left child；B > x 因為 B 原本是 x 的 right subtree，且 B < y 因為 B 原本在 y 的 left subtree，所以 B 放在 y 的左邊沒問題（[01:12:02]）。
   - Rotate left 就是鏡像（[01:15:06]）。
   - 講義補充：只改三個 link、不比較不複製，所以是常數時間；每個 node 要存自己的 height，balance factor 才能 O(1) 算出（講義 p3）。code（講義 p3）：
     ```python
     def rotate_right(y):
         x = y['left']
         y['left'] = x['right']   # B moves across
         x['right'] = y           # y drops below x
         update_height(y)         # y is lower now, so fix it first
         update_height(x)
         return x                 # x is the new root of this subtree
     ```
     `rotate_left(x)` 是鏡像。沿用 insert / delete「回傳這個 subtree 的新 root」的寫法。

9. **四種 case 和 height O(log n) 的證明：上課沒講，在講義裡**（[01:13:05]–[01:16:01]）
   - 同學問 rotation 是不是最後一步；老師說還差「什麼時候 rotate、往左還往右」的四種 case，**今天講不完，會寫進 notes，下週一（11/2）簡短講**（[01:13:05]、[01:15:06]）。
   - 講義（下課後補的）內容：
     | Case | 多出來的高度在 | balance factor | 修法 |
     |---|---|---|---|
     | Left-left | left child 的 left subtree | node +2，left child +1（或 0） | 在 node rotate right |
     | Right-right | right child 的 right subtree | node −2，right child −1（或 0） | 在 node rotate left |
     | Left-right | left child 的 right subtree | node +2，left child −1 | 先在 left child rotate left，再在 node rotate right |
     | Right-left | right child 的 left subtree | node −2，right child +1 | 先在 right child rotate right，再在 node rotate left |

     口訣：**多出來的高度在外側就轉一次；在內側就先轉 child 把它變成外側**。Left-right 只轉一次會變成往另一邊歪（balance factor −2），沒解決（講義 p4–p5）。
   - 插入 3,2,1 / 1,2,3 / 3,1,2 / 1,3,2 四種順序，最後都是 2 為 root、1 和 3 為 children（講義 p5）。
   - 範例樹改用 AVL 插入：插到 13 時 node 10 是 −2、right child 14 是 +1 → right-left case：在 14 rotate right，再在 10 rotate left，13 變成 10 和 14 的 parent；pre-order `8 3 1 6 4 7 13 10 14`，高度仍是 3，但每個 node 都平衡（講義 p5）。
   - Insert 後最多只需要一次修復（single 或 double rotation）；**delete 可能要在好幾層修**（講義 p5）。
   - **Height O(log n)**：N(h) = 高度 h 的 AVL tree 最少的 node 數，N(0)=1、N(1)=2、**N(h) = 1 + N(h−1) + N(h−2)** → 1, 2, 4, 7, 12, 20, 33, 54, 88。因為 N(h) > 2·N(h−2)，每兩層至少翻倍，n ≥ 2^(h/2)，所以 **h ≤ 2 log₂ n**；實際成長像 Fibonacci（約 1.6 倍/層），更緊的 bound 約 1.44 log₂ n。100 萬個值的 AVL 最高 27 層（完美樹 19、chain 999,999），search / insert / delete 在 worst case 都是 O(log n)（講義 p5–p6）。

10. **Asymptotic analysis（老師說是她最喜歡的內容）**（[01:16:01]–[01:26:02]）
    - asymptotic analysis 就是大家說的 Big O，本質是**用數學描述函數的成長（characterizing the growth of functions）**（[01:17:03]–[01:19:16]）。
    - 和程式的關係：如果能把一個 function 的 **number of operations 寫成 input size n 的函數**，就能描述它的成長，進而比較兩個演算法的 runtime（[01:21:02]–[01:25:05]）。
    - 為什麼數 operations 而不是秒數：秒數取決於硬體；週一數的是 BST search 的 comparisons 次數（[01:23:11]–[01:24:05]）。老師說她會用 algorithm 指程式、用 function 指數學（[01:25:05]）。

11. **Big O 的正式定義和例子**（[01:26:02]–[01:42:03]）
    - **f(n) = O(g(n))：存在 c > 0 和 n₀，使得對所有 n ≥ n₀，f(n) ≤ c·g(n)**（[01:27:17]）。意思是 f 長得不比 g 快，g 是上界（[01:28:07]、[01:40:02]）。
    - 例：f(n) = 3n² + 5n + 2，g(n) = n²（[01:29:01]–[01:30:00]）。
      - c = 3：3n² + 5n + 2 ≤ 3n² ⇔ 5n + 2 ≤ 0，n > 0 時不成立（[01:33:11]–[01:34:02]）。
      - c = 4：n ≥ 6 之後成立（[01:36:02]）。n = 3：27 + 15 + 2 = 44 > 36，不成立（[01:37:02]）；n = 7：兩邊各減 3·49，剩 37 ≤ 49，成立（[01:39:00]）。所以 c = 4、n₀ = 6。
      - 講義補充：n = 5 時 f(5) = 102 > 4·25 = 100，這就是為什麼需要 n₀；n ≥ 6 時 5n + 2 ≤ 6n ≤ n²（講義 p6–p7）。
    - 連到 code：`for i in range(n): print(...)` 跑 n 次，f(n) = n，所以 O(n)；平常寫的「O(n)」就是「f(n) = O(n)」的簡寫（[01:41:03]–[01:42:03]）。

12. **Θ 和 Ω；業界的 Big O 其實是 Θ**（[01:42:03]–[01:53:02]）
    - **O：g 是 f 的上界**；**Θ：g 和 f 大約相等，以同樣速度成長（tight bound）**；**Ω：g 是 f 的下界**（[01:43:02]–[01:44:04]）。
    - 老師自稱很在意（pedantic）：業界和面試說「Big O」時，幾乎都是指 Θ（[01:44:04]–[01:45:08]）。她說大概不會硬性要求，但要知道技術上兩者不同（[01:44:04]）。
    - 例：n² 的演算法說它是 O(n³)、O(n⁴)、O(n⁶) **技術上都對**，但面試時會被當成錯，因為對方要的是 tight bound（[01:51:01]–[01:52:01]）。
    - 為什麼有三種：asymptotic analysis 原本是數學用來**比較兩個函數**的工具，就像數字的 <、=、>；早期很多 computer scientist 是數學出身，把它拿來比較演算法的 operation 數（[01:49:06]–[01:51:01]）。理論 CS 會在意上界和下界的差別（[01:52:01]）。
    - **捷徑**：**丟掉低次項，再丟掉係數**。3n² + 5n + 2 → n²；兩次雙層迴圈加一個單層迴圈加 5 個 operation，2n² + n + 5 → n²（[01:46:01]–[01:47:02]）。
    - Ethan 確認：f(n) 是實際的步數，g(n) 是它的 bound；operations 大致就是被執行的 code 行數（[01:47:02]–[01:48:11]）。
    - 講義補充：log 的底數不重要（log₂ n 和 ln n 只差常數倍）；成長順序 1 < log n < n < n log n < n² < n³ < 2ⁿ；**O 不等於 worst case**：O 描述的是函數怎麼成長，那個函數可以是 best / worst / average case 的 runtime。例如 plain BST search 的 worst case 是 Θ(n)，random 插入順序的 average case 是 Θ(log n)，AVL 的 worst case 是 Θ(log n)（講義 p7）。

## 名詞解釋

- **Balanced tree**：每個 node 左右兩邊的高度差不多，整棵樹的高度接近 log₂ n。今天先用 AVL 的規則把它定義清楚。
- **Height（高度）**：從 node 到 leaf 最長路徑的邊數。**單一 node = 0，空樹 = −1**（[00:57:05]）。
- **Balance factor**：height(left subtree) − height(right subtree)。正的代表偏左、負的代表偏右（[00:50:05]）。
- **AVL tree**：每個 node 的 balance factor 都在 {−1, 0, 1} 的 BST（[01:00:13]）。名字來自 Adelson-Velsky 和 Landis（課堂沒提，補充）。
- **Rotation（right / left）**：把某個 node 的 child 升上來當 parent 的局部重排，只改三個 link，in-order 順序不變，所以 BST 性質不變（[01:06:01]；講義 p3）。
- **Single / double rotation**：外側不平衡（left-left、right-right）轉一次；內側不平衡（left-right、right-left）先轉 child 再轉 node（講義 p4–p5）。
- **N(h)**：高度 h 的 AVL tree 最少有幾個 node，N(h) = 1 + N(h−1) + N(h−2)（講義 p5）。
- **Asymptotic analysis**：描述函數在 n 很大時怎麼成長，忽略常數倍和小 n 的行為（[01:18:06]；講義 p6）。
- **Big O（O）**：上界。f = O(g) ⇔ ∃ c > 0、n₀，∀ n ≥ n₀，f(n) ≤ c·g(n)（[01:27:17]）。
- **Big Omega（Ω）**：下界。f(n) ≥ c·g(n)，n ≥ n₀（[01:43:02]；講義 p7）。
- **Big Theta（Θ）**：tight bound，O 和 Ω 同時成立：c₁·g(n) ≤ f(n) ≤ c₂·g(n)（[01:43:02]；講義 p7）。
- **n₀**：從哪個 n 開始不等式成立；小 n 不算數（講義 p7）。
- **Number of operations**：把演算法執行的步數（comparisons、被執行的 code 行數）寫成 n 的函數，就是 f(n)（[01:24:05]、[01:48:11]）。
- **Visualgo**：資料結構動畫網站，連結在 Canvas resources（[01:15:06]）。

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

- [00:09:01] sorted 插入的 BST 平均要 n/2 步才找得到，等於在 list 上找。
- [00:12:00] 很多真實資料本來就接近排序（timestamp、照字母的單字），直接放進 BST 效能會很差，所以這個問題真的重要。
- [00:20:04]–[00:22:03] n = 10⁶ 時，n² 步要約 17 分鐘，n 步只要 1 ms；這就是為什麼要數步數。
- [00:27:05] 不管整棵樹算不算平衡，至少 node 10 那一塊明顯不平衡。
- [00:34:05]–[00:36:08] shuffle 只在資料一開始全部到齊時可行，而且可能 shuffle 得不巧，「doesn't promise us anything」。
- [00:36:08] rebuild 很貴，跟 array 滿了要 resize 是同一種問題。
- [00:44:08]–[00:45:04] BST 的第一個值會一直是 root；AVL 會隨插入一直換 root。
- [00:48:10] AVL 的 search 仍受高度限制，但高度接近 log n，不會出現高度 n 的最壞情況。
- [00:57:05] 休息後更正：單一 node 高度 0、空樹高度 −1；14 的 balance factor 是 0 − (−1) = 1。
- [01:00:13] AVL 定義：每個 node 的 balance factor 是 −1、0 或 1。
- [01:06:01] rotation 前後由左到右讀都是 A, x, B, y, C，順序沒變。
- [01:12:02] B 原本在 x 右邊、y 左邊，所以放到 y 的 left 仍然符合 BST 規則。
- [01:13:05]、[01:15:06] 四種 case 今天來不及，會寫進 Canvas notes，**11/2（一）簡短講**。
- [01:15:06] 推薦 Visualgo（Canvas resources），每種資料結構都有動畫。
- [01:18:06] 她會講數學定義，但不要被嚇到，有 cheat sheet 和大方向可以帶走。
- [01:23:11]–[01:24:05] 數 comparisons 而不是秒數，才不會受硬體影響。
- [01:27:17] Big O 的正式定義（∃ c > 0、n₀，f(n) ≤ c·g(n) for all n ≥ n₀）。
- [01:34:02]–[01:36:02] 找 c 的過程：c = 3 不行，c = 4 從 n ≥ 6 起成立。
- [01:39:00] 這些推導不用每次都做，但定義是背後的意義。
- [01:44:04] 她「very pedantic」：大家說 O(n) 常常其實是 Θ(n)；她大概不會硬性要求，但要知道差別。
- [01:46:01] 捷徑：drop the lower order terms，再 drop the coefficient。
- [01:52:01] 面試時說 n² 演算法是 O(n⁶) 技術上對，但會被當成錯，對方要的是 tight bound。
- [01:53:02] 下週會再多做幾個例子；[01:54:03] notes 會在 Canvas 上補完（已補：outline 頁尾時間 10/28 9:01 PM）。

## 和作業 / 考試的關聯

- **A4 Bug Hunt：11/1（日）11:59 PM PST 截止**（`due_at` 2026-11-02T07:59:59Z，DST 結束當天），目前 unsubmitted。今天課上沒提 A4。
- **A5 BSTs and AVLs：11/22（日）11:59 PM PST**。今天的 balance factor、rotation、四種 case 就是 A5 AVL 部分的內容；講義寫「今天沒有 AVL insert code 要寫」（講義 p1），但已經給了 `rotate_right` / `rotate_left` 和「回傳新 subtree root」的寫法（講義 p3），AVL 節點要存 `height`。週一老師建議先做 A5 Part 1（BST）準備 midterm。
- **Midterm：11/9（一）4:30–6:30 PM PST，實體紙筆，Moore 220**。週一說過 11/2 那週會講 midterm 範圍；四種 case 也會在 11/2 講。可能考的題型可以直接拿講義的 Check Your Knowledge 練（講義 p8–p9 有答案）：
  - 判斷是不是 AVL、算 balance factor；
  - 為什麼 rotation 不會破壞 BST 順序；
  - node +2、left child −1 是哪個 case、怎麼修（left-right：先在 left child rotate left，再在 node rotate right）；
  - N(h) 表、為什麼 N(h) > 2·N(h−2) 推出 O(log n)；例如 N(6) = 33，10,000 個 node 的 AVL 最高 17 層（N(17) = 6,764、N(18) = 10,945）；
  - 找 c 和 n₀ 證明 2n + 10 = O(n)（c = 3、n₀ = 10）；
  - 「O 等於 worst case」錯在哪；
  - 迴圈的 Θ：雙層 n·n → Θ(n²)；`while i > 1: i //= 2` → Θ(log n)；外層 n、內層 j 倍增 → Θ(n log n)；`for j in range(i)` → n(n−1)/2 → Θ(n²)；2ⁿ⁺¹ = O(2ⁿ) 對；2²ⁿ = O(2ⁿ) 錯（4ⁿ/2ⁿ = 2ⁿ 無界）；3n² + 5n + 2 不是 O(n)。
- 老師 [01:44:04] 說 Θ / Ω 的區分「大概不會 hold you to」，但講義的 CYK 有要求用 Θ 分類，考前要確認。

## 還要釐清的問題

1. **四種 case 和 N(h) 證明上課沒講**，只在下課後補的 outline 裡（講義 p4–p6）。11/2 老師說會「brief」帶過；這些算不算 midterm 範圍？11/2 講 midterm 範圍時要確認。
2. **Midterm 要不要分 O / Θ / Ω？** 老師口頭說大概不會硬性要求（[01:44:04]），但講義的練習題全部要求用 Θ（講義 p7–p8）。
3. **「O 不等於 worst case」**：老師的講義明確這樣說（講義 p7），Grokking 第 1 版 Ch 1 卻寫「Big O establishes a worst-case run time」。依 BOOTSTRAP §3 以老師為準；考試照老師的定義答。
4. **A5 要寫到多完整的 AVL？** 講義說今天不用寫 AVL insert，A5 名稱是「BSTs and AVLs」，需要看 A5 說明是否要求 delete 後的 rebalance（講義 p5 說 delete 可能要在多層修復）。
5. timing demo 的數字：上課跑出 0.009 s vs 超過 1 s（[00:06:04]），講義寫 0.005 s vs 0.6 s（講義 p1）。以上課為準；只是機器差異，不影響結論。
6. 講義寫 random 插入的高度「大約是理想的兩倍」（講義 p1），老師的實驗表 1,000 個值高度約 20（log₂ 1000 ≈ 10），一致；但平均 search 步數只有 11.7，比高度少很多，因為平均深度比最大深度小。如果考試問「random BST 的 search 成本」，要分清楚是高度（worst）還是平均。
