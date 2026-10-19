# GPU Lecture 2 — 2026-10-13（CUDA 編譯流程、資料／index space 維度、CUDA kernel 語言、Turing T4、Nsight 除錯、HW1）

> 來源：transcript（Teams 自動逐字稿 `transcript.vtt`，2554 cues，00:00:11–03:37:25，約 3 小時 37 分）、slides（Au26_GPU-Compute_Lecture2.pdf，55 頁）、閱讀章節：Reading Set #2 = PMPP 4th ed. Ch3 §1–4、Ch4 §1–4（對應 L2、L3）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：little Indian → little-endian；Cuban / Kubin / kubin → cubin；SIAS → SASS；Malak → malloc；Coop dump / kuobj dump → cuobjdump；dump in → dumpbin；PECOF / cough PE → PE-COFF；Beck ad → vecadd；Gen. code → `-gencode`；dash arc → `-arch`；touring → Turing；Ada Loveless → Ada Lovelace；N site / and site → Nsight；Takuda → to CUDA；sam's → SMs；IN32 → INT32；nips and risk → MIPS、RISC；"Say, IEEE" → 索引變數 i；"CUDA 3.4 or 13.4 runtime" → 投影片 p6 寫 CUDA Toolkit 13.x；Devika 應為助教名字（拼法未確認）。
>
> 錄影注意：[00:29:00] 附近老師約 10 秒處於靜音；休息時忘記停錄，[01:17:09]–[01:25:02] 是空白。

## 重點摘要

1. **CUDA 平台與編譯流程**（p3–p6）
   - Host 端有兩套 API：Runtime API（`cuda_runtime.h`、`cudart`）和 Driver API（`cuda.h`）。Runtime 疊在 Driver 之上。本課先用 Runtime API，因為比較簡單。
   - `nvcc` 把 `.cu` 拆成兩部分：host code 交給 host compiler（Windows 用 `CL.exe`），device code 由 nvcc 自己編。
   - Device code 先變成 PTX（virtual architecture `compute_XY`，文字格式的中間表示），再經 `ptxas` 組譯成 cubin／SASS（real architecture `sm_XY`，ELF 格式）。
   - 所有 PTX 和 cubin 會一起打包進執行檔的 fatbin section。
   - 執行時 driver 先找符合裝置的 cubin。找不到就把 PTX JIT 編譯成當下裝置的版本，並快取結果。
   - PTX 只能往新架構相容（forward compatible），不能往舊架構跑。
   - T4 是 CC 7.5，要編 `compute_75` / `sm_75`。
   - 檢查執行檔內容的工具：`dumpbin /headers`（看 `.nv_fatbin` section）、`cuobjdump -lelf`、`cuobjdump -lptx`。
2. **Demo：AWS WorkSpaces 上的 Visual Studio**
   - 建 CUDA 專案。
   - 在 Project Properties → CUDA C/C++ → Device → Code Generation 設定 `compute_XX,sm_XX`，多組之間用分號隔開。
   - 選 x64。
   - 用 x64 Native Tools Command Prompt 執行 `nvidia-smi`。T4 有約 16 GB 記憶體。
3. **資料維度與記憶體**（p7–p11）
   - 應用領域本身的維度可能是 2D 或 3D，但記憶體是平的 1D 位址空間（base + offset），所以多維資料一定要先 linearize 才能存。
   - C-style 陣列最左邊的 index 移動最慢，最右邊的移動最快。
   - C、CUDA、OpenCL 都採 row-major：`M(row,col) = row*W + col`。到了 3D 是 `W*H*z + W*y + x`。
   - x86 是 little-endian。
   - Device 端配置 linear memory 用 `cudaMalloc`，搬資料用 `cudaMemcpy` 並指定方向（HtoD、DtoH、DtoD）。另外有 CUDA Arrays（給 texture 用，之後才會講）。
