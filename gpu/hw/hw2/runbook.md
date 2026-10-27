# GPU HW2 本機 Runbook（Windows GPU box）

> 2026-10-27 15:40 PDT 建立。截止 **2026-10-27（二）5:59 PM PDT**（Canvas assignment 11810626）。
> 原文：[spec.md](spec.md)（[PDF](spec.pdf)），摘要：[README.md](README.md)。下面的「p4」是 PDF 頁碼，「步驟 N」是原文 Programming Exercises 的編號。
> 環境和 HW1 一樣（VS 2026 18.10.3、CUDA 13.4 V13.4.92、RTX 3050 CC 8.6、driver 617.42），環境配置見 [../local-runbook.md](../local-runbook.md) §0–§1，這份不再重複。
> 這份 runbook 的數字都是本機實測，不是 AWS T4 上的結果。

## 怎麼用

- 用法和 HW1 的 [runbook-guide.md](../runbook-guide.md) 一樣：以原文為主線，從頭往下讀，每讀到一段就到這份 runbook 找對應的小節。
- 兩種標記：
  - **✍️**：要寫進答案的東西。這份只給答案方向和本機數據，交出去的要用你自己的截圖和文字。
  - **⚠️**：原文和實際情況不一樣，以這裡的實測為準。
- 學習單：[`D:\Repos\Au26_GPU\Au26_GPUCompute\HW2\HW2_Answers.docx`](../../../../Au26_GPU/Au26_GPUCompute/HW2/HW2_Answers.docx)，格式照 HW1_Answers.docx（Calibri、灰底表頭、1×1 作答框），**2026-10-27 起是完整填好的版本**，只剩匯出 PDF 和上傳。
  - 只放原文要求的項目：
    - Part 1：Q1–Q3
    - Part 2：P1 a–c 各一張 `algorithm | FLOPs | Mem bytes | AI` 表，加上 order of complexity；P2 的規格表、代入值、兩張 roofline 圖
    - Part 3：模糊影像 #1–#3、理論 AI（extra credit）、計時表、DEBUG vs RELEASE、Warp QUESTION 和兩張截圖、NCU 8 列和 CLI 原始輸出、兩題 HW Q
    - Extra credit：CPU vs GPU
  - 開頭的 Build environment 寫明是本機 RTX 3050、不是 AWS T4，也寫了量測用的 build 和 debugger 用的 build 不同。
  - 填完用 Word「另存 PDF」交。
  - 產生流程是 [src/make_sheet.ps1](src/make_sheet.ps1)：空白版只產生在 `%TEMP%` 當中間檔，接著填入數據和簡答，直接寫成 `HW2_Answers.docx`。**重跑會覆蓋你在 Word 裡手改的內容。**
  - 2026-10-27 用四個獨立 agent 檢查過兩輪：刪掉原文沒要求的項目、逐格驗算數字、確認每題都有回答。

### 進度：哪些做完了，哪些要你動手

| 項目 | 狀態 |
|---|---|
| 3 個 blur kernel + CPU 版本 + timer（[src/hw2.cu](src/hw2.cu)） | ✅ 背景 build，4 張圖 × 3 kernel 全部和 CPU 版**逐 pixel 相同**（0 mismatch） |
| 計時：Debug、Release 各跑 5 次 | ✅ [results/timing_release.txt](results/timing_release.txt)、[results/timing_debug.txt](results/timing_debug.txt)，整理在 §4 |
| NCU：global／static × 4 張圖，共 8 次 | ✅ 2026-10-27 15:30 PDT 用 admin 跑完（你按了 UAC），[results/ncu/](results/ncu/)，整理在 §6 |
| P2 roofline 圖 | ✅ [fig/roofline_quadro.png](fig/roofline_quadro.png)、[fig/roofline_h100.png](fig/roofline_h100.png)，數值在 [fig/p1_p2_values.md](fig/p1_p2_values.md) |
| 模糊後的影像 #1–#3 | ✅ [results/images/](results/images/) |
| 把程式放進 VS 的 HW2 專案 | ✅ 2026-10-27 15:50 PDT 經你同意後完成，msbuild Debug（有 `-G`）和 Release 都成功，不帶參數執行是影像 1、0 mismatch（§2）。**沒有 commit** |
| 學習單 | ✅ `HW2_Answers.docx` 已完整填好（見上面）。預填版 `HW2_Answers_data.docx` 已刪除 |
| Nsight VSE debugger 兩張截圖（步驟 9–13） | ✅ 你在 GUI 截好：`HW2\screenshot_1.png`（640/640 warps）、`screenshot_2.png`（`<<<1,1>>>`，Launch Details 展開） |
| 匯出 PDF、上傳 Canvas | ⏳ 你 |

