# 動手練習

每個檔案 `NN-slug.cu` 都能單獨編譯，檔頭註解寫要改哪一行、預期看到什麼。

在 PowerShell、這個資料夾裡編譯並執行（2026-10-27 在 RTX 3050 上實測可用；開頭那行「不是內部或外部命令」的警告是 vcvars 印的，可忽略）：

```powershell
cmd /c '"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul && nvcc -O3 -arch=sm_86 -Xcompiler /utf-8 -o NN-slug.exe NN-slug.cu && .\NN-slug.exe'
```

`printf` 的字串一律只用 ASCII。這台繁中 Windows 有兩個問題（2026-10-28 實際遇到）：nvcc 前端用 Big5 讀原始檔，中文後面緊接 `\` 時，`\n` 會被印成字面上的 `\n`；另外 PowerShell 主控台用 CP950 顯示，UTF-8 中文會變亂碼。註解寫中文沒有問題。

練習用 `-arch=sm_86`（這台的 RTX 3050）；作業照老師設定用 `compute_75,sm_75`（`gpu/hw/hw2/src/build.bat`）。`*.exe`、`*.exp`、`*.lib`、`*.pdb` 已 gitignore。
