# YOUAI 云端视频工厂 v3.5 · 全栈灾备固化、5TB 模型金库构建与六大 SOP 能力上限实操测试总任务单

> **文档定位**：本文件为跨会话最高执行纲领（Master Task Order）。新开启的 Antigravity 会话（如 Gemini Flash / Pro）读取本文件后，须严格按照本任务单的阶段顺序、技术红线、CLI 工具链与验收门禁，依次完成 **阶段一（全栈三端灾备校验）**、**阶段二（5TB Google Drive Colab 模型金库预热固化）** 与 **阶段三（SOP 01 ~ SOP 06 六轮能力上限实操压测与交片）**。
> **本地 GitHub 路径**：`/home/antigravity/qihao1226/AIStudio/docs/YOUAI_v3.5_Master_Task_Order.md`
> **Google Drive 内容生产根目录 ID**：`1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc`
> **Google Drive 云端系统配置根目录 ID**：`1YJqjW_FDdyY0iZsFeOSr1x_RK-F1_FFd`

---

## 〇、新会话开机必跑第一指令（Step 0：1 秒环境恢复）

任何新会话启动后的**第一个动作**，必须无条件执行以下恢复脚本，将 24 款 CLI 工具、37 个核心 Skills、中文字体池与 `google-colab-cli` 纯 HTTPS RPC 补丁完整挂载到当前临时虚拟机：

```bash
/home/antigravity/qihao1226/AIStudio/scripts/bootstrap.sh
export PATH="/home/antigravity/.local/bin:/shared/user/.gemini/youai/bin:$PATH"
colab status
```

同时调用 `lookup_skill` 查阅以下三大已注册系统技能：
1. `youai-video-factory`（6 大 SOP 总控与 4 层 OpenFilm 编译协议）
2. `minimax-h3-colab`（Colab A100 + `MiniMax-H3` 音画同出 + 32kHz 立体声 + 中英口型对白视频生成）
3. `colab-multimodal-suite`（Colab L4 + `Z-Image-Turbo` 1080p 中英海报/写实生图 + `Kokoro-82M` 演播室配音 + `F5-TTS` 5 秒零样本克隆 + `Faster-Whisper-Turbo` 毫秒级逐字时间戳）

---

## 一、阶段一任务单：Antigravity 云端配置全栈三端灾备与一键恢复加固

### 1.1 背景与可行性结论
Antigravity 运行环境由三部分组成：
1. **会话级临时盘 (`/home/antigravity`)**：每次彻底更换容器可能重置。
2. **跨会话永久共享盘 (`/shared/user/.gemini` — 1.0 PB `virtiofs`)**：同一账号下跨会话持久保留，目前已存放 `youai/bin`（24 款 CLI）、`youai/skills`（37 个技能）、`youai/patches`、`colab_token.json`（含永久 `refresh_token`）及系统原生技能。
3. **外部双保险（GitHub `qihao1226/AIStudio` + 5TB Google Drive `云端系统配置`）**：为防止极端情况下连 `/shared/user/.gemini` 发生迁移或重置，**必须将 `/shared/user/.gemini` 中的全部非代码资产（37 套 Skills 完整包、字体池、Colab 补丁与恢复镜像包）同步打包备份至 Google Drive `云端系统配置` (`1YJqjW_FDdyY0iZsFeOSr1x_RK-F1_FFd`)，并将所有 CLI/脚本/SOP 同步至 GitHub**。

### 1.2 新会话执行清单（阶段一）
1. **打包全量灾备快照包 (`youai_full_disaster_recovery_v3.5.tar.gz`)**：
   - 将 `/shared/user/.gemini/youai`（含 `bin/`、`skills/`、`fonts/`、`patches/`、`sops/`）与 `/shared/user/.gemini/skills`（原生注册技能 `youai-video-factory`、`minimax-h3-colab`、`colab-multimodal-suite`、`colab-operator`）打包为 `/tmp/youai_full_disaster_recovery_v3.5.tar.gz`。
2. **上传至 Google Drive `云端系统配置` (`1YJqjW_FDdyY0iZsFeOSr1x_RK-F1_FFd`)**：
   - 使用 `gdrive mutate upload /tmp/youai_full_disaster_recovery_v3.5.tar.gz --parent 1YJqjW_FDdyY0iZsFeOSr1x_RK-F1_FFd` 上传备份包。
3. **升级 `scripts/bootstrap.sh` 支持“极端零状态从 Google Drive 自动拉取恢复”**：
   - 若检测到 `/shared/user/.gemini/youai/skills` 为空，自动通过 `gdrive readonly download` 拉取该灾备包解压恢复，实现 **“哪怕换全新账号/全新机器，10 秒内 100% 满血复活”**。

