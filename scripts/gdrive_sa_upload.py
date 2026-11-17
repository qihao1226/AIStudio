#!/usr/bin/env python3
"""
Google Drive uploader for headless Interactions API sandboxes.

Credential modes, resolved in this order:

1. Explicit Service Account (`GOOGLE_APPLICATION_CREDENTIALS` set by the caller)
   - kept for Google Workspace shared drives, where a SA does own quota.
2. OAuth user credential with the minimal `drive.file` scope (default path)
   - `GDRIVE_ACCESS_TOKEN`: short-lived token injected at task time (1 h TTL).
   - `GDRIVE_OAUTH_JSON_B64` / `GDRIVE_OAUTH_JSON` / `~/.config/youai/gdrive_oauth.json`:
     a refresh token minted once by `scripts/gdrive_oauth_login.py`; it is
     exchanged for an access token automatically by google-auth.
3. Service Account file (`GDRIVE_SA_JSON_B64`, `GDRIVE_SA_JSON`, or
   `~/.config/youai/gdrive_sa.json`).

Why OAuth is the default: a Service Account owns no storage quota, so uploading
into a personal-account ("My Drive") folder fails with
`403 storageQuotaExceeded: Service Accounts do not have storage quota`.
Service accounts only work against Workspace shared drives.

Why `drive.file`: the app may only touch files it created, so the refresh token
cannot read anything else in the user's Drive. Creating a file inside an existing
user folder works in practice; if a parent is ever not writable the run falls back
to the app-owned `YOUAI产出` folder instead of failing the production run.

Usage:
  # OAuth (recommended)
  python3 scripts/gdrive_sa_upload.py \\
      --source ./projects/my_output \\
      --folder-id <drive_folder_id>

  # One-off with an injected short-lived token (no refresh token on the box)
  GDRIVE_ACCESS_TOKEN=ya29... python3 scripts/gdrive_sa_upload.py --source ./out
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path

DEFAULT_OAUTH_TOKEN_URI = "https://oauth2.googleapis.com/token"
OAUTH_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
SA_SCOPES = ["https://www.googleapis.com/auth/drive"]
DEFAULT_OAUTH_FILE = Path.home() / ".config/youai/gdrive_oauth.json"
DEFAULT_SA_FILE = Path.home() / ".config/youai/gdrive_sa.json"


def _oauth_info() -> dict | None:
    """Returns a dict with client_id / client_secret / refresh_token, or None."""
    for env in ("GDRIVE_OAUTH_JSON_B64", "GDRIVE_OAUTH_JSON"):
        raw = os.environ.get(env, "").strip()
        if raw:
            if env.endswith("_B64"):
                raw = base64.b64decode(raw).decode("utf-8")
            return json.loads(raw)

    oauth_file = Path(os.environ.get("GDRIVE_OAUTH_FILE") or DEFAULT_OAUTH_FILE)
    if oauth_file.exists():
        return json.loads(oauth_file.read_text(encoding="utf-8"))

    client_id = os.environ.get("GDRIVE_OAUTH_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GDRIVE_OAUTH_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("GDRIVE_OAUTH_REFRESH_TOKEN", "").strip()
    if client_id and client_secret and refresh_token:
        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }
    return None


def _oauth_credentials():
    from google.oauth2.credentials import Credentials

    access_token = os.environ.get("GDRIVE_ACCESS_TOKEN", "").strip()
    if access_token:
        return Credentials(token=access_token, scopes=OAUTH_SCOPES)

    info = _oauth_info()
    if not info:
        return None
    return Credentials(
        token=None,
        refresh_token=info["refresh_token"],
        token_uri=info.get("token_uri") or DEFAULT_OAUTH_TOKEN_URI,
        client_id=info["client_id"],
        client_secret=info["client_secret"],
        scopes=info.get("scopes") or OAUTH_SCOPES,
    )


def _service_account_credentials():
    from google.oauth2 import service_account

    sa_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if sa_path and Path(sa_path).exists():
        return service_account.Credentials.from_service_account_file(sa_path, scopes=SA_SCOPES)
    if os.environ.get("GDRIVE_SA_JSON_B64"):
        info = json.loads(base64.b64decode(os.environ["GDRIVE_SA_JSON_B64"]).decode("utf-8"))
        return service_account.Credentials.from_service_account_info(info, scopes=SA_SCOPES)
    if os.environ.get("GDRIVE_SA_JSON"):
        info = json.loads(os.environ["GDRIVE_SA_JSON"])
        return service_account.Credentials.from_service_account_info(info, scopes=SA_SCOPES)
    if DEFAULT_SA_FILE.exists():
        return service_account.Credentials.from_service_account_file(str(DEFAULT_SA_FILE), scopes=SA_SCOPES)
    return None


def load_credentials():
    # An explicitly exported SA path wins: the caller asked for it by name.
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip():
        creds = _service_account_credentials()
        if creds:
            return creds

    creds = _oauth_credentials()
    if creds:
        return creds

    creds = _service_account_credentials()
    if creds:
        return creds

    raise FileNotFoundError(
        "No Drive credentials found. Provide an OAuth refresh token "
        "(GDRIVE_OAUTH_JSON_B64 / GDRIVE_OAUTH_JSON / ~/.config/youai/gdrive_oauth.json, "
        "minted by scripts/gdrive_oauth_login.py), a short-lived GDRIVE_ACCESS_TOKEN, "
        "or a Service Account (GOOGLE_APPLICATION_CREDENTIALS / GDRIVE_SA_JSON_B64 / "
        "~/.config/youai/gdrive_sa.json)."
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
    parser = argparse.ArgumentParser(
        description="Upload file or directory to Google Drive (OAuth drive.file or Service Account)."
    )
    parser.add_argument("--source", required=True, help="Local file or directory to upload.")
    parser.add_argument(
        "--folder-id",
        default=os.environ.get("GDRIVE_ROOT_FOLDER_ID", ""),
        help="Target parent Google Drive folder ID. Empty or 'root' uploads to My Drive root.",
    )
    args = parser.parse_args()

    src = Path(args.source)
    if not src.exists():
        print(f"Error: Source path does not exist: {src}", file=sys.stderr)
        return 1

    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    creds = load_credentials()
    service = build("drive", "v3", credentials=creds)
    folder_id = args.folder_id.strip() or "root"

    def _upload(parent_id: str) -> str:
        if src.is_file():
            return upload_file(service, src, parent_id)
        return upload_directory(service, src, parent_id)

    try:
        url = _upload(folder_id)
    except HttpError as exc:
        status = getattr(exc.resp, "status", None)
        if status not in (403, 404) or folder_id == "root":
            raise
        # drive.file only covers files/folders this app created itself, so a
        # pre-existing user folder is invisible to it. Fall back to a dedicated
        # folder owned by the app instead of failing the whole production run.
        fallback_name = os.environ.get("GDRIVE_FALLBACK_FOLDER", "YOUAI产出")
        fallback_id = ensure_folder(service, fallback_name, "root")
        print(
            f"Warning: cannot write into folder {folder_id} (HTTP {status}).\n"
            f"  The drive.file scope only covers folders this app created itself.\n"
            f"  Falling back to the app-owned folder '{fallback_name}' ({fallback_id}).",
            file=sys.stderr,
        )
        url = _upload(fallback_id)

    print(f"DRIVE_URL={url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
