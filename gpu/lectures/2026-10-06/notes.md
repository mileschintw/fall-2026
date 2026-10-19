# GPU Lecture 1 — 2026-10-06（課程介紹與行政、AWS VDE、GPU 歷史、平行化概念、CUDA 入門、HW0）

> 來源：transcript（Teams 自動逐字稿 `transcript.vtt`，1897 cues，00:00:03–02:42:10，約 2 小時 42 分）、slides（Au26_GPU-Compute_Lecture1_updated.pdf，Canvas file 154353784，62 頁）、閱讀章節：Reading Set #1 = PMPP 4th ed. Ch1–2（對應 L1、HW0）。逐字稿是自動產生，專有名詞可能聽錯。
>
> **錄影缺頭**：上課 6:30 PM 開始，錄影到 6:48 PM 才開始，所以前約 18 分鐘沒有逐字稿。這段大致對應 p1–p3（歡迎、About me），逐字稿從 p3 的尾巴開始。老師在 [02:39:00] 說自己忘了開錄影，是某位同學幫忙開的，之後會設定自動錄影。
> 時間對照：逐字稿 [00:00:00] ≈ 6:48 PM PDT。驗證：[00:42:02] 老師說「現在大約 7:30」，[02:39:00] 說「現在 9:27」，兩者都吻合。
>
> 休息時段（逐字稿空白）：[00:43:00] 那一分鐘之後到 [00:54:09]（10 分鐘）、[01:53:04]–[01:58:50]（5 分鐘）。
>
> 常見誤聽對照：SIAS → SASS（[00:06:04] 那句）；ASUW → AWS；Qt → CuTe（NVIDIA 的 DSL）；Rock them or hip → ROCm / HIP；NeurF → NeRF；Insight Compute → Nsight Compute；PAs → TAs；880 G-Force → GeForce 8800；Cindy → SIMD；PC IEEE Express → PCI Express；sam's → SMs；Ada Loveless → Ada Lovelace；a cert → `assert`；multi-GPO → multi-GPU；Jensen Wang → Jensen Huang；OTT 26 GPU Compute → 應該是 AUT26（Autumn 26）的 O'Reilly 書單名稱；3.4 → 老師馬上更正為 13.4（[02:37:04]）。
> 未確認：[00:03:04]「Gautam who was in my SIAS class」，脈絡是在講以前的 graphics／Scientific Visualization 課，這裡的 SIAS 可能是 SciVis，不一定是 SASS。

## 重點摘要

1. **課程定位與 GPU track**（p4、p6、p7）
   - UW ECE 新的 GPU track 有三門課：Au26 本課（單 GPU、CUDA 基礎）→ Wi27 multi-GPU／multi-node（NCCL、NVLink、各種 parallelism）→ Sp27 Python-centric（Triton、CuTe DSL、PyTorch、FlashAttention、Gaussian splatting、NeRF 等）。
   - 以前的第二門課是 Scientific Visualization（OpenGL），今年改成以 machine learning 為中心。
   - 教學方式是「多次 pass」：先建立大概的印象，之後每一輪再補細節，避免第一天就把所有細節塞給你。
   - 本課**是**：close-to-the-metal 的低階 API、hardware-software interface（ISA、microarchitecture）、設計／測試／調校 GPU compute layer 的工具。
   - 本課**不是**：C/C++ 入門，也不是教寫上層應用（ML framework 等）。
2. **課程行政**（p5、p8–p13）
   - 全線上，用 MS Teams（不是 Zoom，見「還要釐清」#1）。每週二 6:30–9:30 PM PDT。6:30–9:00 是技術內容，9:00–9:30 是 Q&A／作業協助。
   - 4 份計分作業（11／12／12／15 分），占 50%；final project 占 50%（proposal 10%、design spec 30%、final report／code／結果 60%）。**沒有考試。**
   - 作業節奏：這週發、下週二上課前（5:59 PM）截止。
   - Final project：2–3 人一組，finals week 週二到週四在 Teams 上報告，每組 10 分鐘（投影片沒寫，見 [00:35:03]）。
   - TA：Diya Shetty、Devika Nair。TA office hours 用投票決定，教授 office hours 是每週課後時段，也可另約。
   - 教科書：PMPP 4th ed.（Kirk & Hwu），透過 UW NetID SSO 在 O'Reilly 免費讀。每週閱讀進度放在 Canvas Pages 的 weekly reading sets。
   - 可能另外在 Panopto 放預錄的補充影片（p11）。
