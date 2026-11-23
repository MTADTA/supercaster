#!/usr/bin/env python3
"""Supercaster II set neck, v2 (owner answers 2026-11-13). Imports v1 (neck_model.py) and patches it; v1 stays reproducible.

v2 changes
  1. depth 0.90 at fret 1; three growth laws to fret 12 (radius-proportional, SRV taper, moderate); REC2 = 'MOD'
  2. section CHANGES SHAPE along the neck: exact straight-line (ruled) loft between a thumb-over nut section A and a
     symmetric C heel-start section B (= the body's heel-loft start section) -> ONE rule, exactly ruled on [0, x_h]
  3. round-laminate rosewood board: uniform thickness t_b, concentric with the conical compound radius; planed relief is
     cut into the maple glue face so the board stays uniform; roll kept inside the rosewood
  4. scallop flows INTO the fret: frets seated h into a rebate; the flank leaves the crown TANGENTIALLY at height h with a
     circular fillet of radius rho, then a flat floor. One law: rho_k = Delta_k / (1 - cos theta), theta = crown slope at h
  5. wire: Jescar FW43080-S (0.080 x 0.043) kept; Allparts/Dunlop SS6230 (0.079 x 0.039) noted
Run: viz python -I -W ignore neck_v2.py   (writes results_v2.json, fig/v2_*.png)
"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # -I drops the script dir
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import neck_model as nm
from neck_model import P, fret_x, width, radius, sag, S, IN, STR, X1, X12, X15, X17, X21, X22

HERE = os.path.dirname(os.path.abspath(__file__)); FIG = os.path.join(HERE, 'fig')

V2 = dict(
    D1=0.90,                         # owner
    D12_mod=0.96,                    # moderate law target at fret 12 [judged]
    srv_d1=0.84, srv_d12=0.97,       # Musikraft SRV chart [lit]; Warmoth SRV .835/.970 [lit]
    x_h=X15 - 0.5,                   # heel-loft parameter start (final_carve heel_lead 0.5 before fret 15) [lit: body/carve]
    A=(0.06, 2.40, 1.90),            # nut section: apex 0.06 to bass, full bass shoulder, slightly V treble [judged; scan in DESIGN]
    B=(0.00, 2.30, 2.30),            # heel-start section: symmetric C, p 2.3 = body heel loft start section [lit: body/carve]
    e=0.008,                         # exposed crown above the board top (levelling budget; largest e with no catch to fret 22) [computed]
    rod_z_end=-0.30, rod_sag=0.36,  # deeper curved channel for the thicker neck: 0.0040 in per 100 lb vs 0.0019 with the v1 path [computed]
    rho_min=0.33,                    # fillet radius floor = fingertip proxy 0.30 + 10 % [judged]
    roll_margin=0.025,               # roll bottom stays this far above the glue line [judged]
    rose_min=0.040,                  # rosewood under the deepest scallop floor [owner/coordinator]
    edge_frac=0.0,                   # scallop depth kept at the roll start (0 = clean straight board edge) [judged]
)
DLAWS = {
    'R':   ('radius-proportional (v1 rule C at 0.90)', lambda x: V2['D1'] * radius(x) / radius(X1)),
    'SRV': ('SRV taper (+0.13 by fret 12, Musikraft SRV)', lambda x: V2['D1'] + (V2['srv_d12'] - V2['srv_d1']) * (x - X1) / (X12 - X1)),
    'MOD': ('moderate 0.90 -> 0.96', lambda x: V2['D1'] + (V2['D12_mod'] - V2['D1']) * (x - X1) / (X12 - X1)),
}
REC2 = ['MOD']
def D2(x, law=None): return DLAWS[law or REC2[0]][1](np.asarray(x, float))

# ------------------------------------------------------------------------------------------------ 2. section rule
XH = V2['x_h']
def back2(x, y, rule=None, law=None):
    """z_back = -[(1-t) D(0) Phi_A(u) + t D(x_h) Phi_B(u)], t = x/x_h (clamped), u = 2y/W(x). Exactly ruled on [0, x_h]."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    u = 2 * y / width(x); t = np.clip(x / XH, 0, 1)
    PA = nm.Phi(u, *V2['A']); PB = nm.Phi(u, *V2['B'])
    DA = D2(0.0, law); DB = D2(XH, law)
    zr = -((1 - t) * DA * PA + t * DB * PB)
    return np.where(x <= XH, zr, -D2(x, law) * PB)