---

## 1. 檔案

| 檔案 | 內容 |
|---|---|
| [src/hw2.cu](src/hw2.cu) | 從你的 `hw2_starter.cu` 改出來：3 個 Gaussian kernel、L2 的 box blur（原文提示要先做）、CPU 循序版本、Windows high-performance timer、和 CPU 結果逐 pixel 比對 |
| [src/cuda_check.h](src/cuda_check.h) | HW1 的 `checkCuda()`，原樣複製 |
| [src/roofline.py](src/roofline.py) | P1 的 AI 數值和 P2 的兩張 roofline 圖 |
| [src/make_sheet.ps1](src/make_sheet.ps1) | 產生學習單：[make_answers_docx.py](src/make_answers_docx.py)（版面）→ [fill_data_docx.py](src/fill_data_docx.py)（數據、圖、P1/P2）→ [fill_answers_docx.py](src/fill_answers_docx.py)（簡答） |
| [src/build.bat](src/build.bat)、[src/run_all.ps1](src/run_all.ps1)、[src/ncu_admin.ps1](src/ncu_admin.ps1) | 背景流程，build 資料夾是 `%TEMP%\claude\hw2build`（repo 外面） |

對照原文的要求：

| 原文要求 | `hw2.cu` 裡的位置 |
|---|---|
| 8-bit 單色、`unsigned char`、`stbi_load(..., 1)` | `main()`。實測 4 張圖都是 1 channel，和 README 的「本機檔案核對」一致 |
| kernel 內用 32-bit `int` 累加（5a.ii.1） | `gaussPixel()` 的 `int pixVal` |
| 2D row／col index、邊界檢查、一個 thread 寫一個 pixel（5b.i–iii） | 每個 kernel 開頭的 `col`／`row`、`if (col < w && row < h)` |
| 係數乘 pixel 後**四捨五入成 int**（5b.vi） | `__float2int_rn(wt * in[...])`。不要寫 `(int)(w*p + 0.5f)`：nvcc 會把它併成 FMA，和 CPU 差一次捨入（就是 HW1 的 SAXPY 問題） |
| 除以**實際用到的係數總和**（5b.vii） | `weightSum` 只加落在影像內的係數，所以邊緣 pixel 的除數比較小 |
| 版本 i：只用 GMEM | `gaussBlurKernel_globalmem` |
| 版本 ii：static SMEM | `gaussBlurKernel_sharedmem_static`，`__shared__ float s_filt[81]` |
| 版本 iii：dynamic SMEM | `gaussBlurKernel_sharedmem_dynamic`，`extern __shared__ float s_filtDyn[]`，launch 的第 3 個參數 `81*sizeof(float)`（L3 p47） |
| 多一個 kernel 參數傳係數到 GMEM（5c.iv） | `const float* d_filt`，host 先 `cudaMemcpy(d_filt, BLUR_FILT, ...)` |
| 前 N 個 thread 一起複製係數 + `__syncthreads()`（5c.v） | block-strided 迴圈 `for (i = tid; i < 81; i += blockDim.x*blockDim.y)`。用這種寫法，`<<<1,1>>>` 時單一 thread 也會把 81 個全部複製完；如果寫 `if (tid < 81)`，debug 那一步只會載到第 0 個係數。另外，**邊界外的 thread 也要參與複製、也要走到 `__syncthreads()`**，所以邊界檢查放在 barrier 之後 |
| `profileapi.h` timer（步驟 6） | `QueryPerformanceFrequency` / `QueryPerformanceCounter`，timer #1、#2、#3 的位置照 starter 的註解 |
| Extra credit：host 循序 blur | `gaussBlurHost()`，算法和 GPU 完全相同（`nearbyintf` = round-half-even，和 `__float2int_rn` 一致），所以可以逐 pixel 比對 |

設計說明：
- **執行設定**：`dim3 block(16,16)`，`grid(ceil(w/16), ceil(h/16))`。例如影像 1 是 grid(15,15)，影像 4 是 grid(252,189)。
- **命令列參數**（不帶參數就用編譯時的 `IMG_IDX`、`KERNEL_SEL`）：
  ```
  hw2.exe [1-4|all] [global|static|dynamic|all|box] [--box N] [--reps N] [--nocpu] [--dir DIR] [--out DIR]
  ```
  原文步驟 21 要「每張圖各一個 exe」，所以用 `-DIMG_IDX=3 -DKERNEL_SEL=0` 編出 `hw2_rel_global_img3.exe`，這個 exe 不帶參數跑就只 launch 一個 global kernel（步驟 16）。