3. **AWS WorkSpaces VDE**（p15–p16、p61）
   - 每個 instance 有自己獨享的 Tesla T4（Turing，CC 7.5，16 GB），裝好 Windows、Visual Studio 2026、CUDA Toolkit 13.4、Nsight Compute、VS Code（VS Code 不是主要環境）。
   - 登入流程：會收到兩封信，第一封是臨時密碼，要先改密碼，第二封才是 apps available。AWS 密碼和 NetID 密碼是分開的。選 Autumn 26 GPU compute stack，要選 **Desktop**，選 application 只會串流 Visual Studio。
   - 遇到 "no streaming resources available"：等 5–10 分鐘再試。
   - 每個 session 4 小時，而且是 stateless，結束後所有東西會消失，一定要備份到雲端硬碟。用完要明確登出，釋放資源。
   - 自己的機器也可以：NVIDIA GPU CC ≥ 7.5、Windows 10/11、VS 2022/2026 Community、CUDA Toolkit 13.4。但助教和老師不提供自有機器的技術支援。
4. **GPU 歷史**（p18–p27）
   - 早期 GPU 是 fixed-function 的 graphics pipeline（vertex processing → rasterization → fragment processing），每個 vertex／pixel 都可以獨立處理，屬於 embarrassingly parallel。
   - 後來加入可程式化的 shader（最早只有 vertex 和 fragment 兩個 stage），再來所有 stage 都可程式化。
   - GPGPU：早期有人把數值問題「偽裝」成圖形（例如把 Navier-Stokes 的 2D 網格塞進 vertex buffer），在 GPU 上算，避免和 CPU 來回傳資料。
   - 2006–2007：NVIDIA 推出 Tesla 架構（GeForce 8800，128 個 streaming processors）和 CUDA，把 shader 一般化成 kernel。之後出現 OpenCL、DirectCompute、OpenGL／Vulkan compute shader。
   - 架構時間軸（p27）：Tesla → Fermi → Kepler → Maxwell → Pascal → Turing → Ampere → Hopper → Blackwell → Rubin（2026）。
5. **為什麼需要平行化**（p28–p35）
   - CPU 和記憶體的速度差距（memory wall）：DRAM 和 on-chip SRAM 的存取時間差一個數量級以上，核心數越多，每次存取的「有效 cycle time」越短，和記憶體的差距越大。
   - 三道牆：Power wall、Memory wall、ILP wall。結論：要繼續提升效能，只能靠 explicit parallel programming。
   - 名詞：multi-core（CPU，幾十個複雜核心）、many-core（GPU，數千個簡單核心）、heterogeneous computing（CPU + GPU 一起用）。
6. **各家 GPU 架構很像**（p31–p34）
   - NVIDIA Blackwell：GPC → TPC → SM → 4 個 sub-partition。每個 sub-partition 有自己的 scheduler、instruction cache、register file、32 個 core、tensor core、load/store unit、SFU，整個 SM 共 128 個 core，L1／shared memory 是整個 SM 共用。
   - Intel Xe／Xe3P（render slice、Xe core、XVE vector engine、XMX matrix engine）和 AMD CDNA（shader engine、compute unit）的分層方式基本一樣。
   - 各家都在加 tensor／matrix accelerator，因為 dense matrix 運算是 ML 的核心。
7. **平行化的基本概念**（p37–p45）
   - 平行運算的三個目標：同樣問題更快解、同樣時間解更大的問題、同樣時間得到更好的解（更精確的模型、更高解析度、更多資料）。
   - **Independence**：S(n) 和所有 S(m)（n ≠ m）之間都沒有相依。相依分兩類：data dependency（存取／修改同一個資源）、control dependency（一個元件的結果決定另一個要不要執行）。獨立的元件可以用任何順序執行。
   - Vector addition 是完全獨立的範例，可以 data parallel。
   - CPU serial 版本（`vecadd_idx`、`vecadd_ptr`）。指標遞增時會跳過一個元素型別的大小；陣列名稱就是指向第 0 個元素的指標，`A2` 等於 `&A2[0]`。
   - Loop unrolling／strip mining：把 8 次迴圈分給 2、4、8 條 lane 同時算。
   - Time vs space tradeoff：GPU 選 space，用大量平行核心換取更少的時間。
8. **Computational index space 與第一個 kernel**（p46–p47）
   - 計算的範圍叫 grid，切成 Nb 個 block，每個 block 有 Nt 個 thread，G = Nb × Nt。
   - 內建變數：`threadIdx`、`blockIdx`、`blockDim`、`gridDim`。每個 kernel instance 從這些值知道自己要處理哪一筆資料。
   - `vecAdd1D`：`gid = threadIdx.x + blockDim.x * blockIdx.x`，然後 `c[gid] = a[gid] + b[gid]`。
   - 例子：N=16，4 個 block × 4 個 thread。thread 3、block 3 → 3 + 4×3 = 15，處理最後一個元素。
