# Copies Epic's UE5 mannequin (template content) from the local engine into
# Content/Characters/Mannequins - the path the template assets reference internally.
# Epic template content may be used in UE projects but not redistributed: it is NOT stored in
# this public repository (.gitignore). Run once after cloning:
#   powershell -ExecutionPolicy Bypass -File tools\setup\Copy-EngineMannequin.ps1
param([string]$EngineRoot = "C:\Program Files\Epic Games\UE_5.8")

$ErrorActionPreference = "Stop"
$src = Join-Path $EngineRoot "Templates\TemplateResources\High\Characters\Content\Mannequins"
$dst = Join-Path (Resolve-Path "$PSScriptRoot\..\..").Path "Content\Characters\Mannequins"
if (-not (Test-Path $src)) { throw "Mannequin source not found: $src" }

New-Item -ItemType Directory -Force (Join-Path $dst "Anims") | Out-Null
foreach ($d in "Meshes", "Materials", "Textures", "Rigs") {
    Copy-Item -Recurse -Force (Join-Path $src $d) $dst
}
Copy-Item -Recurse -Force (Join-Path $src "Anims\Unarmed") (Join-Path $dst "Anims")
Write-Output ("Copied {0} files to {1}" -f (Get-ChildItem -Recurse -File $dst).Count, $dst)
