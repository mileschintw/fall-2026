# DSA Class 1 — 2026-09-30（課程介紹、AI 政策、Data Structures 概論、Array 與 Linked List）

> 來源：transcript（Panopto 自動字幕 `transcript.srt`，831 cues，00:03:54–01:42:03，約 1 小時 38 分）、slides（L1_Fall2026_ee590a.pdf，Canvas file 153729203，51 頁）、閱讀：Grokking Algorithms Ch2（Selection Sort：array vs. linked list）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：Adrian → Adrienne（老師）；Cracking Algorithms → Grokking Algorithms；Claudette / plot → Claude；cannabis / campus → Canvas；Dubai midnight → "due by midnight"；papers / press → PRs；cue → queue；for of hearts / four parts → 投影片上的 4（撲克牌）；E program → EE program；430 to 20 → 4:30–6:20。
>
> 錄影注意：開頭約 4 分鐘沒錄到（第一句在 [00:03:54]）。[00:09:11]–[00:21:06] 是學生自我介紹，[00:55:01]–[00:56:42] 是休息。

## 重點摘要

1. **課務**（p4–p5、p16）
   - 上課：週一、週三 4:30–6:20 PM。週一在 Moore 220 實體上課，週三 Zoom（有考試的那週例外）。
   - 老師說順序可以調整（週三實體、週一遠距），先照這樣開始。
   - 課程資料在 Canvas 和 GitHub；討論區是 Piazza；成績在 Canvas；繳交透過 Canvas 和 GitHub。
   - 聯絡老師優先用 Piazza，個人事務用 private note；email 容易漏掉。
   - Office hours（只在投影片 p4）：週六 9:30–11 AM，Zoom；其他時間預約。
2. **課程目標**（p6）：列舉、描述、比較常見 data structures；描述 algorithm 的 runtime；比較 trade-off；用 Python 實作；能跑有多個元件的 Python 程式。
3. **週次與作業**（p7）
   - Week 0 課程介紹；Week 1 Big-O、array、linked list；Week 2 stack、queue、dynamic array、testing；Week 3 tree、BST；Week 4 AVL、red-black tree；Week 5 hash table；Week 6 midterm；Week 7 heap；Week 8 graph；Week 9 trie、skip list、LRU cache；Week 10 review + final。
   - 共 7 份作業，前面幾份是「手寫程式」，後面幾份可以用 AI 輔助。A4 Bug Hunt 是新設計：給一段 AI 寫的程式，找出 AI 哪裡做錯。
4. **成績與規則**（p8–p9、p12）
   - 作業（programming / writing）65%、midterm 15%、final 20%。老師特別加了「writing」，因為作業除了寫程式還要回答問題。
   - 遲交每天扣 25%，超過 4 天不收。生病等狀況要事先或當下告知，事後才講不受理。最後一份作業不能遲交。
   - Regrade：拿到成績一週內，在 Piazza 發 private note 給老師，標「Regrade Request」。不要找 grader 改分數。
5. **AI 政策**（p13–p14）
   - 前三週（老師說可能縮成兩週）不准用 AI 寫程式；不要把 starter code 丟給任何 AI 工具；不要用 advanced code completion（basic 可以）。
   - 可以問 AI「解釋這段 code」「有什麼替代做法」、查語法；不可以叫它寫出答案。
   - 三週後可以用 AI，但要附上和 AI 的對話紀錄當作繳交的一部分。細節會再演變。
6. **Data structure 是什麼**（p19–p22）
   - 存放 elements 的容器，典型操作：`add()`、`remove()`、`clear()`、`size()`、`contains()`、`isEmpty()`。
   - 種類：list（array、linked）、stack、queue、map、set、tree、graph。
   - 餅乾比喻（p21）：stack＝罐子裡疊起來的餅乾，只能拿最上面（LIFO）；queue＝一盤盤進烤箱，先進先出（FIFO）；set＝一盤餅乾，任一塊都能直接拿（random access）。
   - 之後比較 data structure 的三個面向：特性（LIFO / FIFO / random access / 可否重複）、可做的操作、效能（放進去多久、拿出來多久、佔多少記憶體）。
7. **Array**（p23–p29）
   - 一塊連續（contiguous）記憶體，每格必須是同一個 type；index 對應到實體位址。
   - 因為知道起始位址和每個 element 的大小，第 i 個的位址可以直接算出來，所以按 index 存取很快。
   - 宣告時要給名稱和 type；很多語言還要指定長度，要放更多就得重新宣告並搬到更大的 array。Python 會自動 resize。
   - Python 的 `array` module：`array('i', [1,2,3,4])`（p28）。
   - Python 的 `list` 可以放不同 type，但它**不是** array，下週細講（[01:27:01]）。
