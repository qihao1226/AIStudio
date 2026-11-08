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

## 三、阶段三任务单：六大 SOP 能力上限实操测试（6 轮极限压测规约 · 算力解耦版）

> **【最高架构边界原则：按需解耦，严禁盲目强绑 Colab】**
> 1. **只有 `AG_SOP_04`（全源素材重构与外挂多模态车间）是以 `Colab GPU` 为核心主力的产线**（重度调用 `MiniMax-H3`、`Z-Image-Turbo`、`F5-TTS`）。
> 2. **`AG_SOP_01`、`02`、`03`、`05`、`06` 五条产线各自拥有独立的本地原生渲染引擎与复合 Skills 模具**（真实物证 2.5D 视差、代码级快闪动效、SVG 矢量手绘白板、工业口播伴侣浮层、极客架构聚光灯），**默认 100% 在 Antigravity 云端主机本地极速闭环完成（零 GPU 消耗、秒级出片）**！除非某个特定分镜极端缺失底图或配音，否则严禁强行拉起 Colab GPU。
> 3. 每一轮测试必须产出真正达到商业交付标准的完整成片，100% 通过客观机器门禁（[`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper)、[`motion_check`](file:///home/antigravity/qihao1226/AIStudio/bin/motion_check)、[`pen_motion`](file:///home/antigravity/qihao1226/AIStudio/bin/pen_motion)、[`face_occlusion_check`](file:///home/antigravity/qihao1226/AIStudio/bin/face_occlusion_check)、[`cognitive_load_linter`](file:///home/antigravity/qihao1226/AIStudio/bin/cognitive_load_linter)），并按自包含目录结构完整上传至 Google Drive `内容生产` (`1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc`) 对应产线文件夹！

---

### 🔥 第 1 轮压测：`AG_SOP_01` · 商业深度纪实与真素材数字可视化线（本地真物证 + 2.5D 视差 + 电影调色，零 Colab 强绑）
- **参考手册**：[`docs/sops/AG_SOP_01_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_01_v3.0.md)
- **Google Drive 交付目录**：`内容生产/01_真素材数字可视化/20261108_SOP01_AI算力能源战争_本地真素材版/`
- **压测命题**：《AI 算力尽头是能源：为什么科技巨头正在全球抢购核电站？》（时长 `30~45 秒`，6~8 个分镜，16:9 横屏 `1920x1080 @ 30fps`）。
- **核心原生工序（纯 Antigravity 本地闭环，不绑 Colab）**：
  1. **奥斯卡电影调色定调 (`search_styles`)**：调用 `search_styles "Spotlight"` 与 `search_styles "Oppenheimer"` 提取暗调商业纪实色彩令牌与径向暗角滤镜（Vignette）。
  2. **37 套持久化 Skills 复合模具装配**：严禁 PIL 静态画图！强制认领 `Jacky-motion L01/L03/L05/L08`（左轴大字、非对称机柜对比、电网层级、研报证据板）、`Remotion Financial Chart`（发光走势曲线与跳动计数器）、`Stage25D`（真实研报/SEC 10-K 原件 2.5D 连续帧景深推拉 + 0.6s 荧光笔涂抹高亮）与 `HyperFrames T8`（交割凭单红章砸印）。
  3. **音频母带混音 (`audio_bgm_mixer`)**：按 `3.7 字/秒` 深度叙事节奏生成旁白，混入深沉调查背景乐，30ms 首尾防爆音淡化，严格锁定 `-16.0 ± 1.0 LUFS`。
  4. **OpenFilm 4 层编译与三重门禁**：输出 12 格 [`wallstreet-strip`](file:///home/antigravity/qihao1226/AIStudio/bin/wallstreet-strip) 检视表，100% 通过 [`motion_check`](file:///home/antigravity/qihao1226/AIStudio/bin/motion_check)（镜头运动活跃率 $\ge 30\%$）与 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper) 绿单。

---

### ⚡ 第 2 轮压测：`AG_SOP_02` · 极速快闪大字动效线（150Hz 底鼓重音同频 + 代码级排版引擎，零 Colab 强绑）
- **参考手册**：[`docs/sops/AG_SOP_02_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_02_v3.0.md)
- **Google Drive 交付目录**：`内容生产/02_极速快闪动效/20261108_SOP02_超级个体时代宣言_极限压测/`
- **压测命题**：《一人即千军：AI 超级个体的黄金时代》（时长 `20~30 秒`，高密度快节奏 12~16 镜，同时产出 `16:9` 与 `9:16` 双版本）。
- **核心原生工序（纯 Antigravity 本地闭环）**：
  1. **`beat_detector` 鼓点提取**：提取 BGM 150Hz 以下底鼓（Kick）毫秒级峰值时间戳。
  2. **代码级高对比大字冲击舞台**：黑金/高饱和极简撞色交替、巨幅核心词弹簧缩放冲击（误差 $\le 40\text{ms}$）。
  3. **硬核门禁**：通过 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper)（`-14.0 ± 1.0 LUFS`）验收。

---

### ✍️ 第 3 轮压测：`AG_SOP_03` · 白板手绘与火柴人讲解线（3.14 字/秒黄金认知节奏 + 纯矢量 SVG，零 Colab 强绑）
- **参考手册**：[`docs/sops/AG_SOP_03_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_03_v3.0.md)
- **Google Drive 交付目录**：`内容生产/03_白板火柴人讲解/20261108_SOP03_复利与认知陷阱_极限压测/`
- **压测命题**：《为什么 90% 的人明明很努力，却掉进了“伪勤奋”陷阱？》（时长 `30~40 秒`，6~8 个白板分镜）。
- **核心原生工序（纯 Antigravity 本地闭环）**：
  1. **黄金认知语速控制**：生成清晰知性的讲解语音，严格将语速控制在 **`3.14 ± 0.15` 字/秒** 黄金区间。
  2. **`wb` + `pen_motion` 渐进笔触渲染**：羊皮纸护眼底色（`#FAF6EE`）+ 手绘 SVG 路径渐进勾勒 + 火柴人情绪简笔画 + 翻页书写摩擦拟音（Foley SFX）。
  3. **硬核门禁**：100% 通过 [`pen_motion`](file:///home/antigravity/qihao1226/AIStudio/bin/pen_motion) 与 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper)（`-16.0 LUFS`）验收。

---

### 🚀 第 4 轮压测：`AG_SOP_04` · 全源素材重构与外挂多模态车间（Colab A100/L4 全明星模型大联合作战）
- **参考手册**：[`docs/sops/AG_SOP_04_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_04_v3.0.md)
- **Google Drive 交付目录**：`内容生产/04_全源素材重构/20261108_SOP04_硅谷算力帝国重构_极限压测/`
- **压测命题**：读取 `04_全源素材重构` 现有黄仁勋/算力中心基础图片素材，全流程重构一部 **“真动态音画同出 + 零样本声音克隆 + 四层景深合成”** 的旗舰样片（时长 `25~30 秒`，同时输出 `16:9` 横屏与 `9:16` 智能竖屏双母带）。
- **必须动用的 Colab 顶级能力组合（本产线为主力 GPU 车间）**：
  1. **Colab A100 `MiniMax-H3` (`minimax_h3_colab --mode ref2va`)**：基于人物参考图生成 2~3 段保持同一人物形象、不同景别且带 32kHz 立体声与中文口型对白的真动态视频片段。
  2. **Colab L4 `Z-Image-Turbo` (`colab_image_gen`)**：生成配套的 1080p 中英双语数据可视化底图。
  3. **Colab L4 `F5-TTS` (`colab_voice_gen --engine f5-tts`)**：使用参考音频完成零样本克隆旁白 + `Faster-Whisper-Turbo` 逐词字幕对齐。
  4. **OpenFilm 四层景深总装**：输出 `16:9` 与 `9:16` 双成片，100% 通过 [`sop04_colab_orchestrator.py --verify-only`](file:///home/antigravity/qihao1226/AIStudio/scripts/sop04_colab_orchestrator.py) 与 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper) 验收。

---

### 🎙️ 第 5 轮压测：`AG_SOP_05` · 工业口播伴侣动效线（本地口播 A-Roll + 面部避障伴动浮层，按需选配 Colab）
- **参考手册**：[`docs/sops/AG_SOP_05_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_05_v3.0.md)
- **Google Drive 交付目录**：`内容生产/05_工业口播伴侣/20261108_SOP05_AI商业认知口播_极限压测/`
- **压测命题**：基于已有或本地合成的商业主播口播 A-Roll 视频轨，在主播身侧安全区叠加 `adu-motion-video` 工业级伴侣数据浮层、逻辑推演图与金句字卡（时长 `20~30 秒`）。
- **核心原生工序（默认纯 Antigravity 本地闭环）**：
  1. **`motionkit` 伴动浮层构建**：根据口播逐词时间戳，在主播身侧三分法安全区动态弹出玻璃拟态数据卡与金句高亮。
  2. **`face_occlusion_check` 硬核避障门禁**：强制通过 [`face_occlusion_check`](file:///home/antigravity/qihao1226/AIStudio/bin/face_occlusion_check)（面部避障间距 $\ge 120\text{px}$、底部 `220px` 字幕隔离带零遮挡）与 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper) 验收。（注：仅当无现成口播视频且明确需要生成虚拟主播时，才按需调用 Colab `MiniMax-H3`）。

---

### 💻 第 6 轮压测：`AG_SOP_06` · 极客架构与概念演示线（Jacky-Motion 单聚光灯 + 零乱码架构推演，零 Colab 强绑）
- **参考手册**：[`docs/sops/AG_SOP_06_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_06_v3.0.md)
- **Google Drive 交付目录**：`内容生产/06_极客演示导演/20261108_SOP06_多智能体云端工厂架构_极限压测/`
- **压测命题**：《揭秘 Antigravity + Colab + Drive 云端视频工厂底层架构》（时长 `30~40 秒`，深色极客终端美学 + 动态数据流聚光灯推演）。
- **核心原生工序（纯 Antigravity 本地闭环）**：
  1. **`Jacky-motion` 极客深色拓扑舞台**：纯代码 SVG/HTML5 构建三层云端协同架构图，随语音叙事逐级点亮当前讲解模块（单聚光灯焦点），其余模块自动降暗虚化。
  2. **`jacky-validate` + `cognitive_load_linter` 硬核门禁**：确保同屏单聚光灯焦点、高对比度深色背景、零未解析占位符、**零 Emoji 豆腐块 (`☒`) 乱码**，并通过 [`film_gatekeeper`](file:///home/antigravity/qihao1226/AIStudio/bin/film_gatekeeper) 终审。

---

## 四、每轮测试的标准交付物清单（缺一不可）

每完成一轮 SOP 压测，智能体必须在 Google Drive 对应目录下交付完整自包含包裹，并向用户汇报：
1. `交付成片/final_master_1080p.mp4`（及 SOP 02/04 的 `9:16` 竖屏版）
2. `交付成片/final_master.fcpxml`（可导入剪映专业版 / Final Cut Pro / Premiere 的非编工程文件）
3. `08_判据/final_contact_sheet.jpg`（12 格分镜抽帧检视表）
4. `08_判据/gatekeeper_report.json`（客观机器门禁 100% 绿单）
5. **严守算力纪律**：每轮 Colab GPU 任务跑完后，必须立即执行 `colab stop -s <session>` 释放 GPU，严禁后台空转消耗 Compute Units！
