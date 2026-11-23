"""Landing-independent dead-spot metrics for STUDIES-neck-trem-guard.md.

A neck mode can sit anywhere within about +-10 % of its computed frequency (board-to-board variation and model error,
see acoustic-hybrid.md section 1). So instead of reading each note's decay at one frequency, each note's fret conductance is
read over a window f_note x [1/1.1, 1.1] (log-uniform), and the decay is averaged over that window:
  T_body(f) = 6.91 L / (T (G_bridge(f) + G_fret(f)))         [Pate et al. relation, as used in rom.py]
(bridge conductance is windowed the same way: trem and guard modes are as uncertain as neck modes)
  T_eff = 1 / (1/T_body + 1/TS), TS = 8 s string's own decay [judged]
Outputs per case: expected T_eff geo-mean, worst note, spread of ln T_eff, expected number of dead notes
(window fraction with T_body < TS), peak fret conductance per neck band.

  cache/venv/bin/python -I -B study_deadspots.py [--ts 8] TAG [TAG ...]
"""
import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
TS = 8.0; WIN = 1.10; IN = 0.0254
STR = dict(E2=(82.41, 77.8), A2=(110.0, 86.7), D3=(146.83, 81.8), G3=(196.0, 73.8), B3=(246.94, 68.5), E4=(329.63, 72.1))
SN = list(STR)


def analyse(tag):
    R = json.load(open(os.path.join(HERE, 'results', tag + '.json'))); z = np.load(os.path.join(HERE, 'results', tag + '.npz'))
    f = z['f']; Gf = z['G_fret']; Gs = z['G_saddle_z']  # (nf, 13, 6), (nf, 6)
    Te = np.zeros((6, 13)); pdead = np.zeros((6, 13)); Tpt = np.zeros((6, 13)); Tn_ = np.zeros((6, 13)); pdn = np.zeros((6, 13))
    for nt in R['notes']:
        s = SN.index(nt['string']); n = nt['fret']; f0, Tn = STR[nt['string']]; fn = nt['f']
        L = 25.5 * IN * 2 ** (-n / 12)
        m = (f >= fn / WIN) & (f <= fn * WIN)
        G = Gs[m, s] + Gf[m, n, s]
        Tb = 6.91 * L / (Tn * G)
        w = 1 / f[m]; w = w / w.sum()                    # log-uniform weights on the linear grid
        Te[s, n] = np.exp((w * np.log(1 / (1 / Tb + 1 / TS))).sum())
        pdead[s, n] = (w * (Tb < TS)).sum()
        Tbn = 6.91 * L / (Tn * Gf[m, n, s])                 # neck (fret) loss only
        Tn_[s, n] = np.exp((w * np.log(1 / (1 / Tbn + 1 / TS))).sum()); pdn[s, n] = (w * (Tbn < TS)).sum()
        Tpt[s, n] = 1 / (1 / nt['T60_body_s'] + 1 / TS)
    bands = {}
    for lo, hi in ((140, 230), (230, 420), (420, 700)):
        m = (f >= lo) & (f < hi); g = Gf[m].max(axis=(1, 2)); j = int(np.argmax(g))
        bands[f'{lo}-{hi}'] = (round(float(g[j]), 4), float(f[m][j]))
    return dict(tag=tag, Te_geo=float(np.exp(np.log(Te).mean())), Te_min=float(Te.min()),
                worst=f"{SN[np.unravel_index(Te.argmin(), Te.shape)[0]]}/{np.unravel_index(Te.argmin(), Te.shape)[1]}",
                spread=float(np.log(Te).std()), dead_expected=float(pdead.sum()),
                pt_Te_geo=float(np.exp(np.log(Tpt).mean())), pt_dead=int((np.array([n['T60_body_s'] for n in R['notes']]) < TS).sum()),
                neck_Te_geo=float(np.exp(np.log(Tn_).mean())), neck_Te_min=float(Tn_.min()), neck_spread=float(np.log(Tn_).std()),
                neck_dead_expected=float(pdn.sum()),
                neck_worst=f"{SN[np.unravel_index(Tn_.argmin(), Tn_.shape)[0]]}/{np.unravel_index(Tn_.argmin(), Tn_.shape)[1]}",
                fret_peak=bands, mass=R['mass_kg'], bal=R['balance_x_in'], Te=Te.round(2).tolist(), pdead=pdead.round(2).tolist())


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--ts':
        TS = float(args[1]); args = args[2:]
    out = [analyse(t) for t in args]
    print(f"{'case':22s} {'TeGeo':>6s} {'TeMin':>6s} {'worst':>6s} {'spread':>6s} {'Edead':>6s} | {'ptGeo':>6s} {'ptDead':>6s} | peaks G_fret (s/kg @ Hz)")
    for o in out:
        print(f"{o['tag']:22s} {o['Te_geo']:6.2f} {o['Te_min']:6.2f} {o['worst']:>6s} {o['spread']:6.3f} {o['dead_expected']:6.2f} | "
              f"{o['pt_Te_geo']:6.2f} {o['pt_dead']:6d} | neck-only geo {o['neck_Te_geo']:.2f} min {o['neck_Te_min']:.2f} {o['neck_worst']} spread {o['neck_spread']:.3f} Edead {o['neck_dead_expected']:.2f} | {o['fret_peak']}")
    if TS == 8.0: json.dump(out, open(os.path.join(HERE, 'results', 'study_deadspots.json'), 'w'), indent=1)
