"""Reference images for GENESIS with the local FLUX.2 klein 4B (ComfyUI on 127.0.0.1 only).

Starts the GAMEFORGE portable ComfyUI if it is not running, renders one image per view and writes
the image plus a provenance record (prompt, seed, model hashes) next to it.

  python tools/v4_1/flux_klein_ref.py --asset SM_R03_Generator_N02 --view front34 --seed 7 \
      --prompt "..." --out ArtSource/Reference/G7
"""
import argparse, json, os, subprocess, time, urllib.request, uuid
from pathlib import Path

HOST, PORT = "127.0.0.1", 8188
COMFY = Path(os.environ.get("GENESIS_COMFYUI",
             "C:/Users/manue/Desktop/GAMEFORGE_GODMODE_v2_0/engines/ComfyUI_windows_portable"))
# Recorded in F0_FREE_AI_INVENTUR.md (SHA-256 of the installed files, Apache-2.0)
MODELS = {
    "unet": ("flux-2-klein-4b.safetensors", "ec3d4e733a771f61c052fb4856c48b336c55eaf2c65487c2a1faeb9bbda7a343"),
    "text_encoder": ("qwen_3_4b.safetensors", "6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a"),
    "vae": ("flux2-vae.safetensors", "868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3"),
}


def req(path, data=None, timeout=10):
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(f"http://{HOST}:{PORT}{path}", data=body,
                               headers={"Content-Type": "application/json"} if body else {})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(r, timeout=timeout) as resp:
        raw = resp.read()
        return json.loads(raw) if resp.headers.get("Content-Type", "").startswith("application/json") else raw


def online():
    try:
        return req("/system_stats", timeout=2)
    except OSError:
        return None


def ensure_comfy(log_dir):
    if online():
        return False
    log_dir.mkdir(parents=True, exist_ok=True)
    log = open(log_dir / "comfyui_genesis.log", "ab")
    subprocess.Popen([str(COMFY / "python_embeded/python.exe"), "-s", str(COMFY / "ComfyUI/main.py"),
                      "--listen", HOST, "--port", str(PORT), "--disable-auto-launch", "--windows-standalone-build"],
                     cwd=str(COMFY), stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                     creationflags=subprocess.CREATE_NO_WINDOW)
    for _ in range(160):
        if online():
            return True
        time.sleep(1.5)
    raise SystemExit("ComfyUI did not come up, see " + str(log_dir / "comfyui_genesis.log"))


def workflow(prompt, seed, w, h, steps, prefix):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": MODELS["unet"][0], "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": MODELS["text_encoder"][0], "type": "flux2", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": MODELS["vae"][0]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "6": {"class_type": "Flux2Scheduler", "inputs": {"steps": steps, "width": w, "height": h}},
        "7": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "8": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "9": {"class_type": "CFGGuider", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["10", 0], "cfg": 1.0}},
        "10": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
        "11": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["7", 0], "guider": ["9", 0], "sampler": ["8", 0],
                                                                 "sigmas": ["6", 0], "latent_image": ["5", 0]}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "30": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": prefix}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset", required=True)
    ap.add_argument("--view", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--width", type=int, default=1536)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--steps", type=int, default=4)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    started = ensure_comfy(a.out / "_logs")
    t0 = time.time()
    pid = req("/prompt", {"prompt": workflow(a.prompt, a.seed, a.width, a.height, a.steps, "genesis_" + a.asset),
                          "client_id": uuid.uuid4().hex}, timeout=30)["prompt_id"]
    while True:
        h = req("/history/" + pid, timeout=10)
        if pid in h:
            entry = h[pid]
            break
        time.sleep(2)
    if entry.get("status", {}).get("status_str") != "success":
        raise SystemExit("generation failed: " + json.dumps(entry.get("status"))[:800])
    img = entry["outputs"]["30"]["images"][0]
    data = req(f"/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}", timeout=30)
    dst = a.out / a.asset
    dst.mkdir(parents=True, exist_ok=True)
    n = len(list(dst.glob(f"{a.view}_v*.png"))) + 1
    png = dst / f"{a.view}_v{n}.png"
    png.write_bytes(data)
    meta = {"asset": a.asset, "view": a.view, "file": png.name, "status": "GENERATED_PREVIEW",
            "prompt": a.prompt, "seed": a.seed, "size": [a.width, a.height], "steps": a.steps, "cfg": 1.0,
            "sampler": "euler", "models": {k: {"file": f, "sha256": s} for k, (f, s) in MODELS.items()},
            "license": "FLUX.2 klein 4B Apache-2.0; not an approved game asset",
            "generator": "ComfyUI local 127.0.0.1", "seconds": round(time.time() - t0, 1), "comfy_started_now": started}
    png.with_suffix(".json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    print(json.dumps({"png": str(png), "seconds": meta["seconds"]}))


if __name__ == "__main__":
    main()
