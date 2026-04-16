"""
Generate per-pillar variants of the dashboard header background pattern.

Input : images/Background Patterns/StratPlan-Dashboard-Header_White-HiRes.png
Output: images/Background Patterns/_pillars/StratPlan-Dashboard-Header_White-HiRes_PN_<slug>.png

Approach:
1. Detect each colored square in the source (connected components on non-white mask).
2. Cluster the source shades into 5 tiers (very light -> dark) using luminance.
3. For each pillar, build a parallel 5-tier palette from the main pillar color by
   blending it toward white at fixed ratios (matches how the original blues step).
4. Repaint each square with its tier's pillar shade on a white background.

Why a palette ramp instead of just re-tinting: the original uses 5 discrete shades,
not a continuous gradient, so a clean 5-stop ramp preserves the original's
"stepped" look while letting each pillar own its hue.
"""

from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage

REPO = Path(__file__).resolve().parents[1]
SRC  = REPO / 'images' / 'Background Patterns' / 'StratPlan-Dashboard-Header_White-HiRes.png'
OUT  = REPO / 'images' / 'Background Patterns' / '_pillars'
OUT.mkdir(parents=True, exist_ok=True)

# Pillar main colors (from reference_pillar_colors.md)
PILLARS = [
    ('P1', 'Students',      '#003A70'),
    ('P2', 'Educators',     '#922880'),
    ('P3', 'Community',     '#29B5D9'),
    ('P4', 'HealthySafe',   '#FF9015'),
    ('P5', 'Operational',   '#74C04B'),
    ('P6', 'Transformative','#8C9EA0'),
    ('P7', 'Celebrate',     '#0077BF'),
    ('P8', 'Champions',     '#801323'),
]

# ---------------------------------------------------------------------------
# 1. Load source and detect squares
# ---------------------------------------------------------------------------
im = Image.open(SRC).convert('RGB')
arr = np.array(im)
H, W, _ = arr.shape

# non-white mask (anything the eye sees as colored)
mask = ~((arr[:,:,0] > 240) & (arr[:,:,1] > 240) & (arr[:,:,2] > 240))
labeled, n = ndimage.label(mask)

squares = []
for i, sl in enumerate(ndimage.find_objects(labeled), start=1):
    if sl is None:
        continue
    region_mask = (labeled[sl] == i)
    region_pix  = arr[sl][region_mask]
    avg = region_pix.mean(axis=0)  # average RGB in the region
    squares.append({'slice': sl, 'mask': region_mask, 'avg_rgb': avg})

print(f"Detected {len(squares)} squares")

# ---------------------------------------------------------------------------
# 2. Cluster into 5 tiers by luminance (lighter = higher tier index 0..4)
#    We use luminance because "how dark is this blue" is the only thing that
#    matters for mapping onto a new hue.
# ---------------------------------------------------------------------------
def luminance(rgb):
    r, g, b = rgb / 255.0
    return 0.2126*r + 0.7152*g + 0.0722*b

lum = np.array([luminance(s['avg_rgb']) for s in squares])
# 5 tiers, equal-quantile split
order = np.argsort(lum)
tier_of = np.empty_like(order)
bucket_edges = np.linspace(0, len(squares), 6, dtype=int)  # 5 buckets
for tier in range(5):
    idxs = order[bucket_edges[tier]:bucket_edges[tier+1]]
    tier_of[idxs] = tier  # 0 = darkest, 4 = lightest

for s, t in zip(squares, tier_of):
    s['tier'] = int(t)

# ---------------------------------------------------------------------------
# 3. Build a 5-tier ramp for each pillar by blending the main color toward white.
#    Ratios match the roughly equal spacing seen in the original source palette.
# ---------------------------------------------------------------------------
def hex_to_rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)], dtype=float)

# Blend weights toward white. 0.0 = pure main color, 1.0 = pure white.
# Tier 0 = darkest (uses main color), tier 4 = lightest (mostly white).
BLEND = [0.0, 0.30, 0.55, 0.75, 0.88]

def ramp_for(hexcolor):
    base = hex_to_rgb(hexcolor)
    white = np.array([255, 255, 255], dtype=float)
    return [tuple(((1-b)*base + b*white).astype(int).tolist()) for b in BLEND]

# ---------------------------------------------------------------------------
# 4. Paint each pillar variant
# ---------------------------------------------------------------------------
for pnum, pname, phex in PILLARS:
    shades = ramp_for(phex)  # 5 RGB tuples, darkest first
    canvas = np.full_like(arr, 255)  # start white
    for s in squares:
        tier = s['tier']
        color = np.array(shades[tier], dtype=np.uint8)
        sl = s['slice']
        region_mask = s['mask']
        # Paint only the pixels that belonged to this square in the source
        region = canvas[sl]
        region[region_mask] = color
        canvas[sl] = region
    out_path = OUT / f"StratPlan-Dashboard-Header_White-HiRes_{pnum}_{pname}.png"
    Image.fromarray(canvas).save(out_path, optimize=True)
    print(f"  wrote {out_path.name}  (main={phex})")

print(f"\nDone. {len(PILLARS)} files written to {OUT}")
