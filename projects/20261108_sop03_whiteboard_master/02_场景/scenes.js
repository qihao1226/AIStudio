// 《为什么 90% 的人明明很努力，却掉进了“伪勤奋”陷阱？》— SOP 03 白板场景定义
// 遵循 AG_SOP_03_v3.0 规约：
//  - 画布尺寸 1920×1080，安全边界 X:[120, 1800], Y:[100, 840]，底部 Y>=860 为字幕保留区
//  - 四色马克笔：C.ink (#2B2B2B), C.red (#D9381E), C.blue (#1E56A0), C.yellow (#FFE066)
//  - 恒定 3.14 字/秒黄金认知节奏

const scenes = [];

// ==========================================
// 场景 1：左画右解故事型 (WB_L04) · 疲惫困惑
// 旁白 18 字：你每天忙到深夜，为什么却毫无长进？
// ==========================================
{
  const s = {
    id: '01-intro',
    layout: 'WB_L04',
    duration: 5.732,
    narration: '你每天忙到深夜，为什么却毫无长进？',
    elements: [
      { type: 'title', x: 960, y: 120, text: '为什么越努力越迷茫？', size: 68, color: '#2B2B2B', align: 'center' },
      { type: 'stickman_anxious', x: 480, y: 480, scale: 1.2 }, // 抱头抓狂
      { type: 'desk_mess', x: 380, y: 620, w: 320, h: 140 },
      { type: 'rect_highlight', x: 1100, y: 320, w: 560, h: 180, fill: '#FFE066', stroke: '#D9381E' },
      { type: 'text', x: 1380, y: 380, text: '「努力的错觉」', size: 54, color: '#D9381E', align: 'center' },
      { type: 'text', x: 1380, y: 460, text: '低价值耗能 · 感动自己', size: 36, color: '#2B2B2B', align: 'center' },
      { type: 'arrow', points: [[720, 480], [1080, 410]], color: '#D9381E', width: 3 }
    ]
  };
  scenes.push(s);
}

// ==========================================
// 场景 2：纵向漏斗型 / 仓鼠轮 (WB_L05) · 陷阱剖析
// 旁白 18 字：因为你掉进了低水平重复的伪勤奋陷阱。
// ==========================================
{
  const s = {
    id: '02-trap',
    layout: 'WB_L05',
    duration: 5.732,
    narration: '因为你掉进了低水平重复的伪勤奋陷阱。',
    elements: [
      { type: 'title', x: 960, y: 120, text: '致命陷阱：仓鼠滚轮效应', size: 68, color: '#D9381E', align: 'center' },
      { type: 'hamster_wheel', x: 620, y: 460, r: 210, color: '#2B2B2B' },
      { type: 'stickman_running', x: 620, y: 480, scale: 1.0 },
      { type: 'text', x: 1360, y: 320, text: '伪勤奋的三大特征：', size: 44, color: '#2B2B2B', align: 'center' },
      { type: 'text', x: 1360, y: 420, text: '1. 机械重复，拒绝深思\n2. 盲目打卡，缺乏反馈\n3. 逃避关键，位移为零', size: 34, color: '#1E56A0', align: 'center' },
      { type: 'box_alert', x: 1120, y: 640, w: 480, h: 90, text: '耗尽 99% 精力，位移 = 0', color: '#D9381E' }
    ]
  };
  scenes.push(s);
}

// ==========================================
// 场景 3：左右天平对抗型 (WB_L02) · 认知纠偏
// 旁白 18 字：战术上的勤奋，永远掩盖不了战略的懒惰。
// ==========================================
{
  const s = {
    id: '03-contrast',
    layout: 'WB_L02',
    duration: 5.732,
    narration: '战术上的勤奋，永远掩盖不了战略的懒惰。',
    elements: [
      { type: 'title', x: 960, y: 120, text: '认知天平：伪勤奋 vs 真突破', size: 68, color: '#2B2B2B', align: 'center' },
      { type: 'balance_scale', x: 960, y: 440, tilt: -18 }, // 倾斜天平
      { type: 'panel_left', x: 260, y: 320, w: 500, h: 360, title: '战术假勤奋', items: ['每天加班感动自己', '机械处理繁琐杂事', '逃避真正核心难点'], color: '#777777' },
      { type: 'panel_right', x: 1160, y: 320, w: 500, h: 360, title: '战略真懒惰', items: ['从不复盘商业闭环', '从不推演关键破局', '从不寻找核心杠杆'], color: '#D9381E' },
      { type: 'vs_badge', x: 960, y: 560, text: '≠', size: 80, color: '#D9381E' }
    ]
  };
  scenes.push(s);
}