8. **Linked List**（p30–p42）
   - 每個 node 存 data 和指向下一個 node 的 pointer；從 head 開始，最後一個 node 沒有 next。
   - Node 不必相鄰，所以不能用算術找第 k 個，只能從 head 一路走。
   - 加到尾端：從 head 走到最後一個再接上。可以一直加，不像 array 有固定長度。
   - 插在中間：要找到前一個 node，改兩個 pointer。
   - 刪除：走訪時要記住前一個 node，再讓前一個指向被刪 node 的下一個（p38、p40）。被移除的 node 要不要處理「看情況」（p37）。
   - Doubly linked list：每個 node 多一個 `prev` pointer，刪除比較容易（p41–p42）。
9. **本堂只在投影片上、沒有講到的內容**
   - p44–p45 的討論題（百萬筆資料選哪種結構；「linked list 插入一定比較好」哪裡不對）。老師說留到下週當起點（[01:37:00]）。
   - p46–p51 Intro to Python、PyCharm、notebooks、environments。老師說下週再講 Python（[01:41:04]）。

## 名詞解釋

| 名詞 | 說明 |
|---|---|
| data structure | 存放資料（elements）的結構，用操作（add、remove、contains…）和效能特性來描述。 |
| element | 放進 data structure 的資料項目。 |
| array | 連續記憶體、同一 type、用 index 直接算位址存取。存取第 i 個是一次算術就到。 |
| contiguous memory | 一整段相鄰的記憶體位址。Array 靠這點才能用「起始位址 + i × element 大小」找到資料。 |
| index | Array 中的位置編號，從 0 開始（p26 `a[0]`…`a[9]`）。 |
| Python `list` vs. `array` | `list` 可混放不同 type，不是傳統 array；`array` module 要指定 type code（如 `'i'`）。 |
| linked list | 由 node 串起來的 list，node 不必相鄰。 |
| node | Linked list 的單位，含 data 和指向下一個 node 的 pointer（doubly 版再加 `prev`）。 |
| head | 指向第一個 node 的 pointer，是唯一已知的起點。 |
| doubly linked list | 每個 node 同時有 `next` 和 `prev`，可以往回走，刪除時不必另外記前一個 node。 |
| stack（LIFO） | Last In, First Out，只能從頂端放和拿。 |
| queue（FIFO） | First In, First Out，先放進去的先拿出來。 |
| set | 投影片的餅乾比喻裡指「可以直接拿任一個」；正式定義（不重複元素的集合）之後再講。 |
| random access | 不用依序走訪，可以直接存取任一位置的資料。 |

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

**上課方式與錄影**
- [00:04:05] 每堂課都開 Zoom 給不能到場的人，也是錄影機制；錄影會放在 Canvas。
- [00:04:05] 教室裡聽不到或看不到時，隨時打斷老師。
- [00:46:04] 週一在教室，週三預計遠距；之後可以討論對調。
- [00:57:05] [00:58:03] 投影片課前上傳 Canvas；老師上課用 iPad 註記，課後再放註記版。
- [00:58:03] 錄影大約課後 24 小時會連到對應的 Module；還沒連上的話直接去 Panopto 找。
- [00:58:03] [00:59:04] 本週結束前要填一份小問卷，讓老師了解班上組成。
- [00:59:04] Canvas 的 Resources 頁放所有站外連結：JetBrains 免費授權、PyCharm、GitHub repo、視覺化工具、Piazza。

**AI 與這門課**
- [00:21:06] [00:22:04] 這門課的定位：面試會考 data structure 和 algorithm 分析，實際工作也越來越需要。有 CS 學士學位的人可能學不到太多新東西。
- [00:27:02] 用 AI 寫 code、開 PR 後，責任在你：不只沒 bug、有測試，還要確定它做了該做的事、沒做不該做的事。
- [00:32:03] 自己 review 自己的 code 有偏誤，因為你知道全部 context；用 AI 寫程式時，你的角色越來越像 reviewer。
- [00:34:08] [00:35:06] AI 最適合的情境：你懂 context、解過類似問題、知道輸入輸出大概長什麼樣。
- [00:35:06] [00:36:09] [00:37:04] 不要把 AI 用在 safety-critical 的部分；不要把個人或敏感資料直接丟給 AI。用 AI 產生「處理資料的程式」則還好。
- [00:38:05] AI 工具很急著照你說的做，可能寫出兩萬行、其實改一下需求只要二十行。工程師要懂底層架構才能及時修正方向。
- [00:42:01] [00:44:09] 老師自己的經驗：新工作前三個月靠 AI 交付功能，但不了解 codebase；改回手寫兩週後才真正懂架構。
- [00:40:00] 這門課以前完全禁止 AI，今年改了；約三分之二的作業重新設計，用來練習怎麼好好用 AI。
- [00:41:05] 手寫 code 像去健身房舉重：本身沒產出，但在鍛鍊你。
- [01:11:07] 官方政策（syllabus 也有寫）：前三週手寫，不准用 AI 寫 code；之後可以用。
- [01:12:03] 三週後用 AI 的作業，要把和 AI 的對話一起交上來；做法會再調整。
- [01:08:07] 卡住時可以找同學或 AI 討論，但前三週不能問「哪段 code 能修好這個問題」；可以問「我寫的這段在做什麼」。
- [01:08:07] [01:09:08] 老師沒辦法證明你有沒有作弊，這是信任問題；大家是成年人，自己選擇。

