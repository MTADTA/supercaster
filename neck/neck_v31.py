#!/usr/bin/env python3
"""Supercaster II set neck, v3.1 (2026-11-13): roll option d + steel fret ends that blend into the board.

On top of v3 (neck_v3.py), changed:
  back     : the ruled loft A -> B keeps v3's depth law and A/B shapes but uses the VINTAGE width law W_v(x) (u = 2y/W_v),
             so girth returns toward v2. The board top stays W = W_v + 2 * 0.030.
  edge     : one law, constant in x, in edge coordinates (s = depth below the board-top edge):
               flat top -> superellipse roll (n = 2.5, a across x b down; zero curvature at both ends, G2)
               -> straight side wall down to s_v = b + d_max (the scallop translates the roll down by d at mid-cell)
               -> quintic shoulder s_v -> s_j, G2 at both ends (y' = y'' = 0 at s_v; value/slope/curvature of the back at s_j)
               -> back (vintage-width ruled loft).
  fret end : ground-only steel taper over the last L: thickness t(y) = t_tip + (H - t_tip)(1 - S5(xi)), the across-x crown
             profile blends from the ellipse to (1 - xi_x^2)^2 (tangent to the wood), tip 0.004 tangent to the flat wood,
             the tip sits AT the roll start (steel cannot follow the roll down: bend study below).
  scallop  : same S5 law; kappa trimmed globally so the cell-20 catch is <= the flat board.
Run: viz python -I -W ignore neck_v31.py   (writes results_v31.json, fig/v31_*.png)
"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import neck_v2 as v2
import neck_v3 as v3
import neck_model as nm
from neck_model import P, fret_x, width, sag, STR, X22, S5

HERE = v2.HERE; FIG = v2.FIG
V31 = dict(
    widen=0.030,        # per side, as v3 [computed: bend-room rule]
    margin=0.003,       # usable crown beyond vintage (owner: 'still beats vintage') [judged]
    L=0.040,            # steel taper length, full crown -> tip [judged; trade table]
    t_tip=0.004,        # steel thickness at the tip (rounded, r ~0.002) [judged]
    r_nose=0.040,       # plan radius of the steel nose (= crown half-width: semicircular in plan) [judged]
    n=2.5,              # roll superellipse exponent (>2: zero curvature at both ends -> G2) [judged]
    b_over_a=1.0,       # roll depth / roll width [judged: largest corner radius for a given width]
    s_j=0.40,           # shoulder joins the back this far below the board-top edge [computed: scan below]
    slot_back=0.030,    # stopped slot ends this far inside the roll start [judged, as v3]
    tang_back=0.035,    # tang nipped this far inside the roll start [judged, as v3]
    kappa=None,         # set by kappa_scan()
    eps_allow=(0.02, 0.05),   # bending-strain levels studied for hard-drawn stainless [lit: 2-8 % elongation, cold-worked 304]
)
H = P['crown_h']; CW = P['crown_w'] / 2

# ------------------------------------------------------------------------------------------------ steel end
def xi_usable():
    """Taper fraction where the steel is back to 90 % crown height."""
    xs = np.linspace(0, 1, 200001); t = V31['t_tip']; h = t + (H - t) * (1 - S5(xs))
    return float(xs[np.argmax(h < 0.9 * H)])
def roll_a31(x=None):
    """Board-top roll width: the board edge -> vintage usable end (widen + bevel_usable) less the margin and the taper run."""
    a = V31['widen'] + v3.bevel_usable() - V31['margin'] - (1 - xi_usable()) * V31['L']
    return a if x is None else np.full_like(np.asarray(x, float), a)
def roll_b31(): return V31['b_over_a'] * roll_a31()
def d_max(): return max(float(nm.sc_depth_cell(k)) for k in range(1, 23))
def s_v(): return roll_b31() + d_max()
def steel_h(y_rel):
    """Steel thickness vs y_rel = |y| - y_c (<= 0): full H until -L, taper to t_tip at 0."""
    L = V31['L']; xi = np.clip((y_rel + L) / L, 0, 1); t = V31['t_tip']
    return np.where(y_rel <= 0, t + (H - t) * (1 - S5(xi)), np.nan), S5(xi)
def steel_z(dx, y_rel):
    """Steel top above the wood at (dx from the fret centre, y_rel).
    Plan: the tip is a rounded nose, y_tip(q) = -r_nose (1 - sqrt(1 - q^2)); the taper runs L back from it at every q.
    Section across the crown: rim te = t_tip * lam plus (h - te) * [ellipse -> (1 - q^2)^2 blend], times a steep rounded
    foot sqrt(1 - q^16) -> the boundary is a finite ~vertical foot (like a normal fret foot), never a feather."""
    dx = np.asarray(dx, float); y_rel = np.asarray(y_rel, float); q = np.clip(np.abs(dx) / CW, 0, 1)
    ytip = -V31['r_nose'] * (1 - np.sqrt(1 - q * q)); L = V31['L']; t = V31['t_tip']
    xi = np.clip((y_rel - ytip + L) / L, 0, 1); lam = S5(xi); h = t + (H - t) * (1 - lam); te = t * lam
    f = (1 - lam) * np.sqrt(1 - q * q) + lam * (1 - q * q) ** 2
    z = np.sqrt(np.clip(1 - q ** 16, 0, 1)) * (te + (h - te) * f)
    return np.where((np.abs(dx) < CW) & (y_rel <= ytip), z, np.nan)
def steel_boundary_check():
    """Steel thickness 0.002 inside its boundary (sides and nose) and the foot angle; vs the original crown (no steel added)."""
    L = V31['L']; ys = np.linspace(-L - 0.02, 0, 2001); dxs = np.linspace(0, CW - 1e-6, 4001)
    side = steel_z(np.full_like(ys, CW - 0.002), ys); side_min = float(np.nanmin(side))
    q = dxs / CW; ytip = -V31['r_nose'] * (1 - np.sqrt(1 - q * q)); ok = dxs <= CW - 0.002
    nose = steel_z(dxs[ok], ytip[ok] - 0.002); nose_min = float(np.nanmin(nose))
    zt = steel_z(dxs, np.zeros_like(dxs) - 1e-9)                     # thickness along the y = 0 line (centre of the nose)
    # foot angle at the tip centre line: slope of the steel top over its last 0.002 at the side
    yt = -0.001; z1 = float(steel_z(np.array(CW - 0.002), np.array(yt))); z0 = float(steel_z(np.array(CW - 1e-5), np.array(yt)))
    # steel added beyond the original crown H sqrt(1 - q^2) (tolerance band near the foot)
    YY, QQ = np.meshgrid(ys, q, indexing='ij'); Z = steel_z(QQ * CW, YY); orig = H * np.sqrt(np.clip(1 - QQ ** 2, 0, 1))
    excess = np.nan_to_num(Z - orig, nan=-1); bad = excess > 1e-6
    return dict(tip_centre=float(steel_z(np.array(0.0), np.array(-1e-9))), side_rim_min_at_0p002_in=side_min, nose_rim_min_at_0p002_in=nose_min,
                foot_angle_deg=float(np.degrees(np.arctan((z1 - z0) / 0.002))), r_nose=V31['r_nose'],
                excess_over_original_max=float(excess.max()), excess_band_from_foot=float(CW * (1 - QQ[bad].min())) if bad.any() else 0.0)

# ------------------------------------------------------------------------------------------------ section: roll, wall, shoulder, back
def width_v(x): return v3.width_v(x)
def back3(x, y):
    """v3 ruled loft (A -> B, MOD depth) with u = 2y/W_v(x): exactly ruled on [0, x_h]."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    u = 2 * y / width_v(x); t = np.clip(x / v2.XH, 0, 1)
    PA = nm.Phi(u, *v2.V2['A']); PB = nm.Phi(u, *v2.V2['B']); DA = v2.D2(0.0); DB = v2.D2(v2.XH)
    zr = -((1 - t) * DA * PA + t * DB * PB)
    return np.where(x <= v2.XH, zr, -v2.D2(x) * PB)
