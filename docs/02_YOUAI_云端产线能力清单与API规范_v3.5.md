# YOUAI 优爱云端多模态产线能力清单与 API 规范 (v3.5)

> **文档密级**：工业制造级标准  
> **适用受众**：本地智能体矩阵（Hermes、OpenClaw、OpenCode、DSH 等）、本地 Prompt 模板库及云端调度总控（Antigravity Agent）  
> **核心目标**：提供云端模型能力底座、提示词工程规范与基于 Google Drive 网盘流（Trigger Option B）的生产清单（Manifest）对接协议。

---

## 一、 顶层架构与作业拓扑（Architecture & Boundary）

优爱云端多模态生产体系采取**“本地为创意大脑与导演室（Studio），云端为工业化无人渲染农场（Factory）”**的分层解耦设计。

```
+---------------------------------------------------------------------------------+
|                         【本地 YOUAI 创意导演室】                                  |
|   - 人机协同：创作者 (User) + 本地智能体 (Hermes / OpenClaw / DSH / OpenCode)      |
|   - 职责：剧本推敲、镜头分镜、审美指导、音色选型、提示词打磨与契约自检             |
|   - 交付物：结构化《生产需求与物料清单》（production_manifest.yaml / .json）         |
+---------------------------------------------------------------------------------+
                                      │
                                      ▼ (网盘流 Option B 同步)
+---------------------------------------------------------------------------------+
|                       【Google Drive 生产中转枢纽】                              |
|   /YOUAI_FACTORY/                                                               |
|   ├── 00_待生产队列_QUEUE/       <-- 本地智能体放入待执行项目任务包                |
|   ├── 01_生产中_PROCESSING/     <-- 云端 Antigravity 锁定正在执行的任务           |
|   ├── 02_已交付成片_DELIVERED/   <-- 云端工厂输出最终成片、分轨物料与质检报告      |
|   └── 03_异常中断_FAILED/       <-- 语法报错、算力熔断或未通过质检的任务包        |
+---------------------------------------------------------------------------------+
                                      │
                                      ▼ (全自动扫描与执行)
+---------------------------------------------------------------------------------+
|                         【云端 Antigravity 工业工厂】                             |
|   - 调度总控：Antigravity Agent (Schema 校验、依赖拓扑排序、资产分发、状态回写)  |
|   - 算力引擎：Google Colab GPU 集群 (A100 80GB / L4 24GB) + 5TB GDrive Model Vault|
|   - 本地动效：Antigravity Cloud VM (Stage25D / HyperFrames / Whiteboard / OpenFilm)|
+---------------------------------------------------------------------------------+
```

---

## 二、 网盘流（Trigger Option B）协同作业规范

### 1. 目录拓扑与命名规则
在 Google Drive 中配置统一根目录（默认根目录或当前项目目录下的 `YOUAI_FACTORY_QUEUE`）：
```text
YOUAI_FACTORY_QUEUE/
├── 00_待生产队列_QUEUE/
│   └── PROJECT_20261112_001/               # 项目唯一目录名
│       ├── production_manifest.yaml        # 【必须】生产总控清单
│       └── custom_assets/                  # 【可选】自定义参考资产
│           ├── speaker_ref_5s.wav          # 声音克隆参考音频
│           ├── character_ref_01.png        # 角色/风格参考原画
│           └── brand_logo.svg              # 品牌矢量标识
├── 01_生产中_PROCESSING/
│   └── PROJECT_20261112_001/
│       └── progress.log                    # 云端动态回写的心跳与日志
├── 02_已交付成片_DELIVERED/
│   └── PROJECT_20261112_001/
│       ├── final_master_1080p.mp4          # 最终母带成片
│       ├── final_master.fcpxml             # FCPXML / PR 剪辑工程
│       ├── delivery_report.md              # 交付质量分析报告
│       └── assets/                         # 各镜头独立生成的 4K 图 / 音频 / 字戳
└── 03_异常中断_FAILED/
    └── PROJECT_20261112_001/
        └── error_diagnostic.log            # 详细报错堆栈与修正建议
```

