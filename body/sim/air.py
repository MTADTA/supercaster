"""Chamber air: finite-volume acoustic network of the wing chamber, the f-hole through the skin and veneer, and the liner.

Method
  * Plan columns on a grid of spacing h_air, built from the carve's chamber at 0.025 in (partial columns at the walls keep
    their true area). Each column is split into three zones, every zone into equal sub-layers (terrain following):
      A  hole neck: ceiling -> top surface, only where the column overlaps the traced f-hole (open fraction f_hole)
      B  liner zone: ceiling -> ceiling - liner depth (open fraction f_B: 1 without liner; with a liner, the column area
         that is neither liner wood nor solid; the throat inside an inset outline is resolved by a 0.004 in raster)
      C  the rest of the chamber down to the floor (open fraction 1)
  * Each cell is a compliance V/(rho c^2); each face between cells an inertance rho L / A_open (A_open = the smaller open
    area of the two cells). That is the lossless acoustic wave equation discretised by two-point fluxes.
  * The top of the hole neck connects to the outside air through the one-sided radiation conductance K1 of the traced
    hole in a baffle, computed here by an integral equation (hole_conductance()), not assumed.
  * Losses (per mode, energy weighted): viscous boundary layer on the hole and throat walls (resistance
    P/A^2 sqrt(rho mu omega/2) per unit length), radiation of the port flow (rho omega^2 / 4 pi c), heat conduction at the
    chamber walls, plus a base air loss factor air_eta [judged].
Rigid-wall modes come from the generalised eigenproblem Gamma p = omega^2 C p. Coupling to the structure is through wall
areas that move with the roof (ceiling and the liner's bottom face) and the floor.
"""
import os, json
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy import ndimage
import geom

IN = 0.0254
RHO, C0, MU, GAMMA, ALPHA_T = 1.204, 343.2, 1.81e-5, 1.4, 2.2e-5   # air at 20 C


# ------------------------------------------------------------------------------------------ f-hole geometry
def hole_raster(r=0.004):
    """Raster of the traced f-hole: mask, distance inside (to the outline) and outside, on a grid of spacing r (in)."""
    fn = os.path.join(geom.CACHE, f'hole_raster_{r:.4f}.npz')
    if os.path.exists(fn):
        z = np.load(fn); return {k: z[k] for k in z.files}
    P = geom.fc().FHOLE_POLY
    x = np.arange(P[:, 0].min() - 0.2, P[:, 0].max() + 0.2, r); y = np.arange(P[:, 1].min() - 0.2, P[:, 1].max() + 0.2, r)
    X, Y = np.meshgrid(x, y, indexing='ij')
    m = geom.inside_poly(P, X, Y)
    din = ndimage.distance_transform_edt(m) * r          # inside: distance to the nearest outside pixel
    dout = ndimage.distance_transform_edt(~m) * r
    out = dict(x=x, y=y, m=m, din=din, dout=dout, r=np.array(r))
    np.savez_compressed(fn, **out)
    return out


def _perimeter(mask, r):
    """Boundary length of a raster mask (pixel edges x pi/4, the isotropic correction)."""
    e = np.count_nonzero(mask[1:, :] != mask[:-1, :]) + np.count_nonzero(mask[:, 1:] != mask[:, :-1])
    return e * r * np.pi / 4


def throat_mask(raster, inset_mm, tool_radius_mm=0.0):
    """Optional single pocket swept by a circular cutter in the inset aperture."""
    r = float(raster['r'])
    opening = raster['m']
    if inset_mm > 0:
        opening = opening & (raster['din'] > inset_mm/25.4 + 0.5*r)
    if not tool_radius_mm:
        return opening
    radius_px = tool_radius_mm/(25.4*r)
    centers = ndimage.distance_transform_edt(opening) > radius_px
    labels, count = ndimage.label(centers)
    if not count:
        raise ValueError('Tool does not fit the throat')
    largest = 1 + np.argmax(np.bincount(labels.ravel())[1:])
    return opening & (ndimage.distance_transform_edt(labels != largest) <= radius_px)


def hole_summary(inset_mm=0.0, tool_radius_mm=0.0):
    H = hole_raster(); r = float(H['r'])
    th = throat_mask(H, inset_mm, tool_radius_mm)
    lab, n = ndimage.label(th)
    return dict(area_in2=float(H['m'].sum() * r * r), perimeter_in=_perimeter(H['m'], r),
                throat_area_in2=float(th.sum() * r * r), throat_frac=float(th.sum() / H['m'].sum()),
                throat_perimeter_in=_perimeter(th, r), throat_pieces=int(n))


