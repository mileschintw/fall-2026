# GPU 課程地圖

> 教材正本：`gpu/lectures/<date>/`（notes.md、slides.txt、transcript.vtt）、`gpu/hw/<hwN>/`。
> 已涵蓋到：2026-10-27（L4）。新講次＝`gpu/lectures/` 下日期比這個新、而且有 `notes.md` 的資料夾。

| # | 模組 | 互動頁點子 | 課程來源 | 作業 |
|---|---|---|---|---|
| 0 | 診斷 | 對話裡 9 題小測 | L1–L3 | — |
| 1 | CPU vs GPU、為什麼要平行 | 1 個大核心 vs 幾千個小核心處理同一張圖的動畫；latency vs throughput | L1、L3 p11–13 | HW0 |
| 2 | 一個 CUDA 程式的完整流程 | 拖曳排序 host/device 步驟；`nvcc` 編譯流程（.cu → PTX → SASS）；host 和 device 記憶體是兩塊 | L1、L2 | HW0、HW1 |
| 3 | Grid / block / thread 對應到資料 | 調 gridDim、blockDim，看每個 thread 負責哪一格、哪些越界被 `if` 擋掉；2D/3D 攤平 | L2 | HW1 |
| 4 | SIMT、warp、divergence | block 切成 warp 的動畫；32 lane 遇到 `if` 時一半閒置；zero-overhead 切換 | L3 p4–10、L4 p34–41 | HW3 |
| 5 | 效能理論 | Amdahl 滑桿（f、P）；AI 計算器；可拖點的 roofline（T4、H100、RTX 3050） | L3 p11–31、L4 p50（NCU roofline） | HW2 P1–P2 |
| 6 | 記憶體階層、tiling、shared memory | 記憶體金字塔（延遲／容量）；tiled MMULT 的 phase 動畫，即時數 GMEM load；`__syncthreads()` 拿掉會怎樣 | L3 p37–74 | HW2、HW3 |
| 7 | 拆解 HW2 | Gaussian blur 三種寫法逐行對照；用 `gpu/hw/hw2/results/` 的實測和 ncu 數據讀 roofline | L3 p75–76、HW2 spec | HW2 |
| 8 | Occupancy 與 launch configuration | Occupancy 計算器：調 threads/block、registers/thread、shared/block，看四個限制哪個先卡住（T4 vs RTX 3050 vs H100）；p8–p9 例題 A–D 逐題拖拉；register spilling | L4 p5–11、[00:59:05]–[01:13:01] | HW3 |
| 9 | Warp scheduling、stall、latency hiding、waves | 4 個 SMSP 的 warp pool 動畫：每 cycle 挑一個 eligible warp，調 warp 數和指令延遲看 issue slot 使用率（Little's law）；stall 原因對照表；wave／tail wave 計算 | L4 p27–33 | HW3 |
| 10 | 任意尺寸 tiled MMULT 的邊界檢查與 divergence 分析 | 3×3／2×2 tile 逐 phase 動畫，標出「錯但合法」和越界的讀取；J×K×L 長方形矩陣；100×100、16×16 tile 的 warp-phase divergence 計數器（M tile 示範，N tile 是 HW3 自己做） | L4 p12–25、p42–48 | HW3 |
| 11 | Nsight Compute 實作 | 在 RTX 3050 上用 `ncu` 跑 loop-divergence 和 transpose 範例，讀 Summary、Speed of Light、Roofline、Warp State、Source view（SASS），用 Baseline 比較 | L4 p49–51、[02:55:01]–[03:31:01] | HW3 |

## 模組 0 診斷題
目的是找出卡在哪。出題時一次貼出 9 題，告訴學生：每題寫答案、「不會」或「猜：…」，憑現在的理解作答就好。

完成條件：9 題都有學生的回答並已批改；依下表把每題對應的模組在 progress.md 標 🟩（答對且說得出原因）／🟨（部分對）／⬜（錯或不會），同一模組有多題時取最低的；「下一步」設為第一個不是 🟩 的模組。

1. GPU 有幾千個核心，CPU 只有十幾個。那為什麼不把所有程式都丟給 GPU 跑？（M1）
2. 排順序：a 啟動 kernel、b `cudaMemcpy` device→host、c `cudaMalloc`、d `cudaMemcpy` host→device、e `cudaFree`。（M2）
3. 1000 個元素、`blockDim.x = 256`，要開幾個 block？為什麼 kernel 裡要寫 `if (i < n)`？（M3）
4. 影像寬 W、高 H，存成 1D 陣列，thread 算出 row、col 後，元素 index 是多少？（M3）
5. 100 個 thread 的 block 切成幾個 warp？為什麼 block 大小建議用 32 的倍數？（M4）
6. 同一個 warp 裡偶數 thread 走 `if`、奇數走 `else`，會發生什麼事？（M4）
7. 一個程式有 10% 必須依序執行，給無限多核心，最多快幾倍？（M5）
8. SAXPY `y[i] = a*x[i] + y[i]`（float）：每個元素幾 FLOP、讀寫幾 bytes、AI 多少、memory-bound 還是 compute-bound？（M5）
9. shared memory 和 global memory 差在哪？tiled MMULT 為什麼要 `__syncthreads()`？（M6）

## 之後的課（syllabus，未上）
- HW3 已在 L4 發布：Control Divergence & Tiled MMULT improvements & NCU profiling，截止 11/6（五）11:59 PM PST（Canvas 11810628），對應模組 8–11。
- HW4（11/10）：去年是 memory access patterns、corner turning（coalescing）。

## 診斷題答案（批改時才讀，只給學生看批改結果）
1. GPU 擅長大量相同、互相獨立的工作（throughput）；單一工作的 latency、分支多的邏輯、序列部分 CPU 比較快。資料還要在 host 和 device 之間搬，小工作不划算。
2. c d a b e。
3. 4 個（ceil(1000/256)）；共 1024 個 thread，最後 24 個超出範圍，`if` 防止越界讀寫。
4. `row*W + col`（row-major）。
5. 4 個 warp，最後一個只有 4 個 active thread，其他 28 個 lane 浪費。
6. Divergence：兩條路徑依序執行，每條路徑執行時另一半 lane 被 mask 閒置，效率約減半。
7. 10×（Amdahl：1/f，f = 0.1）。
8. 2 FLOP（一乘一加）；讀 x、y 各 4 B、寫 y 4 B，共 12 B；AI = 1/6；遠低於 T4 的 ~25 FLOP/B，memory-bound。
9. Shared 是 SM 上的 on-chip SRAM、block 內共用、由程式管理、快很多；global 是 DRAM、大但慢、host 也能存取。每個 phase 要兩次：LOAD 後防 RAW（tile 搬完才能用），USE 後防 WAR（大家用完才能覆寫下一個 tile）。
