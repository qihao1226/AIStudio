# AG_SOP_04 · 全源素材重构与外挂多模态视频生产流水线 SOP (v3.0 极致执行手册版)

> **版本**：v3.0 (Antigravity + Colab CLI 纯 HTTPS RPC 桥接 + 零外部付费 API 闭环版) ｜ **更新日期**：2026-11-08  
> **产线编号**：P10「全源素材重构 + 外挂多模态车间」 ｜ **表现形态**：形态 11「普适全品类动态重构」(Universal Media Remix)  
> **总协调大脑**：Antigravity Cloud VM (策划、去水精剪、智能构图、4层代码动效总装)  
> **外挂算力车间**：Google Colab GPU (`colab` CLI + Pure-HTTP RPC Bridge `http_rpc.py` 全自动无头调用)  
> **核心铁律**：**严格采用 `Antigravity + Google Colab + Google Drive` 高性价比全自动闭环，暂不调用任何外部付费多模态路由（如 `omni-*-router`）。**  
> **GitHub 归档路径**：[`docs/sops/AG_SOP_04_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_04_v3.0.md)  
> **Google Drive 知识库路径**：`1YJqjW_FDdyY0iZsFeOSr1x_RK-F1_FFd/AG_SOP_04_全源素材重构与外挂多模态视频生产流水线 SOP v1.0.md`  
> **Google Drive 交付路径**：`1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/04_全源素材重构/`

---

## 〇、强制前置铁律（Step 0：跨会话永久底座与 Colab 纯 HTTPS 桥接唤醒）

在启动任何多模态生产任务前，**必须首先执行以下两行底座唤醒指令**：

```bash
/home/antigravity/qihao1226/AIStudio/scripts/bootstrap.sh
export PATH="/home/antigravity/.local/bin:/shared/user/.gemini/youai/bin:$PATH"
```

> **【为什么必须执行 `bootstrap.sh`？】**
> Antigravity 云端虚拟机代理默认拦截 WebSocket 升级请求（`403 Forbidden: WebSocket upgrades are not allowed`）。`bootstrap.sh` 会自动将 [`http_rpc.py`](file:///home/antigravity/qihao1226/AIStudio/scripts/patches/colab-cli/http_rpc.py) 纯 HTTPS 内核桥接补丁与 [`contents.py`](file:///home/antigravity/qihao1226/AIStudio/scripts/patches/colab-cli/contents.py) 修复补丁注入 `google-colab-cli`，使 `colab run`、`colab exec`、`colab upload`、`colab download` 100% 穿透代理全自动运行。

---

## 一、七大顶层设计决策（v3.5 顶级开源多模态量化门禁）

| # | 决策维度 | 核心规范与物理量化标准 | 机器拦截红线 |
| :---: | :--- | :--- | :--- |
| **1** | **零外部付费 API 闭环** | 所有视频生成（`MiniMax-H3`）、1080p 生图与中英海报排版（`Z-Image-Turbo` / `FLUX.1-schnell`）、超拟真播客配音（`Kokoro-82M`）、零样本声音克隆（`F5-TTS`）及毫秒级字幕转写（`Faster-Whisper-Turbo`），一律通过 `colab` CLI 派发至 Google Colab GPU 执行，并依托 5TB Google Drive 模型金库缓存。 | 严禁在脚本中硬编码调用外部收费多模态网关。 |
| **2** | **Z-Image-Turbo / FLUX.1 1080p 铁律** | 默认调用开源榜首 `Tongyi-MAI/Z-Image-Turbo`（6B S3-DiT + `Qwen3` 文本编码器，`num_inference_steps=9, guidance_scale=0.0, low_cpu_mem_usage=True`）或 `unsloth/FLUX.1-schnell`，原生支持中英双语海报大字精准渲染，并通过 `LANCZOS` 输出 **`1920x1080` 或 `1080x1920` 全高清 PNG**。 | 分辨率低于 `1080p`（如 `512x512`）直接由 `verify_assets_gatekeeper` 拦截。 |
| **3** | **Kokoro-82M / F5-TTS + `-14 LUFS` 防爆音** | 默认采用 `hexgrad/Kokoro-82M`（8 大中文演播室音色 `zm_yunjian`/`zm_yunxi`/`zf_xiaoxiao` 等）或 `SWivid/F5-TTS`（5 秒参考音频零样本克隆），产出必须经 FFmpeg 施加 **`30ms afade` 防爆音淡入淡出 + `-14.0 LUFS` 响度标准化 + `44100Hz / 16-bit PCM WAV` (`pcm_s16le`)**。 | 扩展名为 `.wav` 但内部为 MP3 编码或无淡化直接拦截。 |
| **4** | **逐词级毫秒时间戳（Faster-Whisper-Turbo）** | 采用 `mobiuslabsgmbh/faster-whisper-large-v3-turbo` 开启 `word_timestamps=True`，通过 FFmpeg 16kHz 浮点管道直传，同时输出 `words` 与 `segments` 双层 JSON。 | 缺少逐词时间戳导致字幕与重音卡点脱节。 |
| **5** | **四层视觉景深合成架构** | 严禁“单张静态底图 + 居中白字”幻灯片式拼贴！每一镜必须包含四层景深：① `MiniMax-H3` 真动态分镜或动态推拉底图；② 电影暗角遮罩（Vignette）；③ 视觉主体卡片/数据挂件；④ 逐词高亮字幕与底部进度条。 | `motion_check` 运镜活跃率 $<30\%$ 直接拦截。 |
| **6** | **横转竖 `9:16` 智能焦点构图** | 输出竖屏 `1080x1920` 版本时，禁止无脑裁切画面正中央导致左/右侧文字被腰斩；必须采用独立竖屏排版或焦点安全区重构。 | 竖屏画面出现文字截断或边缘出界。 |
| **7** | **100% 自包含货架交付** | 立项、Colab 原始产出、双画幅成片、12 格联系表与质检绿单全部收拢于 `04_全源素材重构/{YYYYMMDD}_{项目名}_v3/`。 | 根目录散落临时文件直接判定违规。 |
| **8** | **纯净视觉与零技术水印铁律** | 严禁在画面四周叠加 `[ SOP-04 ... ]`、`Z-IMAGE`、`MINIMAX-H3`、`L01~L08` 等模型或工程内部标签！所有文字纯粹聚焦于主题叙事。 | 出现任何技术标签直接被 `visual_purity_linter` 拦截。 |
| **9** | **电影级声学质感与场景化 BGM** | BGM 必须采用宏大深沉的史诗管弦乐（Cinematic Hybrid Orchestra），音量避让（-22 dB），严禁含高频机械滴答；无合适音乐默认 `--no-bgm`。 | 罐头音效刺耳或含电子蜂鸣。 |

---

## 二、全自动多模态生产四步标准工序与精确 CLI 指令手册

### 第 1 步：准备多模态任务工单 (`visual_prompts.json` & `tts_script.json`)
在本地任务目录（如 `./work/colab_job/`）写入分镜提示词与配音脚本：
```json
// ./work/colab_job/visual_prompts.json
[
  {"id": "shot_001", "prompt": "Massive hyperscale AI data center interior, glowing liquid cooling pipes, cinematic dark mood", "aspect": "16:9", "model": "z-image-turbo"},
  {"id": "shot_002", "prompt": "High voltage electrical grid transformer substation at dusk, industrial amber lighting", "aspect": "16:9", "model": "z-image-turbo"}
]
```

### 第 2 步：一键调度 Google Colab GPU 顶级开源多模态矩阵
```bash
# 方式 A：单点独立调用三大王牌 CLI（按需随时生成分镜图、配音克隆或音画同出视频）
# 1) 1080p 写实生图 & 中英双语海报渲染 (Z-Image-Turbo / FLUX.1-schnell on Colab L4)
colab_image_gen --prompt '科技感数据中心，中央全息屏显示金色中文「云端视频工厂」' --model z-image-turbo --aspect 16:9 --output ./03_素材/shot_001.png

# 2) 演播室级中文旁白 (Kokoro-82M) 或 5 秒零样本声音克隆 (F5-TTS) + 毫秒级逐词时间戳 (.words.json)
colab_voice_gen --text "欢迎来到云端视频生产工厂，每一帧都是工业级母带。" --voice zm_yunjian --with-timestamps --output ./03_素材/generated_tts.wav
colab_voice_gen --text "这是零样本克隆出的专属主播音色。" --engine f5-tts --ref-audio ./03_素材/speaker_ref_5s.wav --output ./03_素材/cloned_tts.wav

# 3) 角色参考图生成音画同步对口型视频 (MiniMax-H3 Ref2VA / FL2VA on Colab A100)
minimax_h3_colab --mode ref2va --image ./03_素材/shot_001.png --prompt "Cinematic medium shot..." --speech "[Mandarin] 欢迎来到云端视频工厂。" --output ./03_素材/shot_001_video.mp4

# 方式 B：工程级批量工单全自动编排 (sop04_colab_orchestrator.py)
python3 /home/antigravity/qihao1226/AIStudio/scripts/sop04_colab_orchestrator.py \
  --job-dir ./work/colab_job \
  --session youai-mm-l4
```
- 底层由 [`colab_multimodal_worker.py`](file:///home/antigravity/qihao1226/AIStudio/scripts/colab_multimodal_worker.py) (v3.5) 与 [`colab_minimax_h3_worker.py`](file:///home/antigravity/qihao1226/AIStudio/scripts/colab_minimax_h3_worker.py) 驱动。

### 第 3 步：音频母带混音与 4 层 OpenFilm 工业总装
```bash
# 3.1 人声与 BGM 混音，锁定 -14.0 LUFS
audio_bgm_mixer \
  --voice ./work/colab_job/generated_tts.wav \
  --bgm ./03_素材/cinematic_pulse_bgm.mp3 \
  --output ./03_素材/mixed_audio_lufs14.wav \
  --lufs -14.0

# 3.2 编译 16:9 横屏主片与 9:16 竖屏成片
to_timeline generic ./02_剪辑决策/shots_decision.json \
  -o ./work/timeline.json \
  --film ./work/openfilm_remix \
  --width 1920 --height 1080 --cover

edl2film ./work/timeline.json -o ./work/openfilm_remix --width 1920 --height 1080 --force
cd ./work/openfilm_remix && openfilm look 1-12
openfilm render -o ./交付成片/final_remix_16x9.mp4
openfilm export fcpxml -o ./交付成片/remix_project.fcpxml
```

### 第 4 步：三重客观机器门禁终审
```bash
# 4.1 Colab 资产规格核验（1080p PNG + 24kHz PCM WAV）
python3 /home/antigravity/qihao1226/AIStudio/scripts/sop04_colab_orchestrator.py --job-dir ./work/colab_job --verify-only > ./08_判据/colab_asset_report.json

# 4.2 镜头运动率与成片广播级终审
motion_check ./交付成片/final_remix_16x9.mp4 --top 0.8 --json > ./08_判据/motion_check_report.json
film_gatekeeper --video ./交付成片/final_remix_16x9.mp4 --lufs -14.0 --tolerance 1.0 --json > ./08_判据/gatekeeper_report.json
wallstreet-strip ./交付成片/final_remix_16x9.mp4 0.0 60.0 12 ./08_判据/final_contact_sheet.jpg 4 --w 480
```

---

## 三、Google Drive 自包含交付标准（v3.0 强制规约）

所有产物归档至 `1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/04_全源素材重构/{YYYYMMDD}_{项目名}_v3/`：

```text
{YYYYMMDD}_{项目名}_v3/
├── 00_需求界定/
│   ├── visual_prompts.json          # 分镜生图提示词工单
│   └── tts_script.json              # 配音台词工单
├── 01_文案与逐字稿/
│   ├── word_timestamps.json         # faster-whisper 毫秒级逐词时间戳
│   └── 文案精修版.md
├── 02_剪辑决策/
│   ├── shots_decision.json
│   └── timeline.json
├── 03_素材/
│   ├── generated_plates/            # Colab 生成的 1920x1080 无损分镜底图
│   ├── generated_tts.wav            # 24kHz PCM WAV + 30ms afade 纯净人声
│   └── mixed_audio_lufs14.wav       # -14 LUFS 混音母带
├── 08_判据/
│   ├── colab_asset_report.json      # Colab 算力产物 100% 齐套合格单
│   ├── motion_check_report.json     # 4层视觉景深运动率合格单
│   ├── final_contact_sheet.jpg      # 12 帧抽样联系表
│   └── gatekeeper_report.json       # 工业级终审绿单
└── 交付成片/
    ├── final_remix_16x9.mp4         # 1920x1080 横屏四层合成主片
    ├── final_remix_9x16.mp4         # 1080x1920 智能重构竖屏成片
    ├── remix_project.fcpxml         # FCPX / 达芬奇工程交割单
    └── 封面_16x9.jpg
```
