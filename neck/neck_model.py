"""Supercaster II set neck: parametric geometry + design checks (v1, 2026-11-13).

Units: inches, lb, degrees unless stated. Frame (same as body/carve/final_carve.py and src/neck-geometry.js):
  x along the neck from the nut (0) toward the bridge (scale 25.5), y across (BASS side +), z up,
  z = 0 is the board-top CENTRELINE chord (before planed relief and scallops).

Run:  python -I -W ignore neck_model.py          -> fig/*.png, results.json, tables printed (copied into DESIGN.md)
Import: from neck_model import P, fret_x, width, radius, depth, Phi, back_z, top_z, scallop_z, section_polygon, ...
Every number in P carries a tag: [lit: source] / [judged] / [body] (= read from body/carve/final_carve.py, read-only).
"""
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, 'fig')
IN = 0.0254

# ------------------------------------------------------------------------------------------------ parameters
P = dict(
    scale=25.5, frets=22,                      # [owner]
    nut_w=1.650, w21=2.20,                     # vintage Strat nut width [owner/body: neck_width]; 2.20 at fret 21 [body]
    R_nut=7.25, R_bridge=9.5,                  # conical compound radius, 9.5 lands at the saddle line x = 25.5 [owner/body]
    D1=0.82,                                   # centreline depth at fret 1 incl. board [body: neck_depth]
    board_t=0.20,                              # slab rosewood, centre thickness, flat glue face [body/BALANCE]
    # asymmetric shape (fixed in normalised coordinates for the recommended rule) [judged; repo neck-geometry.js defaults]
    u0=0.08, pb=2.30, pt=1.70,                 # apex offset (fraction of half-width, bass +), bass / treble superellipse exp.
    # frets: Jescar FW43080-S = stainless "6230-size" [lit: Jescar dimension guide via Philadelphia Luthier Tools]
    crown_w=0.080, crown_h=0.043, tang_w=0.020, barb_w=0.032, tang_d=0.050,
    slot_w=0.025, slot_d=0.060,                # loose fit: 0.007 barb interference (Jescar recommends 0.023 -> 0.009) [judged]
    # strings / setup
    nut_spread=1.375,                          # E-E centres at the nut [judged: measure Jordan's nut]
    bridge_spread_vintage=2.21875,             # 2-7/32 [lit: Fender/StewMac vintage spacing]
    bridge_spread_vt1=2.106,                   # 53.5 mm [lit: Thomann/Warwick VT1 listings]
    a17_bass=0.078, a17_treble=0.070,          # action at fret 17 (Fender method; 7.25" table 5/64 & 4/64, +hard player) [judged]
    nut_clear_bass=0.012, nut_clear_treble=0.008,  # string bottom above the fret plane at the nut [judged]
    relief_min=0.010, relief_max=0.016,        # range Jordan should be able to dial (~0.012 or more) [judged from owner spec]
    # planed relief + fall-away
    x_clamp=15.7,                              # board glued to body from here (pocket datum 15.69) [body]
    fall_away=0.006, fall_from_fret=15,        # [judged]
    # scallops
    sc_d1=0.030, sc_d22=0.075,                 # depth below the land at cell 1 / cell 22, linear in x (= geometric in fret) [judged]
    sc_land=0.0,                               # flat land beyond the crown foot: 0 = full-span S5 (best in the catch scan) [computed]
    sc_kappa=0.15,                             # catch cap d <= kappa L^2 (fit of the catch-limited depth ~0.168 L^2, 10 % margin) [computed]
    sc_edge_frac=0.40,                         # scallop depth kept at the start of the edge roll (fade from outer string) [judged]
    finger_R=0.30,                             # rigid fingertip proxy radius (7.6 mm) [judged]
    # edge roll + fret ends
    roll_b=0.14,                               # roll extent down the side (heavy) [judged]
    string_keep=0.030,                         # outer string centre stays this far inside the full-height crown [judged]
    dome_r=0.040,                              # hemispherical fret end radius = crown half-width [computed from wire]
    # truss rod (single acting, curved channel, spoke wheel at the body end)
    rod_d=0.1875, rod_x0=-0.30, rod_x1=18.45,  # 3/16 rod, anchor under the nut end, wheel under the board end [judged]
    rod_z_end=-0.31, rod_sag=0.25,             # rod centre below board top at the ends, extra depth mid-channel [judged]
    # wood
    E_maple=12.4e9, E_maple_rng=(11e9, 14e9),  # roasted curly maple E_L [lit: body/sim wood-properties.json]
    E_rose=11.5e9,                             # Indian rosewood E_L [judged, Wood-Handbook order]
    rho_maple=650., rho_rose=830., rho_steel=7850.,  # kg/m^3 [body/BALANCE ranges, likely values]
    # headstock / nut
    head_t=0.55,                               # [body/BALANCE, repo]
    post_pitch=0.937, post_x1=1.85, post_y1=0.88, post_dy=0.016, post_r=0.125,  # [lit: 23.8 mm hole pitch; rest judged]
    hole_h_flat=18.5, hole_h_short=18.0, hole_h_tall=19.0,  # mm from tuner baseplate to string hole [lit: Thomann / Rockinger]
    face_drop=0.0,                             # extra recess of the headstock face below the board glue plane [design knob]
    tuner_g=28.0,                              # g per SD91 MG-T incl. bushing (168 g / 6) [body/BALANCE]
    # trem (both bridges, parametric; MEASURE) [judged unless noted]
    pivot_x=25.25,                             # scale less 1/4 in [lit: published installation dimension, vintage-style trem]
    plate_t=0.10, plate_rear=1.70, float_lift=0.125,   # plate rear 1.70 behind pivot; 1/8" float [lit: Fender support]
    hole_behind_pivot=0.70, crest_min=0.20, crest_max=0.45,
    comp=(0.06, 0.10, 0.14, 0.10, 0.12, 0.16),  # saddle compensation high E..low E [judged]
    board_height=0.375, x_ref=15.69,           # board top above body top at the pocket datum [body]
)

# strings, high E (i=0, treble, y<0) .. low E (i=5, bass, y>0); 10.5-48 nickel round core (from calc/relief.py)
STR = [('E4', .0105, 329.63, 0.2226 * .0105**2), ('B3', .0135, 246.94, 0.2226 * .0135**2), ('G3', .017, 196.00, 0.2226 * .017**2),
       ('D3', .026, 146.83, 1.297e-4), ('A2', .036, 110.00, 2.404e-4), ('E2', .048, 82.41, 4.18e-4)]

def tensions(semis=-1, drop6=0):
    out = []
    for i, (n, d, f, uw) in enumerate(STR):
        ff = f * 2 ** (semis / 12) * (2 ** (-drop6 / 12) if i == 5 else 1)
        out.append(uw * (2 * P['scale'] * ff) ** 2 / 386.4)
    return np.array(out)
TUNINGS = {'E std': (0, 0), 'Eb std': (-1, 0), 'Eb drop C#': (-1, 2)}

# ------------------------------------------------------------------------------------------------ basic laws
S = P['scale']
def fret_x(n): return S * (1 - 2.0 ** (-np.asarray(n, float) / 12))
def fret_n(x): return -12 * np.log2(1 - np.asarray(x, float) / S)
X1, X12, X15, X16, X17, X21, X22 = (float(fret_x(k)) for k in (1, 12, 15, 16, 17, 21, 22))
BOARD_END = X22 + 0.25
def width(x): return P['nut_w'] + (P['w21'] - P['nut_w']) * np.asarray(x, float) / X21
def radius(x): return P['R_nut'] + (P['R_bridge'] - P['R_nut']) * np.asarray(x, float) / S
def sag(x, y): R = radius(x); return R - np.sqrt(R * R - np.asarray(y, float) ** 2)
def spread(x, bridge='vintage'):
    sb = P['bridge_spread_vintage'] if bridge == 'vintage' else P['bridge_spread_vt1']
    return P['nut_spread'] + (sb - P['nut_spread']) * np.asarray(x, float) / S
def string_y(i, x, bridge='vintage'): return (i / 5 - 0.5) * spread(x, bridge)   # i=0 high E at -spread/2

# ------------------------------------------------------------------------------------------------ profile rules
def _shape(u, u0, pb, pt):
    u = np.asarray(u, float)
    vb = np.clip((u - u0) / (1 - u0), 0, 1); vt = np.clip((u0 - u) / (1 + u0), 0, 1)
    return np.where(u >= u0, (1 - vb ** pb) ** (1 / pb), (1 - vt ** pt) ** (1 / pt))
def Phi(u, u0=None, pb=None, pt=None):
    """Unit asymmetric superellipse, normalised so Phi(0) = 1 (D is the CENTRELINE depth, the body model's convention)."""
    u0 = P['u0'] if u0 is None else u0; pb = P['pb'] if pb is None else pb; pt = P['pt'] if pt is None else pt
    return _shape(u, u0, pb, pt) / _shape(0.0, u0, pb, pt)