def _quintic(y0, d0, c0, y1, d1, c1, h, tau):
    """Quintic Hermite on tau in [0,1] for an interval of length h: value, 1st and 2nd derivative (w.r.t. s)."""
    D0, D1, C0, C1 = d0 * h, d1 * h, c0 * h * h, c1 * h * h
    a0, a1, a2 = y0, D0, C0 / 2
    a3 = 10 * (y1 - y0) - 6 * D0 - 4 * D1 - 1.5 * C0 + 0.5 * C1
    a4 = -15 * (y1 - y0) + 8 * D0 + 7 * D1 + 1.5 * C0 - C1
    a5 = 6 * (y1 - y0) - 3 * D0 - 3 * D1 - 0.5 * C0 + 0.5 * C1
    t = tau
    y = a0 + a1 * t + a2 * t ** 2 + a3 * t ** 3 + a4 * t ** 4 + a5 * t ** 5
    yp = (a1 + 2 * a2 * t + 3 * a3 * t ** 2 + 4 * a4 * t ** 3 + 5 * a5 * t ** 4) / h
    ypp = (2 * a2 + 6 * a3 * t + 12 * a4 * t ** 2 + 20 * a5 * t ** 3) / (h * h)
    return y, yp, ypp
_SH = {}
def shoulder(x, side, s_j=None):
    """Outer outline |y|(s) of one side at x for s in [s_v, s_j] (quintic) and the join data. Cached."""
    s_j = V31['s_j'] if s_j is None else s_j
    key = (round(float(x), 7), side, round(s_j, 5), round(s_v(), 6), V31['widen'])
    if key in _SH: return _SH[key]
    x = float(x); hw = float(width(x)) / 2; ze = float(sag(x, hw) + nm.planed(x))
    u0 = v2.V2['A'][0] * (1 - min(x / v2.XH, 1))
    u = np.linspace(u0, side * 1.0, 6001) if side > 0 else np.linspace(u0, -1.0, 6001)
    yb = np.abs(u) * float(width_v(x)) / 2; sb = -back3(np.full_like(u, x), u * float(width_v(x)) / 2) - ze
    o = np.argsort(sb); sb, yb = sb[o], yb[o]
    sg = np.linspace(s_j - 0.004, s_j + 0.004, 9); yg = np.interp(sg, sb, yb)
    y1 = yg[4]; d1 = (yg[5] - yg[3]) / 0.002; c1 = (yg[6] - 2 * yg[4] + yg[2]) / 0.002 ** 2
    sv = s_v(); h = s_j - sv; tau = np.linspace(0, 1, 801)
    ys, yp, ypp = _quintic(hw, 0.0, 0.0, y1, d1, c1, h, tau)
    out = dict(s=sv + tau * h, y=ys, yp=yp, ypp=ypp, hw=hw, ze=ze, sb=sb, yb=yb, y_join=y1, inset_join=hw - y1)
    _SH[key] = out; return out
def bottom3(x, y, rule=None, law=None):
    """Lower outline z(x, y): back3 inboard of the shoulder join, the shoulder outside it, the side-wall foot at |y| = W/2."""
    x = np.asarray(x, float); y = np.asarray(y, float); X, Y = np.broadcast_arrays(x, y)
    out = back3(X, Y).astype(float).copy()
    for xv in np.unique(X):
        m = X == xv
        for side in (1, -1):
            sh = shoulder(xv, side); mm = m & (side * Y > 0) & (np.abs(Y) > sh['y_join'])
            if mm.any():
                s = np.interp(np.abs(Y[mm]), sh['y'][::-1], sh['s'][::-1]); out[mm] = -sh['ze'] - s
    return out
def roll_drop31(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); hw = width(x) / 2; a = roll_a31(); b = roll_b31()
    q = (np.abs(y) - (hw - a)) / a; n = V31['n']
    w = np.where(q <= 0, 1.0, (1 - np.clip(q, 0, 1) ** n) ** (1 / n))
    return np.where(q <= 1 + 1e-9, b * (1 - w), 10.0)
def scallop_z31(x, y):
    """Full scallop depth right across, including the roll (the roll is translated down by d at mid-cell)."""
    x = np.asarray(x, float); y = np.asarray(y, float); return -nm.scallop_long(x) * np.ones_like(y)

