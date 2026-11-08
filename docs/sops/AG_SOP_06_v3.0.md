# AG_SOP_06 · 极客架构与概念演示视频生产流水线 SOP (v3.0 极致执行手册版)

> **版本**：v3.0 (零豆腐块乱码铁律 + 单一认知聚光灯 + Jacky-motion 2.1 60fps 极客版) ｜ **更新日期**：2026-11-08  
> **战队编制**：战队 3「极客演示导演队」 ｜ **表现形态**：形态 6「代码打字机与系统架构演示」(Tech Walkthrough)  
> **核心定位**：**把复杂的系统讲明白，让硬核的代码有灵魂。面向开发者、架构师与技术决策者的高维技术演示视频。以 GitHub Dark / Dracula 极客终端美学、单一认知聚光灯、内联矢量图标（零 `☒` 豆腐块乱码）与 60fps 丝滑粒子流震撼出片。**  
> **GitHub 归档路径**：[`docs/sops/AG_SOP_06_v3.0.md`](file:///home/antigravity/qihao1226/AIStudio/docs/sops/AG_SOP_06_v3.0.md)  
> **Google Drive 知识库路径**：`1YJqjW_FDdyY0iZsFeOSr1x_RK-F1_FFd/AG_SOP_06_极客架构与概念演示视频生产流水线 SOP v1.0.md`  
> **Google Drive 交付路径**：`1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/06_极客演示导演/`

---

## 〇、强制前置铁律（Step 0：跨会话永久底座唤醒与零豆腐块乱码铁律）

在启动极客架构演示视频生产前，**必须首先执行以下两行底座唤醒指令**：

```bash
/home/antigravity/qihao1226/AIStudio/scripts/bootstrap.sh
export PATH="/home/antigravity/.local/bin:/shared/user/.gemini/youai/bin:$PATH"
```

> **【红线禁令：算力解耦原则 + 零豆腐块乱码铁律 (Zero-Tofu Glyph Policy)】**
> 0. **【算力边界】本产线（SOP 06）是基于 `Jacky-motion 2.1` 单文件 HTML5/SVG 的极客代码与架构推演产线，100% 在 Antigravity 本地闭环完成，严禁调用 Colab GPU！**
> 1. **严禁在 HTML/Canvas 中裸写 `⚡🔥🚀💡✅❌` 等 Emoji 字符**！所有闪电、服务器、数据库、警告、勾选图标，**必须 100% 使用内联 `<svg>` 矢量路径或纯几何 CSS 徽标**！
> 2. 所有代码区必须显式声明字体栈：`font-family: 'JetBrains Mono', 'Fira Code', 'DejaVu Sans Mono', monospace;`；所有中文说明区必须显式声明：`font-family: 'Noto Sans CJK SC', 'Source Han Sans SC', sans-serif;`。
> 3. 渲染前必须通过 `cognitive_load_linter` 的 `zero_tofu_emoji_risk` 门禁检查！

---

## 一、七大极客美学与认知聚光灯铁律

| # | 决策维度 | 核心规范与物理量化标准 | 机器拦截红线 |
| :---: | :--- | :--- | :--- |
| **1** | **单一认知聚光灯（Single Spotlight）** | 同一时刻画面**有且仅有 1 个高亮聚焦对象**（当前执行的代码行或当前激活的微服务节点，Opacity `1.0` + 发光边框）；其余非焦点节点自动退行压暗（Opacity `0.25 ~ 0.35`）。 | 全屏所有节点同时高亮闪烁导致观众认知过载。 |
| **2** | **深色极客终端底色（GitHub Dark）** | 主背景 `#0D1117`，卡片容器 `#161B22`，边框 `#30363D`，文字对比度 $\ge 7.0:1$（WCAG AAA）。 | 刺眼白底或低对比度灰底灰字。 |
| **3** | **真实 AST 语法高亮（Code Fidelity）** | 代码块必须按语法树着色（关键字 `#FF7B72`、函数名 `#D2A8FF`、字符串 `#A5D6FF`、注释 `#8B949E`、数字 `#79C0FF`），左侧附带行号栏。 | 整段代码使用同一种颜色生硬贴出。 |
| **4** | **脉冲光标打字机与高亮扫描条** | 代码演示必须配合逐字符打字机揭示（18~25 字符/秒）+ 500ms 呼吸光标 `▋` + 当前讲解行半透明蓝金扫描背景条。 | 静态截图式整页贴满 30 行小字代码。 |
| **5** | **SVG 粒子数据流动画（Data Flow）** | 架构拓扑图中的服务调用连线必须采用 `stroke-dasharray: 8 6` 并随时间 `t` 动态递减 `stroke-dashoffset`，呈现真实的请求/回滚粒子流向。 | 死板的静态直线箭头。 |
| **6** | **架构演进左右对比（L02 Split）** | 拆解技术方案时，强制采用 `L02-Compare` 骨架：左侧暗灰红展示旧方案瓶颈（如 `2PC 同步阻塞锁死`），右侧亮青绿展示新架构流转（如 `Saga 异步事件补偿`）。 | 只讲抽象概念而不展示新旧拓扑状态机对比。 |
| **7** | **60fps 丝滑帧率与从容语速（3.4 字/秒）** | 成片帧率锁定 **`60fps`**（确保光标移动与拓扑粒子流极致丝滑），技术解说语速控制在 **3.3 ~ 3.6 字/秒**，综合响度 **`-16.0 LUFS`**。 | 30fps 卡顿掉帧或语速过快无气口。 |

---

## 二、`Jacky-motion 2.1` 极客骨架组件族映射表 (`L01` ~ `L10`)

| 骨架编号 | 组件名称 | 典型技术演示场景 | 视觉结构特征 |
| :--- | :--- | :--- | :--- |
| **`L01-Hero`** | 极客终端巨字揭示 | 开场高并发压测崩盘悬念、反常识架构结论 | 顶部 `>_` 终端状态栏 + SVG 矢量闪电徽标 + 96px 等宽巨字 |
| **`L02-Compare`** | 架构分屏对抗演进 | 2PC 强一致锁死 vs Saga 最终一致性对比 | 左右对称深色容器 + 延迟耗时红绿进度条实时博弈 |
| **`L05-Hierarchy`** | 多层协议栈/微服务拓扑 | API Gateway ➔ Order ➔ Inventory ➔ Payment 链路 | 纵向/横向节点拓扑 + 双向 SVG 发光脉冲粒子流（正向绿/补偿橙） |
| **`L06-CodeWalk`** | IDE 逐行光标拆解 | 核心状态机代码、分布式锁或补偿事务源码剖析 | 仿 VSCode/Neovim 顶栏 + 语法高亮 + 聚光灯激活行放大 |
| **`L08-Benchmark`** | 压测指标与 P99 看板 | 吞吐量 QPS 飙升、P99 延迟断崖下降量化证明 | 实时跳数仪表盘 + 双柱状图对比 + 零未解析占位符 |

---

## 三、标准生产工序与精确 CLI 指令手册

### 第 1 步：克隆 `Jacky-motion 2.1` 单文件骨架并注入内联 SVG 与 GSAP 时间轴
```bash
# 从持久化技能库复制基础模板（或生成单文件自包含 HTML5 工程）
mkdir -p ./02_工程源码 ./03_素材 ./08_判据 ./交付成片
```
- 编写 `./02_工程源码/tech_demo.html`，确保所有图标均为 `<svg>`，所有分镜节点均带有 `data-layout="L01..L08"` 属性。

### 第 2 步：静态模板校验与认知负荷/零乱码门禁 (`jacky-validate` & `cognitive_load_linter`)
```bash
# 2.1 校验无残留 {{PLACEHOLDER}} 占位符且规范声明 data-layout
jacky-validate ./02_工程源码/tech_demo.html > ./08_判据/jacky_validate_report.json

# 2.2 校验单一聚光灯、深色终端对比度、等宽字体与零 Emoji 豆腐块风险
cognitive_load_linter --html ./02_工程源码/tech_demo.html --json > ./08_判据/cognitive_load_report.json
```

### 第 3 步：音频母带混音与 1080p 60fps 硬件加速渲染
```bash
# 3.1 技术解说人声与极客合成器底乐混音（锁定 -16.0 LUFS）
audio_bgm_mixer \
  --voice ./03_素材/tech_voice.wav \
  --bgm ./03_素材/synthwave_ambient_bgm.mp3 \
  --output ./03_素材/mixed_audio_lufs16.wav \
  --bgm-vol 0.12 --lufs -16.0

# 3.2 渲染 1920x1080 @ 60fps 极客演示成片并导出 FCPXML 工程
openfilm look ./02_工程源码/tech_demo.html 1-12
openfilm render ./02_工程源码/tech_demo.html -o ./交付成片/final_geek_master_1080p_60fps.mp4
openfilm export fcpxml -o ./交付成片/final_master.fcpxml
```

### 第 4 步：终审门禁与 12 格高清检视表生成
```bash
film_gatekeeper \
  --video ./交付成片/final_geek_master_1080p_60fps.mp4 \
  --target-w 1920 --target-h 1080 --fps 60 \
  --lufs -16.0 --tolerance 1.0 \
  --json > ./08_判据/gatekeeper_report.json

wallstreet-strip ./交付成片/final_geek_master_1080p_60fps.mp4 0.0 60.0 12 ./08_判据/evidence_contact_sheet.jpg 4 --w 480
```

---

## 四、Google Drive 自包含交付标准（v3.0 强制规约）

所有产物归档至 `1FHApfkCr9Xq76E4gTAVR5i3weVsRTmJc/06_极客演示导演/{YYYYMMDD}_{项目名}_v3/`：

```text
{YYYYMMDD}_{项目名}_v3/
├── 00_需求界定/
│   └── 素材就位单.json
├── 01_文案/
│   └── 文案_极客口播版.md            # 3.4字/秒带聚光灯焦点标记脚本
├── 02_导演表/
│   ├── 导演表_极客架构版.md          # L01~L08 骨架映射导演表
│   ├── shots_decision.json
│   └── tech_demo.html               # 自包含单文件极客演示源码 (零外部构建依赖)
├── 03_素材/
│   └── mixed_audio_lufs16.wav
├── 08_判据/
│   ├── jacky_validate_report.json   # 0 占位符遗留合格单
│   ├── cognitive_load_report.json   # 单聚光灯 + 零豆腐块乱码合格单
│   ├── evidence_contact_sheet.jpg   # 12 格代码与拓扑特写联系表（100% 无 ☒ 乱码）
│   └── gatekeeper_report.json       # 1920x1080 @ 60fps / -16 LUFS 终审绿单
└── 交付成片/
    ├── final_geek_master_1080p_60fps.mp4
    ├── final_master.fcpxml
    └── 封面_16x9.jpg
```