def section_back(x, law=None, n=801):
    u = np.linspace(-1, 1, n); return u * width(x) / 2, back2(np.full_like(u, x), u * width(x) / 2, law=law)
def side_y2(x, zb, side, rule=None):
    """|y| on the bass (+1) / treble (-1) side where the back is zb below the board-top centre (outer branch)."""
    def one(xx, z):
        yy, zz = section_back(float(xx), n=601); i = np.argmin(zz)
        if side > 0: Y, Z = yy[i:], -zz[i:]
        else: Y, Z = -yy[:i + 1][::-1], -zz[:i + 1][::-1]
        return np.interp(z, Z[::-1], Y[::-1])
    x = np.asarray(x, float); zb = np.asarray(zb, float)
    if x.ndim == 0: return one(float(x), zb)
    X, Z = np.broadcast_arrays(x, zb); out = np.empty(X.shape)
    for xv in np.unique(X):
        m = X == xv; out[m] = one(xv, Z[m])
    return out
def ruled_check2(law=None):
    xs = np.linspace(0, XH, 9); dev = 0.0
    for u in np.linspace(-0.98, 0.98, 41):
        z = np.array([back2(xx, u * width(xx) / 2, law=law) for xx in xs]); dev = max(dev, np.abs(np.diff(z, 2)).max())
    return float(dev)
def shape_metrics(x, law=None):
    W = float(width(x)); yy, zz = section_back(x, law); i = np.argmin(zz)
    ins = W / 2 - 0.25
    tb_ = -float(back2(x, ins, law=law)) - float(sag(x, ins)); tt_ = -float(back2(x, -ins, law=law)) - float(sag(x, ins))
    # shoulder half-widths at 75 % depth (v1 metric)
    zc = 0.75 * float(-zz.min()); yb = side_y2(x, zc, 1); yt = side_y2(x, zc, -1)
    return dict(fret=None, x=x, D=float(D2(x, law)), Dmax=float(-zz.min()), apex_y=float(yy[i]), W=W,
                sh_bass_025=tb_, sh_treb_025=tt_, ratio75=float(yb / yt), t=float(min(x / XH, 1)))

# ------------------------------------------------------------------------------------------------ 4. crown-tangent scallop
CROWN_A = P['crown_w'] / 2; CROWN_B = P['crown_h']
def blend_geom(e=None):
    e = V2['e'] if e is None else e; h = CROWN_B - e
    q = h / CROWN_B; xb = CROWN_A * math.sqrt(1 - q * q)
    m = CROWN_B ** 2 * xb / (CROWN_A ** 2 * h); th = math.atan(m)
    return dict(e=e, h=h, xb=xb, m=m, theta=th)
def delta_cell(k, e=None):
    """Floor depth below the board top (wood peak) for cell k:
       Delta_k = clip(h + d_v1(k),  rho_min (1 - cos th),  S_k tan(th/2))
       lower bound: fillet radius >= rho_min (fingertip can follow it); upper bound: the two fillets fit the cell."""
    g = blend_geom(e); L = float(fret_x(k) - fret_x(k - 1)); Sk = L / 2 - g['xb']
    lo = V2['rho_min'] * (1 - math.cos(g['theta']))
    return float(min(max(g['h'] + float(nm.sc_depth_cell(k)), lo), Sk * math.tan(g['theta'] / 2)))
FX = np.array([float(fret_x(n)) for n in range(0, P['frets'] + 1)])
def wood_long(x, w=1.0, e=None):
    """Wood surface below the board top along x (<= 0) at lateral weight w: fillet radius rho = w Delta/(1-cos th)."""
    g = blend_geom(e); x, w = np.broadcast_arrays(np.asarray(x, float), np.asarray(w, float))
    out = np.zeros(x.shape)
    n = np.clip(np.searchsorted(FX, x, side='right') - 1, 0, P['frets'] - 1)
    ok = (x > 0) & (x < FX[-1])
    Dk = np.array([delta_cell(k, e) for k in range(1, P['frets'] + 1)])
    s = np.minimum(x - FX[n], FX[n + 1] - x); D = Dk[n] * w
    rho = D / (1 - math.cos(g['theta'])); ext = rho * math.sin(g['theta'])
    t = s - g['xb']
    arc = rho * math.cos(g['theta']) - np.sqrt(np.clip(rho ** 2 - (t - ext) ** 2, 0, None))
    z = np.where(t <= 0, 0.0, np.where(t >= ext, -D, arc))
    return np.where(ok, z, 0.0)
