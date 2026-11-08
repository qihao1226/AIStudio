#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edl2film.py - 把「结构化剪辑决策」转成 openfilm 工程（film.html）

定位：P2「指定素材 → 自动剪辑」的第 ② 段 —— 承载层。
      autoclip / video-use / openfilm skill long-to-short 产出选片结果（JSON），
      本工具把它落成 openfilm 可 render、可在 Studio 手改、可 export 给剪辑师的工程。

三条关键约束（照 openfilm 协议来，不自创）：
  1. 一条素材反复取片段 → 用 `#t=in,out` 媒体片段，绝不重编码、不切新文件
  2. 同一轨道内片段不得重叠；轨道顺序即层级，第 1 条在最上层
  3. 同一秒必须画出同一张图 → 本工具只生成声明式时间线，不生成任何脚本

用法：
    python3 edl2film.py timeline.json -o ./我的片子            # 生成工程
    python3 edl2film.py timeline.json -o ./我的片子 --check    # 只校验，不写盘
    python3 edl2film.py timeline.json -o ./我的片子 --force    # 覆盖已有目录
    python3 edl2film.py timeline.json -o ./我的片子 --copy     # 复制素材而非软链

输入结构见同目录 examples/timeline.example.json
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

# ---------- 基础工具 ----------

def die(msg, code=1):
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(code)


def num(v):
    """秒数格式化：最多 3 位小数，去掉多余的 0"""
    if v is None:
        return "0"
    s = f"{float(v):.3f}".rstrip("0").rstrip(".")
    return s or "0"


def esc(s):
    """HTML 属性/text 转义"""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


_DUR_CACHE = {}


def probe_duration(path):
    """用 ffprobe 取媒体时长（秒）；缓存，避免同素材重复探测"""
    if path in _DUR_CACHE:
        return _DUR_CACHE[path]
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", path]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        die("找不到 ffprobe，请先安装 ffmpeg")
    raw = (out.stdout or "").strip()
    if out.returncode != 0 or not raw:
        die(f"ffprobe 读不出时长：{path}\n{out.stderr.strip()[:300]}")
    d = float(raw)
    _DUR_CACHE[path] = d
    return d


# ---------- 素材落位 ----------

class AssetStore:
    """把外部素材收进 <片目录>/assets/，保持 openfilm 要求的相对路径访问"""

    def __init__(self, assets_dir, mode="auto"):
        self.assets_dir = assets_dir
        self.mode = mode
        self.map = {}       # 源绝对路径 -> assets 下的文件名
        self.counter = 0
        self.used_mode = None   # auto 模式下实际用了什么

    def _safe_name(self, src):
        base = os.path.basename(src)
        base = re.sub(r"[^\w.\-\u4e00-\u9fff]+", "_", base) or f"asset{self.counter}"
        return base

    def add(self, src_abs):
        if src_abs in self.map:
            return self.map[src_abs]
        self.counter += 1
        name = self._safe_name(src_abs)
        target = os.path.join(self.assets_dir, name)
        # 同名不同源 → 加序号，避免互相覆盖
        if os.path.exists(target) or name in self.map.values():
            stem, ext = os.path.splitext(name)
            name = f"{stem}_{self.counter}{ext}"
            target = os.path.join(self.assets_dir, name)
        self.map[src_abs] = name
        return name

    def _place(self, src, target):
        """按模式落位；auto = 硬链优先，跨卷自动退回复制"""
        if os.path.lexists(target):
            os.remove(target)
        mode = self.mode
        if mode == "auto":
            try:
                os.link(src, target)
                self.used_mode = "hardlink"
                return
            except OSError:
                mode = "copy"
        if mode == "hardlink":
            os.link(src, target)
            self.used_mode = "hardlink"
        elif mode == "symlink":
            os.symlink(src, target)
            self.used_mode = "symlink"
        else:
            shutil.copy2(src, target)
            self.used_mode = "copy"

    def materialize(self):
        os.makedirs(self.assets_dir, exist_ok=True)
        linked = []
        for src_abs, name in self.map.items():
            self._place(src_abs, os.path.join(self.assets_dir, name))
            linked.append(name)
            # 旁挂字幕：openfilm 认「同目录同名 .vtt」自动建字幕轨
            stem, _ = os.path.splitext(src_abs)
            for ext in (".vtt", ".srt"):
                side = stem + ext
                if os.path.exists(side):
                    side_target = os.path.join(self.assets_dir,
                                               os.path.splitext(name)[0] + ext)
                    self._place(side, side_target)
                    linked.append(os.path.basename(side_target))
        return linked


