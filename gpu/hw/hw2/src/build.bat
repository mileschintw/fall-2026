@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
cd /d %~dp0src
set GEN=-gencode arch=compute_75,code=[sm_75,compute_75]
set REL=-O3 -DNDEBUG -Xcompiler "/O2 /utf-8 /MD" %GEN%
set DBG=-G -g -D_DEBUG -Xcompiler "/Od /utf-8 /MDd" %GEN%
nvcc %REL% -o ..\bin\hw2_rel.exe hw2.cu || exit /b 1
nvcc %DBG% -o ..\bin\hw2_dbg.exe hw2.cu || exit /b 1
for %%i in (1 2 3 4) do (
  nvcc %REL% -DIMG_IDX=%%i -DKERNEL_SEL=0 -o ..\bin\hw2_rel_global_img%%i.exe hw2.cu || exit /b 1
  nvcc %REL% -DIMG_IDX=%%i -DKERNEL_SEL=1 -o ..\bin\hw2_rel_shared_img%%i.exe hw2.cu || exit /b 1
)
echo BUILD OK
