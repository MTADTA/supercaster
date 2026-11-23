#!/usr/bin/env python3
"""Supercaster II fret ends: what the skin sees.

A soft finger (an elastic half-space, frictionless) is pressed with a fixed force onto the finished neck edge
and slid along the neck past a fret. The neck is rigid. The solver is the standard conjugate-gradient contact
method with FFT convolution (Polonsky and Keer 1999; Love's rectangle solution for the influence function).

For each candidate fret end it reports, per scenario:
    peak     the hardest pressure anywhere under the finger during the pass, as a multiple of the peak the same
             finger makes on a flat smooth surface (1.0 = feels like nothing is there)
    catch    the largest sideways drag the shape puts on the sliding finger, as the slope it is equivalent to (deg)
    lift     how far the finger rides up and down during the pass
    on       which material carries the peak (steel or wood)

This is a comparison tool. Skin is not a linear half-space; the stiffness and loads are judged values, and the
ranking between shapes is what should be trusted, not the absolute pressures.

Run:  python -I -B fe_contact.py selftest     -> Hertz check
      python -I -B fe_contact.py run          -> feel.json  (about 5 minutes on 10 cores)
"""
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy import fft as sfft

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fe_model as fm  # noqa: E402

n4 = fm.n4
E_STAR = 20.0            # psi: plane-strain modulus of finger pulp, about 0.14 MPa  [judged, order of the literature]
DX = 0.004               # grid, in
N = 192                  # grid points each way: a window 0.77 square
LBF_PER_N = 0.2248

FINGERS = {              # radius along the neck, radius across                                    [judged]
    'tip': (0.30, 0.30),              # fingertip: the 0.30 radius used in SPEC section 4
    'index': (0.35, 1.20),            # side of the index finger lying across the treble edge
    'thumb': (0.45, 0.90),            # thumb wrapped over the bass edge
}
# name, finger, side, angle above side-on, aim point on the edge (s, z from the nominal corner), load in N, text
SCEN = [
    ('index_side', 'index', 'T', 20.0, (0.02, -0.04), 1.0, 'Side of the index finger sliding along the treble edge, hand low (20 deg), light'),
    ('index_45', 'index', 'T', 45.0, (0.03, -0.02), 1.0, 'Side of the index finger sliding along the treble edge at 45 deg, light'),
    ('tip_slide', 'tip', 'T', 65.0, (0.06, 0.0), 1.0, 'Fingertip sliding along the high E, pad overlapping the fret ends'),
    ('tip_above', 'tip', 'T', 85.0, (0.045, 0.0), 1.0, 'Fingertip coming down on a treble fret end from above'),
    ('thumb_45', 'thumb', 'B', 45.0, (0.03, -0.02), 1.0, 'Thumb sliding along the bass edge at 45 deg, light'),
    ('thumb_over', 'thumb', 'B', 70.0, (0.05, -0.01), 3.0, 'Thumb wrapped over the bass edge (thumb-over), gripping'),
]
SWEEP = np.arange(-0.40, 0.4001, 0.020)        # finger centre relative to the fret, along the neck

_K = {}


def kernel(n=N, dx=DX):
    """Surface deflection at each grid point from unit pressure on one cell (Love 1929), FFT-ready."""
    key = (n, dx)
    if key in _K:
        return _K[key]
    a = dx / 2
    i = np.arange(2 * n)
    i = np.where(i < n, i, i - 2 * n) * dx
    X, Y = np.meshgrid(i, i, indexing='ij')

    def f(x, y):
        return x * np.log(y + np.sqrt(x * x + y * y)) + y * np.log(x + np.sqrt(x * x + y * y))

    k = f(X + a, Y + a) + f(X - a, Y - a) - f(X + a, Y - a) - f(X - a, Y + a)
    _K[key] = sfft.rfft2(k / (math.pi * E_STAR))
    return _K[key]


def conv(p, Kf):
    n = p.shape[0]
    pp = np.zeros((2 * n, 2 * n))
    pp[:n, :n] = p
    return sfft.irfft2(sfft.rfft2(pp) * Kf, s=pp.shape)[:n, :n]


def solve(gap, load, tol=2e-5, itmax=400):
    """Pressure for a rigid surface with initial separation `gap` (finger minus neck) under a total load.
    Returns p, rigid approach."""
    Kf = kernel(gap.shape[0])
    dA = DX * DX
    p = np.full(gap.shape, load / (gap.size * dA))
    G_old, t_old, delta = 1.0, np.zeros_like(p), 0.0
    appr = 0.0
    for it in range(itmax):
        u = conv(p, Kf)
        g = u + gap
        c = p > 0
        gbar = g[c].mean()
        g = g - gbar
        G = float((g[c] ** 2).sum())
        t = np.where(c, g + delta * (G / G_old) * t_old, 0.0)
        G_old = G
        r = conv(t, Kf)
        r = r - r[c].mean()
        den = float((r[c] * t[c]).sum())
        tau = float((g[c] * t[c]).sum()) / den if den != 0 else 0.0
        p_old = p
        p = np.clip(p - tau * t, 0, None)
        ov = (p == 0) & (g < 0)
        if ov.any():
            p = p + np.where(ov, -tau * g, 0.0)
            delta = 0.0
        else:
            delta = 1.0
        p = p * (load / (p.sum() * dA))
        t_old = t
        appr = -gbar
        if dA * np.abs(p - p_old).sum() / load < tol:
            break
    return p, appr


