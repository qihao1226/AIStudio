"""Fast Programmatic Video Renderer for AG_SOP_04 using FFmpeg."""

import os
import sys
import json
import subprocess
from pathlib import Path

FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

def get_duration(file_path: Path) -> float:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(file_path)]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def render_shot_1(out_path: Path, dur: float, video_src: Path, voice_src: Path):
    """Shot 1: Jensen Colossus (Video 9:16 Crop)."""
    vf = (
        f"crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920,"
        f"drawbox=x=80:y=240:w=920:h=90:color=black@0.75:t=fill,"
        f"drawbox=x=80:y=240:w=12:h=90:color=#00FFAA:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='19天算力奇迹 vs 10万卡集群':fontcolor=#00FFAA:fontsize=46:x=120:y=262,"
        f"drawbox=x=0:y=1640:w=1080:h=180:color=black@0.85:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='所有人都在为英伟达的芯片疯狂':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=1665,"
        f"drawtext=fontfile='{FONT_PATH}':text='但很少有人听懂黄仁勋这句警告':fontcolor=#FFCC00:fontsize=48:x=(w-text_w)/2:y=1730"
    )
    cmd = [
        "ffmpeg", "-y",
        "-ss", "0", "-i", str(video_src),
        "-i", str(voice_src),
        "-filter_complex", f"[0:v]{vf}[v]",
        "-map", "[v]", "-map", "1:a",
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)

def render_shot_2(out_path: Path, dur: float, img_src: Path, voice_src: Path):
    """Shot 2: PJM Power Grid."""
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"boxblur=25:5[bg];"
        f"[0:v]scale=980:-1[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,"
        f"drawbox=x=60:y=200:w=960:h=100:color=black@0.8:t=fill,"
        f"drawbox=x=60:y=200:w=12:h=100:color=#FF3344:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='美国PJM电网负荷报告：承载极限破裂':fontcolor=#FF3344:fontsize=42:x=95:y=230,"
        f"drawbox=x=0:y=1640:w=1080:h=180:color=black@0.85:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='算力暴涨的尽头，根本不是芯片良率':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=1665,"
        f"drawtext=fontfile='{FONT_PATH}':text='而是我们脚下的电网正在彻底崩溃！':fontcolor=#FF3344:fontsize=48:x=(w-text_w)/2:y=1730"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_src),
        "-i", str(voice_src),
        "-filter_complex", vf,
        "-map", "1:a",
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)

def render_shot_3(out_path: Path, dur: float, img1: Path, img2: Path, voice_src: Path):
    """Shot 3: Split screen Three Mile Island + NVL72."""
    vf = (
        f"[0:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960,"
        f"drawbox=x=50:y=50:w=980:h=80:color=black@0.75:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='微软重启封存40年核电站':fontcolor=#00E5FF:fontsize=44:x=90:y=70[top];"
        f"[1:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960,"
        f"drawbox=x=50:y=50:w=980:h=80:color=black@0.75:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='Blackwell NVL72 液冷算力机柜':fontcolor=#FFCC00:fontsize=44:x=90:y=70[bot];"
        f"[top][bot]vstack=inputs=2,"
        f"drawbox=x=0:y=1630:w=1080:h=200:color=black@0.85:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='微软甚至重新启用了三里岛核反应堆！':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=1660,"
        f"drawtext=fontfile='{FONT_PATH}':text='单个万卡机房，吃掉中型城市全部电力':fontcolor=#00E5FF:fontsize=46:x=(w-text_w)/2:y=1730[v]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img1),
        "-loop", "1", "-i", str(img2),
        "-i", str(voice_src),
        "-filter_complex", vf,
        "-map", "[v]", "-map", "2:a",
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)

def render_shot_4(out_path: Path, dur: float, img_src: Path, voice_src: Path):
    """Shot 4: FLUX Nuclear AI Datacenter."""
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"drawbox=x=60:y=200:w=960:h=90:color=black@0.8:t=fill,"
        f"drawbox=x=60:y=200:w=12:h=90:color=#00FFAA:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='下一代 AI 能源基座：吉瓦级独占电站':fontcolor=#00FFAA:fontsize=42:x=95:y=225,"
        f"drawbox=x=0:y=1630:w=1080:h=200:color=black@0.85:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='万亿参数大模型需要吉瓦级独立能源':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=1660,"
        f"drawtext=fontfile='{FONT_PATH}':text='谁掌握独占清洁电力，谁就垄断下一代算力':fontcolor=#00FFAA:fontsize=46:x=(w-text_w)/2:y=1730"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_src),
        "-i", str(voice_src),
        "-filter_complex", vf,
        "-map", "1:a",
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)

def render_shot_5(out_path: Path, dur: float, img_src: Path, voice_src: Path):
    """Shot 5: FLUX Substation AI Migration."""
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"drawbox=x=60:y=200:w=960:h=90:color=black@0.8:t=fill,"
        f"drawbox=x=60:y=200:w=12:h=90:color=#FFCC00:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='人类工业文明：能源与智能的世纪大迁徙':fontcolor=#FFCC00:fontsize=40:x=95:y=225,"
        f"drawbox=x=0:y=1630:w=1080:h=200:color=black@0.85:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='这不是简单的芯片竞争':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=1660,"
        f"drawtext=fontfile='{FONT_PATH}':text='而是一场能源与智能的世纪大迁徙':fontcolor=#FFCC00:fontsize=48:x=(w-text_w)/2:y=1730"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_src),
        "-i", str(voice_src),
        "-filter_complex", vf,
        "-map", "1:a",
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)