def _lin(x, a, b, xa, xb): return a + (b - a) * (np.asarray(x, float) - xa) / (xb - xa)
RULES = {
    # name: (label, D(x), (u0, pb, pt)(x), ruled?)
    'L': ('Linear in x (param. loft)',
          lambda x: _lin(x, P['D1'], 0.92, X1, X12),
          lambda x: (_lin(x, .08, .04, X1, X15), _lin(x, 2.30, 2.15, X1, X15), _lin(x, 1.70, 1.90, X1, X15)), False),
    'F': ('Fret-position (equal step per fret)',
          lambda x: P['D1'] + (0.92 - P['D1']) * (fret_n(np.maximum(x, 1e-9)) - 1) / 11,
          lambda x: (_lin(fret_n(np.maximum(x, 1e-9)), .08, .04, 1, 15), _lin(fret_n(np.maximum(x, 1e-9)), 2.30, 2.15, 1, 15),
                     _lin(fret_n(np.maximum(x, 1e-9)), 1.70, 1.90, 1, 15)), False),
    'C': ('Cone-coupled: D ~ board radius',
          lambda x: P['D1'] * radius(x) / radius(X1),
          lambda x: (P['u0'], P['pb'], P['pt']), True),
    'G': ('Constant ratio D/W (true cone)',
          lambda x: P['D1'] * width(x) / width(X1),
          lambda x: (P['u0'], P['pb'], P['pt']), True),
}
REC = 'C'
def depth(x, rule=REC): return RULES[rule][1](np.asarray(x, float))
def asym(x, rule=REC):
    a = RULES[rule][2](np.asarray(x, float)); return tuple(np.broadcast_to(v, np.shape(x)) * 1.0 for v in a)
def back_z(x, y, rule=REC):
    """Back of the neck: z = -D(x) Phi(2y/W(x)). For rules C and G every term is linear in x at fixed u -> ruled surface."""
    u0, pb, pt = asym(x, rule); return -depth(x, rule) * Phi(2 * np.asarray(y) / width(x), u0, pb, pt)

# ------------------------------------------------------------------------------------------------ board top: relief, scallops, roll
def planed(x):
    """Depth planed into the board top (>0 = removed). Parabola with sagitta s_p between the nut and x_clamp + C2 fall-away."""
    x = np.asarray(x, float); s = PLANED_SAG[0]; xc = P['x_clamp']
    xi = np.clip(x / xc, 0, 1); r = 4 * s * xi * (1 - xi)
    xf = fret_x(P['fall_from_fret']); t = np.clip((x - xf) / (BOARD_END - xf), 0, 1)
    return r + P['fall_away'] * (10 * t**3 - 15 * t**4 + 6 * t**5)
PLANED_SAG = [0.010]   # set by relief_design()

def S5(t): t = np.clip(t, 0, 1); return t**3 * (10 - 15 * t + 6 * t * t)
def sc_depth_cell(k):
    """Scallop depth law for cell k (between fret k-1 and k): linear in the cell-centre x (geometric in fret number)."""
    xm = 0.5 * (fret_x(k - 1) + fret_x(k)); xm1 = 0.5 * fret_x(1); xm22 = 0.5 * (X21 + X22)
    lin = P['sc_d1'] + (P['sc_d22'] - P['sc_d1']) * (xm - xm1) / (xm22 - xm1)
    L = fret_x(k) - fret_x(k - 1)
    return np.minimum(lin, P['sc_kappa'] * L * L) if CATCH_CAP[0] else lin
CATCH_CAP = [True]
def cell_geom(k):
    a = (fret_x(k - 1) + P['crown_w'] / 2) if k > 1 else 0.0; b = fret_x(k) - P['crown_w'] / 2
    C = b - a; land = min(P['sc_land'], 0.30 * C); return a, b, C, land
def scallop_long(x, k=None, d=None, land=None):
    """Scallop depth (>0) along x at full lateral weight. S5 ramps: zero slope AND curvature where they meet the land."""
    x = np.asarray(x, float); out = np.zeros_like(x)
    ks = range(1, P['frets'] + 1) if k is None else [k]
    for kk in ks:
        a, b, C, l0 = cell_geom(kk); l = l0 if land is None else land; dd = sc_depth_cell(kk) if d is None else d
        r = C / 2 - l; xi = np.minimum(x - a, b - x); m = (x > a) & (x < b)
        out = np.where(m, dd * S5((xi - l) / max(r, 1e-6)), out)
    return out
def roll_a(x):
    """Top setback of the edge roll: whatever the outer-string margin leaves after the domed end and string_keep (vintage spread)."""
    m = width(x) / 2 - spread(x, 'vintage') / 2 - STR[0][1] / 2
    return np.clip(m - P['dome_r'] - P['string_keep'], 0.03, 0.08)
def lateral_w(x, y):
    yo = spread(x, 'vintage') / 2 + 0.03; ye = width(x) / 2 - roll_a(x)
    t = (np.abs(y) - yo) / np.maximum(ye - yo, 1e-3)
    return 1 - (1 - P['sc_edge_frac']) * S5(t)
def scallop_z(x, y): return -scallop_long(x) * lateral_w(x, y)
def side_y(x, z_below_top, side, rule=REC):
    """|y| of the back surface at depth z (below the board-top centreline), on the bass (+1) or treble (-1) side. Analytic."""
    u0, pb, pt = asym(x, rule); D = depth(x, rule); s0 = _shape(0.0, u0, pb, pt)
    t = np.clip(z_below_top / D * s0, 0, 1)
    if side > 0: v = (1 - t ** pb) ** (1 / pb); u = u0 + v * (1 - u0)
    else:        v = (1 - t ** pt) ** (1 / pt); u = -(u0 - v * (1 + u0))
    return u * width(x) / 2
def roll_b_side(x, side):
    """Side extent of the roll on each side: roll_b, but no deeper than where the shoulder has already curved in to
    yc + 0.6 a (keeps the ellipse's horizontal semi-axis >= 0.6 a). The trimmed treble shoulder gets a shorter roll."""
    x = np.asarray(x, float); hw = width(x) / 2; a = roll_a(x); yc = hw - a
    u0, pb, pt = asym(x); ut = np.asarray(side, float) * (yc + 0.6 * a) / hw
    dep = depth(x) * Phi(ut, u0, pb, pt) - (sag(x, hw) + planed(x))
    return np.clip(dep, 0.02, P['roll_b'])
def roll_drop(x, y):
    """Drop of the top inside the edge roll: quarter ellipse from the top (setback roll_a from the nominal edge W/2, tangent
    to the top) to the side wall roll_b below the top edge (tangent to the back superellipse there). Outside it: no wood."""
    x = np.asarray(x, float); y = np.asarray(y, float); hw = width(x) / 2; a = roll_a(x); b = P['roll_b']
    zt_edge = sag(x, hw) + planed(x); yc = hw - a
    bs = roll_b_side(x, np.sign(y) + (y == 0))
    ys = np.where(y >= 0, side_y(x, zt_edge + bs, 1), side_y(x, zt_edge + bs, -1))
    ah = np.maximum(ys - yc, 1e-4); b = bs
    q = (np.abs(y) - yc) / ah
    return np.where(q <= 0, 0.0, np.where(q < 1, b * (1 - np.sqrt(np.clip(1 - q * q, 0, 1))), 10.0))
def top_z(x, y, scallops=True, roll=True):
    z = -sag(x, y) - planed(x)
    if scallops: z = z + scallop_z(x, y)
    if roll: z = z - roll_drop(x, y)
    return z

def section_polygon(x, rule=REC, scallops=True, n=801):
    """Closed (y, z) outline of the neck cross-section at x (board + neck, roll applied, back by the rule)."""
    hw = width(x) / 2; y = np.linspace(-hw, hw, n)
    zt = top_z(x, y, scallops); zb = back_z(x, y, rule)
    ok = zb < zt
    yy = np.concatenate([y[ok], y[ok][::-1]]); zz = np.concatenate([zt[ok], zb[ok][::-1]])
    return yy, zz

# ------------------------------------------------------------------------------------------------ section stiffness
def EI_section(x, scallops=True, Em=None, rod_hole=True, ny=161, nz=241):
    """Composite EI (N m^2) and neutral-axis z (in) of the section at x. Rosewood above z=-board_t, maple below.
    Rod hole (3/16 round at rod_z(x)) removed; the glued filler strip above it counts as maple. Loose frets: no stiffness."""
    Em = P['E_maple'] if Em is None else Em
    hw = width(x) / 2; D = float(depth(x)) / float(Phi(0.0)) * 1.01
    y = np.linspace(-hw, hw, ny); z = np.linspace(-D - 0.01, 0.01, nz); dy = y[1] - y[0]; dz = z[1] - z[0]
    Y, Z = np.meshgrid(y, z, indexing='ij')
    inside = (Z < top_z(x, Y, scallops)) & (Z > back_z(x, Y))
    if rod_hole and P['rod_x0'] < x < P['rod_x1']:
        inside &= ~((Y**2 + (Z - rod_z(x))**2) < (P['rod_d'] / 2)**2)
    E = np.where(Z > -P['board_t'] - planed(x) * 0, P['E_rose'], Em) * inside
    dA = dy * dz * IN * IN
    EA = (E * dA).sum(); zc = (E * Z * dA).sum() / EA
    EI = (E * ((Z - zc) * IN) ** 2 * dA).sum()
    return EI, zc, (inside * dA).sum(), ((Z > -P['board_t']) * inside * dA).sum()
