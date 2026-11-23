"""Supercaster II weight-and-balance model (whole guitar, in hand and seated).

Inputs (read-only): body_<variant>.npz from body_fields.py (columns of the final carve + chamber, from body/carve/final_carve.py),
final_carve.py itself for the neck/heel loft (heel_back_z), the trem routes (P['trem']) and the tongue, bodylib for the outline.
Coordinates: inches, x from the nut toward the tail, y across (bass +), z up, body top plane z = 0, back z = -1.75.
Run: <venv>/bin/python -I -B balance.py   -> prints every table used in BALANCE.md and writes balance_results.json.

Strap model. Hanging from the horn button alone the guitar settles at the neck angle theta_free (above horizontal) where the
CoM is straight below the button: tan(theta_free) = (x_cm - x_h) / (y_h - y_cm). Playing at a steeper neck angle alpha, the rear
strap goes slack and the fretting hand must supply  tau = m g d sin(alpha - theta_free)  (d = |CoM - horn button| in plane);
playing flatter than theta_free, the rear strap carries it and no hand torque is needed. Seated: pivot on the treble waist.
"""
import sys, os, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
CARVE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'carve')
sys.path.insert(0, CARVE)
import final_carve as F
import bodylib as BL
from bodylib import _inside, _segdist

IN3 = 16.387064          # cm^3 per in^3
G = 9.80665
INCH = 0.0254
P = F.P; T = P['trem']

# ------------------------------------------------------------------------------------------------ geometry constants
# Landmarks of the outline come from the plan file (see body/carve/bodylib.py), not from this script.
_LM = BL.LANDMARKS
HORN_BTN = (*_LM['horn_button'], -0.875)      # traditional horn-tip strap button, mid-thickness
TAIL_BTN = (_LM['tail_x'], 0.0, -0.875)       # traditional tail button on the centreline (outline tail point)
WAIST = tuple(_LM['waist'])                   # treble-side waist (outline y max on the lower side): seated leg contact
JACK_C = tuple(_LM['jack_center'])
NPU, MPU, BPU = BL.NECK_PU, BL.MID_PU, BL.BRIDGE_PU[0]   # pickup centre lines
TUNER_XY = [(-1.75 - i * 0.98, 1.0 - i * 0.03) for i in range(6)]   # post positions as in src/neck-geometry.js
TUNER_Z = -0.45                        # gear housing behind a 0.55 headstock whose face is z +0.175 [judged]
HEADSTOCK = np.array([[0.05, 0.825], [-0.5, 0.9], [-1.2, 1.32], [-2.1, 1.55], [-3.6, 1.6], [-5.2, 1.48], [-6.4, 1.2],
                      [-7.05, 0.75], [-7.3, 0.15], [-7.15, -0.45], [-6.75, -0.78], [-6.1, -0.82], [-5.4, -0.62],
                      [-4.4, -0.42], [-3.2, -0.42], [-2.0, -0.6], [-1.0, -0.84], [-0.4, -0.86], [0.05, -0.825]])  # placeholder head outline, mass only (as in neck/v4/neck_v4.py)
HS_T = 0.55; BOARD_T = 0.20; BH = P['board_height']        # headstock thickness, slab board, board top above body top
fret_x = lambda n: 25.5 * (1 - 2 ** (-n / 12))
POCKET = dict(x0=P['pocket_datum_x'], x1=P['pocket_datum_x'] + P['pocket_len'], hw=P['pocket_w'] / 2, z=-P['insertion_depth'])
TONGUE = dict(x0=P['tenon_end'], x1=P['tongue_end'], hw=P['tongue_w'] / 2, z0=-0.875, z1=-0.625)   # z band [judged]: under the PU routes, above the split

