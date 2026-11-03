# DSA Class 10 — 2026-11-02（週一，Mod 4 AVL, Asymptotic Analysis：Big-O 定義套到程式碼、upper bound vs tight bound、balance factor 練習、rotation、AVL 四種 case）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，1151 cues，00:06:44–01:52:40，約 106 分鐘，DeliveryID `5414766c-8f41-465d-9a81-b4f70039291b`，Canvas Module 4 item 27648955「Mod 4 AVL, Asymptotic Analysis [Mon, Class 10]」）、slides：**這堂沒有新講義**。老師下課前說今天沒有新 notes，用的是上週那份（[01:51:04]），Module 4 也只有 Class 9 的兩個檔案。`slides.txt` 是 11/3 重新抽出的 `EE590a_Class_Wed_AVL_and_asymptotics_outline_students.pdf`（file 155413878，9 頁），跟 Class 9 的版本逐字相同。下面標「講義 pN」的就是這份；填空講義（file 155378415）見 `../2026-10-28/slides.txt`。
>
> 閱讀：課程沒有指定本堂章節（Module 5 的 Reading 是 Ch 5 Hashtables，屬於下一個 module）。下面是自行對照的：Grokking Algorithms Ch 1（Big O、binary search 的 log₂ n）。Grokking 第 1 版沒有 AVL，第 2 版 Ch 8 "Balanced trees" 有 AVL / rotation，可以用那章補。逐字稿是自動產生，專有名詞可能聽錯。
>
> 字幕從 00:06:44 才開始，第一句是 Panopto 塞進來的「該逐字稿自動產生…」。老師 [00:08:26] 說 4:30 開課，休息 [00:58:01]–[00:59:43]（約 10 分鐘），[01:52:40] 結束。
>
> 常見誤聽對照：Aval / ADL / ABL / Avel → AVL；Benth time / end times → n times；Zen squared → n squared；and Cube → n cubed；Constantine → constant (time)；sweet / AIC → C / a C；Recultism and not → ≥ n₀；type bound / takedown → tight bound；Prop 0 → `pop(0)`；Ovin / My oven → O(n)；rate heavy → right heavy；substrate → subtree；bounced / Boom → balanced；Tend the parent → 10 the parent；plaus → （聽不出來）；Media → （聽不出來）。人名：Gus（開場）、Beth（[00:32:00] 提問）、Alan（[00:51:02] 問大家是不是真的手算）、Rudy（[01:25:02] 糾正 0 − 2 = −2）、Natalie（[01:31:05] 點名）。

## 重點摘要

1. **開場：這週和下週的安排**（[00:09:01]–[00:11:01]）
   - 今天：把 asymptotic analysis 跟實際看程式碼連起來（上週只給了定義），然後把 AVL 收尾。
   - **下週一 11/9 midterm，就在這間教室，實體紙筆**。要提早計畫、準時到。
   - **這週三 11/4 複習**：列 midterm 範圍、回答問題、做題目；看狀況可能開始講 heaps，讓 midterm 之後接得上。
   - **下週三 11/11 沒課**（學校放假，[00:10:03]）。

2. **Big-O 的定義怎麼對到程式碼**（[00:12:01]–[00:25:28]）
   - 老師重寫定義：f(n) = O(g(n))，如果存在 C 和 n₀，使得 n ≥ n₀ 時 f(n) ≤ C·g(n)（[00:13:00]–[00:14:02]）。
   - **f(n)** = 一段程式碼執行的「operation 數」（以 n 表示）；**g(n)** 是我們拿來比較的那幾個常見函數：1、log n、n、n log n、n²、n³…（[00:14:02]–[00:16:00]）。
   - 例 1：雙層 `for i in range(n): for j in range(n): count += 1`，像在數方陣的格子數。數 `count += 1` 跑幾次：n × n × 1 → **f(n) = n²**（[00:18:02]–[00:21:04]）。
     - g(n) = 1：n² ≤ C·1 對所有夠大的 n 成立嗎？C 取多大（例如一百萬）n² 最後都會超過 → **不是 O(1)**（[00:23:03]–[00:24:04]）。
     - g(n) = n³：C = 1 或 2 都行 → **n² 是 O(n³)**，這是真的敘述（[00:26:02]–[00:29:00]）。
     - g(n) = n²：C = 1 就相等 → n² 是 O(n²)（[00:29:00]–[00:30:06]）。
   - 重點：asymptotic analysis 是在**比較兩個函數的成長速度**（[00:30:06]）。

