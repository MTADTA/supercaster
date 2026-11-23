"""Structural model: layered orthotropic solid mesh of the body (skins as solid-shell QM6 elements with their real
thickness fields from final_carve), pickguard plate on screws and contact springs, set neck + headstock as Timoshenko
beams with tuner masses, floating tremolo as a 6-dof rigid body on pivot springs, trem springs and string axial springs,
player contacts as spring-dashpots. Units: inches for geometry input, SI inside the matrices.
"""
import os, json, time, hashlib
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy import ndimage
import geom, fe, materials

IN = 0.0254
NL = 8   # node levels per column (7 element layers)


def _interp(F, arr, x, y, order=1):
    hf = F['gx'][1] - F['gx'][0]
    c = np.stack([(np.asarray(x) - F['gx'][0]) / hf, (np.asarray(y) - F['gy'][0]) / hf])
    return ndimage.map_coordinates(np.asarray(arr, float), c.reshape(2, -1), order=order, mode='nearest').reshape(np.shape(x))


def _rect(x, y, x0, x1, y0, y1):
    return (x >= x0) & (x <= x1) & (y >= y0) & (y <= y1)


def _capsule(x, y, pts, r):
    m = np.zeros(np.shape(x), bool)
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        dx, dy = bx - ax, by - ay; t = np.clip(((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy), 0, 1)
        m |= np.hypot(x - ax - t * dx, y - ay - t * dy) < r
    return m


STRINGS = dict(   # name, open f0 (Hz), tension N [literature: D'Addario EXL110 10-46 tension chart, 25.5 in], core dia (in)
    E2=(82.41, 77.8, 0.018), A2=(110.0, 86.7, 0.016), D3=(146.83, 81.8, 0.0135),
    G3=(196.0, 73.8, 0.017), B3=(246.94, 68.5, 0.013), E4=(329.63, 72.1, 0.010))
SNAMES = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
Y_NUT = [0.7, 0.42, 0.14, -0.14, -0.42, -0.7]
Y_SADDLE = [1.1, 0.66, 0.22, -0.22, -0.66, -1.1]
X_SADDLE = 25.5
Z_SADDLE = 0.55      # string height above the body top at the saddle (in)
Z_NUT = 0.42


NECK_INSERTS = []        # set by neck_inserts(D) inside build(); list of (x0, x1, fibers)
NECK_SCALE = [1.0, 1.0]  # maple_E, maple_rho applied to the neck beam too (set in neck_inserts; before 2026-11-13 they scaled the tenon only)
NECK_TENDON = []         # (x_a, x_b, z_local, EA) anchored-rod axial springs
ROD_SRC = dict(
    oneway_steel='single 3/16 in (4.76 mm) steel rod, 17 in, centre 0.45 in below the board top [judged geometry]; mass '
                 '= geometry x 7850 kg/m3 + 6 g nut/anchor [computed]',
    twoway_steel='StewMac Hot Rod type: two 3/16 in steel rods stacked in a 7/32 x 7/16 in slot under the board, 17 in; '
                 'listed weight of the 18 in slotted-nut Hot Rod 0.3075 lb = 139 g [literature: stewmac.com Hot Rod listing, '
                 'via search summary]; modelled as rods (geometry x 7850) + nut/blocks to that weight [computed]',
    twoway_ti='same geometry in Ti-6Al-4V (E 114 GPa, 4430 kg/m3) [literature: standard alloy data]; ~72 g + 8 g ends '
              '[computed]; vendors claim ~50 % saving vs steel two-way [literature: philadelphialuthiertools listing, via search]',
    carbon='two pultruded carbon bars 1/8 x 3/8 in, 16 in, either side of the slot (y = +-0.22 in), epoxied; '
           'E_L 135 GPa, 1550 kg/m3 [judged: typical pultruded unidirectional carbon]',
)


def neck_inserts(D):
    """Fill NECK_INSERTS / NECK_TENDON for the design. Units: in, in^2, Pa, kg/m3 (section sums are in inch units)."""
    NECK_INSERTS.clear(); NECK_TENDON.clear(); lumps = []
    NECK_SCALE[0] = float(D.get('maple_E', 1.0)); NECK_SCALE[1] = float(D.get('maple_rho', 1.0))
    rod = D.get('truss_rod', 'none'); cpl = D.get('rod_coupling', 'tendon')
    M = materials.load(); Em, rm = M['maple']['EL'] * NECK_SCALE[0], M['maple']['rho'] * NECK_SCALE[1]
    d = 0.1875; Ar = np.pi * d * d / 4; Ir = np.pi * d ** 4 / 64
    fib = []
    if rod != 'none':
        if rod == 'oneway_steel':
            E, rho, zs, slot = 200e9, 7850.0, [-0.45], (0.1875, 0.25, -0.45)        # slot w, h, centre z
            ends = 0.006
        else:
            E, rho = (200e9, 7850.0) if rod == 'twoway_steel' else (114e9, 4430.0)
            zs = [-0.2 - 0.4375 + d / 2, -0.2 - 0.4375 + 1.5 * d]; slot = (7 / 32, 0.4375, -0.2 - 0.4375 / 2)
            # steel: rods + ends to the listed 139 g at 18 in (rods 0.457 m x 2 x 17.8 mm2 x 7850 = 128 g) -> ends 11 g
            ends = 0.011 if rod == 'twoway_steel' else 0.008
        w, hh, zc_ = slot
        fib.append((0.0, zc_, w * hh, -Em, -rm, 0.0, 0.0, 0.0))                  # slot void (filler strip neglected)
        for z in zs:
            if cpl == 'bonded':   fib.append((0.0, z, Ar, E, rho, E, Ir, Ir))
            elif cpl == 'tendon': fib.append((0.0, z, Ar, 0.0, rho, E, Ir, Ir))
            else:                 fib.append((0.0, z, Ar, 0.0, rho, 0.0, Ir, Ir))
        if cpl == 'tendon':
            NECK_TENDON.append((0.0, 17.0, float(np.mean(zs)), E * Ar * len(zs) * 0.0254 ** 2))
        lumps.append((-0.3, ends * 0.6)); lumps.append((17.0, ends * 0.4))   # adjuster at the headstock, anchor at the heel
    if D.get('carbon_rods', False):
        Ec, rc = 135e9, 1550.0; wc, hc = 0.125, 0.375; zc_ = -0.2 - hc / 2
        for yy in (-0.22, 0.22):
            fib.append((yy, zc_, wc * hc, Ec - Em, rc - rm, Ec - Em, wc * hc ** 3 / 12, hc * wc ** 3 / 12))
        NECK_INSERTS.append((0.3, 16.3, [f for f in fib if f[0] != 0.0]))
        fib = [f for f in fib if f[0] == 0.0]
    if fib: NECK_INSERTS.append((0.0, 17.0, fib))
    return lumps


def neck_section(x):
    """Composite section of the neck at x (in): returns dict of SI section properties and centroid (y, z) in inches.
    Neck: rosewood board 0.2 in on a maple C (superellipse p=2.2), total depth neck_depth(x), width neck_width(x).
    Headstock (x < 0): flat maple plate 0.55 in, top 0.2 in below the board top, outline from src/neck-geometry.js."""
    T = geom.neck_tables(); M = materials.load()
    HS = np.array([[0.05, 0.825], [-0.5, 0.9], [-1.2, 1.32], [-2.1, 1.55], [-3.6, 1.6], [-5.2, 1.48], [-6.4, 1.2],
                   [-7.05, 0.75], [-7.3, 0.15], [-7.15, -0.45], [-6.75, -0.78], [-6.1, -0.82], [-5.4, -0.62],
                   [-4.4, -0.42], [-3.2, -0.42], [-2.0, -0.6], [-1.0, -0.84], [-0.4, -0.86], [0.05, -0.825]])
    n = 120
    if x >= 0:
        w = float(T['neck_width'](min(x, 18.8))); Dp = float(T['neck_depth'](min(x, 18.8)))
        yy = np.linspace(-w / 2, w / 2, n); zz = np.linspace(-Dp, 0.375 - 0.375, n)  # board top at z_local 0
        Y, Z = np.meshgrid(yy, np.linspace(-Dp, 0, n), indexing='ij')
        board = Z > -0.2
        cprof = (Dp - 0.2) * (1 - np.abs(2 * Y / w) ** 2.2).clip(0) ** (1 / 2.2)
        maple = (~board) & (Z > -0.2 - cprof)
        dA = (yy[1] - yy[0]) * (Dp / (n - 1))
        mats = [(board, M['rosewood']['EL'], M['rosewood']['rho']), (maple, M['maple']['EL'] * NECK_SCALE[0], M['maple']['rho'] * NECK_SCALE[1])]
    else:
        up = HS[HS[:, 0] <= 0.05]; ys_top = np.interp(x, up[:9, 0][::-1], up[:9, 1][::-1])
        lo = HS[9:]; ys_bot = np.interp(x, lo[:, 0], lo[:, 1])
        if x > -1.0:   # blend from the nut section to the plate
            s0 = neck_section(0.0); t = -x / 1.0
        yy = np.linspace(ys_bot, ys_top, n); Y, Z = np.meshgrid(yy, np.linspace(-0.75, -0.2, n), indexing='ij')
        maple = np.ones_like(Y, bool); dA = (yy[1] - yy[0]) * (0.55 / (n - 1))
        mats = [(maple, M['maple']['EL'] * NECK_SCALE[0], M['maple']['rho'] * NECK_SCALE[1])]
    # discrete inserts (truss rod, slot void, carbon bars): fibers (y, z_local, A, E_stiff, rho, E_own, Iy_own, Iz_own)
    fib = [f for (x0, x1, fl) in NECK_INSERTS if x0 <= x <= x1 for f in fl]
    EA = sum(E * m.sum() * dA for m, E, r in mats) + sum(f[3] * f[2] for f in fib)
    RA = sum(r * m.sum() * dA for m, E, r in mats) + sum(f[4] * f[2] for f in fib)
    yc = (sum(E * (Y * m).sum() * dA for m, E, r in mats) + sum(f[3] * f[2] * f[0] for f in fib)) / EA
    zc = (sum(E * (Z * m).sum() * dA for m, E, r in mats) + sum(f[3] * f[2] * f[1] for f in fib)) / EA
    EIy = sum(E * (((Z - zc) ** 2) * m).sum() * dA for m, E, r in mats)        # vertical bending (about horizontal axis)
    EIz = sum(E * (((Y - yc) ** 2) * m).sum() * dA for m, E, r in mats)
    rIy = sum(r * (((Z - zc) ** 2) * m).sum() * dA for m, E, r in mats); rIz = sum(r * (((Y - yc) ** 2) * m).sum() * dA for m, E, r in mats)
    for (fy, fz, fA, fE, fr, fEo, fIy, fIz) in fib:
        EIy += fE * fA * (fz - zc) ** 2 + fEo * fIy; EIz += fE * fA * (fy - yc) ** 2 + fEo * fIz
        rIy += fr * (fA * (fz - zc) ** 2 + fIy); rIz += fr * (fA * (fy - yc) ** 2 + fIz)
    A = sum(m.sum() * dA for m, E, r in mats); Ip = (EIy / EA + EIz / EA) * A
    G = M['maple']['EL'] * 0.5 * (M['maple']['GLR_EL'] + M['maple']['GLT_EL'])
    J = A ** 4 / (40 * Ip)                                                      # Saint-Venant approximation [judged]
    s = IN ** 2; s4 = IN ** 4
    out = dict(EA=EA * s, EIy=EIy * s4, EIz=EIz * s4, GJ=G * J * s4, GA=G * A * s * 5 / 6, rhoA=RA * s,
               rhoIy=rIy * s4, rhoIz=rIz * s4, rhoIp=(rIy + rIz) * s4, yc=yc, zc=zc + 0.375)   # z in body coords
    if -1.0 < x < 0:
        t = -x / 1.0
        for k in out: out[k] = (1 - t) * s0[k] + t * out[k]
    return out


def struct_key(D):
    keys = ['chamber', 'top_skin_mm', 'back_skin_mm', 'veneer_mm', 'fhole', 'liner', 'liner_depth_mm', 'liner_inset_mm',
            'liner_wall_mm', 'liner_structural', 'tongue_end_x', 'trem', 'trem_mass_kg', 'pivot_k', 'n_springs', 'spring_k',
            'tuner_g', 'guard', 'guard_contact', 'hold', 'alder_E', 'alder_rho', 'alder_cross', 'maple_E', 'maple_rho',
            'h_struct', 'fmax_modes', 'wood']
    M = materials.load()
    d = {k: D[k] for k in keys}; d['mat'] = {k: v for k, v in M.items() if not k.startswith('_')}; d['v'] = 7
    if D.get('liner_tool_radius_mm'):
        d['liner_tool_radius_mm'] = D['liner_tool_radius_mm']
    if D['back_skin_mm'] != 7.0:
        d['floor_revision'] = 2
    # study options (added for STUDIES-neck-trem-guard.md): hashed only when not default, so older caches stay valid
    NEWDEF = dict(neck_curly=False, truss_rod='none', rod_coupling='tendon', carbon_rods=False, trem_block='default',
                  guard_bosses='none', guard_screws='all', guard_screw_k=0.0)
    for k, v in NEWDEF.items():
        if D.get(k, v) != v: d[k] = D[k]
    if D.get('truss_rod', 'none') == 'none' and 'rod_coupling' in d: del d['rod_coupling']
    if D['maple_E'] != 1.0 or D['maple_rho'] != 1.0: d['neck_beam_scaled'] = 1
    return hashlib.sha1(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:14]


def build(D, verbose=True):
    t0 = time.time()
    M = materials.load()
    h = D['h_struct']; ts = D['top_skin_mm'] / 25.4; tv = D['veneer_mm'] / 25.4
    F = geom.chamber_fields(ts if D['chamber'] else 0.197, 0.025)
    S = geom.static_geometry()
    xs = np.arange(12.85, 31.45, h); ys = np.arange(-6.55, 6.55 + 1e-9, h)
    ys = ys - (ys[np.argmin(np.abs(ys))])            # a node line on the centreline
    nx, ny = len(xs), len(ys)
    XC, YC = np.meshgrid(xs[:-1] + h / 2, ys[:-1] + h / 2, indexing='ij')
    body = _interp(F, F['sd'], XC, YC) > 0
    chf = _interp(F, F['ch'].astype(float), XC, YC) if D['chamber'] else np.zeros_like(XC)
    chm = body & (chf > 0.5)
    hole = body & geom.inside_poly(S['fhole'], XC, YC) & D['fhole'] & D['chamber']
    zt_c = _interp(F, F['zt'], XC, YC); zb_c = _interp(F, F['zb'], XC, YC)
    zc_c = _interp(F, F['zin_top'], XC, YC, order=0)
    zf_c = geom.chamber_floor(_interp(F, F['zin_back'], XC, YC, order=0), D['back_skin_mm'])
    # node fields: average of adjacent cells
    def nodeavg(v, m):
        a = np.zeros((nx, ny)); c = np.zeros((nx, ny))
        for di in (0, 1):
            for dj in (0, 1):
                a[di:nx - 1 + di, dj:ny - 1 + dj] += np.where(m, v, 0); c[di:nx - 1 + di, dj:ny - 1 + dj] += m
        with np.errstate(invalid='ignore'):
            return a / np.maximum(c, 1), c > 0
    ztn, nb = nodeavg(zt_c, body); zbn, _ = nodeavg(zb_c, body)
    zcn, nch = nodeavg(zc_c, chm); zfn, _ = nodeavg(zf_c, chm)
    eps = 0.3e-3 / IN
    lv = np.zeros((NL, nx, ny))
    lv[0] = ztn; lv[7] = zbn
    l2_s = ztn - ts - tv if tv > 0 else ztn - ts
    l2_c = zcn - tv if tv > 0 else zcn
    l2 = np.where(nch, l2_c, l2_s); lv[2] = l2
    lv[1] = l2 + (tv if tv > 0 else 0.6 / 25.4)
    l6 = np.where(nch, zfn, zbn + D['back_skin_mm'] / 25.4); lv[6] = l6
    lv[3] = np.where(nch, np.maximum(l2 - D['liner_depth_mm'] / 25.4, l6 + 1.5 / 25.4), np.minimum(-0.70, l2 - 1 / 25.4))
    lv[5] = np.where(nch, l6 + 0.25 * (lv[3] - l6), zbn + 0.625)
    lv[4] = 0.5 * (lv[3] + lv[5])
    for k in range(1, 7):
        lv[k] = np.clip(lv[k], lv[7], lv[0])
    for k in range(6, 0, -1):
        lv[k] = np.maximum(lv[k], lv[k + 1] + eps)
    for k in range(1, 7):
        lv[k] = np.minimum(lv[k], lv[k - 1] - eps)
    bad = np.any(np.diff(-lv, axis=0) < 0.5 * eps, axis=0) | ((lv[0] - lv[7]) < 8 * eps)
    for k in range(NL):
        lv[k] = np.where(bad, lv[0] + (lv[7] - lv[0]) * k / 7, lv[k])
    # ---------------------------------------------------------------- elements
    L_alder, L_maple, L_ven, L_liner = 0, 1, 2, 3
    mat = -np.ones((nx - 1, ny - 1, 7), int)
    mat[body] = L_alder
    if D['chamber']:
        mat[chm, 2:6] = -1
    mat[hole, 0:2] = -1
    if tv > 0 and D['chamber']:
        m1 = chm & ~hole; mat[m1, 1] = L_ven
    # routes (centre and treble side only, outside the chamber)
    R = lambda *a: _rect(XC, YC, *a) & body & ~chm
    for xp in (S['neck_pu'], S['mid_pu']):
        mat[R(xp - 0.36, xp + 0.36, -1.7, 1.7), 0:3] = -1
    bx = S['bridge_pu'][0]; mat[R(bx - 0.78, bx + 0.78, -1.45, 1.45), 0:3] = -1
    TR = S['trem']; RB = lambda k: R(TR[k]['x0'], TR[k]['x1'], TR[k]['yc'] - TR[k]['hw'], TR[k]['yc'] + TR[k]['hw'])
    mat[RB('slot'), 0:2] = -1                                        # top through-slot (plan file)
    mat[RB('block'), 2:7] = -1                                       # block cavity from the back to just below the top
    mat[RB('spring'), 5:7] = -1                                      # spring cavity
    # control cavity 1.125 deep [judged] and jack channel: centre lines from the plan file; skipped when it has none
    cm = np.zeros_like(body)
    if len(S['control_cavity']) >= 2: cm |= _capsule(XC, YC, list(S['control_cavity']), 0.5)
    if len(S['jack_channel_end']) == 2: cm |= _capsule(XC, YC, [tuple(S['jack_center']), tuple(S['jack_channel_end'])], 0.4)
    cm &= body & ~chm
    mat[cm, 0:5] = -1
    # set-neck tenon and tongue: maple in the top three layers
    xbe = float(np.min(XC[body & (np.abs(YC) < 0.5)]))
    ten = body & (XC >= xbe) & (XC <= D['tongue_end_x']) & (np.abs(YC) < 0.95)
    for k in range(3):
        sel = ten & (mat[:, :, k] == L_alder); mat[sel, k] = L_maple
    # liner (structural option): wood ring under the roof around the hole
    liner_mass = 0.0
    if D['chamber'] and D['fhole'] and D['liner'] != 'bare':
        import air
        tool_radius = D.get('liner_tool_radius_mm',0)
        if tool_radius and D['liner_structural']:
            raise ValueError('Rounded throat stiffness needs a conforming liner mesh')
        Hs = air.hole_summary(D['liner_inset_mm'] if D['liner'] == 'narrowed' else 0.0, tool_radius)
        ring_in2 = (Hs['area_in2'] + Hs['perimeter_in'] * D['liner_wall_mm'] / 25.4) - Hs['throat_area_in2']
        liner_mass = ring_in2 * IN ** 2 * D['liner_depth_mm'] * 1e-3 * M['alder']['rho']
        if D['liner_structural']:
            dpoly = geom.fc()._segdist(S['fhole'], XC, YC)
            inside = geom.inside_poly(S['fhole'], XC, YC)
            ringm = chm & ((~inside & (dpoly < D['liner_wall_mm'] / 25.4 + h / 2)) | (inside & (dpoly < (D['liner_inset_mm'] if D['liner'] == 'narrowed' else 0) / 25.4 + h / 2)))
            mat[ringm, 2] = L_liner
            liner_mass = 0.0
    # solid bosses under the guard screws that land over the chamber (hidden; alder, 1/2 in diameter [judged])
    chamber_screws = [(sx, sy) for (sx, sy) in S['screws'] if D['chamber'] and
                      _interp(F, F['ch'].astype(float), np.array([sx]), np.array([sy]))[0] > 0.5]
    gb_mode = D.get('guard_bosses', 'none')
    if gb_mode != 'none' and D['chamber']:
        for (sx, sy) in chamber_screws:
            bm = chm & ~hole & (np.hypot(XC - sx, YC - sy) < 0.25 + h / 2)
            for k in ((2,) if gb_mode == 'hanging' else (2, 3, 4, 5)):
                mat[bm, k] = L_alder
    # nodes
    I, J, K = np.nonzero(mat >= 0)
    node_used = np.zeros((nx, ny, NL), bool)
    for di, dj, dk in [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1), (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]:
        node_used[I + di, J + dj, K + dk] = True
    nid = -np.ones((nx, ny, NL), int); nid[node_used] = np.arange(node_used.sum()); nbody = int(node_used.sum())
    XN = np.zeros((nbody, 3))
    ii, jj, kk = np.nonzero(node_used)
    XN[nid[ii, jj, kk]] = np.c_[xs[ii], ys[jj], lv[kk, ii, jj]]
    conn = np.stack([nid[I + di, J + dj, K + dk] for di, dj, dk in
                     [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1), (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]], 1)
    emat = mat[I, J, K]
    # guard
    gnodes = None; conn_g = None
    if D['guard']:
        gc = body & geom.inside_poly(S['guard'], XC, YC) & ~hole
        for xp in (S['neck_pu'], S['mid_pu']):
            gc &= ~_rect(XC, YC, xp - 0.36, xp + 0.36, -1.45, 1.45)
        gc &= ~_rect(XC, YC, bx - 0.75, bx + 0.75, -1.4, 1.4)
        gi, gj = np.nonzero(gc)
        gu = np.zeros((nx, ny), bool)
        for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)): gu[gi + di, gj + dj] = True
        tg = M['guard']['t_mm'] / 25.4
        gb = -np.ones((nx, ny), int); gt = -np.ones((nx, ny), int)
        ui, uj = np.nonzero(gu); n0 = nbody
        gb[ui, uj] = n0 + np.arange(len(ui)); gt[ui, uj] = n0 + len(ui) + np.arange(len(ui))
        # screws: merge the guard bottom node with the body top node
        merged = {}; screw_pairs = []
        scr = S['screws']
        if D.get('guard_screws', 'all') == 'no_chamber':
            scr = [p for p in scr if p not in chamber_screws]
        for (sx, sy) in scr:
            i0 = int(round((sx - xs[0]) / h)); j0 = int(round((sy - ys[0]) / h))
            if 0 <= i0 < nx and 0 <= j0 < ny and gu[i0, j0] and nid[i0, j0, 0] >= 0:
                if D.get('guard_screw_k', 0.0) > 0: screw_pairs.append((gb[i0, j0], nid[i0, j0, 0]))
                else: merged[gb[i0, j0]] = nid[i0, j0, 0]
        XG = np.zeros((2 * len(ui), 3))
        XG[:len(ui)] = np.c_[xs[ui], ys[uj], np.maximum(lv[0, ui, uj], 0) * 0]
        XG[len(ui):] = np.c_[xs[ui], ys[uj], np.full(len(ui), tg)]
        XN = np.vstack([XN, XG])
        conn_g = np.stack([gb[gi, gj], gb[gi + 1, gj], gb[gi + 1, gj + 1], gb[gi, gj + 1],
                           gt[gi, gj], gt[gi + 1, gj], gt[gi + 1, gj + 1], gt[gi, gj + 1]], 1)
        # renumber merged
        remap = np.arange(XN.shape[0])
        for a, b in merged.items(): remap[a] = b
        conn_g = remap[conn_g]
        sp_set = {a for a, b in screw_pairs}
        contact_pairs = [(gb[i, j], nid[i, j, 0]) for i, j in zip(ui, uj) if nid[i, j, 0] >= 0 and gb[i, j] not in merged
                         and gb[i, j] not in sp_set]
        gnodes = dict(gb=gb, gt=gt, merged=merged, n=len(ui), remap=remap)
    else:
        contact_pairs = []; screw_pairs = []
        remap = np.arange(XN.shape[0])
    nsolid = XN.shape[0]
    # ---------------------------------------------------------------- neck beam nodes
    T = geom.neck_tables()
    xj = xbe
    bx_list = [-7.2, -6.65, -5.67, -4.69, -3.71, -2.73, -1.75, -1.0, -0.5, 0.0] + [float(T['fret_x'](n)) for n in range(1, 13)]
    bx_list = sorted(set(np.round(bx_list, 4)))
    xl = bx_list[-1]
    while xl < xj - 0.05:
        xl = min(xl + 0.6, xj); bx_list.append(xl)
    if abs(bx_list[-1] - xj) > 1e-6: bx_list.append(xj)
    rod_lumps = neck_inserts(D)
    secs = [neck_section(x) for x in bx_list]
    XB = np.array([[x, s['yc'], s['zc']] for x, s in zip(bx_list, secs)])
    nbeam = len(bx_list)
    # dof numbering: solid nodes 3 dof (after merge, unused merged nodes stay as zero rows -> removed), beam 6, trem 6
    ndof_s = 3 * nsolid; b0 = ndof_s; t0d = b0 + 6 * nbeam; ndof = t0d + 6
    groups = {}
    def addK(name, Kmat):
        groups[name] = groups.get(name, 0) + Kmat
    # ---- solid elements
    mats = {}
    aE = D['alder_E']; aR = D['alder_rho']; mE = D['maple_E']; mR = D['maple_rho']
    mats[L_alder] = (materials.D_matrix(M['alder'], 'LTR', aE, D['alder_cross']), M['alder']['rho'] * aR, 'alder')
    mats[L_maple] = (materials.D_matrix(M['maple'], 'LRT', mE), M['maple']['rho'] * mR, 'maple')
    ven = M.get('veneer', M['maple'])
    mats[L_ven] = (materials.D_matrix(ven, 'TLR', mE), ven['rho'] * mR, 'veneer')
    mats[L_liner] = (materials.D_matrix(M['alder'], 'LTR', aE, D['alder_cross']), M['alder']['rho'] * aR, 'liner')
    Mrows = []
    def add_hex(conn_, Dm, rho, name):
        nonlocal Mtot
        for s0 in range(0, len(conn_), 6000):
            c = conn_[s0:s0 + 6000]; X = XN[c] * IN
            Ke, Me = fe.hex_matrices(X, np.repeat(Dm[None], len(c), 0), np.full(len(c), rho))
            cd = (c[:, :, None] * 3 + np.arange(3)).reshape(len(c), 24)
            addK(name, fe.assemble(cd, Ke, ndof)); Mtot = Mtot + fe.assemble(cd, Me, ndof)
    Mtot = sp.csr_matrix((ndof, ndof))
    for L_, (Dm, rho, name) in mats.items():
        sel = emat == L_
        if sel.any(): add_hex(conn[sel], Dm, rho, name)
    if conn_g is not None:
        add_hex(conn_g, fe.iso_D(M['guard']['E'], M['guard']['nu']), M['guard']['rho'], 'guard')
    # ---- springs helper: list of (dof rows a (3), map a (3xna), dof rows b, map b, k matrix 3x3)
    def spring3(da, Ta, db, Tb, k3, name):
        Tm = np.zeros((3, len(da) + len(db))); Tm[:, :len(da)] = Ta; Tm[:, len(da):] = -Tb if db is not None and len(db) else 0
        dofs = np.r_[da, db] if db is not None and len(db) else np.asarray(da)
        Tm = Tm[:, :len(dofs)]
        Ke = Tm.T @ k3 @ Tm
        r = np.repeat(dofs, len(dofs)); c = np.tile(dofs, len(dofs))
        addK(name, sp.csr_matrix((Ke.ravel(), (r, c)), shape=(ndof, ndof)))
    def ndofs(n): return np.array([3 * n, 3 * n + 1, 3 * n + 2])
    I3 = np.eye(3)
    # guard contact
    kn = D['guard_contact'] * (h * IN) ** 2
    if contact_pairs:
        a = np.array([p[0] for p in contact_pairs]); b = np.array([p[1] for p in contact_pairs])
        kd = np.array([0.1 * kn, 0.1 * kn, kn])
        rr, cc, vv = [], [], []
        for d in range(3):
            da = 3 * a + d; db = 3 * b + d
            rr += [da, db, da, db]; cc += [da, db, db, da]; vv += [np.full(len(a), kd[d])] * 2 + [np.full(len(a), -kd[d])] * 2
        addK('guard_contact', sp.csr_matrix((np.concatenate(vv), (np.concatenate(rr), np.concatenate(cc))), shape=(ndof, ndof)))
    if screw_pairs:   # finite screw joints (3 directions, equal stiffness [judged])
        ksc = D['guard_screw_k']
        for a_, b_ in screw_pairs:
            spring3(ndofs(a_), I3, ndofs(b_), I3, ksc * I3, 'screws')
    # ---- beam
    for e in range(nbeam - 1):
        sa, sb = secs[e], secs[e + 1]; s = {k: 0.5 * (sa[k] + sb[k]) for k in sa}
        Kb, Mb = fe.beam_matrices(XB[e] * IN, XB[e + 1] * IN, s['EA'], s['EIy'], s['EIz'], s['GJ'], s['GA'], s['GA'],
                                  s['rhoA'] + 0.14 * (bx_list[e] >= 0) + 0.05, s['rhoIp'], s['rhoIy'], s['rhoIz'])
        dofs = np.r_[b0 + 6 * e + np.arange(6), b0 + 6 * (e + 1) + np.arange(6)]
        r = np.repeat(dofs, 12); c = np.tile(dofs, 12)
        addK('beam', sp.csr_matrix((Kb.ravel(), (r, c)), shape=(ndof, ndof)))
        Mtot = Mtot + sp.csr_matrix((Mb.ravel(), (r, c)), shape=(ndof, ndof))
    def add_mass6(dof6, M6):
        r = np.repeat(dof6, 6); c = np.tile(dof6, 6)
        return sp.csr_matrix((M6.ravel(), (r, c)), shape=(ndof, ndof))
    # tuners: 6 x tuner_g at the posts (src/neck-geometry.js), 0.4 in above the headstock face (centre of mass) [judged]
    for i in range(6):
        px, py = -1.75 - i * 0.98, 1.0 - i * 0.03
        e = int(np.argmin(np.abs(np.array(bx_list) - px)))
        r = (np.array([px, py, -0.2 + 0.1]) - XB[e]) * IN
        Mtot = Mtot + add_mass6(b0 + 6 * e + np.arange(6), fe.point_mass_6(D['tuner_g'] * 1e-3, r))
    for (lx, lm) in rod_lumps:   # truss-rod adjuster nut and anchor
        e = int(np.argmin(np.abs(np.array(bx_list) - lx)))
        Mtot = Mtot + add_mass6(b0 + 6 * e + np.arange(6), fe.point_mass_6(lm, np.zeros(3)))
    for (xa, xb_, zl, EAr) in NECK_TENDON:   # anchored rod: axial spring between its anchors at rod height
        ea = int(np.argmin(np.abs(np.array(bx_list) - xa))); eb = int(np.argmin(np.abs(np.array(bx_list) - xb_)))
        La = (xb_ - xa) * IN; kr = EAr / La          # real rod length; the heel anchor lies in the rigid joint block
        pa = np.array([bx_list[ea], 0.0, zl + 0.375]); pb = np.array([bx_list[eb], 0.0, zl + 0.375])
        spring3(b0 + 6 * ea + np.arange(6), fe.rigid_point((pa - XB[ea]) * IN), b0 + 6 * eb + np.arange(6),
                fe.rigid_point((pb - XB[eb]) * IN), kr * np.diag([1.0, 0.0, 0.0]), 'rod')
    # nut and string trees: 10 g [judged]
    # fingerboard over the body and frets: lumped on body top nodes in the joint strip
    jt = [nid[i, j, 0] for i in range(nx) for j in range(ny)
          if nid[i, j, 0] >= 0 and xj <= xs[i] <= 18.17 and abs(ys[j]) <= 1.05]
    if jt:
        mb = 0.013 + 0.010
        for n in jt:
            Mtot = Mtot + sp.csr_matrix((np.full(3, mb / len(jt)), (ndofs(n), ndofs(n))), shape=(ndof, ndof))
    # ---- RBE2 neck joint: body nodes in the joint block follow the last beam node rigidly
    slaves = [nid[i, j, k] for i in range(nx) for j in range(ny) for k in range(4)
              if nid[i, j, k] >= 0 and xj - 1e-6 <= xs[i] <= xj + 0.6 and abs(ys[j]) <= 1.0]
    master = b0 + 6 * (nbeam - 1)
    # ---- trem rigid body: reference at the pivot line centre (pivot_x, 0, 0)
    pref = np.array([S['pivot_x'], 0.0, 0.0])
    tdof = t0d + np.arange(6)
    # inertia: steel block 2.25 (y) x 0.45 (x) x 1.55 (z) centred 0.95 behind the pivot line on the block-cavity centre, z -0.85;
    # plate 2.85 x 1.6 x 0.08 at 0.65 behind, z 0.04; saddles 6 x 11 g at 0.30 behind, z 0.35; scaled to trem_mass_kg
    # [judged geometry and positions]
    px = S['pivot_x']; yb = round(S['trem']['block']['yc'], 2)
    parts = [(0.215, (px + 0.95, yb, -0.85), (0.45, 2.25, 1.55)), (0.075, (px + 0.65, 0.0, 0.04), (1.6, 2.85, 0.08))]
    parts += [(0.0117, (px + 0.30, y, 0.35), (0.3, 0.38, 0.3)) for y in Y_SADDLE]
    ms = sum(p[0] for p in parts); sc = D['trem_mass_kg'] / ms
    tb = D.get('trem_block', 'default')
    if tb != 'default':   # same block dimensions, mass by density; plate and saddles as listed (not scaled)
        rho_b = dict(steel=7850.0, ti=4430.0, brass=8500.0)[tb]
        parts[0] = (rho_b * 0.45 * 2.25 * 1.55 * IN ** 3, parts[0][1], parts[0][2]); sc = 1.0
    Mt = np.zeros((6, 6))
    for m, c, dims in parts:
        m *= sc; a, b, cdim = [d * IN for d in dims]
        Icm = m / 12 * np.diag([b * b + cdim * cdim, a * a + cdim * cdim, a * a + b * b])
        Mt += fe.point_mass_6(m, (np.array(c) - pref) * IN, Icm)
    Mtot = Mtot + add_mass6(tdof, Mt)
    def body_node_near(x, y, k):
        i0 = int(round((x - xs[0]) / h)); j0 = int(round((y - ys[0]) / h))
        best = None
        for r_ in range(0, 4):
            for di in range(-r_, r_ + 1):
                for dj in range(-r_, r_ + 1):
                    i, j = i0 + di, j0 + dj
                    if 0 <= i < nx and 0 <= j < ny and nid[i, j, k] >= 0:
                        d = np.hypot(xs[i] - x, ys[j] - y)
                        if best is None or d < best[0]: best = (d, nid[i, j, k])
            if best: return best[1]
        raise RuntimeError(f'no body node near {x},{y} level {k}')
    kp = D['pivot_k'] * (100.0 if D['trem'] == 'locked' else 1.0)
    piv_y = [-1.11, -0.666, -0.222, 0.222, 0.666, 1.11]
    for y in piv_y:
        nb_ = body_node_near(S['pivot_x'], y, 0)
        Ta = fe.rigid_point((np.array([S['pivot_x'], y, 0.0]) - pref) * IN)
        spring3(tdof, Ta, ndofs(nb_), I3, np.diag([kp, 0.2 * kp, kp]), 'pivot')
    nsp = D['n_springs']; spy = [-0.5, 0.0, 0.5] if nsp == 3 else list(np.linspace(-0.7, 0.7, nsp))
    for y in spy:
        nb_ = body_node_near(S['trem']['spring']['x0'], y, 6)
        Ta = fe.rigid_point((np.array([26.1, y, -1.45]) - pref) * IN)
        spring3(tdof, Ta, ndofs(nb_), I3, D['spring_k'] * np.diag([1.0, 0.0, 0.0]) * (100 if D['trem'] == 'locked' else 1), 'springs')
    # strings: axial springs saddle -> nut (beam node at x = 0)
    e0 = bx_list.index(0.0)
    for i, sname in enumerate(SNAMES):
        f0, Tn, dcore = STRINGS[sname]
        ps = np.array([X_SADDLE, Y_SADDLE[i], Z_SADDLE]); pn = np.array([0.0, Y_NUT[i], Z_NUT])
        Ls = np.linalg.norm(ps - pn) * IN + 0.08; A = np.pi * (dcore * IN) ** 2 / 4
        k = 200e9 * A / Ls; nvec = (ps - pn) / np.linalg.norm(ps - pn)
        Ta = fe.rigid_point((ps - pref) * IN); Tb = fe.rigid_point((pn - XB[e0]) * IN)
        spring3(tdof, Ta, b0 + 6 * e0 + np.arange(6), Tb, k * np.outer(nvec, nvec), 'strings')
    # ---- player contacts (spring to ground + dashpot)
    hold = D['hold']; Cd = sp.csr_matrix((ndof, ndof)); patches = {}
    top_nodes = {(i, j): nid[i, j, 0] for i in range(nx) for j in range(ny) if nid[i, j, 0] >= 0}
    back_nodes = {(i, j): nid[i, j, 7] for i in range(nx) for j in range(ny) if nid[i, j, 7] >= 0}
    PATCH = dict(belly=('back', (21.5, 3.8), 1.5, 2.0e4, 30.0), forearm=('top', (28.3, 3.4), 1.1, 1.0e4, 15.0),
                 thigh=('back', (23.0, -5.2), 1.0, 2.0e4, 30.0), chest=('back', (27.5, 1.5), 1.2, 1.0e4, 15.0))
    for nm, (side, (cx_, cy_), rad, ktot, ctot) in PATCH.items():
        src_ = top_nodes if side == 'top' else back_nodes
        nn = [v for (i, j), v in src_.items() if np.hypot(xs[i] - cx_, ys[j] - cy_) < rad]
        patches[nm] = nn
        if hold in ('held', 'firm') and nn:
            f_ = 3.0 if hold == 'firm' else 1.0
            dd = np.concatenate([ndofs(n) for n in nn])
            kd = np.tile([0.3, 0.3, 1.0], len(nn)) * ktot * f_ / len(nn); cd_ = np.tile([0.3, 0.3, 1.0], len(nn)) * ctot * f_ / len(nn)
            addK('hold', sp.csr_matrix((kd, (dd, dd)), shape=(ndof, ndof)))
            Cd = Cd + sp.csr_matrix((cd_, (dd, dd)), shape=(ndof, ndof))
    fret_hand = bx_list.index(round(float(T['fret_x'](5)), 4))
    if hold in ('held', 'firm'):
        f_ = 3.0 if hold == 'firm' else 1.0; dd = b0 + 6 * fret_hand + np.array([1, 2])
        addK('hold', sp.csr_matrix((np.full(2, 1.5e4 * f_), (dd, dd)), shape=(ndof, ndof)))
        Cd = Cd + sp.csr_matrix((np.full(2, 20.0 * f_), (dd, dd)), shape=(ndof, ndof))
    # hardware masses on the guard: pickups and controls [judged]
    if gnodes is not None:
        gt_ = gnodes['gt']
        for (mx, my, mm) in [(S['neck_pu'], 0.0, 0.045), (S['mid_pu'], 0.0, 0.045), (bx, 0.0, 0.090), (24.5, -3.3, 0.060)]:
            near = [gt_[i, j] for i in range(nx) for j in range(ny) if gt_[i, j] >= 0 and 0.75 <= np.hypot(xs[i] - mx, (ys[j] - my) * 0.6) <= 1.3]
            for n in near:
                Mtot = Mtot + sp.csr_matrix((np.full(3, mm / len(near)), (ndofs(n), ndofs(n))), shape=(ndof, ndof))
    if liner_mass > 0:
        roof = [nid[i, j, 2] for i in range(nx) for j in range(ny) if nid[i, j, 2] >= 0 and
                abs(geom.fc()._segdist(S['fhole'], np.array([xs[i]]), np.array([ys[j]]))[0]) < 0.12]
        for n in roof:
            Mtot = Mtot + sp.csr_matrix((np.full(3, liner_mass / len(roof)), (ndofs(n), ndofs(n))), shape=(ndof, ndof))
    # ---------------------------------------------------------------- reduction: RBE2 + remove unused dofs
    Ktot = sum(groups.values())
    diagK = np.abs(Ktot.diagonal()) + np.abs(Mtot.diagonal())
    used = diagK > 0
    slave_dofs = np.concatenate([ndofs(n) for n in slaves])
    keep = np.nonzero(used)[0]; keep = np.setdiff1d(keep, slave_dofs)
    col_of = -np.ones(ndof, int); col_of[keep] = np.arange(len(keep))
    rr = list(keep); cc = list(np.arange(len(keep))); vv = [1.0] * len(keep)
    mcols = col_of[master + np.arange(6)]
    for n in slaves:
        Tm = fe.rigid_point((XN[n] - XB[-1]) * IN)
        for d in range(3):
            for q in range(6):
                if Tm[d, q] != 0:
                    rr.append(3 * n + d); cc.append(mcols[q]); vv.append(Tm[d, q])
    Tr = sp.csr_matrix((vv, (rr, cc)), shape=(ndof, len(keep)))
    out = dict(D=D, ndof=ndof, Tr=Tr, groups={k: v for k, v in groups.items()}, M=Mtot, C=Cd, XN=XN, nid=nid, xs=xs, ys=ys,
               lv=lv, mat=mat, body=body, chm=chm, hole=hole, XB=XB, bx_list=bx_list, b0=b0, tdof=tdof, pref=pref,
               gnodes=gnodes, patches=patches, nbody=nbody, liner_mass=liner_mass, xj=xj, slaves=slaves,
               remap=remap)
    if verbose:
        print(f'[model] {D["name"]}: {len(I)} body hex, {0 if conn_g is None else len(conn_g)} guard hex, {nbeam} beam nodes, '
              f'{len(keep)} dof, built in {time.time() - t0:.1f}s', flush=True)
    return out


