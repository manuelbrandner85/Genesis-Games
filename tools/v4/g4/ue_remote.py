"""Run a Python file inside the RUNNING (visible) Unreal Editor of this project.

    python tools/v4/g4/ue_remote.py <script.py> [--wait 600] [--project Genesis]

Uses Epic's remote_execution.py (PythonScriptPlugin, localhost multicast 239.0.0.1:6766).
Requires `bRemoteExecution=True` in Config/DefaultEngine.ini. Prints the editor's log output
of the script and exits non-zero if the script raised.
"""
import argparse
import sys
import time
from pathlib import Path

ENGINE_PY = Path(r"C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
sys.path.insert(0, str(ENGINE_PY))
import remote_execution as rex  # noqa: E402


def find_node(session, project, wait):
    end = time.time() + wait
    while time.time() < end:
        for node in session.remote_nodes:
            if node.get("project_name", "").lower() == project.lower():
                return node
        time.sleep(1.0)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("--wait", type=float, default=30.0, help="seconds to wait for the editor to appear")
    ap.add_argument("--project", default="Genesis")
    a = ap.parse_args()
    session = rex.RemoteExecution()
    session.start()
    try:
        node = find_node(session, a.project, a.wait)
        if not node:
            print(f"UE_REMOTE: no editor for project '{a.project}' found", file=sys.stderr)
            return 3
        session.open_command_connection(node["node_id"])
        res = session.run_command(str(a.script.resolve()), unattended=True, exec_mode=rex.MODE_EXEC_FILE)
        for line in res.get("output", []):
            print(f"[{line.get('type')}] {line.get('output')}".rstrip())
        if not res.get("success"):
            print("UE_REMOTE: script failed: " + str(res.get("result")), file=sys.stderr)
            return 1
        return 0
    finally:
        session.stop()


if __name__ == "__main__":
    sys.exit(main())
