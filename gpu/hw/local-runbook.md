# GPU HW0 + HW1 本機 Runbook（Windows GPU box，和 AWS 同版本）

> 2026-10-20 PDT 改版：只保留一條環境路線，就是把這台電腦配置成和 AWS WorkSpaces 相同的版本。下面所有步驟都在這台電腦（RTX 3050）上實際執行過，「未實測」的地方會特別標出。
> HW1 截止：**2026-10-20（二）5:59 PM PDT**。作業原文和摘要：[hw0/README.md](hw0/README.md)、[hw1/README.md](hw1/README.md)。
> 程式碼參考檔（2026-10-20 起已進 git）：[`hw0/src/`](hw0/src/)（`kernel.cu` 預設範本、`devicequery.cu`）、[`hw1/src/`](hw1/src/)（`kernel.cu`、`cuda_check.h`）。
> 照作業原文逐步對照這份 runbook 的用法：[runbook-guide.md](runbook-guide.md)。

---

## 0. 目標環境

| 項目 | AWS WorkSpaces（使用者 2026-10-20 03:47 PDT 實測） | 這台電腦（2026-10-20 05:15 PDT 實測） |
|---|---|---|
| GPU | Tesla T4，15360 MiB，WDDM，CC 7.5 | GeForce RTX 3050，8 GB，WDDM，**CC 8.6**（換不了） |
| Driver | 596.36（CUDA 13.2） | **617.42**（CUDA 13.4）。03:39 PDT 自動更新，不是這份 runbook 裝的 |
| Visual Studio | Community 2026 **18.10.3**（September 2026 功能更新） | Community 2026 **18.10.3** ✅ |
| MSVC | **19.51.36260** for x64 | **19.51.36260** for x64 ✅ |
| CUDA Toolkit | 13.4，**V13.4.92**（`Built on Sun_Sep_01_02:23:07_Pacific_Standard_Time_2026`） | 13.4.2，**V13.4.92**，同一個 build ✅ |
| CUDA 專案範本 | CUDA 13.x Runtime | **CUDA 13.4 Runtime** ✅（要手動修，見 §1.5） |
| Nsight | Nsight Compute | Nsight Compute 2026.3.1、Nsight Systems、Nsight VSE 2026.3（延伸模組選單看得到 Nsight） |

這台電腦上另外還有以下東西，都保留不動：
- VS 2022 Community 17.12：只有 .NET 桌面、ASP.NET workload，沒有 C++
- VS 2026 Build Tools 18.7.1：MSVC 19.51.36248
- CUDA 11.8、12.9

它們只會在兩個地方造成麻煩，§1.5 和 §1.6 會說明怎麼處理。

GPU 不一樣只影響兩件事：一是 device query 和效能數字會不同，二是 1000³ 的 3D 測資在 8 GB 的卡上要分批跑（§3.1）。編譯設定和老師一樣，用 `compute_75,sm_75`。這會同時嵌入 sm_75 SASS 和 compute_75 PTX，在 RTX 3050 上由 driver 把 PTX JIT 成 sm_86 來跑。617.42 實測可以；更舊的 driver 沒有測過，如果出現 PTX 相關的錯誤，就把 driver 更新到支援 CUDA 13.4 的版本。

---

## 1. 環境配置

總共需要點 **4 次 UAC**（系統管理員權限）：VS 安裝 1 次、CUDA 安裝 1 次、修 VS integration 1 次，另外保留 1 次重開機的餘裕。

UAC 從背景程式跳出來時，常常只會在**工作列閃爍盾牌圖示**，不會自動跳到最前面。沒點開的話，過一陣子就會自動取消，訊息是「操作被使用者取消」。

### 1.1 Driver：確認就好，不用裝
```bash
nvidia-smi
```
第一行要顯示 `CUDA ... Version: 13.4` 以上（目前是 617.42）。

從 CUDA 13.1 開始，toolkit 不再附 driver，如果低於 13.4，就到 nvidia.com/drivers 更新 GeForce driver。AWS 的 596.36 是 Tesla 用的 datacenter driver，GeForce 卡裝不了同一版，這一項本來就沒辦法一樣。driver 不會影響編譯出來的結果。

### 1.2 安裝 Visual Studio Community 2026 18.10.3（固定版本）
Microsoft 只提供 Enterprise、Professional、Build Tools 的固定版本 bootstrapper，Community 的下載連結永遠是最新版（目前已經是 18.10.4）。做法是**用 18.10.3 的 Professional bootstrapper 加 `--productId` 指定安裝 Community**。這個方法實測可以，裝出來是免費的 Community。

1. 下載（5.7 MB，Microsoft 簽章；網址裡那串 hash 就是檔案的 SHA-256）：
   `https://download.visualstudio.microsoft.com/download/pr/e5f740e0-92f9-49d7-ab3b-5d17b84108fd/97bb40c60d26e9086de55baa49498933ed2fe0666292c19aed3954c18c4e64c8/vs_Professional.exe`
   來源：Visual Studio 2026 Release History 頁面 18.10.3（2026-09-29）那一列的 Professional 連結。