3. **例 2：內層迴圈依賴外層（三角形迴圈）**（[00:34:20]–[00:40:05]）
   - 外層跑 n 次；內層第一次 1、第二次 2… 最多 n。老師說這題「通常會有人吵」（[00:35:02]）。
   - 內層**最壞是 n**，也就是 upper bound 是 n（[00:36:00]–[00:37:02]），所以 n × n → n²。
   - 這就是定義裡用 ≤ 的原因：Big-O 是 upper bound，**比它大的函數也都成立**。5 < 10，5 也 < 20、< 100（[00:38:01]–[00:39:07]）。O(n) 的東西也是 O(n²)、O(n³)、O(n¹⁵)。

4. **例 3：f(n) = 3n² + 5n + 2**（[00:41:01]–[00:48:04]，講義 p6–p7 同一題）
   - 老師隨手寫了對應的假程式：三次 n×n 迴圈 → 3n²、五次 n 迴圈 → 5n、兩個 print → 2（[00:42:07]–[00:43:00]）。
   - 是 O(n) 嗎？找不到 C 讓 3n² + 5n + 2 ≤ C·n → **不是**（[00:44:06]）。
   - 是 O(n²) 嗎？取 **C = 100**，n 夠大就成立 → **是**（[00:45:02]–[00:46:05]）。講義的證明用 c = 4、n₀ = 6（講義 p7）；兩者都對，只要「存在」一組就好。
   - **實務捷徑**：**drop lower order terms + ignore the constant（coefficient）** → O(n²)（[00:47:00]–[00:48:04]）。熟了以後直接看程式：常數的部分不管，n 的迴圈被 n² 的迴圈蓋過，「the n² dominates」（[00:49:01]）。

5. **語言實作細節藏在一行程式裡**（[00:52:01]–[00:54:00]）
   - Python list：`my_list.pop()` 是 **O(1)**；`my_list.pop(0)` **不是 O(1)**，是 O(n)，因為 list 底層是 array，拿掉 index 0 要把後面全部往前搬。
   - 兩行看起來幾乎一樣，runtime 卻不同。老師說這是「prepare and review for next week」（[00:53:00]），midterm 可能考。

6. **Big-O 是 upper bound，不是 tight bound**（[00:55:00]–[00:58:01]）
   - n² 的程式說它是 O(n³) **形式上是對的**，但業界很多人把 Big-O 當 tight bound 用，聽到 O(n³) 會有意見。
   - 講義有 **Big Θ（tight bound）** 和 **Big Ω（lower bound）** 的定義（講義 p7），老師說上課沒花時間講，因為現在很少聽到（[00:57:00]）。
   - 老師的期望：知道兩者的差別；面試時不要耍聰明說「其實是 n³」，但可以表現出你知道 upper bound 和 tight bound 的差別（[00:58:01]）。

7. **AVL 回顧：BST 的問題**（[01:00:02]–[01:09:04]）
   - BST：左 subtree 全部比 node 小，右 subtree 全部比 node 大；每一步砍掉一半 → 找得快（[01:02:00]）。
   - 依序插入 1, 2, 3, 4, 5 → 一條鏈，跟 list 一樣，search 範圍完全沒縮小（[01:03:06]–[01:04:11]）。
   - Lookup 的 runtime 是 O(h)。**寫 O(n) 時一定要講清楚 n 是什麼**：tree 的 n 預設是 node 數，所以寫 O(n) 而 n 指 height 時要明說，或直接寫 O(h)（[01:06:05]）。
   - 平衡的 BST 高度是 log n；長歪的 BST 可能高到 n（[01:08:02]）。
   - AVL 的目的：建樹的過程中維持平衡，而且**不用每次插入都重建整棵樹**（[01:09:04]）。

8. **定義：height 與 balance factor**（[01:10:00]–[01:14:01]，講義 p2）
   - Height convention：**single node = 0、empty tree = −1**；其他是到 leaf 的步數（數 **edges**，不數 nodes，[01:25:02]）。
   - **Balance factor = height(left subtree) − height(right subtree)**。
   - **正 = left heavy，負 = right heavy**（[01:13:02]）。
   - **AVL tree = 每個 node 的 balance factor 都是 −1、0、1 的 BST**（[01:13:02]–[01:14:01]）。

