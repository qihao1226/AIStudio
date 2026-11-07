"""Gap Manifest Manager: Builds and validates the contract for Colab Multimodal Worker."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

VALID_TASK_TYPES = ["tts_narration", "text_to_image", "text_to_video", "asr_transcribe"]

class GapManifestBuilder:
    def __init__(self, project_id: str, project_title: str):
        self.manifest = {
            "project_id": project_id,
            "project_title": project_title,
            "global_style_preset": {
                "image_style": "cinematic lighting, modern clean tech blueprint, high contrast, 8k resolution, minimalist",
                "video_style": "slow smooth cinematic camera movement, 4k, photorealistic",
                "tts_voice_reference": None
            },
            "tasks": []
        }

    def set_style_preset(self, image_style: Optional[str] = None, video_style: Optional[str] = None, tts_ref: Optional[str] = None):
        if image_style:
            self.manifest["global_style_preset"]["image_style"] = image_style
        if video_style:
            self.manifest["global_style_preset"]["video_style"] = video_style
        if tts_ref:
            self.manifest["global_style_preset"]["tts_voice_reference"] = tts_ref

    def add_tts_task(self, task_id: str, text: str, output_path: str, ref_audio: Optional[str] = None, speed: float = 1.0):
        self.manifest["tasks"].append({
            "task_id": task_id,
            "type": "tts_narration",
            "model": "f5-tts",
            "params": {
                "text": text,
                "ref_audio": ref_audio or self.manifest["global_style_preset"].get("tts_voice_reference"),
                "speed": speed
            },
            "output_path": output_path
        })

    def add_image_task(self, task_id: str, prompt: str, output_path: str, aspect_ratio: str = "16:9", steps: int = 4, seed: Optional[int] = None):
        self.manifest["tasks"].append({
            "task_id": task_id,
            "type": "text_to_image",
            "model": "flux-schnell",
            "params": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "steps": steps,
                "seed": seed
            },
            "output_path": output_path
        })

    def add_video_task(self, task_id: str, prompt: str, output_path: str, duration_seconds: int = 5, aspect_ratio: str = "16:9"):
        self.manifest["tasks"].append({
            "task_id": task_id,
            "type": "text_to_video",
            "model": "cogvideox-2b",
            "params": {
                "prompt": prompt,
                "duration_seconds": duration_seconds,
                "aspect_ratio": aspect_ratio
            },
            "output_path": output_path
        })

    def add_asr_task(self, task_id: str, audio_file: str, output_path: str):
        self.manifest["tasks"].append({
            "task_id": task_id,
            "type": "asr_transcribe",
            "model": "faster-whisper-large-v3",
            "params": {
                "audio_file": audio_file
            },
            "output_path": output_path
        })

    def save(self, filepath: Path) -> Path:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, ensure_ascii=False, indent=2)
        return filepath

def validate_manifest(manifest_path: Path) -> bool:
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "project_id" not in data or "tasks" not in data:
        raise ValueError("Invalid manifest: Missing 'project_id' or 'tasks'")

    for task in data["tasks"]:
        if "task_id" not in task or "type" not in task or "output_path" not in task:
            raise ValueError(f"Task {task} missing required keys")
        if task["type"] not in VALID_TASK_TYPES:
            raise ValueError(f"Task type {task['type']} is not supported")

    return True
