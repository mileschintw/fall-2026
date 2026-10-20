# GPU HW0 + HW1 本機 Runbook（Windows GPU box）

> 2026-10-20 PT 寫成。HW1 截止 **2026-10-20（二）5:59 PM PDT**。
> 作業說明：[hw0/README.md](hw0/README.md)、[hw1/README.md](hw1/README.md)。這份只講「在這台電腦上怎麼做完」。
> 程式碼都已經寫好，也在本機 RTX 3050 上實測過（WSL、CUDA 12.8）：
> - HW1：[hw1/src/kernel.cu](hw1/src/kernel.cu)、[hw1/src/cuda_check.h](hw1/src/cuda_check.h)
> - HW0：[hw0/src/kernel.cu](hw0/src/kernel.cu)（預設 template，見 §0.4）、[hw0/src/devicequery.cu](hw0/src/devicequery.cu)

---

## 0. 本機環境現況（2026-10-20 實測）

| 項目 | 狀態 |
|---|---|
| GPU | NVIDIA GeForce RTX 3050，8 GB，**CC 8.6**（AWS 是 T4、CC 7.5） |
| Driver | 610.47，支援到 CUDA 13.3 |
| CUDA Toolkit（Windows） | v12.9（在 PATH 上）、v11.8 |
| Visual Studio 2022 Community 17.12 | IDE 有裝，但**沒有 C++ toolset**（`VC\Tools\MSVC` 不存在），沒有 CUDA 專案範本 |
| VS 18（2026）BuildTools | MSVC 19.51（14.51.36231） |
| WSL Ubuntu | CUDA 12.8（`/usr/local/cuda`），`nvidia-smi` 看得到 RTX 3050，RAM 15 GB |
| RAM | 32 GB |

### 0.0 AWS WorkSpaces 的環境（使用者 2026-10-20 03:47 PDT 在 AWS 上實測）
| 項目 | AWS |
|---|---|
| GPU | Tesla T4，15360 MiB，**WDDM** 模式 |
| Driver | **596.36**（CUDA Version: 13.2） |
| CUDA Toolkit | **13.4, V13.4.92**（`Built on Sun_Sep_01_02:23:07_Pacific_Standard_Time_2026`） |
| Visual Studio | **Visual Studio Community 2026 18.10.3**（vswhere `catalog_productDisplayVersion`），裝在 `C:\Program Files\Microsoft Visual Studio\18\Community` |
| MSVC | **19.51.36260** for x64（在「Visual Studio 2026 Developer Command Prompt v18.10.3」執行 `cl`） |

本機的 VS 18 BuildTools 18.7.1 是 MSVC **19.51.36248**（toolset 14.51.36231），和 AWS 同屬 19.51，只差 build 號。

注意：AWS 的 driver（13.2）比 toolkit（13.4）**舊**，靠的是 CUDA minor version compatibility。編出來的 sm_75 SASS 可以直接跑，但 13.4 產生的 PTX 沒辦法在這個 driver 上 JIT。

### 0.1 為什麼現在 Windows 上直接 `nvcc` 會失敗
試過的結果：
```
nvcc hello.cu                              -> host_config.h: unsupported Microsoft Visual Studio version! Only 2017–2022
nvcc -allow-unsupported-compiler hello.cu  -> MSVC type_traits: "operator may not be a static member function"（或 cudafe++ ACCESS_VIOLATION）
```
VS 18 BuildTools 的 MSVC 14.51 STL 一律用 C++23 的 `static operator()`，CUDA 12.9 的前端（cudafe++）解析不了，**沒有 flag 可以繞過**。要在 Windows 上編譯，二選一：

| 路線 | 做法 | 適合 |
|---|---|---|
| **A. WSL**（現在就能用，已實測） | 在 WSL 裡用 CUDA 12.8 的 `nvcc` | 今天先把 HW1 做完 |
| B. VS 2022 + C++ workload（退而求其次，**未實測**） | 在 VS 2022 加裝「使用 C++ 的桌面開發」（MSVC v143），再補裝 CUDA 12.9 的 VS integration | 要 VS IDE、debugger、CUDA 專案範本（HW0 的 debugger 段、之後整學期） |
| **C. VS 2026 Community 18.10.3 + CUDA 13.4（V13.4.92）**（推薦，和 AWS 一致，**未實測**） | 安裝時勾「使用 C++ 的桌面開發」；裝完把 CUDA 13.4 的 Visual Studio Integration 一起裝上。**driver 不用更新**：610.47 比 AWS 的 596.36 還新。Code Generation 填 `compute_75,sm_75;compute_86,sm_86`（13.4 產生的 PTX 在 13.3 的 driver 上不能 JIT，所以本機要直接帶 sm_86 的 SASS） | 想跟 AWS 版本完全一致 |

