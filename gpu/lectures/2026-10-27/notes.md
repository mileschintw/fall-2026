# GPU Lecture 4 — 2026-10-27（occupancy 與資源分配、launch configuration、通用尺寸的 tiled MMULT 邊界檢查、warp scheduling 與 control divergence、Nsight Compute GUI、HW3）

> 來源：transcript（Teams 自動逐字稿 `transcript.vtt`，2346 cues，00:02:07–03:32:43，約 3 小時 30 分）、slides（Au26_GPU-Compute_Lecture4.pdf，Canvas file 155101601，52 頁；另有 10/28 上傳的手寫註解版 `Au26_GPUCompute_L4_w_notes.pdf`，file 155143699，52 頁。註解是壓平的筆跡，不在文字層裡，是逐頁轉成圖片再和原版比對讀出來的，見「講義手寫註解」一節，標成（註解 pN））、閱讀章節：Reading Set #3 = PMPP 4th ed. Ch5 全章（10/19 起，對應 L3–L5、HW2–3）。本講 occupancy、warp scheduling、control divergence 的內容對應 PMPP Ch4 §4.4–4.8（自行對照；Reading Set #2 只指定到 Ch4 §1–4）；邊界檢查對應 Ch5 §5.5，記憶體用量對 occupancy 的影響對應 §5.6（自行對照）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：Insight Compute / N site compute / NSight → Nsight Compute；NCU → `ncu`（Nsight Compute CLI）；sam's → SMs；Touring → Turing；coobs dump / Kuobjdump / coo obj dump → cuobjdump；SIAS → SASS；PTXA / PTXAS verbose → `ptxas` verbose（`-Xptxas -v`）；Lu kernel / Lu divergent / loop div → loop divergence demo kernel；Gustavson-Barcis / Gustafson-Barsi's → Gustafson-Barsis；Colonels → kernels；Orp → warp；M-Mult / MMult → MMULT；warp faces → warp-phases；"14 out of 1392" → 14 out of 392（投影片 p47）；Ballad → valid；1G grid → 1D grid；"10, 20, 48" → 2048；"over 15,000 threads" → 1,536 threads；"2000 or 200 and 61" → 1024×255 = 261,120；museums（[01:10:00]）→ 應是指 occupancy 隨 block size 呈鋸齒狀的低谷（推測）；GPU Telecom cluster → 推測是 UW 的 Tillicum GPU cluster（Hopper）；Devika、Diya 是兩位 TA；Gautam 是下課道謝的同學。
>
> 錄影注意：錄影檔 18:28 開始，[00:02:07] 就開始上課（約 6:30 PM）。老師說自己生病、聲音快沒了，講得比較短。[01:44:00]–[01:59:23] 是 pop quiz（8:15–8:25 PM）加休息，約 15 分鐘空白。投影片 p33 之後的 warp/divergence 投影片老師多半快速帶過，要自己回頭讀（[02:00:04]、[02:16:00]）。

## 重點摘要

1. **課務更新**（p2–p3）
   - HW2 今天（10/27）5:59 PM 截止。HW3 今晚下課後發布，截止延到 **11/6（五）11:59 PM PST**（原本 11/3 二）。Canvas `due_at` 2026-11-07T07:59:59Z 也是 11/6 11:59 PM PST。原版 p52 仍寫舊的「11/03/26 5:59 PM」，老師口頭說那頁沒改（[03:31:01]）；10/28 的註解版已手寫改成 11/6 11:59 PM。
   - **Late days**：每人 7 天，今天起生效；可用在 HW 和 final project 的各階段，但**不能用在 final project 發表和 final report**。週末（六＋日）只算 1 天。之後作業盡量都排在週五截止，所以拖到週一只花 1 天。沒用完的每天換 0.5 分 extra credit。
   - **Pop quiz**：隨機出現，每次 3 題，不算進基本分；最多 2 分 extra credit（參加 0.5 ＋ 每答對一題 0.5）。基本分滿分 100 只由 4 份 HW 和 final project 組成。參與度（pop quiz、Teams 討論、上課發問）在成績邊界時列入考量。老師說隔天會把這些補進 Canvas。
   - TA office hours 時間已公布但很少人去；Devika 可以在週二上課前 5:20–6:20 PM 多開一小時，有興趣或想換時段就貼到 Teams。
2. **Occupancy 的定義與 SM 資源**（p5–p7）
   - Occupancy = SM 上 active warps ÷ 該 SM 允許的最大 warps。
   - SM 的有限資源：registers、shared memory、thread block slots、thread／warp slots、barriers。每一項都可能是限制，但通常同一時間只有一項真的卡住。
   - GPU 效能兩大原則（p6）：(1) 提供大量 thread 來隱藏 latency：提高 warp occupancy、減少 warp divergence；(2) 有效使用記憶體階層（L5 起深入）。
   - 每個 SM 分成 4 個 sub-partition（SMSP），各有 FP32/INT32、Tensor Core、FP64、SFU 等 execution pipe。整個 block 一定放在同一個 SM（因為 shared memory 是 SM 層級）；block 切成 warp 後 round-robin 分到 4 個 SMSP，warp 進了 slot 就一直待在那個 SMSP。資源（register、shared memory 等）不夠時 warp 不會被放進 slot。
   - p7 對照表：

     | | Hopper GH100 | Turing T4 |
     |---|---|---|
     | compute capability | 9.0 | 7.5 |
     | FP32 cores/SM | 128 | 64 |
     | SP/SM | 4 | 4 |
     | thread blocks/SM | 32 | 16 |
     | warps/SM | 64 | 32（8/SP） |
     | threads/SM | 2048 | 1024 |
     | threads/block | 1024 | 1024 |
     | registers/SM（32-bit） | 65,536 | 65,536 |
     | registers/thread | 255 | 255 |
     | shared memory/SM | 228 KB | 64 KB |

   - Turing 每個 SMSP 只有 16 個 FP32 core，一個 warp 要分兩個 cycle 跑完；較新的裝置每個 SMSP 有 32 個 core，一個 cycle 跑完一個 warp（[00:25:04]–[00:27:00]）。