def rod_z(x):
    xi = np.clip((np.asarray(x, float) - P['rod_x0']) / (P['rod_x1'] - P['rod_x0']), 0, 1)
    return P['rod_z_end'] - P['rod_sag'] * 4 * xi * (1 - xi)

# ------------------------------------------------------------------------------------------------ relief
def string_height_avg(x):
    """Mean string-centre height above the board-top chord along the neck (setup in P), for the tension eccentricity."""
    zs = []
    for i in range(6):
        c = P['nut_clear_treble'] + (P['nut_clear_bass'] - P['nut_clear_treble']) * i / 5
        a = P['a17_treble'] + (P['a17_bass'] - P['a17_treble']) * i / 5
        z0 = -sag(0, string_y(i, 0)) + P['crown_h'] + c; z17 = -sag(X17, string_y(i, X17)) + P['crown_h'] + a
        zs.append(z0 + (z17 - z0) * np.asarray(x) / X17 + STR[i][1] / 2)
    return np.mean(zs, axis=0)

_EI_CACHE = {}
def EI_table(scallops, Em):
    key = (scallops, Em, PLANED_SAG[0], P['sc_d1'], P['sc_d22'])
    if key not in _EI_CACHE:
        xs = np.linspace(0, P['x_clamp'], 700)
        r = np.array([EI_section(xx, scallops, Em)[:2] for xx in xs]); _EI_CACHE[key] = (xs, r[:, 0], r[:, 1])
    return _EI_CACHE[key]
def bow(Tlb, scallops=True, Em=None, F_rod=0.0):
    """Gap under a straightedge on frets 1..16 (in) from string compression at the string line + rod tendon (F_rod lb).
    Clamped at x_clamp (glued joint). Same method as calc/relief.py, generalised."""
    Em = P['E_maple'] if Em is None else Em
    xs, EI, zc = EI_table(scallops, Em)
    T = Tlb * 4.448; F = F_rod * 4.448
    e_s = (string_height_avg(xs) - zc) * IN
    e_r = (rod_z(xs) - zc) * IN * ((xs > P['rod_x0']) & (xs < P['rod_x1']))
    k = (T * e_s + F * e_r) / EI
    X = xs * IN; th = np.zeros_like(X); v = np.zeros_like(X)
    for i in range(len(X) - 2, -1, -1):
        dx = X[i + 1] - X[i]; th[i] = th[i + 1] - k[i] * dx; v[i] = v[i + 1] - th[i] * dx
    a, b = X1 * IN, X16 * IN
    chord = np.interp(X, [a, b], [np.interp(a, X, v), np.interp(b, X, v)])
    m = (X >= a) & (X <= b); g = (chord - v)[m]
    return float(g[np.argmax(np.abs(g))] / IN)  # + = relief (concave fret line), - = back-bow
def planed_relief_gap():
    xs = np.linspace(X1, X16, 400); z = -planed(xs); ch = np.interp(xs, [X1, X16], [z[0], z[-1]])
    return float(np.max(ch - z))

# ------------------------------------------------------------------------------------------------ fingertip catch metric
def crown_z(t):
    a = P['crown_w'] / 2; h = P['crown_h']; q = np.abs(t) / a
    return np.where(q < 1, h * np.sqrt(np.clip(1 - q * q, 0, 1)), -np.inf)
def cell_profile(L, mode, d=0.0, land=None, rebate=0.0):
    """Longitudinal profile across one cell from crown centre at 0 to crown centre at L.
    mode: 'flat' | 'land' (S5 with lands, proposed) | 'sin2' (full-span sin^2 between crown feet) | 'rebate' (land + seat)."""
    a = P['crown_w'] / 2
    def f(x):
        x = np.asarray(x, float); c = np.maximum(crown_z(x), crown_z(x - L)) - rebate
        A, B = a, L - a; C = B - A
        if mode == 'flat' or d == 0: w = np.zeros_like(x)
        elif mode == 'sin2': s = np.clip((x - A) / C, 0, 1); w = -d * np.sin(np.pi * s) ** 2
        else:
            l = (min(P['sc_land'], 0.30 * C) if land is None else land); r = C / 2 - l
            xi = np.minimum(x - A, B - x); w = -d * S5((xi - l) / max(r, 1e-6))
        w = np.where((x > A) & (x < B), w, 0.0)
        return np.maximum(c, w)
    return f
def finger_catch(f, L, R=None, dx=0.001):
    """Rigid fingertip (radius R) slid across a whole cell, crown L -> crown 0. Its centre path is the upper envelope of f.
    Returns (catch = largest slope jump of the path in deg, dip = how far the centre drops below its height on a bare
    land, max uphill slope deg, pad touches wood at mid-cell?)."""
    R = P['finger_R'] if R is None else R
    q = np.arange(-R - 0.05, L + R + 0.05, dx); zq = f(q); w = int(R / dx)
    i0 = np.searchsorted(q, 0.0); i1 = np.searchsorted(q, L)
    idx = np.arange(i0, i1 + 1)[:, None] + np.arange(-w, w + 1)[None, :]
    off = np.arange(-w, w + 1) * dx; cap = np.sqrt(np.clip(R * R - off * off, 0, None))
    V = zq[idx] + cap[None, :]; path = V.max(1); arg = V.argmax(1)
    sl = np.arctan(np.diff(path) / dx); jump = np.abs(np.diff(sl))
    mid = len(path) // 2; qc = q[idx[mid, arg[mid]]]
    wood = (abs(qc) > P['crown_w'] / 2) and (abs(qc - L) > P['crown_w'] / 2)
    return float(np.degrees(jump.max())), float(R - path.min()), float(np.degrees(np.abs(sl).max())), bool(wood)
def max_depth_for_catch(k, mode='land', tol=1.0):
    """Deepest scallop of this mode whose catch stays within `tol` deg of the unscalloped board in cell k."""
    L = float(fret_x(k) - fret_x(k - 1)); ref = finger_catch(cell_profile(L, 'flat'), L)[0]
    lo, hi = 0.0, 0.20
    for _ in range(14):
        mid = 0.5 * (lo + hi); c = finger_catch(cell_profile(L, mode, mid), L)[0]
        lo, hi = (mid, hi) if c <= ref + tol else (lo, mid)
    return lo, ref

# ------------------------------------------------------------------------------------------------ headstock / nut
HEADSTOCK_STD = np.array([   # repo src/neck-geometry.js vintage outline (bass side +y); reverse = mirror y -> -y
    [0.05, 0.825], [-0.5, 0.9], [-1.2, 1.32], [-2.1, 1.55], [-3.6, 1.6], [-5.2, 1.48], [-6.4, 1.2],
    [-7.05, 0.75], [-7.3, 0.15], [-7.15, -0.45], [-6.75, -0.78], [-6.1, -0.82], [-5.4, -0.62],
    [-4.4, -0.42], [-3.2, -0.42], [-2.0, -0.6], [-1.0, -0.84], [-0.4, -0.86], [0.05, -0.825]])
def posts(reverse=True):
    """Post centres k = 1..6 from the nut. Standard: k=1 carries low E (bass side). Reverse: k=1 carries high E (treble side)."""
    out = []
    for k in range(1, 7):
        x = -(P['post_x1'] + P['post_pitch'] * (k - 1)); y = P['post_y1'] - P['post_dy'] * (k - 1)
        out.append((x, -y if reverse else y))
    return out   # list index k-1
def string_post(i, reverse=True):
    k = (i + 1) if reverse else (6 - i)       # reverse: high E (i=0) nearest
    return k, posts(reverse)[k - 1]
def hole_height(kind, k):
    """String-hole height above the headstock FACE (in). Baseplate figure minus the headstock thickness."""
    if kind == 'flat': mm = P['hole_h_flat']
    elif kind == 'stag_far_short':  mm = P['hole_h_short'] if k >= 4 else P['hole_h_tall']   # short posts on the far strings (standard RH head: trebles)
    elif kind == 'stag_near_short': mm = P['hole_h_tall'] if k >= 4 else P['hole_h_short']   # short posts nearest the nut (reverse head: trebles) - recommended
    return mm / 25.4 - P['head_t']