# ------------------------------------------------------------------------------------------------ body voxels
_BODY = {}
def body_geom(variant='final', solid=False, routes='HSS'):
    """Alder volume and first moments of the routed body (in^3, in^4), plus pocket maple volume/moments.
    solid=True: no chamber, no f-hole. routes: 'HSS' (this guitar) or 'SSS' (stock vintage)."""
    key = (variant, solid, routes)
    if key in _BODY: return _BODY[key]
    fn = os.path.join(HERE, f'body_{variant}.npz')
    if not os.path.exists(fn):
        sys.exit(f'balance.py: {os.path.basename(fn)} is missing. It is a generated file and is not in the repository. Make it with\n'
                 f'  python body_fields.py {variant}\n(needs the real plan file, see the README; with the sample plan the numbers mean nothing).')
    d = np.load(fn)
    h = float(d['h']); X = d['X'].astype(float); Y = d['Y'].astype(float); t = d['t'].astype(float); zc = d['zc'].astype(float)
    zt = zc + t / 2; zb = zc - t / 2; ins = t > 0
    dz = 0.025; zs = -1.75 + dz * (np.arange(int(round(1.75 / dz))) + 0.5)
    sol = ins[..., None] & (zs[None, None, :] > zb[..., None]) & (zs[None, None, :] < zt[..., None])
    def box(x0, x1, y0, y1, z0, z1):
        return ((X > x0) & (X < x1) & (Y > y0) & (Y < y1))[..., None] & ((zs > z0) & (zs < z1))[None, None, :]
    removed = np.zeros_like(sol)
    if not solid:
        ch = d['ch']; ct = d['ct'].astype(float); cz = d['cz'].astype(float)
        removed |= ch[..., None] & (zs[None, None, :] > (cz - ct / 2)[..., None]) & (zs[None, None, :] < (cz + ct / 2)[..., None])
        fh = d['fh']; removed |= fh[..., None] & (zs[None, None, :] > d['roof_z'].astype(float)[..., None])   # f-hole through the roof
    # pickup routes [judged sizes: SC 0.80 x 3.50 x 0.625 deep incl. ears; HB 1.56 x 2.84 x 0.75 deep]
    removed |= box(NPU - 0.40, NPU + 0.40, -1.75, 1.75, -0.625, 0.1)
    removed |= box(MPU - 0.40, MPU + 0.40, -1.75, 1.75, -0.625, 0.1)
    if routes == 'HSS': removed |= box(BPU - 0.78, BPU + 0.78, -1.42, 1.42, -0.75, 0.1)
    else: removed |= box(BPU - 0.40, BPU + 0.40, -1.75, 1.75, -0.625, 0.1)
    # control pocket [judged]: HSS + 3 minis + slide switch needs a bigger pocket than the vintage one; depth 1.45 (0.30 floor)
    sdf = BL.sdf_outline(X, Y)
    cp = (sdf > 0.35)[..., None] & (box(23.6, 27.2, -5.4, -2.0, -1.45, 0.1) if routes == 'HSS' else box(24.0, 26.9, -5.3, -2.2, -1.45, 0.1))
    removed |= cp
    cp_in3 = float((cp & sol).sum() * h * h * dz)
    # trem routes from final_carve P['trem'] (v3.2, plan file), rectangles (corner radii ignored)
    for k in ('slot', 'block', 'spring'):
        r = T[k]; removed |= box(r['x0'], r['x1'], r['yc'] - r['hw'], r['yc'] + r['hw'], r['z_bot'], r['z_top'] + (0.1 if r['z_top'] >= 0 else 0))
    removed |= box(JACK_C[0] - 0.42, JACK_C[0] + 0.42, JACK_C[1] - 0.42, JACK_C[1] + 0.42, -1.2, 0.1)      # jack bore (0.84 cup, 1.2 deep) [judged]
    removed |= box(19.0, 23.2, -0.25, 0.25, -0.75, 0.1)                                     # pickup wiring channel [judged]
    pocket = box(POCKET['x0'], POCKET['x1'], -POCKET['hw'], POCKET['hw'], POCKET['z'], 0.1) & sol   # neck heel/tenon replaces alder
    tongue = box(TONGUE['x0'], TONGUE['x1'], -TONGUE['hw'], TONGUE['hw'], TONGUE['z0'], TONGUE['z1']) & sol & ~removed
    alder = sol & ~removed & ~pocket & ~tongue
    dv = h * h * dz
    def mom(m):
        n = m.sum(axis=2).astype(float); zsum = (m * zs[None, None, :]).sum(axis=2)
        return np.array([n.sum(), (n * X).sum(), (n * Y).sum(), zsum.sum()]) * dv
    routes_only = sol & removed
    if not solid: routes_only = routes_only & ~(ch[..., None] & (zs[None, None, :] > (cz - ct / 2)[..., None]) & (zs[None, None, :] < (cz + ct / 2)[..., None])) & ~fh[..., None]
    out = dict(control_pocket_in3=cp_in3, routes_in3=float(routes_only.sum() * h * h * dz), alder=mom(alder), pocket=mom(pocket), tongue=mom(tongue), removed=mom(sol & removed),
               chamber=(mom(sol & removed & (cp == 0)) if False else None), solid=mom(sol))
    # surface area for the finish: top + back plan area x carve factor + side wall
    plan = ins.sum() * h * h; per = float(np.sum(np.hypot(*np.diff(np.vstack([BL.OUTLINE, BL.OUTLINE[:1]]), axis=0).T)))
    out['finish_area_in2'] = 2 * plan * 1.03 + per * 1.75
    out['plan_c'] = (float((X * ins).sum() / ins.sum()), float((Y * ins).sum() / ins.sum()))
    _BODY[key] = out
    return out

