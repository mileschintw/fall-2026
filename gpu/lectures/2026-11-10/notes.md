# GPU Lecture 6 — 2026-11-10（Final Project：ResNet-18 inference engine＋leaderboard；SRAM、L1TEX / shared memory、cache 複習、L2、bank conflicts；transpose kernel 的 padding 與 XOR swizzle；Nsight Compute demo）

> 來源：transcript（Teams 自動逐字稿 `transcript.vtt`，2243 cues，約 00:00:11–03:12:30，約 3 小時 12 分；錄影檔 `Weekly Live Lecture-20261110_183022-Meeting Recording.mp4`）、slides（Au26_GPU-Compute_L6_SMEM-SRAM-caches.pdf，Canvas file 156063066，56 頁，文字在 `slides.txt`；p16–p22、p29–p35 幾乎只有圖，擷取不到文字）。**Final Project 那一段的投影片（[00:07]–[00:49]）不在這份 PDF 裡**，老師說課後或隔天早上另外貼，所以專題的部分只有逐字稿。閱讀章節：Reading Set #5 = PMPP 4th ed. Ch7（convolution）＋ Ch16 §16.1–16.4（deep learning），11/10 起，對應 L6、L7 和 final project（Canvas 頁面 2026-11-11 01:42 UTC 更新）；Reading Set #4 = PMPP Ch6。本講的 bank conflict、padding、swizzle 在 PMPP 裡沒有直接對應的章節，最接近的是 Ch6（自行對照）；講義 p56 列的參考資料是 Harris 的 *An Efficient Matrix Transpose in CUDA C/C++*（NVIDIA blog, 2013）和 Ruetsch & Micikevicius 的 *Optimizing Matrix Transpose in CUDA*（2010）。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：sam's → SMs；SIAS → SASS；N site / insight / inside compute → Nsight Compute；L1 text / L1 tax → L1TEX；gem / gems → GEMM；image net（「just a different spelling」，10 類、3,925 張）→ 推測是 Imagenette；touring → Turing；Ada Loveless → Ada Lovelace（sm_89）；check py / checked up. pie → check.py；CUDA func set attribute → `cudaFuncSetAttribute()`；right through / right back → write-through / write-back；cash → cache；Colonel → kernel；swizzle 沒聽錯，就是這個字；"fully convolutional layer"（[00:19]）→ fully connected layer；"start with FP16"（[00:10]）→ FP32（老師自己更正）；"120 bytes"（[01:25]）→ 128 B cache line；"0. 011"（[01:27]）→ 12 的二進位 01100；"812"（[01:51]）→ 8,192 sectors；"a 16-bit stride"（[02:03]）→ 4-byte stride（老師自己說投影片上那行字不對）；"threads or blocks of a warp"（[02:13]）→ threads / warps of a block（講義 p36）；"A at B"、"BX or R"、"CX or R"（[02:37]–[02:44]）→ `a ^ b`、`c ^ r`；"8 bank conflicts, 8 wavefronts"（[02:21]）→ 8-way conflict = 8 個 wavefront（多出 7 個）；"access wave fronts" → excess wavefronts；"10, 48, 7. 576"、"One 1 million, forty-eight. 756" → 1,048,576；"831.725"、"786. 432" → 831,725、786,432；"3208"（[03:04]）→ 32,8xx（後面唸的是 32,817、32,822）；"3276"（[03:00]）→ 32,768；Merrick view → metric view；"asuwsfcm"（[02:23]）→ SMEM；Gabriella、Keith 是發問的同學；"drain bread" 是老師口誤的玩笑。
>
> 錄影注意：錄影 18:30 開始，[00:00:11] 就開始上課。**這堂沒有 pop quiz**。[01:09]–[01:15] 休息（老師說 7:45 回來）。[02:51] 換電腦做 Nsight Compute demo，[03:10] 回投影片收尾，[03:12:30] 結束。

## 重點摘要

1. **課務更新**（[00:02]–[00:07]）
   - 今天沒有 pop quiz。
   - **HW4 截止延到 11/15（日）11:59 PM PST**（原本 11/13 五）。投影片上原本誤寫成 December，同學 Gabriella 指出後老師當場改掉。Canvas `due_at` 已經是 `2026-11-16T07:59:59Z`，一致。
   - 下學期的後續課（multi-GPU scaling）還沒有 SLN，time scheduling office 積案，老師說「any day now」。
   - **Final project 分組，剛好 3 人一組**：72 人 → 24 組，期末 3 天發表、每天 8 組。Canvas People → Groups 可以自己加入，但老師建議等隔天（11/11）TA 貼出正式說明再加。**11/16（一）當天結束前沒加入的，11/17（二）早上自動分組。**有人問能不能不是 3 人，答案是不行（[00:34]）。

