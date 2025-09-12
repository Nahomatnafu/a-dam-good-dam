# Improved PowerShell version with parallel processing
param(
  [string]$InputDir      = "D:\NeoFinder_Test\Footage",
  [string]$OutputDir     = "D:\NeoFinder_Test\Stills",
  [int]$FramesPerClip    = 10,
  [string]$ImageExt      = "png",   # "png" or "jpg"
  [int]$MaxParallel      = 4        # Number of parallel jobs
)

if (-not (Test-Path $InputDir))  { throw "InputDir not found: $InputDir" }
if (-not (Test-Path $OutputDir)) { New-Item -Force -ItemType Directory -Path $OutputDir | Out-Null }

function Get-CleanBase([string]$name) {
  $base = [System.IO.Path]::GetFileNameWithoutExtension($name)
  $base = $base -replace '[^\w\-\.\(\) ]',''
  return ($base -replace ' +','_')
}

function Get-VideoDuration([string]$videoPath) {
  try {
    $durTxt = & ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 -- "$videoPath" 2>$null
    if ($durTxt) {
      return [double]::Parse($durTxt, [System.Globalization.CultureInfo]::InvariantCulture)
    }
  } catch {
    Write-Warning "Could not read duration for $videoPath"
  }
  return $null
}

function Get-Timestamps([double]$duration, [int]$frameCount) {
  $times = @()
  $epsilon = [Math]::Min(0.25, $duration * 0.01)   # 250ms or 1% of dur
  for ($i = 1; $i -le $frameCount; $i++) {
    $t = ($duration * $i) / ($frameCount + 1)
    $t = [Math]::Max($epsilon, [Math]::Min($duration - $epsilon, $t))
    $times += $t
  }
  return $times
}

function Extract-FramesBatch([string]$videoPath, [double[]]$timestamps, [string]$outputDir, [string]$baseName, [string]$imageExt) {
  $extractedCount = 0
  
  # Create batch extraction using filter_complex for better performance
  if ($timestamps.Count -gt 1) {
    # Build filter complex for multiple outputs
    $filterParts = @()
    $outputParts = @()
    
    for ($i = 0; $i -lt $timestamps.Count; $i++) {
      $idxStr = "{0:D3}" -f ($i + 1)
      $outPath = Join-Path $outputDir ("{0}_{1}.{2}" -f $baseName, $idxStr, $imageExt)
      
      # Use select filter with frame number approximation
      $frameNum = [int]($timestamps[$i] * 30)  # Assume 30fps for approximation
      $filterParts += "[0:v]select='eq(n,$frameNum)'[out$i]"
      $outputParts += @("-map", "[out$i]", "-frames:v", "1", $outPath)
    }
    
    $filterComplex = $filterParts -join ";"
    $ffmpegArgs = @(
      "-hide_banner", "-loglevel", "error", "-y",
      "-i", $videoPath,
      "-filter_complex", $filterComplex
    ) + $outputParts
    
    & ffmpeg @ffmpegArgs 2>$null
    
    # Count successful extractions
    for ($i = 0; $i -lt $timestamps.Count; $i++) {
      $idxStr = "{0:D3}" -f ($i + 1)
      $outPath = Join-Path $outputDir ("{0}_{1}.{2}" -f $baseName, $idxStr, $imageExt)
      if (Test-Path $outPath) { $extractedCount++ }
    }
  } else {
    # Single frame extraction
    $idxStr = "001"
    $outPath = Join-Path $outputDir ("{0}_{1}.{2}" -f $baseName, $idxStr, $imageExt)
    & ffmpeg -hide_banner -loglevel error -y -i $videoPath -ss $timestamps[0] -frames:v 1 $outPath 2>$null
    if (Test-Path $outPath) { $extractedCount = 1 }
  }
  
  return $extractedCount
}

