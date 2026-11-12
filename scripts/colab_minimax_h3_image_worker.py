#!/usr/bin/env python3
"""
YOUAI Cloud Video Factory — Remote Colab MiniMax-H3-Image Worker (v3.5)
======================================================================
Runs ON the Google Colab GPU VM (A100 80GB/40GB, L4 24GB, H100).
Operated via Pure-HTTP RPC Bridge by `minimax_h3_image_colab` and `colab_image_gen`.

Core Capabilities:
  1. Native 4K (4096x4096 / 3840x2160, 16MP) Direct Synthesis in ~10-25s.
  2. Fixed 6-Step Sampling (6 NFE, Distilled Flow Matching, No CFG).
  3. Single Checkpoint Multi-Task: Text-to-Image (T2I) & Multi-Image Editing
     with up to 16 Reference Images for character/asset consistency.
  4. 5TB Google Drive Model Vault Caching:
     - Automatically shares `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` (14.6 GiB)
       with the MiniMax-H3 Video stack (0 duplicate storage!).
     - Caches `minimax_h3_image_pruned_w4a8.safetensors` (or `INT8-ConvRot` 20.27 GiB)
       and `minimax_h3_image_vae.safetensors` under `/content/drive/MyDrive/AIStudio_Models/MiniMax-H3-Image`.
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

JOB_DIR = Path(os.environ.get("H3_IMG_JOB_DIR", "/content/h3_img_job"))
STATUS_PATH = JOB_DIR / "status.json"
COMFY_DIR = Path("/content/ComfyUI")
DRIVE_IMAGE_CACHE_DIR = Path("/content/drive/MyDrive/AIStudio_Models/MiniMax-H3-Image")
DRIVE_VIDEO_CACHE_DIR = Path("/content/drive/MyDrive/AIStudio_Models/MiniMax-H3")
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
    STATE["logs"] = (STATE["logs"] + [line])[-80:]
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
        raise RuntimeError(f"GPU capability {cap} ({gpu_name}) is below (8, 0); please use L4, A100, or H100.")

    if not cuda_ver.startswith("13"):
        log("Upgrading PyTorch to CUDA 13.0 (cu130) for A100/L4 optimized kernel execution...")
        subprocess.run(
            [
                sys.executable, "-m", "pip", "install", "-q",
                "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cu130",
            ],
            check=True,
        )

    if not COMFY_DIR.exists():
        log("Cloning Comfy-Org/ComfyUI (latest master with MiniMax H3 Image support)...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/Comfy-Org/ComfyUI.git", str(COMFY_DIR)],
            check=True,
        )
    else:
        # Pull latest master if already cloned
        try:
            subprocess.run(["git", "-C", str(COMFY_DIR), "pull", "--ff-only"], check=False)
        except Exception:
            pass

    subprocess.run(
        [
            sys.executable, "-m", "pip", "install", "-q",
            "-r", str(COMFY_DIR / "requirements.txt"),
            "huggingface_hub", "hf_xet", "pillow", "requests", "accelerate",
        ],
        check=True,
    )
    return {"gpu_name": gpu_name, "capability": cap, "vram_gib": vram_gib}


def ensure_models() -> None:
    from huggingface_hub import hf_hub_download

    os.environ["HF_XET_HIGH_PERFORMANCE"] = "1"
    image_repo = "Comfy-Org/MiniMax-H3-Image"
    video_repo = "Comfy-Org/MiniMax-H3"

    # Define required model files:
    # 1. Text Encoder (shared with video stack)
    # 2. Diffusion Transformer (W4A8 or INT8-ConvRot)
    # 3. Image VAE
    models = [
        {
            "category": "text_encoders",
            "name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
            "remote_repo": video_repo,
            "remote_path": "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
            "alt_drive_dir": DRIVE_VIDEO_CACHE_DIR / "text_encoders",
        },
        {
            "category": "diffusion_models",
            "name": "minimax_h3_image_pruned_w4a8.safetensors",
            "remote_repo": image_repo,
            "remote_path": "diffusion_models/minimax_h3_image_pruned_w4a8.safetensors",
            "alt_drive_dir": None,
        },
        {
            "category": "vae",
            "name": "minimax_h3_image_vae.safetensors",
            "remote_repo": image_repo,
            "remote_path": "vae/minimax_h3_image_vae.safetensors",
            "alt_drive_dir": None,
        },
    ]

    use_drive_cache = Path("/content/drive/MyDrive").exists()
    if use_drive_cache:
        DRIVE_IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        log(f"Google Drive Model Vault detected at {DRIVE_IMAGE_CACHE_DIR}", "download")

    for item in models:
        folder = item["category"]
        fname = item["name"]
        repo = item["remote_repo"]
        remote_name = item["remote_path"]
        alt_dir = item["alt_drive_dir"]

        comfy_target = COMFY_DIR / "models" / folder / fname
        comfy_target.parent.mkdir(parents=True, exist_ok=True)

        if comfy_target.is_file() and comfy_target.stat().st_size > 0:
            log(f"Model ready in ComfyUI: {fname} ({comfy_target.stat().st_size / 2**30:.2f} GiB)")
            continue

        # Check Google Drive Cache
        found_in_drive = False
        if use_drive_cache:
            candidate_dirs = [DRIVE_IMAGE_CACHE_DIR / folder]
            if alt_dir:
                candidate_dirs.append(alt_dir)

            for c_dir in candidate_dirs:
                drive_p = c_dir / fname
                if drive_p.is_file() and drive_p.stat().st_size > 0:
                    log(f"Mounting cached model from 5TB Google Drive Model Vault: {fname}...")
                    if comfy_target.exists() or comfy_target.is_symlink():
                        comfy_target.unlink()
                    comfy_target.symlink_to(drive_p)
                    found_in_drive = True
                    break

        if found_in_drive:
            continue

        # Download from Hugging Face
        t0 = time.time()
        log(f"Downloading {fname} from {repo}...", "download")
        dl_root = COMFY_DIR / "models" / folder
        got = Path(hf_hub_download(repo_id=repo, filename=remote_name, local_dir=dl_root))
        if got != comfy_target:
            shutil.move(str(got), str(comfy_target))
        size_gib = comfy_target.stat().st_size / (2**30)
        log(f"Downloaded {fname} ({size_gib:.2f} GiB) in {time.time() - t0:.1f}s")

        # Persist to Google Drive Model Vault
        if use_drive_cache:
            try:
                drive_target = DRIVE_IMAGE_CACHE_DIR / folder / fname
                drive_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(comfy_target, drive_target)
                log(f"Persisted {fname} to Google Drive Model Vault ({drive_target})")
            except Exception as e:
                log(f"Warning: could not persist {fname} to Drive cache: {e}")


def start_comfyui(vram_gib: float) -> subprocess.Popen:
    import requests

    try:
        r = requests.get(BASE_URL + "/system_stats", timeout=2)
        if r.ok:
            log("Reusing running ComfyUI server on 127.0.0.1:8188", "server")
            return None
    except Exception:
        pass

    log("Starting ComfyUI server for H3-Image on 127.0.0.1:8188...", "server")
    cmd = [
        sys.executable, str(COMFY_DIR / "main.py"),
        "--listen", "127.0.0.1", "--port", "8188", "--disable-auto-launch",
    ]
    if vram_gib < 38.0:
        cmd.append("--lowvram")

    log_f = open("/content/comfyui_h3_image.log", "a")
    proc = subprocess.Popen(cmd, cwd=str(COMFY_DIR), stdout=log_f, stderr=subprocess.STDOUT)
    for _ in range(150):
        if proc.poll() is not None:
            tail = Path("/content/comfyui_h3_image.log").read_text(errors="replace")[-3000:]
            raise RuntimeError(f"ComfyUI exited early:\n{tail}")
        try:
            if requests.get(BASE_URL + "/system_stats", timeout=2).ok:
                log("ComfyUI server is UP and ready for H3-Image!")
                return proc
        except Exception:
            time.sleep(2)
    raise TimeoutError("Timed out waiting for ComfyUI server.")


def compute_dimensions(resolution: str, aspect_ratio: str) -> tuple:
    """Return (width, height) aligned to 32px patch boundaries."""
    aspect_map = {
        "16:9": (16, 9),
        "9:16": (9, 16),
        "1:1": (1, 1),
        "21:9": (21, 9),
        "4:3": (4, 3),
        "3:4": (3, 4),
    }
    aw, ah = aspect_map.get(aspect_ratio, (16, 9))

    if resolution.lower() in ("4k", "16mp"):
        base_pixels = 4096 * 4096  # ~16.7MP
    elif resolution.lower() in ("2k", "4mp"):
        base_pixels = 2048 * 2048  # ~4.2MP
    else:  # 1k, 1080p
        base_pixels = 1920 * 1080  # ~2.1MP

    scale = (base_pixels / (aw * ah)) ** 0.5
    w = int(round(aw * scale / 32.0) * 32)
    h = int(round(ah * scale / 32.0) * 32)
    return w, h


def run_image_job(job: dict) -> dict:
    import requests
    from PIL import Image

    jid = job["id"]
    prompt = job["prompt"]
    resolution = job.get("resolution", "4k")
    aspect = job.get("aspect", "16:9")
    steps = int(job.get("steps", 6))
    seed = int(job.get("seed", 42))
    images = job.get("images", [])

    width, height = compute_dimensions(resolution, aspect)

    in_dir = COMFY_DIR / "input"
    in_dir.mkdir(parents=True, exist_ok=True)
    ref_names = []
    for idx, img_rel in enumerate(images, 1):
        src_p = JOB_DIR / img_rel if not Path(img_rel).is_absolute() else Path(img_rel)
        dst_name = f"h3img_{jid}_ref_{idx:02d}.png"
        with Image.open(src_p) as im:
            im.convert("RGB").save(in_dir / dst_name)
        ref_names.append(dst_name)

    diffusion_model = "minimax_h3_image_pruned_w4a8.safetensors"
    clip_model = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
    vae_model = "minimax_h3_image_vae.safetensors"

    # Base ComfyUI Graph
    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": diffusion_model, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": clip_model, "type": "minimax", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": vae_model}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
    }

    if ref_names:
        # Multi-Image Reference / Editing Mode (1 to 16 images)
        edit_inputs = {
            "clip": ["2", 0],
            "vae": ["3", 0],
            "prompt": prompt,
            "width": width,
            "height": height,
        }
        for i, rname in enumerate(ref_names[:16]):
            nid = str(100 + i)
            graph[nid] = {"class_type": "LoadImage", "inputs": {"image": rname}}
            edit_inputs[f"ref_images.ref_image_{i}"] = [nid, 0]

        graph["5"] = {"class_type": "MiniMaxH3ReferenceToImage", "inputs": edit_inputs}
        cond_node = ["5", 0]
        latent_node = ["5", 1]
    else:
        # Pure Text-to-Image (T2I) Mode
        graph["5"] = {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}}
        cond_node = ["4", 0]
        latent_node = ["5", 0]

    graph.update({
        "6": {"class_type": "BasicGuider", "inputs": {"model": ["1", 0], "conditioning": cond_node}},
        "7": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "8": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["1", 0], "scheduler": "simple", "steps": steps, "denoise": 1.0}},
        "10": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["8", 0], "sigmas": ["9", 0], "latent_image": latent_node},
        },
        "11": {"class_type": "VAEDecode", "inputs": {"samples": ["10", 0], "vae": ["3", 0]}},
        "12": {"class_type": "SaveImage", "inputs": {"images": ["11", 0], "filename_prefix": f"H3IMG_{jid}"}},
    })

    t0 = time.time()
    mode_str = f"Multi-Reference Edit ({len(ref_names)} images)" if ref_names else "Text-to-Image"
    log(f"Job {jid}: Submitting H3-Image {mode_str} [{width}x{height}, {steps} steps]...", "generating")

    res = requests.post(BASE_URL + "/prompt", json={"prompt": graph, "client_id": f"youai-img-{jid}"}, timeout=60)
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
            if "12" in outputs:
                break
        time.sleep(3)

    saved_images = outputs["12"].get("images", [])
    if not saved_images:
        raise RuntimeError(f"No output images found in ComfyUI output node 12: {outputs}")

    img_info = saved_images[0]
    src_img = COMFY_DIR / "output" / img_info.get("subfolder", "") / img_info["filename"]
    out_dir = JOB_DIR / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    dst_img = out_dir / f"{jid}.png"
    shutil.copy2(src_img, dst_img)

    elapsed = round(time.time() - t0, 1)
    log(f"Job {jid}: Completed 4K generation in {elapsed}s -> {dst_img} ({width}x{height}, {dst_img.stat().st_size / 2**20:.2f} MiB)")
    return {
        "id": jid,
        "status": "done",
        "file": f"{jid}.png",
        "width": width,
        "height": height,
        "bytes": dst_img.stat().st_size,
        "seconds": elapsed,
    }


def main() -> None:
    manifest_path = JOB_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    jobs = manifest.get("jobs", [])
    for j in jobs:
        STATE["jobs"][j["id"]] = {"status": "queued"}
    save_state()

    hw = ensure_comfyui_and_cuda13()
    ensure_models()
    start_comfyui(hw["vram_gib"])

    for j in jobs:
        jid = j["id"]
        STATE["jobs"][jid]["status"] = "running"
        save_state()
        try:
            info = run_image_job(j)
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