4. **計算的 index space**（p12–p16）
   - Grid → block → thread，每一層都可以是 1D、2D 或 3D，用 `dim3` 設定，沒指定的維度預設是 1。
   - 每個 kernel instance 啟動後，從內建變數 `threadIdx`、`blockIdx`、`blockDim`、`gridDim` 得知自己是哪一個 thread。這些值存在各自的 register 裡。
   - 1D global ID：`blockDim.x*blockIdx.x + threadIdx.x`。
   - 2D／3D 公式見 p13、p14。
   - Grid 和 block 的維度可以不同，例如 2D grid 搭配 3D block（p15）。
   - 要分清楚三個空間：application space、computational index space、hardware execution resources。
5. **邊界處理與 warp divergence**（p17–p18）
   - 範例：62×76 的影像用 16×16 block 覆蓋，grid 是 4×5 個 block，也就是 64×80 個 thread。
   - 超出影像的 thread 必須用 `if` 擋掉。
   - Warp 是 32 個 thread，以 lock-step 方式一起執行。
   - 邊界區（region 2–4）會產生 control-flow divergence。影像越大，邊界造成的影響比例越小。
6. **範例 kernel**（p19–p23）
   - RGB → grayscale：每個 thread 負責一個獨立的輸出 pixel，完全平行。
   - Box blur：每個 thread 讀一整個鄰域，但只寫一個 pixel。只讀的資料重疊沒有問題，要小心的是寫入。
   - Blur 有兩層邊界檢查：一層檢查輸出位置是否有效，一層檢查讀進來的鄰域 pixel 是否有效。
7. **Host 端流程**（p24–p27）
   - Explicit memory management 的順序：`cudaMallocHost`（pinned）→ 初始化 → `cudaMalloc` → `cudaMemcpy` HtoD → `cudaMemset` → `<<<grid, block>>>` launch → `cudaDeviceSynchronize` → `cudaMemcpy` DtoH → `cudaFree` / `cudaFreeHost`。
   - Block 數量的算法：`(n-1)/256+1`、`ceil(n/256.0)`、`cuda::ceil_div`。
8. **3D 範例、grid-stride loop、grid sizing**（p28–p31）
   - MRI 資料是 1001×1001×511，補到 1024×1024×512，用 8×8×8 的 block，共 1,048,576 個 block。
   - Grid-stride loop：thread 數比資料少時，每個 thread 以 `blockDim.x*gridDim.x` 為步長走過資料。
   - 經驗法則：threads/block 取 32 的倍數。
9. **CUDA kernel 語言**（p32–p36）
   - Vector types：`float4` 等，用 `.x/.y/.z/.w` 取值，用 `make_float4` 建構。
   - Function execution space：`__global__`（在 device 上執行、由 host 呼叫，回傳型別必須是 void）、`__device__`、`__host__`。
   - Memory space qualifiers：`__device__`、`__shared__`、`__constant__`。
   - 內建變數 `warpSize` 是 32。
10. **結果驗證**（p37）
    - 浮點數加法沒有結合律，CPU 和 GPU 算出的結果可能不完全相同。
    - 判斷方式：`|cpu - gpu| <= max(aTol, rTol*max(|cpu|,|gpu|))`。
    - 建議值：FP32 用 rtol 1e-5、atol 1e-6；FP64 用 rtol 1e-12、atol 1e-15。
11. **Turing T4**（p38–p44）
    - CC 7.5，每個 SM 有 64 FP32 + 64 INT32 cores，分成 4 個 processing block，每個 block 有 16 FP32 cores。
    - 所以一個 warp 要分兩個 cycle 才能執行完。
    - 硬體限制見 p42：40 個 SM，每個 SM 最多 16 個 block、1024 個 thread。
    - Transparent scalability：block 之間不能假設執行順序。
12. **Thread block 粒度範例**（p52，Volta）
    - 4×4 的 block 只能用到 25%。
    - 8×8 的 block 可以用滿 100%。
    - 30×30 的 block 約 88%。
13. **Nsight VSE Demo**（p54）
    - 要用 Debug build，從 Extensions → Nsight → Start CUDA Debugging 啟動。
    - 可以看 Warp Info、Lanes、GPU registers，也可以在不同 thread 之間切換。
    - Kernel 裡可以用 `printf`。
    - `--resource-usage` flag 會列出每個 kernel 用到的 register 和 shared memory。
