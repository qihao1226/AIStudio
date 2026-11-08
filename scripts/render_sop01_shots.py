#!/usr/bin/env python3
"""
YOUAI Cloud Video Factory - AG_SOP_01 Authentic Evidence & 2.5D Stage Master Renderer (v3.0)
100% Local Antigravity Engine (Zero Colab GPU Binding).
Renders 6 high-density commercial documentary shots @ 1920x1080 30fps.
"""

import math
import os
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

PROJ = Path("/home/antigravity/qihao1226/AIStudio/projects/20261108_sop01_energy_local")
ASSETS_DIR = PROJ / "03_素材"
FONT_SANS_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_SERIF_BOLD = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

# Color Tokens (Oppenheimer x Spotlight)
C_BG = (13, 11, 9)          # #0D0B09 Primary Dark
C_SURFACE = (27, 35, 32)    # #1B2320 Investigative Dark Green Surface
C_SURFACE_ALT = (28, 22, 18)# #1C1612 Dark Amber Surface
C_ACCENT_AMBER = (255, 154, 80) # #FF9A50 Amber Gold
C_ACCENT_GOLD = (255, 216, 160) # #FFD8A0 Light Gold
C_ACCENT_GREEN = (160, 220, 175)# #A0DCAF Spotlight Green
C_TEXT_WHITE = (250, 244, 235)  # #FAF4EB Primary Off-White
C_TEXT_MUTED = (138, 153, 173)  # #8A99AD Secondary Slate Gray
C_RED_STAMP = (211, 47, 47)     # #D32F2F Official Red Stamp


def create_vignette_mask(w: int, h: int) -> Image.Image:
    """Precompute radial dark vignette mask."""
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2.0, h / 2.0
    r = np.sqrt(((X - cx) / (w * 0.55)) ** 2 + ((Y - cy) / (h * 0.55)) ** 2)
    # 0 inside 0.4 radius, ramps up to 0.88 at edge
    mask = np.clip((r - 0.35) / 0.65, 0.0, 1.0)
    vignette = (mask * 220).astype(np.uint8)
    return Image.fromarray(vignette, mode="L")


VIGNETTE_MASK = create_vignette_mask(1920, 1080)
VIGNETTE_LAYER = Image.new("RGB", (1920, 1080), (5, 4, 3))


def apply_vignette(img: Image.Image) -> Image.Image:
    """Apply Oscar documentary dark radial vignette."""
    return Image.composite(VIGNETTE_LAYER, img, VIGNETTE_MASK)


def ease_expo_out(t: float) -> float:
    return 1.0 if t >= 1.0 else 1.0 - math.pow(2, -10 * t)


def ease_back_out(t: float, s: float = 1.4) -> float:
    t = t - 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0


def draw_subtle_grid(draw: ImageDraw.ImageDraw, w: int, h: int, offset_y: float = 0.0, alpha: int = 18):
    step = 80
    c = (alpha + 5, alpha + 5, alpha + 6)
    for x in range(0, w, step):
        draw.line([(x, 0), (x, h)], fill=c, width=1)
    y_start = int(offset_y) % step
    for y in range(y_start, h, step):
        draw.line([(0, y), (w, y)], fill=c, width=1)


