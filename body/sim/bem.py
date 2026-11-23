"""Exterior radiation by a boundary-element method: constant triangular panels, collocation at centroids, conventional
boundary integral equation  p/2 - int p dG/dn dS = i omega rho int G v_n dS  (time convention e^{i omega t}, n out of
the body). Below the first interior Dirichlet resonance of the body volume (about 3.5 kHz for a 44 mm thick body) the
equation has no fictitious frequencies, so no Burton-Miller term is needed up to 1.1 kHz.

radiation_factors() returns, per frequency, L with R = L L^T, where R is the real symmetric radiation resistance matrix
of the panels: radiated power W = 1/2 v^H R v (v = complex normal velocities of the panels).
"""
import numpy as np
import scipy.linalg as sl

RHO, C0 = 1.204, 343.2

# Dunavant degree-4, 6 points (barycentric, weights sum to 1)
_QA = np.array([[0.445948490915965, 0.445948490915965, 0.108103018168070], [0.445948490915965, 0.108103018168070, 0.445948490915965],
                [0.108103018168070, 0.445948490915965, 0.445948490915965], [0.091576213509771, 0.091576213509771, 0.816847572980459],
                [0.091576213509771, 0.816847572980459, 0.091576213509771], [0.816847572980459, 0.091576213509771, 0.091576213509771]])
_QW = np.array([0.223381589678011] * 3 + [0.109951743655322] * 3)


def panel_data(V, T):
    """V (nv, 3) vertices (m), T (np, 3) triangles (counter-clockwise seen from outside)."""
    A_, B_, C_ = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    cr = np.cross(B_ - A_, C_ - A_); area = 0.5 * np.linalg.norm(cr, axis=1); n = cr / (2 * area[:, None])
    cen = (A_ + B_ + C_) / 3
    qp = np.einsum('qk,pkd->pqd', _QA, np.stack([A_, B_, C_], 1))       # (np, 6, 3)
    return dict(V=V, T=T, area=area, n=n, cen=cen, qp=qp, size=np.sqrt(area))


def _self_int_1_over_r(P, i):
    """Integral of 1/r over triangle i from its centroid (analytic, in-plane)."""
    tri = P['V'][P['T'][i]]; x = P['cen'][i]; s = 0.0
    for a, b in ((0, 1), (1, 2), (2, 0)):
        pa, pb = tri[a], tri[b]; e = pb - pa; L = np.linalg.norm(e); t = e / L
        d = np.linalg.norm(np.cross(x - pa, t))       # distance to the edge line
        t1 = np.dot(pa - x, t); t2 = np.dot(pb - x, t)
        s += d * (np.arcsinh(t2 / d) - np.arcsinh(t1 / d))
    return s