---

## 二、阶段二任务单：5TB Google Drive “Colab 大模型金库 (Model Vault)” 固化工程

### 2.1 可行性与核心工程准则（必读！）
**结论：完全可行，且必须采用，但必须遵循「Drive 持久存储 + 本地 NVMe 高速缓存/软链分流」架构！**

- **为什么绝对可行？**
  您拥有 **5TB Google Drive 空间**，而我们全套顶级开源模型权重总大小仅约 **75 GiB**：
  - `MiniMax-H3` (`Pruned INT8 ConvRot` + `Qwen3VL-32B NVFP4` + `4-step/8-step LoRA` + `VAE`)：**39.14 GiB**
  - `Tongyi-MAI/Z-Image-Turbo` (6B S3-DiT + Qwen3)：**~19.5 GiB**
  - `hexgrad/Kokoro-82M` + 8 大中文演播室音色 + 英文音色：**~0.4 GiB**
  - `SWivid/F5-TTS` (`F5TTS_v1_Base`)：**~1.3 GiB**
  - `mobiuslabsgmbh/faster-whisper-large-v3-turbo`：**~1.6 GiB**
  合计仅占 5TB 空间的 **1.5%**！
- **核心工程避坑准则（为什么很多人在网上说 Drive 加载慢，以及我们如何解决）**：
  - ❌ **错误做法**：让 PyTorch 直接通过 `/content/drive/MyDrive/...` 的 FUSE 网络挂载盘随机 `mmap` 读取几千个碎文件，会触发 Google Drive FUSE 的 IOPS 限流。
  - ✅ **工业级正确做法（“Drive 连续大文件金库 + 开机流式拉取/软链”）**：
    1. 在 Google Drive 建立标准模型金库目录：`/content/drive/MyDrive/AIStudio_Models/`（包含 `MiniMax-H3/` 与 `hf_cache/`）。
    2. 首次在 Colab 节点下载完成后，自动落盘至 `/content/drive/MyDrive/AIStudio_Models/`。
    3. 后续每次新开 Colab 会话，优先检查 `/content/drive/MyDrive/AIStudio_Models/`：对于 `MiniMax-H3` 单文件大权重（`.safetensors`），直接软链或通过顺序流式拷贝（Google 内网 Drive -> Colab `/content` NVMe 顺序读取速度高达 **350~500 MB/s**，无需经过外网 HuggingFace 限流，且完全不受 HF 429 限速影响！）。

