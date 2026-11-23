"""Summaries and pairwise comparisons for STUDIES-neck-trem-guard.md (reads results/st_*.json).

  cache/venv/bin/python -I -B study_summary.py BASE_TAG OTHER_TAG [...]     # compare others to the base
  cache/venv/bin/python -I -B study_summary.py --one TAG                     # one case in detail
"""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
TS = 8.0   # string's own T60 at the fundamental without body loss (s) [judged]; combined 1/T = 1/T_body + 1/TS
FN = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def note_name(f):
    n = int(round(12 * np.log2(f / 440.0))) + 57
    return f'{NAMES[n % 12]}{n // 12}'


def load(tag):
    return json.load(open(os.path.join(HERE, 'results', tag + '.json')))


def metrics(R):
    N = R['notes']; T = np.array([n['T60_body_s'] for n in N]); Gf = np.array([n['G_fret'] for n in N]); Gb = np.array([n['G_bridge'] for n in N])
    L = np.array([n['level_dB'] for n in N]); Te = 1 / (1 / T + 1 / TS)
    dead = [f"{N[i]['string']}/{N[i]['fret']} {note_name(N[i]['f'])} {T[i]:.1f}s" for i in range(len(N)) if T[i] < TS]
    neck = [m for m in R['modes'] if m['label'] == 'neck' and 60 < m['f'] < 800]
    trem = [m for m in R['modes'] if m['shares']['trem'] > 0.4 and m['f'] < 200]
    v = R['velocity_dB_re_1mps_per_N']
    return dict(mass=R['mass_kg'], bal=R['balance_x_in'], bands=R['power_dB_re_1pW_per_N2'],
                T60_min=float(T.min()), T60_med=float(np.median(T)), T60_geo=float(np.exp(np.mean(np.log(T)))),
                spread=float(np.std(np.log(T))), past=R['notes_past_halving'], neck_dom=int((Gf > Gb).sum()),
                worst=[(N[i]['string'], N[i]['fret'], note_name(N[i]['f']), N[i]['T60_body_s'], round(Gf[i] / (Gf[i] + Gb[i]), 2)) for i in np.argsort(T)[:6]],
                neck_modes=[(m['f'], m['eta']) for m in neck][:8], trem_modes=[(m['f'], m['eta'], m['shares']['trem']) for m in trem],
                A0=R['A0']['f_coupled'] if R['A0'] else None, twist=R['twist_mode']['f'] if R['twist_mode'] else None,
                vel={k: v[k] for k in ('belly', 'forearm', 'neck_back', 'mid_chamber')},
                fret_peak=R['fret_conductance_s_per_kg']['peak'], bridge_peak=R['bridge_conductance_mean_6']['peak'],
                bridge_band=R['bridge_conductance_mean_6']['band_mean'], T=T, L=L, N=N, Te=Te,
                Te_geo=float(np.exp(np.mean(np.log(Te)))), Te_min=float(Te.min()), Te_spread=float(np.std(np.log(Te))), dead=dead)


def compare(a, b, la, lb):
    A, B = metrics(a), metrics(b)
    dT = B['Te'] / A['Te'] - 1; dL = B['L'] - A['L']
    print(f'--- {lb} vs {la}')
    print(f"mass {B['mass']:.3f} ({1000 * (B['mass'] - A['mass']):+.0f} g), balance {B['bal']:.2f} in ({B['bal'] - A['bal']:+.2f})")
    print('bands', B['bands'], 'delta', [round(x - y, 2) for x, y in zip(B['bands'], A['bands'])])
    print(f"T60 min {A['T60_min']:.2f}->{B['T60_min']:.2f}  geo-mean {A['T60_geo']:.2f}->{B['T60_geo']:.2f}  spread(ln) {A['spread']:.3f}->{B['spread']:.3f}  "
          f"past-halving {A['past']}->{B['past']}  neck-dominated {A['neck_dom']}->{B['neck_dom']}")
    print(f"T_eff (string {TS}s) geo {A['Te_geo']:.2f}->{B['Te_geo']:.2f} min {A['Te_min']:.2f}->{B['Te_min']:.2f} spread {A['Te_spread']:.3f}->{B['Te_spread']:.3f}")
    print(f"dead (T_body<{TS}s) {len(A['dead'])}->{len(B['dead'])}:", B['dead'])
    print('neck modes', A['neck_modes'][:6], '->', B['neck_modes'][:6])
    print('trem modes', A['trem_modes'], '->', B['trem_modes'])
    print('A0', A['A0'], '->', B['A0'], ' twist', A['twist'], '->', B['twist'])
    print('vel', {k: [round(x - y, 2) for x, y in zip(B['vel'][k], A['vel'][k])] for k in B['vel']})
    big = [(n['string'], n['fret'], note_name(n['f']), round(100 * dT[i]), round(dL[i], 1)) for i, n in enumerate(A['N'])
           if abs(dT[i]) >= 0.15 or abs(dL[i]) >= 3]
    print(f'notes with |dT_eff|>=15% or |dL|>=3 dB ({len(big)}):', big)
    print('worst', B['worst'])
    return A, B


def one(R):
    M = metrics(R)
    for k, v in M.items():
        if k not in ('T', 'L', 'N'): print(k, v)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[0] == '--one':
        one(load(args[1]))
    else:
        base = load(args[0])
        for t in args[1:]: compare(base, load(t), args[0], t)
