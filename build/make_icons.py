"""Generate home-screen icons for The Lachie Index: a whitebait over a river ground."""
from PIL import Image, ImageDraw
import sys, pathlib

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")

BG_TOP = (255, 226, 122)   # butter, light
BG_BOT = (255, 209, 58)    # butter, deep
BAIT   = (20, 18, 16)      # ink
WAVE   = (255, 79, 159)    # hot pink


def icon(size, rounded=True):
    S = size * 4  # supersample for clean edges
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # vertical gradient ground
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=tuple(
            int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)) + (255,))

    # two river bands behind the fish
    for k, (yy, alpha, w) in enumerate([(0.70, 70, 0.030), (0.80, 45, 0.022)]):
        pts = []
        for x in range(0, S + 1, S // 60):
            import math
            pts.append((x, yy * S + math.sin(x / S * math.pi * 2 + k) * S * 0.035))
        d.line(pts, fill=WAVE + (alpha,), width=max(2, int(S * w)), joint="curve")

    # whitebait: slim body, forked tail
    cx, cy = S * 0.50, S * 0.46
    L, H = S * 0.62, S * 0.155
    d.ellipse([cx - L / 2, cy - H / 2, cx + L / 2 - L * 0.16, cy + H / 2], fill=BAIT + (255,))
    tx = cx + L / 2 - L * 0.20
    d.polygon([(tx, cy), (tx + L * 0.22, cy - H * 0.78), (tx + L * 0.14, cy),
               (tx + L * 0.22, cy + H * 0.78)], fill=BAIT + (255,))
    # eye
    er = H * 0.17
    d.ellipse([cx - L / 2 + L * 0.10 - er, cy - er * 1.5, cx - L / 2 + L * 0.10 + er, cy + er * 0.5],
              fill=(255, 217, 74, 255))

    if rounded:
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, S, S], radius=int(S * 0.22), fill=255)
        img.putalpha(mask)

    return img.resize((size, size), Image.LANCZOS)


for size, name, rnd in [(192, "icon-192.png", False), (512, "icon-512.png", False),
                        (180, "apple-touch-icon.png", True), (32, "favicon-32.png", False)]:
    p = OUT / name
    icon(size, rnd).save(p)
    print(f"  {name}  {p.stat().st_size/1024:.1f} KB")