# Script block for parallel processing
$processVideoScript = {
  param($videoFile, $outputDir, $framesPerClip, $imageExt)
  
  # Import functions into the script block scope
  function Get-CleanBase([string]$name) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($name)
    $base = $base -replace '[^\w\-\.\(\) ]',''
    return ($base -replace ' +','_')
  }
  
  function Get-VideoDuration([string]$videoPath) {
    try {
      $durTxt = & ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 -- "$videoPath" 2>$null
      if ($durTxt) {
        return [double]::Parse($durTxt, [System.Globalization.CultureInfo]::InvariantCulture)
      }
    } catch {
      return $null
    }
    return $null
  }
  
  function Get-Timestamps([double]$duration, [int]$frameCount) {
    $times = @()
    $epsilon = [Math]::Min(0.25, $duration * 0.01)
    for ($i = 1; $i -le $frameCount; $i++) {
      $t = ($duration * $i) / ($frameCount + 1)
      $t = [Math]::Max($epsilon, [Math]::Min($duration - $epsilon, $t))
      $times += $t
    }
    return $times
  }
  
  function Extract-FramesBatch([string]$videoPath, [double[]]$timestamps, [string]$outputDir, [string]$baseName, [string]$imageExt) {
    $extractedCount = 0
    
    # Simple approach for parallel execution - extract frames individually but efficiently
    for ($i = 0; $i -lt $timestamps.Count; $i++) {
      $idxStr = "{0:D3}" -f ($i + 1)
      $outPath = Join-Path $outputDir ("{0}_{1}.{2}" -f $baseName, $idxStr, $imageExt)
      & ffmpeg -hide_banner -loglevel error -y -i $videoPath -ss $timestamps[$i] -frames:v 1 $outPath 2>$null
      if (Test-Path $outPath) { $extractedCount++ }
    }
    
    return $extractedCount
  }
  
  # Process the video
  $src = $videoFile.FullName
  $base = Get-CleanBase $videoFile.Name
  
  $duration = Get-VideoDuration $src
  if (-not $duration -or $duration -le 0) {
    return @{ Name = $videoFile.Name; Success = $false; Count = 0; Error = "Could not read duration" }
  }
  
  $timestamps = Get-Timestamps $duration $framesPerClip
  $extractedCount = Extract-FramesBatch $src $timestamps $outputDir $base $imageExt
  
  return @{ Name = $videoFile.Name; Success = $true; Count = $extractedCount; Error = $null }
}

# Main execution
$videoExts = @("*.mp4","*.mov","*.mxf","*.mkv","*.avi","*.mts","*.m2ts","*.wmv","*.webm","*.3gp","*.m4v")
$files = foreach ($pat in $videoExts) { Get-ChildItem -Path $InputDir -File -Filter $pat }

if ($files.Count -eq 0) { 
  Write-Host "No video files found in $InputDir"
  exit 
}

Write-Host "Found $($files.Count) clips. Target: $FramesPerClip $ImageExt still(s)/clip → $OutputDir"
Write-Host "Using $MaxParallel parallel workers`n"

# Process files in parallel batches
$totalProcessed = 0
$totalFrames = 0
$batchSize = $MaxParallel

for ($i = 0; $i -lt $files.Count; $i += $batchSize) {
  $batch = $files[$i..([Math]::Min($i + $batchSize - 1, $files.Count - 1))]
  
  # Start parallel jobs for this batch
  $jobs = @()
  foreach ($file in $batch) {
    $job = Start-Job -ScriptBlock $processVideoScript -ArgumentList $file, $OutputDir, $FramesPerClip, $ImageExt
    $jobs += $job
  }
  
  # Wait for batch to complete and collect results
  foreach ($job in $jobs) {
    $result = Receive-Job -Job $job -Wait
    Remove-Job -Job $job
    
    if ($result.Success) {
      Write-Host ("{0} → {1} still(s)" -f $result.Name, $result.Count)
      $totalFrames += $result.Count
    } else {
      Write-Warning ("{0} → Error: {1}" -f $result.Name, $result.Error)
    }
    $totalProcessed++
  }
  
  # Progress update
  $progress = [Math]::Round(($totalProcessed / $files.Count) * 100, 1)
  Write-Host "Progress: $progress% ($totalProcessed/$($files.Count) videos processed)"
}

Write-Host "`nCompleted! Processed $totalProcessed videos, extracted $totalFrames frames total."