9. **Host／device 系統與開發流程**（p48–p53）
   - Host application → GPU runtime API（kernel 設定與 dispatch、記憶體管理與傳輸）→ device driver → GPU 上的 scheduler 把 kernel 分給各個 core。
   - 基本流程：設定 VS 的 include／lib → include header → 用 Runtime API（簡單但控制少）或 Driver API（複雜但控制多）寫 host 程式 → 寫 kernel → `nvcc`（device）+ `CL.exe`（host）編譯連結。
   - 常見 build error：`C3861 identifier not found` 通常是少 include；`LNK2001 unresolved external symbol` 通常是少了 `.lib`。
   - 本課之後會往下看 Driver API、PTX（virtual architecture）、SASS（real architecture）。HW0 先用 Runtime API。
   - Host 程式樣板（p51）：初始化 → 查 device → 配置 host 記憶體 `_h` → 配置 device 記憶體 `_d` → HtoD 複製 → 決定 execution configuration → launch → 等待並檢查錯誤 → 取回結果 → 在 host 驗證。
   - 最簡單的情況：一個 `.cu` 檔同時放 kernel 和 `main`，用 `nvcc -o <name> <name>.cu -run` 編譯執行（要在 VS Dev Command Prompt，才找得到 `CL.exe`）。
   - Execution configuration：`kernel<<<blocksPerGrid, threadsPerBlock>>>(args)`。p53：`threadsPerBlock = 32`（一個 warp 是 32 個 thread），`blocksPerGrid = (numElements + threadsPerBlock - 1) / threadsPerBlock`。
10. **錯誤處理**（p54–p55）
    - GPU 的錯誤可能同步發生，也可能非同步發生。Kernel launch 是非同步的，會立刻返回。
    - Runtime API：`cudaGetErrorName`、`cudaGetErrorString`、`cudaGetLastError`、`cudaPeekAtLastError`。
    - Kernel 回傳 void，不能直接包 macro。要在 launch 後呼叫 `cudaGetLastError()` 抓 launch error，kernel 跑完後再檢查一次。
    - `checkCuda(result, srcStr)`：result 不是 `cudaSuccess` 時印出錯誤字串，並在 debug build 下 `assert`。所有回傳 `cudaError_t` 的 Runtime API 都可以包起來。
    - 本機的 slides.txt 已經是 **updated 版**：p55 的 `checkCuda` 有兩個參數（第二個是字串，標出呼叫的函式）。原版的呼叫語法有錯，老師在 L2 [01:12:01] 更正，詳見 `gpu/lectures/2026-10-13/notes.md`。
11. **HW0**（p62）
    - 不計分、不用交，但非常重要，要在 L2（10/13）前做完。放在 Canvas Files → Homeworks → Hw0。
    - 內容是 GPU 程式的「hello world」：查詢 device 資訊。也會讓你自己摸一遍 build 流程。
    - 也是自我評估先修能力的方法。
12. **本堂只在投影片上、沒有講到的內容**
    - p56–p57 只在 [02:37:04] 帶過（VS 和 CUDA Toolkit 下載連結）。
    - p58–p60（CUDA 平台元件、編譯流程、fatbin／`cuobjdump`）本堂沒講，L2 講了，見 `gpu/lectures/2026-10-13/notes.md` 重點摘要 #1。
    - p61 的 demo 分散在 [01:01:01]–[01:11:02]（AWS 登入、`nvidia-smi`）和 [02:39:00]（VS 裡可以建 CUDA runtime project）。

## 名詞解釋

