# GPU Lecture 5 — 2026-11-03（Global memory 與 DRAM、burst / 32-byte sector、coalesced access、MMULT 存取模式、SGEMM Kernel 2、Nsight Compute 記憶體表格 demo、HW4）

> 來源：transcript（Teams 自動逐字稿 `transcript.vtt`，2072 cues，00:00:03–03:15:53，約 3 小時 16 分；錄影檔 `Weekly Live Lecture-20261103_183100-Meeting Recording.mp4`）、slides（Au26_GPU-Compute_Lecture5.pdf，Canvas file 155723617，50 頁；另有 `Au26_GPU-Compute_Lecture5_w_notes.pptx`，file 155737575，這次沒有擷取）、閱讀章節：Reading Set #3 = PMPP 4th ed. Ch5 全章（10/19 起，對應 L3–L5、HW2–3）；Reading Set #4 = PMPP Ch6（11/3 起，Canvas 頁面 11/4 00:40 UTC 更新）。本講 DRAM burst、memory coalescing、corner turning 對應 PMPP Ch6 §6.1（memory coalescing），DRAM 平行度與 latency hiding / bytes in flight 對應 §6.2（自行對照）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：sam's → SMs；SIAS → SASS；N site compute / Nsite / insight → Nsight Compute；Kublas / Kublast → cuBLAS；SGM / S gem / S-GEM → SGEMM；BLAST level 3 → BLAS level 3；matrix malt / basic matrix mold → matrix mult；Colonel → kernel；selectors（[00:46:04]）→ sectors；cash lines → cache lines；log（[00:57:00]）→ LDG（load global，老師自己更正）；FB 32s → FP32s；HPM → HBM；GDDR6X32 → GDDR6 x32 chip；touring → Turing；"120 bytes"（[00:10:03]）→ 128 B cache line；"500 milliseconds"（[01:06:02]）→ 500 ns（講義 p25）；"A100 ... 768 GB/s"（[01:07:03]）→ RTX A6000（A100 不是 768 GB/s，講義 p25）；"584 kilobytes" → 384 KB（老師自己更正）；"4092 ... not evenly divided by 32, 4096 is"（[02:03:00]）意思是 4092 不是 32 的倍數；ALAN. SLN → SLN（課號）；May Lim → 學程主任（名字照逐字稿）；Diya、Devika 是兩位 TA；"Dirt Winter 27" → 推測是 Winter 2027 課綱檔名；Phoebe / Lim（[02:45]–[02:46]）是 demo 時的雜音。
>
> 錄影注意：錄影 18:31 開始，[00:00:03] 就開始上課（約 6:31 PM）。[01:43:02] 8:15 PM 休息，8:20–8:30 PM pop quiz（3 題），[01:44:20]–[01:59:22] 約 15 分鐘空白。[02:00:30] 起老師換電腦做 Nsight Compute demo，[03:05] 回投影片收尾，[03:11]–[03:15] 是下學期課程的 Q&A。老師說今天比較早結束，以後也會盡量準時。

## 重點摘要

1. **課務更新**（p2、p49）
   - HW3 截止 **11/6（五）11:59 PM PST**；HW4 今晚下課後發布，截止 **11/13（五）11:59 PM PST**。HW4 是最後一份 HW，之後只剩 final project（[00:02:01]）。週末用 late day 只算 1 天。
   - Final project 細節下週 L6 公布，老師要大家一定要來或看錄影（[00:03:01]、[03:15:00]）。
   - HW 佔 50%，HW4 也有 extra credit（[00:02:01]–[00:03:01]）。HW1、HW2 由 TA 批改，預計一週內出成績（[00:10:03]）。
   - Winter 有後續課程（Spring 也有），SLN 這週會開，老師把 Winter 27 課綱貼在 Teams 會議 chat（[03:12:02]–[03:14:04]）。內容：multi-GPU、multi-node、Hopper、新的 tensor core、DGX / NVLink switch 系統（[03:13:01]）。