# ---------- 时间线解析与校验 ----------

REQUIRED_TYPE = {"video", "audio", "image", "page"}


def resolve_clips(tl, base_dir):
    """把 JSON 变成内部结构，同时算好每段在成片上的长度"""
    tracks = tl.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        die("JSON 里没有 tracks（至少一条轨道）")

    resolved_tracks = []
    for ti, track in enumerate(tracks, 1):
        clips = track.get("clips") or []
        if not clips:
            print(f"⚠ 轨道 {ti}「{track.get('name', '')}」没有片段，已跳过")
            continue
        resolved = []
        for ci, c in enumerate(clips, 1):
            ctype = c.get("type", "video")
            if ctype not in REQUIRED_TYPE:
                die(f"轨道{ti} 片段{ci}: type 必须是 {sorted(REQUIRED_TYPE)}，收到 {ctype}")
            src = c.get("src")
            if not src:
                die(f"轨道{ti} 片段{ci}: 缺少 src")

            if ctype == "page":
                # 页面是工程内文件，不走 assets
                src_abs = src if os.path.isabs(src) else os.path.join(os.path.dirname(tl["_json_path"]), src)
            else:
                src_abs = src if os.path.isabs(src) else os.path.join(base_dir, src)
            if not os.path.exists(src_abs):
                die(f"轨道{ti} 片段{ci}: 素材不存在 -> {src_abs}")

            in_pt = c.get("in")
            out_pt = c.get("out")
            speed = float(c.get("speed", 1.0))
            if speed < 0.25 or speed > 4:
                die(f"轨道{ti} 片段{ci}: speed 必须在 0.25–4 之间（收到 {speed}）")

            if ctype in ("video", "audio"):
                media_dur = probe_duration(src_abs)
                in_pt = float(in_pt or 0)
                out_pt = float(out_pt) if out_pt is not None else media_dur
                if in_pt < 0:
                    die(f"轨道{ti} 片段{ci}: in 不能为负")
                if out_pt <= in_pt:
                    die(f"轨道{ti} 片段{ci}: out({out_pt}) 必须大于 in({in_pt})")
                if out_pt > media_dur + 0.05:
                    die(f"轨道{ti} 片段{ci}: out({out_pt}) 超出素材时长({media_dur:.3f}s) -> {os.path.basename(src_abs)}")
                length = (out_pt - in_pt) / speed
            else:
                media_dur = None
                dur = c.get("duration")
                if dur is None:
                    die(f"轨道{ti} 片段{ci}: {ctype} 必须给 duration（图上停留秒数）")
                in_pt, out_pt = None, None
                length = float(dur)
                if length <= 0:
                    die(f"轨道{ti} 片段{ci}: duration 必须大于 0")

            at = float(c.get("at", 0))
            if at < 0:
                die(f"轨道{ti} 片段{ci}: at 不能为负")

            resolved.append({
                "type": ctype, "src": src, "src_abs": src_abs,
                "in": in_pt, "out": out_pt, "at": at, "speed": speed,
                "length": length, "media_dur": media_dur,
                "volume": c.get("volume"), "muted": bool(c.get("muted", False)),
                "style": c.get("style") or {}, "klass": c.get("class"),
                "id": c.get("id"), "overrides": c.get("overrides"),
                "note": c.get("note"), "size": c.get("size"),
                "ti": ti, "ci": ci,
            })
        resolved.sort(key=lambda x: x["at"])
        resolved_tracks.append({
            "name": track.get("name", f"轨道{ti}"),
            "hidden": bool(track.get("hidden", False)),
            "muted": bool(track.get("muted", False)),
            "locked": bool(track.get("locked", False)),
            "clips": resolved,
        })
    if not resolved_tracks:
        die("所有轨道都没有片段")
    return resolved_tracks


