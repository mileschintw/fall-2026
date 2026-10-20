# 照作業原文使用 runbook（HW0 + HW1 逐步對照）

> 2026-10-20 PDT。這份是 [local-runbook.md](local-runbook.md) 的使用說明：照作業原文的順序，一步一步對到 runbook 的段落。
> 原文：[hw0/spec.md](hw0/spec.md)（Canvas file 154009274，[PDF](hw0/spec.pdf)）、[hw1/spec.md](hw1/spec.md)（Canvas assignment 11810625，[PDF](hw1/spec.pdf)）。下面的「L123」是 spec.md 的行號，「p4」是 PDF 頁碼。
> 環境配置（runbook §0–§1）已經完成，這份全部跳過。

## 怎麼用

1. **以原文為主線**：開 `spec.md`（或 PDF），從頭往下讀。每讀到一段，就到下面的表格找同一列。
2. **每一列有三欄**：
   - **原文**：PDF 頁碼、spec.md 行號，加上那一段要你做什麼。
   - **runbook**：去 runbook 的哪一節。
   - **動作 → 預期**：要執行的指令或要點的選單，加上本機實測會看到的結果。結果對不上，就先看 runbook §3.9 的常見問題。
3. **兩種標記**：
   - **✍️**：這一步有要寫進答案的東西。runbook 只給答案方向和本機數據，交出去要用你自己跑出來的截圖和文字。
   - **⚠️**：原文和實際情況不一樣，以 runbook 的實測為準。
4. **衝突時的採信順序**：老師上課說的 > Teams/Piazza 上老師或 TA 的回覆 > 原文 PDF > runbook。runbook 的「實測」只代表這台電腦的結果。

做的順序：
- HW0 不計分，可以跳過。不過 HW1 原文 p2 要你「從 HW0 那樣的新專案開始」，所以至少要做過 HW0 的步驟 6–18。
- HW1 照原文的順序做：Questions → Programming → SUBMIT。

---

## HW0：Preliminaries and Refreshers（不計分、不用交）

