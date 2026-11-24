"""news-image-20261123: draw one newspaper front page that sums up the world
news of Monday 23 November 2026, and write it to /output/entry.png.

Runs with no network. Pure drawing with Pillow and the DejaVu fonts that ship
with the system; every run produces the same bytes. Run it with:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
INK = (18, 18, 18)
PAPER = (250, 247, 238)
RED = (178, 34, 34)
BLUE = (28, 68, 128)
GREY = (110, 108, 100)
LIGHT = (232, 228, 218)
TEAL = (14, 110, 110)
ORANGE = (214, 110, 20)

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts",
]


def find_font(names):
    """Return the first usable font file from the usual system locations."""
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.isfile(p):
                return p
    return None


def font(names, size):
    p = find_font(names)
    if p:
        return ImageFont.truetype(p, size)
    return ImageFont.load_default()


SERIF_B = ["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"]
SERIF = ["DejaVuSerif.ttf", "LiberationSerif-Regular.ttf"]
SERIF_I = ["DejaVuSerif-Italic.ttf", "LiberationSerif-Italic.ttf"]
SANS_B = ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
SANS = ["DejaVuSans.ttf", "LiberationSans-Regular.ttf"]


def wrap(draw, text, fnt, width):
    """Split text into lines that fit inside width pixels."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, width, text, fnt, fill=INK, leading=None):
    """Draw wrapped text; return the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x0, y, x1, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def globe(draw, cx, cy, r):
    """A simple wireframe globe: disc, meridians, parallels, land blobs."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(196, 222, 235),
                 outline=BLUE, width=4)
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
                 outline=BLUE, width=2)
    draw.ellipse([cx - r * 0.85, cy - r * 0.62, cx + r * 0.85, cy + r * 0.62],
                 outline=BLUE, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=BLUE, width=2)
    draw.line([(cx - r * 0.82, cy - r * 0.55), (cx + r * 0.82, cy - r * 0.55)],
              fill=BLUE, width=2)
    draw.line([(cx - r * 0.82, cy + r * 0.55), (cx + r * 0.82, cy + r * 0.55)],
              fill=BLUE, width=2)
    # land masses, kept abstract so nothing reads as a wrong map
    draw.ellipse([cx - r * 0.72, cy - r * 0.55, cx - r * 0.18, cy - r * 0.05],
                 fill=(96, 160, 96))
    draw.ellipse([cx + r * 0.05, cy + r * 0.05, cx + r * 0.68, cy + r * 0.55],
                 fill=(96, 160, 96))
    draw.ellipse([cx - r * 0.3, cy + r * 0.3, cx + r * 0.1, cy + r * 0.72],
                 fill=(120, 175, 110))


