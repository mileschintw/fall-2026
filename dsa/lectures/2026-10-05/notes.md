# DSA Class 2 — 2026-10-05（Mod 1：Linked Lists / Arrays，週一實體課）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，522 cues，00:01:05–00:51:01，約 51 分鐘）、slides（Mod1_LInkedListsArrays_Monday.pdf，Canvas file 153960101，11 頁，老師手寫筆記的 OCR，雜訊很多）、閱讀章節：Grokking Algorithms，推測是 Ch2 前半（arrays vs. linked lists；repo 沒有記錄閱讀進度）。逐字稿是自動產生，專有名詞可能聽錯。
>
> **錄影只有下半堂**：老師在 [00:01:05] 說開頭可能沒錄到，錄影從休息後開始。投影片 p2–p5（公告、array 的特性、resize、insert／shift）屬於上半堂，**沒有逐字稿可對照**，以下標「（僅投影片）」。老師在 [00:50:15] 說會把完整錄影補上。
>
> 常見誤聽對照：O / oven → O(1) 或 O(n)（[00:02:09] 的「the cost is O」是 O(1)）；the case element → the k-th element；Teeth → T（插入的節點字母）；be glad you're not using Z → C；Mike, Meg → 無意義；O of M → O(n)；note → node。
>
> 投影片 p11 是「Weekly Overview: Intro to Data Structures and Python」，屬於第一週（Module 0）的 Canvas 頁面，和本堂內容無關。

## 重點摘要

1. **Array 的特性**（p3，僅投影片）
   - 用 index 存取；佔用一整塊連續（contiguous）記憶體；大小固定；所有元素同一型別。
   - 要分清楚 size（目前元素數，例：3）和 capacity（配置的格數，例：5）。
2. **Array 的 resize／insert／remove**（p4–p5，僅投影片；[00:32:03] 的練習有複習）
   - Resize：配置一個更大的新 array，再用迴圈把 n 個元素逐一複製過去，總共 O(n)。
   - Insert（非尾端）：要把後面的元素全部往後移一格，O(n)。
   - Remove：要把後面的元素往前移補洞（shift），O(n)。
3. **Linked list 的結構**（p6–p7）
   - Node = element／data + 指向下一個 node 的 pointer。
   - Node 不必連續存放，不需要一大塊記憶體（[00:47:01]–[00:49:06]）。
   - 本堂的 linked list 記錄 `head` 和 `size` 兩個 metadata；之後討論可再加 `tail`。
4. **Linked list 各操作的做法**
   - 取第 k 個元素：從 head 一路 traverse 並計數，O(n)。先檢查 size，超出範圍就直接回報失敗（[00:03:00]–[00:04:00]）。
   - 在開頭插入：建立新 node → 新 node 指向目前 head 指的東西 → 再把 head 改指新 node → size + 1。O(1)（[00:05:00]–[00:07:00]）。
   - 插入在某個值（例：C）之前：traverse 找到位置，新 node 指向 C，前一個 node（B）改指新 node。找位置 O(n)，改指標只要 O(1)（[00:08:00]–[00:12:11]）。
   - 刪除某個值（例：T）：traverse 找到 T，讓前一個 node 改指「T 原本指的 node」。Python 會把沒人指向的 T garbage collect，C 要自己釋放。O(n)（[00:13:07]–[00:17:00]）。
   - 刪除開頭：head 改指第二個 node，O(1)（[00:24:05]）。
   - 在尾端插入：沒有 tail 要 traverse，O(n)；有 `tail` pointer 就是 O(1)（[00:39:00]–[00:40:00]）。
   - 用 index 或用值來指定位置都可以，是實作者的設計選擇（[00:13:07]–[00:14:04]）。
