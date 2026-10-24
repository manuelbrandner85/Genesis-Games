"""Download CC0 textures/HDRIs from Poly Haven exactly as listed in an approved plan (V4.1).

    python -I tools/v4_1/polyhaven_fetch.py --plan docs/v4_1/install_plans/FA-POLYHAVEN-001.json --out ArtSource/External/PolyHaven

Only https://dl.polyhaven.org is contacted (URLs come from api.polyhaven.com/files), every file is
checked against the MD5 Poly Haven publishes, and a manifest with SHA-256, source URL and licence is
written next to the files. Nothing is executed or installed.
"""
import argparse, hashlib, json, time, urllib.parse, urllib.request
from pathlib import Path

API = "https://api.polyhaven.com/files/"
ALLOWED_HOST = "dl.polyhaven.org"
UA = {"User-Agent": "GENESIS-asset-fetch/1.0 (local game project)"}


def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.build_opener(urllib.request.ProxyHandler()).open(req, timeout=timeout) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    plan = json.loads(a.plan.read_text(encoding="utf8"))
    manifest = {"plan_id": plan["plan_id"], "licence": "CC0 1.0 (https://polyhaven.com/license)", "fetched_utc": None, "files": []}
    total = 0
    for item in plan["assets"]:
        files = json.loads(get(API + item["id"]))
        for m in item["maps"]:
            kind, res, fmt = m["map"], m["res"], m["format"]
            entry = files["hdri"][res][fmt] if kind == "hdri" else files[kind][res][fmt]
            url = entry["url"]
            if urllib.parse.urlparse(url).hostname != ALLOWED_HOST:
                raise SystemExit("refusing host " + url)
            dst = a.out / item["id"] / Path(urllib.parse.urlparse(url).path).name
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not (dst.exists() and hashlib.md5(dst.read_bytes()).hexdigest() == entry["md5"]):
                data = get(url, timeout=300)
                if hashlib.md5(data).hexdigest() != entry["md5"]:
                    raise SystemExit("MD5 mismatch " + url)
                dst.write_bytes(data)
            data = dst.read_bytes()
            total += len(data)
            manifest["files"].append({"asset": item["id"], "map": kind, "res": res, "file": str(dst.relative_to(a.out)).replace("\\", "/"),
                                      "bytes": len(data), "md5": entry["md5"], "sha256": hashlib.sha256(data).hexdigest(), "url": url})
            print("OK", dst.name, len(data))
    manifest["fetched_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    manifest["total_bytes"] = total
    (a.out / f"MANIFEST_{plan['plan_id']}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8")   # one per plan
    print("FETCH_DONE", len(manifest["files"]), "files", round(total / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