# -------------------------------------------------------------
# Shot 1: Claim (开场核心揭示) - Jacky-motion L01 + HyperFrames T1
# -------------------------------------------------------------
def render_shot1_frame(f_idx: int, total_f: int) -> Image.Image:
    t = f_idx / 30.0
    dur = total_f / 30.0
    p = f_idx / total_f

    # Camera slow push (Scale 1.00 -> 1.05)
    scale = 1.00 + 0.05 * p

    base = Image.new("RGB", (1920, 1080), C_BG)
    draw = ImageDraw.Draw(base)

    # 1. Subtle moving tech grid with parallax
    draw_subtle_grid(draw, 1920, 1080, offset_y=p * 60.0, alpha=16)

    # 2. Golden energy glow in background (pulsing and drifting)
    cx = int(1400 + math.sin(t * 0.8) * 40)
    cy = int(450 + math.cos(t * 0.8) * 30)
    for r in range(400, 40, -40):
        alpha = int(14 * (1.0 - r / 400.0))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(C_BG[0] + alpha * 2, C_BG[1] + int(alpha * 1.2), C_BG[2]))

    # Floating particles (40 motes drifting 1.5x speed)
    for i in range(40):
        seed_x = (i * 137.5) % 1920
        seed_y = (i * 249.3) % 1080
        px = int((seed_x + t * 25.0 * (1.0 + (i % 3) * 0.3)) % 1920)
        py = int((seed_y - t * 18.0 * (1.0 + (i % 2) * 0.4)) % 1080)
        size = 2 if i % 4 != 0 else 3
        draw.ellipse([px, py, px + size, py + size], fill=C_ACCENT_AMBER)

    # 3. Dominant-Left Hero Typography (Jacky-motion L01)
    font_kicker = ImageFont.truetype(FONT_SANS_BOLD, 28)
    font_hero = ImageFont.truetype(FONT_SANS_BOLD, 108)
    font_sub = ImageFont.truetype(FONT_SANS_BOLD, 32)
    font_badge = ImageFont.truetype(FONT_SANS_BOLD, 20)

    # Left alignment anchor: x = 160
    base_x = 160 + int(p * 20.0) # Slow drift
    base_y = 260

    # Top Topic Label (Clean, professional documentary)
    draw.text((base_x, 150), "深度商业纪实调查", font=font_kicker, fill=C_ACCENT_AMBER)

    # Thin accent rule
    rule_w = int(min(600, 200 + p * 400))
    draw.line([(base_x, 195), (base_x + rule_w, 195)], fill=C_ACCENT_AMBER, width=2)

    # Hero title (strict Chinese phrase line breaks)
    draw.text((base_x, base_y), "AI 算力的终局", font=font_hero, fill=C_TEXT_WHITE)
    draw.text((base_x, base_y + 125), "不是算法与芯片", font=font_hero, fill=C_TEXT_WHITE)
    draw.text((base_x, base_y + 250), "而是能源。", font=font_hero, fill=C_ACCENT_AMBER)

    # Subtitle
    draw.text((base_x, base_y + 400), "万亿大模型正在击穿全球工业电网极限", font=font_sub, fill=C_TEXT_MUTED)

    # Right side stylistic signature visual: Concentric energy ring
    rcx, rcy = 1450, 540
    for ring_r in [120, 200, 280]:
        draw.ellipse([rcx - ring_r, rcy - ring_r, rcx + ring_r, rcy + ring_r], outline=(40, 32, 22), width=1)
    # Rotating notch
    ang = t * 1.2
    nx = rcx + int(math.cos(ang) * 200)
    ny = rcy + int(math.sin(ang) * 200)
    draw.ellipse([nx - 6, ny - 6, nx + 6, ny + 6], fill=C_ACCENT_AMBER)
    draw.text((rcx - 70, rcy - 12), "GRID STRESS", font=font_badge, fill=C_ACCENT_GOLD)

    # Scale transform for continuous camera slow push
    if abs(scale - 1.0) > 1e-4:
        nw, nh = int(1920 * scale), int(1080 * scale)
        scaled = base.resize((nw, nh), Image.Resampling.BILINEAR)
        x_off = (nw - 1920) // 2
        y_off = (nh - 1080) // 2
        base = scaled.crop((x_off, y_off, x_off + 1920, y_off + 1080))

    return apply_vignette(base)


# -------------------------------------------------------------------
# Shot 2: Evidence (真实研报/文件物证) - Jacky-motion L08 + Stage25D
# -------------------------------------------------------------------
PJM_RAW = Image.open(ASSETS_DIR / "pjm_grid_report.png").convert("RGBA")