2. 在下載資料夾開 PowerShell 執行（會跳 UAC；安裝約 6 分鐘）：
```powershell
Start-Process .\vs_Professional.exe -ArgumentList '--productId Microsoft.VisualStudio.Product.Community --channelId VisualStudio.18.Release --add Microsoft.VisualStudio.Workload.NativeDesktop --includeRecommended --passive --norestart --wait' -Verb RunAs -Wait
```
3. 確認裝好的版本：
```powershell
& "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -all -format text | Select-String "displayName|catalog_productDisplayVersion"
```
   應該出現 `Visual Studio Community 2026` / `18.10.3`，安裝位置是 `C:\Program Files\Microsoft Visual Studio\18\Community`。
4. **關掉自動更新**（我還沒做，請你自己設定）：開「Visual Studio Installer」→ Community 2026 那一列的「其他」→「更新設定」→ 取消自動下載更新。不關的話，VS 會自己升到 18.10.4 以後的版本，就和 AWS 不一樣了。
5. 第一次開 VS 會要求登入，按「跳過並稍後再登入」，開發設定選「一般」即可。

### 1.3 安裝 CUDA Toolkit 13.4.2（= V13.4.92）
**一定要在 VS 之後裝**，CUDA installer 只會整合到它安裝當下已經存在的 VS。

1. 下載（3.9 GB，NVIDIA 簽章）：
   `https://developer.download.nvidia.com/compute/cuda/13.4.2/local_installers/cuda_13.4.2_windows_x86_64.exe`
   md5 要是 `51f1ee37b2cc75ae46c55d113aa741c6`（NVIDIA 在 `.../13.4.2/docs/sidebar/md5sum.txt` 公布的值）。
   - 現在 CUDA Downloads 頁面的最新版是 13.4.3（October），**不要下載那一版**。13.4.2 在 CUDA Toolkit Archive → 「CUDA Toolkit 13.4.2 (September 2026)」。
2. 安裝。下面兩種方式擇一，結果相同：
   - 圖形介面：對 exe 按右鍵 →「以系統管理員身分執行」→ 選「精簡（Express）」。
   - 靜默安裝（實測用的就是這個，約 5 分鐘，`-n` 表示不自動重開機）：
```powershell
Start-Process .\cuda_13.4.2_windows_x86_64.exe -ArgumentList '-s -n' -Verb RunAs -Wait
```
3. 裝完之後**一定要開新的終端機**，舊的視窗拿不到新的 PATH。

### 1.4 確認命令列環境
從開始選單開「**Developer Command Prompt for VS**」或「**Developer PowerShell for VS**」。這台電腦上有好幾個同名項目（VS 2026 Community、Build Tools 18.7.1、VS 2022），所以要用 `cl` 的版本號判斷開到的是哪一個：
```bash
cl
```
要顯示 `Version 19.51.36260 for x64`。
- 顯示 `19.51.36248`：開到的是 Build Tools。
- 結尾是 `for x86`：開到 x86 的 prompt，換一個。
- 也可以直接執行 `"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"` 來設定環境。

```bash
nvcc --version
```
要顯示 `release 13.4, V13.4.92`。
```bash
where nvcc
```
第一行要是 `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\nvcc.exe`。如果 12.9 排在前面，表示這個終端機是安裝前開的，關掉重開。

中文 Windows（cp950）編譯時會冒出一大堆 `warning C4819`，來自 CUDA 的 header，可以忽略。命令列加 `-Xcompiler /utf-8` 就不會出現。

### 1.5 修 VS integration（這台電腦一定要做）
**症狀**：VS 2026 → 建立新專案 → 語言清單裡沒有 CUDA，找不到「CUDA 13.4 Runtime」範本。重開機、重跑 installer 都沒用。

**原因**（用 `-log:<dir> -loglevel:6` 跑 installer 找到的）：installer 的 `VSModernDevenvSetupInstall` 步驟會依序處理每個 VS。它**先處理 VS 2022 Community**，而這個 VS 2022 沒有 C++，找不到 `BuildCustomizations` 的目標路徑：
```
Installing VSI to Visual Studio "17.12.35728.132" at: "C:\Program Files\Microsoft Visual Studio\2022\Community"
Target:  .
ERROR: ... ModernDevenvInstall : Copy error:  3.
```
這一個錯誤就讓整個步驟中止，**後面的 VS 2026 完全沒有處理到**。installer 最後還是會回報 `All packages installed successfully`。

**修法**：手動補上 installer 少做的兩件事，再請 VS 重新掃描擴充功能。用「以系統管理員身分執行」開 PowerShell，貼上：
```powershell
$vs='C:\Program Files\Microsoft Visual Studio\18\Community'; $cuda='C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4'; $wiz='C:\ProgramData\NVIDIA GPU Computing Toolkit\v13.4\extras\visual_studio_integration\CudaProjectVsWizards\18'
Copy-Item "$cuda\extras\visual_studio_integration\MSBuildExtensions\*" "$vs\MSBuild\Microsoft\VC\v180\BuildCustomizations" -Force
$ext="$vs\Common7\IDE\Extensions\NVIDIA\CUDA 13.4 Wizards\13.4"; New-Item -ItemType Directory -Force $ext | Out-Null; Copy-Item "$wiz\*" $ext -Recurse -Force
Start-Process "$vs\Common7\IDE\devenv.exe" -ArgumentList '/updateconfiguration' -Wait
```
- 第 1 行：把 `CUDA 13.4.props`、`.targets`、`.Version.props`、`.xml`、`Nvda.Build.CudaTasks.v13.4.dll` 複製到 VS 2026 的 `v180\BuildCustomizations`。
- 第 2 行：把 CUDA 13.4 Wizards（專案範本和項目範本的擴充功能）放進 VS 2026 的 `Extensions\NVIDIA`。
- 第 3 行：`devenv /updateconfiguration`，讓 VS 重新掃描擴充功能，實測 exit 0。

