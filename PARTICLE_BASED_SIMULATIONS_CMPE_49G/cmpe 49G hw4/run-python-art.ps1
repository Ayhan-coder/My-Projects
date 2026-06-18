[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidateSet('starry', 'dunes', 'aurora', 'diffuse_flow', 'flow_lines', 'noisy_circles', 'field_particles', 'confetti', 'confetti_chunky', 'marbled_ribbons', 'neon_currents', 'reaction_diffusion', 'topo_contours', 'kaleido_noise')]
  [string]$Style,

  [int]$Seed = 1,

  [string]$Size = '1920x1080',

  [ValidateSet('auto', 'night', 'desert', 'storm', 'colorful')]
  [string]$Vibe = 'auto',

  [ValidateSet('rect', 'line', 'dot', 'arc', 'tri', 'perp')]
  [string]$Brush = 'rect',

  [ValidateSet('none', 'pro')]
  [string]$Grade = 'none'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
  throw "Could not find venv python at $python. Create the venv or run the script with your system python."
}

$script = Join-Path $PSScriptRoot 'python_art\generate_paintings.py'
if (-not (Test-Path $script)) {
  throw "Missing script: $script"
}

& $python $script --style $Style --seed $Seed --size $Size --vibe $Vibe --brush $Brush --grade $Grade
