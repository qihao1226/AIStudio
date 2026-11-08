"""Persistent OAuth Helper for Google Colab CLI in Antigravity."""

import json
import os
import sys
from importlib import resources
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

PUBLIC_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/colaboratory",
    "https://www.googleapis.com/auth/drive.file",
]

REMOTE_REDIRECT_URI = "https://sdk.cloud.google.com/applicationdefaultauthcode.html"
CONFIG_DIR = Path(os.path.expanduser("~/.config/colab-cli"))
PENDING_FILE = CONFIG_DIR / "pending_oauth.json"
TOKEN_FILE = CONFIG_DIR / "token.json"
BACKUP_TOKEN_FILE = Path(os.path.expanduser("~/.gemini/colab_token.json"))

def _get_client_config():
    config_resource = resources.files("colab_cli").joinpath("oauth_config.json")
    return json.loads(config_resource.read_text())

def generate_auth_url() -> str:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    client_config = _get_client_config()
    flow = InstalledAppFlow.from_client_config(client_config, PUBLIC_SCOPES)
    flow.redirect_uri = REMOTE_REDIRECT_URI
    url, state = flow.authorization_url(prompt="consent", token_usage="remote")
    
    state_data = {
        "url": url,
        "state": state,
        "code_verifier": flow.code_verifier
    }
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=2)
    return url

def exchange_code(code: str) -> dict:
    if not PENDING_FILE.exists():
        raise FileNotFoundError(f"Pending OAuth session not found at {PENDING_FILE}")
    
    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        state_data = json.load(f)
    
    client_config = _get_client_config()
    flow = InstalledAppFlow.from_client_config(client_config, PUBLIC_SCOPES)
    flow.redirect_uri = REMOTE_REDIRECT_URI
    flow.code_verifier = state_data["code_verifier"]
    
    # Exchange code for tokens
    clean_code = code.strip()
    flow.fetch_token(code=clean_code)
    creds = flow.credentials
    
    token_json = creds.to_json()
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token_json)
    
    # Persist to ~/.gemini backup
    BACKUP_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BACKUP_TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token_json)
        
    return {
        "status": "success",
        "scopes": creds.scopes,
        "expiry": str(creds.expiry) if hasattr(creds, "expiry") else None
    }

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "url":
        print(generate_auth_url())
    elif len(sys.argv) > 2 and sys.argv[1] == "exchange":
        res = exchange_code(sys.argv[2])
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python colab_auth_helper.py [url|exchange <code>]")
