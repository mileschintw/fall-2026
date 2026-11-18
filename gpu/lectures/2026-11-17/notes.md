# GPU Lecture 7 — 2026-11-17（Convolution layer 從 direct kernel 到 GEMM：im2col / im2row、explicit vs implicit GEMM、register tiling 預告；CUDA Events；Final Project starter kit 導覽與 NCU profiling）

> 來源：transcript（Teams 自動逐字稿 `transcript.vtt`，2345 cues，約 00:00:04–03:30:10，約 3 小時 30 分；錄影檔 `Weekly Live Lecture-20261117_183030-Meeting Recording.mp4`）、slides（Au26_GPU-Compute_L7_conv-gemm_v3_w_notes.pdf，Canvas file 156387329，57 頁，文字在 `slides.txt`；另有不含 notes 的 v3，file 156374164）。閱讀章節：Reading Set #5 = PMPP 4th ed. Ch7（convolution）＋ Ch16 §16.1–16.4（deep learning），11/10 起，對應 L6、L7 和 final project（Canvas 頁面 2026-11-11 01:42 UTC 更新）。本講的 im2col → GEMM 對應 PMPP Ch16 裡「把 convolutional layer 寫成 GEMM」那一節（自行對照）；register tiling 下週 L8 才細講。逐字稿是自動產生，專有名詞可能聽錯。
>
> 常見誤聽對照：gem / gems / Jim → GEMM；im to call / in to call / M to call / him to call → im2col；in to row / M to row → im2row；Imen to Win → im2win；N site compute / inside compute → Nsight Compute；SIAS → SASS；Colonel → kernel；Directconf / conv direct → `conv_direct`（starter 的 direct conv kernel）；D vgrad / W vgrad → dgrad / wgrad；F prop → fprop；size T → `size_t`；float for → `float4`；brain float 16 / FB16 → BF16；resonate 18 / ResNet 18 → ResNet-18；Shaw 256 → SHA-256；ASUW T4 → AWS T4；Telecom / Tilikum → Tillicum（UW 的 GPU cluster）；Hayak → Hyak；RNS → R and S；KML → 老師自己對 kernel 的縮寫；570 or 256 → 256。
>
> 錄影注意：錄影 18:30 開始，[00:00:04] 就開始上課。**這堂沒有 pop quiz**，改成不計分的 poll。[01:27]–[01:40] 休息＋poll。[03:12]–[03:14] 老師換電腦、麥克風沒開，這段沒聲音。[03:30:10] 結束（比平常晚，老師 [03:06] 說已經 9:27，[03:29] 說已經 10 點）。

## 重點摘要

1. **課務更新**（[00:00]–[00:09]；講義 p2、p53）
   - **遲交作業最後期限 11/27（五）11:59 PM**：所有 HW 都已經過了正式截止，要遲交的一律在 11/27 前交，之後要開始改 final project（[00:05:05]–[00:06:02]）。
   - **Final Project Proposal 延到 11/20（五）11:59 PM**，兩頁 PDF。Canvas 的繳交連結「今晚約 10 PM」開（[00:06:02]；講義 p57）。
   - 老師說「as of this time」所有人都已經被分到三人一組（[00:03:02]）。**但 11/18 晨報記錄 Canvas 的 team sign-up 重開到 11/18 11:59 PM、組別全部重置**，以 Canvas 為準，見「還要釐清」。
   - 組號沒有意義，只用來在 leaderboard 上排名，也跟發表順序無關；想改隊名應該可以（[00:07:01]）。
   - Final project 的資料全部在 Teams 的「Final Project ResNet 18」channel（spec、更新、投影片、starter kit 和 data pack 連結）。看不到 channel 的話，到 Teams 裡把 channel 設成顯示（[00:02:00]–[00:04:04]）。
   - 發表時段 sign-up：講義 p2 寫 11/24（二）6 PM 前，p53 寫 11/24 5:59 PM，老師說「next day or two」會貼（[03:08:02]）。
   - 下學期（Winter 2027）的續課快滿了，會從單 GPU 擴到 multi-GPU、多節點（[00:11:01]）。

2. **本講路線**（[00:09]–[00:13]；講義 p4）
   - L7、L8、L9 三堂都在講怎麼加速 GEMM（`C = αAB + βC`；α=1、β=0 就是一般的 matrix multiply），因為 convolution 可以轉成 GEMM，而 GEMM 是 GPU 最理想的工作：AI 高、可以充分利用 memory hierarchy。
   - 今天：foundations → direct kernel → im2col identity → fprop / dgrad / wgrad → explicit im2col / im2row → implicit GEMM（I1、I2）→ 現代 convolution 變體。**今天只用 FP32 CUDA cores，不碰 tensor core**；L8 細講 register tiling，L9 才講 tensor core。