| 名詞 | 說明 |
|---|---|
| GPU track（PMP / Certificate） | UW ECE 的三門 GPU 系列課：Au26 本課、Wi27 multi-GPU／multi-node、Sp27 GPU-accelerated ML。 |
| VDE / AWS WorkSpaces | Virtual Desktop (Development) Environment。本課用的雲端 Windows 桌面，每台有自己的 T4。以前叫 AppStream。Stateless，session 4 小時。 |
| Tesla T4 / Turing | 本課的硬體。Compute Capability 7.5，16 GB，有第二代 tensor core。 |
| Compute Capability (CC) | GPU 架構的 major.minor 版本。本課要求自有 GPU 至少 7.5。 |
| fixed-function pipeline | 早期 GPU 的 vertex／fragment 處理是寫死在硬體裡的，不能程式化。 |
| shader | 在 graphics pipeline 某個 stage 執行的小程式。CUDA kernel 就是從 shader 的概念一般化而來。 |
| GPGPU | General-Purpose computing on GPUs。早期把數值問題偽裝成圖形來借用 GPU 運算。 |
| CUDA | Compute Unified Device Architecture。NVIDIA 2006–2007 年推出的平台和 C-based kernel 語言。 |
| OpenCL | 跨廠商的開放標準 GPU 程式語言，概念和 CUDA 很像。老師以前用 OpenCL 教這門課。 |
| ROCm / HIP | AMD 的 GPU 平台和語言。有工具可以把 CUDA 自動轉成 HIP，老師沒親自試過。 |
| SM / sub-partition | Streaming Multiprocessor。Blackwell 的 SM 分成 4 個 sub-partition，每個有 32 個 core，共 128 個。 |
| GPC / TPC | Graphics Processing Cluster／Texture Processing Cluster。NVIDIA GPU 由 GPC → TPC → SM 一層層組成。 |
| tensor core | 專門做矩陣乘加的硬體單元。T4 有，課程後面會寫 tensor core 指令。 |
| memory wall / power wall / ILP wall | 單核效能無法再自動提升的三個原因：記憶體存取跟不上運算、功耗與散熱的上限、指令層級的平行已經被用盡。 |
| multi-core / many-core | Multi-core 是 CPU 的幾十個複雜核心；many-core 是 GPU 的數千個簡單核心。 |
| heterogeneous computing | 同時使用 CPU 和 GPU。瓶頸常常在兩者之間的資料傳輸。 |
| independence | 一組元件裡，任何一個都不依賴其他元件，所以可以用任何順序或同時執行。 |
| data / control dependency | 前者是存取或修改同一個資源；後者是一個元件的結果決定另一個要不要執行。 |
| data parallelism | 對不同資料做同一個運算，例如 vector addition 的每個元素。 |
| loop unrolling / strip mining | 把迴圈展開，再依可用的 lane 數把元素分組，同時執行。 |
| time vs space tradeoff | 用少量硬體跑很多步，或用大量硬體跑很少步。GPU 選擇後者（space）。 |
| SIMD | Single Instruction, Multiple Data。SIMD 和 SIMT 的差別延到 L2／L3。 |
| computational index space | 計算的範圍。CUDA 用 grid → block → thread 表示。 |
| `threadIdx` / `blockIdx` / `blockDim` / `gridDim` | CUDA 內建變數，存在每個 thread 的 register 裡，讓 kernel instance 知道自己是誰。 |
| global thread ID (`gid`) | `threadIdx.x + blockDim.x * blockIdx.x`，每個 thread 在整個 1D grid 中的唯一編號。 |
| kernel | 用 `__global__` 宣告、在 GPU 上由大量 thread 平行執行的函式。 |
| execution configuration | `<<<blocksPerGrid, threadsPerBlock>>>`，告訴 driver 要啟動多少 block 和 thread。 |
| warp | 32 個 thread 組成的排程單位。L2 會正式講。 |
| CUDA Runtime API / Driver API | Runtime 簡單但控制少，HW0 用它；Driver API 複雜但能控制到最底層，本課之後會用。 |
| nvcc / CL.exe | nvcc 是 CUDA device compiler；`CL.exe` 是 Visual Studio 的 MSVC host compiler。 |
| PTX / SASS | PTX 是 NVIDIA 的中間表示（virtual architecture）；SASS 是特定架構的組合語言（real architecture）。詳見 L2。 |
| `cudaError_t` / `checkCuda` | Runtime API 的回傳錯誤型別；`checkCuda` 是本課標準的錯誤檢查 wrapper。 |
| `cudaGetLastError` | 取得最近一次的錯誤，用來檢查 kernel launch 是否出錯。 |
| `nvidia-smi` | 命令列工具，顯示 driver 版本、CUDA 版本、GPU 型號和記憶體。 |
| roofline / speedup 上限 | 老師提到的理論工具：先估算最好情況下能加速多少，再和實測比較。課表排在 Week 3。 |

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

**課程定位與 track**
- [00:00:03] 這門課已經發展成整個 certificate program，有學生去了 NVIDIA、Intel、Microsoft、AMD，有人成了 GPU compiler 開發者。
- [00:02:03] [00:04:01] 第二、三門課今年是全新的。以前的第二門課是 Scientific Visualization（OpenGL），現在整個 track 改成 ML-centric。
- [00:04:01] [00:05:01] 本季只做單 GPU，但就算只有一張 GPU 也有上萬個 core，仍然是新的思考方式。Winter 才擴展到 multi-GPU、multi-node。
- [00:06:04] [00:07:03] Spring 會教 Triton、CuTe 這類 DSL，重點是判斷什麼時候用 Pythonic DSL、什麼時候要往下寫 raw CUDA，甚至 PTX／SASS。
- [00:12:04] T4 是 CC 7.5，不是最新的，但有 tensor core，課程後段會寫 tensor core 指令。
- [00:13:00] [00:14:05] 教法是多次 pass：第一次聽很多地方會不清楚是正常的，之後會一輪一輪補細節，不用 fire hose 的方式。
- [00:16:02] [00:17:09] 先用理論（例如演算法複雜度）估出效能上限，再用 profiling 找出實際的瓶頸。實際上幾乎不可能達到理論上限，但要知道卡在哪裡。
- [00:18:02] 只聽課或看書不夠，要自己寫 code、遇到不能跑的情況，才真的學得會。
- [00:21:02] [00:24:04] 本課處理的是軟體 stack 最底層、很薄的那一層 GPU compute layer。上層多半跑在 host（CPU），把繁重的運算交給 GPU。
- [00:25:04] 「back of the napkin」的理論工具：先估算最好情況下能加速多少。