修完重開 VS → 建立新專案 → 語言下拉選單出現 **CUDA**，範本出現 **CUDA 13.4 Runtime**（實測 2026-10-20 05:07 PDT）。

**注意**：只要 VS 2022 還是「沒有 C++」的狀態，**之後每次重裝或升級 CUDA 都會發生同樣的問題**，要重做這一節。要根治有兩個辦法：把 VS 2022 移除，或在 VS 2022 加裝 C++ workload。我沒有移除，因為它還有 .NET 的 workload，你可能會用到。

### 1.6 工作資料夾和其他注意事項
- 這學期的 solution 放在 `D:\Repos\Au26_GPU`（private repo `mileschintw/Au26_GPU`，`.gitignore` 排除了 build 產物；做法見 §2.0）。HW0 原文寫的 `C:\Au26_GPU` 是 AWS 上的建議位置，不影響繳交。不要在 fall-2026 repo（`D:\Repos\fall-2026`）裡 build，免得 `.exe`、`x64\` 這些產物跑進 git。
- 從 Claude Code 的終端機執行剛 build 好的 exe 時，要寫 `.\hw1.exe`，不能只寫 `hw1.exe`。這是因為它設了 `NoDefaultCurrentDirectoryInExePath=1`，cmd 不會從目前資料夾找執行檔，會回報「not recognized」。自己開的終端機不受影響，但一律加 `.\` 比較保險。

---

## 2. HW0（不計分、不用交）

### 2.0 極簡路線：只為了能開始 HW1（約 5 分鐘）
HW0 不計分，HW1 只依賴它的一件事：原文 HW1 p2 要你「從新的預設 CUDA 專案開始（像 HW0 那樣）」。所以只做下面這些，其他段落（debugger、cuobjdump、指標練習、device query）都可以之後再補。

1. 開始功能表 → **Visual Studio 2026** → **建立新專案**（HW0 步驟 6–7）。
2. 右上的語言下拉選 **CUDA** → 選 **CUDA 13.4 Runtime** → 下一步（步驟 8–9）。清單裡沒有 CUDA 的話看 §1.5。
3. 填寫（步驟 10–12）：
   - 位置：`D:\Repos\Au26_GPU`（已經是 private repo [mileschintw/Au26_GPU](https://github.com/mileschintw/Au26_GPU)，`.gitignore` 排除了 build 產物）。HW0 原文寫 `C:\Au26_GPU`，只是 AWS 上的整理建議，不影響繳交。
   - **取消勾選**「將解決方案與專案放在相同目錄中」。
   - 解決方案名稱：`Au26_GPUCompute`；專案名稱：`HW1`（直接拿來做 HW1，就不用再加一個專案）。
4. 按**建立**（步驟 13）→ 上方工具列切成 **Release**、**x64** → **建置 → 建置方案**，輸出視窗看到「成功 1 個，失敗 0 個」（步驟 16–18）。
5. **Ctrl+F5**，看到 `{1,2,3,4,5} + {10,20,30,40,50} = {11,22,33,44,55}`，環境就確認沒問題。
6. 接著直接跳到 §3.2 的步驟 2（加 `cuda_check.h`、換 `kernel.cu`）。

建出來的結構：`D:\Repos\Au26_GPU\Au26_GPUCompute\Au26_GPUCompute.slnx`，`HW1\` 在它旁邊。

| HW0 段落 | 原文步驟 | 本機 |
|---|---|---|
| AWS WorkSpaces | 1–5 | 不需要 |
| VS 建專案、build | 6–18 | §2.1 |
| VS debugger | 19–38 | §2.2 |
| nvcc、cuobjdump | 39 + Binary Tools | §2.3 |
| C 指標與陣列 | 40–58 | §2.4 |
| Device Query | p8–p9 | §2.5 |
| nvidia-smi | p9–p10 | 在任何 terminal 執行 `nvidia-smi` |

### 2.1 建 solution 和 project（步驟 6–18）
照原文操作：VS 2026 → 建立新專案 → 語言選 **CUDA** → **CUDA 13.4 Runtime** → 下一步。位置填 `C:\Au26_GPU`，取消勾選「將解決方案與專案放在相同目錄中」，Solution 填 `Au26_GPUCompute`，Project 填 `EX1_vecadd_cudart`。
- 我實測用的是預設名稱 `CudaRuntime1`，放在 `C:\Users\user3\source\repos`，因為 IDE 只能點擊、不能打字。所以**名稱、位置、勾選框這幾步沒有實際操作過**；其他步驟都一樣。
- VS 2026 產生的 solution 檔是 **`.slnx`**，不是原文寫的 `.sln`；project 一樣是 `.vcxproj`。
- 產生的 `kernel.cu` 和 `gpu/hw/hw0/src/kernel.cu` 一致，只差 BOM 和行尾空白。範本原檔在 `C:\ProgramData\NVIDIA GPU Computing Toolkit\v13.4\extras\visual_studio_integration\CudaProjectVsWizards\18\ProjectTemplates\kernel.cu`。行號和原文對得上：第 11 行 `int i = threadIdx.x;`、第 17 行 `arraySize`、第 18–20 行 `a`/`b`/`c`、第 29 行 `printf`、第 46 行 `int *dev_a = 0;`。
- 建置 → 重建方案，輸出視窗實測：`全部重建：成功 1 個，失敗 0 個，略過 0 個`（英文版是 `1 succeeded, 0 failed`）。230 個 C4819 warning 可以忽略。
- VS 預設的 Code Generation 是 `compute_75,sm_75`。build log 裡 nvcc 的參數是 `-gencode=arch=compute_75,code=\"sm_75,compute_75\"`，和 AWS 一樣，不用改。
- 執行結果：`{1,2,3,4,5} + {10,20,30,40,50} = {11,22,33,44,55}`（Debug 和 Release 都實測過）。

