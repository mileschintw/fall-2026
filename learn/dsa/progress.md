# DSA 學習進度

> 每次上課結束更新。時間用 Pacific。掌握程度：⬜ 未學、🟨 看過但不穩、🟩 能自己解釋並做對題目。

## 目前位置
- 下一步：期中衝刺。學生自己用 [DSA Midterm Sprint](https://claude.ai/artifact/YbhLzEk8ce1D5hPBfdm7BU)（`modules/midterm-sprint.html`）由上往下讀，再做「模擬題」67 題。學生回來時先問模擬題做到第幾題、哪幾題錯，從錯題的節開始講。
- 待補材料：Class 11 notes（file 155891168，有練習題）和 `class_scribbles.pdf` 都在 Canvas Module 7，但 module 鎖到 11/16 12 AM PST（11/8 重新登入後確認），學生打不開。學生在 Piazza 請老師解鎖的話，再抓下來補進衝刺頁的模擬題；否則 11/16 後補。
- 期中之後：問長期目標、做診斷，模組 9（heap）接 A6。
- 上次上課：2026-11-09 PT 考前 AVL 速成（約 30 分鐘）
- 累計上課分鐘：30

## 模組
| # | 模組 | 狀態 | Artifact | 最後上課 |
|---|---|---|---|---|
| 2026-11-09 | 插入 1,3,2 後 node 3 的 BF | −1 | 只有左 child 的 node 誤算成負的（BF = 左高 − 右高，左邊有東西應為正）；講了「z 與 child BF 同號單旋、異號雙旋」 | 講解後未再測 |
| 1 | Array vs linked list | ⬜（未診斷） | 衝刺頁 §Array / Linked list | — |
| 2 | Stack 實作、unittest | ⬜ | 衝刺頁 §必背 code | — |
| 3 | Dynamic array、amortized | ⬜ | 衝刺頁 §Dynamic array | — |
| 4 | Stack／queue ADT、deque | ⬜ | 衝刺頁 §Stack / Queue | — |
| 5 | Tree、traversal | ⬜ | 衝刺頁 §Tree / Traversal | — |
| 6 | BST | 🟨（學生自評：A5 part 1 做完，delete 會了） | 衝刺頁 §BST | 2026-11-09 |
| 7 | AVL | 🟨 | 衝刺頁 §AVL | 2026-11-09 |
| 8 | Big-O | ⬜ | 衝刺頁 §Big-O | — |
| 9 | Heap | ⬜（期中不考） | — | — |

## 觀念掌握（細項）
| 觀念 | 狀態 | 證據 |
|---|---|---|
| AVL 單旋轉 RR/LL | 🟩 | 11/9：1,2,3 → BF −2,−1,0、左旋成 2 1 3；20,10,30,5,15,3 → z=20 BF+2、LL、結果 level order 10 5 20 3 15 30（15 掛到 20 左邊）全對 |
| AVL 雙旋轉 LR/RL | 🟨 | 11/9：1,3,2 判斷 RL、旋轉步驟對，但 3 的 BF 算成 −1 |

## 錯題與錯誤觀念
| 日期 | 題目 | 學生的答案 | 背後的錯誤模型 | 是否已修正 |
|---|---|---|---|---|

## 待複習
- 只有單邊 child 的 node 算 BF 的正負號
- AVL 的 N(h) 最少 node 數、AVL delete（考前沒講到）

## 上課紀錄
- 2026-11-09 PT，約 30 分鐘：學生說 AVL 從沒學過。從高度／BF／z／rotate 定義教起，練 1,2,3（RR）、1,3,2（RL）、20,10,30,5,15,3（LL 含子樹搬移），單旋轉都對，雙旋轉 BF 正負號錯一次。
- 2026-11-08 18:32 PT：Canvas 重新登入，確認 Class 11 notes 和 scribbles 都在鎖住的 Module 7（到 11/16），衝刺頁的缺漏說明改成這件事。
- 2026-11-08 18:25 PT，0 分鐘互動：考前一天盤點材料（Class 1–11 notes 都在；缺 Class 11 notes 和 scribbles，Canvas 登入過期），做期中衝刺頁並發布。