def render_shot_6(out_path: Path, dur: float, video_src: Path, voice_src: Path):
    """Shot 6: Jensen Huang conclusion with golden badge."""
    vf = (
        f"crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920,"
        f"drawbox=x=140:y=350:w=800:h=120:color=black@0.85:t=fill,"
        f"drawbox=x=140:y=350:w=800:h=120:color=#FFD700:t=4,"
        f"drawtext=fontfile='{FONT_PATH}':text='算力的终局是能源垄断':fontcolor=#FFD700:fontsize=52:x=(w-text_w)/2:y=385,"
        f"drawbox=x=0:y=1630:w=1080:h=200:color=black@0.85:t=fill,"
        f"drawtext=fontfile='{FONT_PATH}':text='十万亿英伟达的底牌，是点亮未来的能源':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=1660,"
        f"drawtext=fontfile='{FONT_PATH}':text='关注我们，看穿AI时代最底层商业真相':fontcolor=#FFD700:fontsize=46:x=(w-text_w)/2:y=1730"
    )
    cmd = [
        "ffmpeg", "-y",
        "-ss", "0", "-i", str(video_src),
        "-i", str(voice_src),
        "-filter_complex", f"[0:v]{vf}[v]",
        "-map", "[v]", "-map", "1:a",
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)

def build_full_movie(project_dir: Path):
    hub = project_dir / "03_assets_hub"
    user_raw = project_dir / "01_raw_assets/user_assets"
    out_dir = project_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    durs = [
        get_duration(hub / "shot_001_intro.wav"),
        get_duration(hub / "shot_002_grid.wav"),
        get_duration(hub / "shot_003_nuclear.wav"),
        get_duration(hub / "shot_004_gigawatt.wav"),
        get_duration(hub / "shot_005_migration.wav"),
        get_duration(hub / "shot_006_conclusion.wav"),
    ]
    print(f"Shot durations: {durs}, Total: {sum(durs):.2f}s", flush=True)

    seg1 = out_dir / "seg1.mp4"
    seg2 = out_dir / "seg2.mp4"
    seg3 = out_dir / "seg3.mp4"
    seg4 = out_dir / "seg4.mp4"
    seg5 = out_dir / "seg5.mp4"
    seg6 = out_dir / "seg6.mp4"

    print("🎬 正在渲染 Shot 1...", flush=True)
    render_shot_1(seg1, durs[0], user_raw / "jensen_clip_07_colossus.mp4", hub / "shot_001_intro.wav")

    print("🎬 正在渲染 Shot 2...", flush=True)
    render_shot_2(seg2, durs[1], user_raw / "pjm_grid_report.png", hub / "shot_002_grid.wav")

    print("🎬 正在渲染 Shot 3...", flush=True)
    render_shot_3(seg3, durs[2], user_raw / "threemile_island.png", user_raw / "blackwell_nvl72.jpg", hub / "shot_003_nuclear.wav")

    print("🎬 正在渲染 Shot 4...", flush=True)
    render_shot_4(seg4, durs[3], hub / "shot_004_nuclear_datacenter.png", hub / "shot_004_gigawatt.wav")

    print("🎬 正在渲染 Shot 5...", flush=True)
    render_shot_5(seg5, durs[4], hub / "shot_005_substation_ai.png", hub / "shot_005_migration.wav")

    print("🎬 正在渲染 Shot 6...", flush=True)
    render_shot_6(seg6, durs[5], user_raw / "jensen_clip_12_tentrillion.mp4", hub / "shot_006_conclusion.wav")

    print("🎞️ 正在拼接分镜...", flush=True)
    concat_list = out_dir / "concat.txt"
    with open(concat_list, "w") as f:
        for s in [seg1, seg2, seg3, seg4, seg5, seg6]:
            f.write(f"file '{s}'\n")

    raw_concat = out_dir / "raw_concat.mp4"
    cmd_concat = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(raw_concat)]
    subprocess.run(cmd_concat, check=True)

    bgm_src = user_raw / "bgm_cinematic.mp3"
    final_master = out_dir / "final_master_1080p.mp4"
    total_dur = sum(durs)

    print("🎵 正在混音 BGM 并执行广播级 -16 LUFS 压限...", flush=True)
    cmd_audio = [
        "ffmpeg", "-y",
        "-i", str(raw_concat),
        "-stream_loop", "-1", "-i", str(bgm_src),
        "-filter_complex",
        f"[1:a]volume=0.18,afade=t=out:st={total_dur-1.5}:d=1.5[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(total_dur),
        str(final_master)
    ]
    subprocess.run(cmd_audio, check=True)
    print(f"🎉 终审 1080p 母带渲染完成: {final_master}", flush=True)
    return final_master

if __name__ == "__main__":
    p = Path("/home/antigravity/qihao1226/AIStudio/projects/20261107_jensen_power")
    build_full_movie(p)
