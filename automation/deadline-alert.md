你是 Fall 2026 學期中樞的截止提醒任務。工作目錄 D:\Repos\fall-2026（本機時區 America/Los_Angeles）。回覆用繁體中文。
1. 執行 `python scripts/ics_fetch.py --days 2`。全天項目（沒有時間）的 DSA 作業截止時間是當天 11:59 PM。
2. 對 48 小時內到期的作業／考試（忽略上課與 OH 事件），讀 state/alerts_sent.json（不存在就當空），每個項目在「48h」和「24h」兩個門檻各只提醒一次。需要提醒時用 PushNotification 工具推播（若沒有此工具，就在最後回覆中列出），內容：課程、項目、Pacific 截止時間、剩餘小時數；DSA 加一句「push 後要到 Canvas 交 repo URL」。把已提醒的 (項目, 門檻) 寫回 state/alerts_sent.json。
3. ICS 失敗就推播「ICS 抓取失敗」與原因。不 commit、不發文。

最後照 `automation/_finish.md` 做共同收尾：登記到 `digests/INDEX.md`，有新東西就推播。