### 0.2 Arch flag：本機和 AWS 不一樣
- 本機 RTX 3050：`-arch=sm_86`（VS 裡寫 `compute_86,sm_86`）
- AWS T4：`compute_75,sm_75`（L2 [00:43:21]）
- 一個執行檔兩邊都能跑：`-gencode arch=compute_75,code=sm_75 -gencode arch=compute_86,code=sm_86`

### 0.3 路線 B 的安裝步驟（大約 20–40 分鐘，要系統管理員權限）
> **未實測**：這台電腦還沒裝 v143，所以這一節和後面所有「Windows（路線 B）」的指令、VS IDE 步驟、PowerShell 迴圈都沒有實際跑過。實際跑過的只有 WSL（路線 A）。
1. 開「Visual Studio Installer」→ **Visual Studio Community 2022** → **修改**。
2. 勾 **使用 C++ 的桌面開發**（Desktop development with C++）。右邊確認有勾 **MSVC v143 - VS 2022 C++ x64/x86 建置工具**、**Windows 11 SDK**。按「修改」。
3. 補 CUDA 的 VS integration（CUDA installer 只會整合到「安裝當下已經有 C++ 的 VS」）：
   - 重跑 CUDA 12.9 的 installer（沒有的話到 NVIDIA 的 CUDA Toolkit Archive 下載 12.9 的 Windows x86_64 exe）→ **自訂（Custom）** → 只勾 **CUDA → Visual Studio Integration**（Nsight VSE 也可以勾）→ 安裝。
4. 驗證：
   - 開 **x64 Native Tools Command Prompt for VS 2022**（開始選單搜尋），執行 `cl` 會顯示 `Version 19.4x`，執行 `nvcc --version` 會顯示 12.9。
   - 開 VS 2022 → 建立新專案 → 語言選 **CUDA** → 看得到 **CUDA 12.9 Runtime**，就代表裝好了（L1 [02:39:00]：看得到這個範本就代表環境正常）。
   - 如果 `cl` 顯示 19.5x（叫到 BuildTools 18 的那一個），表示你開到的是 VS 18 的 prompt，改開 VS 2022 的 prompt，或執行：
     `"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"`
5. 中文 Windows（cp950）編譯時會冒出一堆 `warning C4819`，無害；加 `-Xcompiler /utf-8` 就不會出現。

### 0.4 預設 `kernel.cu`
本機沒有 CUDA 專案範本，所以 [hw0/src/kernel.cu](hw0/src/kernel.cu) 是**我依標準 VS CUDA Runtime 範本重建的**，並且用 HW0 原文的行號核對過：第 11 行 `int i = threadIdx.x;`、第 17 行 `arraySize`、第 18–20 行 `a`/`b`/`c`、第 29 行 `printf`、第 46 行 `int *dev_a = 0;`、第 66 行是 `cudaMalloc(dev_a)` 之後的 `if`。走路線 B 時，改用 VS 產生的真正範本；兩者如果有差異，以 VS 產生的為準。

---

## 1. 路線 A：WSL 建置（現在就能用）

每次開新的 WSL shell 都要先設 PATH（login shell 預設找不到 `nvcc`）：
```bash
wsl.exe -d Ubuntu
```
進到 WSL 之後：
```bash
export PATH=/usr/local/cuda/bin:$PATH
nvcc --version          # 應該顯示 release 12.8
nvidia-smi -L           # 應該顯示 GPU 0: NVIDIA GeForce RTX 3050
```
建一個工作資料夾，把 repo 裡的檔案複製過去（不要在 repo 裡 build，免得產物混進 git）：
```bash
mkdir -p ~/gpu && cp -r /mnt/d/Repos/fall-2026/gpu/hw/hw0/src ~/gpu/hw0 && cp -r /mnt/d/Repos/fall-2026/gpu/hw/hw1/src ~/gpu/hw1
```

