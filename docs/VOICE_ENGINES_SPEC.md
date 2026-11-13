# YOUAI 工业级语音合成与母带音频架构规范 (v3.5)
`YOUAI Voice & Audio Production Fleet Specification`

## 一、 顶层选型理念与四阶军火库

在 YOUAI 云端视频生产流水线中，旁白解说与音效对齐是决定成片工业质感与沉浸感的核心。为了平衡 **生成速度、算力开销（Compute Units）、中文专有名词/多音字准确度、情绪表现力与母带音质**，工厂构建了互为补充的“黄金四阶”音频军火库：

| 生产阶梯 | 核心模型 | 模型基座与架构 | 核心能力与专长 | 采样率与母带标准 | 单任务算力成本 (CU) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1 极致低耗解说** | `Kokoro-82M` | 82M StyleTTS2 + ISTFTNet | 极速秒级出片、8 款精调普通话男女声、流式播客 | 24kHz -> -14.0 LUFS 44.1kHz | ~0.001 CU / 视频 |
| **Tier 2 工业级精度播音** | `IndexTTS-2.5` | Bilibili 0.8B GPT + CFM + BigVGAN | **多音字拼音强控**、**毫秒停顿注入**、**音色与情绪解耦** | 24kHz -> -14.0 LUFS 44.1kHz | ~0.008 CU / 视频 |
| **Tier 3 广播级母带造声** | `VoxCPM2` | OpenBMB 2B Tokenizer-Free (MiniCPM-4) | **原生 48kHz 母带**、**Prompt 文本描述直接造声** | **原生 48kHz** -14.0 LUFS | ~0.015 CU / 视频 |
| **Tier 4 极速声音复刻** | `F5-TTS` | 388M Flow Matching Non-AR | 3~10秒音频零样本克隆、拒绝吃字复读 | 24kHz -> -14.0 LUFS 44.1kHz | ~0.006 CU / 视频 |
| **ASR 词级打点** | `Faster-Whisper-Turbo` | CTranslate2 float16 4-Layer Decoder | 毫秒级逐词时间戳提取 (`.words.json`) | 对齐 16kHz Float32 | 极速 (~0.002 CU) |

---

## 二、 核心模型详解与调用规范

### 1. Tier 2: Bilibili `IndexTTS-2.5`（专有名词纠错与情绪解耦）

#### 为什么工业流水线需要 IndexTTS-2.5？
在技术讲解、商业研报和架构演示中，传统 TTS 极易读错中文多音字（如将“重(chong)构”读成“重(zhong)量”，将“行(xing)业”读成“行(hang)列”）。IndexTTS-2.5 通过字音混合建模彻底解决了这一痛点。

#### 语法规则
1. **多音字拼音指定**：使用 `{汉字|拼音+声调}` 或全大写拼音：
   ```text
   我们必须对底层调度器进行{重|chong2}构，才能彻底杜绝并发死锁。
   ```
2. **毫秒级精准停顿注入**：使用 `[pause:Xs]` 显式指定呼吸停顿点：
   ```text
   算力即生产力。[pause:0.5s]每一帧，都是工业级母带。
   ```
3. **音色与情绪分离（Disentanglement）**：
   - 音色参考 (`--ref-audio`)：决定由“谁”来说。
   - 情绪参考 (`--emo-audio` 或 `--emo-text`)：决定“以何种语气”来说（如 `--emo-text "激昂振奋、从容沉稳"`）。

#### CLI 调用指令
```bash
# 专用 CLI
colab_index_tts \
  --text "必须对架构进行{重|chong2}构，[pause:0.4s]才能实现飞跃。" \
  --emo-text "从容沉稳且富有科技感" \
  --with-timestamps \
  --output ./03_素材/indextts_master.wav

# 或通过通用 colab_voice_gen
colab_voice_gen \
  --text "欢迎来到工厂，[pause:0.3s]请核验{行|hang2}业基准。" \
  --engine index-tts \
  --output ./03_素材/narration.wav
```

---

### 2. Tier 3: OpenBMB `VoxCPM2`（原生 48kHz 与 Prompt 声音设计）

#### 为什么工业流水线需要 VoxCPM2？
1. **彻底摆脱“找干净无杂音参考音频”的痛苦**：支持 **Voice Design**，直接用一段自然语言 Prompt 描述人物音色，即可即时凭空生成高保真角色语音。
2. **48kHz 院线母带采样率**：超越普通 TTS 的 24kHz/16kHz 限制，高频泛音与呼吸感极其细腻，达到广播大片母带水准。

#### Voice Design 提示词规范
在 `--voice-design` 中描述：**年龄 + 职业身份 + 音质特征 + 语调风格**：
*   *沉稳的中年男性科技布道师，带有轻微磁性与清晰的吐字节奏*
*   *知性、冷静而干练的女性人工智能研究员，语气克制且具有专业说服力*
*   *富有激情、节奏明快的商业纪录片解说员*

#### CLI 调用指令
```bash
# 专用 CLI（文字描述造声，无需任何参考音频）
colab_voxcpm \
  --text "欢迎收看本期科技深度前沿，我是您的智能向导。" \
  --voice-design "沉稳、富有磁性的35岁科技纪录片男声，吐字清晰从容" \
  --with-timestamps \
  --output ./03_素材/voxcpm_48k.wav

# 高保真 48kHz 声音克隆
colab_voxcpm \
  --text "这是基于高保真母带级克隆出的专属数字音色。" \
  --ref-audio ./03_素材/ceo_voice_5s.wav \
  --output ./03_素材/cloned_48k.wav
```

---

### 3. Tier 1: `Kokoro-82M`（演播室日常主力）

工厂现役 8 款中文精调普通话音色：
- `zm_yunjian`：浑厚、权威纪录片男声（`AG_SOP_01`、`AG_SOP_06` 默认首选）
- `zm_yunxi`：活泼、富有叙事张力男声（`AG_SOP_02`、`AG_SOP_03` 默认首选）
- `zm_yunyang`：严谨的新闻播音员男声
- `zf_xiaoxiao`：温暖、知性的旗舰级播客女声
- `zf_xiaobei`：清脆、精炼的极客科技女声
- `zf_xiaoni`, `zf_xiaoyi`, `zm_yunxia`

---

## 三、 广播级音频母带流水线（Mastering Pipeline）

无论由哪个模型合成的原始音频，都必须强制通过 Colab Worker 内置的 **FFmpeg 母带处理链**：

```
[原始波形] 
   │
   ▼
[30ms 防爆音淡入淡出 (Anti-Pop Fade-In/Out)]
   │
   ▼
[EBU R128 标准响度归一化 (loudnorm=I=-14.0:TP=-1.5:LRA=11)]
   │
   ▼
[重采样与定标: 48kHz (VoxCPM2) / 44.1kHz 16-bit PCM WAV]
   │
   ▼
[Faster-Whisper-Turbo 毫秒逐词时间戳提取 (.words.json)]
```

---

## 四、 算力与存储优化（Drive Model Vault）

1. **自动缓存机制**：
   - `IndexTTS-2.5` 权重自动保存在 Google Drive 永久存储卷：`/content/drive/MyDrive/AIStudio_Models/IndexTTS-2.5/`
   - `VoxCPM2` 与 `Kokoro` 权重保存在：`/content/drive/MyDrive/AIStudio_Models/hf_cache/`
   - 重复开启 Colab 容器时无需重复从外网下载权重，冷启动加载时间由 5 分钟缩短至 15 秒。
2. **算力即时计量**：
   - 每次任务执行前后，`ColabMeter` 自动比对 Colab 算力点数变化，并在终端打印统一结算卡片。