14. **本堂只在投影片上、沒有講到的內容**
    - p45–p51：Von Neumann、Flynn's taxonomy、SIMD vs SIMT、warp scheduling。老師在 [03:19:01] 說先跳過 warp 結構這一段。
    - p53：Thread Block Clusters，老師在 [03:23:07] 說以後再講。
    - 這幾頁預計 L3 會講。

## 名詞解釋

| 名詞 | 說明 |
|---|---|
| CUDA Runtime API / Driver API | Host 端的兩套 API。Runtime 比較高階，會替你做一些決定。Driver 比較細，可以自己管 context 和 module loading。本課先用 Runtime。 |
| nvcc | NVIDIA 的 CUDA compiler，負責 device code，並呼叫 host compiler 處理其餘部分。屬於 offline compilation；runtime JIT 編譯用的是 nvrtc。 |
| PTX | 文字格式的虛擬 ISA／中間表示，對應 virtual architecture `compute_XY`。可以由 driver JIT 編成新架構的 native code。 |
| cubin / SASS | 針對某個 real architecture（`sm_XY`）的原生機器碼，ELF 格式。SASS 是 NVIDIA 的組合語言。 |
| fatbin | 執行檔裡的一個 section，裝著多個 cubin 和 PTX 版本。 |
| Compute Capability (CC) | GPU 的 major.minor 版本。x.0 是一代架構的基準版本。T4 是 7.5。 |
| JIT compilation | 執行時由 driver 把 PTX 編成當下裝置的 native code。會拖慢第一次啟動，但結果會被快取起來。 |
| row-major / column-major | 把 2D 資料攤平成 1D 的兩種方式。row-major 是一列接一列存放，C、CUDA、OpenCL 都用這種。 |
| little-endian | 多 byte 數值在記憶體裡從最低位的 byte 開始存。x86 是 little-endian。 |
| `dim3` | 長度 3 的整數向量 struct，用來指定 grid 和 block 的大小。沒指定的分量預設是 1。 |
| grid / thread block / thread | CUDA 的三層 index space。OpenCL 裡分別叫 NDRange、work-group、work-item。 |
| global (linear) thread ID | 把 block index 和 thread index 合起來，算出每個 thread 在整個 grid 中獨一無二的 1D 編號。 |
| warp | 32 個連續 thread 組成的排程單位，以 lock-step 方式執行。Warp 大小是實作決定，不屬於 programming model。 |
| warp divergence | 同一個 warp 裡的 thread 走了不同的 control-flow 路徑，例如邊界檢查的 `if`，導致執行被拉長。 |
| wave | 某個時間點同時在整張 GPU 上執行的那一批 thread block。 |
| grid-stride loop | Kernel 內的迴圈，每次前進 `blockDim.x*gridDim.x`，讓較少的 thread 就能處理大量資料。 |
| pinned memory | 用 `cudaMallocHost` 配置、不會被 swap 出去的 host 記憶體。HtoD／DtoH 傳輸比較快，也可以做非同步傳輸。 |
| `cudaDeviceSynchronize` | Kernel launch 是非同步的。這個 blocking call 會等 GPU 上先前的工作全部做完才返回。 |
| `__global__` / `__device__` / `__host__` | Function execution space specifier。`__global__` 是 kernel：在 device 上執行、由 host 呼叫、回傳 void。`__device__` 只能被 device code 呼叫。`__host__` 是預設值。 |
| transparent scalability | Block 之間沒有固定的執行順序，硬體可以自由分配，所以同一份 grid 在 SM 比較多的 GPU 上會自動跑得比較快。 |
| SM / processing block | Streaming Multiprocessor。T4 的每個 SM 有 4 個 processing block（sub-partition）。 |
| occupancy | SM 上 thread／warp 槽位被用到的比例。p52 用 Volta 的 25%、100%、88% 當例子。 |
| Nsight VSE | 整合在 Visual Studio 裡的 CUDA debugger，可以設 kernel breakpoint，看 warp、lane 和 register。 |

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

