# PostToolUse event telemetry, minimal fields. Never log arguments or secret values.
$ErrorActionPreference='Stop'
try {
  $raw=[Console]::In.ReadToEnd()
  $obj=$raw | ConvertFrom-Json
  $root=$env:CLAUDE_PROJECT_DIR
  if (-not $root) { exit 0 }
  $out=Join-Path $root '.genesis-local'
  New-Item -ItemType Directory -Path $out -Force | Out-Null
  $record=@{event='PostToolUse';tool=[string]$obj.tool_name;time=(Get-Date).ToUniversalTime().ToString('o');session_id=[string]$obj.session_id}
  $line=$record | ConvertTo-Json -Compress
  Add-Content -LiteralPath (Join-Path $out 'hook-events.jsonl') -Value $line -Encoding UTF8
  exit 0
} catch {
  # Telemetry must not turn a successful edit into a claimed production failure.
  exit 0
}
