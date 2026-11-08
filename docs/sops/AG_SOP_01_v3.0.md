# AG_SOP_01 · 商业深度纪实与数字可视化视频生产流水线 SOP (v3.0 极致执行手册版)

> **版本**：v3.0 (跨会话永久底座 + 复合模具强制认领 + 4层流水线零报错执行版) ｜ **更新日期**：2026-11-08  
> **产线编号**：P9「真素材 + 数字可视化」 ｜ **战队编制**：战队 4「商业深度纪实队」  
> **核心定位**：**拒绝单引擎从零手搓，严禁 Python PIL 静态画图伪造动效。依托 37 套持久化 Skills 模具进行工业级复合装配，以真实物证链、Stage25D 连续帧视差机位、奥斯卡电影调色与权威金融图表，产出高信任度商业深度大片。**  
> **GitHub 归档路径**：[`docs/sops/AG_SOP_01_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_01_v3.0.md)  
> **Google Drive 知识库路径**：`1YJqjW_FDdyY0iZsFeOSr1x_RK-F1_FFd/AG_SOP_01_真素材数字可视化视频_v2.0_复合装配版.md`  
> **Google Drive 交付路径**：`1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/01_真素材数字可视化/`

---

## 〇、强制前置铁律（Step 0：跨会话永久底座一键唤醒）

在任何新对话窗口启动本 SOP 生产前，**必须首先执行以下两行底座唤醒指令**，将 `/shared/user/.gemini/youai`（1.0 PB 永久盘）中的 37 套 Skills、21 个工业 CLI 工具、中英文字体库与 Colab RPC 补丁挂载到当前环境：

```bash
/home/antigravity/qihao1226/AIStudio/scripts/bootstrap.sh
export PATH="/home/antigravity/.local/bin:/shared/user/.gemini/youai/bin:$PATH"
```

> **【红线禁令：严禁退回 PIL/OpenCV 手搓静态画面】**
> 1. 严禁因未跑 `bootstrap.sh` 找不到命令而临时编写 Python `PIL.ImageDraw` 画简陋色块转 MP4！
> 2. 严禁把静态模板目录（如 `/home/antigravity/skills/Jacky-motion/`）当成 Shell 命令直接执行！
> 3. 每一镜必须在 `frame(t)` 时间函数中声明连续摄像机位移（Drift $\ge 0.02/\text{s}$ 或 Scale $1.00 \to 1.06$），确保 `motion_check` 镜头运动活跃率 $\ge 30\%$。

---

## 一、分镜信息原语与顶级 Skills 模具强制映射表

在编写第 2 站《导演表》时，每一镜的「视觉承担」列必须指明 **Skill 模具血统编号** 与 **物理模板路径**：

| 分镜信息原语 (Primitive) | 典型视觉场景 | **强制认领的 Skill 模具** | 云端物理资产寻址 (`/home/antigravity/skills/`) | 严禁出现的低劣做法 |
| :--- | :--- | :--- | :--- | :--- |
| **Claim (核心观点/开场揭示)** | 4万亿市值、宏观惊人结论、反常识钩子 | **`Jacky-motion L01`**（左轴主导大字）或 **`HyperFrames T1`** | `skills/Jacky-motion/assets/base-template.html`<br>`skills/hyperframes-factory/` | ❌ 居中纯白宋体/黑体大字硬贴 |
| **Data / Metric (走势与数据)** | 市值走势曲线、电网负荷激增、财务增长 | **`Remotion Financial Chart`**（发光路径、渐变面积阴影、跳数计数器） | `skills/remotion-financial-motion/` | ❌ 用 Matplotlib 或 Canvas 画细单线 |
| **Contrast (误区/悬殊对比)** | 传统 7kW 机柜 vs 120kW 液冷机柜 | **`Jacky-motion L03`**（左右非对称对比骨架，内置短语断行） | `skills/Jacky-motion/` (`data-layout="L03"`) | ❌ 两个纯色方框加单字孤行（如“单/柜”） |
| **Evidence (权威文件/研报)** | PJM 电网排队报告、SEC 10-K 原件高亮 | **`Jacky-motion L08`**（证据板）+ **`Stage25D`** 探照灯扫光与荧光笔涂抹 | `skills/wallstreet-explainer/` | ❌ 全屏贴密密麻麻看不清的小字截图 |
| **System (层级/多维架构)** | 五层算力基础设施蛋糕、电网拓扑结构 | **`Jacky-motion L05`**（纵向层级骨架）或 **`HyperFrames T5`** | `skills/Jacky-motion/` (`data-layout="L05"`) | ❌ 几个矩形框加静态直线箭头 |
| **Keynote / Audio (原声对位)** | 黄仁勋/奥特曼演讲切片、现场原声引述 | **`CVF PodcastWaveform`**（动态声纹）+ **`Stage25D demote()`** 背景景深虚化 | `skills/wallstreet-explainer/` | ❌ 静态照片加几根死板长条 |
| **Punchline (交割结算/终局)** | 核电锁定凭证、长期算力交割单、红章砸印 | **`HyperFrames T8`**（防伪凭单）+ 阻尼缩放公章砸印（Drop Stamp） | `skills/hyperframes-factory/` | ❌ 纯文本刷屏加红横条 |

---

## 二、七大工业排版与视觉美学铁律（Gate E 强制检验项）

1. **中文短语断行铁律（零孤字折行）**：中文标题严禁由浏览器自然折行破坏词义；必须显式按短语断行，每行 4~9 个汉字（上限 12 字），CSS 强制声明 `word-break: keep-all; line-break: strict; overflow-wrap: normal;`。
2. **第一眼视觉重心法则（45%–65%）**：画面缩放到 50% 审视时，主视觉证据/核心大字必须占据 45%~65% 视觉权重，辅助结构占 20%~35%，角标与脚注 $\le 15\%$。
3. **1080P 字号阶梯底线（1920×1080）**：
   - Hero 核心大字 / 巨型数字：$\ge 96\text{px}$（纯结论页 $\ge 120\text{px}$）；
   - 副标题 / 核心数据标签：$\ge 32\text{px}$；
   - 正文说明：$\ge 24\text{px}$；
   - 底部来源注脚：$\ge 18\text{px}$（**全片严禁出现 $<18\text{px}$ 的蚂蚁字**）。
4. **奥斯卡电影调色盘绑定（`search_styles`）**：严禁使用 `#ff0000`、`#00ff00` 等刺眼裸原色；开篇第 0 步必须调用 `search_styles` 获取电影色彩 Token（如 `Spotlight` 调查深绿 `#0B0F19 / #A0DCAF` 或 `Oppenheimer` 工业琥珀金 `#0D0B09 / #FF9A50`）与径向暗角滤镜（Vignette）。
5. **连续帧微动与视差契约（Living Motion）**：任何在屏停留超过 1.8 秒的视觉层，必须绑定基于时间变量 `t` 的连续缓动（摄像机慢推 Scale $1.00 \to 1.05$ + 前景与背景 1.5x 差速平移），确保画面每一帧都在呼吸。
6. **物证荧光笔涂抹动画（0.6s Draw Mask）**：文件原件重点语句必须采用 `clip-path: inset(0 calc(100% - var(--p)) 0 0)` 实现从左至右的半透明荧光笔涂抹高亮。
7. **数字跳动与落点辉光（Ticking Counter & Bloom）**：核心统计数字进场必须在 0.8s 内从 0 滚动递增至目标值，并在锁定瞬间触发辉光脉冲。
8. **纯净画质与零技术水印铁律**：严禁在画面四周叠加 `DEEP INVESTIGATION //`、`REMOTION FINANCIAL CHART //`、`ASYMMETRIC CONTRAST L03`、`OFFICIAL EVIDENCE //` 等内部技术代号与虚假伪英文标签！所有画面文字必须是真实清晰的中文专业调查表述与权威文献，必须 100% 通过 `visual_purity_linter`。
9. **深沉纪实声学与 BGM 宁缺毋滥原则**：严禁高频刺耳机械滴答；BGM 必须是低频电影氛围垫乐（Investigative Pad），若无精准匹配的高品质音乐，无条件执行 `--no-bgm` 纯净解说母带，以演播室原声保证深度调查片的严肃权威感。

---

## 三、七站式标准生产工序与精确 CLI 指令手册

### 站 0 & 站 1：电影调色定调与文案气口切分
```bash
# 1. 查询奥斯卡商业调查调色盘 Token（输出 JSON 供 CSS 变量直接引用）
search_styles "Spotlight" > ./00_需求界定/style_tokens.json
search_styles "Oppenheimer" > ./00_需求界定/style_tokens_alt.json
```
- 文案严格按 **3.7 字/秒** 第一人称深度叙事撰写，落盘至 `./01_文案/文案_v3.md`。

### 站 2 & 站 3：真实物证装配、代码级 2.5D 舞台构建与连续帧核验（默认零 Colab 依赖）
> **【算力解耦原则】**：SOP 01 是以**真实物证链 + 数字可视化图表 + Stage25D 视差运镜**为核心的本地高吞吐产线，**默认全程在 Antigravity 本地闭环完成，不调用 Colab GPU**！仅当特定分镜极端缺失历史纪实底图、且本地素材无法替代时，才允许按需单点调用 `colab_image_gen`。

```bash
# 2. 对本地真实视频物证/演讲切片生成 4x3 (12格) 连续帧物证联系表
wallstreet-strip ./03_素材/raw_keynote.mp4 0.0 15.0 12 ./08_判据/evidence_contact_sheet.jpg 4 --w 480
```

### 站 4：音频母带混音与 `-16.0 LUFS` 响度锁死
```bash
# 自动执行 30ms 首尾防爆音淡化 (afade)、背景乐智能压低与 -16.0 LUFS 广播级响度归一化
audio_bgm_mixer \
  --voice ./03_素材/voiceover_raw.wav \
  --bgm ./03_素材/investigation_bgm.mp3 \
  --output ./03_素材/mixed_audio_lufs16.wav \
  --lufs -16.0
```

### 站 5 & 站 6：4 层工业流水线标准装配 (`to_timeline` ➔ `edl2film` ➔ `openfilm`)
```bash
# 步骤 6.1：将导演表分镜决策 JSON 转化为标准 timeline.json 并自动生成 openfilm 工程
to_timeline generic ./02_导演表/shots_decision.json \
  -o ./work/timeline.json \
  --film ./work/openfilm_project \
  --width 1920 --height 1080 --cover

# 步骤 6.2：若基于复合 HTML 舞台直接编译，显式调用 edl2film
edl2film ./work/timeline.json -o ./work/openfilm_project --width 1920 --height 1080 --force

# 步骤 6.3：双向乱序抽帧确定性测试（输出 12 帧接触表与响度图）
cd ./work/openfilm_project && openfilm look 1-12
```

### 站 7：1080p 硬件加速压制、三重门禁终审与 Google Drive 交付
```bash
# 步骤 7.1：渲染 1080p 30fps 成片并导出达芬奇/FCPX 专业工程交割单
openfilm render -o ./交付成片/final_master_1080p.mp4
openfilm export fcpxml -o ./交付成片/final_master.fcpxml
openfilm export premiere -o ./交付成片/final_master_premiere.xml

# 步骤 7.2：三重客观机器门禁强制校验（全绿方可上传）
motion_check ./交付成片/final_master_1080p.mp4 --top 0.8 --json > ./08_判据/motion_check_report.json
film_gatekeeper --video ./交付成片/final_master_1080p.mp4 --lufs -16.0 --tolerance 1.0 --json > ./08_判据/gatekeeper_report.json
wallstreet-strip ./交付成片/final_master_1080p.mp4 0.0 60.0 12 ./08_判据/final_contact_sheet.jpg 4 --w 480
```

---

## 四、Google Drive 自包含交付标准（v3.0 强制规约）

所有产物必须通过 `gdrive mutate mkdir` 与 `gdrive mutate upload` 完整归档至 `1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/01_真素材数字可视化/{YYYYMMDD}_{项目名}_v3/`，目录结构如下：

```text
{YYYYMMDD}_{项目名}_v3/
├── 00_需求界定/
│   ├── 素材就位单.json
│   └── style_tokens.json            # lemo-opuscar 电影调色令牌
├── 01_文案/
│   └── 文案_v3.md                   # 3.7字/秒深度叙事稿
├── 02_导演表/
│   ├── 导演表_v3.md                 # 含强制 Skill 模具映射编号的 7 列导演表
│   └── shots_decision.json          # 4层流水线标准输入
├── 03_素材/                         # 高清物证、1080p 底图、-16 LUFS 母带音频
├── 08_判据/
│   ├── evidence_contact_sheet.jpg   # 原始物证 12 格联系表
│   ├── final_contact_sheet.jpg      # 成片 12 格抽帧联系表（网盘直览）
│   ├── motion_check_report.json     # 运镜活跃度 >= 30% 合格单
│   └── gatekeeper_report.json       # 1920x1080 / -16 LUFS 终审绿单
└── 交付成片/
    ├── final_master_1080p.mp4       # 1080P 商业纪实成片
    ├── final_master.fcpxml          # FCPX / 达芬奇可编辑工程
    └── 封面_16x9.jpg                 # 电影级主视觉封面
```
