"""Lug-level netlist of the Supercaster control circuit, plus a tiny MNA solver.

Pure Python (no numpy). Every wire in WIRES is one solder joint group; the
switch tables below are the only place switching lives. verify_switching.py
builds on this file, so the doc's tone chart comes from the same netlist the
builder solders. No pickup coil values live here: the caller passes impedances.
"""
import cmath, math

# ---------------------------------------------------------------- netlist
# Superswitch (4P5T). SS{pole}_C is the pole common, SS{pole}_L{pos} the lug
# that pole connects to in position pos (1 = bridge, 5 = neck).
# Pickup lead names:
#   N1, N2  neck leads (go to the phase toggle commons). Normal: N1 -> "N+".
#   M+, M-  middle hot / return.
#   A+      bridge humbucker hot end (coil A).
#   BJ      junction of coil A and coil B (series link inside the humbucker).
#   B-      cold end of coil B.
WIRES = [
    # superswitch commons
    ("SS1_C", "OUT"), ("SS2_C", "XC"), ("SS3_C", "YH"), ("SS4_C", "PR"),
    # pole 1 = slot X hot -> output
    ("SS1_L1", "A+"), ("SS1_L2", "A+"),
    ("SS1_L4", "N+"), ("SS1_L5", "N+"),
    # pole 2 = slot X return
    ("SS2_L2", "BJ"), ("SS2_L4", "N-"),
    # pole 3 = slot Y hot
    ("SS3_L2", "M+"), ("SS3_L3", "N+"), ("SS3_L4", "M+"),
    # pole 4 = return of slot Y / of a lone pickup -> PR
    ("SS4_L1", "B-"), ("SS4_L2", "M-"), ("SS4_L3", "N-"),
    ("SS4_L4", "M-"), ("SS4_L5", "N-"),
    # series toggle (DPDT on-on). pole a common = YH, pole b common = XC
    ("SER_a_C", "YH"), ("SER_a_P", "OUT"), ("SER_a_S", "XC"),
    ("SER_b_C", "XC"), ("SER_b_P", "PR"),          # SER_b_S unused
    # phase toggle (DPDT on-on, crossover): commons = neck leads
    ("PH_1_C", "N1"), ("PH_1_NORM", "N+"), ("PH_1_FLIP", "N-"),
    ("PH_2_C", "N2"), ("PH_2_NORM", "N-"), ("PH_2_FLIP", "N+"),
    # piezo toggle (SPDT on-off-on, or one pole of a DPDT on-off-on)
    ("PZ_C", "PR"), ("PZ_UP", "GND"), ("PZ_DOWN", "OUT"),   # centre = open
    # piezo disc and its 1M rheostat sit between PR and true ground
    ("DISC_SILVER", "PR"), ("DISC_BRASS", "GND"),
    ("POT1M_L1", "PR"), ("POT1M_W", "GND"),       # lug 3 left free (rheostat)
]

# Position 3's bridge coil (pole 1 lug 3 = its hot, pole 2 lug 3 = its return).
# VARIANT "A":       always coil A (the original design; position 3 in phase hums).
# VARIANT "auto":    4PDT PHASE toggle. Its poles 3 and 4 pick coil B (opposite
#                    magnet to the neck) when PHASE is normal and coil A when
#                    flipped, so position 3 humbucks both ways.
# VARIANT "B":       always coil B (DPDT PHASE; position 3 out of phase hums).
VARIANT_WIRES = {
    "A":    [("SS1_L3", "A+"), ("SS2_L3", "BJ")],
    "B":    [("SS1_L3", "BJ"), ("SS2_L3", "B-")],
    "auto": [("SS1_L3", "PH_3_C"), ("PH_3_NORM", "BJ"), ("PH_3_FLIP", "A+"),
             ("SS2_L3", "PH_4_C"), ("PH_4_NORM", "B-"), ("PH_4_FLIP", "BJ")],
}
VARIANT = "auto"

def all_wires():
    return WIRES + VARIANT_WIRES[VARIANT]

