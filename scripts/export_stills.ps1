# D:\NeoFinder_Test\export_stills.ps1
param(
  [string]$InputDir      = "D:\NeoFinder_Test\Footage",
  [string]$OutputDir     = "D:\NeoFinder_Test\Stills",
  [int]$FramesPerClip    = 10,
  [string]$ImageExt      = "png"   # "png" or "jpg"
)

if (-not (Test-Path $InputDir))  { throw "InputDir not found: $InputDir" }
if (-not (Test-Path $OutputDir)) { New-Item -Force -ItemType Directory -Path $OutputDir | Out-Null }

function Get-CleanBase([string]$name) {
  $base = [System.IO.Path]::GetFileNameWithoutExtension($name)
  $base = $base -replace '[^\w\-\.\(\) ]',''
  return ($base -replace ' +','_')
}

$videoExts = @("*.mp4","*.mov","*.mxf","*.mkv","*.avi","*.mts","*.m2ts","*.wmv","*.webm","*.3gp","*.m4v")
$files = foreach ($pat in $videoExts) { Get-ChildItem -Path $InputDir -File -Filter $pat }
if ($files.Count -eq 0) { Write-Host "No video files found in $InputDir"; exit }

Write-Host "Found $($files.Count) clips. Target: $FramesPerClip $ImageExt still(s)/clip → $OutputDir`n"

foreach ($f in $files) {
  $src  = $f.FullName
  $base = Get-CleanBase $f.Name

  # Duration (seconds)
  $durTxt = & ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 -- "$src"
  if (-not $durTxt) { Write-Warning "Could not read duration for $src; skipping."; continue }
  $duration = [double]::Parse($durTxt, [System.Globalization.CultureInfo]::InvariantCulture)
  if ($duration -le 0) { Write-Warning "Non-positive duration for $src; skipping."; continue }

  # Evenly-spaced timestamps, skipping tiny head/tail slates
  $times = New-Object System.Collections.Generic.List[double]
  $epsilon = [Math]::Min(0.25, $duration * 0.01)   # 250ms or 1% of dur
  for ($i = 1; $i -le $FramesPerClip; $i++) {
    $t = ($duration * $i) / ($FramesPerClip + 1)
    $t = [Math]::Max($epsilon, [Math]::Min($duration - $epsilon, $t))
    $times.Add($t)
  }

  # Extract frames with accurate seek: -ss AFTER -i, take 1 frame
  $count = 0; $idx = 1
  foreach ($t in $times) {
    $idxStr  = "{0:D3}" -f $idx
    $outPath = Join-Path $OutputDir ("{0}_{1}.{2}" -f $base, $idxStr, $ImageExt)
    & ffmpeg -hide_banner -loglevel error -y -i "$src" -ss $t -frames:v 1 "$outPath"
    if (Test-Path $outPath) { $count++; $idx++ }
  }

  Write-Host ("{0} → {1} still(s)" -f $f.Name, $count)
}

Write-Host "`nDone."

# Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
# D:\NeoFinder_Test\export_stills.ps1 `
#   -InputDir "D:\NeoFinder_Test\Footage" `
#   -OutputDir "D:\NeoFinder_Test\Stills" `
#   -FramesPerClip 10 `
#   -ImageExt png
