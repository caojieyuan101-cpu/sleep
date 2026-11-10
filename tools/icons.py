"""App icons: two overlapping circles on warm paper - a sunset disc (peach to pink) and a lavender disc,
multiplied where they overlap the way inks do - over one fine ink line for the horizon, with a faint grain.
Run: python3 tools/icons.py (needs numpy and Pillow). Writes icon-180/192/512.png at the site root."""
import os
import numpy as np
from PIL import Image

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the site root
K = 3                       # drawn at 3x the 1024 grid, then scaled down
S = 1024 * K
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)


def rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


def disc(cx, cy, r):
    return np.clip(r * K - np.hypot(xx - cx * K, yy - cy * K) + .5, 0, 1)[..., None]


def bar(x0, y0, x1, y1):
    return np.clip(np.minimum.reduce([xx - x0 * K, x1 * K - xx, yy - y0 * K, y1 * K - yy]) + .5, 0, 1)[..., None]


def vgrad(top, bottom, y0, y1):
    t = np.clip((yy - y0 * K) / ((y1 - y0) * K), 0, 1)[..., None]
    return rgb(top) * (1 - t) + rgb(bottom) * t


t = (yy / S)[..., None]
img = rgb('#f4ede7') * (1 - t) + rgb('#ede3dc') * t                                   # paper
m = disc(450, 470, 230)
img = img * (1 - m) + img * vgrad('#f7c7a8', '#ee8ea3', 300, 700) * m                 # sunset disc
m = disc(600, 560, 200) * .92
img = img * (1 - m) + img * vgrad('#cdb6e6', '#9f86c8', 320, 760) * m                 # lavender disc
m = bar(220, 810, 804, 814)
img = img * (1 - m) + rgb('#2a1f2c') * m                                              # horizon

big = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((1024, 1024), Image.LANCZOS)
a = np.asarray(big, np.float32) / 255
a += np.random.default_rng(7).normal(0, .018, (1024, 1024, 1)).astype(np.float32)      # grain
big = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
for s in (180, 192, 512):
    big.resize((s, s), Image.LANCZOS).save(os.path.join(OUT, 'icon-%d.png' % s), optimize=True)
print('icons written to', OUT)
