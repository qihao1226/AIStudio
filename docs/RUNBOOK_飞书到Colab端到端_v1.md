# RUNBOOK · 飞书需求单 → Antigravity 沙箱 → Colab GPU → Google Drive → 飞书回执

> **版本**：v1（首次实测通过）｜**实测日期**：2026-11-17
> **状态**：链路已跑通并外部核验；**未验证**真实 SOP-04 模型推理（见 §7）
> **配套**：配置步骤见 [`FEISHU_GROK_ANTIGRAVITY_SETUP.md`](FEISHU_GROK_ANTIGRAVITY_SETUP.md)；本文只讲「怎么跑一次、怎么判真假、收尾怎么做」

---

## 1. 一次完整链路由谁做什么

```
夜风（飞书私聊，发需求单）
  └─ Hermes-1（本机）
       ├─ 把需求单编译成沙箱可执行指令（触发脚本）
       ├─ 铸 1h 短时凭据并注入（Drive + Colab）
       ├─ 轮询 --status 取结构化回执
       └─ 外部核验产物（不信沙箱自报）→ 飞书回执
            └─ Gemini Interactions API（境外，CPU 沙箱）
                 ├─ git clone AIStudio + interactions_bootstrap.sh
                 ├─ colab new --gpu T4  ← 真正调 Colab 的是沙箱，不是本机
                 ├─ 上传 worker → exec → download 产物
                 ├─ gdrive_sa_upload.py 上传产物
                 └─ 输出 STATUS / DRIVE_URL / SUMMARY
```

**关键认知**：本机只负责「编译 + 递钥匙 + 记账 + 核验」，GPU 计算与 Drive 写入都发生在境外。
回执里不要写成「本机渲染」，否则下次排障会找错地方。

---

## 2. 前置：三份凭据，全部短时化

| 凭据 | 从哪来 | 有效期 | 注入方式 |
|---|---|---|---|
| `GEMINI_API_KEY` | `YOUAI自动化系统/MCP_Config/.env` | 长期 | 触发脚本读环境变量 |
| Drive 写入 | `~/.config/youai/gdrive_oauth.json`（`drive.file` refresh token） | refresh 长期、**下发 access 1h** | `GDRIVE_ACCESS_TOKEN` |
| Colab | 本机钥匙串 `google-colab-cli / oauth_token` | refresh 长期、**下发 access 1h** | `COLAB_TOKEN_JSON`（bootstrap 落成 `~/.config/colab-cli/token.json`） |

**红线**：不要把 refresh token 下发到沙箱。两枚 access token 都用本机现铸：

```bash
# Drive（drive.file）
python3 - <<'PY'
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json, os
d = json.load(open(os.path.expanduser("~/.config/youai/gdrive_oauth.json")))
c = Credentials(token=None, refresh_token=d["refresh_token"], token_uri=d["token_uri"],
                client_id=d["client_id"], client_secret=d["client_secret"], scopes=d["scopes"])
c.refresh(Request()); open("/tmp/df_access_token.txt", "w").write(c.token)
PY

# Colab（从钥匙串换 1h，写成不含 refresh_token 的 token.json）
PY=$(ls ~/.local/share/uv/tools/google-colab-cli/bin/python* | head -1)
"$PY" -c "
import json, keyring
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
d = json.loads(keyring.get_password('google-colab-cli','oauth_token'))
c = Credentials(token=None, refresh_token=d['refresh_token'], token_uri=d['token_uri'],
                client_id=d['client_id'], client_secret=d['client_secret'], scopes=d['scopes'])
c.refresh(Request())
json.dump({'token': c.token, 'refresh_token': '', 'token_uri': d['token_uri'],
           'client_id': d['client_id'], 'client_secret': d['client_secret'],
           'scopes': d['scopes'], 'expiry': c.expiry.isoformat()+'Z'},
          open('$HOME/.config/colab-cli/token.json','w'))
"
```

---

## 3. 沙箱必须做的事（写进 prompt，别指望它自己知道）

1. `git clone --depth 1 https://github.com/qihao1226/AIStudio.git && cd AIStudio`
2. 导出 `COLAB_TOKEN_JSON` / `GDRIVE_ACCESS_TOKEN` 后 `bash scripts/interactions_bootstrap.sh`
   —— bootstrap 负责装 `colab-cli`、打 Pure-HTTP RPC 补丁、把 token 落到 `~/.config/colab-cli/token.json`
   —— 沙箱若因 externally-managed-environment 装不上，退到 `python3 -m pip install --user --break-system-packages google-colab-cli google-api-python-client google-auth pysocks`