### 2.2 新会话执行清单（阶段二）
1. 拉起一个 Colab `L4 --high-mem` 节点，执行 `colab drivemount`，运行一次 [`scripts/colab_multimodal_worker.py`](file:///home/antigravity/qihao1226/AIStudio/scripts/colab_multimodal_worker.py) 预热任务，确保 `Z-Image-Turbo`、`Kokoro-82M`、`F5-TTS` 与 `Faster-Whisper-Turbo` 完整落盘至 `/content/drive/MyDrive/AIStudio_Models/hf_cache/`。
2. 在运行 SOP 04 / SOP 05 的 `MiniMax-H3` 任务时，开启 `--mount-drive`，让 `39.14 GiB` 的 H3 权重自动落盘至 `/content/drive/MyDrive/AIStudio_Models/MiniMax-H3/`。

---

## 三、阶段三任务单：六大 SOP 能力上限实操测试（6 轮极限压测规约）

> **总体要求**：每一轮测试必须产出一个**真正达到爆款商业交付标准**的完整视频成片（绝不允许用几秒钟的简陋测试片敷衍），必须调用我们在 Colab 上的顶级开源模型矩阵（`MiniMax-H3` / `Z-Image-Turbo` / `Kokoro-82M` / `F5-TTS` / `Faster-Whisper-Turbo`），必须 100% 通过客观机器门禁（[`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper)、[`motion_check`](file:///home/antigravity/qihao1226/AIStudio/bin/motion_check)、[`pen_motion`](file:///home/antigravity/qihao1226/AIStudio/bin/pen_motion)、[`face_occlusion_check`](file:///home/antigravity/qihao1226/AIStudio/bin/face_occlusion_check)、[`cognitive_load_linter`](file:///home/antigravity/qihao1226/AIStudio/bin/cognitive_load_linter)），并按自包含目录结构完整上传至 Google Drive `内容生产` (`1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc`) 对应产线文件夹！

---

### 🔥 第 1 轮压测：`AG_SOP_01` · 商业深度纪实视频线（2.5D 物证微动 + 电影调色）
- **参考手册**：[`docs/sops/AG_SOP_01_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_01_v3.0.md)
- **Google Drive 交付目录**：`内容生产/01_真素材数字可视化/20261108_SOP01_AI算力能源战争_极限压测/`
- **压测命题**：《AI 算力尽头是能源：为什么科技巨头正在全球抢购核电站？》（时长 `30~45 秒`，6~8 个分镜，16:9 横屏 `1920x1080 @ 30fps`）。
- **必须动用的顶级能力组合**：
  1. **Colab `Z-Image-Turbo` (`colab_image_gen`)**：生成 4 张超写实 1080p 商业纪实底图 + 2 张带精准中文/英文标题的华尔街财报数据物证卡。
  2. **Colab `MiniMax-H3` (`minimax_h3_colab`)**：将其中 2 个核心分镜（如核电冷却塔/算力中心巡检）生成为真 3D 运镜 + 32kHz 工业环境音动态视频。
  3. **Colab `Kokoro-82M` (`colab_voice_gen --voice zm_yunjian --with-timestamps`)**：生成浑厚商业纪录片男声旁白与毫秒级逐字时间戳，混音锁定 `-16.0 LUFS`。
  4. **OpenFilm + 门禁**：套用 `lemo-opuscar` (`Oppenheimer` 琥珀暗金调色)，生成 12 格 [`wallstreet-strip`](file:///home/antigravity/qihao1226/AIStudio/bin/wallstreet-strip) 检视表，通过 [`motion_check`](file:///home/antigravity/qihao1226/AIStudio/bin/motion_check)（运动率 $\ge 30\%$）与 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper) 绿单。

---

### ⚡ 第 2 轮压测：`AG_SOP_02` · 极速快闪大字动效线（150Hz 底鼓重音同频 + 视觉大字报）
- **参考手册**：[`docs/sops/AG_SOP_02_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_02_v3.0.md)
- **Google Drive 交付目录**：`内容生产/02_极速快闪动效/20261108_SOP02_超级个体时代宣言_极限压测/`
- **压测命题**：《一人即千军：AI 超级个体的黄金时代》（时长 `20~30 秒`，高密度快节奏 12~16 镜，同时产出 `16:9` 与 `9:16` 双版本）。
- **必须动用的顶级能力组合**：
  1. **Colab `Z-Image-Turbo` (`colab_image_gen`)**：生成 4 张包含巨幅 3D 金属中文核心词（如「算力革命」「一人成军」「极致杠杆」）的赛博黑金背景底图。
  2. **Colab `Kokoro-82M` (`colab_voice_gen --voice zm_yunxi --speed 1.15 --with-timestamps`)**：生成高能量快节奏男声旁白与逐字毫秒级时间戳。
  3. **`beat_detector` + OpenFilm 快闪卡点**：提取 BGM 150Hz 以下底鼓（Kick）毫秒级峰值，使重音字卡缩放冲击与底鼓误差 $\le 40\text{ms}$，通过 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper)（`-14.0 LUFS`）验收。

---

### ✍️ 第 3 轮压测：`AG_SOP_03` · 白板手绘与火柴人讲解线（3.14 字/秒黄金认知节奏）
- **参考手册**：[`docs/sops/AG_SOP_03_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_03_v3.0.md)
- **Google Drive 交付目录**：`内容生产/03_白板火柴人讲解/20261108_SOP03_复利与认知陷阱_极限压测/`
- **压测命题**：《为什么 90% 的人明明很努力，却掉进了“伪勤奋”陷阱？》（时长 `30~40 秒`，6~8 个白板分镜）。
- **必须动用的顶级能力组合**：
  1. **Colab `Kokoro-82M` (`colab_voice_gen --voice zf_xiaobei --with-timestamps`)**：生成清晰知性的科技讲解女声，严格将语速控制在 **`3.14 ± 0.15` 字/秒** 黄金区间。
  2. **`wb` + `pen_motion` 渐进笔触渲染**：羊皮纸护眼底色（`#FAF6EE`）+ 手绘 SVG 路径渐进勾勒 + 火柴人情绪微动 + 翻页擦除拟音（Foley SFX）。
  3. **硬核门禁**：100% 通过 [`pen_motion`](file:///home/antigravity/qihao1226/AIStudio/bin/pen_motion) 与 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper)（`-16.0 LUFS`）验收。

---

### 🚀 第 4 轮压测：`AG_SOP_04` · 全源素材重构与外挂多模态车间（全明星模型大联合作战）
- **参考手册**：[`docs/sops/AG_SOP_04_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_04_v3.0.md)
- **Google Drive 交付目录**：`内容生产/04_全源素材重构/20261108_SOP04_硅谷算力帝国重构_极限压测/`
- **压测命题**：读取 `04_全源素材重构` 现有黄仁勋/算力中心基础图片素材，全流程重构一部 **“真动态音画同出 + 零样本声音克隆 + 四层景深合成”** 的旗舰样片（时长 `25~30 秒`，同时输出 `16:9` 横屏与 `9:16` 智能竖屏双母带）。
- **必须动用的顶级能力组合**：
  1. **Colab A100 `MiniMax-H3` (`minimax_h3_colab --mode ref2va`)**：基于人物参考图生成 2~3 段保持同一人物形象、不同景别且带 32kHz 立体声与中文口型对白的真动态视频片段。
  2. **Colab L4 `Z-Image-Turbo` (`colab_image_gen`)**：生成配套的 1080p 中英双语数据可视化底图。
  3. **Colab L4 `F5-TTS` (`colab_voice_gen --engine f5-tts`)**：使用参考音频完成零样本克隆旁白 + `Faster-Whisper-Turbo` 逐词字幕对齐。
  4. **OpenFilm 四层景深总装**：输出 `16:9` 与 `9:16` 双成片，100% 通过 [`sop04_colab_orchestrator.py --verify-only`](file:///home/antigravity/qihao1226/AIStudio/scripts/sop04_colab_orchestrator.py) 与 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper) 验收。

---

### 🎙️ 第 5 轮压测：`AG_SOP_05` · 工业口播伴侣动效线（AI 主播对口型 + 面部避障伴动浮层）
- **参考手册**：[`docs/sops/AG_SOP_05_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_05_v3.0.md)
- **Google Drive 交付目录**：`内容生产/05_工业口播伴侣/20261108_SOP05_AI商业认知口播_极限压测/`
- **压测命题**：打造一条真人级商业主播口播视频，并在主播身侧/安全区叠加 `adu-motion-video` 工业级伴侣数据浮层与金句字卡（时长 `20~30 秒`）。
- **必须动用的顶级能力组合**：
  1. **Colab `Z-Image-Turbo` (`colab_image_gen`)**：生成高质感演播室商业主播定妆首帧（采用三分法构图，为主播右侧预留伴动浮层安全区）。
  2. **Colab A100 `MiniMax-H3` (`minimax_h3_colab --mode fl2va`)**：驱动主播定妆照生成自然手势、呼吸感与精准中文口型对白的主播A-Roll视频轨。
  3. **`motionkit` + `face_occlusion_check`**：挂载伴侣动效卡片，强制通过 [`face_occlusion_check`](file:///home/antigravity/qihao1226/AIStudio/bin/face_occlusion_check)（面部避障间距 $\ge 120\text{px}$、底部 `220px` 字幕隔离带零遮挡）与 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper) 验收。

---

### 💻 第 6 轮压测：`AG_SOP_06` · 极客架构与概念演示线（Jacky-Motion 单聚光灯 + 零乱码架构推演）
- **参考手册**：[`docs/sops/AG_SOP_06_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_06_v3.0.md)
- **Google Drive 交付目录**：`内容生产/06_极客演示导演/20261108_SOP06_多智能体云端工厂架构_极限压测/`
- **压测命题**：《揭秘 Antigravity + Colab + Drive 云端视频工厂底层架构》（时长 `30~40 秒`，深色极客终端美学 + 动态数据流聚光灯推演）。
- **必须动用的顶级能力组合**：
  1. **Colab `Z-Image-Turbo` (`colab_image_gen`)**：生成高分辨率深色赛博架构隐喻过场底图（含精准中英文模块标签）。
  2. **Colab `Kokoro-82M` (`colab_voice_gen --voice zm_yunyang --with-timestamps`)**：生成沉稳极客技术叙事男声与毫秒级逐词时间戳。
  3. **`jacky-validate` + `cognitive_load_linter`**：确保同屏单聚光灯焦点、高对比度深色背景、零未解析占位符、**零 Emoji 豆腐块 (`☒`) 乱码**，并通过 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper) 终审。

---

## 四、每轮测试的标准交付物清单（缺一不可）

每完成一轮 SOP 压测，智能体必须在 Google Drive 对应目录下交付完整自包含包裹，并向用户汇报：
1. `交付成片/final_master_1080p.mp4`（及 SOP 02/04 的 `9:16` 竖屏版）
2. `交付成片/final_master.fcpxml`（可导入剪映专业版 / Final Cut Pro / Premiere 的非编工程文件）
3. `08_判据/final_contact_sheet.jpg`（12 格分镜抽帧检视表）
4. `08_判据/gatekeeper_report.json`（客观机器门禁 100% 绿单）
5. **严守算力纪律**：每轮 Colab GPU 任务跑完后，必须立即执行 `colab stop -s <session>` 释放 GPU，严禁后台空转消耗 Compute Units！
