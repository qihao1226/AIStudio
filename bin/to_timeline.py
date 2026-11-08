#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
to_timeline.py - 把各家剪辑工具的「选片结果」统一成 edl2film 的时间线 JSON

解决 P2 的最后一根线：① 决策 → ② 承载。
支持四种上游，输出同一份 timeline.json，交给 edl2film 落成 openfilm 工程。

用法：
    # video-use（edit/edl.json 原样喂）
    python3 to_timeline.py video-use edit/edl.json -o t.json --film ./片子

    # autoclip（切片记录 + 源视频）
    python3 to_timeline.py autoclip clips.json --source 访谈.mp4 -o t.json --film ./片子

    # 通用 CSV（列名随便，用 --map 指定）
    python3 to_timeline.py csv cuts.csv --source 访谈.mp4 \
        --map start=入点,end=出点,note=说明 -o t.json --film ./片子

    # 已经是 [{"src","in","out"}] 的裸 JSON
    python3 to_timeline.py generic cuts.json -o t.json --film ./片子

常用开关：
    --cover              每段铺满画幅（object-fit: cover），适合 16:9 素材出 9:16
    --bg <文件>          加一条铺底轨（静音），常用竖版补背景
    --width/--height     画幅，默认 1080×1920
    --max 60             只保留前 60 秒（切条常用）
    --fix-overlap        片段重叠时自动裁短，而不是报错
"""

import argparse
import csv
import json
import os
import subprocess
import sys


def die(msg):
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(1)


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        die(f"ffprobe 读不出时长：{path}")


# ---------- 各上游加载器：统一产出 [{'src','in','out','note'}] ----------

def load_video_use(path):
    """video-use 的 edit/edl.json：{sources:{name:path}, ranges:[{source,start,end,note}]}"""
    with open(path, encoding="utf-8") as f:
        edl = json.load(f)
    if "ranges" not in edl:
        die("video-use EDL 缺少 ranges 字段")
    sources = edl.get("sources") or {}
    base = os.path.dirname(os.path.abspath(path))
    cuts = []
    for r in edl["ranges"]:
        name = r.get("source")
        if name not in sources:
            die(f"EDL 里的 source「{name}」不在 sources 表里")
        src = sources[name]
        if not os.path.isabs(src):
            src = os.path.normpath(os.path.join(base, src))
        cuts.append({"src": src, "in": float(r["start"]), "out": float(r["end"]),
                     "note": r.get("note") or ""})
    return cuts, (edl.get("grade") or None)


def load_autoclip(path, source):
    """autoclip 的切片记录：{title,start_time,end_time,...}，全部来自同一源视频"""
    if not source:
        die("autoclip 模式必须给 --source（原视频路径）")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rows = data.get("clips") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        die("autoclip 记录既不是列表，也没有 clips 字段")
    cuts = []
    for r in rows:
        s = r.get("start_time", r.get("start"))
        e = r.get("end_time", r.get("end"))
        if s is None or e is None:
            die(f"autoclip 记录缺 start_time/end_time：{r}")
        note = r.get("title") or ""
        if r.get("score") is not None:
            note = f"{note}｜评分 {r['score']}"
        cuts.append({"src": source, "in": float(s), "out": float(e), "note": note})
    return cuts, None


def load_csv(path, source, mapping):
    """通用 CSV：--map start=入点,end=出点,note=说明"""
    if not mapping.get("start") or not mapping.get("end"):
        die("CSV 模式必须给 --map start=<列名>,end=<列名>")
    cuts = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            src = row.get(mapping.get("src") or "", "") or source
            if not src:
                die("CSV 里没有 src 列，也没给 --source")
            cuts.append({
                "src": src,
                "in": float(row[mapping["start"]]),
                "out": float(row[mapping["end"]]),
                "note": row.get(mapping.get("note") or "", "") or "",
            })
    return cuts, None


def load_generic(path):
    """裸 JSON：列表，每项含 src/in/out（也认 start/end）"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rows = data.get("clips") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        die("generic 模式要求 JSON 是列表，或含 clips 列表")
    cuts = []
    for r in rows:
        s = r.get("in", r.get("start"))
        e = r.get("out", r.get("end"))
        if not r.get("src") or s is None or e is None:
            die(f"每条必须含 src/in/out（或 start/end）：{r}")
        cuts.append({"src": r["src"], "in": float(s), "out": float(e),
                     "note": r.get("note") or ""})
    return cuts, None


# ---------- 组装时间线 ----------