def system(P, k, near_factor=2.5, nsub=4):
    """Matrices H (p/2 - int p dG/dn) and Gm (int G) for wavenumber k."""
    cen, qp, n, area = P['cen'], P['qp'], P['n'], P['area']; N = len(cen)
    H = np.zeros((N, N), complex); Gm = np.zeros((N, N), complex)
    w = _QW[None, :] * area[:, None]        # (np, 6)
    for s0 in range(0, N, 400):
        x = cen[s0:s0 + 400]                                    # (b, 3)
        d = x[:, None, None, :] - qp[None]                      # (b, np, 6, 3)
        r = np.sqrt((d ** 2).sum(-1)); r = np.maximum(r, 1e-12)
        ekr = np.exp(-1j * k * r)
        G = ekr / (4 * np.pi * r)
        dGdn = ekr * (1 + 1j * k * r) * np.einsum('bpqd,pd->bpq', d, n) / (4 * np.pi * r ** 3)
        Gm[s0:s0 + 400] = (G * w[None]).sum(-1); H[s0:s0 + 400] = -(dGdn * w[None]).sum(-1)
    # near-singular and singular corrections
    size = P['size']
    dist = np.sqrt(((cen[:, None, :] - cen[None, :, :]) ** 2).sum(-1))
    near = np.argwhere((dist < near_factor * np.maximum(size[:, None], size[None, :])))
    # subdivided quadrature for near pairs (excluding self)
    bary = []
    m = nsub
    for i in range(m):
        for j in range(m - i):
            # upright sub-triangle
            bary.append(np.array([[i, j], [i + 1, j], [i, j + 1]]) / m)
            if i + j < m - 1:
                bary.append(np.array([[i + 1, j], [i + 1, j + 1], [i, j + 1]]) / m)
    bary = np.array(bary)                                  # (ns, 3, 2) in (u, v)
    sub_q = []
    for tri in bary:
        uv = np.einsum('qk,kd->qd', _QA, tri)              # (6, 2)
        sub_q.append(uv)
    sub_q = np.concatenate(sub_q); sub_w = np.tile(_QW, len(bary)) / len(bary)
    for i, j in near:
        if i == j: continue
        tri = P['V'][P['T'][j]]; pts = tri[0] + sub_q[:, :1] * (tri[1] - tri[0]) + sub_q[:, 1:] * (tri[2] - tri[0])
        d = cen[i] - pts; r = np.sqrt((d ** 2).sum(-1)); ekr = np.exp(-1j * k * r)
        ww = sub_w * area[j]
        Gm[i, j] = (ekr / (4 * np.pi * r) * ww).sum()
        H[i, j] = -(ekr * (1 + 1j * k * r) * (d @ n[j]) / (4 * np.pi * r ** 3) * ww).sum()
    for i in range(N):
        s = _self_int_1_over_r(P, i)
        Gm[i, i] = s / (4 * np.pi) + (-1j * k) * area[i] / (4 * np.pi) - (k * k) * 0.0
        H[i, i] = 0.5
    return H, Gm


def impedance(P, f):
    """Panel pressures per unit normal velocity: p = Z v."""
    k = 2 * np.pi * f / C0; om = 2 * np.pi * f
    H, Gm = system(P, k)
    Z = sl.solve(H, 1j * om * RHO * Gm)
    return Z


def resistance(P, f):
    Z = impedance(P, f); A = P['area']
    Za = A[:, None] * Z                       # W = 1/2 Re(v^H diag(A) Z v)
    R = 0.5 * (Za + Za.conj().T)
    return R.real


def factor(R, rel=1e-7):
    w, U = np.linalg.eigh(R)
    keep = w > rel * w.max()
    return (U[:, keep] * np.sqrt(w[keep])).astype(np.float32)