- **`cudaFree(0)` 放在 timer #1 之前**：先建好 CUDA context，否則第一次的 timer #1 會把建 context 的時間（約 100 ms）算進去，各張圖之間就看不出差異。
- **第 1 次 launch 比較慢**：本機是用 PTX JIT（sm_75 的 code 跑在 sm_86 上），加上 lazy module loading。JIT cache 是冷的時候，第一次 timer #2 實測有 123 ms，熱的時候是 0.6 ms。所以每個 case 跑 5 次（`--reps 5`），§4 取第 2–5 次的中位數。AWS 的 T4 本身就是 sm_75，不用 JIT，但 lazy loading 一樣會讓第一次比較慢。

## 2. 放進 VS 專案（原文步驟 1–4）

你的 HW2 專案已經建好了（`Au26_GPUCompute\HW2\HW2.vcxproj`，`hw2_starter.cu`、`util\stb_*.h`、`dat\*.png` 都在）。剩下要做的：

1. 把 [src/hw2.cu](src/hw2.cu) 的內容貼進 `hw2_starter.cu`（或加成新檔 `hw2.cu`，再把 `hw2_starter.cu` 從專案移除），並把 [src/cuda_check.h](src/cuda_check.h) 用「加入 → 現有項目」加進專案。
2. **⚠️ 影像路徑**：你 starter 裡的 `IMG_DIR "D:/Repos/Au26_GPU/HW2/dat/"` 少了一層，實際位置是 `D:/Repos/Au26_GPU/Au26_GPUCompute/HW2/dat/`。`hw2.cu` 已經改好了，讀檔失敗時會印出 `stbi_load failed for ...`。
3. **⚠️ Code Generation**：`HW2.vcxproj` 目前是 `compute_86,sm_86`，原文 p3 要 `sm_75`（T4）。建議改成 `compute_75,sm_75;compute_86,sm_86`（專案屬性 → CUDA C/C++ → Device → Code Generation，Debug、Release 都要改）：
   - 交出去的設定符合原文。
   - 本機 debugger 直接跑 sm_86 SASS，不用 JIT。
   - 背景 build 用的是 `compute_75,sm_75`，結果一樣。
4. **已經做好了**（2026-10-27 15:50 PDT，你同意之後）：
   - `HW2.vcxproj` 的 `CudaCompile` 改成 `hw2.cu`。`hw2_starter.cu` 改成 `None`，還在專案裡看得到，但不編譯。
   - 加了 `cuda_check.h`。
   - Debug、Release 的 CodeGeneration 都改成 `compute_75,sm_75;compute_86,sm_86`。
   - msbuild 實測：Debug 的 nvcc 參數有 `-G -g`，Release 沒有；兩個都是「建置成功、0 個錯誤」。
   - 輸出在 `Au26_GPUCompute\HW2\x64\{Debug,Release}\HW2.exe`，已經被 `.gitignore` 排除。
   - 你那邊 `git status` 會看到：`HW2.vcxproj` 修改，新增 `hw2.cu`、`cuda_check.h`、`HW2_Answers*.docx`（加上你原本就沒 commit 的 `.slnx`、`HW0/`）。都還沒 commit。