3. **Convolutional layer 的一般形式**（[00:13]–[00:20]；講義 p6–p7）
   - 輸入 N 張 C×H×W；filter bank 有 K 個 filter，**每個 filter 都是 C×R×S**（橫跨所有 input channel）；每個 filter 對每張圖產生一張 P×Q 的輸出，所以輸出是 N×K×P×Q。filter 權重總共 KCRS 個。
   - **常見誤解**：以為是「每個 channel 一個 filter，各自卷積後再相加，再乘上 K 個 filter」。實際上 channel 的加總發生在單一 filter 內部，這正是 GEMM 的 reduction dimension 會是 C·R·S 的原因（[00:18:01]–[00:19:01]；講義 p6）。老師說他自己以前也這樣誤會過。
   - 一個 filter 在某個位置蓋住的輸入區域叫 **patch**（3×3 filter → patch 有 9 個元素）。
   - 符號（NVIDIA / cuDNN / CUTLASS 慣例）：N batch、C（Ci）input channels、K（Co）output channels、H×W 輸入、R×S filter、P×Q 輸出、G groups（本課幾乎都是 1）、stride、pad、dil。
   - **N 和 K 是 overloaded 的**：GEMM 的 `M×N = (M×K)(K×N)` 裡的 N、K 跟 convolution 的 N、K 不是同一個東西，講義用 M_gemm / N_gemm / K_gemm 區分（[00:21:01]–[00:24:02]）。K_gemm 是 reduction dimension。
   - 兩種 layout：**NCHW**（W 最快，channels-first）和 **NHWC**（C 最快，channels-last）。「最快」= 在記憶體裡連續（[00:24:02]–[00:25:02]）。filter 和 output 也各有兩種 layout。

4. **Convolution equation、stride / pad / dilation、輸出大小**（[00:26]–[00:34]；講義 p8–p9）
   - 深度學習的 convolution 其實是 **cross-correlation**（filter 不翻轉）；學出來的權重自己會翻，所以沒差（[00:27:03]；講義 p8）。
   - 圖片外的 X 一律當 0（這就是 pad 的實際意義）；padding 有時要明寫，有時是隱含的。
   - **stride**：filter 每產生一個輸出往前移幾格輸入；**pad**：周圍補幾圈，用來控制輸出大小；**dilation**：filter tap 之間插空格，tap 數不變但 receptive field 變大（2×2 dil 1 個空格 → 涵蓋 3×3），**運算量不會隨 receptive field 平方成長**（[00:31:00]–[00:34:02]）。
   - 輸出大小：`P = ⌊(H + 2·pad − dil·(R−1) − 1) / stride⌋ + 1`（Q 同理）。stride=1 且 `2·pad = dil·(R−1)` 時 P=H（「same」padding：3×3 → pad 1、7×7 → pad 3、3×3 dil 2 → pad 2）。「valid」padding = pad 0，3×3 stride 1 → P = H−2（講義 p9；口述 [00:36:01]）。
   - 口述 [00:30:01] 說 3×3、pad 1「0 dilation factor」時 H=P；講義的公式用 dil=1 表示沒有 dilation，口誤，以公式為準。

5. **Arithmetic intensity 與 roofline**（[00:34]–[00:43]；講義 p9–p11）
   - FLOPs = 2·N·K·P·Q·C·R·S（乘加各算一次）；compulsory bytes（FP32 ×4）= 讀 X 一次＋讀 W 一次＋寫 Y 一次，是最低限度、不算 cache 的節省。AI = FLOPs / bytes。老師說這跟之前某份作業算的應該一致（[00:34:02]）。
   - 例：ResNet-50 stage-2 3×3（N=32, C=K=64, 56×56）→ 7.40 GFLOP、51.5 MB、**AI ≈ 144 FLOP/B，compute-bound**（[00:37:05]；講義 p9）。
   - 老師自己的 RTX 4090（CC 8.9；講義寫 RTX 4090 Laptop GPU：FP32 28 TFLOP/s、DRAM 448 GB/s）roofline：3×3（144）是 compute-bound；1×1（26）、depthwise（12）是 memory-bound；**explicit im2col 會把 3×3 拉到 AI ≈ 14**，掉一個數量級以上，變成 memory-bound（[00:38:07]–[00:41:00]；講義 p10）。圖上還有 TF32 / BF16 tensor core 的 roofline，比 FP32 高很多。
   - 重點觀念：layer 的 shape 決定 compulsory bytes；kernel 的設計決定實際搬多少（多少冗餘）、資料放在哪一層 memory、由哪種單元（FP32 core vs tensor core）算（[00:41:00]–[00:43:01]；講義 p11）。