# ------------------------------------------------------------------------------------------------ neck geometry
_NECK = {}
def neck_geom(frets=22):
    """Maple and rosewood volume + moments of the neck outside the body (incl. headstock and the heel loft), the board and the
    maple above the body top (in the pocket footprint). The heel/tenon inside the pocket is counted in body_geom."""
    if frets in _NECK: return _NECK[frets]
    h = 0.025; gx = np.arange(-7.4, 19.2, h) + h / 2; gy = np.arange(-1.8, 1.8, h) + h / 2; X, Y = np.meshgrid(gx, gy, indexing='ij')
    board_end = fret_x(frets) + 0.25
    W = 1.65 + (2.2 - 1.65) * np.clip(X, 0, None) / fret_x(21)
    outside = BL.sdf_outline(X, Y) <= 0
    def mom(thick, zmid, mask):
        th = np.where(mask, np.clip(thick, 0, None), 0.0)
        return np.array([th.sum(), (th * X).sum(), (th * Y).sum(), (th * np.where(mask, zmid, 0)).sum()]) * h * h
    # headstock slab (x < 0): z from BH - BOARD_T - HS_T to BH - BOARD_T, minus 6 tuner holes (10 mm)
    hs = _inside(HEADSTOCK, X, Y) & (X < 0.0)
    holes = np.zeros_like(hs)
    for (tx, ty) in TUNER_XY: holes |= np.hypot(X - tx, Y - ty) < 0.197
    ztop = BH - BOARD_T
    m_hs = mom(np.full(X.shape, HS_T), np.full(X.shape, ztop - HS_T / 2), hs & ~holes)
    # shaft + heel loft outside the outline: maple from heel_back_z up to the board underside
    zh = F.heel_back_z(np.clip(X, 0, None), Y)
    shaft = (X >= 0) & outside & np.isfinite(zh) & (np.abs(Y) < W / 2 + 0.2)
    zh = np.where(np.isfinite(zh), zh, ztop)
    m_shaft = mom(ztop - zh, 0.5 * (ztop + zh), shaft)
    # maple above the body top inside the outline (0 .. ztop) over the pocket footprint, up to the board end
    above = (X >= 0) & ~outside & (np.abs(Y) < POCKET['hw']) & (X < board_end)
    m_above = mom(np.full(X.shape, ztop), np.full(X.shape, ztop / 2), above)
    # rosewood board: width W, 0.20 slab less the radius crown (7.25 -> 9.5 conical)
    R = 7.25 + (9.5 - 7.25) * np.clip(X, 0, None) / 25.5
    crown = R - np.sqrt(np.maximum(R * R - Y * Y, 0)); bt = BOARD_T - crown
    board = (X >= 0) & (X < board_end) & (np.abs(Y) < W / 2)
    m_board = mom(bt, ztop + bt / 2, board)
    # frets: per-inch mass x width at each fret (crown above the board top)
    fxs = np.array([fret_x(n) for n in range(1, frets + 1)]); fw = 1.65 + (2.2 - 1.65) * fxs / fret_x(21)
    out = dict(maple=m_hs + m_shaft + m_above, maple_hs=m_hs, rosewood=m_board, fret_x=fxs, fret_len=fw, board_end=board_end)
    _NECK[frets] = out
    return out

# ------------------------------------------------------------------------------------------------ parts
def tri(rng, lo, mode, hi, n):
    return rng.triangular(lo, mode, hi, n) if hi > lo else np.full(n, mode)