5. **Big-O 總表**（本堂的核心）

   | 操作 | Array | Linked list（head + size） |
   |---|---|---|
   | 依 index 讀取（get index 500） | **O(1)**：直接算位址 | **O(n)**：從 head 逐一走 |
   | 在開頭插入 | **O(n)**：全部往後移 | **O(1)**：改兩個 pointer |
   | 在中間插入 | **O(n)**：可直接到位置，但要 shift | **O(n)**：要 traverse 找位置；改 pointer 本身 O(1) |
   | 在尾端插入 | **O(1)**（還有空間時）；滿了要 resize，**O(n)** | 沒有 tail：**O(n)**；有 tail：**O(1)** |
   | 刪除開頭 | **O(n)**：其餘元素往前移 | **O(1)** |
   | 刪除中間／依值刪除 | **O(n)**（shift） | **O(n)**（traverse） |
   | Resize | **O(n)**（配置 + 逐一複製） | 不需要 |
   | 取得長度 | O(1) | 有 size metadata：**O(1)**；沒有就要走完整個 list，O(n) |

6. **常見錯誤**（p8，[00:17:00]–[00:21:02]）
   - 忘了更新 size（老師自己在示範中就漏了）。
   - 改 pointer 的順序錯：先改 head 再設新 node 的 next，新 node 會指向自己，原本的 list 就丟了。原則是「先讀再寫」。
   - Traverse 時早一個或晚一個 node 停下（off-by-one）。
7. **課堂練習：array `[3, 7, 1, 9, 4]` 在 index 2 插入 5 vs. linked list 在 7 和 1 之間插入 5**（p10，[00:27:04]–[00:36:04]）
   - Array 已滿，要先 resize（新 array、全部複製），再把 1、9、4 往後移，最後放入 5。
   - 一定要**先 shift 再 insert**，而且 shift 要從尾端開始搬；先放 5 會把 1 蓋掉。這和 linked list 改 pointer 的順序問題是同一個概念。
   - Linked list：traverse 找到 7 → 建立 node 5 → 5 指向 7 原本指的 node（1）→ 7 改指 5。其他 node 都不用動。
8. **「Linked list 的插入一定比較好」是錯的**（[00:37:02]–[00:42:00]）
   - Array 在尾端有空位時插入是 O(1)，比沒有 tail 的 linked list 快。
   - Linked list 雖然不用 shift，但要 traverse 找位置，還是 O(n)。工作類型不同，量級相同。
   - 結論：這是「有時成立」的說法，要看使用方式。
9. **什麼時候用 linked list**（[00:42:00]–[00:49:06]）
   - 經常要刪除／插入開頭元素（queue 類用法）。
   - 已經走到某個位置後要在那裡插入。
   - 存不同大小、不同型別的資料（學生提出，老師「允許」，週三會給 array 的反例做法）。
   - 記憶體破碎時，不需要一大塊連續空間。

## 名詞解釋

| 名詞 | 說明 |
|---|---|
| array | 連續記憶體、固定大小、同型別元素。依 index 存取是 O(1)，因為位址可以直接算出來。 |
| size / capacity | size 是目前存放的元素數，capacity 是已配置的格數。size == capacity 時再插入就要 resize。 |
| resize | 配置更大的新 array，把舊元素逐一複製過去，O(n)。 |
| shift | 插入或刪除時把後面的元素整批往後或往前移一格，O(n)。 |
| linked list | 由 node 串起來的序列，每個 node 存資料和指向下一個 node 的 pointer。不需要連續記憶體。 |
| node | linked list 的單位：element／data + next pointer。 |
| head / tail | 指向第一個／最後一個 node 的 pointer。有 tail 時尾端插入變 O(1)。 |
| traverse | 從 head 沿著 pointer 一個一個走，用來找第 k 個元素或某個值。 |
| metadata（size、tail） | 額外記錄的狀態。讓某些操作變快（例：取長度 O(1)），代價是每次修改都要記得更新。 |
| garbage collection | Python 自動回收沒有任何參照的物件，所以刪除 node 時只要讓它沒人指向即可；C 要自己釋放。 |
| O(1) / constant time | 不管資料多少，步驟數都一樣。 |
| O(n) / linear time | 最壞情況要碰到每一個元素。 |
| trade-off | 本堂一再出現的主題：多存 metadata 或換資料結構，會讓某些操作變快、某些變慢或變麻煩。 |

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

