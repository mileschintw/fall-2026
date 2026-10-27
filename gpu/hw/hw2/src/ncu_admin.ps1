# Runs the 8 HW2 ncu profiles (global/static x img1-4). Needs admin for GPU performance counters.
$B = 'C:\Users\user3\AppData\Local\Temp\claude\hw2build'
Set-Location "$B\bin"
$ncu = 'C:\Program Files\NVIDIA Corporation\Nsight Compute 2026.3.1\ncu.bat'
if (-not (Test-Path $ncu)) { $ncu = 'ncu' }
$m = 'smsp__cycles_elapsed.sum,smsp__cycles_elapsed.sum.per_second,smsp__inst_executed.sum,dram__sectors_read.sum,dram__sectors_write.sum,dram__bytes.sum,sm__cycles_elapsed.avg,sm__cycles_elapsed.avg.per_second,sm__inst_executed.sum,dram__bytes_read.sum,dram__bytes_write.sum,gpu__cycles_elapsed.sum,gpu__time_duration.sum,gpu__time_duration.avg'
foreach ($k in @(@('global','gaussBlurKernel_globalmem'), @('shared','gaussBlurKernel_sharedmem_static'))) {
  foreach ($i in 1..4) {
    $exe = ".\hw2_rel_$($k[0])_img$i.exe"
    & $ncu -k $k[1] --metrics $m $exe --nocpu --out ../out/ncu_ 2>&1 | Out-File -Encoding utf8 "$B\ncu_$($k[0])_img$i.txt"
    & $ncu -k $k[1] --metrics $m --csv --print-units base $exe --nocpu --out ../out/ncu_ 2>&1 | Out-File -Encoding utf8 "$B\ncu_$($k[0])_img$i.csv"
  }
}
'DONE' | Out-File "$B\ncu_done.txt"