### 2. 状态机流转与执行协议
1. **本地投递**：本地 Agent 组装完毕 `production_manifest.yaml` 及依赖素材后，整体保存至 `00_待生产队列_QUEUE/<PROJECT_ID>/`。
2. **云端接单**：云端 Antigravity 巡检或收到用户触发指令后，执行**原子移动（Move）**，将该项目文件夹移动至 `01_生产中_PROCESSING/<PROJECT_ID>/`，防止重复消费。
3. **Schema 校验与依赖拓扑**：
   - 检查模型名是否合法、参数是否越界、引用素材是否存在。
   - 拓扑排序：`TTS 音频合成 (测出精确时长)` $\rightarrow$ `ASR 毫秒级字戳提取` $\rightarrow$ `关键帧图像渲染` $\rightarrow$ `视频片段生成 / 2.5D 本地动效合成` $\rightarrow$ `OpenFilm 复合装配` $\rightarrow$ `Gatekeeper 响度与画质终审`。
4. **交付或熔断**：
   - 质检通过：移动至 `02_已交付成片_DELIVERED/<PROJECT_ID>/`，并在清单内标记 `status: SUCCESS`。
   - 异常失败：保留已生成资产，移动至 `03_异常中断_FAILED/<PROJECT_ID>/`，输出 `error_diagnostic.log` 供本地排查。

---

## 三、 云端多模态模型能力矩阵（Full Capability Matrix）

### 1. 视觉图像生成引擎 (Image Generation)

| 模型标识 (Engine ID) | 核心架构与底层底座 | 典型耗时 & 算力 | 分辨率规格 | 适用场景与绝对优势 |
| :--- | :--- | :--- | :--- | :--- |
| **`z-image-turbo`** *(默认主力)* | `Tongyi-MAI/Z-Image-Turbo` (6B DiT + `Qwen3Model`, 8步蒸馏) | ~2.5s (L4 / A100) | `1920x1080` (16:9)<br>`1080x1920` (9:16)<br>`1080x1080` (1:1) | **商用中英双语文字排版海报**、高频科技 PPT 视觉配图、商业摄影、UI 界面卡片。中英文字渲染无乱码。 |
| **`minimax-h3-image`** *(画质旗舰)* | `Comfy-Org/MiniMax-H3-Image` (33.1B DiT + `Qwen3-VL-32B`, 6步蒸馏) | ~10-20s (A100) | **原生 4K**: `3840x2160`<br>`4096x4096`<br>`16MP` 任意比例 | **顶级 4K 电影级分镜原画、原生支持 1-16 张参考图的角色/道具跨镜头一致性编辑**。与 H3 视频共享特征空间。 |
| **`flux-schnell`** *(影调补充)* | `unsloth/FLUX.1-schnell` (12B MMDiT, 4步蒸馏) | ~3.0s (L4 / A100) | `1920x1080` (16:9)<br>`1080x1920` (9:16) | 欧美写实人物肖像、强戏剧化光影、35mm 胶片质感。 |

### 2. 语音合成、克隆与对齐引擎 (Voice & Audio)

| 模型标识 (Engine ID) | 核心架构 | 采样率与母带标准 | 核心参数与音色选项 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **`kokoro`** *(录音室母带)* | `hexgrad/Kokoro-82M` (StyleTTS2 + ISTFTNet) | 44.1kHz / 24-bit<br>标准 `-14.0 LUFS` | **国语主播**：<br>• `zm_yunjian` (权威/宏大深度纪实男声)<br>• `zm_yunxi` (活力/高亢快闪讲解男声)<br>• `zm_yunyang` (专业新闻播音男声)<br>• `zf_xiaoxiao` (温暖细腻播客纪实女声)<br>• `zf_xiaobei` (干练知性极客技术女声)<br>**英语主播**：`af_heart`, `am_fenrir` | 纪实片旁白、技术讲解、快闪口播。发音清澈无底噪，节奏起伏极佳。 |
| **`f5-tts`** *(零样本克隆)* | `SWivid/F5-TTS` (Flow Matching v1_Base) | 24kHz / 16-bit<br>标准 `-14.0 LUFS` | 入参：`ref_audio` (3~10秒无杂音 WAV/MP3) + `ref_text` (参考音频原文字) | 个人 IP 专属声音克隆、创始人商业演说复刻、多语种音色迁移。 |
| **`faster-whisper-large-v3-turbo`** | OpenAI Whisper 蒸馏优化版 (CUDA fp16) | 毫秒级字戳 | 伴生输出 `<name>.words.json` | 自动生成对齐字幕、精准驱动分镜剪辑与大字快闪（SOP 02）。 |
| **`audio_bgm_mixer`** | 云端本地 DSP 动态母带混音器 | 48kHz 立体声<br>标准 `-16.0 LUFS` | 人声闪避 (Auto-Ducking -18dB)、响度归一化、EQ 降噪 | 自动压制背景音乐并混合人声，杜绝人声被 BGM 掩盖。 |