def stamp(draw, x, y, text, fnt, color=RED, angle=-8):
    """A rotated rubber-stamp label on its own layer."""
    tmp = Image.new("RGBA", (520, 120), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    tw = td.textlength(text, font=fnt)
    td.rectangle([8, 18, tw + 34, 78], outline=color, width=5)
    td.text((20, 26), text, font=fnt, fill=color)
    tmp = tmp.rotate(angle, expand=True, resample=Image.BICUBIC)
    draw._image.paste(tmp, (x, y), tmp)


def pic_ship(draw, x, y, s):
    """Warship at sea under a small drone."""
    draw.rectangle([x, y + s * 0.62, x + s, y + s * 0.8], fill=GREY)
    draw.polygon([(x + s * 0.08, y + s * 0.62), (x + s * 0.92, y + s * 0.62),
                  (x + s * 0.78, y + s * 0.8), (x + s * 0.22, y + s * 0.8)],
                 fill=(70, 70, 78))
    draw.rectangle([x + s * 0.42, y + s * 0.42, x + s * 0.55, y + s * 0.62],
                   fill=(70, 70, 78))
    for i in range(3):
        wx = x + s * (0.1 + i * 0.3)
        draw.arc([wx, y + s * 0.82, wx + s * 0.22, y + s * 0.98],
                 180, 360, fill=BLUE, width=3)
    # drone above
    dx, dy = x + s * 0.62, y + s * 0.08
    draw.ellipse([dx - 8, dy - 6, dx + 8, dy + 6], fill=INK)
    for ox, oy in [(-16, -12), (16, -12), (-16, 12), (16, 12)]:
        draw.line([(dx, dy), (dx + ox, dy + oy)], fill=INK, width=2)
        draw.line([(dx + ox - 9, dy + oy), (dx + ox + 9, dy + oy)],
                  fill=INK, width=2)
    draw.line([(dx, dy + 6), (dx + 4, y + s * 0.38)], fill=RED, width=2)


def pic_blast(draw, x, y, s):
    """City skyline with a blast star above it."""
    base = y + s * 0.78
    heights = [0.5, 0.72, 0.42, 0.62, 0.55]
    for i, hfrac in enumerate(heights):
        bx = x + i * s * 0.2
        draw.rectangle([bx, base - s * hfrac, bx + s * 0.17, base],
                       fill=(70, 70, 78))
    draw.rectangle([x, base, x + s, base + 4], fill=INK)
    cx, cy = x + s * 0.5, y + s * 0.2
    for k in range(8):
        ang = k * math.pi / 4
        r1, r2 = s * 0.1, s * 0.3
        c, sn = math.cos(ang), math.sin(ang)
        draw.line([(cx + c * r1, cy + sn * r1), (cx + c * r2, cy + sn * r2)],
                  fill=ORANGE, width=5)
    draw.ellipse([cx - s * 0.09, cy - s * 0.09, cx + s * 0.09, cy + s * 0.09],
                 fill=RED)


def pic_fire(draw, x, y, s):
    """Factory with a sawtooth roof and flames."""
    draw.rectangle([x, y + s * 0.45, x + s * 0.72, y + s * 0.82], fill=GREY)
    for i in range(3):
        fx = x + i * s * 0.24
        draw.polygon([(fx, y + s * 0.45), (fx + s * 0.24, y + s * 0.45),
                      (fx + s * 0.24, y + s * 0.25)], fill=(70, 70, 78))
    draw.rectangle([x + s * 0.78, y + s * 0.18, x + s * 0.92, y + s * 0.82],
                   fill=(70, 70, 78))
    fx, fy = x + s * 0.36, y + s * 0.42
    draw.polygon([(fx - s * 0.2, fy + s * 0.18), (fx, fy - s * 0.2),
                  (fx + s * 0.1, fy), (fx + s * 0.2, fy - s * 0.28),
                  (fx + s * 0.34, fy + s * 0.18)],
                 fill=ORANGE)
    draw.polygon([(fx - s * 0.08, fy + s * 0.18), (fx, fy),
                  (fx + s * 0.12, fy + s * 0.18)], fill=RED)


def pic_chip(draw, x, y, s):
    """A chip with a rising chart arrow."""
    draw.rectangle([x + s * 0.12, y + s * 0.3, x + s * 0.62, y + s * 0.8],
                   fill=(40, 90, 60))
    for i in range(3):
        px = x + s * (0.2 + i * 0.18)
        draw.line([(px, y + s * 0.3), (px, y + s * 0.16)], fill=INK, width=3)
        draw.line([(px, y + s * 0.8), (px, y + s * 0.94)], fill=INK, width=3)
        py = y + s * (0.38 + i * 0.18)
        draw.line([(x + s * 0.12, py), (x - s * 0.02, py)], fill=INK, width=3)
        draw.line([(x + s * 0.62, py), (x + s * 0.76, py)], fill=INK, width=3)
    pts = [(x + s * 0.1, y + s * 0.72), (x + s * 0.35, y + s * 0.55),
           (x + s * 0.55, y + s * 0.62), (x + s * 0.85, y + s * 0.18)]
    draw.line(pts, fill=RED, width=5, joint="curve")
    ax, ay = pts[-1]
    draw.polygon([(ax - 14, ay + 2), (ax + 10, ay - 2), (ax + 2, ay + 16)],
                 fill=RED)


def pic_planet(draw, x, y, s):
    """Mercury with craters, a probe and an orbit ring."""
    cx, cy, r = x + s * 0.42, y + s * 0.55, s * 0.3
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(188, 168, 140),
                 outline=(120, 105, 85), width=3)
    for ox, oy, cr in [(-0.12, -0.1, 0.09), (0.14, 0.06, 0.07),
                       (-0.05, 0.16, 0.06), (0.1, -0.18, 0.05)]:
        draw.ellipse([cx + ox * r - cr * r, cy + oy * r - cr * r,
                      cx + ox * r + cr * r, cy + oy * r + cr * r],
                     outline=(120, 105, 85), width=2)
    draw.ellipse([x + s * 0.02, y + s * 0.05, x + s * 0.98, y + s * 0.95],
                 outline=BLUE, width=2)
    px, py = x + s * 0.82, y + s * 0.16
    draw.rectangle([px - 8, py - 6, px + 8, py + 6], fill=TEAL)
    draw.line([(px - 16, py), (px - 8, py)], fill=TEAL, width=3)
    draw.line([(px + 8, py), (px + 16, py)], fill=TEAL, width=3)


def pic_ribbon(draw, x, y, s):
    """Pink awareness ribbon over a scan frame."""
    draw.rectangle([x + s * 0.08, y + s * 0.08, x + s * 0.92, y + s * 0.92],
                   outline=TEAL, width=4)
    for i in range(4):
        ly = y + s * (0.25 + i * 0.16)
        draw.line([(x + s * 0.18, ly), (x + s * 0.82, ly)], fill=LIGHT, width=5)
    cx = x + s * 0.5
    draw.ellipse([cx - s * 0.16, y + s * 0.18, cx + s * 0.16, y + s * 0.42],
                 outline=(226, 90, 150), width=6)
    draw.polygon([(cx - s * 0.13, y + s * 0.38), (cx + s * 0.13, y + s * 0.38),
                  (cx, y + s * 0.78)], outline=(226, 90, 150), width=6)


