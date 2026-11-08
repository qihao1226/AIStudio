# AG_SOP_03 · 白板手绘与火柴人讲解视频生产流水线 SOP (v3.0 极致执行手册版)

> **版本**：v3.0 (8大黄金白板布局模具 + SVG 笔触渐进生长 + 三轨拟音混音版) ｜ **更新日期**：2026-11-08  
> **产线编号**：P8「白板手绘讲解」/ P11「火柴人叙事」 ｜ **战队编制**：战队 5「手绘白板故事队」  
> **核心定位**：**边画边讲（Drawing while talking）、概念降维解构、手绘温度、火柴人具象叙事。适用于知识科普、商业模式拆解、认知心理学与方法论推演。**  
> **GitHub 归档路径**：[`docs/sops/AG_SOP_03_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_03_v3.0.md)  
> **Google Drive 知识库路径**：`1YJqjW_FDdyY0iZsFeOSr1x_RK-F1_FFd/AG_SOP_03_白板手绘与火柴人讲解视频生产线_v1.0.md`  
> **Google Drive 交付路径**：`1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/03_白板火柴人讲解/`

---

## 〇、强制前置铁律（Step 0：跨会话永久底座一键唤醒）

在启动白板手绘视频生产前，**必须首先执行以下两行底座唤醒指令**（已彻底修复历史 `wb` 脚本递归死循环 `Argument list too long` 报错）：

```bash
/home/antigravity/qihao1226/AIStudio/scripts/bootstrap.sh
export PATH="/home/antigravity/.local/bin:/shared/user/.gemini/youai/bin:$PATH"
```

> **【白板产线三大生死铁律】**
> 0. **【算力边界】本产线（SOP 03）是基于纯矢量 SVG 路径与认知节奏的本地产线，100% 在 Antigravity 本地闭环完成，严禁调用 Colab GPU！**
> 1. **严禁对白板视频执行 `motion_check`**：白板视频采用固定机位俯瞰羊皮纸画布，靠“画笔笔触渐进生长”驱动视觉，背景本就静止。白板产线唯一合法的动态门禁是 **`pen_motion`**！
> 2. **严禁自由散漫排布坐标**：所有 Scene 必须从下方 **「8 大 Excalidraw 黄金布局模具」** 中选型，严格遵守画布安全框 `X: [120, 1800], Y: [100, 840]`（底部 `Y: 860~1080` 为字幕独占禁区，绝不允许任何手绘图形或文字压入底部字幕区！）。

---

## 一、白板手绘 8 大 Excalidraw 黄金布局模具（彻底根治排版拥挤与越界）

每一个 Scene（一镜一完整画板）必须在导演表中声明所采用的布局模具编号 `WB_L01` ~ `WB_L08`：

| 模具编号 | 布局名称 | 空间网格坐标契约 (`1920×1080` 安全区) | 适用知识表达场景 |
| :--- | :--- | :--- | :--- |
| **`WB_L01`** | **三栏递进演进型** | 左(`X:160~620`) ➔ 中(`X:730~1190`) ➔ 右(`X:1300~1760`)，顶标题 `Y:120` | 历史演进、三层大脑结构（爬行脑➔哺乳脑➔皮层）、三步法则 |
| **`WB_L02`** | **左右天平对抗型** | 左旧误区(`X:160~860` 灰黑笔触) vs 右新方案(`X:1060~1760` 朱红/宝蓝高亮) | 认知纠偏、传统做法 vs 高手思维、成本收益对比 |
| **`WB_L03`** | **中心辐射脑图型** | 中心核心火柴人/概念圆(`960, 460`) + 四角辐射分支(`左上/右上/左下/右下`) | 核心本质拆解、多元成因剖析、系统四大支柱 |
| **`WB_L04`** | **左画右解故事型** | 左侧 55% 火柴人情景剧场(`X:160~1020`) + 右侧 45% 手绘要点清单(`X:1080~1760`) | 案例故事引入、痛点场景还原（如情绪劫持瞬间） |
| **`WB_L05`** | **纵向漏斗/金字塔型** | 顶部宽层(`Y:220`) ➔ 中腰层(`Y:440`) ➔ 底部核心结晶(`Y:660`)，两侧批注 | 认知筛选漏斗、马斯洛层级、商业转化模型 |
| **`WB_L06`** | **四象限矩阵型** | 十字手绘坐标轴交于(`960, 470`)，四个象限均匀留白 $\ge 40\text{px}$ | 重要紧急矩阵、风险收益评估、品类定位图 |
| **`WB_L07`** | **折线路径闯关型** | S 型手绘虚线路径串联 4 个里程碑节点（配火柴人行走/举旗动作） | 实操 SOP 路线图、从新手到专家成长路径 |
| **`WB_L08`** | **公式结晶顿悟型** | 上半屏具象图示(`Y:180~480`) + 下半屏超大号手写荧光框公式(`Y:540~760`) | 结尾金句升华、核心心法口诀定格（如 `觉察 = 暂停键`） |

---

## 二、七大白板美学与视听同频铁律

1. **一镜一完整画板（One Scene = One Board）**：一个 Scene 内逐笔增量绘制 3~5 个视觉 Beat，**Scene 内部严禁切镜**；画满一块白板后，通过“翻页推移”进入下一个 Scene。
2. **恒定黄金语速（`3.14 ± 0.15` 字/秒）**：解说词速率严格锁死在 **3.14 字/秒**，给观众眼睛留出跟随笔尖轨迹阅读的生理时间。
3. **笔随声动，画完即止（SVG `stroke-dashoffset` 渐进绘制）**：每个火柴人、手绘框、手绘箭头必须使用真实的 SVG 路径长度插值动画（随当前词语时间戳从 `dashoffset = pathLength` 平滑过渡到 `0`），严禁整张图直接淡入闪现！
4. **温润羊皮纸底与四色马克笔规范**：
   - 画布底色锁定为暖米白羊皮纸 `#FAF7F0`（附微弱纸张噪点纹理，拒绝刺眼 `#FFFFFF`）；
   - 全片仅限 4 支马克笔颜色：主线碳黑 `#2B2B2B`、痛点警示朱红 `#D9381E`、方法洞察宝蓝 `#1E56A0`、顿悟高亮暖黄荧光笔 `rgba(255, 224, 102, 0.55)`。
5. **具象火柴人肢体语言库**：火柴人必须包含具象姿态（抓头困惑 `?`、头顶灯泡顿悟 `💡`、抱头焦虑闪电、手持放大镜、昂首握拳），拒绝画死板十字火柴棍。
6. **真实物理拟真音频架构（严禁电子蜂鸣）**：由 **`audio_bgm_mixer`** 混合音频：① 纯净人声解说；② 马克笔真实书写拟音（`--foley`，使用真实毛毡笔摩擦录音或平滑物理宽带噪声，**绝对严禁 `np.sin(2400*t)` 等电子正弦波滴滴脉冲**）；③ 场景化轻音乐（`--bgm`，音量系数 `0.10`；若无精准匹配的高品质轻音乐，**无条件执行 `--no-bgm` 纯净解说母带**，宁缺毋滥！）。
7. **字画绝对避让与字号底线**：任何文字与线条严禁交叉重叠；标题字号 $\ge 52\text{px}$，批注字号 $\ge 32\text{px}$，底部 `Y > 840` 严禁画图。
8. **零技术杂质与纯净画质铁律**：严禁在白板画面的任何位置叠加 `YOUAI //`、`AG_SOP_03`、`WB_L01~L08`、`3.14 CPS`、`1080P` 等开发代号或性能遥测信息。画板呈现的每一字每一图均必须是直接给受众看的纯净认知内容，必须 100% 通过 `visual_purity_linter`。

---

## 三、标准生产工序与精确 CLI 指令手册

### 第 1 步：初始化白板工程与编写 3.14 字/秒恒速脚本
```bash
# 1. 初始化白板项目目录
wb new "大脑底层操作系统"
```
- 编写旁白稿并统计总汉字数 `N_CHARS`，目标时长严格按 $T = N_{\text{CHARS}} / 3.14$ 设定。

### 第 2 步：三轨解耦混音母带制作（人声 + 马克笔拟音 + 轻音乐）
```bash
# 调用三轨混音器：自动叠加马克笔书写沙沙声 (--foley) 与轻音乐 (--bgm)，锁定 -16.0 LUFS
audio_bgm_mixer \
  --voice ./work/voice.wav \
  --foley ./work/marker_foley.wav \
  --bgm ./work/acoustic_light_bgm.mp3 \
  --output ./work/final_mixed_audio.wav \
  --foley-vol 0.20 \
  --bgm-vol 0.12 \
  --lufs -16.0
```

### 第 3 步：Excalidraw / SVG 渐进笔触渲染与 4 层流水线合成
```bash
# 生成各 Scene 静帧排版检视表，人工/视觉核验零字画重叠、零底部字幕侵占
wb stills "大脑底层操作系统"

# 接入 4 层流水线无损压制 1080p 成片
to_timeline generic ./02_场景/scenes_decision.json -o ./work/timeline.json --film ./work/wb_openfilm --width 1920 --height 1080
edl2film ./work/timeline.json -o ./work/wb_openfilm --width 1920 --height 1080 --force
cd ./work/wb_openfilm && openfilm look 1-12
openfilm render -o ./交付成片/final_whiteboard_1080p.mp4
```

### 第 4 步：白板专属双重机器门禁校验 (`pen_motion` + `film_gatekeeper`)
```bash
# 4.1 笔触同频与 3.14 字/秒恒速门禁（严禁在此产线运行 motion_check！）
pen_motion \
  --video ./交付成片/final_whiteboard_1080p.mp4 \
  --script-chars 188 \
  --expected-rate 3.14 \
  --tolerance 0.20 \
  --json > ./08_判据/pen_motion_report.json

# 4.2 工业成片终审门禁（1920x1080 / -16.0 LUFS / 0黑帧）
film_gatekeeper \
  --video ./交付成片/final_whiteboard_1080p.mp4 \
  --target-w 1920 --target-h 1080 \
  --lufs -16.0 --tolerance 1.0 \
  --json > ./08_判据/gatekeeper_report.json

# 4.3 生成 12 格成片手绘演进检视表
wallstreet-strip ./交付成片/final_whiteboard_1080p.mp4 0.0 60.0 12 ./08_判据/final_contact_sheet.jpg 4 --w 480
```

---

## 四、Google Drive 自包含交付标准（v3.0 强制规约）

所有产物归档至 `1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/03_白板火柴人讲解/{YYYYMMDD}_{项目名}_v3/`：

```text
{YYYYMMDD}_{项目名}_v3/
├── 00_需求界定/
│   └── 白板科普立项单.json          # 标注每个 Scene 选用的 WB_L01~WB_L08 模具编号
├── 01_文案/
│   └── 旁白稿.md                    # 严格 3.14 字/秒恒速白板讲稿
├── 02_场景/
│   ├── scenes.js                    # SVG/Excalidraw 渐进笔触源码
│   └── scenes_decision.json         # 时间线分镜表
├── 03_素材/
│   ├── marker_foley.wav             # 马克笔书写拟音轨
│   └── final_mixed_audio.wav        # 三轨混音母带 (-16 LUFS)
├── 08_判据/
│   ├── stills/                      # 各 Scene 完笔静帧图
│   ├── final_contact_sheet.jpg      # 12 格渐进手绘抽帧联系表
│   ├── pen_motion_report.json       # 3.14字/秒恒速与笔触同频合格单
│   └── gatekeeper_report.json       # 工业级终审绿单
└── 交付成片/
    ├── final_whiteboard_1080p.mp4   # 1080P 白板手绘成片
    ├── 封面-4x3.png                 # 横版羊皮纸手绘封面
    └── 封面-3x4.png                 # 竖版小红书手绘封面
```
