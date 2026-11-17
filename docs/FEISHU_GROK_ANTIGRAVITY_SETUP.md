# 飞书 → Grok Bot → Antigravity (Interactions API) → Colab → Google Drive 配置指南

> **适用场景**：国内无需 VPN，通过飞书发送「需求单 + Prompt」，经墙外 Grok Bot 触发 Google Gemini Interactions API 中的托管 Antigravity Agent，由其调度 Colab GPU 完成生产、上传 Google Drive，并直接通过飞书机器人 Webhook 回传结果卡片。

---

## 1. 仓库内已就绪的组件

- [`scripts/grok_trigger_antigravity.py`](../scripts/grok_trigger_antigravity.py)：部署/运行在 **Grok Bot 云电脑**，负责把飞书需求单与 Prompt 转发给 `POST https://generativelanguage.googleapis.com/v1beta/interactions`（`antigravity-preview-09-2026`，`background=true`）。
- [`scripts/interactions_bootstrap.sh`](../scripts/interactions_bootstrap.sh)：运行在 **Interactions API 沙箱**内，自动安装 `google-colab-cli`、注入 Pure-HTTP RPC 补丁，并恢复 Colab 与 Drive 凭据。
- [`scripts/gdrive_sa_upload.py`](../scripts/gdrive_sa_upload.py)：通过 **Google Service Account** 将产物递归上传到指定 Google Drive 文件夹（不依赖网页版 `gdrive` 插件）。
- [`scripts/feishu_notify.py`](../scripts/feishu_notify.py)：生产完成或异常时，向飞书群自定义机器人 Webhook 发送带 Drive 链接的交互卡片。

---

## 2. 上线前只需补齐的 3 个配置（一次性）

### ① 创建 Google Service Account 并共享 Drive 目录（替代主账号 Cookie）
1. 在 Google Cloud Console 创建一个 Service Account（开启 **Google Drive API**），下载 JSON 密钥文件。
2. 在你的 Google Drive 中打开目标产出目录（例如 `1bnZ8YCeAtaS8F1VkcIjHK3PXS9P4FaUw`），点**共享**，把该 Service Account 的邮箱（`xxx@xxx.iam.gserviceaccount.com`）设为**编辑者（Editor）**。
3. 将 JSON 密钥做 Base64 编码，记为 `GDRIVE_SA_JSON_B64`。

### ② 获取飞书群自定义机器人 Webhook
1. 在飞书目标群 → **群设置 → 群机器人 → 添加自定义机器人**。
2. 复制 Webhook 地址（`https://open.feishu.cn/open-apis/bot/v2/hook/...`），记为 `FEISHU_WEBHOOK_URL`。

### ③ 在 Grok Bot 云电脑配置环境变量与触发命令
在 Grok Bot 中配置以下环境变量（**注意：不要把 Google 主账号 Cookie 放进 Grok**）：
- `GEMINI_API_KEY`：设好月度预算上限的 Gemini API Key
- `FEISHU_WEBHOOK_URL`：上一步获取的飞书 Webhook
- `GDRIVE_ROOT_FOLDER_ID`：目标 Drive 文件夹 ID（默认 `1bnZ8YCeAtaS8F1VkcIjHK3PXS9P4FaUw`）

Grok Bot 收到飞书指令后，只需执行：
```bash
python3 scripts/grok_trigger_antigravity.py \
  --title "<任务标题>" \
  --prompt "<飞书发来的需求单和Prompt>"
```

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