def nut_geometry(i, reverse=True, posts_kind='stag_near_short', face_drop=None, tree=None):
    """3-D wrap at the nut for string i. tree=(x, h_above_face) or None. Returns dict of angles (deg), lengths."""
    fd = P['face_drop'] if face_drop is None else face_drop
    c = P['nut_clear_treble'] + (P['nut_clear_bass'] - P['nut_clear_treble']) * i / 5
    y0 = string_y(i, 0); d = STR[i][1]
    z0 = -sag(0, y0) + P['crown_h'] + c + d / 2            # string centre at the nut break point
    zf = -P['board_t'] - fd                                 # headstock face
    k, (xp, yp) = string_post(i, reverse)
    yc = yp + (P['post_r'] + d / 2) * np.sign(-yp)          # inner side of the post
    zh = zf + hole_height(posts_kind, k)
    # speaking direction (toward the bridge): rises ~ string_height slope
    sl = (string_height_avg(X12) - string_height_avg(0)) / X12
    v_sp = np.array([1.0, (string_y(i, 1.0) - y0), sl]); v_sp /= np.linalg.norm(v_sp)
    pts = [(0.0, y0, z0)]
    if tree is not None:
        xt, ht = tree; yt = y0 + (yc - y0) * xt / xp; pts.append((xt, yt, zf + ht + d / 2))
    pts.append((xp, yc, zh))
    segs = [np.array(pts[j + 1]) - np.array(pts[j]) for j in range(len(pts) - 1)]
    u = [s / np.linalg.norm(s) for s in segs]
    th_nut = math.degrees(math.acos(np.clip(np.dot(-v_sp, u[0]), -1, 1)))   # deflection at the nut
    th_v = math.degrees(math.atan2(pts[0][2] - pts[1][2], abs(pts[1][0])) + math.atan(sl))
    th_l = math.degrees(math.atan2(abs(pts[-1][1] - y0), abs(xp)))
    th_tree = math.degrees(math.acos(np.clip(np.dot(u[0], u[1]), -1, 1))) if tree is not None else 0.0
    Ls = [float(np.linalg.norm(s)) for s in segs]
    return dict(k=k, post=(xp, yp), theta_nut=th_nut, vert=th_v, lat=th_l, theta_tree=th_tree, L=Ls, z0=z0, zh=zh)
def return_error_cents(i, g, mu, Tlb):
    """Worst-case pitch offset after a dive/return when friction holds a tension step at the nut (and tree).
    Behind-nut segments are elastic and the locking post is fixed: dT_speaking = sum(j_m * L_beyond_m) / L_total."""
    Ls = S; Lb = g['L']; jn = mu * math.radians(g['theta_nut']); jt = mu * math.radians(g['theta_tree'])
    Ltot = Ls + sum(Lb)
    num = jn * sum(Lb) + (jt * Lb[-1] if len(Lb) > 1 else 0.0)
    return 865.6 * num / Ltot   # cents (865.6 = 1200/(2 ln 2))

# ------------------------------------------------------------------------------------------------ saddles / neck angle
def string_line(i, x, bridge='vintage'):
    """String-BOTTOM height above the board-top chord (neck frame) on a straight line nut -> fret 17 (setup in P)."""
    c = P['nut_clear_treble'] + (P['nut_clear_bass'] - P['nut_clear_treble']) * i / 5
    a = P['a17_treble'] + (P['a17_bass'] - P['a17_treble']) * i / 5
    z0 = -sag(0, string_y(i, 0, bridge)) + P['crown_h'] + c
    z17 = -sag(X17, string_y(i, X17, bridge)) - planed(X17) + P['crown_h'] + a
    return z0 + (z17 - z0) * np.asarray(x) / X17, (z17 - z0) / X17
def saddle_case(alpha_deg, bridge='vintage', H=None, Tlb=None, plate_t=None, lift=None, hole=None):
    """Per string: crest height above the plate, behind-saddle angle, total deflection, down-force (lb)."""
    H = P['board_height'] if H is None else H; plate_t = P['plate_t'] if plate_t is None else plate_t
    lift = P['float_lift'] if lift is None else lift; hole = P['hole_behind_pivot'] if hole is None else hole
    Tlb = tensions(-1, 0) if Tlb is None else Tlb
    ta = math.tan(math.radians(alpha_deg)); tphi = lift / P['plate_rear']
    rows = []
    for i in range(6):
        xc = S + P['comp'][i]; zl, sl = string_line(i, xc, bridge)
        zb = H + (xc - P['x_ref']) * ta + zl                     # string bottom on the crest, body frame
        zpl = plate_t + (xc - P['pivot_x']) * tphi
        hc = zb - zpl
        xh = P['pivot_x'] + hole; drop = hc - (xh - xc) * tphi
        beh = math.degrees(math.atan2(drop, xh - xc)); sp = math.degrees(math.atan(sl + ta))
        th = beh + sp; F = 2 * Tlb[i] * math.sin(math.radians(th) / 2)
        rows.append(dict(string=STR[i][0], crest=hc, behind=beh, total=th, down_lb=F))
    return rows
def alpha_for_crest(target, bridge='vintage', H=None):
    """Neck angle (deg) that puts the MEAN outer-string (E, e) crest height at `target` above the plate."""
    lo, hi = -3.0, 3.0
    for _ in range(60):
        mid = 0.5 * (lo + hi); r = saddle_case(mid, bridge, H); m = 0.5 * (r[0]['crest'] + r[5]['crest'])
        lo, hi = (mid, hi) if m < target else (lo, mid)
    return 0.5 * (lo + hi)

# ------------------------------------------------------------------------------------------------ mass / modes (acoustic notes)
def poly_props(poly):
    x, y = poly[:, 0], poly[:, 1]; x2, y2 = np.roll(x, -1), np.roll(y, -1); cr = x * y2 - x2 * y
    A = cr.sum() / 2; cx = ((x + x2) * cr).sum() / (6 * A); cy = ((y + y2) * cr).sum() / (6 * A)
    Ixx = ((x * x + x * x2 + x2 * x2) * cr).sum() / 12   # int x^2 dA about origin
    return abs(A), cx, cy, abs(Ixx)
def headstock_mass(reverse=True):
    poly = HEADSTOCK_STD.copy(); poly = poly[poly[:, 0] <= 0.05]
    if reverse: poly[:, 1] *= -1
    A, cx, cy, Ixx = poly_props(poly)
    hole_A = 6 * math.pi * (11 / 32 / 2) ** 2
    m_wood = (A - hole_A) * P['head_t'] * IN**3 * P['rho_maple'] * 1000    # g
    m_t = 6 * P['tuner_g']; pp = np.array(posts(reverse))
    M = m_wood + m_t
    cxm = (m_wood * cx + P['tuner_g'] * pp[:, 0].sum()) / M; cym = (m_wood * cy + P['tuner_g'] * pp[:, 1].sum()) / M
    Iw = m_wood * (Ixx / A - cx**2) + m_wood * (cx - cxm) ** 2
    It = (P['tuner_g'] * (pp[:, 0] - cxm) ** 2).sum()
    return dict(m_wood=m_wood, m_tuners=m_t, M=M, cx=cxm, cy=cym, I_cm_gin2=Iw + It)
def neck_modes(scallops=True, Em=None, n_el=60):
    """Cantilever (glued joint at x_clamp) Euler-Bernoulli FE + rigid headstock at the nut. Lowest two bending f (Hz).
    For RANKING scallop effects only: the body sim (STUDIES) carries the real coupled neck modes (177 / 282 Hz)."""
    from scipy.linalg import eigh
    Em = P['E_maple'] if Em is None else Em
    xs = np.linspace(0, P['x_clamp'], n_el + 1); N = n_el + 1
    K = np.zeros((2 * N, 2 * N)); M = np.zeros_like(K)
    for e in range(n_el):
        xm = 0.5 * (xs[e] + xs[e + 1]); EI, zc, A, Ab = EI_section(xm, scallops, Em, ny=81, nz=121)
        mpl = (Ab * P['rho_rose'] + (A - Ab) * P['rho_maple'] + math.pi * (P['rod_d'] * IN / 2) ** 2 * P['rho_steel'])  # kg/m
        L = (xs[e + 1] - xs[e]) * IN
        k = EI / L**3 * np.array([[12, 6*L, -12, 6*L], [6*L, 4*L*L, -6*L, 2*L*L], [-12, -6*L, 12, -6*L], [6*L, 2*L*L, -6*L, 4*L*L]])
        m = mpl * L / 420 * np.array([[156, 22*L, 54, -13*L], [22*L, 4*L*L, 13*L, -3*L*L], [54, 13*L, 156, -22*L], [-13*L, -3*L*L, -22*L, 4*L*L]])
        idx = [2*e, 2*e+1, 2*e+2, 2*e+3]; K[np.ix_(idx, idx)] += k; M[np.ix_(idx, idx)] += m
    for n in range(1, P['frets'] + 1):    # frets as point masses (stainless ~7.9 g/cc, crown+tang ~ 0.0028 in^2)
        xn = float(fret_x(n))
        if xn < P['x_clamp']:
            j = int(round(xn / P['x_clamp'] * n_el)); M[2*j, 2*j] += 0.004 * width(xn) * IN**3 * 7900
    h = headstock_mass(True); Mh = h['M'] / 1000; e = h['cx'] * IN; Icm = h['I_cm_gin2'] / 1000 * IN**2
    M[0, 0] += Mh; M[0, 1] += Mh * e; M[1, 0] += Mh * e; M[1, 1] += Mh * e * e + Icm
    free = np.arange(0, 2 * N - 2)
    w2 = eigh(K[np.ix_(free, free)], M[np.ix_(free, free)], eigvals_only=True)
    return np.sqrt(np.abs(w2[:3])) / (2 * math.pi)
