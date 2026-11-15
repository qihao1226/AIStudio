# Antigravity 云端作战部 · 能力接入与产出物路由 v1.0

> **什么时候读**：任何本地智能体（Hermes / OpenClaw / OpenCode / DSH）或本地产线需要「云端 GPU 多模态生成 / 6 大 SOP 工业视频压制 / 云端代码与流水线构建」时，先读这一份。
> **一句话**：Antigravity 云端作战部（Cloud VM + Colab GPU + Google Drive + GitHub）是我们的**重型工业渲染与云端研发工厂**——只负责“重算力制造与标准化装配”，不负责“选题策划与平台发布”。
> **归属**：横向能力接入（不属任何单条本地产线）
> **维护**：Antigravity Cloud Agent × Hermes 调度矩阵｜**建立**：2026-11-14
> **底层协议手册**：[`AIStudio/docs/02_YOUAI_云端产线能力清单与API规范_v3.5.md`](https://github.com/qihao1226/AIStudio/blob/main/docs/02_YOUAI_%E4%BA%91%E7%AB%AF%E4%BA%A7%E7%BA%BF%E8%83%BD%E5%8A%9B%E6%B8%85%E5%8D%95%E4%B8%8EAPI%E8%A7%84%E8%8C%83_v3.5.md)

---

## 〇、它能干什么 / 不干什么（先看这段，避免误用）

| ✅ 它干 | ❌ 它不干 |
|---|---|
| 调度 Colab L4/A100 跑重度多模态（MiniMax H3 4K/Video、Z-Image、Kokoro、F5-TTS、Whisper） | 不做选题策划、不写深度原创长文、不做商业审美拍板 |
| 在云端 VM 秒级跑通 `SOP 01/02/03/05/06`（零 Colab GPU 消耗）与 OpenFilm 4 层装配 | 不直接向抖音/B站/YouTube 等自媒体平台发布内容 |
| 输出过 `film_gatekeeper` 质检的 1080p 成片、`.fcpxml` 工程与独立分轨物料 | **不碰飞书多维表凭证、不碰本地客户私密业务数据** |
| 在 GitHub (`qihao1226/AIStudio`) 迭代产线脚本、工具链与持久化 Skills | **不是本地总控指挥层**，不反向调度本地智能体 |

> **算力黄金法则**：
> - **能本地秒出，不开 GPU**：`AG_SOP_01`（商业纪实）、`AG_SOP_02`（快闪大字）、`AG_SOP_03`（白板火柴人）、`AG_SOP_05`（口播伴侣）、`AG_SOP_06`（极客架构）默认 **100% 在云端 VM 本地执行**，零 GPU 等待。
> - **重度 AIGC 才上 Colab**：只有 `AG_SOP_04` 及单点 `MiniMax H3 / Z-Image / Kokoro / F5-TTS / Whisper` 任务才唤醒 Colab GPU 集群。

---

## 一、它现在能产出四类东西

| 产物 | 一句话 | 触发通道 | 落盘位置 |
|---|---|---|---|
| **① 工业成片母带** | 可直接预览/发布的 1080p MP4（已过 `film_gatekeeper` 响度与画质门禁） | Drive 网盘流 (`Option B`) | `YOUAI_FACTORY_QUEUE/02_已交付成片_DELIVERED/<PROJECT_ID>/` |
| **② 粗剪工程与分轨包** | 供本机 FCP / Premiere 二次精剪的 `.fcpxml` + 独立音视频分轨 | Drive 网盘流 (`Option B`) | `YOUAI_FACTORY_QUEUE/02_已交付成片_DELIVERED/<PROJECT_ID>/` |
| **③ 多模态单品物料** | 4K 原画、音画一体镜头、母带旁白 + `.words.json` 毫秒字戳 | Drive 网盘流 / 即时指令 | `YOUAI_FACTORY_QUEUE/02_已交付成片_DELIVERED/<PROJECT_ID>/assets/` |
| **④ 产线代码与技能** | 新 SOP 脚本、OpenFilm 补丁、Colab RPC 封装、Skill 沉淀 | GitHub 仓库流 / 对话指令 | GitHub `qihao1226/AIStudio` + `/shared/user/.gemini/` |

---

## 二、产物规格（下游按这个取用）

### 2.0 交付验收四件套（2026-11-14 起，视频产线缺一不收）

| 交付物 | 要求 | 为什么必须有 |
|---|---|---|
| **`final_master_1080p.mp4`** | 过 `film_gatekeeper` 门禁 | 保证画面编码、音画同步与响度达标，开箱即可发布或审片 |
| **`final_master.fcpxml`** | 含完整轨道与素材相对路径 | 方便本机导演室在 Final Cut Pro / PR 中微调字幕、替换镜头 |
| **`delivery_report.md`** | 含使用模型、耗时、LUFS 实测、异常降级说明 | 避免“假 DONE”，让本地调度层一眼确认交付质量 |
| **`assets/` 分轨目录** | 独立保留 4K 图 / 旁白 WAV / `.words.json` / 片段 MP4 | 下游“一鱼多吃”（图文/切片/二创）直接复用原子物料 |

*(注：若派单类型为「纯单品物料生成」，则交付 `assets/` + `delivery_report.md`，免除 `.fcpxml`。)*

### 2.1 目录格式硬规则

**严禁将交付物打成 zip / rar / 7z。** 下游按目录取文件，压缩包会导致 Drive 无法在线预览并增加本地解压步骤。

```text
<PROJECT_ID>/                          ← 顶层就是项目文件夹（如 YOUAI_20261114_TECH_001）
├── production_manifest.yaml           ← 原始派单契约（留档溯源）
├── final_master_1080p.mp4             ← 最终母带成片（单品任务可无）
├── final_master.fcpxml                ← FCPXML 剪辑工程（单品任务可无）
├── delivery_report.md                 ← 交付质量分析报告（必填）
└── assets/                            ← 原子物料分轨目录
    ├── images/                        ← 4K / 1080p 原画 (.png)
    ├── audio/                         ← 旁白 (.wav) + 字戳 (.words.json) + 混音
    └── video/                         ← 独立镜头片段 (.mp4)
```

### 2.2 技术规格

| 类型 | 规格 | 备注 |
|---|---|---|
| 交付视频 | **H.264 + AAC + `faststart`**，1080p 封顶 | **严禁 AV1/VP9**（会导致 Drive 在线预览只有声音没画面） |
| 语音旁白 | 44.1kHz / 24-bit（Kokoro）或 24kHz（F5-TTS），**`-14.0 LUFS`** | 必须伴生 `<name>.words.json` 毫秒字戳 |
| 成片混音 | 48kHz 立体声，**`-16.0 LUFS`**（`audio_bgm_mixer` Auto-Ducking -18dB） | 杜绝 BGM 盖过人声 |
| 关键帧原画 | `3840×2160`（MiniMax H3 4K）或 `1920×1080`（Z-Image-Turbo）PNG | 中英文字排版海报优先用 `z-image-turbo` |
| 白板讲解 | 矢量 SVG 渐进笔触，**严格 `3.14 字/秒` 语速物理对齐** | `AG_SOP_03` 强制校验，超速即判失败 |

---

## 三、怎么调用它（双通道唯一入口）

**本地产线不能跳过契约直接口头糊弄，规则必须写进 Manifest 或 Issue。**

- **通道 A（内容生产 · Google Drive 网盘流 Option B）**：
  > **本地导演室（Hermes / OpenClaw）组装 `production_manifest.yaml` → 放入 Drive `00_待生产队列_QUEUE/<PROJECT_ID>/` → 通知/触发 Antigravity → 原子移入 `01_生产中_PROCESSING/` → 交付至 `02_已交付成片_DELIVERED/`**
- **通道 B（能力研发 · GitHub 仓库流）**：
  > **本地/云端提交需求 → Antigravity 在 `qihao1226/AIStudio` 开发并过测 → 同步更新本路由表与 `v3.5` 规范 → 推送 GitHub**

### 3.1 派单格式（直接照抄）

> 完整 YAML Schema 与 6 段式 Prompt 规则见 [`02_YOUAI_云端产线能力清单与API规范_v3.5.md`](https://github.com/qihao1226/AIStudio/blob/main/docs/02_YOUAI_%E4%BA%91%E7%AB%AF%E4%BA%A7%E7%BA%BF%E8%83%BD%E5%8A%9B%E6%B8%85%E5%8D%95%E4%B8%8EAPI%E8%A7%84%E8%8C%83_v3.5.md)。
> **规则只有写进 `production_manifest.yaml` 才算数**——本机未确认的隐含要求云端不会脑补。

```text
需求类型：SOP成片生产（SOP 01~06） / 多模态单品物料 / 产线代码研发
项目ID：YOUAI_YYYYMMDD_<SERIES>_<NNN>
指定产线：AG_SOP_01 ~ AG_SOP_06（或单品引擎：minimax-h3-image / z-image-turbo / kokoro / f5-tts / minimax-h3-video）
输入源：
  - production_manifest.yaml（已校验模型名、分辨率、with_timestamps: true）
  - custom_assets/（可选：参考图最多16张、声音克隆3-10s参考WAV+原文字）
验收标准（缺一不收）：
  - 成片过 film_gatekeeper（-14/-16 LUFS，H.264 faststart）
  - 输出 final_master.fcpxml + delivery_report.md + assets/ 分轨
交付路径：YOUAI_FACTORY_QUEUE/02_已交付成片_DELIVERED/<PROJECT_ID>/
```

### 3.2 典型耗时与算力成本（实测参考）

| 任务类型 | 算力底座 | 典型耗时 | 备注 |
|---|---|---|---|
| `SOP 01/02/03/05/06`（全流程装配） | 云端 VM 本地（零 GPU） | **30 秒 – 3 分钟** | 秒级响应，不占 Colab 配额 |
| `Z-Image-Turbo` / `FLUX` 单张出图 | Colab L4 / A100 | **~2.5 – 3.0 秒/张** | 含冷启动首次加载约 1-2 分钟 |
| `MiniMax-H3-Image` 原生 4K 出图 | Colab A100 (80GB) | **~10 – 20 秒/张** | 支持 1-16 张参考图一致性编辑 |
| `MiniMax-H3-Video` 5秒音画同步 | Colab A100 (80GB) | **~1 – 3 分钟/段** | 含 32kHz 立体声与口型同步 |
| `Kokoro` / `F5-TTS` + `Whisper` | Colab L4 / 云端 | **~5 – 20 秒/段** | 自动输出 `.words.json` |

---

## 四、哪条本地产线可以吃哪类产物

| 本地产线 / 场景 | 能吃的云端产物 | 用法 |
|---|---|---|
| **商业深度纪实 / 人物传记** | `AG_SOP_01` 成片 + `Stage25D` 镜头 | 直接出片，或取 `.fcpxml` 与 GrokBot 人物素材包混剪 |
| **极速快闪 / 短视频爆款** | `AG_SOP_02` 成片 + `Kokoro` 字戳 | 基于 Whisper 毫秒字戳与鼓点自动卡点成片 |
| **知识科普 / 商业拆解** | `AG_SOP_03` 白板手绘 + `AG_SOP_06` 极客架构 | SVG 矢量笔触讲解 + 单聚光灯架构动效 |
| **AI 短剧 / 高拟真广告片** | `AG_SOP_04` + `MiniMax H3 4K/Video` | 4K 跨镜头一致原画 + 台词口型音画一体镜头 |
| **真人 IP 口播后期** | `AG_SOP_05` 口播伴侣 + `F5-TTS` | 本机拍口播原片上传 `custom_assets/`，云端自动人脸避障加画中画动效 |
| **图文 / PPT / 封面一鱼多吃** | `z-image-turbo` / `minimax-h3-image` | 4K 封面原画 + 中英双语无乱码排版海报 |

---

## 五、红线（违反即判失败）

1. **禁止未过 Schema 校验直接唤醒 Colab GPU**：Manifest 语法或模型名错误，必须直接熔断移入 `03_异常中断_FAILED/`，严禁空烧 A100 额度。
2. **禁止在云端存放飞书凭证或本机私密业务数据**（如颐万家护、美节拍客户身份证/病历/合同金额等）。
3. **禁止交付压缩包**（zip/rar/7z）或 **AV1/VP9 编码视频**。
4. **禁止跳过 `film_gatekeeper` 门禁直接宣称交付**：响度不达标、音画不同步、缺 `delivery_report.md` 一律判失败。
5. **禁止引用未在本路由表登记的实验性模型或参数**。

---

## 六、已知失败模式（下游排期前必看）

| 失败模式 | 现象 | 对策 |
|---|---|---|
| **Manifest 格式报错** | 云端拒单并退回 `03_异常中断_FAILED/` | 本地 Agent 派单前必须跑完 `v3.5` Linter 4 项自检 |
| **Colab 冷启动 / RPC 断连** | 单次请求超时或内核重置 | Pure-HTTP RPC 内置 3 次指数退避重试；已完成单品物料留在 Drive 断点续跑 |
| **Drive 视频只有声音没画面** | 编码为 AV1 或 VP9 | 强制 OpenFilm / FFmpeg 压制为 `H.264 + AAC + faststart` |
| **SOP 02 快闪字幕不同步** | 大字与旁白对不上 | `Kokoro / F5-TTS` 任务必须显式开启 `with_timestamps: true` 生成 `.words.json` |
| **SOP 03 白板画面超前/滞后** | 笔触画完人还在说，或没画完就切镜 | 严格遵守 `3.14 字/秒` 物理对齐规则，文案超长需拆分镜头 |
| **BGM 压过人声** | 旁白听不清 | 必须走 `audio_bgm_mixer`（`-18dB` Auto-Ducking + `-16 LUFS` 归一化） |
| **A100 显存 OOM** | 4K + 多参考图并发超限 | 云端自动降级分辨率至 1080p 重试，并在 `delivery_report.md` 中告警 |

---

## 七、能力全景与扩展登记（SSOT）

| 能力模块 | 当前状态 | 对应文档 / 载体 |
|---|---|---|
| `AG_SOP_01 ~ 06` 六大产线 | ✅ 已全部工业化 | `AIStudio/docs/sops/AG_SOP_01~06_v3.0.md` |
| `OpenFilm` 4 层装配 + `film_gatekeeper` | ✅ 已持久化到云端底座 | `to_timeline → edl2film → openfilm → film_gatekeeper` |
| `MiniMax H3-Image` (4K / 16图参考) | ✅ 已接入 Colab A100 | `AIStudio/docs/MINIMAX_H3_IMAGE_SPEC.md` |
| `MiniMax H3-Video` (音画同步 / 口型) | ✅ 已接入 Colab A100 | `minimax-h3-colab` Skill |
| `Z-Image-Turbo` / `FLUX.1-schnell` | ✅ 已接入 Colab L4/A100 | `colab-multimodal-suite` Skill |
| `Kokoro-82M` / `F5-TTS` / `Whisper-Turbo` | ✅ 已接入 | `AIStudio/docs/VOICE_ENGINES_SPEC.md` |
| Drive `YOUAI_FACTORY_QUEUE` 状态机 | ✅ 目录已就位 | 见文末硬规则 |
| `IndexTTS-2.5` / `VoxCPM2` 48kHz | 🚧 灰度可用，待写入 v3.5 Manifest 枚举 | `colab-multimodal-suite` Skill |

**扩展原则**：云端新增任何模型、SOP 或 CLI 工具，**一律先在本路由表登记，再同步更新 `v3.5` 规范与本地 Agent Prompt**。未登记的能力，不应被本地产线引用。

---

## 八、维护

- **交付物异常 / 退单排查**：查看 `03_异常中断_FAILED/<PROJECT_ID>/error_diagnostic.log`，附 `PROJECT_ID` 与 Drive 链接反馈给 Antigravity。
- **新增能力或调整规格**：先在 GitHub `qihao1226/AIStudio` 更新本路由表与底层规范，再同步至 Google Drive `整合工作流程/`。
- **本文档版本**：v1.0（2026-11-14）。首次建立 Antigravity 云端作战部能力接入与产出物路由契约，对齐 GrokBot 外部作战部路由规范。

---

## 硬规则 · Google Drive 队列与目录拓扑

**禁止在 `YOUAI_FACTORY_QUEUE` 根目录下平铺项目文件夹。** 必须严格按四态队列流转：

```text
Google Drive 根/
└── YOUAI_FACTORY_QUEUE/
    ├── 00_待生产队列_QUEUE/         ← 【本地投递】放入 <PROJECT_ID>/ (含 production_manifest.yaml)
    ├── 01_生产中_PROCESSING/       ← 【云端锁定】Antigravity 原子移入并回写 progress.log
    ├── 02_已交付成片_DELIVERED/     ← 【云端交付】输出成片、.fcpxml、delivery_report.md 与 assets/
    └── 03_异常中断_FAILED/         ← 【异常熔断】保留已生成物料 + error_diagnostic.log
```
