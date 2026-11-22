#!/usr/bin/env python3
"""Entry for make.fun bounty news-image-20261122.

Draws a one-page newspaper front page summing up the world news of
Sunday 22 November 2026 and writes it to $MAKEFUN_OUTPUT_DIR/entry.png
(or /output/entry.png when the variable is unset).

Python 3.13, Pillow only, no network, no randomness, no clock:
the same bytes on every run.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

PAPER = (248, 244, 236)
INK = (20, 20, 20)
NAVY = (20, 33, 61)
RED = (179, 39, 30)
BLUE = (29, 78, 137)
GOLD = (192, 138, 0)
GREY = (110, 105, 95)
CARD = (255, 255, 255)
CARD_LINE = (216, 210, 196)
LIGHT_BLUE = (214, 230, 242)
LIGHT_GOLD = (247, 232, 190)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def font(name, size):
    """Load a DejaVu font by role, falling back to PIL's default font."""
    wanted = {
        "serif_bold": "DejaVuSerif-Bold.ttf",
        "serif": "DejaVuSerif.ttf",
        "sans_bold": "DejaVuSans-Bold.ttf",
        "sans": "DejaVuSans.ttf",
    }[name]
    for path in FONT_PATHS:
        if path.endswith(wanted):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                break
    return ImageFont.load_default(size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading):
    """Draw lines of text, return the y below the last line."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_poster(draw, x0, y0, x1, y1):
    """A 'WANTED' poster with a silhouette and a CAPTURED stamp."""
    draw.rectangle([x0, y0, x1, y1], fill=(255, 253, 247), outline=INK, width=3)
    draw.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], outline=GREY, width=1)
    f_small = font("sans_bold", 22)
    label = "WANTED"
    tw = draw.textlength(label, font=f_small)
    draw.text(((x0 + x1 - tw) / 2, y0 + 16), label, font=f_small, fill=INK)
    # Silhouette: head + shoulders.
    cx = (x0 + x1) // 2
    cy = y0 + 108
    draw.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], fill=NAVY)
    draw.pieslice([cx - 78, cy + 52, cx + 78, cy + 190], 180, 360, fill=NAVY)
    draw.rectangle([x0 + 14, y0 + 232, x1 - 14, y0 + 236], fill=GREY)
    # CAPTURED stamp, rotated slightly, kept inside the poster frame.
    stamp = Image.new("RGBA", (240, 56), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sf = font("sans_bold", 30)
    sd.text((8, 9), "CAPTURED", font=sf, fill=RED + (255,))
    sd.rectangle([2, 2, 237, 53], outline=RED + (255,), width=4)
    stamp = stamp.rotate(-10, expand=True, resample=Image.BICUBIC)
    draw._image.paste(stamp, (cx - 120, y0 + 232), stamp)


def draw_laptop(draw, x, y, s):
    """Monitor with a warning triangle: the FBI database hack."""
    draw.rectangle([x, y, x + s, y + int(s * 0.62)], fill=LIGHT_BLUE,
                   outline=NAVY, width=3)
    draw.rectangle([x + int(s * 0.36), y + int(s * 0.62), x + int(s * 0.64),
                    y + int(s * 0.72)], fill=NAVY)
    draw.rectangle([x + int(s * 0.22), y + int(s * 0.72), x + int(s * 0.78),
                    y + int(s * 0.78)], fill=NAVY)
    cx, cy = x + s // 2, y + int(s * 0.31)
    draw.polygon([(cx, cy - 16), (cx + 17, cy + 12), (cx - 17, cy + 12)],
                 fill=GOLD, outline=INK)
    draw.text((cx - 2, cy - 8), "!", font=font("sans_bold", 20), fill=INK)


def draw_ship(draw, x, y, s):
    """Ship hull on waves with a small blast star above."""
    draw.polygon([(x, y + int(s * 0.55)), (x + s, y + int(s * 0.55)),
                  (x + int(s * 0.82), y + int(s * 0.82)),
                  (x + int(s * 0.18), y + int(s * 0.82))],
                 fill=NAVY)
    draw.rectangle([x + int(s * 0.3), y + int(s * 0.28), x + int(s * 0.42),
                    y + int(s * 0.55)], fill=NAVY)
    draw.rectangle([x + int(s * 0.55), y + int(s * 0.18), x + int(s * 0.63),
                    y + int(s * 0.55)], fill=NAVY)
    for i, wy in enumerate((int(s * 0.88), int(s * 0.97))):
        for k in range(4):
            wx = x + k * int(s * 0.26) + (i * 12)
            draw.arc([wx, y + wy, wx + 22, y + wy + 12], 180, 360,
                     fill=BLUE, width=3)
    # Blast star.
    bx, by = x + int(s * 0.78), y + 6
    for ang in range(0, 360, 45):
        import math
        r = 16 if ang % 90 == 0 else 8
        dx = int(r * math.cos(math.radians(ang)))
        dy = int(r * math.sin(math.radians(ang)))
        draw.line([bx, by, bx + dx, by + dy], fill=RED, width=3)
    draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=RED)


def draw_globe(draw, x, y, s):
    """Globe with a small flame: COP31 climate deadlock."""
    cx, cy, r = x + s // 2, y + s // 2 - 4, s // 2 - 4
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=LIGHT_BLUE,
                 outline=BLUE, width=3)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=BLUE,
                 width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=BLUE, width=2)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 0, 180, fill=BLUE,
             width=2)
    # Flame.
    fx, fy = x + s - 16, y + s - 14
    draw.polygon([(fx, fy - 18), (fx + 10, fy), (fx + 4, fy),
                  (fx, fy + 6), (fx - 4, fy), (fx - 10, fy)],
                 fill=RED)


def draw_aidbox(draw, x, y, s):
    """Open aid box with a cross on it."""
    draw.polygon([(x + 6, y + int(s * 0.3)), (x + int(s * 0.5), y + 4),
                  (x + s - 6, y + int(s * 0.3)), (x + s - 6, y + s - 6),
                  (x + 6, y + s - 6)], fill=(232, 214, 178),
                 outline=INK, width=3)
    draw.rectangle([x + int(s * 0.44), y + int(s * 0.42), x + int(s * 0.56),
                    y + int(s * 0.72)], fill=RED)
    draw.rectangle([x + int(s * 0.34), y + int(s * 0.52), x + int(s * 0.66),
                    y + int(s * 0.62)], fill=RED)


def draw_ballot(draw, x, y, s):
    """Ballot box with a check mark."""
    draw.rectangle([x + 4, y + int(s * 0.34), x + s - 4, y + s - 4],
                   fill=LIGHT_BLUE, outline=NAVY, width=3)
    draw.rectangle([x + int(s * 0.36), y + int(s * 0.3), x + int(s * 0.64),
                    y + int(s * 0.42)], fill=NAVY)
    draw.line([x + int(s * 0.22), y + int(s * 0.62), x + int(s * 0.42),
               y + int(s * 0.8)], fill=RED, width=5)
    draw.line([x + int(s * 0.42), y + int(s * 0.8), x + int(s * 0.82),
               y + int(s * 0.3)], fill=RED, width=5)


def draw_rugby(draw, x, y, s):
    """Rugby ball with a seam."""
    import math
    cx, cy = x + s // 2, y + s // 2
    rx, ry = s // 2 - 4, int(s * 0.32)
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(150, 84, 32),
                 outline=INK, width=3)
    draw.line([cx - rx + 10, cy, cx + rx - 10, cy], fill=INK, width=2)
    for t in (-0.55, -0.18, 0.18, 0.55):
        px = cx + int(rx * t)
        half = int(ry * math.sqrt(max(0.0, 1 - t * t)) * 0.55)
        draw.line([px, cy - half, px, cy + half], fill=INK, width=2)


CARDS = [
    ("FBI PROBES HACK OF ITS\nCRIME DATABASE",
     "The bureau confirms an apparent intrusion into the NCIC, the database shared by federal and local police.",
     draw_laptop),
    ("SHIP ATTACKED IN\nGULF OF FINLAND",
     "A Russia-bound merchant vessel is hit by a drone strike; Helsinki warns the Ukraine war is spilling over.",
     draw_ship),
    ("COP31 DEADLOCK OVER\nFOSSIL FUELS",
     "Nearly 200 nations stall on a new climate deal as the fight over fossil fuels blocks agreement.",
     draw_globe),
    ("FOUR NATIONS URGE\nGAZA AID ACCESS",
     "Australia, Canada, Italy and the UK call on Israel to let aid reach flooded Gaza without restriction.",
     draw_aidbox),
    ("EISENKOT TAPPED TO\nFORM GOVERNMENT",
     "Israel's president asks ex-army chief Gadi Eisenkot to form a cabinet, bypassing Netanyahu.",
     draw_ballot),
    ("FRANCE REACH\nRUGBY FINAL",
     "France beat Argentina in Paris to book a Nations Championship final against South Africa.",
     draw_rugby),
]


def draw_card(draw, x, y, w, h, headline, summary, icon_fn):
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=CARD_LINE,
                   width=2)
    icon_fn(draw, x + 14, y + 12, 62)
    f_head = font("sans_bold", 21)
    f_sum = font("sans", 16)
    hx = x + 88
    head_lines = wrap(draw, headline.replace("\n", " "), f_head, w - 102)
    yy = text_block(draw, hx, y + 12, head_lines, f_head, INK, 25)
    sum_lines = wrap(draw, summary, f_sum, w - 28)
    text_block(draw, x + 14, yy + 6, sum_lines, f_sum, (58, 56, 50), 20)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Masthead.
    draw.rectangle([0, 0, W, 92], fill=NAVY)
    f_mast = font("serif_bold", 52)
    title = "THE WORLD IN ONE PAGE"
    tw = draw.textlength(title, font=f_mast)
    draw.text(((W - tw) / 2, 16), title, font=f_mast, fill=(255, 255, 255))
    draw.rectangle([0, 92, W, 138], fill=RED)
    f_date = font("sans_bold", 32)
    date = "SUNDAY, 22 NOVEMBER 2026"
    tw = draw.textlength(date, font=f_date)
    draw.text(((W - tw) / 2, 100), date, font=f_date, fill=(255, 255, 255))

    # Lead story.
    f_kick = font("sans_bold", 19)
    draw.text((28, 156), "LEAD STORY  —  MEXICO", font=f_kick, fill=RED)
    f_lead = font("serif_bold", 44)
    lead_lines = ["MEXICO CAPTURES", "\u2018EL CHAPO ISIDRO\u2019"]
    yy = text_block(draw, 28, 186, lead_lines, f_lead, INK, 52)
    f_lead_sum = font("sans", 20)
    lead_sum = ("Mexican troops storm a Sinaloa hideout in a shoot-out and "
                "arrest Fausto Isidro Meza Flores \u2014 a fugitive on the "
                "FBI\u2019s 10 most wanted list.")
    sum_lines = wrap(draw, lead_sum, f_lead_sum, 600)
    text_block(draw, 28, yy + 10, sum_lines, f_lead_sum, (58, 56, 50), 27)
    draw.rectangle([28, 448, 628, 452], fill=CARD_LINE)
    f_cap = font("sans_bold", 17)
    draw.text((28, 460), "ARRESTED AFTER A GUNFIGHT AT A REMOTE HIDE-OUT",
              font=f_cap, fill=GREY)
    draw_poster(draw, 660, 152, 996, 470)

    # Section label + card grid.
    draw.rectangle([28, 496, 996, 498], fill=INK)
    f_sec = font("sans_bold", 20)
    draw.text((28, 508), "MORE FROM THE DAY", font=f_sec, fill=INK)
    card_w, card_h = 312, 196
    xs = [28, 356, 684]
    ys = [544, 756]
    for i, (headline, summary, icon_fn) in enumerate(CARDS):
        draw_card(draw, xs[i % 3], ys[i // 3], card_w, card_h,
                  headline, summary, icon_fn)

    # Ticker strip (shrink the font until the line fits the width).
    draw.rectangle([0, 964, W, 996], fill=NAVY)
    ticker = ("ALSO:  6.7 quake shakes Peru\u2019s Andes, no casualties  •  "
              "4.1 quake hits Myanmar  •  TikTok launches deepfake detector")
    tick_size = 16
    while tick_size > 10:
        f_tick = font("sans", tick_size)
        if draw.textlength(ticker, font=f_tick) <= 1000:
            break
        tick_size -= 1
    tw = draw.textlength(ticker, font=f_tick)
    draw.text(((W - tw) / 2, 974), ticker, font=f_tick, fill=(255, 255, 255))

    # Footer.
    f_foot = font("sans", 14)
    foot = "Compiled from wire reports  •  22 NOVEMBER 2026"
    tw = draw.textlength(foot, font=f_foot)
    draw.text(((W - tw) / 2, 1004), foot, font=f_foot, fill=GREY)

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    img.save(os.path.join(out_dir, "entry.png"), format="PNG", optimize=True)


if __name__ == "__main__":
    main()
