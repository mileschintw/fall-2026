# GPU HW0：Preliminaries and Refreshers

> 原文：[spec.md](spec.md)（PDF 原檔 [spec.pdf](spec.pdf)，[Canvas file 154009274](https://canvas.uw.edu/courses/1917398/files/154009274)，Files → `course files/Homeworks`）。HW0 在 Canvas Assignments 裡沒有對應項目，排程「作業說明」抓不到，這份是 2026-10-20 手動整理的，有疑問以原文為準。

| 項目 | 內容 |
|---|---|
| 截止 | 無。L1 建議在 L2（10/13）前做完（`gpu/lectures/2026-10-06/notes.md`，p62、[00:33:00]、[02:38:03]） |
| 分數 | 0 分，不計分（L1 [02:38:03]；Canvas 上沒有這份作業） |
| 繳交方式 | 不用交 |
| 要交的東西 | 無。有問題到 Teams 的 Hw0 Discussion channel 問（L1 [02:38:03]） |

## 學習目標
（PDF p1「Learning Objectives」）
- 熟悉 AWS WorkSpaces virtual desktop environment（VDE）
- 熟悉 Visual Studio 2026 IDE：建立並 build VS CUDA solution／project，使用 debugger，設中斷點，查看變數和記憶體內容
- 認識 Visual Studio 開發和 CUDA API 的主要參考資源
- 第一次看 GPU host application 的基本結構：用 CUDA Runtime API 和簡單的 device kernel 做 vector addition（L1 內容）
- 用 NVCC 從命令列編譯 CUDA 程式，試用編譯選項
- 用 CUDA binary tools 查看編譯產物
- 複習 C 的指標和陣列

開發環境（PDF p1「Development Resources」）：Visual Studio 2026 Community（≥ 2026 年 9 月的 18.10.2 版）、CUDA Toolkit ≥ 13.4.2。

## 要做什麼
步驟編號沿用原文（1–58）。

### 1. AWS WorkSpaces Applications VDE（步驟 1–5，PDF p1–p2）
| 步驟 | 內容 |
|---|---|
| 1 | 第一封信「Start accessing your apps using Amazon AppStream 2.0」（from no-reply）有臨時密碼，第一次登入要設新密碼。**常在垃圾郵件或垃圾桶** |
| 2 | 第二封信「Amazon WorkSpaces Applications: New apps available」（from no-reply）有登入連結 |
| 3 | 用信裡的連結登入，選 **Desktop**。開機器要等幾分鐘 |
| 4 | 登入後的歡迎視窗會顯示本週已用時數 |
| 5 | 結束時先把檔案存到 VDE 以外的地方，再點右上角使用者名稱 → **Log Out**，釋放資源 |

使用限制：
- **每週最多 15 小時**，用完要等下一週（步驟 2b）
- **單一 session 最長 4 小時**，結束時 instance 會被銷毀，資料全部消失。本週剩下的時數不到 4 小時的話，session 會更早結束。結束前 10、5、2 分鐘會跳提醒（步驟 4）

### 2. Visual Studio 2026 Usage（步驟 6–18，PDF p2–p3）
- 從工作列左邊的 VS 圖示（紫色）打開 → Create a new project → 語言選 **CUDA** → **CUDA 13.x Runtime** → Next
- 位置改成 `C:\Au26_GPU`；取消勾選「Place solution and project in the same directory」
  - Solution：`Au26_GPUCompute`（之後整學期的 project 都放在這個 solution 裡）
  - Project：`EX1_vecadd_cudart`
- 確認 `.sln`（solution）和 `.vcxproj`（project）的位置；project 是 solution 的子資料夾
- 讀懂整份 `kernel.cu`（vector add 的 host 和 kernel 程式，只用到 L1 教的東西）。熟悉 Solution Explorer；對 project 按右鍵 → Properties 可以改編譯和連結選項
- Build → Build Solution，Output 視窗應該顯示 `Build: 1 succeeded, 0 failed, 0 up-to-date, 0 skipped`

### 3. Visual Studio Debugging（步驟 19–38，PDF p3–p5）
- 在 `kernel.cu` 第 **11、17、29、46、66** 行設中斷點；在第 17 行的中斷點按右鍵看 Conditions… 選項
- 用 Local Windows Debugger 執行，接著用 Continue、F10（Step Over）一步一步跑
- Debug → Windows → **Memory 1** 和 **Immediate**：
  - 在 Immediate 輸入 `a`、`&a[0]`，比較兩個位址
  - 把 `a` 的位址貼到 Memory 1，切成 4-byte integer、Signed Display，看第 18 行初始化前後的值
  - 在 `addWithCuda()` 裡看 `dev_a` 和 `&dev_a`，到第 66 行再看一次
- 跨過第 29 行的 `printf` 前後，各看一次 debug console（紫色圖示）
- 用紅色方塊 Stop Debugging 結束

原文要你想的問題：
| 步驟 | 問題 |
|---|---|
| 22 | 為什麼程式停在 `main()` 開頭，而不是第一個中斷點？ |
| 22b | 為什麼 `addKernel` 裡第 11 行的中斷點不見了？ |
| 33b | 為什麼 `&dev_a` 沒變，`dev_a` 卻變了？ |

### 4. CUDA Compilation with NVCC（步驟 39，PDF p5–p6）
- 從工作列的黑色命令提示字元圖示打開 VS developer command prompt，`cd` 到 `EX1_vecadd_cudart`（`kernel.cu` 所在的資料夾）
- 執行 `nvcc -o vecadd kernel.cu -run`，再直接執行 `vecadd`，輸出應該和 VS 裡一樣
- 用 File Explorer 確認多出 `vecadd`（執行檔）、`vecadd.exp`、`vecadd.lib`

### 5. First Look at CUDA Binary Tools（PDF p6）
- 說明：nvcc 把 host 和 device 的部分分開編譯。`.cubin` 是 GPU 執行檔（ELF 格式），內含特定架構（例如 Turing）的 SASS 和 metadata。平常會嵌在 host 執行檔裡，也可以單獨產生，再用 `cuobjdump` 查看，或用 Driver API 在 runtime 載入
- 要跑的指令：

| 指令 | 作用 |
|---|---|
| `cuobjdump -lptx vecadd.exe` | 列出嵌入的 PTX section |
| `cuobjdump -lelf vecadd.exe` | 列出嵌入的 SASS（ELF）section |
| `cuobjdump --dump-ptx vecadd.exe` | 輸出 PTX |
| `cuobjdump --dump-sass vecadd.exe` | 輸出 SASS |

### 6. Refresher: C Pointers and Arrays（步驟 40–58，PDF p6–p8）
把 host 端的陣列 `a`、`b`、`c`（第 18–20 行）改成指標，每改一步就用 `nvcc -o addvec kernel.cu` 重編、執行 `addvec`，回答原文的「Why?」：

| 步驟 | 改動 | 要回答 |
|---|---|---|
| 41–44 | 註解掉第 18–20 行，改成 `int* a = 0;`（`b`、`c` 一樣）；VS Rebuild | 為什麼還能 build 成功？（44a） |
| 45–46 | 用 nvcc 重編、執行 | 為什麼執行時出現錯誤？（46a） |
| 47–50 | 改成 `(int*)malloc(arraySize * sizeof(int))` | 現在輸出什麼？為什麼？（50a） |
| 51–53 | 加上原文的 `for` 迴圈，用 `*pa++`、`*pb++` 填值（warning 先不管） | 現在輸出什麼？為什麼？（53a） |
| 54–56 | 把 `main()` 裡 `addWithCuda()` 之後的 `printf` 換成原文那行（印出 `a`、`b`、`c` 各 5 個元素） | 現在輸出什麼？為什麼？（56a） |
| 57–58 | 也可以在 VS 用 Rebuild Solution，再用 Local Windows Debugger 執行 | 確定懂每一步：語法，以及為什麼指標可以取代陣列 |

### 7. CUDA Host Runtime API：Device Query（PDF p8–p9）
寫一個 host 程式（靜態連結 Runtime API），查詢系統上所有 CUDA device。原文給了 starter 骨架：`#include "cuda_runtime.h"`，`main()` 裡依序 initialize → 取 device 數 → 對每個 device：select → driver/runtime 版本 → device properties → 印出來。

要用的 API：`cudaInitDevice()`、`cudaGetDeviceCount()`、`cudaSetDevice()`、`cudaDriverGetVersion()`、`cudaRuntimeGetVersion()`、`cudaGetDeviceProperties()`。

要印出的 `cudaDeviceProp` 欄位：

| 欄位 | 欄位 |
|---|---|
| `l2CacheSize` | `maxThreadsPerMultiProcessor` |
| `major`、`minor`（compute capability） | `multiProcessorCount` |
| `maxBlocksPerMultiProcessor` | `name[256]` |
| `maxGridSize[3]` | `regsPerBlock` |
| `maxThreadDim[3]`（實際欄位名是 `maxThreadsDim`，見「還不確定的地方」） | `regsPerMultiprocessor` |
| `maxThreadsPerBlock` | `sharedMemPerMultiprocessor` |
| `totalGlobalMem` | `warpsize`（實際欄位名是 `warpSize`） |

參考：https://docs.nvidia.com/cuda/cuda-runtime-api/cuda_runtime_api/apis.html

### 8. NVIDIA-SMI basics（PDF p9–p10）
在 x64 developer command prompt 執行 `nvidia-smi`，看 driver 版本、CUDA 版本、GPU 型號等等。文件：https://docs.nvidia.com/deploy/nvidia-smi/index.html

## 注意事項
- **每週 15 小時、單一 session 4 小時**，session 結束資料全部消失；結束前存到 Google Drive 或 OneDrive，再 Log Out（spec.md 步驟 2b、4、5；L1 [01:08:06]）。
- L2 [00:03:11]：把 Google Drive／OneDrive 連到 AWS instance 的功能還不能用，要等 UW IT 核准；目前用瀏覽器上傳到雲端硬碟，再 Disconnect（`gpu/lectures/2026-10-13/notes.md` [00:04:43]）。
- AWS 密碼和 NetID 密碼是分開的（L1 [01:02:01]）。
- 出現「no streaming resources」時，等 5–10 分鐘再試。試幾次還不行，就到 Teams 的 AWS_Info_Issues channel 貼時間、嘗試次數和錯誤截圖（L1 [01:03:04] [01:04:00]）。
- 中斷點的行號是預設 `kernel.cu` 的行號（spec.md 步驟 19）；改過程式碼之後行號會跑掉。
- 第 51 步的程式碼會出現 warning，原文說先不管（步驟 52b、55b）。
- 原文 PDF 的 `cuobjdump -–dump-ptx` 是「hyphen + en dash」，直接複製貼上會失敗，要自己打成 `--dump-ptx`、`--dump-sass`。
- HW1 也要從「新的預設 CUDA VS project」開始，做法和這份一樣（`gpu/hw/hw1/README.md`）。

## 和上課內容的關聯
- L1（`gpu/lectures/2026-10-06/notes.md`）：重點摘要 #3「AWS WorkSpaces VDE」（p15–p16、p61）；#11「HW0」（p62）；p49 常見 build error、p51 host 樣板、p52 單一 `.cu` 檔、p55 `checkCuda`；[02:28:04] HW0 是 GPU 的 hello world（device query）；[02:39:00] VS 裡看得到 CUDA runtime project 就代表環境正常。
- L2（`gpu/lectures/2026-10-13/notes.md`）：重點摘要 #2「Demo：AWS WorkSpaces 上的 Visual Studio」；[03:01:00] HW0 device query 查到的就是 block／thread／register／shared memory 的資源限制；[03:13:00] 在 AWS 上查到的 compute capability 是 7.5（T4）。L2 也講了 L1 p58–p60 的編譯流程和 fatbin／`cuobjdump`，對應這份第 5 節。
- 閱讀：Reading Set #1 = PMPP Ch1–2，對應 L1 和 HW0（`gpu/assignments.md`）。

## 還不確定的地方
- **欄位名稱拼錯**：原文 p9 寫 `maxThreadDim[3]` 和 `warpsize`，CUDA 的 `cudaDeviceProp` 實際欄位是 `maxThreadsDim[3]` 和 `warpSize`。照原文打會編譯失敗。
- **Visual Studio 和 CUDA 版本**：原文寫 VS 2026 ≥ 18.10.2、CUDA Toolkit ≥ 13.4.2；L2 notes「還要釐清的問題」第 9 點記錄投影片和逐字稿的說法不一致，實際版本以 AWS 上為準。
- **printf 練習**：L2 [03:36:02] 老師不確定 printf 練習在 HW0 還是 HW1。這份原文沒有 printf kernel 的題目，確定在 HW1（`gpu/hw/hw1/README.md`）。
- **Task 0 和 HW0**：L1 [00:57:05] 老師說 Canvas 的 task zero 就是 HW0；但 Canvas 上的 Task 0 是 Teams 自我介紹（`gpu/hw/task0/README.md`），兩者是不同的東西，都不計分。
- **Teams Hw0 Discussion channel 還沒讀過**（`digests/semester-to-date/2026-10-18-brief.md`），裡面可能有老師或 TA 的補充。

## 改版紀錄
| 日期 | 變動 |
|---|---|
| 2026-10-20 | 第一次整理（手動存，Canvas file updated_at 2026-10-07T01:44:56Z） |

GPU 課禁止用 AI 產生作業解答