3. **Kernel launch configuration 的經驗法則與例題**（p8–p11）
   - Grid／block 的維度配合問題本身（1D 問題用 1D、影像用 2D、體積資料用 3D）。
   - 每個 block 至少 128 threads（4 個 SMSP 各分到一個 warp）；用 2 的次方，且要是 32 的倍數。
   - 例題（Turing，單一 SM）：
     - A. block 1024／512／256／128 → 1／2／4／8 個 block（受 1024 threads/SM 限制）；64 → 16 個 block；32 → 仍只能 16 個 block（受 16 block slots 限制），只有 512 threads，occupancy 50%。
     - B. block 10×10 = 100 threads → 每個 block 4 個 warp（3 個滿的 ＋ 1 個只有 4 個 thread 在做事）。老師口頭答 10 個 block、40 個 warp，但這超過 Turing 的 32 warps/SM（見「還要釐清的問題」）。
     - C. block 768 threads → 只放得下 1 個 block（2 個就要 1,536 threads），24 warps，occupancy 24/32 = 75%。
     - D. 滿 occupancy（1024 threads）時每個 thread 最多 65,536 ÷ 1024 = 64 個 register；每個 thread 用 128 個 → 只能 512 threads，occupancy 50%；要 300 個 → 超過 255 上限，compiler 會默默 **register spilling** 到 local memory（實際在 global memory），慢很多。
   - Occupancy 是 warps、thread blocks、registers、shared memory 四項中的最小值。p10：「Compute it, don't guess it.」
   - 工具：Nsight Compute 內建 **Occupancy Calculator**（取代已停用的 Excel 試算表）；`nvcc` 的 ptxas verbose 輸出和 `cuobjdump` 可以看 register、shared、local（spill）、constant 用量；也可以在程式裡查詢 device properties，NVIDIA 的函式庫就會依裝置動態選最佳版本。
4. **Occupancy Calculator 示範**（p11，[00:59:05]–[01:13:01]）
   - 選 compute capability（7.5 Turing、9.0 Hopper）後，右邊會列出該裝置的 physical limits。
   - 用滑桿設定 threads/block、registers/thread、shared memory/block，以及 shared memory 與 L1 的配置（兩者共用同一塊，shared 用不到就調小，剩下的給 L1）。
   - 例：300 threads/block → 每 block 10 warps，只能放 3 個 block（受 block size 限制），active threads 960（30 warps × 32，含沒在做事的 thread），occupancy 94%。256 → 4 個 block。
   - Graph view 可以看 threads/block、registers/thread、shared memory/block 對 occupancy 的影響曲線；register 和 shared memory 超過某個量後 occupancy 只會一路下降。
   - 用 `cuobjdump` 看 loop divergence kernel：10 registers、0 shared、0 local、constant 376 bytes，register 不是限制。
5. **通用尺寸的 tiled MMULT：邊界檢查**（p12–p25）
   - L3 的 tiled kernel 只能處理 Width 是 TILE_WIDTH 倍數的方陣。實際要處理任意尺寸、維度相容（conforming）的長方形矩陣。補 0 對齊（padding）會多花空間和傳輸時間，有更好的做法。
   - 3×3 矩陣、2×2 tile 的例子（p13–p16）：
     - Block(0,0) phase 1 載入 M tile 時，thread (0,1)、(1,1) 因為 row-major 換行，會讀到**錯誤但合法**的元素。
     - 載入 N tile 時，thread (1,0)、(1,1) 會讀到**陣列範圍外**（9 個元素之後的第 10、11 個），可能 access violation。
     - Use 階段：phase 1 時所有 thread 都可能拿到無效值。
     - Block(1,1) 在 phase 0 也有同樣問題，所以每個 phase 都可能出事。
   - 兩種關鍵情況（p17）：(1) thread 不負責算有效的 P 元素，但仍要參與載入 tile；(2) thread 負責算有效的 P 元素，卻可能去讀不存在的輸入元素。
   - 解法（p18）：載入任何輸入元素前，先檢查它是否在 2D 有效範圍內；有效就載入，否則在 SMEM 寫 0。0 不會影響 multiply-add 的結果。
     - LOAD 階段檢查輸入元素在 M、N 的 2D 範圍內；USE 階段檢查沒有超過 inner-product 維度 K；寫回 P 前檢查 Row、Col 有效。
     - 檢查條件要把 phase 編號 p 和 TILE_WIDTH 算進去。
     - 用 2D（row、col／寬、高）思考邊界，再換成 1D index 實作。
   - M tile（p20）：載入 `M[Row][p*TILE_WIDTH+tx]`，條件是 Row < M 的高度且 p*TILE_WIDTH+tx < M 的寬度。N tile（p21）：載入 `N[p*TILE_WIDTH+ty][Col]`，條件是 p*TILE_WIDTH+ty < N 的高度且 Col < N 的寬度。
   - p20 的 1D index 和條件有筆誤，老師說應該是乘 M 的寬度、比 M 的寬度（[01:32:02]、[01:34:06]），會再更新投影片。
   - p22–p23 的程式碼只標出要加檢查的地方（`++` 行），仍用 Width；改成 J、K、L 是 HW3 的 to-do（[01:37:01]、[01:38:10]）。
   - 一般長方形矩陣（p25）：M 是 J×K、N 是 K×L、P 是 J×L。Width 指 M 或 P 的列數時換成 J；指 M 的行數或 N 的列數時換成 K（inner-product 維度）；指 N 或 P 的行數時換成 L。Tile 仍是固定的方形，TILE_WIDTH 是可調參數。