def render_shot2_frame(f_idx: int, total_f: int) -> Image.Image:
    t = f_idx / 30.0
    p = f_idx / total_f

    # Camera slow push: 1.00 -> 1.06
    scale = 1.00 + 0.06 * p
    drift_x = int(-25.0 * p)

    base = Image.new("RGB", (1920, 1080), C_SURFACE)
    draw = ImageDraw.Draw(base)

    draw_subtle_grid(draw, 1920, 1080, offset_y=p * 40.0, alpha=14)

    # Document placement with 2.5D board framing
    doc_w = int(1400 * scale)
    doc_h = int(780 * scale)
    doc_x = (1920 - doc_w) // 2 + drift_x
    doc_y = 170

    # Draw document background card with glass drop shadow
    shadow_box = [doc_x - 12, doc_y - 12, doc_x + doc_w + 12, doc_y + doc_h + 12]
    draw.rectangle(shadow_box, fill=(10, 14, 12), outline=(50, 65, 58), width=1)

    # Resize raw PJM report
    resized_pjm = PJM_RAW.resize((doc_w, doc_h), Image.Resampling.LANCZOS)
    base.paste(resized_pjm.convert("RGB"), (doc_x, doc_y))

    # Spotlight sweep across document (left to right, t=0.5 to t=4.5)
    spot_x = int(doc_x + doc_w * (t / 5.5))
    spot_y = doc_y + doc_h // 2
    # Draw soft spotlight overlay
    spot_layer = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    spot_draw = ImageDraw.Draw(spot_layer)
    for sr in range(260, 40, -30):
        s_alpha = int(22 * (1.0 - sr / 260.0))
        spot_draw.ellipse([spot_x - sr, spot_y - sr, spot_x + sr, spot_y + sr], fill=(255, 230, 180, s_alpha))
    base = Image.alpha_composite(base.convert("RGBA"), spot_layer).convert("RGB")
    draw = ImageDraw.Draw(base)

    # 0.6s Highlighter Draw Mask (t=1.0s to 1.6s, duration 0.6s)
    # Target highlight box: "260 GW Capacity Queue" row inside the document
    if t >= 1.0:
        hl_p = min(1.0, (t - 1.0) / 0.6)
        hl_w_full = int(doc_w * 0.72)
        hl_w = int(hl_w_full * hl_p)
        hl_x = doc_x + int(doc_w * 0.14)
        hl_y = doc_y + int(doc_h * 0.52)
        hl_h = int(doc_h * 0.10)

        # Semi-transparent yellow-amber highlighter
        hl_layer = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        hl_draw = ImageDraw.Draw(hl_layer)
        hl_draw.rounded_rectangle([hl_x, hl_y, hl_x + hl_w, hl_y + hl_h], radius=6, fill=(255, 215, 0, 95))
        # Add highlighter glow border
        hl_draw.rounded_rectangle([hl_x, hl_y, hl_x + hl_w, hl_y + hl_h], radius=6, outline=(255, 240, 100, 160), width=2)
        base = Image.alpha_composite(base.convert("RGBA"), hl_layer).convert("RGB")
        draw = ImageDraw.Draw(base)

    # HUD & Evidence Headers
    font_hud = ImageFont.truetype(FONT_SANS_BOLD, 24)
    font_head = ImageFont.truetype(FONT_SANS_BOLD, 36)
    font_stamp = ImageFont.truetype(FONT_SANS_BOLD, 22)

    draw.text((doc_x, 95), "官方权威物证 · PJM 区域电网并网负荷规划报告", font=font_hud, fill=C_ACCENT_GREEN)
    draw.text((doc_x + doc_w - 280, 95), "美国 SEC 10-K 正式备案", font=font_hud, fill=C_TEXT_MUTED)

    # Bottom floating takeaway card
    tag_y = 960
    draw.rectangle([doc_x, tag_y, doc_x + 850, tag_y + 60], fill=(16, 22, 19), outline=C_ACCENT_GREEN, width=1)
    draw.text((doc_x + 24, tag_y + 14), "权威物证：全美数据中心申请接入负荷突破 260 吉瓦", font=font_head, fill=C_TEXT_WHITE)

    return apply_vignette(base)


