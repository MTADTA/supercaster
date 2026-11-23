#!/usr/bin/env python3
"""Supercaster II neck, v4. One standalone model: geometry laws, physics checks, figures, gauges.

Run (one process, under two minutes each):
    python -I -B neck_v4.py calc      -> results.json, interface.json
    python -I -B neck_v4.py fig       -> fig/*.png line figures
    python -I -B neck_v4.py render    -> fig/*.png shaded views
    python -I -B neck_v4.py gauges    -> gauges.pdf
    python -I -B neck_v4.py selftest  -> numerical checks against closed forms

Frame: x from the nut toward the bridge, y positive on the BASS side, z up, z = 0 on the board-top
centreline before scalloping. Inches unless a name ends in _si. Depth figures are WOOD ONLY
(board-top centreline to the deepest point of the back, no frets): assumed, see SPEC.md.
Nothing here imports the earlier neck files.
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, 'fig')
IN = 0.0254
LBF = 4.4482216
PSI_PER_GPA = 145037.7377
G_IN = 386.09

# ----------------------------------------------------------------------------------------------
# Parameters: value, tag, note.  Tags: fixed = owner input, lit = published figure, judged, derived.
# ----------------------------------------------------------------------------------------------
PARAMS = dict(
    scale=(25.5, 'fixed', 'scale length'),
    n_frets=(22, 'fixed', 'frets'),
    w_nut=(1.6875, 'fixed', 'board width at the nut, 1-11/16'),
    w_vintage_nut=(1.650, 'lit', 'vintage nut width that sets the string spacing'),
    w_gain_21=(0.550, 'lit', 'vintage width gain nut to fret 21 (1.650 to 2.200)'),
    r_nut=(7.25, 'fixed', 'board radius at the nut'),
    r_bridge=(9.5, 'fixed', 'board radius at the bridge end of the scale (x = 25.5)'),
    d1=(0.900, 'fixed', 'wood depth at fret 1'),
    d12=(0.960, 'fixed', 'wood depth at fret 12 (earlier choice, kept)'),
    fullness=(0.45, 'judged', 'back exponent m in (1-w^2)^m: 0.50 ellipse, lower is fuller shoulders'),
    eps_nut=(0.08, 'judged', 'asymmetry at the nut: apex offset as a fraction of the half width, + = bass side fuller'),
    x_fade=(None, 'derived', 'asymmetry is zero from here on (fret 15, heel start)'),
    board_t=(0.140, 'judged', 'round-laminate rosewood thickness, uniform, measured on the centreline'),
    fret_h=(0.043, 'lit', 'crown height, Jescar FW43080-S'),
    fret_w=(0.080, 'lit', 'crown width, Jescar FW43080-S'),
    tang_depth=(0.050, 'lit', 'tang depth as transcribed earlier, not re-verified: measure the wire'),
    slot_extra=(0.008, 'judged', 'slot depth beyond the tang for glue'),
    slot_stop=(0.075, 'judged', 'blind slot ends this far from the board side'),
    land=(0.055, 'judged', 'full-height land each side of a fret centreline (crown half width 0.040 + 0.015)'),
    l0=(0.33, 'judged', 'deepest point of a scallop sits this far behind the bridge-side fret (or mid-cell if shorter)'),
    d_nut=(0.030, 'fixed', 'scallop depth under the high E in cell 1'),
    d_peak=(0.055, 'judged', 'largest scallop depth under the high E (earlier law: 0.064)'),
    x_peak=(13.3, 'judged', 'depth reaches d_peak where the deepest point is at this x (cells 13-14)'),
    k_ramp=(0.70, 'judged', 'cap: depth <= k_ramp * (shorter ramp)^2, keeps slide catch at the level of a medium-jumbo fret'),
    tilt=(0.50, 'judged', 'scallop is this fraction shallower at the bass edge than at the treble edge, linear across'),
    roll_drop=(0.110, 'judged', 'B: roll bottom below the nominal board corner, a straight line'),
    af_treble=(0.048, 'judged', 'envelope width at a fret, treble: full crown height starts this far from the side'),
    am_treble=(0.062, 'judged', 'roll width on top between frets, treble'),
    af_bass=(0.058, 'judged', 'envelope width at a fret, bass'),
    am_bass=(0.085, 'judged', 'roll width on top between frets, bass'),
    cap_n=(2.0, 'judged', 'the envelope top stands at crown height on the lands and falls as (1-g)^n into the cell'),
    dress_q=(2.5, 'judged', 'model of the hand-dressed ridge between crown and end face (p-norm blend)'),
    rod_d=(0.1875, 'fixed', 'single-acting rod diameter'),
    rod_x_anchor=(0.80, 'judged', 'fixed anchor centre'),
    rod_z_anchor=(-0.46, 'judged', 'rod axis at the anchor'),
    rod_x_wheel=(18.70, 'judged', 'spoke wheel centre (board ends at 18.594)'),
    rod_z_wheel=(-0.40, 'judged', 'rod axis at the wheel'),
    rod_sag=(0.260, 'judged', 'parabolic sag of the rod axis below the chord between its ends'),
    chan_w=(0.200, 'judged', 'rod channel width (rod + sleeve)'),
    relief_target=(0.012, 'fixed', 'playing relief the owner asked for (or more)'),
    relief_built=(0.009, 'judged', 'relief machined into the board top, gap under a fret 1-17 chord, no load'),
    rod_preload_min=(40.0, 'judged', 'least rod tension that keeps it quiet, lb'),
    x_clamp=(15.6875, 'lit', 'body joint (pocket datum from body/carve): neck treated as fixed from here'),
    nut_clear=(0.020, 'judged', 'string underside above the fret-top plane at the nut'),
    action_12=(0.070, 'judged', 'string underside above fret 12 (plays hard)'),
    bridge_spread=(2.21875, 'lit', 'vintage 2-7/32 E-to-E at the saddles (Vega-Trem VT1: 2.106)'),
    nut_spread=(1.375, 'lit', 'E-to-E at a vintage 1.650 nut'),
    head_face_drop=(0.44, 'judged', 'headstock face below the board-top centreline'),
    head_t=(0.56, 'lit', 'headstock thickness'),
    post_x1=(1.85, 'judged', 'nut face to the nearest post'),
    post_pitch=(0.9375, 'lit', 'post pitch along the tuner row, 15/16'),
    post_hole_tall=(20.0 / 25.4, 'lit', 'Gotoh staggered: base plate to string hole, tall posts'),
    post_hole_short=(18.5 / 25.4, 'lit', 'Gotoh staggered: base plate to string hole, short posts'),
    tuner_mass_g=(28.0, 'lit', 'SD91 MG-T 27 g + bushing'),
    mu_nut=(0.20, 'judged', 'string on polished bone, lightly lubricated (0.10 to 0.30 spans graphite to dry bone)'),
    E_maple=(12.4, 'lit', 'roasted curly maple E_L, GPa (body/acoustics/inputs/wood-properties.json)'),
    rho_maple=(678.0, 'lit', 'kg/m3'),
    G_maple_LR=(1.54, 'lit', 'GPa'),
    G_maple_LT=(0.873, 'lit', 'GPa'),
    E_rw=(13.5, 'lit', 'East Indian rosewood E_L, GPa'),
    rho_rw=(855.0, 'lit', 'kg/m3'),
    G_rw_LR=(1.19, 'lit', 'GPa'),
    G_rw_LT=(0.92, 'lit', 'GPa'),
    rho_steel=(7850.0, 'lit', 'kg/m3'),
    season_strain=(1.0e-4, 'judged', 'seasonal difference in lengthwise strain between rosewood and roasted maple, +/-'),
)
P = {k: v[0] for k, v in PARAMS.items()}

S = P['scale']
NF = P['n_frets']
FX = S * (1 - 2.0 ** (-np.arange(0, NF + 1) / 12.0))      # FX[0] = nut face, FX[n] = fret n
X1, X12, X21, X22 = FX[1], FX[12], FX[21], FX[22]
XH = FX[15]                                              # heel start = asymmetry fade end
P['x_fade'] = float(XH)
X_BOARD_END = X22 + 0.25
XC = P['x_clamp']
HF = P['fret_h']
CW = P['fret_w'] / 2
TB = P['board_t']


def S5(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * t * (10 + t * (-15 + 6 * t))


def width(x):
    return P['w_nut'] + P['w_gain_21'] * np.asarray(x, float) / X21


def width_vintage(x):
    return P['w_vintage_nut'] + P['w_gain_21'] * np.asarray(x, float) / X21


def radius(x):
    return P['r_nut'] + (P['r_bridge'] - P['r_nut']) * np.asarray(x, float) / S


def board(x, y):
    """Unscalloped board top: a cone, radius R(x), z = 0 on the centreline."""
    R = radius(x)
    return -(R - np.sqrt(R * R - np.asarray(y, float) ** 2))


def glue(x, y):
    """Glue surface: the same cone offset down by the board thickness (round laminate)."""
    R = radius(x)
    return -R + np.sqrt((R - TB) ** 2 - np.asarray(y, float) ** 2)


def depth(x):
    return P['d1'] + (P['d12'] - P['d1']) * (np.asarray(x, float) - X1) / (X12 - X1)


def eps(x):
    return P['eps_nut'] * np.clip(1 - np.asarray(x, float) / XH, 0, None)


def shoulder(x):
    """Level where the back curve reaches full width: the glue line at the board edge."""
    return glue(x, width(x) / 2)


def back(x, u, m=None, e=None):
    """Back of the neck at lateral station u = 2y/W in [-1, 1]. ONE rule nut to heel:
    z = z_sh - (D - |z_sh|) * (1 - w^2)^m,  w = u - eps(x) * (1 - u^2)."""
    m = P['fullness'] if m is None else m
    e = eps(x) if e is None else e
    u = np.asarray(u, float)
    w = u - e * (1 - u * u)
    zs = shoulder(x)
    return zs - (depth(x) + zs) * np.clip(1 - w * w, 0, 1) ** m


# ---------------------------------------------------------------------------------- scallop ----
def cell_of(x):
    return np.clip(np.searchsorted(FX, np.asarray(x, float), side='right'), 1, NF)


def cell_geometry(k):
    """Cell k lies between fret k-1 (the nut for k = 1) and fret k."""
    k = np.asarray(k)
    xa, xb = FX[k - 1], FX[k]
    L = xb - xa
    xd = xb - np.minimum(L / 2, P['l0'])
    ramp_b = xb - P['land'] - xd          # bridge-side ramp (the one a slide climbs going up)
    ramp_n = xd - xa - P['land']
    return xa, xb, L, xd, ramp_b, ramp_n


def depth_law():
    k = np.arange(1, NF + 1)
    xa, xb, L, xd, rb, rn = cell_geometry(k)
    wish = P['d_nut'] + (P['d_peak'] - P['d_nut']) * np.clip((xd - cell_geometry(1)[3]) / (P['x_peak'] - cell_geometry(1)[3]), 0, 1)
    cap = P['k_ramp'] * np.minimum(rb, rn) ** 2
    d = np.minimum(wish, cap)
    return np.concatenate([[0.0], d])


DK = depth_law()                       # DK[k] = depth under the high E in cell k


def cell_g(x):
    """Per-cell function g in [0, 1]: 0 on the lands, 1 at the deepest point. Drives scallop AND roll."""
    x = np.asarray(x, float)
    k = cell_of(x)
    xa, xb, L, xd, rb, rn = cell_geometry(k)
    up = (x - xa - P['land']) / rn
    dn = (xb - P['land'] - x) / rb
    g = np.where(x < xd, S5(up), S5(dn))
    return np.where((x <= 0) | (x >= X22), 0.0, g), k


def nearest_fret(x):
    x = np.asarray(x, float)
    k = cell_of(x)
    lo, hi = FX[k - 1], FX[k]
    use_hi = (hi - x) < (x - lo)
    return np.where(use_hi, hi, lo), np.where(use_hi, k, k - 1)


def bump(u):
    return np.clip(1 - u * u, 0, None) ** 2


def fq(t):
    t = np.clip(t, 0.0, 1.0)
    return np.sqrt(np.clip(1 - (1 - t) ** 2, 0, 1))


V4 = dict(name='v4', scallop=True, edge='v4', B=P['roll_drop'], AfT=P['af_treble'], amT=P['am_treble'],
          AfB=P['af_bass'], amB=P['am_bass'], q=P['dress_q'])
# comparison surfaces, used only for the edge-feel and catch metrics
UNIFORM = dict(name='uniform roll + inboard dome', scallop=True, edge='uniform', B=P['roll_drop'], AfT=0.062, amT=0.062,
               AfB=0.085, amB=0.085, q=1.0, dome_len=0.030)
VINTAGE = dict(name='vintage: no scallop, broken corner, 35 deg bevel', scallop=False, edge='vintage', B=0.012,
               AfT=0.012, amT=0.012, AfB=0.012, amB=0.012, q=12.0, bevel=35.0)


def top_field(X, Y, V=V4):
    """Finished top of the neck (wood and steel) as a height field over the board plan.
    Returns z, steel mask, wood height. Valid for |Y| <= W/2."""
    X, Y = np.broadcast_arrays(np.asarray(X, float), np.asarray(Y, float))
    W = width(X)
    land = board(X, Y)
    g, k = cell_g(X)
    dep = DK[k] * g * (1 - P['tilt'] * (Y / W + 0.5)) if V['scallop'] else 0.0
    topw = land - dep
    zb = board(X, W / 2) - V['B']
    xf, nf = nearest_fret(X)
    xi = X - xf
    cap = HF * (1 - g) ** P['cap_n'] if V['edge'] == 'v4' else 0.0
    wood = topw
    defic = []
    with np.errstate(invalid='ignore', over='ignore'):
        for s, Af, am in ((Y + W / 2, V['AfT'], V['amT']), (W / 2 - Y, V['AfB'], V['amB'])):
            A = Af + (am - Af) * g
            t = s / A
            env = np.where(t < 1, zb + (topw + cap - zb) * fq(t), np.inf)
            wood = np.minimum(wood, env)
            if V['edge'] == 'v4':
                e = env - land
            elif V['edge'] == 'uniform':
                e = np.where(s < A, -np.inf, np.where(s < A + V['dome_len'], HF * fq((s - A) / V['dome_len']), np.inf))
            else:
                e = s / math.tan(math.radians(V['bevel']))
            defic.append(np.clip(HF - e, 0, None))
        crown = HF * np.sqrt(np.clip(1 - (xi / CW) ** 2, 0, 1))
        q = V['q']
        d = ((HF - crown) ** q + defic[0] ** q + defic[1] ** q) ** (1 / q)
        zs = land + HF - d
    steel = (np.abs(xi) < CW) & (nf >= 1) & (zs > wood + 1e-7)
    return np.where(steel, zs, wood), steel, wood


# -------------------------------------------------------------------------------------- rod ----
def rod_z(x):
    xa, xw = P['rod_x_anchor'], P['rod_x_wheel']
    t = (np.asarray(x, float) - xa) / (xw - xa)
    return P['rod_z_anchor'] + (P['rod_z_wheel'] - P['rod_z_anchor']) * t - P['rod_sag'] * 4 * t * (1 - t)


def rod_present(x):
    x = np.asarray(x, float)
    return (x >= P['rod_x_anchor']) & (x <= P['rod_x_wheel'])


# ------------------------------------------------------------------------------ section props ----
def section_grid(x, h=0.004, V=V4):
    """Material map of the section at x. Returns y, z (cell centres), maple, rosewood masks."""
    W = float(width(x))
    D = float(depth(x))
    ny = int(round(W / h))
    y = (np.arange(ny) + 0.5) * (W / ny) - W / 2
    z = -np.arange(int((D + 0.02) / h) + 1) * h - h / 2 + 0.0
    z = z[::-1]
    Yg, Zg = np.meshgrid(y, z)
    _, _, wood = top_field(np.full_like(y, x), y, V)
    zg = glue(x, y)
    zbk = back(x, 2 * y / W)
    rw = (Zg <= wood[None, :]) & (Zg > zg[None, :])
    mp = (Zg <= zg[None, :]) & (Zg >= zbk[None, :])
    if rod_present(x):
        zr = float(rod_z(x))
        void = (np.abs(Yg) <= P['chan_w'] / 2) & (np.abs(Zg - zr) <= P['chan_w'] / 2)
        mp &= ~void
    return y, z, Yg, Zg, mp, rw, (W / ny) * h


def section_props(x, h=0.004, V=V4):
    y, z, Yg, Zg, mp, rw, dA = section_grid(x, h, V)
    Em, Er = P['E_maple'] * PSI_PER_GPA, P['E_rw'] * PSI_PER_GPA
    Ew = Em * mp + Er * rw
    EA = Ew.sum() * dA
    zc = (Ew * Zg).sum() * dA / EA
    yc = (Ew * Yg).sum() * dA / EA
    EIv = (Ew * (Zg - zc) ** 2).sum() * dA
    EIl = (Ew * (Yg - yc) ** 2).sum() * dA
    A_m, A_r = mp.sum() * dA, rw.sum() * dA
    rho_m, rho_r = P['rho_maple'], P['rho_rw']
    rod_area = math.pi * P['rod_d'] ** 2 / 4 if rod_present(x) else 0.0
    mu = (A_m * rho_m + A_r * rho_r + rod_area * P['rho_steel']) * IN ** 2      # kg/m
    zcm = ((mp * Zg).sum() * dA * rho_m + (rw * Zg).sum() * dA * rho_r + rod_area * P['rho_steel'] * float(rod_z(x))) * IN ** 2 / mu
    zrc = (rw * Zg).sum() * dA / max(A_r, 1e-12)
    return dict(x=float(x), EA=EA, zc=zc, yc=yc, EIv=EIv, EIl=EIl, A_m=A_m, A_r=A_r, mu=mu, zcm=zcm, zrc=zrc,
                Er_Ar=Er * A_r)


def torsion_GJ(x, h=0.008, V=V4):
    """Saint-Venant torsion of the two-wood section, Prandtl stress function on a grid.
    d/dy((1/Gxz) dphi/dy) + d/dz((1/Gxy) dphi/dz) = -2, phi = 0 on the outline, GJ = 2 * integral(phi).
    Flat-sawn blank assumed: z is radial, y tangential, so Gxz = G_LR and Gxy = G_LT. Returns lb*in^2."""
    from scipy import sparse
    from scipy.sparse.linalg import spsolve
    y, z, Yg, Zg, mp, rw, dA = section_grid(x, h, V)
    hy = y[1] - y[0]
    hz = z[1] - z[0]
    inside = mp | rw
    if rod_present(x):
        zr = float(rod_z(x))
        void = (np.abs(Yg) <= P['chan_w'] / 2) & (np.abs(Zg - zr) <= P['chan_w'] / 2) & (Zg <= glue(x, y)[None, :])
    else:
        void = np.zeros_like(inside)
    solid = inside | void                      # the rod bay is a closed hole: model it as very soft fill
    Gxz = np.where(rw, P['G_rw_LR'], P['G_maple_LR']) * PSI_PER_GPA
    Gxy = np.where(rw, P['G_rw_LT'], P['G_maple_LT']) * PSI_PER_GPA
    Gxz = np.where(void, Gxz * 1e-3, Gxz)
    Gxy = np.where(void, Gxy * 1e-3, Gxy)
    cy, cz = 1 / Gxz, 1 / Gxy
    idx = -np.ones(solid.shape, int)
    idx[solid] = np.arange(solid.sum())
    nz, ny = solid.shape
    rows, cols, vals = [], [], []
    diag = np.zeros(solid.sum())
    I, J = np.nonzero(solid)
    me = idx[I, J]
    for di, dj, c, hh in ((0, 1, cy, hy), (0, -1, cy, hy), (1, 0, cz, hz), (-1, 0, cz, hz)):
        I2, J2 = I + di, J + dj
        ok = (I2 >= 0) & (I2 < nz) & (J2 >= 0) & (J2 < ny)
        nb = np.zeros(len(I), bool)
        nb[ok] = solid[I2[ok], J2[ok]]
        c1 = c[I, J]
        c2 = np.where(nb, c[np.clip(I2, 0, nz - 1), np.clip(J2, 0, ny - 1)], c1)
        cf = 2 * c1 * c2 / (c1 + c2)
        diag += np.where(nb, cf, 2 * c1) / hh ** 2        # outline lies half a cell beyond a boundary cell
        rows.append(me[nb])
        cols.append(idx[I2[nb], J2[nb]])
        vals.append(-cf[nb] / hh ** 2)
    rows.append(me)
    cols.append(me)
    vals.append(diag)
    A = sparse.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))))
    phi = spsolve(A.tocsc(), np.full(len(me), 2.0))
    return 2 * phi.sum() * hy * hz


# ---------------------------------------------------------------------------------- strings ----
PLAIN = 0.22274                                           # lb/in per in^2 of diameter squared, steel
STRINGS = [('E1', 0.0105, 329.63, PLAIN * 0.0105 ** 2), ('B', 0.0135, 246.94, PLAIN * 0.0135 ** 2),
           ('G', 0.017, 196.00, PLAIN * 0.017 ** 2), ('D', 0.026, 146.83, 1.2671e-4),
           ('A', 0.036, 110.00, 2.3964e-4), ('E6', 0.048, 82.41, 4.1382e-4)]


def tensions(semis=-1, drop6=0):
    out = []
    for i, (n, d, f, uw) in enumerate(STRINGS):
        ff = f * 2 ** (semis / 12) * (2 ** (-drop6 / 12) if i == 5 else 1)
        out.append(uw * (2 * S * ff) ** 2 / G_IN)
    return np.array(out)


def string_y(x, spread_bridge=None):
    sb = P['bridge_spread'] if spread_bridge is None else spread_bridge
    yn = np.linspace(-P['nut_spread'] / 2, P['nut_spread'] / 2, 6)
    yb = np.linspace(-sb / 2, sb / 2, 6)
    x = np.asarray(x, float)
    return yn[:, None] + (yb - yn)[:, None] * x[None, :] / S


def string_z(x):
    """String centre height: straight from the nut to the saddle, each string over its own part of the radius."""
    x = np.asarray(x, float)
    ys = string_y(x)
    dia = np.array([s[1] for s in STRINGS])[:, None]
    rise = P['nut_clear'] + (P['action_12'] - P['nut_clear']) * x[None, :] / X12
    return board(x[None, :], ys) + HF + dia / 2 + rise


# ----------------------------------------------------------------------------------- relief ----
_BEAM = {}


def beam(dx=0.05, V=V4, key='v4'):
    if key not in _BEAM:
        xs = np.arange(0.0, XC + 1e-9, dx)
        pr = [section_props(x, V=V) for x in xs]
        _BEAM[key] = (xs, {k: np.array([p[k] for p in pr]) for k in pr[0]})
    return _BEAM[key]


def deflect(xs, kappa):
    """v'' = kappa with v = v' = 0 at the body joint; v > 0 means the nut end rises toward the strings."""
    dxs = np.diff(xs)
    th = np.zeros_like(xs)
    v = np.zeros_like(xs)
    for i in range(len(xs) - 2, -1, -1):
        th[i] = th[i + 1] - 0.5 * (kappa[i] + kappa[i + 1]) * dxs[i]
        v[i] = v[i + 1] - 0.5 * (th[i] + th[i + 1]) * dxs[i]
    return v


