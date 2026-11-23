#!/usr/bin/env python3
"""Supercaster II fret ends, round 2: the round-1 hand-contact model run on the round-2 candidates.

Same model, same hand positions, same loads as fe_contact.py (imported, unchanged). Writes feel_r2.json and
feel_maps_r2.npz; round 1's feel.json is not touched.

Run:  python -I -B fe_r2_contact.py explore          -> every variant at fret 12 (choosing the candidates)
      python -I -B fe_r2_contact.py final 12         -> the candidates at fret 12, with the board dry and swollen
      python -I -B fe_r2_contact.py final 2 20       -> the candidates at the other frets
      python -I -B fe_r2_contact.py table
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fe_contact as fc  # noqa: E402
import fe_r2_model as r2  # noqa: E402  (registers the round-2 candidates in fe_model)

PATH = os.path.join(HERE, 'feel_r2.json')
FINAL = ['vintage', 'v4', 'rec'] + list(r2.FINAL)
SHIFTS = (0.004, -0.004, -0.008)
SHIFTED = ['vintage', 'rec', 'A_wrap', 'A_twin', 'B_dome', 'C_short', 'C_long', 'C_graded']
KEEP = set(FINAL)


def job(j):
    return fc.run_one(j)


def run(cands, frets, shifted=(), keep=()):
    t0 = time.time()
    jobs = []
    for fret in frets:
        for sc in fc.SCEN:
            for cn in cands:
                jobs.append((cn, sc, fret, 0.0, cn in keep and fret == 12))
            if fret == 12:
                for cn in shifted:
                    for sh in SHIFTS:
                        jobs.append((cn, sc, fret, sh, False))
    results = []
    with Pool(10) as pool:
        for i, r in enumerate(pool.imap_unordered(job, jobs, chunksize=1)):
            results.append(r)
            if (i + 1) % 20 == 0:
                print('  %d / %d jobs, %.0f s' % (i + 1, len(jobs), time.time() - t0), flush=True)
    pflat = {s[0]: fc.flat_peak(s[1], s[5]) for s in fc.SCEN}
    if os.path.exists(PATH):
        out = json.load(open(PATH))
    else:
        out = dict(meta=dict(E_star_psi=fc.E_STAR, grid=fc.DX, window=fc.N * fc.DX, fingers=fc.FINGERS,
                             sweep=[float(fc.SWEEP[0]), float(fc.SWEEP[-1]), len(fc.SWEEP)], flat_peak_psi=pflat,
                             scenarios={s[0]: dict(finger=s[1], side=s[2], angle=s[3], aim=s[4], load_N=s[5], text=s[6]) for s in fc.SCEN},
                             seconds=0.0), feel={}, curves={})
    maps = {}
    for (cn, sn, fret, sh), res, best in results:
        key = cn if sh == 0 else '%s%+d' % (cn, round(sh * 1000))
        out['feel'].setdefault(key, {}).setdefault('fret_%d' % fret, {})[sn] = fc.summarise(res, pflat[sn])
        out['curves'].setdefault(key, {}).setdefault('fret_%d' % fret, {})[sn] = {k: [round(float(v), 6) for v in res[k]] for k in ('pmax', 'psteel', 'pwood', 'fx', 'ride')}
        if best is not None:
            maps['%s|%s' % (cn, sn)] = best
    out['meta']['seconds'] = round(float(out['meta'].get('seconds') or 0) + time.time() - t0, 1)
    json.dump(out, open(PATH, 'w'), indent=1)
    if maps:
        np.savez_compressed(os.path.join(HERE, 'feel_maps_r2.npz'),
                            **{k.replace('|', '__') + '__' + f: v[f] for k, v in maps.items() for f in ('p', 'steel', 'h', 't')},
                            **{k.replace('|', '__') + '__xc': np.array(v['xc']) for k, v in maps.items()})
    print('done in %.0f s' % (time.time() - t0))
    for fret in frets:
        table(out, 'fret_%d' % fret, cands + ['%s%+d' % (c, round(s * 1000)) for c in shifted for s in SHIFTS])


def table(out, fret='fret_12', only=None):
    names = [s[0] for s in fc.SCEN]
    print('\n%s   hardest spot (x flat, s steel / w wood) / steel-only / catch (deg) / lift (thou)' % fret)
    print('%-14s' % '' + ''.join('%-26s' % n for n in names))
    for cn, d in out['feel'].items():
        if fret not in d or (only and cn not in only):
            continue
        print('%-14s' % cn + ''.join('%5.2f%s %4.2f %4.1f %5.1f      ' % (d[fret][n]['peak'], d[fret][n]['on'][0], d[fret][n]['peak_steel'],
                                                                         d[fret][n]['catch_deg'], d[fret][n]['lift'] * 1000) for n in names))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'table'
    if cmd == 'explore':
        fc.selftest()
        run([a for a in sys.argv[2:] if a in r2.fm.CANDS] or (['vintage', 'v4', 'rec'] + list(r2.R2)), (12,))
    elif cmd == 'final':
        fc.selftest()
        frets = tuple(int(a) for a in sys.argv[2:] if a.isdigit()) or (12,)
        run(FINAL, frets, shifted=SHIFTED if 12 in frets else (), keep=KEEP)
    else:
        o = json.load(open(PATH))
        for f in ('fret_12', 'fret_2', 'fret_20'):
            table(o, f)
