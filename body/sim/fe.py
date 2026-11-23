"""Finite elements: orthotropic 8-node hexahedra with incompatible bending modes (Wilson-Taylor QM6), 3-D Timoshenko
beams, springs, rigid bodies. SI units inside (m, kg, N, Pa)."""
import numpy as np
import scipy.sparse as sp

G2 = np.array([-1, 1]) / np.sqrt(3.0)
NAT = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], float)
GP = np.array([[a, b, c] for a in G2 for b in G2 for c in G2])     # 8 Gauss points, weight 1


def ortho_D(E1, E2, E3, n12, n13, n23, G12, G13, G23):
    """Stiffness in Voigt order [xx, yy, zz, yz, xz, xy] for material axes 1, 2, 3 = x, y, z."""
    S = np.zeros((6, 6))
    S[0, 0], S[1, 1], S[2, 2] = 1 / E1, 1 / E2, 1 / E3
    S[0, 1] = S[1, 0] = -n12 / E1
    S[0, 2] = S[2, 0] = -n13 / E1
    S[1, 2] = S[2, 1] = -n23 / E2
    S[3, 3], S[4, 4], S[5, 5] = 1 / G23, 1 / G13, 1 / G12
    return np.linalg.inv(S)


def wood_D(EL, ER, ET, GLR, GLT, GRT, nLR, nLT, nRT, axes='LTR'):
    """Wood with L, R, T assigned to x, y, z by `axes` (e.g. 'LTR': L along x, T along y, R along z = flat-sawn top).
    Poisson ratios nu_ij = -eps_j / eps_i for stress along i."""
    E = dict(L=EL, R=ER, T=ET)
    nu = {('L', 'R'): nLR, ('L', 'T'): nLT, ('R', 'T'): nRT}
    def n(a, b):
        if (a, b) in nu: return nu[(a, b)]
        return nu[(b, a)] * E[a] / E[b]          # reciprocity nu_ab / E_a = nu_ba / E_b
    Gm = {frozenset('LR'): GLR, frozenset('LT'): GLT, frozenset('RT'): GRT}
    a1, a2, a3 = axes
    return ortho_D(E[a1], E[a2], E[a3], n(a1, a2), n(a1, a3), n(a2, a3), Gm[frozenset(a1 + a2)], Gm[frozenset(a1 + a3)],
                   Gm[frozenset(a2 + a3)])


def iso_D(E, nu):
    G = E / (2 * (1 + nu)); return ortho_D(E, E, E, nu, nu, nu, G, G, G)


def _shape(xi):
    """N (8,) and dN/dxi (3, 8) at natural point xi."""
    s = NAT
    N = 0.125 * (1 + s[:, 0] * xi[0]) * (1 + s[:, 1] * xi[1]) * (1 + s[:, 2] * xi[2])
    dN = 0.125 * np.array([s[:, 0] * (1 + s[:, 1] * xi[1]) * (1 + s[:, 2] * xi[2]),
                           s[:, 1] * (1 + s[:, 0] * xi[0]) * (1 + s[:, 2] * xi[2]),
                           s[:, 2] * (1 + s[:, 0] * xi[0]) * (1 + s[:, 1] * xi[1])])
    return N, dN


_SH = [_shape(g) for g in GP]
_N = np.array([a for a, _ in _SH])            # (8 gp, 8 nodes)
_dN = np.array([b for _, b in _SH])           # (8 gp, 3, 8)
_dN0 = _shape(np.zeros(3))[1]


def _Bmat(dNx):
    """dNx (E, 3, n) -> B (E, 6, 3n), Voigt [xx, yy, zz, yz, xz, xy]."""
    E, _, n = dNx.shape
    B = np.zeros((E, 6, 3 * n))
    B[:, 0, 0::3] = dNx[:, 0]; B[:, 1, 1::3] = dNx[:, 1]; B[:, 2, 2::3] = dNx[:, 2]
    B[:, 3, 1::3] = dNx[:, 2]; B[:, 3, 2::3] = dNx[:, 1]
    B[:, 4, 0::3] = dNx[:, 2]; B[:, 4, 2::3] = dNx[:, 0]
    B[:, 5, 0::3] = dNx[:, 1]; B[:, 5, 1::3] = dNx[:, 0]
    return B