**溝通**
- [00:47:03] 正式溝通一律用 Piazza；email 會漏，Piazza 不會。要找老師就上 Piazza。
- [01:01:02] Resources 頁的 Piazza 有兩個連結：sign-up 連結和課程頁連結。每個人都要點 sign-up 加入，才收得到公告。
- [01:02:00] [01:03:01] 老師在課堂上口頭設了一組 class access code，給用第二個連結加入的人用；照 sign-up 連結走應該不需要。Access code 見 Canvas Resources（筆記不記錄）。
- [01:03:01] 開學頭幾天 Piazza 還沒弄好的話，可以先在 Canvas 傳訊息給老師。

**考試**
- [00:51:00] Midterm 在 11/9（一），實體、教室、紙筆。那週三是 Veterans Day，停課，不補課。
- [00:53:00] Final 在最後一週上課日，實體、教室、紙筆，**不在 finals week**。老師說會一再重複這件事。
- [00:53:00] 要人在西雅圖；如果最後一天不在，開學初就要先講，不要 12 月才來問。
- [00:54:04] [00:55:01] 有同學問會不會要用鉛筆手寫 code：老師說通常不會寫真正的 code，頂多 pseudocode；之後會給範例題。
- [01:07:02] 老師口頭更正 p11：final 是週三（不是週二），不是 2025-06-10，不是 online、不在 Canvas，是紙筆考。老師說會修正 Canvas 上的投影片。
- [01:04:09] [01:05:06] Midterm 的用意是讓你知道題型、範圍和紙筆考的感覺，期末就知道要準備什麼。

**作業與時程**
- [00:49:01] A1 其實是「assignment zero」：寫很少的 code，主要是設定開發環境、熟悉繳交流程。
- [00:50:01] [00:51:00] 前面的作業（A2、A3）全部手寫；A4 Bug Hunt 用 AI 輔助，找出 AI 做錯的地方。
- [00:52:04] 有一份作業在感恩節週末的週日截止，老師先道歉；感恩節那週的週三停課。
- [01:05:06] 作業截止是當天午夜（投影片 p8：11:59 PM）。遲交每天扣 25%，4 天後不收。
- [01:05:06] 生病要盡早說；事後三天才說「我生病了」不會被接受。
- [01:06:03] 最後一份作業在學期最後一天截止，**不能延期**。
- [01:06:03] [01:07:02] Regrade：一週內在 Piazza 發 private note 給老師，不要找 grader 爭。
- [01:09:08] [01:10:01] 有同學提議改成週日截止，舉手表決後老師說改成週日（原本週五的下一個週日），所以大多數作業約有兩週。
- [01:11:07] 開學第一份作業刻意要快點交，好把流程上的問題先解決。
- [01:41:04] A1 出了點狀況，會在一天內發出；要盡快完成。

**學程式的方法**
- [01:13:04] 保持好奇、改一點東西再跑看看；自己把範例打一遍再跑，不要複製貼上。
- [01:14:04] 在課堂和 Piazza 多發問，也回答別人的問題。

**Data structures**
- [01:21:08] 比較 data structure 的效能（放進去、拿出來要多久，用多少記憶體）是面試必考，工作上也會用到。
- [01:23:01] Array 最重要的一點：它是一塊 contiguous 記憶體。
- [01:26:01] 因為知道每個 element 多大、總共幾個，就能直接算出第 i 個的位址，所以查找很快。
- [01:27:01] [01:28:04] Array 不能混放不同 type；Python list 可以，但它不是 array。老師說這正是用 Python 教這門課讓人頭痛的地方。
- [01:30:07] Linked list 的 node 不必相鄰，這是它和 array 的根本差異。
- [01:33:02] Array 存取任一位置是一次算術；但寫進去前不知道那裡原本有沒有資料。Linked list 可以一直往後加，array 放滿就沒位置了。
- [01:34:01] 預告：作業要寫 linked list，畫圖、移動 pointer 是熟悉它最好的方法。
- [01:36:03] [01:37:00] 實務上很少自己實作 linked list（嵌入式等受限環境除外）；重要的是懂 linked list 和 array 型結構的差別。面試常考，是因為它很能看出你懂不懂寫 code。
- [01:38:00] 刪除 node 時要記住前一個 node，不然會失去指向它的 pointer。
- [01:39:00] Doubly linked list 每個 node 多存一個往回指的 pointer，刪除比較簡單。
- [01:40:05] 同學舉例：瀏覽器分頁可以用 linked 的順序存。老師認同。

