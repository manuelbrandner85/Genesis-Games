"""C00 (runs in Blender, BACKGROUND, any file): step 2 of 3 - soften the age spots in the man's body albedo.

blender -b --factory-startup --python tools/v4_2/c00_skin_spots_soften_blender.py -- <in.png> <out.png>

Real solar lentigines are flat, light-to-mid brown, with soft, slightly irregular edges and little contrast against
weathered skin; the baked texture had dense, high-contrast, saturated orange-brown dots with hard edges.
Frequency separation (numpy, in tiles so an 8K map fits in memory):
- large  = Gaussian(sigma 24 px)  - skin tone, no spots
- small  = Gaussian(sigma 1.4 px) - everything but pores / fine lines
- band   = small - large          - the spots (2-25 px), plus veins and broad tonal variation
- fine   = img - small            - pores, wrinkles, hair follicles: kept untouched
Where the band is DARKER than the surrounding skin (a spot) it is softened: its edge blurred (sigma 3 px), its
contrast reduced to 45 %, and its colour pulled halfway toward neutral brown (less orange saturation). Lighter
detail (highlights, vein ridges) and the pores stay as they were.
"""
import sys

import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, DST = argv[0], argv[1]
KEEP_CONTRAST, DESAT = 0.35, 0.55
S_LARGE, S_SMALL, S_EDGE = 24.0, 1.4, 3.0
TILE, PAD = 2048, 96


def box(a, r, axis):
    """box filter of radius r along axis (edge-clamped), via cumulative sums"""
    n = a.shape[axis]
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis, dtype=np.float32)
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return (hi - lo) / (2 * r + 1)


def gauss(a, sigma):
    """Gaussian approximated by three box passes per axis"""
    r = max(1, int(round(np.sqrt(12 * sigma * sigma / 3 + 1) / 2 - 0.5)))
    for axis in (0, 1):
        for _ in range(3):
            a = box(a, r, axis)
    return a


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


img = bpy.data.images.load(SRC)
w, h = img.size
px = np.empty(w * h * 4, dtype=np.float32)
img.pixels.foreach_get(px)
px = px.reshape(h, w, 4)
rgb = px[..., :3]
out = rgb.copy()
lum_w = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
stats = []
for y0 in range(0, h, TILE):
    for x0 in range(0, w, TILE):
        ya, yb = max(0, y0 - PAD), min(h, y0 + TILE + PAD)
        xa, xb = max(0, x0 - PAD), min(w, x0 + TILE + PAD)
        t = rgb[ya:yb, xa:xb]
        large = gauss(t, S_LARGE)
        small = gauss(t, S_SMALL)
        band = small - large
        fine = t - small
        band_l = band @ lum_w
        spot = smoothstep(0.005, 0.035, -band_l)[..., None]        # darker than the skin around it
        soft = gauss(band, S_EDGE) * KEEP_CONTRAST                 # softer edge, lower contrast
        soft_l = soft @ lum_w
        soft = soft + (soft_l[..., None] - soft) * DESAT            # less orange saturation
        res = large + band * (1 - spot) + soft * spot + fine
        iy, ix = y0 - ya, x0 - xa
        th, tw = min(TILE, h - y0), min(TILE, w - x0)
        out[y0:y0 + th, x0:x0 + tw] = res[iy:iy + th, ix:ix + tw]
        stats.append(float(spot[iy:iy + th, ix:ix + tw].mean()))
px[..., :3] = np.clip(out, 0.0, 1.0)
res_img = bpy.data.images.new("soft", w, h, alpha=True)
res_img.colorspace_settings.name = img.colorspace_settings.name
res_img.pixels.foreach_set(px.ravel())
res_img.filepath_raw = DST
res_img.file_format = "PNG"
res_img.save()
print("C00_SKIN_SOFTEN", w, h, "spot_cover_%", round(100 * float(np.mean(stats)), 2), DST)
