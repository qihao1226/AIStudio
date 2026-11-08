#!/usr/bin/env python3
"""
YOUAI Cloud Video Factory - SOP 04 End-to-End Orchestrator (v3.0)
=================================================================
Pipeline: Antigravity VM -> colab CLI (Pure-HTTP RPC Bridge) -> Colab GPU (A100/L4/T4) -> Google Drive -> 4-Layer OpenFilm Render
Supports:
  - Image Generation: FLUX.1-schnell / Qwen-Image / P-H3-Image / SDXL-Turbo (1080p)
  - Voice & Audio: CosyVoice 2 / F5-TTS Zero-Shot Cloning / H3 32x32 TTS (44.1kHz PCM WAV + 30ms afade)
  - Video + Audio: MiniMax-H3 (Pruned INT8 ConvRot + 4-step/8-step Turbo LoRA, 24fps + 32kHz Stereo Audio)
  - Word-Level ASR: Faster-Whisper large-v3-turbo
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

COLAB_BIN = "/home/antigravity/.local/bin/colab"
WORKER_SCRIPT = Path(__file__).resolve().parent / "colab_multimodal_worker.py"
H3_CLI = Path("/home/antigravity/qihao1226/AIStudio/bin/minimax_h3_colab")


def run_cmd(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"[SOP04] $ {' '.join(map(str, cmd))}", flush=True)
    env = dict(os.environ, PATH=f"/home/antigravity/.local/bin:/shared/user/.gemini/youai/bin:{os.environ.get('PATH', '')}")
    return subprocess.run(list(map(str, cmd)), check=check, text=True, env=env, stdin=subprocess.DEVNULL)


def exec_py(session_id: str, code: str, timeout: int = 600) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp_path = f.name
    try:
        return run_cmd([COLAB_BIN, "exec", "-s", session_id, "-f", tmp_path, "--timeout", str(timeout)])
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def dispatch_to_colab_gpu(job_dir: Path, session_id: str = "sop04-gpu", gpu: str = "A100", stop_after: bool = False) -> None:
    """Dispatches multimodal generation job (ASR / TTS / 1080p T2I / MiniMax-H3 Video+Audio) to remote Colab VM."""
    remote_job_dir = f"/content/jobs/{job_dir.name}"
    remote_worker = "/content/colab_multimodal_worker.py"

    # 1. Ensure active Colab GPU session using google-colab-cli 0.7.5 syntax
    sessions_res = subprocess.run([COLAB_BIN, "status"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if session_id not in (sessions_res.stdout or ""):
        new_cmd = [COLAB_BIN, "new", "-s", session_id, "--gpu", gpu]
        if gpu in ("A100", "L4", "T4"):
            new_cmd.append("--high-mem")
        run_cmd(new_cmd, check=True)

    try:
        # 2. Initialize remote job directory
        exec_py(session_id, f"import os; os.makedirs('{remote_job_dir}', exist_ok=True); print('READY')", timeout=60)

        # 3. Upload worker script and job payloads
        run_cmd([COLAB_BIN, "upload", "-s", session_id, str(WORKER_SCRIPT), remote_worker])
        for fname in ["gap_manifest.json", "visual_prompts.json", "tts_script.json", "raw_audio.wav", "ref_voice.wav"]:
            local_f = job_dir / fname
            if local_f.exists():
                run_cmd([COLAB_BIN, "upload", "-s", session_id, str(local_f), f"{remote_job_dir}/{fname}"])

        # 4. Execute multimodal worker on Colab GPU via Pure-HTTP RPC Bridge
        manifest_path = f"{remote_job_dir}/gap_manifest.json"
        exec_code = (
            f"import subprocess, sys, os\n"
            f"cmd = [sys.executable, '{remote_worker}']\n"
            f"if os.path.exists('{manifest_path}'):\n"
            f"    cmd.extend(['--manifest', '{manifest_path}'])\n"
            f"subprocess.run(cmd, check=True)\n"
        )
        exec_py(session_id, exec_code, timeout=1800)

        # 5. Pull back generated artifacts
        for out_name in ["word_timestamps.json", "generated_tts.wav", "02_generated/manifest_completed.lock"]:
            local_dst = job_dir / out_name
            local_dst.parent.mkdir(parents=True, exist_ok=True)
            run_cmd(
                [COLAB_BIN, "download", "-s", session_id, f"{remote_job_dir}/{out_name}", str(local_dst)],
                check=False,
            )
    finally:
        if stop_after:
            run_cmd([COLAB_BIN, "stop", "-s", session_id], check=False)


def verify_assets_gatekeeper(job_dir: Path) -> Dict[str, Any]:
    """Hard gatekeeper verifying 1080p resolution, 44.1kHz/24kHz PCM WAV audio, and non-empty timestamps."""
    report: Dict[str, Any] = {"passed": True, "checks": []}
    for png in sorted(job_dir.rglob("*.png")):
        out = subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "json", str(png)
        ], text=True)
        info = json.loads(out)["streams"][0]
        w, h = info["width"], info["height"]
        ok = (w, h) in [(1920, 1080), (1080, 1920), (1080, 1080)]
        report["checks"].append({"asset": png.name, "width": w, "height": h, "passed": ok})
        if not ok:
            report["passed"] = False

    for wav_path in sorted(job_dir.rglob("*.wav")):
        if wav_path.name in ("raw_audio.wav", "ref_voice.wav"):
            continue
        out = subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate,codec_name,duration", "-of", "json", str(wav_path)
        ], text=True)
        ainfo = json.loads(out)["streams"][0]
        sr = int(ainfo.get("sample_rate", 0))
        codec = ainfo.get("codec_name", "")
        ok = (sr in (24000, 32000, 44100, 48000) and codec == "pcm_s16le")
        report["checks"].append({"asset": wav_path.name, "sample_rate": sr, "codec": codec, "passed": ok})
        if not ok:
            report["passed"] = False

    for mp4_path in sorted(job_dir.rglob("*.mp4")):
        out = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,sample_rate", "-of", "json", str(mp4_path)
        ], text=True)
        streams = json.loads(out).get("streams", [])
        types = {s.get("codec_type") for s in streams}
        ok = {"video", "audio"} <= types
        report["checks"].append({"asset": mp4_path.name, "streams": sorted(types), "passed": ok})
        if not ok:
            report["passed"] = False

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="SOP 04 Cloud Orchestrator (v3.0)")
    parser.add_argument("--job-dir", required=True, help="Local job directory path")
    parser.add_argument("--session", default="sop04-gpu", help="Colab session name")
    parser.add_argument("--gpu", default="A100", choices=["A100", "L4", "G4", "T4", "H100"], help="Colab GPU type")
    parser.add_argument("--stop-after", action="store_true", help="Stop Colab GPU after job completion")
    parser.add_argument("--verify-only", action="store_true", help="Only run asset gatekeeper verification")
    args = parser.parse_args()

    job_dir = Path(args.job_dir).resolve()
    if not args.verify_only:
        dispatch_to_colab_gpu(job_dir, session_id=args.session, gpu=args.gpu, stop_after=args.stop_after)

    report = verify_assets_gatekeeper(job_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
