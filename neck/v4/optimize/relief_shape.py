#!/usr/bin/env python3
"""Supercaster II: what shape should the fret line have? (2026-11-22)

Run: body/sim/cache/venv/bin/python -I -B neck/v4/optimize/relief_shape.py
The relief is machined in (SPEC 8), so its shape is free. This finds the fret-top line that lets the hardest
pick through without fret contact, for a fixed action, and scores v4's arc against it.

Physics (ideal string, vibrating length l from the fretted fret to the saddle, picked at distance a from the saddle
with a force F square to the board): half a period after release the string is the mirror image of the pluck
triangle, so its lowest excursion at distance s from the fretted fret is
    e(s) = (F/T) * min(s (l - a), a (l - s)) / l .
It leaves the fretted fret downward at slope (F/T)(1 - a/l). The string clears fret k if the static clearance there
exceeds e. The margin m is the largest F/T that clears every fret for every fretted position: a linear programme
in the fret heights and the saddle height.
"""
import json, math, os, sys
import numpy as np
from scipy.optimize import linprog
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import neck_v4 as N  # noqa
P, S, FX = N.P, N.S, N.FX
NF = 22
A12, NUTC = P['action_12'], P['nut_clear']
A_SET = (2.5, 4.0, 6.0)             # pick distance from the saddle, in (bridge pickup to neck pickup)


def env(n, k, a):
    l = S - FX[n]; s = FX[k] - FX[n]
    a = min(a, 0.9 * l)
    return min(s * (l - a), a * (l - s)) / l


def geometry(z, zs):
    """z[1..22] fret tops, zs saddle (string underside). Returns nut underside height and open action at 12 and 22."""
    zn = z[1] - (z[2] - z[1]) / (FX[2] - FX[1]) * FX[1] + NUTC
    line = lambda x: zn + (zs - zn) * x / S
    return zn, line(FX[12]) - z[12], line(FX[22]) - z[22]


def margin(z, zs, a_set=A_SET, detail=False):
    zn, _, _ = geometry(z, zs)
    best = (np.inf, None)
    per_n = []
    for n in range(0, NF):
        x0, z0 = (0.0, zn) if n == 0 else (FX[n], z[n])
        mn = np.inf
        for k in range(n + 1, NF + 1):
            c = z0 + (zs - z0) * (FX[k] - x0) / (S - x0) - z[k]
            for a in a_set:
                e = env(n, k, a)
                if c / e < mn:
                    mn = c / e; arg = (n, k, a)
        per_n.append(mn)
        if mn < best[0]:
            best = (mn, arg)
    return (best[0], best[1], per_n) if detail else best[0]


def solve(a_set=A_SET, a22_max=None, relief_max=None, convex=True, kappa_max=None):
    """Variables: z1..z22, zs, m. Gauge: z1 = z17 = 0 (the straightedge frets). Maximise m."""
    nv = NF + 2
    iz = lambda k: k - 1
    IS, IM = NF, NF + 1
    Aub, bub, Aeq, beq = [], [], [], []
    # nut underside as a linear form in z: zn = c1 z1 + c2 z2 + NUTC
    r = FX[1] / (FX[2] - FX[1])
    def nut_row(scale=1.0):
        row = np.zeros(nv); row[iz(1)] += scale * (1 + r); row[iz(2)] += -scale * r
        return row, scale * NUTC
    for n in range(0, NF):
        for k in range(n + 1, NF + 1):
            # clearance c = z0 (1 - t) + zs t - zk >= m e   with t = (xk - x0)/(S - x0)
            x0 = 0.0 if n == 0 else FX[n]
            t = (FX[k] - x0) / (S - x0)
            for a in a_set:
                row = np.zeros(nv); const = 0.0
                if n == 0:
                    rr, cc = nut_row(1 - t); row += rr; const += cc
                else:
                    row[iz(n)] += 1 - t
                row[IS] += t; row[iz(k)] -= 1
                row[IM] -= env(n, k, a)
                Aub.append(-row); bub.append(const)             # -(c - m e) <= 0  ->  -row.x <= const
    # open action at fret 12
    t = FX[12] / S
    rr, cc = nut_row(1 - t); row = rr.copy(); row[IS] += t; row[iz(12)] -= 1
    Aeq.append(row); beq.append(A12 - cc)
    if a22_max is not None:
        t = FX[22] / S
        rr, cc = nut_row(1 - t); row = rr.copy(); row[IS] += t; row[iz(22)] -= 1
        Aub.append(row); bub.append(a22_max - cc)
    for k in (1, 17):
        row = np.zeros(nv); row[iz(k)] = 1; Aeq.append(row); beq.append(0.0)
    if convex or kappa_max is not None:
        for k in range(2, NF):
            h1, h2 = FX[k] - FX[k - 1], FX[k + 1] - FX[k]
            row = np.zeros(nv)                                   # second divided difference
            row[iz(k - 1)] = 2 / (h1 * (h1 + h2)); row[iz(k)] = -2 / (h1 * h2); row[iz(k + 1)] = 2 / (h2 * (h1 + h2))
            if convex:
                Aub.append(-row); bub.append(0.0)
            if kappa_max is not None:
                Aub.append(row); bub.append(kappa_max)
    if relief_max is not None:
        for k in range(2, 17):
            row = np.zeros(nv); row[iz(k)] = -1; Aub.append(row); bub.append(relief_max)
    c = np.zeros(nv); c[IM] = -1
    bounds = [(-0.2, 0.2)] * NF + [(0.0, 0.5), (0.0, None)]
    res = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub), A_eq=np.array(Aeq), b_eq=np.array(beq), bounds=bounds, method='highs')
    assert res.success, res.message
    z = np.concatenate([[np.nan], res.x[:NF]])
    return z, res.x[IS], res.x[IM]


