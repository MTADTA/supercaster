"""Coupled reduced-order solve: structural modes (model.py) + chamber air modes (air.py) + exterior radiation (BEM on
the closed body surface, surface.py). All projections are cached per structural key in sim/cache/modes_<key>.npz.

Equations (time convention e^{i w t}):
  structure  (Lambda(1 + i eta) - w^2) a + i w Cm a + Cp^T b = Phi^T f
  air        (Om^2 (1 + i eta_a) - w^2) b + w^2 Cp a = 0,     Cp = Psi^T W Phi
with Phi M-normalised structural modes, Psi C-normalised rigid-wall air modes, W the signed moving-wall areas of the
roof (underside of the skin or veneer) and the floor. Port volume flow q = sum(w_ext p) / (i w).
Radiated power W = 1/2 x^H Rm(w) x, x = [i w a ; b / (i w)], Rm = (L^T S)^T (L^T S) from the BEM factors.
"""
import os, time, json
import numpy as np
import scipy.sparse as sp
import geom, model, air, surface, fe, materials

IN = 0.0254
SCALE = 25.5                     # in, nut to saddle
BUDGET = [1.0e-3, 1.5e-3, 2.0e-3, 3.0e-3, 3.0e-3, 3.0e-3]   # s/kg, halving conductance per string, low E first
BUDGET_SRC = '[literature: as quoted in sim3d-REPORT section 1.2 (Woodhouse/Pate relation; A, D, B interpolated there), not re-read]'
BANDS = [(80, 200), (200, 300), (300, 500), (500, 1000)]
NFRET = 13
GROUP_ETA_SRC = dict(guard_contact='0.10 [judged]', springs='0.01 [judged]', strings='0.001 [judged]', hold='0 (dashpots carry the loss)',
                     beam='maple eta [judged]')


# ----------------------------------------------------------------------------------------------- interpolation maps
def _bilinear(B, x, y, level=None, grid=None):
    """Weights (list of (node, w)) for a point on a node grid level (or a guard grid), skipping missing nodes."""
    xs, ys = B['xs'], B['ys']; h = xs[1] - xs[0]
    ids = B['nid'][:, :, level] if grid is None else grid
    fx = (x - xs[0]) / h; fy = (y - ys[0]) / h
    i0 = int(np.floor(fx)); j0 = int(np.floor(fy)); tx = fx - i0; ty = fy - j0
    out = []
    for di, dj, w in ((0, 0, (1 - tx) * (1 - ty)), (1, 0, tx * (1 - ty)), (0, 1, (1 - tx) * ty), (1, 1, tx * ty)):
        i, j = i0 + di, j0 + dj
        if 0 <= i < ids.shape[0] and 0 <= j < ids.shape[1] and ids[i, j] >= 0 and w > 1e-9:
            out.append((ids[i, j], w))
    if not out:
        for r in range(1, 5):
            cand = [(np.hypot(xs[i] - x, ys[j] - y), ids[i, j]) for i in range(max(0, i0 - r), min(ids.shape[0], i0 + r + 2))
                    for j in range(max(0, j0 - r), min(ids.shape[1], j0 + r + 2)) if ids[i, j] >= 0]
            if cand:
                out = [(min(cand)[1], 1.0)]; break
    if not out: return []
    s = sum(w for _, w in out)
    return [(n, w / s) for n, w in out]


def _rows(entries, ndof):
    r, c, v = [], [], []
    for k, ent in enumerate(entries):
        for (dof, w) in ent:
            r.append(k); c.append(dof); v.append(w)
    return sp.csr_matrix((v, (r, c)), shape=(len(entries), ndof))