def finger_shape(fg, dxg, dtg):
    Rx, Rt = FINGERS[fg]
    fx = Rx - np.sqrt(np.clip(Rx * Rx - dxg ** 2, 1e-6, None))
    ft = Rt - np.sqrt(np.clip(Rt * Rt - dtg ** 2, 1e-6, None))
    return fx[:, None] + ft[None, :] + np.where(np.abs(dxg)[:, None] > 0.97 * Rx, 1.0, 0.0)


def flat_peak(fg, load_n):
    d = (np.arange(N) - N / 2 + 0.5) * DX
    p, _ = solve(finger_shape(fg, d, d), load_n * LBF_PER_N)
    return float(p.max())


def run_one(job):
    """One candidate, one scenario, one fret: sweep the finger past the fret."""
    cname, scen, fret, shift, keep = job
    c = fm.CANDS[cname]
    name, fg, side, phi, aim, load_n, _ = scen
    load = load_n * LBF_PER_N
    ph = math.radians(phi)
    tc = aim[0] * math.sin(ph) + aim[1] * math.cos(ph)
    xf = float(n4.FX[fret])
    half = N * DX / 2
    # the neck as this hand sees it, over the whole sweep
    nx_all = int(round((SWEEP[-1] - SWEEP[0] + 2 * half) / DX)) + 1
    x_all = xf + SWEEP[0] - half + DX * np.arange(nx_all)
    H, M, tg = fm.view_field(c, side, x_all, phi, dt=DX, t_lo=tc - half, t_hi=tc + half - DX, steel_shift=shift)
    H, M, tg = H[:, :N], M[:, :N], tg[:N]
    dH = np.gradient(H, DX, axis=0)
    dxg = (np.arange(N) - N / 2 + 0.5) * DX
    fsh = finger_shape(fg, dxg, tg - tc)
    out = dict(pmax=[], psteel=[], pwood=[], fx=[], ride=[], area=[])
    best = (-1, None)
    for xc in SWEEP:
        i0 = int(round((xc - SWEEP[0]) / DX))
        h = H[i0:i0 + N]
        p, appr = solve(fsh - h, load)
        m = M[i0:i0 + N]
        out['pmax'].append(float(p.max()))
        out['psteel'].append(float(p[m].max()) if m.any() else 0.0)
        out['pwood'].append(float(p[~m].max()))
        out['fx'].append(float((p * dH[i0:i0 + N]).sum() * DX * DX / load))
        out['ride'].append(float(appr))
        out['area'].append(float((p > 0).sum() * DX * DX))
        if keep and p.max() > best[0]:
            best = (float(p.max()), dict(p=p.astype(np.float32), steel=m.copy(), xc=float(xc), h=h.astype(np.float32), t=tg.copy()))
    res = {k: np.array(v) for k, v in out.items()}
    return (cname, name, fret, shift), res, best[1]


def summarise(res, pflat):
    i = int(np.argmax(res['pmax']))
    ride = -res['ride']                           # finger height
    return dict(peak=float(res['pmax'].max() / pflat), peak_steel=float(res['psteel'].max() / pflat),
                peak_wood=float(res['pwood'].max() / pflat), on='steel' if res['psteel'][i] >= res['pwood'][i] else 'wood',
                catch_deg=float(np.degrees(np.arctan(np.abs(res['fx']).max()))), lift=float(ride.max() - ride.min()),
                peak_at=float(SWEEP[i]), base=float(np.median(res['pmax']) / pflat))


def selftest():
    fg = 'tip'
    R, F = FINGERS[fg][0], 2.0 * LBF_PER_N
    d = (np.arange(N) - N / 2 + 0.5) * DX
    p, appr = solve(finger_shape(fg, d, d), F)
    appr = -appr
    a = (3 * F * R / (4 * E_STAR)) ** (1 / 3)
    p0 = 3 * F / (2 * math.pi * a * a)
    print('Hertz check, sphere R %.2f on a flat: contact radius %.4f (closed form %.4f), peak %.3f psi (closed form %.3f), approach %.4f (%.4f)'
          % (R, math.sqrt((p > 0).sum() * DX * DX / math.pi), a, p.max(), p0, appr, a * a / R))
    assert abs(p.max() / p0 - 1) < 0.04