### 3. 动态视频生成引擎 (Video Generation)

| 模型标识 (Engine ID) | 硬件底座与算力需求 | 规格与帧率 | 核心能力与关键特性 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **`minimax-h3-video`** *(视音频同步旗舰)* | NVIDIA A100 (80GB)<br>CUDA 13 + INT8 ConvRot | 960x544 / 768p / 1080p<br>24fps / 4~8 步采样 | • **视频与 32kHz 立体声原生同步生成**。<br>• **台词口型同步（Lip-Sync）**：在 Prompt 中嵌入 `<d>[Mandarin] 台词</d>` 即可同步生成说话口型与对应真人发音。<br>• 模式：`reference` (单/多图引申) 与 `first_frame` (首帧延续)。 | 高拟真人物解说、电影感推拉摇移运镜、音画一体短剧镜头。 |

### 4. 零 Colab 算力消耗的云端本地轻量生产线 (SOP 01~06 边界)

> **[黄金算力规则]**：除了 `AG_SOP_04`（外挂 Colab GPU 车间）之外，以下流水线**默认 100% 在 Antigravity 云电脑本地执行**，零 GPU 等待时间，秒级出片：

* **`AG_SOP_01` (商业深度纪实视频)**：Stage25D 视差镜头、金融图表动态生成、真物证扫描展台。
* **`AG_SOP_02` (极速快闪大字动效)**：HyperFrames 动效引擎，基于 Whisper 毫秒字戳与鼓点瞬态（Beat Sync）纯代码对齐。
* **`AG_SOP_03` (白板手绘与火柴人)**：`wb` 矢量 SVG 渐进笔触，严格 3.14 字/秒语速物理对齐。
* **`AG_SOP_05` (工业口播伴侣动效)**：`motionkit` 人脸避障算法，自动在口播视频的安全边距生成画中画动效。
* **`AG_SOP_06` (极客架构与概念演示)**：`Jacky-motion 2.1` 单聚光灯动效，内联技术架构 SVG 动效。
* **`OpenFilm 工业组装流水线`**：`to_timeline` $\rightarrow$ `edl2film` $\rightarrow$ `openfilm render` $\rightarrow$ `film_gatekeeper` 全自动压制交付。

---

## 四、 单个物料提示词工程金标准 (Prompt Engineering Standard)

本地 Agent 在输出物料提示词时，**必须严格遵守以下各模型的语法规范**，严禁使用模糊口语！

### 1. 图像提示词规范 (Image Prompts)

#### A. `z-image-turbo`（注重中英文字排版与高质感商业摄影）
* **文字排版语法**：若画面需要出现文字，必须使用双引号包裹，例如 `"未来算力中心"` 或 `"AGI 2026"`。
* **结构范式**：`[核心主体与动作] + [文字排版指定] + [构图与景别] + [灯光与色彩] + [相机镜头规格]`。
* **优质范例**：
  ```text
  A minimalist tech keynote slide background, dark navy blue and matte graphite surface. In the center, crisp glowing typography displaying "YOUAI 工业化产线" in ultra-clean sans-serif font. Isometric perspective, subtle cyan volumetric edge lighting, 8k resolution, cinematic commercial photography, 50mm lens.
  ```

#### B. `minimax-h3-image`（4K 原生与多图一致性）
* **特征**：6步快速蒸馏，**无需负向提示词 (Negative Prompt 无效)**，支持多图引用。
* **多图引用语法**：若提供了参考图，在 Prompt 中用 `<Subject 1> from <Picture 1>` 进行定位与约束。
* **优质范例（纯生图）**：
  ```text
  Cinematic ultra-realistic 4K commercial shot of an advanced automated robotics cleanroom at dawn. In the foreground, sleek carbon-fiber robotic arms assemble glowing semiconductor wafers. Volumetric golden hour sunlight piercing through floor-to-ceiling glass windows, dust motes visible in air, 35mm anamorphic lens, f/1.8, shallow depth of field, photorealistic, 8k master.
  ```
* **优质范例（多图引用一致性）**：
  ```text
  Keep the facial features and hair style of <Subject 1> from <Picture 1> completely unchanged. Place <Subject 1> wearing a tailored charcoal business suit, confidently walking through a bustling Singapore futuristic financial center, background blurred with warm bokeh, cinematic lighting, 4K resolution.
  ```

---

### 2. 音频提示词与文本标注规范 (Audio & Voice)

