#!/usr/bin/env python3
"""
Mint the OAuth refresh token used by scripts/gdrive_sa_upload.py.

Runs a loopback OAuth flow against a Google Cloud "Desktop app" OAuth client and
stores client_id / client_secret / refresh_token in
`~/.config/youai/gdrive_oauth.json` (mode 600).

Default scope is `drive.file`: the resulting token can only touch files this app
created, so it cannot read the rest of the user's Drive.

Create the OAuth client once:
  https://console.cloud.google.com/apis/credentials?project=<project>
  -> Create credentials -> OAuth client ID -> Application type: Desktop app

Usage:
  export GDRIVE_OAUTH_CLIENT_ID="xxxx.apps.googleusercontent.com"
  export GDRIVE_OAUTH_CLIENT_SECRET="GOCSPX-xxxx"
  python3 scripts/gdrive_oauth_login.py

  # then verify
  python3 scripts/gdrive_sa_upload.py --source ./test.txt --folder-id root
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
DEFAULT_SCOPE = "https://www.googleapis.com/auth/drive.file"
DEFAULT_OUT = Path.home() / ".config/youai/gdrive_oauth.json"


def _ssl_context() -> ssl.SSLContext:
    """Framework Python on macOS ships no root store; fall back to certifi."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:  # noqa: BLE001 - certifi is optional
        return ssl.create_default_context()


def _post_form(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60, context=_ssl_context()) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Mint a Google Drive OAuth refresh token (loopback flow).")
    parser.add_argument("--client-id", default=os.environ.get("GDRIVE_OAUTH_CLIENT_ID", ""))
    parser.add_argument("--client-secret", default=os.environ.get("GDRIVE_OAUTH_CLIENT_SECRET", ""))
    parser.add_argument("--scope", default=DEFAULT_SCOPE)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    if not args.client_id or not args.client_secret:
        print(
            "Error: --client-id/--client-secret (or GDRIVE_OAUTH_CLIENT_ID/"
            "GDRIVE_OAUTH_CLIENT_SECRET) are required. Create a Desktop app OAuth "
            "client at https://console.cloud.google.com/apis/credentials",
            file=sys.stderr,
        )
        return 1

    redirect_uri = f"http://127.0.0.1:{args.port}/"
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    state = secrets.token_urlsafe(16)

    auth_url = AUTH_ENDPOINT + "?" + urllib.parse.urlencode(
        {
            "client_id": args.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": args.scope,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )

    result: dict = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib naming
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" not in query:
                self.send_response(400)
                self.end_headers()
                return
            result["code"] = query["code"][0]
            result["state"] = query.get("state", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2>授权完成，可以关闭此页面</h2>".encode("utf-8"))

        def log_message(self, format: str, *args) -> None:  # noqa: A002 - stdlib signature
            return

    server = http.server.HTTPServer(("127.0.0.1", args.port), Handler)
    print("在浏览器打开下面的链接并同意授权：\n", flush=True)
    print(auth_url, flush=True)
    print(f"\n等待回调 {redirect_uri} ...", flush=True)
    while "code" not in result:
        server.handle_request()
    server.server_close()

    if result.get("state") != state:
        print("Error: state mismatch, aborting.", file=sys.stderr)
        return 1

    tokens = _post_form(
        TOKEN_ENDPOINT,
        {
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "code": result["code"],
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code_verifier": verifier,
        },
    )
    if "refresh_token" not in tokens:
        print(f"Error: no refresh_token in response: {tokens}", file=sys.stderr)
        return 1

    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "client_id": args.client_id,
                "client_secret": args.client_secret,
                "refresh_token": tokens["refresh_token"],
                "token_uri": TOKEN_ENDPOINT,
                "scopes": [args.scope],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    os.chmod(out, 0o600)
    print(f"\n已写入 {out}（scope={args.scope}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