def surface_map(B, P):
    """Sparse (npanel x ndof) map from structural dofs to the normal displacement of each BEM panel, and the f-hole
    fraction of each top panel."""
    S = geom.static_geometry(); D = B['D']
    kind = P['kind']; cen = P['cen'] / IN; nrm = P['n']
    gt = B['gnodes']['gt'] if B['gnodes'] is not None else None
    guard_poly = S['guard']
    ent = []; frac = np.zeros(len(kind))
    # f-hole fraction by sampling each top panel
    bar = np.array([[a, b, 1 - a - b] for a in np.linspace(0.05, 0.95, 7) for b in np.linspace(0.05, 0.95, 7) if a + b < 0.98])
    tri = P['V'][P['T']] / IN
    for p in range(len(kind)):
        x, y = cen[p, 0], cen[p, 1]
        if kind[p] == 0:
            if D['fhole'] and D['chamber']:
                q = bar @ tri[p]; frac[p] = geom.inside_poly(S['fhole'], q[:, 0], q[:, 1]).mean()
            w = None
            if gt is not None and geom.inside_poly(guard_poly, np.array([x]), np.array([y]))[0]:
                w = _bilinear(B, x, y, grid=gt)
            if not w: w = _bilinear(B, x, y, level=0)
            ent.append([(3 * n + d, wt * nrm[p, d] * (1 - frac[p])) for n, wt in w for d in range(3)])
        elif kind[p] == 1:
            w = _bilinear(B, x, y, level=7)
            ent.append([(3 * n + d, wt * nrm[p, d]) for n, wt in w for d in range(3)])
        else:
            w0 = _bilinear(B, x, y, level=0); w7 = _bilinear(B, x, y, level=7)
            ent.append([(3 * n + d, 0.5 * wt * nrm[p, d]) for n, wt in w0 + w7 for d in range(2)])
    return _rows(ent, B['ndof']), frac


def point_maps(B):
    """Modal-map rows (in full dofs) for saddles (3 directions), fret points (vertical) and response points."""
    ndof = B['ndof']; T = geom.neck_tables(); rows = {}
    tdof = B['tdof']; pref = B['pref']
    for i, y in enumerate(model.Y_SADDLE):
        Tp = fe.rigid_point((np.array([model.X_SADDLE, y, 0.0]) - pref) * IN)       # saddle top at the body surface line
        rows[f'saddle{i}'] = [[(tdof[q], Tp[d, q]) for q in range(6) if Tp[d, q] != 0] for d in range(3)]
    bx = np.array(B['bx_list'])
    for n in range(NFRET):
        xf = 0.0 if n == 0 else float(T['fret_x'](n)); e = int(np.argmin(np.abs(bx - xf)))
        for i in range(6):
            ys = model.Y_NUT[i] + (model.Y_SADDLE[i] - model.Y_NUT[i]) * xf / model.X_SADDLE
            Tp = fe.rigid_point((np.array([xf, ys, 0.375]) - B['XB'][e]) * IN)
            rows[f'fret{n}_{i}'] = [[(B['b0'] + 6 * e + q, Tp[2, q]) for q in range(6) if Tp[2, q] != 0]]
    # neck back at fret 7 (bottom of the C), mid chamber top, belly / forearm patches (mean of patch nodes, normal)
    xf = float(T['fret_x'](7)); e = int(np.argmin(np.abs(bx - xf))); dep = float(T['neck_depth'](xf))
    Tp = fe.rigid_point((np.array([xf, 0.0, 0.375 - dep]) - B['XB'][e]) * IN)
    rows['neck_back'] = [[(B['b0'] + 6 * e + q, Tp[2, q]) for q in range(6) if Tp[2, q] != 0]]
    w = _bilinear(B, 23.0, 4.6, level=0); rows['mid_chamber'] = [[(3 * n + 2, wt) for n, wt in w]]
    for nm in ('belly', 'forearm'):
        nn = B['patches'][nm]
        rows[nm] = [[(3 * n + 2, 1.0 / len(nn)) for n in nn]] if nn else [[]]
    names = list(rows)
    flat = []; index = {}
    for nm in names:
        index[nm] = list(range(len(flat), len(flat) + len(rows[nm]))); flat += rows[nm]
    return _rows(flat, ndof), index