2. **Final Project：ResNet-18 inference engine**（[00:07]–[00:50]，這段沒有講義頁碼）
   - 只做 forward pass，不做 training、gradient、backprop。會給一份完整、正確、但故意寫得很慢的 starter engine（含 host 端 executor 和每一層的 naive kernel），**工作就是一層一層把 kernel 換成比較快的**。
   - 給的東西（data pack＋starter kit）：pre-trained weights（FP32 和 FP16 兩份，batch norm 已經 fold 進 W′、b′）、完整資料集和 dev 子集（約 500 張）、labels、reference logits、每一層的 reference activations、描述每層 shape 的 manifest 和它的 reader、`check.py` / `submit.py` / setup 工具、README、spec 文件。
   - 資料：ImageNet 的 10 類子集（逐字稿聽起來是 Imagenette），3,925 張、591 MB；模型 FP32 權重 47 MB。全部加起來不到 1 GB，可以整個放上 T4，不用來回搬。
   - ResNet-18 結構：224×224×RGB 輸入 → 第一層 conv → max pool → 一串 basic block（channel 數變多、feature map 變小）→ global average pool → fully connected → logits。basic block 裡是 conv → ReLU → conv，加上 skip（residual）connection。不用做 softmax，直接比 logits。
   - 為什麼選這個題目：幾乎都是 convolution，可以轉成 GEMM（L7 整堂講 im2col、implicit / explicit GEMM），arithmetic intensity 高。
   - **禁用**：kernel 裡不能用現成的 CUDA 運算函式庫（NVIDIA 的 library、Thrust、Boost、其他第三方 GPU 運算庫等），checker 會檢查，查到就過不了 gate。
   - Template kernel：用 C++ template 讓同一個 kernel 支援 float / half，也可以把 shape 當 template 參數，一個 kernel 套所有層。
   - **Tier 制**（每個 tier 做完就 submit 到 leaderboard，各 tier 分開排名）：

     | Tier | 內容 | 需要的課堂內容 | 大約時程 |
     |---|---|---|---|
     | T0 | baseline smoke test：拿到 kit、build、跑 `check.py`、profile、`submit.py` | 現在就可以 | **11/22 前** |
     | T1 | batched GEMM path，本質上就是已經寫過的 SMEM tiled matrix multiply | 現在就可以 | 之後每週約一個 tier |
     | 中間幾個 tier | conv → GEMM 等 | L7 起 | 「next week」「the following week」「December 1st」 |
     | tensor core tier | 這時才用 FP16 | 後面的課 | — |
     | 最後一個 | bonus，給做完其他的人 | — | 非必要 |

     Tier 的確切名稱和數量要等專題投影片貼出來才能確認，上表是照 [00:33]–[00:37] 的口述整理。
   - **正確性 gate**：`check.py` 會逐層拿你的輸出和 reference activations 比 max error，容差很寬鬆；沒過 gate 的 run 不會上 leaderboard。哪一層沒過會標出來，方便 debug。
   - Leaderboard 記錄：images/sec、top-1 / top-5 error、各 kernel 離 roofline 多近等。**一律在 AWS T4 上跑、取多次平均**；開發可以用別的 GPU，但不要針對別的架構過度最佳化。batch size 自己選，submit 時一起交。同一個 tier 可以重交，但每天可能有次數上限。Leaderboard 只在班內公開。
   - 每個 tier 都要做 NCU profiling，數據會放進 final report。
   - **時程**（口述，[00:41]–[00:49]）：

     | 日期 | 事項 |
     |---|---|
     | 11/11（三） | TA 貼分組說明；老師貼專題投影片和 spec（「today or tomorrow morning」） |
     | 11/16（一） | 分組截止；starter kit 發布（週末還在 beta 測試） |
     | 11/17（二）早上 | 沒分組的自動分組 |
     | **11/18** | Project proposal（最多 2 頁）——老師口頭說「due again on the 18th」，和先前記的 11/17 不同，見「還要釐清的問題」 |
     | 11/22 | T0 smoke test 交到 leaderboard；目標是這天前組好隊、交完 proposal、T0 完成 |
     | 之後 | 報名發表時段；T1–TN，約 3.5 週，大約一週一個 tier |
     | 接近期末 | Design spec（比 proposal 深入，寫各 kernel 的做法） |
     | **12/15（二）** | Leaderboard 和程式碼凍結；發表開始 |
     | 12/15–12/17 | 發表：每組 10 分鐘＋5 分鐘 Q&A |
     | **12/17（四）** | Final report，當天結束前 |

     標星號的項目（報名類和期末那幾項）不能用 late day。程式碼要在發表前凍結，是為了避免看了別組的發表再回去改。
   - Proposal 內容：組員、打算做哪些 tier、分工、打算用的 profiling metrics、參考資料。
   - 評分：proposal、design spec，加上 final code / presentation / report。Leaderboard 名次有 bonus，總冠軍和各 tier 冠軍都有，細節還沒定。
   - 預期工作量：和作業差不多，每週 10–15 小時（[00:50]）。