6. **Warp scheduling**（p27–p33）
   - Kernel launch（例：`<<<256,256>>>` = 65,536 threads）→ work distributor 把 block 分到各 SM（A100 有 108 個 SM）→ block 切成 8 個 warp，round-robin 分到 4 個 SMSP（W0、W4 在 SMSP0……）。Block 彼此獨立、順序不定，一個 block 會待在同一個 SM 直到所有 thread 結束。
   - 每個 SMSP 有一個 warp scheduler 和一個 warp pool。Pool 的 slot 數：Turing 8、Hopper／Ada 16（[02:03:03]；p29 的圖是 16 slots、64 KB register file）。每個 cycle 最多從 eligible warp 裡挑 1 個發出一道指令。
   - Warp eligible 的條件：下一道指令已 fetch、decode，運算元都備妥，目標 pipe 可以接收。
   - Warp 狀態（p30）：active 之後每個 cycle 只會處在 eligible（selected 或 not selected）或 stalled 其中一種；執行到 SASS 的 EXIT 指令後釋放 slot。Nsight Compute 統計每種狀態的 cycle 數。
   - 常見 stall 原因（p30）：Long scoreboard（等 global／local memory → coalesce、用 shared memory reuse）、Wait（固定延遲，例如 FMA→FMA → 增加獨立指令 ILP）、Short scoreboard（shared memory 或 SFU → 避免 bank conflict）、Barrier（等 `__syncthreads()` → 平衡 warp 間工作量）、Math pipe throttle（execution unit 忙，通常代表 compute-bound）、MIO／LG throttle（記憶體指令 queue 滿 → 用更少、更寬的存取）、No instruction（instruction fetch，少見，避免程式碼膨脹）。
   - Latency hiding（p31）：每道指令要等 4 cycle 時，1 個 warp 只用到 25% issue slot，4 個 warp 才能 100%。Little's law：平均 active warps = issue rate × 每道指令 cycles。Global memory 約 400–600 cycle（[02:10:00]），所以需要很多 warp，再加上每個 warp 內的獨立指令（ILP，例如非阻塞的 memory load 後繼續做不相依的運算）。
   - 讀 Nsight Compute 的 Scheduler／Warp State Statistics（p32）：issue rate ≈ 0.8 以上表示 scheduler 很忙，看 pipe 和記憶體 throughput；issue rate 低就比較 active 和 theoretical warps 找 occupancy 限制，再找最大的 stall 原因，用 Source view 定位。CLI：`ncu --section SchedulerStats --section WarpStateStats ./app`。
   - Waves（p33，A100）：每 SM 64 warp slots、32 block slots、65,536 registers、164 KB shared memory。Blocks/SM = min(64 ÷ warps/block, 32, 65,536 ÷ regs/block, 164 KB ÷ smem/block)；blocks/wave = 108 × blocks/SM；waves = grid blocks ÷ blocks/wave。例：kernel A（4096 blocks、32 regs）每 SM 8 個 block（受 warp slots 限制）、864 blocks/wave、4.74 → 5 waves；kernel D（256 blocks、128 regs）每 SM 2 個 block、只有 2 waves，效率 59%。最後不滿的 tail wave 在 wave 數少時影響最大，概念和 Gustafson-Barsis 一樣：問題越大，固定的尾巴占比越小。Wave 是計數工具，不是 barrier，空出來的 slot 會立刻補上。
7. **Warp 的線性化與 SIMD 執行**（p34–p37）
   - 多維 block 先以 row-major 攤平（x 先、y 次、z 最後），再依 warp 大小切。Warp 內 thread index 連續遞增，warp 0 從 thread 0 開始；切法在各裝置一致，但 warp 大小可能隨世代改變。
   - 不要依賴 warp 內或 warp 間的執行順序；thread 之間有相依就用 `__syncthreads()` 或 `__syncwarp()`。
   - SM 是 SIMD／SIMT 處理器：每個 SP 內多個 core 共用 instruction fetch／decode／control，降低控制開銷。Warp 內所有 thread 同一時間執行同一道指令；所有 if-then-else 判斷相同、迴圈次數相同時最有效率。
8. **Control divergence**（p38–p41）
   - Warp 內的 thread 走不同的 control flow 路徑（if 的 then／else 不同，或迴圈次數不同）就叫 control divergence。各條路徑依序執行，每條路徑上的 thread 同時跑；巢狀控制流程會讓路徑數變多。
   - 實作方式（[02:20:01]–[02:24:03]）：每道 SASS 指令附帶 predicate／active bit，每個 thread 都執行運算，但非 active 的 thread 結果被丟棄。N 條路徑就要花約 N 倍時間。
   - 例：`if (threadIdx.x > 10)` 會 diverge（判斷粒度小於 warp）；`if (blockIdx.x > 2)` 不會（同一個 block 內所有 warp 走同一條路）。
   - Branch-induced（例：`threadIdx.x < 24`，先跑 A 路徑、再翻轉 active bits 跑 B 路徑，最後 reconverge）與 loop-induced（迴圈次數取自依 thread index 讀到的資料，跑最久的 thread 拖住整個 warp）。
9. **MMULT 邊界檢查造成的 control divergence 分析**（p42–p48）
   - 假設 TILE_WIDTH = 16、16×16 block（8 個 warp，每個 warp 是 block 內的 2 列）、100×100 方陣：ceil(100/16) = 7 個 phase，7×7 = 49 個 block。
   - 載入 M tile 的兩類 block：Type 1（tile 在最後一個 phase 前都在有效範圍內）、Type 2（最底下一排，所有 phase 都有部分在範圍外）。
   - Type 1：42 個 block × 8 warps = 336 warps，× 7 phases = 2,352 warp-phases，只有最後一個 phase diverge → 336 個。
   - Type 2：7 個 block × 8 warps = 56 warps，× 7 = 392 warp-phases。最後一排 tile 涵蓋 row 96–111，只有 96–99 這 4 列有效，也就是前 2 個 warp；其餘 6 個 warp 全程在範圍外，大家一起什麼都不做，不算 divergence。所以只有 7 × 2 = 14 個 warp-phase diverge。
   - 合計 (336+14)/(2,352+392) = 350/2,744 ≈ 12.76%，效能影響上限約 12.8%，實際更小（diverge 的 warp 裡多數 thread 仍在算有效值）。矩陣越大比例越小。
   - 載入 N tile 的 divergence 分析留作 HW3 練習（p48）。
   - 結論：不要因為怕 divergence 而省掉邊界檢查，省掉的代價是結果錯誤。程式裡有很多控制流程不代表 divergence 會很嚴重。本來就會 diverge 的演算法（例如 parallel reduction）在 L6–L10 的 parallel patterns 會講。
10. **Nsight Compute（NCU）**（p49–p51）
    - Profiled execution：NCU 啟動應用程式，在 CUDA runtime 和 driver 之間插入 injection layer，攔截所有溝通，讀取 GPU 的硬體 counter。
    - 每次能收的 metric 有限，所以同一個 kernel 要重跑多個 pass；每個 pass 之間會還原記憶體狀態、清 cache、鎖定 GPU clock，確保結果可重現。
    - 層級：set → section → metric。Sets：Basic（229）、Detailed（1150）、Full（9059）、Roofline（6783）。`ncu --list-sets`、`ncu --list-sections`。Sections 包含 Speed of Light Throughput、各種 Roofline、Occupancy、Workload（Compute、Memory）、Statistics（Scheduler、Warp State、Instruction、Launch）、Source Counters。有 CLI 和 GUI 兩種介面。
    - Roofline（p50）：NCU 會依實測算出 kernel 的 AI 並畫在 roofline 上，有 FP64／FP32／FP16 不同的 compute ceiling，以及 DRAM、L2、L1 不同的記憶體 ceiling。理論值是上限，實測含各種 overhead，通常較低。
