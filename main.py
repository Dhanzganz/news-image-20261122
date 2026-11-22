#!/usr/bin/env python3
"""Entry for make.fun bounty news-image-20261122 (round 2).

Pure Python standard library only: no PIL, no third-party imports.
Draws a 1024x1024 front page for Sunday 22 November 2026 and writes it
as a PNG to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).
Deterministic: same bytes on every run. No network, no clock, no randomness.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

NAVY = (14, 42, 71)
RED = (176, 30, 40)
GOLD = (201, 162, 39)
PAPER = (251, 248, 241)
INK = (20, 20, 20)
GREY = (85, 85, 85)
TAN = (243, 233, 210)
LIGHT = (220, 232, 242)
WHITE = (255, 255, 255)
BROWN = (122, 74, 33)
GREEN = (34, 120, 60)

# 5x7 bitmap font. Each glyph is 7 rows of 5 characters ('#' = on).
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "*": (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "%": ("##..#", "##.#.", "..#..", ".#...", "#..##", "#..##", "....."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = r
                self.px[i + 1] = g
                self.px[i + 2] = b

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def circle(self, cx, cy, r, color, t=2):
        for rr in range(r - t + 1, r + 1):
            for dy in range(-rr, rr + 1):
                dx = int(math.sqrt(max(0, rr * rr - dy * dy)))
                self.set(cx - dx, cy + dy, color)
                self.set(cx + dx, cy + dy, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            dx = int(rx * math.sqrt(max(0.0, 1.0 - (dy * dy) / float(ry * ry))))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def fill_triangle(self, p0, p1, p2, color):
        (x0, y0), (x1, y1), (x2, y2) = p0, p1, p2
        ymin = min(y0, y1, y2)
        ymax = max(y0, y1, y2)
        for y in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in ((p0, p1), (p1, p2), (p2, p0)):
                if ay == by:
                    continue
                if (y >= min(ay, by)) and (y < max(ay, by) or y == ymax):
                    t = (y - ay) / float(by - ay)
                    xs.append(ax + t * (bx - ax))
            if len(xs) >= 2:
                xa = int(min(xs))
                xb = int(max(xs))
                self.fill_rect(xa, y, xb - xa + 1, 1, color)


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_char(cv, ch, x, y, scale, color):
    glyph = FONT.get(ch, FONT[" "])
    for row in range(7):
        bits = glyph[row]
        for col in range(5):
            if bits[col] == "#":
                cv.fill_rect(x + col * scale, y + row * scale, scale, scale, color)


def draw_text(cv, text, x, y, scale, color):
    text = text.upper().replace("\u2014", "-").replace("\u2019", "'")
    cx = x
    for ch in text:
        draw_char(cv, ch, cx, y, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, text, cx, y, scale, color):
    text = text.upper().replace("\u2014", "-").replace("\u2019", "'")
    w = text_width(text, scale)
    draw_text(cv, text, cx - w // 2, y, scale, color)


def wrap_text(text, max_width, scale):
    text = text.upper().replace("\u2014", "-").replace("\u2019", "'")
    char_w = 6 * scale
    max_chars = max(1, max_width // char_w)
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        cur = ""
        for word in words:
            trial = (cur + " " + word).strip() if cur else word
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                while len(word) > max_chars:
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                cur = word
        if cur:
            lines.append(cur)
    return lines


def draw_wrapped(cv, text, x, y, max_width, scale, color, leading=3):
    lines = wrap_text(text, max_width, scale)
    for i, line in enumerate(lines):
        draw_text(cv, line, x, y + i * (7 * scale + leading), scale, color)
    return len(lines)


# ---- tiny icons, drawn in a 64x64 box at (ox, oy) ----

def icon_laptop(cv, ox, oy):
    cv.fill_triangle((ox + 32, oy + 4), (ox + 20, oy + 24), (ox + 44, oy + 24), RED)
    cv.fill_rect(ox + 30, oy + 11, 4, 7, WHITE)
    cv.fill_rect(ox + 30, oy + 20, 4, 3, WHITE)
    cv.rect(ox + 10, oy + 28, 44, 20, NAVY, 2)
    cv.fill_rect(ox + 6, oy + 50, 52, 4, NAVY)


def icon_ship(cv, ox, oy):
    cv.fill_rect(ox + 30, oy + 10, 3, 30, NAVY)
    cv.fill_triangle((ox + 33, oy + 10), (ox + 33, oy + 20), (ox + 47, oy + 15), RED)
    cv.fill_triangle((ox + 8, oy + 40), (ox + 56, oy + 40), (ox + 48, oy + 54), NAVY)
    cv.fill_triangle((ox + 8, oy + 40), (ox + 56, oy + 40), (ox + 16, oy + 54), NAVY)
    cv.hline(ox + 4, oy + 58, 56, NAVY)
    cv.hline(ox + 10, oy + 61, 44, NAVY)


def icon_globe(cv, ox, oy):
    cv.fill_circle(ox + 32, oy + 32, 22, LIGHT)
    cv.circle(ox + 32, oy + 32, 22, NAVY, 2)
    cv.fill_ellipse(ox + 32, oy + 32, 8, 22, LIGHT)
    cv.circle(ox + 32, oy + 32, 22, NAVY, 1)
    for dy in (-11, 0, 11):
        cv.hline(ox + 14, oy + 32 + dy, 36, NAVY)
    cv.line(ox + 24, oy + 12, ox + 40, oy + 52, NAVY)


def icon_aid(cv, ox, oy):
    cv.fill_rect(ox + 10, oy + 12, 44, 8, NAVY)
    cv.rect(ox + 12, oy + 20, 40, 34, NAVY, 2)
    cv.fill_rect(ox + 28, oy + 26, 8, 22, RED)
    cv.fill_rect(ox + 19, oy + 33, 26, 8, RED)


def icon_ballot(cv, ox, oy):
    cv.fill_rect(ox + 26, oy + 6, 14, 16, WHITE)
    cv.rect(ox + 26, oy + 6, 14, 16, NAVY, 1)
    cv.line(ox + 28, oy + 14, ox + 31, oy + 18, GREEN)
    cv.line(ox + 31, oy + 18, ox + 38, oy + 9, GREEN)
    cv.fill_rect(ox + 20, oy + 22, 24, 4, NAVY)
    cv.rect(ox + 12, oy + 26, 40, 26, NAVY, 2)


def icon_rugby(cv, ox, oy):
    cv.fill_ellipse(ox + 32, oy + 32, 24, 15, BROWN)
    cv.line(ox + 12, oy + 32, ox + 52, oy + 32, WHITE)
    for dx in (-8, 0, 8):
        cv.vline(ox + 32 + dx, oy + 27, 10, WHITE)


ICONS = (icon_laptop, icon_ship, icon_globe, icon_aid, icon_ballot, icon_rugby)

CARDS = (
    ("FBI PROBES HACK OF ITS CRIME DATABASE",
     "The bureau confirms an apparent intrusion into the NCIC, the database shared by federal and local police."),
    ("SHIP ATTACKED IN GULF OF FINLAND",
     "A Russia-bound merchant vessel is hit by a drone strike; Helsinki warns the Ukraine war is spilling over."),
    ("COP31 DEADLOCK OVER FOSSIL FUELS",
     "Nearly 200 nations stall on a new climate deal as the fight over fossil fuels blocks agreement."),
    ("FOUR NATIONS URGE GAZA AID ACCESS",
     "Australia, Canada, Italy and the UK call on Israel to let aid reach flooded Gaza without restriction."),
    ("EISENKOT TAPPED TO FORM GOVERNMENT",
     "Israel's president asks ex-army chief Gadi Eisenkot to form a cabinet, bypassing Netanyahu."),
    ("FRANCE REACH RUGBY FINAL",
     "France beat Argentina in Paris to book a Nations Championship final against South Africa."),
)


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        start = y * cv.w * 3
        raw += cv.px[start:start + cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", comp)
        + chunk(b"IEND", b"")
    )


def build():
    cv = Canvas(W, H, PAPER)

    # Masthead
    cv.fill_rect(0, 0, W, 92, NAVY)
    draw_text_centered(cv, "THE WORLD IN ONE PAGE", W // 2, 28, 5, WHITE)
    cv.fill_rect(0, 92, W, 4, GOLD)

    # Date strip
    cv.fill_rect(0, 96, W, 36, RED)
    draw_text_centered(cv, "SUNDAY, 22 NOVEMBER 2026", W // 2, 103, 3, WHITE)

    # ---- Lead story, left column ----
    draw_text(cv, "BREAKING - MEXICO", 24, 150, 2, RED)
    draw_text(cv, "MEXICO CAPTURES", 24, 180, 4, NAVY)
    draw_text(cv, "'EL CHAPO ISIDRO'", 24, 216, 4, NAVY)
    cv.fill_rect(24, 254, 576, 3, GOLD)
    draw_wrapped(
        cv,
        "Mexican troops storm a Sinaloa hideout in a shoot-out and arrest "
        "Fausto Isidro Meza Flores - a fugitive on the FBI's 10 most wanted list.",
        24, 272, 560, 2, INK, leading=3,
    )
    # Fact box (words taken from the lead summary above)
    cv.rect(24, 372, 576, 128, NAVY, 2)
    cv.fill_rect(24, 372, 576, 4, NAVY)
    draw_text(cv, "THE CAPTURE", 40, 392, 2, NAVY)
    facts = (
        "MEXICAN TROOPS STORMED A SINALOA HIDEOUT",
        "ARRESTED IN A SHOOT-OUT",
        "ON THE FBI'S 10 MOST WANTED LIST",
    )
    for i, fact in enumerate(facts):
        y = 420 + i * 24
        cv.fill_circle(48, y + 6, 4, RED)
        draw_text(cv, fact, 62, y, 2, INK)

    # ---- WANTED poster, right column ----
    cv.fill_rect(624, 148, 376, 364, TAN)
    cv.rect(624, 148, 376, 364, NAVY, 3)
    draw_text_centered(cv, "WANTED", 812, 164, 5, NAVY)
    cv.fill_circle(812, 262, 46, NAVY)
    cv.fill_ellipse(812, 372, 100, 44, NAVY)
    cv.rect(700, 424, 224, 44, RED, 3)
    draw_text_centered(cv, "CAPTURED", 812, 436, 3, RED)
    draw_text_centered(cv, "FBI 10 MOST WANTED", 812, 480, 2, NAVY)

    # ---- More from the day ----
    draw_text(cv, "MORE FROM THE DAY", 24, 536, 3, NAVY)
    cv.fill_rect(24, 570, 976, 3, GOLD)

    for i, (headline, summary) in enumerate(CARDS):
        col = i % 2
        row = i // 2
        x = 24 + col * 496
        y = 580 + row * 120
        cv.fill_rect(x, y, 480, 116, WHITE)
        cv.rect(x, y, 480, 116, NAVY, 1)
        cv.fill_rect(x + 10, y + 10, 64, 64, LIGHT)
        cv.rect(x + 10, y + 10, 64, 64, NAVY, 1)
        ICONS[i](cv, x + 10, y + 10)
        tx = x + 88
        tw = 480 - 88 - 12
        head_lines = wrap_text(headline, tw, 2)
        for j, line in enumerate(head_lines[:2]):
            draw_text(cv, line, tx, y + 8 + j * 17, 2, NAVY)
        sy = y + 8 + 2 * 17 + 4
        draw_wrapped(cv, summary, tx, sy, tw, 2, INK, leading=3)

    # ---- Ticker ----
    cv.fill_rect(0, 944, W, 48, RED)
    draw_text(
        cv,
        "ALSO: 6.7 QUAKE SHAKES PERU'S ANDES, NO CASUALTIES \u2022 4.1 QUAKE HITS MYANMAR",
        12, 950, 2, WHITE,
    )
    draw_text(cv, "TIKTOK LAUNCHES DEEPFAKE DETECTOR", 12, 970, 2, WHITE)

    # ---- Footer ----
    draw_text_centered(
        cv, "COMPILED FROM WIRE REPORTS - 22 NOVEMBER 2026", W // 2, 1002, 2, GREY
    )
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
