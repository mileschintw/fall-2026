# GPU 學習進度

> 每次上課結束更新。時間用 Pacific。掌握程度：⬜ 未學、🟨 看過但不穩、🟩 能自己解釋並做對題目。

## 目前位置
- 下一步：模組 5（效能理論）／步驟 3 互動頁／問題 3a 待答：「用互動頁找出 RTX 3050 上 WORK 大約多少時 kernel 開始變慢，用 AI 和 ridge point 說明」（答案：2W−1 = 12 × 40.6 → W ≈ 244）。之後步驟 4 講解（L3 p24–31、[01:16:00]–[01:53:02]，T4 推算 [02:31:03]）→ 步驟 5 練習（含診斷 Q8 SAXPY 重測）→ 步驟 6 動手。模組 5 之後照 curriculum.md 的建議順序：6 → 10 → 8 → 9 → 11，M7 延後；進 10 前補測 M4 的 L4 新內容
- 上次上課：2026-10-28 17:50 – 18:15 PT
- 累計上課分鐘：145

## 模組
| # | 模組 | 狀態 | Artifact | 最後上課 |
|---|---|---|---|---|
| 0 | 診斷 | 🟩（已批改） | — | 10/27 |
| 1 | CPU vs GPU | 🟩（練習 2 全對、交叉點對；latency 定義和 SI 換算放待複習） | [GPU Round-Trip 帳單](https://claude.ai/artifact/UgjmP4Rsx5Lyrg8ko5wCjP)（`modules/01-cpu-vs-gpu.html`） | 10/28 |
| 2 | CUDA 程式流程 | 🟩（診斷 Q2 對；10/28 掃描 S1 錯後重問對、S2、S3 對） | — | — |
| 3 | Grid / block / thread | 🟩（Q3 對；Q4 經學生確認是筆誤，自行更正為 +col；10/28 掃描 S4 對） | — | — |
| 4 | SIMT、warp | 🟩（診斷 Q5、Q6 對；10/28 掃描 S5 對、S6 部分對；L4 p34–41 新內容未測，見 curriculum 建議順序） | — | — |
| 5 | 效能理論 | 🟨（進行中：熱身 2 題對；預測 WORK=100 錯，見錯題表） | [Roofline 兩條水管](https://claude.ai/artifact/Fs1fQTcsxcM2HMXz2vUUnX)（`modules/05-roofline.html`） | 10/28 |
| 6 | 記憶體階層、tiling | ⬜（Q9 不會） | — | — |
| 7 | 拆解 HW2 | ⬜ | — | — |
| 8 | Occupancy 與 launch configuration | ⬜ | — | — |
| 9 | Warp scheduling、latency hiding | ⬜（S6 已碰到 zero-overhead 切換） | — | — |
| 10 | 任意尺寸 tiled MMULT 邊界檢查 | ⬜（S5 的右排／下排 divergence 就是 p42–47 的同一種分析） | — | — |
| 11 | Nsight Compute 實作 | ⬜ | — | — |

## 觀念掌握（細項）
<!-- 每列：觀念 | 狀態 | 證據（哪一題答對/答錯、日期） -->
| 觀念 | 狀態 | 證據 |
|---|---|---|
| GPU 適合什麼工作（throughput、簡單重複運算） | 🟩 | M1 練習 2（10/28）四個情境全對，理由能講出傳輸成本與運算量的權衡；b 理由寫「比較規則複雜不利平行」，主因其實是 n 太小（latency）。先前證據：診斷 Q1（10/27）：說出「簡單算術、要規劃情境」；漏了 host↔device 搬資料成本、序列/分支多/單一 latency 敏感的工作 CPU 較快。M1 熱身（10/27）：說出 alloc→H2D→算→D2H、傳輸可能抵銷加速 ✔；但以為「資料量大時」傳輸才吃掉優勢（vector add 這種 AI 低的工作在任何大小都被傳輸主導，小 n 時還有固定 overhead） |
| Host/device 流程順序（malloc→H2D→kernel→D2H→free） | 🟩 | 診斷 Q2（10/27）c d a b e 全對 |
| nvcc：.cu→PTX→SASS、fatbin、PTX JIT 相容性 | 🟩 | 掃描 S3（10/28）答「CC 不同吃不了 7.5 的 SASS，沒 PTX 就無法 JIT，不能執行」✔；RTX 3050 實測只編 sm_75 → launch 報 no kernel image，加 compute_75 → 正常。補充：同一個 major 內新的 minor 可以跑舊 SASS（sm_80 cubin 能在 8.6 跑），所以「CC 不同就不能跑」說得太寬 |
| kernel launch 非同步、錯誤在 sync 才回報 | 🟩 | 掃描 S2（10/28）答「錯誤在 GPU 上，sync 前 CPU 不知道」✔；補充：launch 立刻返回、設定錯誤 launch 時就報、`cudaMemcpy` 會隱含同步、CPU 計時要先 sync |
| block 數 = ceil(n/blockDim)、邊界 `if` | 🟩 | 診斷 Q3（10/27）4 個、知道最後一個 block 超出範圍 |
| 2D→1D row-major index | 🟩 | 診斷 Q4（10/27）寫成 `row*W + H`，被問到時自己說是筆誤，更正為 `row*W + col` |
| 2D grid 配置（`dim3 grid` x 對寬、ceil-div、越界 thread 數） | 🟩 | 掃描 S4（10/28）76×62、16×16 → grid(5,4)、5120 threads、408 個被擋，全對，x/y 順序也對 |
| kernel launch 固定 overhead（小 n 輸的原因） | 🟨 | M1 追問（10/27）答「compile 或啟動 kernel」：launch 對；compile 錯（nvcc 事先編好 SASS，只有第一次啟動多約 0.16 ms 的 lazy module loading） |
| latency vs throughput（T = 固定延遲 + 工作量/throughput） | 🟨 | M1 練習 1（10/27）列式對、單位錯；練習 3（10/28）短答：latency 定義成「資料傳輸的時間」太窄（應是完成一件事的時間：一次存取、一個指令、一次 launch、一趟 round trip）；throughput 對；「GPU 為 throughput 設計、單次較慢、靠大量工作掩蓋 latency」✔ |
| warp = 32 threads、block 大小取 32 倍數 | 🟩 | 診斷 Q5（10/27）4 個 warp、不整除會有 lane 空轉 |
| zero-overhead warp 切換、latency hiding | 🟨 | 掃描 S6（10/28）答「換 warp 不用像 CPU 那樣 offload 再 load」✔；但原因說成「GPU 核心數多」✘（真正原因是 register file 大到每個常駐 warp 的 context 一直留在 SM 上：Turing／GA10x 每 SM 64K 個 32-bit register = 256 KB）；還沒問「所有 warp 都在等時會怎樣」（L3 [00:40:01]，模組 8／9 再接） |
| Control divergence | 🟩 | 診斷 Q6（10/27）兩條路徑分開跑、用 mask 遮住另一半 |
| 2D block 攤平切 warp（tid = ty*bx + tx、warp = tid/32） | 🟩 | 掃描 S5（10/28）一開始不知道怎麼切（猜 16×2 ✔），講解 + 互動圖後答對右排 8、下排 0 個 divergence；理由說成「整個越界的 warp 不會排入執行」✘（其實照樣執行、一起跳過 if） |
| Amdahl's law | 🟩 | M5 熱身 2（10/28）：f=0.1、P=4 一開始不知道 P 的影響；看「序列段不變、平行段 ÷P」的時間圖後算出 100 s → 32.5 s、約 3 倍 ✔。先前證據：診斷 Q7（10/27）答 10×（P→∞） |
| FLOP / bytes / arithmetic intensity | ⬜ | 診斷 Q8（10/27）不會；M5 預測（10/28）以為 kernel 時間跟運算量成正比 |
| memory-bound vs compute-bound（roofline） | ⬜ | 診斷 Q8（10/27）不會 |
| shared vs global memory | ⬜ | 診斷 Q9（10/27）不會 |
| `__syncthreads()` 在 tiling 的兩個用途（RAW、WAR） | ⬜ | 診斷 Q9（10/27）不會 |
| occupancy（四項限制取最小、block slot vs warp slot） | ⬜ | L4 p5–11，HW3 Part 1 I、IV、V |
| register spilling、`cuobjdump`／ptxas verbose | ⬜ | L4 p8 例 D、[00:54:03] |
| warp scheduler、eligible／stalled、stall 原因、Little's law | ⬜ | L4 p27–32 |
| waves／tail wave | ⬜ | L4 p33 |
| loop-induced 與巢狀 branch divergence、predicate bit | ⬜ | L4 p37–41，HW3 3.1 |
| 任意尺寸 tiled MMULT 邊界檢查（LOAD／USE／寫回、`__syncthreads()` 在 if 外） | ⬜ | L4 p12–25、[01:41:00]，HW3 3.2 |
| warp-phase divergence 計數 | ⬜ | L4 p42–48，HW3 Part 2 |
| NCU 讀報告（Summary、SOL、Roofline、Warp State、Baseline、Source view） | ⬜ | L4 p49–51，HW3 3.1、3.2 |
| host 和 device 是兩個位址空間（`d_` 指標不能在 host 解參考） | 🟨 | 掃描 S1 重問（10/28）答「GPU 碰不到 CPU 的 RAM」✔（實測 error 700 illegal memory access，sync 才報、之後的呼叫都失敗、exit code 仍是 0）；補充過 pinned/mapped、unified memory 是例外。掃描 S1（10/28）答「還沒 sync，不會有差別」✘；RTX 3050 實測 host 寫 `d_x[0]` 直接 access violation（0xC0000005） |

## 錯題與錯誤觀念
<!-- 日期 | 題目 | 學生的答案 | 背後的錯誤模型 | 是否已修正 -->
| 日期 | 題目 | 學生的答案 | 背後的錯誤模型 | 是否已修正 |
|---|---|---|---|---|
| 10/27 | 診斷 Q4 2D→1D index | `row*W + H` | 筆誤（學生 10/27 自行更正為 +col），不是觀念錯 | 是 |
| 10/27 | M1 練習 1 交叉點計算 | 列式 `10us + 8n/100G = 8n/20G` ✔；下一步寫 `1000 s = 40n - 8n`，得 n = 31.25 | SI 字首相乘：把 10u × 100G 算成 1000（μ×G 當成互相抵消），實際 = 10⁻⁵ × 10¹¹ = 10⁶（= 1 MB）；也沒做合理性檢查（31 個元素 GPU 怎麼可能贏）。10/27 已講解，待再測 | 部分 |
| 10/27 | M1 互動頁：資料已在 GPU，n 多大 GPU 才贏 | 約 9000（✔，模型交叉點 ≈ 8800）；理由「GPU 本身運算能力比較差，優勢是平行化」 | 把小 n 輸的原因歸給「算得慢」；實際上小 n 時 kernel 時間幾乎固定（launch overhead／latency ≈ 6 μs），跟算力無關。「單一 thread 比 CPU 核心弱」這半句是對的 | 否 |
| 10/28 | 掃描 S1 host 寫 `d_x[0]` | 「還沒開始執行也還沒 sync，應該不會有差別」 | 把 `cudaMalloc` 拿到的指標當成一般 host 指標，以為問題只在時間順序（sync），沒有「兩塊記憶體、各自的位址」的模型 | 部分（反方向重問答對） |
| 10/28 | 掃描 S5 下排 block 為什麼沒有 divergence | 「整區灰色代表一開始就不會排入執行」 | 以為越界的 warp 不存在／不被排程；實際上 block 的 256 個 thread 全部都會啟動，整個 warp 都走 `if` 為 false 那條路，一起跳過，所以沒有 divergence，但還是占 warp slot 和 register | 否 |
| 10/28 | 掃描 S6 為什麼 GPU 換 warp 幾乎免費 | 「因為 GPU 核心數多，換 warp 不用 offload 再 load」 | 後半對；前半把原因歸給核心數。切換免費靠的是每個常駐 warp 都有自己的一份 register（SM 上的大 register file），跟 core 數量無關 | 部分 |
| 10/28 | M5 預測：WORK 1→100（運算 ×200，資料量不變），kernel 時間？ | 「100 倍，運算量提升多少就要多少 cycle」 | 把 kernel 時間當成只由運算量決定；沒有「搬資料和運算同時進行、時間取較長者」的模型。實測 RTX 3050 WORK=1 0.68 ms、WORK=100 0.69 ms（搬 120 MB 要 0.54 ms，運算 2×10⁹ FLOP 只要 0.22 ms）；WORK=1000 才變 3.0 ms | 否（步驟 3 互動頁進行中） |
| 10/27 | 診斷 Q1 為什麼不全丟 GPU | 「擅長平行但只做簡單算術，要規劃情境」 | 沒有 host↔device 傳輸成本的概念；沒提到 latency vs throughput、序列部分 | 否 |

## 待複習
<!-- 下次熱身要問的題目 -->
1. 用一句話定義 latency，舉兩個不是「資料傳輸」的例子。（10/28 練習 3 定義太窄）
2. 程式 20% 序列、8 個核心，最多快幾倍？（Amdahl P 有限，10/28 經引導後才算對，再測一次不給圖）
3. 一個 kernel 運算量變 10 倍、資料量不變，時間一定變 10 倍嗎？什麼情況下幾乎不變？（M5 預測錯過）

## 上課紀錄
<!-- 日期 時間 PT｜分鐘數｜做了什麼 -->
- 2026-10-27 22:10 PT｜65｜模組 0 診斷：9 題，Q2、Q3、Q5、Q6、Q7 對；Q1 部分對；Q4 筆誤（自行更正）；Q8、Q9 不會；Q4 確認筆誤；M1 熱身（round-trip 組成）答對大方向；M1 預測「n=10⁷ kernel 占幾 %」猜 50%（自述亂猜），實測 3.5–4%；做了 exercises/01-roundtrip.cu 和互動頁
- 2026-10-28 02:05 PT｜（含在上列 65 分鐘）｜模組 1 動手：WORK=10 猜 GPU 贏（憑互動頁印象）✔，實測 GPU 18.1 ms vs CPU 23.0 ms；kernel 0.73 ms 跟 WORK=1 幾乎一樣（memory-bound 的伏筆）。M1 完成 🟩
- 2026-10-28 14:40 PT｜約 55｜M2–M4 快速掃描（學生要求）：S1 host 寫 `d_x[0]` 錯（以為是 sync 問題，實測 access violation），反方向重問對；S2 非同步 launch 對；S3 只編 sm_75 對（實測 no kernel image）；S4 2D grid 全對；S5 不知道 2D block 怎麼切 warp → 講解 + show_widget 互動圖後答對，理由小錯；S6 latency hiding 部分對。進模組 5 熱身
- 2026-10-28 17:00 PT｜0（不計）｜檢查 L4 新增的模組 8–11：頁碼正確；補時間戳、HW3 對照（FMAD、四個 divergence metric）、8 列 L4 觀念、建議順序 5→6→10→8→9→11。M5 熱身第 1 題重問，學生改到下個 session 再開始
- 2026-10-28 17:50 PT｜約 25｜M5 熱身 1 SI 換算 5 μs × 200 GB/s = 1 MB ✔（μ×G 已修正）；熱身 2 Amdahl P=4 先不會，時間圖引導後算出 32.5 s、約 3× ✔；預測 WORK=100 猜 100 倍 ✘，實測 RTX 3050 WORK 1／100／1000 = 0.68／0.69／3.0 ms（1000 另兩次 16–17 ms，疑似未升頻）；做 roofline 互動頁