def relief_of(xs, v, a=None, b=None):
    """Feeler-gauge relief: largest gap under a straightedge from fret 1 to fret 17 (rigid beyond the joint)."""
    a = X1 if a is None else a
    b = FX[17] if b is None else b
    xx = np.concatenate([xs, [b]]) if b > xs[-1] else xs
    vv = np.concatenate([v, [0.0]]) if b > xs[-1] else v
    va, vb = np.interp(a, xx, vv), np.interp(b, xx, vv)
    m = (xx >= a) & (xx <= b)
    gap = va + (vb - va) * (xx[m] - a) / (b - a) - vv[m]
    i = int(np.argmax(gap))
    return float(gap[i]), float(xx[m][i])


def kappa_strings(T, Escale=1.0):
    xs, B = beam()
    zs = string_z(xs)
    M = (T[:, None] * (zs - B['zc'][None, :])).sum(0)
    return xs, M / (B['EIv'] * Escale)


def kappa_rod(F=1.0, Escale=1.0):
    xs, B = beam()
    e = np.where(rod_present(xs), B['zc'] - rod_z(xs), 0.0)
    return xs, -F * e / (B['EIv'] * Escale)


def kappa_layer_strain(strain, layer='board', Escale=1.0):
    """Curvature from a lengthwise strain mismatch in the board (season) or in its fret-slot layer (tight frets)."""
    xs, B = beam()
    Er = P['E_rw'] * PSI_PER_GPA
    if layer == 'board':
        N = B['Er_Ar'] * strain
        arm = B['zrc'] - B['zc']
    else:
        t = P['tang_depth']
        N = Er * width(xs) * t * strain
        arm = -t / 2 - B['zc']
    return xs, -N * arm / (B['EIv'] * Escale)       # board longer than the maple (strain > 0) -> back bow


def built_in(r0):
    """Board top machined to a constant-curvature arc from the nut to the body joint. Returns kappa0 for a relief r0."""
    xs, _ = beam()
    r1, _ = relief_of(xs, deflect(xs, np.ones_like(xs)))
    return r0 / r1


# ----------------------------------------------------------------------------- slide catch ----
def catch_profile(k, V=V4, tall=None, wide=None, flat=False, xr=None):
    """Board + frets along the high E over cell k and its neighbours, for the rolling-finger metric."""
    x = np.arange(FX[max(k - 2, 0)] - 0.1, FX[min(k + 1, NF)] + 0.1, 0.0005) if xr is None else np.arange(xr[0], xr[1], 0.0005)
    y = string_y(x)[0]
    _, k_all = cell_g(x)
    g, _ = cell_g(x)
    dep = 0.0 if flat else DK[k_all] * g * (1 - P['tilt'] * (y / width(x) + 0.5))
    xf, nf = nearest_fret(x)
    hh = HF if tall is None else tall
    ww = CW if wide is None else wide / 2
    infret = (np.abs(x - xf) < ww) & (nf >= 1)
    crown = hh * np.sqrt(np.clip(1 - ((x - xf) / ww) ** 2, 0, 1))
    return x, np.where(infret, crown, -dep)


def roll_disc(x, p, r):
    """Path of the centre of a disc of radius r rolled over the profile."""
    n = int(r / (x[1] - x[0]))
    off = np.arange(-n, n + 1) * (x[1] - x[0])
    lift = np.sqrt(r * r - off ** 2)
    pp = np.pad(p, n, constant_values=-9)
    win = np.lib.stride_tricks.sliding_window_view(pp, 2 * n + 1)
    return (win + lift[None, :]).max(1)


