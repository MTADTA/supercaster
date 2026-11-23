"""Closed exterior surface of the body for the BEM (top, back, side wall), from the carve, and its radiation
resistance factors cached in sim/cache (the exterior is the same for every hidden-interior design)."""
import os, json, time
import numpy as np
from scipy.spatial import Delaunay
import geom, bem

IN = 0.0254
FREQS = np.r_[np.geomspace(50, 1150, 34)]


def body_surface(hp=0.6):
    F = geom.fc()
    EO = np.asarray(F.EO); per = float(F.EPER)
    nb = int(np.ceil(per / hp)); s = np.linspace(0, len(EO), nb, endpoint=False).astype(int)
    bpts = EO[s]
    if np.sum(bpts[:, 0] * np.roll(bpts[:, 1], -1) - np.roll(bpts[:, 0], -1) * bpts[:, 1]) < 0:
        bpts = bpts[::-1].copy()                     # counter-clockwise seen from the top
    gx = np.arange(12.9, 31.4, hp); gy = np.arange(-6.6, 6.6, hp) + hp / 2
    GX, GY = np.meshgrid(gx, gy, indexing='ij'); g = np.c_[GX.ravel(), GY.ravel()]
    sd = F.outline_sdf(g[:, 0], g[:, 1]); g = g[sd > 0.35 * hp]
    # refine around the f-hole so it is covered by small panels
    pts = np.vstack([bpts, g])
    tri = Delaunay(pts); Tp = tri.simplices
    cen = pts[Tp].mean(1); keep = F.outline_sdf(cen[:, 0], cen[:, 1]) > 0
    Tp = Tp[keep]
    cr = np.cross(np.c_[pts[Tp[:, 1]] - pts[Tp[:, 0]], np.zeros(len(Tp))], np.c_[pts[Tp[:, 2]] - pts[Tp[:, 0]], np.zeros(len(Tp))])[:, 2]
    Tp[cr < 0] = Tp[cr < 0][:, ::-1]
    n = len(pts)
    zt = -F.top_full(pts[:, 0], pts[:, 1]); zb = -F.P['THICK'] + F.back_full(pts[:, 0], pts[:, 1])
    zm = 0.5 * (zt + zb)
    V = np.vstack([np.c_[pts, zt], np.c_[pts, zb], np.c_[pts[:nb], zm[:nb]]])
    T_top = Tp; T_bot = Tp[:, ::-1] + n
    side = []
    for i in range(nb):
        j = (i + 1) % nb
        a_t, b_t = i, j; a_m, b_m = 2 * n + i, 2 * n + j; a_b, b_b = n + i, n + j
        side += [[a_t, a_m, b_m], [a_t, b_m, b_t], [a_m, a_b, b_b], [a_m, b_b, b_m]]
    side = np.array(side)
    # side quads traverse the top boundary edge backwards (outline counter-clockwise), so their normals point outward
    T = np.vstack([T_top, T_bot, side])
    kind = np.r_[np.zeros(len(T_top), int), np.ones(len(T_bot), int), np.full(len(side), 2)]
    P = bem.panel_data(V * IN, T); P['kind'] = kind; P['nb'] = nb; P['nplan'] = n
    return P


def radiation_cache(verbose=True):
    fn = os.path.join(geom.CACHE, 'bem_body_v1.npz')
    if os.path.exists(fn):
        z = np.load(fn)
        P = {k[2:]: z[k] for k in z.files if k.startswith('P_')}
        return dict(P=P, freqs=z['freqs'], L=[z[f'L{k:02d}'] for k in range(len(z['freqs']))])
    t0 = time.time(); P = body_surface()
    Ls = []
    for f in FREQS:
        R = bem.resistance(P, f); Ls.append(bem.factor(R))
        if verbose: print(f'[bem] {f:.0f} Hz rank {Ls[-1].shape[1]} ({time.time() - t0:.0f}s)', flush=True)
    np.savez(fn, freqs=FREQS, **{f'P_{k}': np.asarray(v) for k, v in P.items()}, **{f'L{k:02d}': L for k, L in enumerate(Ls)})
    return dict(P=P, freqs=FREQS, L=Ls)