11. **NCU GUI 示範**（p51，[02:55:01]–[03:31:01]）
    - 準備：開 NCU 一定要用系統管理員身分執行，否則讀不到 GPU counter。程式用 Release build、確認 compute architecture、開 line info（才能對照原始碼）、開 ptxas verbose 看 register 用量。
    - Loop divergence demo：每個 thread 依 `counts[tid]` 決定迴圈次數，迴圈內只有一個 FMA（SASS 4 道指令）。比較 uniform（所有 thread 次數相同）和 one-lane（每個 warp 只有第一個 thread 跑 N 次，其餘跑 1 次）。設定 output 檔名（`%i` 自動編號）、選 Full set（9,059 metrics），跑了 45 個 pass；第一次 launch 是 warm-up。
    - Summary 頁的規則分析直接指出 thread divergence：平均每 cycle 只有約 6 個 thread active，再因 predication 降到 5.6。Summary 也列出 compute／memory throughput、registers（NCU 顯示 16，ptxas 報 10）、launch config、duration。
    - Details：GPU Speed of Light 是整體使用率；可切換 double／single／half precision roofline，標出達到 ceiling 所需的 AI；這個 kernel 是 memory-bound、AI 很低。
    - Matrix transpose 示範：naive 版 summary 指出 uncoalesced global accesses（而且是 **store** 不是 load），預估修好可快 76%；coalesced 版 compute throughput 從 5.9 變三倍以上、duration 大降，memory throughput 反而下降（之前是浪費的流量），但引入 shared memory bank conflicts（約 400 萬次）；no-bank-conflict 版降到 0，runtime 再大幅改善。Memory Workload Analysis 的圖和表可以看各層記憶體的 request 與 bytes。Coalescing 和 bank conflict 之後專門講（bank conflict 約在 L7）。
    - Baseline：選一個 kernel「Add Baseline」，其他 kernel 的結果就以百分比對照（例：coalesced 的 compute throughput +236%），可以加多個 baseline；換分析對象時要 Clear Baselines。
    - Raw 頁有全部 counter（例：`smsp__thread_inst_executed_per_inst_executed`、divergent branches），可以和自己推算的理論值對照。通常從 Summary 開始，再看 Details，很少直接看 Raw。
    - Source view：左邊 CUDA source、右邊 SASS（或 PTX）。例：計算 global thread ID 的那行對應 `S2R`（讀 CTAID、TID 特殊暫存器）和 `IMAD`（乘加 blockDim，blockDim 放在 constant memory）。SASS 是裝置專屬的機器碼，是實際執行內容的 ground truth；PTX 是虛擬 ISA。
12. **HW3 總覽**（p52）
    - 學習目標：理解 warp 的 control divergence；實作並 profile 有 warp divergence 的簡單 kernel；實作通用化的 tiled-phased MMULT；練習 kernel launch configuration 調校；用 Nsight Compute GUI profile kernel 執行與 occupancy、分析效能問題、最佳化 kernel。

## 名詞解釋

| 名詞 | 說明 |
|---|---|
| occupancy | SM 上 active warps ÷ 最大 warps；由 warps、block slots、registers、shared memory 四項中最緊的一項決定。 |
| theoretical / achieved occupancy | 依資源計算出的上限／實際執行時量到的平均值（NCU 的 Occupancy section 兩者都列）。 |
| SM sub-partition（SMSP、SP） | 每個 SM 分成 4 塊，各有自己的 warp scheduler、warp pool、register file 和 execution pipes；warp 固定在一個 SMSP 上。 |
| warp slot / block slot | SM 能同時容納的 warp 數／block 數上限，兩者是不同的限制。 |
| execution pipe | SMSP 裡的執行單元：FP32/FMA、INT、Load/Store、SFU、Tensor core 等。 |
| SFU | Special Function Unit，算 exp、sin、1/x 等。 |
| register spilling | 每個 thread 需要的 register 超過上限（255）或超過分配量，compiler 把多的放到 local memory（實際在 global memory），很慢。 |
| local memory | Thread 私有但實際放在 global memory 的空間；老師說這是他最討厭的 NVIDIA 用語，寧可叫 spill memory。 |
| L1 / shared memory carveout | 同一塊 on-chip 記憶體可在 L1 cache 和 shared memory 之間調整比例。 |
| Occupancy Calculator | Nsight Compute 內建工具，輸入 compute capability、threads/block、registers/thread、shared memory/block，算出 occupancy 與限制因素。 |
| `cuobjdump` | 查看編譯後 binary 的工具，可以列出每個 kernel 的 register、shared、local、constant 用量。 |
| ptxas verbose | 編譯時讓 `ptxas` 印出各 kernel 的資源用量（`-Xptxas -v` 或 `--resource-usage`）。 |
| conforming matrices | 維度相容、可以相乘的矩陣：M 的行數等於 N 的列數（inner-product 維度 K）。 |
| boundary check | 載入或寫回前檢查 index 是否在有效範圍內；tiled MMULT 中超出範圍時在 SMEM 寫 0。 |
| warp scheduler | 每個 SMSP 一個，每 cycle 從 eligible warps 中挑一個發出一道指令。 |
| active / eligible / selected / stalled warp | 已放進 slot／可以發指令／本 cycle 被選中／在等某件事（記憶體、運算結果、barrier 等）。 |
| stall reason | NCU 統計 warp 卡住的原因，例如 long scoreboard、short scoreboard、wait、barrier、math pipe throttle、MIO/LG throttle、no instruction。 |
| scoreboard | 追蹤指令結果是否已可使用的硬體機制；long 對應 global/local memory，short 對應 shared memory 或 SFU。 |
| latency hiding | 用大量 warp（和 ILP）填滿 stall 的 cycle，讓 issue slot 每個 cycle 都有指令可發。 |
| ILP | Instruction-level parallelism：同一個 warp 內，彼此不相依的指令可以在前一道還沒完成時先發出。 |
| Little's law（單一 scheduler） | 平均 active warps = issue rate × 每道指令的 cycles。 |
| wave / tail wave | 整個 GPU 同時容納得下的一批 block／最後一批不滿的 block。 |
| work distributor | 把 grid 的 block 分配到各 SM 的硬體排程器。 |
| control divergence（warp divergence） | Warp 內 thread 走不同路徑，各路徑依序執行，沒走該路徑的 thread 閒置。 |
| branch-induced / loop-induced divergence | 因 if 條件不同／因迴圈次數不同造成的 divergence。 |
| predicate（active）bit | SASS 指令附帶的每個 thread 的啟用位元；非 active 的 thread 結果會被丟棄。 |
| reconvergence | Divergent 的路徑跑完後，warp 內 thread 再回到同一條路徑一起執行。 |
| `__syncwarp()` | Warp 層級的同步。 |
| warp-phase | MMULT 分析用的計數單位：一個 warp 在一個 phase 中的執行。 |
| Nsight Compute（NCU） | NVIDIA 的 kernel profiler，有 CLI（`ncu`）和 GUI。 |
| injection layer | NCU 插在 CUDA runtime 和 driver 之間、攔截呼叫並收集 counter 的那一層。 |
| profiling pass / replay | NCU 為了收集所有 metric 而重跑 kernel 的次數；每次都還原記憶體、清 cache、鎖 clock。 |
| set / section / metric | NCU metric 的三層組織：set 由多個 section 組成，section 由相關 metric 組成。 |
| Speed of Light（SOL） | NCU 中表示 compute 與 memory 使用率占硬體峰值百分比的 section。 |
| baseline（NCU） | 把某次結果設為對照，其他 kernel 的 metric 以相對差顯示。 |
| uncoalesced access | 同一個 warp 的記憶體存取沒有落在連續區段，浪費 bandwidth（之後專門講）。 |
| bank conflict | 同一個 warp 存取 shared memory 同一個 bank 的不同位址，必須序列化（約 L7 講）。 |
| SASS | NVIDIA GPU 的實際機器組合語言，依架構不同，是執行內容的 ground truth。 |
| PTX | NVIDIA 的虛擬 ISA（中介表示），不綁定特定硬體。 |
| CTA | Cooperative Thread Array，SASS／PTX 中 thread block 的名稱；`S2R` 從 CTAID、TID 特殊暫存器讀 block／thread index。 |
| `IMAD` | SASS 的整數乘加指令。 |

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

