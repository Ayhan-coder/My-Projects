[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Pde,

  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$SketchArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-ProcessingHome {
  if ($env:PROCESSING4_HOME -and (Test-Path $env:PROCESSING4_HOME)) {
    return (Resolve-Path $env:PROCESSING4_HOME).Path
  }

  $where = & where.exe processing 2>$null
  if ($LASTEXITCODE -eq 0 -and $where) {
    $processingExe = ($where -split "`r?`n" | Where-Object { $_ } | Select-Object -First 1)
    if ($processingExe -and (Test-Path $processingExe)) {
      return (Split-Path -Parent $processingExe)
    }
  }

  $fallback = 'C:\Program Files\Processing'
  if (Test-Path $fallback) {
    return $fallback
  }

  throw "Could not find Processing. Set PROCESSING4_HOME to your Processing install folder (the one containing Processing.exe)."
}

$pdePath = Resolve-Path $Pde -ErrorAction Stop
$sketchName = [IO.Path]::GetFileNameWithoutExtension($pdePath.Path)

$processingHome = Resolve-ProcessingHome
$appDir = Join-Path $processingHome 'app'
$javaExe = Join-Path $appDir 'resources\jdk\bin\java.exe'

$cfgPath = Join-Path $appDir 'Processing.cfg'

if (-not (Test-Path $javaExe)) {
  throw "Could not find bundled Java at: $javaExe"
}

$javaOptions = @()
if (Test-Path $cfgPath) {
  $javaOptions = Get-Content $cfgPath |
    Where-Object { $_ -like 'java-options=*' } |
    ForEach-Object { $_.Substring('java-options='.Length) } |
    ForEach-Object { $_.Replace('$APPDIR', $appDir) }
}

$cp = @(
  (Join-Path $appDir '*'),
  (Join-Path $appDir 'resources\core\library\*')
) -join ';'

$workspaceRoot = $PSScriptRoot
$stageRoot = Join-Path $workspaceRoot '.processing_stage'
$outRoot = Join-Path $workspaceRoot '.processing_output'

$sketchDir = Join-Path $stageRoot $sketchName
$outputDir = Join-Path $outRoot $sketchName

# Clean stage/output for a deterministic run
if (Test-Path $sketchDir) { Remove-Item -Recurse -Force $sketchDir }
if (Test-Path $outputDir) { Remove-Item -Recurse -Force $outputDir }

New-Item -ItemType Directory -Path $sketchDir | Out-Null
New-Item -ItemType Directory -Path $outputDir | Out-Null

$stagedMain = Join-Path $sketchDir ($sketchName + '.pde')
Copy-Item -Path $pdePath.Path -Destination $stagedMain -Force

# Stage assets (Processing expects images/fonts/etc. under a sketch-level `data` folder)
$srcDir = Split-Path -Parent $pdePath.Path
$srcDataDir = Join-Path $srcDir 'data'
$dstDataDir = Join-Path $sketchDir 'data'

if (Test-Path $srcDataDir) {
  Copy-Item -Path $srcDataDir -Destination $dstDataDir -Recurse -Force
} else {
  # If the sketch keeps assets next to the .pde (common in p5.js ports), copy images into data/
  $assetExts = @('*.jpg', '*.jpeg', '*.png', '*.gif', '*.svg')
  $assets = @()
  foreach ($ext in $assetExts) {
    $assets += Get-ChildItem -Path $srcDir -Filter $ext -File -ErrorAction SilentlyContinue
  }
  if ($assets.Count -gt 0) {
    New-Item -ItemType Directory -Path $dstDataDir | Out-Null
    foreach ($a in $assets) {
      Copy-Item -Path $a.FullName -Destination (Join-Path $dstDataDir $a.Name) -Force
    }
  }
}

Write-Host "Processing home : $processingHome"
Write-Host "Sketch (staged)  : $sketchDir"
Write-Host "Output           : $outputDir"

$baseArgs = @()
$baseArgs += $javaOptions
$baseArgs += @(
  '-cp', $cp,
  'processing.app.ProcessingKt',
  'cli',
  "--sketch=$sketchDir",
  "--output=$outputDir",
  '--force',
  '--run'
)

if ($SketchArgs) {
  $baseArgs += $SketchArgs
}

& $javaExe @baseArgs
