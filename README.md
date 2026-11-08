# 🏭 YOUAI Cloud Video Factory (`AIStudio` v3.0)

**Antigravity 云端视频工场 · 六大主力产线与三层持久化执行底座**

## 1. 快速唤醒底座（每个新会话第 0 步）

```bash
/home/antigravity/qihao1226/AIStudio/scripts/bootstrap.sh
export PATH="/home/antigravity/.local/bin:/shared/user/.gemini/youai/bin:$PATH"
```

## 2. 六大 SOP v3.0 极致执行手册索引 (`docs/sops/`)

- **全局顶层蓝图**：[`docs/sops/00_顶层规划_v3.0.md`](docs/sops/00_顶层规划_v3.0.md)
- **全景技术协议**：[`docs/sops/01_全景技术架构_v3.0.md`](docs/sops/01_全景技术架构_v3.0.md)
- **`AG_SOP_01` 商业深度纪实视频线**：[`docs/sops/AG_SOP_01_v3.0.md`](docs/sops/AG_SOP_01_v3.0.md)
- **`AG_SOP_02` 极速快闪大字动效线**：[`docs/sops/AG_SOP_02_v3.0.md`](docs/sops/AG_SOP_02_v3.0.md)
- **`AG_SOP_03` 白板手绘与火柴人讲解线**：[`docs/sops/AG_SOP_03_v3.0.md`](docs/sops/AG_SOP_03_v3.0.md)
- **`AG_SOP_04` 全源素材重构与外挂多模态车间**：[`docs/sops/AG_SOP_04_v3.0.md`](docs/sops/AG_SOP_04_v3.0.md)
- **`AG_SOP_05` 工业口播伴侣动效线**：[`docs/sops/AG_SOP_05_v3.0.md`](docs/sops/AG_SOP_05_v3.0.md)
- **`AG_SOP_06` 极客架构与概念演示线**：[`docs/sops/AG_SOP_06_v3.0.md`](docs/sops/AG_SOP_06_v3.0.md)

## 3. 核心工业 CLI 工具集 (`bin/`)

已同步持久化至 `/shared/user/.gemini/youai/bin/` 与 `/home/antigravity/.local/bin/`：
- **4层装配流水线**：`to_timeline` (`to_timeline.py`), `edl2film` (`edl2film.py`), `openfilm`
- **多模态算力调度**：`colab` (内置 [`http_rpc.py`](scripts/patches/colab-cli/http_rpc.py) 纯 HTTPS 内核桥接), [`scripts/sop04_colab_orchestrator.py`](scripts/sop04_colab_orchestrator.py), [`scripts/colab_multimodal_worker.py`](scripts/colab_multimodal_worker.py)
- **母带混音与门禁守门员**：`audio_bgm_mixer`, `film_gatekeeper`, `wallstreet-strip`, `motion_check`, `search_styles`, `beat_detector`, `wb`, `pen_motion`, `motionkit`, `face_occlusion_check`, `jacky-validate`, `cognitive_load_linter`