### 2.2 Debugger（步驟 19–38）
在第 11、17、29、46 行設中斷點，按「本機 Windows 偵錯工具」啟動。

- **22 / 22b：為什麼停在 `main()` 開頭？為什麼第 11 行的中斷點不見了？**（實測驗證過）
  - 程式停在**第 16 行**，也就是 `main` 的 `{`。
  - 「中斷點」視窗裡只看到 `kernel.cu, 第 16 行（目前 1）`、17、29、46，**沒有第 11 行**。
  - 原因：第 11 行在 `__global__ addKernel` 裡，那是 GPU 程式碼，在 host（CPU）執行檔裡沒有對應的指令。Local Windows Debugger 只能 debug CPU 端，所以 VS 把這個中斷點**移到下一行有 host 程式碼的地方，也就是第 16 行**。
  - 所以程式第一次停下來就是這個被移過來的中斷點，這就是原文說的「黃色箭頭疊在紅點上」。要在 kernel 裡停下來，要用 Nsight（延伸模組 → Nsight，用 Debug build）。
- **33b：`&dev_a` 沒變，`dev_a` 卻變了？**（推理，沒有實際操作 Immediate 視窗）
  - `&dev_a` 是 host stack 上這個指標變數本身的位址，所以固定不變。
  - `dev_a` 是它存的值：一開始是 0，`cudaMalloc((void**)&dev_a, …)` 把 GPU 記憶體的位址寫進去，值就變了。
  - 這也是為什麼要傳 `&dev_a`：`cudaMalloc` 要改的是呼叫端的這個變數。
- Debug build 的 nvcc 參數裡有 `-G`（device debug），這和 HW1 驗證要用 Release 的理由有關（§3.4）。
- 中斷點的 Conditions、Memory 1、Immediate 視窗這幾步沒有實際操作過，照原文做即可。

### 2.3 nvcc 命令列和 cuobjdump（步驟 39 與 Binary Tools）
開 §1.4 的 Developer Command Prompt，`cd` 到 `kernel.cu` 所在的資料夾，照原文執行：
```bash
nvcc -o vecadd kernel.cu -run
```
```bash
.\vecadd.exe
```
- 兩個都輸出 `{11,22,33,44,55}`。不帶 `-arch` 時，CUDA 13.4 預設編 sm_75，在本機也是靠 PTX JIT 執行。
- 實測**只產生 `vecadd.exe`**，沒有原文說的 `vecadd.exp`、`vecadd.lib`。

cuobjdump（原文 PDF 的 `-–dump-ptx` 是 en dash，要自己打兩個 `-`）：
```bash
cuobjdump -lptx vecadd.exe
```
實測：`PTX file    1: vecadd.1.sm_75.ptx`
```bash
cuobjdump -lelf vecadd.exe
```
實測：`ELF file    1: vecadd.1.sm_75.cubin`、`ELF file    2: vecadd.2.sm_75.cubin`
```bash
cuobjdump --dump-ptx vecadd.exe
```
```bash
cuobjdump --dump-sass vecadd.exe
```
注意：如果編譯時只用 `-gencode arch=…,code=sm_XX`（只產生 SASS），執行檔裡就沒有 PTX，`-lptx` 會顯示 `No PTX file found`。做這一段練習要用上面不帶參數的編法。

### 2.4 C 指標與陣列（步驟 40–58），Windows 實測
每改一步都重編一次，再執行 `.\addvec.exe`。改之前先把原檔另存一份。
```bash
nvcc -o addvec kernel.cu
```

| 步驟 | 改動 | 實測輸出 | 為什麼 |
|---|---|---|---|
| 42–44 | 第 18–20 行註解掉，改成 `int* a = 0;`（b、c 同樣） | build 成功 | `addWithCuda(int*, const int*, const int*, …)` 本來就收指標。陣列傳進函式時本來就會 decay 成指標，所以型別一樣，compiler 不會抱怨。NULL 是合法的指標值，只是不能 dereference |
| 45–46 | 執行 | `cudaMemcpy failed!addWithCuda failed!`，exit 1 | `cudaMemcpy(dev_a, a=NULL, …, HostToDevice)` 要從 NULL 讀 host 記憶體，回傳錯誤。這種錯誤要到執行時才看得出來 |
| 47–50 | 改成 `(int*)malloc(arraySize * sizeof(int))`（要加 `#include <stdlib.h>`） | `{1,2,3,4,5} + {10,20,30,40,50} = {14549198,13828200,14811355,11272295,11796666}` | 記憶體有配置了，但 malloc **不會初始化**：a、b 是殘留的垃圾值，c = a + b 也是垃圾值。前面的 `{1,2,3,4,5}` 是寫死在 printf 字串裡的，不是真的值 |
| 51–53 | 加 `for (int x = 0, *pa = a, *pb = b; …) { *pa++ = x + 1; *pb++ = 10 * (x + 1); }` | `… = {11,22,33,44,55}` | `pa`、`pb` 從 a、b 的開頭開始，`*pa++` 寫入目前位置後再往後移一個 int，所以 a = 1..5、b = 10..50。原文說會有 warning，但實測預設、`/W3`、`/W4` 都**沒有** warning。另外要注意 a、b、c 都沒有 `free()`（memory leak） |
| 54–56 | printf 改成印出 `a[0..4]`、`b[0..4]`、`c[0..4]` | `{1,2,3,4,5} + {10,20,30,40,50} = {11,22,33,44,55}` | 現在印的是真的記憶體內容。`a[i]` 就是 `*(a + i)`，所以指標可以直接用陣列語法 |
| 57–58 | 在 VS 裡重建方案，再用偵錯工具執行 | 輸出相同 | — |