## 3. 背景流程（已經跑完，要重跑時用）

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\Repos\fall-2026\gpu\hw\hw2\src\run_all.ps1
```

腳本會做這些事：
- 把 `src\` 和 `Au26_GPU\...\util\` 複製到 `%TEMP%\claude\hw2build`。
- 用 `vcvars64.bat` 和 nvcc build 出 `hw2_rel.exe`、`hw2_dbg.exe`（`-G`），以及 8 個 `hw2_rel_{global,shared}_img{1..4}.exe`。
- 跑 Release、Debug 各 5 reps 的計時，再跑一次 box blur（`--box 10`）。
- 試跑一般權限的 ncu。

NCU 一定要 admin：一般權限會出現 `ERR_NVGPUCTRPERM`（2026-10-27 實測）。原文步驟 17 本來就要 Run as Admin。
```powershell
Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','D:\Repos\fall-2026\gpu\hw\hw2\src\ncu_admin.ps1' -Verb RunAs -Wait
```
這行會跳一次 UAC，常常只在工作列閃盾牌圖示，不會自動跳到最前面。

要在 VS 裡自己跑：工具列切 **Release / x64** → 建置 → **Ctrl+F5**。要帶參數的話，在專案屬性 → 偵錯 → 命令引數填，例如 `all all --reps 5`。

## 4. 計時（原文步驟 6–7）✍️

不在 debugger 裡跑。表裡是第 2–5 次的中位數，單位 ms：
- T1 = alloc + HtoD + kernel + DtoH + free
- T2 = kernel launch 到 `cudaDeviceSynchronize()`

| 影像 | kernel | Debug T1 | Debug T2 | Release T1 | Release T2 |
|---|---|---|---|---|---|
| #1 240×240 | global | 1.329 | 0.755 | 0.514 | 0.059 |
| | static SMEM | 1.186 | 0.764 | 0.474 | 0.055 |
| | dynamic SMEM | 1.157 | 0.758 | 0.474 | 0.045 |
| #2 512×512 | global | 3.736 | 3.192 | 0.706 | 0.135 |
| | static SMEM | 3.700 | 3.207 | 0.644 | 0.112 |
| | dynamic SMEM | 3.748 | 3.203 | 0.495 | 0.103 |
| #3 850×850 | global | 10.456 | 9.742 | 0.823 | 0.269 |
| | static SMEM | 10.624 | 9.818 | 0.853 | 0.263 |
| | dynamic SMEM | 9.722 | 8.965 | 1.089 | 0.271 |
| #4 4032×3024 | global | 149.221 | 144.512 | 8.415 | 4.172 |
| | static SMEM | 140.460 | 136.590 | 7.431 | 3.886 |
| | dynamic SMEM | 145.704 | 141.675 | 7.672 | 3.903 |

CPU 循序版本（timer #3，Extra credit）：

| 影像 | Debug | Release |
|---|---|---|
| #1 | 16.53 | 9.68 |
| #2 | 68.94 | 41.53 |
| #3 | 189.73 | 109.97 |
| #4 | 3700.19 | 2210.16 |

DEBUG vs RELEASE 的答案方向：
- Debug 的 kernel 時間（T2）約是 Release 的 **13–36 倍**：影像 4 是 144.5 vs 4.17 ms，影像 2 是 3.19 vs 0.135 ms。
  - 原因是 VS 的 Debug 會對 device code 加 `-G`，關掉所有 device 最佳化：沒有 loop unroll，變數每次都寫回 local memory 讓 debugger 看得到。
  - 證據是 register 用量：`nvcc --resource-usage` 顯示 Debug 的 shared 版本用 56 個 register，Release 是 38 個。
- CPU 版本 Debug 是 `/Od`，約慢 1.7 倍。
- 小影像的 T1 主要是 `cudaMalloc`、`cudaMemcpy` 的固定成本，大約 0.4–0.5 ms，kernel 本身只有 0.05 ms。影像 4 的 T1 約是 T2 的 2 倍：多出來的是 12 MB 的 HtoD 和 DtoH。
- 三個 kernel 在 Release 差很少（影像 4：global 4.17、static 3.89、dynamic 3.90 ms），HW Q 的討論見 §6。

## 5. Nsight VSE Debugger（原文步驟 8–13）：要你在 GUI 操作

這一段沒辦法在背景做。先完成 §2，讓 VS 專案裡是 `hw2.cu` 的內容。

1. 工具列切 **Debug / x64** → 建置 → 建置方案。原文步驟 10b：沒有先 build Debug，debugger 會 attach 失敗。
2. 先確認 `DEBUG_SINGLE_THREAD` 是 **0**（`hw2.cu` 第 34 行），不帶命令引數就是影像 1（240×240），三個 kernel 都會跑。
3. 在 `gaussBlurKernel_globalmem` 的兩行相鄰程式碼設中斷點（步驟 9）：
   - **第 94 行** `int col = blockIdx.x * blockDim.x + threadIdx.x;`
   - **第 95 行** `int row = blockIdx.y * blockDim.y + threadIdx.y;`
   - 貼進 VS 之後行號可能不同，找這兩行就對了。✍️ 學習單要寫你實際的行號。
4. **延伸模組 → Nsight → Start CUDA Debugging (Next-Gen)**（步驟 10）。
5. 停下來之後（步驟 11）：
   - 在「區域變數」或「監看式」看 `col`、`row`、`blockIdx`、`threadIdx`。
   - 按 **F10**：多半會停在同一行，但 `col`／`row` 會變。再按一次 F10 也一樣。
   - ✍️ 把每一步看到的值記在學習單的表格裡。原因寫：很多 thread（不同 warp）都執行到同一行，debugger 每次切到另一個 warp 的 thread，所以畫面停在同一行。
6. **延伸模組 → Nsight → Windows → Lanes**，再開 **Warp Info**（步驟 12）：
   - 在 Lanes 點一個 thread、在 Warp Info 點一個 warp，看 `col`／`row` 的變化。
   - ✍️ **截圖 1**：兩個視窗都看得到。Win+Shift+S 截圖後直接貼進學習單。
7. 停止偵錯，把第 34 行改成 `#define DEBUG_SINGLE_THREAD 1`，重新 build Debug，再開一次 debugger（步驟 13）：
   - 現在 launch 是 grid(1,1) block(1,1)，Lanes 只會有 1 個 active lane，Warp Info 只有 1 個 warp。
   - ✍️ **截圖 2**。
   - 做完記得改回 0。`<<<1,1>>>` 只算 (0,0) 一個 pixel，輸出的圖是錯的，這是正常的。
