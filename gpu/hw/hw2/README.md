# GPU HW2：Parallel performance theory, Gaussian blur kernels and more!

> 原文：[spec.md](spec.md)（[Canvas assignment 11810626](https://canvas.uw.edu/courses/1917398/assignments/11810626)；PDF 原檔 [spec.pdf](spec.pdf)，Canvas file 154697826；附檔在 Canvas Files 的 [Homeworks/Hw2_materials](https://canvas.uw.edu/courses/1917398/files/folder/Homeworks/Hw2_materials)）。摘要由排程「作業說明」整理，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | **2026-10-27（二）5:59 PM PDT**（Canvas `due_at` 2026-10-28T00:59:59Z、PDF p1「DUE: 27 October 2026, 5:59 PM」、`assignments.md` 三者一致）；lock 12/13 |
| 分數 | 12 分（HW 合計佔總成績 50%；原文沒有寫各部分配分） |
| 繳交方式 | Canvas（原文只寫「SUBMIT」，沒寫方式；HW1 是 online upload，HW2 的 submission type 這次沒確認） |
| 要交的東西 | 1. 選擇題 Q1–Q3、Performance Theory P1–P2、所有「HW Q」和 QUESTION 的答案，**要附過程和理由**<br>2. CUDA host application 原始碼：**只交 `.cu`、`.cpp`、`.h`**，不要交 project／solution 檔和 build 產物<br>3. CUDA kernel functions（3 個 blur kernel；可以和 host code 放同一個 `.cu`）<br>4. 模糊後的測試影像 #1、#2、#3<br>5. 各 blur kernel 版本的計時結果<br>6. CUDA kernel 除錯視窗的截圖（Lanes + Warp Info，兩組）<br>7. 全部測試影像 × global／shared kernel 的 NCU CLI profiling 結果，附算出的 kernel execution time 和 instruction intensity<br>8. Extra credit（選做）：host CPU 循序 blur 和各 GPU kernel 的計時比較表；global vs shared kernel 的理論 AI |

## 學習目標
（PDF p1「Learning Objectives」）
- 練習套用 parallel performance theory 的概念
- 實作幾種 2D Gaussian blur CUDA kernel
- 用 device shared memory 存放和讀取 blur filter 係數
- 用 Nsight VSE CUDA debugger 檢查 kernel 執行中各 thread 的 breakpoint
- 用 Nsight Compute CLI profile kernel
- 用 host 計時函式量 host 和 device 的執行時間
- 比較理論效能估計和實測值

## 要做什麼
HW2 分兩大部分：(i) 書面問題，(ii) 程式練習（2D CUDA grid、shared memory、Nsight VSE debugger、Nsight Compute profiler）（PDF p1「Overview」）。

### Part 1：Questions（PDF p1–p2）
書面或打字作答，**必須寫出過程或理由才給分**。三題選擇題：

| 題 | 在問什麼 | 選項 |
|---|---|---|
| Q1 | 1000 個 block、每 block 512 thread，宣告成 shared memory 的變數在整個 kernel 執行期間會產生幾份 | 1／1,000／512／512,000 |
| Q2 | Tiled matrix-matrix multiplication 用 32×32 tile，A、B 的 memory bandwidth 用量比 non-tiled 減少到多少 | 1/8／1/16／1/32／1/64 |
| Q3 | 上課的 tiled 單精度 MM kernel，tile 32×32、DRAM burst 128 bytes，一個 block 載入一個 A tile 會送來幾個 DRAM burst | 16／32／64／128 |

### Part 2：Performance Theory Questions（PDF p2–p3）

#### P1：Arithmetic intensity
- 定義：`AI := computations / memory accesses = FLOPs / BYTE`（Lecture 3）。
- 對下面 3 個 ML operation 各做一張表，欄位：`algorithm | FLOPs | Mem bytes | AI`。
- 先寫出採用的演算法式子，**每個計算項和記憶體存取項都要分開定義**，不能只給總 FLOPs 和總 Mem_bytes；分子分母都要拆成各項。
- 只算 global memory（DRAM：HBM、GDDR）的讀和寫；register 和 cache 的流量當作免費。預設 FP32。
- 約定：transcendental（exp、tanh、erf、sqrt）= 4 FLOP；FMA = 2 FLOP。

| | ML Operation | 變數 |
|---|---|---|
| a | matrix transpose | N×N 矩陣 |
| b | SoftMax，3-pass，unfused | （原文沒指定） |
| c | Convolution | 影像 W×H、kernel size K、channels C、batch size N |

#### P2：Roofline
- 查下面兩張卡的 peak compute 和 peak global memory bandwidth，算 ridge point，畫 roofline。
- 把 P1 的 3 個 AI 畫到**每張** roofline 上；AI 式子裡的變數要代具體值，並寫出用了哪些值。換不同的值可能讓 kernel 換 regime（例如從 memory-bound 變 compute-bound）。
- 每張圖標出每個 kernel 落在哪個 regime：(a) memory-bound、(b) transitional、(c) compute-bound。

| | GPU |
|---|---|
| a | Turing Quadro RTX 6000（TU102） |
| b | Hopper H100 SXM5 |

### Part 3：Programming Exercises（PDF p3–p9）

#### 3.1 Preliminaries（步驟 1–4，PDF p3–p4）
1. 開一個新的預設 CUDA Visual Studio solution／project（同 EX1、HW1），編譯目標設 `sm_75`（T4）。
2. Solution Explorer 對 `kernel.cu` 按右鍵 → Remove → Delete，永久刪掉。
3. 從 Canvas Files/Homeworks/HW2_Materials 下載到 project 資料夾：

   | 檔案 | 說明 |
   |---|---|
   | `hw2_starter.cu` | starter code |
   | `hw2_testimage1.png` | 240×240 |
   | `hw2_testimage2.png` | 512×512 |
   | `hw2_testimage3.png` | 850×850 |
   | `hw2_testimage4.png` | 4032×3024（原文寫 4023，是筆誤；實際檔頭 4032×3024，見「本機檔案核對」） |
   | `stb_image.h`、`stb_image_write.h` | 影像讀寫 |
4. 對 project 按右鍵 → Add → Existing Item，加入 `hw2_starter.cu`（檔案總管可能要手動打 `C:\` 才到得了 C 槽根目錄）。

#### 3.2 CUDA Blur Kernels（步驟 5，PDF p4–p5）
照 L1、L2 的內容，完成 `hw2_starter.cu` 註解標出的工作。
- **讀影像**：
  - 用提供的 STB header 和 starter 裡的範例片段。
  - 輸入是 **8-bit 單色**，host 和 device 的影像型別都用 `unsigned char`。
  - kernel 內累加 pixel 要用 32-bit `int` 避免 overflow，寫輸出時再轉回 `uchar`。
  - 檢查 pixel bit depth：檔案總管 Properties → Details 的寬、高、bit depth 要和 `stb_load()` 回傳的一致。
  - 輸入／輸出**檔案路徑**多半和 starter 寫的不同，要改成實際存放的位置。
- **Blur kernel**：
  - 用 L2 的 2D row／col thread index。
  - 做邊界檢查，不存取超出範圍的記憶體。
  - 每個 thread 只寫一個輸出 pixel。
  - 提示：先把 L2 投影片的一般（非 Gaussian）blur 做出來，用 blur width = 10 測試，效果會很明顯。
  - 用提供的 **9×9 Gaussian filter 係數陣列**（float）；係數乘上輸入 pixel 後**四捨五入成 int**。
  - Gaussian 版本的正規化**改成除以用到的係數總和**，不是除以加總的 pixel 數。
- **實作 3 個版本**：

  | 版本 | 係數放哪裡 |
  |---|---|
  | i | 只用 global device memory（GMEM） |
  | ii | **static** shared memory（SMEM） |
  | iii | **dynamic** shared memory，從 host 指定 |

  - 需要多一個 kernel 參數，把係數陣列傳到 device global memory。
  - SMEM 版本：每個 block 的前 N 個 thread 一起把係數複製進 shared memory，**之後要 `__syncthreads()`**。
  - 參考投影片的範例和 PMPP 課本。
- **Extra credit**：global memory kernel vs shared memory kernel 的理論 AI 計算。

#### 3.3 Host-side Code Execution Timing（步驟 6–7，PDF p5）
- `#include` Windows profiling API（`profileapi.h`），在 starter 註解標的位置加 high-performance timer 的變數、start、stop。用法見 Lecture 3 投影片。
- AWS WorkSpace 上 header 在 `C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\um\profileapi.h`。
- 對測試影像 1–4 各跑一次計時（**不要在 debugger 裡跑**）：
  - 比較 DEBUG 和 RELEASE build 的時間差。
  - 每個 timer、每張影像的結果都要存下來。

#### 3.4 Nsight VSE Debugger（步驟 8–13，PDF p6–p7）
- 背景（步驟 8）：同時跑很多 warp，單步執行會一直在 thread 之間切換。三種處理方法：
  - a. host 用 `your_kernel_function<<<1,1>>>(...)` 只 launch 一個 thread（但看不到同步、race、deadlock 等多 thread 問題）。
  - b. kernel 裡加 `if (threadIdx.x == brk_value) { … }`，breakpoint 設在大括號裡。
  - c. Conditional Breakpoint 指定 blockIdx／threadIdx（老師說他自己用起來不穩）。
- 步驟 9：在其中一個 blur kernel 的**相鄰兩行**設 breakpoint；launch 設定要有足夠的 block 和 thread 涵蓋整張影像。
- 步驟 10：Extensions → Nsight → Start CUDA Debugging（Next-Gen）。**啟動前要先成功 build DEBUG**，否則 attach 不上。
- 步驟 11：停在 kernel 裡之後：
  - 看 col、row（或 blockIdx.x/y、threadIdx.x/y）。
  - 按 Step Over（F10）。多半會停在同一行，這不是錯誤；再看一次 col、row，**大概**會不同（device 上的執行是非確定性的）。
  - 再按一次 F10，一樣可能不前進但 row、col 改變：因為很多 thread 都在跑同一行。
- 步驟 12：Extensions → Nsight → Windows 打開除錯視窗：
  - **Lanes**：除了測試影像 3、4，幾乎都是完整的 warp（32 thread）。
  - **Warp Info**：顯示目前在 SM 上執行的每個 warp 的所有 thread。
    - **QUESTION**：有幾個 warp 在跑？用 Tesla T4 的硬體資源解釋這個數字。
  - 在 Lanes 點一個 thread、在 Warp Info 點一個 warp，切到那個 thread，看 col、row 的變化。
  - **截圖 1**：`hw2_testimage1.png`（240×240）除錯中，Lanes 和 Warp Info 兩個視窗都開著。
- 步驟 13：停止除錯，把 launch 改成 `<<<1,1>>>`，重新除錯停在 breakpoint，打開 Lanes 和 Warp Info，**截圖 2**。

#### 3.5 Nsight Compute CLI Profiling（步驟 14–26，PDF p7–p9）
- NCU 只支援 Volta GV100 以後（CC 7.0+）；更舊的卡用 `nvprof`（步驟 14）。
- 步驟 16：**Release、x64 build**，`main()` 裡只 launch **一個** blur kernel，用 **global-memory 版本**。profile 一律用 Release build。
- 步驟 17–18：用**系統管理員**開 command prompt（右鍵 → Run as Admin），`cd` 到 Release 輸出資料夾。
- 步驟 19：執行（kernel 名稱和 exe 名稱換成自己的）：
  ```
  ncu -k <your_kernel_function_name> --metrics smsp__cycles_elapsed.sum,smsp__cycles_elapsed.sum.per_second,smsp__inst_executed.sum,dram__sectors_read.sum,dram__sectors_write.sum,dram__bytes.sum,sm__cycles_elapsed.avg,sm__cycles_elapsed.avg.per_second,sm__inst_executed.sum,dram__bytes_read.sum,dram__bytes_write.sum,gpu__cycles_elapsed.sum,gpu__time_duration.sum,gpu__time_duration.avg ./<your_host_application_name>.exe
  ```
  原文 p8 附了一份範例輸出（`gaussBlurKernel_globalmem`、`HW2_starter_img3.exe`）。
- 步驟 21–23：改 host code 分別用 4 張測試影像，**各做一個 Release build**，命名例如 `hw2_rel_global_img1.exe`、`hw2_rel_global_img2.exe`，避免重 build 時被覆蓋；每個都跑 NCU，收集全部輸出。
- 步驟 24：對 **static shared-memory** blur kernel 重複以上步驟。
- 步驟 25：共 **8 次** profiling（4 張影像 × global／shared），每次算：

  | 指標 | 公式 | 單位換算 |
  |---|---|---|
  | kernel execution time | `smsp__cycles_elapsed.sum / smsp__cycles_elapsed.sum.per_second` | nanosecond → second |
  | kernel instruction intensity | `smsp__inst_executed.sum / dram_bytes.sum` | Kbyte → byte |
- 步驟 26：
  - **HW Q**：shared mem 版和 global mem 版的 kernel execution time 為什麼不同？從記憶體類型的性質想。
  - **HW Q**：根據量到的 kernel execution time、instruction intensity，以及相關的記憶體和運算操作，推論 naive 和 tiled 的差異。

## 注意事項
- 選擇題、P1、P2、HW Q **沒附過程或理由不給分**（spec.md p1「Questions」；p9「SUBMIT」1）。
- P1 每個計算項和記憶體項都要個別定義，不能只給總數；只算 global memory 流量（spec.md p2「P1」）。
- P1 約定：transcendental = 4 FLOP、FMA = 2 FLOP（spec.md p3）。
- P2 要寫出代入的變數值（spec.md p3「P2」）。
- 編譯目標 `sm_75`（spec.md p3「Preliminaries」1a）。
- 影像是 8-bit 單色，`unsigned char`；kernel 內累加用 32-bit `int`（spec.md p4「CUDA Blur Kernels」5a.ii）。
- 檔案路徑要改成自己實際存放的位置（spec.md p4，5a.iv）。
- Gaussian 係數乘完四捨五入成 int；正規化除以係數總和（spec.md p5，5b.vi–vii）。
- SMEM 版本複製完係數一定要 `__syncthreads()`（spec.md p5，5c.v）。
- 計時不要在 debugger 裡跑；DEBUG 和 RELEASE 都要量（spec.md p5，步驟 7）。
- 啟動 Nsight debugger 前要先 build 好 DEBUG，否則 attach 失敗（spec.md p6，步驟 10b）。
- NCU profiling 一律用 Release、x64，command prompt 要 Admin；每張影像各一個 exe，命名分開避免覆蓋（spec.md p7–p8，步驟 16–21）。
- 原始碼只交 `.cu`、`.cpp`、`.h`，不要交 project／solution 和 build 產物（spec.md p9「SUBMIT」2a）。
- 模糊後的影像只要交 #1、#2、#3（spec.md p9「SUBMIT」4）。
- 遲交：遲 1 天 -1，之後每 24h 再 -1，第 5 天累計 -6；第 10 天再 -2，之後每 5 天 -1（`assignments.md`）。滿分 12。
- 用 Nsight 除錯要用 Debug build；`--resource-usage` 可以列出每個 kernel 用的 register 和 shared memory（`gpu/lectures/2026-10-13/notes.md`「重點摘要」13，[03:25:00]、[03:32:01]）。
- AWS WorkSpaces session 4 小時、stateless，結束前把檔案存到雲端硬碟（`gpu/lectures/2026-10-06/notes.md` [01:08:06]；`gpu/lectures/2026-10-13/notes.md` [00:04:43]）。

## 和上課內容的關聯
- **Blur kernel**：L2 p19–p23 的 box blur，每個 thread 讀鄰域、寫一個 pixel，兩層邊界檢查（`gpu/lectures/2026-10-13/notes.md`「重點摘要」6）。老師說作業要做 2D Gaussian-weighted blur，不是權重全 1 的版本（同檔「老師強調的地方」Index space 段，[02:31:35]、[02:34:28]）；每個 thread 的計算量隨 blur size 增加，之後會正式化成評估指標（[02:37:00]）。
- **2D index 和邊界／warp divergence**：L2 p17–p18（62×76 影像、16×16 block 的例子）（同檔「重點摘要」5，[02:09:00]）。
- **`__shared__` qualifier**：L2 p32–p36（同檔「重點摘要」9）。
- **T4 硬體資源（Warp Info 的 QUESTION）**：L2 p38–p44，40 個 SM，每個 SM 最多 16 個 block、1024 個 thread，每個 processing block 16 個 FP32 core（同檔「重點摘要」11，[03:14:01]）；occupancy 例子見 p52（「重點摘要」12）。
- **Nsight VSE**：L2 p54 demo，Warp Info、Lanes、切換 thread（同檔「重點摘要」13，[03:25:00]–[03:27:01]）。
- **Host 端流程**：L2 p24–p27（同檔「重點摘要」7）。
- **Roofline**：L1 老師提過 roofline，課表排在 Week 3（`gpu/lectures/2026-10-06/notes.md`「名詞解釋」）。
- **AI、roofline、Windows high-performance timer、tiled MM（Q2、Q3）**：原文說在 Lecture 3（10/20）。repo 裡還沒有 L3 筆記（`gpu/lectures/` 只有 10-06、10-13），講義 `Au26_GPU-Compute_Lecture3.pdf` 和錄影已在 10/21 晨報記錄。
- **閱讀**：Reading Set #2 PMPP Ch3 §1–4（含 image blur）、Ch4 §1–4（`gpu/lectures/2026-10-13/notes.md`「和作業 / 考試的關聯」）。

## 還不確定的地方
- **P1 要求「use chatbot assistance」和 AI 政策**：原文 p2 要大家用 chatbot 找演算法的簡單表示式；BOOTSTRAP 記的 GPU 課 AI 政策是不可以用 AI 產生作業解答。原文看起來只允許用 chatbot 查演算法式子，FLOPs／bytes／AI 的推導還是要自己做；界線原文沒講，有疑慮可以在 Teams 問。
- **SoftMax 的變數**：P1b 沒有說輸入大小（例如長度 N 或 N×D），要自己定義。
- **P2 第一張卡**：題目是 Quadro RTX 6000（TU102），不是課程用的 T4；Lanes 和 Warp Info 的問題才是 T4（原文 p7 寫「Tesla T4」）。
- **HW Q 26b 的「naive vs tiled」**：這份作業的 kernel 是 global vs shared（係數放 SMEM），沒有 tiled 版本。這題可能沿用往年 tiled MM 的題目，或「tiled」就是指 shared memory 版本；原文沒講清楚。
- **Lanes 的說明**：原文 p7 說「除了測試影像 3、4，幾乎都是完整 warp」。依 block 大小而定，原文沒說預期的 block 設定。
- **NCU 範例輸出是舊的**：p8 範例路徑是 `C:\Temp\AUT22_GPUCompute`、日期 2022-Oct-17，只列了 6 個 metric；步驟 19 的指令有 14 個 metric。照步驟 19 的指令做。
- **步驟 13c 是空的**：原文 p7 只有「c.」沒有內容。
- **步驟 25b 的 `dram_bytes.sum`**：metric 實際名稱是 `dram__bytes.sum`（兩個底線），原文少一個底線。
- **Dynamic SMEM 版本要不要 profile**：步驟 24 只說重做 static shared-memory 版本，所以 8 次 profiling 不含 dynamic；計時（SUBMIT 5「GPU CUDA blur kernel variants」）看起來 3 個版本都要。
- **計時要量哪些 timer**：已解決，看 starter 註解：timer #1 = 配置 device 記憶體 → H2D → kernel → D2H（整段）；timer #2 = 只含 kernel launch → `cudaDeviceSynchronize()`；timer #3（Extra credit）= host 循序 blur。
- **繳交方式和配分**：原文沒寫 Canvas submission type，也沒寫各部分佔幾分。

## 本機檔案核對（2026-10-26）
來源資料夾 `D:\Repos\Au26_GPU\Au26_GPUCompute\HW2\`（使用者從 Canvas 下載）。starter 已複製進 repo：[hw2_starter.cu](hw2_starter.cu)（原樣，未修改）。測試影像（共約 9 MB）和 stb header 沒複製進 repo，Canvas Files/Homeworks/Hw2_materials 可再下載。
- **PDF**：`Homework #2 (HW2) - Au26 - GPUCompute.pdf` 是 259794 bytes，與 spec.md 記的 Canvas file 154697826 大小相同，與 repo 的 `spec.pdf` 逐 byte 比對相同（`cmp`），沒有新增資訊。PDF 沒有密碼（Google Docs 匯出，檔頭無加密欄位）；Read 工具曾誤報 password-protected，改用 `spec.md` 的抽出文字。
- **測試影像實測（PNG 檔頭）**：全部 8-bit grayscale（color type 0）、非 interlaced。

  | 檔案 | 寬×高 |
  |---|---|
  | `hw2_testimage1.png` | 240×240 |
  | `hw2_testimage2.png` | 512×512 |
  | `hw2_testimage3.png` | 850×850 |
  | `hw2_testimage4.png` | **4032×3024**（原文寫 4023×3024，筆誤） |
- **STB 版本**：`stb_image.h` v2.16。
- **Starter 裡的 timer 位置**：timer #1 在配置 device 記憶體之前開始、D2H 之後停；timer #2 夾住 kernel launch 到 `cudaDeviceSynchronize()`；timer #3（Extra credit）夾住 host 循序 blur。
- **Starter 直接編不過／要改的地方**（沒有實際編譯，是讀程式碼的判斷）：
  1. `#include "../util/stb_image.h"`：路徑指向上一層的 `util/`，但檔案在同一個資料夾，要改成 `"stb_image.h"`。
  2. `int imgSize = x_cols * y_rows * sizeof(uchar);`：`uchar` 不是標準型別，改 `unsigned char`（或自己 `typedef`）。
  3. `cudaStatus` 沒宣告就使用，要自己加 `cudaError_t cudaStatus;`。
  4. `h_imgOut` 沒宣告，要自己 malloc host 輸出 buffer。
  5. 檔名路徑是 `c:/Temp/AUT22_GPUCompute/dat/...`（去年的），要改成本機路徑；輸出檔名 `hw2_outimage1.png` 要依影像／kernel 版本分開命名。
  6. `goto Error` 會跳過後面 `const char imgFileOut[] = ...` 這類有初始化的宣告，C++ 會報 jump bypasses initialization。宣告集中放在 `main()` 最前面。
  7. 開頭 `// #include your error-check macro header file here`：要自己寫 error-check macro（含 `goto Error`），HW1 應該有現成的。
  8. 錯誤訊息字串寫 `addKernel launch failed`，是複製自 VS 預設範本，可改成自己 kernel 名稱。
  9. `stbi_load(..., 1)` 強制 1 channel；最後 `stbi_write_png(..., x_cols * n_pixdepth)` 的 stride 用的是檔案原本的 channel 數，這 4 張都是 1 channel 所以剛好對，換彩色圖會錯。
- **Starter 的 kernel 註解**：
  - `// blur kernel #1 - global memory only`
  - `// blur kernel #2 - device shared memory (static alloc)`
  - `// blur kernel #2 - device shared memory (dynamic alloc)`（第二個也寫 #2，應該是 #3 的筆誤）
  - `BLUR_FILT[81]` 是 host 端 `const float` 陣列，kernel 不能直接讀，所以要多一個 kernel 參數把它複製到 device（步驟 5c.iv）。
  - 正規化除數是「實際用到的係數權重總和」（步驟 5b.vii）；邊緣 pixel 只用到落在影像內的係數，除數要跟著只加這些係數。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-10-21 | 第一次整理 |
| 2026-10-26 | 補「本機檔案核對」：starter、影像尺寸（image4 實為 4032×3024）、starter 要修的地方；timer 位置已確認 |

GPU 課禁止用 AI 產生作業解答