### 2.5 Device Query
參考檔是 `gpu/hw/hw0/src/devicequery.cu`：
```bash
nvcc -o devicequery.exe devicequery.cu
```
```bash
.\devicequery.exe
```
Windows 實測：
```
CUDA devices: 1

=== Device 0: NVIDIA GeForce RTX 3050 ===
  Driver / Runtime version     : 13.4 / 13.4
  Compute capability           : 8.6
  totalGlobalMem               : 8589410304 bytes (8.59 GB)
  l2CacheSize                  : 1572864 bytes
  multiProcessorCount          : 20
  maxBlocksPerMultiProcessor   : 16
  maxThreadsPerMultiProcessor  : 1536
  maxThreadsPerBlock           : 1024
  maxThreadsDim[3]             : 1024 x 1024 x 64
  maxGridSize[3]               : 2147483647 x 65535 x 65535
  regsPerBlock                 : 65536
  regsPerMultiprocessor        : 65536
  sharedMemPerMultiprocessor   : 102400 bytes
  warpSize                     : 32
```
- 原文的 `maxThreadDim`、`warpsize` 是錯字，實際欄位是 `maxThreadsDim`、`warpSize`。
- `cudaInitDevice` 要三個參數 `(device, deviceFlags, flags)`，CUDA 12.0 以後才有。
- 在 AWS T4 上 CC 會是 7.5（L2 [03:13:00]），SM 數、記憶體大小也都不同。

---

## 3. HW1（11 分，今天 5:59 PM PDT 截止）

### 3.1 檔案與結構
參考檔在 `gpu/hw/hw1/src/`：

| 檔案 | 內容 |
|---|---|
| `cuda_check.h` | L1 updated p55 的 `checkCuda(cudaError_t, const char* srcStr)`，另外加了 `CHECK_CUDA(call)`（失敗就 exit；Release build 會拿掉 `assert`，所以要靠它）和 `CHECK_KERNEL(name)`（`cudaGetLastError` + `cudaDeviceSynchronize`）。投影片寫的是 `char* srcStr`：實測在預設 C++17 下傳字串常值只會出現 `warning #2464-D`，改成 `-std=c++20` 就會變成 compile error，所以改用 `const char*` |
| `kernel.cu` | 預設範例的 `main`、`addWithCuda` 改成全部用 `checkCuda` 包起來，另外加 4 個 kernel、CPU 版本和驗證 |

對照 HW1 原文的要求：

| 原文要求 | `kernel.cu` 裡的位置 |
|---|---|
| checkCuda 放 `.h`，`main`/`addWithCuda` 都用它 | `#include "cuda_check.h"`；`addWithCuda()` 每個呼叫都用 `checkCuda(…, "說明")` |
| printf kernel（tid、bid、GTID 印在同一行） | `printfKernel`：`gtid = blockIdx.x * blockDim.x + threadIdx.x` |
| SAXPY，kernel 參數要有 N 做邊界檢查 | `saxpyKernel(int n, float a, const float* x, float* y)`，`if (i < n)` |
| 2D add，參數 M、N，2D 邊界檢查 | `matAdd2DKernel(C, A, B, M, N)`，x→col、y→row，`idx = row*N + col` |
| 3D add，參數 M、N、P，用 `dim3` | `gridAdd3DKernel(C, A, B, M, N, P)`，`idx = (z*M + y)*N + x`，`dim3 block(16,8,4)` |
| host 動態配置、初始化成已知值、每個 malloc 都有 free | `hostAlloc` + `fillRandom`（固定 seed 的亂數，可以重現）；每個 test 結尾都有 `free` / `cudaFree` |
| 明確寫 HtoD／DtoH（L2 [02:40:16]） | 全部用 `cudaMemcpyHostToDevice` / `cudaMemcpyDeviceToHost` |
| CPU 循序版本 + tolerance 驗證（L2 p37） | `saxpyCPU`、`addCPU`、`verify()`：`|cpu-gpu| <= max(aTol, rTol*max(|cpu|,|gpu|))`，預設 rTol=1e-5、aTol=1e-6，另外跑一次 tolerance sweep |
| 測資 | SAXPY 10 / 1e3 / 1e7；2D 4×4 / 500×500 / 3024×4032；3D 3³ / 100³ / 1000³（加 `--big`） |

