#!/usr/bin/env bash
# Usage: tools/v4/g4/take_shot.sh <camera label> <WxH> <out.png> ["console cmds; separated"]
# Pilots the camera in the running editor, takes HighResShot, waits for the file, copies it.
set -euo pipefail
cd "$(dirname "$0")/../../.."
shots="Saved/Screenshots/WindowsEditor"
mkdir -p "$shots" Saved/G4
before=$(ls -1 "$shots" 2>/dev/null | wc -l)
echo "$1 $2 ${4:-}" > Saved/G4/shot_request.txt
python -I tools/v4/g4/ue_remote.py tools/v4/g4/g4_shot.py --wait 30 | grep G4_SHOT || true
for _ in $(seq 1 300); do
  now=$(ls -1 "$shots" 2>/dev/null | wc -l)
  if [ "$now" -gt "$before" ]; then
    sleep 2
    newest=$(ls -1t "$shots"/*.png | head -1)
    mkdir -p "$(dirname "$3")"
    cp "$newest" "$3"
    echo "SHOT $3"
    exit 0
  fi
  sleep 1
done
echo "SHOT_TIMEOUT" >&2
exit 1