**先修與 HW0**
- [00:27:04] 先修不是硬性門檻。過去也有 C 不熟、沒用過 Visual Studio 的學生表現很好，關鍵是投入和動機。
- [00:28:02] 用 HW0 自我評估：覺得簡單就沒問題；覺得難就要多花點力氣，不代表做不到。
- [00:28:02] [00:29:01] ML 基礎對本季不是那麼關鍵，主要是 winter 和 spring 會用到。
- [00:30:01] [00:31:02] 班級很大，自有機器的問題無法保證支援。最好在 AWS 環境上測試，特別是非標準的家用系統（例如用 AMD GPU 轉 HIP）。

**時程與截止**
- [00:09:01] 上課時間是 6:30–9:30。老師說之前在幾個地方寫了 6 點，是因為往年都是 6 點，今年被排到 6:30。
- [00:31:02] [00:32:03] 前五週的主題和作業會很貼近投影片的課表，後面幾週可能會調整。前五、六堂課提供寫作業需要的基礎。
- [00:32:03] 作業節奏：這週發、下週上課前截止。HW1 是 10/20 5:59 PM，然後上 L3、發 HW2，依此類推到 HW4。
- [00:33:00] 投影片、syllabus、課程網站之間的日期可能不一致，是老師忘記改。目前以這頁投影片（p9）最準。
- [00:34:02] 有同學指出 syllabus 寫錯，HW1 應該是 10/20（week 3）截止，老師說會修正 syllabus。
- [00:34:02] Canvas 的 Assignments 頁面是實際繳交的地方，那裡的截止日期「一定是對的」。
- [00:43:00] 休息前又有同學問到 HW1 的截止日期，老師再次確認 syllabus 是 typo，正確是 10/20。
- [00:55:03] 課程網站 syllabus 頁上的作業日期「off by one」甚至更多，老師說會修，先以其他地方的日期為準。

**Final project 與成績**
- [00:19:00] [00:20:03] 前半季是作業，之後轉做 final project。這季 homework 和 final project 各占 50%。Final project 分成好幾個階段，不是最後一次定生死，過程中會清楚知道自己的進度。
- [00:34:02] Proposal 11/17、design spec 12/1。Design spec 大約有兩週，final report 再兩週多。
- [00:34:02] [00:35:03] 投影片漏了 final project 的報告：finals week 的週二、週三、週四在 Teams 上報告，2–3 人一組，每組 10 分鐘。
- [00:35:03] [00:36:03] Final project 內部比例：proposal 10%、design spec 30%、final report／presentation／code／results 60%。

**協作與 AI 政策**
- [00:36:03] 可以和同學討論作業和專題，但交出去的東西必須是自己的，code 要自己寫。
- [00:37:04] 老師的說法比投影片 p10 寬鬆：AI 是現實，可以用來輔助，但目標是學 GPU，所以盡量自己想，卡住了再問 AI。全部交給 AI 寫，學習效果最差。另外 profiling、測試這類工作需要自己參與。

**Teams、TA、office hours**
- [00:38:04] Teams channel 會大量使用，老師和 TA 都會盯。可能另外在 Panopto 放預錄的補充影片。
- [00:39:05] [00:41:03] 兩位 TA 自我介紹：Diya（第二年 PMP 學生）、Devika（背景是 embedded／硬體）。
- [00:41:03] [00:42:02] TA office hours 會在隔天發投票（Poll Everywhere），可以排序偏好的時段。如果時間都不行，可以約教授個別談。
- [00:57:05] Teams 上已經開了 AWS issues channel、HW0 discussion channel，之後每份作業都會有自己的 channel。
- [00:58:01] 建議在 Teams 開啟通知，channel 多了很容易漏掉訊息。