def lateral_w2(x, y):
    yo = nm.spread(x, 'vintage') / 2 + 0.03; ye = width(x) / 2 - nm.roll_a(x)
    t = (np.abs(y) - yo) / np.maximum(ye - yo, 1e-3)
    return 1 - (1 - V2['edge_frac']) * nm.S5(t)
def scallop_z2(x, y): return wood_long(x, lateral_w2(x, y))

def cell_profile_blend(L, e=None, Dl=None):
    """Finger-catch frame: crown centres at 0 and L, crowns seated h below the board top (top of crown = e)."""
    g = blend_geom(e); D = Dl
    rho = D / (1 - math.cos(g['theta'])); ext = rho * math.sin(g['theta'])
    def f(x):
        x = np.asarray(x, float)
        c = np.maximum(nm.crown_z(x), nm.crown_z(x - L)) - g['h']
        s = np.minimum(np.abs(x), np.abs(L - x)); t = s - g['xb']
        arc = rho * math.cos(g['theta']) - np.sqrt(np.clip(rho ** 2 - (t - ext) ** 2, 0, None))
        w = np.where(t <= 0, -1.0, np.where(t >= ext, -D, arc))
        w = np.where((x > 0) & (x < L), w, -1.0)
        return np.maximum(c, w)
    return f

# ------------------------------------------------------------------------------------------------ 3. round-lam board
TB = [0.135]
def glue_z(x, y):
    """Maple top / glue face: concentric with the board-top cone, t_b below it, with the planed relief cut into it."""
    R = radius(x); return -nm.planed(x) - R + np.sqrt((R - TB[0]) ** 2 - np.asarray(y, float) ** 2)
def roll_b_side2(x, side):
    x = np.asarray(x, float); hw = width(x) / 2; a = nm.roll_a(x); yc = hw - a
    ut = np.asarray(side, float) * (yc + 0.6 * a)
    dep = -back2(x, ut) - (sag(x, hw) + nm.planed(x))
    return np.clip(dep, 0.02, P['roll_b'])
def EI_section2(x, scallops=True, Em=None, rod_hole=True, ny=161, nz=241):
    Em = P['E_maple'] if Em is None else Em
    hw = float(width(x)) / 2; y = np.linspace(-hw, hw, ny)
    zlo = float(back2(np.full_like(y, x), y).min()) - 0.01
    z = np.linspace(zlo, 0.01, nz); dy = y[1] - y[0]; dz = z[1] - z[0]
    Y, Z = np.meshgrid(y, z, indexing='ij')
    inside = (Z < nm.top_z(x, Y, scallops)) & (Z > back2(np.full_like(Y, x), Y))
    if rod_hole and P['rod_x0'] < x < P['rod_x1']:
        inside &= ~((Y ** 2 + (Z - nm.rod_z(x)) ** 2) < (P['rod_d'] / 2) ** 2)
    rose = Z > glue_z(x, Y)
    E = np.where(rose, P['E_rose'], Em) * inside
    dA = dy * dz * IN * IN; EA = (E * dA).sum(); zc = (E * Z * dA).sum() / EA
    EI = (E * ((Z - zc) * IN) ** 2 * dA).sum()
    return EI, zc, (inside * dA).sum(), (rose * inside * dA).sum()
_sha_v1 = nm.string_height_avg
def string_height_avg2(x): return _sha_v1(x) - blend_geom()['h']     # crown plane is h lower relative to the board top

def install(v2=True):
    """Patch v1 functions in place (v2=True) or restore v1."""
    global _SAVE
    if v2:
        _SAVE = {k: getattr(nm, k) for k in ('depth', 'back_z', 'side_y', 'roll_b_side', 'scallop_z', 'EI_section', 'string_height_avg')}
        _SAVE['P'] = dict(P)
        nm.depth = lambda x, rule=None: D2(x); nm.back_z = back2; nm.side_y = side_y2; nm.roll_b_side = roll_b_side2
        nm.scallop_z = scallop_z2; nm.EI_section = EI_section2; nm.string_height_avg = string_height_avg2
        P['roll_b'] = TB[0] - V2['roll_margin']
        P['rod_z_end'], P['rod_sag'] = V2['rod_z_end'], V2['rod_sag']
    else:
        for k, v in _SAVE.items():
            if k == 'P': P.update(v)
            else: setattr(nm, k, v)
    nm._EI_CACHE.clear()