def check(tracks):
    """结构校验：重叠、空档、总时长；返回 (warnings, total_duration)"""
    warns = []
    for t in tracks:
        prev_end = None
        prev_name = None
        for c in t["clips"]:
            if prev_end is not None and c["at"] < prev_end - 1e-6:
                die(f"轨道「{t['name']}」片段重叠：{prev_name} 结束于 {prev_end:.3f}s，"
                    f"但下一段从 {c['at']:.3f}s 开始（openfilm 同轨不允许重叠，"
                    f"叠画面请拆到不同轨道）")
            if prev_end is not None and c["at"] - prev_end > 1e-6:
                warns.append(f"轨道「{t['name']}」在 {prev_end:.3f}s → {c['at']:.3f}s 有 {c['at']-prev_end:.2f}s 空档（该轨此段无画面）")
            prev_end = c["at"] + c["length"]
            prev_name = c.get("note") or f"片段{c['ci']}"

    total = max((c["at"] + c["length"]) for t in tracks for c in t["clips"])

    # 画面覆盖：把所有「有画面」的片段并起来，找 [0, total] 内的空档（空档 = 成片黑帧）
    spans = sorted(
        (c["at"], c["at"] + c["length"])
        for t in tracks for c in t["clips"]
        if c["type"] in ("video", "image", "page")
    )
    cursor = 0.0
    for start, end in spans:
        if start > cursor + 1e-6:
            warns.append(f"成片 {cursor:.2f}s → {start:.2f}s 无任何画面轨覆盖，将出黑帧")
        cursor = max(cursor, end)
    if cursor < total - 1e-6:
        warns.append(f"成片 {cursor:.2f}s → {total:.2f}s 无画面覆盖，将出黑帧")
    return warns, total


# ---------- HTML 生成 ----------

def clip_src_attr(c, store):
    """拼出 openfilm 的 src：媒体片段 + 相对路径"""
    if c["type"] == "page":
        # 页面按「相对 film.html 的路径」原样引用，保证它自己的相对依赖不破
        return f"{c['src']}#t=0,{num(c['length'])}"
    name = store.add(c["src_abs"])
    rel = f"assets/{name}"
    if c["type"] == "image":
        return f"{rel}#t=0,{num(c['length'])}"
    # video / audio：始终写显式片段，交给 openfilm 明确"从哪到哪"
    return f"{rel}#t={num(c['in'])},{num(c['out'])}"


def style_attr(c):
    """style 字典 + 通用约束 → 内联 CSS 字符串"""
    st = dict(c["style"] or {})
    parts = []
    for key in ("left", "top", "width", "height"):
        if st.get(key) is not None:
            v = st[key]
            parts.append(f"{key}: {v}px" if isinstance(v, (int, float)) else f"{key}: {v}")
    if st.get("rotate") is not None:
        parts.append(f"transform: rotate({st['rotate']}deg)")
    if st.get("objectFit"):
        parts.append(f"object-fit: {st['objectFit']}")
    if st.get("objectPosition"):
        parts.append(f"object-position: {st['objectPosition']}")
    if st.get("borderRadius") is not None:
        v = st["borderRadius"]
        parts.append(f"border-radius: {v}px" if isinstance(v, (int, float)) else f"border-radius: {v}")
    if st.get("opacity") is not None:
        parts.append(f"opacity: {st['opacity']}")
    if st.get("filter"):
        parts.append(f"filter: {st['filter']}")
    # 用户在 style 里给的其它原始 CSS 键，直接透传
    for k, v in (st.get("raw") or {}).items():
        parts.append(f"{k}: {v}")
    return "; ".join(parts)


