# AG_SOP_02 · 极速快闪大字动效视频生产流水线 SOP (v3.0 极致执行手册版)

> **版本**：v3.0 (StaticGuard 零冲突铁律 + 毫秒级低音鼓点锁死 + 4层极速压制版) ｜ **更新日期**：2026-11-08  
> **战队编制**：战队 1「极速快闪动效队」 ｜ **表现形态**：形态 3「动态大字快闪金句」(Kinetic Typography)  
> **核心定位**：**字即画面，节拍即生命。面向小红书/抖音/视频号/Reels 的 15s~45s 高燃抓眼球短视频爆款。零真人出镜，纯靠 120px~180px 超重型排版大字、1~2 帧白光频闪转场与重低音鼓点毫秒级共振震撼出片。**  
> **GitHub 归档路径**：[`docs/sops/AG_SOP_02_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_02_v3.0.md)  
> **Google Drive 知识库路径**：`1YJqjW_FDdyY0iZsFeOSr1x_RK-F1_FFd/AG_SOP_02_极速快闪大字动效生产流水线 SOP v1.0.md`  
> **Google Drive 交付路径**：`1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/02_极速快闪动效/`

---

## 〇、强制前置铁律（Step 0：跨会话永久底座一键唤醒）

在启动任何快闪视频生产前，**必须首先执行以下两行底座唤醒指令**：

```bash
/home/antigravity/qihao1226/AIStudio/scripts/bootstrap.sh
export PATH="/home/antigravity/.local/bin:/shared/user/.gemini/youai/bin:$PATH"
```

> **【红线避坑：算力解耦原则 + StaticGuard CSS Transform 与 GSAP 零冲突铁律】**
> 0. **【算力边界】本产线（SOP 02）是纯代码级排版与音频脉冲驱动的极速产线，100% 在 Antigravity 本地闭环完成，严禁调用 Colab GPU！**
> 1. 所有屏幕居中必须使用 **Flexbox / Grid 容器居中**（`display: flex; align-items: center; justify-content: center;`），**严禁使用 `left: 50%; transform: translateX(-50%)` 居中**！
> 2. 所有位移、缩放、微震必须 100% 通过时间函数 `frame(t)` 或 GSAP 独立属性控制。

---

## 一、七大快闪视觉与节拍铁律（机器门禁硬指标）

| # | 决策维度 | 核心规范与物理量化标准 | 机器拦截红线 |
| :---: | :--- | :--- | :--- |
| **1** | **字即核心视觉（文字膨胀率）** | 每一屏主题大字占据画面核心区的 **65%~80%**。竖屏（1080×1920）主字号下限 **120px ~ 180px**，辅助角标 $\ge 28\text{px}$。 | 主字号 $< 100\text{px}$ 或画面空旷直接拦截。 |
| **2** | **毫秒级卡点契约（Beat Sync）** | 字卡入场首帧必须与 `beat_detector` 提取的 Kick/Downbeat 鼓点**毫秒级锁死（误差 $|\Delta t| \le 0.05\text{s}$）**。 | 偏离鼓点 $>0.05\text{s}$ 直接判定节奏失衡。 |
| **3** | **短促句式切分（4~9 字/屏）** | 单屏仅传递 1 个核心冲击意象，字数严格控制在 **4~9 个汉字**（绝对上限 12 字），行数 $\le 2$ 行。 | 单屏 $>12$ 字或出现单字孤行直接拦截。 |
| **4** | **白光频闪过冲（White Flash Bloom）** | 关键结论揭晓或强重音落点前 1~2 帧（16ms~33ms）施加纯白曝光过冲（Opacity $0.85 \to 0.0$），瞬间砸入高反差大字。 | 使用温吞平淡的慢速淡入淡出。 |
| **5** | **WCAG AAA 极高反差配色** | 严格执行纯黑底（`#050507`）配荧光黄（`#FFDE00`）、激光绿（`#00FF66`）、电光紫（`#8B5CF6`）或纯白（`#FFFFFF`），对比度 $\ge 7:1$。 | 使用低对比度灰字或莫兰迪暗淡色。 |
| **6** | **重力砸落与弹性阻尼（Drop & Shake）** | 字卡进场采用过冲缩放（Scale $2.2 \to 0.96 \to 1.00$，时长 $0.14\text{s}$）配合屏幕径向微震（$\pm 6\text{px}$）。 | 匀速生硬平移或长时间静止不动。 |
| **7** | **高燃紧凑语速（4.0~4.5 字/秒）** | 配音语速锁定在 **4.0 ~ 4.5 字/秒**，句间停顿切除至 $\le 0.15\text{s}$，综合响度锁死在 **`-14.0 LUFS`**（短视频平台高能标准）。 | 语速拖沓 $<3.5$ 字/秒或留有长空白。 |

---

## 二、HyperFrames 黄金模板族选型表

| 模板编号 | 模板名称 | 适用分镜节拍 | 视觉与物理动效特征 |
| :--- | :--- | :--- | :--- |
| **`T1_minimal_bold`** | 极简黑白巨字冲击 | 黄金前 3 秒反常识 Hook、打脸常识 | `#050507` 黑底 + `168px` 纯白/荧光黄巨字 + 2帧白光频闪 + 落地微震 |
| **`T2_kinetic_slice`** | 动能斜切与错位排比 | 连续三连问、数据密集扫射 | `-6deg` 动能斜切色带 + 上下交错滑入 + 字距动态收紧 |
| **`T3_neon_pulse`** | 赛博霓虹脉冲 | AI/算力/科技未来感高潮金句 | `#00FF66` 激光绿双层外发光 + 底部动态音频频谱 |
| **`T4_stomp_punch`** | 逐词重锤定格 | 结尾核心金句、强力 CTA 行动号召 | 随鼓点逐词连珠炮砸入 + 末词全屏反色定格 |

---

## 三、四步极速出片标准工序与精确 CLI 指令手册

### 第 1 步：BGM 低音鼓点毫秒级提取 (`beat_detector`)
```bash
# 提取 150Hz 以下底鼓 (Kick) 能量包络峰值，生成毫秒级鼓点序列 beats.json
beat_detector \
  --input ./03_素材/cyberpunk_beat.mp3 \
  --output ./08_判据/beats.json \
  --sensitivity 0.58 \
  --min-interval 0.45
```

### 第 2 步：高燃配音合成与 `-14.0 LUFS` 母带混音 (`audio_bgm_mixer`)
```bash
# 合成紧凑配音并与高燃卡点 BGM 混音，锁定短视频高能响度 -14.0 LUFS
audio_bgm_mixer \
  --voice ./03_素材/fast_voice.wav \
  --bgm ./03_素材/cyberpunk_beat.mp3 \
  --output ./03_素材/mixed_audio_lufs14.wav \
  --bgm-vol 0.22 \
  --lufs -14.0
```

### 第 3 步：鼓点吸附编排与 4 层流水线编译 (`to_timeline` ➔ `edl2film` ➔ `openfilm`)
- 将切分好的 4~9 字金句序列自动吸附至 `beats.json` 中最近的鼓点时间戳（确保 $|\text{start} - \text{beat}| = 0.000\text{s} \le 0.05\text{s}$），写入 `./02_导演表/flash_beats.json`。

```bash
# 编译为 1080x1920 竖屏 OpenFilm 工程并生成 12 帧接触表
to_timeline generic ./02_导演表/flash_beats.json \
  -o ./work/timeline.json \
  --film ./work/openfilm_project \
  --width 1080 --height 1920 --cover

edl2film ./work/timeline.json -o ./work/openfilm_project --width 1080 --height 1920 --force
cd ./work/openfilm_project && openfilm look 1-12
openfilm render -o ./交付成片/final_flash_1080x1920.mp4
```

### 第 4 步：双重机器门禁校验（鼓点对齐 + 成片验收）
```bash
# 4.1 毫秒级鼓点对齐门禁（断言所有镜头与鼓点误差 <= 0.05s）
python3 - <<'PY'
import json
beats = json.load(open("./08_判据/beats.json"))["beats"]
shots = json.load(open("./02_导演表/flash_beats.json"))["shots"]
report = {"passed": True, "max_drift_s": 0.0, "details": []}
for idx, s in enumerate(shots):
    t = float(s["start"])
    closest = min(beats, key=lambda b: abs(b - t))
    drift = round(abs(closest - t), 4)
    ok = drift <= 0.05
    report["max_drift_s"] = max(report["max_drift_s"], drift)
    report["details"].append({"shot": idx + 1, "start": t, "beat": closest, "drift_s": drift, "passed": ok})
    if not ok:
        report["passed"] = False
json.dump(report, open("./08_判据/beat_alignment_report.json", "w"), indent=2, ensure_ascii=False)
assert report["passed"], f"Beat alignment failed! Max drift: {report['max_drift_s']}s"
print("[beat_alignment] PASS | max_drift =", report["max_drift_s"], "s")
PY

# 4.2 工业级终审门禁（1080x1920 / -14.0 LUFS / 0黑帧）
film_gatekeeper --video ./交付成片/final_flash_1080x1920.mp4 --target-w 1080 --target-h 1920 --lufs -14.0 --tolerance 1.0 --json > ./08_判据/gatekeeper_report.json
wallstreet-strip ./交付成片/final_flash_1080x1920.mp4 0.0 30.0 12 ./08_判据/final_contact_sheet.jpg 4 --w 360
```

---

## 四、Google Drive 自包含交付标准（v3.0 强制规约）

所有产物归档至 `1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/02_极速快闪动效/{YYYYMMDD}_{项目名}_v3/`：

```text
{YYYYMMDD}_{项目名}_v3/
├── 00_需求界定/
│   └── 爆款金句选型单.json
├── 01_文案/
│   └── 快闪切词脚本.md               # 严格 4~9 字/屏切分脚本
├── 02_导演表/
│   └── flash_beats.json             # 与鼓点 0.00s 锁死的导演时间线
├── 03_素材/
│   ├── cyberpunk_beat.mp3           # 重低音 BGM
│   └── mixed_audio_lufs14.wav       # -14 LUFS 高能混音母带
├── 08_判据/
│   ├── beats.json                   # beat_detector 鼓点时间戳
│   ├── beat_alignment_report.json   # 鼓点误差 <= 0.05s 绿单
│   ├── final_contact_sheet.jpg      # 12 帧快闪字卡抽样联系表
│   └── gatekeeper_report.json       # 1080x1920 / -14 LUFS 终审绿单
└── 交付成片/
    ├── final_flash_1080x1920.mp4    # 竖屏高燃快闪成片
    └── 封面_3x4.jpg                  # 小红书/抖音高点击巨字封面
```
