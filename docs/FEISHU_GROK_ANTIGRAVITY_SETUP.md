# 飞书 → Grok Bot → Antigravity (Interactions API) → Colab → Google Drive 配置指南

> **适用场景**：国内无需 VPN，通过飞书**私聊**向 Hermes / Grok 发送「需求单 + Prompt」，经墙外 Grok Bot 触发 Google Gemini Interactions API 中的托管 Antigravity Agent，由其调度 Colab GPU 完成生产、上传 Google Drive，并由 Hermes / Grok 轮询结果后通过**现有飞书私聊通道**回传给你。

---

## 1. 仓库内已就绪的组件

- [`scripts/grok_trigger_antigravity.py`](../scripts/grok_trigger_antigravity.py)：运行在 **Grok Bot 云电脑**（或墙外转发节点），负责把飞书需求单与 Prompt 转发给 `POST https://generativelanguage.googleapis.com/v1beta/interactions`（`antigravity-preview-09-2026`，`background=true`），并支持 `--status <id>` 轮询状态与结果。
- [`scripts/interactions_bootstrap.sh`](../scripts/interactions_bootstrap.sh)：运行在 **Interactions API 沙箱**内，自动安装 `google-colab-cli`、注入 Pure-HTTP RPC 补丁，并恢复 Colab 与 Drive 凭据。
- [`scripts/gdrive_sa_upload.py`](../scripts/gdrive_sa_upload.py)：通过 **Google Service Account** 将产物递归上传到指定 Google Drive 文件夹（不依赖网页版 `gdrive` 插件）。
- [`scripts/feishu_notify.py`](../scripts/feishu_notify.py)：可选组件（仅当未来需要额外推送到飞书群时使用）。

---

## 2. 上线前只需补齐的 2 个配置（一次性，无需建飞书群）

### ① 创建 Google Service Account 并共享 Drive 目录（替代主账号 Cookie）
1. 在 Google Cloud Console 创建一个 Service Account（开启 **Google Drive API**），下载 JSON 密钥文件（建议由本机 Hermes 协助操作）。
2. 在你的 Google Drive 中打开目标产出目录（例如 `1bnZ8YCeAtaS8F1VkcIjHK3PXS9P4FaUw`），点**共享**，把该 Service Account 的邮箱（`xxx@xxx.iam.gserviceaccount.com`）设为**编辑者（Editor）**。
3. 将 JSON 密钥做 Base64 编码，记为 `GDRIVE_SA_JSON_B64`。

### ② 在 Grok Bot 云电脑配置环境变量与触发命令
在 Grok Bot 中配置以下环境变量（**注意：不要把 Google 主账号 Cookie 或 SA 私钥走明文 webhook 下发**）：
- `GEMINI_API_KEY`：本机 `YOUAI自动化系统/MCP_Config/.env` 中已验证有效的 Key
- `GDRIVE_ROOT_FOLDER_ID`：目标 Drive 文件夹 ID（默认 `1bnZ8YCeAtaS8F1VkcIjHK3PXS9P4FaUw`）

Grok Bot 收到飞书私聊指令后，执行：
```bash
python3 scripts/grok_trigger_antigravity.py \
  --title "<任务标题>" \
  --prompt "<飞书发来的需求单和Prompt>"
```
任务在后台跑完后，Grok / Hermes 通过 `--status <interaction_id>` 获取沙箱输出的结构化 `STATUS` / `DRIVE_URL` / `SUMMARY`，直接通过**现有飞书私聊通道**回传给你。

> **提示**：Colab 凭据（`colab-cli/token.json`）与 Service Account（`GDRIVE_SA_JSON_B64`）建议配置在 Interactions API 沙箱的 Credentials / Egress Proxy 或受控环境初始化中，避免经过第三方共享环境。

---

## 3. 快速验收测试

1. **本地/Grok 报文演练（不消耗额度）**：
   ```bash
   python3 scripts/grok_trigger_antigravity.py --dry-run --title "测试任务" --prompt "测试需求单"
   ```
2. **飞书回执通道测试**：
   ```bash
   python3 scripts/feishu_notify.py --webhook "$FEISHU_WEBHOOK_URL" --title "通道测试" --status success --summary "飞书回执测试成功"
   ```
3. **Grok 实测触发 Interactions API**：
   ```bash
   GEMINI_API_KEY="你的Key" python3 scripts/grok_trigger_antigravity.py --title "冒烟测试" --prompt "检查环境并回复测试完成"
   ```
