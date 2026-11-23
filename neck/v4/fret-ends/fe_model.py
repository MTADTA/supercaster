#!/usr/bin/env python3
"""Supercaster II fret ends: geometry of every candidate end and the wood edge around it.

Reads the v4 model (neck_v4.py) without changing it. Everything here is a proposal.

Frame: as neck_v4 (x from the nut, y + on the bass side, z up). Near an edge the working coordinates are
    s = distance in from the board side (the side wall is s = 0)
    z = height above the nominal sharp board corner at that station.
Inches throughout.

Run:  python -I -B fe_model.py        -> prints the geometry checks, writes geometry.json
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import neck_v4 as n4  # noqa: E402  (read only)

HF, CW, FX, NF = n4.HF, n4.CW, n4.FX, n4.NF
P = n4.P

# ------------------------------------------------------------------------------------------------
# Candidates.  kind 'n4' = a surface defined by neck_v4.top_field; kind 'dome' = defined here.
#   t0   steel toe, from the board side          a   length of the rounded end along the fret
#   Af   roll width on top at the fret centre     am  roll width between frets
#   Bf   roll height at the fret centre           Bm  roll height between frets (v4: 0.110)
#   sig  half-length of the wood nose that carries the end (bell width along the neck)
#   plat the nose stays at full height this far each side of the fret centreline before the bell starts
#   dish fraction of the scallop depth recovered at the board side: the floor rises from under the outer
#        string to the side on a parabola (0 = the scallop runs out through the edge, as v4)
#   cheek  height of a raised wood bolster outboard of the toe (the "pocket" idea), 0 = none
# ------------------------------------------------------------------------------------------------
R_CUP = 0.040          # radius the forming cutter leaves; equal to the crown half width

S_DISH = 0.140        # the dish is centred this far in from the side: under the outer strings


def dome(name, t0T, aT, t0B=None, aB=None, amT=0.062, amB=0.085, sig=0.080, dish=0.0, cheek=0.0, uniform=False,
         plat=0.0, label=None):
    t0B = t0T if t0B is None else t0B
    aB = aT if aB is None else aB
    return dict(kind='dome', name=name, label=label or name, t0=dict(T=t0T, B=t0B), a=dict(T=aT, B=aB),
                am=dict(T=amT, B=amB), sig=sig, dish=dish, cheek=cheek, uniform=uniform, plat=plat, Bm=P['roll_drop'])


CANDS = {
    'vintage': dict(kind='n4', name='vintage', label='Vintage: 35 deg bevel, flush', V=n4.VINTAGE),
    'v4': dict(kind='n4', name='v4', label='v4: 72 deg face, rounded ridge', V=n4.V4),
    'uniform': dict(kind='n4', name='uniform', label='Uniform heavy roll, dome set inboard', V=n4.UNIFORM),
    # the owner's request, at the same bending room as v4 and a vintage neck
    'bullet': dome('bullet', 0.010, 0.040, label='Full quarter-sphere, R 0.040, toe at 0.010'),
    # less-than-full roundover: same full-height point, shorter and steeper
    'short': dome('short', 0.024, 0.026, label='Short dome 0.026 long, toe at 0.024'),
    'mid': dome('mid', 0.016, 0.034, label='Three-quarter dome 0.034 long, toe at 0.016'),
    # longer and softer: gives away fret
    'long': dome('long', 0.010, 0.052, label='Long dome 0.052, toe at 0.010 (costs 0.012)'),
    # the pocket idea in the only form that can be cut: a raised bolster of wood outboard of the toe
    'pocket': dome('pocket', 0.014, 0.040, cheek=0.012, label='Quarter-sphere nested in a raised wood bolster'),
    # design variants used to choose the nose: a longer full-height nose, and the toe set further in
    'bullet_plat': dome('bullet_plat', 0.010, 0.040, plat=0.045, label='Quarter-sphere, nose held full 0.045 each side'),
    'bullet_t016': dome('bullet_t016', 0.016, 0.040, label='Quarter-sphere, toe at 0.016 (costs 0.006)'),
    'mid_d': dome('mid_d', 0.016, 0.034, dish=0.8, label='Three-quarter dome, dished run-out'),
    'bullet_tight': dome('bullet_tight', 0.010, 0.040, dish=1.0, amT=0.045, amB=0.060, label='Quarter-sphere, full dish, tighter roll'),
    # recommended: quarter-sphere on a wrapped wood nose, scallop dished up to the side
    'rec': dome('rec', 0.010, 0.040, dish=1.0, sig=0.100, label='Recommended: quarter-sphere on a wrapped nose, dished run-out'),
    'rec_d08': dome('rec_d08', 0.010, 0.040, dish=0.8, sig=0.100, label='As recommended, dish 0.8'),
    # fallback: the same wood, the end rounded by hand with files to a three-quarter dome
    'fallback': dome('fallback', 0.016, 0.034, dish=1.0, sig=0.100, label='Fallback: hand-filed three-quarter dome, same wood'),
}


def side_y(x, s, side):
    W = n4.width(x)
    return (-W / 2 + s) if side == 'T' else (W / 2 - s)


def corner_z(x):
    return n4.board(x, n4.width(x) / 2)


def bell(x, sig, plat=0.0):
    """1 between frets, 0 at each fret centreline (and at the nut): where the wood nose stands."""
    xf, nf = n4.nearest_fret(x)
    d = np.clip(np.abs(np.asarray(x, float) - xf) - plat, 0, None)
    return 1.0 - np.exp(-(d / sig) ** 2)


def scallop_dep(x, y, dish=0.0, s=None):
    g, k = n4.cell_g(x)
    W = n4.width(x)
    dep = n4.DK[k] * g * (1 - P['tilt'] * (y / W + 0.5))
    if dish:
        dep = dep * (1 - dish * (np.clip(S_DISH - s, 0, None) / S_DISH) ** 2)
    return dep


def dome_parts(x, s, side, c, steel_shift=0.0):
    """Wood height, steel height (nan where no steel), both absolute z. steel_shift > 0 moves the steel toward
    the side relative to the wood (a dry board, or a fret placed outboard)."""
    x, s = np.broadcast_arrays(np.asarray(x, float), np.asarray(s, float))
    y = side_y(x, s, side)
    land = n4.board(x, y)
    topw = land - scallop_dep(x, y, c['dish'], s)
    t0, a, am = c['t0'][side], c['a'][side], c['am'][side]
    xf, nf = n4.nearest_fret(x)
    xi = x - xf
    w = np.ones_like(x) if c['uniform'] else bell(x, c['sig'], c['plat'])
    Af = t0                                   # the roll starts exactly at the steel toe on the fret centreline
    A = Af + (am - Af) * w
    Bz = Af + (c['Bm'] - Af) * w              # circular section at the nose, the v4 ellipse between frets
    if c['cheek'] > 0:
        # raised bolster: wood left proud of the land, outboard of the dome footprint, fading to nothing by the flanks
        sc = t0 + a
        rho = np.sqrt((xi / CW) ** 2 + (np.clip(sc - s, 0, None) / a) ** 2)      # 1 on the footprint edge
        outb = np.clip((sc - s) / a, 0, 1) ** 2                                 # 1 at the nose, 0 at the flanks
        clear = 0.003 / a
        raise_ = c['cheek'] * outb * np.exp(-((rho - 1 - clear) / 0.45) ** 2) * (np.abs(xi) < 0.11)
        topw = topw + np.where(rho >= 1 + clear, raise_, 0.0)
    zb = corner_z(x) - Bz
    with np.errstate(invalid='ignore'):
        wood = np.where(s < A, zb + (topw - zb) * n4.fq(s / A), topw)
    ss = s + steel_shift
    sc = t0 + a
    with np.errstate(invalid='ignore'):
        rr = 1 - (xi / CW) ** 2 - (np.clip(sc - ss, 0, None) / a) ** 2
    h = HF * np.sqrt(np.clip(rr, 0, None))
    steel = (rr > 0) & (nf >= 1)
    zs = np.where(steel, n4.board(x, side_y(x, ss, side)) + h, np.nan)
    return wood, zs


def surface(x, s, side, c, steel_shift=0.0):
    """Finished surface seen from above: z (absolute), steel mask, wood z."""
    x, s = np.broadcast_arrays(np.asarray(x, float), np.asarray(s, float))
    if c['kind'] == 'n4':
        y = side_y(x, s, side)
        z, steel, wood = n4.top_field(x, y, c['V'])
        if steel_shift:
            zsft, stsft, _ = n4.top_field(x, side_y(x, s + steel_shift, side), c['V'])
            zs = np.where(stsft, zsft, -np.inf)
            steel = zs > wood
            z = np.where(steel, zs, wood)
        return z, steel, wood
    wood, zs = dome_parts(x, s, side, c, steel_shift)
    steel = np.nan_to_num(zs, nan=-np.inf) > wood
    return np.where(steel, zs, wood), steel, wood


def rel(x, s, side, c, **kw):
    """Surface height above the nominal board corner."""
    z, steel, wood = surface(x, s, side, c, **kw)
    zc = corner_z(np.asarray(x, float))
    return z - zc, steel, wood - zc


# ---------------------------------------------------------------------------------- bending room ----
def end_profile(n, side, c):
    """Along the fret centreline: toe, where full height begins, where the ridge is within 0.005 of full height,
    and the 'hold line' where the ridge slope passes 10 degrees (a string resting there starts to slide off)."""
    x = FX[n]
    s = np.linspace(0, 0.14, 14001)
    z, steel, wood = surface(np.full_like(s, x), s, side, c)
    top = n4.board(x, side_y(x, s, side)) + HF
    lost = top - z
    full = float(s[np.argmax(lost < 1e-5)])
    use = float(s[np.argmax(lost < 0.005)])
    toe = float(s[np.argmax(steel)])
    slope = np.degrees(np.arctan(np.gradient(lost, s)))          # how fast the ridge falls going outboard
    m = steel & (s < full + 1e-9)
    inside = np.where(m & (-slope > 10.0))[0]
    hold = float(s[inside.max()]) if len(inside) else toe
    return dict(toe=toe, full=full, usable=use, hold=hold)


def vintage_profile(polish_r=0.008):
    """35 degree bevel from a flush end, the top edge polished to polish_r."""
    full = HF * math.tan(math.radians(35))
    use = (HF - 0.005) * math.tan(math.radians(35))
    # a radius r tangent to the top and to the 55 degree bevel face: tangent point on top is r*tan(27.5) inboard
    tang = full + polish_r * math.tan(math.radians(27.5))
    hold = tang - polish_r * math.sin(math.radians(10))
    return dict(toe=0.0, full=full, usable=use, hold=hold, full_polished=tang)


def margins(c):
    out = {}
    vp = vintage_profile()
    for n in (1, 12, 21):
        x = FX[n]
        ys = n4.string_y(np.array([x]))[:, 0]
        row = {}
        for side, yi in (('T', -ys[0]), ('B', ys[5])):
            e_new = float(n4.width(x)) / 2 - yi
            e_vin = float(n4.width_vintage(x)) / 2 - yi
            if c['name'] == 'vintage':
                p, e = vp, e_vin
            else:
                p, e = end_profile(n, side, c), e_new
            row[side] = dict(string_to_side=e, toe=p['toe'], full_from_side=p['full'],
                             to_full=e - p['full'], to_usable=e - p['usable'], to_hold=e - p['hold'],
                             vintage_to_full=e_vin - vp['full'], vintage_to_usable=e_vin - vp['usable'],
                             vintage_to_hold=e_vin - vp['hold'])
        out['fret_%d' % n] = row
    return out


# -------------------------------------------------------------------------- v4's own edge metric ----
def protrusion(c, side, phi, n0=9, n1=16, steel_shift=0.0):
    """v4's metric, for continuity: how far the steel end stands above the wood beside it for a flat hand
    held at phi above side-on; and the wave of the wood edge along the neck."""
    x = np.arange(FX[n0] - 0.2, FX[n1] + 0.2, 0.001)
    s = np.concatenate([[0.0], 0.16 * (1 - np.cos(np.linspace(0, np.pi / 2, 320)[1:]))])
    X, Sg = np.meshgrid(x, s, indexing='ij')
    z, steel, wood = rel(X, Sg, side, c, steel_shift=steel_shift)
    ph = math.radians(phi)
    sup = (-Sg * math.cos(ph) + z * math.sin(ph)).max(1)
    supw = (-Sg * math.cos(ph) + wood * math.sin(ph)).max(1)
    xf, nf = n4.nearest_fret(x)
    steps = []
    for n in range(n0 + 1, n1):
        m = np.abs(x - FX[n]) < CW
        m2 = (np.abs(x - FX[n]) > CW + 0.004) & (np.abs(x - FX[n]) < CW + 0.012)
        steps.append(float(sup[m].max() - supw[m2].max()))
    away = np.abs(x - xf) > CW + 0.004
    return dict(step=float(np.max(steps)), wood_wave=float(supw[away].max() - supw[away].min()),
                wave=float(sup.max() - sup.min()))


# ------------------------------------------------------------------------------- curvature ----
def sharpest(c, side, n=12, h=0.0004):
    """Smallest convex radius of curvature on the steel end, and on the wood around it, from the finished
    surface itself. Creases (two surfaces meeting at an angle) are reported separately by crease_angle()."""
    xf = FX[n]
    x = np.arange(xf - 0.10, xf + 0.10 + h / 2, h)
    s = np.arange(0.0, 0.10 + h / 2, h)
    X, Sg = np.meshgrid(x, s, indexing='ij')
    z, ST, wood = rel(X, Sg, side, c)
    out = {}
    for nm, Z, m0 in (('steel', z, ST), ('wood', wood, np.ones_like(ST))):
        Zx, Zs = np.gradient(Z, h, h)
        Zxx, Zxs = np.gradient(Zx, h, h)
        _, Zss = np.gradient(Zs, h, h)
        g = 1 + Zx ** 2 + Zs ** 2
        K = (Zxx * Zss - Zxs ** 2) / g ** 2
        Hm = ((1 + Zs ** 2) * Zxx - 2 * Zx * Zs * Zxs + (1 + Zx ** 2) * Zss) / (2 * g ** 1.5)
        kmin = Hm - np.sqrt(np.clip(Hm ** 2 - K, 0, None))
        m = _erode(m0, 4) & (np.sqrt(Zx ** 2 + Zs ** 2) < 3.5)
        m[:5] = m[-5:] = False
        m[:, :5] = m[:, -5:] = False
        if nm == 'steel':
            m &= Sg < end_profile(n, side, c)['full'] + 0.004 if c['name'] != 'vintage' else Sg < 0.04
        out[nm] = float(-1 / np.percentile(kmin[m], 0.5)) if m.any() and np.percentile(kmin[m], 0.5) < 0 else float('inf')
    return out


def _erode(m, k):
    o = m.copy()
    for _ in range(k):
        o[1:-1, 1:-1] = o[1:-1, 1:-1] & o[:-2, 1:-1] & o[2:, 1:-1] & o[1:-1, :-2] & o[1:-1, 2:]
    return o


# ------------------------------------------------------------- the edge as a hand sees it ----
def edge_polyline(x, side, c, steel_shift=0.0, s_max=0.45):
    """Section of the neck edge at stations x: the top out to s_max, then down the side and round the back.
    Returns s, z (relative to the nominal corner), steel flag; arrays [nx, npts] ordered from the back upward."""
    x = np.asarray(x, float)
    s_top = np.concatenate([np.arange(0, 0.16, 0.00025), np.arange(0.16, s_max + 1e-9, 0.002)])
    X, Sg = np.meshgrid(x, s_top, indexing='ij')
    z, steel, wood = rel(X, Sg, side, c, steel_shift=steel_shift)
    # side wall from the roll bottom down to the shoulder, then the back curve
    zc = corner_z(x)
    z_sh = n4.shoulder(x) - zc
    u = 1 - np.linspace(0, 1, 160) ** 2 * 0.55                 # lateral station on the back, 1 = full width
    W = n4.width(x)
    ub = (-u if side == 'T' else u)[None, :] + 0 * x[:, None]
    zback = n4.back(x[:, None], ub) - zc[:, None]
    sback = (1 - u)[None, :] * W[:, None] / 2
    wall_z = z[:, :1] + (z_sh[:, None] - z[:, :1]) * np.linspace(1, 0, 60)[None, :]   # from shoulder up to the roll bottom
    wall_s = np.zeros_like(wall_z)
    S_all = np.concatenate([sback[:, ::-1], wall_s, Sg], axis=1)
    Z_all = np.concatenate([zback[:, ::-1], wall_z, z], axis=1)
    ST_all = np.concatenate([np.zeros_like(sback, bool), np.zeros_like(wall_z, bool), steel], axis=1)
    return S_all, Z_all, ST_all


def view_field(c, side, x, phi, dt=0.004, t_lo=-0.40, t_hi=0.40, steel_shift=0.0, sub=4):
    """The edge as a height field for a hand approaching at phi above side-on.
    n = height toward the hand, t = across (positive toward the top of the board), both from the nominal corner.
    Returns H[nx, nt], steel mask, t grid."""
    S_all, Z_all, ST = edge_polyline(x, side, c, steel_shift)
    ph = math.radians(phi)
    nn = -S_all * math.cos(ph) + Z_all * math.sin(ph)
    tt = S_all * math.sin(ph) + Z_all * math.cos(ph)
    # densify each polyline so no t bin is skipped, then take the upper envelope
    fine = dt / sub
    nt = int(round((t_hi - t_lo) / fine)) + 1
    H = np.full((len(x), nt), -np.inf)
    M = np.zeros((len(x), nt), bool)
    seg = np.abs(np.diff(tt, axis=1))
    kmax = int(min(40, max(1, math.ceil(np.nanmax(seg) / fine))))
    rows = np.arange(len(x))[:, None]
    for j in range(kmax):
        f = j / kmax
        tj = tt[:, :-1] + f * (tt[:, 1:] - tt[:, :-1])
        nj = nn[:, :-1] + f * (nn[:, 1:] - nn[:, :-1])
        sj = ST[:, :-1] & ST[:, 1:] if 0 < j else ST[:, :-1]
        idx = np.rint((tj - t_lo) / fine).astype(int)
        ok = (idx >= 0) & (idx < nt)
        r = np.broadcast_to(rows, idx.shape)[ok]
        i = idx[ok]
        v = nj[ok]
        better = v > H[r, i]
        # two passes of maximum.at keep this exact when several samples land in one bin
        np.maximum.at(H, (r, i), v)
        hit = np.isclose(H[r, i], v)
        M[r[hit], i[hit]] = sj[ok][hit]
        del better
    # fill any empty bins along t, then reduce to the working grid by the maximum of each group
    tf = t_lo + fine * np.arange(nt)
    for r in range(len(x)):
        bad = ~np.isfinite(H[r])
        if bad.any() and (~bad).any():
            H[r, bad] = np.interp(tf[bad], tf[~bad], H[r, ~bad], left=-9, right=-9)
            near = np.clip(np.searchsorted(tf[~bad], tf[bad]), 0, (~bad).sum() - 1)
            M[r, bad] = M[r, ~bad][near]
    ng = (nt - 1) // sub + 1
    Hc = np.full((len(x), ng), -np.inf)
    Mc = np.zeros((len(x), ng), bool)
    for k in range(-(sub // 2), sub - sub // 2):
        idx = np.clip(np.arange(ng) * sub + k, 0, nt - 1)
        hk = H[:, idx]
        up = hk > Hc
        Hc = np.where(up, hk, Hc)
        Mc = np.where(up, M[:, idx], Mc)
    return Hc, Mc, t_lo + dt * np.arange(ng)


# ------------------------------------------------------------------- can a real cutter make it ----
def ball_nose_check(c, side, n=12, r=0.125, h=0.004, span=0.5):
    """Roll a ball of radius r over the bare wood (no frets) and see what it cannot reach.
    Returns the largest amount of wood the cutter would leave or over-cut (0 = fully machinable)."""
    xf = FX[n]
    x = np.arange(xf - span, xf + span + h / 2, h)
    s = np.arange(-0.14, 0.5 + h / 2, h)
    X, Sg = np.meshgrid(x, s, indexing='ij')
    _, _, wood = rel(X, np.clip(Sg, 0, None), side, c)
    # beyond the side the cutter runs down the wall: model it as open air well below the roll
    Z = np.where(Sg < 0, -0.5, wood)
    k = int(round(r / h))
    off = np.arange(-k, k + 1) * h
    OX, OY = np.meshgrid(off, off, indexing='ij')
    ok = OX ** 2 + OY ** 2 <= r * r
    lift = np.sqrt(np.clip(r * r - OX ** 2 - OY ** 2, 0, None))
    # tool-centre surface, then the surface that tool leaves
    Zp = np.pad(Z, k, mode='edge')
    C = np.full_like(Z, -np.inf)
    for i, j in zip(*np.where(ok)):
        C = np.maximum(C, Zp[i:i + Z.shape[0], j:j + Z.shape[1]] + lift[i, j])
    Cp = np.pad(C, k, mode='edge')
    Zc = np.full_like(Z, np.inf)
    for i, j in zip(*np.where(ok)):
        Zc = np.minimum(Zc, Cp[i:i + Z.shape[0], j:j + Z.shape[1]] - lift[i, j])
    core = (Sg >= 0.0) & (np.abs(X - xf) < span - r - 0.02) & (Sg < 0.5 - r - 0.02)
    left = (Zc - Z)[core]
    i = np.argmax(left)
    return dict(max_uncut=float(left.max()), at_x=float(X[core][i] - xf), at_s=float(Sg[core][i]))


def support_gap(c, side, n=12):
    """Largest air gap between the flat underside of the steel end and the wood below it (nominal fit)."""
    xf = FX[n]
    xi = np.linspace(-CW, CW, 161)
    s = np.linspace(0, 0.09, 721)
    X, Sg = np.meshgrid(xf + xi, s, indexing='ij')
    wood, zs = dome_parts(X, Sg, side, c)
    land = n4.board(X, side_y(X, Sg, side))
    under = np.isfinite(zs)
    return float(np.max(np.where(under, land - wood, 0.0)))


def shrink_per_side(n=12, coeff=None, dmc=None):
    """Seasonal movement of the board side relative to a steel fret anchored at the centreline."""
    out = {}
    W = float(n4.width(FX[n]))
    for name, sh in (('quartersawn (radial)', 0.027), ('flatsawn (tangential)', 0.059)):
        k = sh / 28.0                                  # per 1 % moisture content, shrinkage / fibre saturation
        out[name] = {('MC +-%.1f' % d): round(W / 2 * k * d, 4) for d in (1.0, 2.0, 3.0)}
    return out


def fret_table(t0=0.010, nip=0.075):
    rows = []
    for n in range(1, NF + 1):
        W = float(n4.width(FX[n]))
        rows.append(dict(fret=n, x=round(float(FX[n]), 4), board_width=round(W, 4), crown_length=round(W - 2 * t0, 4),
                         tang_length=round(W - 2 * t0 - 2 * nip, 4)))
    return rows


if __name__ == '__main__':
    out = dict(margins={}, protrusion={}, sharpest={}, machinable={}, gap={})
    for k, c in CANDS.items():
        out['margins'][k] = margins(c)
        out['protrusion'][k] = {sd: {str(int(p)): protrusion(c, sd, p) for p in (15, 30, 45, 60)} for sd in 'TB'}
        out['sharpest'][k] = {sd: sharpest(c, sd) for sd in 'TB'}
        m = out['margins'][k]['fret_12']
        print('%-8s toe %.4f full %.4f | to_full T %.4f B %.4f | usable T %.4f | hold T %.4f | vintage full %.4f hold %.4f'
              % (k, m['T']['toe'], m['T']['full_from_side'], m['T']['to_full'], m['B']['to_full'], m['T']['to_usable'],
                 m['T']['to_hold'], m['T']['vintage_to_full'], m['T']['vintage_to_hold']))
        pr = out['protrusion'][k]['T']
        print('         step 30/45/60: %.4f %.4f %.4f  wood wave 45: T %.4f B %.4f   sharpest steel %.4f wood %.4f'
              % (pr['30']['step'], pr['45']['step'], pr['60']['step'], pr['45']['wood_wave'],
                 out['protrusion'][k]['B']['45']['wood_wave'], out['sharpest'][k]['T']['steel'], out['sharpest'][k]['T']['wood']))
    for k in ('bullet', 'rec', 'fallback', 'pocket'):
        c = CANDS[k]
        out['machinable'][k] = {sd: {('fret_%d' % n): ball_nose_check(c, sd, n) for n in (2, 12, 21)} for sd in 'TB'}
        out['gap'][k] = {sd: support_gap(c, sd) for sd in 'TB'}
        print(k, 'ball-nose 1/4:', {sd: round(max(v['max_uncut'] for v in out['machinable'][k][sd].values()), 5) for sd in 'TB'},
              'gap under steel:', out['gap'][k])
    out['shrink_per_side_fret12'] = shrink_per_side()
    out['frets'] = fret_table()
    print(json.dumps(out['shrink_per_side_fret12'], indent=1))
    json.dump(out, open(os.path.join(HERE, 'geometry.json'), 'w'), indent=1)