def scallop_volume():
    xs = np.linspace(0, X22, 6000); out = 0.0; dx = xs[1] - xs[0]
    for x in xs:
        hw = width(x) / 2; y = np.linspace(-hw, hw, 81); dy = y[1] - y[0]
        out += float((-scallop_z(x, y)).sum() * dy * dx)
    return out   # in^3

# ================================================================================================ studies
def relief_design():
    """Choose the planed sagitta: slack-rod relief at the lowest tension, stiffest wood = relief_max. Then the rod force
    that brings the highest tension, softest wood back to relief_min."""
    Tmin = tensions(*TUNINGS['Eb drop C#']).sum(); Tmax = tensions(*TUNINGS['E std']).sum()
    Eh, El = P['E_maple_rng'][1], P['E_maple_rng'][0]
    PLANED_SAG[0] = 0.0
    b_min = bow(Tmin, True, Eh)
    # planed geometric gap is (to first order) additive to the elastic bow
    lo, hi = 0.0, 0.03
    for _ in range(40):
        mid = 0.5 * (lo + hi); PLANED_SAG[0] = mid
        (lo, hi) = (mid, hi) if planed_relief_gap() + b_min < P['relief_max'] else (lo, mid)
    PLANED_SAG[0] = 0.5 * (lo + hi)
    g = planed_relief_gap()
    rows = {}
    for nm, (s, d6) in TUNINGS.items():
        T = tensions(s, d6).sum(); rows[nm] = dict(T=T)
        for lab, sc in (('flat', False), ('scal', True)):
            for E, el in ((El, 'soft'), (P['E_maple'], 'nom'), (Eh, 'stiff')):
                rows[nm][f'{lab}_{el}'] = bow(T, sc, E)
    # rod force for the worst case
    need = g + bow(Tmax, True, El) - P['relief_min']
    per = (bow(Tmax, True, El, 0.0) - bow(Tmax, True, El, 100.0)) / 100.0
    F = need / per
    return dict(planed_sag=PLANED_SAG[0], planed_gap=g, rows=rows, rod_need_in=need, rod_in_per_100lb=per * 100, rod_F_lb=F)

def catch_study():
    out = []
    for k in (1, 3, 5, 7, 9, 11, 12, 13, 14, 15, 17, 19, 22):
        L = float(fret_x(k) - fret_x(k - 1)); d = float(sc_depth_cell(k))
        cf = finger_catch(cell_profile(L, 'flat'), L)
        cl = finger_catch(cell_profile(L, 'land', d), L)
        cs = finger_catch(cell_profile(L, 'sin2', d), L)
        cr = finger_catch(cell_profile(L, 'rebate', d, rebate=0.010), L)
        CATCH_CAP[0] = False; dl = float(sc_depth_cell(k)); CATCH_CAP[0] = True
        cy = finger_catch(cell_profile(L, 'land', dl), L)
        out.append(dict(cell=k, L=L, d=d, d_lin=dl, yng=cy, land=cell_geom(k)[3], flat=cf, land_=cl, sin2=cs, rebate=cr,
                        cap_land=max_depth_for_catch(k, 'land')[0], cap_sin2=max_depth_for_catch(k, 'sin2')[0]))
    return out

def press_sharp_cents(i, p, L_cell, Tlb):
    """Cents sharp when string i is pressed p (in) below the crown plane mid-cell (rigid frets, free to slide over them)."""
    d = STR[i][1]; EA = 29e6 * math.pi / 4 * d * d   # plain steel only
    a = L_cell / 2; dL = 2 * (math.sqrt(a * a + p * p) - a)
    return 865.6 * EA * dL / (Tlb * (S + 2.0)) if i <= 2 else float('nan')

def wood_checks():
    """Least rosewood left under scallop bottoms / at slots; rod cover; string-margin & dome checks per fret."""
    rows = []
    for k in range(1, P['frets'] + 1):
        a, b, C, l = cell_geom(k); xm = 0.5 * (a + b); hw = width(xm) / 2
        y = np.linspace(-hw + roll_a(xm), hw - roll_a(xm), 201)
        left = P['board_t'] - sag(xm, y) - planed(xm) - (-scallop_z(xm, y))
        rod_cover = (-P['board_t'] - (rod_z(xm) + P['rod_d'] / 2))
        rows.append(dict(cell=k, x=xm, d=float(sc_depth_cell(k)), rose_min=float(left.min()), rose_ctr=float(left[100]),
                         rod_top_below_glue=float(rod_cover)))
    frets = []
    for n in range(1, P['frets'] + 1):
        x = float(fret_x(n)); hw = width(x) / 2; a = float(roll_a(x))
        yslot = hw - a - 0.02; slot_left = P['board_t'] - sag(x, yslot) - planed(x) - P['slot_d']
        for br in ('vintage', 'vt1'):
            pass
        mv = hw - spread(x, 'vintage') / 2 - STR[0][1] / 2; mt = hw - spread(x, 'vt1') / 2 - STR[0][1] / 2
        full_end = hw - a - P['dome_r']
        frets.append(dict(fret=n, x=x, width=2 * hw, roll_a=a, dome_apex_from_edge=a, full_crown_from_edge=a + P['dome_r'],
                          keep_vintage=float(mv - (a + P['dome_r'])), keep_vt1=float(mt - (a + P['dome_r'])),
                          wood_under_slot_end=float(slot_left), edge_board_t=float(P['board_t'] - sag(x, hw) - planed(x))))
    return rows, frets

def profile_table():
    out = {}
    for r in RULES:
        rows = []
        for n in (1, 5, 9, 12, 15, 17, 22):
            x = float(fret_x(n)); D = float(depth(x, r)); W = float(width(x)); u0, pb, pt = (float(v) for v in asym(x, r))
            sb = float(Phi(0.75, u0, pb, pt)) * D; st = float(Phi(-0.75, u0, pb, pt)) * D
            rows.append(dict(fret=n, x=x, D=D, W=W, DW=D / W, apex_in=u0 * W / 2, pb=pb, pt=pt, sh_bass=sb, sh_treb=st,
                             asym=sb / st, R=float(radius(x))))
        xs = np.linspace(X1, X15, 400); Ds = depth(xs, r); d1 = np.gradient(Ds, xs); d2 = np.gradient(d1, xs)
        out[r] = dict(rows=rows, dDdx_1=float(d1[0]), dDdx_15=float(d1[-1]), d2max=float(np.abs(d2).max()),
                      D_heel_x0=float(depth(X15 - 0.5, r)), body_D_heel_x0=float(P['D1'] * radius(X15 - 0.5) / radius(X1)),
                      ruled=RULES[r][3])
    return out

def ruled_check(rule, n=7):
    """Max deviation (in) of the back surface from straight lines at fixed u between x = fret 1 and fret 15."""
    us = np.linspace(-0.95, 0.95, n); xa, xb = X1, X15; dev = 0.0
    for u in us:
        xs = np.linspace(xa, xb, 50); z = np.array([float(back_z(x, u * width(x) / 2, rule)) for x in xs])
        y = np.array([u * float(width(x)) / 2 for x in xs])
        zl = np.interp(xs, [xa, xb], [z[0], z[-1]]); yl = np.interp(xs, [xa, xb], [y[0], y[-1]])
        dev = max(dev, float(np.max(np.hypot(z - zl, y - yl))))
    return dev