8. 原文 8c 的 Conditional Breakpoint 老師自己也說不穩，不用做。

**⚠️ Lanes 的說明和本機不一樣**：原文 p7 說影像 3、4 不是完整的 warp。用 16×16 block 時：
- 影像 3 的 850 不是 16 的倍數，最右和最下那排 block 會有 thread 在 `if` 外面。
- 影像 4 是 4032×3024，兩邊都是 16 的倍數（252×189 個 block），所以其實也是完整的 warp。
- 而且就算 thread 在邊界外，Lanes 還是會列出它，只是它不會進到 `if` 裡面。

**QUESTION：有幾個 warp 在跑？用 T4 的硬體資源解釋。**
- ✍️ 數字用你截圖裡 Warp Info 實際顯示的。
- **⚠️ 你截到的是 RTX 3050，不是 T4**，要把兩個都寫出來。T4 的推算（L2 p38–p44：40 個 SM，每個 SM 最多 1024 threads = 32 warps、16 個 block、64K registers）：
  - 一個 block 16×16 = 256 threads = 8 warps。
  - 影像 1 有 15×15 = 225 個 block，總共 1800 個 warp。
  - 每個 SM 能放幾個 block：
    - thread 上限：1024 / 256 = 4 個 block。
    - register 上限：Debug 每個 thread 56 個 register，一個 block 要 56 × 256 = 14,336 個，65536 / 14,336 = 4.57 → 4 個 block。
    - block 上限 16 個，不是瓶頸。
  - 所以每個 SM 最多 4 個 block = 32 個 warp，整張 T4 同時最多 40 × 32 = **1280 個 warp**（160 個 block），剩下 65 個 block 要等第二波。
- RTX 3050（`devicequery`：20 個 SM、每個 SM 1536 threads、64K registers）：
  - thread 上限：1536 / 256 = 6 個 block。
  - register 上限：Debug 56 個 register → 4 個 block。
  - 所以每個 SM 最多 32 個 warp，整張卡最多 20 × 32 = **640 個 warp**。
- Warp Info 顯示的數字可能比上限少：它可能只列出目前停在中斷點、或還留在 SM 上的 warp。如果你看到的是 8 的倍數，就是「幾個 block × 8 warps」。
- 不確定 Nsight Next-Gen 的 Warp Info 列的是整張卡還是單一 SM。截圖時看一下視窗裡有沒有 SM 編號欄位，把觀察寫進答案。

## 6. Nsight Compute CLI（原文步驟 14–26）✍️

- 指令照原文步驟 19，14 個 metric 全部收。每個 exe 都跑了兩次：一次一般輸出（`ncu_*.txt`，可以截圖），一次 `--csv --print-units base`（`ncu_*.csv`，下表從這裡算）。
- **⚠️ 學習單（2026-10-27 改版）的 NCU 表改用 `.txt` 那次執行**，和學習單裡貼的 CLI 原始輸出是同一次，HW Q 的數字也照這次寫：影像 4 的 DRAM 是 80.3 MB（global）vs 45.8 MB（shared），inst intensity 6.43 vs 10.77，頻寬 19.5 vs 11.8 GB/s。下表是 `.csv` 那次，兩次的 DRAM 數字不一樣，原因見下面的 ⚠️。
- ⚠️ 原文步驟 25b 的 `dram_bytes.sum` 少一個底線，正確是 `dram__bytes.sum`。用 `--print-units base` 時單位已經是 byte，不用再從 Kbyte 換算。
- 第 1 列範例（global、影像 1）：kernel time = 3,464,440 / 1.428e11 = 2.426e-5 s，和 ncu 的 `gpu__time_duration.sum` 24,256 ns 一致。