**課務、AWS、Teams**
- [00:01:00] [00:02:04] 課程規定和時程以 Canvas 為準；作業討論放 Teams 的作業 channel。老師和 TA 會盯這個 channel。請不要私訊，因為大家常有同樣的問題，放在公開 channel 每個人都能看到。
- [00:02:04] [00:03:03] AWS 有問題也貼到 Teams channel。
- [00:03:11] 把 Google Drive／OneDrive 連到 AWS instance 的功能目前還不能用，要等 UW IT 核准相關權限。
- [00:03:44] [00:04:31] 暫時的做法：在 instance 裡開 Chrome 或 Edge，登入自己的雲端硬碟，把檔案存過去。
- [00:04:43] Instance 關掉後資料不會保留，每次結束前都要備份。用完要選 Disconnect，把資源讓給其他同學。
- [00:09:03] 老師說 HW1 下課後就會發布，題目是把 vector addition 的概念擴展到 1D、2D、3D，用來練習 indexing 和不同維度的資料表示。
- [00:11:54] 這門課的第三季會介紹 Pythonic 的 GPU kernel 寫法。老師強調要同時懂低階 CUDA（甚至 PTX／SASS），再靠 profiling 決定哪裡值得花力氣做低階優化。
- [00:14:00] 本課大部分時間在 AWS WorkSpaces 的 T4 上做；之後會一直用到 Visual Studio 整合的 Nsight debugger。

**編譯與 Visual Studio**
- [00:24:00] [00:25:01] 所有 PTX 都向前相容，舊的 virtual arch 一定能在新 GPU 上跑，但用不到新硬體功能（例如 9.0 的新一代 tensor core）。一般建議在執行檔裡附一份 PTX。
- [00:27:02] [00:28:01] `-arch`、`-code`、`-gencode` 的語法很敏感，文件也寫得不太清楚。可以在 Visual Studio 的 Project Properties 設好，再去看它產生的命令列，用來確認語法正確。
- [00:31:00] [00:32:02] 建議做法：開一個主要的 solution（例如 GPU compute），底下每份作業各開一個 project（homework 1、homework 2…），之後把整個資料夾打包就很方便。
- [00:35:59] 第一次 build 建議用 Rebuild。平台要選 x64，不要選 x86。要除錯就用 Debug build。
- [00:43:21] 現場示範：只編 8.0 的版本拿到 T4（7.5）上跑，出現 "no kernel image is available for execution on the device"。遇到架構相關的編譯或執行錯誤，先回 Project Properties 確認編譯目標是 7.5 或更舊的架構。
- [00:44:26] JIT 的代價通常只有幾秒，driver 會把結果快取起來。

**資料配置與 index**
- [00:50:06] 最左邊的 index 移動最慢，最右邊的移動最快。
- [00:52:04] 在 kernel 裡，只要陣列大小不是編譯期就確定的（包括 host 傳進來的 buffer），就不能用 `a[i][j]` 這種多維語法，一定要自己算出攤平後的 offset。
- [00:57:00] [00:58:05] 習慣寫 M(row, col) 等於寫 M(y, x)，順序和 (x, y) 是反的。老師說自己也常搞混，提醒大家寫 index 時特別小心。
- [01:00:06] Row-major 下 x 是移動最快的 index。z（slice）是最慢的。
- [01:04:00] 「stride」在不同情境意思不同：資料列寬的 stride 和 thread 的 stride 是兩回事。
- [01:10:01] [01:11:00] 變數名稱用 `h_` 和 `d_` 前綴分清楚 host 和 device 資料。在 host 上直接存取 device 指標，或把 host 資料直接傳給 device，程式都會壞掉。

**L1 slide 55 錯誤處理 macro 的更正（HW1 會用到）**
- [01:12:01] [01:12:09] L1 第 55 頁的 CUDA error checking macro 示範呼叫語法有錯。
  - 正確用法：第一個參數放 error code，第二個參數放一段字串，標出錯誤發生在哪個函式。
  - 少了第二個參數，macro 會爆出一大堆 compile error。
- [01:13:03] [01:13:13] 更新後的 L1 投影片放在網站 Files 的 "lecture 1 updated" 下。

**問卷與 office hours**
- [01:13:48] TA（逐字稿寫 Devika）在 chat 貼了問卷連結。問卷用來排 TA office hours，也調查大家有沒有收到 AWS 邀請、能不能登入。
- [01:14:01] [01:15:02] 老師的建議：
  - 作業通常是隔週二截止，填 office hours 時間時，想想自己通常什麼時候寫作業。
  - Office hours 可以排在週五（週末開工前）或週一（截止前）。
  - 沒有 office hours 的時候就貼 Teams，希望幾小時內回覆。
