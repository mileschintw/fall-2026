# HW2 background pipeline: copy sources to a build dir outside both repos, build, time Debug/Release.
# ncu needs admin: run ncu_admin.ps1 afterwards (see runbook.md section 3).
$ErrorActionPreference = 'Continue'
$B = Join-Path $env:TEMP 'claude\hw2build'
$S = $PSScriptRoot
New-Item -ItemType Directory -Force "$B\src", "$B\util", "$B\out", "$B\bin" | Out-Null
Copy-Item "$S\hw2.cu", "$S\cuda_check.h" "$B\src" -Force
Copy-Item 'D:\Repos\Au26_GPU\Au26_GPUCompute\util\*.h' "$B\util" -Force
Copy-Item "$S\build.bat", "$S\ncu_admin.ps1" $B -Force
cmd /c "$B\build.bat" 2>&1 | Select-String -Pattern 'error|BUILD OK' | Out-File -Encoding utf8 "$B\build.log"
Set-Location "$B\bin"
.\hw2_rel.exe all all --reps 5 --out ../out/ 2>&1 | Out-File -Encoding utf8 "$B\timing_release.txt"
.\hw2_dbg.exe all all --reps 5 --out ../out/dbg_ 2>&1 | Out-File -Encoding utf8 "$B\timing_debug.txt"
.\hw2_rel.exe 1 --box 10 --nocpu --out ../out/ 2>&1 | Out-File -Encoding utf8 "$B\box.txt"
'DONE' | Out-File "$B\done.txt"