def install():
    v3.install()
    if V31['kappa'] is not None: P['sc_kappa'] = V31['kappa']
    P['nut_w'] = v3.W_NUT_V + 2 * V31['widen']; P['w21'] = 2.20 + 2 * V31['widen']
    nm.roll_a = roll_a31; nm.roll_drop = roll_drop31; nm.scallop_z = scallop_z31
    v2.back2 = bottom3; nm.back_z = bottom3
    _SH.clear(); nm._EI_CACHE.clear()

# ------------------------------------------------------------------------------------------------ studies
def kappa_scan():
    rows = []
    for kap in (0.15, 0.145, 0.14, 0.135, 0.13, 0.125, 0.12):
        P['sc_kappa'] = kap; r = {}
        for k in range(1, 23):
            L = float(fret_x(k) - fret_x(k - 1)); d = float(nm.sc_depth_cell(k))
            lin_bound = d < kap * L * L - 1e-9
            r[k] = dict(d=d, catch=nm.finger_catch(nm.cell_profile(L, 'land', d), L)[0],
                        flat=nm.finger_catch(nm.cell_profile(L, 'flat'), L)[0], kappa_bound=not lin_bound)
        rows.append(dict(kappa=kap, cells=r))
    P['sc_kappa'] = 0.15
    ok = [r for r in rows if r['cells'][20]['catch'] <= r['cells'][20]['flat'] + 1e-9]
    pick = max(ok, key=lambda r: r['kappa']) if ok else rows[-1]
    return rows, pick['kappa']
def shoulder_scan():
    """Smallest s_j for which the shoulder is monotone (y' <= 0) and convex (y'' <= 0) on both sides at all x."""
    out = []
    xs = [0.0, float(fret_x(1)), float(fret_x(5)), float(fret_x(12)), v2.XH, float(fret_x(17)), float(fret_x(21))]
    for sj in np.arange(0.20, 0.701, 0.025):
        worst_pp = -9.0; worst_p = -9.0; ins = []
        for x in xs:
            for side in (1, -1):
                sh = shoulder(x, side, sj); worst_pp = max(worst_pp, float(sh['ypp'].max())); worst_p = max(worst_p, float(sh['yp'].max()))
                ins.append(sh['inset_join'])
        out.append(dict(s_j=float(sj), max_ypp=worst_pp, max_yp=worst_p, inset_min=min(ins), ok=bool(worst_pp <= 1e-6 and worst_p <= 1e-9)))
    return out
def shoulder_metrics():
    """Per station and side: shoulder min radius, depth where it meets the glue line, inset at the join, roll metrics."""
    rows = []; a = roll_a31(); b = roll_b31(); n = V31['n']
    th = np.linspace(1e-4, np.pi / 2 - 1e-4, 20001)
    Yr = a * np.cos(th) ** (2 / n); Zr = b * np.sin(th) ** (2 / n)          # superellipse corner (centred)
    dY = np.gradient(Yr, th); dZ = np.gradient(Zr, th); ddY = np.gradient(dY, th); ddZ = np.gradient(dZ, th)
    kr = np.abs(dY * ddZ - dZ * ddY) / (dY ** 2 + dZ ** 2) ** 1.5
    roll_rmin = float(1 / kr[100:-100].max())
    for n_ in (0, 1, 12, 21):
        x = float(fret_x(n_)) if n_ else 0.0
        for side in (1, -1):
            sh = shoulder(x, side); k = np.abs(sh['ypp']) / (1 + sh['yp'] ** 2) ** 1.5
            sg = 0.140                                                    # glue line ~ t_b below the edge top
            yg = float(np.interp(sg, sh['s'], sh['y'])); slope = float(np.degrees(np.arctan(abs(np.interp(sg, sh['s'], sh['yp'])))))
            rows.append(dict(fret=n_, side='bass' if side > 0 else 'treble', shoulder_rmin=float(1 / max(k.max(), 1e-9)),
                             inset_at_glue=sh['hw'] - yg, side_angle_from_vertical_at_glue=slope, inset_join=sh['inset_join'],
                             s_v=s_v(), s_j=V31['s_j']))
    return dict(roll_a=a, roll_b=b, roll_rmin=roll_rmin, rows=rows)
def ruled_check31():
    """back3: second difference along x at fixed u (exactly ruled). Shoulder band: at fixed shoulder parameter tau, deviation of
    (y, z)(x) from the straight line between x = 0 and x = x_h."""
    xs = np.linspace(0, v2.XH, 9); dev_back = 0.0
    for u in np.linspace(-0.98, 0.98, 41):
        z = np.array([float(back3(xx, u * float(width_v(xx)) / 2)) for xx in xs]); dev_back = max(dev_back, float(np.abs(np.diff(z, 2)).max()))
    dev_sh = 0.0
    for side in (1, -1):
        pts = []
        for xx in xs:
            sh = shoulder(xx, side); pts.append(np.c_[sh['y'], -sh['ze'] - sh['s']])
        pts = np.array(pts); t = (xs / v2.XH)[:, None, None]
        lin = (1 - t) * pts[0][None] + t * pts[-1][None]
        dev_sh = max(dev_sh, float(np.abs(pts - lin).max()))
    return dict(back_second_diff=dev_back, shoulder_dev_from_ruled=dev_sh)
def margins():
    """Outer string to the usable crown end (>= 90 % height), v3.1 vs vintage, at the nut and frets 1, 12, 21."""
    out = {}; xu = xi_usable()
    for n_ in (0, 1, 12, 21):
        x = float(fret_x(n_)) if n_ else 0.0; hw = float(width(x)) / 2; yc = hw - roll_a31()
        y_u = yc - (1 - xu) * V31['L']; s = float(nm.spread(x, 'vintage')) / 2
        out[n_] = dict(W=2 * hw, roll_start_from_edge=roll_a31(), usable_end_from_edge=hw - y_u, usable_margin=y_u - s,
                       vintage_margin=float(v3.vint_margin(x, 0)), over_vintage=(y_u - s) - float(v3.vint_margin(x, 0)),
                       full_height_end_from_edge=roll_a31() + V31['L'], tip_from_edge=roll_a31(),
                       slot_stop_from_edge=roll_a31() + V31['slot_back'], tang_stop_from_edge=roll_a31() + V31['tang_back'],
                       steel_h_at_slot_end=float(steel_h(np.array(-V31['slot_back']))[0]), steel_h_at_tang_end=float(steel_h(np.array(-V31['tang_back']))[0]))
    return out