- [01:25:02] AWS 登入不了「幾乎是 showstopper」，除非有自己的 GPU，所以問卷一定要填。

**Index space、warp、獨立性**
- [01:31:04] [01:32:04] 比喻：每個 kernel instance 像《星際大戰》裡睡著的 clone，醒來第一件事就是查自己的 thread index 和 block index，弄清楚自己是誰。
- [01:35:01] p13 的 1D 公式不能直接套在 2D 的圖上：會算出 5，正確答案是 7。
- [01:41:09] [01:42:04] 用 2D 公式算 block (1,0)、thread (1,1)，得到 13。老師中途也算錯一次再更正，說明這種計算很容易反過來。
- [01:55:00] Index 公式會在作業裡練到，到時把數字代進去驗證就好。
- [01:57:00] Host 端 `dim3` 的順序是 (x, y, z)，和 (slice, row, col) 的寫法相反，別搞混。
- [02:09:00] [02:11:04] 超出資料範圍的 thread 一定要擋掉，不能存取不存在的資料。這個 `if` 會造成 control-flow divergence。
- [02:12:02] [02:13:01] Warp 是 32 個 thread，以 lock-step 執行，這是 GPU 平行化的根本。
- [02:16:00] [02:17:04] Grid 最好以整數個 warp 為單位來定義。資料越大，邊界效應越可以忽略。
- [02:23:03] [02:24:00] 關鍵在每個 thread 寫到自己專屬的輸出 pixel，這樣就不需要 synchronization 或 barrier，也不會有 race condition。
- [02:26:07] [02:27:01] 只讀的資料可以被很多 thread 同時重疊讀取，要小心的是寫入。
- [02:25:03] 有同學問為什麼轉成 unsigned char：影像是 8-bit unsigned，寫回之前一定要 cast 成正確的型別。
- [02:31:35] [02:34:28] 老師說 blur 的雙層迴圈「你們會在作業裡做」，而且作業會做 2D Gaussian-weighted blur，不是投影片上權重全為 1 的版本。這和 HW1 在 Canvas 上的標題對不起來，見「還要釐清的問題」。
- [02:37:00] 每個 thread 的計算量會隨 blur size 增加。之後會把這個量正式化，作為評估 kernel 的指標。

**Host 端流程**
- [02:39:02] Host 記憶體建議用 `cudaMallocHost`（pinned），不要用 `malloc`。傳輸比較快，之後也能做非同步傳輸。
- [02:40:16] 投影片 p24 用的是 `cudaMemcpyDefault`，但老師說不建議依賴它，至少一開始要明確寫出 HostToDevice、DeviceToHost。
- [02:43:01] 算 grid 大小的程式只會跑一次，寫法不影響效能，真正要在意的是 kernel 內的程式碼。
- [02:45:07] [02:47:00] Kernel launch 是非同步的，會立刻返回。沒有先呼叫 `cudaDeviceSynchronize` 就把結果複製回來，可能拿到只算了一半的 buffer。
- [03:00:36] p31 的 grid sizing 經驗法則「可能有點樂觀」，參考就好，不是鐵律。
- [03:01:00] HW0 的 device query 查到的參數就是這些資源限制。之後會學怎麼依裝置在 runtime 動態調整。

**驗證（作業一定會用到）**
- [03:08:01] [03:08:37] 結果驗證一定會出現在作業裡。老師的原則：kernel 再快，算錯就是垃圾。
- [03:09:01] [03:10:02] CPU 和 GPU 的浮點結果不一定逐 bit 相同，所以要用 absolute／relative tolerance 判斷。
- [03:11:00] 先寫 CPU baseline，同時用來量時間和驗證結果，而且你得確定 CPU 版本本身是對的。

