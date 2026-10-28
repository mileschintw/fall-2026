# 動手練習

每個檔案 `NN-slug.cu` 都能單獨編譯，檔頭註解寫要改哪一行、預期看到什麼。

編譯（Developer PowerShell 或先跑 vcvars64，設定照 `gpu/hw/hw2/src/build.bat`）：

```
nvcc -O3 -gencode arch=compute_75,code=[sm_75,compute_75] -Xcompiler "/utf-8" -o NN-slug.exe NN-slug.cu
```

`*.exe`、`*.exp`、`*.lib`、`*.pdb` 不進 git。