def trade_table():
    """Closed form: roll width a = widen + bevel_usable - margin - (1 - xi_u) L (taper on flat wood, tip at the roll start)."""
    xu = xi_usable(); bu = v3.bevel_usable(); rows = []
    for widen in (0.030, 0.045, 0.060):
        for L in (0.020, 0.030, 0.040, 0.060, 0.080, 0.100):
            rows.append(dict(widen=widen, L=L, a=widen + bu - V31['margin'] - (1 - xu) * L))
    need = {f'a{a_}_L{L}': a_ + V31['margin'] + (1 - xu) * L - bu for a_ in (0.06, 0.08) for L in (0.06, 0.10)}
    return dict(rows=rows, widen_needed=need, xi_u=xu, bevel_usable=bu)
def bend_study():
    """Could the thinned steel end be pre-bent to follow a 0.06-0.08 roll down? Strain = c * h * kappa_wood, c = 0.62 (extreme
    fibre of the blended crown section). Tip placed where the wood has dropped delta_tip; taper L ends there."""
    rows = []; C = 0.62; t = V31['t_tip']
    for a in (0.06, 0.08):
        for b in (0.105, a):
            for n in (2.0, 2.5):
                for L in (0.06, 0.10):
                    for dtip in (0.002, 0.005, 0.010, 0.020):
                        s = np.linspace(0, a * 0.999, 20001); de = b * (1 - (1 - (s / a) ** n) ** (1 / n))
                        st = float(np.interp(dtip, de, s)); s0 = st - L
                        ss = np.linspace(max(s0, 0), st, 4000); dd = b * (1 - (1 - (ss / a) ** n) ** (1 / n))
                        kap = np.abs(np.gradient(np.gradient(dd, ss), ss)); h = t + (H - t) * (1 - S5((ss - s0) / L))
                        eps = float((C * h * kap)[5:-5].max()) if len(ss) > 10 else 0.0
                        # usable end of the steel crown top above the board plane (wood drop counts against it)
                        sall = np.linspace(s0, st, 4000); dall = np.where(sall > 0, b * (1 - (1 - (np.clip(sall, 0, None) / a) ** n) ** (1 / n)), 0)
                        top = -dall + t + (H - t) * (1 - S5((sall - s0) / L)); su = float(sall[np.argmax(top < 0.9 * H)])
                        rows.append(dict(a=a, b=b, n=n, L=L, tip_drop=dtip, strain=eps, usable_from_roll_start=su,
                                         usable_end_from_edge=a - su))
    return rows
def edge_slide31():
    """Pad (rigid R 0.30) held against the bass edge at 30 / 45 / 60 deg from vertical, slid along x over a fret end.
    Largest slope jump of the pad path (deg): wood only, with steel, and the difference (= what the fret end adds)."""
    out = []; R = P['finger_R']; w = int(R / 0.001); off = np.arange(-w, w + 1) * 0.001; cap = np.sqrt(np.clip(R * R - off * off, 0, None))
    for n_ in (5, 12, 19):
        x0 = float(fret_x(n_)); hw = float(width(x0)) / 2; yc = hw - roll_a31()
        xs = np.arange(x0 - 0.3, x0 + 0.3, 0.001); y = np.linspace(yc - V31['L'] - 0.03, hw, 500)
        ZW = np.array([nm.top_z(x, y) + sag(x, y) + nm.planed(x) for x in xs])
        SZ = steel_z(xs[:, None] - x0, (y - yc)[None, :]); ZS = np.where(np.isfinite(SZ), np.maximum(ZW, SZ), ZW)
        res = dict(fret=n_)
        for ang in (30, 45, 60):
            c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            for steel, Z in ((False, ZW), (True, ZS)):
                h = (Z * c + y[None, :] * s_).max(1)
                idx = np.clip(np.arange(len(h))[:, None] + np.arange(-w, w + 1)[None, :], 0, len(h) - 1)
                path = (h[idx] + cap).max(1); sl = np.arctan(np.diff(path) / 0.001)
                res[f'{"steel" if steel else "wood"}_{ang}'] = float(np.degrees(np.abs(np.diff(sl)).max()))
                res[f'rise_{"steel" if steel else "wood"}_{ang}'] = float(path.max() - path.min())
            res[f'delta_{ang}'] = res[f'steel_{ang}'] - res[f'wood_{ang}']
            res[f'delta_rise_{ang}'] = res[f'rise_steel_{ang}'] - res[f'rise_wood_{ang}']
        out.append(res)
    return out
def slot_wall31():
    """Rosewood between the stopped-slot end and the rolled surface, horizontal, at depths 0 .. slot depth."""
    out = []
    for n_ in (1, 12, 21):
        x = float(fret_x(n_)); hw = float(width(x)) / 2; yc = hw - roll_a31(); yse = yc - V31['slot_back']
        y = np.linspace(yc - 0.05, hw, 6000); zt = nm.top_z(x, y, scallops=False) + sag(x, y) + nm.planed(x)
        walls = {}
        for dz in (0.0, 0.010, 0.030, P['slot_d']):
            below = zt < -dz - 1e-9; yr = y[np.argmax(below)] if below.any() else hw
            walls[f'{dz:.3f}'] = float(max(yr, yc) - yse)
        out.append(dict(fret=n_, slot_end_from_edge=hw - yse, wall=walls, slot_bottom_to_glue=v3.V3['t_b'] - P['slot_d']))
    return out
def along_fret_check():
    """Hand sliding ALONG the fret toward the edge at the fret centre: slope of the steel top + wood, steel -> wood at the tip."""
    x0 = float(fret_x(12)); hw = float(width(x0)) / 2; yc = hw - roll_a31()
    y = np.linspace(yc - V31['L'] - 0.02, hw - 0.002, 4001); zw = nm.top_z(x0, y) + sag(x0, y) + nm.planed(x0)
    sz = steel_z(np.zeros_like(y), y - yc); z = np.where(np.isfinite(sz), zw + sz, zw)
    sl = np.degrees(np.arctan(np.gradient(z, y))); i = np.argmin(np.abs(y - yc))
    return dict(max_down_slope_deg=float(-sl.min()), slope_step_at_tip_deg=float(abs(sl[i + 3] - sl[i - 3])),
                steel_slope_max_deg=float(np.degrees(np.arctan((H - V31['t_tip']) * 1.875 / V31['L']))))