2. **GPU kernel 開發流程**（[00:05:00]）：先寫 naive（只用 global memory、無最佳化）能跑的版本 → 套用最佳化概念 → 每次都重新 baseline、驗證答案、profile → 重複。
3. **為什麼記憶體是第一個瓶頸**（p4）：RTX A6000 FP32 峰值 38.7 TFLOP/s vs DRAM 768 GB/s，ridge ≈ 50 FLOP/B。vector add ≈ 1 FLOP/12 B，cuBLAS SGEMM ≈ 245 FLOP/B（講義 p4）。
4. **記憶體子系統**（p6、p18）
   - L1/shared memory：SRAM，32 banks × 4 B = 128 B 存取寬度，等於一條 cache line（4 sectors）。下週 L6 才深入 shared memory。
   - Global memory：off-chip DRAM（GDDR 或 HBM），在 GPU 板子上但不在 SoC die 上（[00:14:00]）。
   - 延遲量級（p18–p19）：register ≈1 cycle、L1 ≈30、L2 ≈200、DRAM ≈400–800 cycles。所有 global 存取都**經過** L2（不一定命中）（[01:11:02]）。
   - NVIDIA 的命名是「越上層越快」，老師提醒討論時要講清楚，因為有人反過來叫（[00:09:02]）。
5. **DRAM 基礎**（p7–p14）
   - Cell = 1T1C（一個電晶體＋一個電容），讀取是 destructive read，要寫回；電荷會漏，要定期 refresh（講義寫 32–64 ms；老師口頭說 few milliseconds）。
   - 讀取流程：ACTIVATE（整列讀進 row buffer，每 bank 約 1–2 KB）→ READ（選一小段經 pins 以 burst 送出）→ PRECHARGE（關列）。每段延遲約 10–20 ns，等於幾十個 GPU cycle。
   - Row hit ≈1×、row empty ≈2×、row conflict ≈3×（p10）。memory controller 會重排請求以增加 row hit。
   - 平行度：一顆 GDDR6 x32 = 2 channels × 16 banks；A6000 有 12 顆 → 384 banks（p11）。位址經 hash 平均分散到各 channel / bank。
   - **Access granularity = channel width × burst length = 32 B**，GDDR6 / GDDR6X / HBM2 / HBM3 全部一樣，Turing 到 Hopper / Blackwell 都是（p12）。
   - 峰值頻寬 = (bus width ÷ 8) × 每 pin data rate：A6000 384/8 = 48 B × 16 GT/s = 768 GB/s；H100 SXM 5120-bit ≈ 3.35 TB/s；B200 ≈ 8 TB/s（p14）。bus 變寬是「同時更多 32 B atom」，不是 atom 變大。
   - GDDR：板上晶片、窄 bus 快 pin、便宜、消費級；HBM：interposer 上的 stack、超寬 bus、data center（p13）。
6. **一次 global load 的生命週期**（p19）：warp 發出 LDG（32 個位址）→ coalescer 找出不重複的 32 B sectors → L1 lookup → crossbar → L2 slice（位址 hash 決定）→ memory controller 排隊重排 → DRAM ACT/RD → 資料回填 L2、L1、register。
7. **Sector 與 cache line**（p20）：sector = 32 B = 8 個 float；cache line = 128 B = 4 sectors（tag 單位，但 fill / evict 以 sector 為單位）。只要碰到 sector 裡 1 byte，整個 32 B 都要搬。
8. **Coalescing 的效率**（p21–p22）：efficiency = 請求的 bytes ÷ (sectors × 32 B)。
   - `a[tid]`：4 sectors，100%；`a[tid+1]`：5 sectors，80%；`a[2*tid]`：8 sectors，50%；stride ≥ 8（4 B 元素）：32 sectors，12.5%。
   - sector 數本身不代表好壞，要看資料型別：char 1 sector、float 4、double 8、float4 16 sectors 都是 100%。
   - Broadcast（全 warp 讀同一個 word）只要 1 sector，也算 coalesced。