# ------------------------------------------------------------------------------------------------ studies
FR = (1, 5, 9, 12, 17)
CELLS = (1, 3, 5, 7, 9, 12, 14, 17, 19, 22)
def depth_options():
    rows = {}
    for k, (lab, f) in DLAWS.items():
        rows[k] = dict(label=lab, D={n: float(f(fret_x(n))) for n in (1, 5, 9, 12, 15, 17)}, D_xh=float(f(XH)),
                       slope_thou_per_in=float((f(X12) - f(X1)) / (X12 - X1) * 1000), ruled_dev=None)
    return rows
def catch_compare(es=(0.006, 0.008, 0.010)):
    out = []
    for k in CELLS:
        L = float(fret_x(k) - fret_x(k - 1)); d1 = float(nm.sc_depth_cell(k))
        r = dict(cell=k, L=L, d_v1=d1, flat=nm.finger_catch(nm.cell_profile(L, 'flat'), L)[:3],
                 v1=nm.finger_catch(nm.cell_profile(L, 'land', d1), L)[:3],
                 v1_rebate=nm.finger_catch(nm.cell_profile(L, 'rebate', d1, rebate=0.010), L)[:3])
        for e in es:
            Dl = delta_cell(k, e); r[f'blend_{e:.3f}'] = nm.finger_catch(cell_profile_blend(L, e, Dl), L)[:3] + (Dl,)
        out.append(r)
    return out
def clearance_checks():
    """Per cell: exposed crown (speaking-side wood clearance at the fret), fillet size, and the press depth p (below the
    crown top, finger at mid-cell) at which the dead-side string first touches wood anywhere but under the finger."""
    g = blend_geom(); rows = []
    for k in range(1, P['frets'] + 1):
        L = float(fret_x(k) - fret_x(k - 1)); Dl = delta_cell(k); f = cell_profile_blend(L, None, Dl)
        rho = Dl / (1 - math.cos(g['theta'])); xs = np.linspace(0.0, L / 2, 1500); wz = f(xs)
        top = g['e']; p_touch = None
        for p in np.linspace(0.002, g['e'] + Dl, 300):
            sz = top - p * xs / (L / 2)       # straight string from the crown top (x=0) to the finger at mid-cell
            if np.any((sz - wz)[(xs > 0.005) & (xs < L / 2 - 0.02)] < 0): p_touch = float(p); break
        rows.append(dict(cell=k, L=L, Delta=Dl, d_below_seat=Dl - g['h'], rho=rho, fillet_len=rho * math.sin(g['theta']),
                         floor_len=max(L - 2 * (g['xb'] + rho * math.sin(g['theta'])), 0.0), e=g['e'],
                         p_touch=p_touch, p_floor=g['e'] + Dl, rose_under_floor=TB[0] - Dl))
    return rows
def filler_area(k=13):
    # per side, in^2: between the crown flank (below) and the tangent fillet (above), out to the rebate wall at the crown foot
    g = blend_geom(); Dl = delta_cell(k); rho = Dl / (1 - math.cos(g['theta']))
    x = np.linspace(g['xb'], CROWN_A, 400); t = x - g['xb']
    fil = g['h'] + rho * math.cos(g['theta']) - np.sqrt(np.clip(rho ** 2 - (t - rho * math.sin(g['theta'])) ** 2, 0, None))  # height above the seat
    cr = CROWN_B * np.sqrt(np.clip(1 - (x / CROWN_A) ** 2, 0, 1))
    return float(getattr(np, 'trapezoid', getattr(np, 'trapz', None))(np.clip(fil - cr, 0, None), x))
def press_sharp2():
    T = nm.tensions(-1, 0); out = []
    for i in (0, 2):
        for k in (3, 12):
            L = float(fret_x(k) - fret_x(k - 1)); Dl = delta_cell(k); g = blend_geom()
            for p in (0.010, 0.020, 0.043, g['e'] + Dl):
                out.append(dict(string=STR[i][0], cell=k, p=p, cents=nm.press_sharp_cents(i, p, L, T[i])))
    return out