設計說明（寫報告會用到）：
- 輸入用固定 seed 的亂數浮點數，不用小整數。小整數的乘加在 float 裡是精確的，CPU 和 GPU 一定完全一致，HW Q 就沒有東西可以觀察。
- 1000³ 的 3D 測資：每個陣列 4 GB，A、B、C 共 12 GB。T4 有 16 GB 放得下，RTX 3050 只有 8 GB，所以程式會先用 `cudaMemGetInfo` 看剩多少，放不下就**沿 z 切成 slab** 分批處理。每個 slab 都是連續的 M×N×Pslab 子體積，用同一個 3D kernel 和 3D 邊界檢查。host 端只配 3 個陣列，CPU 結果直接覆寫 B，總共約 12 GB（這台有 32 GB RAM）。
- 所有 byte 數和 index 都用 `size_t`，因為 1e9 × 4 bytes 會超過 `int` 的範圍。

### 3.2 用 Visual Studio 建置（和 AWS 相同的做法）
1. 在 `Au26_GPUCompute` solution 上按右鍵 → 加入 → 新增專案 → **CUDA 13.4 Runtime**，取名例如 `HW1`。走 §2.0 極簡路線、專案已經叫 `HW1` 的話，跳過這步。
2. 對 `HW1` 按右鍵 → 加入 → 新增項目 → **標頭檔 (.h)**，命名為 `cuda_check.h`，貼上參考檔的內容。
3. 把 VS 產生的 `kernel.cu` 整份換成參考檔的 `kernel.cu`。
4. 上方工具列 **Debug → Release**，平台 **x64**。**Code Generation 不用改**，保持預設的 `compute_75,sm_75`，和 AWS 一樣。
5. 要帶參數（例如 `grid3d --big`）：專案屬性 → 偵錯 → 命令引數。
6. 建置 → 建置方案，再按 **Ctrl+F5**（啟動但不偵錯），視窗才不會一閃就關掉。
7. FMA 對照組：專案屬性 → CUDA C/C++ → Command Line → 其他選項填 `-fmad=false`，重建。做完記得拿掉。

實測（2026-10-20 PDT）：用 VS 2026 的 CUDA 13.4 Runtime 專案、**預設 Release 設定**，加上 `cuda_check.h`，MSBuild 建置成功。執行結果和 §3.5 逐位數相同。這次是用 `msbuild` 跑和 IDE 一樣的專案設定；IDE 的「重建方案」只在 HW0 範本專案上點過。

### 3.3 用命令列建置（同一套環境）
在 §1.4 的 Developer Command Prompt 裡，先把參考檔複製到 repo 外面：
```bash
xcopy D:\Repos\fall-2026\gpu\hw\hw1\src C:\Au26_GPU\hw1\ /I /Y
```
```bash
cd /d C:\Au26_GPU\hw1
```
```bash
nvcc -O3 -DNDEBUG -Xcompiler "/O2 /fp:precise" -gencode arch=compute_75,code=[sm_75,compute_75] -o hw1.exe kernel.cu
```
```bash
.\hw1.exe
```
```bash
.\hw1.exe grid3d --big
```
FMA 對照組：
```bash
nvcc -O3 -DNDEBUG -fmad=false -Xcompiler "/O2 /fp:precise" -gencode arch=compute_75,code=[sm_75,compute_75] -o hw1_nofma.exe kernel.cu
```
```bash
.\hw1_nofma.exe saxpy
```
實測：
- 上面這行 `code=[sm_75,compute_75]` 和 VS 預設相同，cuobjdump 看得到 `sm_75.ptx` 和 `sm_75.cubin`，結果和 §3.5 逐位數相同。
- 另外試過 `-gencode arch=compute_75,code=sm_75 -gencode arch=compute_86,code=sm_86`（直接嵌入兩份 SASS，不需要 JIT），結果也一樣。
- `--big` 實測 58.6 秒。

### 3.4 一定要用 Release 驗證
原文 p5 要求驗證用 Release。實測原因：VS 的 Debug 設定會對 device code 加 `-G`，而用 `nvcc -G` 編出來的 SAXPY，三個 N 都是 **0 個差異**，因為 `-G` 會關掉 FMA 合併。所以用 Debug build 什麼差異都看不到，兩題 HW Q 也就沒有數據可以寫。

### 3.5 實測輸出（Windows、RTX 3050、Release）
```
=== default template: addWithCuda ===
{1,2,3,4,5} + {10,20,30,40,50} = {11,22,33,44,55}

=== SAXPY  N=10 ===        not bit-identical=1 (10%)          max|diff|=1.907e-06  max rel=8.740e-08
  sweep (aTol=0):  1e-05 pass  1e-06 pass  1e-07 pass  5e-08 FAIL(1)  1e-08 FAIL(1)  0 FAIL(1)
=== SAXPY  N=1000 ===      not bit-identical=273 (27.3%)      max|diff|=3.815e-06  max rel=5.485e-06
  sweep (aTol=0):  1e-05 pass  1e-06 FAIL(2)  1e-07 FAIL(97)  5e-08 FAIL(273)  ...
=== SAXPY  N=10000000 ===  not bit-identical=2520379 (25.2%)  max|diff|=3.815e-06  max rel=7.165e-02
  worst at i=5734209: cpu=2.86102295e-06 gpu=2.65604103e-06
  sweep (aTol=0):  1e-05 FAIL(3569)  1e-06 FAIL(35434)  1e-07 FAIL(815715)  ...
  （三個 N 在 rTol=1e-5、aTol=1e-6 下都 PASSED）

=== 2D 4x4 / 500x500 / 3024x4032 ===  not bit-identical=0，tolerance 0 也 pass
=== 3D 3^3 / 100^3 ===                 not bit-identical=0，tolerance 0 也 pass
=== 3D 1000^3 (--big) ===  device free 7.54/8.59 GB, need 12.00 GB -> z-slabs (slab depth 502)
                           grid(63,125,126) block(16,8,4)  not bit-identical=0  PASSED（58.6 s）

=== -fmad=false 的 SAXPY ===  三個 N 都是 not bit-identical=0
=== -G（Debug）的 SAXPY ===    三個 N 都是 not bit-identical=0
```