9. **AoS vs SoA**（p23）：`pts[tid].x` 的 AoS 每 thread 間隔 16 B → 16 sectors、25% 有用；SoA `xs[tid]` → 4 sectors、100%。原則上 SoA 較好；但如果每個 thread 用一次 float4 讀整個 struct，AoS 也可以。`cudaMalloc` 至少 256 B 對齊；2-D row pitch 最好是 128 B 倍數（`cudaMallocPitch`）（講義 p23）。
10. **判斷是否 coalesced 的規則**（p24、p29）：index 寫成 `A[(與 threadIdx.x 無關的項) + threadIdx.x]`。row-major 下 `a[row*N + threadIdx.x]` 是 coalesced，`a[threadIdx.x*N + col]` 是 stride N。
11. **Little's law / bytes in flight**（p25）：bytes in flight = bandwidth × latency。A6000：768 GB/s × 500 ns ≈ 384 KB ≈ 12,000 sectors ≈ 3,000 個 128 B warp load ÷ 84 SMs ≈ 每 SM 36 個未完成 warp load。coalescing（每個請求的 bytes 有用）和大量 warp（請求數量多）兩者都要。
12. **Caches 與 store**（p26，多數講義內容）：L1 不跨 SM coherent、不存 dirty global 資料，store 直接送 L2；L2 write-back。store 也會 coalesce；零散的部分 sector 寫入可能多花 DRAM 工作（如 ECC read-modify-write）。cache 不能取代 coalescing（講義 p26）。可以用特殊指令 bypass cache，但課程不會深入（[01:12:00]）。
13. **Naive MMULT 的存取模式**（p29–p34）：`A[row*width+k] * B[k*width+col]`，blockDim(32,32) 時一個 warp 的 row 固定、col = 0..31。
    - A：全 warp 讀同一個值 → broadcast，1 sector。
    - B：32 個連續 float → coalesced，4 sectors。
    - C store：coalesced。
    - 用 4×4 矩陣、2×2 block、2×2 grid 的表格逐格推（p34），老師建議自己做一兩次。
    - 冗餘：不同 row 的 warp 重複讀同一組 B column（[01:24:00]）——這是 shared memory tiling 解決的；但 tiled kernel 從 global 搬到 shared 時 A 仍然 **沒有 coalesced**（[01:25:04]）。
14. **Transpose pattern / corner turning**（p35）：host 先把 M 轉置（存成 column-major）再送到 device，讓 M、N 從 global → shared 都用同一個 coalesced 的存取方式；shared memory → register 沒有 coalescing 要求。兩種做法：(a) 寫進 shared 時「轉回來」，乘法照舊；(b) 照轉置存進 shared，乘法時用轉置的 index（column × column）。**這就是 HW4 要寫的 kernel**（[01:42:03]）。
15. **SGEMM case study（siboehm/SGEMM_CUDA）**（p36–p44、p47）
    - C = α·A·B + β·C，M = N = K = 4092：≈137 GFLOP、最少讀 201 MB、寫 67 MB、合計 ≈268 MB；peak 運算 ≈3.5 ms vs peak 頻寬 ≈0.35 ms → 好的 SGEMM 是 compute bound。4092 不是 32 的倍數，邊緣 tile 只有 28 行/列有效（tile quantization）。
    - **Kernel 1（naive）**：這份 code 的 x = row、y = col（和平常相反）。blockDim(32,32)，warp 內 threadIdx.x 變 → row 變 → A 讀 stride K（16,368 B）→ 32 sectors；B broadcast 1 sector；每 warp 每 iteration 33 sectors 換 64 FLOP；C store 也是 32 sectors。309 GFLOP/s、≈15 GB/s。
    - **Kernel 2（coalesced）**：1-D block 1024 threads，`cRow = blockIdx.x*32 + threadIdx.x/32`、`cCol = blockIdx.y*32 + threadIdx.x%32` → 一個 warp = C 的一列。A broadcast 1 sector + B 4 sectors = 5 sectors/iteration；C load / store 各 4 sectors。1,986.5 GFLOP/s、≈110 GB/s，約 6.4× 快（老師口頭說 6×）。SASS 完全一樣，只改 index mapping；coalescing 是 runtime 由硬體做。
    - 因為 N = 4092，B 的奇數列從 sector 中間 16 B 開始 → 5 sectors（80%）；改成 4096 或用 pitch padding 就沒有（p43、[02:21:03]）。
    - 只有 cuBLAS 的 8.5%：coalescing 只改善「怎麼抓」，沒減少「抓幾次」；AI ≈0.5 FLOP/B 遠低於 ridge 50；接下來 Kernel 3 SMEM caching → 4–5 blocktiling → 6 vectorized → 9 autotuning → 10 warptiling（p47）。