def girth_bound():
    """Lower bound on the hand girth of ANY convex section that holds the +0.030 board top and the vintage-width back:
    perimeter of the convex hull of the two, minus the top between the roll starts."""
    from scipy.spatial import ConvexHull
    out = {}
    for n_ in v3.FW:
        x = float(fret_x(n_)) if n_ else 0.02; hw = float(width(x)) / 2; a = roll_a31()
        u = np.linspace(-1, 1, 4001); yv = u * float(width_v(x)) / 2; zb = back3(np.full_like(u, x), yv)
        ok = zb < -sag(x, yv) - nm.planed(x); yv, zb = yv[ok], zb[ok]
        yt = np.linspace(-hw, hw, 2001); zt = -sag(x, yt) - nm.planed(x)
        pts = np.r_[np.c_[yv, zb], np.c_[yt, zt]]; hl = ConvexHull(pts); Pp = pts[hl.vertices]; Pp = np.r_[Pp, Pp[:1]]
        yc = hw - a; ytop = np.linspace(-yc, yc, 2001); ztop = -sag(x, ytop) - nm.planed(x)
        out[n_] = float(np.hypot(*np.diff(Pp, axis=0).T).sum() - np.hypot(np.diff(ytop), np.diff(ztop)).sum())
    return out
def trade_rerun():
    """Full-model rerun of the main trade: widen and taper length L (margin fixed), roll a by the budget."""
    keep = dict(V31); rows = []
    for widen, L in ((0.030, 0.030), (0.030, 0.040), (0.030, 0.060), (0.045, 0.060), (0.060, 0.060), (0.060, 0.100)):
        V31['widen'] = widen; V31['L'] = L; install()
        a = roll_a31()
        if a < 0.004: rows.append(dict(widen=widen, L=L, a=a, feasible=False)); continue
        mg = margins(); sl = [r for r in edge_slide31() if r['fret'] == 12][0]
        ypp = max(float(shoulder(x, sd)['ypp'].max()) for x in (0.0, float(fret_x(12)), float(fret_x(21))) for sd in (1, -1))
        rows.append(dict(widen=widen, L=L, a=a, feasible=True, nut_W=float(width(0.0)), margin_nut=mg[0]['usable_margin'], margin_f12=mg[12]['usable_margin'],
                         girth_nut=v3.hand_girth(0.02)[1], girth_f12=v3.hand_girth(float(fret_x(12)))[1],
                         slide_f12_wood_30=sl['wood_30'], slide_f12_delta_30=sl['delta_30'], slide_f12_delta_45=sl['delta_45'],
                         steel_slope_max_deg=float(np.degrees(np.arctan((H - V31['t_tip']) * 1.875 / L))), shoulder_max_ypp=ypp))
    V31.clear(); V31.update(keep); install()
    return rows

# ------------------------------------------------------------------------------------------------ baselines (v2, v3) for comparison
def baselines():
    B = {}
    v2.V2['A'] = (0.06, 2.40, 1.90); v2.TB[0] = 0.140; v2.V2['roll_margin'] = 0.025
    v2.install(True)
    B['v2'] = dict(girth={n_: v3.hand_girth(float(fret_x(n_)) if n_ else 0.02) for n_ in v3.FW}, poly={}, roll={})
    for lab, x in (('A', 0.0), ('f12', float(fret_x(12))), ('B', v2.XH)):
        B['v2']['poly'][lab] = nm.section_polygon(max(x, 0.02), scallops=False)
    for n_ in (1, 12, 21):
        x = float(fret_x(n_)); hw = float(width(x)) / 2; a = float(nm.roll_a(x)); yc = hw - a
        bb = float(v2.roll_b_side2(x, 1.0)); ys = float(v2.side_y2(x, float(sag(x, hw) + nm.planed(x)) + bb, 1)); ah = ys - yc
        B['v2']['roll'][n_] = dict(a=a, b=bb, ah=ah, rmin=min(ah * ah / bb, bb * bb / ah))
    v2.install(False)
    v3.install()
    B['v3'] = dict(poly={}, roll={})
    for lab, x in (('A', 0.0), ('f12', float(fret_x(12))), ('B', v2.XH)):
        B['v3']['poly'][lab] = nm.section_polygon(max(x, 0.02), scallops=False)
    for n_ in (1, 12, 21):
        x = float(fret_x(n_)); hw = float(width(x)) / 2; a = float(nm.roll_a(x))
        q, b, b0, ah, yc, d = v3.roll_geom(np.array([x]), np.array([hw - a / 2])); b = float(b0[0]); ah = float(ah[0])
        B['v3']['roll'][n_] = dict(a=a, b=b, ah=ah, rmin=min(ah * ah / b, b * b / ah))
    with open(os.path.join(HERE, 'results_v3.json')) as fh: B['v3']['girth'] = {int(k): (v['v3_perim'], v['v3_hand']) for k, v in json.load(fh)['width']['girth'].items()}
    return B

# ------------------------------------------------------------------------------------------------ figures
ROSE, MAPLE, STEEL = v3.ROSE, v3.MAPLE, v3.STEEL
def draw31(ax, x, at_fret, zoom=None):
    yy, zz = nm.section_polygon(x); ax.fill(yy, zz, color=MAPLE, ec='#6b4f2a', lw=0.8)
    hw = float(width(x)) / 2; yg = np.linspace(-hw, hw, 3000); zt = nm.top_z(x, yg); zg = v2.glue_z(x, yg); zb = bottom3(np.full_like(yg, x), yg)
    rose = (zt > zg) & (zt > -5)
    ax.fill_between(yg, np.where(rose, np.maximum(zg, zb), np.nan), np.where(rose, zt, np.nan), color=ROSE)
    ax.plot(yg, np.where(rose & (zg > zb), zg, np.nan), 'k:', lw=0.6)
    if at_fret:
        yc = hw - roll_a31(); ys = np.linspace(-yc, yc, 1600); z0 = -sag(x, ys) - nm.planed(x)
        hh = steel_h(np.abs(ys) - yc)[0]; ax.fill_between(ys, z0, z0 + hh, color=STEEL, lw=0)
        yt = yc - V31['tang_back']; yt_ = np.linspace(-yt, yt, 400); z1 = -sag(x, yt_) - nm.planed(x)
        ax.fill_between(yt_, z1 - P['tang_d'], z1, color='0.45', lw=0)
    for i in (0, 5):
        ys_ = float(nm.string_y(i, x)); ax.plot([ys_], [float(-sag(x, ys_) - nm.planed(x)) + H + 0.06], 'o', ms=4 if i == 5 else 3, color='tab:red')
    ax.set_aspect('equal')
    if zoom: ax.set_xlim(*zoom[0]); ax.set_ylim(*zoom[1])