3. **SRAM 基礎**（p4–p9）
   - SRAM cell 是 6T：兩個 cross-coupled inverter（M1–M4）存 bit，M5 / M6 接到 bitline。不用 refresh、讀取不破壞資料；面積比 DRAM 的 1T1C 大、比較貴，但快。GPU 的高速 SRAM 常用 8T 變體。
   - 一個 bank 一個 cycle 輸出 **1 word = 4 bytes**（本課的定義）。實體 array 不一定只有一個 word 寬：1024 個 word 做成 32×32 比 1×1024 好，所以需要 column mux。
   - **32 banks，不是 32 ports**。Multi-port cell 的面積大約隨 port 數平方成長，只用在 register file。Shared memory 和 L1 用 banking：32 個獨立的 single-port array，一個 cycle 最多 32 個存取（128 B）。
   - **bank = (byte address ÷ 4) mod 32**。word 0、32、64… 都在 bank 0；word 5、37、69、101 都在 bank 5。
   - 一個 warp 一次送 32 個位址，三種情況：
     - 32 個不同的 bank（任何排列）→ 1 個 wavefront。
     - 多個 thread 讀**同一個 word**（broadcast）→ 1 個 wavefront，而且可以同時有好幾組 broadcast。
     - **同一個 bank、不同的 word** → bank conflict，要序列化，N-way conflict 要 N 個 wavefront。
   - SRAM vs DRAM：SRAM 來回是幾十個 cycle，DRAM 是幾百個。SRAM 的問題是 bank conflict（解法：padding、swizzling、broadcast）；DRAM 的問題是 uncoalesced access（解法：coalescing）。

4. **記憶體階層和 Nsight Compute 的 memory chart**（p10–p12）
   - L1 / SMEM：32 banks × 4 B = 128 B = 一條 cache line = 4 個 32-byte sector。
   - Memory chart 左邊是邏輯單位（global、local、texture、surface、shared），右邊是實體單位（L1/TEX cache、shared memory、L2、device memory）。local 其實是 spill 到 global 的 register。**所有 global / local 請求都先過 L1TEX，miss 才到 L2；L2 是所有 global memory 的入口。**

5. **Cache 複習**（p13）
   - Cache 是自動管理的記憶體，靠 spatial locality 和 temporal locality。Hit / miss / miss penalty。cache block = cache line = 128 B。
   - Associativity（例子：32 個 block 的主記憶體、8 個 block 的 cache，要放 block 12）：
     - fully associative：放哪都行，conflict 少，但要搜尋整個 cache。
     - direct mapped：12 mod 8 = 4，只能放 block 4，不用搜尋，但 block 20 也會對到 4，會互相踢。
     - set associative：12 mod 4 = set 0，set 裡的 2 格任選，折衷。
   - Replacement policy：random、LRU、FIFO。Write policy：write-through（同時寫回）和 write-back（先只寫 cache，設 dirty bit，被踢掉時才寫回）。
   - **L1 是 incoherent、write-through；L2 是 coherent、write-back。**L1 每個 SM 各一份，不保證其他 SM 看得到；L2 的 fabric 負責 slice 之間的一致性。

6. **L1TEX 單元**（p14–p22）
   - 每個 SM 一個 L1TEX，**L1 data cache 和 shared memory 是同一塊實體 SRAM**。用 carveout 決定分多少給 SMEM。
   - **Turing T4：每個 SM 96 KB，SMEM 可以設 32 / 48 / 64 KB**，L1 就是剩下的 64 / 48 / 32 KB。要改 carveout 必須用 dynamic shared memory，並呼叫 `cudaFuncSetAttribute()`。可用的 carveout 可以在 Nsight Compute 的 occupancy calculator 查。
   - 什麼時候要多給 SMEM：例如 tiled matrix multiply，tile 越大、重複讀取越少、AI 越高，tile 得放在 SMEM。
   - Load-store pipeline：warp 的一個 SASS 指令（LDG、STS、LDS…）= 一個 request → LSU → tag stage（查是否在 cache）→ miss stage（送去 L2）→ data stage → 回 register file。每一段都有對應的 NCU metric，命名規則是「單元名在最前面」，例如 `l1tex__t_requests_pipe_lsu_mem_global_op_ld`。
   - **instruction : request 通常是 1:1**（一個指令代表整個 warp）。sector 數 ≥ request 數。wavefront 數大致反映 GPU 做了多少工。
   - Global load 的 stride 實驗（1024 個 warp，每個 thread 讀 4 B）：
     - stride 4 B：32×4 = 128 B = 4 sectors / request，1 條 cache line，fully coalesced，最佳。沒對齊 128 B 的話會跨 2 條 cache line。
     - stride 8 B：256 B = 8 sectors / request，2 條 cache line。
     - stride 32 B：每個 thread 各佔一個 sector，32 sectors / request，sector 數到頂（32×1024 = 32,768）。
     - stride 64、128 B：sector 數不再增加，但 wavefront 還是線性增加，因為碰到的 cache line 越來越多。