### 3.6 printf kernel：每種設定跑 10 次
```powershell
1..10 | % { (.\hw1.exe printf 32 1 1 | Select-String GTID | % { ($_.Line -split 'GTID=')[1].Trim() }) -join ' ' }
```
- 把 `32 1` 換成 `1 32`、`4 8`，各跑一次。
- 這行只印出每次執行的 GTID 順序。要截完整輸出，執行 `.\hw1.exe printf 4 8 10`。

Windows 實測（每列是一次執行的 GTID 順序）：

| 設定 | 結果 |
|---|---|
| `<<<1,32>>>` | 每次都是 `0 1 2 … 31` |
| `<<<4,8>>>` | 每次都是 `8..15, 24..31, 0..7, 16..23`：block 內照 thread 順序，block 之間的順序是 1、3、0、2 |
| `<<<32,1>>>` | 順序會變，但有時會重複。例如 5 次裡有 `17 11 7 15 19 1 …`、`17 7 27 13 19 15 3 9 11 5 23 16 …`、`17 7 27 13 19 15 3 9 11 5 23 29 …`，其中第 3 次和第 5 次完全相同 |

三個觀察題的答案方向（用你自己跑出來的結果寫）：
- **(a) 一致嗎？可預測嗎？**
  - 同一個 block（同一個 warp）裡的 thread 會照 lane 順序印出來，因為 32 個 thread 是同時執行同一個 printf。
  - 不同 block 的順序由硬體 scheduler 決定：`<<<4,8>>>` 在這台機器上剛好每次相同，但順序不是 0、1、2、3；`<<<32,1>>>` 有時一樣、有時不一樣。
  - **都沒有保證**（L2 [03:23:07]：kernel printf 的順序沒有保證）。
- **(b) block 和 thread index 的行為不同嗎？** 不同。block 是獨立排程到各個 SM 的單位，執行順序任意。同一個 warp 內的 thread 以 lockstep（SIMT）執行，所以看起來有順序，但這是實作細節，CUDA 沒有保證。
- **(c) 對 kernel 的計算有什麼含意？**
  - kernel 的正確性不能依賴 thread 或 block 的執行順序。
  - 每個 thread 只寫自己 GTID 對應的輸出，這次的 3 個數學 kernel 都是這樣寫的。
  - 不同 block 之間沒有同步，不能互相等結果。需要合作時，用 `__syncthreads()`（block 內）、atomic 操作，或拆成多次 kernel launch。

### 3.7 書面題答案（每題都要附理由）
**Q1 → A** `i = blockIdx.x*blockDim.x + threadIdx.x`
前面有 `blockIdx.x` 個 block，每個 block 有 `blockDim.x` 個 thread，所以這個 block 的第一個元素是 `blockIdx.x*blockDim.x`，再加上 block 內的偏移 `threadIdx.x`。
- B 沒有用到 block。
- C 用乘的，會重複：例如 thread 0 不管在哪個 block，算出來都是 0。
- D 不同 block 的範圍會重疊。

**Q2 → D** `i = (blockIdx.x*blockDim.x + threadIdx.x)*2`
每個 thread 處理相鄰的兩個元素 `i`、`i+1`，所以 global thread id 為 g 的 thread 負責 `2g`、`2g+1`，第一個元素是 `2g`。例如 blockDim=4：block 0 的 thread 0..3 → 0、2、4、6；block 1 的 thread 0 → (4+0)*2 = 8，剛好接續。
- C 會讓同一個 block 裡的 thread 拿到連續的 i，而不是間隔 2。
- A、B 也都不成立。

**Q3 → A** `i = blockIdx.x*blockDim.x*2 + threadIdx.x`
每個 block 負責 `2*blockDim.x` 個連續元素，所以 block 的起點是 `blockIdx.x*2*blockDim.x`。thread t 在第一個 section 處理「起點 + t」，在第二個 section 處理 `i + blockDim.x`。這樣排，相鄰的 thread 會存取相鄰的位址（coalesced）。

**Q4 → A 8192**
block 數 = ⌈8000/1024⌉ = ⌈7.8125⌉ = 8，8 × 1024 = 8192 個 thread。多出來的 192 個 thread 由 kernel 裡的 `if (i < n)` 擋掉。

**HW Q1：tolerance 設到多少時驗證開始失敗？**（請用你自己的截圖數字；以下是本機結果）
- 2D 和 3D 加法：CPU 和 GPU 的結果**逐 bit 相同**，tolerance 設成 0 也不會失敗。
- SAXPY（aTol=0，只調 rTol）：
  - N=10：rTol 小於約 8.7e-8 就開始失敗（5e-8 失敗）。
  - N=1e3：rTol=1e-6 開始失敗。
  - N=1e7：連 rTol=1e-5 都有 3569 個失敗。