TUNERS = {   # per tuner incl. bushing + screw, g. Sources in BALANCE.md
    'kluson_vintage':  (22.0, 24.0, 28.0),    # stock reference, non-locking
    'gotoh_sd91_mgt':  (27.0, 28.0, 30.0),    # vintage-look locking (Rockinger 27 g/pc)
    'hipshot_griplock':(30.0, 31.0, 35.0),    # 27.2 g closed w/o button (Hipshot) + button; 34.8 g incl. hardware (retailer)
    'sperzel_trimlok': (33.0, 36.0, 40.0),    # 3+3 set weights / 6 (StewMac listing), modern look
}
RODS = {     # whole rod, g, ~450 mm (headstock-adjust set neck) or ~430 mm (vintage heel-adjust)
    'oneway_steel':   (55.0, 63.0, 72.0),     # 3/16" steel rod + nut [computed geometry]
    'twoway_steel':   (86.0, 110.0, 134.0),   # StewMac Hot Rod 86 g weighed (forum) .. 134 g listed 18"; Maderas 360 mm 108 g
    'twoway_hybrid':  (85.0, 92.0, 100.0),    # Boston TRD-HY 420 mm 80-90 g, 460 mm 97 g
    'twoway_titanium':(60.0, 68.0, 76.0),     # Maderas full Ti 360 mm 56 g, scaled to 440-460 mm
    'oneway_titanium':(33.0, 38.0, 44.0),     # 3/16" Ti-6Al-4V rod + steel nut [computed]
}

