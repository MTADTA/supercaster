"""Compose the annotated prototype-fingerboard sheets from renders/neck-proto/ (Blender stills + anchors.json + params.json
+ params.png + plan.png).  Labels sit on projected 3-D anchor points, numbers come from params.json.
Writes renders/neck-proto/sheet-overview.png and sheet-stations.png.   Run:  <venv>/python -I -B compose.py
"""
import json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', '..', '..', 'renders', 'neck-proto')
P = json.load(open(os.path.join(D, 'params.json')))
A = json.load(open(os.path.join(D, 'anchors.json')))
SURF, INK, INK2, MUTED, ACC = (26, 26, 25), (240, 239, 236), (195, 194, 183), (141, 140, 133), (57, 135, 229)
FONT = '/System/Library/Fonts/HelveticaNeue.ttc'
def font(sz, bold=False): return ImageFont.truetype(FONT, sz, index=1 if bold else 0)
def v(key, k): return P[key][k - 1]


def label(dr, xy, anchor, text, f, side='r', dy=0):
    """Leader line from the anchor to a boxed label."""
    ax, ay = anchor; lx, ly = xy
    dr.line([(ax, ay), (lx, ly + dy)], fill=INK, width=2)
    dr.ellipse([ax - 5, ay - 5, ax + 5, ay + 5], outline=INK, width=2)
    bb = dr.multiline_textbbox((0, 0), text, font=f, spacing=4)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    x0 = lx if side == 'r' else lx - w - 20
    dr.rounded_rectangle([x0, ly - h / 2 - 9 + dy, x0 + w + 20, ly + h / 2 + 9 + dy], radius=8, fill=(20, 20, 19), outline=(90, 89, 85))
    dr.multiline_text((x0 + 10, ly - h / 2 - 3 + dy), text, font=f, fill=INK, spacing=4)


def title(dr, xy, text, f):
    bb = dr.textbbox(xy, text, font=f)
    dr.rounded_rectangle([bb[0] - 12, bb[1] - 9, bb[2] + 12, bb[3] + 9], radius=8, fill=(20, 20, 19))
    dr.text(xy, text, font=f, fill=INK)


def station_tile(name, k, side, scale):
    im = Image.open(os.path.join(D, name + '.png')).convert('RGB')
    W0, H0 = im.size
    im = im.resize((int(W0 * scale), int(H0 * scale)), Image.LANCZOS)
    dr = ImageDraw.Draw(im); f = font(int(25 * scale / 0.62)); fb = font(int(30 * scale / 0.62), True)
    px = {a: (p[0] * scale, p[1] * scale) for a, p in A[name]['px'].items()}
    Wt, Ht = im.size
    strn = 'high E' if side == 'T' else 'low E'
    dep = v('depth_high_E' if side == 'T' else 'depth_low_E', k)
    # labels: placed in the clear dark corners, leaders to the true 3-D points
    label(dr, (Wt * 0.04, Ht * 0.10), px['trough'], 'Centred trough, cell %d\n%.3f deep under the %s\n%.3f behind fret %d' % (k, dep, strn, v('trough_behind_fret', k), k), f)
    label(dr, (Wt * 0.60, Ht * 0.08), px['fret_end'], 'Fret %d end: %.0f° line\nsteel from %.3f, full height %.3f\nturnover r %.3f' % (
        k, v('face_angle', k), v('steel_from_side', k), v('full_height_from_side', k), v('turnover_radius', k)), f)
    if side == 'T':
        label(dr, (Wt * 0.62, Ht * 0.88), px['rail'], 'Level rail + edge roll r %.3f' % v('roll_radius', k), f)
        title(dr, (Wt * 0.04, Ht * 0.90), 'Treble edge · cell %d / fret %d' % (k, k), fb)
    else:
        label(dr, (Wt * 0.04, Ht * 0.80), px['rail'], 'Level rail + edge roll r %.3f' % v('roll_radius', k), f)
        title(dr, (Wt * 0.58, Ht * 0.90), 'Bass edge · cell %d / fret %d' % (k, k), fb)
    return im


def caption_block(dr, x, y, lines, f, fill=INK2, gap=8):
    for t in lines:
        dr.text((x, y), t, font=f, fill=fill); y += f.size + gap
    return y