**課務：HW、late days、pop quiz、TA**
- [00:08:00] HW2 今天截止，晚幾分鐘「不是世界末日」。HW3 今晚下課後發布。
- [00:09:02] [00:10:02] HW3 從 11/3（二）延到 11/6（五）；之後的作業都盡量排週五，這樣週末拖到週一只花 1 個 late day。
- [00:09:02] Late days 從今天開始生效，之前遲交的作業想用也可以。
- [00:10:02] [00:11:04] Late days 不能用在期末週的 final project 現場發表（約 10 分鐘，時段排定後不能改，除非有很強的理由），也不能用在 final report，因為要趕在學期最後一天前改完送成績。
- [00:11:04] 沒用的 late day 每天 0.5 分 extra credit，用了也不扣分。
- [00:11:04] [00:12:02] Pop quiz 每次 3 題，不算入基本分；基本分滿分 100 只有 4 份 HW 和 final project，extra credit 加在上面，只會加分不會扣分。
- [00:12:02] [00:13:03] 參加 pop quiz、Teams 上的討論、上課發問，在成績卡在邊界時都會納入考量。
- [00:13:03] 這些新規定還沒放上 Canvas，老師說隔天補。
- [00:13:03] [00:14:00] TA 說 office hours 很少人去；兩位 TA 都很強，卡住就去用。Devika 可以在週二上課前多開一小時，有興趣或想換時段就在 Teams 說。
- [00:14:00] [00:15:02] 上次 pop quiz 太趕，這次保證給滿 10 分鐘。[01:43:02] [01:44:00] 本次 quiz 8:15–8:25 PM，約 8:27 繼續上課。[01:59:23] Pop quiz 不是要考倒大家，只是複習基本觀念、增加參與。

**L3 複習中的觀念**
- [00:16:01] Analysis-driven optimization 流程是所有 kernel 開發和 final project 都要用的方法，業界實務也這樣做。
- [00:20:00] [00:21:01] 有同學問 naive 是什麼意思：就是最簡單、能正確平行執行、沒有任何最佳化的版本，資料全在 global memory，當之後改進的 baseline。
- [00:21:01] [00:22:01] 有重複存取同一份資料，就是 shared memory 可能派上用場的訊號；shared memory 比 global memory 快好幾個數量級。
- [00:05:03] [00:06:00] MMULT 會貫穿整學期，用來示範一連串越來越進階的最佳化，也可能是現在 production 上最重要的演算法。

**Occupancy 與資源**
- [00:04:00] Occupancy 有用也有限制，不是一個指標解決所有問題。
- [00:29:04] 每個 warp slot 保有完整 context（instruction pointer、registers 等），所以一個 cycle 內就能換 warp；GPU 靠很多 warp 輪流來隱藏 latency，而不是像 CPU 用大 cache 降低 latency。
- [00:30:04] [00:31:03] 這些資源都是「潛在」限制，通常同時只有一個真的卡住，要學會找出是哪一個。
- [00:36:03] [00:37:01] Warp 要等所需資源都夠了才會放進 slot；放進去就保證留在那個 SP，barrier 才不會 deadlock。
- [00:37:01] 之後的課程可能會用到 UW 的 GPU cluster（Hopper），老師之後會再說明（逐字稿是「GPU Telecom cluster」）。
- [00:41:03] [00:42:05] 經驗法則不是定律，但沒有其他資訊時先照著做；naive 版本寫完後，下一步要做什麼由 profiler 決定。
- [00:43:05] 不管硬體有 16 還是 32 個 core，執行單位永遠是 32-thread warp；128 threads/block 讓每個 SMSP 至少有一個 warp，是最低限度。
- [00:47:03] [00:49:02] 100 threads/block 不符合經驗法則，最後一個 warp 只有 4 個 thread 在做事。
- [00:51:00] [00:52:02] Block slots 和 warp slots 是不同的限制；grid 比整個 GPU 大時會分成多個 wave 執行。
- [00:54:03] [00:56:01] 每個 thread 超過 255 個 register 時，compiler 會「silently」把 register spill 到 local memory；老師說 local memory 是他最討厭的 NVIDIA 用語，因為它其實在 global memory。Register file 比 global memory 快三個數量級以上。
- [00:57:01] [00:58:01] Occupancy 是四項因素的最小值：「compute it, don't guess it」，也就是用 NCU 算。
- [00:58:01] [00:59:05] NVIDIA 寫函式庫的工程師會在執行期查詢裝置參數，動態選最佳版本，自己也可以這樣做。
- [00:59:05] [01:00:04] 開 Nsight Compute 一定要右鍵「以系統管理員身分執行」，否則讀不到 GPU counter、不會正常運作。只用 occupancy calculator 則不需要。
- [01:02:00] Shared memory 和 L1 共用同一塊；用不到 shared memory 就調小，剩下的自動給 L1 用。
- [01:03:01] [01:04:09] Calculator 算的 active threads 是以 warp 為單位，例如 300 threads/block 時會顯示 960 個 active threads，包含沒在做事的 thread。
- [01:05:01] [01:06:00] 起點是讓 warp 數盡量多，給 scheduler 更多可切換的選擇。
- [01:10:00] [01:12:03] 寫完 kernel 先用 `cuobjdump` 看 register 用量，再填進 calculator 確認 register 不是限制。