def catch_angle(k, r=0.30, **kw):
    """Steepest slope of the fingertip path while it crosses fret k (deg): climbing toward the bridge, toward the nut."""
    x, p = catch_profile(k, **kw)
    c = roll_disc(x, p, r)
    s = np.gradient(c, x)
    m = (x > FX[k] - 0.45 * (FX[k] - FX[k - 1]) - 0.05) & (x < FX[k] + 0.3)
    return float(np.degrees(np.arctan(s[m].max()))), float(np.degrees(np.arctan(-s[m].min())))


# ------------------------------------------------------------------------------- edge feel ----
def edge_support(x, side, phi_deg, V=V4, wv=False):
    """Support function of the finished edge in the direction phi above horizontal-outward, measured from the
    nominal sharp board corner. What a flat hand held at that angle rides on. Negative = cut back."""
    x = np.asarray(x, float)
    W = width(x)
    s = np.concatenate([[0.0], 0.14 * (1 - np.cos(np.linspace(0, np.pi / 2, 220)[1:]))])
    X = x[:, None] + 0 * s[None, :]
    Y = (-W[:, None] / 2 + s[None, :]) if side == 'treble' else (W[:, None] / 2 - s[None, :])
    z, steel, wood = top_field(X, Y, V)
    zc = board(x, W / 2)[:, None]
    ph = math.radians(phi_deg)
    sup = -s[None, :] * math.cos(ph) + (z - zc) * math.sin(ph)
    supw = -s[None, :] * math.cos(ph) + (wood - zc) * math.sin(ph)
    return sup.max(1), supw.max(1)


def edge_feel(V, side, phi=45.0, x0=None, x1=None):
    """Numbers for a hand sliding along the edge at the angle phi: long wave, steepest slope of the wood between
    frets, and how far each steel end stands above the wood right beside it."""
    x0 = FX[9] - 0.2 if x0 is None else x0
    x1 = FX[16] + 0.2 if x1 is None else x1
    x = np.arange(x0, x1, 0.001)
    sup, supw = edge_support(x, side, phi, V)
    xf, nf = nearest_fret(x)
    away = np.abs(x - xf) > CW + 0.004
    slope = np.gradient(supw, x)
    steps = []
    for n in range(int(nf.min()) + 1, int(nf.max())):
        m = np.abs(x - FX[n]) < CW
        m2 = (np.abs(x - FX[n]) > CW + 0.004) & (np.abs(x - FX[n]) < CW + 0.012)
        steps.append(float(sup[m].max() - supw[m2].max()))
    return dict(wave=float(sup.max() - sup.min()), wood_wave=float(supw[away].max() - supw[away].min()),
                wood_max_slope_deg=float(np.degrees(np.arctan(np.abs(slope[away]).max()))),
                fret_end_step=float(np.max(steps)))


# ---------------------------------------------------------------------------- slip-off margin ----
def fret_end_profile(n, side, V=V4, drop=0.005):
    """Along the fret centreline: distance from the board side to full crown height and to 'drop' below it."""
    W = float(width(FX[n]))
    s = np.linspace(0, 0.12, 2401)
    y = (-W / 2 + s) if side == 'treble' else (W / 2 - s)
    z, steel, wood = top_field(np.full_like(s, FX[n]), y, V)
    top = board(FX[n], y) + HF
    lost = top - z
    full = float(s[np.argmax(lost < 1e-5)])
    use = float(s[np.argmax(lost < drop)])
    toe = float(s[np.argmax(steel)])
    return dict(full=full, usable=use, toe=toe)


def margins(V=V4):
    out = {}
    for n in (0, 1, 12, 21):
        x = FX[n]
        ys = string_y(np.array([x]))[:, 0]
        row = {}
        for side, yi in (('treble', -ys[0]), ('bass', ys[5])):
            ev4 = float(width(x)) / 2 - yi
            evi = float(width_vintage(x)) / 2 - yi
            if n == 0:
                row[side] = dict(string_to_edge_v4=ev4, string_to_edge_vintage=evi)
                continue
            f4 = fret_end_profile(n, side, V)
            vint_full = HF * math.tan(math.radians(35))
            vint_use = (HF - 0.005) * math.tan(math.radians(35))
            row[side] = dict(string_to_edge_v4=ev4, string_to_edge_vintage=evi,
                             v4_full=ev4 - f4['full'], vintage_full=evi - vint_full,
                             v4_usable=ev4 - f4['usable'], vintage_usable=evi - vint_use,
                             gain_full=(ev4 - f4['full']) - (evi - vint_full),
                             gain_usable=(ev4 - f4['usable']) - (evi - vint_use),
                             steel_toe_from_side=f4['toe'], full_from_side=f4['full'])
        out['nut' if n == 0 else 'fret_%d' % n] = row
    return out


# -------------------------------------------------------------------------- nut and headstock ----
HEAD_OUTLINE = np.array([[0.05, 0.825], [-0.5, 0.9], [-1.2, 1.32], [-2.1, 1.55], [-3.6, 1.6], [-5.2, 1.48], [-6.4, 1.2],
                         [-7.05, 0.75], [-7.3, 0.15], [-7.15, -0.45], [-6.75, -0.78], [-6.1, -0.82], [-5.4, -0.62],
                         [-4.4, -0.42], [-3.2, -0.42], [-2.0, -0.6], [-1.0, -0.84], [-0.4, -0.86], [0.05, -0.825]])
# PLACEHOLDER six-in-line head outline, a rough cartoon used for MASS ONLY (mirrored in y for the reverse head). The
# headstock shape is not designed yet (OPEN-CALCS.md, item 8); this is not it and it is never drawn as the design.


def nut_and_head(face_drop=None, mu=None):
    fd = P['head_face_drop'] if face_drop is None else face_drop
    mu = P['mu_nut'] if mu is None else mu
    T = tensions(-1, 0)
    step_x = math.sqrt(P['post_pitch'] ** 2 - (P['nut_spread'] / 5) ** 2)     # straight pull: one string pitch per post
    rows = []
    for i, (name, dia, f, uw) in enumerate(STRINGS):
        xp = P['post_x1'] + i * step_x                    # reverse head: high E nearest, low E farthest
        hole = (P['post_hole_tall'] if i < 3 else P['post_hole_short']) - P['head_t']
        z_nut = HF + P['nut_clear'] + dia / 2
        z_post = -fd + hole
        th = math.atan((z_nut - z_post) / xp)
        th_total = th + math.atan((P['action_12'] - P['nut_clear']) / X12)      # plus the small rise on the playing side
        down = 2 * T[i] * math.sin(th_total / 2)
        cents = 865.6 * mu * th_total * xp / (S + xp)
        # largest end slope of the open string for a hard pluck 0.15 in off line, one fifth from the saddle
        lift = 0.15 / (0.8 * S)
        rows.append(dict(string=name, post_x=xp, hole_above_face=hole, break_deg=math.degrees(th),
                         downforce_lb=down, seat_margin=th / lift, return_error_cents=cents, tension_lb=float(T[i])))
    # mass
    o = HEAD_OUTLINE * np.array([1, -1])
    xs, ys = o[:, 0], o[:, 1]
    cr = xs * np.roll(ys, -1) - np.roll(xs, -1) * ys
    area = abs(cr.sum()) / 2
    cx = ((xs + np.roll(xs, -1)) * cr).sum() / (3 * cr.sum())
    cy = ((ys + np.roll(ys, -1)) * cr).sum() / (3 * cr.sum())
    m_wood = area * P['head_t'] * IN ** 3 * P['rho_maple']
    posts = [(-(P['post_x1'] + i * step_x), -P['nut_spread'] / 2 + i * P['nut_spread'] / 5) for i in range(6)]
    mt = P['tuner_mass_g'] / 1000
    # tuner bodies hang on the back of the head, 0.3 in toward the treble edge from their posts (judged)
    tun = [(px, py - 0.30, -fd - P['head_t'] - 0.15) for px, py in posts]
    M = m_wood + 6 * mt
    com = [(m_wood * cx + mt * sum(t[0] for t in tun)) / M, (m_wood * cy + mt * sum(t[1] for t in tun)) / M,
           (m_wood * (-fd - P['head_t'] / 2) + mt * sum(t[2] for t in tun)) / M]
    I_nut = m_wood * ((cx * IN) ** 2 + area * IN ** 2 / 6) + mt * sum((t[0] * IN) ** 2 for t in tun)
    return dict(strings=rows, step_x=step_x, row_angle_deg=math.degrees(math.atan2(P['nut_spread'] / 5, step_x)),
                head=dict(area_in2=area, wood_kg=m_wood, tuners_kg=6 * mt, total_kg=M, com_in=com,
                          com_m=[c * IN for c in com], inertia_about_nut_line_kgm2=I_nut,
                          tuner_points_in=tun, post_points_in=posts))


# ----------------------------------------------------------------------------------- checks ----
def wood_checks():
    x = np.arange(P['rod_x_anchor'], XC, 0.05)
    W = width(x)
    zb = np.maximum(back(x, P['chan_w'] / W), back(x, -P['chan_w'] / W))     # the back at the channel corners
    under = (rod_z(x) - P['chan_w'] / 2) - zb
    i = int(np.argmin(under))
    slot = P['tang_depth'] + P['slot_extra']
    span = P['rod_x_wheel'] - P['rod_x_anchor']
    kap = 8 * P['rod_sag'] / span ** 2
    # steel/wood junction on a fret centreline (treble): slope of the envelope where it crosses board level
    Bz, H, A = P['roll_drop'], P['roll_drop'] + HF, P['af_treble']
    c = Bz / H
    toe = A * (1 - math.sqrt(1 - c * c))
    ang = math.degrees(math.atan((H / A) * math.sqrt(1 - c * c) / c))
    return dict(
        under_rod_min=float(under[i]), under_rod_min_x=float(x[i]), rod_depth_max=float(-rod_z(x).min()),
        rod_curvature_per_in=float(kap), rod_bend_stress_psi=float(30e6 * P['rod_d'] / 2 * kap),
        rod_bearing_lb_per_in_at_250lb=float(250 * kap),
        slot_depth=slot, rosewood_under_slot=TB - slot, rosewood_under_deepest_scallop=float(TB - DK.max()),
        roll_bottom_to_glue_line=TB - P['roll_drop'],
        roll_height_at_deepest_scallop_treble=float(P['roll_drop'] - DK.max()),
        slot_end_from_side=P['slot_stop'], steel_toe_from_side_treble=toe, steel_face_angle_at_toe_deg=ang,
        wood_corner_included_angle_at_fret_deg=180 - ang,
        steel_nose_radius_top=float(A * A / H), min_concave_radius_scallop=float(1 / (5.7735 * P['k_ramp'])),
    )


def fit_from_calipers(d_fret1, d_fret12, bass_t=None, treble_t=None, off=0.5, at_fret=1):
    """Re-fit the named profile parameters from a reference neck.
    d_fret1, d_fret12: wood depth on the centreline (frets off, or subtract the fret height).
    bass_t, treble_t: thickness measured square to the board at 'off' inches either side of the centreline at
    'at_fret' (a contour gauge or the printed gauges give the same information). Returns d1, d12, fullness, eps_nut."""
    from scipy.optimize import least_squares
    x = FX[at_fret]
    out = dict(d1=d_fret1, d12=d_fret12)
    if bass_t is None or treble_t is None:
        return out
    save = (P['d1'], P['d12'])
    P['d1'], P['d12'] = d_fret1, d_fret12
    u = 2 * off / float(width(x))

    def res(q):
        m, e0 = q
        e = e0 * (1 - x / XH)
        tb = board(x, off) - back(x, u, m, e)
        tt = board(x, -off) - back(x, -u, m, e)
        return [tb - bass_t, tt - treble_t]
    sol = least_squares(res, [0.45, 0.0], bounds=([0.30, -0.3], [0.70, 0.3]))
    P['d1'], P['d12'] = save
    out.update(fullness=float(sol.x[0]), eps_nut=float(sol.x[1]))
    return out


def selftest():
    # 1. section integrator against a rectangle
    y = np.linspace(-1, 1, 2001)
    print('fret positions 1, 12, 22:', FX[1], FX[12], FX[22])
    # 2. disc metric against the closed form for a step: contact angle = acos((r - h) / r) for a square step
    r, h = 0.30, 0.043
    x = np.arange(-1, 1, 0.0005)
    p = np.where(np.abs(x) < 0.0005, h, 0.0)
    c = roll_disc(x, p, r)
    print('disc on a 0.043 blade: %.2f deg, closed form %.2f' % (np.degrees(np.arctan(np.gradient(c, x).max())),
                                                                   math.degrees(math.acos((r - h) / r))))
    # 3. deflection integrator against a uniform cantilever: tip = kappa L^2 / 2
    xs = np.linspace(0, 10, 201)
    print('cantilever tip %.6f, closed form %.6f' % (deflect(xs, np.full_like(xs, 1e-3))[0], 1e-3 * 100 / 2))
    # 4. torsion solver against an isotropic ellipse: J = pi a^3 b^3 / (a^2 + b^2)
    from scipy import sparse
    from scipy.sparse.linalg import spsolve
    a, b, h = 1.0, 0.45, 0.01
    yy = np.arange(-a + h / 2, a, h)
    zz = np.arange(-b + h / 2, b, h)
    Y, Z = np.meshgrid(yy, zz)
    ins = (Y / a) ** 2 + (Z / b) ** 2 <= 1
    idx = -np.ones(ins.shape, int)
    idx[ins] = np.arange(ins.sum())
    I, J = np.nonzero(ins)
    me = idx[I, J]
    rows, cols, vals = [me], [me], [np.zeros(len(me))]
    diag = np.zeros(len(me))
    for di, dj in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        okb = (I + di >= 0) & (I + di < ins.shape[0]) & (J + dj >= 0) & (J + dj < ins.shape[1])
        nb = okb & ins[np.clip(I + di, 0, ins.shape[0] - 1), np.clip(J + dj, 0, ins.shape[1] - 1)]
        diag += np.where(nb, 1, 2) / h ** 2
        rows.append(me[nb])
        cols.append(idx[I[nb] + di, J[nb] + dj])
        vals.append(-np.ones(nb.sum()) / h ** 2)
    vals[0] = diag
    A = sparse.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))))
    phi = spsolve(A.tocsc(), np.full(len(me), 2.0))
    print('ellipse J %.4f, closed form %.4f' % (2 * phi.sum() * h * h, math.pi * a ** 3 * b ** 3 / (a * a + b * b)))
    # 5. string tension against the published 10-46 E-standard set total (about 103 lb at 25.5 in)
    print('tension Eb std %.1f lb, Eb drop C# %.1f lb, E std %.1f lb' % (tensions(-1).sum(), tensions(-1, 2).sum(), tensions(0).sum()))