def _conductance_raster(mask, d):
    """One-sided conductance (m) of an aperture in a rigid baffle, raster cells of side d (m):
    sum_j s_j A_j / (2 pi r_ij) = 1 on the aperture, K1 = sum s_j A_j. Exact for a circle: K1 = 4a."""
    ij = np.argwhere(mask); pts = ij * d; n = len(pts); A = d * d
    G = np.empty((n, n))
    for s in range(0, n, 2000):
        dx = pts[s:s + 2000, None, :] - pts[None, :, :]
        G[s:s + 2000] = A / (2 * np.pi * np.sqrt((dx ** 2).sum(-1)) + 1e-300)
    G[np.arange(n), np.arange(n)] = 4 * d * np.arcsinh(1.0) / (2 * np.pi)     # integral of 1/r over the own square
    sig = np.linalg.solve(G, np.ones(n))
    return float(sig.sum() * A)


def hole_conductance():
    """One-sided exterior conductance of the traced f-hole (m), with a circle of equal area on the same raster as the
    calibration (the raster error is the same for both; the circle's exact value is 4a)."""
    fn = os.path.join(geom.CACHE, 'hole_conductance.json')
    if os.path.exists(fn):
        return json.load(open(fn))
    P = geom.fc().FHOLE_POLY; res = {}
    S = None
    for d_in in (0.05, 0.035, 0.025):
        x = np.arange(P[:, 0].min(), P[:, 0].max(), d_in) + d_in / 2; y = np.arange(P[:, 1].min(), P[:, 1].max(), d_in) + d_in / 2
        X, Y = np.meshgrid(x, y, indexing='ij'); m = geom.inside_poly(P, X, Y)
        S = hole_summary()['area_in2'] * IN ** 2; a = np.sqrt(S / np.pi)
        R = a / (d_in * IN) + 2; g = np.arange(-int(R), int(R) + 1) * d_in * IN
        GX, GY = np.meshgrid(g, g, indexing='ij'); mc = GX ** 2 + GY ** 2 < a * a
        kt = _conductance_raster(m, d_in * IN); kc = _conductance_raster(mc, d_in * IN)
        res[str(d_in)] = dict(trace_raw=kt, circle_raw=kc, circle_exact=4 * a, trace_cal=kt * 4 * a / kc, n=int(m.sum()))
    ds = sorted(res, key=float)
    res['K1_trace'] = res[ds[0]]['trace_cal']; res['K1_circle'] = 4 * np.sqrt(S / np.pi)
    res['ratio_trace_circle'] = res['K1_trace'] / res['K1_circle']
    json.dump(res, open(fn, 'w'), indent=1)
    return res