**AWS WorkSpaces**
- [00:42:02] AWS 邀請信當晚課後寄出。
- [01:02:01] AWS 的密碼是你自己另外設定的，不是 NetID 密碼。
- [01:02:01] [01:03:04] 要選 Desktop。選 application 只會串流 Visual Studio，不是你要的。
- [01:03:04] [01:04:00] 出現 no streaming resources 時，等 5–10 分鐘再試，因為 AWS 是 on-demand 動態開機器。試了幾次還不行，就到 Teams 的 AWS issues channel 貼：時間、嘗試次數、錯誤畫面截圖。
- [01:05:01] 用完要明確登出，才會釋放資源。建議允許剪貼簿，方便在本機和虛擬桌面之間複製。
- [01:06:01] 主要開發環境是 Visual Studio。VS Code 有裝，但不是本課主要工具。
- [01:07:13] 每台都有自己獨享的 T4，不需要和別人搶。
- [01:07:13] [01:08:06] 自有 GPU 要 CC 7.5 以上（Turing 或更新：Ampere、Ada Lovelace、Hopper、Blackwell）。VS 2022 大致可用，但 2026 比較好。投影片寫的 CUDA 版本是錯的，要用 13.4。
- [01:08:06] [01:09:02] AWS 最大的缺點：stateless，session 結束後一切消失，救不回來。每次都要備份到 Google Drive 之類的雲端硬碟。Session 只有 4 小時，快到時要記得存檔。
- [01:10:05] 在 x64 Native Tools Command Prompt 跑 `nvidia-smi`，可以看到 driver、CUDA 版本、Tesla T4 和 16 GB 記憶體。
- [01:11:02] 邀請信有兩封，常常被分到垃圾郵件，老師會在 Teams 上公布信件主旨。

**GPU 歷史與架構**
- [01:15:02] [01:16:04] 早期 GPU 的 vertex 和 fragment 處理是硬體寫死的 fixed function，1990 年代開始普及。
- [01:19:00] [01:20:02] 為了不必每次改效果就重新做晶片，加入了 shader 的可程式化，最早只有 vertex 和 fragment 兩個 stage。
- [01:21:02] [01:24:05] GPGPU 的起源：遊戲開發者想在 GPU 上直接算流體之類的物理，避免和 CPU 來回傳資料而無法即時。做法是把數值問題偽裝成圖形網格。
- [01:26:04] [01:27:00] NVIDIA 決定全力投入：設計不專屬於圖形的新架構，把 shader 一般化成 kernel，什麼函式都可以。
- [01:31:03] CUDA 是 NVIDIA 自己的 C-based 語言，它的抽象和硬體能力貼得很近，課程大部分時間都在學它。
- [01:32:04] [01:33:03] 老師以前用 OpenCL 教這門課，但 OpenCL 發展不起來，加上大部分裝置是 NVIDIA，所以改教 CUDA。CUDA 和 OpenCL 非常像。
- [01:35:03] 幾乎所有 GPU 都在 TSMC 製造；Rubin 是今年的新架構。
- [01:37:02] [01:39:01] 我們最在意的是 DRAM（device 上的 global memory）和 SRAM（on-chip）之間的差距。核心越多，運算速度和記憶體存取的差距越大，這是設計演算法時的主要瓶頸。
- [01:42:01] 效能不會再自動提升，程式設計者必須主動介入，而且要清楚意識到運算和記憶體存取之間的落差。
- [01:43:01] 理想的 heterogeneous 系統會用上所有的運算資源，但真正卡住你的是資料傳輸，尤其是跨 PCIe 在 host 和 device 之間搬資料。
- [01:45:03] [01:46:00] Blackwell 的 SM 分成 4 個 sub-partition，每個有自己的 scheduler 和 register file，各有 32 個 core。老師說 32 這個數字「之後會一再回來」。
- [01:47:02] Texture unit 有硬體的 trilinear interpolation，在 3D volume 的內插問題上可以大幅加速，課程某些地方會用到。
- [01:50:04] 各家廠商的 GPU 架構和 kernel 寫法都很相似，所以學會 CUDA 的觀念可以直接轉移。
- [01:52:02] 結論：需要 explicit parallel 機制和程式設計，這正是本課的核心。

**平行化與第一個 kernel**
- [02:01:02] GPU 平行執行的關鍵是 independence。
- [02:03:00] [02:04:04] Vector addition 是完全獨立的理想範例：順序無關，倒著算、隨機算都會得到同樣的結果。
- [02:05:01] [02:06:00] 每個 CUDA kernel 都要有一份 CPU serial 版本，一方面當效能 baseline，一方面驗證正確性。老師的原則：「runs 1000 times faster but produces the wrong result, it's useless」。這和 L2 [03:08:01] 講的結果驗證是同一件事。
- [02:08:01] 很多人寫 Python 太久，忘了 C 的指標。陣列名稱就是指向開頭的指標。
- [02:10:00] 只有靜態配置的陣列一定是連續記憶體；動態配置的多維陣列不一定連續。
- [02:13:04] GPU 在 time vs space 的取捨裡選 space，配置盡量多的平行核心，再用設計良好的 code 把它們用滿，不浪費空間。
- [02:15:00] Block 的大小是設計決策。
- [02:18:00] [02:20:01] 你只寫一份 kernel，它被複製到每個 core 上執行。每個 instance 靠 register 裡的 thread index、block index 知道自己要處理哪筆資料。
- [02:19:02] 這一頁一次講了很多，現在不用全懂，之後會花很多時間回來講。
- [02:22:02] 例子：thread 3、block 3、blockDim 4 → gid 15，處理最後一個元素。
- [02:23:01] 每個 thread 只存取自己的那一筆資料，所以沒有 race condition 或資料相依，讀寫 global memory 都是安全的。
- [02:26:01] Lecture 1 有很多疑問是正常的，之後會一一補齊。