# ================================================================================================ figures
def figures(R):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa
    os.makedirs(FIG, exist_ok=True)
    plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
    FR = (1, 5, 9, 12, 17, 22); cols = plt.cm.viridis(np.linspace(0.05, 0.9, len(FR)))
    # 1. sections per rule
    fig, axs = plt.subplots(2, 2, figsize=(11, 7.4), sharex=True, sharey=True)
    for ax, r in zip(axs.flat, RULES):
        for n, c in zip(FR, cols):
            y, z = section_polygon(float(fret_x(n)), r, scallops=False); ax.plot(y, z, color=c, lw=1.3, label=f'fret {n}')
        ax.axvline(0, color='0.8', lw=0.6); ax.set_aspect('equal'); ax.set_title(f"{r}: {RULES[r][0]}" + ('  [ruled]' if RULES[r][3] else ''))
        ax.text(0.98, 0.04, 'bass +y  ->', transform=ax.transAxes, ha='right', color='0.4')
    axs[0, 0].legend(ncol=3, fontsize=7, loc='lower left'); fig.supxlabel('y (in), bass side right'); fig.supylabel('z (in), board top = 0')
    fig.suptitle('Neck sections at frets 1, 5, 9, 12, 17, 22 by profile rule (plain neck law; the heel loft takes over after fret 15)')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'profile_rules_sections.png'), dpi=130); plt.close(fig)
    # 2. curves
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.4)); xs = np.linspace(0, X22, 300); ns = fret_n(np.maximum(xs, 1e-6))
    for r, ls in zip(RULES, ('-', '--', '-', ':')):
        lw = 2.4 if r == REC else 1.3
        D = depth(xs, r); W = width(xs); u0, pb, pt = asym(xs, r)
        A = Phi(0.75, u0, pb, pt) / Phi(-0.75, u0, pb, pt)
        axs[0].plot(ns, D, ls, lw=lw, label=r); axs[1].plot(ns, D / W, ls, lw=lw); axs[2].plot(ns, A, ls, lw=lw)
        axs[3].plot(ns[1:], np.diff(D) / np.diff(ns) * 1000, ls, lw=lw)
    axs[0].axhline(0.82, color='0.8', lw=0.6); axs[0].set_ylabel('centreline depth D (in)'); axs[1].set_ylabel('D / W')
    axs[2].set_ylabel('shoulder ratio bass/treble at |u|=0.75'); axs[3].set_ylabel('dD per fret (thou)')
    for a in axs: a.set_xlabel('fret number'); a.axvspan(15, 22, color='0.93', zorder=0)
    axs[0].legend(); axs[0].text(15.3, 0.83, 'heel loft', color='0.5')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'profile_rules_curves.png'), dpi=130); plt.close(fig)
    # 3. 3-D taper of the recommended rule
    fig = plt.figure(figsize=(12, 6.5)); ax = fig.add_subplot(111, projection='3d')
    xg = np.linspace(0, X17, 70); ug = np.linspace(-1, 1, 61); Xg, Ug = np.meshgrid(xg, ug, indexing='ij')
    Yg = Ug * width(Xg) / 2; Zg = back_z(Xg, Yg)
    ax.plot_surface(Xg, Yg, Zg, color='#c9a46a', alpha=0.55, linewidth=0, rstride=1, cstride=1)
    for j in range(0, 61, 6): ax.plot(Xg[:, j], Yg[:, j], Zg[:, j], color='#6b4f2a', lw=0.5)   # rulings
    for n in FR[:-1]:
        y, z = section_polygon(float(fret_x(n))); ax.plot(np.full_like(y, fret_x(n)), y, z, color='k', lw=1)
    ax.set_box_aspect((X17, 2.3 * 2.2, 1.1 * 2.2)); ax.view_init(-28, -58)
    ax.set_xlabel('x (in)'); ax.set_ylabel('y (in)'); ax.set_zlabel('z (in)')
    ax.set_title('Rule C, seen from below (y, z exaggerated 2.2x): back z = -0.82 R(x)/R(x1) Phi(2y/W(x));\nbrown lines = straight rulings at fixed u; black = sections at frets 1, 5, 9, 12, 17', fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'profile_3d_taper.png'), dpi=130); plt.close(fig)
    # 4. scallop law + wood
    rows = R['wood']; k = [r['cell'] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
    ax[0].plot(k, [r['d'] * 1000 for r in rows], 'o-', label='scallop depth below land (centre)')
    ax[0].plot(k, [r['rose_min'] * 1000 for r in rows], 's-', label='least rosewood left under scallop')
    ax[0].plot(k, [r['rose_ctr'] * 1000 for r in rows], '^-', label='rosewood left at centreline')
    ax[0].axhline(60, color='r', lw=0.8, ls='--'); ax[0].text(1, 63, 'slot depth 0.060 / floor for 0.06 rosewood', color='r', fontsize=7)
    ax[0].set_xlabel('cell (between fret k-1 and k)'); ax[0].set_ylabel('thou'); ax[0].legend(fontsize=7)
    c = R['catch']
    ax[1].plot([r['cell'] for r in c], [r['flat'][0] for r in c], 'k-o', label='unscalloped board')
    ax[1].plot([r['cell'] for r in c], [r['land_'][0] for r in c], 'g-o', label='proposed: full-span S5, d = min(law, 0.15 L^2)')
    ax[1].plot([r['cell'] for r in c], [r['sin2'][0] for r in c], 'r-o', label='full-span sin^2, same depth')
    ax[1].plot([r['cell'] for r in c], [r['rebate'][0] for r in c], 'b--', label='same + 0.010 rebated fret seat')
    ax[1].plot([r['cell'] for r in c], [r['yng'][0] for r in c], 'm:', marker='o', label='S5 at the uncapped linear law (deep top)')
    ax[1].set_xlabel('cell'); ax[1].set_ylabel('fingertip catch (deg, slope jump)'); ax[1].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'scallop_law.png'), dpi=130); plt.close(fig)
    # 5. close-up: longitudinal section through fret 12 with cells 12 and 13
    fig, ax = plt.subplots(figsize=(11, 4.2))
    x12, x11, x13 = (float(fret_x(n)) for n in (12, 11, 13)); xx = np.linspace(x11 - 0.05, x13 + 0.05, 4000)
    zt = -scallop_long(xx); ax.fill_between(xx, -0.20, zt, color='#5a3a22', alpha=0.85, label='rosewood (centreline)')
    ax.fill_between(xx, -0.36, -0.20, color='#e8d2a6', label='maple')
    for xf in (x11, x12, x13):
        t = np.linspace(-0.04, 0.04, 200); ax.fill_between(xf + t, 0, crown_z(t), color='0.65')
        ax.add_patch(plt.Rectangle((xf - P['tang_w'] / 2, -P['tang_d']), P['tang_w'], P['tang_d'], color='0.55'))
        ax.add_patch(plt.Rectangle((xf - P['slot_w'] / 2, -P['slot_d']), P['slot_w'], P['slot_d'], fill=False, ec='w', lw=0.6))
    # sin^2 alternative for cell 13
    L = x13 - x12; f2 = cell_profile(L, 'sin2', float(sc_depth_cell(13)))
    xx2 = np.linspace(0, L, 600); ax.plot(x12 + xx2, np.minimum(f2(xx2), 0), 'r--', lw=1, label='full-span sin^2 (not used)')
    # fingertip at catch position over the land
    R0 = P['finger_R']; f = cell_profile(L, 'land', float(sc_depth_cell(13)))
    xc = x12 + 0.155; qq = np.linspace(-0.3, L + 0.3, 3000); zz = f(qq)
    m = np.abs(qq - 0.155) < R0; zc = (zz[m] + np.sqrt(R0**2 - (qq[m] - 0.155) ** 2)).max()
    th = np.linspace(0, 2 * np.pi, 300); ax.plot(xc + R0 * np.cos(th), zc + R0 * np.sin(th), color='tab:blue', lw=1)
    for i in (0, 5):
        ax.plot(xx, np.full_like(xx, float(string_line(i, x12)[0]) + STR[i][1] / 2), lw=0.8, color='0.3')
    ax.set_xlim(x11 - 0.05, x13 + 0.05); ax.set_ylim(-0.30, 0.22); ax.set_aspect('equal')
    ax.set_title('Fret 12 close-up (x along the neck, centreline): crown 0.080 x 0.043, tang 0.020/0.032 barb x 0.050 in a 0.025 x 0.060 slot;\n'
                 'scallop = full-span S5 trough: zero slope AND curvature at the crown foot; fingertip R 0.30 shown where it meets the crown')
    ax.legend(fontsize=7, loc='lower right', ncol=2); ax.set_xlabel('x (in)'); ax.set_ylabel('z (in)')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'fret_scallop_closeup.png'), dpi=140); plt.close(fig)
    # 6. board edge + domed fret ends
    fig, axs = plt.subplots(2, 2, figsize=(12, 8.2))
    x = float(fret_x(12)); xm = 0.5 * (x + float(fret_x(13))); hw = width(x) / 2; a = float(roll_a(x)); r = P['dome_r']
    for ax, sd, nm_ in ((axs[0, 0], 1, 'bass'), (axs[0, 1], -1, 'treble')):
        yy, zz = section_polygon(x); ax.fill(sd * yy, zz, color='#e8d2a6', ec='#6b4f2a', lw=1, label='section at fret 12 (land)')
        yy2, zz2 = section_polygon(xm); ax.plot(sd * yy2, zz2, color='#6b4f2a', ls='--', lw=1, label='mid-cell 12-13 (scallop)')
        ax.axhline(-P['board_t'], color='0.5', lw=0.6, ls=':'); ax.text(hw - 0.33, -P['board_t'] + 0.005, 'glue line', fontsize=7, color='0.4')
        yap = hw - a; yv = np.linspace(hw - 0.4, yap, 400); base = top_z(x, sd * yv, False)
        hcr = np.where(yv < yap - r, P['crown_h'], P['crown_h'] * np.sqrt(np.clip(1 - ((yv - (yap - r)) / r) ** 2, 0, 1)))
        ax.fill_between(yv, base, base + hcr, color='0.6', label='fret, hemispherical end r 0.040')
        yt = yap - r - 0.01; ys_ = yap - 0.02
        ax.add_patch(plt.Rectangle((hw - 0.4, float(top_z(x, sd * yt, False)) - P['tang_d']), yt - (hw - 0.4), P['tang_d'], color='0.45', label='tang (nipped)'))
        ax.add_patch(plt.Rectangle((hw - 0.4, float(top_z(x, sd * ys_, False)) - P['slot_d']), ys_ - (hw - 0.4), P['slot_d'], fill=False, ec='tab:blue', lw=0.8, label='stopped slot'))
        i = 5 if sd > 0 else 0
        for br, c in (('vintage', 'k'), ('vt1', 'tab:green')):
            ysr = abs(float(string_y(i, x, br))); zsb = float(string_line(i, x, br)[0])
            ax.add_patch(plt.Circle((ysr, zsb + STR[i][1] / 2), STR[i][1] / 2, color=c)); ax.text(ysr + (0.03 if br == 'vintage' else -0.03), zsb + 0.045 + (0.0 if br == 'vintage' else 0.015), br, fontsize=6, ha='center', color=c)
        ax.set_xlim(hw - 0.4, hw + 0.03); ax.set_ylim(-0.42, 0.15); ax.set_aspect('equal'); ax.legend(fontsize=6, loc='lower left')
        ax.set_xlabel(f'|y| (in), {nm_} side'); ax.set_title(f'{nm_.capitalize()} edge, fret 12: roll {a:.3f} across x {float(roll_b_side(x, sd)):.3f} down', fontsize=9)
    ax = axs[1, 0]; yap = hw - a
    for xf in (float(fret_x(12)), float(fret_x(13))):
        yy = np.linspace(hw - 0.35, yap - r, 50); ax.fill_between(yy, xf - 0.04, xf + 0.04, color='0.65')
        th = np.linspace(-np.pi / 2, np.pi / 2, 60); ax.fill(yap - r + r * np.cos(th), xf + 0.04 * np.sin(th), color='0.65')
        ax.add_patch(plt.Rectangle((hw - 0.35, xf - P['slot_w'] / 2), (yap - 0.02) - (hw - 0.35), P['slot_w'], fill=False, ec='tab:blue', lw=0.7))
        ax.plot([hw - 0.35, yap - r - 0.01], [xf, xf], color='0.25', lw=2)
    ax.axvline(hw, color='#6b4f2a', lw=1.5); ax.axvline(hw - a, color='#a0703e', ls='--', lw=0.8); ax.text(hw - a + 0.003, float(fret_x(12)) + 0.3, 'roll starts', rotation=90, fontsize=7)
    for br, c in (('vintage', 'k'), ('vt1', 'tab:green')): ax.axvline(spread(x, br) / 2, color=c, lw=1, label=f'low E string, {br} bridge')
    ax.axvline(hw - a - r, color='tab:red', lw=0.6, ls=':', label='full-height crown ends')
    ax.set_xlim(hw - 0.35, hw + 0.03); ax.set_xlabel('y (in)'); ax.set_ylabel('x (in)'); ax.legend(fontsize=6, loc='center left')
    ax.set_title('Plan, frets 12-13 bass end: dome, stopped slot (blue), nipped tang', fontsize=9)
    ax = axs[1, 1]; xx = np.linspace(float(fret_x(9)) - 0.1, float(fret_x(16)) + 0.1, 3000); hwx = width(xx) / 2; ax_ = roll_a(xx)
    ax.plot(xx, top_z(xx, hwx - ax_), color='#a0703e', label='top where the roll starts')
    ax.plot(xx, top_z(xx, 0.0 * xx), color='0.6', lw=0.8, label='centreline (full scallop)')
    for n in range(9, 17):
        xf = float(fret_x(n)); z0 = float(top_z(xf, width(xf) / 2 - roll_a(xf), False))
        th = np.linspace(0, np.pi, 60); ax.fill(xf + 0.04 * np.cos(th), z0 + P['crown_h'] * np.sin(th), color='0.55')
    ax.set_ylim(-0.12, 0.07); ax.legend(fontsize=7, loc='lower right'); ax.set_xlabel('x (in)'); ax.set_ylabel('z (in)')
    ax.set_title('Side view, bass edge, frets 9-16 (edge scallop 40 % of centre)', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'board_edge_domes.png'), dpi=140); plt.close(fig)
    # 7. headstock + nut
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw=dict(width_ratios=[1.5, 1]))
    ax = axs[0]; hs = HEADSTOCK_STD.copy(); hs[:, 1] *= -1
    ax.fill(hs[:, 0], hs[:, 1], color='#e8d2a6', ec='#6b4f2a'); xs = np.linspace(0, 3, 10)
    ax.fill_between(xs, -width(xs) / 2, width(xs) / 2, color='#5a3a22')
    for (px, py) in posts(True): ax.add_patch(plt.Circle((px, py), P['post_r'], color='0.4'))
    for i in range(6):
        g = nut_geometry(i); k, (px, py) = string_post(i)
        yc = py + (P['post_r'] + STR[i][1] / 2) * np.sign(-py); ax.plot([2.5, 0, px], [string_y(i, 2.5), string_y(i, 0), yc], lw=0.6 + 8 * STR[i][1], color='k')
        ax.text(px, py - 0.25, f"{STR[i][0]}\n{g['theta_nut']:.1f} deg", ha='center', fontsize=7, va='top')
    ax.set_aspect('equal'); ax.set_xlim(-7.6, 2.6); ax.set_title('Reverse headstock (repo outline mirrored); recommended LH set, short posts on E4 B3 G3', fontsize=10)
    ax = axs[1]; nr = R['nut']['table']
    labs = list(nr.keys()); xi = np.arange(6); wdt = 0.8 / len(labs)
    for j, lab in enumerate(labs):
        ax.bar(xi + j * wdt, [nr[lab][i]['theta_nut'] for i in range(6)], wdt, label=lab)
    ax.set_xticks(xi + 0.4 - wdt / 2); ax.set_xticklabels([s[0] for s in STR]); ax.set_ylabel('3-D wrap angle at the nut (deg)')
    ax.legend(fontsize=6); ax.set_title('Nut wrap angle per string')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'headstock_nut.png'), dpi=130); plt.close(fig)
    # 8. saddles vs neck angle
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8)); al = np.linspace(-1.5, 1.5, 31)
    for br, ls in (('vintage', '-'), ('vt1', '--')):
        cr = np.array([[r['crest'] for r in saddle_case(a, br)] for a in al]); be = np.array([[r['total'] for r in saddle_case(a, br)] for a in al])
        for i, c in zip((0, 2, 5), ('tab:blue', 'tab:orange', 'tab:red')):
            axs[0].plot(al, cr[:, i], ls, color=c, label=f'{STR[i][0]} {br}'); axs[1].plot(al, be[:, i], ls, color=c)
    axs[0].axhspan(P['crest_min'], P['crest_max'], color='0.92', zorder=0); axs[0].text(-1.4, P['crest_max'] - 0.02, 'assumed saddle range (measure)', fontsize=7)
    axs[0].set_xlabel('neck angle (deg, + = headstock back)'); axs[0].set_ylabel('saddle crest above plate (in)'); axs[0].legend(fontsize=6, ncol=2)
    axs[1].set_xlabel('neck angle (deg)'); axs[1].set_ylabel('total string deflection at the saddle (deg)')
    for a in axs: a.axvline(R['saddle']['alpha_rec'], color='k', lw=0.6, ls=':')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'saddle_break.png'), dpi=130); plt.close(fig)
    # 9. relief
    fig, ax = plt.subplots(figsize=(7, 3.6)); xx = np.linspace(0, BOARD_END, 400)
    ax.plot(xx, -planed(xx) * 1000, label='planed board top (relief + fall-away)')
    ax.plot(xx, -planed(xx) * 1000 - scallop_long(xx) * 1000 * 0.2, lw=0.5, color='0.6', label='with scallops (x0.2, centreline)')
    ax.plot(xx, (rod_z(xx) + P['board_t']) * 1000 / 10, color='tab:red', label='rod centre below glue line (/10)')
    ax.set_xlabel('x (in)'); ax.set_ylabel('thou'); ax.legend(fontsize=7); ax.axvline(P['x_clamp'], color='0.7', ls=':')
    ax.set_title('Planed relief (sagitta) and curved rod channel; dotted = body clamp x 15.7', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'relief_rod.png'), dpi=130); plt.close(fig)