**Tiled MMULT 的邊界檢查**
- [01:14:02] [01:15:00] 目標是處理任意尺寸、維度相容的長方形矩陣；padding 會增加空間和傳輸時間，所以不採用。
- [01:19:04] [01:20:00] M 是 row-major 線性存放，所以超出右邊界的讀取會「換行」讀到下一列的值（合法但錯誤）；N 超出下邊界則是真的越界存取。
- [01:21:02] 越界存取可能直接 access violation 當掉，也可能只是讀到垃圾值。
- [01:25:01] [01:26:03] 用 2D（寬、高）思考邊界比用 1D index 直觀；超出範圍就寫 0，因為 0 不影響 inner product 的結果。
- [01:27:02] 載入（LOAD）和使用（USE）的檢查條件不同，不能擋掉只負責載入、不負責計算的 thread。
- [01:32:02] [01:34:06] p20 的 1D index 和比較條件有誤，應該用 M 的寬度；老師說會修正後重新上傳投影片。註解版 p20 已經改成 M_WIDTH（見「講義手寫註解」）。
- [01:37:01] 投影片上的程式碼故意沒有改完，因為通用化的實作是 HW3 的作業內容。
- [01:41:00] `__syncthreads()` 一定要放在 if 區塊外面；放在只有部分 thread 會進去的 if 裡面會 deadlock。沒通過檢查的 thread 也要走到 barrier 等其他 thread。
- [01:42:02] 邊界檢查的 if/else 依 thread index 決定，就是 control divergence。
- [01:43:02] Tile 仍是固定的方形，但 tile 大小是可調參數。

**Warp scheduling、divergence**
- [02:00:04] Warp scheduling 的投影片資訊量很大，課堂上不逐字講，要自己回頭讀。[02:16:00] [02:17:05] 看完 NCU 示範後再回來讀這幾頁，自己算一遍 p33 的數字是很好的練習。
- [02:03:03] Turing 每個 SMSP 的 warp pool 是 8 個 slot，Hopper／Ada 是 16 個。
- [02:05:03] 即使是浮點運算也要 2–4 個 cycle 才完成，發出後 warp 就會 stall。
- [02:10:00] [02:11:02] Global memory 存取約 400–600 cycle，需要更多 warp，再加上 ILP：發出非阻塞的 load 後，繼續做不相依的運算。
- [02:15:05] [02:16:00] Tail wave 和 serial fraction 是同一個概念：資料量越大、wave 越多，最後不滿的那一批占比越小。
- [02:17:05] 「Everything is row major, if you just remember row major.」記住這點在 CUDA 裡通常不會錯。
- [02:18:00] [02:19:04] 不能假設 warp 一定是 32，也不能依賴 warp 內或 warp 間的執行順序，需要時用 `__syncthreads()` 或 `__syncwarp()`。老師說依經驗 thread 0–31 大致依序，但 NVIDIA 沒有保證。
- [02:22:02] [02:23:01] Divergence 時每個 thread 仍然做了運算，只是非 active 的結果被丟掉；N 條路徑約等於 N 倍的執行時間。
- [02:29:00] 用 `blockIdx` 做判斷不會 divergence，因為同一個 block 內所有 warp 走同一條路。
- [02:32:01] Loop-induced divergence 中，一個跑很久的 thread（例如 8000 次）會讓整個 warp 效率很差。

**MMULT divergence 分析**
- [02:35:01] 16×16 block 時每個 warp 是 block 裡的 2 列。
- [02:41:05] [02:42:00] Type 2 block 中全程在範圍外的 6 個 warp 都「什麼都不做」，沒有 divergence；只有包含 row 96–99 的 2 個 warp 會 diverge，所以這個數字完全取決於 100×100 和 16×16 這組設定。
- [02:43:04] [02:44:04] 12.8% 是最壞情況上限；實際更低，因為 diverge 的 warp 裡很多 thread 仍在算有效值。老師說放大到 1000×1000 時比例會大幅下降（見「還要釐清的問題」）。
- [02:44:04] 載入 N tile 的 divergence 計算是 HW3 練習。
- [02:45:00] 不做邊界檢查的下場是結果錯誤，這不能接受；可以把資料合併成更大的問題來降低比例。有控制流程不代表一定有大量 divergence，要看演算法和實際情況。

**Nsight Compute**
- [00:07:03] [00:08:00] NCU 是整個 GPU track 的基本工具；最佳化有點像「black magic」，很多事要實際用工具才學得會。
- [02:47:01] [02:48:01] Profiling 很難不干擾效能，NCU 靠插入 injection layer 和讀取硬體 counter 達成。
- [02:50:00] 每個 pass 之間會還原記憶體、清 cache、鎖 clock，讓結果可重現。
- [02:52:03] 自己手畫 roofline 是為了理解，NCU 會依實測自動畫出來並算出 AI。
- [02:53:07] 「Theory gives upper bound.」理論分析是最好情況，實測包含各種 overhead。
- [02:54:14] Profile 時最好不要同時跑其他程式，以免影響結果。
- [02:58:00] [02:59:00] 一定要 profile Release build；開 line info 才能對照原始碼；開 ptxas verbose 看 register 和 spill。
- [03:02:03] Output 檔名加 `%i` 會自動編號，多次 profile 不會互相覆蓋。
- [03:03:01] 第一次 launch 是 warm-up，正式分析時應該跳過（這次示範故意沒跳過）。
- [03:05:03] Summary 頁的自動規則分析很準，是排查問題的第一站；這次直接指出 thread divergence。
- [03:07:01] NCU 顯示 16 個 register，但 ptxas 報 10 個，老師覺得有趣但沒解釋。
- [03:12:09] [03:13:04] Naive transpose：NCU 指出問題在 global **store** 沒有 coalesce，預估可快 76%，老師說這個判斷完全正確。
- [03:14:02] 數字上升或下降不一定代表變好或變壞，要知道原因；例如 memory throughput 下降可能是少了浪費的流量。
- [03:15:01] 排查順序：先看 Summary 的建議，再到 Details 對應的 section。
- [03:18:00] Shared memory bank conflict 之後會專門講一整堂（大約 lecture 7）。
- [03:22:02] [03:23:02] Baseline 讓多個版本在同一個畫面上量化比較；「higher or lower」不等於「better」，要看是哪個 metric。
- [03:24:02] 某個值是 0 也不一定代表什麼，例如 naive 版沒有 bank conflict 是因為根本沒用 shared memory。
- [03:26:01] [03:27:04] Raw counter 可以拿來驗證自己推算的理論值，但平常很少直接看，先看 Summary 再看 Details。
- [03:31:01] SASS 是實際執行內容的 ground truth；PTX 是抽象的中介表示。
- [03:31:01] [03:32:00] HW3 會用 NCU，內容包括 control divergence、通用化的 MMULT 和 profiling；有問題就找 TA。

