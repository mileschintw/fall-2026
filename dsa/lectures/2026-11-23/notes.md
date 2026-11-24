# DSA Class 14 — 2026-11-23（週一，Module 5 Hashtables：open addressing vs. chaining、load factor、resize、hash function 的條件、現場寫 chaining hash table）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，1109 cues，00:05:08–01:47:32，約 102 分鐘；session `a0beb1cc-fc97-40b3-b6b6-b50c00308b12`，Panopto 預設標題「EEP 590A: Class Meeting」）。slides：**講義尚未發布**（老師下課前說「I will put my notes up on Canvas」[01:46:10]；11/24 10 AM 查 Canvas，Module 8: Graphs（Week of Nov 23）只有 Overview page 和「Reading: Chapter 7, Djikstra's Algorithm」，這堂課的錄影和講義都還沒掛上去）。這堂是實體課（老師提到「for those in the classroom」[01:24:01]），同時有線上學生；老師在手寫板上畫圖，後半段現場寫 Python。
>
> 閱讀：Canvas Module 5 標的是「Reading: Chapter 5, Hashtables」→ Grokking Algorithms Ch 5（Hash Tables）。Canvas 把這週排成 Module 8 Graphs（Ch 7 Dijkstra），但這堂實際上還在講 hash table，graph 還沒開始（以課堂為準）。open addressing 的細節 Grokking 沒有，可以參考 CLRS Ch 11.4（自行對照）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：Python dicks → Python dicts；ash table / Mesh table / Catch table → hash table；Chani / entertaining approach → chaining approach；Maude / mod → mod（取餘數）；Age of X / H of X / h of x → h(x)；cache function / cache of / Cash of / Ash of → hash function / `hash(...)`；mill terminator → null terminator（linked list 結尾的 None）；weave → read；branch → range（key 的範圍）；Nom buckets / numbuckets → `num_buckets`；MyHC → `my_ht`；Very Ht → `query_ht(...)`（推測）；O of N / O of one → O(n) / O(1)；Gas → Gus（同學名字）；Brian、Gus、Rudy → 同學的名字；Skype → 推測是「Sure」或口誤，無意義。

## 重點摘要

1. **為什麼要 hash table**（[00:06:00]–[00:09:04]）
   - 最大的好處是效率：insert 和 retrieve 平均 O(1)。另一個好處是 key-value 儲存，Python 的 `dict` 就是。
   - O(1) 的來源是 array：知道 index 就能直接跳到那個記憶體位置讀或寫。hash table 的所有設計都是為了「把 key 變成 array index」。

2. **Direct addressing（把 key 直接當 index）**（[00:09:04]–[00:13:02]）
   - 課堂例子：42、12、5、33、7、2、86、10 放進一個 100 格的 array，key 是多少就放第幾格。
   - 優點：走一遍剛好是排序好的。
   - 缺點：(1) 浪費空間，100 格只用 10 格左右；(2) key 被限制在 array 的範圍內，175 放不進去。
   - 解法：在 array 前面加一個 hash function。

3. **Hash function + mod = hash table**（[00:14:01]–[00:17:00]）
   - hash function：任何輸入（string、image、任何資料）進去，出來一個數字；同樣的輸入永遠得到同樣的數字。
   - bucket index = `hash(key) % num_buckets`。mod 很便宜，算完就直接到那個記憶體位置。
   - 「array 本身沒什麼特別，前面加了 hash function 才變成 hash table」（[00:36:09]）。
   - 前半堂為了簡化，hash function 用 identity：h(x) = x（[00:59:05]、[01:05:09]）。