**T4 與資源**
- [03:13:00] 在 AWS 上查 compute capability 會得到 7.5（T4）。
- [03:14:01] [03:14:14] 每個 processing block 只有 16 個 FP32 cores，一個 warp 要分兩個 cycle 執行。
- [03:17:05] 這些硬體限制不可能一次就消化，之後會用 profiler 一步一步看。
- [03:18:00] Transparent scalability：同一份 grid 在資源越多的裝置上跑得越快，但要拿到最佳效能還是得往下深入。
- [03:20:01] [03:22:05] 用 Volta 算 4×4、8×8、30×30 的利用率。另外提醒：threads/block 最好湊成連續 32 個一列，例如 4×16、2×32 這類形狀可能更好。

**除錯與 printf**
- [03:23:07] Kernel 裡的 `printf` 適合看基本數值，但不要用來查 race condition 或 deadlock，也不要用在 profiling，因為它會讓執行序列化，結果會被扭曲。
- [03:24:03] 要能除錯，就要用 Debug build，而且編譯目標要改回 7.5，否則 kernel 根本不會跑。
- [03:25:00] [03:27:01] 要除錯 device code，一定要從 Extensions → Nsight → Start CUDA Debugging 啟動。停在 kernel 的 breakpoint 後，可以開 Warp Info 和 Lanes 視窗查看。範例只有 5 個 active thread，其餘 27 個被 mask 掉。
- [03:31:32] [03:32:01] Kernel `printf` 的輸出順序沒有保證，作業會進一步探討這件事。老師的理解是，單一 warp 內通常是依序的，但這屬於實作細節，NVIDIA 文件沒有寫。
- [03:32:01] `--resource-usage` flag 會顯示每個 kernel 用到的 register 和 shared memory，之後做資源分析時很重要。

**HW1 總覽**
- [03:35:01] [03:35:05] HW1「下週二」（也就是 Lecture 3 那天）截止。學習目標：
  - 使用 error checking macro
  - 寫 multi-dimensional grid 和 indexing 的 kernel
  - 自己管理 host 和 device 的記憶體配置與搬移
  - 用 multi-dimensional execution configuration 做 kernel launch
  - 練習 2D／3D 的 row-major 索引
  - 處理 out-of-bounds 邊界檢查
  - 在 host 端用 tolerance 驗證結果
- [03:36:02] [03:36:12] HW1 可能也有 printf 的練習，但老師不確定是不是在 HW0。老師強調 printf 在 kernel 裡很好用，只是要避開 race／同步問題和 profiling。
- [03:36:02] TA office hours 預計一兩天內開始。Teams channel 會有人盯。如果有沒聽到的部分，請回去看錄影。

## 和作業 / 考試的關聯

- **HW1：SAXPY, 2D & 3D Matrix addition**
  - 截止：10/20（二）5:59 PM PDT，11 分，Canvas id 11810625。
  - 投影片 p2 和 p55 寫 5:59 PM。老師在 [03:35:05] 說「下週二」，和 `assignments.md` 一致。
  - 繳交方式：online upload。投影片 p2 寫透過課程網站的 Assignments 頁面繳交。
  - 目前狀態：unsubmitted。
- **HW1 會直接用到的本堂內容**
  - 更新後的 error macro：L1 updated slide 55，見 [01:12:09]。
  - Row-major 的 2D／3D 攤平公式：p9、p14。2D 是 `W*y + x`，3D 是 `W*H*z + W*y + x`。
  - `dim3` 的 grid 和 block 配置，以及 ceil-div：p25、p26、p33。
  - 邊界檢查：p17、p22。
  - Explicit memory management 的流程：p24。改用明確的 HtoD／DtoH，不要用 Default，見 [02:40:16]。
  - `cudaDeviceSynchronize`：p26。
  - CPU baseline 加上 tolerance 驗證：p37。FP32 用 rtol 1e-5、atol 1e-6。見 [03:08:37]。
  - 編譯目標設 `compute_75,sm_75`（[00:43:21]），平台選 x64（[00:35:59]）。
- **環境**
  - AWS WorkSpaces 的雲端硬碟連結目前不能用。每次結束前用瀏覽器把檔案存到 Google Drive 或 OneDrive，然後選 Disconnect，見 [00:04:43]。
  - 建議用「一個 solution 底下多個 project」的結構管理所有作業，見 [00:31:00]。
