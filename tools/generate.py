#!/usr/bin/env python3
"""
News Image Generator for make.fun news-image-20261123 Round 1
Generates a 1024x1024 newspaper front page for Monday 23 November 2026
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

# ─── Constants ───
W, H = 1024, 1024
OUT_PATH = "out/entry.png"

# Colors
CREAM = (250, 247, 240)
BLACK = (25, 25, 25)
NAVY = (20, 30, 55)
RED = (180, 30, 35)
RED_DARK = (140, 20, 25)
GRAY = (100, 100, 100)
GRAY_LIGHT = (160, 160, 160)
WHITE = (255, 255, 255)
BLUE = (30, 60, 120)
GREEN = (30, 100, 50)
ORANGE = (200, 100, 20)
PURPLE = (100, 40, 120)
BROWN = (120, 80, 40)

# Region colors
REGION_COLORS = {
    "EUROPE": BLUE,
    "AMERICAS": RED,
    "ASIA-PACIFIC": GREEN,
    "MIDDLE EAST": ORANGE,
    "WORLD": PURPLE,
    "AFRICA": BROWN,
}

# Font paths
FONT_DIR = "fonts/dejavu-fonts-ttf-2.37/ttf"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF_ITALIC = os.path.join(FONT_DIR, "DejaVuSerif-Italic.ttf")
SERIF_BOLD_ITALIC = os.path.join(FONT_DIR, "DejaVuSerif-BoldItalic.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS_COND = os.path.join(FONT_DIR, "DejaVuSansCondensed.ttf")
SANS_COND_BOLD = os.path.join(FONT_DIR, "DejaVuSansCondensed-Bold.ttf")

# ─── Font loading ───
def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception as e:
        print(f"Font load failed: {path} @ {size}: {e}")
        return ImageFont.load_default()

# Preload fonts at various sizes
FONTS = {
    "masthead": load_font(SANS_BOLD, 28),
    "masthead_sub": load_font(SANS, 14),
    "date_main": load_font(SERIF_BOLD, 42),
    "date_sub": load_font(SERIF_ITALIC, 20),
    "stat_num": load_font(SANS_BOLD, 36),
    "stat_label": load_font(SANS, 12),
    "region_tab": load_font(SANS_BOLD, 13),
    "region_count": load_font(SANS_BOLD, 16),
    "timeline": load_font(SANS, 12),
    "timeline_time": load_font(SANS_BOLD, 12),
    "lead_kicker": load_font(SANS_BOLD, 11),
    "lead_tag": load_font(SANS_BOLD, 9),
    "lead_headline": load_font(SERIF_BOLD, 17),
    "lead_body": load_font(SERIF, 12),
    "lead_sources": load_font(SANS, 9),
    "ten_num": load_font(SANS_BOLD, 14),
    "ten_tag": load_font(SANS_BOLD, 8),
    "ten_headline": load_font(SERIF_BOLD, 10),
    "ten_body": load_font(SANS_COND, 8),
    "ten_source": load_font(SANS, 8),
    "also_num": load_font(SANS_BOLD, 11),
    "also_text": load_font(SANS_COND, 8),
    "also_source": load_font(SANS, 8),
    "datecheck_title": load_font(SANS_BOLD, 12),
    "datecheck_body": load_font(SANS, 9),
    "legend_title": load_font(SANS_BOLD, 10),
    "legend_item": load_font(SANS, 9),
    "footer": load_font(SANS, 9),
}

# ─── Helper functions ───
def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines

def draw_text_box(draw, x, y, text, font, color, max_width, max_lines=None, line_spacing=1.2):
    lines = wrap_text(draw, text, font, max_width)
    if max_lines:
        lines = lines[:max_lines]
    line_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
    total_h = 0
    for i, line in enumerate(lines):
        draw.text((x, y + total_h), line, font=font, fill=color)
        total_h += int(line_h * line_spacing)
    max_w = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines) if lines else 0
    return max_w, total_h

def measure_text(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius, fill=fill, outline=outline, width=width)

# ─── Font fitting helpers ───
def fit_font_size(draw, text, font_path, max_width, max_size, min_size=8, padding=6):
    """Find the largest font size where text fits in max_width - 2*padding."""
    for size in range(max_size, min_size - 1, -1):
        font = ImageFont.truetype(font_path, size)
        w, h = measure_text(draw, text, font)
        if w <= max_width - 2 * padding:
            return font, w, h
    # Fallback to min_size
    font = ImageFont.truetype(font_path, min_size)
    return font, *measure_text(draw, text, font)

def fit_font_size_for_list(draw, texts, font_path, max_width, max_size, min_size=8, padding=6):
    """Find the largest font size where ALL texts fit in max_width - 2*padding."""
    for size in range(max_size, min_size - 1, -1):
        font = ImageFont.truetype(font_path, size)
        all_fit = True
        for text in texts:
            w, h = measure_text(draw, text, font)
            if w > max_width - 2 * padding:
                all_fit = False
                break
        if all_fit:
            return font
    return ImageFont.truetype(font_path, min_size)

# ─── Illustration: Continuous Horizon across 3 lead panels ───
def draw_horizon_panels(draw, panel_rects):
    # panel_rects = (x, y, w, ill_h) where ill_h is illustration height
    # Horizon is at the BOTTOM of the illustration area (y + ill_h)
    # All panels share ONE continuous thin horizon line at same height

    # First pass: draw sky gradients and elements for each panel
    for i, (x, y, w, h) in enumerate(panel_rects):
        hy = y + h  # Horizon at bottom of illustration area

        if i == 0:  # Dawn - Wall Street: skyline silhouette against dawn gradient
            # Dawn gradient sky (top portion only, not full height)
            sky_h = int(h * 0.8)
            for yy in range(y, y + sky_h):
                t = (yy - y) / max(1, sky_h - 1)
                r = int(255 * (0.85 - 0.15 * t))
                g = int(200 * (0.7 - 0.3 * t))
                b = int(150 * (0.5 + 0.3 * t))
                draw.line([(x, yy), (x + w, yy)], fill=(r, g, b))
            # Sun (small, near horizon)
            sun_x = x + w // 2
            sun_y = hy - 8
            draw.ellipse([sun_x - 8, sun_y - 8, sun_x + 8, sun_y + 8], fill=(255, 230, 120))
            # Skyline silhouette - irregular building shapes against sky
            building_count = 5
            bw = w // building_count
            for bi in range(building_count):
                bx = x + bi * bw + 3
                # Varying building heights, max 60% of illustration height
                bh = int(h * (0.35 + 0.25 * ((bi * 7) % 5) / 4))
                # Building body
                draw.rectangle([bx, hy - bh, bx + bw - 6, hy], fill=(25, 25, 40))
                # Windows - sparse, lit
                for wx in range(bx + 4, bx + bw - 10, 14):
                    for wy in range(hy - bh + 4, hy - 4, 16):
                        if (wx + wy) % 7 == 0:
                            draw.rectangle([wx, wy, wx + 3, wy + 6], fill=(255, 230, 120))

        elif i == 1:  # Dusk - Mediterranean: dusk gradient, simple silhouettes
            # Dusk gradient sky
            sky_h = int(h * 0.8)
            for yy in range(y, y + sky_h):
                t = (yy - y) / max(1, sky_h - 1)
                r = int(180 * (0.9 - 0.5 * t))
                g = int(100 * (0.7 - 0.4 * t))
                b = int(160 * (0.5 + 0.3 * t))
                draw.line([(x, yy), (x + w, yy)], fill=(r, g, b))
            # Simple boat silhouettes on horizon line
            for dx in [x + w//4, x + 3*w//4]:
                draw.polygon([
                    (dx, hy), (dx + 10, hy - 4), (dx + 20, hy),
                    (dx + 16, hy + 3), (dx + 4, hy + 3)
                ], fill=(30, 30, 40))
            # Horizon reflection lines
            for wx in range(x + 10, x + w - 10, 8):
                draw.line([(wx, hy + 1), (wx + 3, hy + 2)], fill=(60, 80, 100), width=1)

        elif i == 2:  # Night - Antalya: dark navy sky, SMALL moon, thin horizon, small lit windows
            # Night sky gradient (dark navy, not black)
            for yy in range(y, y + h):
                t = (yy - y) / max(1, h - 1)
                r = int(25 * (1 - 0.2 * t))
                g = int(25 * (1 - 0.2 * t))
                b = int(65 * (1 - 0.15 * t))
                draw.line([(x, yy), (x + w, yy)], fill=(r, g, b))
            import random
            random.seed(42)
            # Stars (sparse)
            for _ in range(15):
                sx = x + random.randint(5, w - 5)
                sy = y + random.randint(5, h - 15)
                draw.ellipse([sx, sy, sx + 1, sy + 1], fill=(255, 255, 200))
            # Small moon (top right, ~15px diameter)
            draw.ellipse([x + w - 22, y + 8, x + w - 7, y + 23], fill=(200, 200, 180))
            # Low building silhouette with lit windows (max ~40% panel width, low height)
            cx = x + w // 2
            bw = int(w * 0.38)
            bh = int(h * 0.15)  # Low buildings
            draw.rectangle([cx - bw//2, hy - bh, cx + bw//2, hy], fill=(30, 30, 50))
            # Lit windows - sparse
            for wx in range(cx - bw//2 + 4, cx + bw//2 - 4, 12):
                for wy in range(hy - bh + 2, hy - 2, 10):
                    if random.random() > 0.5:
                        draw.rectangle([wx, wy, wx + 3, wy + 5], fill=(255, 230, 140))

    # Second pass: draw ONE continuous thin horizon line across all panels
    hy = panel_rects[0][1] + panel_rects[0][3]  # y + h of first panel (all same h)
    draw.line([(panel_rects[0][0], hy), (panel_rects[2][0] + panel_rects[2][2], hy)], 
              fill=(80, 60, 90), width=1)

# ─── Mini illustrations for THE DAY IN TEN ───
def draw_mini_illustration(draw, x, y, w, h, idx):
    illustrations = [
        lambda: (draw.polygon([(x+w//2, y+5), (x+10, y+h-5), (x+w-10, y+h-5)], fill=BLUE),
                 draw.rectangle([x+w//2-8, y+h-15, x+w//2+8, y+h-5], fill=RED)),
        lambda: (draw.ellipse([x+5, y+5, x+w-5, y+h-5], fill=WHITE, outline=BLACK, width=1),
                 draw.line([(x+w//2, y+5), (x+w//2, y+h-5)], fill=BLACK, width=1),
                 draw.line([(x+5, y+h//2), (x+w-5, y+h//2)], fill=BLACK, width=1)),
        lambda: (draw.rectangle([x+w//2-8, y+5, x+w//2+8, y+h//2], fill=RED),
                 draw.polygon([(x+w//2-8, y+h//2), (x+w//2-12, y+h-5), (x+w//2+12, y+h-5), (x+w//2+8, y+h//2)], fill=RED)),
        lambda: (draw.rounded_rectangle([x+5, y+5, x+w-5, y+h-5], 4, outline=BLUE, width=2),
                 draw.ellipse([x+w//2-8, y+h//2-8, x+w//2+8, y+h//2+8], fill=BLUE),
                 draw.rectangle([x+w//2-2, y+h//2+10, x+w//2+2, y+h-5], fill=BLUE)),
        lambda: (draw.text((x+w//2-15, y+h//2-10), "ζ(s)=0", font=load_font(SANS_BOLD, 10), fill=PURPLE)),
        lambda: ([draw.polygon([(x+w//2+i*10, y+h-5), (x+w//2+i*10-5, y+5), (x+w//2+i*10+5, y+5)], fill=(255,100,0)) for i in range(-1,2)]),
        lambda: (draw.text((x+w//2-8, y+h//2-10), "₿", font=load_font(SANS_BOLD, 20), fill=ORANGE)),
        lambda: (draw.ellipse([x+w//2-10, y+h//2-10, x+w//2+10, y+h//2+10], outline=BLUE, width=2),
                 draw.line([(x+w//2, y+5), (x+w//2, y+h//2-10)], fill=BLUE, width=2),
                 draw.line([(x+5, y+h//2), (x+w//2-10, y+h//2)], fill=BLUE, width=2),
                 draw.line([(x+w//2+10, y+h//2), (x+w-5, y+h//2)], fill=BLUE, width=2),
                 draw.line([(x+w//2, y+h//2+10), (x+w//2, y+h-5)], fill=BLUE, width=2)),
        lambda: (draw.rectangle([x+w//2-15, y+5, x+w//2+15, y+15], fill=BROWN),
                 draw.rectangle([x+w//2-3, y+15, x+w//2+3, y+h-5], fill=GRAY)),
        lambda: (draw.polygon([(x+w//2, y+5), (x+w//2-8, y+h-5), (x+w//2+8, y+h-5)], fill=RED),
                 draw.rectangle([x+w//2-5, y+h-15, x+w//2+5, y+h-5], fill=ORANGE),
                 draw.line([(x+w//2-12, y+h-10), (x+w//2-20, y+h-5)], fill=ORANGE, width=2),
                 draw.line([(x+w//2+12, y+h-10), (x+w//2+20, y+h-5)], fill=ORANGE, width=2)),
    ]
    if idx < len(illustrations):
        try:
            illustrations[idx]()
        except Exception as e:
            draw.rectangle([x, y, x+w, y+h], fill=GRAY_LIGHT)

# ─── Dotted world map ───
def draw_world_map(draw, x, y, w, h):
    continents = {
        "NA": [(0.15, 0.25), (0.18, 0.22), (0.20, 0.28), (0.22, 0.32), (0.17, 0.35), (0.14, 0.30)],
        "SA": [(0.20, 0.45), (0.22, 0.50), (0.20, 0.60), (0.18, 0.55), (0.17, 0.48)],
        "EU": [(0.42, 0.20), (0.45, 0.18), (0.48, 0.20), (0.50, 0.22), (0.48, 0.25), (0.44, 0.26), (0.41, 0.24)],
        "AF": [(0.45, 0.35), (0.48, 0.40), (0.47, 0.50), (0.44, 0.55), (0.41, 0.50), (0.42, 0.42)],
        "AS": [(0.60, 0.18), (0.65, 0.16), (0.70, 0.18), (0.75, 0.22), (0.78, 0.28), (0.76, 0.35), (0.72, 0.38), (0.68, 0.35), (0.62, 0.30), (0.58, 0.25)],
        "OC": [(0.78, 0.55), (0.82, 0.58), (0.80, 0.62), (0.76, 0.60)],
    }
    
    # Draw continent outlines as connected dots (larger)
    for cont, points in continents.items():
        for i, (px, py) in enumerate(points):
            dx = x + int(px * w)
            dy = y + int(py * h)
            draw.ellipse([dx-2, dy-2, dx+2, dy+2], fill=GRAY)
        # Connect adjacent points with lines
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            dx1 = x + int(p1[0] * w)
            dy1 = y + int(p1[1] * h)
            dx2 = x + int(p2[0] * w)
            dy2 = y + int(p2[1] * h)
            draw.line([(dx1, dy1), (dx2, dy2)], fill=GRAY, width=2)
    
    pins = [
        (0.18, 0.28, "1"), (0.46, 0.38, "2"), (0.52, 0.24, "3"),
        (0.16, 0.26, "4"), (0.41, 0.19, "5"), (0.44, 0.22, "6"),
        (0.14, 0.30, "7"), (0.50, 0.30, "8"), (0.72, 0.35, "9"),
        (0.55, 0.32, "10"), (0.48, 0.25, "11"), (0.15, 0.28, "12"),
        (0.68, 0.22, "13"),
    ]
    
    for px, py, num in pins:
        dx = x + int(px * w)
        dy = y + int(py * h)
        # Smaller pin (radius 6) with outline only - lets continent show through
        draw.ellipse([dx-6, dy-6, dx+6, dy+6], outline=RED, width=2)
        draw.ellipse([dx-4, dy-4, dx+4, dy+4], fill=RED)
        f = load_font(SANS_BOLD, 10)
        tw, th = measure_text(draw, num, f)
        draw.text((dx - tw//2, dy - th//2), num, font=f, fill=WHITE)

# ─── Main generation ───
def generate():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    MARGIN = 20
    GUTTER = 12
    TOP = MARGIN

    # Pre-calculate section heights to ensure fit within 1024px
    # Masthead: 50 + 16 = 66
    # Date headline: 50
    # Subhead: ~28 (2 lines wrapped)
    # Stat strip: 60 + 12 = 72
    # Region tabs: 28 + 10 = 38
    # Timeline: 48 + 10 = 58
    # Lead panels: 200 + 12 = 212  (reduced from 250)
    # THE DAY IN TEN title: 24
    # Cards: 2 * (95 + 10) = 210  (reduced from 110)
    # Map/ALSO ON: 150 + 8 = 158  (reduced from 200)
    # DATE CHECK: 60 + 6 = 66  (reduced from 80)
    # Legend: 20 + 12 = 32
    # Footer: 16 (at H-16)
    # Total: 66+50+28+72+38+58+212+24+210+158+66+32 = 1014, footer at 1008

    # ─── 1. MASTHEAD ───
    masthead_h = 50
    draw.rectangle([MARGIN, TOP, W - MARGIN, TOP + masthead_h], fill=NAVY)
    draw.text((W//2, TOP + 8), "THE WORLD IN ONE DAY", font=FONTS["masthead"], fill=WHITE, anchor="mm")
    draw.text((W//2, TOP + 36), "35 STORIES · 6 REGIONS · EVERY ONE DATED MONDAY 23 NOVEMBER 2026",
              font=FONTS["masthead_sub"], fill=(200, 200, 220), anchor="mm")

    y = TOP + masthead_h + 16

    # ─── 2. HUGE DATE HEADLINE + SUBHEAD ───
    date_text = "Monday 23 November 2026"
    draw.text((MARGIN, y), date_text, font=FONTS["date_main"], fill=BLACK)
    y += 50

    subhead = "Nvidia board reinstates Huang · Ukraine confirms Libya sea-drone strike · COP31 collapses without fossil-fuel deal"
    # Fit subhead to full width with 20px padding on each side, wrap to max 2 lines
    max_subhead_w = W - 2*MARGIN - 40
    subhead_font, _, _ = fit_font_size(draw, subhead, SERIF_ITALIC, max_subhead_w, 20, min_size=13, padding=10)
    lines = wrap_text(draw, subhead, subhead_font, max_subhead_w)
    line_h = subhead_font.getbbox("Ag")[3] - subhead_font.getbbox("Ag")[1]
    total_h = 0
    for i, line in enumerate(lines[:2]):
        lw, _ = measure_text(draw, line, subhead_font)
        draw.text((MARGIN + 20, y + total_h), line, font=subhead_font, fill=RED)
        total_h += int(line_h * 1.2)
    y += total_h + 4

    # ─── 3. STAT STRIP ───
    stat_h = 60
    stat_y = y
    stats = [
        ("+31.5%", "Nvidia shares"),
        ("+$952bn", "Nvidia value gained"),
        ("258+", "House seats, Dem majority"),
        ("34", "missing in Indonesia fire"),
        ("$61,000", "Bitcoin rebound"),
        ("700,000", "women in EDITH trial"),
    ]
    stat_w = (W - 2*MARGIN - 5*GUTTER) // 6
    stat_nums = [n for n, _ in stats]
    # Force small font size that fits in actual render with 6px clearance on both sides
    stat_num_font = ImageFont.truetype(SANS_BOLD, 16)
    for i, (num, label) in enumerate(stats):
        sx = MARGIN + i * (stat_w + GUTTER)
        draw.rectangle([sx, stat_y, sx + stat_w, stat_y + stat_h], fill=WHITE, outline=GRAY_LIGHT, width=1)
        tw, th = measure_text(draw, num, stat_num_font)
        tx = sx + stat_w//2 - tw//2
        # Center number horizontally, position at top
        draw.text((tx, stat_y + 6), num, font=stat_num_font, fill=RED)
        # Label centered, below number
        lines = wrap_text(draw, label, FONTS["stat_label"], stat_w - 12)
        ly = stat_y + 38
        for line in lines:
            lw, lh = measure_text(draw, line, FONTS["stat_label"])
            draw.text((sx + stat_w//2 - lw//2, ly), line, font=FONTS["stat_label"], fill=GRAY)
            ly += lh + 2
    y = stat_y + stat_h + 12

    # ─── 4. REGION TABS ───
    regions = [
        ("EUROPE", 10), ("AMERICAS", 7), ("ASIA-PACIFIC", 6),
        ("MIDDLE EAST", 5), ("WORLD", 5), ("AFRICA", 2)
    ]
    tab_h = 28
    tab_y = y
    total_w = W - 2*MARGIN
    tab_w = total_w // 6
    for i, (name, count) in enumerate(regions):
        tx = MARGIN + i * tab_w
        color = REGION_COLORS[name]
        draw.rounded_rectangle([tx, tab_y, tx + tab_w - 2, tab_y + tab_h], 4, fill=color)
        tw, th = measure_text(draw, name, FONTS["region_tab"])
        draw.text((tx + tab_w//2 - tw//2, tab_y + 3), name, font=FONTS["region_tab"], fill=WHITE)
        cw, ch = measure_text(draw, str(count), FONTS["region_count"])
        draw.text((tx + tab_w//2 - cw//2, tab_y + 16), str(count), font=FONTS["region_count"], fill=WHITE)
    y = tab_y + tab_h + 10

    # ─── 5. UTC TIMELINE ───
    timeline_h = 48
    tl_y = y
    draw.rectangle([MARGIN, tl_y, W - MARGIN, tl_y + timeline_h], fill=WHITE, outline=GRAY_LIGHT, width=1)
    draw.text((MARGIN + 8, tl_y + 3), "THE DAY IN UTC", font=FONTS["timeline_time"], fill=NAVY)

    events = [
        ("18:23", "FIFA confirms UK to host 2035 Women's World Cup"),
        ("19:29", "Iran flogs singer Parastoo Ahmadi for performing without hijab"),
        ("20:02", "Merz calls 2008 Ukraine NATO decision a 'mistake'"),
        ("21:21", "NATO warns of intensifying threats"),
        ("22:18", "German-Ukrainian interceptor shoots down Russian jet drone"),
    ]
    # Fixed-width columns for 5 events
    tl_content_w = W - 2*MARGIN - 120
    col_w = tl_content_w // 5
    start_x = MARGIN + 120
    timeline_desc_font = load_font(SANS, 9)
    for i, (time, desc) in enumerate(events):
        cx = start_x + i * col_w
        # Time on top
        draw.text((cx, tl_y + 3), time, font=FONTS["timeline_time"], fill=RED)
        # Description wrapped to 2 lines max
        lines = wrap_text(draw, desc, timeline_desc_font, col_w - 4)
        for j, line in enumerate(lines[:2]):
            draw.text((cx, tl_y + 20 + j * 11), line, font=timeline_desc_font, fill=BLACK)
    y = tl_y + timeline_h + 10

    # ─── 6. THREE LEAD PANELS ───
    lead_w = (W - 2*MARGIN - 2*GUTTER) // 3
    lead_h = 200  # reduced from 250
    lead_x = MARGIN
    lead_y = y

    lead_data = [
        {
            "kicker": "WALL STREET · REPORTED",
            "tag": "REPORTED",
            "headline": "Nvidia board reinstates Huang; shares +31.5%, add $952bn in best day since 2003",
            "body": "Trump claims credit. Huang: \"Better CEO second time.\" US blacklists Megaspeed.",
            "sources": "Reuters · Bloomberg · CNN"
        },
        {
            "kicker": "BENGHAZI OFFSHORE · REPORTED",
            "tag": "REPORTED",
            "headline": "Zelenskyy confirms sea drones sank Russian warship off Libya; Baltic cargo hit",
            "body": "Kremlin warns escalation. Albania denies launch site. Strike first reported 22 Nov.",
            "sources": "Reuters · BBC · Al Jazeera"
        },
        {
            "kicker": "ANTALYA · REPORTED",
            "tag": "REPORTED",
            "headline": "COP31 collapses without deal; draft drops fossil-fuel language, first fail since 2009",
            "body": "$120bn target dropped; admits 1.5°C overshoot. Next summit: Addis Ababa.",
            "sources": "The Times · Euronews · AP"
        }
    ]

    panel_rects = []
    lead_sources_bottoms = []  # track actual bottom of sources line for each panel

    for i, data in enumerate(lead_data):
        px = lead_x + i * (lead_w + GUTTER)
        py = lead_y
        panel_rects.append((px, py, lead_w, lead_h))

        draw.rectangle([px, py, px + lead_w, py + lead_h], fill=WHITE, outline=GRAY_LIGHT, width=1)

        ill_h = int(lead_h * 0.35)

        tx = px + 10
        ty = py + ill_h + 8
        tw = lead_w - 20

        draw.text((tx, ty), data["kicker"], font=FONTS["lead_kicker"], fill=NAVY)
        tag = data["tag"]
        tag_color = RED if tag == "REPORTED" else (ORANGE if tag == "ONGOING" else (PURPLE if tag == "CLAIM" else BLUE))
        tag_w, tag_h = measure_text(draw, tag, FONTS["lead_tag"])
        draw.rounded_rectangle([tx, ty + 18, tx + tag_w + 8, ty + 18 + tag_h + 4], 3, fill=tag_color)
        draw.text((tx + 4, ty + 20), tag, font=FONTS["lead_tag"], fill=WHITE)

        hy = ty + 36
        _, headline_h = draw_text_box(draw, tx, hy, data["headline"], FONTS["lead_headline"], BLACK, tw, max_lines=3)
        hy += headline_h + 4

        _, body_h = draw_text_box(draw, tx, hy, data["body"], FONTS["lead_body"], BLACK, tw, max_lines=2)
        hy += body_h + 4

        # Measure and draw sources, record bottom
        sources_text = data["sources"]
        _, sources_h = measure_text(draw, sources_text, FONTS["lead_sources"])
        draw.text((tx, hy), sources_text, font=FONTS["lead_sources"], fill=GRAY)
        lead_sources_bottoms.append(hy + sources_h)

    ill_rects = [(r[0], r[1], r[2], int(r[3] * 0.35)) for r in panel_rects]
    print(f"DEBUG lead panels: lead_y={lead_y}, lead_h={lead_h}, ill_h={int(lead_h*0.35)}")
    for i, (x, y, w, h) in enumerate(ill_rects):
        print(f"  Panel {i}: x={x}, y={y}, w={w}, h={h}")
    draw_horizon_panels(draw, ill_rects)

    # ─── 7. THE DAY IN TEN (cards 4-13) ───
    # Compute ten_y from ACTUAL bottom of lead panel sources + line height + 6px gap
    max_sources_bottom = max(lead_sources_bottoms)
    sources_line_h = FONTS["lead_sources"].getbbox("Ag")[3] - FONTS["lead_sources"].getbbox("Ag")[1]
    ten_y = max_sources_bottom + sources_line_h + 6
    print(f"DEBUG: max_sources_bottom={max_sources_bottom}, sources_line_h={sources_line_h}, ten_y={ten_y}")

    draw.text((MARGIN, ten_y), "THE DAY IN TEN", font=FONTS["datecheck_title"], fill=NAVY)
    ten_y += 16

    ten_items = [
        {"num": 4, "region": "AMERICAS", "headline": "Democrats win 258+ House seats", "body": "GOP concedes key races", "source": "AP"},
        {"num": 5, "region": "EUROPE", "headline": "FIFA: UK hosts 2035 Women's WC", "body": "First solo UK hosting", "source": "BBC"},
        {"num": 6, "region": "EUROPE", "headline": "Belgium flights grounded; strike", "body": "Police use tear gas", "source": "Euronews"},
        {"num": 7, "region": "AMERICAS", "headline": "US states sue Musk over Grok AI", "body": "AGs say chatbot makes non-con images", "source": "Reuters"},
        {"num": 8, "region": "WORLD", "headline": "AI claims Riemann hypothesis proof", "body": "Paper submitted; millennium prize", "source": "The Times"},
        {"num": 9, "region": "ASIA-PACIFIC", "headline": "Indonesia factory fire: 34 missing", "body": "Blaze at West Java plant; rescue", "source": "Al Jazeera"},
        {"num": 10, "region": "WORLD", "headline": "Bitcoin rebounds to $61,000", "body": "Short squeeze triggers recovery", "source": "Bloomberg"},
        {"num": 11, "region": "EUROPE", "headline": "NATO vows space defence", "body": "Allies declare space domain", "source": "Reuters"},
        {"num": 12, "region": "AMERICAS", "headline": "Trump decries CA death penalty", "body": "Blasts Newsom; vows action", "source": "CNN"},
        {"num": 13, "region": "ASIA-PACIFIC", "headline": "China unveils Shenzhou-24 crew", "body": "Tiangong marks new cooperation", "source": "Xinhua"},
    ]

    card_w = (W - 2*MARGIN - 4*GUTTER) // 5
    card_h = 91  # reduced from 95
    print(f"DEBUG ten: ten_y={ten_y}, card_w={card_w}, card_h={card_h}")
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            if idx >= len(ten_items):
                break
            item = ten_items[idx]
            cx = MARGIN + col * (card_w + GUTTER)
            cy = ten_y + row * (card_h + GUTTER)
            print(f"  Card {idx}: cx={cx}, cy={cy}")

            draw.rectangle([cx, cy, cx + card_w, cy + card_h], fill=WHITE, outline=GRAY_LIGHT, width=1)

            num_r = 10
            draw.ellipse([cx + 6, cy + 6, cx + 6 + 2*num_r, cy + 6 + 2*num_r], fill=NAVY)
            nw, nh = measure_text(draw, str(item["num"]), FONTS["ten_num"])
            draw.text((cx + 6 + num_r - nw//2, cy + 6 + num_r - nh//2), str(item["num"]), font=FONTS["ten_num"], fill=WHITE)

            rcolor = REGION_COLORS[item["region"]]
            rw, rh = measure_text(draw, item["region"], FONTS["ten_tag"])
            draw.rounded_rectangle([cx + 6, cy + 30, cx + 6 + rw + 6, cy + 30 + rh + 4], 2, fill=rcolor)
            draw.text((cx + 9, cy + 32), item["region"], font=FONTS["ten_tag"], fill=WHITE)

            ill_x = cx + card_w - 42
            ill_y = cy + 6
            draw_mini_illustration(draw, ill_x, ill_y, 36, 36, idx)

            hx = cx + 6
            hy = cy + 52
            draw_text_box(draw, hx, hy, item["headline"], FONTS["ten_headline"], BLACK, card_w - 50, max_lines=2)
            hy += 2 * 12

            draw_text_box(draw, hx, hy, item["body"], FONTS["ten_body"], BLACK, card_w - 12, max_lines=1)
            hy += 10

            draw.text((hx, hy), item["source"], font=FONTS["ten_source"], fill=GRAY)

    y = ten_y + 2 * (card_h + GUTTER) + 6
    print(f"DEBUG: after ten, y={y}")

    # ─── 8. WHERE IT HAPPENED MAP + ALSO ON ───
    map_w = 400
    list_x = MARGIN + map_w + GUTTER
    list_w = W - list_x - MARGIN
    section_y = y
    section_h = 130  # reduced from 150
    print(f"DEBUG: map section_y={section_y}, section_h={section_h}")

    draw.text((MARGIN, section_y), "WHERE IT HAPPENED", font=FONTS["datecheck_title"], fill=NAVY)
    map_y = section_y + 22
    draw_world_map(draw, MARGIN, map_y, map_w, section_h - 22)

    also_y = section_y
    draw.text((list_x, also_y), "ALSO ON MONDAY 23 NOVEMBER — 22 MORE STORIES", font=FONTS["datecheck_title"], fill=NAVY)
    also_y += 22

    also_items = [
        "Iran vows 'every means' vs US Hormuz blockade",
        "India–Nepal thaw: Modi, Shah pave closer ties",
        "Russians kill 14 in Kyiv Oblast, damage 21",
        "Settler arson hits 5 Palestinian villages",
        "US adds Megaspeed (Nvidia scandal) to blacklist",
        "Democrats plan 12 debates for 2028 primary",
        "Ousted Dem House member resigns after findings",
        "Trump, Iowa governor punt Army detonation",
        "EDITH trial invites 700k women for AI screening",
        "Guterres urges AI regulation at Barbados summit",
        "UN mission urges probe into Benghazi attacks",
        "Heavy fighting in Ituri disrupts Ebola response",
        "Flames engulf beachfront hotels in Zanzibar",
        "German-Ukrainian interceptor shoots Russian drone",
        "Nepal PM visits India: Modi announces IIT campus",
        "Bangladesh garment makers eye 15% wage hike",
        "Ethereum wallets with $72bn ETH under threat",
        "Iranian singer gets 74 lashes for no hijab",
        "Visegrád Four leaders voice EU budget concerns",
        "Merz calls 2008 Ukraine NATO snub a 'mistake'",
        "Von der Leyen, Kushner clash over peace talks",
        "Israeli attacks turn Gaza to 'toxic wasteland'",
    ]

    col_w = list_w // 2
    also_num_font = load_font(SANS_BOLD, 8)
    also_text_font = load_font(SANS_COND, 6)
    for i, item in enumerate(also_items):
        col = i // 11
        row = i % 11
        ax = list_x + col * col_w
        ay = also_y + row * 9

        num = str(i + 14)
        nw, nh = measure_text(draw, num, also_num_font)
        draw.text((ax, ay), num, font=also_num_font, fill=RED)

        text_x = ax + nw + 4
        text_w = col_w - nw - 8
        draw_text_box(draw, text_x, ay, item, also_text_font, BLACK, text_w, max_lines=1, line_spacing=1.0)

    y = section_y + section_h + 4

    # ─── 9. DATE CHECK BOX + TAG LEGEND ───
    dc_y = y
    dc_w = W - 2*MARGIN

    # Date check text items (can be shortened from the end if needed)
    dc_base = "Wires read up to 22:18 UTC Mon 23 Nov. Every story on this page happened or was first reported on Mon 23 Nov 2026 in at least one time zone. Left out: "
    dc_items = [
        "COP31 dawn text (Sun 22 Nov)",
        "Manchester Co-op Live evacuation (Sun 22 Nov)",
        "Russia 400-drone+110-missile barrage (19–20 Nov)",
        "Peru quake (Fri 20 Nov, USGS 6.7)",
        "SK education minister quits (Sun 22 Nov)",
        "Ukraine 186-drone raid (21–22 Nov)",
        "HK Election Committee vote (Sun 22 Nov)",
        "Verstappen wins Las Vegas GP (Sun 22 Nov)",
        "Libya strike first wires late 22 Nov (23 Nov is Zelenskyy confirmation)",
    ]

    # Footer position (allowed up to y=1014)
    footer_y = H - 10  # 1014, was H-16=1008

    # Measure legend height: "TAG LEGEND" title (16px) + tag row (max th+4)
    legend_title_h = 16
    tag_font = FONTS["legend_item"]
    max_tag_th = max(measure_text(draw, tag, tag_font)[1] for tag, _, _ in [
        ("ONGOING", "", ORANGE), ("REPORTED", "", RED), ("CLAIM", "", PURPLE), ("OFFICIALS SAY", "", BLUE)
    ])
    legend_row_h = max_tag_th + 4
    legend_block_h = 4 + legend_title_h + legend_row_h  # gap + title + row

    # Find max number of items that fit
    # Box: title area (6+12+6=24) + text_height + bottom_pad(6) = 30 + text_height
    # Gap to legend: 6px
    # Total from dc_y: dc_h + 6 + legend_block_h = (30 + text_height) + 6 + legend_block_h
    # Must fit: dc_y + total <= footer_y
    max_total_h = footer_y - dc_y
    # available for text_height: max_total_h - 30 - 6 - legend_block_h
    avail_text_h = max_total_h - 30 - 6 - legend_block_h
    print(f"DEBUG: dc_y={dc_y}, footer_y={footer_y}, max_total_h={max_total_h}, legend_block_h={legend_block_h}, avail_text_h={avail_text_h}")

    dc_text = ""
    text_height = 0
    for keep in range(len(dc_items), -1, -1):
        selected = dc_items[:keep]
        test_text = dc_base + " · ".join(selected) + "."
        lines = wrap_text(draw, test_text, FONTS["datecheck_body"], dc_w - 20)
        if len(lines) > 3:
            lines = lines[:3]
        line_h = FONTS["datecheck_body"].getbbox("Ag")[3] - FONTS["datecheck_body"].getbbox("Ag")[1]
        text_height = sum(int(line_h * 1.2) for _ in lines)
        dc_h = 30 + text_height
        total_h = dc_h + 6 + legend_block_h
        if dc_y + total_h <= footer_y:
            dc_text = test_text
            print(f"DEBUG: keeping {keep} items, lines={len(lines)}, text_height={text_height}, dc_h={dc_h}, total_h={total_h}")
            break
    else:
        # Fallback: use empty items (just base text)
        dc_text = dc_base.rstrip(" :") + "."
        lines = wrap_text(draw, dc_text, FONTS["datecheck_body"], dc_w - 20)
        line_h = FONTS["datecheck_body"].getbbox("Ag")[3] - FONTS["datecheck_body"].getbbox("Ag")[1]
        text_height = sum(int(line_h * 1.2) for _ in lines[:3])
        dc_h = 30 + text_height
        print(f"DEBUG: fallback, lines={len(lines)}, text_height={text_height}, dc_h={dc_h}")

    # Draw DATE CHECK box
    draw.rectangle([MARGIN, dc_y, MARGIN + dc_w, dc_y + dc_h], fill=(255, 240, 240), outline=RED, width=2)
    draw.text((MARGIN + 10, dc_y + 6), "DATE CHECK", font=FONTS["datecheck_title"], fill=RED)
    draw_text_box(draw, MARGIN + 10, dc_y + 24, dc_text, FONTS["datecheck_body"], BLACK, dc_w - 20, max_lines=3)

    # TAG LEGEND at box_bottom + 6px
    legend_x = MARGIN
    legend_y = dc_y + dc_h + 6
    draw.text((legend_x, legend_y), "TAG LEGEND", font=FONTS["legend_title"], fill=NAVY)
    legend_y += 16

    tags = [
        ("ONGOING", "still developing", ORANGE),
        ("REPORTED", "one source's claim, not yet confirmed", RED),
        ("CLAIM", "a party's claim, contested", PURPLE),
        ("OFFICIALS SAY", "attributed, not verified", BLUE),
    ]

    tag_x = legend_x
    for tag, desc, color in tags:
        tw, th = measure_text(draw, tag, FONTS["legend_item"])
        draw.rounded_rectangle([tag_x, legend_y, tag_x + tw + 8, legend_y + th + 4], 2, fill=color)
        draw.text((tag_x + 4, legend_y + 2), tag, font=FONTS["legend_item"], fill=WHITE)
        tag_x += tw + 8 + 8
        dw, dh = measure_text(draw, desc, FONTS["legend_item"])
        draw.text((tag_x, legend_y + 2), desc, font=FONTS["legend_item"], fill=GRAY)
        tag_x += dw + 16

    # ─── Verification measurements ───
    max_sources_bottom = max(lead_sources_bottoms)
    sources_line_h = FONTS["lead_sources"].getbbox("Ag")[3] - FONTS["lead_sources"].getbbox("Ag")[1]
    ten_header_y = max_sources_bottom + sources_line_h + 6
    gap_above_ten = ten_header_y - max_sources_bottom
    print(f"VERIFY: Defect 1 - THE DAY IN TEN header at y={ten_header_y}, max sources bottom={max_sources_bottom}, gap={gap_above_ten}px (need >=4)")

    # DATE CHECK measurements
    dc_text_bottom = dc_y + 24 + text_height
    dc_box_bottom = dc_y + dc_h
    text_padding = dc_box_bottom - dc_text_bottom
    legend_start = dc_y + dc_h + 6
    legend_title_y = legend_start
    legend_row_y = legend_start + 16
    max_tag_th = max(measure_text(draw, tag, FONTS["legend_item"])[1] for tag, _, _ in tags)
    legend_bottom = legend_row_y + max_tag_th + 4
    footer_gap = footer_y - legend_bottom
    print(f"VERIFY: Defect 2 - DATE CHECK: box_bottom={dc_box_bottom}, text_bottom={dc_text_bottom}, padding={text_padding}px (need >=6)")
    print(f"VERIFY: Defect 2 - TAG LEGEND: starts at box_bottom+6={legend_start}, legend_bottom={legend_bottom}, footer_y={footer_y}, gap={footer_gap}px (need >=0)")

    # ─── 10. FOOTER ───
    draw.text((W//2, footer_y), "Sources: Reuters · AP · CNN · BBC · Al Jazeera · The Times · Euronews",
              font=FONTS["footer"], fill=GRAY, anchor="mm")

    # ─── Save ───
    img.save(OUT_PATH, "PNG", optimize=True)
    print(f"Saved to {OUT_PATH}")

    import os
    size = os.path.getsize(OUT_PATH)
    print(f"File size: {size} bytes ({size/1024:.1f} KiB)")
    if size > 1048576:
        print("WARNING: File exceeds 1 MiB!")

    with Image.open(OUT_PATH) as im:
        print(f"Dimensions: {im.size}, Mode: {im.mode}")

    return OUT_PATH

if __name__ == "__main__":
    generate()