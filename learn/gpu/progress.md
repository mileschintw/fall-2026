# GPU 學習進度

> 每次上課結束更新。時間用 Pacific。掌握程度：⬜ 未學、🟨 看過但不穩、🟩 能自己解釋並做對題目。

## 目前位置
- 下一步：M2–M4 快速掃描（學生 10/28 要求：診斷每模組只考 1–2 題，想補沒考到的部分）。一則一題，答對就過，答錯才停下來教。題目：S1 host 端寫 `d_x[0]` 會怎樣（M2 兩塊記憶體）→ S2 kernel launch 是非同步、`cudaDeviceSynchronize` 的用途（M2）→ S3 .cu→PTX→SASS、只編 sm_75 的執行檔拿到 RTX 3050 能不能跑（M2）→ S4 62×76 影像、16×16 block 的 `dim3 grid` 與 2D index（M3）→ S5 2D block 16×16 的 warp 怎麼切、grid-stride loop（M3/M4）→ S6 zero-overhead warp 切換如何藏 latency（M4）。S1 重問答對（10/28）。S2 答對（10/28）。S3 答對（10/28）。S4 全對（10/28）。目前在 S5（已問：同一張 76×62 影像，右邊那排 block（blockIdx.x=4，只有 col 64–75 有效）8 個 warp 幾個 divergence？下排 block（blockIdx.y=3，row 62–63 無效）呢？答案：右排 8 個全部（每個 warp 是 2 列 × 16，每列都有 4 個越界）；下排 0 個（warp 7 = row 62–63 整個越界，整個 warp 一起跳過，不算 divergence），角落那塊 7 個）。grid-stride loop 併入 S6 或略過。掃完接模組 5／步驟 1 熱身／待複習第 1 題（SI 字首換算）；步驟 2 預測可以從「01-roundtrip WORK=100 時 kernel 時間怎麼變」切入（實測 WORK 1→100 都約 0.6–0.7 ms，WORK=1000 才變 2.4 ms）（格式：模組 #／流程步驟／題號）
- 上次上課：2026-10-27 22:10 – 10/28 02:05 PT（模組 0 診斷、模組 1 完成）
- 累計上課分鐘：65