# ------------------------------------------------------------------------------------ export ----
def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return [_clean(v) for v in o.tolist()]
    if isinstance(o, (np.floating, float)):
        return round(float(o), 6)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


STATIONS = [('nut', 0.0), ('fret 1', FX[1]), ('fret 5', FX[5]), ('fret 9', FX[9]), ('fret 12', FX[12]),
            ('fret 15', FX[15]), ('fret 17', FX[17])]


def run_calc():
    R = dict(meta=dict(model='Supercaster II neck v4', units='inches, lb, degrees unless stated',
                       frame='x nut to bridge, y + bass, z up, z = 0 board-top centreline',
                       depth_convention='wood only: board-top centreline to the deepest point of the back, no frets (assumed)'))
    R['params'] = {k: dict(value=P[k], tag=v[1], note=v[2]) for k, v in PARAMS.items()}
    R['fret_x'] = FX
    # --- profile law at the gauge stations
    sec = {}
    for name, x in STATIONS:
        W = float(width(x))
        pr = section_props(x)
        u = np.linspace(-1, 1, 4001)
        zb = back(x, u)
        i = int(np.argmin(zb))
        half = np.interp(-0.5, [0, 1], [0, 1])
        zs = float(shoulder(x))
        # width of the back at half its own depth (fullness reading)
        zmid = zs - 0.5 * (float(depth(x)) + zs)
        inside = u[zb <= zmid]
        sec[name] = dict(
            x=x, width=W, depth=float(depth(x)), radius=float(radius(x)), eps=float(eps(x)),
            apex_offset_toward_bass=float(u[i] * W / 2), shoulder_level=zs, edge_drop=float(-board(x, W / 2)),
            thickness_bass_at_0p5=float(board(x, 0.5) - back(x, 1.0 / W)),
            thickness_treble_at_0p5=float(board(x, -0.5) - back(x, -1.0 / W)),
            back_width_at_half_depth=float((inside.max() - inside.min()) * W / 2),
            EI_vertical_lb_in2=pr['EIv'], EI_vertical_N_m2=pr['EIv'] * LBF * IN ** 2,
            neutral_axis_z=pr['zc'], mass_per_length_kg_m=pr['mu'],
            law_note='inside the heel blend: board, edge and width follow the law, the back is the body heel loft'
            if x > XH + 1e-9 else '')
    R['sections'] = sec
    # --- scallop
    cells = []
    for k in range(1, NF + 1):
        xa, xb, L, xd, rb, rn = [float(v) for v in cell_geometry(k)]
        W = float(width(xd))
        ys = string_y(np.array([xd]))[:, 0]
        lat = lambda y: 1 - P['tilt'] * (y / W + 0.5)
        up, dn = catch_angle(k, 0.30)
        cells.append(dict(cell=k, length=L, deepest_x=xd, behind_fret=xb - xd, ramp_bridge=rb, ramp_nut=rn,
                          depth_treble_edge=float(DK[k]), depth_high_E=float(DK[k] * lat(ys[0])),
                          depth_centre=float(DK[k] * lat(0.0)), depth_low_E=float(DK[k] * lat(ys[5])),
                          depth_bass_edge=float(DK[k] * (1 - P['tilt'])),
                          min_concave_radius=float(min(rb, rn) ** 2 / (5.7735 * DK[k])),
                          catch_up_deg=up, catch_down_deg=dn))
    ref = {}
    for r in (0.25, 0.30, 0.40):
        ref['fingertip_r_%.2f' % r] = dict(
            vintage_043x080_flat=catch_angle(8, r, flat=True)[0],
            medium_047x104_flat=catch_angle(8, r, flat=True, tall=0.047, wide=0.104)[0],
            tall_narrow_055x090_flat=catch_angle(8, r, flat=True, tall=0.055, wide=0.090)[0],
            jumbo_058x110_flat=catch_angle(8, r, flat=True, tall=0.058, wide=0.110)[0],
            v4_worst=max(max(catch_angle(k, r)) for k in range(1, NF + 1)))
    # depth options, for the owner trade
    opts = []
    keep = (P['d_peak'], P['k_ramp'])
    for dp, kr in ((0.038, 0.50), (0.055, 0.70), (0.064, 1.00)):
        P['d_peak'], P['k_ramp'] = dp, kr
        DK[:] = depth_law()
        opts.append(dict(d_peak=dp, k_ramp=kr, depth_max=float(DK.max()), depth_cell_22=float(DK[22]),
                         catch_worst_deg=max(max(catch_angle(k, 0.30)) for k in range(1, NF + 1)),
                         rosewood_left=float(TB - DK.max())))
    P['d_peak'], P['k_ramp'] = keep
    DK[:] = depth_law()
    R['scallop'] = dict(cells=cells, catch_reference=ref, depth_options=opts)
    # --- edge
    feel = {}
    for V in (V4, UNIFORM, VINTAGE):
        row = {}
        for side in ('treble', 'bass'):
            row[side] = {('%d_deg' % ph): edge_feel(V, side, ph) for ph in (15, 30, 45, 60)}
            fe = fret_end_profile(12, side, V)
            ys = string_y(np.array([FX[12]]))[:, 0]
            edge = float(width(FX[12])) / 2 - (ys[5] if side == 'bass' else -ys[0])
            if V is VINTAGE:
                edge -= (P['w_nut'] - P['w_vintage_nut']) / 2
            row[side]['fret12_string_to_full_height'] = edge - fe['full']
            row[side]['fret12_string_to_usable'] = edge - fe['usable']
            row[side]['full_height_from_side'] = fe['full']
        feel[V['name']] = row
    R['edge'] = dict(margins=margins(), feel=feel, checks=wood_checks())
    # --- relief and rod
    xs, B = beam()
    T_eb, T_dc, T_e = tensions(-1), tensions(-1, 2), tensions(0)
    rel = {}
    for name, T in (('Eb standard', T_eb), ('Eb drop C#', T_dc), ('E standard', T_e)):
        _, k = kappa_strings(T)
        v = deflect(xs, k)
        r, xr = relief_of(xs, v)
        rel[name] = dict(total_tension_lb=float(T.sum()), relief=r, at_x=xr, nut_rise=float(v[0]),
                         relief_chord_1_to_22=relief_of(xs, v, b=X22)[0])
    _, kr = kappa_rod(100.0)
    eta = relief_of(xs, -deflect(xs, kr))[0] / 100.0
    _, ks = kappa_layer_strain(P['season_strain'])
    season = relief_of(xs, -deflect(xs, ks))[0]
    _, kf = kappa_layer_strain(0.001 * NF / X22, 'slots')
    tight = relief_of(xs, -deflect(xs, kf))[0]
    r_s = rel['Eb standard']['relief']
    tgt = P['relief_target']
    table = []
    for r0 in (0.0, 0.006, 0.009, 0.012):
        slack = r0 + r_s
        F = (slack - tgt) / eta
        table.append(dict(built_in=r0, relief_rod_slack=slack, rod_lb_for_target=F,
                          rod_lb_dry_to_wet=[(slack - season - tgt) / eta, (slack + season - tgt) / eta],
                          most_relief_available_worst_season=slack - season - P['rod_preload_min'] * eta,
                          both_ways_ok=bool((slack - season - tgt) / eta >= P['rod_preload_min'])))
    # rod and wood axial stiffness -> relief per turn of a 10-32 wheel
    span = P['rod_x_wheel'] - P['rod_x_anchor']
    k_rod = 30e6 * math.pi * P['rod_d'] ** 2 / 4 / span
    k_wood = float(np.mean(B['EA'])) / span
    k_sys = 1 / (1 / k_rod + 1 / k_wood)
    e_arm = np.where(rod_present(xs), B['zc'] - rod_z(xs), np.nan)
    R['relief'] = dict(strings=rel, rod_relief_per_100lb=eta * 100, season_swing=season, season_strain=P['season_strain'],
                       tight_fret_backbow_per_0p001_per_fret=tight, stiffness_15pct_changes_string_relief_by=0.15 * r_s,
                       built_in_options=table, chosen_built_in=P['relief_built'], kappa0_per_in=built_in(P['relief_built']),
                       arc_radius_in=1 / built_in(P['relief_built']),
                       nut_lift_of_arc=built_in(P['relief_built']) * XC ** 2 / 2,
                       rod_lb_per_turn_upper_bound=k_sys / 32.0, relief_per_quarter_turn_upper_bound=k_sys / 32.0 / 4 * eta,
                       rod_arm_below_neutral_axis=dict(at_anchor=float(np.nanmin(e_arm[xs < 1.5])), max=float(np.nanmax(e_arm)),
                                                       at_joint=float(e_arm[-1])),
                       rod_thread_stress_psi_at_250lb=250 / 0.0200, anchor_bearing_psi_at_250lb=250 / (math.pi * (0.25 ** 2 - 0.1 ** 2)))
    R['nut_head'] = nut_and_head()
    R['nut_head']['face_drop_options'] = [dict(face_drop=fd, low_E_break_deg=nut_and_head(fd)['strings'][5]['break_deg'],
                                               return_error_cents_low_E=nut_and_head(fd)['strings'][5]['return_error_cents'])
                                          for fd in (0.38, 0.44, 0.50)]
    R['nut_head']['mu_options'] = [dict(mu=m, worst_return_error_cents=max(r['return_error_cents'] for r in nut_and_head(mu=m)['strings']))
                                   for m in (0.05, 0.10, 0.20, 0.30)]
    # --- small derived figures quoted in SPEC.md
    mg = R['edge']['margins']['fret_12']
    toeT, toeB = mg['treble']['steel_toe_from_side'], mg['bass']['steel_toe_from_side']
    tang_clear = 0.005                                           # tang end to slot end, each side
    slack = [o for o in R['relief']['built_in_options'] if o['built_in'] == P['relief_built']][0]['relief_rod_slack']
    per = R['relief']['rod_relief_per_100lb']
    xa = P['rod_x_anchor']
    R['derived'] = dict(
        board_surface_strain_if_bent_to_nut_radius=P['board_t'] / (2 * P['r_nut']),
        board_shrink_before_a_fret_end_stands_proud=dict(nut=2 * toeT / P['w_nut'], fret_12=2 * toeT / float(width(FX[12]))),
        relief_range_average_season=dict(rod_250lb=slack - 2.5 * per, rod_40lb=slack - P['rod_preload_min'] / 100 * per),
        crown_length_is_width_minus=toeT + toeB,
        tang_length_is_width_minus=2 * (P['slot_stop'] + tang_clear),
        tang_nip_from_crown_end=dict(treble=P['slot_stop'] + tang_clear - toeT, bass=P['slot_stop'] + tang_clear - toeB),
        anchor_washer_radius=0.25,
        wood_under_anchor=float(depth(xa)) + P['rod_z_anchor'] - 0.25,
        maple_over_anchor=-(P['rod_z_anchor'] + 0.25) - P['board_t'],
        width_at_joint=float(width(XC)), depth_at_joint=float(depth(XC)), board_end_x=X_BOARD_END,
        frets=[dict(fret=n, x=FX[n], board_width=float(width(FX[n])), crown_length=float(width(FX[n])) - toeT - toeB,
                    tang_length=float(width(FX[n])) - 2 * (P['slot_stop'] + tang_clear)) for n in range(1, NF + 1)])
    with open(os.path.join(HERE, 'results.json'), 'w') as f:
        json.dump(_clean(R), f, indent=1)

    # ------------------------------------------------------------------ interface for the body agent
    segs = []
    bounds = list(FX[:17]) + [XC]
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        xx = np.linspace(a, b, 9)[1:-1] if i > 0 else np.linspace(a + 0.02, b, 9)[:-1]
        pr = [section_props(x) for x in xx]
        hm = lambda key: len(pr) / sum(1 / p[key] for p in pr)
        GJ = torsion_GJ(0.5 * (a + b))
        segs.append(dict(
            cell=i + 1, x0_in=a, x1_in=b, x0_m=a * IN, x1_m=b * IN,
            EI_vertical_Nm2=hm('EIv') * LBF * IN ** 2, EI_lateral_Nm2=hm('EIl') * LBF * IN ** 2,
            GJ_Nm2=GJ * LBF * IN ** 2, EA_N=hm('EA') * LBF,
            mass_per_length_kg_m=float(np.mean([p['mu'] for p in pr])),
            neutral_axis_z_m=float(np.mean([p['zc'] for p in pr])) * IN,
            mass_centre_z_m=float(np.mean([p['zcm'] for p in pr])) * IN,
            area_m2=float(np.mean([p['A_m'] + p['A_r'] for p in pr])) * IN ** 2))
    frets = []
    for n in range(1, NF + 1):
        area = math.pi * CW * HF / 2 + 0.020 * P['tang_depth']
        frets.append(dict(fret=n, x_m=FX[n] * IN, mass_kg=area * (float(width(FX[n])) - 0.06) * IN ** 3 * 7900))
    nh = R['nut_head']['head']
    I = dict(
        meta=dict(what='Supercaster II neck v4, beam description for the body model', units='SI unless a key ends in _in',
                  frame='x from the nut face toward the bridge, y + bass, z up, z = 0 on the board-top centreline',
                  how_built='composite sections integrated on a 0.004 in grid (bending) and a 0.008 in grid (torsion); '
                            'EI and EA are harmonic means over each fret cell so the scallops are included; GJ at mid-cell',
                  validity='neck alone, nut to the body joint. Do not read dead spots from these values without the body.'),
        materials=dict(maple=dict(E_GPa=P['E_maple'], rho=P['rho_maple'], G_LR_GPa=P['G_maple_LR'], G_LT_GPa=P['G_maple_LT'],
                                  loss_factor_L=0.0099, sawn='flat-sawn assumed: z radial, y tangential'),
                       rosewood=dict(E_GPa=P['E_rw'], rho=P['rho_rw'], G_LR_GPa=P['G_rw_LR'], G_LT_GPa=P['G_rw_LT']),
                       uncertainty='E of one blank is +/-15 % of the species figure; scale EI, EA together'),
        segments=segs,
        timoshenko=dict(shear_factor=0.85, G_for_vertical_shear_GPa=P['G_maple_LR'], G_for_lateral_shear_GPa=P['G_maple_LT']),
        frets=frets,
        nut=dict(x_m=-0.0015, mass_kg=0.0013),
        rod=dict(type='single-acting 3/16 in steel, sleeved, in a curved channel under a glued maple spline',
                 mass_per_length_kg_m=math.pi * P['rod_d'] ** 2 / 4 * IN ** 2 * P['rho_steel'], included_in_segments=True,
                 x_anchor_m=P['rod_x_anchor'] * IN, x_wheel_m=P['rod_x_wheel'] * IN,
                 anchor_mass_kg=0.006, wheel_mass_kg=0.012,
                 axis_z_m=[dict(x_m=float(x) * IN, z_m=float(rod_z(x)) * IN) for x in np.linspace(P['rod_x_anchor'], P['rod_x_wheel'], 10)],
                 stiffness_note='the rod is a tendon: it adds axial preload, not bending stiffness; in service 70 to 190 lb'),
        headstock=dict(reverse=True, wood_kg=nh['wood_kg'], tuners_kg=nh['tuners_kg'], total_kg=nh['total_kg'],
                       centre_of_mass_m=nh['com_m'], inertia_about_nut_line_kgm2=nh['inertia_about_nut_line_kgm2'],
                       tuner_points_m=[[c * IN for c in t] for t in nh['tuner_points_in']], tuner_mass_each_kg=P['tuner_mass_g'] / 1000,
                       thickness_m=P['head_t'] * IN, face_below_board_top_m=P['head_face_drop'] * IN,
                       note='outline area from the site model outline, mirrored; +/-10 % on the wood mass'),
        joint=dict(x_m=XC * IN, board_end_x_m=X_BOARD_END * IN, width_at_joint_m=float(width(XC)) * IN,
                   depth_at_joint_m=float(depth(XC)) * IN,
                   note='from the joint on, the section is the body heel loft and tenon: body model owns it'),
        strings=dict(tuning='Eb standard', tension_N=[float(t) * LBF for t in T_eb], total_N=float(T_eb.sum()) * LBF,
                     drop_C_sharp_total_N=float(T_dc.sum()) * LBF),
        damping_notes=[
            'Rod: sleeved and bedded on silicone at three points, never slack below 40 lb, so it cannot buzz against the channel.',
            'Frets: bedded in glue over the whole tang with the crown seated on the land; an unseated fret end is a local loss and a dead note.',
            'Glue lines (board, spline): thin rigid lines (hot hide or Titebond Original); they add no measurable loss if under 0.005 in.',
            'Set-neck joint stiffness and loss belong to the body model; they matter more to sustain than anything in this file.'])
    with open(os.path.join(HERE, 'interface.json'), 'w') as f:
        json.dump(_clean(I), f, indent=1)
    return R