**其他**
- [01:19:00] 老師的 PSA：UW 10/30 有 COVID 和流感疫苗接種活動。
- [01:00:07] 課堂 demo 用 PyCharm，老師只支援 PyCharm；用 Cursor 或其他工具也可以，但問題要自己處理。
- [01:00:07] [01:01:02] 教科書 Grokking Algorithms 可以從圖書館免費借電子版，課堂上夠用，不必特地買。

## 和作業 / 考試的關聯

- **A1 My First Python Assignment**：10/4（日）11:59 PM，50 分，已 graded。老師說它其實是環境設定和繳交流程的練習（[00:49:01]）。
- **A2 Lists, lists and more lists**：**今天 10/18（日）11:59 PM PDT**，150 分，Canvas **unsubmitted**；`assignment-2-mileschintw` repo 只有 Initial commit（見 `dsa/repos.md`）。本堂的 array / linked list（p24–p42）就是 A2 的基礎。
  - 依政策，A2 落在前三週「手寫」期間（Week 2 作業）。如果 A2 的 README 仍沿用 p13 規定，提醒：把 starter code 交給 AI 是課程明文禁止的。
- **A3 Stacks, Queues and Testing**：10/23（五）11:59 PM，150 分。
- **A4 Bug Hunt**：10/30（五），AI 輔助；之後用 AI 的作業要附 chat session（[01:12:03]）。
- **Midterm**：11/9（一）4:30 PM PST，實體紙筆，Moore 220，15%。可能有 pseudocode，不太會寫真正的 code（[00:55:01]）。
- **Final**：**12/9（三）4:30 PM PST，實體紙筆，教室**，20%。L1 p11 的「Tuesday of Finals Week, June 10, 2025, Online in Canvas」是舊內容，老師已在 [01:07:02] 口頭更正。Canvas 上的 New Quizzes 只代表時段。
- **A7**：12/11（五）11:59 PM，不能遲交（[01:06:03]、p8）。
- 成績：作業 65%、midterm 15%、final 20%（p8，和 `assignments.md` 一致）。
- 閱讀：Grokking Algorithms Ch2（array vs. linked list、reading / insertion / deletion 的效能比較）對應本堂；Ch1 的 Big-O 對應下週。
- 繳交方式：push 到 `uw-python-fall2026/assignment-<N>-mileschintw`，再到 Canvas 交 repo URL（`assignments.md`）。

## 還要釐清的問題

1. **作業截止日到底是週日還是週五？** 老師在 [01:10:01] 說改成週日。A1（10/4）、A2（10/18）確實是週日，但 Canvas 上 A3（10/23）、A4（10/30）、A5（11/6）都是週五。以 Canvas 的 `due_at` 為準，但值得在 Piazza 確認是否後來又改回。
2. **感恩節那份作業的截止日**：老師說在感恩節週末的週日（11/29），`assignments.md` 記錄 A6 是 11/30（一）11:59 PM。要對照 Canvas `due_at`。
3. **「前三週不用 AI」從哪天算到哪天？** 老師說「可能縮成兩週」（[00:40:00]）。是否涵蓋 A2、A3，需要看作業 README 或 Piazza 公告。
4. **遲交政策兩個版本**：投影片 p8 是每天 -25%、超過 4 天不收；`assignments.md` 記錄 syllabus 另有「每學季一次免罰延期（事先告知、最多 1 週）」。本堂老師沒提到免罰那一條。
5. **上課地點對調**：老師說週一實體、週三遠距可以再討論（[00:46:04]），後來有沒有改需要確認。Canvas 行事曆的地點欄不可信（BOOTSTRAP §3）。
6. **Final 當天其他細節**：投影片 p11 的「mostly multiple-choice, some short answers」是舊內容的一部分，題型是否仍適用不確定；老師只說會給範例題（[00:55:01]）。
7. **Office hours**：投影片寫週六 9:30–11 AM Zoom，本堂口頭沒提到，要確認是否仍有效。
