# 動手練習

每個檔案 `NN-slug.cu` 都能單獨編譯，檔頭註解寫要改哪一行、預期看到什麼。

在 PowerShell、這個資料夾裡編譯並執行（2026-10-27 在 RTX 3050 上實測可用；開頭那行「不是內部或外部命令」的警告是 vcvars 印的，可忽略）：

```powershell
cmd /c '"C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul && nvcc -O3 -arch=sm_86 -Xcompiler /utf-8 -o NN-slug.exe NN-slug.cu && .\NN-slug.exe'
```

練習用 `-arch=sm_86`（這台的 RTX 3050）；作業照老師設定用 `compute_75,sm_75`（`gpu/hw/hw2/src/build.bat`）。`*.exe`、`*.exp`、`*.lib`、`*.pdb` 已 gitignore。
