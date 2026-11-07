"""Material Inventory Scanner: Scans user assets and web assets for AG_SOP_04."""

import os
import json
import subprocess
from pathlib import Path
from .config import MEDIA_EXTENSIONS

def probe_file(file_path: Path) -> dict:
    """Uses ffprobe to extract media metadata."""
    meta = {
        "path": str(file_path),
        "filename": file_path.name,
        "size_bytes": file_path.stat().st_size,
        "extension": file_path.suffix.lower(),
        "category": "unknown"
    }

    # Identify category
    for cat, exts in MEDIA_EXTENSIONS.items():
        if meta["extension"] in exts:
            meta["category"] = cat
            break

    # Probe multimedia files
    if meta["category"] in ["video", "audio", "image"]:
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", str(file_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                fmt = data.get("format", {})
                meta["duration_seconds"] = float(fmt.get("duration", 0.0))
                meta["bit_rate"] = int(fmt.get("bit_rate", 0))

                for stream in data.get("streams", []):
                    codec_type = stream.get("codec_type")
                    if codec_type == "video" and "width" in stream:
                        meta["width"] = stream.get("width")
                        meta["height"] = stream.get("height")
                        meta["codec"] = stream.get("codec_name")
                        break
                    elif codec_type == "audio" and "sample_rate" in stream:
                        meta["sample_rate"] = stream.get("sample_rate")
                        meta["channels"] = stream.get("channels")
        except Exception:
            pass

    return meta

def scan_inventory(project_dir: Path) -> dict:
    """Scans raw assets and writes material_inventory.json."""
    raw_dir = project_dir / "01_raw_assets"
    user_assets_dir = raw_dir / "user_assets"
    web_assets_dir = raw_dir / "web_assets"

    inventory = {
        "project_dir": str(project_dir),
        "user_assets": [],
        "web_assets": [],
        "total_files": 0
    }

    if user_assets_dir.exists():
        for f in user_assets_dir.rglob("*"):
            if f.is_file() and not f.name.startswith("."):
                inventory["user_assets"].append(probe_file(f))

    if web_assets_dir.exists():
        for f in web_assets_dir.rglob("*"):
            if f.is_file() and not f.name.startswith("."):
                inventory["web_assets"].append(probe_file(f))

    inventory["total_files"] = len(inventory["user_assets"]) + len(inventory["web_assets"])

    output_path = raw_dir / "material_inventory.json"
    raw_dir.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

    return inventory
