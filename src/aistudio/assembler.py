"""Asset Assembler & Machine Gate: Assembles raw and generated assets into 03_assets_hub."""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List

def assemble_assets(project_dir: Path) -> dict:
    """
    Scans 01_raw_assets/ and 02_generated/, copies/links standardized assets into 03_assets_hub/,
    runs Machine Gate assertions, and outputs assets_ready.lock.
    """
    project_dir = Path(project_dir)
    hub_dir = project_dir / "03_assets_hub"
    hub_dir.mkdir(parents=True, exist_ok=True)

    raw_dir = project_dir / "01_raw_assets"
    gen_dir = project_dir / "02_generated"

    assembled = []
    errors = []

    # 1. Collect generated assets
    if gen_dir.exists():
        for f in gen_dir.rglob("*"):
            if f.is_file() and not f.name.endswith(".lock") and not f.name.startswith("."):
                dest = hub_dir / f.name
                shutil.copy2(f, dest)
                assembled.append({
                    "name": f.name,
                    "source": "generated",
                    "path": str(dest),
                    "size": dest.stat().st_size
                })

    # 2. Collect selected raw assets (if referenced)
    # Check physical assertions (Machine Gate B)
    for asset in assembled:
        if asset["size"] == 0:
            errors.append(f"Zero-byte corrupt file: {asset['name']}")

    is_ready = len(errors) == 0 and len(assembled) > 0
    lock_file = hub_dir / "assets_ready.lock"

    status = {
        "is_ready": is_ready,
        "assembled_count": len(assembled),
        "assets": assembled,
        "errors": errors
    }

    if is_ready:
        with open(lock_file, "w", encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False, indent=2)

    return status