16. **Nsight Compute demo**（[02:23:01]–[03:05:00]）：在 debugger 看 warp info，再用 NCU 的 Memory Workload Analysis → Memory Tables 驗證預測（詳見下方「老師強調」）。
17. **Key takeaways**（p48）：DRAM 以 32 B burst 搬；開 row 很貴；sector 是各層的通貨；一個 warp 存取 = 一個 request，成本 = 碰到幾個不同 sector；threadIdx.x 對應連續資料；coalescing 必要但不充分。

## 名詞解釋

- **1T1C**：DRAM cell，一個 access transistor＋一個 storage capacitor（femtofarad 級）。比 SRAM（6 個電晶體）密度高很多。
- **Wordline / bitline / sense amplifier**：wordline 選列；cell 電荷分享到 bitline；sense amp 把小 ΔV 放大成邏輯電位。
- **Destructive read / refresh**：讀取會把電荷放掉所以要寫回；電荷會漏所以要定期重讀重寫。
- **Row buffer**：ACTIVATE 後整列（約 1–2 KB）放在 sense amps 上，之後同列的讀取很便宜。
- **ACTIVATE / READ / PRECHARGE；tRCD、CL、tRP**：開列、讀欄、關列；對應的時間常數（row→column delay、CAS latency、precharge time）。
- **Row hit / row empty / row conflict**：目標列已開 / bank 已 precharge / 開著別的列。
- **Channel / bank group / bank**：DRAM 的平行階層。一顆 GDDR6 x32 = 2 channels × 4 bank groups × 4 banks。
- **Burst length / beat**：一次存取在 pins 上連續傳的拍數。channel width × burst length = 32 B。
- **GDDR / HBM**：板上獨立晶片、窄而快 vs 疊在 interposer 上、超寬 bus 的 stacked DRAM（TSV 連接）。
- **Memory controller**：在 GPU die 外圍，負責把請求送到正確 channel、排隊與重排。和 channel 不一定 1 對 1（p16）。
- **L2 slice**：L2 分成多片，由位址 hash 選片。
- **Crossbar**：SM 與 L2 slices 之間的 on-chip interconnect。
- **LDG / STG**：SASS 的 load global / store global。
- **Coalescer**：把一個 warp 的 32 個位址合併成最少的 32 B sectors。
- **Sector**：32 B，記憶體各層的最小傳輸單位。
- **Cache line**：128 B = 4 sectors，是 cache 的 tag 單位。
- **Request / wavefront**：NCU 表格裡的欄位。一個 warp 的一條 load 指令 = 一個 request；wavefront 之後再講（[03:01:06]）。
- **Sectors per request**：NCU 衡量 coalescing 的指標；32 × 4 B 讀取的理想值是 4，32 代表完全分散。
- **Fully coalesced**：warp 存取剛好落在最少的 sectors 裡（含 broadcast、同 sector 內任意排列）。
- **Broadcast**：warp 內多個 thread 讀同一個位址，只請求一次再分送。
- **AoS / SoA**：array of structs / struct of arrays。
- **Little's law**：bytes in flight = bandwidth × latency。
- **Compulsory traffic**：最少必須搬的資料量（每個矩陣只讀一次）。
- **Tile quantization**：矩陣大小不是 tile 的整數倍時，邊緣 block 有閒置 thread。
- **Corner turning / transpose pattern**：先轉置其中一個矩陣，讓 global → shared 的搬運都 coalesced，再在 shared memory 用轉置的 index 計算。
- **SGEMM**：BLAS level 3 的單精度 general matrix multiply，C = αAB + βC。
- **CTA**：cooperative thread array，就是 thread block（debugger 裡的欄位名）。
- **`cudaMallocPitch`**：配置 2-D 陣列時把每列補齊對齊。

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