def build(cfg, rng, n):
    """Returns list of (name, mass_g[n], x, y, z) items; positions may be arrays of length n or scalars."""
    I = []
    add = lambda name, m, x, y, z: I.append((name, np.asarray(m, float) * np.ones(n), x, y, z))
    stock = cfg['kind'] == 'stock'
    bg = body_geom(cfg.get('variant', 'precbs' if stock else 'final'), solid=cfg.get('solid', stock), routes='SSS' if stock else 'HSS')
    rho_al = tri(rng, *cfg['alder'], n)                           # g/cm^3
    V, Mx, My, Mz = bg['alder']; add('body alder', rho_al * V * IN3, Mx / V, My / V, Mz / V)
    rho_mp = tri(rng, *cfg['maple'], n); rho_rw = tri(rng, 0.75, 0.83, 0.90, n)
    for k in ('pocket',) + (() if stock else ('tongue',)):
        V, Mx, My, Mz = bg[k]
        if V > 0: add('neck ' + k + ' (maple)', rho_mp * V * IN3, Mx / V, My / V, Mz / V)
    if stock:                                                     # bolt-on: the tongue region stays alder
        V, Mx, My, Mz = bg['tongue']; add('alder where the tongue would be', rho_al * V * IN3, Mx / V, My / V, Mz / V)
    ng = neck_geom(21 if stock else 22)
    V, Mx, My, Mz = ng['maple']; add('neck maple + headstock', rho_mp * V * IN3, Mx / V, My / V, Mz / V)
    V, Mx, My, Mz = ng['rosewood']; add('rosewood board', rho_rw * V * IN3, Mx / V, My / V, Mz / V)
    fl = tri(rng, 0.35, 0.45, 0.55, n)                            # g per inch of fret wire (medium-jumbo nickel silver) [judged]
    L = ng['fret_len']; xf = float((ng['fret_x'] * L).sum() / L.sum()); add('frets', fl * L.sum(), xf, 0.0, BH + 0.02)
    add('nut (bone)', tri(rng, 2, 3, 4, n), -0.1, 0.0, BH + 0.05)
    add('string tree', tri(rng, 2, 3, 4, n), -3.4, 0.3, BH - BOARD_T + 0.2)
    tm = tri(rng, *TUNERS[cfg['tuners']], n) * 6
    add('tuners x6', tm, float(np.mean([p[0] for p in TUNER_XY])), float(np.mean([p[1] for p in TUNER_XY])), TUNER_Z)
    if cfg.get('slug', 0): add('headstock trim slug', np.full(n, cfg['slug']), -6.6, 0.2, BH - BOARD_T - HS_T / 2)
    rod = RODS[cfg['rod']]; x0, x1 = (-0.3, 17.5) if not stock else (0.4, 17.9)
    add('truss rod', tri(rng, *rod, n), 0.5 * (x0 + x1), 0.0, BH - BOARD_T - 0.30)
    add('strings 10-46', tri(rng, 6, 7, 8, n), 11.5, 0.0, BH + 0.15)
    add('neck finish', tri(rng, 0.06, 0.10, 0.15, n) * 0.1 * 80 * 6.4516 * 1.2 / 1.0, 6.0, 0.0, -0.1)   # mm->cm x 80 in2 x g/cc
    # tremolo (vintage steel block, synchronized, floating)
    add('trem block (steel)', tri(rng, 255, 280, 305, n), T['pivot_x'] + 0.83, T['block']['yc'], -0.80)
    add('trem plate + saddles + screws', tri(rng, 75, 90, 105, n), T['pivot_x'] + 0.5, 0.0, 0.25)
    add('trem arm', tri(rng, 20, 25, 30, n), T['pivot_x'] - 0.25, -2.2, 0.55)
    add('pivot screws x6', tri(rng, 10, 12, 14, n), T['pivot_x'], 0.0, -0.35)
    add('springs x3', tri(rng, 15, 20, 25, n), 24.0, 0.0, -1.44)
    add('claw + 2 screws', tri(rng, 35, 42, 50, n), 22.4, 0.0, -1.44)
    # pickups, guard, electronics
    sc = lambda: tri(rng, 32, 36, 42, n)
    add('neck single coil', sc(), NPU, 0.0, 0.05); add('middle single coil', sc(), MPU, 0.0, 0.05)
    if stock: add('bridge single coil', sc(), BPU, 0.0, 0.05)
    else: add('bridge humbucker', tri(rng, 120, 145, 175, n), BPU, 0.0, -0.05)
    gA = guard_area(); gthk = tri(rng, 0.060, 0.075, 0.090, n); grho = tri(rng, 1.30, 1.38, 1.45, n)
    add('pickguard', gA * gthk * IN3 * grho + 3, GUARD_C[0], GUARD_C[1], 0.04)
    add('guard screws x11', tri(rng, 9, 11, 13, n), GUARD_C[0], GUARD_C[1], -0.1)
    pots = tri(rng, 14, 16, 18, n) * 3; knobs = tri(rng, 8, 10, 12, n)
    add('3 pots + knobs', pots + knobs, 25.2, -3.6, -0.3)
    add('5-way switch', tri(rng, 10, 13, 16, n), 23.6, -3.0, -0.4)
    add('wiring + caps', tri(rng, 10, 15, 25, n), 24.5, -2.5, -0.5)
    add('jack + Electrosocket', tri(rng, 22, 30, 38, n), JACK_C[0], JACK_C[1], -0.6)
    add('horn strap button', tri(rng, 5, 6, 8, n), HORN_BTN[0] + 0.2, HORN_BTN[1] - 0.05, HORN_BTN[2])
    add('tail strap button', tri(rng, 5, 6, 8, n), TAIL_BTN[0] - 0.2, TAIL_BTN[1], TAIL_BTN[2])
    # finish: nitro (sealer + white + clear) [judged film 0.08-0.25 mm, 1.2-1.3 g/cc]
    film = tri(rng, 0.08, 0.15, 0.25, n) * 0.1; A = bg['finish_area_in2'] * 6.4516
    add('body finish', film * A * tri(rng, 1.2, 1.25, 1.3, n), bg['plan_c'][0], bg['plan_c'][1], -0.875)
    # configuration-specific parts are drawn LAST so the shared parts above use the same random stream in every config (paired draws)
    if stock:
        add('neck plate + 4 screws', tri(rng, 42, 53, 65, n), 17.0, 0.0, -1.55)
        add('trem cover plate', tri(rng, 8, 12, 16, n), 24.2, 0.0, -1.76)
    else:
        add('3 mini toggles', tri(rng, 6, 8, 10, n) * 3, 24.6, -4.4, -0.4)
        add('slide switch', tri(rng, 3, 5, 7, n), 26.4, -2.9, -0.3)
        add('passive piezo + lead', tri(rng, 3, 6, 10, n), 25.6, 0.0, 0.1)
    if not stock and not cfg.get('solid', False):
        # chamber extras (final plan): 0.6 mm cross-grain maple veneer under the roof, f-hole cleats, the narrowed liner (2.0 in^3, carve v3.2)
        add('roof veneer (maple)', tri(rng, 0.60, 0.65, 0.72, n) * 46.2 * (0.6 / 25.4) * IN3, 21.5, 3.9, -0.25)
        add('f-hole cleats', np.full(n, 0.5), 22.8, 3.9, -0.25)
        add('f-hole liner (alder)', rho_al * 2.0 * IN3, 23.38, 3.97, -0.60)
    for extra in cfg.get('extra', []):
        add(extra[0], np.full(n, extra[1]), extra[2], extra[3], extra[4])
    return I

GUARD_A = None; GUARD_C = None
def guard_area():
    global GUARD_A, GUARD_C
    if GUARD_A is None:
        h = 0.02; gx = np.arange(12.5, 31.5, h); gy = np.arange(-7, 7, h); X, Y = np.meshgrid(gx, gy, indexing='ij')
        m = BL.in_guard(X, Y)
        cut = np.zeros_like(m)                                     # pickup + switch openings (HSS) [judged]
        for xc in (NPU, MPU): cut |= (np.abs(X - xc) < 0.36) & (np.abs(Y) < 1.6)
        cut |= (np.abs(X - BPU) < 0.73) & (np.abs(Y) < 1.38)
        m &= ~cut
        GUARD_A = float(m.sum() * h * h); GUARD_C = (float((X * m).sum() / m.sum()), float((Y * m).sum() / m.sum()))
    return GUARD_A

