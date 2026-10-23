# Windows PowerShell 5.1. PreToolUse: deny clearly unsafe commands and edits of guarded canon.
# This is defense in depth, NOT a sandbox or comprehensive OS security boundary.
$ErrorActionPreference = 'Stop'
try {
    $raw = [Console]::In.ReadToEnd()
    $event = $raw | ConvertFrom-Json
    $tool = [string]$event.tool_name
    $inputValue = $event.tool_input
    $denial = $null
    $cmd = [string]$inputValue.command
    if (($tool -match 'Bash|PowerShell') -and $cmd) {
        $patterns = @(
            '(?i)\bgit\s+(push|reset\s+--hard|clean\s+-[a-z]*f|branch\s+-D)\b',
            '(?i)\bgh\s+repo\s+delete\b',
            '(?i)\b(rm\s+-rf|del\s+/[fsq]|rmdir\s+/s|Remove-Item\b)',
            '(?i)\b(curl|wget|Invoke-WebRequest|Invoke-RestMethod|Start-BitsTransfer)\b',
            '(?i)\b(pip\s+install|npm\s+install|winget\s+install|choco\s+install)\b',
            '(?i)\b(gh\s+release\s+create|docker\s+push|git\s+filter-repo)\b'
        )
        foreach ($rx in $patterns) { if ($cmd -match $rx) { $denial = 'Riskanter Befehl muss außerhalb dieser Session nach expliziter Freigabe manuell geprüft werden.'; break } }
        # Shell aliases/indirection may circumvent checks: guard never replaces explicit permissions/review.
    }
    if ($tool -match 'Edit|Write|NotebookEdit') {
        $path = [string]$inputValue.file_path
        if ($path -and $path -match '(?i)(ScriptLock|Storybibel|Spielebibel|original_md_unveraendert|GAMEFORGE_Verbesserung_03_Ultimate_Living_World|C00[-_]C21|J00[-_]J24|SOURCE_READ_REPORT\.md)') {
           $denial = 'Geschuetzter Quellen-/Kanonpfad: nicht direkt bearbeiten. Erst Originalrevision, Storyfreigabe und separaten Patchprozess klaeren.'
        }
    }
    if ($denial) {
      [Console]::Out.WriteLine((@{hookSpecificOutput=@{hookEventName='PreToolUse';permissionDecision='deny';permissionDecisionReason=$denial}} | ConvertTo-Json -Compress -Depth 4))
    }
    exit 0
} catch {
    [Console]::Error.WriteLine('GENESIS PreToolUse guard validation failure: ' + $_.Exception.Message)
    exit 2
}