- [00:02:01] HW3 改到這週五、HW4 下週五；HW4 是最後一份 HW。
- [00:04:00]–[00:06:00] 開發流程：先 naive 能跑 → 最佳化 → 每次都 re-baseline、驗證正確性、profile → 重複。老師說這是可以一直回來參考的 rule of thumb。
- [00:07:06] compute 和頻寬差約 50 倍，記憶體存取不能浪費、不能重複，否則永遠達不到想要的 AI。
- [00:11:03]–[00:12:02] 要記住 sector = 32 B、cache line = 4 sectors；今天講 global memory，shared memory 下週。
- [00:16:01]–[00:17:06] 開列很慢；資料有空間/時間 locality 的話，同一列可以多讀幾次，不必重開。
- [00:20:00]–[00:22:02] 不同 DRAM 的 pin 數和 bus 寬差很多，但每次讀取都是 32 B——這是重點。
- [00:23:02] 要有夠多獨立的讀取請求（來自所有 SM、所有 warp），channel 和 bank 才能連續被餵滿。
- [00:27:01]–[00:28:02] 寫 kernel 時不必管是 GDDR 還是 HBM，只要用好 32 B 和 burst mode；不用為每種 DRAM 調 kernel。
- [00:28:02]–[00:29:06] 做 roofline 時如果沒給峰值頻寬，用 bus width ÷ 8 × 傳輸率自己算（A6000 → 768 GB/s）。
- [00:32:04] 所有請求都打同一個 channel 是最壞情況，可以用 profiler 看出來。
- [00:39:03]–[00:40:04] 後面每一版 kernel 都在想辦法讓請求獨立、讓記憶體 pipeline 一直滿，因為 compute 快太多，要先顧資料進來。
- [00:42:03] 一個 warp 請求 4 個 sectors 不一定差，32 個 float 就是 128 B，4 sectors 是 100% 效率。
- [00:47:02]–[00:48:05] 起始位址偏一格就多一個 sector：5 sectors 只用 4 個 → 80%。只要碰到 sector 的 1 byte，就要整個抓。
- [00:50:00] stride 很大時 float 是 12.5%；如果是 byte 存取最壞是 1/32。
- [00:52:01] 光看 sector 數看不出效率，要知道資料型別。
- [00:55:03] 一般來說 SoA 對 global memory 的存取模式比較好。
- [00:56:03]–[01:00:01] 學生問：同一個 thread 會用到 struct 的其他欄位時效率還是 25% 嗎？老師說要從「每一條 LDG 是 32 個 thread 同時發出」的角度看；先用 cooperative load 搬進 shared memory 可以繞過，但那是更進階的設計。「there's always probably a valid counterargument」——重點是理解原理後有根據地選。
- [01:02:00]–[01:04:03] 固定 row、thread index 遞增 → 連續；`threadIdx * N + col` → stride N，N 越大越糟，直到每個 sector 只用一個值。
- [01:06:02]–[01:08:04] Little's law 例子：約 384 KB in flight ≈ 12,000 sectors ≈ 3,000 個 warp load ≈ 每 SM 36 個；有 12–16 個 warp slot 加上 warp 內獨立指令，是做得到的。
- [01:09:00] coalescing 和很多 warp 兩者都需要，才能從 memory bound 走到 compute bound。
- [01:10:05] 之後講到 tensor core，flops 又再高一個數量級，記憶體壓力更大。
- [01:16:00]–[01:17:01] 課堂提問：naive MMULT 的 row 和 col 哪個 coalesced？答案：row 不好、col 好（只有 col 含 threadIdx.x）。
- [01:22:03]–[01:23:04] 全 warp 讀同一個 A 位址 → broadcast，只要一個 sector；B 讀取與 C 寫入是 coalesced。
- [01:25:04] shared memory tiled kernel 解決了冗餘，但 global → shared 時 A 仍沒 coalesced，所以還能再快。
- [01:26:07] 投影片裡矩陣名字一下 A/B 一下 M/N，老師為此道歉。
- [01:27:00] 這種逐格推表的練習，自己做一兩次很有用。
- [01:31:02] 老師在推表時說「this is actually sorry, this is wrong」，自己更正了 B 的元素是連續的。
- [01:38:01] 目標就是 global → shared 的存取全部 coalesced；shared → register 怎麼讀都可以。
- [01:40:02] 轉置後乘法仍要算 P = M × N，要確定答案正確；兩種做法（寫入時轉回來，或讀出時用轉置 index）都可以。
- [01:42:03] **HW4 就是做這個 transpose pattern 的 kernel**，要和之前的 shared memory kernel 一起 profile 比較，應該看到效能提升；demo 會示範要看 NCU 的哪些 metrics。
- [02:06:02]–[02:07:03] SGEMM 範例的 x/y 和平常相反（x = row），各處 kernel 都不一致，要習慣切換。
- [02:13:02]–[02:14:02] Kernel 1 每 warp 每 iteration 33 sectors，AI 不到 1；C store 也是 strided。
- [02:17:01] Kernel 2 的 SASS 和 Kernel 1 一樣，只改 index；coalescing 在 runtime 做，因為 compile 時不知道對齊。
- [02:21:03] 4092 造成奇數列多一個 sector；改成 4096 就消失。
- [02:22:02] 6 倍加速「Nothing to shirk about」，但還只是 cuBLAS 的一小部分。
- [02:32:04] **profile 一定要用 release build**；NCU 的檔名用 `%i` 會自動遞增（[02:34:02]）。
- [02:35:00] 4×4 矩陣、2×2 block、2×2 grid：預測 global load 32 instructions / 32 requests / 32 sectors、1 sector/request，store 4 —— NCU 結果完全吻合。實際搬 1024 B，但只需要 128 B → 8 倍多餘（[02:36:03]–[02:37:02]）。
- [02:44:00]–[02:46:05] NCU 出問題時要重開，而且一定要右鍵 **run as administrator**。
- [02:46:05]–[02:52:01] 改成一個 4×4 block：load 8 requests、12 sectors（老師原本預測 16，當場說看不出多的 sector 從哪來，推測是 misalignment）；store 1 request、2 sectors。
- [02:51:02]–[02:52:01] NCU 的 global store 欄空白是 bug：關掉檔案再從 recent list 重開就會出現。
- [02:54:02]–[03:02:03] 32×32 矩陣、blockDim(32,1)、grid(1,32)：預測 load 2048 requests、5120 sectors（2.5 sectors/request），store 32 requests、128 sectors、4 sectors/request，寫出 4096 B —— NCU 完全吻合，store 是最佳的。
- [03:03:01] 用 shared memory 把 tile 開到越大越好，冗餘存取會降到 1/tile width。
- [03:04:06] **從現在起，所有 DRAM 存取都假設已經 coalesced**（A、B 讀取和 C 寫回全部），必要時改 index 或資料排列。之後才去拉高 flop 效率、提高 AI。
- [03:05:00]–[03:06:01] 只有 cuBLAS 8.5% 的原因：coalescing 改善怎麼抓，沒改善抓幾次；不要只靠 cache，要用 shared memory。
- [03:08:01] 一個 float4 vector load 是一條指令搬四倍資料，有時比 4 條 float load 還好，之後講 vectorized kernel。
- [03:09:00] 要 coalesced 就盯著 threadIdx.x；coalescing 是必要但不充分。
- [03:10:01] HW4 一定要用 demo 裡的方法 profile，證明看到預期的行為並能解釋原因。
- [03:10:01]–[03:11:02] HW4 extra credit：在 device 上做 transpose kernel（不在 host 預先轉置），一定要驗證正確性並簡單 profile；transpose 的 AI 是 0，全部是記憶體存取，所以要注意 coalescing。