# ---------------------------------------------------------------- stations sheet
TS = [('t1', 1, 'T'), ('t7', 7, 'T'), ('t12', 12, 'T'), ('t17', 17, 'T'), ('t22', 22, 'T'), ('b1', 1, 'B'), ('b12', 12, 'B'), ('b22', 22, 'B')]
sc = 0.62; tw, th = int(1600 * sc), int(1100 * sc); gap = 16; cols = 3
rows_T, rows_B = 2, 1
Wsh = cols * tw + (cols + 1) * gap
head = 190
Hsh = head + 3 * (th + gap) + 2 * 70 + 260
sh = Image.new('RGB', (Wsh, Hsh), SURF); dr = ImageDraw.Draw(sh)
dr.text((gap, 24), 'Supercaster II prototype fingerboard: stations along the neck', font=font(44, True), fill=INK)
caption_block(dr, gap, 88, [
    'Nov 18 test-piece spec: centred mirror-symmetric scallop, level rail, graded fret ends (gradual at the nut, full height 0.080 from the side; '
    'steeper at the body, 0.048), same on both edges. Neck v4 back, wire and board unchanged.',
    'Every number is from neck/v4/transition (study.py, results.json) and fe_r2_model.py. Inches. Close-ups are the CAD surface '
    'in Cycles, not an illustration; strings drawn at vintage spacing.'], font(22))
y = head
dr.text((gap, y), 'Treble edge, frets 1 · 7 · 12 · 17 · 22', font=font(30, True), fill=INK); y += 46
tiles = [station_tile(n, k, s, sc) for n, k, s in TS]
for i in range(5):
    r, c = divmod(i, 3)
    sh.paste(tiles[i], (gap + c * (tw + gap), y + r * (th + gap)))
# the empty 6th cell: what changes, in words
x6, y6 = gap + 2 * (tw + gap) + 24, y + th + gap + 20
yy = caption_block(dr, x6, y6, ['What changes, at fret 1 · 12 · 22'], font(30, True), fill=INK)
rows = [('Scallop under high E', 'depth_high_E', '%.3f'), ('Scallop under low E', 'depth_low_E', '%.3f'),
        ('Trough behind fret', 'trough_behind_fret', '%.3f'), ('Fret-end line', 'face_angle', '%.0f°'),
        ('Edge roll radius', 'roll_radius', '%.3f'), ('Turnover radius', 'turnover_radius', '%.3f'),
        ('Full height from side', 'full_height_from_side', '%.3f'), ('Steel outside high E', 'full_steel_outside_high_E', '%.3f'),
        ('Board width', 'width_at_fret', '%.3f'), ('Board radius', 'radius_at_fret', '%.2f')]
fr = font(25)
for lab, key, fm in rows:
    dr.text((x6, yy + 6), lab, font=fr, fill=INK2)
    dr.text((x6 + 330, yy + 6), '   ·   '.join(fm % v(key, k) for k in (1, 12, 22)), font=fr, fill=INK)
    yy += 38
yy += 14
caption_block(dr, x6, yy, ['Fixed: 0.055 land each side of the fret,', '0.080 × 0.043 stainless, 0.140 board, rail full', 'depth 0.140 in, bass scallop = half the treble.'], font(22), fill=MUTED, gap=6)
y += 2 * (th + gap) + 20
dr.text((gap, y), 'Bass edge (thumb side), frets 1 · 12 · 22', font=font(30, True), fill=INK); y += 46
for i in range(3):
    sh.paste(tiles[5 + i], (gap + i * (tw + gap), y))
y += th + 24
yend = caption_block(dr, gap, y, [
    'Thumb-over check: hand-contact model on this centred scallop (thumb.py), at frets 2, 12 and 20. Two options, neither adopted:',
    '•  Gradual end on the bass edge all the way up: thumb 8–21 % softer at frets 12–20 (no real change at fret 2, already gradual there). '
    'Cost: full-height steel outside the low E 0.062 at fret 12 and 0.055 at fret 21, instead of 0.084 and 0.087.',
    '•  Shallower scallop at the bass edge (30 % of the treble instead of 50 %): the wrapped thumb rises and falls about 20 % less at frets 2 and 12. '
    'Cost: low-E scallop 0.018 instead of 0.028 at cell 12.',
    'An end can be made more gradual by hand after playing the test piece; steel filed off cannot go back. The back carve has no thumb model yet.'], font(22))
sh = sh.crop((0, 0, Wsh, int(yend + 24)))
sh.save(os.path.join(D, 'sheet-stations.png'))