def energy_shares(B, Phi):
    """Kinetic-energy share of each mode in body, bass wing (chamber side, y > 2.2), guard, neck, trem."""
    M = B['M']; MP = M @ Phi; e = Phi * MP
    ns = B['XN'].shape[0]; nb = B['nbody']
    node = np.arange(ns); dof_node = np.repeat(node, 3)
    part = np.full(B['ndof'], 'other', dtype=object)
    XN = B['XN']
    body = dof_node < nb
    part[:3 * ns][body] = 'body'
    wing = body & (XN[dof_node, 1] > 2.2)
    part[:3 * ns][wing] = 'wing'
    part[:3 * ns][~body] = 'guard'
    part[B['b0']:B['b0'] + 6 * len(B['bx_list'])] = 'neck'
    part[B['tdof']] = 'trem'
    tot = e.sum(0)
    return {k: (e[part == k].sum(0) / tot) for k in ('body', 'wing', 'guard', 'neck', 'trem')}


def twist_index(B, Phi):
    """Share of the body-top vertical motion explained by the anticlastic x*y term after removing the rigid plane."""
    nid0 = B['nid'][:, :, 0]; I, J = np.nonzero(nid0 >= 0); n = nid0[I, J]
    x = B['xs'][I] - B['xs'][I].mean(); y = B['ys'][J] - B['ys'][J].mean()
    uz = Phi[3 * n + 2]
    A3 = np.c_[np.ones_like(x), x, y]; A4 = np.c_[A3, x * y]
    tot = (uz ** 2).sum(0)
    r3 = uz - A3 @ np.linalg.lstsq(A3, uz, rcond=None)[0]; r4 = uz - A4 @ np.linalg.lstsq(A4, uz, rcond=None)[0]
    rigid = 1 - (r3 ** 2).sum(0) / tot
    return (r3 ** 2).sum(0) / tot - (r4 ** 2).sum(0) / tot, rigid


# ----------------------------------------------------------------------------------------------- structural cache
def struct_cache(D, verbose=True):
    materials.use(D['wood'], D.get('neck_curly', False))
    key = model.struct_key(D)
    fn = os.path.join(geom.CACHE, f'modes_{key}.npz')
    if os.path.exists(fn):
        z = np.load(fn, allow_pickle=True)
        return {k: (z[k].item() if z[k].dtype == object and z[k].shape == () else z[k]) for k in z.files}
    t0 = time.time()
    B = model.build(D, verbose=verbose)
    m_tot, xbal = model.mass_props(B)
    R = model.solve_modes(B, D['fmax_modes'], verbose=verbose)
    Phi = B['Tr'] @ R['V']
    kg = {g: np.einsum('ij,ij->j', Phi, K @ Phi) for g, K in B['groups'].items()}
    Cm = Phi.T @ (B['C'] @ Phi)
    RC = surface.radiation_cache(verbose=verbose)
    Smap, frac = surface_map(B, RC['P'])
    S_s = (Smap @ Phi).astype(np.float32)
    Pm, index = point_maps(B)
    Pp = (Pm @ Phi)
    nid = B['nid']
    def level_z(k):
        ids = nid[:, :, k]; out = np.zeros(ids.shape + (Phi.shape[1],), np.float32)
        I, J = np.nonzero(ids >= 0); out[I, J] = Phi[3 * ids[I, J] + 2]
        return out, ids >= 0
    roofz, roofm = level_z(2); floorz, floorm = level_z(6)
    sh = energy_shares(B, Phi); tw, rig = twist_index(B, Phi)
    out = dict(key=key, f=R['f'], lam=R['lam'], kg=kg, Cm=Cm, S_s=S_s, frac=frac, Pp=Pp, index=index,
               roofz=roofz, roofm=roofm, floorz=floorz, floorm=floorm, xs=B['xs'], ys=B['ys'],
               mass=m_tot, xbal=xbal, shares=sh, twist=tw, rigid=rig, ndof=len(R['lam']) and R['V'].shape[0],
               liner_mass=B['liner_mass'], solve_s=time.time() - t0, materials=materials.load())
    np.savez(fn, **{k: (np.array(v, dtype=object) if isinstance(v, (dict, list)) else v) for k, v in out.items()})
    if verbose: print(f'[rom] structural cache {key} written ({time.time() - t0:.0f}s)', flush=True)
    return out


