#!/usr/bin/env python3
"""
Google Drive Uploader via Service Account (for headless Interactions API sandboxes).

Does not require Antigravity's built-in `gdrive` plugin or browser OAuth.
Shares deliverables into a target Google Drive folder that has been shared
with the Service Account email (Editor role).

Usage:
  python3 scripts/gdrive_sa_upload.py \
      --source ./projects/my_output \
      --folder-id 1bnZ8YCeAtaS8F1VkcIjHK3PXS9P4FaUw
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path


def load_credentials():
    from google.oauth2 import service_account

    scopes = ["https://www.googleapis.com/auth/drive"]
    sa_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    default_sa = Path.home() / ".config/youai/gdrive_sa.json"

    if sa_path and Path(sa_path).exists():
        return service_account.Credentials.from_service_account_file(sa_path, scopes=scopes)
    if default_sa.exists():
        return service_account.Credentials.from_service_account_file(str(default_sa), scopes=scopes)
    if os.environ.get("GDRIVE_SA_JSON_B64"):
        info = json.loads(base64.b64decode(os.environ["GDRIVE_SA_JSON_B64"]).decode("utf-8"))
        return service_account.Credentials.from_service_account_info(info, scopes=scopes)
    if os.environ.get("GDRIVE_SA_JSON"):
        info = json.loads(os.environ["GDRIVE_SA_JSON"])
        return service_account.Credentials.from_service_account_info(info, scopes=scopes)

    raise FileNotFoundError(
        "No Service Account credentials found. Set GOOGLE_APPLICATION_CREDENTIALS, "
        "GDRIVE_SA_JSON_B64, or place key at ~/.config/youai/gdrive_sa.json."
    )


def ensure_folder(service, name: str, parent_id: str) -> str:
    query = (
        f"name = '{name.replace(chr(39), chr(92) + chr(39))}' "
        f"and '{parent_id}' in parents "
        f"and mimeType = 'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )
    resp = service.files().list(
        q=query,
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = resp.get("files", [])
    if files:
        return files[0]["id"]

    meta = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    created = service.files().create(body=meta, fields="id", supportsAllDrives=True).execute()
    return created["id"]


def upload_file(service, local_path: Path, parent_id: str) -> str:
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(str(local_path), resumable=True)
    meta = {"name": local_path.name, "parents": [parent_id]}
    created = service.files().create(
        body=meta,
        media_body=media,
        fields="id, webViewLink",
        supportsAllDrives=True,
    ).execute()
    print(f"Uploaded {local_path.name} -> {created.get('webViewLink', created['id'])}", flush=True)
    return created.get("webViewLink", f"https://drive.google.com/file/d/{created['id']}/view")


def upload_directory(service, local_dir: Path, parent_id: str) -> str:
    target_id = ensure_folder(service, local_dir.name, parent_id)
    for item in sorted(local_dir.iterdir()):
        if item.name.startswith("."):
            continue
        if item.is_dir():
            upload_directory(service, item, target_id)
        elif item.is_file():
            upload_file(service, item, target_id)
    return f"https://drive.google.com/drive/folders/{target_id}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload file or directory to Google Drive via Service Account.")
    parser.add_argument("--source", required=True, help="Local file or directory to upload.")
    parser.add_argument(
        "--folder-id",
        default=os.environ.get("GDRIVE_ROOT_FOLDER_ID", "1bnZ8YCeAtaS8F1VkcIjHK3PXS9P4FaUw"),
        help="Target parent Google Drive folder ID.",
    )
    args = parser.parse_args()

    src = Path(args.source)
    if not src.exists():
        print(f"Error: Source path does not exist: {src}", file=sys.stderr)
        return 1

    from googleapiclient.discovery import build

    creds = load_credentials()
    service = build("drive", "v3", credentials=creds)

    if src.is_file():
        url = upload_file(service, src, args.folder_id)
    else:
        url = upload_directory(service, src, args.folder_id)

    print(f"DRIVE_URL={url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