| kernel | 影像 | smsp__cycles_elapsed.sum | …per_second (cycle/s) | smsp__inst_executed.sum | dram__bytes.sum (B) | kernel time (s) | inst intensity (inst/B) |
|---|---|---|---|---|---|---|---|
| global | 1 | 3,464,440 | 1.428e11 | 2,439,000 | 65,024 | 2.4256e-05 | 37.51 |
| global | 2 | 13,475,800 | 1.448e11 | 11,100,160 | 306,944 | 9.3088e-05 | 36.16 |
| global | 3 | 36,727,480 | 1.454e11 | 31,101,030 | 961,408 | 2.5264e-04 | 32.35 |
| global | 4 | 599,967,680 | 1.457e11 | 516,287,520 | 88,193,280 | 4.1165e-03 | 5.85 |
| static SMEM | 1 | 3,300,320 | 1.430e11 | 2,329,425 | 145,408 | 2.3072e-05 | 16.02 |
| static SMEM | 2 | 12,667,280 | 1.446e11 | 10,601,472 | 436,608 | 8.7584e-05 | 24.28 |
| static SMEM | 3 | 34,318,240 | 1.453e11 | 29,708,532 | 928,768 | 2.3613e-04 | 31.99 |
| static SMEM | 4 | 563,388,080 | 1.457e11 | 493,092,684 | 30,713,344 | 3.8655e-03 | 16.05 |

觀察（寫 HW Q 用）：
- **時間**：static SMEM 每張圖都比 global 快 **5–7%**（4.12 → 3.87 ms）。兩次 ncu 的結果一致，和 §4 的 host timer 也一致。
- **指令數**：SMEM 版本少約 4.5%（516M → 493M）。
- **⚠️ `dram__bytes.sum` 很不穩**，同一個 exe 兩次 ncu 差很多，例如 static 影像 2 一次 0.44 MB、一次 1.22 MB。原因：
  - ncu 預設每個 pass 之前會清 cache（`--cache-control all`）。
  - 小影像的輸出整張留在 3050 的 1.5 MB L2 裡，kernel 結束前不會寫回 DRAM，所以影像 1、2 的 `dram__bytes_write` 是 0。
  - 所以影像 1–3 的 inst intensity 主要反映 DRAM 量測的雜訊，**只有影像 4 有參考價值**。
  - 影像 4 兩次都是 global 的 DRAM 讀取比較多（68–77 MB vs 19–34 MB；輸入只有 12.2 MB）。可能的原因是 global 版本的係數 load 和 pixel load 搶 L1，pixel 的 L1 命中率比較低，造成比較多 L2／DRAM 流量。這一點**我沒有用 ncu 的 L1 hit rate 驗證**。

**HW Q a：為什麼 shared mem 版本和 global mem 版本的 kernel 時間不同？** 答案方向：
- 每個輸出 pixel 要讀 81 個係數。
  - global 版本：每次都是一個 global load（LDG），要經過 L1 → L2 → DRAM 的階層。就算命中 L1，延遲也有數十個 cycle，而且和 pixel 的 load 共用 L1 的頻寬和容量。
  - shared 版本：每個 block 只從 GMEM 讀一次係數（81 × 4 = 324 B），之後都從 on-chip SMEM 讀。SMEM 延遲低，而且同一個 warp 讀同一個位址時是 broadcast，不會有 bank conflict。
- 差距只有 5–7%，原因有兩個：
  - 同一個 warp 的 32 個 thread 讀的是**同一個係數**（uniform access），global 版本其實也幾乎都命中 L1。
  - kernel 的時間主要花在 81 次 pixel load（1 byte、不連續的 row）和整數／浮點運算上。
- SMEM 版本多了一次 `__syncthreads()` 和複製迴圈，但每個 block 只做一次，成本可以忽略。

**HW Q b：naive vs tiled（這份作業就是 global vs shared）的差異。** 答案方向：
- inst intensity（instruction／DRAM byte）在影像 4 是 5.9（global）vs 16（shared）。
  - 兩者的指令數差不多，差在 DRAM byte：shared 版本 DRAM 流量少，同樣的指令只需要比較少的 DRAM 資料。
  - 兩個 kernel 的 inst intensity 都很高（每個 DRAM byte 要執行好幾個指令），表示這個 kernel 偏 **compute／latency bound**，不是 DRAM 頻寬 bound：
    - 3050 的峰值頻寬約 224 GB/s。影像 4 global 的實際 DRAM 頻寬是 88 MB / 4.1 ms ≈ 21 GB/s，不到峰值的 10%。
  - 所以把係數搬到 SMEM 只省下 L1／L2 的存取，效果有限。
- 要再快，該把**輸入 pixel** 做 tiling：每個 block 把 (16+8)×(16+8) 的 input tile 搬進 SMEM，鄰近 thread 共用。這樣每個 pixel 的 global load 從 81 次降到大約 (24×24)/(16×16) = 2.25 次。這就是 L3 tiled MM 的想法。
- 影像 1–3 的 DRAM 數字被 L2 吸收、雜訊大（見上面的 ⚠️），寫答案時要說明這一點。