# ------------------------------------------------------------------------------- verification geometries
def sphere(a, n_sub=3):
    """Icosphere of radius a."""
    t = (1 + 5 ** 0.5) / 2
    V = np.array([[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
                  [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]], float)
    F = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
         [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
    V = list(V / np.linalg.norm(V, axis=1)[:, None])
    for _ in range(n_sub):
        cache = {}; F2 = []
        def mid(a_, b_):
            key = tuple(sorted((a_, b_)))
            if key not in cache:
                m = (V[a_] + V[b_]) / 2; V.append(m / np.linalg.norm(m)); cache[key] = len(V) - 1
            return cache[key]
        for a_, b_, c_ in F:
            ab, bc, ca = mid(a_, b_), mid(b_, c_), mid(c_, a_)
            F2 += [[a_, ab, ca], [b_, bc, ab], [c_, ca, bc], [ab, bc, ca]]
        F = F2
    V = np.array(V) * a; T = np.array(F)
    cen = V[T].mean(1); cr = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    flip = (cr * cen).sum(1) < 0; T[flip] = T[flip][:, ::-1]
    return V, T


def pillbox(a, t, n_r=10, n_th=40):
    """Closed thin cylinder (disc of radius a, thickness t), outward normals."""
    V = [[0, 0, t / 2], [0, 0, -t / 2]]; T = []
    rings = []
    for side, z in ((0, t / 2), (1, -t / 2)):
        idx = []
        for ir in range(1, n_r + 1):
            r = a * ir / n_r; row = []
            for it in range(n_th):
                th = 2 * np.pi * it / n_th; V.append([r * np.cos(th), r * np.sin(th), z]); row.append(len(V) - 1)
            idx.append(row)
        rings.append(idx)
    for side in (0, 1):
        c = side; R = rings[side]
        for it in range(n_th):
            a_, b_ = R[0][it], R[0][(it + 1) % n_th]; T.append([c, a_, b_])
        for ir in range(n_r - 1):
            for it in range(n_th):
                a_, b_ = R[ir][it], R[ir][(it + 1) % n_th]; c_, d_ = R[ir + 1][it], R[ir + 1][(it + 1) % n_th]
                T += [[a_, c_, d_], [a_, d_, b_]]
    top, bot = rings[0][-1], rings[1][-1]
    for it in range(n_th):
        a_, b_ = top[it], top[(it + 1) % n_th]; c_, d_ = bot[it], bot[(it + 1) % n_th]
        T += [[a_, c_, d_], [a_, d_, b_]]
    V = np.array(V, float); T = np.array(T)
    cen = V[T].mean(1); cr = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    out = cen.copy(); out[:, 2] = np.where(np.abs(cr[:, 2]) > 1e-12 * 0 + 0.5 * np.linalg.norm(cr, axis=1), cen[:, 2], 0)
    flip = (cr * out).sum(1) < 0; T[flip] = T[flip][:, ::-1]
    return V, T


def verify():
    """Pulsating and oscillating sphere (exact) and a rigid thin disc translating (low-frequency dipole limit)."""
    out = {}
    a = 0.1; V, T = sphere(a, 3); P = panel_data(V, T)
    for f in (100.0, 500.0, 1000.0):
        k = 2 * np.pi * f / C0; R = resistance(P, f)
        v0 = np.ones(len(T)); W = 0.5 * v0 @ R @ v0
        Wex = 0.5 * RHO * C0 * 4 * np.pi * a * a * (k * a) ** 2 / (1 + (k * a) ** 2)
        vz = P['n'][:, 2]; W1 = 0.5 * vz @ R @ vz
        ka = k * a
        W1ex = 0.5 * RHO * C0 * (4 * np.pi * a * a / 3) * ka ** 4 / (4 + ka ** 4)
        out[f'sphere_pulsating_{int(f)}Hz_dB_err'] = float(10 * np.log10(W / Wex))
        out[f'sphere_oscillating_{int(f)}Hz_dB_err'] = float(10 * np.log10(W1 / W1ex))
    # thin disc: radius 0.17 m, thickness 0.044 m (guitar-like), rigid translation along its axis.
    a, t = 0.17, 0.008; V, T = pillbox(a, t, 12, 56); P = panel_data(V, T)
    for f in (60.0, 120.0):
        k = 2 * np.pi * f / C0; R = resistance(P, f); vz = P['n'][:, 2]; W = 0.5 * vz @ R @ vz
        # low-frequency limit: dipole of volume moment D = (8/3 a^3 + V_body) U for a thin disc (V_body = pi a^2 t)
        Dm = (8 / 3 * a ** 3 * (1 + 0.0) + np.pi * a * a * t) * 1.0
        Wd = RHO * (2 * np.pi * f) ** 4 * Dm ** 2 / (24 * np.pi * C0 ** 3)
        # monopole-sum estimate (no scattering), for comparison: only the body volume term
        Wm = RHO * (2 * np.pi * f) ** 4 * (np.pi * a * a * t) ** 2 / (24 * np.pi * C0 ** 3)
        out[f'disc_translating_{int(f)}Hz_dB_vs_thin_disc_dipole'] = float(10 * np.log10(W / Wd))
        out[f'disc_monopole_sum_estimate_{int(f)}Hz_dB_vs_dipole'] = float(10 * np.log10(Wm / Wd))
    return out
