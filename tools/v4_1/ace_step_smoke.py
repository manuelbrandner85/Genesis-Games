"""F1 smoke test for the local ACE-Step 1.5 install: one short instrumental cue, DiT only
(no 5Hz LM, so it fits next to a running Unreal Editor). Run with the ACE-Step venv python:

  <ace-step>/ACE-Step-1.5/.venv/Scripts/python.exe tools/v4_1/ace_step_smoke.py --out docs/evidence/F1
"""
import argparse, json, os, sys, time
from pathlib import Path

ROOT = Path(os.environ.get("ACESTEP_ROOT", "C:/Users/manue/AI-Tools/GENESIS/ace-step/ACE-Step-1.5"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seconds", type=float, default=30)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)                                   # the handler resolves checkpoints from the project root
    import torch
    from acestep.handler import AceStepHandler
    from acestep.inference import GenerationParams, GenerationConfig, generate_music

    t0 = time.time()
    dit = AceStepHandler()
    msg, ok = dit.initialize_service(project_root=str(ROOT), config_path="acestep-v15-turbo", device="cuda")
    if not ok:
        raise SystemExit("DiT init failed: " + str(msg))
    params = GenerationParams(
        caption="calm acoustic folk, fingerpicked guitar, soft accordion, light strings, "
                "small river village morning, warm and unhurried, no drums",
        instrumental=True, lyrics="[Instrumental]", bpm=84, keyscale="D Major", timesignature="4",
        duration=a.seconds, inference_steps=8, shift=3.0, seed=a.seed, thinking=False,
        use_cot_metas=False, use_cot_caption=False, use_cot_language=False)
    config = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[a.seed], audio_format="wav")
    t1 = time.time()
    res = generate_music(dit, None, params, config, save_dir=str(a.out))
    report = {"success": res.success, "error": getattr(res, "error", None),
              "files": [x.get("path") for x in (res.audios or [])],
              "init_s": round(t1 - t0, 1), "generate_s": round(time.time() - t1, 1),
              "max_vram_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2),
              "model": "ACE-Step/Ace-Step1.5 acestep-v15-turbo, seed %d" % a.seed}
    (a.out / "ace_step_smoke.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
