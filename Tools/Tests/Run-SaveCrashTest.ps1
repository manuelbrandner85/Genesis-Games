# WK-M02-001 crash test: kills the saving process hard (TerminateProcess) at random moments
# and verifies that Soul/World/Life always load from one complete transaction.
param(
    [int]$Iterations = 15,
    [string]$Engine = "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
)

$ErrorActionPreference = "Stop"
$proj = (Resolve-Path "$PSScriptRoot\..\..").Path
$uproject = Join-Path $proj "Genesis.uproject"
$dir = Join-Path $proj "Saved\Automation\WK-M02-001\crash"
$csv = Join-Path $proj "Saved\Automation\WK-M02-001\crash_test.csv"

if (Test-Path $dir) { Remove-Item $dir -Recurse -Force }
New-Item -ItemType Directory -Force $dir | Out-Null
"iteration,kill_delay_ms,exit_code,result,seq,backup,consistent,memories" | Set-Content -Encoding ascii $csv

$failed = 0
$lastSeq = -1
for ($i = 1; $i -le $Iterations; $i++) {
    $flag = Join-Path $dir "running.flag"
    if (Test-Path $flag) { Remove-Item $flag -Force }

    $w = Start-Process -FilePath $Engine -PassThru -WindowStyle Hidden -ArgumentList "`"$uproject`" -run=GenesisSaveStress -mode=write -dir=`"$dir`" -payload=3000 -unattended -nullrhi -nosplash -nop4 -log=StressWrite.log"
    $deadline = (Get-Date).AddSeconds(180)
    while (-not (Test-Path $flag)) {
        if ((Get-Date) -gt $deadline -or $w.HasExited) { break }
        Start-Sleep -Milliseconds 100
    }
    $delay = Get-Random -Minimum 20 -Maximum 1500
    Start-Sleep -Milliseconds $delay
    if (-not $w.HasExited) { Stop-Process -Id $w.Id -Force }
    $w.WaitForExit()

    $result = Join-Path $dir "verify_result.txt"
    if (Test-Path $result) { Remove-Item $result -Force }
    # Exit code is not used: the engine logs its own self-test errors at startup and the commandlet then reports 1.
    $v = Start-Process -FilePath $Engine -PassThru -Wait -WindowStyle Hidden -ArgumentList "`"$uproject`" -run=GenesisSaveStress -mode=verify -dir=`"$dir`" -unattended -nullrhi -nosplash -nop4 -log=StressVerify.log"
    if (-not (Test-Path $result)) {
        $failed++
        "$i,$delay,$($v.ExitCode),NO_RESULT,,,," | Add-Content -Encoding ascii $csv
        Write-Output ("[{0}/{1}] kill after {2} ms -> verify produced no result" -f $i, $Iterations, $delay)
        continue
    }
    $line = Get-Content $result -Raw
    $kv = @{}
    foreach ($pair in $line.Trim().Split(' ')) { $k, $val = $pair.Split('='); $kv[$k] = $val }

    $ok = ($kv['result'] -eq 'EGenesisSaveResult::Ok') -and ($kv['consistent'] -eq '1') -and ([int64]$kv['seq'] -ge $lastSeq)
    if (-not $ok) { $failed++ }
    $lastSeq = [int64]$kv['seq']
    "$i,$delay,$($v.ExitCode),$($kv['result']),$($kv['seq']),$($kv['backup']),$($kv['consistent']),$($kv['memories'])" | Add-Content -Encoding ascii $csv
    Write-Output ("[{0}/{1}] kill after {2} ms -> {3}" -f $i, $Iterations, $delay, $line.Trim())
}

Write-Output "FAILED=$failed of $Iterations"
Write-Output "CSV: $csv"
exit $failed
