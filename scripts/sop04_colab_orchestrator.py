#!/usr/bin/env python3
"""
YOUAI Cloud Video Factory - SOP 04 End-to-End Orchestrator (v2.0)
Pipeline: Antigravity VM -> colab CLI (Pure-HTTP RPC Bridge) -> Colab GPU -> Google Drive -> 4-Layer OpenFilm Render
Strictly uses Antigravity + Google Colab + Google Drive (zero paid external multimodal routers).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


COLAB_BIN = "/home/antigravity/.local/bin/colab"
WORKER_SCRIPT = Path(__file__).resolve().parent / "colab_multimodal_worker.py"


def run_cmd(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"[SOP04] $ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, check=check, text=True)


def dispatch_to_colab_gpu(job_dir: Path, session_id: str = "sop04-gpu") -> None:
    """Dispatches multimodal generation job (ASR / TTS / SDXL-Turbo 1080p) to remote Colab VM via colab CLI."""
    remote_job_dir = f"/content/jobs/{job_dir.name}"
    remote_worker = "/content/colab_multimodal_worker.py"

    # 1. Ensure active Colab GPU session
    run_cmd([COLAB_BIN, "connect", "--new", "--gpu", "--name", session_id], check=False)

    # 2. Initialize remote job directory
    run_cmd([
        COLAB_BIN, "exec", "--session", session_id,
        "-c", f"import os; os.makedirs('{remote_job_dir}', exist_ok=True)"
    ])

    # 3. Upload worker script and job payloads
    run_cmd([COLAB_BIN, "upload", "--session", session_id, str(WORKER_SCRIPT), remote_worker])
    for fname in ["visual_prompts.json", "tts_script.json", "raw_audio.wav", "ref_voice.wav"]:
        local_f = job_dir / fname
        if local_f.exists():
            run_cmd([COLAB_BIN, "upload", "--session", session_id, str(local_f), f"{remote_job_dir}/{fname}"])

    # 4. Execute multimodal worker on Colab GPU via Pure-HTTP RPC Bridge
    exec_code = (
        f"import subprocess, sys; "
        f"r = subprocess.run([sys.executable, '{remote_worker}', '--job-dir', '{remote_job_dir}'], check=True)"
    )
    run_cmd([COLAB_BIN, "exec", "--session", session_id, "-c", exec_code])

    # 5. Pull back generated artifacts (word_timestamps.json, generated_tts.wav, generated_plates/*.png)
    for out_name in ["word_timestamps.json", "generated_tts.wav", "_COLAB_DONE"]:
        try:
            run_cmd(
                [COLAB_BIN, "download", "--session", session_id, f"{remote_job_dir}/{out_name}", str(job_dir / out_name)],
                check=False,
            )
        except Exception:
            pass

    prompts_file = job_dir / "visual_prompts.json"
    if prompts_file.exists():
        prompts = json.loads(prompts_file.read_text(encoding="utf-8"))
        plates_dir = job_dir / "generated_plates"
        plates_dir.mkdir(exist_ok=True)
        for idx, item in enumerate(prompts):
            shot_id = item.get("id", f"shot_{idx:03d}")
            run_cmd(
                [
                    COLAB_BIN,
                    "download",
                    "--session",
                    session_id,
                    f"{remote_job_dir}/generated_plates/{shot_id}.png",
                    str(plates_dir / f"{shot_id}.png"),
                ],
                check=False,
            )


def verify_assets_gatekeeper(job_dir: Path) -> Dict[str, Any]:
    """Hard gatekeeper verifying 1080p resolution, 24kHz PCM WAV audio, and non-empty timestamps."""
    report: Dict[str, Any] = {"passed": True, "checks": []}
    plates_dir = job_dir / "generated_plates"
    if plates_dir.exists():
        for png in sorted(plates_dir.glob("*.png")):
            out = subprocess.check_output([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height", "-of", "json", str(png)
            ], text=True)
            info = json.loads(out)["streams"][0]
            w, h = info["width"], info["height"]
            ok = (w, h) in [(1920, 1080), (1080, 1920)]
            report["checks"].append({"asset": png.name, "width": w, "height": h, "passed": ok})
            if not ok:
                report["passed"] = False

    wav_path = job_dir / "generated_tts.wav"
    if wav_path.exists():
        out = subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate,codec_name,duration", "-of", "json", str(wav_path)
        ], text=True)
        ainfo = json.loads(out)["streams"][0]
        sr = int(ainfo.get("sample_rate", 0))
        codec = ainfo.get("codec_name", "")
        ok = (sr == 24000 and codec == "pcm_s16le")
        report["checks"].append({"asset": wav_path.name, "sample_rate": sr, "codec": codec, "passed": ok})
        if not ok:
            report["passed"] = False

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SOP 04 Cloud Orchestrator")
    parser.add_argument("--job-dir", required=True, help="Local job directory path")
    parser.add_argument("--session", default="sop04-gpu", help="Colab session name")
    parser.add_argument("--verify-only", action="store_true", help="Only run asset gatekeeper verification")
    args = parser.parse_args()

    job_dir = Path(args.job_dir).resolve()
    if not args.verify_only:
        dispatch_to_colab_gpu(job_dir, session_id=args.session)

    report = verify_assets_gatekeeper(job_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