7. **L2 cache**（p23–p26）
   - 在晶片上，介於 L1 和 device memory 之間。分成 partition，每個 partition 有多個 slice（LTS = L2 slice，metric 前綴是 `lts__`）。L2 fabric 負責 partition 之間的 coherence，還有 L2 atomic unit。
   - T4：L2 共 4 MiB、32 個 slice（講義 p24）。cache line 大小和 L1 一樣。
   - L1 miss → L2 tag stage → hit 就回傳，miss 就送到 memory controller，回程順便填 L2。

8. **Shared memory 的 bank conflict**（p27–p35）
   - 無 conflict：32 個 thread 各讀一個 4-byte word，各在不同 bank → 1 cycle。
   - 判斷方法：一個 bank 一個 bank 看，數那個 bank 裡被存取的**不同 word** 有幾個，全部 ≤ 1 就沒有 conflict。
   - 16-byte stride 的例子：每個 bank 有 4 個不同的 word → 4-way conflict → 4 個 wavefront，其中 3 個是 excess（= bank conflict）。
   - NCU 的 Source page：`L1 Wavefronts Shared`（實際）、`L1 Wavefronts Shared Ideal`、`L1 Wavefronts Shared Excessive`。例子裡 ideal 262,144、actual 1,048,576（= ×4）、excessive 786,432（= ×3）。
   - **Memory 表的 bank conflicts（831,725）比 Source page 那行指令的 excessive（786,432）多**。原因是 L1 和 SMEM 共用同一組 32 個 bank，附近的 LDG 經過 L1 時也會佔 bank，和 STS 互相衝突。Source page 只算那一行指令造成的，Memory 表算整個單元的總數。
   - SMEM 的 stride 圖和 L1 的很不一樣：L1 是線性上升，SMEM 是尖峰和谷底交替，谷底的 stride 完全沒有 conflict（sweet spots），最差是每個元素隔一整條 cache line。

9. **什麼時候該用 shared memory**（p36）
   - 同一個 block 裡重複讀同一批資料；block 內 thread / warp 之間要同步或合作；想自己決定資料放多久（L1 的 eviction 你控制不了）；存取 pattern 不適合 L1 的 sector / cache line（對角線存取、strided sweet spots）；想減少經過 L2 的 global 流量；shared atomics 比 L2 的 global atomics 快。
   - Hierarchical roofline（p37）：L1、L2、DRAM 各有一條 roofline，越靠近 SM 越高。

10. **Case study：transpose kernel**（p38–p50）
    - 進程：K0 copy（不轉置，當頻寬上限）→ K1 naive（load coalesced、store 是 strided，每個 warp store 32 sectors）→ K2 用 32×32 的 SMEM tile（global 兩邊都 coalesced，但 tile 的 column read 有 32-way bank conflict）→ K3 padding → K4 XOR swizzle。
    - **K2**（p42）：block 是 32×8 個 thread（8 個 warp，一個 warp = tile 的一列），tile 是 32×32，所以每個 thread 跑 4 次迴圈（`j += BLOCK_ROWS`）。
      - 寫入 `tile[threadIdx.y + j][threadIdx.x]`：一個 warp 寫一列，bank = x，32 個不同 → 沒 conflict。
      - `__syncthreads()` 必要，因為之後會讀到別的 warp 寫的東西。
      - 交換的是 `blockIdx`（tile 在輸出矩陣的位置轉置）；讀出時用 `tile[threadIdx.x][threadIdx.y + j]`，一個 warp 讀一**行**。
      - word(i, j) = 32·i + j → bank = j，**和 row 無關**，同一行的 32 個元素全在同一個 bank → 32-way conflict，每個 LDS 要 32 個 wavefront。
    - **K3 padding**（p44–p46）：`tile[TILE_DIM][TILE_DIM + 1]`，只改一個 token。word(i, j) = 33·i + j → bank = (i + j) mod 32，row 也會移動 bank，每一列比上一列往右歪一個 bank。代價是每個 tile 多 128 B，那一行永遠不會被讀寫。
      - **padding 必須是奇數**：column read 沒有 conflict ⇔ i ↦ P·i (mod 32) 是 bijection ⇔ gcd(P, 32) = 1。P = 2 是 2-way、4 是 4-way。P = 1 最省。
    - **K4 XOR swizzle**（p47–p49）：tile 維持 32×32，邏輯上的 (r, c) 存在實體的 `tile[r][c ^ r]`。
      - XOR 是 involution：(c ^ r) ^ r = c，所以寫入和讀出用同一個式子。
      - r 固定時 c ↦ c ^ r 是排列；c 固定時 r ↦ c ^ r 也是排列 → 列寫入和行讀出都沒有 conflict。
      - 老師在白板上用 4×4（2 bit）手算：r = 00 時不變；r = 01 → 01, 00, 11, 10；r = 10 → 10, 11, 00, 01；r = 11 → 11, 10, 01, 00。每一列都是 0–3 的排列，再 XOR 一次 r 就還原。
    - **padding vs swizzle**：對這個 transpose 兩者效果一樣（0 excess wavefront）。padding 是一行修好、適合快速驗證；swizzle 不佔額外記憶體，row stride 維持 128 B，production library 都用它。padding 讓 row stride 變 132 B，vectorized load 和 tensor core 的 load 會對不齊。