# -------------------------------------------------------------------
# Shot 3: Metric (金融与能源走势) - Remotion Financial Chart
# -------------------------------------------------------------------
def render_shot3_frame(f_idx: int, total_f: int) -> Image.Image:
    t = f_idx / 30.0
    p = f_idx / total_f

    scale = 1.00 + 0.05 * p

    base = Image.new("RGB", (1920, 1080), C_BG)
    draw = ImageDraw.Draw(base)

    draw_subtle_grid(draw, 1920, 1080, offset_y=p * 50.0, alpha=16)

    # Chart Coordinate Frame
    chart_x0, chart_y0 = 200, 780
    chart_x1, chart_y1 = 1720, 300

    # Draw grid horizontal lines & axis labels
    font_axis = ImageFont.truetype(FONT_SANS_BOLD, 20)
    for y_val, label in [(780, "0 GW"), (660, "80 GW"), (540, "160 GW"), (420, "240 GW"), (300, "320 GW")]:
        draw.line([(chart_x0, y_val), (chart_x1, y_val)], fill=(32, 26, 20), width=1)
        draw.text((chart_x0 - 90, y_val - 10), label, font=font_axis, fill=C_TEXT_MUTED)

    for x_val, label in [(200, "2020"), (500, "2022"), (800, "2024"), (1100, "2026E"), (1400, "2028E"), (1720, "2030E")]:
        draw.line([(x_val, chart_y0), (x_val, chart_y1)], fill=(32, 26, 20), width=1)
        draw.text((x_val - 25, chart_y0 + 20), label, font=font_axis, fill=C_TEXT_MUTED)

    # Exponential power curve points
    curve_points = [
        (200, 770), (400, 750), (600, 720), (800, 680),
        (1000, 610), (1200, 500), (1400, 390), (1600, 320)
    ]

    # Progressive drawing of curve (reveals over first 2.5s)
    reveal_p = min(1.0, t / 2.5)
    n_pts = max(2, int(len(curve_points) * reveal_p))
    active_pts = curve_points[:n_pts]

    # Draw area fill under curve
    if len(active_pts) >= 2:
        poly_pts = [(chart_x0, chart_y0)] + active_pts + [(active_pts[-1][0], chart_y0)]
        area_layer = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        area_draw = ImageDraw.Draw(area_layer)
        area_draw.polygon(poly_pts, fill=(255, 154, 80, 35))
        base = Image.alpha_composite(base.convert("RGBA"), area_layer).convert("RGB")
        draw = ImageDraw.Draw(base)

    # Draw curve line with thickness & glow
    for i in range(len(active_pts) - 1):
        p1 = active_pts[i]
        p2 = active_pts[i + 1]
        draw.line([p1, p2], fill=C_ACCENT_AMBER, width=4)

    # Critical Redline Warning: 200 GW threshold
    draw.line([(chart_x0, 480), (chart_x1, 480)], fill=(220, 60, 60), width=2)
    draw.text((chart_x1 - 380, 455), "CRITICAL LIMIT: 传统电网安全承载上限", font=font_axis, fill=(255, 100, 100))

    # 0.8s Ticking Counter (t=0.3s to 1.1s, targets 260)
    if t < 0.3:
        counter_val = 0
        bloom = 0.0
    elif t < 1.1:
        c_prog = (t - 0.3) / 0.8
        counter_val = int(260 * ease_expo_out(c_prog))
        bloom = 0.0
    else:
        counter_val = 260
        # Pulse bloom at landing (t=1.1 to 1.6)
        bloom = max(0.0, 1.0 - (t - 1.1) / 0.5)

    # Large Ticker HUD display (top left)
    font_num = ImageFont.truetype(FONT_SANS_BOLD, 140)
    font_unit = ImageFont.truetype(FONT_SANS_BOLD, 52)
    font_desc = ImageFont.truetype(FONT_SANS_BOLD, 32)
    font_title = ImageFont.truetype(FONT_SANS_BOLD, 26)

    draw.text((200, 90), "数据中心申请接入负荷激增走势", font=font_title, fill=C_ACCENT_AMBER)

    num_str = f"{counter_val}"
    draw.text((200, 130), num_str, font=font_num, fill=C_TEXT_WHITE)
    bbox = font_num.getbbox(num_str)
    draw.text((200 + bbox[2] + 20, 205), "GW (吉瓦)", font=font_unit, fill=C_ACCENT_AMBER)
    draw.text((200, 290), "全美数据中心申请接入负荷 (已占全美电网总负荷 33%)", font=font_desc, fill=C_TEXT_MUTED)

    # Bloom pulse on target landing
    if bloom > 0.0:
        bloom_layer = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        b_draw = ImageDraw.Draw(bloom_layer)
        b_alpha = int(120 * bloom)
        b_draw.text((200, 130), num_str, font=font_num, fill=(255, 216, 160, b_alpha))
        base = Image.alpha_composite(base.convert("RGBA"), bloom_layer).convert("RGB")
        draw = ImageDraw.Draw(base)

    # Camera slow push
    if abs(scale - 1.0) > 1e-4:
        nw, nh = int(1920 * scale), int(1080 * scale)
        scaled = base.resize((nw, nh), Image.Resampling.BILINEAR)
        x_off = (nw - 1920) // 2
        y_off = (nh - 1080) // 2
        base = scaled.crop((x_off, y_off, x_off + 1920, y_off + 1080))

    return apply_vignette(base)


# -------------------------------------------------------------------
# Shot 4: Contrast (悬殊对比) - Jacky-motion L03 (7kW vs 120kW NVL72)
# -------------------------------------------------------------------
NVL72_RAW = Image.open(ASSETS_DIR / "blackwell_nvl72.jpg").convert("RGB")

