#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""director_critique.py — 导演自评（建造者迭代，非评分）

读「计划（storyboard + tokens + cue sheet）」与「执行（render probe）」，
输出 5 维**待改清单**（P0–P3）。**不输出 PASS/FAIL**——裁决权归独立评审。

铁律:
  · 无渲染证据 → 相关维度标「待证据」，不得下结论
  · 不宣布通过（本件只能提改进项）
  · 与 motion-film-qa（独立评判）职责分开：本件是建造者视角

用法:
  python3 director_critique.py --storyboard SB.md [--tokens T.json] \
      [--cue C.json] [--probe P.json] [--subtitle-band 872,916] --out report.md
依赖: 仅标准库
"""
import argparse
import json
import os
import re
import sys

CORE_RE = re.compile(r"<!--STORYBOARD-CORE[ \t]*\n(.*?)\n[ \t]*-->", re.S)
HEAVY_TRANSITIONS = {"zoom", "mask_morph"}
BAND_MAX_HOLD_DEFAULT = {"S": 3, "M": 4, "L": 5}
BAND_NEW_STIM_DEFAULT = {"S": 10, "M": 20, "L": 30}


def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def default_tokens():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(
        here, "..", "..", "brand-motion-tokens", "tokens", "brand-motion-tokens.json"))


def parse_core(path):
    with open(path, "r", encoding="utf-8") as f:
        md = f.read()
    m = CORE_RE.search(md)
    if not m:
        raise ValueError("分镜缺 STORYBOARD-CORE 块")
    return json.loads(m.group(1).strip())


class Report:
    def __init__(self):
        self.items = []   # dict(dim, level, text, action)

    def add(self, dim, level, text, action):
        self.items.append({"dim": dim, "level": level, "text": text, "action": action})

    def by_level(self):
        order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        return sorted(self.items, key=lambda x: order.get(x["level"], 9))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--storyboard", required=True)
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--cue", default=None)
    ap.add_argument("--probe", default=None)
    ap.add_argument("--subtitle-band", default="872,916")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tok_path = a.tokens or default_tokens()
    tok = load_json(tok_path) if os.path.isfile(tok_path) else {}
    core = parse_core(a.storyboard)
    cue = load_json(a.cue) if (a.cue and os.path.isfile(a.cue)) else None
    probe = load_json(a.probe) if (a.probe and os.path.isfile(a.probe)) else None

    brief = core.get("brief", {})
    design = core.get("design", {})
    scenes = core.get("scenes", [])
    band = brief.get("length_band", "M")

    caps = tok.get("motion", {}).get("caps", {})
    cap_el = caps.get("max_simultaneous_elements", 3)
    density = tok.get("motion", {}).get("density", {})
    band_cfg = tok.get("motion", {}).get("rhythm", {}).get("by_length_band", {}).get(band, {})
    max_hold = band_cfg.get("max_hold_s", BAND_MAX_HOLD_DEFAULT.get(band, 4))
    new_stim = band_cfg.get("new_stimulus_s", BAND_NEW_STIM_DEFAULT.get(band, 20))

    rep = Report()

    # ---------- 维度1 Hook ----------
    hook_scenes = [s for s in scenes if (s.get("start") or 0) < 3.0]
    if len(hook_scenes) >= 2:
        pass
    else:
        rep.add("Hook", "P1", "开场 3s 内仅 %d 个场景段起，首 3 秒缺乏变化" % len(hook_scenes),
                "在首 3 秒内增加一次视觉变化（切点或动效）")
    hook_txt = "".join((s.get("text") or "") for s in scenes if (s.get("start") or 0) < 3.0)
    if not hook_txt.strip():
        rep.add("Hook", "P1", "开场 3 秒无文案（钩子缺失）", "为钩子场景补一句强观点")
    if probe:
        first_lum = probe.get("probe", {}).get("first_frame_lum")
        if first_lum is not None and first_lum < 3:
            rep.add("Hook", "P0", "首帧亮度仅 %.1f（疑似空帧/黑帧）" % first_lum,
                    "核首帧是否为完整构图")
    else:
        rep.add("Hook", "待证据", "无渲染探针，无法判断开场是否真在动", "运行 render_probe.py 后复评")

    # ---------- 维度2 视觉焦点 ----------
    for s in scenes:
        el = s.get("elements")
        if isinstance(el, int) and el > cap_el:
            rep.add("视觉焦点", "P1", "场景 %s 同屏元素 %d > 上限 %d" % (s.get("id"), el, cap_el),
                    "拆分为两拍或降元素数")
    no_focal = [s.get("id") for s in scenes if not s.get("role_ref") and (s.get("role") not in ("主体",))]
    if len(no_focal) == len(scenes) and scenes:
        rep.add("视觉焦点", "P3", "全片未声明任何出镜角色（role_ref 全空）",
                "若应有品牌出镜，补 role_ref；若为纯图文片，忽略此项")

    # ---------- 维度3 场景衔接/转场 ----------
    heavy_run = 1
    max_run = 1
    prev_heavy = False
    for s in scenes:
        t = s.get("transition_in")
        is_h = t in HEAVY_TRANSITIONS
        heavy_run = heavy_run + 1 if (is_h and prev_heavy) else (1 if is_h else 0)
        max_run = max(max_run, heavy_run)
        prev_heavy = is_h
    if max_run >= 2:
        rep.add("场景衔接", "P2", "出现连续 %d 个重转场（zoom/mask_morph）" % max_run,
                "择一改为硬切或溶解，避免转场打架")

    # ---------- 维度4 节奏密度 ----------
    if probe:
        longest = probe.get("near_frozen_longest_run_s", 0.0)
        if longest > max_hold + 1e-6:
            rep.add("节奏密度", "P1",
                    "最长近静止段 %.2fs > %s 带上限 %.1fs" % (longest, band, max_hold),
                    "在该段内插入一次视觉变化")
        # 报分布，不报单值（沿用教训）
        froz = probe.get("frozen_multi_threshold", {})
        rep.add("节奏密度", "P3",
                "近冻结多阈值(供轮次间比较，勿当绝对值): %s" % json.dumps(froz, ensure_ascii=False),
                "仅用于同片不同轮次对比，阈值须按片调")
    else:
        rep.add("节奏密度", "待证据", "无渲染探针，无法测实际静止段", "运行 render_probe.py 后复评")

    # ---------- 维度5 整体吸引力（新刺激间隔） ----------
    if probe:
        series = probe.get("samples_series", [])
        # 相邻样点差 > 阈值 视为一次"新刺激"
        stim_ts = [s["t"] for s in series[1:] if s.get("diff", 0) >= 0.35]
        gaps = []
        prev = 0.0
        for t in stim_ts:
            gaps.append(t - prev)
            prev = t
        if gaps:
            mx = max(gaps)
            if mx > new_stim + 1e-6:
                rep.add("整体吸引力", "P2",
                        "最长无新刺激间隔 %.2fs > 目标 %ss" % (mx, new_stim),
                        "在该间隔中点安排一次视觉刺激")
        else:
            rep.add("整体吸引力", "待证据", "探针未检出任何强变化点（阈值可能需按片调）",
                    "人工目检确认或调低阈值重跑")

    # ---------- 附加A：文字区撞位预检（P0 类，机械拦截） ----------
    band_lo, band_hi = [float(x) for x in a.subtitle_band.split(",")]
    for s in scenes:
        zones = s.get("zones") or []
        if "sub" in zones and "caption" in zones:
            rep.add("视觉焦点", "P0",
                    "场景 %s 同时声明 sub 与 caption 区（二者在 y≈%d–%d 重叠）" % (s.get("id"), band_lo, band_hi),
                    "删除其一或下移 sub 至 %d 以上" % (band_lo - 40))

    # ---------- 附加B：时长一致性（计划 vs 实测） ----------
    if cue is not None:
        cue_total = cue.get("meta", {}).get("total_duration_s")
        sb_total = brief.get("duration_s")
        if cue_total is not None and sb_total is not None:
            if abs(cue_total - sb_total) > 0.5:
                rep.add("整体吸引力", "P0",
                        "分镜目标时长 %.2fs 与 cue sheet 实测总长 %.2fs 不符（差 %.2fs）"
                        % (sb_total, cue_total, abs(cue_total - sb_total)),
                        "以 cue sheet 实测值为准，回填分镜目标时长")
    else:
        rep.add("整体吸引力", "待证据",
                "未提供 cue sheet，无法核对「计划时长 vs 音频实测时长」",
                "传入 --cue 后复评")

    # ---------- 输出 ----------
    lines = []
    lines.append("# 导演自评报告（建造者迭代 · 非裁决）")
    lines.append("")
    lines.append("> ⚠️ **本报告不是 PASS/FAIL 裁决。** 裁决权归独立评审（motion-film-qa Gauntlet）。")
    lines.append("> 本件只输出**待改清单**，供建造者做下一版。")
    lines.append("")
    lines.append("| 项 | 值 |")
    lines.append("|---|---|")
    lines.append("| 片名 | %s |" % brief.get("title", ""))
    lines.append("| 长度带 | %s |" % band)
    lines.append("| 目标时长 | %ss |" % brief.get("duration_s"))
    lines.append("| 场景段数 | %d |" % len(scenes))
    lines.append("| 渲染证据 | %s |" % ("已提供" if probe else "**缺失**"))
    lines.append("")
    items = rep.by_level()
    if not items:
        lines.append("## 待改清单")
        lines.append("")
        lines.append("机械检查未发现问题。**但请注意**：这**不等于**片子在视觉与商业上合格——")
        lines.append("画面硬伤、静音可懂性等需**独立评审**与**抽帧目检**。")
    else:
        lines.append("## 待改清单（按优先级）")
        lines.append("")
        lines.append("| 级别 | 维度 | 问题 | 建议动作 |")
        lines.append("|---|---|---|---|")
        for it in items:
            lines.append("| **%s** | %s | %s | %s |" % (it["level"], it["dim"], it["text"], it["action"]))
    lines.append("")
    lines.append("## 5 维覆盖")
    lines.append("")
    dims = ["Hook", "视觉焦点", "场景衔接", "节奏密度", "整体吸引力"]
    for d in dims:
        hits = [i for i in items if i["dim"] == d]
        state = "待改 %d 项" % len(hits) if hits else "未发现问题"
        lines.append("- **%s**：%s" % (d, state))
    lines.append("")
    lines.append("> 下一步：按 P0→P3 修复后出 v2，再交**独立评审**复验（建造者不得自判通过）。")

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    n_by = {}
    for it in items:
        n_by[it["level"]] = n_by.get(it["level"], 0) + 1
    print("已写出 %s" % a.out)
    print("  待改项: %s" % (json.dumps(n_by, ensure_ascii=False) if n_by else "无"))
    print("  裁决: 本报告不给出（裁决权归独立评审）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