def summarize(I):
    M = sum(it[1] for it in I)
    cx = sum(it[1] * it[2] for it in I) / M; cy = sum(it[1] * it[3] for it in I) / M; cz = sum(it[1] * it[4] for it in I) / M
    return M, cx, cy, cz

def metrics(M, cx, cy, cz, alpha_play=(15.0, 20.0, 30.0), seat_alpha=15.0, horn=HORN_BTN):
    xh, yh, zh = horn
    dx = cx - xh; dd = yh - cy; d = np.hypot(dx, dd)
    th = np.degrees(np.arctan2(dx, dd))                          # free-hang neck-up angle about the horn button
    out = dict(mass_kg=M / 1000, x_cm=cx, y_cm=cy, z_cm=cz, theta_free=th, d=d)
    hs = np.array([np.mean([p[0] for p in TUNER_XY]), np.mean([p[1] for p in TUNER_XY])])
    for a in alpha_play:
        # signed balance margin about the horn button at neck angle a: + = body-heavy (the rear strap carries it, no dive),
        # - = neck dive, the fretting hand must supply this torque
        out[f'tau_{int(a)}'] = M / 1000 * G * d * INCH * np.sin(np.radians(th - a))
        lever = -((hs[0] - xh) * np.cos(np.radians(a)) + (hs[1] - yh) * np.sin(np.radians(a)))   # horizontal lever of the tuners
        out[f'tuner_lever_{int(a)}'] = lever
    # seated, leg at the treble waist, neck angle seat_alpha: + = CoM on the neck side of the leg (needs the forearm/tail-down)
    a = np.radians(seat_alpha); Hs = (cx - WAIST[0]) * np.cos(a) + (cy - WAIST[1]) * np.sin(a)
    out['seat_H'] = Hs; out['seat_tau'] = M / 1000 * G * (-Hs) * INCH       # + = neck-down moment about the leg
    # forearm force to cancel it, forearm resting on the contour around (28.0, 3.5)
    af = (28.0 - WAIST[0]) * np.cos(a) + (3.5 - WAIST[1]) * np.sin(a)
    out['seat_forearm_N'] = out['seat_tau'] / (af * INCH)
    # roll: face tilt about the strap-button line (CoM in front of / behind the button plane)
    p1 = np.array(HORN_BTN[:2]); p2 = np.array(TAIL_BTN[:2]); u = (p2 - p1) / np.linalg.norm(p2 - p1)
    rel = np.stack([cx - p1[0], cy - p1[1]]); perp = np.abs(rel[0] * u[1] - rel[1] * u[0])
    out['roll_deg'] = np.degrees(np.arctan2(cz - HORN_BTN[2], perp)); out['perp'] = perp
    return out

def q(a, p=(5, 50, 95)): return [float(v) for v in np.percentile(a, p)]

BASE_FINAL = dict(kind='final', alder=(0.36, 0.40, 0.44), maple=(0.60, 0.65, 0.70), tuners='gotoh_sd91_mgt', rod='twoway_steel')
BASE_STOCK = dict(kind='stock', alder=(0.40, 0.45, 0.52), maple=(0.66, 0.70, 0.74), tuners='kluson_vintage', rod='oneway_steel')

def run(cfg, n=4000, seed=1):
    rng = np.random.default_rng(seed); I = build(cfg, rng, n); M, cx, cy, cz = summarize(I); return I, metrics(M, cx, cy, cz)

def nominal(cfg):
    I, m = run(cfg, n=1, seed=0)                                 # n=1 draw is noisy; use the deterministic mode instead
    return I, m

def det(cfg):
    """Deterministic nominal (every triangular at its mode)."""
    global tri
    old = tri
    tri = lambda rng, lo, mode, hi, n: np.full(n, mode)
    try:
        rng = np.random.default_rng(0); I = build(cfg, rng, 1); M, cx, cy, cz = summarize(I); return I, metrics(M, cx, cy, cz)
    finally:
        tri = old

def fmt(m, k, nd=2): return ' / '.join(f'{v:.{nd}f}' for v in q(m[k]))

