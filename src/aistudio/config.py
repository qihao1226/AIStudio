"""Configuration and directory standards for AG_SOP_04 projects."""

import os
from pathlib import Path

# Base Paths
DEFAULT_PROJECTS_DIR = Path("/home/antigravity/qihao1226/AIStudio/projects")

# Google Drive Content Production Unified Architecture (ID: 1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc)
GOOGLE_DRIVE_CONTENT_ROOT_ID = "1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc"
GOOGLE_DRIVE_SOP04_DIR_ID = "19hiobDoFGopYu_4tgMjj-GX_DiiYzwFs"
GOOGLE_DRIVE_BASE_DIR = Path("/content/drive/MyDrive/YOUAI/内容生产/04_全源素材重构")
GOOGLE_DRIVE_FALLBACK_DIR = Path("/content/drive/MyDrive/内容生产/04_全源素材重构")

# Project Directory Standard Structure (AG_SOP_04 Specification)
PROJECT_SUBDIRS = [
    "00_立项与策划",
    "01_raw_assets/user_assets",
    "01_raw_assets/web_assets",
    "02_generated/voices",
    "02_generated/images",
    "02_generated/video_clips",
    "03_assets_hub",
    "04_编排工程/src"
]

# Supported media extensions
MEDIA_EXTENSIONS = {
    "video": [".mp4", ".mov", ".mkv", ".webm", ".avi"],
    "audio": [".mp3", ".wav", ".aac", ".m4a", ".flac", ".ogg"],
    "image": [".png", ".jpg", ".jpeg", ".webp", ".svg"],
    "document": [".pdf", ".md", ".txt", ".docx", ".pptx"]
}
