# 飞书 → Grok Bot → Antigravity (Interactions API) → Colab → Google Drive 配置指南

> **适用场景**：国内无需 VPN，通过飞书**私聊**向 Hermes / Grok 发送「需求单 + Prompt」，经墙外 Grok Bot 触发 Google Gemini Interactions API 中的托管 Antigravity Agent，由其调度 Colab GPU 完成生产、上传 Google Drive，并由 Hermes / Grok 轮询结果后通过**现有飞书私聊通道**回传给你。

---

## 1. 仓库内已就绪的组件

- [`scripts/grok_trigger_antigravity.py`](../scripts/grok_trigger_antigravity.py)：运行在 **Grok Bot 云电脑**（或墙外转发节点），负责把飞书需求单与 Prompt 转发给 `POST https://generativelanguage.googleapis.com/v1beta/interactions`（`antigravity-preview-09-2026`，`background=true`），并支持 `--status <id>` 轮询状态与结果。
- [`scripts/interactions_bootstrap.sh`](../scripts/interactions_bootstrap.sh)：运行在 **Interactions API 沙箱**内，自动安装 `google-colab-cli`、注入 Pure-HTTP RPC 补丁，并恢复 Colab 与 Drive 凭据。
- [`scripts/gdrive_oauth_login.py`](../scripts/gdrive_oauth_login.py)：本机一次性运行，用 OAuth 桌面客户端换取 **`drive.file` 最小权限**的 refresh token，写入 `~/.config/youai/gdrive_oauth.json`（600）。
- [`scripts/gdrive_sa_upload.py`](../scripts/gdrive_sa_upload.py)：把产物递归上传到 Google Drive。**默认走 OAuth（`drive.file`）**，Service Account 仅保留给 Workspace 共享云端硬盘。
- [`scripts/feishu_notify.py`](../scripts/feishu_notify.py)：可选组件（仅当未来需要额外推送到飞书群时使用）。

---

## 2. 上线前只需补齐的 2 个配置（一次性，无需建飞书群）

### ① Google Drive 写入凭据：OAuth refresh token（`drive.file`）

**不要用 Service Account 写个人账号的「我的云端硬盘」。** Service Account 本身没有存储配额，向 My Drive 上传会直接失败：

```
403 storageQuotaExceeded: Service Accounts do not have storage quota.
Leverage shared drives, or use OAuth delegation.
```

共享云端硬盘（Shared Drive）和域委派（Domain-wide delegation）都只有 **Google Workspace** 才有；个人 Gmail 账号两条路都不存在。因此本管线的写入凭据改用**用户 OAuth + `drive.file`**：应用只能碰它自己创建的文件，读不到你 Drive 里的其它内容。

步骤：

1. 在 Google Cloud Console 建一个 **桌面应用**类型的 OAuth 客户端：
   `https://console.cloud.google.com/apis/credentials` → 创建凭据 → OAuth 客户端 ID → 应用类型「桌面应用」。
   首次会要求先配 OAuth 同意屏幕：受众选「外部」，测试用户填自己的账号即可（`drive.file` 不是敏感 scope，无需 Google 审核）。
2. 本机一次性换取 refresh token：

   ```bash
   export GDRIVE_OAUTH_CLIENT_ID="xxxx.apps.googleusercontent.com"
   export GDRIVE_OAUTH_CLIENT_SECRET="GOCSPX-xxxx"
   python3 scripts/gdrive_oauth_login.py          # 默认 scope = drive.file
   ```

   浏览器同意后写入 `~/.config/youai/gdrive_oauth.json`（600）。

### ② 在 Grok Bot 云电脑配置环境变量与触发命令

在 Grok Bot 中配置以下环境变量（**长期凭据不进沙箱**）：
- `GEMINI_API_KEY`：本机 `YOUAI自动化系统/MCP_Config/.env` 中已验证有效的 Key
- `GDRIVE_ROOT_FOLDER_ID`：目标 Drive 文件夹 ID；留空则上传到 My Drive 根目录。实测 `drive.file` 可直接向既有文件夹写入；若某个父文件夹不可写，脚本自动回落到应用自建的 `YOUAI产出`（`GDRIVE_FALLBACK_FOLDER` 可改名）

