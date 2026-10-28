# GPU 課程地圖

> 教材正本：`gpu/lectures/<date>/`（notes.md、slides.txt、transcript.vtt）、`gpu/hw/<hwN>/`。
> 已涵蓋到：L3（2026-10-20）。L4（2026-10-27）錄影還沒抓，抓到後在下面加模組。

| # | 模組 | 互動頁點子 | 課程來源 | 作業 |
|---|---|---|---|---|
| 0 | 診斷 | 對話裡 8 題小測 | L1–L3 | — |
| 1 | CPU vs GPU、為什麼要平行 | 1 個大核心 vs 幾千個小核心處理同一張圖的動畫；latency vs throughput | L1、L3 p11–13 | HW0 |
| 2 | 一個 CUDA 程式的完整流程 | 拖曳排序 host/device 步驟；`nvcc` 編譯流程（.cu → PTX → SASS）；host 和 device 記憶體是兩塊 | L1、L2 | HW0、HW1 |
| 3 | Grid / block / thread 對應到資料 | 調 gridDim、blockDim，看每個 thread 負責哪一格、哪些越界被 `if` 擋掉；2D/3D 攤平 | L2 | HW1 |
| 4 | SIMT、warp、divergence | block 切成 warp 的動畫；32 lane 遇到 `if` 時一半閒置；zero-overhead 切換 | L3 p4–10 | HW3 預習 |
| 5 | 效能理論 | Amdahl 滑桿（f、P）；AI 計算器；可拖點的 roofline（T4、H100、RTX 3050） | L3 p11–31 | HW2 P1–P2 |
| 6 | 記憶體階層、tiling、shared memory | 記憶體金字塔（延遲／容量）；tiled MMULT 的 phase 動畫，即時數 GMEM load；`__syncthreads()` 拿掉會怎樣 | L3 p37–74 | HW2、HW3 |
| 7 | 拆解 HW2 | Gaussian blur 三種寫法逐行對照；用 `gpu/hw/hw2/results/` 的實測和 ncu 數據讀 roofline | L3 p75–76、HW2 spec | HW2 |

## 模組 0 診斷題
目的是找出卡在哪，不是考試。告訴學生：每題寫答案、「不會」或「猜：…」，不要查資料。批改後依結果決定從哪個模組開始、哪些可以跳過，並寫進 progress.md。

1. GPU 有幾千個核心，CPU 只有十幾個。那為什麼不把所有程式都丟給 GPU 跑？（M1）
2. 排順序：a 啟動 kernel、b `cudaMemcpy` device→host、c `cudaMalloc`、d `cudaMemcpy` host→device、e `cudaFree`。（M2；答案 c d a b e）
3. 1000 個元素、`blockDim.x = 256`，要開幾個 block？為什麼 kernel 裡要寫 `if (i < n)`？（M3；4 個，最後一個 block 有 24 個 thread 越界）
4. 影像寬 W、高 H，存成 1D 陣列，thread 算出 row、col 後，元素 index 是多少？（M3；`row*W + col`）
5. 100 個 thread 的 block 切成幾個 warp？為什麼 block 大小建議用 32 的倍數？（M4；4 個，最後一個只有 4 個 active thread）
6. 同一個 warp 裡偶數 thread 走 `if`、奇數走 `else`，會發生什麼事？（M4；兩條路徑依序執行，各有一半 lane 閒置）
7. 一個程式有 10% 必須依序執行，給無限多核心，最多快幾倍？（M5；Amdahl，10×）
8. SAXPY `y[i] = a*x[i] + y[i]`（float）：每個元素幾 FLOP、讀寫幾 bytes、AI 多少、memory-bound 還是 compute-bound？（M5；2 FLOP、12 B、1/6、memory-bound）
9. shared memory 和 global memory 差在哪？tiled MMULT 為什麼要 `__syncthreads()`？（M6；兩次：LOAD 後防 RAW、USE 後防 WAR）

## 之後的課（syllabus，未上）
- HW3（11/3）：去年是 control divergence、tiled MMULT、NCU profiling。
- HW4（11/10）：去年是 memory access patterns、corner turning（coalescing）。