## 模組
| # | 模組 | 狀態 | Artifact | 最後上課 |
|---|---|---|---|---|
| 0 | 診斷 | 🟩（已批改） | — | 10/27 |
| 1 | CPU vs GPU | 🟩（練習 2 全對、交叉點對；latency 定義和 SI 換算放待複習） | [GPU Round-Trip 帳單](https://claude.ai/artifact/UgjmP4Rsx5Lyrg8ko5wCjP)（`modules/01-cpu-vs-gpu.html`） | 10/28 |
| 2 | CUDA 程式流程 | 🟩（診斷 Q2 對） | — | — |
| 3 | Grid / block / thread | 🟩（Q3 對；Q4 經學生確認是筆誤，自行更正為 +col） | — | — |
| 4 | SIMT、warp | 🟩（診斷 Q5、Q6 對） | — | — |
| 5 | 效能理論 | ⬜（Q7 對、Q8 不會） | — | — |
| 6 | 記憶體階層、tiling | ⬜（Q9 不會） | — | — |
| 7 | 拆解 HW2 | ⬜ | — | — |

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
| Control divergence | 🟩 | 診斷 Q6（10/27）兩條路徑分開跑、用 mask 遮住另一半 |
| Amdahl's law | 🟨 | 診斷 Q7（10/27）答 10×，沒寫推導（1/f），還沒確認會用在 f、P 有限的情況 |
| FLOP / bytes / arithmetic intensity | ⬜ | 診斷 Q8（10/27）不會 |
| memory-bound vs compute-bound（roofline） | ⬜ | 診斷 Q8（10/27）不會 |
| shared vs global memory | ⬜ | 診斷 Q9（10/27）不會 |
| `__syncthreads()` 在 tiling 的兩個用途（RAW、WAR） | ⬜ | 診斷 Q9（10/27）不會 |
| host 和 device 是兩個位址空間（`d_` 指標不能在 host 解參考） | 🟨 | 掃描 S1 重問（10/28）答「GPU 碰不到 CPU 的 RAM」✔（實測 error 700 illegal memory access，sync 才報、之後的呼叫都失敗、exit code 仍是 0）；補充過 pinned/mapped、unified memory 是例外。掃描 S1（10/28）答「還沒 sync，不會有差別」✘；RTX 3050 實測 host 寫 `d_x[0]` 直接 access violation（0xC0000005） |

## 錯題與錯誤觀念
<!-- 日期 | 題目 | 學生的答案 | 背後的錯誤模型 | 是否已修正 -->
| 日期 | 題目 | 學生的答案 | 背後的錯誤模型 | 是否已修正 |
|---|---|---|---|---|
| 10/27 | 診斷 Q4 2D→1D index | `row*W + H` | 筆誤（學生 10/27 自行更正為 +col），不是觀念錯 | 是 |
| 10/27 | M1 練習 1 交叉點計算 | 列式 `10us + 8n/100G = 8n/20G` ✔；下一步寫 `1000 s = 40n - 8n`，得 n = 31.25 | SI 字首相乘：把 10u × 100G 算成 1000（μ×G 當成互相抵消），實際 = 10⁻⁵ × 10¹¹ = 10⁶（= 1 MB）；也沒做合理性檢查（31 個元素 GPU 怎麼可能贏）。10/27 已講解，待再測 | 部分 |
| 10/27 | M1 互動頁：資料已在 GPU，n 多大 GPU 才贏 | 約 9000（✔，模型交叉點 ≈ 8800）；理由「GPU 本身運算能力比較差，優勢是平行化」 | 把小 n 輸的原因歸給「算得慢」；實際上小 n 時 kernel 時間幾乎固定（launch overhead／latency ≈ 6 μs），跟算力無關。「單一 thread 比 CPU 核心弱」這半句是對的 | 否 |
| 10/28 | 掃描 S1 host 寫 `d_x[0]` | 「還沒開始執行也還沒 sync，應該不會有差別」 | 把 `cudaMalloc` 拿到的指標當成一般 host 指標，以為問題只在時間順序（sync），沒有「兩塊記憶體、各自的位址」的模型 | 部分（反方向重問答對） |
| 10/27 | 診斷 Q1 為什麼不全丟 GPU | 「擅長平行但只做簡單算術，要規劃情境」 | 沒有 host↔device 傳輸成本的概念；沒提到 latency vs throughput、序列部分 | 否 |

## 待複習
<!-- 下次熱身要問的題目 -->
1. SI 字首換算：5 μs × 200 GB/s 等於多少 bytes？（再測 μ×G，10/27 練習 1 錯過）
2. 用一句話定義 latency，舉兩個不是「資料傳輸」的例子。（10/28 練習 3 定義太窄）
3. 程式 10% 序列、有 4 個核心，最多快幾倍？（Amdahl 用在 P 有限的情況，模組 5 開頭）

## 上課紀錄
<!-- 日期 時間 PT｜分鐘數｜做了什麼 -->
- 2026-10-27 22:10 PT｜65｜模組 0 診斷：9 題，Q2、Q3、Q5、Q6、Q7 對；Q1 部分對；Q4 筆誤（自行更正）；Q8、Q9 不會；Q4 確認筆誤；M1 熱身（round-trip 組成）答對大方向；M1 預測「n=10⁷ kernel 占幾 %」猜 50%（自述亂猜），實測 3.5–4%；做了 exercises/01-roundtrip.cu 和互動頁
- 2026-10-28 02:05 PT｜（含在上列 65 分鐘）｜模組 1 動手：WORK=10 猜 GPU 贏（憑互動頁印象）✔，實測 GPU 18.1 ms vs CPU 23.0 ms；kernel 0.73 ms 跟 WORK=1 幾乎一樣（memory-bound 的伏筆）。M1 完成 🟩
