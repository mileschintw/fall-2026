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

## 之後的課（syllabus，未上）
- HW3（11/3）：去年是 control divergence、tiled MMULT、NCU profiling。
- HW4（11/10）：去年是 memory access patterns、corner turning（coalescing）。