6. **D1：direct convolution**（[00:43]–[01:02]；講義 p12–p16）
   - CPU reference 是 **seven-loop nest**：外 4 層 N、K、P、Q（每個輸出 pixel），內 3 層 C、R、S（reduction）（[00:45:03]–[00:50:00]）。
   - **Naive GPU 版**：內 3 層變成 kernel，外 4 層變成 grid → **一個 thread 算一個輸出值**。grid：x = ⌈P·Q / 256⌉、y = K、z = N；block 256 threads（[00:51:01]–[00:53:01]）。
   - 實作細節（[00:54:01]–[00:58:02]；講義 p15）：
     - `const float* __restrict__`：保證不 alias，compiler 可以把值留在 register、走 read-only non-coherent path（SASS `LDG.E.CONSTANT`、PTX `ld.global.nc`，等同 `__ldg()`）。程式設計者要自己保證不重疊，否則行為未定義。
     - 索引用 `size_t`（64-bit unsigned），因為大 shape 下 32-bit 會 overflow；cast 其中一個值就會讓整個運算用 64-bit。老師一開始說成 double，後來自己更正（[00:57:05]）。
     - 用 `__fmaf_rn`（round-to-nearest-even 的 FMA），保證編成 `FFMA`。
     - 先用 stride / pad / dil 算出輸入座標，超出範圍就 `continue`。
   - **NCU 分析**（講義 p16；口述 [00:59:02]–[01:02:03]）：W 最快 → 讀 X 是 coalesced 的；reuse 只能靠 cache，而 cache 很有效（L1 88%、L2 98%、DRAM 只用到 1%）；**問題是每個 FMA 要約 25 個 instruction**（索引、bounds test、每個 tap 兩次 load）；40 registers、93% occupancy，occupancy 不是問題。結果 8.40 ms、0.88 TFLOP/s，**只有 FP32 peak 的 3%**。老師提醒 T4 的 L2 只有 4 MB，hit rate 可能較低。
   - 老師預告：之後會看到「故意降低 occupancy 反而更快」的例子（[01:01:02]）。

7. **im2col identity**（[01:02]–[01:20]；講義 p17–p18）
   - Toy example：1 channel、4×4 輸入、3×3 filter、valid → 2×2 輸出。把每個 filter 位置蓋住的 9 個值攤成 patch matrix 的一欄 → patch matrix 9×4；filter 攤成 1×9 的 row → `Y(1×4) = W(1×9) · X̃(9×4)`。老師承認投影片上式子寫反了，正確是 Y = W·X̃，X̃ 是 B（[01:08:05]–[01:12:01]）。
   - 多 channel、多 filter、多張圖時就變成大矩陣：**im2col（NCHW，Caffe）**：X̃ 是 [C·R·S] × [N·P·Q]（一個輸出 pixel 一欄），W 是 K × CRS，`Y[K][NPQ] = W · X̃`，patch matrix 是 operand **B**。**im2row（NHWC）**：X̃ᵀ 是 [N·P·Q] × [R·S·C]（一個 pixel 一列，c 最快），W 是 RSC × K，`Y[NPQ][K] = X̃ᵀ · W`，patch matrix 是 operand **A**（講義 p18、p24、p25）。
   - 兩者的運算完全一樣，只差 layout；layout 會影響 coalescing 和能不能用 vectorized load（[01:15:05]–[01:16:00]）。
   - **im2col 版的輸出是 K×NPQ（KNPQ），要在 CPU 端重排成 NKPQ**；im2row 版直接得到 NPQK（= NHWC 的輸出），不用重排（[01:49:06]–[01:52:01]；講義 p24–p25）。
   - 老師強調：專題給的資料有固定 layout，搞錯就會算錯；但 starter code 已經有完整的 load → kernel → 驗證流程，照它的做法就對（[01:18:03]–[01:20:00]）。

8. **fprop / dgrad / wgrad**（[01:20]–[01:27]；講義 p19–p20）
   - fprop：Y = conv(X, W)，推論只要這個。dgrad：∂L/∂X（要 col2im scatter-add）。wgrad：∂L/∂W（在最大的維度 N·P·Q 上 reduce → split-K / stream-K）。
   - 三個都是 GEMM，只用到 W、X、∂L/∂Y 三個矩陣。**專題只做 fprop**，不做 training（[01:24:01]–[01:25:02]）。
   - fprop 的 GEMM 維度：M_gemm = K、N_gemm = N·P·Q、K_gemm = C·R·S。
   - **Explicit X̃ 的記憶體膨脹 = R·S 倍**：3×3 → 9 倍、7×7 → 49 倍。ResNet-50 3×3、batch 32 → X̃ = 231 MB（輸入 25.7 MB）；N=128 → 0.92 GB。這就是要做 implicit 的動機（講義 p20）。
   - ResNet 裡只有一層 fully connected，其他都是 convolution，全部都能寫成 GEMM（[01:25:02]）。