def _grid_interp(Z, Mk, xs, ys, x, y):
    """Bilinear interpolation of a level field Z (nx, ny, n) at points, skipping missing nodes."""
    h = xs[1] - xs[0]; fx = (x - xs[0]) / h; fy = (y - ys[0]) / h
    i0 = np.floor(fx).astype(int); j0 = np.floor(fy).astype(int); tx = fx - i0; ty = fy - j0
    acc = np.zeros((len(x), Z.shape[2])); ws = np.zeros(len(x))
    for di, dj in ((0, 0), (1, 0), (0, 1), (1, 1)):
        i = np.clip(i0 + di, 0, Z.shape[0] - 1); j = np.clip(j0 + dj, 0, Z.shape[1] - 1)
        w = (tx if di else 1 - tx) * (ty if dj else 1 - ty) * Mk[i, j]
        acc += w[:, None] * Z[i, j]; ws += w
    bad = ws < 1e-9
    if bad.any():   # nearest existing node
        I, J = np.nonzero(Mk)
        for p in np.nonzero(bad)[0]:
            k = np.argmin((xs[I] - x[p]) ** 2 + (ys[J] - y[p]) ** 2); acc[p] = Z[I[k], J[k]]; ws[p] = 1.0
    return acc / ws[:, None]


# ----------------------------------------------------------------------------------------------- group loss factors
def modal_eta(D, SC):
    M = SC['materials']; we = D['wood_eta']
    eta_g = dict(alder=M['alder']['eta'] * we, liner=M['alder']['eta'] * we, maple=M['maple']['eta'] * we,
                 veneer=M.get('veneer', M['maple'])['eta'] * we, beam=M['maple']['eta'] * we, guard=M['guard']['eta'],
                 guard_contact=0.10, screws=0.05, rod=0.002, pivot=D['pivot_eta'], springs=0.01, strings=0.001, hold=0.0)
    lam = SC['lam']; num = np.zeros_like(lam)
    for g, k in SC['kg'].items():
        num += eta_g.get(g, 0.0) * k
    with np.errstate(divide='ignore', invalid='ignore'):
        eta = np.where(lam > 1.0, num / lam, 0.0)
    return eta, eta_g