def build_html(tl, tracks, store, total, out_dir):
    """生成 film.html。page 类型按相对 film.html 的路径引用，且必须已落在片目录内"""
    w = int(tl.get("width", 1920))
    h = int(tl.get("height", 1080))
    title = tl.get("name", "film")

    # page 类型：必须在片目录里，否则它的相对依赖会断
    for t in tracks:
        for c in t["clips"]:
            if c["type"] != "page":
                continue
            inside = os.path.join(out_dir, c["src"])
            if not os.path.exists(inside):
                die(f"page 片段「{c['src']}」不在片目录内 -> {inside}\n"
                    f"  页面必须放在片目录里（例如 scenes/01.html），因为页面按相对路径加载自己的依赖。\n"
                    f"  解决：先把页面文件拷进 {out_dir}，或在 JSON 里把 src 写成片目录内的相对路径。")

    lines = [
        "<!doctype html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        f'<meta name="viewport" content="width={w}, height={h}">',
        f"<title>{esc(title)}</title>",
        "<style>",
        "  /* 全局：成片画布。位置/尺寸请写在每个片段的 style 里，这里只放通用类 */",
        "  body { margin: 0; background: #000; }",
        *[f"  .{esc(k)} {{ {v} }}" for k, v in (tl.get("classes") or {}).items()],
        "</style>",
        "</head>",
        "<body>",
        f"<!-- {esc(title)} ｜ 由 edl2film.py 生成 ｜ 总长 {num(total)}s ｜ 轨道 {len(tracks)} 条 ｜ 片段 {sum(len(t['clips']) for t in tracks)} 个 -->",
        "<!-- 轨道顺序 = 层级，第一条在最上层。改这份文件即可手改剪辑，改完交给 openfilm 渲染 -->",
    ]
    seq = 0
    for i, t in enumerate(tracks, 1):
        attrs = [f'id="track{i}"']
        if t["hidden"]:
            attrs.append("hidden")
        if t["muted"]:
            attrs.append("muted")
        if t["locked"]:
            attrs.append("locked")
        label = "（最上层）" if i == 1 else ""
        lines.append("")
        lines.append(f"<!-- 轨道 {i}{label}：{esc(t['name'])} -->")
        lines.append(f"<section {' '.join(attrs)}>")
        for c in t["clips"]:
            seq += 1
            tag = {"video": "video", "audio": "audio",
                   "image": "img", "page": "iframe"}[c["type"]]
            a = [f'src="{esc(clip_src_attr(c, store))}"']
            if c["type"] in ("video", "audio", "image", "page"):
                a.append(f'at="{num(c["at"])}"')
            if c["type"] in ("video", "audio") and c["speed"] != 1.0:
                a.append(f'speed="{num(c["speed"])}"')
            if c["type"] in ("video", "audio") and c["volume"] is not None:
                a.append(f'volume="{num(c["volume"])}"')
            if c["muted"]:
                a.append("muted")
            if c["type"] == "page" and c.get("size"):
                a.append(f'size="{esc(c["size"])}"')
            # 同一素材切多段时，openfilm 默认用文件名当 id 会撞成同一个 → 必须逐段给唯一 id
            cid = c["id"] or f"{re.sub(r'[^0-9A-Za-z_-]', '_', os.path.splitext(os.path.basename(c['src']))[0])}_{seq}"
            a.append(f'id="{esc(cid)}"')
            if c["klass"]:
                a.append(f'class="{esc(c["klass"])}"')
            if c["overrides"]:
                a.append(f"overrides='{esc(json.dumps(c['overrides'], ensure_ascii=False))}'")
            st = style_attr(c)
            if st:
                a.append(f'style="{esc(st)}"')
            note = f"  <!-- {esc(c['note'])} -->" if c.get("note") else ""
            lines.append(f"  <{tag} {' '.join(a)}>{'' if tag == 'img' else '</' + tag + '>'}{note}")
        lines.append("</section>")
    lines.append("")
    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines) + "\n"


