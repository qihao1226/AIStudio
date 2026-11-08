# AG_SOP_05 · 工业口播伴侣动效视频生产流水线 SOP (v3.0 极致执行手册版)

> **版本**：v3.0 (adu-motion-video v3.14 竖屏原生 13 套资产包 + 零角标污染 + 人脸口唇双区避障版) ｜ **更新日期**：2026-11-08  
> **战队编制**：战队 2「工业口播动效队」 ｜ **表现形态**：形态 2「口播伴侣动态挂件 / 智能角标系统」  
> **核心定位**：**为人像赋能，让表达具象。专为真人出镜口播与数字人播报定制的工业级视觉增强伴侣。实现台词时间戳与动态挂件毫秒同频，输出权威身份角标、数据浮窗、引证画中画与金句高光卡，严格遵守人脸与底部字幕双重避障契约。**  
> **GitHub 归档路径**：[`docs/sops/AG_SOP_05_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_05_v3.0.md)  
> **Google Drive 知识库路径**：`1YJqjW_FDdyY0iZsFeOSr1x_RK-F1_FFd/AG_SOP_05_工业口播伴侣动效生产流水线 SOP v1.0.md`  
> **Google Drive 交付路径**：`1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/05_工业口播伴侣/`

---

## 〇、强制前置铁律（Step 0：跨会话永久底座唤醒与默认角标关闭政策）

在启动口播伴侣动效生产前，**必须首先执行以下两行底座唤醒指令**：

```bash
/home/antigravity/qihao1226/AIStudio/scripts/bootstrap.sh
export PATH="/home/antigravity/.local/bin:/shared/user/.gemini/youai/bin:$PATH"
```

> **【v3.0 强制合规配置：默认关闭 `adu-motion-video` 成片强制角标】**
> `adu-motion-video` v3.14.1 默认会在右上角注入引擎签名水印。根据工场统一政策，**必须在项目工程根目录写入 `output-signature.json` 显式关闭角标**：
> ```json
> {"enabled": false}
> ```

---

## 一、七大空间安全区契约与伴侣动效铁律

| # | 决策维度 | 核心规范与物理量化标准 | 机器拦截红线 |
| :---: | :--- | :--- | :--- |
| **1** | **人脸与口唇绝对避障（Face Safety）** | 挂件图层距离主播面部轮廓（双眼、鼻尖、嘴唇、下巴）的物理间距必须 **$\ge 120\text{px}$**。 | `face_occlusion_check` 检出任何遮脸像素直接拦截。 |
| **2** | **底部字幕独占禁区（Subtitle Zone）** | 竖屏（1080×1920）底部 **`220px`（即 `Y: 1700 ~ 1920`）设为字幕独占隔离带**；任何伴侣挂件下边缘严禁超过 `Y = 1660`。 | 挂件侵入底部 220px 与字幕重叠直接判定废片。 |
| **3** | **对角线与胸前黄金锚点** | 身份角标（`lower_third`）锚定在 `Y: 1320 ~ 1580`；数据浮窗（`data_callout`）与画中画（`pip_evidence`）锚定在人物视线对侧上方安全区（`Y: 220 ~ 680`）。 | 挂件悬浮在屏幕正中央挡住主播五官。 |
| **4** | **首音节毫秒级锁死（$\le 0.10\text{s}$）** | 挂件入场时刻必须与主播念出该实体词的首个音节对齐（误差 $\le 0.10\text{s}$），并在话题切换时以 `0.35s` 阻尼滑出。 | 话音已落挂件才迟缓出现。 |
| **5** | **黄金驻留呼吸窗口（3.0s ~ 6.0s）** | 单个伴侣挂件在屏停留时间严格控制在 **3.0s ~ 6.0s**；停留期间必须保持微幅悬浮呼吸（$\pm 4\text{px}$ 正弦浮动）。 | 挂件一闪而过（$<2\text{s}$）或死板定格（$>8\text{s}$）。 |
| **6** | **零默认占位符污染（Sentinel Check）** | 严禁画面残留模板默认的 `"Lorem Ipsum"`、`"$99.9%"`、`"Title Here"` 等未绑定占位符！必须通过 `motionkit sentinel` 校验。 | 参数未生效或出现默认英文占位符。 |
| **7** | **毛玻璃拟态与高信噪比材质** | 挂件底板采用深色半透明毛玻璃（`rgba(15, 23, 42, 0.82)` + `backdrop-filter: blur(16px)` + `1px solid rgba(255,255,255,0.16)`），确保在任何实拍背景上清晰可读。 | 纯色死板方框或透明底文字与背景融成一团。 |

---

## 二、`adu-motion-video` 核心伴侣资产包选型矩阵

| 资产包 ID | 适用口播语义 | 标准安全区坐标 (`1080×1920`) | 核心视觉要素 |
| :--- | :--- | :--- | :--- |
| **`lower_third`** | 嘉宾开场亮明身份、权威机构背书 | `X: 80~920, Y: 1380~1560` | 左侧强调色竖条 + 主姓名 56px + 头衔 32px |
| **`data_callout`** | 提及暴涨百分比、核心财务数字 | `X: 540~1000, Y: 260~560` | 跳数大字 88px + 迷你趋势折线 + 绿/金徽章 |
| **`fact_check`** | 辟谣打假、真伪结论盖戳 | `X: 520~1000, Y: 300~620` | 条款原文卡片 + 动态阻尼砸印红/绿公章 |
| **`quote_card`** | 引用名人金句、财报核心原话 | `X: 80~1000, Y: 1280~1600` | 引号徽标 + 重点词荧光高亮 + 出处署名 |
| **`pip_evidence`** | 展示新闻截图、论文图表画中画 | `X: 480~1000, Y: 240~720` | 圆角视窗 + 扫描线微光 + 底部来源标签 |
| **`step_tracker`** | “第一点、第二点、第三点”结构导航 | `X: 60~420, Y: 200~480` | 胶囊进度指示器 + 当前激活步骤高亮 |

---

## 三、标准生产工序与精确 CLI 指令手册

### 第 1 步：写入去角标配置与执行动效包体检 (`motionkit doctor & sentinel`)
```bash
# 1.1 强制关闭默认引擎水印角标
echo '{"enabled": false}' > ./output-signature.json

# 1.2 动效包健康度与参数接线哨兵校验
motionkit doctor /home/antigravity/skills/adu-motion-video/packs/lower_third/1.0.0/pack.motion > ./08_判据/doctor_report.json
motionkit sentinel /home/antigravity/skills/adu-motion-video/packs/lower_third/1.0.0/pack.motion ./02_挂件配置/params_real.json > ./08_判据/sentinel_report.json
```

### 第 2 步：伴侣挂件图层生产与人脸避障检测 (`face_occlusion_check`)
```bash
# 2.1 生成伴侣动效图层
motionkit produce /home/antigravity/skills/adu-motion-video/packs/lower_third/1.0.0/pack.motion \
  ./02_挂件配置/params_real.json --workflow native --out ./03_素材/overlays/

# 2.2 核验人脸 >= 120px 安全间距与底部 220px 字幕隔离带
face_occlusion_check \
  --speaker ./03_素材/raw_talking_head.mp4 \
  --overlay ./02_挂件配置/params_real.json \
  --margin 120 --subtitle-zone 220 \
  --json > ./08_判据/face_occlusion_report.json
```

### 第 3 步：音频母带混音与 4 层双轨合成 (`to_timeline` ➔ `edl2film` ➔ `openfilm`)
```bash
# 3.1 口播人声与伴侣出场轻音效/底乐混音（锁定 -16.0 LUFS）
audio_bgm_mixer \
  --voice ./03_素材/speaker_voice.wav \
  --bgm ./03_素材/subtle_tech_bgm.mp3 \
  --output ./03_素材/mixed_audio_lufs16.wav \
  --bgm-vol 0.10 --lufs -16.0

# 3.2 双轨合成压制 1080x1920 竖屏成片
to_timeline generic ./02_挂件配置/companion_timeline.json -o ./work/timeline.json --film ./work/companion_project --width 1080 --height 1920
edl2film ./work/timeline.json -o ./work/companion_project --width 1080 --height 1920 --force
cd ./work/companion_project && openfilm look 1-12
openfilm render -o ./交付成片/final_companion_1080x1920.mp4
```

### 第 4 步：终审门禁与抽帧检视表生成
```bash
film_gatekeeper --video ./交付成片/final_companion_1080x1920.mp4 --target-w 1080 --target-h 1920 --lufs -16.0 --tolerance 1.0 --json > ./08_判据/gatekeeper_report.json
wallstreet-strip ./交付成片/final_companion_1080x1920.mp4 0.0 60.0 12 ./08_判据/final_contact_sheet.jpg 4 --w 360
```

---

## 四、Google Drive 自包含交付标准（v3.0 强制规约）

所有产物归档至 `1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/05_工业口播伴侣/{YYYYMMDD}_{项目名}_v3/`：

```text
{YYYYMMDD}_{项目名}_v3/
├── 00_需求界定/
│   ├── 口播伴侣需求单.json
│   └── output-signature.json        # {"enabled": false} 零水印声明
├── 01_文案与时间戳/
│   └── 口播文案带时间码.md           # 标注每个挂件入场/退场毫秒时间码
├── 02_挂件配置/
│   ├── params_real.json             # 伴侣挂件参数注入表
│   └── companion_timeline.json      # 双轨时间线配置
├── 03_素材/
│   ├── raw_talking_head.mp4
│   └── mixed_audio_lufs16.wav
├── 08_判据/
│   ├── face_occlusion_report.json   # 0 遮脸像素合格单 (margin >= 120px)
│   ├── sentinel_report.json         # 参数接线 100% 生效合格单
│   ├── final_contact_sheet.jpg      # 12 帧挂件与人像避障抽样表
│   └── gatekeeper_report.json       # 1080x1920 / -16 LUFS 终审绿单
└── 交付成片/
    ├── final_companion_1080x1920.mp4
    └── 封面_3x4.jpg
```