# ================================================================================================ main
def main():
    R = {}
    R['relief'] = relief_design()
    R['profile'] = profile_table(); R['ruled_dev'] = {r: ruled_check(r) for r in RULES}
    R['wood'], R['frets'] = wood_checks()
    R['catch'] = catch_study()
    T = tensions(-1, 0)
    R['press_sharp'] = [dict(string=STR[i][0], cell=k, p=p, cents=press_sharp_cents(i, p, float(fret_x(k) - fret_x(k - 1)), T[i]))
                        for i in (0, 2) for k in (3, 12) for p in (0.010, 0.020, 0.043, 0.043 + float(sc_depth_cell(k)) * 0.8)]
    # nut options
    tab = {}
    opts = {'flat posts': dict(posts_kind='flat'),
            'LH set, short posts near nut (rec.)': dict(posts_kind='stag_near_short'),
            'LH set, short posts far (bass)': dict(posts_kind='stag_far_short'),
            'rec. + face drop 0.10': dict(posts_kind='stag_near_short', face_drop=0.10),
            'rec. + tree on E/A': dict(posts_kind='stag_near_short', tree='EA')}
    for lab, o in opts.items():
        rows = []
        for i in range(6):
            tr = None
            if o.get('tree') == 'EA' and i >= 4: tr = (-3.0, 0.10)
            kw = {k: v for k, v in o.items() if k != 'tree'}
            g = nut_geometry(i, tree=tr, **kw)
            g['down_lb'] = 2 * T[i] * math.sin(math.radians(g['theta_nut']) / 2)
            g['cents_mu010'] = return_error_cents(i, g, 0.10, T[i]); g['cents_mu025'] = return_error_cents(i, g, 0.25, T[i])
            rows.append(g)
        tab[lab] = rows
    std = [nut_geometry(i, reverse=False, posts_kind='stag_far_short') for i in range(6)]
    for i, g in enumerate(std): g['cents_mu010'] = return_error_cents(i, g, 0.10, T[i]); g['down_lb'] = 2 * T[i] * math.sin(math.radians(g['theta_nut']) / 2)
    tab['standard head, RH staggered (reference)'] = std
    R['nut'] = dict(table=tab)
    # saddles
    a_rec = alpha_for_crest(0.30, 'vintage')
    R['saddle'] = dict(alpha_rec=a_rec, alpha_for_030_vt1=alpha_for_crest(0.30, 'vt1'),
                       vintage={f'{a:+.2f}': saddle_case(a, 'vintage') for a in (0.0, a_rec)},
                       vt1={f'{a:+.2f}': saddle_case(a, 'vt1') for a in (0.0, a_rec)},
                       decked_vintage_rec=saddle_case(a_rec, 'vintage', lift=0.0),
                       H_for_0deg=None)
    # board height that gives the same crest at 0 deg
    lo, hi = 0.0, 0.6
    for _ in range(50):
        mid = 0.5 * (lo + hi); r = saddle_case(0.0, 'vintage', H=mid); m = 0.5 * (r[0]['crest'] + r[5]['crest'])
        lo, hi = (mid, hi) if m < 0.30 else (lo, mid)
    R['saddle']['H_for_0deg'] = 0.5 * (lo + hi)
    R['tongue_drop_per_deg_at_21.7'] = (21.7 - P['x_ref']) * math.tan(math.radians(1.0))
    # acoustics
    R['headstock'] = dict(reverse=headstock_mass(True), standard=headstock_mass(False))
    R['modes'] = dict(plain=neck_modes(False).tolist(), scalloped=neck_modes(True).tolist())
    v = scallop_volume(); R['scallop_removed'] = dict(in3=v, g=v * IN**3 * P['rho_rose'] * 1000)
    R['planed_sag'] = PLANED_SAG[0]
    # spoke wheel packaging
    R['wheel'] = dict(rod_end_x=P['rod_x1'], rod_centre_above_body=P['board_height'] + float(rod_z(P['rod_x1'])),
                      board_end=BOARD_END, neck_pu_route=18.82)
    with open(os.path.join(HERE, 'results.json'), 'w') as fh: json.dump(R, fh, indent=1, default=float)
    figures(R)
    report(R)
    return R