#### A. `kokoro`（韵律学控制）
* **标点停顿控制**：Kokoro 对标点符号极度敏感。
  * 短停顿：用逗号 `,`；
  * 思考与节奏留白：用全角破折号 `——` 或省略号 `……`；
  * 强调：将核心名词置于短句开头。
* **音色与语速匹配表**：
  * 商业纪实（沉稳深度）：`voice: "zm_yunjian"`, `speed: 1.0`
  * 科技讲解（清爽专业）：`voice: "zf_xiaobei"`, `speed: 1.05`
  * 快闪短视频（紧凑有力）：`voice: "zm_yunxi"`, `speed: 1.15`
  * 播客叙事（温暖亲和）：`voice: "zf_xiaoxiao"`, `speed: 0.98`

#### B. `f5-tts`（声音克隆）
* **参考音频黄金法则**：时长 3~10 秒，必须为单声道无伴奏、无回声、高信噪比的纯人声。
* **参考文本对应**：`ref_text` 必须与 `ref_audio` 的实际发音一字不差，标点符号完整。

---

### 3. 视频提示词金标准：MiniMax-H3 Video 严苛六段式结构

> **[强制性规范]**：MiniMax-H3 Video 严禁输入单句提示词！必须组织为标准 6-Section 格式：

```text
subject_definitions:
<Subject 1> is the tech founder from <Picture 1>, East Asian male in his late 30s, short black hair, wearing rimless glasses and a dark obsidian tech jacket.

summary:
[reference generation] <Subject 1> stands before a holographic blueprint display in a command center, calmly presenting the cloud architecture while looking towards the camera.

retention_analysis:
<Subject 1> (appears in Shot 1): fully_preserved - facial features, glasses, haircut, and obsidian jacket must be perfectly identical to Picture 1.

detailed_description:
The target video has a cinematic sci-fi commercial aesthetic, 24fps, teal and orange color grading, 16:9 aspect ratio.
[Shot 1] Medium close-up shot. Smooth, slow cinematic dolly-in camera motion. Soft ambient cool blue light reflects off the holographic glass in front of him. <Subject 1> blinks naturally, gestures gently with his right hand, looks directly at the lens, and speaks: <d>[Mandarin] 我们的云端多模态产线，已经实现了从分镜构思到母带渲染的工业级闭环。</d>

overall_soundscape:
Subtle low-frequency atmospheric hum of high-end servers, distant electronic data chimes, natural studio vocal acoustics.

non_diegetic_music:
N/A
```

* **台词口型规范**：台词部分必须包裹在 `<d>[Mandarin] 你的中文台词 </d>` 或 `<d>[English] English lines </d>` 中，引擎将自动解算唇形并合成 32kHz 伴音。

---

## 五、 生产需求单契约规范 (`production_manifest.yaml` Schema)

本地智能体最终必须输出符合此 Schema 的 YAML 或 JSON 文件，放置在项目的根目录下。

```yaml
version: "3.5"
project_id: "YOUAI_20261112_TECH_001"
project_title: "量子计算与云端算力重构架构解析"
sop_id: "AG_SOP_04" # 可选: AG_SOP_01 ~ 06

global_config:
  aspect_ratio: "16:9"       # 16:9 | 9:16 | 1:1
  color_grading: "Cinematic Neo-Tokyo, Teal & Orange, High Dynamic Range"
  master_audio_lufs: -14.0   # 交付母带响度标准
  export_fcpxml: true        # 是否生成剪辑轨道工程

# 生产任务序列（云端调度引擎将按拓扑关系自动并行与串行）
tasks:
  # ---------------- Task 1: 旁白配音与字戳提取 ----------------
  - task_id: "task_voice_001"
    type: "voice_narration"
    engine: "kokoro"           # kokoro | f5-tts
    voice: "zm_yunjian"
    speed: 1.05
    with_timestamps: true     # 必须开启以生成 .words.json 用于装配
    text: "在深邃的数字星系中，每一台超算节点的轰鸣，都在重写未来的算力边界。"
    output: "assets/audio/shot_001_vo.wav"

  # ---------------- Task 2: 4K 关键帧图像渲染 ----------------
  - task_id: "task_image_001"
    type: "image_generation"
    engine: "minimax-h3-image" # minimax-h3-image | z-image-turbo | flux-schnell
    resolution: "4k"
    aspect_ratio: "16:9"
    prompt: "Cinematic 4K wide establishing shot of a futuristic subterranean quantum data center, glowing glass cryogenic towers with liquid helium conduits, cool blue and amber ambient light, 35mm lens, photorealistic."
    output: "assets/images/shot_001_keyframe.png"

  # ---------------- Task 3: 视频镜头生成 (依赖 Task 2 关键帧) ----------------
  - task_id: "task_video_001"
    type: "video_generation"
    engine: "minimax-h3-video"
    mode: "reference"         # reference | first_frame
    ref_image: "assets/images/shot_001_keyframe.png" # 关联上一步产物
    duration_seconds: 5.0
    width: 960
    height: 544
    steps: 4
    prompt_file_content: |
      subject_definitions:
      <Subject 1> is the quantum cooling tower from <Picture 1>.
      summary:
      [reference generation] Slow cinematic forward camera push-in through cryogenic towers.
      retention_analysis:
      <Subject 1> (appears in Shot 1): fully_preserved.
      detailed_description:
      Cinematic sci-fi lighting. [Shot 1] Slow forward camera dolly-in. Cryogenic vapor slowly drifts across the floor.
      overall_soundscape:
      Deep mechanical hum, low airflow rumble.
      non_diegetic_music:
      N/A
    output: "assets/video/shot_001_clip.mp4"

# 最终时间线组装规则 (OpenFilm)
assembly:
  timeline:
    - shot_id: "shot_001"
      video_ref: "task_video_001"
      audio_ref: "task_voice_001"
      subtitle_align: true     # 基于字戳自动压制字幕
      transition: "fade_in_0.5s"

  bgm:
    track: "assets/bgm/deep_ambient_cyber.mp3" # 若无则从通用库选配
    volume_ducking: -18.0     # 遇人声自动避让
```