JOB_CANDS = ['vintage', 'v4', 'uniform', 'bullet', 'short', 'mid', 'long', 'pocket', 'rec', 'bullet_plat', 'bullet_t016',
             'mid_d', 'rec_d08', 'bullet_tight', 'fallback']
SHIFTED = [('v4', 0.004), ('rec', 0.004), ('v4', -0.004), ('rec', -0.004)]
KEEP = {'vintage', 'v4', 'rec'}
MAIN_CANDS = ['vintage', 'v4', 'uniform', 'bullet', 'pocket', 'rec', 'fallback']     # enough to confirm other frets


def run(frets=(2, 12, 20), merge=False, cands=None):
    """Run the sweeps for the given frets. merge=True adds them to an existing feel.json (use it to run one fret
    at a time: fret 12 first without merge, then the others with it)."""
    t0 = time.time()
    jobs = []
    for fret in frets:
        for sc in SCEN:
            for cn in (cands or JOB_CANDS):
                jobs.append((cn, sc, fret, 0.0, cn in KEEP and fret == 12))
            if fret == 12:
                for cn, sh in SHIFTED:
                    jobs.append((cn, sc, fret, sh, False))
    results = []
    with Pool(10) as pool:
        for i, r in enumerate(pool.imap_unordered(run_one, jobs, chunksize=1)):
            results.append(r)
            if (i + 1) % 20 == 0:
                print('  %d / %d jobs, %.0f s' % (i + 1, len(jobs), time.time() - t0), flush=True)
    pflat = {s[0]: flat_peak(s[1], s[5]) for s in SCEN}
    path = os.path.join(HERE, 'feel.json')
    if merge and os.path.exists(path):
        out = json.load(open(path))
    else:
        out = dict(meta=dict(E_star_psi=E_STAR, grid=DX, window=N * DX, fingers=FINGERS, sweep=[float(SWEEP[0]), float(SWEEP[-1]), len(SWEEP)],
                             flat_peak_psi=pflat, scenarios={s[0]: dict(finger=s[1], side=s[2], angle=s[3], aim=s[4], load_N=s[5], text=s[6]) for s in SCEN},
                             seconds=0.0),
                   feel={}, curves={})
    maps = {}
    for (cn, sn, fret, sh), res, best in results:
        key = cn if sh == 0 else '%s%+d' % (cn, round(sh * 1000))
        out['feel'].setdefault(key, {}).setdefault('fret_%d' % fret, {})[sn] = summarise(res, pflat[sn])
        out['curves'].setdefault(key, {}).setdefault('fret_%d' % fret, {})[sn] = {k: [round(float(v), 6) for v in res[k]] for k in ('pmax', 'fx', 'ride')}
        if best is not None:
            maps['%s|%s' % (cn, sn)] = best
    out['meta']['seconds'] = round(float(out['meta'].get('seconds') or 0) + time.time() - t0, 1)
    json.dump(out, open(path, 'w'), indent=1)
    if maps:
        np.savez_compressed(os.path.join(HERE, 'feel_maps.npz'),
                            **{k.replace('|', '__') + '__' + f: v[f] for k, v in maps.items() for f in ('p', 'steel', 'h', 't')},
                            **{k.replace('|', '__') + '__xc': np.array(v['xc']) for k, v in maps.items()})
    print('done in %.0f s' % (time.time() - t0))
    for fret in frets:
        table(out, 'fret_%d' % fret)


def table(out, fret='fret_12'):
    names = [s[0] for s in SCEN]
    print('\n%s   peak pressure (x flat) / catch (deg) / lift (thou)' % fret)
    print('%-14s' % '' + ''.join('%-22s' % n for n in names))
    for cn, d in out['feel'].items():
        if fret not in d:
            continue
        print('%-14s' % cn + ''.join('%5.2f%s %4.1f %5.1f      ' % (d[fret][n]['peak'], d[fret][n]['on'][0], d[fret][n]['catch_deg'], d[fret][n]['lift'] * 1000) for n in names))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if cmd == 'selftest':
        selftest()
    elif cmd == 'table':
        o = json.load(open(os.path.join(HERE, 'feel.json')))
        table(o, 'fret_12')
        table(o, 'fret_2')
        table(o, 'fret_20')
    else:
        # run            all three frets in one go (about 5 minutes on 10 cores)
        # run 12         fret 12 only, starting a fresh feel.json;  run 2 merge / run 20 merge add to it
        # ... main       only the main candidates (used for frets 2 and 20)
        selftest()
        frets = tuple(int(a) for a in sys.argv[2:] if a.isdigit()) or (2, 12, 20)
        run(frets, merge='merge' in sys.argv, cands=MAIN_CANDS if 'main' in sys.argv else None)
