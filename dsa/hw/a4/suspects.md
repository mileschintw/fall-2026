# A4 嫌疑清單（AI 讀 code 列的，**還沒驗證**）

> 2026-11-02 由 Claude（Opus 5.5）在互動 session 裡讀 [repo/help_desk.py](repo/help_desk.py) 和 docstring 對照後列出。
> 依作業規定，這些全部只是 **suspicion**：每一條都要你自己寫 test 證明（original 上 FAIL、修好後 PASS），或證明它沒錯（兩邊都 PASS）。
> 寫進 `FINDINGS.md` 時，這些列的「Idea came from」要填 **AI**。這份清單本身就是你的 AI 使用紀錄的一部分，請保留。
> 這裡故意不寫 test 和修正，那是作業本身。行號是 starter 版的。

## 看起來是 bug 的

| # | 函式（行號） | docstring 說 | code 實際上 | 種類 | 怎麼驗證（提示） |
|---|---|---|---|---|---|
| A | `da_append`（17–26） | 滿了容量**加倍**，n 次 append 共 O(n) | 新容量是 `len + 1`，每次滿了都整份複製 | 速度 | append 很多個（例如幾萬個）量 `time.time()`；或比較 n 和 2n 的耗時比例。也可以看 append 後的容量（`len(arr['slots'])`）是不是 4→8→16 |
| B | `da_remove_last`（37–44） | 移除並回傳**最後一個**元素 | 讀的是 `slots[size]`（最後一個的**下一格**） | 答案錯 | append 幾個值後 remove_last，看回傳值 |
| C | `stack_pop`（64–66） | 空 stack **回傳 None** | 直接 `s.pop()`，空 list 會 raise `IndexError` | crash | 對空 stack pop。連帶影響：`undo_close` 在沒東西可 undo 時、`brackets_balanced(")")` 都會 crash |
| D | `queue_push_front`（108–110） | 放到**最前面**，下一個被 dequeue | `append` 到**尾端** | 答案錯 | enqueue 幾個後 push_front，看 dequeue／peek 拿到誰。連帶影響：`undo_close` 後的 ticket 不會是下一個被處理的 |
| E | `undo_close`（141–149） | 被 undo 的 ticket **離開 closed list** | 只從 undo stack pop 出來、放回 open queue，**沒有從 closed 移除** | 答案錯 | work_next 後 undo_close，看 `closed_count`／`closed_ids` |
| F | `brackets_balanced`（172–183） | 每個開括號都要被關閉 | 迴圈結束直接 `return True`，沒檢查 stack 是否還有剩 | 答案錯 | `"("`、`"(()"` 這種只開不關的字串 |

注意這幾個 bug 會互相牽連：
- E 的修法很可能會用到 `da_remove_last`，所以 B 沒修好 E 也會怪怪的。
- C、D 會讓 `undo_close` 的 test 因為別的原因 fail。評分的「regression test 要在**只有那一個 bug** 的版本上 fail」是逐一放 bug 測的，所以每個 test 最好**直接測那個函式本身**，而不是只透過 `undo_close` 間接測到。

## 看起來可疑、但可能沒錯的（適合當 `refuted` 列）

| # | 函式 | 為什麼會被懷疑 | 為什麼可能其實沒錯 |
|---|---|---|---|
| G | `queue_dequeue` | 只移動 `head`、不刪元素，記憶體不會釋放 | docstring 只要求 O(1) 和正確回傳；`test_already_correct` 也測了大量 item 依序出來。可以測 n 次 dequeue 的耗時是線性的 |
| H | `queue_size` | `len(items) - head` 看起來容易算錯 | dequeue 後 head 增加，算式剛好是剩下的數量 |
| I | `da_get` | 負數 index 在 Python list 會從尾端取 | code 有先檢查 `index < 0`，會 raise `IndexError` |
| J | `submit` | id 會不會重複使用（例如 undo 之後） | `next_id` 只增不減，undo 不會改它 |
| K | `work_next` | 空 queue 時會不會 crash | `queue_dequeue` 空的時候回 None，這裡有處理 |
| L | `next_ticket`／`open_count` | 包裝 queue 的函式 | 本身只是轉呼叫；但 D 修好之前，`undo_close` 之後 `next_ticket` 的結果會錯（錯在 D，不在這裡） |

## 建議做法
1. 在 `D:\Repos\assignment-4-mileschintw` 裡，每一條先寫 test，跑 `python check_hunt.py` 確認它在 original 上 fail（A–F）或兩邊都 pass（G–L）。
2. 再一個一個修 `help_desk.py`，每修一個跑一次 `python check_hunt.py`，確認 `already` 沒被弄壞。
3. 填 `FINDINGS.md`：A–F 是 confirmed、G–L 挑幾個寫 refuted（只要你真的驗證過）。有任何一條你驗證後發現跟上面寫的不一樣，就是 reflection 第 1 題的好素材。
4. 只有 `help_desk.py`、`test_regressions.py`、`FINDINGS.md` 會被評分。push 到 `main`，再到 Canvas 交 repo URL。
