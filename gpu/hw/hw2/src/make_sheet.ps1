# Builds the finished HW2 answer sheet: blank layout (temp only) -> data -> written answers -> HW2_Answers.docx
$ErrorActionPreference = 'Stop'
$S = $PSScriptRoot
$H = 'D:\Repos\Au26_GPU\Au26_GPUCompute\HW2'
$blank = Join-Path $env:TEMP 'claude\hw2_blank.docx'
New-Item -ItemType Directory -Force (Split-Path $blank) | Out-Null
python "$S\make_answers_docx.py" "$H\..\HW1\HW1_Answers.docx" $blank
python "$S\fill_data_docx.py" $blank "$S\..\results" "$H\HW2_Answers.docx" $H
python "$S\fill_answers_docx.py" "$H\HW2_Answers.docx"