def story(draw, x, y, w, h, picto, kicker, head, body, head_size=22):
    """One grid story: small picture left, kicker + headline + body right."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=LIGHT, width=1)
    picto(draw, x + 12, y + 14, 108)
    tx = x + 132
    tw = w - 144
    draw.text((tx, y + 8), kicker, font=font(SANS_B, 15), fill=RED)
    hy = y + 28
    for line in wrap(draw, head, font(SANS_B, head_size), tw):
        draw.text((tx, hy), line, font=font(SANS_B, head_size), fill=INK)
        hy += head_size + 4
    para(draw, tx, hy + 4, tw, body, font(SANS, 16), fill=(60, 58, 52))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 36  # side margin

    # ---- masthead ----
    d.text((mx, 18), "THE WORLD IN ONE DAY", font=font(SERIF_B, 62), fill=INK)
    rule(d, mx, 96, W - mx, 4)
    rule(d, mx, 102, W - mx, 1)
    d.text((mx, 112), "MONDAY 23 NOVEMBER 2026",
           font=font(SANS_B, 24), fill=RED)
    d.text((W - mx - d.textlength("ONE DAY · SIX CONTINENTS",
                                  font=font(SANS_B, 20)), 116),
           "ONE DAY · SIX CONTINENTS", font=font(SANS_B, 20), fill=GREY)

    # ---- lead story: COP31 ----
    ly = 152
    d.text((mx, ly), "CLIMATE",
           font=font(SANS_B, 17), fill=TEAL)
    head = "COP31 ends with no deal after the longest climate talks on record"
    hy = ly + 26
    for line in wrap(d, head, font(SERIF_B, 40), 560):
        d.text((mx, hy), line, font=font(SERIF_B, 40), fill=INK)
        hy += 48
    deck = ("In Turkey, countries split over phasing out fossil fuels and over "
            "adaptation finance, and the draft text was left unapproved.")
    para(d, mx, hy + 6, 560, deck, font(SERIF_I, 22), fill=(60, 58, 52))
    # globe panel, right of the lead
    panel = (620, 150, 988, 428)
    d.rectangle(panel, fill=(222, 236, 242), outline=BLUE, width=3)
    globe(d, 804, 262, 82)
    d.text((652, 352), "Antalya, Turkey — the summit",
           font=font(SANS, 18), fill=INK)
    d.text((652, 376), "ran past its deadline and still",
           font=font(SANS, 18), fill=INK)
    d.text((652, 400), "could not agree a final text.",
           font=font(SANS, 18), fill=INK)
    stamp(d, 648, 168, "NO DEAL", font(SANS_B, 34))
    rule(d, mx, 446, W - mx, 3)

    # ---- grid of six stories ----
    gy = 460
    cw, ch, gap = 468, 150, 20
    stories = [
        (pic_ship, "UKRAINE · LIBYA",
         "Drone strike hits Russian warship",
         "Kyiv says its sea drones struck the vessel in Benghazi port; "
         "Zelensky confirmed the attack."),
        (pic_blast, "UKRAINE · KYIV",
         "Russian strikes kill at least 15 near Kyiv",
         "A boy was pulled alive from the rubble as bombardment hit "
         "homes across the region."),
        (pic_fire, "INDONESIA",
         "Factory fire kills 24; dozens missing",
         "A blaze swept a sweets factory, leaving about 30 people "
         "unaccounted for."),
        (pic_chip, "TECH · MARKETS",
         "Nvidia brings back Jensen Huang",
         "The board reinstated its founder as CEO and the shares "
         "jumped about 30%."),
        (pic_planet, "SPACE",
         "BepiColombo reaches Mercury",
         "The European-Japanese pair of spacecraft entered orbit "
         "around the Solar System's smallest planet."),
        (pic_ribbon, "HEALTH",
         "NHS to trial AI breast screening",
         "Nearly 700,000 women are invited to test whether AI can "
         "spot cancer earlier."),
    ]
    for i, (picto, kicker, head, body) in enumerate(stories):
        x = mx + (i % 2) * (cw + gap)
        y = gy + (i // 2) * (ch + 2)
        story(d, x, y, cw, ch, picto, kicker, head, body)

    # ---- bottom strip ----
    by = 926
    rule(d, mx, by, W - mx, 3)
    items = [
        "EUROZONE INFLATION 4.0%",
        "UK TO HOST 2035 WOMEN'S WORLD CUP",
        "AI PROVES RIEMANN HYPOTHESIS",
    ]
    size = 18
    while size > 12:
        strip = font(SANS, size)
        total = sum(d.textlength(it, font=strip) for it in items) + 68
        if total <= W - 2 * mx:
            break
        size -= 1
    sx = mx
    for item in items:
        d.text((sx, by + 12), item, font=strip, fill=INK)
        sx += d.textlength(item, font=strip) + 34
        if item is not items[-1]:
            d.text((sx - 24, by + 12), "·", font=strip, fill=RED)
    d.text((mx, 972), "Sources: wire reports of 23 November 2026.",
           font=font(SANS, 15), fill=GREY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    img.save(os.path.join(out_dir, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