- **HW2**
  - 依 `assignments.md`：10/27（二）5:59 PM，12 分，Canvas 尚未發布。去年的題目是 Gaussian Blur Kernels。
  - 本堂 [02:34:28] 說到的「作業要做 Gaussian blur」，很可能指的是 HW2（待確認）。p20–p23 的 blur kernel 可以當預習。
- **本堂沒有提到的事**
  - Final project（proposal 11/17）、成績比例、遲交規則都沒有講。這些資訊以 `assignments.md` 和 syllabus 為準，不是本堂的內容。
  - 這門課沒有考試，成績是 HW 50%、Final Project 50%（依 `assignments.md`）。
- **閱讀**
  - Reading Set #2：PMPP Ch3 §1–4（multidimensional grids、data mapping、image blur）、Ch4 §1–4（GPU 架構、block scheduling、warp）。
  - 本堂跳過的 p45–p51（SIMD／SIMT、warp scheduling）對應 Ch4，L3 前可以先讀。
- 提醒：課程 AI 政策你已表示不介意。這份筆記只整理概念和公式，沒有寫 HW1 的解答程式碼。HW1 的實作請自己完成。

## 還要釐清的問題

1. **Gaussian blur 屬於哪份作業？**
   - 老師在 [02:31:35] 說 blur 迴圈會在「homework one」裡延伸，在 [02:34:28] 說作業要做 Gaussian-weighted blur。
   - 但 HW1 在 Canvas 上的標題是 "SAXPY, 2D & 3D Matrix addition"，p55 的學習目標也沒有提到 blur。
   - `assignments.md` 記錄去年的 HW2 才是 Gaussian Blur。
   - 老師在 [00:09:03] 也把 HW1 描述成 1D、2D、3D 的 vector addition，和 Canvas 標題一致，所以 blur 那段比較可能指的是 HW2。但還沒確定。
   - 需要看 HW1 的作業說明，或在 Teams 上問。
2. **printf 的題目在 HW1 還是 HW0？** 老師在 [03:36:02] 自己也不確定。另外 [03:31:32] 說作業會探討 printf 的輸出順序，需要對照 HW1 的作業說明。
3. **投影片 p17 的 x／y 是否寫反？** `dimGrid(ceil(m/16.0), ceil(n/16.0), 1)` 把 m（列數 62）放在 x 的位置。老師在 [02:06:06] 承認寫錯了。p26 的寫法 `DimGrid((n-1)/16+1, (m-1)/16+1, 1)` 才是正確的。依 BOOTSTRAP §3，以逐字稿為準。
4. **投影片之間的數字不一致**
   - p39 寫 T4 的 L2 是 6 MB，p42 的 device query 結果是 4194304 bytes，也就是 4 MB。
   - p44 寫「每個 SM 最多 32 個 block」，但同一頁和 p42 都寫 Turing 的 SM 最多 16 個 block、1024 個 thread。32 這個數字應該是 Volta 的。
   - p52 的範例用的是 Volta（2048 threads／32 blocks），換成 T4 的限制要重算。
5. **p13 的 2D 公式和老師口頭推導的對照**：老師先用 1D 公式算出 5，說不對（[01:35:01]），之後用 2D 公式算出 13（[01:41:09]）。p13 的公式代入 block(1,0)、thread(1,1) 也得到 13，和投影片一致。建議作業前自己再驗算一次 3D 的版本（p14）。
6. **[03:12:01] 有同學問了跟 thread 有關的問題**（逐字稿寫 "thread separate"，聽不清楚），老師說之後再回答。後來 [03:31:32] 回答的可能就是這題（printf 和執行順序），但無法確定。
7. **AWS 雲端硬碟連結什麼時候會修好？**（[00:03:11]：要等 UW IT 核准，老師希望「幾天內」完成。）
8. **TA office hours 的時間和 Teams channel 的名稱** 等問卷結果出來才知道（[01:13:48]、[03:36:02]）。
9. **Visual Studio 版本**：投影片 p6 寫 Visual Studio 2026、CUDA 13.x，p54 寫 "In VS 22"，逐字稿是 "CUDA 3.4 or 13.4 runtime"（[00:30:03]）。實際版本要在 AWS 上確認。