9. **休息與 poll**（[01:27]–[01:41]）
   - 不計分的 poll（三題）：對 ResNet 的熟悉度、有沒有用過 UW 的 Tillicum / Hyak cluster。結果約三分之二用過 ResNet / CNN；全班 72 人。下學期會用 Tillicum。
   - 老師說專題刻意設計成不用懂 ResNet 也能做，spec 裡有需要的一切（[01:40:11]–[01:41:01]）。

10. **Explicit GEMM：E1 / E2 + E3**（[01:41]–[02:37]；講義 p21–p32）
    - **Explicit** = patch matrix 真的在 HBM（DRAM）裡建出來；**implicit** = 從不建出完整矩陣，每次需要時把那一塊從原始輸入算位址撈進 shared memory（[01:43:00]–[01:45:01]；講義 p22）。其他方法：im2win、Winograd / FFT，本課不講。
    - 歷史：2006 Chellapilla, Puri & Simard（Microsoft）首創；2014 Caffe 的 `im2col.cu` + cuBLAS 變成預設（講義 p23）。現在 explicit 只當入門參考，production 都用 implicit GEMM（[01:46:00]–[01:47:02]）。
    - **E1（im2col, NCHW）**：toy example 2 channels、4×4、3×3、pad 1、假想 GPU 8 threads/block、warp 4。row = 一個 (channel, tap)，16 欄 = 16 個輸出 pixel。值的數字就是列行（ch1 再 +50），row 5 = ch0 tap(1,2)，從 thread 80 開始（[01:53:00]–[02:04:02]；講義 p26）。**pad 的 0 從不真的寫在輸入裡，是 thread 在 bounds check 時填的**（[02:02:02]）。
    - 連續 thread 同 channel、同 tap → stride 1 時讀寫都 coalesced；但 filter 越大，每列中間的空隙越大，coalescing 越差（[02:04:02]–[02:05:05]）。
    - **兩步驟**：step 1 transform kernel（E1 或 E2）只搬資料、不做 FMA，一個 thread 搬一個元素，索引用 `long long`；step 2 是 GEMM kernel E3，**E3 不管 layout，只要 A、B 維度 conformal**（[02:07:03]–[02:22:05]）。
    - **E2（im2row, NHWC）**：每個 pixel 的所有 channel 連續；row = 一個輸出 pixel，裡面 channel 最快。channel 多時連續的元素多，coalescing 較好（[02:14:01]–[02:20:05]；講義 p28–p29）。
    - **E3（`sgemm_tiled`）**：template `<BM, BN, BK, TM, TN>` = 64, 64, 8, 4, 4；256 threads/block。兩層 tiling：SMEM 2D tile（As、Bs 各 512 元素）＋ **register 2D tile**（每個 thread 4×4 = 16 個 accumulator）。每個 thread 載 2 個元素進 SMEM（超出範圍填 0）→ `__syncthreads()` → 每個 kk 從 SMEM 讀 4 個 a、4 個 b 進 register，做 16 個 FMA（8 次 shared load、16 FFMA）→ `__syncthreads()` → 下一個 BK（[02:22:05]–[02:32:03]；講義 p30–p31）。細節 L8 講。
    - **Epilogue**：主 reduction 迴圈之後的額外運算（GEMM 的 α、β；在 conv layer 裡可能是加 bias、ReLU）。**fused epilogue** = 放在同一個 kernel 裡，省一次 launch 和一次 global memory 來回。β=0 時跳過讀 C（[02:32:03]–[02:35:00]；講義 p32、p48）。