def render_shot4_frame(f_idx: int, total_f: int) -> Image.Image:
    t = f_idx / 30.0
    p = f_idx / total_f

    scale = 1.00 + 0.05 * p

    base = Image.new("RGB", (1920, 1080), C_BG)
    draw = ImageDraw.Draw(base)

    draw_subtle_grid(draw, 1920, 1080, offset_y=p * 45.0, alpha=16)

    font_head = ImageFont.truetype(FONT_SANS_BOLD, 26)
    font_col_t = ImageFont.truetype(FONT_SANS_BOLD, 38)
    font_col_stat = ImageFont.truetype(FONT_SANS_BOLD, 96)
    font_col_desc = ImageFont.truetype(FONT_SANS_BOLD, 26)
    font_mult = ImageFont.truetype(FONT_SANS_BOLD, 36)

    draw.text((160, 90), "单柜能耗维度鸿沟对比", font=font_head, fill=C_ACCENT_AMBER)

    # Split Two Columns: Left = 160..900, Right = 1020..1760
    # Left Column: Legacy 7kW Server Rack (Dims at t > 1.8s)
    left_alpha = 1.0 if t < 1.8 else max(0.35, 1.0 - (t - 1.8) * 0.8)

    left_box = [160, 160, 900, 940]
    draw.rectangle(left_box, fill=(int(20 * left_alpha), int(22 * left_alpha), int(25 * left_alpha)),
                   outline=(int(60 * left_alpha), int(70 * left_alpha), int(80 * left_alpha)), width=1)

    c_left_text = (int(C_TEXT_WHITE[0] * left_alpha), int(C_TEXT_WHITE[1] * left_alpha), int(C_TEXT_WHITE[2] * left_alpha))
    c_left_muted = (int(C_TEXT_MUTED[0] * left_alpha), int(C_TEXT_MUTED[1] * left_alpha), int(C_TEXT_MUTED[2] * left_alpha))

    draw.text((200, 200), "传统通用服务器机柜", font=font_head, fill=c_left_muted)
    draw.text((200, 250), "标准单机柜功率", font=font_col_t, fill=c_left_text)
    draw.text((200, 310), "7 kW", font=font_col_stat, fill=c_left_text)
    draw.text((200, 440), "• 传统风冷对流散热\n• 常规 220V 工业低压电网\n• 承载 CPU 通用业务与普通存储", font=font_col_desc, fill=c_left_muted)

    # Left rack icon illustration
    rack_x, rack_y = 350, 600
    draw.rectangle([rack_x, rack_y, rack_x + 180, rack_y + 280], outline=c_left_muted, width=2)
    for ry in range(rack_y + 20, rack_y + 260, 30):
        draw.line([(rack_x + 10, ry), (rack_x + 170, ry)], fill=c_left_muted, width=1)

    # Central Divider with Technical Dimension Marks
    draw.line([(960, 160), (960, 940)], fill=(50, 40, 30), width=2)
    draw.ellipse([954, 540, 966, 552], fill=C_ACCENT_AMBER)

    # Right Column: AI Liquid Cooled NVL72 120kW (Bright Amber/Gold Glow)
    right_box = [1020, 160, 1760, 940]
    draw.rectangle(right_box, fill=(28, 22, 18), outline=C_ACCENT_AMBER, width=2)

    draw.text((1060, 200), "新一代高密算力集群机柜", font=font_head, fill=C_ACCENT_AMBER)
    draw.text((1060, 250), "NVIDIA Blackwell NVL72", font=font_col_t, fill=C_TEXT_WHITE)
    draw.text((1060, 310), "120 kW", font=font_col_stat, fill=C_ACCENT_AMBER)
    draw.text((1060, 440), "• 全浸没/冷板式超密液冷\n• 工业级高压特种供电直通\n• 单柜吞吐 72 颗 B200 算力矩阵", font=font_col_desc, fill=C_TEXT_WHITE)

    # Real Photo of NVL72 embedded in right frame
    nvl_w, nvl_h = 600, 315
    nvl_resized = NVL72_RAW.resize((nvl_w, nvl_h), Image.Resampling.LANCZOS)
    base.paste(nvl_resized, (1080, 580))
    draw.rectangle([1080, 580, 1080 + nvl_w, 580 + nvl_h], outline=C_ACCENT_AMBER, width=1)

    # 17x Gap Badge (pulsing)
    badge_pulse = 1.0 + 0.05 * math.sin(t * 3.0)
    draw.rounded_rectangle([860, 510, 1060, 580], radius=8, fill=(20, 12, 8), outline=C_ACCENT_AMBER, width=2)
    draw.text((885, 526), "17x 暴增", font=font_mult, fill=C_ACCENT_AMBER)

    # Camera slow push
    if abs(scale - 1.0) > 1e-4:
        nw, nh = int(1920 * scale), int(1080 * scale)
        scaled = base.resize((nw, nh), Image.Resampling.BILINEAR)
        x_off = (nw - 1920) // 2
        y_off = (nh - 1080) // 2
        base = scaled.crop((x_off, y_off, x_off + 1920, y_off + 1080))

    return apply_vignette(base)


