#!/usr/bin/env python3
"""Supercaster II headstock: joint optimum over tilt, face step, post heights (2026-11-22).

Run: body/sim/cache/venv/bin/python -I -B neck/v4/optimize/head_opt.py
Imports ../headstock/break_opt.py (geometry, floors, capstan error) and edits nothing.
Question: what is the smallest visible change that seats every string in Eb and drop C# with margin,
and what does it cost in trem return error?
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'headstock'))
import break_opt as BO  # noqa
N = BO.N
MM = BO.MM
T_HEAD = 0.54                         # MG-T max head 13.75 mm
D_NUT = BO.D_NUT
F_STEP = D_NUT - T_HEAD               # face drop at the nut that keeps the back flush with the neck back (no volute)
STAG = [20, 20, 20, 18.5, 18.5, 18.5]
FLAT185 = [18.5] * 6
WR = [1, 1, 1, 1, 1, 0.5]


def ev(H, tilt, B=None, wraps=WR, x1=1.85, t=T_HEAD):
    B = D_NUT if B is None else B
    return BO.evaluate(B, H, wraps, x1, t, tilt_deg=tilt)['rows']


def stats(rows, mu=0.20):
    eff = [r['break_eff_deg'] for r in rows]
    clr = [r['clear_deg'] for r in rows]
    err = [r['err_mu0.20_c'] * mu / 0.20 for r in rows]
    return dict(eff=[round(x, 2) for x in eff], min_eff=min(eff), min_clear=min(clr), worst_err=max(err), sum_err=sum(err),
                err=[round(x, 2) for x in err])


def hapm_equalise(tilt, target, lo=16.0, hi=20.5, wraps=(0.5,) * 6, B=None):
    """Per-string hole height (0.5 mm steps) that brings each string as close as possible to target from above."""
    H = []
    for i in range(6):
        best = lo
        for h in np.arange(hi, lo - 1e-9, -0.5):
            r = ev([h] * 6, tilt, B=B, wraps=list(wraps))[i]
            if r['break_eff_deg'] >= target:
                best = h
                break
        H.append(float(best))
    return H


def main():
    out = dict(F_STEP=F_STEP, D_NUT=D_NUT)
    print('flush face step at nut %.3f (B = neck depth %.3f, head %.2f)' % (F_STEP, D_NUT, T_HEAD))
    # 1. frontier: least tilt for a target minimum angle
    print('\n-- frontier: tilt vs weakest string, fixed post sets (1 wrap, E6 half) --')
    fr = []
    for name, H in (('gotoh_stag', STAG), ('flat_18.5', FLAT185)):
        for tilt in np.arange(0, 4.01, 0.25):
            s = stats(ev(H, tilt))
            fr.append(dict(posts=name, tilt=float(tilt), **s))
            if abs(tilt * 2 - round(tilt * 2)) < 1e-9:
                print('%-10s tilt %.2f eff %s min %.2f clear %.2f worst %.2fc sum %.1fc' % (name, tilt, s['eff'], s['min_eff'], s['min_clear'], s['worst_err'], s['sum_err']))
    out['frontier_fixed'] = fr
    print('\n-- HAP-M equalised at target (0.5 wrap): tilt needed and error --')
    eq = []
    for target in (3.5, 4.0, 4.5, 5.0):
        for tilt in np.arange(0, 4.01, 0.25):
            H = hapm_equalise(tilt, target)
            s = stats(ev(H, tilt, wraps=[0.5] * 6))
            if s['min_eff'] >= target - 1e-6:
                eq.append(dict(target=target, tilt=float(tilt), H=H, **s))
                print('target %.1f: tilt %.2f H %s eff %s worst %.2fc sum %.1fc' % (target, tilt, H, s['eff'], s['worst_err'], s['sum_err']))
                break
    out['hapm_equalised'] = eq
    # 2. what the E6 angle costs, any design: error ~ K mu phi L/(S+L)
    L6 = ev(STAG, 0)[5]['L_in']
    out['E6_cents_per_deg_mu020'] = BO.K_CENT * 0.20 * math.radians(1) * L6 / (BO.S + L6)
    print('\nE6: %.3f cents per degree of wrap at mu 0.20 (L %.2f)' % (out['E6_cents_per_deg_mu020'], L6))
    # 3. tolerance: pivot offset, post-height error, nut-slot height
    print('\n-- candidate checks --')
    for name, H, tilt, wr in (('A stag 2.0', STAG, 2.0, WR), ('B stag 2.5', STAG, 2.5, WR), ('C flat18.5 2.0', FLAT185, 2.0, WR), ('D flat18.5 2.5', FLAT185, 2.5, WR)):
        s = stats(ev(H, tilt, wraps=wr))
        s0 = stats(ev(H, tilt, wraps=[0] * 6))
        hi = stats(ev([h + 1.0 for h in H], tilt, wraps=wr))          # posts 1 mm taller than the retailer figure
        print('%-14s eff %s | 0 wraps min %.2f | posts +1 mm min %.2f | worst %.2fc (mu .10: %.2fc)' % (name, s['eff'], s0['min_eff'], hi['min_eff'], s['worst_err'], s['worst_err'] / 2))
        out[name] = dict(base=s, zero_wraps=s0, posts_plus_1mm=hi)
    json.dump(BO.clean(out), open(os.path.join(HERE, 'head_opt.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