# ----------------------------------------------------------------------------------- figures ----
C_MAPLE, C_SPLINE, C_RW, C_STEEL, C_INK = '#c8935c', '#b9824c', '#4b2d22', '#c4c8ce', '#1c1c1c'


def _plt():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 9, 'font.family': 'DejaVu Sans', 'axes.linewidth': 0.6})
    return plt


def lateral_samples(W, n_edge=160, n_mid=500, s_edge=0.14):
    se = s_edge * (1 - np.cos(np.linspace(0, np.pi / 2, n_edge)))
    mid = np.linspace(-W / 2 + s_edge, W / 2 - s_edge, n_mid)[1:-1]
    return np.concatenate([-W / 2 + se, mid, (W / 2 - se)[::-1]])


def section_outline(x, V=V4):
    W = float(width(x))
    y = lateral_samples(W)
    z, steel, wood = top_field(np.full_like(y, x), y, V)
    u = -np.cos(np.linspace(0, np.pi, 801))
    return dict(W=W, y=y, top=z, steel=steel, wood=wood, glue=glue(x, y), land=board(x, y), yb=u * W / 2, zb=back(x, u))


def draw_section(ax, x, fret=None, strings=True, lw=0.7):
    """Section seen from the nut looking toward the body: bass on the left (horizontal axis is -y)."""
    o = section_outline(x)
    y = -o['y']
    ax.fill(np.concatenate([y, y[::-1]]), np.concatenate([o['glue'], np.interp(o['y'][::-1], o['yb'], o['zb'])]),
            fc=C_MAPLE, ec='none', zorder=1)
    ax.fill(np.concatenate([-o['yb'], y[::-1]]), np.concatenate([o['zb'], o['glue'][::-1]]), fc=C_MAPLE, ec=C_INK, lw=lw, zorder=1)
    ax.fill(np.concatenate([y, y[::-1]]), np.concatenate([o['wood'], o['glue'][::-1]]), fc=C_RW, ec=C_INK, lw=lw, zorder=2)
    if rod_present(x):
        zr, cw = float(rod_z(x)), P['chan_w'] / 2
        ax.fill([-cw, cw, cw, -cw], [glue(x, 0), glue(x, 0), zr - cw, zr - cw], fc=C_SPLINE, ec=C_INK, lw=0.4, zorder=3)
        th = np.linspace(0, 2 * np.pi, 60)
        ax.fill(P['rod_d'] / 2 * np.cos(th), zr + P['rod_d'] / 2 * np.sin(th), fc='#8d9096', ec=C_INK, lw=0.4, zorder=4)
    if fret is not None:
        m = o['steel']
        ax.fill(np.concatenate([y[m], y[m][::-1]]), np.concatenate([o['top'][m], o['land'][m][::-1]]), fc=C_STEEL, ec=C_INK, lw=0.5, zorder=5)
    if strings:
        ys = string_y(np.array([x]))[:, 0]
        zs = string_z(np.array([x]))[:, 0]
        th = np.linspace(0, 2 * np.pi, 40)
        for i in range(6):
            r = STRINGS[i][1] / 2
            ax.fill(-ys[i] + r * np.cos(th), zs[i] + r * np.sin(th), fc='#e8e2c8', ec=C_INK, lw=0.4, zorder=6)
    return o