9. **課堂練習：三棵樹算 balance factor**（[01:14:01]–[01:26:11]）
   ```
   (A)      20            (B)       20           (C)   20
          /    \                  /    \               /  \
        10      30              10      30           10    ?（右 subtree 高 2）
       /  \       \            /  \
      5    15      35         5    15
                             /
                            3
   ```
   - (A)：5、15、35 都是 0；30 = −1 − 0 = **−1**；10 = 0；20 = 1 − 1 = 0 → **是 AVL**（[01:15:05]–[01:18:01]）。
   - (B)：3 = 0；5 = 0 − (−1) = **1**；10 = 1 − 0 = 1；30 = 0；**20 = 2 − 0 = +2** → 不是 AVL，left heavy（[01:19:13]–[01:23:01]）。
   - (C)：左邊 10 是 leaf（高 0），右 subtree 高 2 → **20 = 0 − 2 = −2**，不是 AVL。老師板書先寫成「2」，Rudy 糾正是 −2（[01:24:00]–[01:26:11]）。右 subtree 的確切形狀逐字稿聽不出來。
   - 老師提醒：寫程式時看不到整棵樹，要算每條路徑再取 **max**（[01:22:00]）。

10. **插入後只需檢查新 node 到 root 的路徑**（[01:26:11]–[01:29:07]，講義 p2）
    - 插入只會改變這條路徑上 node 的高度，所以只有它們可能壞掉。
    - 以 (B) 為例：假設最後插入的是 3，往上看 5（+1，OK）、10（+1，OK）、**20（+2，壞了）** → 在 20 rotate。

11. **Rotation 實作示範**（[01:29:07]–[01:38:05]，講義 p2–p3）
    - **Right rotation at 20**（樹 (B) 去掉 3）：10 升上來當 root；20 變成 10 的右 child；10 原本的右 child **15 改掛到 20 的左邊**；30 還在 20 右邊（[01:31:05]–[01:32:01]）。
      ```
            20                 10
           /  \               /  \
         10    30    →       5    20
        /  \                     /  \
       5    15                 15    30
      ```
    - 右轉後左邊變矮、右邊補上（[01:34:09]）。
    - **Left rotation**：把右 child 拉上來，它原本的**左 child** 改掛到被拉下去那個 node 的**右邊**（[01:35:38]–[01:36:00]）。課堂例子是 root 20、右 child 30（底下有 40），轉完 30 當 root、20 當它的左 child。老師畫的時候卡了一下又重畫（[01:36:00]–[01:38:05]），10、5 最後的位置逐字稿講不清楚，以講義 p3 的 `rotate_left` 為準。
    - 老師提到**有一份作業會大量練習 rotation**（[01:38:05]），就是 A5。

12. **四種 case：轉幾次、往哪轉**（[01:39:02]–[01:42:06]，講義 p4 的表）
    | Case | broken node | 看「heavy side 的 child」 | 修法 |
    |---|---|---|---|
    | Left-left | +2 | left child +1（或 0） | 在 node **rotate right** |
    | Right-right | −2 | right child −1（或 0） | 在 node **rotate left** |
    | Left-right | +2 | left child −1 | 先在 **left child rotate left**，再在 node **rotate right** |
    | Right-left | −2 | right child +1 | 先在 **right child rotate right**，再在 node **rotate left** |
    - 老師板書的判斷欄是「child on heavy side」（[01:45:03]）：broken node 是 +2 就看左 child，−2 就看右 child。
    - LL 和 RR 互為鏡像，LR 和 RL 也是（[01:41:00]）。
    - 壞掉的 node 一定是 **+2 或 −2**，因為每次插入都會馬上修，不會讓它變更糟（[01:41:00]）。

13. **兩個完整例子**（[01:42:06]–[01:49:02]，講義 p4–p5 同樣的例子）
    - **插入 3, 2, 1（left-left）**：1 = 0、2 = 0 − (−1) = +1、3 = 1 − (−1) = **+2** → 左 child +1 → 在 3 rotate right → 2 在上，1、3 兩邊（[01:42:06]–[01:46:03]）。
    - **插入 3, 1, 2（left-right）**：2 = 0、1 = −1 − 0 = **−1**、3 = **+2** → 左 child −1 → 先在 1 rotate left（2 上來、1 下去），再在 3 rotate right（2 上來、3 下去）→ 一樣得到 2 在上，1、3 兩邊（[01:47:00]–[01:49:02]）。