# -------------------------------------------------------------------
# Shot 5: Keynote / Stage25D (三里岛核电航拍) - CVF PodcastWaveform
# -------------------------------------------------------------------
TMI_RAW = Image.open(ASSETS_DIR / "threemile_island.png").convert("RGB")

def render_shot5_frame(f_idx: int, total_f: int) -> Image.Image:
    t = f_idx / 30.0
    p = f_idx / total_f

    # Cinematic aerial slow push: 1.00 -> 1.07
    scale = 1.00 + 0.07 * p

    # Resize raw Three Mile Island photo with scale
    cur_w = int(1920 * scale)
    cur_h = int(1080 * scale)
    tmi_scaled = TMI_RAW.resize((cur_w, cur_h), Image.Resampling.LANCZOS)
    x_off = (cur_w - 1920) // 2
    y_off = (cur_h - 1080) // 2
    base = tmi_scaled.crop((x_off, y_off, x_off + 1920, y_off + 1080))

    # Apply Oscar documentary color grade (Industrial teal & amber overlay)
    grade_layer = Image.new("RGBA", (1920, 1080), (13, 20, 24, 75)) # Teal tint
    base = Image.alpha_composite(base.convert("RGBA"), grade_layer).convert("RGB")
    draw = ImageDraw.Draw(base)

    # Top Deal Badges (SEC 10-K & Deals)
    font_badge = ImageFont.truetype(FONT_SANS_BOLD, 24)
    font_hero = ImageFont.truetype(FONT_SANS_BOLD, 48)
    font_sub = ImageFont.truetype(FONT_SANS_BOLD, 28)

    draw.rounded_rectangle([140, 100, 780, 180], radius=8, fill=(10, 14, 18), outline=C_ACCENT_GREEN, width=1)
    draw.text((170, 115), "SEC 10-K DISCLOSURE // 官方采购备案", font=font_badge, fill=C_ACCENT_GREEN)
    draw.text((170, 142), "MICROSOFT 重启三里岛核电站 (835 MW PPA)", font=font_sub, fill=C_TEXT_WHITE)

    draw.rounded_rectangle([1140, 100, 1780, 180], radius=8, fill=(10, 14, 18), outline=C_ACCENT_AMBER, width=1)
    draw.text((1170, 115), "AWS NUCLEAR EXPANSION // 亚马逊直采", font=font_badge, fill=C_ACCENT_AMBER)
    draw.text((1170, 142), "AMAZON 买断宾州核电机组 (960 MW)", font=font_sub, fill=C_TEXT_WHITE)

    # Bottom Glass Container for Audio Waveform
    bar_box = [140, 860, 1780, 1000]
    draw.rounded_rectangle(bar_box, radius=12, fill=(8, 12, 14), outline=(40, 50, 55), width=1)

    draw.text((170, 880), "AUTHENTIC KEYNOTE SPEECH // 动态原声声纹", font=font_badge, fill=C_ACCENT_GREEN)
    draw.text((170, 915), "黄仁勋现场纪实原声：「算力与清洁能源已深度绑定」", font=font_sub, fill=C_TEXT_WHITE)

    # Dynamic Audio Soundwave Bars (36 bars dancing to speech frequencies)
    wave_x_start = 1000
    n_bars = 28
    bar_w = 18
    gap = 8
    for b in range(n_bars):
        bx = wave_x_start + b * (bar_w + gap)
        # Synthetic speech harmonic frequency height
        h_pulse = (
            math.sin(t * 8.0 + b * 0.4) * 20 +
            math.sin(t * 14.0 + b * 0.7) * 15 +
            math.cos(t * 5.0 + b * 0.2) * 12 + 35
        )
        h_pulse = max(6, min(65, int(h_pulse)))
        by = 960 - h_pulse
        color = C_ACCENT_GREEN if b % 2 == 0 else C_ACCENT_AMBER
        draw.rounded_rectangle([bx, by, bx + bar_w, 960], radius=3, fill=color)

    return apply_vignette(base)