def report(R):
    f = lambda v, n=3: f'{v:.{n}f}'
    print('== profile rules (depth incl. board, width, D/W, apex offset in, shoulder ratio)')
    for r, d in R['profile'].items():
        print(f'-- {r} {RULES[r][0]}  ruled={d["ruled"]} (dev {R["ruled_dev"][r]*1000:.1f} thou)  dD/dx fret1 {d["dDdx_1"]*1000:.1f} -> fret15 {d["dDdx_15"]*1000:.1f} thou/in;'
              f' D at heel-loft start {d["D_heel_x0"]:.3f} vs body {d["body_D_heel_x0"]:.3f}')
        for row in d['rows']:
            print(f'   fret {row["fret"]:2d} D {row["D"]:.3f} W {row["W"]:.3f} D/W {row["DW"]:.3f} apex {row["apex_in"]:.3f} pb {row["pb"]:.2f} pt {row["pt"]:.2f}'
                  f' shoulder b/t {row["sh_bass"]:.3f}/{row["sh_treb"]:.3f} ratio {row["asym"]:.3f}')
    rl = R['relief']
    print(f'== relief: planed sagitta {rl["planed_sag"]:.4f}, planed gap fret1-16 {rl["planed_gap"]:.4f}')
    for nm, row in rl['rows'].items():
        print(f'   {nm:11s} T {row["T"]:.1f} lb  tension bow flat soft/nom/stiff {row["flat_soft"]:.4f}/{row["flat_nom"]:.4f}/{row["flat_stiff"]:.4f}'
              f'  scalloped {row["scal_soft"]:.4f}/{row["scal_nom"]:.4f}/{row["scal_stiff"]:.4f}')
    print(f'   rod must remove {rl["rod_need_in"]:.4f} in; {rl["rod_in_per_100lb"]:.4f} in per 100 lb -> F = {rl["rod_F_lb"]:.0f} lb')
    print('== scallop / wood (cell, depth, least rosewood, centre rosewood, rod top below glue)')
    for r in R['wood']: print(f'   {r["cell"]:2d} x {r["x"]:.2f} d {r["d"]:.3f} rose_min {r["rose_min"]:.3f} ctr {r["rose_ctr"]:.3f} rod_cover {r["rod_top_below_glue"]:.3f}')
    print('== frets: roll_a, keep(vintage), keep(vt1), wood under slot end, board edge t')
    for r in R['frets']:
        if r['fret'] in (1, 5, 9, 12, 15, 17, 19, 21, 22):
            print(f'   {r["fret"]:2d} W {r["width"]:.3f} a {r["roll_a"]:.3f} keep_v {r["keep_vintage"]:.3f} keep_vt1 {r["keep_vt1"]:.3f} slotwood {r["wood_under_slot_end"]:.3f} edge_t {r["edge_board_t"]:.3f}')
    print('== fingertip: catch deg | dip in | max uphill deg | pad on wood at mid   for flat / lands / sin2 / rebate; depth caps (catch <= flat+1 deg)')
    for r in R['catch']:
        fm = lambda t: f'{t[0]:5.1f} {t[1]:.3f} {t[2]:4.1f}{"w" if t[3] else "-"}'
        print(f'   cell {r["cell"]:2d} L {r["L"]:.3f} d {r["d"]:.3f} land {r["land"]:.3f}: {fm(r["flat"])} | {fm(r["land_"])} | {fm(r["sin2"])} | {fm(r["rebate"])}'
              f' | lin d {r["d_lin"]:.3f}: {fm(r["yng"])}  cap_S5 {r["cap_land"]:.3f} cap_sin2 {r["cap_sin2"]:.3f}')
    print('== press-sharp cents'); [print(f'   {r}') for r in R['press_sharp']]
    print('== nut (theta_nut 3-D, vertical, lateral, tree, L behind, down lb, cents mu .10/.25)')
    for lab, rows in R['nut']['table'].items():
        print('  --', lab)
        for i, g in enumerate(rows):
            print(f'   {STR[i][0]} k{g["k"]} th {g["theta_nut"]:.2f} v {g["vert"]:.2f} lat {g["lat"]:.2f} tree {g["theta_tree"]:.2f} L {sum(g["L"]):.2f}'
                  f' down {g.get("down_lb", 0):.2f} cents {g["cents_mu010"]:.2f}/{g.get("cents_mu025", float("nan")):.2f}')
    s = R['saddle']; print(f'== saddles: alpha for 0.30 crest vintage {s["alpha_rec"]:.2f} deg, vt1 {s["alpha_for_030_vt1"]:.2f}; H at 0 deg for 0.30: {s["H_for_0deg"]:.3f}')
    for br in ('vintage', 'vt1'):
        for a, rows in s[br].items():
            print(f'   {br} alpha {a}: ' + '  '.join(f'{r["string"]} c{r["crest"]:.3f} b{r["behind"]:.1f} t{r["total"]:.1f} F{r["down_lb"]:.1f}' for r in rows))
    print('   decked vintage at rec: ' + '  '.join(f'{r["string"]} c{r["crest"]:.3f} t{r["total"]:.1f}' for r in s['decked_vintage_rec']))
    print(f'   tongue drop per degree at 21.7: {R["tongue_drop_per_deg_at_21.7"]:.3f}')
    print('== headstock', json.dumps(R['headstock'], default=lambda v: round(float(v), 3)))
    print('== modes plain / scalloped', [round(v, 1) for v in R['modes']['plain']], [round(v, 1) for v in R['modes']['scalloped']])
    print('== scallop removed', R['scallop_removed'])
    print('== wheel', R['wheel'])

if __name__ == '__main__':
    main()