- N=1e7 的最大相對誤差高達 7e-2，因為有些元素的 `a*x` 和 `y` 幾乎互相抵消（catastrophic cancellation），結果接近 0，例如 cpu=2.86e-6、gpu=2.66e-6。絕對誤差只有約 2e-7，但除以一個很小的數，相對誤差就變得很大。這就是 L2 p37 的公式要有 aTol 的原因：加上 aTol=1e-6 之後全部通過。
- 一般元素的差異約 1 ulp，相對誤差約 6e-8（FP32 的 machine epsilon 是 1.19e-7）。所以 rTol 只要低於約 1e-7，就會開始出現失敗。

**HW Q2：哪個 kernel 的 CPU/GPU 差異最嚴重？為什麼？** → **SAXPY**
- nvcc 預設 `--fmad=true`，GPU 把 `a*x + y` 編成一個 **FMA**（fused multiply-add）指令，最後只捨入一次。CPU 端（MSVC `/fp:precise`）是先算 `a*x` 捨入一次，再加 `y` 又捨入一次。兩種算法差一次捨入，所以大約 25% 的元素差 1 ulp。
- 證據：用 `-fmad=false` 重編之後，SAXPY 三個 N 都變成 0 個差異。用 `-G`（VS Debug build）編也一樣是 0 個差異，這也是原文要求驗證要用 Release 的原因。
- 加法 kernel 只有一次 IEEE 754 加法，兩邊都是正確捨入（round-to-nearest-even），所以結果完全相同。
- 補充：FMA 只捨入一次，其實**比較準**。「不一致」不代表 GPU 算錯，和 L2 p37 講的一樣，運算順序和硬體指令不同，就會讓浮點數的結果不同。

### 3.8 繳交（Canvas，你自己上傳）
Canvas assignment 11810625，截止 **2026-10-20 5:59 PM PDT**。

Teams 的 **Hw1 Discussion**（2026-10-20 2:35 PM PDT 讀過，只有 2 篇；這個 channel 預設藏在「Hidden channels」裡）：
- **2026-10-19 9:50 PM PDT，Colin N Reinhardt「Hw1: 4 kernels to submit」**：SUBMIT 說的「4 kernels」是 **printf、SAXPY、2D、3D**，而且 printf kernel 要**連同它的結果和 4 a–c 的回答**一起交。所以 §3.6 的三個觀察題一定要寫進答案文件，也要附 printf 的輸出截圖。
- 另一篇是作業公告，回覆在講 AWS 的連線錯誤（重試，不行就等 20 分鐘），和本機無關。
- 繳交格式（檔案類型、要不要 zip）老師沒有規定。General 裡 Keith Fife 10/20 3:27 AM 問過，到 2:33 PM 還沒有回覆。

要交的東西：
1. **答案文件**（PDF 或 docx）：Q1–Q4 附理由（§3.7）、兩題 HW Q 附數據、printf 三個問題的觀察，以及截圖：
   - `.\hw1.exe` 的完整輸出（SAXPY 的 sweep 那幾行最重要）
   - `-fmad=false` 的 SAXPY 輸出
   - `grid3d --big` 的輸出
   - printf 三種設定各一張
2. **原始碼**：只交 `kernel.cu`、`cuda_check.h`。不要交 `.slnx`、`.vcxproj`、`x64\` 和其他 build 產物。
3. 「4 kernel functions」都在 `kernel.cu` 裡：`printfKernel`、`saxpyKernel`、`matAdd2DKernel`、`gridAdd3DKernel`。想讓助教一眼看到的話，可以在答案文件裡另外貼出這 4 個函式。

### 3.9 常見問題
| 症狀 | 原因與處理 |
|---|---|
| 建立新專案的語言清單裡沒有 CUDA | §1.5（VS 2022 沒有 C++，讓 installer 中止）。重裝或升級 CUDA 之後要再做一次 |
| `unsupported Microsoft Visual Studio version! Only the versions between 2017 and 2022` | 叫到的是 CUDA 12.9 的 nvcc：終端機是安裝前開的，或 PATH 裡 12.9 排在前面。開新的終端機，用 `where nvcc` 確認 |
| `cl` 顯示 19.51.36248 或 `for x86` | 開到 Build Tools 或 x86 的 prompt（§1.4） |
| `'hw1.exe' is not recognized` | 改成 `.\hw1.exe`（§1.6） |
| `no kernel image is available for execution on the device` | Code Generation 裡沒有 PTX，或 driver 太舊沒辦法 JIT。用預設的 `compute_75,sm_75`（含 PTX），並確認 `nvidia-smi` 顯示 CUDA 13.4 以上 |
| `checkCuda` 一堆 compile error | 用到舊版 L1 p55（只有一個參數）。用這份的 `cuda_check.h`（`const char*`） |
| `--big` 出現 `malloc … failed` | host 記憶體不夠，需要約 12 GB 可用。先關掉其他程式 |
| printf 沒有輸出 | launch 之後要 `cudaDeviceSynchronize()`，device printf 的 buffer 才會 flush（`CHECK_KERNEL` 已經處理） |
| 一大堆 C4819 | 中文 Windows 的字碼頁問題，可以忽略；命令列加 `-Xcompiler /utf-8` |

---

GPU 課禁止用 AI 產生作業解答；這份 runbook 和 `src/` 的參考程式碼都是 AI 產生的，要不要用、怎麼用由你自己決定。