---

## 2. HW0（不計分、不用交）

HW0 的段落和本機上的對應：

| HW0 段落 | 原文步驟 | 本機怎麼做 |
|---|---|---|
| AWS WorkSpaces | 1–5 | 本機不需要。要用 AWS 的話照 [hw0/README.md](hw0/README.md) §1 |
| VS 建專案、build | 6–18 | 路線 B 裝好後照原文做（`C:\Au26_GPU`、Solution `Au26_GPUCompute`、Project `EX1_vecadd_cudart`）。範本名稱是「CUDA 12.9 Runtime」，不是 13.x |
| VS debugger | 19–38 | 只能用路線 B（或 AWS）。原文問題的答案在 §2.3 |
| nvcc 命令列 | 39 | §2.1 |
| cuobjdump | — | §2.1 |
| C 指標與陣列 | 40–58 | §2.2 |
| Device Query | p8–p9 | §2.4 |
| nvidia-smi | p9–p10 | 任何 terminal 直接執行 `nvidia-smi` |

### 2.1 nvcc + cuobjdump（步驟 39 與 Binary Tools 段）
WSL：
```bash
cd ~/gpu/hw0 && nvcc -arch=sm_86 -o vecadd kernel.cu -run
```
Windows（路線 B，未實測；x64 Native Tools prompt。先把 `gpu\hw\hw0\src` 複製到 repo 外面，例如 `C:\Au26_GPU\hw0`，再 `cd` 過去，build 產物才不會跑進 git）：
```bash
nvcc -arch=sm_86 -Xcompiler /utf-8 -o vecadd kernel.cu -run
```
預期輸出：`{1,2,3,4,5} + {10,20,30,40,50} = {11,22,33,44,55}`。Windows 上會多出 `vecadd.exe`、`vecadd.exp`、`vecadd.lib`。

cuobjdump（Windows 的檔名加 `.exe`；原文 PDF 的 `-–dump-ptx` 是 en dash，要自己打兩個 `-`）：
```bash
cuobjdump -lptx vecadd
```
```bash
cuobjdump -lelf vecadd
```
```bash
cuobjdump --dump-ptx vecadd
```
```bash
cuobjdump --dump-sass vecadd
```
實測 `-lptx` 列出 `vecadd.1.sm_86.ptx`，`-lelf` 列出 `sm_86.cubin`。在 AWS 上會是 sm_75。

### 2.2 C 指標與陣列（步驟 40–58），實測結果
每一步改完 [hw0/src/kernel.cu](hw0/src/kernel.cu) 都用 `nvcc -arch=sm_86 -o addvec kernel.cu`（Windows 再加 `-Xcompiler /utf-8`）重編，然後執行 `./addvec`。改之前先 `cp kernel.cu kernel_orig.cu` 留一份原檔。

| 步驟 | 改動 | 實測輸出 | 為什麼 |
|---|---|---|---|
| 42–44 | 第 18–20 行註解掉，改成 `int* a = 0;`（b、c 同樣） | build 成功 | `addWithCuda(int*, const int*, const int*, …)` 本來就收指標；陣列名稱傳進函式時本來就會 decay 成指標，所以型別一樣，compiler 不會抱怨。NULL 是合法的指標值，只是不能 dereference |
| 45–46 | 執行 | `cudaMemcpy failed!addWithCuda failed!` | `cudaMemcpy(dev_a, a=NULL, …, HostToDevice)` 從 NULL 讀 host 記憶體，回傳 invalid argument。錯誤要到 runtime 才看得出來 |
| 47–50 | 改成 `(int*)malloc(arraySize * sizeof(int))`（需要 `#include <stdlib.h>`） | `{1,2,3,4,5} + {10,20,30,40,50} = {0,0,0,0,0}` | 記憶體有配置了，但 malloc **不會初始化**：a、b 內容未定義（這次剛好是 0，也可能是垃圾值），c = a + b。printf 的 `{1,2,3,4,5}` 字樣是寫死在字串裡的，不是真的值 |
| 51–53 | 加 `for (int x = 0, *pa = a, *pb = b; …) { *pa++ = x + 1; *pb++ = 10 * (x + 1); }` | `… = {11,22,33,44,55}` | `pa`、`pb` 從 a、b 的開頭開始，`*pa++` 寫入目前位置再往後移一個 int，所以 a = 1..5、b = 10..50。WSL/gcc 實測沒有 warning；原文說的 warning 應該出現在 MSVC，內容沒有核對過。另外要注意 a、b、c 都沒有 `free()`（memory leak） |
| 54–56 | printf 改成印出 `a[0..4]`、`b[0..4]`、`c[0..4]` | `{1,2,3,4,5} + {10,20,30,40,50} = {11,22,33,44,55}` | 現在印的是真的記憶體內容。`a[i]` 就是 `*(a + i)`，所以指標可以直接用陣列語法 |
| 57–58 | 在 VS 裡 Rebuild，再用 Local Windows Debugger 執行 | 輸出相同 | — |