## 講義手寫註解（`Au26_GPUCompute_L4_w_notes.pdf`）

老師上課時在投影片上寫的紅字和螢光筆，10/28 上傳。文字層和原版相比只改了一處：p20 的 1D index 從 `M[Row*M_HEIGHT + …]` 改成 `M[Row*M_WIDTH + …]`。其他差異都是筆跡。沒有筆跡的頁（p1–2、p11–12、p14、p16–17、p24、p26–36、p40、p42–45、p47–48、p51）不列。

**課務**
- （註解 p3）螢光筆標出「Late Days Policy」和「1 late day」（週末算 1 天）。
- （註解 p52）HW3 截止日原本是「11/03/26 5:59 PM」，已劃掉，改寫成「11/6 11:59 PM」。Learning objectives 中，control divergence、divergent kernel、通用化 MMULT、Nsight Compute GUI 這四項畫了箭頭，MMULT 有底線；launch configuration 調校那一項沒畫。

**L3 複習與 occupancy**
- （註解 p4）「Analysis-driven optimization process → use in Final Project!」；Arithmetic Intensity 那行加了外框；redundant GMEM accesses 畫底線；`__syncthreads()` 旁寫「RAW, WAR」，也就是 barrier 要防的 read-after-write 和 write-after-read hazard。
- （註解 p5）在 registers、shared memory、block slots、warp slots、barriers 旁加大括號，寫「potential limiting factors」。SM 圖上標出「SMSP」和「cuda cores = FP32/INT32 ALU」，旁邊另畫「SFU」和「TC」（Tensor Core）方框。
- （註解 p6）「Provide a lot of threads」上面寫「(warps)」；「Minimize warp divergence → wasting threads」；memory hierarchy 的 deep dive 從「Lecture 5」補成「5, 6, 7…」。
- （註解 p7）左邊畫一個 SM 的 4 個 SP（SP0–3），各分到 warp（W0/W4、W1/W5…），表示 warp 輪流分給各 SP。「FP32/INT32, Tensor Core…」旁寫「pipes」；「32 lock-step threads」旁寫「SP level」。表格中 thread blocks/SM、threads/block、registers/thread、shared memory/SM 畫了箭頭，threads/SM 和 Turing T4 打了星號。
- （註解 p8）例題的手寫答案（Turing，1024 threads/SM、16 blocks/SM）：
  - A：block size 1024／512／256／128／64／32 依序放得下 1、2、4、8、16、16 個 block；32 threads/block 時卡在「16 blocks/SM = 50% occ」。
  - B：100 threads = 32×3 + 4，所以要 4 個 warp；寫「10」、「4×10 = 40」和「1000/1024」。這和口頭答案一樣，但和 Turing 的 32 warps/SM 衝突，見「還要釐清的問題」第 5 點。
  - C：768 threads 時是 1 個 block、24 個 warp，768/1024 = 0.75。
  - D：要 full occupancy（1024 threads）時每個 thread 最多 64 個 register；每個 thread 用 128 個時只剩 512 threads；300 個超過「max 255」，多的會「put in local memory」。
- （註解 p9）Occupancy Calculator 旁寫「(no longer the old Excel..)」。
- （註解 p10）「minimum」畫底線；四項因素後面補「/SM」；「Compute it, don't guess it」底下寫「use NCU」。

**Tiled MMULT 的邊界檢查**
- （註解 p13）標出「GMEM」、「N: 3×3」、「M: 3×3」，強調 Phase 1 的「Loads」和「2×2 tiles」。M、N 超出範圍的那一排 tile 塗成黃色。
- （註解 p18）畫一張 2D 示意圖（x 寬、y 高），說明要用 2D 範圍檢查。「0 value…」那行旁寫「ab + cd + ef + gh…」，其中一項改成 0，表示補 0 不影響 inner product。LOAD 和 USE 畫了底線。「input matrix data ranges」上寫「M, N」；「phase #」上寫「(p)」，並和 TILE_WIDTH 一起畫底線。
- （註解 p19）用綠筆標出維度：M 是 N（高）× K（寬），N 是 K（高）× N（寬），也就是 K 是 inner-product 維度。這是另一套命名，和 p25 的 J×K、K×L 不同，要對照著看。
- （註解 p20）2D 那行畫箭頭；條件 `p*TILE_WIDTH+tx < Width` 的「Width」劃掉，改寫「M-WIDTH」。圖上標「p=0」、「p=p」。這證實了口頭更正（[01:32:02]、[01:34:06]）。
- （註解 p21）「Each thread loads」後面補「Row」。
- （註解 p22）大括號標成「updated LOAD phase」；M、N index 裡的 `Width` 都打了星號（要通用化的地方）；`ds_N[ty][tx] = 0.0` 旁寫「outside valid input data ranges」；`__syncthreads()` 畫箭頭。
- （註解 p23）`if(Row < Width && Col < Width)` 的兩個 Width 上寫「generalize! TODO」，這就是 HW3 要做的。Pvalue 那行旁寫「will use zeros if outside data range」。`__syncthreads()` 旁寫「CAREFUL this is outside the if-block!」，對應 [01:41:00] 的 deadlock 警告。最後的寫回條件旁寫「don't write to invalid output location!」。
- （註解 p25）在「(j × k)」和「(k × l)」的 k 下面畫底線，強調 inner-product 維度要一致。

**Warp divergence**
- （註解 p37）畫一個分岔成 1、2、3 條路徑的分支圖。旁邊寫「thread active predicate bit」，用 T0–T3 的位元（case 1：0 0 1 1；case 2：1 1 0 0）說明不同路徑由 predicate mask 決定哪些 thread active。
- （註解 p38）時間軸「t ↓」。
- （註解 p39）「traversed one at a time」後面補「(by all threads)」，意思是整個 warp 依序走過每條路徑。
- （註解 p41）branch-induced 圖上方寫「real execution of warp」，並在旁邊畫時間軸。
- （註解 p46）Type 2 block 旁標 row 96、100、112：96–99 這 4 列在範圍內，100 以後在範圍外，並畫箭頭指出全程在範圍外的 6 個 warp。

