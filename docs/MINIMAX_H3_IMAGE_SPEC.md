# MiniMax H3-Image 4K 原生画质与多图参考工业集成技术规范 (v3.5)

> **集成日期**：2026-11-11  
> **模型来源**：MiniMax 官方开源权重 (`MiniMax-AI/MiniMax-H3-Image` / `Comfy-Org/MiniMax-H3-Image`)  
> **归档位置**：[`docs/MINIMAX_H3_IMAGE_SPEC.md`](file:///home/antigravity/qihao1226/AIStudio/docs/MINIMAX_H3_IMAGE_SPEC.md)

---

## 一、技术全景与架构参数

MiniMax H3-Image 是 MiniMax-H3 家族专为高精度静帧视觉与图像编辑研发的开源旗舰生图模型：

| 架构参数 | 技术指标与配置标准 |
| :--- | :--- |
| **基础骨干网络 (DiT)** | 33.1B 单流扩散 Transformer（50 层、隐藏维度 5376、56 头注意力、3D MM-RoPE） |
| **文本编码器 (Shared Text Encoder)** | `Qwen3-VL-32B`（提取第 50 层隐藏状态），**与 MiniMax-H3 视频模型 100% 共享** |
| **图像自编码器 (Image VAE)** | 专用 24 通道 Image VAE（卷积编码器 + 24 层 ViT 解码器），下采样率 16x，2x2 Patch |
| **采样算法与步数** | 固定 6 步蒸馏流匹配（6 NFE，无 CFG，无需调节负面提示词） |
| **原生输出分辨率** | **原生 4K (4096×4096 / 3840×2160，约 16MP 直出，无需超分网络)**，支持 16:9 / 9:16 / 1:1 / 21:9 等宽高比 |
| **参考图能力 (Multi-Reference)** | **单 Checkpoint 原生支持 1～16 张参考图输入**，文本与全部参考图统一拼接计算全注意力 |
| **推理延迟 (A100 SXM4)** | 10～25 秒完成 4K 16MP 母带图像直出 |

---

## 二、三层资产复用与 5TB Google Drive 模型金库

为避免在不同 Colab 会话中重复下载百 GB 级权重，我们依托 5TB Google Drive 模型金库实现了**跨模型权重复用**与**零闲置存储**：

```text
/content/drive/MyDrive/AIStudio_Models/
├── MiniMax-H3/                       # 视频生成金库
│   └── text_encoders/
│       └── qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors  (14.6 GiB, H3-Image 与 H3-Video 完全复用！)
│
└── MiniMax-H3-Image/                 # 4K 生图专属金库
    ├── diffusion_models/
    │   └── minimax_h3_image_pruned_w4a8.safetensors       (约 20 GiB, 或 INT8-ConvRot)
    └── vae/
        └── minimax_h3_image_vae.safetensors               (约 2.6 GiB)
```

> **冷启动优势**：会话拉起后，Worker 自动检查 Google Drive 挂载，直接通过软链接（`symlink`）注入 ComfyUI 目录，模型装载由 3.5 分钟缩短至 **~14 秒**。

---

## 三、双层调度 CLI 与工具链矩阵

### 1. 专用原生 CLI：`minimax_h3_image_colab`
位于 [`/home/antigravity/qihao1226/AIStudio/bin/minimax_h3_image_colab`](file:///home/antigravity/qihao1226/AIStudio/bin/minimax_h3_image_colab)，面向 4K 超清大图与 1~16 张参考图的高阶编辑。

```bash
# 场景 1：原生 4K 商业特写 / B-Roll 渲染
minimax_h3_image_colab \
  --prompt "Hyper-realistic commercial photography of a high-tech robotic laboratory at sunrise, volumetric light rays, Leica 50mm f/1.4" \
  --resolution 4k \
  --aspect 16:9 \
  --gpu A100 \
  --session youai-h3-a100 \
  --output /path/to/shot_4k.png \
  --stop-after

# 场景 2：1~16 张多图参考一致性编辑（角色/资产换装与姿态演化）
minimax_h3_image_colab \
  --prompt "Preserve Subject 1's facial structure and attire, standing in an ultra-modern glass auditorium giving a keynote presentation" \
  --image /path/to/character_front.png \
  --image /path/to/character_side.png \
  --resolution 4k \
  --aspect 16:9 \
  --gpu A100 \
  --session youai-h3-a100 \
  --output /path/to/keynote_4k.png \
  --stop-after
```

### 2. 统一生图 CLI：`colab_image_gen`
位于 [`/home/antigravity/qihao1226/AIStudio/bin/colab_image_gen`](file:///home/antigravity/qihao1226/AIStudio/bin/colab_image_gen)，已平滑接入 `--model minimax-h3-image`，兼容现有工业脚本与编排管线。

```bash
# 统一 CLI 直接选择 H3-Image 4K 引擎
colab_image_gen \
  --model minimax-h3-image \
  --prompt "科技感商业海报，中央写着醒目的金色中文大字：『云端视频工厂』" \
  --resolution 4k \
  --aspect 16:9 \
  --output /path/to/poster_4k.png
```

---

## 四、与工厂 SOP 的深度协同与业务边界

| 业务场景 | 推荐引擎 | 核心原因与产出标准 |
| :--- | :--- | :--- |
| **日常 B-Roll / 分镜空镜 / 快速文字海报** | `Z-Image-Turbo` (6B) | 2.5 秒极速生成、单图成本忽略不计、L4 显存极充沛，满足 1080p 工业批量装配 |
| **原生 4K 封面 / 工业机械 CAD 剖析图** | `MiniMax H3-Image` (33B) | 16MP 原生分辨率直出无超分伪影，物理真实感与微观材质纹理极高 |
| **多镜头角色/道具强一致性延续** | `MiniMax H3-Image` (33B) | 原生支持 1~16 张参考图联合 Prompt，无需训练 LoRA 即可锁定角色特征 |
| **MiniMax-H3 视频首帧生成 (Image -> Video)** | `MiniMax H3-Image` (33B) | 与 `minimax_h3_colab` 视频模型共用 `Qwen3-VL` 文本隐空间，杜绝视频首帧形变 |

---

## 五、持久化与自动化运维保障

1. **Persistent Bootstrap**：`youai-bootstrap` 自动将 `minimax_h3_image_colab` 同步至 `/shared/user/.gemini/youai/bin/` 与 `/home/antigravity/.local/bin/`。
2. **Pure-HTTP RPC 调度**：基于 `http_rpc.py` 绕过 WebSocket 限制，全自动处理异步日志轮询与成果下载。
3. **计费熔断机制**：`--stop-after` 开关确保单次任务执行后即刻销毁 Colab 虚拟机，绝不产生闲置计算单元（CU）损耗。