沙箱侧的 Drive 凭据，三种注入方式按安全度排序：

| 方式 | 变量 | 说明 |
|---|---|---|
| **短时令牌（推荐）** | `GDRIVE_ACCESS_TOKEN` | 本机现取一个 1 小时有效的 access token 随任务下发，**refresh token 永不出本机** |
| 整份 refresh token | `GDRIVE_OAUTH_JSON_B64` | `base64 -i ~/.config/youai/gdrive_oauth.json \| tr -d '\n'`，权限仍限于 `drive.file` |
| 明文 JSON | `GDRIVE_OAUTH_JSON` | 仅调试用 |

Grok Bot 收到飞书私聊指令后，执行：
```bash
python3 scripts/grok_trigger_antigravity.py \
  --title "<任务标题>" \
  --prompt "<飞书发来的需求单和Prompt>"
```
任务在后台跑完后，Grok / Hermes 通过 `--status <interaction_id>` 获取沙箱输出的结构化 `STATUS` / `DRIVE_URL` / `SUMMARY`，直接通过**现有飞书私聊通道**回传给你。

> **提示**：Colab 凭据（`colab-cli/token.json`）建议配置在 Interactions API 沙箱的 Credentials / Egress Proxy 或受控环境初始化中，避免经过第三方共享环境。

---

## 3. 快速验收测试

1. **本地/Grok 报文演练（不消耗额度）**：
   ```bash
   python3 scripts/grok_trigger_antigravity.py --dry-run --title "测试任务" --prompt "测试需求单"
   ```
2. **Drive 写入回归（真实上传一个小文件）**：
   ```bash
   echo "upload smoke test" > /tmp/smoke.txt
   python3 scripts/gdrive_sa_upload.py --source /tmp/smoke.txt --folder-id root
   ```
   输出 `DRIVE_URL=...` 即为通过。
3. **飞书回执通道测试**：
   ```bash
   python3 scripts/feishu_notify.py --webhook "$FEISHU_WEBHOOK_URL" --title "通道测试" --status success --summary "飞书回执测试成功"
   ```
4. **Grok 实测触发 Interactions API**：
   ```bash
   GEMINI_API_KEY="你的Key" python3 scripts/grok_trigger_antigravity.py --title "冒烟测试" --prompt "检查环境并回复测试完成"
   ```

---

## 4. 已知坑

| 现象 | 根因 | 处理 |
|---|---|---|
| `403 storageQuotaExceeded` | Service Account 无存储配额，只能写 Workspace 共享云端硬盘 | 改用 OAuth（见 §2①） |
| 上传到文件夹返回 `404 File not found` | `drive.file` 只覆盖「本应用创建的文件」，个别父文件夹不可写 | 脚本已自动回落到应用自建目录（默认 `YOUAI产出`，`GDRIVE_FALLBACK_FOLDER` 可改）。实测向既有文件夹 `1bnZ8YCe...` 写入正常，这条仅作兜底 |
| `CERTIFICATE_VERIFY_FAILED`（macOS 框架版 Python） | 框架版 Python 不自带根证书，`urllib` 直连 Google 失败 | `export SSL_CERT_FILE=~/Library/Python/3.13/lib/python/site-packages/certifi/cacert.pem` |
| 沙箱里 `httplib2` 连不上 Google | 沙箱出网走 `HTTPS_PROXY`，`httplib2` 需要 `pysocks` 才能过代理 | 上传前 `pip install google-api-python-client google-auth pysocks` |
| `invalid_grant` 刷新失败 | refresh token 被撤销 / 过期，或换了 OAuth 客户端 | 重跑 `scripts/gdrive_oauth_login.py` |
