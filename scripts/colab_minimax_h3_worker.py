#!/usr/bin/env python3
"""
YOUAI Cloud Video Factory — Remote Colab MiniMax-H3 Worker (v3.0)
=================================================================
Runs ON the Google Colab GPU VM (A100 80GB/40GB, L4 24GB, G4, H100).
Launched asynchronously in the background by `minimax_h3_colab` CLI so long
model downloads and video generations never drop the RPC connection.

Key Industrial Optimizations over Community `minimax-h3-colab-skill` & `h3-colab-skill`:
  1. Fixes the A100 (sm_80) Ref2VA BF16 OOM Trap: verifies CUDA 13 (`cu130`) and forces
     `pruned_int8_convrot` (19.5 GiB) + `qwen3vl_32b_nvfp4_awq` (14.6 GiB) + `int8_convrot` Video VAE (2.6 GiB).
  2. 5TB Google Drive Model Vault: automatically caches and symlinks weights from
     `/content/drive/MyDrive/AIStudio_Models/MiniMax-H3` when Google Drive is mounted,
     reducing startup time to ~14 seconds.
  3. Supports both `reference` (Ref2VA 4-step Turbo LoRA, 1-9 images) and `first_frame`
     (FL2VA 8-step Turbo LoRA) with 24fps (`17k + 5` frame alignment) + 32kHz stereo audio.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

JOB_DIR = Path(os.environ.get("H3_JOB_DIR", "/content/h3_job"))
STATUS_PATH = JOB_DIR / "status.json"
COMFY_DIR = Path("/content/ComfyUI")
VHS_DIR = COMFY_DIR / "custom_nodes" / "ComfyUI-VideoHelperSuite"
DRIVE_CACHE_DIR = Path("/content/drive/MyDrive/AIStudio_Models/MiniMax-H3")
BASE_URL = "http://127.0.0.1:8188"

STATE = {
    "stage": "starting",
    "logs": [],
    "jobs": {},
    "done": False,
    "error": None,
    "started_at": time.time(),
}


def save_state() -> None:
    JOB_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATUS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(STATE, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATUS_PATH)


def log(msg: str, stage: str = None) -> None:
    if stage:
        STATE["stage"] = stage
    elapsed = time.time() - STATE["started_at"]
    line = f"[{elapsed:6.1f}s] {msg}"
    print(line, flush=True)
    STATE["logs"] = (STATE["logs"] + [line])[-60:]
    save_state()


def ensure_comfyui_and_cuda13() -> dict:
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("No CUDA GPU available on this Colab runtime.")

    gpu_name = torch.cuda.get_device_name(0)
    cap = torch.cuda.get_device_capability(0)
    vram_gib = round(torch.cuda.get_device_properties(0).total_memory / (2**30), 2)
    cuda_ver = torch.version.cuda or "0.0"
    log(f"GPU: {gpu_name} | Capability: {cap} | VRAM: {vram_gib} GiB | CUDA: {cuda_ver}", "install")

    if cap < (8, 0):
        raise RuntimeError(f"GPU capability {cap} ({gpu_name}) is below (8, 0); use L4, G4, A100, or H100.")

    if not cuda_ver.startswith("13"):
        log("Upgrading PyTorch to CUDA 13.0 (cu130) for A100/L4 INT8 ConvRot kernel support...")
        subprocess.run(
            [
                sys.executable, "-m", "pip", "install", "-q",
                "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cu130",
            ],
            check=True,
        )

    if not COMFY_DIR.exists():
        log("Cloning Comfy-Org/ComfyUI...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/Comfy-Org/ComfyUI.git", str(COMFY_DIR)],
            check=True,
        )
    subprocess.run(
        [
            sys.executable, "-m", "pip", "install", "-q",
            "-r", str(COMFY_DIR / "requirements.txt"),
            "huggingface_hub", "hf_xet", "pillow", "requests",
        ],
        check=True,
    )

    if not VHS_DIR.exists():
        log("Cloning ComfyUI-VideoHelperSuite...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git", str(VHS_DIR)],
            check=True,
        )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", str(VHS_DIR / "requirements.txt")],
        check=True,
    )
    return {"gpu_name": gpu_name, "capability": cap, "vram_gib": vram_gib}


def ensure_models(modes: set) -> None:
    from huggingface_hub import hf_hub_download

    os.environ["HF_XET_HIGH_PERFORMANCE"] = "1"
    base_repo = "Comfy-Org/MiniMax-H3"

    required = [
        (base_repo, "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "text_encoders"),
        (base_repo, "vae/minimax_h3_video_vae_int8_convrot.safetensors", "vae"),
        (base_repo, "vae/minimax_h3_audio_vae_fp32.safetensors", "vae"),
    ]
    if "reference" in modes:
        required.extend([
            (base_repo, "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors", "diffusion_models"),
            (base_repo, "loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors", "loras"),
        ])
    if "first_frame" in modes:
        required.extend([
            (base_repo, "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors", "diffusion_models"),
            ("drbaph/MiniMax-H3-Turbo-Lora-ComfyUI", "minimax_h3_turbo_v4_step600_ema_pruned_comfyui.safetensors", "loras"),
        ])

    use_drive_cache = Path("/content/drive/MyDrive").exists()
    if use_drive_cache:
        DRIVE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        log(f"Google Drive Model Vault detected at {DRIVE_CACHE_DIR}", "download")

    for repo, remote_name, folder in required:
        fname = Path(remote_name).name
        comfy_target = COMFY_DIR / "models" / folder / fname
        comfy_target.parent.mkdir(parents=True, exist_ok=True)

        if comfy_target.is_file() and comfy_target.stat().st_size > 0:
            log(f"Model ready in ComfyUI: {fname} ({comfy_target.stat().st_size / 2**30:.2f} GiB)")
            continue

        if use_drive_cache:
            drive_target = DRIVE_CACHE_DIR / folder / fname
            drive_target.parent.mkdir(parents=True, exist_ok=True)
            if drive_target.is_file() and drive_target.stat().st_size > 0:
                log(f"Mounting cached model from 5TB Google Drive: {fname}...")
                if comfy_target.exists() or comfy_target.is_symlink():
                    comfy_target.unlink()
                comfy_target.symlink_to(drive_target)
                continue

        t0 = time.time()
        log(f"Downloading {fname} from {repo}...", "download")
        dl_root = COMFY_DIR / "models" if repo == base_repo else COMFY_DIR / "models" / folder
        got = Path(hf_hub_download(repo_id=repo, filename=remote_name, local_dir=dl_root))
        if got != comfy_target:
            shutil.move(str(got), str(comfy_target))
        size_gib = comfy_target.stat().st_size / (2**30)
        log(f"Downloaded {fname} ({size_gib:.2f} GiB) in {time.time() - t0:.1f}s")

        if use_drive_cache:
            try:
                drive_target = DRIVE_CACHE_DIR / folder / fname
                drive_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(comfy_target, drive_target)
                log(f"Persisted {fname} to Google Drive Model Vault")
            except Exception as e:
                log(f"Warning: could not copy {fname} to Drive cache: {e}")


def start_comfyui(vram_gib: float) -> subprocess.Popen:
    import requests

    try:
        r = requests.get(BASE_URL + "/system_stats", timeout=2)
        if r.ok:
            log("Reusing running ComfyUI server on 127.0.0.1:8188", "server")
            return None
    except Exception:
        pass

    log("Starting ComfyUI server on 127.0.0.1:8188...", "server")
    cmd = [
        sys.executable, str(COMFY_DIR / "main.py"),
        "--listen", "127.0.0.1", "--port", "8188", "--disable-auto-launch",
    ]
    if vram_gib < 38.0:
        cmd.append("--lowvram")

    log_f = open("/content/comfyui_h3.log", "a")
    proc = subprocess.Popen(cmd, cwd=str(COMFY_DIR), stdout=log_f, stderr=subprocess.STDOUT)
    for _ in range(150):
        if proc.poll() is not None:
            tail = Path("/content/comfyui_h3.log").read_text(errors="replace")[-3000:]
            raise RuntimeError(f"ComfyUI exited early:\n{tail}")
        try:
            if requests.get(BASE_URL + "/system_stats", timeout=2).ok:
                log("ComfyUI server is UP and ready!")
                return proc
        except Exception:
            time.sleep(2)
    raise TimeoutError("Timed out waiting for ComfyUI server.")


def run_job(job: dict) -> dict:
    import requests
    from PIL import Image

    jid = job["id"]
    mode = job.get("mode", "reference")
    width = int(job.get("width", 960))
    height = int(job.get("height", 544))
    duration = float(job.get("duration_seconds", 5.0))
    seed = int(job.get("seed", 20261108))
    prompt = job["prompt"]

    req_frames = max(5, round(duration * 24))
    frames = req_frames + (5 - req_frames % 17) % 17
    steps = int(job.get("steps", 4 if mode == "reference" else 8))

    in_dir = COMFY_DIR / "input"
    in_dir.mkdir(parents=True, exist_ok=True)
    ref_names = []
    for idx, img_rel in enumerate(job.get("images", []), 1):
        src_p = JOB_DIR / img_rel if not Path(img_rel).is_absolute() else Path(img_rel)
        dst_name = f"h3_{jid}_ref_{idx:02d}.png"
        with Image.open(src_p) as im:
            im.convert("RGB").save(in_dir / dst_name)
        ref_names.append(dst_name)

    diffusion_name = (
        "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
        if mode == "reference"
        else "minimax_h3_fl2va_pruned_int8_convrot.safetensors"
    )
    lora_name = (
        "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors"
        if mode == "reference"
        else "minimax_h3_turbo_v4_step600_ema_pruned_comfyui.safetensors"
    )

    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": diffusion_name, "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": lora_name, "strength_model": 1.0}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_int8_convrot.safetensors"}},
        "5": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
    }

    if mode == "reference":
        pic_inputs = {
            "clip": ["3", 0], "vae": ["4", 0], "audio_vae": ["5", 0],
            "prompt": prompt, "width": width, "height": height, "length": frames,
            "ref_image_size": "match",
        }
        for i, rname in enumerate(ref_names):
            nid = str(100 + i)
            graph[nid] = {"class_type": "LoadImage", "inputs": {"image": rname}}
            pic_inputs[f"ref_images.ref_image_{i}"] = [nid, 0]
        graph["7"] = {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": pic_inputs}
    else:
        graph["6"] = {"class_type": "LoadImage", "inputs": {"image": ref_names[0]}}
        graph["16"] = {
            "class_type": "ImageScaleToTotalPixels",
            "inputs": {"image": ["6", 0], "upscale_method": "nearest-exact", "megapixels": 0.98, "resolution_steps": 32},
        }
        graph["7"] = {
            "class_type": "MiniMaxH3ImageToVideo",
            "inputs": {
                "clip": ["3", 0], "vae": ["4", 0], "first_frame": ["16", 0],
                "prompt": prompt, "width": width, "height": height, "length": frames,
            },
        }

    graph.update({
        "8": {"class_type": "BasicGuider", "inputs": {"model": ["2", 0], "conditioning": ["7", 0]}},
        "9": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "11": {"class_type": "BasicScheduler", "inputs": {"model": ["2", 0], "scheduler": "beta", "steps": steps, "denoise": 1.0}},
        "12": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {"noise": ["9", 0], "guider": ["8", 0], "sampler": ["10", 0], "sigmas": ["11", 0], "latent_image": ["7", 1]},
        },
        "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["4", 0]}},
        "14": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["12", 0], "vae": ["5", 0]}},
        "15": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["13", 0], "audio": ["14", 0], "frame_rate": 24,
                "loop_count": 0, "filename_prefix": f"H3_{jid}",
                "format": "video/h264-mp4", "pix_fmt": "yuv420p", "crf": 20,
                "save_metadata": True, "trim_to_audio": False, "pingpong": False, "save_output": True,
            },
        },
    })

    t0 = time.time()
    log(f"Job {jid}: Submitting {mode} ({width}x{height}, {frames}f, {steps} steps)...", "generating")
    res = requests.post(BASE_URL + "/prompt", json={"prompt": graph, "client_id": f"youai-{jid}"}, timeout=60)
    if not res.ok:
        raise RuntimeError(f"ComfyUI prompt submit failed ({res.status_code}): {res.text}")
    prompt_id = res.json()["prompt_id"]

    while True:
        h = requests.get(BASE_URL + f"/history/{prompt_id}", timeout=30).json()
        if prompt_id in h:
            run_info = h[prompt_id]
            if run_info.get("status", {}).get("status_str") == "error":
                raise RuntimeError(f"ComfyUI execution error: {json.dumps(run_info.get('status', {}), ensure_ascii=False)}")
            outputs = run_info.get("outputs", {})
            if "15" in outputs:
                break
        time.sleep(4)

    gifs = outputs["15"].get("gifs", [])
    mp4_info = next(item for item in gifs if item["filename"].endswith(".mp4"))
    src_mp4 = COMFY_DIR / "output" / mp4_info.get("subfolder", "") / mp4_info["filename"]
    out_dir = JOB_DIR / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    dst_mp4 = out_dir / f"{jid}.mp4"
    shutil.copy2(src_mp4, dst_mp4)
    elapsed = round(time.time() - t0, 1)
    log(f"Job {jid}: Completed in {elapsed}s -> {dst_mp4} ({dst_mp4.stat().st_size / 2**20:.2f} MiB)")
    return {"id": jid, "status": "done", "file": f"{jid}.mp4", "bytes": dst_mp4.stat().st_size, "seconds": elapsed}


def main() -> None:
    manifest_path = JOB_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    jobs = manifest.get("jobs", [])
    for j in jobs:
        STATE["jobs"][j["id"]] = {"status": "queued"}
    save_state()

    hw = ensure_comfyui_and_cuda13()
    modes = {j.get("mode", "reference") for j in jobs}
    ensure_models(modes)
    start_comfyui(hw["vram_gib"])

    for j in jobs:
        jid = j["id"]
        STATE["jobs"][jid]["status"] = "running"
        save_state()
        try:
            info = run_job(j)
            STATE["jobs"][jid].update(info)
        except Exception as e:
            STATE["jobs"][jid].update({"status": "error", "error": str(e)[:1000]})
            log(f"Job {jid} FAILED: {e}", "error")
        save_state()

    STATE["done"] = True
    STATE["stage"] = "finished"
    save_state()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        STATE["done"] = True
        STATE["stage"] = "failed"
        STATE["error"] = f"{e}\n{traceback.format_exc()[-1500:]}"
        save_state()
        raise