// ==========================================
// 场景 4：三栏递进演进型 (WB_L01) · 破局路径
// 旁白 16 字：真正的成长，需要打破行动舒适区。
// ==========================================
{
  const s = {
    id: '04-zones',
    layout: 'WB_L01',
    duration: 5.096,
    narration: '真正的成长，需要打破行动舒适区。',
    elements: [
      { type: 'title', x: 960, y: 120, text: '三层认知圈层突破', size: 68, color: '#1E56A0', align: 'center' },
      { type: 'zone_card', x: 240, y: 300, w: 420, h: 420, title: '舒适区', desc: '熟悉劳作\n毫无心智挑战', color: '#777777', fill: '#EEEEEE' },
      { type: 'zone_card', x: 750, y: 300, w: 420, h: 420, title: '恐慌区', desc: '无序焦虑\n目标混乱失控', color: '#D9381E', fill: '#FFE5E5' },
      { type: 'zone_card', x: 1260, y: 300, w: 420, h: 420, title: '刻意学习区', desc: '瞄准关键痛点\n建立精准反馈', color: '#1E56A0', fill: '#E5F0FF', highlight: true },
      { type: 'arrow_flow', points: [[450, 510], [960, 510], [1470, 510]], color: '#1E56A0' }
    ]
  };
  scenes.push(s);
}

// ==========================================
// 场景 5：四象限矩阵型 (WB_L06) · 二八法则
// 旁白 16 字：抓住两成核心难点，撬动八成突破。
// ==========================================
{
  const s = {
    id: '05-matrix',
    layout: 'WB_L06',
    duration: 5.096,
    narration: '抓住两成核心难点，撬动八成突破。',
    elements: [
      { type: 'title', x: 960, y: 120, text: '二八杠杆矩阵：以点带面', size: 68, color: '#2B2B2B', align: 'center' },
      { type: 'quadrant_axes', cx: 960, cy: 470, w: 900, h: 540, x_label: '认知难度 →', y_label: '杠杆收益 ↑' },
      { type: 'quadrant_focus', x: 990, y: 220, w: 420, h: 220, fill: '#FFE066', text: '【破局杠杆点】\n20% 核心难点\n撬动 80% 质变！', color: '#1E56A0' },
      { type: 'quadrant_sub', x: 510, y: 490, w: 400, h: 200, text: '低价值消耗区（80% 杂事）', color: '#777777' },
      { type: 'stickman_lever', x: 1460, y: 340, scale: 0.95 } // 撬动杠杆
    ]
  };
  scenes.push(s);
}

// ==========================================
// 场景 6：中心辐射脑图型 (WB_L03) · 认知驱动
// 旁白 14 字：从盲目苦干，升级为认知驱动。
// ==========================================
{
  const s = {
    id: '06-epiphany',
    layout: 'WB_L03',
    duration: 4.459,
    narration: '从盲目苦干，升级为认知驱动。',
    elements: [
      { type: 'title', x: 960, y: 120, text: '底层操作系统全面升维', size: 68, color: '#1E56A0', align: 'center' },
      { type: 'stickman_epiphany', x: 960, y: 460, scale: 1.3 }, // 头顶灯泡顿悟
      { type: 'bulb_glow', x: 960, y: 300, color: '#FFE066' },
      { type: 'branch_bubble', x: 450, y: 320, text: '目标穿透：不为过程买单', color: '#1E56A0' },
      { type: 'branch_bubble', x: 1470, y: 320, text: '杠杆借力：调用前沿工具', color: '#1E56A0' },
      { type: 'branch_bubble', x: 450, y: 620, text: '闭环反馈：以输出倒逼输入', color: '#1E56A0' },
      { type: 'branch_bubble', x: 1470, y: 620, text: '复利飞轮：资产滚雪球', color: '#1E56A0' }
    ]
  };
  scenes.push(s);
}

// ==========================================
// 场景 7：公式结晶顿悟型 (WB_L08) · 升华金句
// 旁白 18 字：停止感动自己，让努力产生真正的复利！
// ==========================================
{
  const s = {
    id: '07-formula',
    layout: 'WB_L08',
    duration: 5.733,
    narration: '停止感动自己，让努力产生真正的复利！',
    elements: [
      { type: 'title', x: 960, y: 120, text: '告别伪勤奋 · 做高认知行动者', size: 68, color: '#D9381E', align: 'center' },
      { type: 'stickman_victory', x: 960, y: 320, scale: 1.2 }, // 登顶高举红旗
      { type: 'formula_box', x: 360, y: 480, w: 1200, h: 220, fill: '#FFE066', stroke: '#2B2B2B' },
      { type: 'text', x: 960, y: 550, text: '真成长 = 深度思考 × 杠杆行动²', size: 64, color: '#2B2B2B', align: 'center', bold: true },
      { type: 'text', x: 960, y: 630, text: '觉察 ➔ 停顿 ➔ 击穿核心 ➔ 形成复利', size: 36, color: '#1E56A0', align: 'center' }
    ]
  };
  scenes.push(s);
}

module.exports = { scenes };
