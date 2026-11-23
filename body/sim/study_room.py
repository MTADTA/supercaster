"""Room study for STUDIES-neck-trem-guard.md: sound pressure at the player's ear and at a listener 1-3 m in front, from
the coupled model, the exterior BEM (panel pressures) and the Kirchhoff-Helmholtz integral (exact near field, free
field), plus a diffuse reverberant field from the radiated power in a judged living room.

  cache/venv/bin/python -I -B study_room.py --verify
  cache/venv/bin/python -I -B study_room.py --design final_narrowed --set wood=json ... --label final \
        --design2 solid --set2 wood=json ... --label2 solid

Body coordinates (m): x from the nut toward the tail, y across (bass side +), z out of the top. In playing position the
bass side points up, the top faces the audience. Field points [judged]:
  player ear     x 0.46, y +0.40, z -0.12  (above the bass edge, slightly behind the top plane; no torso or head modelled)
  front 1/2/3 m  on the top normal through the body centre (x 0.56, y 0, z 0)
  front 45 deg   1 m, rotated 45 deg toward the tail (+x) in the x-z plane
  up 1 m         +y (toward the ceiling / the player's head direction, far field)
  back 1 m       -z (behind the body: in reality the player's torso is here)
Room [judged]: 50 m3 living room, RT60 0.5 s -> Sabine absorption A = 0.161 V / T; reverberant p^2 = 4 rho c W (1-a)/A.
"""
import sys, os, json, argparse, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import designs, rom, bem, surface, air, model

RHO, C0 = bem.RHO, bem.C0
FIELD = dict(ear=(0.46, 0.40, -0.12), front1=(0.56, 0.0, 1.0), front2=(0.56, 0.0, 2.0), front3=(0.56, 0.0, 3.0),
             front45=(0.56 + 0.7071, 0.0, 0.7071), up1=(0.56, 1.0, 0.0), back1=(0.56, 0.0, -1.0))
ROOM_V, ROOM_T = 50.0, 0.5


def field_matrices(P, k, pts):
    """Rows mapping panel pressure p and normal velocity v to the field pressure: p(x) = Fp p + Fv v (e^{iwt})."""
    qp, n = P['qp'], P['n']; w = bem._QW[None, :] * P['area'][:, None]
    Fp = np.zeros((len(pts), len(n)), complex); Fv = np.zeros_like(Fp)
    for i, x in enumerate(pts):
        d = np.asarray(x)[None, None, :] - qp; r = np.sqrt((d ** 2).sum(-1)); ekr = np.exp(-1j * k * r)
        G = ekr / (4 * np.pi * r); dG = ekr * (1 + 1j * k * r) * np.einsum('pqd,pd->pq', d, n) / (4 * np.pi * r ** 3)
        Fp[i] = (dG * w).sum(1); Fv[i] = 1j * k * C0 * RHO * (G * w).sum(1)
    return Fp, Fv


def verify():
    out = {}
    a = 0.1; V, T = bem.sphere(a, 3); P = bem.panel_data(V, T)
    for f in (200.0, 800.0):
        k = 2 * np.pi * f / C0; Z = bem.impedance(P, f)
        r = 0.5; pts = [(r, 0.0, 0.0), (0.0, 0.0, r)]
        Fp, Fv = field_matrices(P, k, pts)
        v = np.ones(len(T)); p = Fp @ (Z @ v) + Fv @ v
        ex = RHO * C0 * (1j * k * a / (1 + 1j * k * a)) * (a / r) * np.exp(-1j * k * (r - a))
        out[f'pulsating_{int(f)}Hz_dB_err'] = float(20 * np.log10(np.abs(p[0]) / abs(ex)))
        vz = P['n'][:, 2]; p = Fp @ (Z @ vz) + Fv @ vz
        ka, kr = k * a, k * r
        ex1 = RHO * C0 * a ** 3 / r ** 2 * (1 + 1j * kr) / (2 * (1 + 1j * ka) - ka ** 2) * np.exp(-1j * k * (r - a)) * (1j * ka / a) / 1j * 1j
        # oscillating sphere, on axis: p = rho c U (a/r)^2 (1 + i k r) i k a / (2 (1 + i k a) - (k a)^2) e^{-ik(r-a)}
        ex1 = RHO * C0 * (a / r) ** 2 * (1 + 1j * kr) * 1j * ka / (2 * (1 + 1j * ka) - ka ** 2) * np.exp(-1j * k * (r - a))
        out[f'oscillating_axis_{int(f)}Hz_dB_err'] = float(20 * np.log10(np.abs(p[1]) / abs(ex1)))
        out[f'oscillating_equator_{int(f)}Hz_rel'] = float(np.abs(p[0]) / np.abs(p[1]))
    return out


