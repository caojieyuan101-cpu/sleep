"""Icons for the sleep app: a pink-violet sunset seen through a classroom window - lavender clouds,
a cream horizon, a dark skyline and window frames, and a thin crescent moon rising.
Run: python3 tools/icons.py (needs Pillow)."""
import os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the site root
K = 2
S = 1024 * K
FRAME = (18, 13, 20)
STOPS = [(0, (141, 111, 176)), (.22, (198, 147, 191)), (.48, (226, 129, 144)), (.66, (240, 164, 156)), (.82, (248, 201, 170)), (1, (249, 236, 179))]
hz = 760 * K  # skyline foot / horizon


def sky(t):
    for (a, ca), (b, cb) in zip(STOPS, STOPS[1:]):
        if t <= b:
            u = (t - a) / (b - a)
            return tuple(int(ca[i] + (cb[i] - ca[i]) * u) for i in range(3))
    return STOPS[-1][1]


img = Image.new('RGBA', (S, S))
d = ImageDraw.Draw(img)
for y in range(S):
    d.line([(0, y), (S, y)], fill=sky(min(1, y / hz)) + (255,))


def blurred(draw_fn, radius):
    layer = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    return layer.filter(ImageFilter.GaussianBlur(radius * K))


img = Image.alpha_composite(img, blurred(lambda g: g.ellipse([140 * K, 640 * K, 760 * K, 820 * K], fill=(255, 246, 216, 170)), 70))
clouds = [(60, 420, 470, 470, (108, 87, 114, 200)), (230, 500, 560, 535, (127, 98, 156, 170)),
          (560, 300, 990, 350, (108, 87, 114, 150)), (600, 560, 960, 600, (127, 98, 156, 190))]
img = Image.alpha_composite(img, blurred(lambda g: [g.ellipse([a * K, b * K, c * K, e * K], fill=col) for a, b, c, e, col in clouds], 14))

# crescent moon, upper right pane
moon = Image.new('L', (S, S), 0)
md = ImageDraw.Draw(moon)
cx, cy, r = 740 * K, 168 * K, 82 * K
md.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
md.ellipse([cx - r + 46 * K, cy - r - 26 * K, cx + r + 46 * K, cy + r - 26 * K], fill=0)
img = Image.alpha_composite(img, blurred(lambda g: g.ellipse([cx - 150 * K, cy - 150 * K, cx + 150 * K, cy + 150 * K], fill=(255, 244, 224, 90)), 50))
img.paste(Image.new('RGBA', (S, S), (255, 246, 228, 255)), (0, 0), moon)

d = ImageDraw.Draw(img)
# skyline, then the wall below the window
pts = [(0, 720), (70, 720), (70, 680), (130, 680), (130, 705), (230, 705), (230, 650), (262, 650), (262, 700), (420, 700),
       (420, 725), (560, 725), (560, 690), (620, 690), (620, 712), (750, 712), (750, 664), (790, 664), (790, 630), (806, 630),
       (806, 664), (840, 664), (840, 700), (960, 700), (960, 715), (1024, 715), (1024, 1024), (0, 1024)]
d.polygon([(x * K, y * K) for x, y in pts], fill=FRAME)
# window frame: outer frame, a transom and paired sliding-window mullions
w = 34 * K
d.rectangle([0, 0, S, w * 1.6], fill=FRAME)
d.rectangle([0, 0, w * 1.6, hz], fill=FRAME)
d.rectangle([S - w * 1.6, 0, S, hz], fill=FRAME)
d.rectangle([0, 300 * K, S, 300 * K + w], fill=FRAME)
for x in (300, 352):
    d.rectangle([x * K, 0, x * K + w * .8, hz], fill=FRAME)
d.rectangle([0, 790 * K, S, 800 * K], fill=(58, 46, 60, 255))  # sill edge

big = img.convert('RGB').resize((1024, 1024), Image.LANCZOS)
for s in (180, 192, 512):
    big.resize((s, s), Image.LANCZOS).save(os.path.join(OUT, 'icon-%d.png' % s), optimize=True)
print('icons written to', OUT)