11. **Nsight Compute demo**（[02:51]–[03:10]，p51–p55）
    - 設定：release build、x64、line info 開、target 是 sm_89（Ada Lovelace，老師自己的機器，不是 T4）；NCU 用系統管理員身分開；full metric set；輸入 1024×1024。每個 kernel 跑 3 次，每次約 45 個 replay pass。
    - 預測（p53）：1,024 blocks × 8 warps × 4 次迴圈 = **32,768** 個 LDS。K2：32,768 × 32 = 1,048,576 個 wavefront，excess = 31 × 32,768 = **1,015,808**。K3 / K4：32,768 個 wavefront，excess 0。
    - 實測 K2：Memory 表的 requests = 32,768、bank conflicts = 1,015,808。Source page 上 4 個 LDS 各 8,192 個 instruction、各 253,952 個 excessive（×4 = 1,015,808），各 262,144 個 total（×4 = 1,048,576）。但 Memory 表的 total wavefronts 是 1,052,xxx，比預測多——同樣是 L1 / SMEM 共用 bank 的額外開銷。
    - 實測 K3、K4：Source page 上 excessive = 0、wavefronts = ideal = 32,768，STS 和 LDS 都一樣。Memory 表的 total wavefronts 是 32,8xx（同一個 kernel 三次分別像 32,817、32,822），**每次不一樣，不是 deterministic**，但一定 ≥ request 數。
    - Global load：4 sectors / request，最佳。
    - 效能：K1 naive 很差；K2 約為 copy 的 92%；K3 和 K4 差不多。大的輸入時 K3 略快，改成 1024×1024 之後 K4 甚至比 K0 reference 還快一點。
    - Source page 操作：預設顯示百分比，按上方的按鈕切成數值，再按 ± 顯示完整位數。要看 bank conflict 得看 SASS 的 shared load / store 那幾行，不是原始碼那一行。

## 名詞解釋

- **SRAM / 6T cell**：靜態 RAM，6 個電晶體存 1 bit，不用 refresh。
- **Bank**：一個獨立的 single-port SRAM array，一個 cycle 給 1 個 4-byte word。NVIDIA GPU 的 L1 / SMEM 有 32 個。
- **Word**：本課固定指 4 bytes。
- **Bank conflict**：同一個 warp 的同一個指令裡，有兩個以上的 thread 要同一個 bank 的不同 word，必須序列化。
- **Broadcast**：多個 thread 讀同一個 word，一個 wavefront 就能服務，沒有懲罰。
- **Wavefront**：L1TEX 處理一個 request 時走過 32 個 bank 的一趟，最多 128 B。這裡不是指「整個 device 上同時在跑的所有 warp」，同學問到時老師特別區分（[01:05]）。
- **Excessive wavefronts**：實際 wavefront 減去 ideal，等於 bank conflict 數。
- **Lane**：warp 裡的一個 thread。
- **L1TEX**：每個 SM 一個的 L1 / texture cache 單元，和 shared memory 共用實體 SRAM。
- **Carveout**：把 L1TEX 的實體記憶體切多少給 shared memory。
- **LSU**：load-store unit，L1TEX pipeline 的入口。
- **LDG / STG / LDS / STS**：SASS 的 load global、store global、load shared、store shared。
- **Sector**：32 bytes，記憶體交易的最小單位；一條 cache line = 4 sectors。
- **Associativity**：一個 block 可以放在 cache 的哪些位置（fully associative / direct mapped / set associative）。
- **Replacement policy**：cache 滿了要踢誰（random、LRU、FIFO）。
- **Write-through / write-back / dirty bit**：寫入時立刻寫回下一層，或先只寫 cache、被踢時才寫回。
- **Cache coherency**：多個 cache 之間怎麼保證大家看到的資料一致。
- **LTS**：L2 slice。
- **L2 atomics**：跨 SM 的 atomic 操作，可以用來做 device 層級的同步。
- **Padding**：把 tile 宣告成 `[32][33]`，讓每一列的 bank 位置錯開。
- **XOR swizzle**：把欄索引和列索引做 XOR 再存，讓列和行都落在 32 個不同的 bank。
- **Involution**：做兩次等於沒做的運算，XOR 就是。
- **Bijection**：一對一且映成的對應，這裡指 32 個 lane 剛好對到 32 個不同的 bank。
- **ResNet-18 / residual（skip）connection**：18 層的 ResNet；skip connection 把 block 的輸入直接加到輸出。
- **Logits**：softmax 之前的分數，排名和機率一樣。
- **BatchNorm folding**：把 batch norm 的縮放和平移併進前一層 conv 的權重和 bias（W′、b′），推論時就不用另外算。
- **Top-1 / top-5 error**：正確答案不是第 1 名、不在前 5 名的比例。
- **GEMM**：general matrix multiply。
- **Smoke test（T0）**：原封不動的 starter engine 跑一遍並交上 leaderboard。
- **Correctness gate**：`check.py` 的檢查，沒過就不會上榜。

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