### 2.3 Debugger 段（步驟 19–38）的「Why?」
只有路線 B 或 AWS 才能實際操作。答案：
- **22：為什麼停在 `main()` 開頭？**（**沒有實際核對過**，要在 VS 裡確認）原文第 23 步說按 Continue 之後會停在第 17 行，所以第 17 行本身有綁到 breakpoint。比較可能的原因是 VS CUDA 範本的 debug 設定在進入點中斷（類似用 F10/F11 啟動 debugger 時的 break at entry），或者是 Debug build 在 `main` 的 `{` 插入了初始化程式碼（stack 檢查、Just My Code）。請在 VS 裡看 Call Stack 和 Disassembly 確認。
- **22b：為什麼第 11 行的 breakpoint 不見了？** 第 11 行在 `__global__ addKernel` 裡，是 GPU 上跑的程式碼。Local Windows Debugger 只 debug CPU（host）端，device code 的 breakpoint 要用 Nsight（Extensions → Nsight → Start CUDA Debugging，而且要 Debug build，並開 `-G`）。
- **33b：`&dev_a` 沒變，`dev_a` 卻變了？** `&dev_a` 是 host stack 上那個指標變數本身的位址，固定不變。`dev_a` 是它存的值：一開始是 0，`cudaMalloc((void**)&dev_a, …)` 把 GPU 記憶體的位址寫進去，所以值變了。這也是為什麼要傳 `&dev_a`：函式要改的是呼叫端的變數。

### 2.4 Device Query
WSL：
```bash
cd ~/gpu/hw0 && nvcc -arch=sm_86 -o devicequery devicequery.cu && ./devicequery
```
Windows（路線 B）：
```bash
nvcc -arch=sm_86 -Xcompiler /utf-8 -o devicequery.exe devicequery.cu
```
本機實測（WSL）：
```
CUDA devices: 1
=== Device 0: NVIDIA GeForce RTX 3050 ===
  Driver / Runtime version     : 13.3 / 12.8
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
注意：
- 原文的 `maxThreadDim`、`warpsize` 是錯字，實際欄位是 `maxThreadsDim`、`warpSize`。
- `cudaInitDevice` 要三個參數 `(device, deviceFlags, flags)`，CUDA 12.0 以後才有。
- AWS T4 的 CC 會是 7.5（L2 [03:13:00]）。

---

## 3. HW1（11 分，今天 5:59 PM PDT 截止）

### 3.1 檔案與結構
| 檔案 | 內容 |
|---|---|
| [hw1/src/cuda_check.h](hw1/src/cuda_check.h) | L1 updated p55 的 `checkCuda(cudaError_t, const char* srcStr)`（投影片寫 `char*`，傳字串常值在 C++ 會 compile error，所以改成 `const char*`），加上 `CHECK_CUDA(call)`（失敗就 exit，Release build 的 `assert` 會被拿掉，所以要靠它）和 `CHECK_KERNEL(name)`（`cudaGetLastError` + `cudaDeviceSynchronize`） |
| [hw1/src/kernel.cu](hw1/src/kernel.cu) | 預設範例的 `main`/`addWithCuda` 改成全部用 `checkCuda` 包起來，另外加 4 個 kernel、CPU 版本和驗證 |

對照 HW1 原文的要求：

| 原文要求 | kernel.cu 裡的位置 |
|---|---|
| 2.1 checkCuda 放 `.h`、`main`/`addWithCuda` 都用它 | `#include "cuda_check.h"`；`addWithCuda()` 每個呼叫都用 `checkCuda(…, "說明")` |
| printf kernel（tid、bid、GTID 印在同一行） | `printfKernel`：`gtid = blockIdx.x * blockDim.x + threadIdx.x` |
| SAXPY，kernel 參數要有 N 做邊界檢查 | `saxpyKernel(int n, float a, const float* x, float* y)`，`if (i < n)` |
| 2D add，參數 M、N，2D 邊界檢查 | `matAdd2DKernel(C, A, B, M, N)`，x→col、y→row，`idx = row*N + col` |
| 3D add，參數 M、N、P，用 `dim3` | `gridAdd3DKernel(C, A, B, M, N, P)`，`idx = (z*M + y)*N + x`，`dim3 block(16,8,4)` |
| host 動態配置、初始化成已知值、每個 malloc 都有 free | `hostAlloc` + `fillRandom`（固定 seed 的亂數，可以重現）；每個 test 結尾都有 `free` / `cudaFree` |
| 明確寫 HtoD／DtoH（L2 [02:40:16]） | 全部用 `cudaMemcpyHostToDevice` / `cudaMemcpyDeviceToHost` |
| CPU 循序版本 + tolerance 驗證（L2 p37） | `saxpyCPU`、`addCPU`、`verify()`：`|cpu-gpu| <= max(aTol, rTol*max(|cpu|,|gpu|))`，預設 rTol=1e-5、aTol=1e-6，另外跑一次 tolerance sweep |
| 測資 | SAXPY 10 / 1e3 / 1e7；2D 4×4 / 500×500 / 3024×4032；3D 3³ / 100³ / 1000³（`--big`） |