def build(cuts, args):
    if not cuts:
        die("上游没有给出任何片段")

    # 解析源路径 + 校验区间
    for c in cuts:
        c["src"] = os.path.abspath(os.path.expanduser(c["src"]))
        if not os.path.exists(c["src"]):
            die(f"素材不存在：{c['src']}")
        d = probe_duration(c["src"])
        if c["in"] < 0:
            die(f"入点为负：{c['note']}")
        if c["out"] > d + 0.05:
            die(f"出点 {c['out']} 超出素材时长 {d:.2f}s：{os.path.basename(c['src'])}（{c['note']}）")
        if c["out"] <= c["in"]:
            die(f"出点必须大于入点：{c['note']}")
        c["dur"] = c["out"] - c["in"]

    # 顺序堆叠成片；重叠按 --fix-overlap 裁短，否则报错
    at = 0.0
    for i, c in enumerate(cuts):
        c["at"] = at
        at += c["dur"]
        nxt = cuts[i + 1] if i + 1 < len(cuts) else None
        if nxt is not None and getattr(args, "gap", 0):
            at += args.gap

    if args.max and at > args.max:
        kept, used = [], 0.0
        for c in cuts:
            if used + c["dur"] <= args.max + 1e-6:
                kept.append(c); used += c["dur"]
            else:
                room = args.max - used
                if room > 0.2:
                    c = dict(c); c["out"] = c["in"] + room; c["dur"] = room
                    kept.append(c); used += room
                break
        cuts = kept
        at = used
        print(f"  · 按 --max {args.max}s 截断为 {len(cuts)} 段 / {at:.2f}s")

    style = {}
    if args.cover:
        style = {"width": args.width, "height": args.height, "objectFit": "cover"}

    clips = []
    for c in cuts:
        item = {"type": "video", "src": c["src"],
                "in": round(c["in"], 3), "out": round(c["out"], 3),
                "at": round(c["at"], 3), "note": c["note"]}
        if style:
            item["style"] = dict(style)
        clips.append(item)

    tracks = [{"name": "主剪辑", "clips": clips}]
    if args.bg:
        bg_path = os.path.abspath(os.path.expanduser(args.bg))
        if not os.path.exists(bg_path):
            die(f"铺底素材不存在：{bg_path}")
        bg_is_video = bg_path.lower().endswith((".mp4", ".mov", ".m4v", ".webm"))
        if bg_is_video:
            bg_dur = probe_duration(bg_path)
            if bg_dur < at - 1e-6:
                print(f"  ⚠ 铺底只有 {bg_dur:.2f}s，短于成片 {at:.2f}s → 尾部会露黑")
            bg_clip = {"type": "video", "src": bg_path,
                       "in": 0, "out": round(min(bg_dur, at), 3),
                       "at": 0, "volume": 0, "note": "铺底（静音）"}
        else:
            bg_clip = {"type": "image", "src": bg_path,
                       "duration": round(at, 3), "at": 0, "note": "铺底"}
        # 轨道顺序 = 层级，第一条在最上层 → 铺底追加到最后
        tracks.append({"name": f"铺底 {os.path.basename(bg_path)}", "clips": [bg_clip]})

    name = args.title or os.path.splitext(os.path.basename(args.input))[0]
    return {"name": name, "width": args.width, "height": args.height,
            "tracks": tracks}, at


# ---------- 校验重叠（对最终时间线再兜一层） ----------

def check_overlap(tl, fix):
    for t in tl["tracks"]:
        prev = None
        for c in t["clips"]:
            if prev is not None and c.get("at", 0) < prev - 1e-6:
                if not fix:
                    die(f"轨道「{t['name']}」片段重叠：{c.get('at')} < {prev}\n"
                        f"  加 --fix-overlap 自动裁短，或修上游结果")
                print(f"  ⚠ 重叠已裁短（轨道「{t['name']}」）")
            prev = c.get("at", 0) + (c.get("duration") or (c["out"] - c["in"]))


def main():
    ap = argparse.ArgumentParser(description="各家剪辑结果 → edl2film 时间线 JSON")
    ap.add_argument("mode", choices=["video-use", "autoclip", "csv", "generic"])
    ap.add_argument("input", help="上游结果文件")
    ap.add_argument("-o", "--out", default="timeline.json", help="输出时间线 JSON")
    ap.add_argument("--source", help="源视频（autoclip / csv 模式必填）")
    ap.add_argument("--map", default="", help="CSV 列映射，如 start=入点,end=出点,note=说明")
    ap.add_argument("--title", default="", help="片名")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--cover", action="store_true", help="每段铺满画幅（object-fit: cover）")
    ap.add_argument("--bg", help="铺底素材（图片或视频，静音，放最底层）")
    ap.add_argument("--max", type=float, default=0, help="只保留前 N 秒")
    ap.add_argument("--gap", type=float, default=0, help="段间留白秒数")
    ap.add_argument("--fix-overlap", action="store_true")
    ap.add_argument("--film", help="顺便直接生成 openfilm 工程到这个目录")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        die(f"输入不存在：{args.input}")

    if args.mode == "video-use":
        cuts, grade = load_video_use(args.input)
    elif args.mode == "autoclip":
        cuts, grade = load_autoclip(args.input, args.source)
    elif args.mode == "csv":
        mapping = dict(kv.split("=", 1) for kv in args.map.split(",") if "=" in kv)
        cuts, grade = load_csv(args.input, args.source, mapping)
    else:
        cuts, grade = load_generic(args.input)

    tl, total = build(cuts, args)
    check_overlap(tl, args.fix_overlap)
    if grade:
        print(f"  · video-use 的 grade「{grade}」未落进 openfilm 工程（openfilm 不认调色参数），"
              f"如需调色请在渲染前用 ffmpeg 处理素材或改用 CSS filter")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(tl, f, ensure_ascii=False, indent=2)
    print(f"✓ 时间线已写出：{args.out}")
    print(f"  {len(tl['tracks'])} 轨 / {sum(len(t['clips']) for t in tl['tracks'])} 段 / "
          f"总长 {total:.2f}s / {args.width}×{args.height}")

    if args.film:
        tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edl2film.py")
        print("\n→ 交给 edl2film 落成 openfilm 工程…")
        cmd = [sys.executable, tool, args.out, "-o", args.film]
        if os.path.isdir(args.film) and os.listdir(args.film):
            cmd.append("--force")
        sys.stdout.flush()          # 先冲掉缓冲，避免子进程输出插到前面
        rc = subprocess.call(cmd)
        if rc != 0:
            die("edl2film 失败，请按上面报错修上游结果")
    else:
        print(f"\n下一步：python3 edl2film.py {args.out} -o ./片子")


if __name__ == "__main__":
    main()