- HW4 截止改成這個星期日（11/15）11:59 PM；今天沒有 pop quiz。[00:02:01]
- 專題一定是 3 人一組；11/16（一）當天結束前沒組好，11/17（二）早上自動分。[00:07:01]
- 專題不用從頭寫，也不用懂 ResNet 或訓練；starter kit 開箱就能跑，只是很 naive。[00:08:03]
- 每換一個 kernel 都要先驗證正確性，用給的逐層 reference activations。[00:10:01]
- 沒過 correctness gate 就不會被收；老師的說法是「fast wrong kernel score 0」。[00:38:00]
- 最終一律在 AWS T4 上計時，不要為別的架構過度最佳化。[00:27:05]
- Kernel 裡不能用現成的 GPU 運算函式庫，checker 會抓。[00:30:05]
- 到今天為止學的東西已經夠做到 T1（batched GEMM = 寫過的 SMEM tiled matmul）。[00:33:10]
- 每個人（每組）都要先有 T0 的 leaderboard entry 才往下做；每做完一個 tier 就 submit。[00:35:04]
- 最後一個 tier 是 bonus，不是必要的。[00:36:04]
- Tensor core 那個 tier 才用 FP16，做出來會比其他的快很多。[00:36:04]
- 每個 tier 都要用 NCU profile；這既是 final report 的內容，也是找瓶頸的唯一方法。[00:39:03]
- Leaderboard 和程式碼 12/15 凍結，理由是不該看了別組發表再回去改。[00:41:02]
- 標星號的截止日不能用 late day。[00:45:02]
- 專題的工作量預期是每週 10–15 小時。[00:50:01]
- 本課的 word 一律是 4 bytes。[00:56:02]
- 每個 bank 只輸出一個 word，不代表 SRAM array 只有一個 word 寬，所以才有 column mux。[00:58:05]
- 所有現行世代的 NVIDIA GPU，L1 / SMEM 都是 32 個 bank。[00:59:00]
- Bank conflict 只發生在「同一個 bank、不同的 word」；不同 bank 的任意排列、同一個 word 的 broadcast 都沒事。[01:05:00]
- Conflict 是 warp 層級的事，不是 wave。[01:05:00]
- SRAM 的毛病是 bank conflict，DRAM 的毛病是 uncoalesced access，這是今天最關鍵的對照。[01:08:02]
- L1 cache 和 shared memory 是同一個實體記憶體單元。[01:16:01]
- 所有對 global memory 的請求都要經過 L2。[01:20:01]
- Write-back 比較有效率但危險：L1 是各 SM 自己的，別的 SM 可能讀到舊值。[01:32:05]
- L1 是 incoherent、write-through；L2 是 coherent、write-back。[01:33:07]
- Tile 越大 AI 越高，這種情況就該把 SMEM 的 carveout 開到最大。[01:36:00]
- 要改 carveout 一定要用 dynamic shared memory 加 `cudaFuncSetAttribute`。[01:37:00]
- 回答 Keith：大 stride 不叫 warp divergence。對 global 是 uncoalesced access，對 shared 是可能的 bank conflict。[01:40:00]
- Wavefront 數可以當成 GPU 做了多少工，越少越好。[01:42:02]
- 一個指令對一個 request，因為一個指令就代表整個 warp。[01:44:00]
- Stride 到 32 B 之後 sector 數不再變差，但 wavefront 還會繼續增加。[01:53:03]
- L1 和 SMEM 共用同一組 bank，所以 global 請求和 shared 請求之間也會 conflict，而且很難預測，只能從 NCU 看出來。[02:00:04]
- N-way conflict 是 N 個 wavefront、N−1 個 bank conflict，因為本來就至少要一個。[02:07:04]
- Memory 表的 bank conflict 是整個單元的總數，Source page 只算那一行指令。[02:09:00]
- L1 和 SMEM 是同一塊記憶體，但最佳化策略完全不同。[02:12:02]
- 什麼時候該用 shared memory 的那張清單，「especially for your final project」。[02:16:04]
- K2 的讀出是「column 固定、row 由 thread index 決定」，所以是 32-way conflict。[02:28:01]
- Padding 只改一個 token，其他程式碼都不動。[02:30:04]
- 老師建議自己把 33·i + j mod 32 的數學寫一遍。[02:32:00]
- Padding 一定要是奇數，1 是最便宜的。[02:35:04]
- XOR 是 involution，這是 swizzle 能用同一個式子讀回來的原因。[02:38:01]
- Swizzle 沒有額外記憶體開銷，通常比 padding 好；padding 唯一的優點是簡單。[02:46:00]
- Padding 讓資料對不齊，tensor core 的指令需要對齊的 operand，所以 production 不用 padding。[02:48:05]
- Profile 一定用 release build；NCU 要用系統管理員身分開。[02:54:03]
- 看 bank conflict 要看 SASS 的 shared load / store 那幾行。[02:59:03]
- Source page 的數字是每個指令各自的，4 個 LDS 要加起來才等於 Memory 表的總數。[03:01:00]
- Memory 表的 total wavefronts 至少是 requests + bank conflicts，常常更多。[03:03:01]
- 那個多出來的數字每次跑都不一樣，不是 deterministic。[03:05:05]
- 這種幅度的改善就是專題裡要追求的，用同一套工具。[03:10:01]