設計說明（寫報告會用到）：
- 輸入用固定 seed 的亂數浮點數，不用小整數。小整數的乘加在 float 裡是精確的，CPU 和 GPU 一定完全一致，HW Q 就沒有東西可以觀察。
- 1000³ 的 3D：每個陣列 4 GB，A、B、C 共 12 GB。T4 有 16 GB 放得下，本機 RTX 3050 只有 8 GB，所以程式會先用 `cudaMemGetInfo` 看剩多少，放不下就**沿 z 切成 slab**分批處理。每個 slab 都是連續的 M×N×Pslab 子體積，用同一個 3D kernel 和 3D 邊界檢查。host 端只配 3 個陣列：CPU 結果直接覆寫 B，總共約 12 GB。
- 所有 byte 數和 index 都用 `size_t`（1e9 × 4 bytes 會超過 `int` 範圍）。

### 3.2 建置與執行

**WSL（路線 A，已實測）**
```bash
cd ~/gpu/hw1 && nvcc -O3 -DNDEBUG -arch=sm_86 -o hw1 kernel.cu
```
```bash
./hw1 | tee run_all.txt
```
```bash
./hw1 grid3d --big | tee run_big.txt
```
`--big` 本機實測約 1 分鐘，host 記憶體峰值 11.8 GB。WSL 只有 15 GB，執行時先把其他吃記憶體的程式關掉。

FMA 對照組（HW Q 用）：
```bash
nvcc -O3 -DNDEBUG -fmad=false -arch=sm_86 -o hw1_nofma kernel.cu && ./hw1_nofma saxpy | tee run_nofma.txt
```

**Windows 命令列（路線 B，未實測）**：開 x64 Native Tools Command Prompt for VS 2022，先把 repo 的檔案複製到 repo 外面再 build（`.exe`、`.exp`、`.lib` 才不會跑進 git）：
```bash
xcopy D:\Repos\fall-2026\gpu\hw\hw1\src C:\Au26_GPU\hw1\ /I /Y
```
```bash
cd /d C:\Au26_GPU\hw1
```
```bash
nvcc -O3 -DNDEBUG -Xcompiler "/O2 /fp:precise /utf-8" -gencode arch=compute_75,code=sm_75 -gencode arch=compute_86,code=sm_86 -o hw1.exe kernel.cu
```
```bash
hw1.exe
```
```bash
hw1.exe grid3d --big
```