4. **Open addressing（linear probing）**（[00:16:00]–[00:26:10]）
   - 9 個 bucket（mod 9）：42→6、12→3、5→5、33→6 撞到 → 往下一格 7；7→7 撞到 → 8；2→2；86→5 → 5、6、7、8 都滿 → 繞回開頭；10→1。
   - **collision**：兩個 key 算出同一個 bucket。這裡的處理法是「找下一個空格，到底就繞回開頭」。
   - 查詢 86：先到 index 5，不是 → 一路往下找、繞回去才找到。
   - 最壞情況：插入 9、18、27、36、45…（全部 mod 9 = 0），每次都要從 0 一路找空位，insert/read 退化成 O(n)（[00:20:05]–[00:23:04]）。
   - 這種「只有一個 array、沒有其他儲存空間」的做法叫 **open addressing**（[00:25:05]–[00:26:10]），能存的元素上限就是 array 的格數。

5. **Chaining**（[00:27:02]–[00:34:04]）
   - 每個 bucket 放一條 list（linked list 或 Python list），不是只放一個值。
   - 5 個 bucket：42→2、84→4、23→3、11→1、6→1（collision，接在 bucket 1 的 list 後面）。
   - insert：算 bucket（O(1)）→ append 到那條 list（O(1)）。
   - retrieve：算 bucket → 沿著 list 找 key。
   - 沒有容量上限，list 可以一直變長；但 list 太長就不夠快（[00:38:05]–[00:39:07]）。
   - Brian 問 chaining 和 open addressing 不是一樣都要走訪嗎？老師答：除了容量上限之外，很難說哪個一定比較好，是 trade-off；兩者共同的關鍵都是 **collision 的數量**（[00:57:06]–[00:58:06]）。

6. **Load factor α**（[00:41:06]–[00:46:02]）
   - α = 元素個數 / bucket 數，量 hash table 有多滿。
   - open addressing：例子是 8/9，接近 90%；α 不可能超過 1，到 1 就滿了。
   - chaining：α 就是 **每個 bucket 平均的元素數**，也就是平均要走的 list 長度。例子 5/5 = 1。
   - 存取時間 = O(1) 找 bucket + 走一條平均長度 α 的 list。

7. **Resize（rehash）**（[00:45:02]–[00:53:01]）
   - 時機：chaining 的 α 大約超過 3–4 就 resize；open addressing 因為 α ≤ 1，大約 0.75 或 0.6 就 resize（[00:54:04]–[00:55:03]）。
   - 做法：bucket 數加倍 → 走過舊表每個 bucket、每個 item → 用**新的 bucket 數**重新 mod → 放進新 bucket。因為 bucket 數變了，每個 key 該去的 bucket 也變了，不能直接複製。
   - 例子：加入 14、26、68 後 8/5 = 1.6 → 擴成 10 個 bucket → 11→1、6→6、26→6、42→2、23→3、68→8、84→4、14→4 → α = 0.8。
   - 流程：每次 insert 後算 α，太高就 resize。resize 本身很貴（O(n)），但換來之後的 O(1) 存取。
   - resize 時不需要特別處理某條很長的 chain；重新 hash、mod 之後通常會自然分散（[01:08:02]–[01:09:00]）。

8. **Hash function 的三個條件**（[01:00:01]–[01:11:00]）
   1. **deterministic**：同樣的輸入永遠同樣的輸出。
   2. **fast**：hash function 慢的話整個 hash table 就慢了。
   3. **distribution**：輸出要分散。
   - 課堂反例：
     - h(x) = 1：deterministic、fast，但全部進同一個 bucket → 沒用。
     - h(x) = rand：不 deterministic。
     - h(x) = 下一個空格：不 deterministic，同一個 key 插兩次會到不同位置。
     - h(x) = len(x)：deterministic、x 不太大時夠快，分布可能不好，要看輸入長什麼樣。
     - h(x) = x（identity）：輸入本身分散的話就 OK，課堂一直用這個。
   - Python 的 `hash()`：小 int 直接回傳自己；string 用各字元 ASCII 值配上依位置不同的次方加總，得到一個很大的數字（[01:11:00]、[01:37:07]–[01:39:09]）。細節有公開，老師說不需要深究。

