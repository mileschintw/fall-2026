# GPU 學習進度

> 每次上課結束更新。時間用 Pacific。掌握程度：⬜ 未學、🟨 看過但不穩、🟩 能自己解釋並做對題目。

## 目前位置
- 下一步：模組 1／步驟 6 動手／已請學生把 `exercises/01-roundtrip.cu` 第 21 行 WORK 改成 10，先猜 n=1000 萬時誰贏再跑、貼結果（10/28 01:05）。實測答案：WORK=10 → GPU 18.6 ms vs CPU 22 ms（接近交叉、GPU 小贏）；WORK=100 → GPU 19 ms vs CPU 750 ms；WORK=1000 → kernel 從 0.6 ms 跳到 2.4 ms（變 compute-bound，約 8.5 TFLOPS），CPU 14 s。WORK 1→100 kernel 時間幾乎不變＝memory-bound，可當模組 5 AI/roofline 的伏筆。之後步驟 7 收尾（M1 可升 🟩）
- 上次上課：2026-10-27 22:10 PT（模組 0 診斷）
- 累計上課分鐘：60

## 模組
| # | 模組 | 狀態 | Artifact | 最後上課 |
|---|---|---|---|---|
| 0 | 診斷 | 🟩（已批改） | — | 10/27 |
| 1 | CPU vs GPU | 🟨（診斷 Q1 部分對；學習中） | [GPU Round-Trip 帳單](https://claude.ai/artifact/UgjmP4Rsx5Lyrg8ko5wCjP)（`modules/01-cpu-vs-gpu.html`） | 10/27 |
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
| block 數 = ceil(n/blockDim)、邊界 `if` | 🟩 | 診斷 Q3（10/27）4 個、知道最後一個 block 超出範圍 |
| 2D→1D row-major index | 🟩 | 診斷 Q4（10/27）寫成 `row*W + H`，被問到時自己說是筆誤，更正為 `row*W + col` |
| kernel launch 固定 overhead（小 n 輸的原因） | 🟨 | M1 追問（10/27）答「compile 或啟動 kernel」：launch 對；compile 錯（nvcc 事先編好 SASS，只有第一次啟動多約 0.16 ms 的 lazy module loading） |
| latency vs throughput（T = 固定延遲 + 工作量/throughput） | 🟨 | M1 練習 1（10/27）列式對、單位錯；練習 3（10/28）短答：latency 定義成「資料傳輸的時間」太窄（應是完成一件事的時間：一次存取、一個指令、一次 launch、一趟 round trip）；throughput 對；「GPU 為 throughput 設計、單次較慢、靠大量工作掩蓋 latency」✔ |
| warp = 32 threads、block 大小取 32 倍數 | 🟩 | 診斷 Q5（10/27）4 個 warp、不整除會有 lane 空轉 |
| Control divergence | 🟩 | 診斷 Q6（10/27）兩條路徑分開跑、用 mask 遮住另一半 |
| Amdahl's law | 🟨 | 診斷 Q7（10/27）答 10×，沒寫推導（1/f），還沒確認會用在 f、P 有限的情況 |
| FLOP / bytes / arithmetic intensity | ⬜ | 診斷 Q8（10/27）不會 |
| memory-bound vs compute-bound（roofline） | ⬜ | 診斷 Q8（10/27）不會 |
| shared vs global memory | ⬜ | 診斷 Q9（10/27）不會 |
| `__syncthreads()` 在 tiling 的兩個用途（RAW、WAR） | ⬜ | 診斷 Q9（10/27）不會 |

## 錯題與錯誤觀念
<!-- 日期 | 題目 | 學生的答案 | 背後的錯誤模型 | 是否已修正 -->
| 日期 | 題目 | 學生的答案 | 背後的錯誤模型 | 是否已修正 |
|---|---|---|---|---|
| 10/27 | 診斷 Q4 2D→1D index | `row*W + H` | 筆誤（學生 10/27 自行更正為 +col），不是觀念錯 | 是 |
| 10/27 | M1 練習 1 交叉點計算 | 列式 `10us + 8n/100G = 8n/20G` ✔；下一步寫 `1000 s = 40n - 8n`，得 n = 31.25 | SI 字首相乘：把 10u × 100G 算成 1000（μ×G 當成互相抵消），實際 = 10⁻⁵ × 10¹¹ = 10⁶（= 1 MB）；也沒做合理性檢查（31 個元素 GPU 怎麼可能贏）。10/27 已講解，待再測 | 部分 |
| 10/27 | M1 互動頁：資料已在 GPU，n 多大 GPU 才贏 | 約 9000（✔，模型交叉點 ≈ 8800）；理由「GPU 本身運算能力比較差，優勢是平行化」 | 把小 n 輸的原因歸給「算得慢」；實際上小 n 時 kernel 時間幾乎固定（launch overhead／latency ≈ 6 μs），跟算力無關。「單一 thread 比 CPU 核心弱」這半句是對的 | 否 |
| 10/27 | 診斷 Q1 為什麼不全丟 GPU | 「擅長平行但只做簡單算術，要規劃情境」 | 沒有 host↔device 傳輸成本的概念；沒提到 latency vs throughput、序列部分 | 否 |

## 待複習
<!-- 下次熱身要問的題目 -->
1. 只有 1000 個元素的 vector add，GPU round-trip 裡哪一段最花時間？為什麼「資料小」反而更不划算？
2. SI 字首換算：5 μs × 200 GB/s 等於多少 bytes？（再測 μ×G）
3. 程式 10% 序列、有 4 個核心，最多快幾倍？（Amdahl 用在 P 有限的情況）

## 上課紀錄
<!-- 日期 時間 PT｜分鐘數｜做了什麼 -->
- 2026-10-27 22:10 PT｜60｜模組 0 診斷：9 題，Q2、Q3、Q5、Q6、Q7 對；Q1 部分對；Q4 筆誤（自行更正）；Q8、Q9 不會；Q4 確認筆誤；M1 熱身（round-trip 組成）答對大方向；M1 預測「n=10⁷ kernel 占幾 %」猜 50%（自述亂猜），實測 3.5–4%；做了 exercises/01-roundtrip.cu 和互動頁