**Visual Studio IDE（路線 B 未實測，或在 AWS 上）**
1. 在 `Au26_GPUCompute` solution 上按右鍵 → Add → New Project → **CUDA 12.9 Runtime**（AWS 上是 13.x），取名例如 `HW1`。
2. Solution Explorer → `HW1` 按右鍵 → Add → New Item → **Header File (.h)** → 命名為 `cuda_check.h`，把 [hw1/src/cuda_check.h](hw1/src/cuda_check.h) 的內容貼進去。
3. 把 VS 產生的 `kernel.cu` 整份換成 [hw1/src/kernel.cu](hw1/src/kernel.cu)。
4. 上方工具列 **Debug → Release**、平台 **x64**。
5. `HW1` 按右鍵 → Properties → **CUDA C/C++ → Device → Code Generation**：本機填 `compute_86,sm_86`，AWS 填 `compute_75,sm_75`。
6. 要帶參數（例如 `grid3d --big`）：Properties → **Debugging → Command Arguments**。
7. Build → Build Solution，再按 **Ctrl+F5**（Start Without Debugging，視窗不會一閃就關掉）。
8. FMA 對照組：Properties → **CUDA C/C++ → Command Line → Additional Options** 填 `-fmad=false`，Rebuild。做完記得拿掉。

**一定要用 Release 驗證**（原文 p5）：VS 的 Debug 設定會對 device code 加 `-G`。實測 `nvcc -G` 編出來的 SAXPY，三個 N 都是 **0 個差異**，因為 `-G` 會關掉 FMA 合併。所以用 Debug build 什麼差異都看不到，兩題 HW Q 也就沒有數據可以寫。

### 3.3 printf kernel：跑 10 次並觀察
WSL：
```bash
for i in $(seq 10); do ./hw1 printf 1 32 1 | grep GTID | sed 's/.*GTID=//' | tr -d ' ' | tr '\n' ' '; echo; done
```
（把 `1 32` 換成 `4 8`、`32 1` 再各跑一次。這行只印每次執行的 GTID 順序。要截完整輸出的話，執行 `./hw1 printf 4 8 10`。）

Windows（PowerShell，未實測）：
```powershell
1..10 | % { (.\hw1.exe printf 32 1 1 | Select-String GTID | % { ($_.Line -split 'GTID=')[1].Trim() }) -join ' ' }
```

本機實測（每列是一次執行的 GTID 順序）：

| 設定 | 結果 |
|---|---|
| `<<<1,32>>>` | 每次都是 `0 1 2 … 31` |
| `<<<4,8>>>` | 每次都是 `8..15, 24..31, 0..7, 16..23`：block 內按 thread 順序，block 之間的順序是 1,3,0,2 |
| `<<<32,1>>>` | 每次都不一樣，例如 `15 17 19 1 13 5 7 9 16 …` 和 `17 7 27 13 19 15 3 9 5 …` |

這三個觀察題的答案方向（用你自己跑出來的結果寫）：
- **(a) 一致嗎？可預測嗎？** 同一個 block（同一個 warp）裡的 thread 會照 lane 順序印出來，因為 32 個 thread 同時執行同一個 printf。不同 block 的順序由硬體 scheduler 決定：`<<<4,8>>>` 在這台機器上剛好每次相同，但不是照 0,1,2,3；`<<<32,1>>>` 每次都不同。**都不保證**（L2 [03:23:07]：kernel printf 順序沒有保證）。
- **(b) block 和 thread index 的行為不同嗎？** 不同。block 是獨立排程到各個 SM 的單位，執行順序任意。同一個 warp 內的 thread 是 lockstep（SIMT），所以看起來有順序，但這是實作細節，CUDA 沒有保證。
- **(c) 對 kernel 的計算有什麼含意？** kernel 的正確性不能依賴 thread 或 block 的執行順序。每個 thread 只能寫自己 GTID 對應的輸出（就像這次 3 個數學 kernel 的寫法）；跨 block 沒有同步也不能互相等結果；需要合作的話要用 `__syncthreads()`（block 內）、atomic 操作，或拆成多次 kernel launch。

