# 🎬 AIStudio: 云端多模态视频生产工场

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1AIQX-pm291MjNLdZ2ravKVPxFIBo_KYA)
[![GitHub License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![SOP Version](https://img.shields.io/badge/SOP-AG__SOP__04%20v1.0-green.svg)](docs/AG_SOP_04_全源素材重构与外挂多模态视频生产流水线SOP_v1.0.md)

> 基于 **Antigravity (云端智能中枢)** + **Google Colab (外挂多模态 GPU 车间)** + **Google Drive (统一物理总装货架)** 打造的全源素材重构与视频生产流水线。

---

## 🌟 核心理念与架构

打破特定类型视频的狭窄局限，面向全品类（科技解说、商业拆解、卡点短视频、知识科普）：
1. **双源素材汇流**：支持用户在 Google Drive 上传的原生素材（文档/录音/原片）与 Antigravity 全网自主嗅探搜集的高清素材；
2. **差额按需制造**：基于分镜导演表自动分析缺失元素，生成《差额生产清单》（`gap_manifest.json`）；
3. **Colab 外挂 GPU 车间**：
   - 🎙️ 语音转写与字级时间戳：`faster-whisper`
   - 🗣️ 零样本声音克隆与旁白：`F5-TTS` / `CosyVoice`
   - 🎨 概念插图与视频封面：`FLUX.1-schnell` / `SDXL-Turbo`
   - 🎬 专属动态空镜片段：`CogVideoX-2B` / `LTX-Video`
4. **集中总装与代码动效编排**：全源素材齐套入库 `03_assets_hub/` 后，通过 `HyperFrames` / `Remotion` 实现广播级多轨道运镜动效渲染。

---

## 📂 项目标准目录布局 (`AG_SOP_04`)

```text
AIStudio/
├── docs/                                  # 工业级规约与 SOP 文档
│   ├── AG_SOP_04_全源素材重构...SOP_v1.0.md
│   └── templates/gap_manifest_template.json
├── notebooks/                             # 专供 Colab 运行的外挂车间 Notebook
│   └── colab_multimodal_worker.ipynb
├── src/aistudio/                          # Antigravity 调度与流水线工具包
│   ├── config.py                          # 目录与媒体规范
│   ├── inventory.py                       # 原始素材全景扫描器
│   ├── manifest.py                        # 差额生产清单构建与校验器
│   ├── assembler.py                       # assets_hub 集中总装与门禁断言
│   └── cli.py                             # 统一命令行接口
└── tests/                                 # 单元测试与门禁验证
```

---

## 🚀 快速上手 (Quickstart)

### 1. 本地初始化新项目
```bash
PYTHONPATH=src python3 -m aistudio.cli init 20261107_demo
```

### 2. 扫描原始资产 (`01_raw_assets`)
```bash
PYTHONPATH=src python3 -m aistudio.cli scan projects/20261107_demo
```

### 3. 一键启动 Colab 外挂多模态车间
点击上方 [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1AIQX-pm291MjNLdZ2ravKVPxFIBo_KYA) 按钮，挂载 Google Drive 后一键运行，即可自动监听并处理生成的差额清单任务。

### 4. 总装与机器门禁断言
```bash
PYTHONPATH=src python3 -m aistudio.cli assemble projects/20261107_demo
```