## 和作業 / 考試的關聯

- **HW3**（Control Divergence & Tiled MMULT improvements & NCU profiling）：**11/6（五）11:59 PM PST**（Canvas due_at 2026-11-07T07:59:59Z），目前 unsubmitted。
- **HW4**（Memory access patterns & MMULT coalesced corner turning kernel，15 分）：**11/13（五）11:59 PM PST**（Canvas due_at 2026-11-14T07:59:59Z），11/3 發布，unsubmitted。說明 PDF 是 Canvas file 155723325。本講直接對應：
  - 學習目標（p49）：control divergence、coalesced access 等基本效能概念；練 NCU；實作 MMULT transposed corner turning kernel 並 profile 驗證記憶體存取模式變好。
  - Extra credit 4 分：平行化的 matrix transpose kernel，要驗證正確性並 profile。
  - 用得到的 NCU 指標（p45）：`l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum`、`l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum`（sectors ÷ requests）、`dram__bytes_read.sum`、`dram__throughput.avg.pct_of_peak_sustained_elapsed`、`lts__t_sector_hit_rate.pct`；GUI 看 Memory Workload Analysis → Memory Tables。
  - 提醒：課程 AI 政策你說不在意；這份筆記只整理課堂內容，HW4 的 kernel 還是要自己寫和 profile。