| 原文 | runbook | 動作 → 預期 |
|---|---|---|
| p1 [L15](hw0/spec.md#L15) Learning Objectives | — | 只是說明，沒有要做的事 |
| p1 [L30](hw0/spec.md#L30) Development Resources：VS 2026 ≥ 18.10.2、CUDA ≥ 13.4.2 | §0 | 已經符合：18.10.3、13.4.2 |
| p1–p2 [L40](hw0/spec.md#L40)–[L66](hw0/spec.md#L66) 步驟 1–5：AWS WorkSpaces 登入、配額、4 小時限制、登出 | §2 開頭的表格 | **本機不需要，全部跳過** |
| p2 [L70](hw0/spec.md#L70)–[L75](hw0/spec.md#L75) 步驟 6–9：開 VS，建新專案，語言選 CUDA，選 CUDA 13.x Runtime | §2.1 | 開始功能表 → Visual Studio 2026 → 建立新專案 → 語言下拉選 **CUDA** → **CUDA 13.4 Runtime** → 下一步。如果清單裡沒有 CUDA，看 §1.5 |
| p2 [L76](hw0/spec.md#L76)–[L83](hw0/spec.md#L83) 步驟 10–13：位置 `C:\Au26_GPU`、取消勾選「放在相同目錄」、Solution 名稱 `Au26_GPUCompute`、Project 名稱 `EX1_vecadd_cudart`，按 Create | §2.1、§1.6 | 照原文填。這幾欄 runbook 沒有實際操作過 |
| p2–p3 [L84](hw0/spec.md#L84) 步驟 14：用檔案總管看 `.sln`、`.vcxproj` | §2.1 | ⚠️ VS 2026 產生的是 **`.slnx`**，不是 `.sln` |
| p3 [L93](hw0/spec.md#L93) 步驟 15：讀懂 `kernel.cu`，認識 Solution Explorer | §2.1 | 範本內容和 [hw0/src/kernel.cu](hw0/src/kernel.cu) 相同。行號：11 `threadIdx`、17 `arraySize`、18–20 `a/b/c`、29 `printf`、46 `dev_a` |
| p3 [L109](hw0/spec.md#L109)–[L112](hw0/spec.md#L112) 步驟 16–18：建置方案，看到 `1 succeeded` | §2.1 | 建置 → 建置方案 → 中文介面顯示「成功 1 個，失敗 0 個」。一大堆 C4819 可以忽略 |
| p3 [L115](hw0/spec.md#L115) 步驟 19：在第 11、17、29、46、66 行設中斷點 | §2.2 | 點最左邊的灰色欄位，出現紅點 |
| p3–p4 [L123](hw0/spec.md#L123) 步驟 20：中斷點的 Conditions | §2.2 | 照原文做（runbook 沒有實際操作過） |
| p4 [L131](hw0/spec.md#L131)–[L132](hw0/spec.md#L132) 步驟 21–22：按 Local Windows Debugger。為什麼停在 `main()`？為什麼第 11 行的中斷點不見了？ | §2.2「22 / 22b」 | 停在第 16 行。✍️ 原因：第 11 行在 `__global__` kernel 裡，host 執行檔沒有對應的指令，所以 VS 把中斷點移到第 16 行 |
| p4 [L136](hw0/spec.md#L136)–[L138](hw0/spec.md#L138) 步驟 23–24：Continue 到第 17 行，滑鼠移到 `arraySize` 上，按 F10 | §2.2 | 照原文做 |
| p4 [L144](hw0/spec.md#L144)–[L170](hw0/spec.md#L170) 步驟 25–29：Memory 1、Immediate 視窗，輸入 `a`、`&a[0]`，切換成 4-byte signed | §2.2 | 照原文做（runbook 沒有實際操作過）。重點是 `a` 和 `&a[0]` 是同一個位址 |
| p5 [L176](hw0/spec.md#L176)–[L186](hw0/spec.md#L186) 步驟 30–34：在 `addWithCuda` 裡看 `dev_a`、`&dev_a`。為什麼一個會變、一個不變？ | §2.2「33b」 | ✍️ `&dev_a` 是 host 上這個變數本身的位址，所以不變；`cudaMalloc` 把 GPU 位址寫進 `dev_a`，所以它的值變了 |
| p5 [L187](hw0/spec.md#L187)–[L194](hw0/spec.md#L194) 步驟 35–38：debug console 一開始是空的，跨過 printf 之後才有輸出，最後 Stop Debugging | §2.2 | 輸出：`{1,2,3,4,5} + {10,20,30,40,50} = {11,22,33,44,55}` |
| p5–p6 [L199](hw0/spec.md#L199) 步驟 39：在 Developer Command Prompt 執行 `nvcc -o vecadd kernel.cu -run` | §2.3、§1.4 | 輸出同上，再執行 `.\vecadd.exe`。⚠️ 只會產生 `vecadd.exe`，沒有 `.exp`、`.lib`。⚠️ 要寫成 `.\` |
| p6 [L222](hw0/spec.md#L222) First Look at CUDA Binary Tools：`cuobjdump -lptx`、`-lelf`、`--dump-ptx`、`--dump-sass` | §2.3 | `-lptx` 顯示 `vecadd.1.sm_75.ptx`，`-lelf` 顯示兩個 `sm_75.cubin`。⚠️ PDF 裡的 `-–dump-ptx` 是 en dash，要自己打兩個 `-` |
| p6 [L239](hw0/spec.md#L239)–[L252](hw0/spec.md#L252) 步驟 40–44：把陣列改成 `int* a = 0;`，重建 | §2.4 表格第 1 列 | build 成功。✍️ 為什麼：函式參數本來就是指標，陣列傳進去時會 decay 成指標 |
| p7 [L254](hw0/spec.md#L254)–[L258](hw0/spec.md#L258) 步驟 45–46：`nvcc -o addvec kernel.cu`，執行 | §2.4 第 2 列 | `cudaMemcpy failed!`。✍️ 原因：從 NULL 複製資料 |
| p7 [L260](hw0/spec.md#L260)–[L269](hw0/spec.md#L269) 步驟 47–50：改用 `malloc` | §2.4 第 3 列 | c 是一堆垃圾值。✍️ 原因：malloc 不會初始化記憶體。前面的 `{1,2,3,4,5}` 是寫死在 printf 字串裡的。要加 `#include <stdlib.h>` |
| p7 [L271](hw0/spec.md#L271)–[L281](hw0/spec.md#L281) 步驟 51–53：加上 `*pa++` 的迴圈 | §2.4 第 4 列 | `{11,22,33,44,55}`。⚠️ 原文說會有 warning，實測沒有 |
| p7 [L283](hw0/spec.md#L283)–[L293](hw0/spec.md#L293) 步驟 54–56：printf 改成印出 `a[0..4]` 等 | §2.4 第 5 列 | 印出真正的值。✍️ `a[i]` 就是 `*(a+i)` |
| p8 [L297](hw0/spec.md#L297)–[L300](hw0/spec.md#L300) 步驟 57–58：在 VS 重建、用偵錯工具跑 | §2.4 第 6 列 | 輸出相同 |
| p8–p9 [L304](hw0/spec.md#L304)–[L329](hw0/spec.md#L329) Device Query：照 starter code 和 API 清單印出 device 屬性 | §2.5 | 參考 [hw0/src/devicequery.cu](hw0/src/devicequery.cu)。`nvcc -o devicequery.exe devicequery.cu` → `.\devicequery.exe` 會顯示 RTX 3050、CC 8.6。⚠️ 原文的 `maxThreadDim`、`warpsize` 是錯字，正確是 `maxThreadsDim`、`warpSize` |
| p9–p10 [L352](hw0/spec.md#L352) nvidia-smi | §0、§1.1 | 在任何 terminal 執行 `nvidia-smi`。本機是 617.42 / CUDA 13.4，AWS 是 596.36 / 13.2 |

---

## HW1：SAXPY, 2D & 3D Matrix addition（11 分，2026-10-20 5:59 PM PDT 截止）

### Part 1：Questions（p1–p2）
原文 [L38](hw1/spec.md#L38) 規定**每題都要寫過程或理由**，只寫選項不給分。

| 原文 | runbook | 答案 → 要寫的理由 |
|---|---|---|
| p1 [L42](hw1/spec.md#L42) Q1：每個 thread 算 1 個元素 | §3.7 Q1 | ✍️ **A**。block 的起點 `blockIdx.x*blockDim.x` 加上 block 內的偏移；說明 B、C、D 為什麼錯 |
| p2 [L50](hw1/spec.md#L50) Q2：每個 thread 算 2 個相鄰元素 | §3.7 Q2 | ✍️ **D**。global id g 負責 `2g`、`2g+1`；用 blockDim=4 舉例 |
| p2 [L58](hw1/spec.md#L58) Q3：每個 block 分兩個 section | §3.7 Q3 | ✍️ **A**。block 的起點是 `2*blockDim.x*blockIdx.x`，加上 `threadIdx.x`，第二個元素是 `+blockDim.x` |
| p2 [L68](hw1/spec.md#L68) Q4：長度 8000、block 1024 | §3.7 Q4 | ✍️ **A 8192**。⌈8000/1024⌉ = 8，8 × 1024 = 8192 |

### Part 2：Programming Exercises（p2–p5）
| 原文 | runbook | 動作 → 預期 |
|---|---|---|
| p2 [L76](hw1/spec.md#L76)：從新的預設 CUDA 專案開始（像 HW0 那樣） | §3.2 步驟 1 | 在 `Au26_GPUCompute` 上按右鍵 → 加入 → 新增專案 → CUDA 13.4 Runtime，取名 `HW1` |
| p3 [L85](hw1/spec.md#L85) REMINDER：每個 `malloc` 都要配一個 `free` | §3.1 對照表「host 動態配置」那列 | 參考檔每個 test 結尾都有 `free`、`cudaFree`。自己改程式時也要檢查 |
| p3 [L103](hw1/spec.md#L103) Error checking on host：`main`、`addWithCuda` 都要用 `checkCuda`，macro 放在 `.h` | §3.1、§3.2 步驟 2–3 | 右鍵 → 加入 → 新增項目 → 標頭檔 → `cuda_check.h`，貼上 [hw1/src/cuda_check.h](hw1/src/cuda_check.h)。`kernel.cu` 整份換成 [hw1/src/kernel.cu](hw1/src/kernel.cu)。⚠️ 投影片寫 `char*`，參考檔改成 `const char*` |
| p3–p4 [L112](hw1/spec.md#L112) CUDA Kernels：host 配置記憶體、初始化成已知值、用 `<<<>>>` launch | §3.1「設計說明」 | 用固定 seed 的亂數浮點數，CPU 和 GPU 吃同一份輸入。✍️ 可以在報告裡說明為什麼不用小整數 |
| — 建置 | §3.2 步驟 4–6（或 §3.3） | **Release、x64**，Code Generation 不用改。建置 → Ctrl+F5。命令列：`nvcc -O3 … -o hw1.exe kernel.cu` → `.\hw1.exe` |
| p4 [L122](hw1/spec.md#L122)–[L125](hw1/spec.md#L125) printf kernel 1–2：算 GTID，tid、bid、GTID 印在同一行 | §3.1 對照表 | `printfKernel`：`gtid = blockIdx.x*blockDim.x + threadIdx.x` |
| p4 [L128](hw1/spec.md#L128) printf kernel 3a–d：`<<<1,32>>>`、`<<<4,8>>>`、`<<<32,1>>>` 各跑約 10 次 | §3.6 | 執行 §3.6 的 PowerShell 一行指令，三種設定各一次，再用 `.\hw1.exe printf 4 8 10` 截完整輸出。預期：1,32 每次照順序；4,8 是 block 1、3、0、2；32,1 會變，有時重複 |
| p4 [L134](hw1/spec.md#L134) printf kernel 4a–c：一致嗎？block 和 thread 有差別嗎？對計算有什麼含意？ | §3.6「(a)(b)(c)」 | ✍️ 用你自己的結果寫。重點：順序沒有保證；warp 內看起來有順序只是實作細節；kernel 不能依賴執行順序。（原文沒說這三題要不要書面回答，寫進去比較保險） |
| p4 [L138](hw1/spec.md#L138) SAXPY：`y = a·x + y`，參數要有 N，測 N = 10、1e3、1e7 | §3.1、§3.5 | `saxpyKernel(n, a, x, y)` + `if (i < n)`。`.\hw1.exe saxpy`：三個 N 在 rTol 1e-5 / aTol 1e-6 下都 PASSED，但約 25% 的元素沒有逐 bit 相同 |
| p5 [L157](hw1/spec.md#L157) 2D add：參數 M、N，測 4×4、500×500、3024×4032 | §3.1、§3.5 | `matAdd2DKernel`，`idx = row*N + col`。`.\hw1.exe mat2d`：0 個差異 |
| p5 [L168](hw1/spec.md#L168) 3D add：參數 M、N、P，用 `dim3`，測 3³、100³、1000³（要用 Release） | §3.1「1000³」、§3.5 | `gridAdd3DKernel`，`dim3 block(16,8,4)`。`.\hw1.exe grid3d` 跑小的兩個，`.\hw1.exe grid3d --big` 跑 1000³。⚠️ 8 GB 的卡放不下，程式會自動切成 z-slab，大約 60 秒，需要約 12 GB host RAM |
| p5 [L180](hw1/spec.md#L180) Verification 1a–b：每個 kernel 都要有 CPU 版本，用 tolerance 比對 | §3.1 對照表最後兩列 | `verify()` 用 L2 p37 的公式：`max(aTol, rTol·max(|cpu|,|gpu|))` |
| p5 [L187](hw1/spec.md#L187) Verification 1c：驗證要用 RELEASE | §3.4 | 用 Debug（`-G`）編的話，SAXPY 是 0 個差異，什麼都觀察不到。✍️ 可以當成 HW Q2 的證據 |
| p5 [L191](hw1/spec.md#L191) **HW Q**：tolerance 設到多少開始失敗？ | §3.7 HW Q1、§3.5 的 sweep 行 | ✍️ 2D、3D 設成 0 也通過。SAXPY 的 N=10 約在 5e-8 開始失敗，N=1e3 在 1e-6，N=1e7 連 1e-5 都有失敗（catastrophic cancellation，要靠 aTol）。**用你自己截圖裡的數字** |
| p5 [L192](hw1/spec.md#L192) **HW Q**：哪個 kernel 的差異最嚴重？為什麼？附截圖 | §3.7 HW Q2、§3.2 步驟 7 或 §3.3 的 FMA 對照組 | ✍️ **SAXPY**，因為 GPU 用 FMA 只捨入一次。證據：`-fmad=false` 重編後差異變成 0（`.\hw1_nofma.exe saxpy`）。截兩張圖：一般 build 和 nofma |

### SUBMIT（p6）
| 原文 | runbook | 動作 |
|---|---|---|
| p6 [L198](hw1/spec.md#L198) 1：答案要有過程和理由，包含 HW Q | §3.8 第 1 項 | 一份 PDF 或 docx：Q1–Q4、兩題 HW Q、printf 觀察，加上 §3.8 列的 4 種截圖 |
| p6 [L200](hw1/spec.md#L200) 2：只交 `.cu`、`.cpp`、`.h` | §3.8 第 2 項 | 只交 `kernel.cu`、`cuda_check.h`，不要交 `.slnx`、`.vcxproj`、`x64\` |
| p6 [L203](hw1/spec.md#L203) 3：4 個 kernel function | §3.8 第 3 項 | 4 個都在 `kernel.cu` 裡：`printfKernel`、`saxpyKernel`、`matAdd2DKernel`、`gridAdd3DKernel` |
| （原文沒寫）上傳前 | §3.8 開頭 | 先看 Teams 的 Hw1 Discussion 有沒有更正，再自己上傳到 Canvas assignment 11810625。截止 **5:59 PM PDT** |

---

## 原文以外、runbook 才有的東西
這些不在作業原文裡，遇到問題時才需要看：
- §0 本機和 AWS 的差異：GPU 不同，只影響 device query、效能，以及 1000³ 要分批跑。
- §1.6、§3.9：`.\` 的問題、C4819、`no kernel image`、`malloc failed` 等常見錯誤。
- §3.3：命令列建置。和 VS 專案的結果逐位數相同，只用 VS 也可以。

GPU 課禁止用 AI 產生作業解答；runbook、這份對照和 `src/` 的參考程式碼都是 AI 產生的。