def shape_from_curvature(kappa_fn):
    """Fret heights from a curvature field on the neck (rigid beyond the body joint), gauge z1 = z17 = 0."""
    xs = np.arange(0.0, N.XC + 1e-9, 0.05)
    v = N.deflect(xs, kappa_fn(xs))
    z = np.array([np.nan] + [float(np.interp(FX[k], xs, v)) if FX[k] <= xs[-1] else 0.0 for k in range(1, NF + 1)])
    return regauge(z)


def regauge(z):
    z = z.copy()
    a = (z[17] - z[1]) / (FX[17] - FX[1])
    z[1:] = z[1:] - z[1] - a * (FX[1:NF + 1] - FX[1])
    return z


def saddle_for_action(z):
    """Saddle height that gives the open action at fret 12."""
    lo, hi = 0.0, 0.5
    for _ in range(60):
        m = 0.5 * (lo + hi)
        if geometry(z, m)[1] < A12:
            lo = m
        else:
            hi = m
    return lo


def relief(z):
    return float(-np.nanmin(z[1:18]))


def report(name, z, zs=None):
    zs = saddle_for_action(z) if zs is None else zs
    m, arg, per = margin(z, zs, detail=True)
    zn, a12, a22 = geometry(z, zs)
    T6 = N.tensions(-1, 2)[5] * 4.4482216
    T1 = N.tensions(-1, 0)[0] * 4.4482216
    print('%-34s relief %.4f  margin F/T %.5f (binds: fretted %d, fret %d, pick at %.1f)  action12 %.3f  action22 %.3f  E6 dropC# clears %.2f N, E1 %.2f N'
          % (name, relief(z), m, arg[0], arg[1], arg[2], a12, a22, m * T6, m * T1))
    return dict(name=name, relief=relief(z), margin=m, binds=arg, per_fret=per, z=[None] + [float(v) for v in z[1:]], saddle=zs, action22=a22)


def main():
    out = {}
    zeros = np.concatenate([[np.nan], np.zeros(NF)])
    out['straight'] = report('straight', zeros)
    # v4 as played: machined arc 0.009 + strings (Eb) - rod at the load that gives 0.012
    xs, B = N.beam()
    k0 = N.built_in(P['relief_built'])
    _, ks = N.kappa_strings(N.tensions(-1, 0))
    _, kr = N.kappa_rod(1.0)
    rel = lambda F: N.relief_of(xs, N.deflect(xs, k0 + ks + F * kr))[0]
    lo, hi = 0.0, 400.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if rel(mid) > P['relief_target'] else (lo, mid)
    Fset = lo
    zv4 = shape_from_curvature(lambda x: np.interp(x, xs, k0 + ks + Fset * kr))
    out['v4_as_played'] = report('v4 as played (rod %.0f lb)' % Fset, zv4)
    # uniform arcs of several reliefs
    for r in (0.004, 0.008, 0.012, 0.016, 0.020):
        kap = N.built_in(r)
        out['arc_%.3f' % r] = report('uniform arc to the joint, %.3f' % r, shape_from_curvature(lambda x: np.full_like(x, kap)))
    # LP optima
    a22 = out['straight']['action22']
    for name, kw in (('LP free (no action limit at 22)', dict()),
                     ('LP, action at 22 <= straight', dict(a22_max=a22)),
                     ('LP, a22 <= straight, relief <= .012', dict(a22_max=a22, relief_max=0.012)),
                     ('LP, a22 <= straight, relief <= .008', dict(a22_max=a22, relief_max=0.008))):
        z, zs, m = solve(**kw)
        out[name] = report(name, z, zs)
        print('    z:', ' '.join('%.4f' % v for v in z[1:]))
        d2 = [2 * ((z[k + 1] - z[k]) / (FX[k + 1] - FX[k]) - (z[k] - z[k - 1]) / (FX[k] - FX[k - 1])) / (FX[k + 1] - FX[k - 1]) for k in range(2, NF)]
        print('    curvature x1e4 (frets 2..21):', ' '.join('%.1f' % (v * 1e4) for v in d2))
    print('    v4 z:', ' '.join('%.4f' % v for v in zv4[1:]))
    out['Fset'] = Fset
    json.dump(out, open(os.path.join(HERE, 'relief_shape.json'), 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