### 3.4 實測輸出摘要（WSL、RTX 3050、Release `-O3`）
```
=== default template: addWithCuda ===
{1,2,3,4,5} + {10,20,30,40,50} = {11,22,33,44,55}

=== SAXPY  N=10 ===          not bit-identical=1 (10%)      max rel=8.740e-08
  sweep (aTol=0):  1e-05 pass  1e-06 pass  1e-07 pass  5e-08 FAIL(1)  1e-08 FAIL(1)  0 FAIL(1)
=== SAXPY  N=1000 ===        not bit-identical=273 (27.3%)  max rel=5.485e-06
  sweep (aTol=0):  1e-05 pass  1e-06 FAIL(2)  1e-07 FAIL(97)  5e-08 FAIL(273) ...
=== SAXPY  N=10000000 ===    not bit-identical=2520379 (25.2%)  max|diff|=3.815e-06  max rel=7.165e-02
  worst at i=5734209: cpu=2.86102295e-06 gpu=2.65604103e-06
  sweep (aTol=0):  1e-05 FAIL(3569)  1e-06 FAIL(35434)  1e-07 FAIL(815715) ...
  （三個 N 在 rTol=1e-5、aTol=1e-6 下都 PASSED）

=== 2D 4x4 / 500x500 / 3024x4032 ===  not bit-identical=0，tolerance 0 也 pass
=== 3D 3^3 / 100^3 ===                 not bit-identical=0，tolerance 0 也 pass
=== 3D 1000^3 (--big) ===  device free 7.53/8.59 GB, need 12.00 GB -> z-slabs (slab depth 502)
                           grid(63,125,126) block(16,8,4)  not bit-identical=0  PASSED

=== -fmad=false 的 SAXPY ===  三個 N 都是 not bit-identical=0
```
Windows（MSVC `/fp:precise`）上跑出來的數字應該相同：同一張 GPU，CPU 端一樣是一次乘、一次加，各捨入一次。實際以你截圖的結果為準。

### 3.5 書面題答案（每題都要附理由）
**Q1 → A** `i = blockIdx.x*blockDim.x + threadIdx.x`
前面有 `blockIdx.x` 個 block，每個 block 有 `blockDim.x` 個 thread，所以這個 block 的第一個元素是 `blockIdx.x*blockDim.x`，再加上 block 內的偏移 `threadIdx.x`。B 沒有用到 block；C 用乘的，會重複（例如 thread 0 不管在哪個 block 都是 0）；D 不同 block 會重疊。

**Q2 → D** `i = (blockIdx.x*blockDim.x + threadIdx.x)*2`
每個 thread 處理相鄰兩個元素 `i`、`i+1`，所以 global thread id g 負責 `2g`、`2g+1`，第一個元素是 `2g`。例如 blockDim=4：block 0 的 thread 0..3 → 0,2,4,6；block 1 的 thread 0 → (4+0)*2 = 8，剛好接續。C 會讓同一個 block 的 thread 處理連續的 i（不是間隔 2），A、B 不成立。

**Q3 → A** `i = blockIdx.x*blockDim.x*2 + threadIdx.x`
每個 block 負責 `2*blockDim.x` 個連續元素，所以 block 的起點是 `blockIdx.x*2*blockDim.x`。第一個 section 裡 thread t 處理起點 + t，第二個 section 再處理 `i + blockDim.x`。這種排法讓相鄰 thread 存取相鄰位址（coalesced）。

**Q4 → A 8192**
block 數 = ⌈8000/1024⌉ = ⌈7.8125⌉ = 8，8 × 1024 = 8192 個 thread。多出來的 192 個 thread 靠 kernel 裡的 `if (i < n)` 擋掉。

**HW Q1：tolerance 設到多少時驗證開始失敗？**（數字用你自己的截圖；以下是本機結果）
- 2D 和 3D 加法：CPU 和 GPU 結果**逐 bit 相同**，tolerance 設成 0 也不會失敗。
- SAXPY（aTol=0，只調 rTol）：N=10 在 rTol < 約 8.7e-8 時開始失敗（5e-8 失敗）；N=1e3 在 rTol=1e-6 開始失敗；N=1e7 連 rTol=1e-5 都有 3569 個失敗。
- N=1e7 的最大相對誤差高達 7e-2，因為有些元素的 `a*x` 和 `y` 幾乎互相抵消（catastrophic cancellation），結果接近 0（例如 cpu=2.86e-6、gpu=2.66e-6），絕對誤差只有約 2e-7，但除以一個很小的數，相對誤差就很大。這就是 L2 p37 公式要有 aTol 的原因：加上 aTol=1e-6 之後全部通過。
- 一般元素的差異大約是 1 ulp（相對誤差約 6e-8，FP32 的 machine epsilon 是 1.19e-7）。所以只要 rTol 低於約 1e-7，就會開始出現失敗。

