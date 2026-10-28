# GPU HW3：Control Divergence & Tiled MMULT improvements & NCU profiling

> 原文：[spec.md](spec.md)（[Canvas assignment 11810628](https://canvas.uw.edu/courses/1917398/assignments/11810628)；PDF 原檔 [spec.pdf](spec.pdf)，Canvas file 155100870「Homework #3 (HW3) - Au26 - GPU Compute .pdf」）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-11-06（五）11:59 PM PST**（Canvas `due_at` 2026-11-07T07:59:59Z、PDF p1「DUE: 6 November 2026, 11:59 PM」、L4 口頭 [00:09:02]、`assignments.md` 一致）；lock 12/14。L4 投影片 p52 還寫舊的 11/03 5:59 PM，老師說那頁沒改（[03:31:01]），不採用 |
| 分數 | 12 分（HW 合計佔總成績 50%；原文沒有寫各部分配分） |
| 繳交方式 | Canvas（原文只寫「SUBMIT」，沒寫 submission type） |
| 要交的東西 | 1. Questions I–V 和 Analysis（control divergence）的答案，**要附過程和理由**<br>2. CUDA host application 原始碼：**只交 `.cu`、`.cpp`、`.h`**，不要交 project／solution 檔和 build 產物<br>3. CUDA kernel functions（可以和 host code 放同一個 `.cu`）<br>4. 所有測試案例、global＋shared kernel 的 NCU profiling 結果，附算出的 kernel execution time 和 kernel instruction intensity<br>5. 一頁 PDF 或 Word：MMULT kernel、launch configuration、矩陣大小、FMAD 選項的 profiling 分析討論，附 NCU 報告（含 baselines）截圖和各 kernel／各大小的 roofline 圖<br>（另外程式練習 Control Divergence 步驟 d 要存 `*.ncu-rep`，SUBMIT 清單沒單獨列，見「還不確定的地方」） |

## 學習目標
（PDF p1「Learning Objectives」）
- 理解 warp 裡的 control divergence
- 實作並 profile 有 warp divergence 的 kernel
- 改進 tiled-phased MMULT kernel
- 了解 kernel launch configuration 調校
- 用 Nsight Compute **GUI** profile kernel、分析效能問題和最佳化

## 要做什麼
分三部分：Questions、Analysis（control divergence）、Programming Exercises（control divergence kernel、MMULT 變體）。

### Part 1：Questions（PDF p1–p2）
書面或打字作答，**必須寫出過程或理由才給分**。

| 題 | 在問什麼 | 選項 |
|---|---|---|
| I | SM 最多 1536 threads、最多 4 個 block，哪種 block 大小讓 SM 裡的 thread 最多 | 128／256／512／1024 threads per block |
| II | 向量加法，長度 2000，每個 thread 算一個輸出，block 512 threads，grid 裡有幾個 thread | 2000／2024／2048／2096 |
| III | 承 II，向量長度的邊界檢查會讓幾個 warp diverge | 1／2／3／6 |
| IV | 裝置每 SM 最多 64 blocks、2048 threads；下列每 SM 配置哪些可行，可行的寫出 occupancy | A. 8×128　B. 16×64　C. 32×32　D. 64×32　E. 32×64（blocks × threads/block） |
| V | 裝置每 SM 2048 threads、32 blocks、65,536 registers；每種 kernel 能否 full occupancy，不能的話寫限制因素和最大 occupancy % | A. 128 threads/block、30 regs/thread　B. 32、29　C. 256、34 |

### Part 2：Analysis — Control Divergence（PDF p2）
- 對 tiled MMULT 的 **N tile** 計算 control divergence 的影響，方法照 Lecture 4 對 M tile 的示範（L4 slides；PMPP §4.5）。
- 討論 Type 1 和 Type 2 block：
  - 各有幾個 warp-phase diverge？
  - 預期效能影響 %：Type 1、Type 2 各多少，合計多少？
- **Q**：什麼時候 warp divergence 的影響會變得很小？
- **Q**：改變 tile 大小怎麼影響 arithmetic intensity？

### Part 3：Programming Exercises（PDF p3–p6）
開頭提醒：用 NCU profile 時一律用 **RELEASE（x64）build，而且要拿掉所有 `printf`**，否則結果不正確。

#### 3.1 Control Divergence kernel（PDF p3–p4）
做完 Part 2 之後，寫簡單的 CUDA kernel 呈現 L4 講的兩種 divergence：
1. 單一 branch（control flow 一分為二）
2. 巢狀 branch（每個 warp 至少三條不同的 control path）

規定和步驟：
- kernel 不用做有意義的計算，但**每個 branch 都要寫一個輸出到 GMEM**，否則 compiler 可能把整個 branch 優化掉。
- 用 NCU 分別 profile 有／沒有 divergence 的情況：
  - a. NCU 用法參考 L4 的 demo。
  - b. 輸入資料要能**可預期地**讓 kernel diverge 或不 diverge；原文建議加一個 kernel 參數切換走 divergent 或 non-divergent 的路徑。
  - c. grid 要有足夠多的 thread 和 block，否則 NCU metric 可能不準。
  - d. 每個 divergent kernel 各存一份 `*.ncu-rep`：有 divergence、沒 divergence。
  - e. 解釋 NCU 的哪些 metric 能看出 divergence。要看的：

    | Section | Metric |
    |---|---|
    | Occupancy | Theoretical vs Achieved Occupancy |
    | Occupancy | Theoretical vs Achieved Active Warps Per SM |
    | Warp State Statistics | Avg. Active Threads Per Warp |
    | Warp State Statistics | Avg. Not Predicated Off Threads Per Warp |

  - 另外：GPU Speed of Light 裡還有哪些一般 metric 在 divergent 和 non-divergent 之間有變化？

#### 3.2 MMULT Variants（PDF p4–p5）
實作三個版本：

| 版本 | 說明 |
|---|---|
| CPU serial reference | 用來比較和驗證 |
| GPU kernel v0 | naive，全用 GMEM |
| GPU tiled/phased kernel | shared memory、含邊界檢查；支援一般非方形、維度相容的矩陣 **P: j×l、M: j×k、N: k×l**；支援 tile（= thread block）大小不是矩陣維度整數倍（PMPP Ch5.4–5.5、L3／L4 投影片） |

**驗證**：host 端程式檢查三個版本結果一致，在可接受的誤差內。
- 回答：觀察到的最大單一元素 abs error fraction 是多少？定義 `abs[Pcpu(x,y) - Gpu(x,y)] / Pcpu(x,y)`。
- 測三組大小：

  | 案例 | P | k |
  |---|---|---|
  | 1 | 100×100 | 100 |
  | 2 | 1000×1000 | 1000 |
  | 3 | 2000×3000 | 2500 |

**Profiling（每組大小）**：
- Visual Studio **Release build**，用 NCU 產生報告，看 GPU Speed of Light 的 **Roofline** 圖。
- 用 **baselines** 讓每個 kernel 版本出現在同一張 roofline 上。

**TILE_WIDTH 與 launch configuration**：
- 試 TILE_WIDTH = 8、12、16、32，block 分別是 (8,8,1)、(12,12,1)、(16,16,1)、(32,32,1)，不能超過自己 GPU 的資源限制。目前的 kernel 假設 TILE_WIDTH 和 block 維度相同（都是方形）。
- 盡量用 baselines 把全部結果放在一張 roofline 上；baseline 可以改成有意義的名字。
- 回答：哪個組合（TILE_WIDTH + block 大小）效能最好？分別看：
  - AI 最高？
  - compute throughput 最高？
  - execution duration 最短？
  - occupancy 最高？
  - 有沒有哪個設定或大小下 kernel 進入 compute-bound？
- 回答：結果會不會隨矩陣大小改變？用幾句話解釋，引用裝置資源和其他 NCU metric。

**FMAD 實驗**（P: 2000×3000、k = 2500 的最佳設定）：
- VS Project Properties → Configuration Properties → CUDA C/C++ → Command Line → Additional Options 填 `--fmad=false`（關掉 FFMA；預設是 true），按 OK。
- 重新 build Release 並用 NCU profile。
- 回答：效能有沒有變？看 AI、execution duration、compute throughput、occupancy。
- 回答：關掉 FMA 讓硬體把一道 FMA 拆成 MUL 和 ADD，對 arithmetic intensity 有什麼影響？

**ADDITIONAL QUESTIONS**（PDF p5）：
- 把 N 轉置，讓兩個輸入矩陣在記憶體裡都是 row-major，轉置的額外成本值不值得？
- TILE_WIDTH 推到 32 會用到每個 block 1024 threads 的硬體上限。每個 block 的 thread 數最大，是否保證 occupancy 最高？

## 注意事項
- 所有 Questions 和 Analysis **沒附過程或理由不給分**（spec.md p1「Questions」；p5「SUBMIT」1）。
- NCU profiling 一律 **Release（x64）build、拿掉所有 `printf`**（spec.md p3「Programming Exercises」NOTE）。L4 也強調要 profile Release、開 line info、開 ptxas verbose（`gpu/lectures/2026-10-27/notes.md` [02:58:00]、[02:59:00]）。
- NCU（GUI 也一樣）要用**系統管理員身分**執行，否則讀不到 GPU counter（`gpu/lectures/2026-10-27/notes.md` [00:59:05]、[01:00:04]）。
- Divergence kernel 每個 branch 都要寫 GMEM，避免被優化掉（spec.md p3「Control Divergence」）。
- Divergence kernel 的 grid 要夠大，NCU metric 才準（spec.md p3，c）。
- Profile 時不要同時跑其他程式（`gpu/lectures/2026-10-27/notes.md` [02:54:14]）。10/27 Teams 上有同學問 NCU 結果會不會受其他程式影響（同一 kernel 的 `dram__bytes_read.sum` 差約 5 倍），老師／TA 還沒回覆（`digests/2026-10-28.md`）。
- NCU 第一次 launch 是 warm-up，正式分析應跳過；output 檔名加 `%i` 自動編號避免覆蓋（`gpu/lectures/2026-10-27/notes.md` [03:02:03]、[03:03:01]）。
- Tiled kernel 的 `__syncthreads()` 一定要放在邊界檢查的 if 外面，否則會 deadlock（`gpu/lectures/2026-10-27/notes.md` [01:41:00]）。
- Tiled kernel 不採用 padding，要用邊界檢查處理任意尺寸（`gpu/lectures/2026-10-27/notes.md` [01:14:02]、[01:15:00]）。
- Launch configuration 要在自己 GPU 的資源限制內（spec.md p4「MMULT Variants」）。
- 原始碼只交 `.cu`、`.cpp`、`.h`，不要交 project／solution 和 build 產物（spec.md p5「SUBMIT」2a）。
- 遲交：每人 **7 個 late days**，10/27 起生效，可用在 HW；週末（六＋日）算 1 天；沒用完的每天 +0.5 分 extra credit（`gpu/lectures/2026-10-27/notes.md`「重點摘要」1，[00:09:02]–[00:11:04]）。原本 syllabus 的扣分規則：遲 1 天 -1，之後每 24h 再 -1（`assignments.md`）。
- 11/1 結束夏令時間，截止是 PST（UTC−8）。

## 和上課內容的關聯
- **Questions I、IV、V（occupancy、block／warp／register 限制）**：L4 p5–p11，occupancy 是 warps、block slots、registers、shared memory 四項的最小值；例題 A–D、Occupancy Calculator 示範（`gpu/lectures/2026-10-27/notes.md`「重點摘要」2–4，[00:57:01]–[01:13:01]）。
- **Questions II、III（grid 大小、邊界檢查的 divergence）**：L4 p38–p41 control divergence（同檔「重點摘要」8）；warp 線性化 p34–p37（「重點摘要」7）。
- **Analysis（N tile 的 divergence）**：L4 p42–p48，M tile 的 Type 1／Type 2 分析（100×100、TILE_WIDTH 16、7 phases、49 blocks，合計約 12.76%），p48 留 N tile 當 HW3 練習（同檔「重點摘要」9，[02:35:01]–[02:45:00]）。
- **Arithmetic intensity、roofline**：L3 p24–p31（`gpu/lectures/2026-10-20/notes.md`「重點摘要」7–8）；NCU 的 roofline 和 FP32／FP64 ceiling 見 L4 p50（`gpu/lectures/2026-10-27/notes.md`「重點摘要」10）。
- **Naive MMULT v0、tiled MMULT v1**：L3 p37–p42、p49–p74（`gpu/lectures/2026-10-20/notes.md`「重點摘要」10、12）。
- **通用化 tiled MMULT 的邊界檢查（J、K、L）**：L4 p12–p25；LOAD／USE／寫回三種檢查，p20–p21 的 M、N tile 條件，p22–p23 的程式碼故意沒改完，p25 的 J×K、K×L 對應（`gpu/lectures/2026-10-27/notes.md`「重點摘要」5，[01:37:01]）。p20 有筆誤，見「還不確定的地方」。
- **NCU GUI（Summary、Details、Roofline、Baseline、Raw、Source view）**：L4 p49–p51 和 demo（同檔「重點摘要」10–11，[02:55:01]–[03:31:01]）；loop divergence demo 的 Summary 直接指出 thread divergence，Warp State Statistics 的 active threads per warp 約 6、predication 後 5.6（[03:05:03]）。
- **Warp scheduling、stall reasons、waves**：L4 p27–p33（同檔「重點摘要」6），解釋 occupancy 和 duration 的差異時會用到。
- **閱讀**：Reading Set #3 = PMPP Ch5 全章；spec 指定 PMPP §4.5（divergence）、Ch5.4–5.5（tiled、邊界檢查）。

## 還不確定的地方
- **N tile 分析用的矩陣和 tile 大小**：原文只說「和 L4 對 M tile 的做法一樣」，沒指定大小；L4 的示範是 100×100、TILE_WIDTH 16，推測沿用。
- **「global + shared kernels」**（SUBMIT 4）：HW3 的 kernel 是 naive v0（GMEM）和 tiled（SMEM），應該就是指這兩個；措辭沿用 HW2。
- **kernel execution time 和 instruction intensity 怎麼算**（SUBMIT 4a）：HW3 原文沒定義，HW2 步驟 25 的公式是 `smsp__cycles_elapsed.sum / smsp__cycles_elapsed.sum.per_second` 和 `smsp__inst_executed.sum / dram__bytes.sum`（見 [hw2/README.md](../hw2/README.md)「3.5」）。這次要用 GUI，NCU 的 Duration 也可以直接讀，原文沒說用哪個。
- **`*.ncu-rep` 要不要交**：3.1 步驟 d 說要存，SUBMIT 4 說交「NCU profiling results」，沒明說檔案格式。
- **SUBMIT 5「a page」**：要放的截圖和 roofline 圖很多，一頁可能放不下；原文沒說頁數上限。
- **abs error fraction 分母是 0**：公式除以 `Pcpu(x,y)`，元素值為 0 時沒定義，原文沒講怎麼處理；誤差容許值（tolerance）也沒給。
- **TILE_WIDTH 12**：(12,12,1) = 144 threads，不是 32 的倍數，和 L4 的經驗法則（block 大小是 32 的倍數，`gpu/lectures/2026-10-27/notes.md`「重點摘要」3）不同；原文仍列為要試的設定。
- **用哪個 GPU**：原文說「your specific GPU device」，沒指定。課程環境是 AWS WorkSpaces 的 T4（`sm_75`，HW2 原文）。
- **`--fmad=false` 的設定路徑**是 Visual Studio 的；不用 VS 的話對應 `nvcc --fmad=false`（自行推論）。
- **L4 投影片 p20 的筆誤**：M tile 的 1D index 和條件應該用 M 的寬度（[01:32:02]、[01:34:06]）。**已確認**：10/28 上傳的 `Au26_GPUCompute_L4_w_notes.pdf`（file 155143699）把 p20 改成 `M[Row*M_WIDTH + p*TILE_WIDTH+tx]`，條件也手寫改成 `(Row < M_HEIGHT) && (p*TILE_WIDTH+tx < M_WIDTH)`。註解版的其他重點見 `gpu/lectures/2026-10-27/notes.md`「講義手寫註解」，例如 p23 的「generalize! TODO」，以及 `__syncthreads()` 要放在 if 外面。
- **Late days 和原本扣分規則怎麼併用**：老師沒說；late day 用完後是否回到每 24h -1，等 Canvas 公告（`gpu/lectures/2026-10-27/notes.md`「還要釐清的問題」3）。
- **原文 p5 ADDITIONAL QUESTIONS 最後一個 bullet 是空的**（只有「○」）。
- **繳交方式和配分**：原文沒寫 Canvas submission type，也沒寫各部分佔幾分。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-10-28 | 第一次整理 |

GPU 課禁止用 AI 產生作業解答
