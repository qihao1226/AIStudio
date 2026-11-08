# YOUAI 07 商业与科技 BGM 爆款智库与自动化调度规约 (v3.0)

> **发布版本**：v3.0 (工业级自包含母带 + 纯净人声避让 + 模式 B 骨架神经重构版)  
> **归属路径**：Google Drive `云端系统配置/04_通用资产与模板库/07_商业与科技BGM爆款智库/` (ID: `1oKdwqdM3MQ0u4jxHEhzh9R5GX9yQgHn0`)  
> **本地热盘**：`/shared/user/.gemini/youai/assets/bgm/`  
> **核心调度工具**：[`bin/bgm_picker`](file:///home/antigravity/qihao1226/AIStudio/bin/bgm_picker) ｜ [`bin/audio_bgm_mixer`](file:///home/antigravity/qihao1226/AIStudio/bin/audio_bgm_mixer) ｜ [`scripts/colab_bgm_worker.py`](file:///home/antigravity/qihao1226/AIStudio/scripts/colab_bgm_worker.py)

---

## 一、 顶层定位与五大风格图谱

面向**“商业、AI、科技、知识”**核心内容产线，所有曲目严格遵循**“低频饱满、中频人声避让（800Hz~3kHz -3.5dB）、零高频电子尖叫（>2.4kHz 低通滤波）、-16.0 LUFS 响度标准化”**的工业规范：

| 目录编号 | 风格矩阵代号 | 听觉基因与乐器特征 | 对应视频产线 | BPM 区间 | 默认能级 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`01_tech_pulse`** | **科技深沉与未来律动** | 模拟合成器脉冲（Moog/ARP）、Sub-bass 下潜、极简科技节拍 | `AG_SOP_06` 极客、`AG_SOP_04` 重构 | 100~125 | ★★★ |
| **`02_commercial_depth`** | **商业深度与资本博弈** | 现代电影大提琴/钢琴、微暗调性弦乐、冷峻悬疑递进 | `AG_SOP_01` 商业纪实、`AG_SOP_04` | 75~95 | ★★ |
| **`03_knowledge_flow`** | **知识心流与理性极简** | Rhodes 暖色电钢琴、毛毡原声钢琴、白噪声轻拟音、Lo-Fi 质感 | `AG_SOP_03` 白板、`AG_SOP_05` 口播伴侣 | 80~105 | ★ |
| **`04_kinetic_punch`** | **快闪破局与能量冲击** | 重低音 Drop、硬核打击乐短击、断奏跳跃、极速刹车转场 | `AG_SOP_02` 极速快闪、`AG_SOP_04` | 120~138 | ★★★★★ |
| **`05_epic_breakthrough`** | **科技史诗与产业破局** | 混合管弦乐（Hybrid Orchestral）、Riser 蓄力攀升、浩瀚铜管 | 全 SOP 总结升华、行业里程碑结论 | 90~120 | ★★★★ |

---

## 二、 模式 B：爆款骨架引导生产（Mode B SOP）

为了确保 BGM 既具备互联网已验证的“爆款留存节奏”，又拥有 100% 独家版权与纯净音质，采用三步闭环生产法：

```text
[ 爆款视频音频切片 15s~30s (00_raw_seeds/) ]
                     │
                     ▼
[ 步骤 1：分轨分离 (Demucs) 提取 Drums 律动与 Bassline 骨架 ]
                     │
                     ▼
[ 步骤 2：Colab 神经重构 (MusicGen-Melody) 注入 5 大风格 Prompt 矩阵 ]
                     │
                     ▼
[ 步骤 3：工业母带与避让链 (colab_bgm_worker.py) ]
   ├── 中声场 800Hz-3kHz 动态衰减 -3.5dB (留出人声解说黄金通道)
   ├── 2400Hz 低通抗尖锐滤波 (彻底根除“滴滴滴”合成杂音)
   └── EBU R128 -16.0 LUFS 响度对齐与无缝循环点提取
                     │
                     ▼
[ 步骤 4：自动打标入库，同步上传至 Drive 07 库与本地热盘 ]
```

### 批量生产命令模板：
```bash
# 1. 本地快速生成/测试：
python3 /home/antigravity/qihao1226/AIStudio/scripts/colab_bgm_worker.py \
  --mode mode_b \
  --seed /shared/user/.gemini/youai/assets/bgm/00_raw_seeds/viral_hook_01.wav \
  --category 01_tech_pulse \
  --out-dir /shared/user/.gemini/youai/assets/bgm \
  --duration 45

# 2. 调度远程 Colab GPU (L4/A100) 执行大批次生产：
colab exec -s sop04-gpu -c "python3 /content/colab_bgm_worker.py --mode mode_b --category all --out-dir /content/bgm_out"
```

---

## 三、 全局元数据协议 (`bgm_manifest.json`)

所有入库曲目必须在 `bgm_manifest.json` 中保持实时索引：

```json
{
  "version": "1.0.0",
  "total_tracks": 5,
  "updated_at": "2026-11-08T16:15:00Z",
  "tracks": [
    {
      "id": "BGM_01_TECH_PU_115",
      "filename": "tech_neural_pulse_115bpm.wav",
      "category": "01_tech_pulse",
      "title": "Tech Pulse Theme",
      "tags": ["AI", "未来感", "深沉科技", "算力架构", "极客演示"],
      "sop_affinity": ["AG_SOP_06", "AG_SOP_04", "AG_SOP_01"],
      "duration_sec": 32.0,
      "bpm": 100.0,
      "energy_level": 3,
      "climax_sec": [16.0],
      "loopable": true,
      "loudness_lufs": -16.0,
      "local_path": "/shared/user/.gemini/youai/assets/bgm/01_tech_pulse/tech_neural_pulse_115bpm.wav",
      "prompt_dna": "futuristic modular synth pulse, warm analog moog bass..."
    }
  ]
}
```

---

## 四、 视频装配流水线中的调用方式

视频生成平台支持**两种调用模式**：

### 模式 1：智能自动匹配（默认推荐）
在调用 [`bin/audio_bgm_mixer`](file:///home/antigravity/qihao1226/AIStudio/bin/audio_bgm_mixer) 时传入 `--auto-bgm`，系统自动通过 `bgm_picker` 挑出最优曲目并自动完成避让人声与混音：
```bash
audio_bgm_mixer \
  --voice ./work/voice.wav \
  --auto-bgm \
  --sop AG_SOP_06 \
  --mood "未来感" \
  -o ./交付成片/mastered_audio.wav
```

### 模式 2：精准检索与手动绑定
在导演表中指定具体曲目 ID 或路径：
```bash
# 查询当前库中符合 AG_SOP_01 商业纪实的曲目路径
BGM_FILE=$(bgm_picker pick --sop AG_SOP_01 --mood "商业" -p)

# 送入母带合成
audio_bgm_mixer --voice ./work/voice.wav --bgm "$BGM_FILE" -o ./work/out.wav
```

---

## 五、 增量迭代与飞轮维护

1. **爆款种子采集**：将互联网热门科技/商业短视频的 15~30s 伴奏片段存入 `00_raw_seeds/`。
2. **批处理生成**：定期启动 Colab 任务批量衍生 10~20 首新曲。
3. **一键同步**：使用 `bgm_picker sync` 将 Google Drive 新增的资产拉取至本地热盘。