def mass_props(B):
    """Total mass (kg) and balance point x (in) from the mass matrix (translational x dof sums)."""
    M = B['M']; ndof = B['ndof']
    ones = np.zeros(ndof); xpos = np.zeros(ndof)
    ns = B['XN'].shape[0]
    ones[0:3 * ns:3] = 1; xpos[0:3 * ns:3] = B['XN'][:, 0]
    nb = len(B['bx_list'])
    ones[B['b0']:B['b0'] + 6 * nb:6] = 1; xpos[B['b0']:B['b0'] + 6 * nb:6] = B['XB'][:, 0]
    ones[B['tdof'][0]] = 1; xpos[B['tdof'][0]] = B['pref'][0]
    # rigid x translation of every point: displacement field u = ones (rotational dofs zero) -> m = 1^T M 1
    m = ones @ (M @ ones)
    # rotational dof contributions to first moment: approximate with node positions (point masses at nodes)
    mx = xpos @ (M @ ones)
    return float(m), float(mx / m)


def nd_order(A):
    """Nested-dissection fill-reducing ordering (METIS) of a symmetric sparse matrix."""
    import pymetis
    A = A.tocsr(); n = A.shape[0]
    G = (A != 0).astype(np.int8); G = (G + G.T).tocsr(); G.setdiag(0); G.eliminate_zeros()
    perm, iperm = pymetis.nested_dissection(xadj=G.indptr.astype(np.int64), adjncy=G.indices.astype(np.int64))
    return np.asarray(perm)