9. **現場寫 chaining hash table**（[01:12:06]–[01:42:08]）
   - 老師把 hash table 存成 dict（「用 hash table 表示 hash table」），欄位是 buckets、bucket 數、元素數。以下是依逐字稿**重建**的程式（函式名和 resize 門檻是推測；in-class-code repo 11/24 查時最後更新是 10/27，沒有這次的程式）：

     ```python
     def create_hash_table(num_buckets=5):
         return {
             "buckets": [[] for _ in range(num_buckets)],   # 每個 bucket 是一條 list
             "num_buckets": num_buckets,
             "num_elements": 0,
         }

     def insert_ht(ht, key):                 # 先只存 key，假設 value 跟著 key 走
         which_bucket = hash(key) % ht["num_buckets"]
         ht["buckets"][which_bucket].append(key)   # chaining：collision 直接接在 list 後面
         ht["num_elements"] += 1
         alpha = ht["num_elements"] / ht["num_buckets"]   # load factor
         if alpha > LOAD_LIMIT:              # 課堂上故意設小，讓它觸發 resize
             resize_ht(ht)

     def query_ht(ht, key):
         which_bucket = hash(key) % ht["num_buckets"]
         for i in ht["buckets"][which_bucket]:
             if i == key:
                 return True
         return False

     def resize_ht(ht):
         new_buckets = [[] for _ in range(ht["num_buckets"] * 2)]
         for bucket in ht["buckets"]:
             for item in bucket:
                 new_bucket = hash(item) % len(new_buckets)
                 new_buckets[new_bucket].append(item)
         ht["buckets"] = new_buckets
         ht["num_buckets"] = len(new_buckets)
         # 元素數不變，不用更新 num_elements
     ```
   - 現場踩到的坑：一開始寫 `ht["buckets"][i] = key`，被指出 bucket 裡應該是 list，要 `append`（[01:16:02]–[01:17:03]）；建 buckets 要用 list comprehension 讓每格是一個獨立的空 list（[01:20:00]–[01:21:00]）；寫完 `resize_ht` 忘了在 insert 裡呼叫（[01:33:02]）。
   - 測試：插入 42、84、23、11、6、14、26、68，`query_ht(my_ht, 42)` → True、`query_ht(my_ht, 19)` → False（[01:24:01]–[01:25:01]）。
   - 觀察：起始 5 個 bucket 擴成 10 時，很多 key 還是落在同一個 bucket，因為 10 是 5 的倍數，mod 10 的分布和 mod 5 很像（[01:35:01]）；改成 3 個 bucket 起始，元素太少也看不出差別，要放更多元素才會分散（[01:36:01]）。
   - 老師說「沒處理重複 key」是刻意省略，實作上應該檢查（[01:22:01]）。

## 名詞解釋

- **Hash table**：array + hash function。用 `hash(key) % num_buckets` 把任意 key 對到 array index，平均 O(1) insert / lookup。
- **Bucket**：hash table 底層 array 的每一格。chaining 時每個 bucket 是一條 list。
- **Hash function**：把任意資料變成一個整數的函式；要 deterministic、fast、distributed。
- **Direct addressing**：key 直接當 index，不經 hash。浪費空間、key 範圍受限。
- **Collision**：兩個不同的 key 被分到同一個 bucket。
- **Open addressing**：所有元素都存在 array 本身；collision 時找別的空格（課堂用 linear probing：下一格、到底繞回開頭）。容量上限 = bucket 數，α ≤ 1。
- **Chaining (separate chaining)**：每個 bucket 存一條 list，collision 就接在 list 上。沒有硬性容量上限。
- **Load factor（α）**：元素數 / bucket 數。chaining 時等於每個 bucket 的平均 chain 長度。
- **Resize / rehash**：bucket 數加倍，所有元素依新的 bucket 數重新分配。O(n)，但讓 α 降下來。
- **Identity hash**：h(x) = x，課堂為了簡化用的 hash function。
- **Python `hash()`**：內建 hash；小整數回傳自己，字串依字元和位置算出一個大整數。

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