# ------------------------------------------------------------------------------------------ the network
def build(design):
    """Assemble the air network for a design. Returns a dict with sparse Gamma, diagonal C and per-cell geometry."""
    D = design
    ts = D['top_skin_mm'] / 25.4
    F = geom.chamber_fields(ts, 0.025)
    hf = 0.025; m = int(round(D['h_air'] / hf)); h = m * hf
    gx, gy = F['gx'], F['gy']
    ch = F['ch'].astype(float)
    zc_f = np.where(F['ch'], F['zin_top'] - D['veneer_mm'] / 25.4, 0)      # veneer lowers the roof
    zf_f = np.where(F['ch'], geom.chamber_floor(F['zin_back'], D['back_skin_mm']), 0)
    # coarse columns
    nx, ny = len(gx) // m, len(gy) // m
    def blk(a): return a[:nx * m, :ny * m].reshape(nx, m, ny, m).sum((1, 3))
    fch = blk(ch) / (m * m)
    with np.errstate(invalid='ignore', divide='ignore'):
        zc = blk(zc_f * ch) / blk(ch); zf = blk(zf_f * ch) / blk(ch); zt = blk(F['zt'] * ch) / blk(ch)
    cx = gx[:nx * m].reshape(nx, m).mean(1); cy = gy[:ny * m].reshape(ny, m).mean(1)
    cx = cx - hf / 2 + hf / 2; cy = cy
    # hole / liner fractions per column from the 0.004 in raster
    Hr = hole_raster(); r = float(Hr['r']); RX, RY = np.meshgrid(Hr['x'], Hr['y'], indexing='ij')
    ci = np.floor((RX - (gx[0] - hf / 2)) / h).astype(int); cj = np.floor((RY - (gy[0] - hf / 2)) / h).astype(int)
    ok = (ci >= 0) & (ci < nx) & (cj >= 0) & (cj < ny)
    def frac(mask):
        out = np.zeros((nx, ny)); np.add.at(out, (ci[ok & mask], cj[ok & mask]), 1.0); return out * r * r / (h * h)
    def perim(mask):   # boundary pixel edges per column x pi/4
        e = np.zeros((nx, ny))
        for ax in (0, 1):
            dm = np.diff(mask.astype(np.int8), axis=ax) != 0
            sl = [slice(None)] * 2; sl[ax] = slice(1, None)
            ii, jj = ci[tuple(sl)], cj[tuple(sl)]; okk = ok[tuple(sl)] & dm
            np.add.at(e, (ii[okk], jj[okk]), 1.0)
        return e * r * np.pi / 4
    hole = Hr['m'] if D['fhole'] else np.zeros_like(Hr['m'])
    f_hole = frac(hole); P_hole = perim(hole)
    if D['liner'] == 'bare' or not D['fhole']:
        wood = np.zeros_like(hole); throat = hole
    else:
        inset_mm = D['liner_inset_mm'] if D['liner'] == 'narrowed' else 0.0
        throat = hole & throat_mask(Hr, inset_mm, D.get('liner_tool_radius_mm',0))
        wood = (hole | (Hr['dout'] <= D['liner_wall_mm'] / 25.4)) & ~throat
    f_wood = frac(wood); P_throat = perim(throat) if D['liner'] != 'bare' else np.zeros((nx, ny))
    f_hole = np.minimum(f_hole, 1.0); f_wood = np.minimum(f_wood, 1.0)
    # columns
    col = (fch > 0.02) & np.isfinite(zc) & (zc - zf > 0.02)
    I, J = np.nonzero(col); nc = len(I)
    colid = -np.ones((nx, ny), int); colid[I, J] = np.arange(nc)
    zt_c = zt[I, J]; zc_c = zc[I, J]; zf_c = zf[I, J]; fc_c = fch[I, J]
    depth = zc_c - zf_c
    LB = np.minimum(D['liner_depth_mm'] / 25.4, 0.8 * depth)
    fh_c = np.minimum(f_hole[I, J], fc_c)
    lined = D['fhole'] and D['liner'] != 'bare'
    if lined:
        f_th = np.minimum(frac(throat)[I, J], fc_c); f_out = np.clip(fc_c - f_th - f_wood[I, J], 0, None)
    else:
        f_th = fc_c.copy(); f_out = np.zeros(nc)
    nA, nB, nC = 3, 8, 5
    tA = np.where(fh_c > 0, zt_c - zc_c, 0.0)
    # layers: (stack, z_top, z_bot, f)
    L = []
    for k in range(nA):
        L.append(('A', zc_c + tA * (nA - k) / nA, zc_c + tA * (nA - k - 1) / nA, np.where(tA > 0, fh_c, 0.0)))
    for st, ff in (('Bi', f_th), ('Bo', f_out)):
        for k in range(nB):
            L.append((st, zc_c - LB * k / nB, zc_c - LB * (k + 1) / nB, ff))
    for k in range(nC):
        z0 = zc_c - LB; t = z0 - zf_c
        L.append(('C', z0 - t * k / nC, z0 - t * (k + 1) / nC, fc_c))
    nl = len(L); iA = list(range(nA)); iBi = list(range(nA, nA + nB)); iBo = list(range(nA + nB, nA + 2 * nB))
    iC = list(range(nA + 2 * nB, nl))
    ztop = np.stack([l[1] for l in L], 1); zbot = np.stack([l[2] for l in L], 1); f = np.stack([l[3] for l in L], 1)
    dz = (ztop - zbot) * IN; hm = h * IN
    alive = (f > 1e-3) & (dz > 0)
    idx = -np.ones(f.shape, int); idx[alive] = np.arange(alive.sum()); N = int(alive.sum())
    V = (hm * hm * dz * f)[alive]
    Cdiag = V / (RHO * C0 ** 2)
    P_h = P_hole[I, J] * IN; P_t = (perim(throat)[I, J] * IN) if lined else np.zeros(nc)
    vlinks = [(iA[k], iA[k + 1], fh_c, P_h) for k in range(nA - 1)] + [(iA[-1], iBi[0], np.minimum(fh_c, f_th), P_h)]
    vlinks += [(iBi[k], iBi[k + 1], f_th, P_t) for k in range(nB - 1)] + [(iBi[-1], iC[0], f_th, P_t)]
    vlinks += [(iBo[k], iBo[k + 1], f_out, 0 * P_t) for k in range(nB - 1)] + [(iBo[-1], iC[0], f_out, 0 * P_t)]
    vlinks += [(iC[k], iC[k + 1], fc_c, 0 * P_t) for k in range(nC - 1)]
    rows, cols, wts, kind = [], [], [], []
    for la, lb, fo, Pw in vlinks:
        a, b = idx[:, la], idx[:, lb]; okf = (a >= 0) & (b >= 0) & (fo > 1e-3)
        A_ = hm * hm * fo[okf]; Ld = 0.5 * (dz[okf, la] + dz[okf, lb])
        rows.append(a[okf]); cols.append(b[okf]); wts.append(A_ / (RHO * Ld))
        kind.append(np.c_[np.zeros(okf.sum()), Pw[okf], Ld, A_])
    for di, dj in ((1, 0), (0, 1)):
        ii = I + di; jj = J + dj; okc = (ii < nx) & (jj < ny)
        nb = np.full(nc, -1); nb[okc] = colid[ii[okc], jj[okc]]
        a_col = np.nonzero(nb >= 0)[0]; b_col = nb[nb >= 0]
        for k in range(nl):
            a, b = idx[a_col, k], idx[b_col, k]; okf = (a >= 0) & (b >= 0)
            A_ = hm * 0.5 * (dz[a_col[okf], k] + dz[b_col[okf], k]) * np.minimum(f[a_col[okf], k], f[b_col[okf], k])
            rows.append(a[okf]); cols.append(b[okf]); wts.append(A_ / (RHO * hm))
            kind.append(np.c_[np.ones(okf.sum()), np.zeros(okf.sum()), np.full(okf.sum(), hm), A_])
    rows = np.concatenate(rows); cols = np.concatenate(cols); wts = np.concatenate(wts); kind = np.vstack(kind)
    # exterior: top of the hole neck, through the one-sided conductance K1 of the traced hole
    K1 = hole_conductance()['K1_trace'] / D['air_mass'] if D['fhole'] else 0.0
    ext_cell = idx[:, 0]; ext = ext_cell >= 0
    S_open = float((hm * hm * f[ext, 0]).sum()) if ext.any() else 0.0
    w_ext = np.zeros(N)
    if ext.any():
        Aface = hm * hm * f[ext, 0]
        M_face = RHO / (K1 * Aface / S_open) + RHO * 0.5 * dz[ext, 0] / Aface
        w_ext[ext_cell[ext]] = 1.0 / M_face
    G = sp.coo_matrix((np.r_[-wts, -wts], (np.r_[rows, cols], np.r_[cols, rows])), shape=(N, N)).tocsr()
    G = G + sp.diags(-np.asarray(G.sum(1)).ravel() + w_ext)
    # moving walls: signed area per cell (volume DEcrease per unit upward displacement of the roof / floor)
    roof = np.zeros(f.shape); floor = np.zeros(f.shape)
    roof[:, iA[-1]] += hm * hm * np.clip(fh_c - np.minimum(fh_c, f_th), 0, None) * (tA > 0)     # ledge under the hole neck
    roof[:, iBi[0]] -= hm * hm * np.clip(f_th - np.where(tA > 0, np.minimum(fh_c, f_th), 0), 0, None)
    roof[:, iBo[0]] -= hm * hm * f_out
    roof[:, iC[0]] -= hm * hm * np.clip(fc_c - f_th - f_out, 0, None)                         # liner mouth face
    floor[:, iC[-1]] += hm * hm * fc_c
    # cells that do not exist pass their wall to the next existing cell below (roof) / above (floor)
    roof = np.where(alive, roof, 0); floor = np.where(alive, floor, 0)
    xc = np.repeat(cx[I][:, None], nl, 1); yc = np.repeat(cy[J][:, None], nl, 1); zmid = 0.5 * (ztop + zbot)
    side = np.zeros(nc)
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ii = I + di; jj = J + dj; okc = (ii >= 0) & (ii < nx) & (jj >= 0) & (jj < ny)
        nbv = np.zeros(nc, bool); nbv[okc] = col[ii[okc], jj[okc]]; side += ~nbv
    A_wall_th = (np.abs(roof) + floor + side[:, None] * hm * dz * (f > 0))[alive]
    out = dict(N=N, G=G, C=Cdiag, V=V, w_ext=w_ext, K1=K1, S_open=S_open,
               x=xc[alive], y=yc[alive], z=zmid[alive], roof=roof[alive], floor=floor[alive],
               A_wall_th=A_wall_th, faces=(rows, cols, wts, kind), h=h, volume_in3=float(V.sum() / IN ** 3),
               hole_open_in2=float(S_open / IN ** 2), throat_in2=float((hm * hm * f_th * (fh_c > 0)).sum() / IN ** 2) if lined else None,
               ncol=nc)
    return out