只在講義上、課堂沒講到的：

- 8-byte 和 16-byte 的存取就算沒有 conflict，也至少要 2 個和 4 個 wavefront（一個 wavefront 最多 128 B）。（講義 p8）
- Conflict degree 的通式：lane k 讀 word k·s 時，degree = gcd(s, 32)；stride 32 → 32-way，任何奇數 stride → 沒有 conflict。（講義 p40）
- K20c 的參考頻寬（GB/s）：K0 136.2、K1 55.2、K2 93.0、K3 142.9；T4 那一列是空白。（講義 p39）
- K2 的 32-way conflict 每個 block 大約多花 1,000 個 cycle。（講義 p43）
- Padding 的 tile 是 4,224 B，比 4,096 B 多 3.1%；8-byte 元素用 +1 padding 還是會有 2-way conflict。（講義 p44、p46）
- Vectorized 存取要 swizzle chunk index：`p = j ^ ((i & 7) << 2)`，這是 CUTLASS / CuTe 的 `Swizzle<B, M, S>`（B=3、M=2、S=3）；cuBLAS、CUTLASS GEMM、FlashAttention 都用。（講義 p49）
- Padding 的 row stride 是 132 B，不是 16-byte 對齊，`float4`、`ld.shared.v4`、`ldmatrix` 會對不齊。（講義 p46、p50）
- NCU CLI：`ncu --set full -k regex:transpose -o transpose_t4 ./transpose_t4 1024 1024 1`；只看 bank conflict 的 metric 是 `smsp__sass_inst_executed_op_shared_ld.sum`、`l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum`、`l1tex__data_bank_conflicts_pipe_lsu_mem_shared_op_ld.sum`、`…_op_st.sum`。（講義 p52、p54）
- Global 那一側：`l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum ÷ l1tex__t_requests_pipe_lsu_mem_global_op_st.sum`，naive 是 32，其他是 4。（講義 p52）
- K2 → K3 時 Warp State Statistics 的 Stall Short Scoreboard / MIO Throttle 會下降。（講義 p54）
- NCU 鎖 clock、序列化 launch，時間和 harness 量的不一樣，要比 counter 不要比毫秒。（講義 p51）
- NCU 可以把 K2 設成 baseline，K3 / K4 的每個 metric 會顯示差值。（講義 p51）
- Linux 上 `ERR_NVGPUCTRPERM` → 用 root 或設 `NVreg_RestrictProfilingToAdminUsers=0`。（講義 p51）

逐字稿和講義不一致的地方（照規則採逐字稿）：