def fig_sections():
    plt = _plt()
    sts = [('Nut', 0.03, None), ('Fret 1', FX[1], 1), ('Fret 5', FX[5], 5), ('Fret 9', FX[9], 9), ('Fret 12', FX[12], 12),
           ('Fret 15, heel starts', FX[15], 15)]
    fig, axs = plt.subplots(2, 3, figsize=(16.5, 8.6))
    for ax, (name, x, fr) in zip(axs.ravel(), sts):
        o = draw_section(ax, x, fr)
        W, D = o['W'], float(depth(x))
        if fr:
            xd = float(cell_geometry(fr)[3])
            od = section_outline(xd)
            ax.plot(-od['y'], od['wood'] + 0 * (board(x, 0) - board(xd, 0)), color='#f2c14e', lw=0.7, ls=(0, (4, 2)), zorder=7)
        i = int(np.argmin(o['zb']))
        ax.plot([-o['yb'][i]] * 2, [o['zb'][i] - 0.03, o['zb'][i] + 0.10], color='#b0171f', lw=0.8, zorder=8)
        ax.plot([0, 0], [-D - 0.07, 0.16], color='#555', lw=0.4, ls=(0, (6, 3)), zorder=0)
        ax.plot([-1.2, -0.2], [-1.07, -1.07], color=C_INK, lw=1.5)
        ax.text(-0.7, -1.055, '1.000 in', ha='center', va='bottom', fontsize=7.5)
        ax.text(-1.22, 0.22, 'BASS', fontsize=8, color='#555')
        ax.text(1.22, 0.22, 'TREBLE', fontsize=8, color='#555', ha='right')
        ax.set_title('%s:  width %.3f,  depth %.3f,  radius %.2f,  apex %.3f to bass' %
                     (name, W, D, float(radius(x)), o['yb'][i]), fontsize=9.5)
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.12, 0.3)
        ax.set_aspect('equal')
        ax.axis('off')
    fig.suptitle('Supercaster II neck v4: true-shape cross-sections, all at one scale, seen from the nut looking toward the body.\n'
                 'Brown = roasted maple, dark = rosewood (curved glue line), grey = fret and rod, cream = strings at playing height. '
                 'Dashed yellow = board top at the deepest point of the cell behind that fret. Red tick = deepest point of the back.',
                 fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(os.path.join(FIG, 'sections.png'), dpi=170)
    plt.close(fig)


def fig_edge_detail():
    """Board edge at fret 12, enlarged, with the vintage edge drawn over it."""
    plt = _plt()
    n = 12
    x = FX[n]
    xd = float(cell_geometry(n)[3])
    W = float(width(x))
    fig, axs = plt.subplots(1, 2, figsize=(16.5, 7.4))
    for ax, side in zip(axs, ('bass', 'treble')):
        sg = 1 if side == 'bass' else -1
        s = np.concatenate([[0.0], 0.30 * (1 - np.cos(np.linspace(0, np.pi / 2, 900)[1:]))])
        y = sg * (W / 2 - s)
        zc = float(board(x, W / 2))
        z, steel, wood = top_field(np.full_like(s, x), y)
        zg = glue(x, y) - zc
        hx = (lambda a: -a) if side == 'bass' else (lambda a: a)       # outer side faces outward in both panels
        X = hx(-s)
        ax.fill(np.concatenate([X, X[::-1]]), np.concatenate([wood - zc, zg[::-1]]), fc=C_RW, ec=C_INK, lw=0.8, zorder=2)
        ax.fill(np.concatenate([X, X[::-1]]), np.concatenate([zg, np.full_like(s, -0.25)]), fc=C_MAPLE, ec='none', zorder=1)
        ax.plot([hx(0), hx(0)], [zg[0], -0.25], color=C_INK, lw=0.8, zorder=3)
        m = steel
        land = board(x, y) - zc
        ax.fill(np.concatenate([X[m], X[m][::-1]]), np.concatenate([z[m] - zc, land[m][::-1]]), fc=C_STEEL, ec=C_INK, lw=0.8, zorder=4)
        # tang in its blind slot
        st = P['slot_stop']
        mt = s >= st
        ax.fill(np.concatenate([X[mt], X[mt][::-1]]), np.concatenate([land[mt], land[mt][::-1] - P['tang_depth']]),
                fc='#9da1a8', ec=C_INK, lw=0.4, zorder=3)
        ax.plot(np.concatenate([[hx(-st)], X[mt]]), np.concatenate([[land[mt][0]], land[mt] - P['tang_depth'] - P['slot_extra']]),
                color='#e0c9a0', lw=0.6, zorder=3)
        # mid-cell wood (deepest scallop)
        zd, _, wd = top_field(np.full_like(s, xd), sg * (float(width(xd)) / 2 - s))
        ax.plot(X, wd - float(board(xd, float(width(xd)) / 2)), color='#f2c14e', lw=1.2, ls=(0, (5, 2)), zorder=6)
        # string
        ys = string_y(np.array([x]))[:, 0]
        i = 5 if side == 'bass' else 0
        se = W / 2 - abs(ys[i])
        r = STRINGS[i][1] / 2
        th = np.linspace(0, 2 * np.pi, 60)
        zs = float(board(x, ys[i])) - zc + HF + r
        ax.fill(hx(-se) + r * np.cos(th), zs + r * np.sin(th), fc='#e8e2c8', ec=C_INK, lw=0.6, zorder=7)
        ax.text(hx(-se), zs + r + 0.008, '%s string, fretted' % ('low E' if i == 5 else 'high E'), ha='center', fontsize=8)
        # vintage overlay: board side 0.01875 further in, square corner, 35 degree bevel
        off = (P['w_nut'] - P['w_vintage_nut']) / 2
        bz = float(board(x, W / 2 - off)) - zc
        tb = HF * math.tan(math.radians(35))
        sv = np.array([off, off, off + tb, 0.30])
        zv = np.array([-0.25, bz, bz + HF + (float(board(x, W / 2 - off - tb)) - float(board(x, W / 2 - off))), 0])
        zv[3] = float(board(x, W / 2 - 0.30)) - zc + HF
        ax.plot(hx(-sv), zv, color='#1f77b4', lw=1.3, zorder=8)
        ax.plot(hx(-np.array([off, 0.30])), [bz, float(board(x, W / 2 - 0.30)) - zc], color='#1f77b4', lw=0.8, ls=':', zorder=8)
        ax.text(hx(-(off + 0.006)), -0.235, 'vintage neck: side %.3f further in,\n35 deg bevelled fret end' % off, color='#0b3d66', fontsize=8,
                ha='right' if side == 'treble' else 'left', va='bottom')
        fe = fret_end_profile(n, side)
        Af = P['af_bass'] if side == 'bass' else P['af_treble']
        am = P['am_bass'] if side == 'bass' else P['am_treble']

        def dim(a, b, zz, txt, col=C_INK):
            ax.annotate('', xy=(hx(-a), zz), xytext=(hx(-b), zz), arrowprops=dict(arrowstyle='<->', lw=0.7, color=col))
            ax.text(hx(-(a + b) / 2), zz + 0.004, txt, ha='center', fontsize=8, color=col)
        dim(0, fe['full'], 0.105, 'full fret height %.3f from the side' % fe['full'])
        ax.annotate('steel starts %.3f\nfrom the side' % fe['toe'], xy=(hx(-fe['toe']), float(np.interp(fe['toe'], s, land))),
                    xytext=(hx(0.07), 0.045), fontsize=8, ha='center', va='center', arrowprops=dict(arrowstyle='->', lw=0.6))
        dim(fe['full'], se, 0.125, 'string to full-height fret end %.3f  (vintage %.3f)' %
            (se - fe['full'], se - off - tb))
        ax.annotate('', xy=(hx(0.025), 0), xytext=(hx(0.025), -P['roll_drop']), arrowprops=dict(arrowstyle='<->', lw=0.7))
        ax.text(hx(0.07), -P['roll_drop'] / 2, 'roll starts\n%.3f below\nthe corner' % P['roll_drop'], fontsize=8, va='center', ha='center')
        ax.text(hx(-0.20), zg[np.argmin(abs(s - 0.2))] + 0.006, 'glue line, %.3f under the board top' % TB, fontsize=8, color='#f5e9d8',
                ha='center')
        ax.text(hx(-0.215), float(wd[np.argmin(abs(s - 0.2))] - board(xd, float(width(xd)) / 2)) - 0.016,
                'dashed: between frets\n(scallop %.3f here, roll %.3f wide)' % (DK[n] * (1 - P['tilt'] * (0.0 if side == 'treble' else 1.0)), am),
                fontsize=8, color='#f2c14e', ha='center', va='top')
        ax.plot([hx(0)], [0], marker='+', color='#b0171f', ms=9, zorder=9)
        ax.set_title('%s edge at fret %d, enlarged about 30x' % (side.capitalize(), n), fontsize=11)
        ax.set_aspect('equal')
        lo, hi = sorted([hx(0.12), hx(-0.30)])
        ax.set_xlim(lo, hi)
        ax.set_ylim(-0.25, 0.15)
        ax.set_xticks([hx(-v) for v in (0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30)])
        ax.set_xticklabels(['0', '.05', '.10', '.15', '.20', '.25', '.30'])
        ax.set_xlabel('inches in from the board side')
        ax.set_ylabel('inches above the nominal board corner (red +)')
        ax.grid(True, lw=0.25, color='#bbb')
    fig.suptitle('The edge at a fret: the steel end is the crown itself, ground flush into the same curve as the wood below it. '
                 'No filler, no separate dome. Blue = a vintage 1.650 neck with the same string spacing.', fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(FIG, 'edge_detail.png'), dpi=170)
    plt.close(fig)


def fig_relief():
    plt = _plt()
    xs, B = beam()
    fig, axs = plt.subplots(2, 1, figsize=(15, 8.2), gridspec_kw=dict(height_ratios=[1.0, 1.0]))
    ax = axs[0]
    xx = np.linspace(0, X_BOARD_END + 0.3, 800)
    g, k = cell_g(xx)
    top = -DK[k] * g * (1 - P['tilt'] * 0.5)
    ax.fill_between(xx, top, glue(xx, 0), where=xx <= X_BOARD_END, color=C_RW, lw=0)
    ax.fill_between(xx, glue(xx, 0), -depth(xx), color=C_MAPLE, lw=0)
    ax.fill_between(xx, 0.0, -1.08, where=xx >= XC, color='white', alpha=0.45, lw=0)
    ax.text(XC + 0.08, -0.93, 'heel and tenon: shape below the board is on the body drawing', color='#b0171f', fontsize=8)
    xr = np.linspace(P['rod_x_anchor'], P['rod_x_wheel'], 300)
    ax.fill_between(xr, glue(xr, 0), rod_z(xr) + P['rod_d'] / 2, color=C_SPLINE, lw=0)
    ax.fill_between(xr, rod_z(xr) - P['rod_d'] / 2, rod_z(xr) + P['rod_d'] / 2, color='#8d9096', lw=0)
    ax.plot(xs, B['zc'], color='#1f77b4', lw=1.0, ls='--')
    ax.text(3.0, B['zc'][60] + 0.03, 'neutral axis', color='#1f77b4', fontsize=8)
    ax.plot([P['rod_x_anchor']] * 2, [P['rod_z_anchor'] - 0.25, P['rod_z_anchor'] + 0.25], color=C_INK, lw=3)
    ax.text(P['rod_x_anchor'] + 0.1, -0.86, 'fixed anchor', fontsize=8)
    ax.plot([P['rod_x_wheel']] * 2, [P['rod_z_wheel'] - 0.24, P['rod_z_wheel'] + 0.24], color=C_INK, lw=5)
    ax.text(P['rod_x_wheel'] - 0.1, -0.86, 'spoke wheel', fontsize=8, ha='right')
    for n in range(1, NF + 1):
        ax.plot([FX[n]] * 2, [0, HF], color='#777', lw=1.2)
    ax.axvline(XC, color='#b0171f', lw=0.8, ls=':')
    ax.text(XC + 0.08, -1.03, 'body joint', color='#b0171f', fontsize=8)
    w = wood_checks()
    ax.annotate('%.3f maple under the channel' % w['under_rod_min'], xy=(w['under_rod_min_x'], -depth(w['under_rod_min_x']) + 0.07),
                xytext=(9.6, -0.6), fontsize=8, arrowprops=dict(arrowstyle='->', lw=0.6))
    ax.set_aspect(3.0)
    ax.set_xlim(-0.3, 19.6)
    ax.set_ylim(-1.08, 0.12)
    ax.set_title('Centreline section, height drawn 3x. Rod axis is a parabola: %.2f deep at the anchor, %.2f at mid-neck, %.2f at the wheel.'
                 % (-P['rod_z_anchor'], w['rod_depth_max'], -P['rod_z_wheel']), fontsize=10)
    ax.set_ylabel('in')
    ax = axs[1]
    T = tensions(-1)
    _, ks = kappa_strings(T)
    vs = deflect(xs, ks)
    _, kr = kappa_rod(1.0)
    vr = deflect(xs, kr)
    k0 = built_in(P['relief_built'])
    v0 = deflect(xs, np.full_like(xs, k0))
    r_s = relief_of(xs, vs)[0]
    eta = relief_of(xs, -vr)[0]
    Fset = (P['relief_built'] + r_s - P['relief_target']) / eta

    def gap(v):
        xx2 = np.concatenate([xs, [FX[17]]])
        vv = np.concatenate([v, [0.0]])
        va = np.interp(X1, xx2, vv)
        m = xx2 >= X1
        return xx2[m], va + (0 - va) * (xx2[m] - X1) / (FX[17] - X1) - vv[m]
    for v, lab, c, ls in ((vs, 'strings only, board machined flat, rod slack: %.4f' % r_s, '#888', '-'),
                          (v0, 'machined-in relief alone, no strings: %.4f' % P['relief_built'], '#c8935c', '--'),
                          (v0 + vs, 'as built, rod slack: %.4f' % (P['relief_built'] + r_s), '#1f77b4', '-'),
                          (v0 + vs + Fset * vr, 'set point, rod at %.0f lb: %.4f' % (Fset, P['relief_target']), '#b0171f', '-')):
        gx, gg = gap(v)
        ax.plot(gx, gg * 1000, color=c, ls=ls, lw=1.6, label=lab)
    for n in range(1, 18):
        ax.axvline(FX[n], color='#ddd', lw=0.5, zorder=0)
    ax.set_xlim(-0.3, 19.6)
    ax.set_ylim(0, 22)
    ax.set_xlabel('distance from the nut, in (grey lines are frets 1 to 17)')
    ax.set_ylabel('gap under a straightedge on frets 1 and 17, thousandths')
    ax.legend(loc='upper right', fontsize=9, frameon=False, title='Eb standard, 10.5-48: relief at the fret 7-8 feeler point')
    ax.set_title('Relief: the stiff 0.90 neck gives only %.4f from string pull, so %.3f is machined into the board and the rod works in the middle of its range.'
                 % (r_s, P['relief_built']), fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, 'relief_rod.png'), dpi=160)
    plt.close(fig)