3. `export PATH="$HOME/.local/bin:$PATH"`
4. `colab new -s <name> --gpu T4`
5. `colab upload -s <name> worker.py /content/worker.py`
6. `colab exec -s <name> -f worker.py --timeout 600`
7. `colab download -s <name> /content/<产物> ./<产物>`
8. `GDRIVE_ACCESS_TOKEN=... python3 scripts/gdrive_sa_upload.py --source ./<产物> --folder-id <目标目录>`
9. `colab stop -s <name>`
10. 最终回复必须含 `STATUS` / `DRIVE_URL` / `SUMMARY` + worker 的原始 JSON 输出 + 上传脚本输出

---

## 4. 验收标准（不信自报）

沙箱回 `STATUS: success` **不等于**跑通。必须外部核验：

| 核验项 | 做法 | 通过标准 |
|---|---|---|
| 文件真的在 | `GET /drive/v3/files/<id>?fields=name,size,parents` | parent 是目标文件夹、size > 0、属主是自己的账号 |
| 内容不是坏的 | 下载回本机，看分辨率与画面 | 尺寸符合要求、画面不是空白/花屏 |
| GPU 真的用了 | 看 worker 输出的 `device` / `torch.cuda.is_available()` | 出现 `Tesla T4` 等真实型号 |
| 会话真的关了 | `colab sessions` + `colab usage` | `No active sessions` / `Active assignments: 0` |

---

## 5. 成本口径（2026-11-17 实测）

| 项 | 数值 |
|---|---|
| Interactions API | 单次端到端 ≈ **11.6 万 token**（含 bootstrap、会话、上传全过程；沙箱系统提示占大头） |
| Colab 算力 | 一个 T4 会话约 **3 分钟**；结束后余额 581.67 units，`Active assignments: 0` |
| 本机代价 | 0 GPU；只有网络与少量 CPU |

> 空转会话按小时烧算力单位，**忘停比跑错更贵**。

---

## 6. 已知坑（都踩过）

| 现象 | 根因 | 处理 |
|---|---|---|
| 沙箱里 `colab exec` 报 `WebSocketConnectionClosedException` | 代理拦截 WS 升级 | bootstrap 的 Pure-HTTP RPC 补丁；本机直跑也要先打补丁 |
| 沙箱 pip 装不上 colab-cli | externally-managed-environment | 加 `--user --break-system-packages` |
| `gdrive_sa_upload.py` 报 `No Service Account credentials found` | GitHub 上是旧版脚本 / 没注入 OAuth | 先确认沙箱 clone 到的是最新 main，再确认注入了 `GDRIVE_ACCESS_TOKEN` |
| `colab status` 打印 URL 后立刻 `Aborted.` | 非交互 stdin 读到 EOF | pty 后台跑，验证码用 `process_manage submit` 送回 |
| 沙箱 `httplib2` 连不上 Google | 走 `HTTPS_PROXY` 需 `pysocks` | bootstrap 已含 pysocks |

---

## 7. 尚未验证 / 下一步

- **真实模型推理未跑**：本次只验证链路，worker 是 GPU 渲染的 Mandelbrot 海报（`Tesla T4 / torch 2.14.1+cu130 / 1080×1920`）。
  SOP-04 的 FLUX / Z-Image / MiniMax-H3 需要 GB 级模型下载与十几分钟 GPU，属于**下一次内容侧验收**。
- **Grok 跳当前未启用**：设计图里是「飞书 → Grok Bot 云电脑 → Antigravity」，因本机可直连 `generativelanguage.googleapis.com`，当前由 Hermes-1 直接触发。
  少一跳 = 少一个故障点、少一个 key 过第三方 webhook 的泄露面；如需严格按原图执行，把触发端换成 Grok 即可，脚本本身无需改。
- **无人值守未做**：现在每次都要人工发起 + 注入短时 token（1h 上限决定不能长期挂）。

---

## 8. 2026-11-17 首次实测记录

| 项 | 值 |
|---|---|
| interaction id | `v1_ChdsUV84YXBEc0t1cUh6N0lQaW9YcXFBSRIXbFFfOGFwRHNLdXFIejdJUGlvWHFxQUk` |
| 耗时 | 16:25:57 发起 → 16:28:45 completed（约 2 分 48 秒） |
| 沙箱环境 | Linux x86_64 (gvisor) / Python 3.12.3 / Node 22.23.5 |
| GPU | Tesla T4，`torch 2.14.1+cu130`，`cuda_available True` |
| 产物 | `youai_e2e_poster.png` 1080×1920，257,790 bytes |
| Drive | 落位 `1bnZ8YCeAtaS8F1VkcIjHK3PXS9P4FaUw`，属主 `qihao888@gmail.com` |
| 会话 | 沙箱侧 `youai-e2e` 已 stop；本机探针 `youai-probe` 已 stop；`Active assignments: 0` |