def coupled(D):
    """Return (solve(f) -> panel normal velocities (npanel, 6 saddles), radiated power (6,)) for a design."""
    SC = rom.struct_cache(D, verbose=False); RC = surface.radiation_cache(verbose=False)
    eta_s, _ = rom.modal_eta(D, SC); lam = SC['lam']; ns = len(lam)
    if D['chamber']:
        A = air.build(D); AM = air.modes(D, n=16, A=A); Psi = AM['psi']
        bl = np.array([1 - p['eta_visc'] / 2 for p in AM['parts']]); Om2 = AM['w'] ** 2 * bl ** 2; eta_a = AM['eta']
        roof_u = rom._grid_interp(SC['roofz'], SC['roofm'], SC['xs'], SC['ys'], A['x'], A['y'])
        floor_u = rom._grid_interp(SC['floorz'], SC['floorm'], SC['xs'], SC['ys'], A['x'], A['y'])
        Cp = Psi.T @ (A['roof'][:, None] * roof_u + A['floor'][:, None] * floor_u); port = A['w_ext'] @ Psi; na = Psi.shape[1]
    else:
        na = 0; Cp = np.zeros((0, ns)); Om2 = np.zeros(0); eta_a = np.zeros(0); port = np.zeros(0)
    frac = SC['frac']; Ah = float((frac * RC['P']['area']).sum())
    S_a = (frac / Ah)[:, None] * port[None, :] if (na and Ah > 0) else np.zeros((len(frac), na))
    Sfull = np.hstack([SC['S_s'].astype(float), S_a])
    Pp = SC['Pp']; idx = SC['index']
    sad_z = np.array([Pp[idx[f'saddle{i}'][2]] for i in range(6)])
    Lam_c = lam * (1 + 1j * eta_s); Om_c = Om2 * (1 + 1j * eta_a); Cm = SC['Cm']; nt = ns + na

    def solve(f):
        w = 2 * np.pi * f
        Z = np.zeros((nt, nt), complex); Z[:ns, :ns] = np.diag(Lam_c - w * w) + 1j * w * Cm
        if na:
            Z[:ns, ns:] = Cp.T; Z[ns:, :ns] = w * w * Cp; Z[ns:, ns:] = np.diag(Om_c - w * w)
        X = np.linalg.solve(Z, np.vstack([sad_z.T, np.zeros((na, 6))]))
        x = np.vstack([1j * w * X[:ns], X[ns:] / (1j * w)])
        return Sfull @ x
    return solve, SC


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--design', action='append', default=[]); ap.add_argument('--set', action='append', default=[])
    ap.add_argument('--label', action='append', default=[]); ap.add_argument('--nf', type=int, default=36)
    ap.add_argument('--out', default=os.path.join(HERE, 'results', 'study_room.json'))
    ap.add_argument('--eargrid', action='store_true', help='replace the field points by a 3 x 3 grid of ear positions + front 1 m')
    a = ap.parse_args()
    if a.eargrid:
        FIELD.clear()
        for yy in (0.3, 0.4, 0.5):
            for zz in (-0.05, -0.12, -0.20):
                FIELD[f'ear_y{yy}_z{zz}'] = (0.46, yy, zz)
        FIELD['front1'] = (0.56, 0.0, 1.0)
    if a.verify:
        print(json.dumps(verify(), indent=1)); return
    # --set entries are 'label:key=value'
    Ds = []
    for nm, lb in zip(a.design, a.label):
        ov = dict(s.split(':', 1)[1].split('=', 1) for s in a.set if s.split(':', 1)[0] == lb)
        Ds.append((lb, designs.get(nm, ov)))
    RC = surface.radiation_cache(verbose=False); P = RC['P']
    solvers = {lb: coupled(D)[0] for lb, D in Ds}
    pts = list(FIELD.values()); names = list(FIELD)
    freqs = np.geomspace(80, 1000, a.nf)
    Aabs = 0.161 * ROOM_V / ROOM_T
    res = {lb: dict(p2={n: [] for n in names}, W=[]) for lb, _ in Ds}
    t0 = time.time()
    for f in freqs:
        k = 2 * np.pi * f / C0; Zb = bem.impedance(P, f); Fp, Fv = field_matrices(P, k, pts)
        Ar = P['area']
        for lb, _ in Ds:
            v = solvers[lb](f)                           # (npanel, 6)
            p_s = Zb @ v
            W = 0.5 * np.real(np.einsum('pj,p,pj->j', v.conj(), Ar, p_s))   # power per saddle, from the surface
            pf = Fp @ p_s + Fv @ v                        # (npts, 6)
            res[lb]['W'].append(W.mean())
            for i, n in enumerate(names):
                res[lb]['p2'][n].append(0.5 * (np.abs(pf[i]) ** 2).mean())   # mean-square pressure, mean of 6 saddles
        print(f'{f:.0f} Hz ({time.time() - t0:.0f}s)', flush=True)
    bands = [(80, 200), (200, 300), (300, 500), (500, 1000), (80, 1000)]
    out = dict(freqs=freqs.tolist(), field_points_m=FIELD, room=dict(V_m3=ROOM_V, RT60_s=ROOM_T, A_m2=Aabs, tag='[judged]'),
               note='SPL per unit vertical saddle force, mean of six saddles, dB re 20 uPa/N; free-field direct; '
                    'room = direct + diffuse reverberant (incoherent sum)', designs={})
    for lb, D in Ds:
        r = res[lb]; W = np.array(r['W']); prev = 4 * RHO * C0 * W / Aabs
        o = dict(overrides={k: D[k] for k in D if k in designs.BASE and D[k] != designs.BASE[k]})
        def bm(arr):
            return [round(float(10 * np.log10(np.mean(arr[(freqs >= lo) & (freqs <= hi)]))), 2) for lo, hi in bands]
        o['power_dB_re_1pW'] = bm(W / 1e-12)
        o['direct_dB'] = {n: bm(np.array(r['p2'][n]) / 4e-10) for n in names}
        o['room_dB'] = {n: bm((np.array(r['p2'][n]) + prev) / 4e-10) for n in names}
        o['reverberant_dB'] = bm(prev / 4e-10)
        o['spectra'] = dict(W=W.tolist(), p2={n: list(map(float, r['p2'][n])) for n in names})
        out['designs'][lb] = o
    out['bands'] = bands
    json.dump(out, open(a.out, 'w'), indent=1)
    for lb in out['designs']:
        o = out['designs'][lb]; print(lb, 'W', o['power_dB_re_1pW'])
        for n in names: print('  ', n, 'direct', o['direct_dB'][n], 'room', o['room_dB'][n])


if __name__ == '__main__':
    main()