def hex_matrices(X, D, rho):
    """X (E, 8, 3) node coordinates, D (E, 6, 6), rho (E,). Returns Ke (E, 24, 24) condensed QM6 and Me (E, 24, 24)."""
    E = X.shape[0]
    J0 = np.einsum('in,enj->eij', _dN0, X); det0 = np.linalg.det(J0); iJ0 = np.linalg.inv(J0)
    Kuu = np.zeros((E, 24, 24)); Kua = np.zeros((E, 24, 9)); Kaa = np.zeros((E, 9, 9)); Me = np.zeros((E, 8, 8))
    for g in range(8):
        J = np.einsum('in,enj->eij', _dN[g], X); det = np.linalg.det(J); iJ = np.linalg.inv(J)
        dNx = np.einsum('eij,jn->ein', iJ, _dN[g])
        B = _Bmat(dNx)
        xi = GP[g]
        dP = np.diag(-2 * xi)                                    # (3 incompatible fns, 3 derivs): dP_a/dxi_b
        dPx = np.einsum('eij,aj->eia', iJ0, dP) * (det0 / det)[:, None, None]    # Taylor: centroid Jacobian
        Ba = _Bmat(dPx)                                          # (E, 6, 9)
        DB = D @ B; DBa = D @ Ba
        w = det[:, None, None]
        Kuu += np.einsum('eki,ekj->eij', B, DB) * w
        Kua += np.einsum('eki,ekj->eij', B, DBa) * w
        Kaa += np.einsum('eki,ekj->eij', Ba, DBa) * w
        Me += rho[:, None, None] * np.einsum('i,j->ij', _N[g], _N[g])[None] * w
    Ke = Kuu - Kua @ np.linalg.solve(Kaa, np.transpose(Kua, (0, 2, 1)))
    Ke = 0.5 * (Ke + np.transpose(Ke, (0, 2, 1)))
    M24 = np.zeros((E, 24, 24))
    for d in range(3):
        M24[:, d::3, d::3] = Me
    return Ke, M24


def assemble(conn_dof, Ke, ndof):
    """conn_dof (E, nd) global dofs, Ke (E, nd, nd) -> csr."""
    E, nd = conn_dof.shape
    r = np.repeat(conn_dof, nd, axis=1).ravel(); c = np.tile(conn_dof, (1, nd)).ravel()
    return sp.csr_matrix((Ke.ravel(), (r, c)), shape=(ndof, ndof))


# ----------------------------------------------------------------------------------------------- beams
def beam_matrices(xa, xb, EA, EIy, EIz, GJ, GAy, GAz, rhoA, rhoIp, rhoIy, rhoIz, vref=(0, 0, 1)):
    """3-D Timoshenko beam (12 dof: u,v,w,rx,ry,rz at a then b), global coordinates. Local x along the beam, local y
    horizontal (perpendicular to x and vref), local z ~ vref. Iy = bending about local y (vertical bending, uses EIy).
    Lumped mass with rotary inertia."""
    d = np.asarray(xb, float) - np.asarray(xa, float); L = np.linalg.norm(d); ex = d / L
    ez = np.asarray(vref, float) - np.dot(vref, ex) * ex; ez /= np.linalg.norm(ez); ey = np.cross(ez, ex)
    R = np.array([ex, ey, ez])
    py = 12 * EIz / (GAy * L * L); pz = 12 * EIy / (GAz * L * L)
    K = np.zeros((12, 12))
    K[0, 0] = K[6, 6] = EA / L; K[0, 6] = K[6, 0] = -EA / L
    K[3, 3] = K[9, 9] = GJ / L; K[3, 9] = K[9, 3] = -GJ / L
    # bending in x-y plane (v, rz) uses EIz
    a = EIz / (L ** 3 * (1 + py))
    for (i, j, v) in [(1, 1, 12), (1, 5, 6 * L), (1, 7, -12), (1, 11, 6 * L), (5, 5, (4 + py) * L * L), (5, 7, -6 * L),
                      (5, 11, (2 - py) * L * L), (7, 7, 12), (7, 11, -6 * L), (11, 11, (4 + py) * L * L)]:
        K[i, j] = K[j, i] = a * v
    b = EIy / (L ** 3 * (1 + pz))
    for (i, j, v) in [(2, 2, 12), (2, 4, -6 * L), (2, 8, -12), (2, 10, -6 * L), (4, 4, (4 + pz) * L * L), (4, 8, 6 * L),
                      (4, 10, (2 - pz) * L * L), (8, 8, 12), (8, 10, 6 * L), (10, 10, (4 + pz) * L * L)]:
        K[i, j] = K[j, i] = b * v
    m = rhoA * L / 2
    M = np.diag([m, m, m, rhoIp * L / 2, rhoIy * L / 2 + m * L * L / 12 * 0.0, rhoIz * L / 2] * 2)
    # translational-rotational consistency: add small rotary terms from the lumped translational mass (L^2/12 rule)
    M[4, 4] += m * L * L / 12; M[5, 5] += m * L * L / 12; M[10, 10] += m * L * L / 12; M[11, 11] += m * L * L / 12
    T = np.zeros((12, 12))
    for k in range(4):
        T[3 * k:3 * k + 3, 3 * k:3 * k + 3] = R
    return T.T @ K @ T, T.T @ M @ T


def skew(r):
    return np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])


def rigid_point(r):
    """3x6 map from rigid-body dofs (u, theta) about a reference to the displacement of a point at offset r."""
    return np.hstack([np.eye(3), -skew(r)])


def point_mass_6(m, r, Icm=None):
    """6x6 mass matrix of a point mass (plus optional inertia tensor about its own centre) at offset r from a node."""
    T = rigid_point(r)
    M = m * T.T @ T
    if Icm is not None:
        M[3:, 3:] += Icm
    return M