**HW Q2：哪個 kernel 的 CPU/GPU 差異最嚴重？為什麼？** → **SAXPY**
- nvcc 預設 `--fmad=true`，GPU 把 `a*x + y` 編成一個 **FMA**（fused multiply-add）指令，只在最後捨入一次。CPU 端（MSVC `/fp:precise`、gcc x86-64 預設）是先算 `a*x`、捨入，再加 `y`、再捨入一次。兩種算法差一次捨入，所以約 25% 的元素差 1 ulp。
- 證據：用 `-fmad=false` 重編之後，SAXPY 三個 N 都變成 0 個差異（截圖 `run_nofma.txt`）。用 `-G`（VS Debug build）編也一樣是 0 個差異，這就是原文要求驗證用 Release 的原因。
- 加法 kernel 只有一個 IEEE 754 加法，兩邊都是正確捨入（round-to-nearest-even），所以結果完全相同。
- 補充：FMA 只捨入一次，其實**比較準**。「不一致」不代表 GPU 錯了；和 L2 p37 講的一樣，運算順序和硬體指令不同就會讓浮點數結果不同。

### 3.6 繳交（Canvas，你自己上傳）
Canvas assignment 11810625，截止 **2026-10-20 5:59 PM PDT**。

上傳前：
- 原始碼只用 **gcc（WSL）+ CUDA 12.8** 編譯過。助教很可能用 MSVC + CUDA 13.x（AWS、sm_75）來 build。如果有時間，先在 AWS（或裝好路線 B 之後）用 VS Release build 跑一次，確認能編譯。
- Teams 的 **Hw1 Discussion** channel 還沒讀過（`digests/2026-10-20.md`：SharePoint 顯示 10/17 有活動）。老師或 TA 在那裡的回覆優先於 PDF，交之前花兩分鐘看一下，有沒有改繳交格式、1e9 測資，或 printf 題要不要書面回答。

要交：
1. **答案文件**（PDF 或 docx）：Q1–Q4 附理由（§3.5）、兩題 HW Q 附數據、printf 三個問題的觀察、截圖：
   - `./hw1` 全部輸出（SAXPY 的 sweep 那幾行最重要）
   - `-fmad=false` 的 SAXPY 輸出
   - `grid3d --big` 輸出
   - printf 三種設定各一張
2. **原始碼**：只交 `kernel.cu`、`cuda_check.h`。不要交 `.sln`、`.vcxproj`、`x64/` 和 build 產物。
3. 「4 kernel functions」就在 `kernel.cu` 裡：`printfKernel`、`saxpyKernel`、`matAdd2DKernel`、`gridAdd3DKernel`。如果想讓助教一眼看到，可以另外在答案文件裡貼出這 4 個函式。

### 3.7 常見問題
| 症狀 | 原因與處理 |
|---|---|
| `unsupported Microsoft Visual Studio version` / `static member function` | 叫到 VS 18 的 MSVC 19.51。改用 VS 2022 的 prompt（§0.3），或走 WSL |
| `nvcc: command not found`（WSL） | 沒設 `export PATH=/usr/local/cuda/bin:$PATH` |
| `no kernel image is available for execution on the device` | arch 不對：本機要 sm_86，AWS 要 sm_75，或用 §0.2 的雙 gencode |
| `checkCuda` 一堆 compile error | 用到舊版 L1 p55（只有一個參數）或 `char*`。用這份的 `cuda_check.h` |
| `--big` 出現 `malloc … failed` | host 記憶體不夠（需要約 12 GB 可用）。關掉其他程式；WSL 可以在 `%UserProfile%\.wslconfig` 調高 `memory=` |
| printf 沒有輸出 | launch 之後要 `cudaDeviceSynchronize()`，device printf 的 buffer 才會 flush（`CHECK_KERNEL` 已經有做） |
| 中文 Windows 一堆 C4819 | 加 `-Xcompiler /utf-8` |

---

GPU 課禁止用 AI 產生作業解答；這份 runbook 和 `src/` 的程式碼都是 AI 產生的，要不要用、怎麼用由你自己決定。