def closures(pos, series, flip, piezo):
    """Switch contacts closed in one state. piezo in {'off','blend','solo'}."""
    c = [(f"SS{p}_C", f"SS{p}_L{pos}") for p in (1, 2, 3, 4)]
    if series:
        c += [("SER_a_C", "SER_a_S"), ("SER_b_C", "SER_b_S")]
    else:
        c += [("SER_a_C", "SER_a_P"), ("SER_b_C", "SER_b_P")]
    t = "FLIP" if flip else "NORM"
    c += [("PH_1_C", f"PH_1_{t}"), ("PH_2_C", f"PH_2_{t}"),
          ("PH_3_C", f"PH_3_{t}"), ("PH_4_C", f"PH_4_{t}")]   # poles 3-4 unused unless VARIANT "auto"
    if piezo == "off":
        c += [("PZ_C", "PZ_UP")]
    elif piezo == "solo":
        c += [("PZ_C", "PZ_DOWN")]
    return c

# two-terminal sources: name -> (minus terminal, plus terminal)
COILS = {"N": ("N2", "N1"), "M": ("M-", "M+"), "A": ("BJ", "A+"), "B": ("B-", "BJ")}
PIEZO = ("DISC_BRASS", "DISC_SILVER")
POT = ("POT1M_W", "POT1M_L1")


class UF:
    def __init__(self): self.p = {}
    def f(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def u(self, a, b): self.p[self.f(a)] = self.f(b)


def nets_for(state):
    uf = UF()
    for a, b in all_wires(): uf.u(a, b)
    for a, b in closures(*state): uf.u(a, b)
    return uf


# ---------------------------------------------------------------- MNA solver
def solve(elems, ground, out):
    """elems: list of (kind, n1, n2, value[, emf]).
    kind 'Z': impedance value between n1,n2.
    kind 'V': EMF `emf` in series with impedance `value`, + at n2.
    Returns complex voltage of `out` relative to `ground`."""
    nodes = sorted({n for e in elems for n in e[1:3]} - {ground})
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    G = [[0j] * n for _ in range(n)]
    I = [0j] * n
    for i in range(n):            # 1 Tohm leak keeps floating nets solvable
        G[i][i] += 1e-12
    for e in elems:
        kind, a, b, z = e[0], e[1], e[2], e[3]
        y = 1 / z
        for p, q in ((a, b), (b, a)):
            if p in idx:
                G[idx[p]][idx[p]] += y
                if q in idx: G[idx[p]][idx[q]] -= y
        if kind == "V":           # Norton equivalent: current emf/z into b
            emf = e[4]
            if b in idx: I[idx[b]] += emf * y
            if a in idx: I[idx[a]] -= emf * y
    # Gaussian elimination with partial pivoting
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(G[r][c]))
        G[c], G[piv] = G[piv], G[c]; I[c], I[piv] = I[piv], I[c]
        for r in range(c + 1, n):
            f = G[r][c] / G[c][c]
            if f:
                for k in range(c, n): G[r][k] -= f * G[c][k]
                I[r] -= f * I[c]
    v = [0j] * n
    for r in range(n - 1, -1, -1):
        s = I[r] - sum(G[r][k] * v[k] for k in range(r + 1, n))
        v[r] = s / G[r][r]
    return v[idx[out]] if out in idx else 0j


def circuit(state, coil_z, piezo_z, pot_ohms, load_elems, active):
    """Build element list on merged nets. `active` = name of the one source
    switched on (superposition); coil_z/piezo_z map name -> impedance."""
    uf = nets_for(state)
    R = uf.f
    el = []
    for name, (mn, pl) in COILS.items():
        el.append(("V", R(mn), R(pl), coil_z[name], 1.0 if active == name else 0.0))
    el.append(("V", R(PIEZO[0]), R(PIEZO[1]), piezo_z, 1.0 if active == "P" else 0.0))
    el.append(("Z", R(POT[0]), R(POT[1]), max(pot_ohms, 1e-3)))
    for kind, a, b, z in load_elems(R):
        el.append((kind, a, b, z))
    if R("OUT") == R("GND"):
        return 0j
    return solve([e for e in el if e[1] != e[2]], R("GND"), R("OUT"))