def fig_scallop():
    plt = _plt()
    fig = plt.figure(figsize=(15, 11.5))
    gs = fig.add_gridspec(5, 1, height_ratios=[1.3, 1, 1, 1, 1])
    ax = fig.add_subplot(gs[0])
    k = np.arange(1, NF + 1)
    ax.bar(k - 0.27, DK[1:] * 1000, 0.27, color='#4b2d22', label='treble edge / high E')
    ax.bar(k, DK[1:] * (1 - P['tilt'] / 2) * 1000, 0.27, color='#8a5a44', label='centre')
    ax.bar(k + 0.27, DK[1:] * (1 - P['tilt']) * 1000, 0.27, color='#c9a58f', label='bass edge / low E')
    ax.set_xticks(k)
    ax.set_xlabel('cell (cell n is the space behind fret n)')
    ax.set_ylabel('scallop depth, thousandths')
    ax.legend(frameon=False, ncol=3, loc='upper left')
    ax.set_title('Scallop depth law. One rule: depth rises from %.3f to %.3f, capped where the ramps get short (depth <= %.2f x ramp length squared).'
                 % (P['d_nut'], DK.max(), P['k_ramp']), fontsize=10)
    for row, kk in enumerate((2, 8, 13, 20)):
        ax = fig.add_subplot(gs[row + 1])
        x0 = FX[kk - 1] - 0.30
        x, p = catch_profile(kk, xr=(x0 - 0.5, x0 + 2.6))
        ax.fill_between(x, np.minimum(p, 0), -0.1, where=x <= X_BOARD_END, color=C_RW, lw=0)
        xf, nf = nearest_fret(x)
        st = (np.abs(x - xf) < CW) & (nf >= 1)
        ax.fill_between(x, 0, np.where(st, p, 0), where=st, color=C_STEEL, ec=C_INK, lw=0.4)
        c = roll_disc(x, p, 0.30)
        th = np.linspace(0, 2 * np.pi, 400)
        xd = float(cell_geometry(kk)[3])
        sl = np.gradient(c, x)
        mm = (x > xd) & (x < FX[kk])
        i_first = np.nonzero(mm)[0][int(np.argmax(sl[mm]))]
        for xc, col in ((xd, '#1f77b4'), (x[i_first], '#b0171f')):
            zc = np.interp(xc, x, c)
            ax.plot(xc + 0.30 * np.cos(th), zc + 0.30 * np.sin(th), color=col, lw=1.0)
        up, dn = catch_angle(kk, 0.30)
        ax.set_title('Cell %d: %.3f deep under the high E, deepest %.2f behind fret %d. Fingertip climbs fret %d at %.1f deg going up the neck, %.1f deg coming down '
                     '(vintage fret on a flat board %.1f, jumbo %.1f).' % (kk, DK[kk] * (1 - P['tilt'] * (string_y(np.array([xd]))[0, 0] / float(width(xd)) + 0.5)),
                                                                          FX[kk] - xd, kk, kk, up, dn, catch_angle(8, 0.30, flat=True)[0],
                                                                          catch_angle(8, 0.30, flat=True, tall=0.058, wide=0.110)[0]), fontsize=8.5, loc='left')
        ax.set_aspect('equal')
        ax.set_xlim(x0, x0 + 2.05)
        ax.set_ylim(-0.1, 0.16)
        ax.set_yticks([-0.05, 0, 0.05])
        ax.grid(True, lw=0.2)
    fig.suptitle('Scallops along the high E, true proportions. Blue arc: a 0.30 in radius fingertip resting at the deepest point. '
                 'Red arc: the same fingertip where it climbs steepest onto the next fret.', fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(os.path.join(FIG, 'scallop_cells.png'), dpi=160)
    plt.close(fig)


def fig_edge_feel():
    plt = _plt()
    fig, axs = plt.subplots(2, 2, figsize=(15, 8), sharex=True)
    x = np.arange(FX[10] - 0.1, FX[14] + 0.1, 0.001)
    for j, side in enumerate(('bass', 'treble')):
        for i, ph in enumerate((30, 45)):
            ax = axs[i, j]
            for V, c, lab in ((VINTAGE, '#1f77b4', 'vintage edge, 35 deg bevelled ends, no scallop'),
                              (UNIFORM, '#888888', 'uniform heavy roll, dome ends set inboard (loses %.3f of fret)' % (0.092 - 0.048)),
                              (V4, '#b0171f', 'v4: roll breathes, steel end flush')):
                sup, supw = edge_support(x, side, ph, V)
                ax.plot(x, sup * 1000, color=c, lw=1.4, label=lab)
            for n in range(10, 15):
                ax.axvline(FX[n], color='#ddd', lw=0.5, zorder=0)
            ax.set_title('%s edge, hand at %d deg above side-on' % (side.capitalize(), ph), fontsize=10)
            ax.set_ylabel('thousandths (0 = sharp corner)')
            if i == 1:
                ax.set_xlabel('distance from the nut, in (frets 10 to 14)')
            if i == 0 and j == 0:
                ax.legend(frameon=False, fontsize=8.5, loc='lower left')
            ax.set_ylim(-75, 15)
    fig.suptitle('What a hand rides on along the board edge: height of the surface seen from 30 and 45 degrees, frets 10 to 14. '
                 'Peaks are fret ends. A flat line is a featureless edge.', fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(FIG, 'edge_feel.png'), dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------------------------- renderer ----
def _cam(d, up=(0, 0, 1)):
    d = np.array(d, float)
    d /= np.linalg.norm(d)
    f = -d
    r = np.cross(f, np.array(up, float))
    r /= np.linalg.norm(r)
    return r, np.cross(r, f), d


def _unit(v):
    v = np.array(v, float)
    return v / np.linalg.norm(v)


def _patches(xs, res, zones, sides, c_stretch=1.0, back_frac=0.5, c_range=(-1.0, 1.0)):
    """Surface patches of the finished neck over the stations xs: the top (with rolls and frets), then side wall + back."""
    W = width(xs)[:, None]
    s_edge = 0.14
    ne = max(int(0.45 / res), 12)
    se = s_edge * (1 - np.cos(np.linspace(0, np.pi / 2, ne)))
    cols = []
    if 'T' in zones:
        cols.append(-W / 2 + se[None, :])
    if 'C' in zones:
        nc = max(int(1.0 * (c_range[1] - c_range[0]) / (res * c_stretch)), 8)
        cols.append(np.linspace(c_range[0], c_range[1], nc)[None, :] * (W / 2 - s_edge))
    if 'B' in zones:
        cols.append(W / 2 - se[None, ::-1])
    Y = np.concatenate(cols, 1)
    X = xs[:, None] + 0 * Y
    Z, steel, wood = top_field(X, Y)
    yield X, Y, Z, np.where(steel, 1, 0)
    for side in sides:
        sg = -1.0 if side == 'T' else 1.0
        zb = (board(xs, width(xs) / 2) - P['roll_drop'])[:, None]
        zs = shoulder(xs)[:, None]
        t = np.linspace(0, 1, max(int(0.04 / res), 3))[None, :]
        psi = np.linspace(0, np.pi * back_frac, max(int(2.6 * back_frac / res), 8))[None, :]
        u = sg * np.cos(psi)
        Yw = np.concatenate([sg * W / 2 + 0 * t, u * W / 2], 1)
        Zw = np.concatenate([zb + (zs - zb) * t, back(xs[:, None], u)], 1)
        mat = np.concatenate([0 * t + 0 * W, 2 + 0 * psi + 0 * W], 1).astype(int)
        yield xs[:, None] + 0 * Yw, Yw, Zw, mat


def _cap(xe, res):
    """The sawn end of the piece at x = xe, so a cut-off length of neck reads as a solid (rosewood over maple, curved glue line)."""
    W = float(width(xe))
    y = np.linspace(-W / 2, W / 2, int(W / res) + 2)[:, None]
    t = np.linspace(0, 1, int(1.05 / res) + 2)[None, :]
    ztop = top_field(xe + 0 * y, y)[2]
    zbk = back(xe, 2 * y / W)
    Z = zbk + (ztop - zbk) * t
    Y = y + 0 * t
    mat = np.where(Z > glue(xe, Y), 0, 2)
    return xe + 0 * Y, Y, Z, mat


def _grain(a, b, seed, freqs):
    rng = np.random.default_rng(seed)
    out = np.zeros(a.shape, np.float32)
    tot = 0.0
    for f, amp in freqs:
        ph = rng.uniform(0, 6.28)
        k = rng.uniform(0.25, 0.8)
        out += amp * np.sin(f * a + ph + 1.3 * np.sin(k * b + ph)).astype(np.float32)
        tot += amp
    return out / tot


def _shade(X, Y, Z, mat, cam, L1, L2):
    Pt = np.stack([X, Y, Z], -1)
    N = np.cross(np.gradient(Pt, axis=0), np.gradient(Pt, axis=1))
    N /= np.maximum(np.linalg.norm(N, axis=-1, keepdims=True), 1e-12)
    r, u, d = cam
    N = np.where((N @ d)[..., None] < 0, -N, N)
    H1, H2 = _unit(L1 + d), _unit(L2 + d)
    d1 = np.clip(N @ L1, 0, None)
    d2 = np.clip(N @ L2, 0, None)
    s1 = np.clip(N @ H1, 0, None)
    s2 = np.clip(N @ H2, 0, None)
    col = np.zeros(X.shape + (3,), np.float32)
    xf, nf = nearest_fret(X)
    near = np.clip((np.abs(X - xf) - CW) / 0.02, 0, 1)
    ao = np.where((mat == 0) & (nf >= 1), 0.62 + 0.38 * near, 1.0)                # contact shade beside each crown
    for m_id, base, amb, kd1, kd2, ks, sh, gr in (
            (0, (0.36, 0.20, 0.13), 0.22, 0.95, 0.30, 0.30, 35, 0.22),
            (1, (0.74, 0.76, 0.79), 0.30, 0.55, 0.25, 1.00, 70, 0.0),
            (2, (0.86, 0.60, 0.33), 0.24, 0.85, 0.28, 0.18, 22, 0.07)):
        m = mat == m_id
        if not m.any():
            continue
        lum = (amb + kd1 * d1[m] + kd2 * d2[m]) * ao[m]
        if gr:
            lum = lum * (1 + gr * _grain((Y[m] + Z[m]), X[m], 3 + m_id, ((45, .5), (130, .4), (330, .3), (800, .2))))
        spec = ks * (s1[m] ** sh + 0.5 * s2[m] ** sh)
        col[m] = np.clip(lum[:, None] * np.array(base)[None, :] + spec[:, None], 0, 1)
    return Pt, col


def render(x0, x1, d, pix, zones='TCB', sides=('T',), up=(0, 0, 1), c_stretch=1.0, back_frac=0.5, c_range=(-1.0, 1.0),
           L1=(-0.5, -0.3, 0.8), L2=(0.6, 0.2, 0.5), ss=2, pad=0.04, chunk_pts=1.2e6, bg=0.94, caps=False):
    """Orthographic shaded view by point splatting with a depth buffer. Returns image and its extent in view coordinates."""
    cam = _cam(d, up)
    r, u, dd = cam
    L1, L2 = _unit(L1), _unit(L2)
    res = pix / ss * 0.85
    lo, hi = np.array([1e9, 1e9]), -np.array([1e9, 1e9])
    for X, Y, Z, mat in _patches(np.linspace(x0, x1, 40), 0.02, zones, sides, c_stretch, back_frac, c_range):
        Pt = np.stack([X, Y, Z], -1).reshape(-1, 3)
        q = np.stack([Pt @ r, Pt @ u], 1)
        lo, hi = np.minimum(lo, q.min(0)), np.maximum(hi, q.max(0))
    lo, hi = lo - pad, hi + pad
    p = pix / ss
    Wp, Hp = int((hi[0] - lo[0]) / p) // ss * ss, int((hi[1] - lo[1]) / p) // ss * ss
    img = np.full((Hp * Wp, 3), bg, np.float32)
    zbuf = np.full(Hp * Wp, -np.inf, np.float32)
    xs_all = [np.arange(x0, x1, res)]
    nth = int(np.pi * P['fret_h'] / (0.5 * res)) + 8
    for n in range(1, NF + 1):                              # steep crown flanks need their own stations
        if x0 - CW < FX[n] < x1 + CW:
            xs_all.append(FX[n] + CW * np.sin(np.linspace(-np.pi / 2, np.pi / 2, nth)))
    xs_all = np.unique(np.clip(np.concatenate(xs_all), x0, x1))
    per_station = 0.45 / res * ('T' in zones) + 0.45 / res * ('B' in zones) + 2.0 / (res * c_stretch) * ('C' in zones) * (c_range[1] - c_range[0]) / 2 \
        + len(sides) * 2.6 * back_frac / res
    nch = max(int(len(xs_all) * per_station / chunk_pts), 1)
    edges = np.linspace(0, len(xs_all), nch + 1).astype(int)
    for i in range(nch):
        a, b = max(edges[i] - 2, 0), min(edges[i + 1] + 2, len(xs_all))
        xs = xs_all[a:b]
        if len(xs) < 3:
            continue
        plist = list(_patches(xs, res, zones, sides, c_stretch, back_frac, c_range))
        if i == 0 and caps:
            plist += [_cap(xe, res) for xe in (x0, x1)]
        for X, Y, Z, mat in plist:
            Pt, col = _shade(X, Y, Z, mat, cam, L1, L2)
            Pt = Pt.reshape(-1, 3)
            col = col.reshape(-1, 3)
            px = ((Pt @ r - lo[0]) / p).astype(np.int64)
            py = ((hi[1] - Pt @ u) / p).astype(np.int64)
            dep = (Pt @ dd).astype(np.float32)
            ok = (px >= 0) & (px < Wp) & (py >= 0) & (py < Hp)
            idx = (py[ok] * Wp + px[ok])
            dep, col = dep[ok], col[ok]
            o = np.argsort(dep, kind='stable')
            idx, dep, col = idx[o], dep[o], col[o]
            tz = np.full(Hp * Wp, -np.inf, np.float32)
            tz[idx] = dep                                   # last write wins = nearest point of this patch
            win = np.nonzero(tz > zbuf)[0]
            tc = np.zeros((Hp * Wp, 3), np.float32)
            tc[idx] = col
            zbuf[win] = tz[win]
            img[win] = tc[win]
    img = img.reshape(Hp, Wp, 3)
    filled = np.isfinite(zbuf.reshape(Hp, Wp))
    for _ in range(2):                                      # close pin holes between splats
        acc = np.zeros_like(img)
        cnt = np.zeros((Hp, Wp), np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                sh_f = np.roll(np.roll(filled, dy, 0), dx, 1)
                acc += np.roll(np.roll(img, dy, 0), dx, 1) * sh_f[..., None]
                cnt += sh_f
        fix = (~filled) & (cnt >= 5)
        img[fix] = acc[fix] / cnt[fix][:, None]
        filled = filled | fix
    img = img.reshape(Hp // ss, ss, Wp // ss, ss, 3).mean((1, 3))
    return np.clip(img, 0, 1), (lo[0], lo[0] + Wp * p, hi[1] - Hp * p, hi[1])


def _show(ax, img, ext, title=None):
    ax.imshow(img, extent=ext, origin='upper', interpolation='lanczos')
    ax.set_aspect('equal')
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=10, loc='left')


def render_a():
    """3/4 view of four cells, and a close view of the treble edge."""
    plt = _plt()
    for name, cap, kw in (
            ('render_cells.png', 'Cells 12 to 15 (frets 11 to 15) from the treble side and above. Scallops run through both edges;\nthe roll is narrow at '
             'each fret and wide between; fret ends are ground into it. Sawn end shows the curved glue line.',
             dict(x0=FX[11] - 0.12, x1=FX[15] + 0.12, d=(-0.42, -0.55, 0.72), pix=0.0022, back_frac=0.42)),
            ('render_edge_close.png', 'Treble edge at frets 12 and 13, close. The steel end and the rosewood below it are one curve.\nThe faint line where '
             'the roll meets the board top beside each fret is broken by hand in finishing.',
             dict(x0=FX[12] - 0.22, x1=FX[13] + 0.22, d=(-0.35, -0.62, 0.70), pix=0.001, zones='TC', back_frac=0.22, c_range=(-1.0, -0.25)))):
        img, ext = render(sides=('T',), caps=kw.get('zones', 'TCB') == 'TCB', L1=(-0.45, -0.50, 0.74), L2=(0.6, 0.1, 0.6), **kw)
        hh = img.shape[0] / 150
        fig = plt.figure(figsize=(img.shape[1] / 150, hh + 0.62))
        ax = fig.add_axes([0, 0, 1, hh / (hh + 0.62)])
        _show(ax, img, ext)
        fig.text(0.01, 0.99, cap, fontsize=9.5, va='top')
        fig.savefig(os.path.join(FIG, name), dpi=150)
        plt.close(fig)


def render_b():
    """Top view of the fret ends at both edges, frets 11 to 13."""
    plt = _plt()
    x0, x1 = FX[11] - 0.16, FX[13] + 0.16
    fig, axs = plt.subplots(2, 1, figsize=(15, 8.0))
    for ax, side in zip(axs, ('bass', 'treble')):
        z = 'B' if side == 'bass' else 'T'
        cr = (0.62, 1.0) if side == 'bass' else (-1.0, -0.62)
        L = (-0.45, 0.45 if side == 'bass' else -0.45, 0.77)
        img, ext = render(x0, x1, (0, 0, 1), 0.001, zones=z + 'C', sides=(), up=(0, 1, 0), c_range=cr, L1=L, L2=(0.5, 0.0, 0.85), pad=0.02)
        _show(ax, img, ext)
        xx = np.linspace(x0, x1, 200)
        sg = 1 if side == 'bass' else -1
        ys = string_y(xx)[5 if side == 'bass' else 0]
        ax.plot(xx, ys, color='#f6efcf', lw=1.0, ls=(0, (6, 3)))
        ax.text(x0 + 0.02, ys[0] - sg * 0.012, 'low E string' if side == 'bass' else 'high E string', color='#f6efcf', fontsize=8,
                va='top' if side == 'bass' else 'bottom')
        ax.plot(xx, sg * width(xx) / 2, color='#b0171f', lw=0.7)
        fe = fret_end_profile(12, side)
        xa = FX[12]
        ye = sg * float(width(xa)) / 2
        for sv, lab, dxl in ((fe['toe'], 'steel starts %.3f in' % fe['toe'], 0.07), (fe['full'], 'full height %.3f in' % fe['full'], 0.07)):
            ax.annotate(lab, xy=(xa, ye - sg * sv), xytext=(xa + dxl, ye - sg * (sv + 0.012) + sg * 0.0), color='white', fontsize=8, va='center',
                        arrowprops=dict(arrowstyle='->', lw=0.6, color='white'))
        am = P['am_bass'] if side == 'bass' else P['am_treble']
        xd = float(cell_geometry(13)[3])
        ax.annotate('roll is %.3f wide here' % am, xy=(xd, sg * (float(width(xd)) / 2 - am)), xytext=(xd - 0.03, sg * (float(width(xd)) / 2 - am - 0.115)),
                    color='white', fontsize=8, ha='center', arrowprops=dict(arrowstyle='->', lw=0.6, color='white'))
        ax.set_title('%s edge from directly above, frets 11, 12, 13. Red line = board side. Light from the %s.' % (side.capitalize(), 'nut end, outside'),
                     fontsize=10, loc='left')
    fig.suptitle('Top view of the fret ends (about 8x). Each crown runs out to within 0.015 to 0.018 of the board side and is rounded off inside its own width.',
                 fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(os.path.join(FIG, 'fret_ends_top.png'), dpi=170)
    plt.close(fig)


def render_c(which='T'):
    """Board edge in side view, frets 9 to 16: true side elevation, 30 degrees above it, and a dimensioned line view."""
    plt = _plt()
    side = 'treble' if which == 'T' else 'bass'
    sg = -1.0 if which == 'T' else 1.0
    x0, x1 = FX[9] - 0.12, FX[16] + 0.12
    zc = 'TC' if which == 'T' else 'CB'
    cr = (-1.0, 0.0) if which == 'T' else (0.0, 1.0)
    img0, e0 = render(x0, x1, (0, sg, 0), 0.002, zones=zc, sides=(which,), c_stretch=6.0, back_frac=0.20, c_range=cr,
                      L1=(-0.35, sg * 0.55, 0.76), L2=(0.5, sg * 0.3, 0.6), pad=0.03)
    img1, e1 = render(x0, x1, (0, sg * math.cos(math.radians(30)), math.sin(math.radians(30))), 0.0025, zones='TCB', sides=(which,), c_stretch=2.0,
                      back_frac=0.20, L1=(-0.35, sg * 0.45, 0.82), L2=(0.5, sg * 0.3, 0.6), pad=0.03)
    if which == 'B':                       # show both edges nut-left so they can be compared; say so in the title
        img0, img1 = img0[:, ::-1], img1[:, ::-1]
        e0 = (-e0[1], -e0[0], e0[2], e0[3])
        e1 = (-e1[1], -e1[0], e1[2], e1[3])
    fig = plt.figure(figsize=(17, 9.2))
    h0 = (e0[3] - e0[2])
    h1 = (e1[3] - e1[2])
    gs = fig.add_gridspec(3, 1, height_ratios=[h0, h1, 1.15])
    ax = fig.add_subplot(gs[0])
    _show(ax, img0, e0, '%s edge, true side elevation, frets 9 to 16, nut to the left%s. True proportions.' %
          (side.capitalize(), ' (image mirrored)' if which == 'B' else ''))
    ax = fig.add_subplot(gs[1])
    _show(ax, img1, e1, 'The same edge seen from 30 degrees above side-on.')
    ax = fig.add_subplot(gs[2])
    x = np.arange(x0, x1, 0.002)
    W = width(x)
    s = np.concatenate([[0.0], 0.14 * (1 - np.cos(np.linspace(0, np.pi / 2, 300)[1:]))])
    X = x[:, None] + 0 * s[None, :]
    Y = sg * (W[:, None] / 2 - s[None, :])
    z, steel, wood = top_field(X, Y)
    zcn = board(x, W / 2)
    g, k = cell_g(x)
    topw = board(X, Y) - DK[k][:, None] * g[:, None] * (1 - P['tilt'] * (Y / W[:, None] + 0.5))
    on_roll = wood < topw - 1e-6
    j = np.argmin(on_roll, axis=1)                      # first sample where the roll has met the top
    ztop = wood[np.arange(len(x)), j] - zcn
    zsteel = np.where(steel, z, -9).max(1) - zcn
    zsteel = np.where(steel.any(1), zsteel, np.nan)
    ax.fill_between(x, -P['roll_drop'], ztop, color='#6b4334', lw=0, label='roll (rosewood)')
    ax.fill_between(x, -TB * 1.004, -P['roll_drop'], color=C_RW, lw=0, label='flat side wall, %.3f' % (TB - P['roll_drop']))
    ax.fill_between(x, -0.2, -TB * 1.004, color=C_MAPLE, lw=0)
    ax.fill_between(x, ztop, zsteel, where=np.isfinite(zsteel), color=C_STEEL, ec=C_INK, lw=0.4, label='fret end (steel)')
    ax.plot(x, ztop, color='#f2c14e', lw=1.0, label='where the roll meets the board top')
    ax.axhline(0, color='#b0171f', lw=0.6, ls=':')
    ax.text(x0 + 0.02, 0.004, 'nominal board corner', color='#b0171f', fontsize=8)
    ax.text(x0 + 0.02, -TB - 0.022, 'maple', fontsize=8)
    for n in range(9, 17):
        ax.text(FX[n], 0.062, str(n), ha='center', fontsize=8)
    ax.set_aspect(4.0)
    ax.set_xlim(e0[0], e0[1])
    ax.set_ylim(-0.2, 0.08)
    ax.set_ylabel('in (height drawn 4x)')
    ax.set_xlabel('distance from the nut, in')
    ax.legend(frameon=False, ncol=4, fontsize=8, loc='lower right')
    ax.set_title('Dimensioned side view, height drawn 4x: straight roll bottom %.3f below the corner, straight glue line %.3f, board top dips %.3f to %.3f between frets.'
                 % (P['roll_drop'], TB, np.nanmin(-ztop[(x > FX[15]) & (x < FX[16])].min()), -ztop.min()), fontsize=10, loc='left')
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, 'edge_side_%s.png' % side), dpi=160)
    plt.close(fig)


# ------------------------------------------------------------------------------------ gauges ----
def run_gauges():
    """1:1 contour gauges, US Letter, one page. Print at 100 % (no fit-to-page) and check the scale bars."""
    plt = _plt()
    from matplotlib.backends.backend_pdf import PdfPages
    sts = [('NUT', 0.0), ('FRET 1', FX[1]), ('FRET 5', FX[5]), ('FRET 9', FX[9]), ('FRET 12', FX[12]), ('FRET 17', FX[17])]
    with PdfPages(os.path.join(HERE, 'gauges.pdf')) as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 8.5)
        ax.set_ylim(0, 11)
        ax.axis('off')
        ax.text(0.5, 10.62, 'Supercaster II neck v4: back-contour gauges, full size', fontsize=12, weight='bold')
        ax.text(0.5, 10.44, 'Print at 100 % (no scaling) on US Letter. Check both scale bars with calipers before cutting. Cut on the heavy line; '
                'the gauge is the shaded card.', fontsize=7)
        ax.text(0.5, 10.31, 'Each card is seen from the nut looking toward the body, so BASS is on the left. The straight legs touch the neck sides and end '
                'level with the two board corners', fontsize=7)
        ax.text(0.5, 10.18, '(before the edge is rolled; after rolling, the last 0.11 of each leg stands clear by design). Depths are wood only: no frets, '
                'no finish.', fontsize=7)
        cw, ch = 3.55, 2.72
        for i, (name, x) in enumerate(sts):
            cx = 0.55 + (i % 2) * (cw + 0.3) + cw / 2
            top = 9.92 - (i // 2) * (ch + 0.22)
            W, D = float(width(x)), float(depth(x))
            zc = float(board(x, W / 2))                          # card top = board corner level
            u = -np.cos(np.linspace(0, np.pi, 1201))             # treble (u = -1) to bass (u = +1)
            ys, zb = -u * W / 2, back(x, u) - zc                 # screen x = -y: treble on the right, bass on the left
            px = np.concatenate([[W / 2], ys, [-W / 2]])         # treble corner, down the side, round the back, up to the bass corner
            pz = np.concatenate([[0.0], zb, [0.0]])
            ax.fill(np.concatenate([[cx - cw / 2, cx - cw / 2, cx + cw / 2, cx + cw / 2], cx + px]),
                    np.concatenate([[top, top - ch, top - ch, top], top + pz]), fc='#e9e9e9', ec='none')
            ax.plot([cx + W / 2, cx + cw / 2, cx + cw / 2, cx - cw / 2, cx - cw / 2, cx - W / 2], [top, top, top - ch, top - ch, top, top], color='k', lw=0.5)
            ax.plot(cx + px, top + pz, color='k', lw=1.1)
            yy = np.linspace(-W / 2, W / 2, 200)                 # the board above the card, for reference only
            ax.plot(cx - yy, top + board(x, yy) - zc, color='#777', lw=0.5, ls=(0, (3, 2)))
            ax.plot([cx, cx], [top + 0.10, top - D - zc - 0.10], color='#777', lw=0.4, ls=(0, (6, 2, 1, 2)))
            i_ap = int(np.argmin(zb))
            ax.plot([cx + ys[i_ap]] * 2, [top + zb[i_ap] - 0.07, top + zb[i_ap]], color='k', lw=0.7)
            ax.text(cx - cw / 2 + 0.08, top - 0.18, 'BASS', fontsize=7)
            ax.text(cx + cw / 2 - 0.08, top - 0.18, 'TREBLE', fontsize=7, ha='right')
            ax.text(cx, top - ch + 0.52, name, fontsize=11, weight='bold', ha='center')
            ax.text(cx, top - ch + 0.38, '%.3f in from the nut.  Width %.3f.  Depth %.3f at the deepest point.' % (x, W, D), fontsize=6.5, ha='center')
            ax.text(cx, top - ch + 0.26, 'Board corners are %.3f below the board crown; cut-out %.3f deep at the tick.' % (-zc, D + zc),
                    fontsize=6.2, ha='center')
            ap = -ys[i_ap]
            ax.text(cx, top - ch + 0.15, ('Tick = deepest point, %.3f toward the bass side of centre (chain line).' % ap) if ap > 5e-4
                    else 'Tick = deepest point, on the centre line.', fontsize=6.2, ha='center')
            if x > XH:
                ax.text(cx, top - ch + 0.04, 'Inside the heel: neck law carried on, for reference only.',
                        fontsize=5.8, ha='center')
        # scale bars
        y0 = 0.70
        ax.plot([0.75, 6.75], [y0, y0], color='k', lw=0.8)
        for t in range(0, 49):
            h = 0.12 if t % 8 == 0 else (0.08 if t % 4 == 0 else 0.05)
            ax.plot([0.75 + t / 8] * 2, [y0, y0 + h], color='k', lw=0.5)
            if t % 8 == 0:
                ax.text(0.75 + t / 8, y0 + 0.15, '%d' % (t // 8), fontsize=7, ha='center')
        ax.text(6.9, y0 + 0.03, 'inches:\nmust be 6.000', fontsize=6.5, va='center')
        y1 = 0.36
        ax.plot([0.75, 0.75 + 150 / 25.4], [y1, y1], color='k', lw=0.8)
        for t in range(0, 151, 5):
            h = 0.12 if t % 50 == 0 else (0.08 if t % 10 == 0 else 0.05)
            ax.plot([0.75 + t / 25.4] * 2, [y1, y1 + h], color='k', lw=0.5)
            if t % 50 == 0:
                ax.text(0.75 + t / 25.4, y1 - 0.12, '%d' % t, fontsize=7, ha='center')
        ax.text(6.9, y1 + 0.03, 'mm:\nmust be 150.0', fontsize=6.5, va='center')
        pdf.savefig(fig)
        plt.close(fig)


def run_fig():
    os.makedirs(FIG, exist_ok=True)
    fig_sections()
    fig_edge_detail()
    fig_relief()
    fig_scallop()
    fig_edge_feel()


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'calc'
    t0 = time.time()
    if cmd == 'selftest':
        selftest()
    elif cmd == 'calc':
        run_calc()
    elif cmd == 'fig':
        run_fig()
    elif cmd == 'render':
        os.makedirs(FIG, exist_ok=True)
        part = sys.argv[2] if len(sys.argv) > 2 else 'a'
        dict(a=render_a, b=render_b, cT=lambda: render_c('T'), cB=lambda: render_c('B'))[part]()
    elif cmd == 'gauges':
        run_gauges()
    print('%s done in %.1f s' % (cmd, time.time() - t0))