if __name__ == '__main__':
    R = {}
    print('guard area in2 %.1f  centroid %s' % (guard_area(), tuple(round(v, 2) for v in GUARD_C)))
    for nm, v in body_geom('final').items():
        if isinstance(v, float): print('body', nm, round(v, 2))
        if isinstance(v, np.ndarray): print('body', nm, 'V in3 %.2f' % v[0], 'c', (v[1:] / v[0]).round(3) if v[0] else '')
    ng = neck_geom(22); print('neck maple in3 %.2f (headstock %.2f) rosewood %.2f  board_end %.2f' % (ng['maple'][0], ng['maple_hs'][0], ng['rosewood'][0], ng['board_end']))
    configs = {
        'stock_vintage_solid': BASE_STOCK,
        'this_guitar_solid_body': dict(BASE_FINAL, solid=True),
        'this_guitar_final': BASE_FINAL,
    }
    # paired Monte Carlo: same seed -> same hardware draws where the parts are shared
    for nm, cfg in configs.items():
        I, m = run(cfg); R[nm] = {k: q(v) for k, v in m.items()}
        print(f'\n== {nm}: mass kg {fmt(m, "mass_kg")}, x_cm {fmt(m, "x_cm")}, y_cm {fmt(m, "y_cm")}, z_cm {fmt(m, "z_cm", 3)}')
        print(f'   theta_free deg {fmt(m, "theta_free", 1)}; tau20 Nm {fmt(m, "tau_20", 3)}; tau30 {fmt(m, "tau_30", 3)}; seat_tau {fmt(m, "seat_tau", 3)}; forearm N {fmt(m, "seat_forearm_N", 2)}; roll {fmt(m, "roll_deg", 1)}')
        Id, md = det(cfg)
        R[nm]['nominal'] = {k: float(np.asarray(v).ravel()[0]) for k, v in md.items()}
        R[nm]['parts'] = [(it[0], float(it[1][0]), float(np.asarray(it[2]).ravel()[0]), float(np.asarray(it[3]).ravel()[0]), float(np.asarray(it[4]).ravel()[0])) for it in Id]
        print('   nominal:', {k: round(v, 3) for k, v in R[nm]['nominal'].items()})
    # paired differences (same draws for shared parts)
    for a, b in (('this_guitar_final', 'stock_vintage_solid'), ('this_guitar_final', 'this_guitar_solid_body')):
        _, ma = run(configs[a]); _, mb = run(configs[b])
        R[f'diff_{a}_minus_{b}'] = {k: q(ma[k] - mb[k]) for k in ('mass_kg', 'x_cm', 'theta_free', 'tau_20', 'tau_30', 'seat_tau', 'seat_forearm_N', 'roll_deg')}
        print(f'\n{a} - {b}:', {k: [round(x, 3) for x in v] for k, v in R[f"diff_{a}_minus_{b}"].items()})
    # parts table (nominal) for the final
    print('\nparts, final nominal (g, x, y, z):')
    for p in R['this_guitar_final']['parts']: print('  %-34s %7.1f  %7.2f %6.2f %6.2f' % p)
    print('\nparts, stock nominal (g, x, y, z):')
    for p in R['stock_vintage_solid']['parts']: print('  %-34s %7.1f  %7.2f %6.2f %6.2f' % p)
    # levers (deterministic, relative to the final nominal)
    _, b0 = det(BASE_FINAL); base = {k: float(np.ravel(v)[0]) for k, v in b0.items()}
    _, s0 = det(BASE_STOCK); stockn = {k: float(np.ravel(v)[0]) for k, v in s0.items()}
    lev = {}
    def lever(name, cfg, horn=None):
        _, mm = det(cfg) if horn is None else (None, None)
        if horn is not None:
            Id, _ = det(cfg); M, cx, cy, cz = summarize(Id); mm = metrics(M, cx, cy, cz, horn=horn)
        v = {k: float(np.ravel(x)[0]) for k, x in mm.items()}
        lev[name] = dict(dmass_g=1000 * (v['mass_kg'] - base['mass_kg']), dx_cm=v['x_cm'] - base['x_cm'], theta_free=v['theta_free'],
                         dtheta=v['theta_free'] - base['theta_free'], tau_20=v['tau_20'], tau_30=v['tau_30'], seat_tau=v['seat_tau'],
                         seat_forearm_N=v['seat_forearm_N'], mass_kg=v['mass_kg'])
    lever('final as planned (Gotoh SD91 MG-T, 2-way steel rod)', BASE_FINAL)
    for t in TUNERS: lever(f'tuners: {t}', dict(BASE_FINAL, tuners=t))
    for r in RODS: lever(f'rod: {r}', dict(BASE_FINAL, rod=r))
    lever('headstock slug +45 g', dict(BASE_FINAL, slug=45.0))
    lever('headstock slug +22 g', dict(BASE_FINAL, slug=22.0))
    for gm in (20, 40, 60): lever(f'tail mass +{gm} g in solid tail (x 30.6)', dict(BASE_FINAL, extra=[('tail mass', gm, 30.6, 0.0, -0.875)]))
    lever('mass +40 g in the trem block region (x 26.1)', dict(BASE_FINAL, extra=[('block mass', 40, 26.1, -0.19, -0.8)]))
    lever('Ti 2-way rod + SD91 MG-T', dict(BASE_FINAL, rod='twoway_titanium'))
    lever('Ti 2-way rod + slug +45 g', dict(BASE_FINAL, rod='twoway_titanium', slug=45.0))
    for v in ('arm070', 'arm100', 'bellywhisper', 'bellyfull'): lever(f'carve: {v}', dict(BASE_FINAL, variant=v))
    for dxh, dyh, tag in ((0.25, -0.10, 'horn button 0.25 in tailward along the horn underside'), (0.0, 0.25, 'horn button 0.25 in toward the bass edge'),
                          (-0.15, 0.0, 'horn button 0.15 in further out (tip, impossible past the outline)')):
        lever(f'strap: {tag}', BASE_FINAL, horn=(HORN_BTN[0] + dxh, HORN_BTN[1] + dyh, HORN_BTN[2]))
    lever('roasted alder at 0.36 (light board)', dict(BASE_FINAL, alder=(0.36, 0.36, 0.36)))
    lever('roasted alder at 0.44 (heavy board)', dict(BASE_FINAL, alder=(0.44, 0.44, 0.44)))
    lever('neck maple 0.70 (heavy)', dict(BASE_FINAL, maple=(0.70, 0.70, 0.70)))
    lever('neck maple 0.60 (light)', dict(BASE_FINAL, maple=(0.60, 0.60, 0.60)))
    R['levers'] = lev; R['stock_nominal'] = stockn; R['final_nominal'] = base
    print('\nstock nominal: theta %.1f tau20 %.3f tau30 %.3f seat %.3f forearm %.2f N mass %.3f' % (stockn['theta_free'], stockn['tau_20'], stockn['tau_30'], stockn['seat_tau'], stockn['seat_forearm_N'], stockn['mass_kg']))
    print('levers (vs final nominal):')
    for k, v in lev.items():
        print('  %-62s dm %+6.1f g  dx %+.3f  theta %.2f (%+.2f)  tau20 %.3f tau30 %.3f  seat %.3f  forearm %.2f N  M %.3f' %
              (k, v['dmass_g'], v['dx_cm'], v['theta_free'], v['dtheta'], v['tau_20'], v['tau_30'], v['seat_tau'], v['seat_forearm_N'], v['mass_kg']))
    # sensitivities: 1 g at the tuners vs 1 g at the tail, in theta_free
    for tag, xyz in (('tuners', (-4.2, 0.93, TUNER_Z)), ('truss rod centre', (8.6, 0.0, -0.13)), ('tail', (30.6, 0, -0.875)), ('trem block', (26.1, -0.19, -0.8))):
        Id, _ = det(dict(BASE_FINAL, extra=[('probe', 10.0, *xyz)])); M, cx, cy, cz = summarize(Id); mm = metrics(M, cx, cy, cz)
        R.setdefault('sens_deg_per_10g', {})[tag] = float(np.ravel(mm['theta_free'])[0] - base['theta_free'])
    # headstock mass (at the tuner centroid) that would make the guitar dive at a 30 deg neck angle
    for nm, cfg in (('final', BASE_FINAL), ('stock', BASE_STOCK)):
        lo, hi = 0.0, 5000.0
        for _ in range(40):
            mid = 0.5 * (lo + hi); Id, _ = det(dict(cfg, extra=[('hs', mid, -4.2, 0.93, TUNER_Z)])); mm = metrics(*summarize(Id))
            lo, hi = (mid, hi) if float(np.ravel(mm['theta_free'])[0]) > 30.0 else (lo, mid)
        R.setdefault('headstock_g_to_dive_at_30deg', {})[nm] = mid
    print('headstock grams to dive at 30 deg:', R['headstock_g_to_dive_at_30deg'])
    print('theta_free change per +10 g:', {k: round(v, 3) for k, v in R['sens_deg_per_10g'].items()})
    json.dump(R, open(os.path.join(HERE, 'balance_results.json'), 'w'), indent=1, default=float)
