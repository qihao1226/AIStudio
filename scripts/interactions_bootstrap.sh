#!/usr/bin/env bash
# ==============================================================================
# YOUAI Cloud Video Factory - Interactions API Sandbox Bootstrapper
# Standalone setup for Gemini Interactions API sandboxes (where /shared/user
# and Antigravity's built-in gdrive plugin are absent).
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "[interactions-bootstrap] 1/4 Ensuring directories..."
mkdir -p "${HOME}/.local/bin" \
         "${HOME}/.config/colab-cli" \
         "${HOME}/.config/youai" \
         "${HOME}/.local/share/fonts"

echo "[interactions-bootstrap] 2/4 Installing google-colab-cli & Google Drive SDK..."
if command -v uv >/dev/null 2>&1; then
    if ! command -v colab >/dev/null 2>&1 && [ ! -x "${HOME}/.local/bin/colab" ]; then
        uv tool install google-colab-cli
    fi
    uv pip install --system google-api-python-client google-auth requests 2>/dev/null || \
        python3 -m pip install --quiet --user google-api-python-client google-auth requests
else
    python3 -m pip install --quiet --user google-colab-cli google-api-python-client google-auth requests
fi

export PATH="${HOME}/.local/bin:${PATH}"

echo "[interactions-bootstrap] 3/4 Syncing repo/bin & applying colab-cli Pure-HTTP RPC patches..."
python3 - "${REPO_ROOT}" <<'PY'
import base64
import os
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
local_bin = Path.home() / ".local/bin"
repo_bin = repo_root / "bin"

if repo_bin.exists():
    for p in repo_bin.iterdir():
        if p.is_file():
            dst = local_bin / p.name
            dst.write_bytes(p.read_bytes())
            dst.chmod(0o755)

# Apply Pure-HTTP RPC patches to installed colab_cli package
patch_dir = repo_root / "scripts/patches/colab-cli"
if patch_dir.exists():
    import importlib.util
    spec = importlib.util.find_spec("colab_cli")
    if spec and spec.origin:
        colab_pkg = Path(spec.origin).parent
        for name in ["http_rpc.py", "runtime.py", "contents.py"]:
            psrc = patch_dir / name
            if psrc.exists():
                (colab_pkg / name).write_bytes(psrc.read_bytes())
        print(f"  -> Patched colab_cli at {colab_pkg}")
    else:
        # Also check uv tools site-packages
        uv_tools = Path.home() / ".local/share/uv/tools/google-colab-cli"
        for pkg in uv_tools.glob("lib/python*/site-packages/colab_cli"):
            for name in ["http_rpc.py", "runtime.py", "contents.py"]:
                psrc = patch_dir / name
                if psrc.exists():
                    (pkg / name).write_bytes(psrc.read_bytes())
            print(f"  -> Patched uv colab_cli at {pkg}")

# Restore Colab token from env if provided (COLAB_TOKEN_B64 or COLAB_TOKEN_JSON)
tok_dst = Path.home() / ".config/colab-cli/token.json"
if os.environ.get("COLAB_TOKEN_B64"):
    tok_dst.write_bytes(base64.b64decode(os.environ["COLAB_TOKEN_B64"]))
    print("  -> Restored colab-cli/token.json from COLAB_TOKEN_B64")
elif os.environ.get("COLAB_TOKEN_JSON"):
    tok_dst.write_text(os.environ["COLAB_TOKEN_JSON"], encoding="utf-8")
    print("  -> Restored colab-cli/token.json from COLAB_TOKEN_JSON")

# Restore Google Service Account JSON from env if provided
sa_dst = Path.home() / ".config/youai/gdrive_sa.json"
if os.environ.get("GDRIVE_SA_JSON_B64"):
    sa_dst.write_bytes(base64.b64decode(os.environ["GDRIVE_SA_JSON_B64"]))
    print("  -> Restored gdrive_sa.json from GDRIVE_SA_JSON_B64")
elif os.environ.get("GDRIVE_SA_JSON"):
    sa_dst.write_text(os.environ["GDRIVE_SA_JSON"], encoding="utf-8")
    print("  -> Restored gdrive_sa.json from GDRIVE_SA_JSON")
PY

echo "[interactions-bootstrap] 4/4 ✅ Sandbox ready!"
