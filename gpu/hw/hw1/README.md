# GPU HW1：SAXPY, 2D & 3D Matrix addition

> 原文：[spec.md](spec.md)（[Canvas assignment 11810625](https://canvas.uw.edu/courses/1917398/assignments/11810625)；PDF 原檔 [spec.pdf](spec.pdf)，Canvas file 154350654）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-10-20（二）5:59 PM PDT**（Canvas `due_at`、PDF p1「DUE: 20 October 2026, 5:59 PM」、`assignments.md` 三者一致）；lock 12/11 |
| 分數 | 11 分（HW 合計佔總成績 50%；原文沒有寫各部分配分） |
| 繳交方式 | Canvas online upload |
| 要交的東西 | 1. 選擇題 Q1–Q4 和所有「HW Q」的答案，**要附計算過程或理由**<br>2. CUDA host application 原始碼：**只交 `.cu`、`.cpp`、`.h`**，不要交 project／solution 檔和 build 產物<br>3. 4 個 kernel function（printf、SAXPY、2D matrix add、3D grid add）<br>4. CPU vs GPU 結果不一致的紀錄（截圖即可） |

## 學習目標
（PDF p1「Learning Objectives」）
- 使用 L1 投影片的 CUDA Runtime API error checking macro
- 自己管理 host 和 device 的記憶體配置與資料搬移
- 寫使用多維 grid 和 indexing 的 kernel
- 從 host 用多維 execution configuration launch kernel
- 練習 2D／3D 攤平資料的 row-major index 計算
- 在 kernel 裡做範圍邊界檢查
- 在 host 端比對 CPU baseline 和 GPU kernel 的結果，並考慮數值精度差異
- 多練習幾個簡單的多維 CUDA kernel

## 要做什麼
HW1 分兩大部分：(i) 書面問題，(ii) 程式練習（PDF p1「Overview」）。

### Part 1：Questions（PDF p1–p2）
書面或打字作答，**必須寫出過程或理由才給分**。四題都是 vector addition 的 index 計算，選擇題：

| 題 | 在問什麼 |
|---|---|
| Q1 | 每個 thread 算 1 個輸出元素時，thread/block index 對應到資料 index 的式子 |
| Q2 | 每個 thread 算 2 個**相鄰**輸出元素時，第一個元素的 index 式子 |
| Q3 | 每個 block 處理 `2*blockDim.x` 個連續元素、分成兩個 section，所有 thread 先各處理第一個 section 的一個元素，再一起移到第二個 section；求第一個元素的 index 式子 |
| Q4 | 向量長度 8000、每 thread 1 個元素、block 大小 1024，用最少 block 數涵蓋全部輸出時，grid 裡共有幾個 thread |

### Part 2：Programming Exercises（PDF p2–p6）
從一個**新的預設 CUDA Visual Studio solution／project**開始（和 HW0 一樣）。預設範例是固定 `arraySize = 5`、靜態陣列、`addKernel<<<1, size>>>`；這份作業要把它改成動態配置、多維 launch 的版本。

#### 2.1 Host 端錯誤檢查（PDF p3「Error checking on host」）
- 修改範例的 `main()` 和 `addWithCuda()`，所有回傳 `cudaError_t` 的 CUDA 函式都用 L1 投影片的 `checkCuda` macro 包起來。
- macro 放在**獨立的 `.h` 檔**，在 `kernel.cu` 裡 `#include`；之後的作業都會沿用。
- 建 header：VS Solution Explorer 對 project 按右鍵 → Add → New Item → Header File (.h)。

#### 2.2 共通要求（PDF p3–p4「CUDA Kernels」）
- 每個數學 kernel（SAXPY、2D、3D）都要在 host 配置輸入／輸出記憶體，並把資料初始化成已知值；同一組輸入同時給 CPU 循序版和 GPU kernel 用（見 2.7）。
- 在 host 寫 `<<< … >>>` execution configuration 來 launch 每個新 kernel 並傳參數。

#### 2.3 printf kernel（PDF p4）
1. 在 kernel 裡用 CUDA built-in 變數取得 thread ID、block ID，算出 GTID（Globally unique Thread IDentifier）。
2. 用 `printf()` 在**同一行**印出 thread ID（.x）、block ID（.x）、GTID，結尾加 `\n`。
3. Host 端試不同 exec cfg：

   | 設定 | |
   |---|---|
   | a | `<<<1,32>>>` |
   | b | `<<<4,8>>>` |
   | c | `<<<32,1>>>` |
   | d | 每種各跑多次（約 10 次），觀察結果 |
4. 要思考的問題：
   - 結果一致嗎？可預測嗎？
   - block index 和 thread index 的行為看起來有差別嗎？
   - 這對 kernel 裡做的計算有什麼含意？

#### 2.4 SAXPY kernel（PDF p4）
- Single-Precision A times X plus Y：`y = a·x + y`，全部是 32-bit float。`a` 是 scalar，`x`、`y` 是長度 1×N 的向量。BLAS Level-1，O(n)。
- kernel 參數要包含整數 N，用來做 bounds-checking。

  | 測資 | 用途 |
  |---|---|
  | N = 10 | sanity check |
  | N = 1e3 | 放大規模 |
  | N = 1e7 | 還是全部通過嗎？ |

#### 2.5 2D matrix addition kernel（PDF p5）
- `C = A + B`，A、B、C 都是 M×N 的 float 矩陣。
- kernel 參數要包含整數 M、N，每個 thread 做 2D bounds-checking。

  | 測資 M×N | 說明 |
  |---|---|
  | 4×4 | sanity check |
  | 500×500 | 小矩陣 |
  | 3024×4032 | 約 12MP iPhone 影像解析度 |

#### 2.6 3D volume grid addition kernel（PDF p5）
- `C = A + B`，A、B、C 都是 M×N×P 的 float data grid。
- kernel 參數要包含整數 M、N、P，每個 thread 做 3D bounds-checking。
- 用 `dim3` 定義 3D 的 block 和 thread 大小。

  | 測資 M×N×P | 說明 |
  |---|---|
  | 3×3×3 | sanity check |
  | 100³ | 共 1e6 個點 |
  | 1e3³ | 共 1e9 個點；**一定要用 RELEASE build 編** |

#### 2.7 Host-Side Result Verification（PDF p5）
1. 依 Lecture 2，在 host 程式加結果驗證，定量比對 CPU 和 GPU 的同一個計算：
   - 每個 GPU kernel 的計算都要有對應的 CPU 循序版本。
   - 用 tolerance 門檻判斷是否一致，容許數值精度差異。
   - 驗證用 RELEASE build（VS 上方工具列 Debug → Release），否則沒有最佳化，不同 tolerance 下可能看不出差異。
   - **HW Q**：tolerance 設到多少時驗證開始失敗？
   - **HW Q**：三個 kernel 中哪一個 CPU／GPU 結果差異最嚴重？為什麼？
     - 附上觀察到的差異結果，截圖即可。

## 注意事項
- 選擇題和 HW Q **沒附過程或理由不給分**（PDF p1「Questions」）。
- 原始碼只交 `.cu`、`.cpp`、`.h`，不要交整個 project／solution 和 build 產物（PDF p6「SUBMIT」2a）。
- `checkCuda` macro 放獨立 `.h` 檔再 `#include`（PDF p3「Error checking on host」）。
- 用的是**更新版** L1 p55 的 `checkCuda`：第二個參數是標出呼叫函式的字串，少了會出一堆 compile error；更新版投影片在 Files 的「lecture 1 updated」（`gpu/lectures/2026-10-13/notes.md`，[01:12:01]、[01:13:03]）。
- 每個 `malloc()` 都要配一個 `free()`，否則 memory leak（PDF p3「REMINDER」）。
- kernel 要接收資料維度參數並做邊界檢查（PDF p4–p5 各 kernel 小節）。
- 1e9 的 3D 測資和所有結果驗證都要用 RELEASE build（PDF p5）。
- 編譯目標設 `compute_75,sm_75`（T4），平台選 x64；但用 Nsight 除錯要用 Debug build（`gpu/lectures/2026-10-13/notes.md`，[00:43:21]、[00:35:59]、[03:24:03]）。
- kernel launch 是非同步的，複製結果回來前要 `cudaDeviceSynchronize`（`gpu/lectures/2026-10-13/notes.md`，[02:45:07]）。
- 遲交：遲 1 天 -1，之後每 24h 再 -1（`assignments.md`）。滿分只有 11。
- AWS WorkSpaces session 4 小時、stateless，結束前要把檔案存到雲端硬碟（`gpu/lectures/2026-10-06/notes.md` [01:08:06]；`gpu/lectures/2026-10-13/notes.md` [00:04:43]）。

## 和上課內容的關聯
- **Error macro**：L1 updated p55（`gpu/lectures/2026-10-06/notes.md`「重點摘要」CUDA 入門段；L2 更正見 `gpu/lectures/2026-10-13/notes.md`「L1 slide 55 錯誤處理 macro 的更正」）。
- **1D index 和 grid 大小（Q1–Q4、SAXPY）**：L1 p47、p53 的 `gid` 公式和 `blocksPerGrid = (n + threadsPerBlock - 1) / threadsPerBlock`（`gpu/lectures/2026-10-06/notes.md`「和作業 / 考試的關聯」）。
- **2D／3D row-major 攤平**：L2 p9、p14，2D `W*y + x`、3D `W*H*z + W*y + x`；row-major 下 x 移動最快、`dim3` 順序是 (x, y, z)（`gpu/lectures/2026-10-13/notes.md`「資料配置與 index」、「Index space、warp、獨立性」，[01:00:06]、[01:57:00]）。
- **`dim3` 配置與 ceil-div**：L2 p25、p26、p33；p17 的 x／y 寫反，以 p26 為準（[02:06:06]）。
- **邊界檢查**：L2 p17、p22（[02:09:00]）。
- **Explicit memory management**：L2 p24，明確寫 HostToDevice／DeviceToHost，不要用 `cudaMemcpyDefault`（[02:40:16]）。
- **結果驗證與 tolerance**：L2 p37，FP32 用 rtol 1e-5、atol 1e-6（[03:08:37]、[03:09:01]）。
- **printf 輸出順序**：L2 [03:23:07]、[03:31:32]，老師說 kernel `printf` 順序沒有保證、作業會探討。
- **閱讀**：Reading Set #1（PMPP Ch1–2）、#2（Ch3 §1–4 multidimensional grids）。

## 還不確定的地方
- **L2 說的 Gaussian blur 不在 HW1**：老師在 L2 [02:31:35]、[02:34:28] 說作業要做 Gaussian-weighted blur，但 HW1 原文完全沒有 blur，應該是 HW2（`assignments.md` 記錄去年 HW2 是 Gaussian Blur）。L2 notes 的待釐清第 1 點可以當作已解決：HW1 沒有 blur。
- **printf 題目確定在 HW1**：L2 [03:36:02] 老師不確定 printf 練習在 HW0 還是 HW1；原文 p4 有「printf kernel」，所以在 HW1，而且算在「4 kernel functions」裡。
- **「4 kernel functions」的組成**：原文 p6 說交 4 個 kernel，p3 說實作「several new kernels」。依原文段落推斷是 printf、SAXPY、2D、3D 四個；原文沒有明列。
- **printf 小節的「questions to consider」要不要寫進答案**：原文 p6 要交「questions … including those marked as HW Q」，printf 的三個問題沒有標 HW Q，原文沒講是否要書面回答。
- **1e3³ 測資的記憶體**：1e9 個 float 每個陣列約 4 GB，A、B、C 三個約 12 GB；T4 約 16 GB（`gpu/lectures/2026-10-13/notes.md`「重點摘要」第 2 點）。原文只提醒要用 RELEASE build，沒有講記憶體或 host 端配置的限制。
- **配分**：原文沒有寫 Questions 和 Programming 各佔幾分。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-10-20 | 第一次整理 |

GPU 課禁止用 AI 產生作業解答