def roundlam_checks():
    g = blend_geom(); Dmax = max(delta_cell(k) for k in range(1, 23))
    rows = []
    for n in (1, 5, 9, 12, 17, 22):
        x = float(fret_x(n)); hw = width(x) / 2; a = float(nm.roll_a(x))
        zt = -sag(x, hw) - nm.planed(x)
        for sd in (1, -1):
            b = float(roll_b_side2(x, sd)); ys = float(side_y2(x, -zt + b, sd))
            zg = float(glue_z(x, ys)); zbot = zt - b
            rows.append(dict(fret=n, side='bass' if sd > 0 else 'treble', roll_a=a, roll_b=b, roll_bottom_above_glue=float(zbot - glue_z(x, hw - a)),
                             glue_at_side_y=float(ys), glue_side_below_top=float(zt - zg)))
    wob40 = 0.40 * Dmax
    slot_rose = TB[0] - g['h'] - P['slot_d']
    return dict(t_b=TB[0], Delta_max=Dmax, rose_under_deepest=TB[0] - Dmax, slot_bottom_rose_left=slot_rose, rows=rows,
                edge_wobble_if_40pct=wob40, roll_b_bass=P['roll_b'])

def main():
    R = {}
    g = blend_geom(); R['blend'] = dict(g, theta_deg=math.degrees(g['theta']))
    Dmax = max(delta_cell(k) for k in range(1, 23))
    TB[0] = math.ceil((Dmax + V2['rose_min']) / 0.005) * 0.005
    R['depth_options'] = depth_options()
    for k in DLAWS: REC2[0] = k; R['depth_options'][k]['ruled_dev'] = ruled_check2(k)
    REC2[0] = 'MOD'
    R['shape'] = {}
    for k in DLAWS:
        REC2[0] = k; R['shape'][k] = []
        for n in FR:
            sm = shape_metrics(float(fret_x(n)), k); sm['fret'] = n; R['shape'][k].append(sm)
    REC2[0] = 'MOD'
    # v1 baseline relief for reference is in results.json; v2 construction:
    install(True)
    R['roundlam'] = roundlam_checks()
    R['clearance'] = clearance_checks(); R['filler_area_per_side_in2'] = filler_area()
    R['catch'] = catch_compare(); R['press_sharp'] = press_sharp2()
    R['relief'] = {}
    for k in ('R', 'MOD'):
        REC2[0] = k; nm._EI_CACHE.clear(); R['relief'][k] = nm.relief_design()
    REC2[0] = 'MOD'
    EIs = {}
    for n in (1, 5, 9, 12):
        x = float(fret_x(n)); EIs[n] = dict(v2=EI_section2(x)[0])
    R['modes_v2'] = dict(plain=nm.neck_modes(False).tolist(), scalloped=nm.neck_modes(True).tolist())
    R['scallop_removed_in3'] = scallop_volume2()
    R['heel'] = dict(x_h=XH, D_at_xh=float(D2(XH)), body_v1_D_at_xh=float(0.82 * radius(XH) / radius(X1)),
                     section_at_xh='symmetric p=2.30 (identical to the body loft start section)')
    figures(R)
    install(False)
    for n in (1, 5, 9, 12):
        x = float(fret_x(n)); EIs[n]['v1'] = nm.EI_section(x)[0]
    R['EI_ratio_v2_v1'] = {n: EIs[n]['v2'] / EIs[n]['v1'] for n in EIs}
    with open(os.path.join(HERE, 'results_v2.json'), 'w') as fh: json.dump(R, fh, indent=1, default=float)
    report(R)
def scallop_volume2():
    xs = np.linspace(0, X22, 4000); out = 0.0; dx = xs[1] - xs[0]
    for x in xs:
        hw = width(x) / 2; y = np.linspace(-hw, hw, 61); dy = y[1] - y[0]
        out += float((-scallop_z2(x, y)).sum() * dy * dx)
    return out