**Extra credit：理論 AI，global vs shared kernel。**
- FLOPs（每個內部 pixel）：每個 tap 是 1 個 FMUL（`wt*pixel`）+ 1 個 FADD（`weightSum`），共 81 × 2 = 162，再加最後 1 個 FDIV，**≈ 163 FLOP**。int 加法和 float→int 轉換不算 FLOP，要寫出這個假設。
- 沒有 cache（每次存取都到 GMEM）：
  - global：81 B pixel + 81 × 4 B 係數 + 1 B 寫出 = 406 B → AI ≈ **0.40**
  - shared：81 B + 324 B / 256 個 thread（每個 block 只讀一次係數）+ 1 B ≈ 83.3 B → AI ≈ **1.96**
- 完美 cache（每個 pixel 只讀一次）：兩個版本都約 1 B 讀 + 1 B 寫 → AI ≈ 81。
- 實測（影像 4）：總 FLOP = 163 × 12.19M ≈ 1.99 GFLOP。除以 DRAM byte：global 約 22.5 FLOP/B（88 MB），shared 約 65 FLOP/B（30.7 MB），介於兩個極端之間，表示 L1／L2 吸收了大部分的重複讀取。

## 7. 書面題（每題都要附理由）✍️

**Q1 → b 1,000**
- shared memory 變數的 scope 和 lifetime 都是 thread block（L3 p46）：每個 block 有自己的一份，block 裡的 512 個 thread 共用它。
- 所以有 1000 個 block 就有 1000 份。512 和 512,000 是把它當成 register 或 local 變數（每個 thread 一份）來算。

**Q2 → c 1/32**
- non-tiled：每算一個 P 元素，就要從 GMEM 讀 A 的一整列和 B 的一整行，每個 A、B 元素被讀 N 次。
- tiled：一個 32×32 的 block 每個 phase 載入一個 A tile 和一個 B tile，每個載入的元素在 SMEM 裡被 32 個 thread 重複使用。所以 GMEM 讀取量減少為 1/TILE_WIDTH = **1/32**（L3 tiled MMULT）。

**Q3 → b 32**
- 一個 A tile 是 32 × 32 個 float = 4096 bytes。
- tile 的每一列是 32 個連續的 float = 128 bytes，剛好是一個 burst（假設對齊，而且同一個 warp 的 thread 讀連續的位址，也就是 coalesced）。
- 32 列 → 4096 / 128 = **32 個 burst**。

**P1**：[fig/p1_p2_values.md](fig/p1_p2_values.md)。每一項都要分開寫，下面是方向：

- **a. Transpose**：`B[j][i] = A[i][j]`。
  - FLOPs = 0（只有搬資料）。
  - Mem = 讀 4N² + 寫 4N² = 8N² bytes。
  - AI = **0**。是最極端的 memory-bound。
- **b. SoftMax 3-pass unfused**（長度 N 的向量；R 列時全部乘以 R，AI 不變）：

  | pass | 式子 | FLOPs | Mem bytes |
  |---|---|---|---|
  | 1 | `m = max_i x_i` | N−1 次比較 | 讀 4N |
  | 2 | `e_i = exp(x_i − m)`，`s = Σ e_i` | N（減）+ 4N（exp）+ N−1（加） | 讀 4N、寫 4N（存 e） |
  | 3 | `y_i = e_i / s` | N（除） | 讀 4N、寫 4N |
  | 合計 | | ≈ **8N** | **20N** |

  - AI = **0.4**，memory-bound。
  - ⚠️ 除法原文沒說算幾個 FLOP，這裡當 1 個，要寫出這個假設。
  - 另一種常見寫法是 pass 3 重算 `exp`、pass 2 不存 e：FLOPs 13N、Mem 16N、AI ≈ 0.81。用哪一種要寫清楚。
- **c. Convolution**（direct conv，C_in = C_out = C，stride 1，same padding）：
  - 式子：`Out[n,co,h,w] = Σ_{ci,kh,kw} In[n,ci,h+kh,w+kw] · Wt[co,ci,kh,kw]`
  - FLOPs：每個輸出有 C·K² 個 MAC，一個 MAC 是 1 個 FMA = 2 FLOP，所以總共 **2·N·C²·H·W·K²**。
  - Mem（只算 GMEM，每個元素讀一次）：讀 input 4NCHW + 讀 weight 4C²K² + 寫 output 4NCHW。
  - AI = 2NC²HWK² / (8NCHW + 4C²K²)，當 NHW 很大時 ≈ **C·K²/4**。