11. **Implicit GEMM：I1 / I2**（[02:37]–[03:02]；講義 p35–p43）
    - Patch matrix 從不建出來；GEMM 的 tile load 改成用索引運算直接從原始 X 撈值進 SMEM，transform 和 GEMM 合成一個 kernel。weights 照常直接搬（[02:38:00]–[02:41:00]；講義 p36）。
    - **I1（NCHW）**：從 E3 改，patch matrix 是 B tile，每個元素做 scalar gather ＋ bounds test；compute block 不變；epilogue 拿掉 α/β，改寫成 NKPQ（[02:42:04]–[02:48:06]；講義 p37–p38）。
    - **I2（NHWC）**：channel 連續 → 可以用 **`float4` vectorized load/store**（16-byte、一個 instruction 搬 4 個 float）。PTX 看得到 `ld.global.nc.v4.f32`、`st.shared.v4.f32`、`st.global.v4.f32`。從 SMEM 讀 B 進 register 也改成 vector load（[02:49:04]–[03:00:03]；講義 p39–p42）。
    - Vector load 是回到 **SIMD**（之前都是 SIMT 的 scalar code，靠硬體 coalescing）：資料必須 16-byte 對齊、連續，否則就是垃圾，**比較脆弱但比較快**（[02:52:04]–[02:55:02]）。
    - 這就是 PyTorch 有 `channels_last`、cuDNN tensor core 路徑偏好 NHWC 的原因（講義 p39）。
    - I2 的效果：AI 不變（bytes 已經是最少），但 instruction 變少 → **在 roofline 上往上移**（[03:01:02]）。
    - **CUDA-core ladder**（RTX 4090 Laptop，3×3 shape；講義 p43）：

      | Kernel | 載入方式 | ms | TFLOP/s | % FP32 peak | instr/FMA |
      |---|---|---|---|---|---|
      | D1 naive | 每 tap scalar LDG | 8.40 | 0.88 | 3% | 25 |
      | E1 + E3 | im2col + SGEMM（多 2 × 231 MB） | 2.37 | 3.12 | 11% | 5.9 |
      | I1 NCHW | predicated scalar gather | 1.68 | 4.40 | 16% | 4.6 |
      | I2 NHWC | float4 gather | 0.747 | 9.91 | 35% | 1.9 |

      cycles per instruction 幾乎不變（10–15），**加速幾乎全部來自 instruction per FMA 變少**。1×1 shape 上 I2–I4 都是 memory-bound（60% DRAM bandwidth）。

12. **現代 convolution 變體、BN folding、epilogue fusion**（[03:02]–[03:04]；講義 p44–p49）
    - Convolution 沒有因為 Transformer 消失，只是形狀變多（pointwise、depthwise、Mamba 的 causal conv1d、video VAE 的 3D conv 等），多數仍可寫成 GEMM。老師說專題的 ResNet 應該也有用到 depthwise（[03:03:04]，待確認，見下）。
    - **BN folding**（專題會遇到）：`y = γ·(conv(x) − μ)/σ + β` ⇒ 改用 `W' = W·γ/σ`、`b' = β − μγ/σ`，一個 GEMM 解決（講義 p47）。
    - Epilogue fusion：bias、ReLU/GELU、residual、量化都可以在 register 裡順手做（講義 p48）。

13. **CUDA Events**（[03:04]–[03:07]；講義 p50–p52）
    - `cudaEventCreate` / `cudaEventDestroy` / `cudaEventRecord` / `cudaEventSynchronize` / `cudaEventElapsedTime`；在 GPU 上量 kernel 本身的時間（毫秒），不含 host↔device 傳輸。不要用 disable-timing 的 flag。
    - 講義有一個 `Timer` class：constructor 建兩個 event a、b，destructor 釋放，`start()` record a、`stop()` record b、synchronize 後算 elapsed。
    - 目前都在 default（NULL）stream 0；stream 是 Winter 2027 的內容。
    - **專題 harness 已經內建 event timer，不用自己寫**；要加更多 timer 可以用這個（[03:06:03]）。