# ------------------------------------------------------------------------------------------------ figures
def figures(R):
    # depth options
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    xx = np.linspace(0, XH + 1.5, 300); fn = nm.fret_n(np.maximum(xx, 1e-6))
    for k, st in (('R', ':'), ('SRV', '--'), ('MOD', '-')):
        ax[0].plot(fn, D2(xx, k), st, lw=2.5 if k == 'MOD' else 1.5, label=DLAWS[k][0])
    ax[0].plot(fn, 0.82 * radius(xx) / radius(X1), color='0.6', lw=1, label='v1 (0.82, rule C)')
    ax[0].plot([1, 12], [0.84, 0.97], 'ks', label='Musikraft SRV chart .84/.97 (your neck)')
    ax[0].plot([1, 12], [0.90, 0.99], 'k^', mfc='none', label='Musikraft Chunky C-2 .90/.99')
    ax[0].axvspan(nm.fret_n(XH), 22, color='0.92'); ax[0].text(15.2, 0.86, 'heel loft', color='0.5')
    ax[0].set_xlabel('fret'); ax[0].set_ylabel('centreline depth D (in, board top to back)'); ax[0].legend(fontsize=7)
    ax[1].plot([s['fret'] for s in R['shape']['MOD']], [s['ratio75'] for s in R['shape']['MOD']], 'o-', label='shoulder ratio bass/treble @75 % depth')
    ax[1].plot([s['fret'] for s in R['shape']['MOD']], [s['sh_bass_025'] / s['sh_treb_025'] for s in R['shape']['MOD']], 's-', label='depth ratio bass/treble 0.25 in from edge')
    ax[1].axhline(1, color='0.6', lw=0.6); ax[1].set_xlabel('fret'); ax[1].legend(fontsize=7); ax[1].set_title('Asymmetry fades to a symmetric C at the heel start', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v2_depth_options.png'), dpi=130); plt.close(fig)
    # sections
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw=dict(width_ratios=[1.6, 1]))
    ax = axs[0]; cols = plt.cm.viridis(np.linspace(0.05, 0.9, len(FR)))
    for n, c in zip(FR, cols):
        x = float(fret_x(n)); yy, zz = nm.section_polygon(x)
        ax.plot(yy, zz, color=c, lw=1.4, ls='--' if n == 17 else '-', label=f'fret {n}' + (' (heel loft governs)' if n == 17 else ''))
        yg = np.linspace(-width(x) / 2 + 0.06, width(x) / 2 - 0.06, 200); ax.plot(yg, glue_z(x, yg), color=c, lw=0.5, ls=':')
    ax.axvline(0, color='0.85', lw=0.6); ax.set_aspect('equal'); ax.legend(fontsize=7, loc='lower left')
    ax.set_xlabel('y (in), bass side right'); ax.set_ylabel('z (in), board top = 0')
    ax.set_title('v2 sections (moderate law, ruled shape loft A -> B); dotted = round-lam glue line', fontsize=9)
    ax = axs[1]
    for n, c in zip(FR, cols):
        x = float(fret_x(n)); yy, zz = section_back(x); ax.plot(2 * yy / width(x), zz / D2(x), color=c, ls='--' if n == 17 else '-', label=f'fret {n}')
    ax.axvline(0, color='0.85', lw=0.6); ax.set_xlabel('u = 2y/W (bass +)'); ax.set_ylabel('z / D'); ax.legend(fontsize=7)
    ax.set_title('Normalised shape: thumb-over V-lean (nut) -> symmetric C', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v2_sections.png'), dpi=130); plt.close(fig)
    # round-lam edge
    fig = plt.figure(figsize=(13, 8.5)); gs = fig.add_gridspec(2, 3)
    x12 = float(fret_x(12)); xm = 0.5 * (float(fret_x(13)) + float(fret_x(14)))
    for j, (x, lab) in enumerate(((x12, 'at fret 12 (no scallop)'), (xm, 'mid-cell 14 (deepest scallop)'))):
        ax = fig.add_subplot(gs[0, j]); yy, zz = nm.section_polygon(x)
        ax.fill(yy, zz, color='#e8d2a6', ec='#6b4f2a', lw=0.8)
        hw = width(x) / 2; yg = np.linspace(-hw, hw, 600); zt = nm.top_z(x, yg); zg = glue_z(x, yg); zb = back2(np.full_like(yg, x), yg)
        rose = (zt > zg) & (zg > zb) & (zt < 5)
        ax.fill_between(yg, np.where(rose, zg, np.nan), np.where(rose, zt, np.nan), color='#5a3a22')
        ax.set_aspect('equal'); ax.set_title(f'Round-lam section {lab}', fontsize=9); ax.set_ylim(-1.05, 0.08)
    ax = fig.add_subplot(gs[0, 2]); x = xm; hw = width(x) / 2
    yy, zz = nm.section_polygon(x); m = yy > hw - 0.45
    yg = np.linspace(hw - 0.45, hw, 500); zt = nm.top_z(x, yg); zg = glue_z(x, yg); zb = back2(np.full_like(yg, x), yg)
    ok = zt < 5; ax.fill_between(yg[ok], np.maximum(zb[ok], -0.45), zt[ok], color='#e8d2a6')
    rose = ok & (zt > zg); ax.fill_between(yg[rose], zg[rose], zt[rose], color='#5a3a22', label=f'rosewood t_b {TB[0]:.3f}')
    ax.plot(yg, glue_z(x, yg), color='k', lw=0.6, ls=':', label='glue face (concentric cone)')
    ax.set_aspect('equal'); ax.set_xlim(hw - 0.45, hw + 0.03); ax.set_ylim(-0.45, 0.05); ax.legend(fontsize=7, loc='lower left')
    ax.set_title('Bass edge, mid-cell 14: roll stays in rosewood', fontsize=9)
    ax = fig.add_subplot(gs[1, :]); xx = np.linspace(float(fret_x(9)) - 0.1, float(fret_x(16)) + 0.1, 3000)
    hwx = width(xx) / 2; ax_ = nm.roll_a(xx)
    zt_edge = nm.top_z(xx, hwx - ax_); ax.plot(xx, zt_edge, color='#a0703e', label='board top at the roll start (edge fade 0 -> straight)')
    ax.plot(xx, nm.top_z(xx, 0 * xx), color='0.6', lw=0.8, label='centreline (crown-tangent scallop)')
    yb = side_y2(xx, -(-sag(xx, hwx) - nm.planed(xx)) + P['roll_b'], 1)
    ax.plot(xx, -sag(xx, hwx) - nm.planed(xx) - P['roll_b'], color='#5a3a22', lw=1, label='roll bottom (bass)')
    ax.plot(xx, glue_z(xx, yb), color='k', ls=':', label='glue line where it meets the side')
    for n in range(9, 17):
        xf = float(fret_x(n)); g = blend_geom(); z0 = float(nm.top_z(xf, width(xf) / 2 - nm.roll_a(xf)))
        th = np.linspace(0, np.pi, 50); ax.fill(xf + 0.04 * np.cos(th), z0 - g['h'] + 0.043 * np.sin(th), color='0.55')
    ax.legend(fontsize=7, loc='lower right', ncol=2); ax.set_xlabel('x (in)'); ax.set_ylabel('z (in)')
    ax.set_title('Side elevation, bass edge, frets 9-16: clean edge line, roll bottom and glue line both smooth (fret ends partly buried by h)', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v2_roundlam_edge.png'), dpi=130); plt.close(fig)
    # blend close-up
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw=dict(height_ratios=[1.3, 1]))
    ax = axs[0]; k = 13; L = float(fret_x(k) - fret_x(k - 1)); g = blend_geom(); Dl = delta_cell(k)
    f = cell_profile_blend(L, None, Dl); xs = np.linspace(-0.12, L + 0.12, 3000)
    wz = np.where((xs > 0) & (xs < L), f(xs), 0.0)
    # wood (board top 0, valley), crown seated at -h
    s = np.minimum(np.abs(xs), np.abs(L - xs)); t = s - g['xb']
    rho = Dl / (1 - math.cos(g['theta'])); ext = rho * math.sin(g['theta'])
    arc = rho * math.cos(g['theta']) - np.sqrt(np.clip(rho ** 2 - (t - ext) ** 2, 0, None))
    wood = np.where(t <= 0, 0.0, np.where(t >= ext, -Dl, arc))
    ax.fill_between(xs, -TB[0], np.minimum(wood, 0), color='#5a3a22', label='rosewood')
    ax.fill_between(xs, -TB[0] - 0.08, -TB[0], color='#e8d2a6', label='maple')
    for xc in (0.0, L):
        cz = nm.crown_z(xs - xc); ok = np.isfinite(cz)
        fill = ok & (np.abs(xs - xc) > g['xb']) & (np.abs(xs - xc) < CROWN_A)
        ax.fill_between(xs[fill], (cz - g['h'])[fill], np.maximum(wood, cz - g['h'])[fill], color='#c47a2c', label='blend fillet: CA/epoxy + rosewood dust' if xc == 0 else None)
        ax.fill_between(xs[ok], -g['h'], (cz - g['h'])[ok], color='0.6', label='stainless crown (seated h in a rebate)' if xc == 0 else None)
        ax.add_patch(plt.Rectangle((xc - P['tang_w'] / 2, -g['h'] - P['tang_d']), P['tang_w'], P['tang_d'], color='0.45'))
    d1 = float(nm.sc_depth_cell(k)); v1 = nm.cell_profile(L, 'land', d1)(xs) - g['h']
    ax.plot(xs, np.where((xs > CROWN_A) & (xs < L - CROWN_A), v1, np.nan), 'r--', lw=0.9, label='v1 (S5, flat at the crown foot), same frets')
    pass  # (fingertip circle removed: a static circle misplaced the rolling-contact model)
    ax.set_aspect('equal'); ax.set_xlim(-0.12, L + 0.12); ax.set_ylim(-0.2, 0.12); ax.legend(fontsize=7, loc='upper right', ncol=2)
    ax.set_title(f'Cell 13 (crown-tangent scallop): exposed crown e {g["e"]:.3f}, blend at h {g["h"]:.3f} where the crown slope is {math.degrees(g["theta"]):.0f} deg;'
                 f' fillet r {rho:.3f}, floor {Dl:.3f} below the board top', fontsize=9)
    ax = axs[1]; C = R['catch']; cl = [c['cell'] for c in C]
    ax.plot(cl, [c['flat'][0] for c in C], 'ko-', label='unscalloped board')
    ax.plot(cl, [c['v1'][0] for c in C], 'o-', color='tab:green', label='v1 S5 flat at foot')
    ax.plot(cl, [c['v1_rebate'][0] for c in C], '--', color='tab:blue', label='v1 + 0.010 rebate')
    for e, cc in ((0.006, 'tab:purple'), (0.008, 'tab:red'), (0.010, 'tab:orange')):
        ax.plot(cl, [c[f'blend_{e:.3f}'][0] for c in C], 's-', color=cc, label=f'v2 crown-tangent, e {e:.3f}')
    ax.set_xlabel('cell'); ax.set_ylabel('fingertip catch (deg slope jump)'); ax.legend(fontsize=7, ncol=3)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v2_blend.png'), dpi=130); plt.close(fig)

def report(R):
    print('== blend', {k: round(v, 4) for k, v in R['blend'].items()})
    print('== depth options'); [print('  ', k, json.dumps(v, default=lambda q: round(float(q), 4))) for k, v in R['depth_options'].items()]
    for k in R['shape']:
        print('== shape', k)
        for s in R['shape'][k]:
            print(f"   fret {s['fret']:2d} D {s['D']:.3f} Dmax {s['Dmax']:.3f} apex {s['apex_y']:+.3f} W {s['W']:.3f} t {s['t']:.2f}"
                  f" 0.25in-inset bass/treble {s['sh_bass_025']:.3f}/{s['sh_treb_025']:.3f} ratio75 {s['ratio75']:.3f}")
    print('== heel', R['heel'])
    rl = R['roundlam']; print(f"== round-lam t_b {rl['t_b']:.3f} Delta_max {rl['Delta_max']:.3f} rose under deepest {rl['rose_under_deepest']:.3f}"
                              f" slot-bottom rosewood {rl['slot_bottom_rose_left']:.3f} roll_b {rl['roll_b_bass']:.3f} wobble@40% {rl['edge_wobble_if_40pct']:.3f}")
    for r in rl['rows']: print('  ', json.dumps(r, default=lambda q: round(float(q), 4)))
    print('== clearance / fillet per cell')
    for r in R['clearance']: print('  ', json.dumps(r, default=lambda q: None if q is None else round(float(q), 4)))
    print('== filler area per side in^2', R['filler_area_per_side_in2'])
    print('== catch (deg, dip, max uphill)')
    for r in R['catch']: print('  ', json.dumps(r, default=lambda q: round(float(q), 3)))
    print('== press sharp'); [print('  ', json.dumps(r, default=lambda q: round(float(q), 3))) for r in R['press_sharp']]
    for k, rl in R['relief'].items():
        print(f'== relief {k}: planed sag {rl["planed_sag"]:.4f} gap {rl["planed_gap"]:.4f}  rod need {rl["rod_need_in"]:.4f} per100 {rl["rod_in_per_100lb"]:.4f} F {rl["rod_F_lb"]:.0f}')
        for nm_, row in rl['rows'].items():
            print(f'   {nm_:11s} flat {row["flat_soft"]:.4f}/{row["flat_nom"]:.4f}/{row["flat_stiff"]:.4f} scal {row["scal_soft"]:.4f}/{row["scal_nom"]:.4f}/{row["scal_stiff"]:.4f}')
    print('== EI ratio v2/v1', R['EI_ratio_v2_v1'])
    print('== modes v2', R['modes_v2'], ' scallop removed in3', R['scallop_removed_in3'])

if __name__ == '__main__':
    main()