**Host 端與錯誤處理**
- [02:28:04] HW0 是 GPU 的 hello world：查詢 device 並取回資訊。程式可以依 device capability 走不同的路徑。
- [02:29:03] Host 程式的核心循環：配置 host 和 device 記憶體 → 複製 → 設定並 launch kernel → 等待 → 取回結果。
- [02:30:00] Kernel 的語法細節 L2 才講。最簡單的情況是 host 和 kernel 放在同一個 `.cu` 檔。
- [02:32:03] [02:33:00] `threadsPerBlock = 32` 是因為一個 warp 有 32 個 thread，warp 在 L2 會講。計算 `blocksPerGrid` 的寫法是為了剛好涵蓋所有元素，L2 會再講其他寫法。
- [02:34:01] [02:35:01] Kernel launch 是非同步的，host 會繼續往下跑，kernel 不一定已經執行。
- [02:35:01] [02:36:04] Launch 後立刻呼叫 `cudaGetLastError` 只能抓到 launch 時的錯誤（找不到 kernel、參數或 launch configuration 不合法），kernel 執行中的錯誤要等它跑完再檢查一次。
- [02:36:04] [02:37:04] 所有 Runtime API 都回傳 `cudaError_t`，可以都用 `checkCuda` 包起來；debug build 下還會觸發 `assert`。老師建議一律使用這個 macro。
- [02:38:03] HW0 不計分、不用交，有問題就到 Teams 的 HW0 channel 問。HW0 放在課程網站的 homeworks 下。
- [02:39:00] 登入 AWS 後打開 Visual Studio，應該要看得到建立 CUDA runtime project 的選項，這代表環境正常。

**下課前**
- [02:39:00] 9:27 提早下課（老師要去接小孩），沒有時間做 Q&A。
- [02:40:02] 隔天會有問卷，調查能不能登入 AWS，以及 TA office hours 的偏好時段。
- [02:40:02] [02:41:02] 有同學問 CPU SIMD 和 GPU 平行的差別，老師說會在 L2、L3 講 SIMD 和 SIMT。
- [02:41:02] 還在候補、尚未加進課程的人，可以寫信給老師索取教材。其他問題請貼到 Teams。

## 和作業 / 考試的關聯

- **沒有考試**：成績是 HW 50%（4 份，11／12／12／15 分）+ Final Project 50%（[00:19:00]、[00:36:03]，p10，和 `assignments.md` 一致）。
- **HW0**
  - 不計分、不用交，建議在 L2（10/13）前做完（p62、[00:33:00]、[02:38:03]）。
  - 內容：device query、熟悉 VS 的 CUDA runtime project 和 build 流程。
  - 本堂相關：p49 的常見 build error、p51 的 host 樣板、p52 的單一 `.cu` 檔、p55 的 `checkCuda`。
- **HW1：SAXPY, 2D & 3D Matrix addition**
  - 截止：**10/20（二）5:59 PM PDT**（距今 2 天），11 分，Canvas id 11810625，online upload，目前 unsubmitted。
  - 本堂口頭（[00:32:03]、[00:34:02]、[00:43:00]）、投影片 p9、`assignments.md` 三者一致。Syllabus 上的日期是 typo，以 Canvas Assignments 為準（[00:34:02]）。
  - 本堂會直接用到的內容：
    - 1D 的 `gid` 公式（p47、p53）和 execution configuration `<<<blocks, threads>>>`（p53）。
    - `blocksPerGrid = (n + threadsPerBlock - 1) / threadsPerBlock`（p53），讓 thread 數涵蓋所有元素。超出範圍的 thread 要擋掉，這點 L2 才正式講。
    - CPU serial 版本當 baseline 和正確性參考（[02:05:01]）。
    - `checkCuda` 兩個參數的版本（updated p55），launch 後用 `cudaGetLastError` 檢查（[02:35:01]）。
- **HW2–HW4 和 final project**：依 p9 和 `assignments.md`。HW2 10/27、HW3 11/3、HW4 11/10（syllabus 寫 11:59 PM、投影片寫 5:59 PM）。Proposal 11/17、design spec 12/1 5:59 PM、final report 和 code 12/17（四）11:59 PM。
- **Final project 報告**：finals week 週二到週四在 Teams 上，2–3 人一組，每組 10 分鐘（[00:35:03]）。`assignments.md` 的「Project 發表 12/15–12/17 線上」和這個一致；分組人數和每組 10 分鐘是本堂新增的資訊。
- **環境**
  - AWS 邀請信兩封，可能在垃圾郵件裡。先改密碼，再選 Desktop（[01:02:01]）。
  - Session 4 小時、stateless，每次結束前都要備份（[01:08:06]）。
  - 自有機器要用 CUDA 13.4，不是投影片 p16 寫的 > 12.5（[01:08:06]）。