def modes(design, n=16, A=None):
    """Rigid-wall modes. Psi is C-normalised (Psi^T C Psi = I). Loss factor per mode from the energy-weighted losses."""
    A = build(design) if A is None else A
    G, Cd = A['G'], A['C']
    if A['K1'] == 0:
        n = min(n, 12)
    s = 1 / np.sqrt(Cd)
    Dm = sp.diags(s) @ G @ sp.diags(s)
    sigma = -1.0 if A['K1'] > 0 else -1.0
    lam, v = sla.eigsh(Dm.tocsc(), k=n, sigma=sigma, which='LM')
    o = np.argsort(lam); lam = np.clip(lam[o], 0, None); v = v[:, o]
    psi = v * s[:, None]
    w = np.sqrt(lam); fr = w / (2 * np.pi)
    rows, cols, wts, kind = A['faces']
    eta = np.zeros(n); parts = []
    for j in range(n):
        p = psi[:, j]; om = max(w[j], 1.0)
        dp = p[rows] - p[cols]
        ke_faces = wts * dp ** 2                       # = |Delta p|^2 / M  (twice the kinetic energy x omega^2 ... ratio only)
        ke_ext = A['w_ext'] * p ** 2
        ke = ke_faces.sum() + ke_ext.sum()
        # boundary layer resistance on hole/throat faces: R = P L / A^2 sqrt(rho mu om / 2); M = rho L / A
        Pw, L, Af = kind[:, 1], kind[:, 2], kind[:, 3]
        with np.errstate(divide='ignore', invalid='ignore'):
            R_over_M = np.where(Af > 0, Pw * np.sqrt(RHO * MU * om / 2) / (Af * RHO), 0.0)   # (P L/A^2 sqrt(.)) / (rho L/A)
        # radiation of the port flow: q = sum w_ext p / (i om); P_rad = R_rad |q|^2 / 2
        q = (A['w_ext'] * p).sum() / om
        Rrad = RHO * om ** 2 / (4 * np.pi * C0)
        # heat conduction at walls: eta_th = (gamma-1) delta_t / 2 * sum A_w p^2 / sum V p^2
        dt = np.sqrt(2 * ALPHA_T / om)
        e_th = (GAMMA - 1) * dt / 2 * (A['A_wall_th'] * p ** 2).sum() / (A['V'] * p ** 2).sum()
        ext_share = ke_ext.sum() / ke
        # eta = P_diss / (om E), E = 1/2 (Psi C-normalised), ke = sum w dp^2 = om^2
        eta_visc = (ke_faces * R_over_M).sum() / (om * ke) * design['liner_friction']
        eta_rad = Rrad * q ** 2 / om
        eta[j] = eta_visc + eta_rad + e_th + design['air_eta']
        parts.append(dict(f=float(fr[j]), eta_visc=float(eta_visc), eta_rad=float(eta_rad), eta_th=float(e_th),
                          eta_base=design['air_eta'], ext_share=float(ext_share), Q=float(1 / eta[j])))
    return dict(f=fr, w=w, psi=psi, eta=eta, parts=parts, A=A)


def boundary_layer_shift(design, md):
    """Frequency shift of the Helmholtz mode from the reactive half of the boundary-layer impedance (equal to its
    resistance): delta f / f = -eta_visc / 2."""
    return -md['parts'][0]['eta_visc'] / 2 * md['f'][0]