14. **收尾：midterm 資訊**（[01:49:02]–[01:51:04]）
    - 週三帶問題來；老師沒有範例考卷，但可以從已公布 notes 的 **Check Your Knowledge** 題目找練習，老師也會出一些練習題（[01:50:01]）。
    - 今晚會在 Piazza 發提醒公告（[01:50:01]）。
    - **考試給滿兩小時，但題目設計成一小時寫得完**（[01:50:01]–[01:51:04]）。
    - **範圍到今天這堂為止，AVL 全部都算**；週三如果再講 AVL 也算，但今天以後的新內容不考（[01:51:04]）。

## 名詞解釋

- **Asymptotic analysis**：比較兩個函數在 n → ∞ 時的成長速度，忽略常數倍和小 n 的行為。用來描述演算法的效能隨 input size 怎麼變。
- **f(n)**：某段程式碼執行的 operation 數（例如某一行被執行幾次），以 n 表示。
- **g(n)**：拿來比較的參考函數，常用的有 1、log n、n、n log n、n²、n³。
- **Big-O（O）**：f(n) = O(g(n)) ⇔ 存在 c > 0 和 n₀，使得 n ≥ n₀ 時 f(n) ≤ c·g(n)。是 **upper bound**。
- **Big-Θ（Theta）**：tight bound，f 同時是 O(g) 和 Ω(g)（講義 p7）。
- **Big-Ω（Omega）**：lower bound，f(n) ≥ c·g(n)（講義 p7）。
- **Drop lower order terms / ignore constants**：從 f(n) 推 Big-O 的捷徑，例如 3n² + 5n + 2 → O(n²)。
- **Dominate**：最高次的項壓過其他項，例如 n² 的迴圈蓋過 n 的迴圈。
- **`list.pop()` vs `list.pop(0)`**：Python list 底層是 array，`pop()` 拿最後一個是 O(1)，`pop(0)` 要把後面的元素往前搬，是 O(n)。
- **Height（AVL 慣例）**：single node = 0、empty tree = −1；其他是從該 node 往下到最遠 leaf 經過的 **edge 數**。
- **Balance factor**：height(left) − height(right)。正 = left heavy，負 = right heavy。
- **AVL tree**：每個 node 的 balance factor 都在 {−1, 0, 1} 的 BST。高度 O(log n)（講義 p5–p6，上課沒推導）。
- **Rotation（right / left）**：把一個 child 拉到 parent 的位置，child 的「內側」subtree 改掛到被拉下去的 node 上。只改三個 link，inorder 順序不變，所以還是 BST（講義 p3）。
- **LL / RR / LR / RL case**：插入後失衡的四種形狀，看 broken node（±2）和它 heavy side child 的 balance factor 決定轉一次還是兩次。
- **lg**：老師說 `lg` 表示 log base 2（[01:08:02]）。

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

- [00:09:01] 下週一 midterm，在這間教室，實體紙筆。
- [00:10:03] 週三 11/4 複習（範圍、問題、題目），可能開始講 heaps；**11/11 週三放假沒課**。
- [00:13:00]–[00:14:02] 重寫 Big-O 的定義：存在 C、n₀，n ≥ n₀ 時 f(n) ≤ C·g(n)。
- [00:14:02] f(n) 是描述演算法 operation 數的函數。
- [00:28:05] C 必須是常數而且是正的，不能用負數耍花招（老師也說「has to be an integer」，跟講義的 c > 0 不同，見最後一節）。
- [00:30:06] Asymptotic analysis 是在比較函數的成長速度。
- [00:32:00] 定義看起來比實際做的事複雜很多；要知道定義，但實務上怎麼用更重要。
- [00:38:01] Big-O 是 upper bound，所以定義裡用 ≤；O(n) 的東西也是 O(n²)、O(n³)。
- [00:46:05]–[00:47:00] 「the thing that you need in your back pocket」：drop lower order terms、忽略常數。
- [00:49:01] 熟練之後直接看迴圈：最大的那層 dominates。
- [00:51:02] Alan 問大家是不是真的手算 f(n)：通常不會算到這麼細，直接找出最重的那段程式。
- [00:52:01]–[00:53:00] `pop()` 是 O(1)、`pop(0)` 不是；**知道語言實作細節**才是職場上的難處，也是下週要複習的東西。
- [00:56:04]–[00:57:00] Big-O **不是 tight bound**，是 upper bound；業界常把它當 tight bound。
- [00:58:01] 面試時不要耍聰明說「其實是 n³」，但要表現出你懂兩者的差別。
- [01:06:05] 寫 O(n) 要講清楚 n 是什麼；tree 的 n 預設是 node 數，高度就寫 O(h) 或明說。
- [01:08:02] 平衡 BST 的高度是 log n。
- [01:11:02] Height convention：single node 0、empty tree −1。
- [01:13:02] Balance factor 正 = left heavy、負 = right heavy；AVL = 每個 node 的 balance factor 都在 −1、0、1。
- [01:22:00] 寫程式時看不到整棵樹，要算每條路徑取 max。
- [01:25:02] Height 數的是 edge，不是 node。
- [01:27:06]–[01:28:01] 插入只影響新 node 到 root 那條路徑，只需檢查那些 node。
- [01:38:05] Rotation 要練習；有一份作業會大量練。
- [01:41:00] 壞掉的 node 一定是 ±2，因為每次都在變更糟之前修好。
- [01:45:03] 四種 case 的判斷：看 broken node 的正負，再看 heavy side 那個 child。
- [01:50:01] 沒有範例考卷，用 notes 裡的 Check Your Knowledge 練；週三會出練習題。
- [01:50:01] 考試給滿兩小時，但設計成一小時寫得完。
- [01:51:04] 範圍到今天為止，AVL 全部都考。