# ----------------------------------------------------------------------------------------------- the coupled solve
def run(D, df=0.5, verbose=True):
    t0 = time.time()
    SC = struct_cache(D, verbose=verbose)
    RC = surface.radiation_cache(verbose=verbose)
    eta_s, eta_g = modal_eta(D, SC)
    lam = SC['lam']; ns = len(lam)
    # ---- air
    has_air = D['chamber']
    if has_air:
        A = air.build(D); AM = air.modes(D, n=16, A=A)
        Psi = AM['psi']; Om2 = AM['w'] ** 2
        # boundary-layer reactance lowers each mode by eta_visc / 2 (as much as its resistance) [literature: standard
        # boundary-layer impedance, reactive part = resistive part]
        bl = np.array([1 - p['eta_visc'] / 2 for p in AM['parts']]); Om2 = Om2 * bl ** 2
        eta_a = AM['eta']
        roof_u = _grid_interp(SC['roofz'], SC['roofm'], SC['xs'], SC['ys'], A['x'], A['y'])
        floor_u = _grid_interp(SC['floorz'], SC['floorm'], SC['xs'], SC['ys'], A['x'], A['y'])
        WPhi = A['roof'][:, None] * roof_u + A['floor'][:, None] * floor_u          # (Nair, ns)
        Cp = Psi.T @ WPhi                                                          # (na, ns)
        port = A['w_ext'] @ Psi                                                    # q = port . b / (i w)
        na = Psi.shape[1]
    else:
        na = 0; Cp = np.zeros((0, ns)); Om2 = np.zeros(0); eta_a = np.zeros(0); port = np.zeros(0); A = None; AM = None
    # ---- radiation matrices
    frac = SC['frac']; Ah = float((frac * RC['P']['area']).sum())
    S_a = (frac / Ah)[:, None] * port[None, :] if (na and Ah > 0) else np.zeros((len(frac), na))
    Sfull = np.hstack([SC['S_s'].astype(float), S_a])
    Rm = np.array([(lambda G: G.T @ G)(L.T.astype(float) @ Sfull) for L in RC['L']])
    fb = RC['freqs']; Rn = Rm / (fb ** 2)[:, None, None]
    lfb = np.log(fb)
    def Rm_at(f):
        lf = np.log(f); k = int(np.clip(np.searchsorted(lfb, lf) - 1, 0, len(fb) - 2)); t = (lf - lfb[k]) / (lfb[k + 1] - lfb[k])
        return ((1 - t) * Rn[k] + t * Rn[k + 1]) * f * f
    # ---- points
    Pp = SC['Pp']; idx = SC['index']
    sad_z = np.array([Pp[idx[f'saddle{i}'][2]] for i in range(6)])          # (6, ns) vertical
    sad_y = np.array([Pp[idx[f'saddle{i}'][1]] for i in range(6)])
    sad_x = np.array([Pp[idx[f'saddle{i}'][0]] for i in range(6)])
    fret = np.array([[Pp[idx[f'fret{n}_{i}'][0]] for i in range(6)] for n in range(NFRET)])   # (13, 6, ns)
    resp = {k: Pp[idx[k][0]] for k in ('neck_back', 'mid_chamber', 'belly', 'forearm')}
    # ---- frequencies: grid + note fundamentals
    grid = np.arange(80.0, 1000.0 + 1e-9, df)
    notes = np.array([[model.STRINGS[s][0] * 2 ** (n / 12) for n in range(NFRET)] for s in model.SNAMES])   # (6, 13)
    fgrid = np.r_[grid, notes.ravel()]
    Lam_c = lam * (1 + 1j * eta_s); Om_c = Om2 * (1 + 1j * eta_a)
    Cm = SC['Cm']
    nt = ns + na
    G_sz = np.zeros((len(fgrid), 6)); G_sy = np.zeros((len(fgrid), 6)); G_sx = np.zeros((len(fgrid), 6))
    G_fr = np.zeros((len(fgrid), NFRET, 6)); W = np.zeros((len(fgrid), 6)); Qp = np.zeros((len(fgrid), 6))
    Vr = {k: np.zeros((len(fgrid), 6)) for k in resp}
    PZ = np.vstack([sad_z, sad_y, sad_x, fret.reshape(-1, ns)])              # driving points (structural rows)
    for k, f in enumerate(fgrid):
        w = 2 * np.pi * f
        Z = np.zeros((nt, nt), complex)
        Z[:ns, :ns] = np.diag(Lam_c - w * w) + 1j * w * Cm
        if na:
            Z[:ns, ns:] = Cp.T; Z[ns:, :ns] = w * w * Cp; Z[ns:, ns:] = np.diag(Om_c - w * w)
        H = np.linalg.inv(Z)
        Hss = H[:ns, :ns]
        Y = 1j * w * np.einsum('pi,ij,pj->p', PZ, Hss, PZ)
        G_sz[k] = Y[:6].real; G_sy[k] = Y[6:12].real; G_sx[k] = Y[12:18].real; G_fr[k] = Y[18:].real.reshape(NFRET, 6)
        X = H[:, :ns] @ sad_z.T                                                  # (nt, 6) response to each saddle force
        x = np.vstack([1j * w * X[:ns], X[ns:] / (1j * w)])
        R_ = Rm_at(f)
        W[k] = 0.5 * np.einsum('ij,ik,kj->j', x.conj(), R_, x).real
        if na: Qp[k] = np.abs(port @ X[ns:] / (1j * w))
        for nm, r in resp.items():
            Vr[nm][k] = np.abs(1j * w * (r @ X[:ns]))
    ng = len(grid)
    out = dict(design={k: v for k, v in D.items()}, cache_key=SC['key'], elapsed_s=None)
    out['mass_kg'] = float(SC['mass']); out['balance_x_in'] = float(SC['xbal'])
    out['materials'] = {k: v for k, v in SC['materials'].items() if not k.startswith('_')}
    out['materials_source'] = SC['materials'].get('_source', 'reference')
    out['group_eta'] = eta_g
    # ---- modes (structural, uncoupled) with labels
    sh = SC['shares']; modes = []
    for j in range(ns):
        if SC['f'][j] > 1100: break
        s = {k: float(v[j]) for k, v in sh.items()}
        lab = max(s, key=s.get)
        modes.append(dict(f=round(float(SC['f'][j]), 2), eta=round(float(eta_s[j]), 5), shares={k: round(v, 3) for k, v in s.items()},
                          twist=round(float(SC['twist'][j]), 3), rigid=round(float(SC['rigid'][j]), 3), label=lab))
    out['modes'] = modes
    tw = [m for m in modes if 200 < m['f'] < 400 and (m['shares']['body'] + m['shares']['wing']) > 0.3]
    out['twist_mode'] = max(tw, key=lambda m: m['twist']) if tw else None
    # ---- coupled eigenvalues (no dashpots) and A0
    if na:
        A11 = np.diag(Lam_c); A22 = np.diag(Om_c)
        Mx = np.block([[A11, Cp.T], [Cp @ A11, Cp @ Cp.T + A22]])
        mu, V = np.linalg.eig(Mx)
        fr = np.sqrt(mu.real.clip(0)) / (2 * np.pi)
        wv = np.sqrt(np.abs(mu)).clip(1.0)
        ea = np.abs(V[ns, :]) ** 2 / wv ** 2; et = (np.abs(V[:ns]) ** 2).sum(0) + (np.abs(V[ns:]) ** 2).sum(0) / wv ** 2
        share = ea / et
        j = int(np.argmax(np.where((fr > 150) & (fr < 500), share, 0)))
        out['A0'] = dict(f_coupled=round(float(fr[j]), 2), Q_coupled=round(float(mu[j].real / mu[j].imag), 1),
                         air_share=round(float(share[j]), 3), f_rigid=round(float(AM['f'][0]), 2),
                         f_rigid_bl=round(float(np.sqrt(Om2[0]) / 2 / np.pi), 2), Q_rigid=round(float(1 / AM['eta'][0]), 1),
                         volume_in3=round(A['volume_in3'], 2), hole_open_in2=round(A['hole_open_in2'], 3),
                         throat_in2=None if A['throat_in2'] is None else round(A['throat_in2'], 3))
        qm = Qp[:ng].mean(1); jj = int(np.argmax(np.where((grid > 150) & (grid < 500), qm, 0)))
        out['A0']['f_port_peak'] = float(grid[jj])
        cm = [(round(float(fr[i]), 1), round(float(share[i]), 3)) for i in np.argsort(fr) if 150 < fr[i] < 500 and share[i] > 0.05]
        out['coupled_air_modes'] = cm
        out['air_modes'] = [dict(f=round(p['f'], 1), Q=round(p['Q'], 1), eta_visc=round(p['eta_visc'], 4),
                                 eta_rad=round(p['eta_rad'], 5), eta_th=round(p['eta_th'], 5)) for p in AM['parts'][:6]]
    else:
        out['A0'] = None
    # ---- bands
    def band(arr, lo, hi):
        m = (grid >= lo) & (grid < hi) if hi < 1000 else (grid >= lo) & (grid <= hi)
        return arr[:ng][m].mean(0)
    out['bands_Hz'] = BANDS
    Wm = W[:ng].mean(1)
    out['power_dB_re_1pW_per_N2'] = [round(float(10 * np.log10(band(Wm, lo, hi) / 1e-12)), 2) for lo, hi in BANDS]
    out['power_dB_per_saddle'] = {model.SNAMES[i]: [round(float(10 * np.log10(band(W[:, i], lo, hi) / 1e-12)), 2) for lo, hi in BANDS] for i in range(6)}
    out['velocity_dB_re_1mps_per_N'] = {nm: [round(float(10 * np.log10(band((v[:ng] ** 2).mean(1), lo, hi))), 2) for lo, hi in BANDS]
                                        for nm, v in Vr.items()}
    # ---- bridge conductance
    bc = {}
    for i, s in enumerate(model.SNAMES):
        g = G_sz[:ng, i]; jm = int(np.argmax(g))
        bc[s] = dict(peak=float(g[jm]), peak_Hz=float(grid[jm]), median=float(np.median(g)),
                     band_mean=[float(band(g, lo, hi)) for lo, hi in BANDS],
                     peak_along=float(G_sx[:ng, i].max()), peak_side=float(G_sy[:ng, i].max()))
    out['bridge_conductance_s_per_kg'] = bc
    gm = G_sz[:ng].mean(1)
    out['bridge_conductance_mean_6'] = dict(band_mean=[float(band(gm, lo, hi)) for lo, hi in BANDS], median=float(np.median(gm)),
                                            peak=float(G_sz[:ng].max()), peak_Hz=float(grid[np.argmax(G_sz[:ng].max(1))]))
    out['fret_conductance_s_per_kg'] = dict(peak=float(G_fr[:ng].max()), median=float(np.median(G_fr[:ng])),
                                            per_fret_peak=[float(G_fr[:ng, n].max()) for n in range(NFRET)])
    # ---- notes
    nl = []; past = 0
    for i, s in enumerate(model.SNAMES):
        f0, Tn, _ = model.STRINGS[s]
        for n in range(NFRET):
            k = ng + i * NFRET + n; f = fgrid[k]
            gb = G_sz[k, i]; gf = G_fr[k, n, i]; G = gb + gf
            L = SCALE * IN * 2 ** (-n / 12)
            T60 = 6.91 * L / (Tn * max(G, 1e-12))
            p = G > BUDGET[i]; past += int(p)
            nl.append(dict(string=s, fret=n, f=round(float(f), 2), level_dB=round(float(10 * np.log10(W[k, i] / 1e-12)), 2),
                           G_bridge=float(gb), G_fret=float(gf), T60_body_s=round(float(T60), 2), past_halving=bool(p)))
    out['notes'] = nl; out['notes_past_halving'] = past; out['budget_s_per_kg'] = BUDGET; out['budget_source'] = BUDGET_SRC
    # ---- sum-rule check (uncoupled modal sum vs the computed conductance integral, mean of six saddles)
    sel = (SC['f'] >= 80) & (SC['f'] <= 1000)
    modal = (np.pi / 2) * (sad_z[:, sel] ** 2).sum(1).mean()
    integ = np.trapezoid(gm, 2 * np.pi * grid)
    out['sum_rule'] = dict(integral=float(integ), modal_sum=float(modal), ratio=round(float(integ / modal), 3))
    out['n_modes_struct'] = int(ns); out['n_modes_air'] = int(na)
    out['spectra_note'] = 'full spectra in the .npz next to the JSON'
    out['_spectra'] = dict(f=grid, power_mean=Wm, G_saddle_z=G_sz[:ng], G_fret=G_fr[:ng], port_flow=Qp[:ng].mean(1) if na else np.zeros(ng))
    out['elapsed_s'] = round(time.time() - t0, 1)
    return out