def solve_modes(B, fmax, nmax=600, verbose=True):
    """Shift-invert Lanczos on the reduced system, in blocks of shifts until fmax is covered."""
    t0 = time.time()
    Tr = B['Tr']; K = (Tr.T @ sum(B['groups'].values()) @ Tr).tocsc(); M = (Tr.T @ B['M'] @ Tr).tocsc()
    K = 0.5 * (K + K.T); M = 0.5 * (M + M.T)
    n = K.shape[0]
    lam_all = []; vec_all = []
    sig = -(2 * np.pi * 5.0) ** 2
    lo = 0.0; perm = None
    while True:
        A = (K - sig * M).tocsc()
        if perm is None:
            perm = nd_order(A)
        iperm = np.empty_like(perm); iperm[perm] = np.arange(n)
        Ap = A[perm][:, perm].tocsc()
        lu = sla.splu(Ap, permc_spec='NATURAL', options=dict(SymmetricMode=True), diag_pivot_thresh=0.0)
        OP = sla.LinearOperator((n, n), matvec=lambda b, lu=lu: lu.solve(b[perm])[iperm], dtype=float)
        kblk = 160
        w, v = sla.eigsh(K, k=kblk, M=M, sigma=sig, which='LM', OPinv=OP, ncv=2 * kblk + 20, tol=1e-9)
        del lu
        o = np.argsort(w); w = w[o]; v = v[:, o]
        f = np.sqrt(np.clip(w, 0, None)) / (2 * np.pi)
        if lam_all and f.min() > lo * (1 + 1e-6):            # gap between blocks: move the shift down and retry
            sig = (2 * np.pi * (lo + 0.6 * (np.sqrt(sig) / 2 / np.pi - lo))) ** 2
            if verbose: print('[modes] gap, lowering shift', flush=True)
            continue
        sel = f >= lo - 1e-9
        if lam_all:
            sel &= f > np.sqrt(max(lam_all[-1].max(), 0)) / (2 * np.pi) + 1e-6
        # keep only modes below the highest one found minus a guard (Lanczos captures around the shift)
        lam_all.append(w[sel]); vec_all.append(v[:, sel])
        fhi = f.max()
        if verbose: print(f'[modes] shift {np.sqrt(max(sig, 0)) / 2 / np.pi:.0f} Hz: {sel.sum()} modes up to {fhi:.0f} Hz '
                          f'({time.time() - t0:.0f}s)', flush=True)
        if fhi >= fmax or sum(len(l) for l in lam_all) >= nmax: break
        # next shift above the last converged block: centre on fhi * 1.25
        lo = fhi
        sig = (2 * np.pi * fhi * 1.3) ** 2
    lam = np.concatenate(lam_all); V = np.hstack(vec_all)
    o = np.argsort(lam); lam = lam[o]; V = V[:, o]
    # remove duplicates (overlapping blocks)
    keep = np.r_[True, np.diff(np.sqrt(np.clip(lam, 0, None))) > 1e-6 * np.sqrt(np.clip(lam[1:], 1, None))]
    lam = lam[keep]; V = V[:, keep]
    f = np.sqrt(np.clip(lam, 0, None)) / (2 * np.pi)
    m = f <= fmax
    V = V[:, m]; lam = lam[m]; f = f[m]
    # M-normalise (eigsh already does; enforce)
    nrm = np.sqrt(np.einsum('ij,ij->j', V, M @ V)); V = V / nrm
    # missed-mode check: the blocks must be contiguous (gap check)
    return dict(f=f, lam=lam, V=V, K=K, M=M)