## 和作業 / 考試的關聯

- **Midterm：11/9（一）4:30–6:30 PM PST，實體紙筆，Moore 220**（`dsa/assignments.md`）。老師今天確認：
  - 範圍到 11/2 這堂為止，**AVL 全部都考**（[01:51:04]）；
  - 給兩小時、設計成一小時寫得完（[01:50:01]）；
  - 練習題：notes 的 Check Your Knowledge（Class 9 outline 的 CYK 都有答案，講義 p2–p8），週三 11/4 複習課老師會再出題。
  - 可能考的題型（照今天上課的例子）：
    - 從程式碼數 f(n)（雙層迴圈、三角形迴圈）→ 推 Big-O；
    - 用定義判斷 f = O(g) 真偽，找 C、n₀（n² 不是 O(1)、是 O(n³)；3n² + 5n + 2 不是 O(n)、是 O(n²)）；
    - upper bound vs tight bound；
    - `pop()` vs `pop(0)` 這類 Python 實作細節的 runtime；
    - 算 balance factor、判斷是不是 AVL；
    - 給插入順序，判斷是哪個 case、做 rotation（3,2,1 / 3,1,2 / 1,2,3 / 1,3,2，講義 p5 的 CYK）。
- **A5 BSTs and AVLs：11/22（日）11:59 PM PST**，unsubmitted。老師說有作業會大量練 rotation（[01:38:05]），就是 A5。講義 p3 有 `rotate_right` / `rotate_left` 的寫法，node 要存 `height`。
- **A4 Bug Hunt**：已 submitted（11/3 晨報確認），今天課上沒提。
- **週三 11/4 複習課**，**11/11 週三放假**。

## 還要釐清的問題

1. **C 要不要是整數？** 老師說 C「has to be an integer, has to be positive」（[00:28:05]），講義的定義是 c > 0（講義 p6），沒有要求整數。一般教科書也是正實數就好。依 BOOTSTRAP §3 以上課為準，但實際上取整數不會錯，考試寫整數的 C 最保險。
2. **`log n` 的底數**：老師說 `lg` 是 base 2，`log n` 沒寫底數時「assumes base 10」（[01:08:02]）。CS 的習慣通常 log n 就是 log₂ n；在 Big-O 裡底數只差常數倍，不影響答案。考試寫 log₂ n 或 lg n 比較不會有爭議。
3. **N(h) 的 O(log n) 證明算不算 midterm 範圍？** 老師說「AVL trees are fair game」（[01:51:04]），但 N(h) 推導上課沒講過（只在講義 p5–p6）。週三複習時要確認。
4. **Θ / Ω 要不要會？** 今天老師說上課沒花時間講，現在很少聽到（[00:57:00]），上週也說大概不會硬性要求；但講義 p7–p8 的練習全部要求用 Θ 分類。週三要問清楚。
5. **Left rotation 的課堂例子**（[01:36:00]–[01:38:05]）：老師畫錯又重畫，逐字稿聽不出 10、5 最後掛在哪裡（應該在 20 的左邊）。以講義 p3 的 `rotate_left` 為準，可以看錄影 1:36–1:38 確認。
6. **樹 (C) 右 subtree 的形狀**：逐字稿只說右 subtree 高 2，沒說有哪些 node，要看錄影 1:23–1:26。
7. **週三會不會講 heaps？** 老師說看今天的進度決定（[00:10:03]）；結尾說週三做複習（[01:50:01]）。Heaps 是 Module 7（11/16 那週），midterm 不考。