- T4 的 SMEM carveout：課堂說 32 / 48 / 64 KB 三種 [01:35:02]，p14、p15 也是；只有 p9 寫「32 or 64 KB」。採三種。
- 講義整份寫的是在 T4 上驗證；課堂 demo 實際用的是 sm_89（Ada Lovelace）的機器 [02:53:06]，所以 demo 的效能數字不是 T4 的。
- Tensor core 對 padding 的限制：課堂說需要「power of 2 aligned」的 operand [02:48:05]，講義 p46 寫的是 16-byte 對齊。兩者講的是同一件事，講義比較精確。
- p53 預測 K3 / K4 的 shared wavefront 剛好 32,768；demo 的 Memory 表實測是 32,8xx，老師解釋是 L1 / SMEM 共用 bank 的開銷，Source page 的每指令數字才會剛好等於預測 [03:04:01]。
- [02:03:03] 老師說 p31 圖上那行「16…stride」的字是錯的，正確是每個 thread 4 bytes、連續的 bank。

## 和作業 / 考試的關聯

- **HW4**（Memory access patterns & MMULT coalesced corner turning kernel，15 分）：截止 **11/15（日）11:59 PM PST**，Canvas `due_at` 2026-11-16T07:59:59Z，目前 unsubmitted。本講 [01:46]–[01:54] 的 stride 實驗（sectors / request = 4、8、32）和 `l1tex__t_sectors…` ÷ `l1tex__t_requests…` 的算法，就是 HW4 分析 global memory 存取要用的讀法；demo 裡切換 Source page 數值顯示的操作也用得到。
- **Final Project**（佔學期 50%）：這堂是正式說明。`gpu/assignments.md` 目前記的是 Proposal 11/17、Design Spec 12/1 5:59 PM、發表 12/15–12/17、Final Report + Code 12/17 11:59 PM 不能延期。和課堂口述比對：
  - Proposal：課堂說 **11/18**，和 11/17 不同。
  - Code：課堂說 **12/15 凍結**，比原本記的「12/17 和 report 一起」早兩天。
  - 新增的日期：11/16 分組截止＋starter kit；11/22 T0 smoke test。
  - 這次沒有改 `gpu/assignments.md`，等專題投影片和 Canvas 作業出來再對。
- 專題直接用到本講的：SMEM tile 的 bank conflict 檢查（`L1 Wavefronts Shared Excessive`）、carveout 調大 tile、swizzle（之後要接 tensor core 的話不能用 padding）、hierarchical roofline。
- T1 = batched GEMM = L4 / L5 的 SMEM tiled matmul（SGEMM Kernel 2 那條線），可以先複習。
- L7（11/17）整堂講 convolution → GEMM，對應 Reading Set #5（PMPP Ch7、Ch16.1–16.4）。
- 這門課沒有考試；這堂也沒有 pop quiz。

## 還要釐清的問題

1. **Project proposal 到底是 11/17 還是 11/18？幾點？**課堂說「the 18th」[00:48:00]；`gpu/assignments.md` 記的是 11/17（二），而且 syllabus 11:59 PM 和舊投影片 5:59 PM 本來就不一致。等專題投影片或 Canvas 作業發布後確認。
2. **Design spec 的日期**：課堂只說「towards the end of the quarter」[00:45:02]，又說某個 tier 對應「December 1st」[00:35:04]。原本記的 12/1 5:59 PM 還成立嗎？
3. **評分比重**：課堂說 final code、presentation、report「equally weighted」而且佔大部分 [00:47:03]；原本記的是 proposal 10% / design spec 30% / final 60%。Leaderboard bonus 怎麼算也還沒定。
4. **Tier 的完整清單**（T0 到 TN 各是什麼、哪些必做）要看專題投影片；逐字稿只聽得出 T0、T1、tensor core tier 和最後的 bonus tier。
5. **發表哪一天開始**：「team presentation start that day afterwards」[00:45:02] 聽不出是 12/15 當天還是隔天；3 天 × 8 組的話應該是 12/15–12/17。
6. **分組怎麼加入**：老師當場在 Canvas People 找不到設定好的 group set，說 11/11 會貼說明。要去 Canvas / Teams 看。
7. 輸出是 **1000 個 logits 還是 10 個**？老師說資料集只有 10 類，但又說「spits out the 1000 logits」[00:19:03]。推測模型還是 1000 類的 ImageNet 權重，只看那 10 類，要看 spec。
8. 資料集的正式名稱（Imagenette？）和 3,925 張是哪個 split，要看 spec。
9. Leaderboard 每天可以 submit 幾次，老師只說「might be a limit」[00:40:07]。
10. T4 的 SMEM carveout 預設是多少？32 / 48 / 64 KB 之外，HW 或專題的 kernel 需不需要自己設？
11. Demo 是在 sm_89 上跑的，K0–K4 在 T4 上的實際頻寬（p39 表格空白的那一列）要自己量。
12. [01:53:03] 說 stride 超過 32 B 之後 wavefront 還線性增加是因為「cache line replacement and other overhead」，這個解釋很籠統，機制沒有講清楚。
13. 8T SRAM cell、crossbar / arbiter 的細節課堂只帶過；講義 p8 自己註明是概念模型，NVIDIA 沒有公開實際電路。