def figures(R, B):
    x12 = float(fret_x(12)); xm = 0.5 * (float(fret_x(13)) + float(fret_x(14)))
    # 1. sections with v2 / v3 outlines
    fig, axs = plt.subplots(2, 3, figsize=(15, 8.8), gridspec_kw=dict(width_ratios=[1.6, 1, 1]))
    for r, (x, at, lab) in enumerate(((x12, True, 'at fret 12'), (xm, False, 'mid-cell 14 (deepest scallop)'))):
        hw = float(width(x)) / 2
        for c, ax in enumerate(axs[r]):
            draw31(ax, x, at, zoom=None if c == 0 else (((-hw - 0.01, -hw + 0.24), (-0.50, 0.08)) if c == 1 else ((hw - 0.24, hw + 0.01), (-0.50, 0.08))))
            for k, col in ((('v2', 'tab:blue'), ('v3', 'tab:green')) if r == 0 else ()):
                py, pz = B[k]['poly']['f12']; ax.plot(np.r_[py, py[:1]], np.r_[pz, pz[:1]], color=col, lw=0.9, ls='--', label=f'{k} plain section at fret 12' if (r == 0 and c == 0) else None)
        axs[r, 0].set_ylim(-1.05, 0.12); axs[r, 0].set_title(f'v3.1 section {lab}; dotted = glue line', fontsize=9)
        axs[r, 1].set_title('treble edge', fontsize=9); axs[r, 2].set_title('bass edge', fontsize=9)
    axs[0, 0].legend(fontsize=7, loc='lower left')
    fig.text(0.01, 0.005, f'roll {roll_a31():.3f} x {roll_b31():.3f} (superellipse n {V31["n"]}), side wall to {s_v():.3f},\nquintic shoulder to the vintage-width back at {V31["s_j"]:.2f} below the edge (G2);\ngrey: crown with ground taper ({V31["L"]:.3f} long, tip {V31["t_tip"]:.3f}) ending at the roll start;\ndark: tang (section through it); red: outer strings', fontsize=7, va='bottom')
    fig.text(0.55, 0.005, 'mid-cell: the roll is translated down by the scallop depth; the shoulder below is the same at every x', fontsize=7, va='bottom')
    fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig(os.path.join(FIG, 'v31_sections.png'), dpi=130); plt.close(fig)

    # 2. side elevation, bass edge
    fig, ax = plt.subplots(figsize=(14, 5.4))
    xx = np.linspace(float(fret_x(9)) - 0.25, float(fret_x(16)) + 0.25, 3000); hw = width(xx) / 2; yc = hw - roll_a31()
    ze = sag(xx, hw) + nm.planed(xx); pl = nm.planed(xx)
    z_rs = -sag(xx, yc) - nm.planed(xx) - nm.scallop_long(xx) + pl
    z_wall = -ze - roll_b31() - nm.scallop_long(xx) + pl
    z_sv = -ze - s_v() + pl
    z_g = np.array([float(v2.glue_z(x, h)) for x, h in zip(xx, hw)]) + pl
    z_sj = -ze - V31['s_j'] + pl
    ax.fill_between(xx, np.maximum(z_g, z_sv - 0.2), z_rs, color=ROSE, alpha=0.35, lw=0); ax.fill_between(xx, z_sj, z_g, color=MAPLE, lw=0, alpha=0.7)
    ax.plot(xx, z_rs, color=ROSE, lw=1.6, label='edge top line (roll start): dips by the scallop depth')
    ax.plot(xx, z_wall, color='k', lw=1.0, label=f'roll bottom = top of the straight side wall (roll start - {roll_b31():.3f})')
    ax.plot(xx, z_sv, color='0.3', lw=1.0, ls='--', label=f'shoulder start, straight ({s_v():.3f} below the edge)')
    ax.plot(xx, z_g, 'k:', lw=1.4, label='glue line (0.140 below the edge)')
    ax.plot(xx, z_sj, color='tab:blue', lw=0.8, ls='-.', label=f'shoulder meets the back ({V31["s_j"]:.2f} below the edge)')
    for n_ in range(9, 17):
        xf = float(fret_x(n_)); hwf = float(width(xf)) / 2; z0 = float(-sag(xf, hwf - roll_a31()))
        dx = np.linspace(-CW, CW, 80); ax.fill_between(xf + dx, z0, z0 + np.nan_to_num(steel_z(dx, np.full_like(dx, -0.001))), color=STEEL, zorder=5)
    ax.text(float(fret_x(9)) + 0.02, -0.02, f'grey: fret ends seen from the side at the tip ({V31["t_tip"]:.3f} high, flush with the roll start)', fontsize=7)
    ax.set_ylim(-0.64, 0.0); ax.set_xlabel('x from nut (in)'); ax.set_ylabel('z (in), board-top centre = 0')
    ax.legend(fontsize=7, loc='lower right', ncol=2); ax.set_title('v3.1 side elevation, bass edge, frets 9-16 (vertical scale x4)', fontsize=9)
    ax.set_aspect(4); fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v31_side_edge.png'), dpi=130); plt.close(fig)

    # 3. fret-end close-up: section along the fret, top view, side view
    x0 = x12; hw = float(width(x0)) / 2; yc = hw - roll_a31(); L = V31['L']
    fig = plt.figure(figsize=(18, 7.2)); gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.2, 1])
    ax = fig.add_subplot(gs[0, 0])
    y = np.linspace(yc - L - 0.05, hw + 0.004, 4000); zw = nm.top_z(x0, y) + sag(x0, y) + nm.planed(x0)
    zg = v2.glue_z(x0, y) + sag(x0, y) + nm.planed(x0); zb = bottom3(np.full_like(y, x0), y) + sag(x0, y) + nm.planed(x0)
    ok = zw > -5; ax.fill_between(y[ok], np.maximum(zg, zb)[ok], zw[ok], color=ROSE)
    yy = np.linspace(hw - 0.30, hw, 1200); zb2 = bottom3(np.full_like(yy, x0), yy) + sag(x0, yy) + nm.planed(x0); zg2 = v2.glue_z(x0, yy) + sag(x0, yy) + nm.planed(x0)
    ax.fill_between(yy, zb2, np.minimum(zg2, nm.top_z(x0, yy) + sag(x0, yy) + nm.planed(x0)), where=zg2 > zb2, color=MAPLE)
    ax.plot(yy, np.where(zg2 > zb2, zg2, np.nan), 'k:', lw=0.8)
    hst = steel_h(y - yc)[0]; ax.fill_between(y, np.where(np.isfinite(hst), 0, np.nan), hst, color=STEEL, ec='0.3', lw=0.6)
    yse = yc - V31['slot_back']; yt = yc - V31['tang_back']
    ax.fill_between(np.linspace(y[0], yt, 50), -P['tang_d'], 0, color='0.45', lw=0); ax.plot([yse, yse], [0, -P['slot_d']], color='w', lw=1.0)
    ax.plot([y[0], yse], [-P['slot_d'], -P['slot_d']], color='w', lw=0.6, ls='--')
    for k_, (yv, t_) in enumerate(((yc - L, 'full crown ends'), (yt, 'tang nipped'), (yse, 'slot stop'), (yc - (1 - xi_usable()) * L, '90 % height (usable end)'), (yc, f'tip {V31["t_tip"]:.3f} = roll start'))):
        ax.axvline(yv, color='0.5', lw=0.5, ls=':'); ax.annotate(t_, (yv, 0.045 - 0.0001), xytext=(y[0] + 0.002, 0.090 - 0.011 * k_), fontsize=7, arrowprops=dict(arrowstyle='-', color='0.5', lw=0.5))
    yvu = float(width_v(x0)) / 2 - v3.bevel_usable(); ax.axvline(yvu, color='tab:blue', lw=0.8, ls='--'); ax.text(yvu, -0.10, ' vintage usable end', color='tab:blue', fontsize=7)
    ax.axvline(float(width_v(x0)) / 2, color='tab:blue', lw=0.6, ls=':'); ax.text(float(width_v(x0)) / 2, -0.13, ' vintage edge', color='tab:blue', fontsize=7)
    ax.set_xlim(y[0], hw + 0.005); ax.set_ylim(-0.17, 0.10); ax.set_aspect('equal')
    ax.set_title(f'(a) section along fret 12, bass end: ground taper {L:.3f} on flat wood,\ntip tangent at the roll start, wood roll beyond; steel and wood only', fontsize=9)
    ax.set_xlabel('y (in, from the centreline)'); ax.set_ylabel('z above the board top (in)')
    # top view
    ax = fig.add_subplot(gs[0, 1])
    X = np.linspace(x0 - 0.12, x0 + 0.12, 400); Y = np.linspace(yc - L - 0.04, hw + 0.002, 300); XX, YY = np.meshgrid(X, Y, indexing='ij')
    ZW = nm.top_z(XX, YY) + sag(XX, YY) + nm.planed(XX); SZ = steel_z(XX - x0, YY - yc)
    Z = np.where(np.isfinite(SZ), SZ, np.where(ZW > -5, ZW, np.nan))
    cs = ax.contourf(XX, YY, Z, levels=np.r_[np.linspace(-0.12, 0, 13), np.linspace(0.004, 0.044, 11)], cmap='copper'); fig.colorbar(cs, ax=ax, label='height above the board plane (in)')
    ax.contour(XX, YY, np.nan_to_num(SZ, nan=-1), levels=[0.0005, 0.9 * H], colors=['w', 'tab:cyan'], linewidths=0.8)
    ax.plot(X, np.full_like(X, yc), 'k--', lw=0.8); ax.plot(X, np.full_like(X, hw), 'k', lw=1.2)
    ax.text(X[3], yc + 0.002, 'roll start = steel tip (nose apex)', fontsize=7); ax.text(X[3], hw - 0.006, 'board edge', fontsize=7)
    ax.text(X[3], yc - (1 - xi_usable()) * L - 0.006, 'cyan: 90 % crown height', fontsize=7, color='tab:cyan')
    ax.set_aspect('equal'); ax.set_xlabel('x (in)'); ax.set_ylabel('y (in)'); ax.set_title(f'(b) top view: rounded steel nose (r {V31["r_nose"]:.3f}) blends into the flat wood; roll beyond', fontsize=9)
    # side view: crown silhouettes at stations
    ax = fig.add_subplot(gs[0, 2]); dx = np.linspace(-CW, CW, 400)
    for frac, col in ((0.0, '0.2'), (0.25, '0.35'), (0.5, '0.5'), (0.75, '0.65'), (0.95, '0.8')):
        yr = -L + frac * L; ax.plot(dx, np.nan_to_num(steel_z(dx, np.full_like(dx, yr))), color=col, lw=1.4, label=f'{frac * L:.3f} into the taper (t = {float(steel_h(np.array(yr))[0]):.3f})')
    ax.axhline(0, color=ROSE, lw=2); ax.set_aspect('equal'); ax.set_ylim(-0.01, 0.05); ax.legend(fontsize=7)
    ax.set_xlabel('x across the crown (in)'); ax.set_ylabel('z (in)')
    ax.set_title('(c) side view (looking along the fret): the crown section\nshrinks and flattens to meet the wood tangentially (ground, not bent)', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v31_fret_end_blend.png'), dpi=130); plt.close(fig)

    # 4. end sections A, fret 12, B vs v2 / v3
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.2))
    for ax, (lab, x) in zip(axs, (('A (nut)', 0.02), ('fret 12', x12), ('B (x_h)', v2.XH))):
        yy, zz = nm.section_polygon(x, scallops=False); ax.fill(np.r_[yy, yy[:1]], np.r_[zz, zz[:1]], color=MAPLE, ec='#6b4f2a', lw=1.0, label='v3.1')
        key = {'A (nut)': 'A', 'fret 12': 'f12', 'B (x_h)': 'B'}[lab]
        for k, col in (('v2', 'tab:blue'), ('v3', 'tab:green')):
            py, pz = B[k]['poly'][key]; ax.plot(np.r_[py, py[:1]], np.r_[pz, pz[:1]], color=col, lw=0.9, ls='--', label=k)
        ax.set_aspect('equal'); ax.set_title(f'section {lab}', fontsize=9); ax.legend(fontsize=7, loc='lower center')
    fig.suptitle('v3.1 end sections of the one law (vintage-width back + G2 shoulder up to the +0.030 board) vs v2 and v3', fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v31_profile_sections.png'), dpi=130); plt.close(fig)

# ------------------------------------------------------------------------------------------------ main
def main():
    R = {'V31': dict(V31)}
    R['kappa_scan'], kap = kappa_scan(); V31['kappa'] = kap
    B = baselines()
    install()
    R['shoulder_scan'] = shoulder_scan()
    ok = [r['s_j'] for r in R['shoulder_scan'] if r['ok']]
    V31['s_j'] = float(min(ok)) if ok else V31['s_j']; _SH.clear(); nm._EI_CACHE.clear()
    R['V31'] = dict(V31)
    R['roll'] = dict(a=roll_a31(), b=roll_b31(), s_v=s_v(), d_max=d_max(), xi_usable=xi_usable(), v2=B['v2']['roll'], v3=B['v3']['roll'])
    R['shoulder'] = shoulder_metrics(); R['ruled'] = ruled_check31(); R['margins'] = margins()
    R['trade'] = trade_table(); R['bend'] = bend_study(); R['girth_bound'] = girth_bound()
    R['girth'] = {}
    for n_ in v3.FW:
        g = v3.hand_girth(float(fret_x(n_)) if n_ else 0.02)
        R['girth'][n_] = dict(v2_hand=B['v2']['girth'][n_][1], v3_hand=B['v3']['girth'][n_][1], v31_hand=g[1],
                              v2_perim=B['v2']['girth'][n_][0], v3_perim=B['v3']['girth'][n_][0], v31_perim=g[0])
    R['shape'] = []
    for n_ in (1, 12):
        s = v2.shape_metrics(float(fret_x(n_))); s['fret'] = n_; R['shape'].append(s)
    R['glue_fin'] = v3.glue_and_fin_checks(); R['ball'] = v3.ball_limit(); R['wood'] = v3.wood_min(); R['catch'] = v3.catch_v3()
    R['steel_boundary'] = steel_boundary_check(); R['edge_slide'] = edge_slide31(); R['slot_wall'] = slot_wall31(); R['along_fret'] = along_fret_check()
    R['relief'] = nm.relief_design()
    R['modes'] = dict(plain=nm.neck_modes(False).tolist(), scalloped=nm.neck_modes(True).tolist())
    R['EI'] = {n_: v2.EI_section2(float(fret_x(n_)))[0] for n_ in (1, 5, 9, 12)}
    xs = np.linspace(0, X22, 3000); vol = 0.0; dx = xs[1] - xs[0]
    for x in xs:
        hw = float(width(x)) / 2; vol += float(nm.scallop_long(x)) * 2 * (hw - roll_a31()) * dx
    R['scallop_removed_in3_top'] = vol
    figures(R, B)
    R['trade_rerun'] = trade_rerun()
    with open(os.path.join(HERE, 'results_v31.json'), 'w') as fh: json.dump(R, fh, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else float(o))
    report(R)
def rd(d): return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()}
def report(R):
    ks = R['kappa_scan']
    for r in ks: print('kappa', r['kappa'], 'c20', round(r['cells'][20]['catch'], 1), round(r['cells'][20]['flat'], 1), 'worse-than-flat:', [k for k, c in r['cells'].items() if c['catch'] > c['flat'] + 1e-9], 'bound:', [k for k, c in r['cells'].items() if c['kappa_bound']])
    print('== V31', rd({k: v for k, v in R['V31'].items() if not isinstance(v, tuple)}))
    print('== shoulder scan'); [print('  ', rd(r)) for r in R['shoulder_scan']]
    print('== roll', rd({k: v for k, v in R['roll'].items() if not isinstance(v, dict)}), '\n   v2', R['roll']['v2'], '\n   v3', R['roll']['v3'])
    print('== shoulder', rd({k: v for k, v in R['shoulder'].items() if k != 'rows'})); [print('  ', rd(r)) for r in R['shoulder']['rows']]
    print('== ruled', R['ruled'])
    print('== margins'); [print('  ', k, rd(v)) for k, v in R['margins'].items()]
    print('== trade xi_u', round(R['trade']['xi_u'], 4)); [print('  ', rd(r)) for r in R['trade']['rows']]; print('   widen needed', rd(R['trade']['widen_needed']))
    print('== bend'); [print('  ', rd(r)) for r in R['bend']]
    print('== girth'); [print('  ', k, rd(v)) for k, v in R['girth'].items()]
    print('== girth bound', {k: round(v, 4) for k, v in R['girth_bound'].items()})
    print('== trade rerun'); [print('  ', rd(r)) for r in R['trade_rerun']]
    print('== shape'); [print('  ', rd(s)) for s in R['shape']]
    print('== glue/fin', R['glue_fin']); print('== ball', R['ball']); print('== wood', R['wood'])
    print('== catch'); [print('  ', c['cell'], round(c['catch'], 1), round(c['flat'], 1), round(c['d'], 4)) for c in R['catch']]
    print('== edge slide'); [print('  ', rd(r)) for r in R['edge_slide']]
    print('== steel boundary', rd(R['steel_boundary'])); print('== along fret', rd(R['along_fret'])); [print('   slot', r) for r in R['slot_wall']]
    rl = R['relief']; print('== relief planed sag %.4f gap %.4f need %.4f per100 %.4f F %.0f' % (rl['planed_sag'], rl['planed_gap'], rl['rod_need_in'], rl['rod_in_per_100lb'], rl['rod_F_lb']))
    for k, r in rl['rows'].items(): print('  ', k, rd(r))
    print('== modes', R['modes'], 'vol', R['scallop_removed_in3_top']); print('== EI', R['EI'])

if __name__ == '__main__':
    main()
