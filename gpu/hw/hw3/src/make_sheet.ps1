# Builds the blank HW3 answer sheet (same layout as HW1/HW2) -> D:\Repos\Au26_GPU\Au26_GPUCompute\HW3\HW3_Answers.docx
$ErrorActionPreference = 'Stop'
$S = $PSScriptRoot
$H = 'D:\Repos\Au26_GPU\Au26_GPUCompute\HW3'
New-Item -ItemType Directory -Force $H | Out-Null
python "$S\make_answers_docx.py" "$H\..\HW1\HW1_Answers.docx" "$H\HW3_Answers.docx"
