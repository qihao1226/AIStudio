#!/usr/bin/env bash
# ==============================================================================
# YOUAI Cloud Video Factory - Persistent Environment Bootstrapper (v3.0)
# Restores CLI tools, skills, fonts, and patched google-colab-cli (Pure-HTTP RPC)
# across ephemeral Antigravity conversation VMs using /shared/user/.gemini/youai
# Uses Python byte-copy to avoid virtiofs inode replacement errors with coreutils cp.
# ==============================================================================
set -euo pipefail

PERSIST_ROOT="/shared/user/.gemini/youai"
REPO_ROOT="/home/antigravity/qihao1226/AIStudio"

echo "[youai-bootstrap] 1/5 Ensuring persistent directories on ${PERSIST_ROOT}..."
mkdir -p "${PERSIST_ROOT}/bin" \
         "${PERSIST_ROOT}/skills" \
         "${PERSIST_ROOT}/fonts" \
         "${PERSIST_ROOT}/config/colab-cli" \
         "${PERSIST_ROOT}/patches/colab-cli" \
         "/home/antigravity/.local/bin" \
         "/home/antigravity/.config/colab-cli" \
         "/home/antigravity/.local/share/fonts"

echo "[youai-bootstrap] 2/5 Linking /home/antigravity/skills -> ${PERSIST_ROOT}/skills..."
if [ ! -L "/home/antigravity/skills" ]; then
    rm -rf "/home/antigravity/skills"
    ln -s "${PERSIST_ROOT}/skills" "/home/antigravity/skills"
fi

echo "[youai-bootstrap] 3/5 Checking google-colab-cli installation..."
if [ ! -x "/home/antigravity/.local/bin/colab" ]; then
    uv tool install google-colab-cli
fi

echo "[youai-bootstrap] 4/5 Syncing CLI tools, colab-cli Pure-HTTP RPC patches, and credentials..."
python3 - <<'PY'
import os
from pathlib import Path

persist = Path("/shared/user/.gemini/youai")
repo_bin = Path("/home/antigravity/qihao1226/AIStudio/bin")
local_bin = Path("/home/antigravity/.local/bin")

# 1. Sync repo/bin <-> persist/bin -> local_bin
for src_dir in [persist / "bin", repo_bin]:
    if src_dir.exists():
        for p in src_dir.iterdir():
            if p.is_file():
                data = p.read_bytes()
                dst = local_bin / p.name
                dst.write_bytes(data)
                dst.chmod(0o755)
                if src_dir == repo_bin:
                    (persist / "bin" / p.name).write_bytes(data)

# 2. Restore colab-cli OAuth token (prefer permanent refresh_token in /shared/user/.gemini/colab_token.json)
master_tok = Path("/shared/user/.gemini/colab_token.json")
tok_src = persist / "config/colab-cli/token.json"
tok_dst = Path("/home/antigravity/.config/colab-cli/token.json")
if master_tok.exists():
    data = master_tok.read_bytes()
    tok_src.write_bytes(data)
    tok_dst.write_bytes(data)
elif tok_src.exists():
    tok_dst.write_bytes(tok_src.read_bytes())

# 3. Apply colab-cli Pure-HTTP RPC patches
colab_pkg = Path("/home/antigravity/.local/share/uv/tools/google-colab-cli/lib/python3.13/site-packages/colab_cli")
patch_dir = persist / "patches/colab-cli"
if colab_pkg.exists() and patch_dir.exists():
    for name in ["http_rpc.py", "runtime.py", "contents.py"]:
        psrc = patch_dir / name
        if psrc.exists():
            (colab_pkg / name).write_bytes(psrc.read_bytes())

# 4. Sync fonts
font_dir = persist / "fonts"
local_fonts = Path("/home/antigravity/.local/share/fonts")
if font_dir.exists():
    for fp in font_dir.iterdir():
        if fp.is_file() and fp.suffix.lower() in (".ttf", ".otf", ".ttc", ".woff2", ".css"):
            (local_fonts / fp.name).write_bytes(fp.read_bytes())
PY

fc-cache -f "/home/antigravity/.local/share/fonts" 2>/dev/null || true
echo "[youai-bootstrap] 5/5 ✅ All CLI tools, skills, fonts, and Colab RPC bridge ready!"