# -------------------------------------------------------------------
# Shot 6: Punchline (终局交割) - HyperFrames T8 + Drop Stamp 阻尼公章
# -------------------------------------------------------------------
def render_shot6_frame(f_idx: int, total_f: int) -> Image.Image:
    t = f_idx / 30.0
    p = f_idx / total_f
    dur = total_f / 30.0

    # Camera slow pull: 1.04 -> 1.00
    scale = 1.04 - 0.04 * p

    base = Image.new("RGB", (1920, 1080), (16, 13, 10))
    draw = ImageDraw.Draw(base)

    # 1. Guilloche Security Certificate Border (HyperFrames T8)
    margin = 80
    draw.rectangle([margin, margin, 1920 - margin, 1080 - margin], outline=C_ACCENT_AMBER, width=3)
    draw.rectangle([margin + 12, margin + 12, 1920 - margin - 12, 1080 - margin - 12], outline=(60, 48, 32), width=1)

    # Corner security markers
    for cx, cy in [(margin + 12, margin + 12), (1920 - margin - 12, margin + 12),
                   (margin + 12, 1080 - margin - 12), (1920 - margin - 12, 1080 - margin - 12)]:
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=C_ACCENT_AMBER)

    draw_subtle_grid(draw, 1920, 1080, offset_y=p * 30.0, alpha=12)

    font_code = ImageFont.truetype(FONT_SANS_BOLD, 22)
    font_cert_title = ImageFont.truetype(FONT_SANS_BOLD, 36)
    font_punchline = ImageFont.truetype(FONT_SERIF_BOLD, 68)
    font_footer = ImageFont.truetype(FONT_SANS_BOLD, 24)

    # Header Telemetry
    draw.text((140, 130), "GLOBAL AI COMPUTE INFRASTRUCTURE // PPA SETTLEMENT", font=font_code, fill=C_ACCENT_GOLD)
    draw.text((1400, 130), "DOCUMENT ID: 2026-NUC-835GW", font=font_code, fill=C_TEXT_MUTED)

    draw.text((140, 175), "2026–2036 长期基荷核电战略交割凭单", font=font_cert_title, fill=C_ACCENT_AMBER)
    draw.line([(140, 230), (1780, 230)], fill=(70, 55, 35), width=1)

    # Hero Punchline Statement (Centered prominent lines)
    draw.text((220, 360), "谁能掌控源源不断的核裂变电力，", font=font_punchline, fill=C_TEXT_WHITE)
    draw.text((220, 470), "谁就能锁定下一个十年的全球算力霸权。", font=font_punchline, fill=C_ACCENT_AMBER)

    # Certificate Clauses Detail
    draw.text((220, 630), "交割标的：三里岛 (835MW) + 宾夕法尼亚机组 (960MW) 清洁基荷电力", font=font_footer, fill=C_TEXT_MUTED)
    draw.text((220, 675), "执行周期：2026 年 11 月至 2036 年 12 月（十个完整财年独占）", font=font_footer, fill=C_TEXT_MUTED)
    draw.text((220, 720), "交割凭证等级：AAA 级主权算力保障协议 // 终局定论", font=font_footer, fill=C_ACCENT_GOLD)

    # Drop Stamp Animation (t=1.0s to 1.6s)
    # Circular Official Red Seal with damped back.out overshoot
    stamp_x, stamp_y = 1420, 520
    if t >= 1.0:
        stamp_p = min(1.0, (t - 1.0) / 0.5)
        stamp_scale = 2.5 - 1.5 * ease_back_out(stamp_p, s=1.4)
        stamp_alpha = min(255, int(255 * stamp_p))

        stamp_r = int(140 * stamp_scale)
        stamp_layer = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(stamp_layer)

        # Double red circles
        s_draw.ellipse([stamp_x - stamp_r, stamp_y - stamp_r, stamp_x + stamp_r, stamp_y + stamp_r],
                       outline=(C_RED_STAMP[0], C_RED_STAMP[1], C_RED_STAMP[2], stamp_alpha), width=max(2, int(4 * stamp_scale)))
        inner_r = int(stamp_r * 0.88)
        s_draw.ellipse([stamp_x - inner_r, stamp_y - inner_r, stamp_x + inner_r, stamp_y + inner_r],
                       outline=(C_RED_STAMP[0], C_RED_STAMP[1], C_RED_STAMP[2], stamp_alpha), width=max(1, int(2 * stamp_scale)))

        # Center Star & Text
        font_stamp_t = ImageFont.truetype(FONT_SANS_BOLD, max(10, int(28 * stamp_scale)))
        font_stamp_sub = ImageFont.truetype(FONT_SANS_BOLD, max(8, int(20 * stamp_scale)))
        s_draw.text((stamp_x - int(70 * stamp_scale), stamp_y - int(30 * stamp_scale)), "★ 战略交割 ★", font=font_stamp_t, fill=(C_RED_STAMP[0], C_RED_STAMP[1], C_RED_STAMP[2], stamp_alpha))
        s_draw.text((stamp_x - int(80 * stamp_scale), stamp_y + int(10 * stamp_scale)), "2026-2036 生效", font=font_stamp_sub, fill=(C_RED_STAMP[0], C_RED_STAMP[1], C_RED_STAMP[2], stamp_alpha))

        # Stamp impact shockwave (lasts 0.4s after landing at t=1.5)
        if 1.5 <= t <= 1.9:
            sw_p = (t - 1.5) / 0.4
            sw_r = int(stamp_r + sw_p * 80)
            sw_alpha = int(140 * (1.0 - sw_p))
            s_draw.ellipse([stamp_x - sw_r, stamp_y - sw_r, stamp_x + sw_r, stamp_y + sw_r],
                           outline=(220, 60, 60, sw_alpha), width=2)

        base = Image.alpha_composite(base.convert("RGBA"), stamp_layer).convert("RGB")
        draw = ImageDraw.Draw(base)

    # Floating golden security motes (continuous living motion)
    for i in range(25):
        seed_x = (i * 179.3) % 1920
        seed_y = (i * 283.1) % 1080
        px = int((seed_x + t * 20.0 * (1.0 + (i % 3) * 0.2)) % 1920)
        py = int((seed_y - t * 14.0 * (1.0 + (i % 2) * 0.3)) % 1080)
        draw.ellipse([px, py, px + 2, py + 2], fill=C_ACCENT_AMBER)

    # Continuous camera motion (Scale 1.05 -> 1.00)
    nw, nh = int(1920 * scale), int(1080 * scale)
    scaled = base.resize((nw, nh), Image.Resampling.BILINEAR)
    x_off = (nw - 1920) // 2
    y_off = (nh - 1080) // 2
    base = scaled.crop((x_off, y_off, x_off + 1920, y_off + 1080))

    # Smooth fade out to black during final 0.6s
    if t > (dur - 0.6):
        fade_p = (t - (dur - 0.6)) / 0.6
        black = Image.new("RGB", (1920, 1080), (0, 0, 0))
        base = Image.blend(base, black, fade_p)

    return apply_vignette(base)