**Lookup 與插入**
- [00:02:09] Array 取第三個元素很便宜：知道位址，直接過去。
- [00:03:00] [00:04:00] Linked list 只有 head 和 size，取第 k 個元素要從頭數，O(n)。聰明的做法是先比對 size，超出範圍就直接放棄，不要硬走。
- [00:05:00] [00:06:00] 在開頭插入的關鍵在「順序」：新 node 先指向 head 目前指的東西，再把 head 改指新 node，最後 size + 1。
- [00:07:00] 開頭插入是 constant time：不管 list 多長，指令數都一樣。這是 linked list 相對 array 的好處之一。
- [00:12:11] 在中間插入一樣是 O(n)，但工作不同：array 是 shift，linked list 是 traverse 後改 pointer。

**刪除**
- [00:13:07] [00:14:04] 用 index 或用資料值指定要刪哪一個，都是你自己的設計選擇；但一律從 head 開始走。
- [00:15:00] 刪掉的 node 在 Python 會被 garbage collect；在比較不寬容的語言要自己清掉。
- [00:16:01] 寫程式時要注意：前一個 node 要改指「被刪 node 原本指向的地方」，所以要先讀它的 next。
- [00:17:00] 刪除是 O(n)，因為最壞要走完整個 list 才找到。

**常見錯誤**
- [00:18:03] 老師示範時自己忘了更新 size。存 metadata 的代價是：一定要記得更新，也要記得用。
- [00:19:01] 好處是查長度只要一次讀取，不用走完整個 list。老師說這就是資料結構的 trade-off。
- [00:19:01] [00:20:00] 最常見的錯誤是 pointer 還沒讀就先被覆寫：先把 head 改指新 node，新 node 再去讀 head，結果指向自己。
- [00:20:00] 老師保證：第一次實作 linked list 的人，作業裡至少會犯一次這個錯。
- [00:21:02] 另一個常見錯誤是 traverse 時早一個或晚一個 node 停下。

**Array vs. linked list 舉手題**
- [00:23:03] 取 index 500：array 比較省事，直接到記憶體位置；linked list 要走過 500 個 node。
- [00:23:03] [00:24:05] 在開頭插入：linked list 比較省事。
- [00:24:05] [00:25:02] 刪除開頭：linked list 只要把 head 改指下一個；array 要把全部往前移。老師慶幸這門課不用 C，不必手動釋放記憶體。

**課堂練習（插入 5）**
- [00:32:03] Array 已經沒有空位，要先 resize，等於所有元素都要搬到新位置。
- [00:34:03] [00:35:00] 要先 shift 再 insert；先放 5 再 shift 會把 1 蓋掉。老師把這和 linked list 改 pointer 的順序問題連在一起。
- [00:35:00] [00:36:04] Linked list：找到 7 → 新 node 5 指向 7 原本指的 node → 7 改指 5。只動新 node 和兩個 pointer。

**「一定比較好」的說法**
- [00:38:05] 「Linked list 的插入一定比較好」不是完整、正確的說法。
- [00:39:00] Array 在尾端插入且不用 resize 時是 O(1)。
- [00:39:00] [00:40:00] 學生反駁：linked list 有 tail 時尾端插入也是 O(1)。老師同意，並說多存 metadata 可以讓某些操作更有效率，這是另一個 trade-off。
- [00:40:00] [00:41:04] [00:42:00] Linked list 雖然不用 shift，但要 traverse 找元素，仍可能 O(n)。這是「有時成立」的說法，要看怎麼用。

**為什麼要用 linked list**
- [00:42:00] [00:43:15] 經常要刪除第一個元素時用 linked list；array 每次都要全部往前移，又慢又難寫。
- [00:44:03] 老師說資工人很懶，不想寫那種搬移的程式。
- [00:44:03] [00:45:05] [00:46:05] 學生提出 linked list 可以存不同型別、不同大小的資料。老師接受，但說要看語言和其他限制；array 做不到，週三會給替代做法。
- [00:46:05] [00:47:01] 已經知道插入位置時，linked list 在中間插入比較有效率；昂貴的是找位置那一步。
- [00:47:01] [00:48:02] [00:49:06] 記憶體越用越破碎，越難找到一大塊連續空間給 array；linked list 的 node 可以散在各處。