---

## 六、 本地智能体（Hermes / OpenClaw / DSH）挂载 Prompt 模板

你可以直接将以下提示词配置为本地智能体的 System Prompt 或专有技能（Skill）：

```markdown
### 角色定位：YOUAI 顶层创意导演与工单编译器（Master Storyboarder & Prompt Compiler）

你拥有精湛的剧本创作、影视镜头语言与严谨的工业工程能力。你的唯一任务是协助用户梳理内容创意，产出符合《YOUAI 优爱云端多模态产线能力清单与 API 规范 v3.5》的标准生产需求单（production_manifest.yaml）。

#### 你的执行工作流：
1. **创意需求对齐**：理解用户的内容主题、目标受众、叙事节奏（沉稳纪实 / 极速快闪 / 极客架构等）。
2. **选择最优 SOP 路线**：
   - 商业图表/证物：匹配 AG_SOP_01
   - 极速快闪文字：匹配 AG_SOP_02
   - 白板火柴人：匹配 AG_SOP_03
   - 重度 AIGC（4K图/视频生成）：匹配 AG_SOP_04
   - 口播伴侣：匹配 AG_SOP_05
   - 极客架构演示：匹配 AG_SOP_06
3. **分镜与提示词编译**：
   - 为每个镜头精准匹配云端模型（Z-Image-Turbo / MiniMax-H3-Image / Kokoro / MiniMax-H3-Video）。
   - 严格执行模型提示词规则（如 H3-Video 的六段式结构与台词标签；Kokoro 的标点符号韵律；Z-Image 的双引号排版文字）。
4. **输出自检（Linter Rules）**：
   - [ ] 检查所有模型名是否在规范列表内。
   - [ ] 检查图像与视频的分辨率、长宽比是否合法。
   - [ ] 检查 MiniMax-H3-Video 是否包含完整的 6 个必须字段。
   - [ ] 检查 Kokoro 是否配置了 `with_timestamps: true`。
5. **文件生成**：输出完整的 `production_manifest.yaml`，提示用户存入 Google Drive 队列目录 `YOUAI_FACTORY_QUEUE/00_待生产队列_QUEUE/<项目名>/`。
```

---

## 七、 异常处理与重试机制 (Error Handling)

1. **显存/模型加载异常（OOM & Engine Fault）**：
   - 云端检测到 Colab GPU 显存不足时，自动降级分辨率（如 4K 降至 1080p），并在报告中告警。
2. **提示词校验不通过（Linter Error）**：
   - 若 `production_manifest.yaml` 格式错误，Antigravity 不会启动 Colab GPU，直接生成错误报告并移入 `03_异常中断_FAILED/`，避免浪费算力单元。
3. **网络与 RPC 断连容错**：
   - 纯 HTTP Kernel RPC 具备自动指数退避重试（最多 3 次）。若重试失败，已完成的独立物料完整落盘在 GDrive，断点恢复无需重新生成。

---
*优爱视频工场 (YOUAI Cloud Factory) 架构委员会 制定*  
*最新修订日期：2026年11月*