**P2**：
- ⚠️ 規格是我查到的公開數字，交之前請自己對一下 NVIDIA datasheet。

  | GPU | Peak FP32 | Peak BW | Ridge |
  |---|---|---|---|
  | Quadro RTX 6000（TU102） | 16.3 TFLOP/s（4608 cores × 2 × 1.77 GHz boost） | 672 GB/s（384-bit GDDR6 @ 14 Gbps） | **24.3 FLOP/B** |
  | H100 SXM5 | 67 TFLOP/s（FP32 非 Tensor Core，L3 p34 也是 67） | 3.35 TB/s（HBM3） | **20.0 FLOP/B** |

- 代入的值和 regime：

  | kernel | 代入的值 | AI | RTX 6000 | H100 |
  |---|---|---|---|---|
  | transpose | N = 4096 | 0 | memory-bound | memory-bound |
  | softmax | N = 4096，1024 列 | 0.4 | memory-bound | memory-bound |
  | conv | N=32，224×224，K=3，C=3 | 6.75 | memory-bound | memory-bound |
  | conv | 同上，C=16 | 36 | transitional | transitional |
  | conv | 同上，C=64 | 144 | compute-bound | compute-bound |

- 「transitional」原文沒定義，我用 ridge/2 到 2×ridge 這一段，圖上是黃色區域。要寫出這個定義。
- conv 換 C 就會換 regime，這就是原文 P2 說的「換值可以讓 kernel 換 regime」。
- transpose 的 AI 是 0，在 log 軸上畫不出來，圖上把它釘在最左邊，要加註。
- 圖直接插進學習單 P2 的框裡。

## 8. 繳交（Canvas，你自己上傳）

截止 **2026-10-27 5:59 PM PDT**。原文 p9 SUBMIT：
1. 答案文件（學習單匯出 PDF）：Q1–Q3、P1、P2（含兩張圖）、Warp QUESTION、兩題 HW Q，都要附理由。
2. 原始碼：只交 `.cu`、`.h`，也就是 `hw2.cu`（或你改名後的 `hw2_starter.cu`）和 `cuda_check.h`。不要交 `.slnx`、`.vcxproj`、`x64\`。
3. 3 個 kernel 在同一個 `.cu` 裡。可以在學習單另外貼出這 3 個函式。
4. 模糊後的影像 #1、#2、#3：`Au26_GPUCompute\HW2\output\hw2_outimage{1,2,3}_global.png`（2026-10-27 從 [results/images/](results/images/) 複製過去）。三個 kernel 的輸出逐 pixel 相同，所以只放 global 版。
5. 計時結果：§4 的表。
6. debugger 截圖兩張：§5。
7. NCU 8 次的輸出（[results/ncu/*.txt](results/ncu/) 可以直接截圖或附檔），加上 kernel time 和 inst intensity 兩欄（§6 的表）。
8. Extra credit：CPU vs GPU 的計時表（§4）、理論 AI（§6）。

CPU vs GPU（Release，T2 用中位數）：

| 影像 | CPU T3 | 最快的 GPU T2 | 加速比 |
|---|---|---|---|
| #1 | 9.68 ms | 0.045 ms（dynamic） | 約 215× |
| #2 | 41.53 ms | 0.103 ms（dynamic） | 約 403× |
| #3 | 109.97 ms | 0.263 ms（static） | 約 418× |
| #4 | 2210.16 ms | 3.886 ms（static） | 約 569×（用 T1 算是 297×） |

## 9. 常見問題

| 症狀 | 原因與處理 |
|---|---|
| `stbi_load failed for .../HW2/dat/...` | `IMG_DIR` 少了 `Au26_GPUCompute/`（§2） |
| ncu 出現 `ERR_NVGPUCTRPERM` | 要用 admin 跑（§3） |
| 第一次 timer #2 是一百多 ms | PTX JIT + lazy loading，看第 2 次以後的結果（§1） |
| Nsight debugger attach 不上 | 先 build **Debug**（步驟 10b） |
| `<<<1,1>>>` 的輸出圖幾乎全黑 | 正常，只算了 (0,0) 一個 pixel；記得把 `DEBUG_SINGLE_THREAD` 改回 0 |
| 一大堆 C4819、`warning #550-D`（stb_image.h） | 可以忽略；`/utf-8` 已經加了，#550 是 stb 自己的 |
| `'cudafe++' died with status 0xC0000005` | 開到 x86 prompt，見 [../local-runbook.md](../local-runbook.md) §1.4 |

---

GPU 課禁止用 AI 產生作業解答；這份 runbook、`src/` 的程式碼和圖都是 AI 產生的，要不要用、怎麼用由你自己決定。
