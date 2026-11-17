#!/usr/bin/env python3
"""
Feishu Custom Bot Webhook Notifier.

Sends an interactive card to a Feishu group bot webhook with task status,
summary, and clickable Google Drive deliverable link.

Usage:
  python3 scripts/feishu_notify.py \
      --webhook "https://open.feishu.cn/open-apis/bot/v2/hook/..." \
      --title "白板科普：AI Agent 架构" \
      --status success \
      --drive-url "https://drive.google.com/drive/folders/..." \
      --summary "已完成 AG_SOP_03 渲染与混音，共交付 1 条 1080p 成片"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def build_card(title: str, status: str, summary: str, drive_url: str, interaction_id: str) -> dict:
    is_ok = status.lower() in ("success", "ok", "done")
    header_color = "green" if is_ok else "red"
    status_badge = "✅ 生产完成" if is_ok else "❌ 执行异常"

    elements = [
        {
            "tag": "markdown",
            "content": f"**状态**：{status_badge}\n**摘要**：{summary or '无附加说明'}",
        }
    ]
    if interaction_id:
        elements.append({"tag": "markdown", "content": f"**任务 ID**：`{interaction_id}`"})

    if drive_url:
        elements.append(
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "打开 Google Drive 产物"},
                        "type": "primary",
                        "url": drive_url,
                    }
                ],
            }
        )

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"YOUAI 云端工场 · {title}"},
                "template": header_color,
            },
            "elements": elements,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Send Feishu webhook notification.")
    parser.add_argument("--webhook", default=os.environ.get("FEISHU_WEBHOOK_URL", ""), help="Feishu webhook URL.")
    parser.add_argument("--title", default="内容生产任务", help="Card title.")
    parser.add_argument("--status", default="success", choices=["success", "error"], help="Task status.")
    parser.add_argument("--summary", default="", help="Brief result or error summary.")
    parser.add_argument("--drive-url", default="", help="Google Drive deliverable URL.")
    parser.add_argument("--interaction-id", default="", help="Gemini Interactions API interaction ID.")
    args = parser.parse_args()

    if not args.webhook:
        print("Error: Provide --webhook or set FEISHU_WEBHOOK_URL.", file=sys.stderr)
        return 1

    payload = build_card(args.title, args.status, args.summary, args.drive_url, args.interaction_id)
    req = urllib.request.Request(
        args.webhook,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            print(body)
            return 0
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
