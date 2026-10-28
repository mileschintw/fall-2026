# GPU 學習進度

> 每次上課結束更新。時間用 Pacific。掌握程度：⬜ 未學、🟨 看過但不穩、🟩 能自己解釋並做對題目。

## 目前位置
- 下一步：模組 1／步驟 5 練習／第 1 題（交叉點計算：overhead 10 μs、GPU 100 GB/s、CPU 20 GB/s、每元素 8 B，答案 n = 31,250）學生列式對、單位換算錯得 31.25；已問「1000 s 怎麼來的」（10/27 23:10），等回答後讓他自己改正；之後還要第 2–3 題（看情境判斷該不該丟 GPU、短答 latency vs throughput）（格式：模組 #／流程步驟／題號）
- 上次上課：2026-10-27 22:10 PT（模組 0 診斷）
- 累計上課分鐘：40

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
| GPU 適合什麼工作（throughput、簡單重複運算） | 🟨 | 診斷 Q1（10/27）：說出「簡單算術、要規劃情境」；漏了 host↔device 搬資料成本、序列/分支多/單一 latency 敏感的工作 CPU 較快。M1 熱身（10/27）：說出 alloc→H2D→算→D2H、傳輸可能抵銷加速 ✔；但以為「資料量大時」傳輸才吃掉優勢（vector add 這種 AI 低的工作在任何大小都被傳輸主導，小 n 時還有固定 overhead） |
| Host/device 流程順序（malloc→H2D→kernel→D2H→free） | 🟩 | 診斷 Q2（10/27）c d a b e 全對 |
| block 數 = ceil(n/blockDim)、邊界 `if` | 🟩 | 診斷 Q3（10/27）4 個、知道最後一個 block 超出範圍 |
| 2D→1D row-major index | 🟩 | 診斷 Q4（10/27）寫成 `row*W + H`，被問到時自己說是筆誤，更正為 `row*W + col` |
| kernel launch 固定 overhead（小 n 輸的原因） | 🟨 | M1 追問（10/27）答「compile 或啟動 kernel」：launch 對；compile 錯（nvcc 事先編好 SASS，只有第一次啟動多約 0.16 ms 的 lazy module loading） |
| latency vs throughput（T = 固定延遲 + 工作量/throughput） | 🟨 | M1 步驟 4 講解（10/27），還沒做題驗證 |
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
| 10/27 | M1 練習 1 交叉點計算 | 列式 `10us + 8n/100G = 8n/20G` ✔；下一步寫 `1000 s = 40n - 8n`，得 n = 31.25 | 兩邊同乘 100G 時，10 μs 沒換成秒（應為 1e-5 × 1e11 = 1e6）；也沒做合理性檢查（31 個元素 GPU 怎麼可能贏） | 否 |
| 10/27 | M1 互動頁：資料已在 GPU，n 多大 GPU 才贏 | 約 9000（✔，模型交叉點 ≈ 8800）；理由「GPU 本身運算能力比較差，優勢是平行化」 | 把小 n 輸的原因歸給「算得慢」；實際上小 n 時 kernel 時間幾乎固定（launch overhead／latency ≈ 6 μs），跟算力無關。「單一 thread 比 CPU 核心弱」這半句是對的 | 否 |
| 10/27 | 診斷 Q1 為什麼不全丟 GPU | 「擅長平行但只做簡單算術，要規劃情境」 | 沒有 host↔device 傳輸成本的概念；沒提到 latency vs throughput、序列部分 | 否 |

## 待複習
<!-- 下次熱身要問的題目 -->
1. 只有 1000 個元素的 vector add，GPU round-trip 裡哪一段最花時間？為什麼「資料小」反而更不划算？
2. 程式 10% 序列、有 4 個核心，最多快幾倍？（Amdahl 用在 P 有限的情況）

## 上課紀錄
<!-- 日期 時間 PT｜分鐘數｜做了什麼 -->
- 2026-10-27 22:10 PT｜40｜模組 0 診斷：9 題，Q2、Q3、Q5、Q6、Q7 對；Q1 部分對；Q4 筆誤（自行更正）；Q8、Q9 不會；Q4 確認筆誤；M1 熱身（round-trip 組成）答對大方向；M1 預測「n=10⁷ kernel 占幾 %」猜 50%（自述亂猜），實測 3.5–4%；做了 exercises/01-roundtrip.cu 和互動頁