**Nsight Compute**
- （註解 p49）Profiled execution 圖下寫「Profile 1..N passes」；右邊寫「Sets → Sections → specific metrics」。
- （註解 p50）「GPU Speed of Light Roofline Chart → gives real world measured results including all overhead etc.」；在 ceiling 上標一點，寫「theory gives upper bounds」，對應 [02:53:07]。

## 和作業 / 考試的關聯

- **HW2**（10/27 二 5:59 PM PDT，今天截止）：老師說晚幾分鐘沒關係，而且 late days 從今天起生效（[00:08:00]、[00:09:02]）。`gpu/assignments.md` 最後記錄的繳交狀態是 unsubmitted，請自己確認是否已交。
- **HW3 — Control Divergence & Tiled MMULT improvements & NCU profiling**（Canvas id 11810628）：**11/6（五）11:59 PM PST**（`due_at` 2026-11-07T07:59:59Z，11/1 之後是 UTC−8）。`gpu/assignments.md` 還寫 11/3 5:59 PM 和「未發布」，要由晨報更新。HW3 說明 PDF 是 Canvas file 155100870。對應本講：
  - 通用化 tiled MMULT（J、K、L 三個維度 + LOAD／USE／寫回的邊界檢查），p22–p23 的 to-do（[01:37:01]）。
  - 載入 N tile 的 control divergence 分析（p48），方法照 p43–p47 的 M tile 分析。
  - 寫會 diverge 的簡單 kernel 並 profile（類似 loop divergence demo）。
  - Launch configuration 調校、Occupancy Calculator、NCU GUI（Summary、Details、Roofline、Baseline、Source view）。
  - 提醒：課程 AI policy 使用者表示不介意，但這份筆記刻意沒有替 HW3 寫出 N tile 的分析或通用化 kernel；那部分要自己做。
- **Late days**：共 7 天；週末算 1 天；不能用在 final project 發表和 final report；沒用完每天 +0.5 分。HW 改成週五截止後，週一交只花 1 天。
- **Pop quiz**：Pop Quiz - Lecture 4 - 10/27（Canvas assignment 11860516、quiz 2457104）8:15–8:25 PM 開放，lock 2026-10-28T03:25Z（10/27 8:25 PM PDT）。之後每次 3 題、最多 2 分 extra credit。
- **Final project**：發表在期末週（線上，約 10 分鐘），final report 在學期最後一天，兩者都不能用 late day。
- 本課沒有考試；基本分 = 4 份 HW + final project。

## 還要釐清的問題

1. **HW3 截止時間**：p2、口頭（[00:09:02]、[03:31:01]）、Canvas `due_at` 都是 11/6（五）11:59 PM；原版 p52 還寫 11/03 5:59 PM。**已解決**：註解版 p52 把舊日期劃掉，手寫改成 11/6 11:59 PM。
2. **HW4 和 project proposal 會不會也改到週五？** 老師說「之後的作業盡量都排週五」（[00:10:02]），但 HW4（目前 11/10 二）、Project Proposal（11/17 二）還沒公布新日期。
3. **Late days 和原本的遲交扣分規則怎麼併用？** Syllabus 原本是遲 1 天 −1 分、之後每 24h 再 −1 分。Late days 用完之後是否回到原本的扣分方式，老師沒說；等 Canvas 更新。
4. **Pop quiz 配分**：L3 的 pop quiz 在 Canvas 上是 3 分（`gpu/assignments.md`），但 p3 和口頭說每次最多 2 分 extra credit（0.5 參加 + 每題 0.5）。3 題全對應該是 0.5 + 1.5 = 2 分，和 Canvas 的 3 分不一致，看 Canvas 怎麼算。
5. **例題 B（100 threads/block）的答案**：老師口頭答 Turing 可以放 10 個 block、40 個 warp（[00:49:02]–[00:50:00]）。但 Turing 每個 SM 最多 32 個 warp（p7），每個 block 4 個 warp，所以應該只能放 8 個 block（32 warps，warp occupancy 100%，但只有 800 個 thread 在做事，約 78%）。這是我自己的推算，和 calculator 示範中 300 threads/block 依 warp 數算出 3 個 block 的做法一致（[01:04:09]、[01:05:01]）；可以用 Occupancy Calculator 驗證。註解版 p8 的手寫答案也是「4×10 = 40」和「1000/1024」，和口頭答案一樣，所以老師的版本沒有考慮 warp slot 的限制。可以在 Teams 上問。
6. **p7 的 Turing 數字**：老師一度懷疑 Hopper 的 64 warps/SM，後來自己驗算說是對的（[00:37:01]–[00:39:06]）。[00:38:02] 他把「每個 SP 16 個 core」說成「16 thread blocks per SM」，是口誤。
7. **Warp pool slot 數**：老師口頭說 Turing 每個 SMSP 8 個 slot、Hopper／Ada 16 個（[02:03:03]），和 p7 的「32 (8/SP)」一致；但 [00:29:04] 又說一般是 8、12 或 16。p29 的 16 slots 是示意圖。
8. **NCU 顯示 16 個 register、ptxas 報 10 個**（[03:07:01]）：老師沒解釋。我推測是 register 以 warp 為單位、有分配粒度（per-thread 數量會向上取整），NCU 顯示的是實際分配量；待確認。
9. **放大到 1000×1000 時 divergence 比例會降多少？** 老師說「大概兩個數量級」（[02:44:04]）。用同樣方法自行估算：TILE_WIDTH = 16 時有 63 個 phase，Type 1 只有最後一個 phase diverge，比例約 1/63 ≈ 1.6%，比 12.76% 小約 8 倍，比較接近一個數量級。值得在 HW3 用 NCU 實測驗證。
10. **p20 的 1D index 和條件**：p20 寫 `M[Row * M_HEIGHT + p*TILE_WIDTH+tx]` 和 `p*TILE_WIDTH+tx < Width`，老師說應該是 M 的寬度（[01:32:02]、[01:34:06]）。**已解決**：註解版 p20 的文字層已經改成 `M[Row*M_WIDTH + p*TILE_WIDTH+tx]`，條件裡的 `Width` 也劃掉、手寫改成 M_WIDTH。所以正確的條件是 `(Row < M_HEIGHT) && (p*TILE_WIDTH+tx < M_WIDTH)`。
11. **新的課務規定何時上 Canvas**：老師說 10/28 會把 late days、pop quiz 規則放上 Canvas（[00:13:03]），晨報可以留意。
12. **Devika 週二課前 office hour（5:20–6:20 PM）** 要看有沒有人表示興趣才會開，目前未定。
