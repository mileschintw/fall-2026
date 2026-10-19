# List uw-python-fall2026 repos and flag new assignment-<N> repos vs state/seen_repos.json
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$statePath = Join-Path $root 'state/seen_repos.json'
$repos = gh repo list uw-python-fall2026 --limit 100 --json name,createdAt,pushedAt,url | ConvertFrom-Json
$seen = @()
if (Test-Path $statePath) { $seen = Get-Content $statePath -Raw | ConvertFrom-Json }
$new = $repos | Where-Object { $_.name -notin $seen }
foreach ($r in ($repos | Sort-Object name)) {
  $flag = if ($r.name -in $new.name) { 'NEW ' } else { '    ' }
  "$flag$($r.name)`tcreated $($r.createdAt)`tpushed $($r.pushedAt)"
}
$repos.name | ConvertTo-Json | Set-Content $statePath -Encoding utf8