**課務**
- [00:01:05] 開頭可能沒錄到，錄影從休息後開始。
- [00:21:02] 線上同學卡在 Zoom waiting room，老師說週三（遠端）前會修好，避免一直按 admit。
- [00:49:06] 週三（10/7）改在 Zoom 遠端上課：看實作程式碼、跑起來，並熟悉 unit testing。老師說 unit testing 是下一份作業的一部分，也是實驗資料結構的好方法。
- [00:50:15] 老師會補上從頭開始的錄影，並取消 waiting room。

## 和作業 / 考試的關聯

- **A2 Lists, lists and more lists**
  - 截止：**10/18（日）11:59 PM PDT（今天）**，150 分，Canvas id 11814777，目前 unsubmitted。
  - 依標題，很可能要實作 array-based list 和／或 linked list。老師在 [00:20:00] 說「你們會在作業裡做這個」，指的就是實作 linked list 時的 pointer 順序錯誤。
  - 實作時的檢查清單（本堂的常見錯誤）：
    - 每個 insert／remove 都要更新 size（[00:18:03]）。
    - 改 pointer 前先讀出要保留的 next（[00:19:01]、[00:16:01]）。
    - 檢查 traverse 的停止條件，避免 off-by-one（[00:21:02]）。
    - 存取 index 前先比對 size，超出就報錯（[00:04:00]）。
    - Array 插入要從尾端開始 shift，滿了要先 resize（[00:34:03]）。
    - 有 tail 的話，在空 list 和刪除最後一個 node 時都要記得更新 tail。
  - 繳交流程：push 到 `uw-python-fall2026/assignment-2-mileschintw`，**再到 Canvas 交 repo URL**。
- **A3 Stacks, Queues and Testing**：10/23（五）11:59 PM，150 分。老師在 [00:49:06] 說 unit testing 是「下一份作業」的一部分；A3 標題有 Testing，可能指的是 A3（見「還要釐清的問題」）。Queue 常需要「刪除開頭」，正好對應本堂說的 linked list 優勢（[00:42:00]）。
- **Midterm**：11/9（一）4:30–6:30 PM PST，實體紙筆，Moore 220，佔 15%。本堂的 Big-O 總表和「哪個比較省事」的比較題型（[00:22:01]–[00:25:02]）很可能出現在紙筆考裡。
- **閱讀**：Grokking Algorithms，推測是 Ch2 前半（arrays and linked lists；repo 沒有記錄閱讀進度）。要注意，課本的 running time 表可能把 linked list 的 insert／delete 記成 O(1)，前提是已經拿到那個 node；本堂把 traverse 也算進去，所以是 O(n)。這個差別老師在 [00:46:05] [00:47:01] 講過：已經知道位置時插入很便宜，貴的是找位置。考試作答時要寫清楚有沒有把 traverse 算進去。

## 還要釐清的問題

1. **上半堂沒錄到**：p2–p5（公告、array 特性、resize、insert／shift 的 O(n) 推導）只有 OCR 投影片。p4 resize 的推導是「配置 O(?) + 複製 n 次 O(n) = O(n)」，配置那一步的複雜度 OCR 看不清楚。老師說會補完整錄影（[00:50:15]），補上後要回來對照。
2. **p2 的公告內容**：OCR 只看得出「Github/Assignments」和「Hongyr OH」（某位 TA 或助教的 office hours，名字拼法未確認），細節要看完整錄影或 Canvas。
3. **unit testing 是哪份作業的一部分？** 老師在 [00:49:06] 說「next assignment」。10/5 當時的下一份作業是 A2，但 A3 的標題才有 Testing。需要看 A2、A3 的作業說明確認。
4. **A2 到底要實作 array-based list、linked list 還是兩者？** 本堂只說「你們會在作業裡做」（[00:20:00]），要看 A2 的 README。
5. **不同型別存在 array 的替代做法**：老師在 [00:45:05] 說週三（Class 3，10/7）會講，可對照 2026-10-07 的逐字稿。
6. **Lookup 的平均 vs. 最壞情況**：本堂只講 worst case（O(n)），沒有談 average case 或 amortized（例如 array 尾端插入加上偶爾 resize 的攤銷成本）。Mod 2 的 Dynamic Arrays（10/12）可能會補。
