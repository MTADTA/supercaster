"""Thumb-over check of the prototype edge (2026-11-22).  Inches.  Reads the round-1/round-2 models, writes only thumb.json.

The Nov 18 prototype puts the R2 graded flow end on BOTH edges over the centred scallop (study.depth).  The bass edge is where a
thumb-over hand wraps, so this asks whether the bass side should differ.  The contact model is fe_contact.py, unchanged; its
surface is fe_r2_model's with the scallop swapped for the prototype's centred one (study.depth, rail and string-line blend included;
study.run() asserts the offset form of the same function equals the R2 scallop, so the swap is like for like).
Candidates (treble side is the graded end in every case):
  graded        Nov 18 spec: graded end on the bass side too (50 deg / r .040 at fret 1 -> 65 deg / r .030 at fret 22)
  bass_long     bass side = R2 long flow end everywhere (50 deg line, r .040, turnover .040).  The rail start still follows the
                graded roll radius (study.transverse), at most 0.010 different
  shallow_bass  graded ends, scallop at the bass edge 30 % of the treble instead of 50 % (v4 'tilt' 0.5 -> 0.7)
Scenarios: thumb sliding the bass edge at 45 deg, thumb wrapped over and gripping, treble index finger at 45 deg (control).
Frets 2, 12, 20 (the contact model's stations).   Run:  <venv>/python -I -B thumb.py
"""
import json, os, sys, time
import multiprocessing as mp
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'fret-ends'))
import study as st
import fe_contact as fc
import fe_r2_model as r2
fm = r2.fm
n4 = r2.n4
PICK = (-0.4, 0.30, 0.1)
TILT0 = n4.P['tilt']
_flow_parts = r2.flow_parts


def flow_parts(x, s, side, c, steel_shift=0.0):
    if side == 'B' and 'bass' in c:
        c = c['bass']
    return _flow_parts(x, s, side, c, steel_shift)


def scallop(x, y, s, edge, r):
    """The prototype's centred scallop in place of R2's offset one."""
    return st.depth(np.asarray(x, float), np.asarray(y, float), PICK[0], PICK[1], symmetric=True, bowl=PICK[2])


r2.flow_parts = flow_parts
r2.scallop = scallop

G = dict(r2.FINAL['C_graded'])
CANDS = {'graded': G, 'bass_long': dict(G, name='bass_long', bass=dict(r2.FINAL['C_long'])),
         'shallow_bass': dict(G, name='shallow_bass')}
TILT = {'graded': TILT0, 'bass_long': TILT0, 'shallow_bass': 0.7}
fm.CANDS.update(CANDS)
SC = {s[0]: s for s in fc.SCEN}
SCEN = ['thumb_45', 'thumb_over', 'index_45']
FRETS = (2, 12, 20)


def init(t):
    n4.P['tilt'] = t


def job(j):
    return fc.run_one(j)


def run_set(names, tilt):
    jobs = [(c, SC[s], f, 0.0, False) for c in names for s in SCEN for f in FRETS]
    with mp.get_context('fork').Pool(10, initializer=init, initargs=(tilt,)) as pool:
        return pool.map(job, jobs, chunksize=1)


def low_E_trough(tilt):
    n4.P['tilt'] = tilt
    k = np.array(FRETS); xa, xb, *_ = n4.cell_geometry(k); mid = (xa + xb) / 2
    d = st.depth(mid, n4.string_y(mid)[5], *PICK[:2], symmetric=True, bowl=PICK[2])
    h = st.depth(mid, n4.string_y(mid)[0], *PICK[:2], symmetric=True, bowl=PICK[2])
    n4.P['tilt'] = TILT0
    return {('cell_%d' % kk): dict(low_E=round(float(a), 4), high_E=round(float(b), 4)) for kk, a, b in zip(k, d, h)}


if __name__ == '__main__':
    t0 = time.time()
    pflat = {s: fc.flat_peak(SC[s][1], SC[s][5]) for s in SCEN}
    res = run_set(['graded', 'bass_long'], TILT0) + run_set(['shallow_bass'], 0.7)
    out = dict(note=__doc__, feel={}, margins={}, trough={})
    for (cn, sn, fret, _), r, _b in res:
        out['feel'].setdefault(cn, {}).setdefault('fret_%d' % fret, {})[sn] = fc.summarise(r, pflat[sn])
    for cn in CANDS:
        init(TILT[cn])
        m = fm.margins(fm.CANDS[cn])
        out['margins'][cn] = {k: {sd: round(float(v[sd]['to_full']), 4) for sd in 'TB'} for k, v in m.items()}
        out['trough'][cn] = low_E_trough(TILT[cn])
    init(TILT0)
    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, 'thumb.json'), 'w'), indent=1)
    for cn in CANDS:
        for f in FRETS:
            row = out['feel'][cn]['fret_%d' % f]
            print('%-12s fret %2d ' % (cn, f) + '  '.join('%s peak %.2f catch %.1f lift %.4f' % (s, row[s]['peak'], row[s]['catch_deg'], row[s]['lift']) for s in SCEN))
        print('   full height outside the string:', out['margins'][cn])
        print('   trough depth:', out['trough'][cn])
    print('seconds', out['seconds'])
