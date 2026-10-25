"""C00: render the bedroom shots through the running Unreal Editor and filter them down (runs on the host, not in UE).

For each shot (default: bett wand weit raum tuer) c00_scene_bedroom.py is run with GENESIS_SZ_SHOT set; it writes a 2x
still to Saved/Shots/ (supersampling for the hair strands). That still is filtered down with a high-quality bicubic
filter (Windows System.Drawing via PowerShell - no extra Python packages) to
docs/evidence/V42/C00_Schlafzimmer_UE_<shot>.png.

  python tools/v4_2/c00_render_bedroom_shots.py [shot ...] [--reimport]
"""
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCENE = os.path.join(ROOT, "tools", "v4_2", "c00_scene_bedroom.py")
REMOTE = os.path.join(ROOT, "tools", "v4", "g4", "ue_remote.py")
PS = r'''Add-Type -AssemblyName System.Drawing
$src = [System.Drawing.Image]::FromFile($args[0])
$dst = New-Object System.Drawing.Bitmap 1600, 900
$g = [System.Drawing.Graphics]::FromImage($dst)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$g.DrawImage($src, (New-Object System.Drawing.Rectangle 0, 0, 1600, 900))
$src.Dispose()
$dst.Save($args[1], [System.Drawing.Imaging.ImageFormat]::Png)
'''


RESTORE = r'''Add-Type @"
using System; using System.Runtime.InteropServices;
public class GenW { [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); }
"@
Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" | Where-Object { $_.CommandLine -like '*\Genesis.uproject*' } |
  ForEach-Object { $h = (Get-Process -Id $_.ProcessId).MainWindowHandle; [GenW]::ShowWindow($h, 9) | Out-Null; [GenW]::SetForegroundWindow($h) | Out-Null }
'''


def restore_editor():
    """a minimised (or fully hidden) editor viewport does not render: the high-res still is then never written"""
    subprocess.run(["powershell", "-NoProfile", "-Command", RESTORE], capture_output=True)


def render(shot, reimport=False):
    restore_editor()
    big = os.path.join(ROOT, "Saved", "Shots", f"C00_Schlafzimmer_UE_{shot}_2x.png")
    out = os.path.join(ROOT, "docs", "evidence", "V42", f"C00_Schlafzimmer_UE_{shot}.png")
    os.makedirs(os.path.dirname(big), exist_ok=True)
    if os.path.exists(big):
        os.remove(big)
    env = {"GENESIS_SZ_SHOT": shot, "GENESIS_SZ_SS": "2"}
    if reimport:
        env["GENESIS_SZ_REIMPORT"] = "1"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf8") as f:
        f.write("import os\n")
        for k, v in env.items():
            f.write(f"os.environ[{k!r}] = {v!r}\n")
        f.write(f"try:\n    exec(compile(open({SCENE!r}, encoding='utf8').read(), {SCENE!r}, 'exec'), {{'__name__': 'x'}})\n")
        f.write("finally:\n" + "".join(f"    os.environ.pop({k!r}, None)\n" for k in env))
        wrapper = f.name
    r = subprocess.run([sys.executable, REMOTE, wrapper, "--wait", "900"], capture_output=True, text=True)
    os.remove(wrapper)
    if "Traceback" in r.stdout + r.stderr:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit(f"shot {shot} failed")
    for _ in range(120):                                   # the high-res screenshot is written a few frames later
        if os.path.exists(big) and os.path.getsize(big) > 0:
            time.sleep(2)
            break
        time.sleep(2)
    else:
        return False                                       # the editor skipped the still (busy/occluded): retried
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf8") as f:
        f.write(PS)
        ps = f.name
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps, big, out], check=True)
    os.remove(ps)
    print("C00_SHOT", shot, out)
    return True


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    shots = args or ["bett", "wand", "weit", "raum", "tuer"]
    for i, s in enumerate(shots):
        for attempt in range(3):
            if render(s, reimport="--reimport" in sys.argv and i == 0 and attempt == 0):
                break
        else:
            raise SystemExit(f"shot {s}: no screenshot after 3 attempts")