14. **Final Project：時程與 tier**（[03:07]–[03:12]；講義 p53–p57）
    - 時程（講義 p53，*= 不能用 late days）：team 註冊 11/16 11:59 PM*；starter kit 11/16 10 PM 發布；**Proposal 11/20 11:59 PM**；**T0 smoke test 11/22 11:59 PM**；發表 sign-up 11/24 5:59 PM*；T1–Tn 提交期間 11/22–12/15；**Design Spec 12/2 11:59 PM**；**Leaderboard freeze＋code 12/15 5 PM***；發表 12/15–17 6–9 PM（10 分鐘＋5 分鐘 Q&A）*；**Final Report 12/17 11:59 PM***。
    - 建議進程（講義 p55；口述 [03:09:02]–[03:11:00]）：
      | Tier | 內容 | 對應講次 |
      |---|---|---|
      | T0 | build、過 `check.py`、profile、選 batch size、拿第一筆 leaderboard | 現在 |
      | T1 | NHWC＋batching；explicit im2col＋自己的 SMEM tiled SGEMM；無 bank conflict 的 tile；bias/ReLU fused 進 epilogue。口述：把 naive GEMM 換成加速版 | L3–L6 |
      | T2 | implicit GEMM（拿掉 im2col buffer）、fused residual add、per-shape launch config | L7（今天） |
      | T3 | register tiling、thread coarsening、`float4`、per-shape tile 調參 | L8（11/24） |
      | T4 | tensor core（FP16 WMMA / `mma.sync`，FP32 累加），開啟 FP16 類別 | L9（12/1） |
      | T5 | fusion 與調參（stem conv＋maxpool、downsample、warp-shuffle avgpool、autotune） | stretch |
    - 每到一個 tier 就提交一次，每個 tier 各自排名；同一隊每個 tier 都可以有一筆（[03:11:00]）。
    - **Proposal 內容**（講義 p57）：PDF、最多 2 頁；組員（3 人，Canvas People/Groups 註冊）；預計做到的 tier（之後可調）；work breakdown（誰負責哪個 kernel）；**要評估的 Nsight Compute metrics 清單及其與效能的關係**；主要參考資料。
    - 老師叮嚀：先跟組員約會議，分工，這就是 proposal 的內容（[00:07:01]、[03:07:02]）。

15. **Starter kit 導覽**（[03:12]–[03:29]；講義 p54、p56）
    - Canvas Files → Final Project - ResNet 18：`resnet18_pack.zip`（data pack，權威資料集）和 `resnet18_student_kit_v06.zip`。先讀 README → Getting Started → spec；**先用 SHA-256 checksum 驗證 data pack**（[00:04:04]、[03:15:02]）。
    - Data pack 有 debug（8 張）、dev（500 張）、val（全集，「三千多張」）。**開發時用 dev，val 只在最後提交時跑**（[03:15:02]）。
    - **AWS T4 的新 image 會內建 data pack**，不用每次重下，老師說「hopefully tomorrow」（11/18）上線（[03:16:00]–[03:17:00]）。
    - 程式結構：`include/`、`src/`、kernels；已有 direct conv kernel、im2col（explicit）kernel 和其他層的 kernel，**工作就是把這些換掉**。`main` 解析參數後呼叫 run engine；executor 讀 manifest（JSON，在 data pack 裡）轉成一串 op（convolution、normalize、max pool、avg pool、fully connected）再 launch。產出 `engine.exe`；提交用 `submit.py`（[03:17:00]–[03:20:00]）。
    - Smoke test：照 Getting Started 在 AWS T4 上跑完就會自動產生 submission zip；**繳交位置還沒定，老師說大概是 Canvas**，幾天內公布（[03:08:02]、[03:16:00]）。
    - 建議步驟：build → 跑 → **先 profile 再最佳化**，找出哪些 layer 是 hot spot（[03:20:00]）。

16. **NCU profiling starter kit 的訣竅**（[03:21]–[03:29]）
    - **`--launch-count`**：direct conv kernel 每層一次、ResNet-18 有 20 個 conv layer → 20；explicit im2col 每層兩個 kernel（transform＋GEMM）→ **40**；implicit（一個 kernel）又回到 20。用 debug set、batch 8，**不要在 val 上 profile**（[03:21:03]–[03:23:02]）。
    - 越深的 layer grid 越小。
    - Direct conv demo：AI ≈ 67，離 roofline 很遠（可以往上移很多）；L1 hit 96%、L2 hit 97%、DRAM throughput 0.5%；load 是 16 sectors/request（理想是 4），store 是理想的 4；NCU summary 直接提示「uncoalesced global accesses」（[03:24:01]–[03:27:02]）。
    - im2col transform kernel 沒有 FMA，在 roofline 上直接不見；GEMM kernel 比 direct 更接近 roofline，但每層不同（[03:27:02]–[03:28:03]）。

## 名詞解釋