- **Pop Quiz - Lecture 5**（3 分，extra credit 性質）：8:20–8:30 PM，assignments.md 記為 graded（11/4 確認）。
- **Final project**：下週 L6（11/10）公布細節。Project Proposal 11/17（二）（syllabus 11:59 PM vs 投影片 5:59 PM，尚未確認）。
- **閱讀**：Reading Set #4 = PMPP Ch6，11/3 起。

## 還要釐清的問題

1. 4×4 block demo 的 global load 是 8 requests / 12 sectors，老師預測 16 並說看不出原因（[02:50:01]）。自行推算：A 的位址是 `row*4+k`，row = 0..3 → 4k, 16+4k, 32+4k, 48+4k bytes，跨兩個 sector（0–31、32–63）= 2 sectors；B 的 `k*4+col`，col = 0..3 → 16 B 連續 = 1 sector；每 iteration 3 sectors × 4 iterations = 12，和 NCU 吻合。也就是 B 只要 1 sector，不是老師說的 2。（自行推算，未經老師確認）
2. 老師口頭說 Kernel 2 約 6× 快，講義 p44 是 6.4×（309 → 1,986.5 GFLOP/s）；sector 數下降 6.6×。數字以講義為準。
3. Refresh 週期：口頭說 few milliseconds，講義 p8 寫 32–64 ms。依 BOOTSTRAP §3 應以口頭為準，但這看起來是口誤，標準 DRAM 是 32–64 ms，需要的話再問。
4. [01:06:02] 口頭 DRAM latency「500 milliseconds」、[01:07:03]「A100 ... 768 GB/s」都是口誤；講義 p25 是 500 ns 和 RTX A6000。
5. 講義 p6 寫「1 rank = 8 banks x 8bits = 64bit = 8 Bytes」，和 p11–p12 的 32 B burst 是不同層級的描述，課堂沒解釋，可以問一下。
6. `Au26_GPU-Compute_Lecture5_w_notes.pptx`（file 155737575）有老師的註解，這次沒有擷取（`pdf_text.js` 只處理 PDF）。之後如果有 PDF 版註解再補。
7. Winter 後續課程的 SLN 和課綱檔：課綱貼在 Teams 會議 chat，repo 裡還沒存。
8. 錄影 [02:00]–[03:05] 的 demo 用的是 Nsight Compute GUI＋Visual Studio CUDA debugger（warp info），HW4 是否也要求截圖 Memory Tables，要看 HW4 PDF。
