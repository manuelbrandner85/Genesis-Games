# Downloads the NASA SVS Deep Star Map (public domain, SVS item 4851), verifies its SHA256
# and builds the Unreal texture + sky material (Tools/Editor/build_wk_m02_006.py).
# The star map is not stored in the repository to keep Git LFS usage low.
# Run once after cloning: powershell -ExecutionPolicy Bypass -File Tools\Setup\Get-StarMap.ps1
param([string]$EngineRoot = "C:\Program Files\Epic Games\UE_5.8")

$ErrorActionPreference = "Stop"
$proj = (Resolve-Path "$PSScriptRoot\..\..").Path
$url = "https://svs.gsfc.nasa.gov/vis/a000000/a004800/a004851/starmap_2020_8k.exr"
$expected = "dc6c4f413e85707a29a25a9451148154554ecca2c996f84fa8f47b65ef9ff7c4"
$dst = Join-Path $proj "SourceArt\Sky\starmap_2020_8k.exr"

New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
if (-not (Test-Path $dst) -or (Get-FileHash $dst -Algorithm SHA256).Hash.ToLower() -ne $expected) {
    Write-Output "Downloading $url (124.5 MB) ..."
    Invoke-WebRequest -Uri $url -OutFile $dst -UseBasicParsing
}
$hash = (Get-FileHash $dst -Algorithm SHA256).Hash.ToLower()
if ($hash -ne $expected) { throw "SHA256 mismatch: $hash (expected $expected)" }
Write-Output "Star map OK ($hash)"

$editor = Join-Path $EngineRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
& $editor (Join-Path $proj "Genesis.uproject") -run=pythonscript "-script=$(Join-Path $proj 'Tools\Editor\build_wk_m02_006.py')" -unattended -nullrhi -nosplash -nop4
Write-Output "Sky texture and material built (see Saved/Logs/Genesis.log, GENESIS_BUILD)."