- **im2col / im2row**：把 convolution 的輸入攤成 patch matrix，讓 convolution 變成一次 GEMM。im2col 對應 NCHW（patch matrix 是 [CRS]×[NPQ]、operand B），im2row 對應 NHWC（[NPQ]×[RSC]、operand A，channel 最快）。
- **Patch / receptive field**：filter 在某個位置蓋住的輸入區域；對輸出 pixel (p,q) 有貢獻的所有輸入值。
- **Patch matrix（X̃）**：把每個 patch 攤平後排成的矩陣；explicit 版本會膨脹 R·S 倍。
- **Explicit GEMM**：先用 transform kernel 在 DRAM 建出 patch matrix，再丟給一般 GEMM（兩個 kernel）。
- **Implicit GEMM**：不建 patch matrix，GEMM 的 tile loader 直接算位址從原始輸入 gather（一個 kernel）。之後還有 hardware im2col（TMA，講義 p22，本課後面才會講）。
- **Reduction dimension（K_gemm）**：GEMM 內積相加的維度；conv fprop 是 C·R·S。
- **NCHW / NHWC**：tensor 的記憶體 layout，最右邊的維度在記憶體中連續（最快）。NHWC = channels-last。
- **Stride / pad / dilation**：filter 每步移動量 / 周圍補 0 的圈數 / filter tap 間的間隔。
- **Valid / same padding**：pad 0（輸出變小）/ 補到輸出和輸入一樣大。
- **Cross-correlation**：不翻轉 filter 的 convolution，深度學習的「convolution」其實是這個。
- **Compulsory bytes**：X、W 各讀一次、Y 寫一次的最低記憶體流量，用來算理論 AI。
- **fprop / dgrad / wgrad**：forward 輸出、對輸入的梯度、對權重的梯度；都是 GEMM。
- **col2im**：im2col 的反向（scatter-add），dgrad 需要。
- **Register tiling**：每個 thread 在 register 裡保留一塊輸出（例如 4×4），從 SMEM 讀少量值做很多 FMA。L8 細講。
- **Epilogue / fused epilogue**：主 reduction 之後的逐元素運算（α/β、bias、ReLU、residual）；放進同一個 kernel 叫 fused。
- **BN folding**：把 batch norm 的 γ、β、μ、σ 併進 conv 的 W'、b'，推論時就不用另外做 normalize。
- **`__restrict__`**：告訴 compiler 指標不 alias，可走 read-only path（`ld.global.nc`）。
- **`float4` vectorized load/store**：一個 instruction 搬 16 bytes；需要 16-byte 對齊、連續。
- **SIMD vs SIMT**：明確寫向量指令 vs 寫 scalar code、由硬體把 warp 的存取合併。
- **CUDA Events**：GPU 端的時間戳物件，用 `cudaEventElapsedTime` 量 kernel 時間（ms）。
- **Tier（專題）**：T0–T5 的最佳化階段，每階段各自提交、各自排 leaderboard。
- **Sectors per request**：NCU 的 coalescing 指標；FP32 一個 warp 理想是 4 個 32-byte sector。

## 老師強調的地方（附逐字稿時間戳 [hh:mm:ss]）

- [00:05:05] 這堂是 final project 的關鍵講次，因為專題整個都是 convolution layer；L7、L8、L9 會一步步給你更多最佳化手段。
- [00:06:02] 遲交作業 11/27 前一定要交齊，之後要開始改專題。
- [00:07:01] 這幾天就要和組員開會，決定做法和分工，這就是 proposal 的內容。
- [00:09:01] 專題「not that hard」：只要寫 kernel 換進去，其他程式都寫好了。
- [00:10:00]–[00:11:01] GEMM 是 GPU 的理想 case study；沒有 GEMM 在 GPU 上這麼快，就不會有現在的機器學習。
- [00:18:01]–[00:19:01] 每個 filter 跟輸入有一樣多的 channel，不是「每個 channel 一個 filter 再相加」；老師自己也曾這樣誤解。
- [00:20:02]–[00:22:01] 維度符號要分清楚，「nobody is consistent」；GEMM 的 N、K 和 conv 的 N、K 不同，有疑問就先確認在講哪一個。
- [00:41:00]–[00:43:01] Layer shape 決定 compulsory bytes；你的 kernel 設計決定冗餘多少、資料離運算單元多近。
- [01:01:02] D1 每個 FMA 要約 25 個 instruction；occupancy 93% 不是問題，occupancy 不是唯一指標，之後會看到故意降低 occupancy 反而更快。
- [01:08:05] 投影片上 Y、W、X̃ 的式子寫反了；X̃ 是 C = A·B 裡的 B，所以是 Y = W·X̃。
- [01:18:03]–[01:20:00] layout 搞錯結果就錯；照 starter code 載入資料的方式做就對，不用自己從頭推。
- [01:24:01]–[01:25:02] 專題只做 forward prop。
- [01:41:01] 不用會實作 ResNet 也能把專題做好，但要懂 im2col 的實作。
- [01:42:03] 同樣的 kernel 改成 FP16 至少快兩倍（一個 FP32 的空間放兩個 FP16），專題可以做 FP16。
- [01:44:01]–[01:45:01] Explicit 在 DRAM 建 patch matrix，佔記憶體又要來回搬；implicit 分段放進 shared memory，更快但更複雜。
- [01:47:02] Production 沒人用 explicit，大家用 implicit GEMM，但要從 explicit 學起。
- [02:02:02] Padding 的 0 不會寫進記憶體，是 thread 在處理時補上的。
- [02:21:02]–[02:22:05] E3 GEMM 不在乎 layout，只要 A、B conformal；E1 或 E2 都餵給同一個 E3。
- [02:31:00] Register tile 裡的 FMA 全是 register 對 register，「as fast as you're going to get」。
- [02:34:04] Fused epilogue 省掉一次 kernel launch 和 global memory 來回。
- [02:54:04]–[02:55:02] Vector load 要求 16-byte 對齊和連續，不符合就「this code breaks」：比較脆弱但比較快。
- [03:01:02] I2 不改變 AI，而是減少 instruction，在 roofline 上往上移。
- [03:06:03] 專題 harness 已經有 event timer，不用自己實作。
- [03:10:03] T1：把 naive GEMM 換成加速過的 GEMM；用今天教的內容就可以開始做 implicit GEMM。
- [03:15:02] 開發用 dev set，val 只在最後提交時跑。
- [03:20:00] 先 build，再 profile 找 hot spot，把力氣花在報酬最大的地方。
- [03:21:03]–[03:23:02] NCU 的 launch count：direct 20、explicit im2col 40、implicit 20；用 debug set batch 8，在 val 上 profile「will kill you」。
- [03:27:02] NCU summary 的提示（uncoalesced global accesses）「spot on」，是第一個該看的地方。