# -------------------------------------------------------------
# Main Renderer Pipeline: Stream Frames Directly to FFmpeg
# -------------------------------------------------------------
SHOTS = [
    ("shot1_claim.mp4", 4.5, render_shot1_frame),
    ("shot2_evidence.mp4", 6.0, render_shot2_frame),
    ("shot3_metric.mp4", 6.0, render_shot3_frame),
    ("shot4_contrast.mp4", 6.0, render_shot4_frame),
    ("shot5_keynote.mp4", 7.0, render_shot5_frame),
    ("shot6_punchline.mp4", 7.0, render_shot6_frame),
]

def render_shot_to_mp4(name: str, duration: float, render_fn):
    out_path = ASSETS_DIR / name
    if out_path.exists() and out_path.stat().st_size > 100000:
        print(f"   ✓ {name} already exists, skipping")
        return
    fps = 30
    total_frames = int(round(duration * fps))
    print(f"-> Rendering {name}: {duration:.2f}s ({total_frames} frames)...", flush=True)

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", "1920x1080",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(out_path)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for f_idx in range(total_frames):
        img = render_fn(f_idx, total_frames)
        proc.stdin.write(img.tobytes())

    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg render failed for {name}")
    print(f"   ✓ Finished {name} ({out_path.stat().st_size // 1024} KB)")


def main():
    print("=== YOUAI AG_SOP_01 Authentic Evidence Shot Renderer ===")
    for name, dur, fn in SHOTS:
        render_shot_to_mp4(name, dur, fn)
    print("\n✓ All 6 SOP 01 shots rendered successfully into 03_素材/!")


if __name__ == "__main__":
    main()
