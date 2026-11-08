#!/usr/bin/env python3
"""
Uploads SOP 03 project deliverables to Google Drive folder 1bnZ8YCeAtaS8F1VkcIjHK3PXS9P4FaUw.
"""
import subprocess
import json
import re
from pathlib import Path

ROOT_FOLDER_ID = "1bnZ8YCeAtaS8F1VkcIjHK3PXS9P4FaUw"
LOCAL_PROJECT = Path("/home/antigravity/qihao1226/AIStudio/projects/20261108_sop03_whiteboard_master")

def create_folder(name: str, parent_id: str) -> str:
    print(f"Creating remote folder '{name}' in {parent_id}...", flush=True)
    out = subprocess.check_output([
        "gdrive", "mutate", "mkdir", name, "--parent", parent_id
    ], text=True)
    # Extract ID
    m = re.search(r"ID:\s*([a-zA-Z0-9_-]+)", out)
    if not m:
        raise RuntimeError(f"Could not parse folder ID from: {out}")
    fid = m.group(1)
    print(f"  -> Created '{name}': {fid}", flush=True)
    return fid

def upload_file(local_path: Path, parent_id: str):
    print(f"Uploading {local_path.name} ({local_path.stat().st_size} bytes) -> {parent_id}...", flush=True)
    subprocess.run([
        "gdrive", "mutate", "upload", str(local_path), "--parent", parent_id
    ], check=True)

def main():
    # 1. 00_需求界定
    f00 = create_folder("00_需求界定", ROOT_FOLDER_ID)
    upload_file(LOCAL_PROJECT / "00_需求界定/白板科普立项单.json", f00)

    # 2. 01_文案
    f01 = create_folder("01_文案", ROOT_FOLDER_ID)
    upload_file(LOCAL_PROJECT / "01_文案/旁白稿.md", f01)

    # 3. 02_场景 & 02_导演表
    f02 = create_folder("02_场景", ROOT_FOLDER_ID)
    upload_file(LOCAL_PROJECT / "02_场景/scenes.js", f02)
    upload_file(LOCAL_PROJECT / "02_场景/scenes_decision.json", f02)

    f02_dir = create_folder("02_导演表", ROOT_FOLDER_ID)
    upload_file(LOCAL_PROJECT / "02_导演表/scenes_decision.json", f02_dir)

    # 4. 03_素材
    f03 = create_folder("03_素材", ROOT_FOLDER_ID)
    upload_file(LOCAL_PROJECT / "03_素材/marker_foley.wav", f03)
    upload_file(LOCAL_PROJECT / "03_素材/narration.wav", f03)
    upload_file(LOCAL_PROJECT / "03_素材/final_mixed_audio.wav", f03)

    # 5. 08_判据
    f08 = create_folder("08_判据", ROOT_FOLDER_ID)
    upload_file(LOCAL_PROJECT / "08_判据/gatekeeper_report.json", f08)
    upload_file(LOCAL_PROJECT / "08_判据/pen_motion_report.json", f08)
    upload_file(LOCAL_PROJECT / "08_判据/final_contact_sheet.jpg", f08)

    # stills subfolder inside 08_判据
    f_stills = create_folder("stills", f08)
    for still in sorted((LOCAL_PROJECT / "08_判据/stills").glob("*.png")):
        upload_file(still, f_stills)

    # 6. 交付成片
    f_out = create_folder("交付成片", ROOT_FOLDER_ID)
    upload_file(LOCAL_PROJECT / "交付成片/final_whiteboard_1080p.mp4", f_out)
    upload_file(LOCAL_PROJECT / "交付成片/whiteboard_master.fcpxml", f_out)
    upload_file(LOCAL_PROJECT / "交付成片/封面-4x3.png", f_out)
    upload_file(LOCAL_PROJECT / "交付成片/封面-3x4.png", f_out)

    print("\n✅ All deliverables successfully uploaded to Google Drive!")

if __name__ == "__main__":
    main()