# ---------------------------------------------------------------- overview sheet: long view + plan + params
lv = Image.open(os.path.join(D, 'long.png')).convert('RGB')
pl = Image.open(os.path.join(D, 'plan.png')).convert('RGB')
pa = Image.open(os.path.join(D, 'params.png')).convert('RGB')
Wo = lv.width
pl = pl.resize((Wo, int(pl.height * Wo / pl.width)), Image.LANCZOS)
pa = pa.resize((Wo, int(pa.height * Wo / pa.width)), Image.LANCZOS)
dl = ImageDraw.Draw(lv); f = font(30); fb = font(34, True)
for key, p in A['long']['px'].items():
    kk = int(key.split('_')[1])
    if kk == 21:
        continue
    x, y0 = p[0], p[1]
    dl.line([(x, y0 - 20), (x, y0 - 110)], fill=INK2, width=2)
    t = '%.3f' % v('depth_high_E', kk)
    bb = dl.textbbox((0, 0), t, font=f); w = bb[2] - bb[0]
    dl.rounded_rectangle([x - w / 2 - 10, y0 - 160, x + w / 2 + 10, y0 - 112], radius=8, fill=(20, 20, 19), outline=(90, 89, 85))
    dl.text((x - w / 2, y0 - 155), t, font=f, fill=INK)
dl.text((40, 36), 'Whole board from the bass (thumb) side, strings off, soft light from the head end. Numbers: scallop depth under the high E at '
        'the trough, cells 1–22.', font=fb, fill=INK)
shp = Image.open(os.path.join(D, 'shape.png')).convert('RGB')
shp = shp.resize((Wo, int(shp.height * Wo / shp.width)), Image.LANCZOS)
H = 140 + lv.height + shp.height + pl.height + pa.height + 40
ov = Image.new('RGB', (Wo, H), SURF); do = ImageDraw.Draw(ov)
do.text((40, 30), 'Supercaster II prototype fingerboard: centred scallop, level rail, graded fret ends', font=font(54, True), fill=INK)
do.text((40, 96), 'Nov 18 test-piece spec on neck v4. Renders, plan and charts are all generated from the same model files.', font=font(28), fill=INK2)
yy = 140
for im in (lv, shp, pl, pa):
    ov.paste(im, (0, yy)); yy += im.height
ov.save(os.path.join(D, 'sheet-overview.png'))

# ---------------------------------------------------------------- fret-end sheet: one end from three directions
sc = 0.62; tw, th = int(1200 * sc), int(800 * sc); gap = 16
COLS = [('mt%deye', 'Treble end, from above the edge'), ('mt%dside', 'Treble end, from the side'), ('mt%dabove', 'Treble end, from straight above'),
        ('mb%deye', 'Bass (thumb) end, from above the edge')]
We = 4 * tw + 5 * gap; head = 150; rowh = th + 64
fe = Image.new('RGB', (We, head + 3 * rowh + 20), SURF); de = ImageDraw.Draw(fe)
de.text((gap, 24), 'Supercaster II prototype fingerboard: fret ends at frets 1, 12 and 22', font=font(44, True), fill=INK)
caption_block(de, gap, 88, ['Graded flow end, the same on both edges: rounded from above, a straight line up from the edge roll, turned over into the fret top. '
                            'Gradual at the nut, steeper toward the body. Strings off. Each frame is about half an inch wide.'], font(22))
for r_, k in enumerate((1, 12, 22)):
    y0 = head + r_ * rowh
    de.text((gap, y0 + 6), 'Fret %d:  %.0f° line  ·  steel starts %.3f from the side  ·  full height from %.3f  ·  edge roll r %.3f  ·  turnover r %.3f  ·  '
            'full-height steel outside the high E %.3f' % (k, v('face_angle', k), v('steel_from_side', k), v('full_height_from_side', k),
                                                           v('roll_radius', k), v('turnover_radius', k), v('full_steel_outside_high_E', k)),
            font=font(25, True), fill=INK)
    for c_, (pat, lab) in enumerate(COLS):
        im = Image.open(os.path.join(D, (pat % k) + '.png')).convert('RGB').resize((tw, th), Image.LANCZOS)
        title(ImageDraw.Draw(im), (20, th - 48), lab, font(22))
        fe.paste(im, (gap + c_ * (tw + gap), y0 + 48))
fe.save(os.path.join(D, 'sheet-fret-ends.png'))
print('wrote sheets')