# ---------- 入口 ----------

def main():
    ap = argparse.ArgumentParser(description="结构化剪辑决策 → openfilm 工程（film.html）")
    ap.add_argument("timeline", help="时间线 JSON 路径")
    ap.add_argument("-o", "--out", help="输出片目录（默认 ./<name>）")
    ap.add_argument("--assets", help="素材根目录（覆盖 JSON 里的 assets 字段）")
    ap.add_argument("--width", type=int, help="覆盖画幅宽")
    ap.add_argument("--height", type=int, help="覆盖画幅高")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的非空目录")
    ap.add_argument("--check", action="store_true", help="只校验，不写盘")
    ap.add_argument("--link-mode", choices=["auto", "hardlink", "copy", "symlink"],
                    default="auto",
                    help="素材落位方式：auto=硬链优先/跨卷退复制（默认）；symlink 会被 openfilm 拒为 403")
    args = ap.parse_args()

    if not os.path.exists(args.timeline):
        die(f"时间线文件不存在：{args.timeline}")
    with open(args.timeline, encoding="utf-8") as f:
        try:
            tl = json.load(f)
        except json.JSONDecodeError as e:
            die(f"JSON 解析失败：{e}")
    tl["_json_path"] = os.path.abspath(args.timeline)

    base_dir = args.assets or tl.get("assets") or os.path.dirname(tl["_json_path"])
    base_dir = os.path.abspath(base_dir)
    if not os.path.isdir(base_dir):
        die(f"素材目录不存在：{base_dir}")
    if args.width:
        tl["width"] = args.width
    if args.height:
        tl["height"] = args.height

    tracks = resolve_clips(tl, base_dir)
    warns, total = check(tracks)

    print(f"✓ 解析完成：{len(tracks)} 条轨道 / {sum(len(t['clips']) for t in tracks)} 个片段 / 总长 {num(total)}s")
    print(f"  画幅 {tl.get('width', 1920)}×{tl.get('height', 1080)} ｜ 素材根 {base_dir}")
    for w in warns:
        print(f"  ⚠ {w}")

    if args.check:
        print("\n（--check 模式，未写盘）")
        return

    out = os.path.abspath(args.out or tl.get("name", "film").replace("/", "_"))
    if os.path.isdir(out) and os.listdir(out) and not args.force:
        die(f"输出目录非空：{out}\n如确认覆盖请加 --force")
    os.makedirs(out, exist_ok=True)

    store = AssetStore(os.path.join(out, "assets"), mode=args.link_mode)
    html = build_html(tl, tracks, store, total, out)     # 先遍历一遍收集素材
    linked = store.materialize()

    with open(os.path.join(out, "film.html"), "w", encoding="utf-8") as f:
        f.write(html)
    # 把时间线一并存进工程，便于复盘/重生成
    with open(os.path.join(out, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in tl.items() if not k.startswith("_")},
                  f, ensure_ascii=False, indent=2)

    print(f"✓ 已生成 {out}")
    print(f"  film.html / timeline.json / assets/（{len(linked)} 个文件，{store.used_mode or args.link_mode}）")
    print("\n下一步：")
    print(f"  cd {out}")
    print("  npx -y openfilm@latest open      # Studio 手改（改完记得校验 chromium）")
    print("  npx -y openfilm@latest look      # 确定性体检 + 接触表")
    print("  npx -y openfilm@latest render    # 出 MP4")
    print("  npx -y openfilm@latest export    # 出 FCPXML/Premiere/DaVinci 交剪辑师")


if __name__ == "__main__":
    main()