- **閱讀**：Reading Set #1 = PMPP Ch1–2（Introduction、Heterogeneous data parallel computing），對應 L1 和 HW0。PMPP 透過 O'Reilly 用 NetID SSO 免費讀（[00:58:01]），老師在 O'Reilly 上建了書單。
- 提醒：GPU 課的 AI 政策（p10）禁止用 AI 產生作業解答、專題報告或專題程式碼。老師口頭的說法比較寬鬆（[00:37:04]），但沒有取消這條規定。這份筆記只整理概念，沒有寫作業解答。

## 還要釐清的問題

1. **投影片和逐字稿的行政資訊衝突（依 BOOTSTRAP §3，以逐字稿為準）**
   - p10 寫「10 live lectures delivered via online Zoom」，是舊文字。實際用 Teams：[00:09:01] 說 delivered online via Teams，p5、p13 也寫 Teams。[00:43:00] 提到 Zoom 只是老師在說以前 Zoom 有計時器功能，不代表這門課用 Zoom。
   - 上課時間：歡迎公告寫 6–9 PM，老師在 [00:09:01] 說之前寫 6 點是誤植，實際是 6:30–9:30（和 p10、p11 一致）。
   - CUDA 版本：p16 寫「> 12.5」，老師在 [01:08:06] 說這是錯的，要 13.4（和 p8、p15、p57 一致）。
   - 截止日期：syllabus 和 Canvas syllabus 頁上的作業日期有錯（[00:34:02]、[00:55:03]），以 p9 和 Canvas Assignments 為準。老師說會修，之後要確認 syllabus 是否已經更新。
2. **Canvas 的「Task 0」到底是什麼？**
   - 老師在 [00:57:05] 說 Canvas assignments 裡的 task zero 就是 homework 0，不用交。
   - 但 `assignments.md` 記錄的 Task 0 是「self introductions」，10/9 11:59 PM 截止，online_url，0 分，目前 unsubmitted、已過期（lock 12/18 前仍可交）。
   - 老師在 [00:01:02] 也提到大家在 Teams 上貼的自我介紹。
   - 所以可能是：老師口誤；或 Task 0 後來改成自我介紹，要交一個 URL（例如 Teams 自我介紹貼文的連結）。0 分，不影響成績，但需要看 Canvas 上 Task 0 的說明確認。
   - **10/18 已查證**：Canvas 說明是「在 Teams 頻道貼自我介紹」，`omit_from_final_grade: true`，不計分。老師口述應是把它和 HW0 混在一起；不論哪個說法，都不影響成績。
3. **老師口誤（技術細節，以投影片和 L2 為準，不適用「逐字稿優先」）**
   - [01:27:00] 說 GeForce 8800 有「128 streaming multi-processors, or CUDA cores」。p24 寫的是 128 streaming processors（SP），SP 和 SM 是不同的東西。
   - [01:28:02] 說 Ada Lovelace「kind of like Hopper」。兩者是同一時期但不同的架構（Ada 以 GeForce／工作站為主，Hopper 是資料中心）；p25 只寫 Ada Lovelace AD102。
   - [02:33:00] 說每個 sub-partition 一個 cycle 就能算完一個 warp。這是 Blackwell（每個 sub-partition 32 個 core）的情況。**課程用的 T4** 每個 processing block 只有 16 個 FP32 core，一個 warp 要兩個 cycle（L2 [03:14:01]）。
   - [02:21:03] 一開始說 block dim 範圍是 0–3，隨即更正為 block index 是 0–3、block dim 是 4。
   - [00:12:04] 老師一度不確定 T4 的 tensor core 是第二代還是第三代，隨即說是第二代（Turing 確實是第二代）。
4. **SIMD vs SIMT**：[02:40:02] 有同學問，老師延到 L2／L3。L2 也跳過了 p45–p51（SIMD／SIMT、warp scheduling），所以要到 L3 才會講。
5. **Panopto 預錄影片**：p11 和 [00:38:04] 說「可能」會另外放，目前不確定有沒有、放在哪裡。
6. **SIAS class**：[00:03:04] 提到 Gautam 上過老師的「SIAS class」，脈絡是以前的 graphics／Scientific Visualization 課，可能是 SciVis 的誤聽，不影響課程內容。
7. **錄影缺頭的 18 分鐘**（6:30–6:48 PM）：p1–p3 的開場內容沒有逐字稿。如果當時有宣布行政事項，只能問同學或看 Teams 上的公告。
