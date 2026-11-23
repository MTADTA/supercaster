#!/usr/bin/env python3
"""Supercaster II truss rod with the adjuster at the headstock (decision 2026-11-16): path and built-in relief.

Run: body/sim/cache/venv/bin/python -I -B neck/v4/optimize/rod_opt.py
Imports ../neck_v4.py and edits nothing on disk; it overrides the rod entries of N.P in memory.
Single-acting 3/16 compression rod in a curved channel, as SPEC section 8. Roles reversed: adjusting nut near
the nut, fixed anchor in the heel. Path z(t) = zh (1-t) + za t - 4 sag t (1-t) (1 + skew (1-2t)), t from head end to anchor.
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import neck_v4 as N  # noqa
P = N.P
SKEW = [0.0]
_rz0 = N.rod_z


def rod_z(x):
    xa, xw = P['rod_x_anchor'], P['rod_x_wheel']
    t = (np.asarray(x, float) - xa) / (xw - xa)
    return P['rod_z_anchor'] + (P['rod_z_wheel'] - P['rod_z_anchor']) * t - P['rod_sag'] * 4 * t * (1 - t) * (1 + SKEW[0] * (1 - 2 * t))


N.rod_z = rod_z
DX = 0.1
XS = np.arange(0.0, N.XC + 1e-9, DX)


def set_rod(xh, zh, xa, za, sag, skew):
    P['rod_x_anchor'], P['rod_z_anchor'], P['rod_x_wheel'], P['rod_z_wheel'], P['rod_sag'] = xh, zh, xa, za, sag
    SKEW[0] = skew


def under_wood(x):
    """Maple left under the channel floor at its corners."""
    W = N.width(x)
    zb = np.maximum(N.back(x, P['chan_w'] / W), N.back(x, -P['chan_w'] / W))
    return (rod_z(x) - P['chan_w'] / 2) - zb


def max_sag(xh, zh, xa, za, skew, need=0.142):
    x = np.arange(xh, min(xa, N.XC) + 1e-9, 0.05)
    lo, hi = 0.0, 0.6
    for _ in range(40):
        m = 0.5 * (lo + hi)
        set_rod(xh, zh, xa, za, m, skew)
        if under_wood(x).min() >= need:
            lo = m
        else:
            hi = m
    return lo


def build_beam():
    pr = [N.section_props(x, h=0.006) for x in XS]
    N._BEAM.clear()
    N._BEAM['v4'] = (XS, {k: np.array([p[k] for p in pr]) for k in pr[0]})


def authority():
    """Relief removed per lb of rod tension, and string relief (Eb, drop C#)."""
    build_beam()
    xs, k = N.kappa_rod(1.0)
    eta = -N.relief_of(xs, N.deflect(xs, k))[0] if False else None
    v = N.deflect(xs, k)
    # relief_of returns the largest gap; the rod makes negative relief, so measure at the string-relief location
    out = {}
    for name, T in (('Eb', N.tensions(-1, 0)), ('dropCs', N.tensions(-1, 2)), ('E', N.tensions(0, 0))):
        xs2, ks = N.kappa_strings(T)
        vs = N.deflect(xs2, ks)
        r, xr = N.relief_of(xs2, vs)
        out[name] = (r, xr)
    xs2, ks = N.kappa_strings(N.tensions(-1, 0))
    vs = N.deflect(xs2, ks)
    r0, _ = N.relief_of(xs, vs)
    r1, _ = N.relief_of(xs, vs + 100 * v)
    xs3, kse = N.kappa_layer_strain(P['season_strain'])
    season = N.relief_of(xs3, -N.deflect(xs3, kse))[0]
    return (r0 - r1) / 100, out, season


def table(eta, rs, season, tgt=0.012, pre=40.0):
    rows = []
    for r0 in (0.0, 0.003, 0.005, 0.006, 0.007, 0.008, 0.009, 0.010, 0.012):
        slack = r0 + rs
        F = (slack - tgt) / eta
        rows.append(dict(built_in=r0, slack=slack, F_target=F, F_dry=(slack - season - tgt) / eta, F_wet=(slack + season - tgt) / eta,
                         max_relief_worst=slack - season - pre * eta))
    return rows


def main():
    R = {}
    # 0. reproduce v4 (anchor 0.80 / -0.46, wheel 18.70 / -0.40, sag 0.26)
    set_rod(0.80, -0.46, 18.70, -0.40, 0.260, 0.0)
    eta, rel, season = authority()
    xs, B = N.beam()
    print('v4 rod: eta %.5f in per 100 lb, string relief Eb %.4f dropC# %.4f E %.4f, season +/-%.4f, under-wood min %.3f' % (
        eta * 100, rel['Eb'][0], rel['dropCs'][0], rel['E'][0], season, under_wood(np.arange(0.8, N.XC, 0.05)).min()))
    print('neutral axis zc: nut %.3f, fret1 %.3f, fret5 %.3f, fret12 %.3f, joint %.3f' % tuple(np.interp([0, N.FX[1], N.FX[5], N.FX[12], N.XC], xs, B['zc'])))
    R['v4'] = dict(eta_per_100lb=eta * 100, relief=rel, season=season)
    rs = rel['Eb'][0]
    # 1. head-end adjust: sweep
    print('\n zh     za    xa   skew  sag   eta/100lb  slope_head  R_min  under')
    best = []
    for xh in (0.45,):
        for zh in (-0.30, -0.33, -0.36, -0.40):
            for xa in (16.5, 17.5):
                for za in (-0.40, -0.50, -0.60):
                    for skew in (0.0, 0.3, 0.6):
                        sag = max_sag(xh, zh, xa, za, skew)
                        set_rod(xh, zh, xa, za, sag, skew)
                        eta, rel, season = authority()
                        x = np.arange(xh, xa, 0.02)
                        z = rod_z(x)
                        d1 = np.gradient(z, x); d2 = np.gradient(d1, x)
                        Rmin = 1 / np.abs(d2).max()
                        row = dict(xh=xh, zh=zh, xa=xa, za=za, skew=skew, sag=sag, eta100=eta * 100, slope_head=float(-d1[0]), R_min=float(Rmin),
                                   z_deep=float(z.min()), under=float(under_wood(np.arange(xh, N.XC, 0.05)).min()), rs=rel['Eb'][0])
                        best.append(row)
                        print('%.2f  %.2f  %.1f  %.1f  %.3f  %.5f   %.3f      %5.0f  %.3f' % (zh, za, xa, skew, sag, eta * 100, row['slope_head'], Rmin, row['under']))
    R['sweep'] = best
    json.dump(R, open(os.path.join(HERE, 'rod_opt.json'), 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