- [00:07:02] hash table 最大的價值是效率：平均 O(1) insert 和 retrieve，「This is the magic of a hash table」。
- [00:08:00] 聽到 O(1) 存取就要想到 array；那是直接存取記憶體位置的唯一方式。
- [00:23:04] 不管 collision 怎麼處理，資料都擠進同一個 bucket 就會變慢；重點是減少 collision。
- [00:49:01] 要注意 resize 的流程，「because you may have to implement it」→ 很可能出現在作業裡。
- [00:52:03] resize 時每個 item 都要用新的 bucket 數重算位置，因為 bucket 數變了。
- [00:53:01] resize 讓 chain 保持很短，存取才維持 O(1)。
- [00:54:04] resize 門檻依 collision 處理法而定：chaining 約 3–4，open addressing 約 0.75 或 0.6。
- [00:58:06] chaining 和 open addressing 沒有絕對的好壞，跟所有工程決策一樣是 trade-off。
- [01:02:02] hash function 第一條件是 deterministic，接著是 fast（[01:03:03]）和 distribution（[01:04:02]）。
- [01:06:03] 就算 hash function 好、有 resize，還是有可能全部擠到同一個 bucket，只是機率很低。
- [01:41:01] 寫完 chaining hash table 其實很快：記 bucket 數、建 buckets、記元素數，insert 時算 α、太高就 resize。
- [01:44:00] 有空的 bucket 沒關係，只要被用到的 bucket 不要太長；這些分析都是機率性的（平均，不是精確值）。
- [01:45:06] 實務上發現 hash table 一直很慢、key 都落在同一個 bucket，才需要換 hash function 或客製化。
- [01:46:10] 所有資料結構都有 trade-off 和 worst case，不用一直擔心 worst case，實際碰到了再處理。
- [00:06:00]、[01:47:07] **11/25（三）感恩節前一天沒有課，而且這次不會錄補課影片**（老師說往年錄了也沒人看）。
- [01:46:10] midterm 的解答已經放上 Canvas（Module「Week 6: Midterm」的 `midterm_fall2026_solutions.pdf`，file id 156382779）。

## 和作業 / 考試的關聯

- **A6 Heaps**：12/6（日）11:59 PM PST 截止（Canvas id 11814820），目前 unsubmitted。這堂沒講 heap，但 A6 是下一份要交的作業。
- **hash table 作業**：Canvas 上還沒看到 hash table 的作業。老師在 [00:49:01] 提醒要注意 resize 的流程，「you may have to implement it」，後面的作業（可能是 A7 Surprise，12/11 五，不能遲交）或期末很可能要寫 hash table insert / query / resize。
- **Final Exam**：12/9（三）4:30 PM PST，實體紙筆。適合準備的題型：
  - 手算 mod 把 key 放進 open addressing（linear probing、繞回開頭）和 chaining 的表
  - 算 load factor
  - 畫 resize 前後的表
  - 判斷某個 h(x) 符不符合 deterministic / fast / distribution
- **Midterm**：解答已上 Canvas，可以拿來對自己的考卷（成績 11/17 已出）。
- **時程更正**：`dsa/assignments.md` 把 11/25 寫成「可能改非同步」。老師在課堂上說了不會錄補課影片（[00:06:00]），依 BOOTSTRAP §3，課堂發言優先。

## 還要釐清的問題

1. 課堂程式裡的 resize 門檻：老師說「let's keep it small」（[01:26:04]），沒有聽到確切數字。講義或程式上傳後確認。
2. open addressing 的 resize（老師說「looks a little bit different」，沒有展開，[00:54:04]），以及 open addressing 的 delete（用 tombstone？）課堂都沒講。如果作業要寫 open addressing，要另外查。
3. 這週 Canvas 排的是 Module 8 Graphs（Reading Ch 7 Dijkstra），但這堂還在 hash table。12/1 那堂是不是直接進 graph？Module 9（Tries、Skip Lists、LRU Cache，Week of Nov 30）的進度會不會往後延？
4. hash table 有沒有對應的作業？A7「Surprise」的內容還不知道。
5. 起始 5 個 bucket 擴成 10 時，分布改善不大（[01:35:01]）。這和「bucket 數用質數比較好」有沒有關係？老師沒有明講，可以自己驗證。
