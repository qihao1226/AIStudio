#!/usr/bin/env python3
"""
Grok Bot -> Gemini Interactions API (Antigravity Remote Agent) Trigger.

Runs on an overseas machine (e.g., Grok Bot cloud sandbox) to forward a Feishu
production requirement + prompt to the hosted Antigravity agent via the Gemini
Interactions API, without needing a VPN on the user's phone or Mac.

Usage:
  # Dry run (prints JSON payload without calling the API)
  python3 scripts/grok_trigger_antigravity.py --dry-run --prompt "按 AG_SOP_03 制作..."

  # Trigger background production from inline prompt or requirement file
  GEMINI_API_KEY=... python3 scripts/grok_trigger_antigravity.py \
      --title "白板科普：AI Agent 架构" \
      --prompt-file /path/to/requirement.md

  # Check status of a running interaction
  GEMINI_API_KEY=... python3 scripts/grok_trigger_antigravity.py --status <interaction_id>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_API_BASE = "https://generativelanguage.googleapis.com/v1beta/interactions"
DEFAULT_AGENT = os.environ.get("ANTIGRAVITY_AGENT_MODEL", "antigravity-preview-09-2026")
DEFAULT_REPO_URL = os.environ.get("AISTUDIO_REPO_URL", "https://github.com/qihao1226/AIStudio.git")
DEFAULT_DRIVE_FOLDER = os.environ.get("GDRIVE_ROOT_FOLDER_ID", "1bnZ8YCeAtaS8F1VkcIjHK3PXS9P4FaUw")


def build_agent_instruction(
    title: str,
    prompt_text: str,
    repo_url: str,
    drive_folder_id: str,
    feishu_webhook: str,
) -> str:
    """Builds the structured instruction sent to the Interactions API sandbox."""
    if feishu_webhook:
        notify_step = (
            f'- 完成后请使用 `python3 scripts/feishu_notify.py --webhook "{feishu_webhook}" '
            f'--title "{title}" --status success --drive-url "<DRIVE_URL>"` 发送飞书回执。\n'
            f'   - 若中途失败，也请调用 `scripts/feishu_notify.py --status error --summary "<失败原因>"` 通知用户。'
        )
    else:
        notify_step = (
            "- 完成后请在最终回复中清晰输出以下结构化结果（供 Hermes/Grok 通过飞书私聊回传用户）：\n"
            "     - `STATUS: success`（失败则为 `STATUS: error`）\n"
            "     - `DRIVE_URL: <上传后的 Google Drive 链接>`\n"
            "     - `SUMMARY: <交付物清单与简明摘要>`"
        )

    return f"""你现在处于 Gemini Interactions API 云端生产沙箱中，正在执行来自飞书的自动化内容生产任务。

## 任务标题
{title}

## 需求单与 Prompt
{prompt_text}

## 标准执行流程（严格按顺序）
1. **初始化环境**：
   - 如当前目录还没有 `AIStudio` 仓库，执行 `git clone {repo_url} AIStudio && cd AIStudio`（若已有则 `git pull`）。
   - 运行 `bash scripts/interactions_bootstrap.sh` 安装 `google-colab-cli`、Pure-HTTP RPC 补丁及依赖。
2. **执行生产计划与 Colab GPU 调度**：
   - 根据需求单与 `docs/sops/` 下对应的 SOP，通过 `colab` CLI 或 `scripts/colab_*_worker.py` 调度 Colab GPU 完成素材生产与装配。
3. **上传产物到 Google Drive**：
   - 使用 `python3 scripts/gdrive_sa_upload.py --source <产物目录或文件> --folder-id {drive_folder_id}` 上传全部交付物，并记录输出的 Drive 链接。
4. **回传结果**：
   {notify_step}
"""


def http_json(url: str, method: str, api_key: str, payload: dict | None = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Trigger Antigravity agent via Gemini Interactions API.")
    parser.add_argument("--title", default="飞书云端内容生产任务", help="Task title for tracking & Feishu card.")
    parser.add_argument("--prompt", default="", help="Inline requirement / prompt text.")
    parser.add_argument("--prompt-file", default="", help="Path to requirement / prompt file.")
    parser.add_argument("--agent", default=DEFAULT_AGENT, help="Interactions API agent name.")
    parser.add_argument("--environment-id", default="", help="Optional reusable environment_id (7-day TTL).")
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL, help="AIStudio git repo URL.")
    parser.add_argument("--drive-folder-id", default=DEFAULT_DRIVE_FOLDER, help="Target Google Drive folder ID.")
    parser.add_argument("--feishu-webhook", default=os.environ.get("FEISHU_WEBHOOK_URL", ""), help="Feishu bot webhook URL.")
    parser.add_argument("--status", default="", help="Query status of an existing interaction ID.")
    parser.add_argument("--dry-run", action="store_true", help="Print request payload without sending.")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if args.status:
        if not api_key:
            print("Error: GEMINI_API_KEY environment variable is required.", file=sys.stderr)
            return 1
        res = http_json(f"{DEFAULT_API_BASE}/{args.status}", "GET", api_key)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    prompt_text = args.prompt.strip()
    if args.prompt_file:
        prompt_text = Path(args.prompt_file).read_text(encoding="utf-8").strip()
    if not prompt_text:
        print("Error: Provide --prompt or --prompt-file.", file=sys.stderr)
        return 1

    instruction = build_agent_instruction(
        title=args.title,
        prompt_text=prompt_text,
        repo_url=args.repo_url,
        drive_folder_id=args.drive_folder_id,
        feishu_webhook=args.feishu_webhook,
    )

    payload: dict = {
        "agent": args.agent,
        "input": instruction,
        "environment": "remote",
        "background": True,
    }
    if args.environment_id:
        payload["environment_id"] = args.environment_id

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is required.", file=sys.stderr)
        return 1

    res = http_json(DEFAULT_API_BASE, "POST", api_key, payload)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