## 和作業 / 考試的關聯

- **遲交作業**：11/27（五）11:59 PM 前交齊（講義 p2；[00:06:02]）。目前 `gpu/assignments.md` 記錄 HW1–HW4 都已 submitted / graded，HW0（Task 0）不計分。
- **Final Project Proposal**：**11/20（五）11:59 PM PST**（Canvas id 11810636，due_at 2026-11-21T07:59:59Z），專題 10%。內容見重點摘要 14：組員、tier 計畫、分工、**NCU metrics 清單**（本講的 sectors/request、L1/L2 hit rate、DRAM throughput、instructions per FMA、roofline AI 都是可以列的候選）、參考資料（講義 p49 有 core readings）。
- **T0 smoke test**：11/22（日）11:59 PM，繳交位置待公布（大概是 Canvas）。
- **發表 sign-up**：11/24（二）5:59 PM / 6 PM，不能用 late days。
- **Design Spec**：講義 p53 寫 12/2 11:59 PM；`gpu/assignments.md` 目前記 12/1（二）5:59 PM（未發布），要核對。
- **Leaderboard freeze＋code**：12/15 5 PM；**發表** 12/15–17 6–9 PM；**Final Report** 12/17 11:59 PM。
- 本講直接對應 **T1（explicit im2col＋SMEM SGEMM）和 T2（implicit GEMM）**；L8 register tiling → T3；L9 tensor core → T4。
- 下週 L8（11/24）細講 register tiling（本講 E3 的 TM×TN）。

## 還要釐清的問題

- **組別到底定了沒？** 老師 [00:03:02] 說已經全部分好三人一組；但 11/18 晨報記錄 Canvas 的 team sign-up 重開到 **11/18 11:59 PM**、所有組別重置，要到 People → Project Teams 重新加入。以 Canvas 的最新狀態為準，今晚截止前確認自己有在組裡。
- **Proposal 截止**：講義 p56 還寫「Proposal with work breakdown due Nov 18」，是舊文字；講義 p2、p53、口述 [00:06:02] 和 Canvas 都是 11/20。
- **Design Spec 截止**：講義 p53 是 12/2 11:59 PM，`gpu/assignments.md` 是 12/1 5:59 PM，Canvas 發布後再核對。
- **發表 sign-up 時間**：講義 p2「6 PM」vs p53「5:59 PM」，差一分鐘，照早的算。
- **T0 smoke test 的繳交位置**：老師說「to be announced」，大概是 Canvas。
- **AWS T4 新 image（內建 data pack）** 是否已在 11/18 上線。
- 老師說專題的 ResNet 層「I think」有用到 depthwise conv（[03:03:04]）。標準 ResNet-18 沒有 depthwise，要對照 manifest／spec 的 12 個 shape class 確認。
- Val set 的張數：口述「三千多」；L6 筆記記的是 Imagenette 10 類共 3,925 張，看 spec 確認。
- E3 的 register tiling 細節（每個 thread 負責哪些 row/col、為什麼 BK=8）留到 L8。
- 講義 p22 提到的 § 3.3（TMA hardware im2col、T1–T3 kernel）和 I3、I4 這堂沒講，是否在 L8/L9 講。
