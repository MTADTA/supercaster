#!/usr/bin/env python3
"""Supercaster II set neck, v3 (2026-11-13): the buildable scallop, edge and fret ends.

Replaces v2's withdrawn crown-tangent scallop / rebated seat / filler fillets / edge rail.
Kept from v2: MOD depth law (0.90 -> 0.96), ruled loft A -> B (A now: fuller bass shoulder ONLY, no V-lean),
0.140 round-lam rosewood board, deeper rod path, Jescar FW43080-S.

v3 geometry
  frets  : fully proud on the full-height land, normal stopped slots, pressed + glued; no rebate, no filler
  scallop: v1 law (full-span S5 from the crown foot, d_k = min(0.030 + 0.045 xi, 0.15 L^2)), full depth across the top
           to the roll start, then THROUGH the roll: in the roll (q = (|y| - y_c)/a_h, cos(phi) = sqrt(1 - q^2))
               drop(x, y) = d(x) cos(phi) + b (1 - cos(phi))
           i.e. at mid-cell the roll is the same quarter ellipse squashed to height b - d, starting d lower.
           Monotone in y whenever b >= d  ->  no rail, no fin. Where the roll would be shallower than the scallop,
           b is raised to d + 0.010 (b_eff).
  roll   : a(x) = v1 law (outer string + 0.030 keep + dome r 0.040); bass b = t_b - 0.035 = 0.105
  ends   : hemispherical crown end r = 0.040, apex AT the roll start y_c (the end sits on the full-height land, the nib);
           stopped slot ends 0.030 inside the apex; tang nipped 0.035 back from the apex
Run: viz python -I -W ignore neck_v3.py   (writes results_v3.json, fig/v3_*.png)
"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import neck_v2 as v2
import neck_model as nm
from neck_model import P, fret_x, width, radius, sag, STR, X1, X12, X22, IN

HERE = v2.HERE; FIG = v2.FIG
V3 = dict(
    A=(0.05, 2.60, 2.30),      # nut section: apex 0.05 to bass, fuller bass (p 2.6), treble = heel-section C (2.3) -> no V [judged; scan]
    t_b=0.140,                 # round-lam board [v2, kept]
    glue_margin=0.035,         # roll bottom stays this far above the glue line (>= 0.030 required) [judged]
    slot_back=0.030,           # stopped slot ends this far inside the dome apex (wood beyond >= 0.03 at the top) [judged]
    tang_back=0.035,           # tang nipped this far back from the apex (0.005 behind the slot end) [judged]
    b_over_d=0.010,            # if the roll is shallower than the local scallop, deepen it to d + this [judged]
    # fret length FIRST (owner 2026-11-13: strings must not slip off): usable crown (>= 90 % height) must reach at least
    # as far out as on a vintage Strat (1.650 nut, ends bevelled flush with the edge at bevel_deg from vertical)
    bevel_deg=35.0,            # vintage end bevel [judged, common 35-45]
    usable=0.90,               # 'usable' crown = still >= 90 % of its height [coordinator]
    end_c=0.025,               # fret-end ellipsoid: semi-axes 0.040 (along x, = crown half-width) x end_c (along y) x 0.043 [judged]
    margin_extra=0.010,        # usable-crown margin beyond vintage [judged: owner wants >= vintage]
    widen=0.030,               # PER SIDE neck/board widening, constant along the neck; string spread stays vintage [computed: bend-room rule]
    finger_side=0.150,         # bend-room rule: string centre to board edge >= this at frets 12-17 (fingertip pad beside the string) [judged]
    ah_min=0.006,              # minimum horizontal semi-axis of the roll ellipse [judged]
)
W_NUT_V = 1.650
def bevel_usable():
    """Vintage: distance from the board edge to where a bevelled end is back to 90 % crown height."""
    return V3['usable'] * P['crown_h'] * math.tan(math.radians(V3['bevel_deg']))
def end_usable_t():
    """v3: distance from the end apex back to where the ellipsoid end is at 90 % height."""
    return V3['end_c'] * (1 - math.sqrt(1 - V3['usable'] ** 2))
def width_v(x): return W_NUT_V + (2.20 - W_NUT_V) * np.asarray(x, float) / nm.X21          # vintage width law
def roll_a3(x):
    """Fret length first: usable crown end at the vintage position (+ extra), apex end_usable_t further out, roll starts at the apex."""
    y_u = width_v(x) / 2 - bevel_usable() + V3['margin_extra']
    return width(x) / 2 - (y_u + end_usable_t())
def vint_margin(x, i):
    return width_v(x) / 2 - bevel_usable() - abs(float(nm.string_y(i, x)))
CELLS = list(range(1, 23))

# ------------------------------------------------------------------------------------------------ geometry patches
def roll_geom(x, y):
    """q in the roll (0 at the roll start y_c, 1 at the side wall), b_eff and a_h for points (x, y)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    hw = width(x) / 2; a = nm.roll_a(x); yc = hw - a
    zt_edge = sag(x, hw) + nm.planed(x)
    sd = np.where(y >= 0, 1.0, -1.0)
    b0 = np.where(y >= 0, v2.roll_b_side2(x, 1.0), v2.roll_b_side2(x, -1.0))
    d = nm.scallop_long(x)
    b = np.maximum(b0, d + V3['b_over_d'])
    ys = np.where(y >= 0, v2.side_y2(x, zt_edge + b, 1), v2.side_y2(x, zt_edge + b, -1))
    ah = np.maximum(ys - yc, V3['ah_min']); q = (np.abs(y) - yc) / ah
    return q, b, b0, ah, yc, d
def scallop_z3(x, y):
    q, b, b0, ah, yc, d = roll_geom(x, y)
    w = np.where(q <= 0, 1.0, np.sqrt(np.clip(1 - q * q, 0, 1)))
    return -d * w
def roll_drop3(x, y):
    q, b, b0, ah, yc, d = roll_geom(x, y)
    return np.where(q <= 0, 0.0, np.where(q < 1, b * (1 - np.sqrt(np.clip(1 - q * q, 0, 1))), 10.0))

def install():
    v2.V2['A'] = V3['A']; v2.TB[0] = V3['t_b']; v2.V2['roll_margin'] = V3['glue_margin']
    v2.install(True)
    P['nut_w'] = W_NUT_V + 2 * V3['widen']; P['w21'] = 2.20 + 2 * V3['widen']
    nm.roll_a = roll_a3
    nm.scallop_z = scallop_z3; nm.roll_drop = roll_drop3; nm.string_height_avg = v2._sha_v1   # frets proud again: v1 datum
    nm._EI_CACHE.clear()

# ------------------------------------------------------------------------------------------------ checks
def surf_grid(x, n=1601):
    hw = float(width(x)) / 2; y = np.linspace(-hw, hw, n); zt = nm.top_z(x, y); zb = v2.back2(np.full_like(y, x), y)
    ok = (zt > zb) & (zt > -5); return y[ok], zt[ok], zb[ok]
def glue_and_fin_checks():
    """Every top-surface point (flat top, scallop, roll) vs the glue line; monotonicity of the edge (no rail / fin)."""
    xs = np.concatenate([np.linspace(0.05, X22 + 0.2, 900)])
    worst = dict(above_glue=9.0); fin = 0.0; rows = []
    for x in xs:
        y, zt, zb = surf_grid(float(x))
        zg = v2.glue_z(x, y); m = zt - zg
        i = int(np.argmin(m))
        if m[i] < worst['above_glue']: worst = dict(above_glue=float(m[i]), x=float(x), y=float(y[i]))
        # fin / rail: from the board centre outward the top must not rise again (beyond the radius sag) at either side
        for sd in (1, -1):
            s = (y * sd) >= 0; yy = np.abs(y[s]); zz = zt[s] + sag(x, yy)          # remove the radius
            o = np.argsort(yy); zz = zz[o]; rise = np.maximum.accumulate(zz[::-1])[::-1] - zz   # later points higher than here?
            fin = max(fin, float(rise.max()))
    return dict(min_top_above_glue=worst, max_outward_rise=fin)
def edge_rows():
    """Per fret: roll a, b (bass/treble), b_eff at the next mid-cell, dome / slot / tang positions, string margins."""
    rows = []
    for n in (1, 3, 5, 7, 9, 12, 15, 17, 19, 21, 22):
        x = float(fret_x(n)); hw = float(width(x)) / 2; a = float(nm.roll_a(x)); yc = hw - a
        s_v = float(nm.spread(x, 'vintage')) / 2; s_t = float(nm.spread(x, 'vt1')) / 2
        yf = yc - V3['end_c']                      # full-height crown ends here
        rE = STR[0][1] / 2; rLE = STR[5][1] / 2      # high E / low E radii
        xm = 0.5 * (float(fret_x(n)) + float(fret_x(min(n + 1, 22)))) if n < 22 else 0.5 * (float(fret_x(21)) + x)
        qb, bb, b0b, ahb, _, d = roll_geom(np.array([xm]), np.array([hw - a / 2]))
        qt, bt, b0t, aht, _, _ = roll_geom(np.array([xm]), np.array([-(hw - a / 2)]))
        rows.append(dict(fret=n, W=2 * hw, a=a, b_bass=float(b0b[0]), b_treb=float(b0t[0]), d_next_cell=float(d[0]),
                         b_eff_treb_mid=float(bt[0]), apex_from_edge=a, crown_full_from_edge=a + V3['end_c'],
                         slot_stop_from_edge=a + V3['slot_back'], tang_stop_from_edge=a + V3['tang_back'],
                         usable_margin=(yc - end_usable_t()) - s_v, usable_margin_vintage_ref=vint_margin(x, 0),
                         usable_margin_vt1=(yc - end_usable_t()) - s_t,
                         string_to_edge=hw - s_v, string_to_edge_vintage=float(width_v(x)) / 2 - s_v, W_vintage=float(width_v(x))))
    return rows
def slot_wall_checks():
    """Rosewood between the stopped-slot end and the rolled surface (horizontal, at depths 0..slot_d), the slot bottom to
    the glue line, and the dome base covering the slot end."""
    out = []
    for n in (1, 12, 22):
        x = float(fret_x(n)); hw = float(width(x)) / 2; a = float(nm.roll_a(x)); yc = hw - a; yse = yc - V3['slot_back']
        y = np.linspace(yc - 0.05, hw, 4000); zt = nm.top_z(x, y, scallops=False) + sag(x, y) + nm.planed(x)
        walls = {}
        for dz in (0.0, 0.010, 0.030, P['slot_d']):
            yr = y[np.argmax(zt < -dz - 1e-9)] if np.any(zt < -dz - 1e-9) else hw
            walls[f'{dz:.3f}'] = float(max(yr, yc) - yse)
        # dome base circle (r = dome_r about yf) must cover the slot stadium (half-width slot_w/2, round end at yse)
        yf = yc - V3['end_c']; cover = V3['end_c'] - (yse - yf)       # radial room beyond the slot tip
        out.append(dict(fret=n, slot_end_from_edge=hw - yse, wall_horiz=walls, dome_covers_slot_tip_by=cover,
                        slot_bottom_to_glue=V3['t_b'] - P['slot_d']))
    return out
def ball_limit():
    """Smallest concave radius of the cut wood surface (x direction, S5 scallops; the roll and the radius are convex)."""
    rmin = 9.0; where = None
    for k in CELLS:
        a_, b_, C, l = nm.cell_geom(k); xs = np.linspace(a_ + 1e-4, b_ - 1e-4, 3001); d = nm.scallop_long(xs)
        z = -d; c = np.gradient(np.gradient(z, xs), xs); zp = np.gradient(z, xs)
        kap = c / (1 + zp ** 2) ** 1.5; km = kap.max()
        if km > 0 and 1 / km < rmin: rmin = 1 / km; where = k
    return dict(min_concave_radius=float(rmin), cell=where)
def wood_min():
    """Other minimum-wood checks along the centreline: maple between the rod and the glue face, and under the rod."""
    xs = np.linspace(P['rod_x0'] + 0.3, P['rod_x1'] - 0.1, 300); top = []; bot = []
    for x in xs:
        rz = float(nm.rod_z(x)); r = P['rod_d'] / 2
        top.append(float(v2.glue_z(x, 0.0)) - (rz + r)); bot.append((rz - r) - float(v2.back2(x, 0.0)))
    i = int(np.argmin(top)); j = int(np.argmin(bot))
    return dict(maple_rod_to_glue_min=top[i], at_x=float(xs[i]), maple_under_rod_min=bot[j], at_x2=float(xs[j]),
                rose_under_deepest_scallop=V3['t_b'] - max(float(nm.sc_depth_cell(k)) for k in CELLS),
                rose_under_slot=V3['t_b'] - P['slot_d'])
def catch_v3():
    out = []
    for k in CELLS:
        L = float(fret_x(k) - fret_x(k - 1)); d = float(nm.sc_depth_cell(k))
        out.append(dict(cell=k, d=d, catch=nm.finger_catch(nm.cell_profile(L, 'land', d), L)[0],
                        flat=nm.finger_catch(nm.cell_profile(L, 'flat'), L)[0]))
    return out
def edge_slide():
    """Hand sliding along the bass edge: rigid R 0.30 pad held against the roll at 45 deg, path over a fret end (dome)
    vs the wood alone. Reports the largest slope jump of the pad path along x (deg)."""
    out = []
    for n in (5, 12, 19):
        x0 = float(fret_x(n)); hw = float(width(x0)) / 2; a = float(nm.roll_a(x0)); yc = hw - a
        q, b, *_ = roll_geom(np.array([x0]), np.array([yc + 0.5 * a])); b = float(b[0])
        xs = np.arange(x0 - 0.3, x0 + 0.3, 0.001)
        # pad touches along the 45-deg normal line through the roll; sample the outward-normal height of wood + steel
        res = {}
        for steel in (False, True):
            h = []
            for x in xs:
                y = np.linspace(yc - 0.06, hw, 400); z = nm.top_z(x, y) + sag(x, y) + nm.planed(x)
                if steel:
                    dx = x - x0; yf = yc - V3['end_c']
                    rr2 = 1 - (dx / (P['crown_w'] / 2)) ** 2 - (np.maximum(y - yf, 0) / V3['end_c']) ** 2
                    cz = np.where((np.abs(dx) < P['crown_w'] / 2) & (y < yf), np.asarray(nm.crown_z(dx)), np.sqrt(np.clip(rr2, 0, None)) * P['crown_h'])
                    cz = np.where(rr2 > 0, cz, np.where((np.abs(dx) < P['crown_w'] / 2) & (y < yf), cz, -1))
                    z = np.maximum(z, np.where(cz > 0, cz, -9))
                h.append(float(np.max((z + y) / math.sqrt(2))))      # support along the 45-deg outward normal
            h = np.array(h); R = P['finger_R']; w = int(R / 0.001)
            off = np.arange(-w, w + 1) * 0.001; cap = np.sqrt(np.clip(R * R - off * off, 0, None))
            idx = np.clip(np.arange(len(h))[:, None] + np.arange(-w, w + 1)[None, :], 0, len(h) - 1)
            path = (h[idx] + cap).max(1); sl = np.arctan(np.diff(path) / 0.001)
            res['with_dome' if steel else 'wood_only'] = float(np.degrees(np.abs(np.diff(sl)).max()))
            res[('rise_' + ('with_dome' if steel else 'wood_only'))] = float(path.max() - path.min())
        out.append(dict(fret=n, **res))
    return out

# ------------------------------------------------------------------------------------------------ figures
ROSE = '#5a3a22'; MAPLE = '#e8d2a6'; STEEL = '0.62'
def draw_section(ax, x, at_fret, zoom=None):
    yy, zz = nm.section_polygon(x); ax.fill(yy, zz, color=MAPLE, ec='#6b4f2a', lw=0.8)
    hw = float(width(x)) / 2; yg = np.linspace(-hw, hw, 1200); zt = nm.top_z(x, yg); zg = v2.glue_z(x, yg); zb = v2.back2(np.full_like(yg, x), yg)
    rose = (zt > zg) & (zg > zb) & (zt > -5)
    ax.fill_between(yg, np.where(rose, zg, np.nan), np.where(rose, zt, np.nan), color=ROSE)
    # wood above the glue line but beyond where the glue meets the back: rosewood down to the back
    rose2 = (zt > zb) & (zg <= zb) & (zt > -5)
    ax.fill_between(yg, np.where(rose2, zb, np.nan), np.where(rose2, zt, np.nan), color=ROSE)
    ax.plot(yg, np.where(rose | rose2, np.maximum(zg, zb), np.nan), 'k:', lw=0.6)
    if at_fret:
        a = float(nm.roll_a(x)); yc = hw - a; yf = yc - V3['end_c']
        ys = np.linspace(-yc, yc, 800); zt0 = -sag(x, ys) - nm.planed(x)
        cr = np.where(np.abs(ys) <= yf, P['crown_h'], P['crown_h'] * np.sqrt(np.clip(1 - ((np.abs(ys) - yf) / V3['end_c']) ** 2, 0, 1)))
        ax.fill_between(ys, zt0, zt0 + cr, color=STEEL, lw=0)
        yt = yc - V3['tang_back']; yt_ = np.linspace(-yt, yt, 400); zt1 = -sag(x, yt_) - nm.planed(x)
        ax.fill_between(yt_, zt1 - P['tang_d'], zt1, color='0.45', lw=0)
        yse = yc - V3['slot_back']
        for s in (1, -1):
            ax.plot([s * yse, s * yse], [float(-sag(x, yse) - nm.planed(x)), float(-sag(x, yse) - nm.planed(x)) - P['slot_d']], color='w', lw=0.6)
    for i in (0, 5):
        ys_ = float(nm.string_y(i, x)); ax.plot([ys_], [float(-sag(x, ys_) - nm.planed(x)) + P['crown_h'] + 0.06], 'o', ms=4 if i == 5 else 3, color='tab:red')
    ax.set_aspect('equal')
    if zoom: ax.set_xlim(*zoom[0]); ax.set_ylim(*zoom[1])

def figures(R):
    x12 = float(fret_x(12)); xm = 0.5 * (float(fret_x(13)) + float(fret_x(14)))
    # 1. sections at a fret and mid-cell + edge close-ups
    fig, axs = plt.subplots(2, 3, figsize=(15, 8.6), gridspec_kw=dict(width_ratios=[1.6, 1, 1]))
    for r, (x, at, lab) in enumerate(((x12, True, 'at fret 12'), (xm, False, 'mid-cell 14 (deepest scallop 0.064)'))):
        draw_section(axs[r, 0], x, at); axs[r, 0].set_title(f'v3 section {lab}: rosewood 0.140 round-lam, dotted = glue line', fontsize=9)
        axs[r, 0].set_ylim(-1.02, 0.12)
        hw = float(width(x)) / 2
        draw_section(axs[r, 1], x, at, zoom=((-hw - 0.01, -hw + 0.20), (-0.27, 0.07))); axs[r, 1].set_title('treble edge', fontsize=9)
        draw_section(axs[r, 2], x, at, zoom=((hw - 0.20, hw + 0.01), (-0.27, 0.07))); axs[r, 2].set_title('bass edge', fontsize=9)
        if not at:
            for ax in axs[r, 1:]:
                yg = np.linspace(-hw, hw, 1200); ax.plot(yg, nm.top_z(x, yg, scallops=False), color='tab:blue', lw=0.7, ls='--')
    axs[0, 2].text(0.02, 0.03, 'grey: crown, ellipsoid end (0.040 x 0.025), apex at the roll start;\ndark: tang (nipped 0.035 from apex); white: stopped-slot end;\nred: outer strings', transform=axs[0, 2].transAxes, fontsize=7, va='bottom')
    axs[1, 2].text(0.02, 0.03, 'blue dashed: the same section at a fret (no scallop).\nThe scallop runs through the roll: same ellipse,\nsquashed to b - d, never below the fret-position roll bottom', transform=axs[1, 2].transAxes, fontsize=7, va='bottom')
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v3_sections.png'), dpi=130); plt.close(fig)

    # 2. side elevation, bass edge, frets 9-16
    fig, ax = plt.subplots(figsize=(14, 4.6))
    xx = np.linspace(float(fret_x(9)) - 0.25, float(fret_x(16)) + 0.25, 3000)
    hw = width(xx) / 2; a = nm.roll_a(xx); yc = hw - a
    z_rs = np.array([float(nm.top_z(x, y)) for x, y in zip(xx, yc)]) + nm.planed(xx)        # roll start line (edge top line)
    zb_ = np.array([float(roll_geom(np.array([x]), np.array([h - 1e-4]))[1][0]) for x, h in zip(xx, hw)])
    z_rb = -sag(xx, hw) - zb_                                                                # roll bottom (where the roll meets the side)
    z_g = np.array([float(v2.glue_z(x, h)) for x, h in zip(xx, hw)]) + nm.planed(xx)
    ax.fill_between(xx, z_g, z_rs, color=ROSE, alpha=0.35, lw=0)
    ax.fill_between(xx, z_g - 0.06, z_g, color=MAPLE, lw=0)
    ax.plot(xx, z_rs, color=ROSE, lw=1.6, label='edge top line (roll start): the scallop runs through it')
    ax.plot(xx, z_rb, color='k', lw=1.0, label='roll bottom on the side: straight (bass b 0.105)')
    ax.plot(xx, z_g, 'k:', lw=1.4, label='round-lam glue line on the side (0.035 below the roll bottom)')
    for n in range(9, 17):
        xf = float(fret_x(n)); hwf = float(width(xf)) / 2; z0 = float(-sag(xf, hwf - nm.roll_a(xf)))
        th = np.linspace(0, np.pi, 60); ax.fill(xf + 0.04 * np.cos(th), z0 + 0.043 * np.sin(th), color=STEEL, zorder=5)
    ax.text(float(fret_x(9)) + 0.02, -0.012, 'grey: fret ends seen from the side (dome on the full-height nib; the steel stops at the roll start)', fontsize=7)
    ax.set_ylim(-0.27, 0.0); ax.set_xlabel('x from nut (in)'); ax.set_ylabel('z (in), board-top centre = 0')
    ax.legend(fontsize=7, loc='lower right', ncol=2); ax.set_title('v3 side elevation, bass edge, frets 9-16 (vertical scale x4 vs horizontal)', fontsize=9)
    ax.set_aspect(4); fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v3_side_edge.png'), dpi=130); plt.close(fig)

    # 3. top view close-up of fret ends at the bass edge, frets 12-13
    fig, ax = plt.subplots(figsize=(11, 5.4))
    x0, x1 = float(fret_x(11)) + 0.2, float(fret_x(13)) + 0.15
    X = np.linspace(x0, x1, 500); Y = np.linspace(0.70, float(width(x1)) / 2 + 0.01, 260)
    XX, YY = np.meshgrid(X, Y, indexing='ij')
    Z = nm.top_z(XX, YY) + sag(XX, YY) + nm.planed(XX)
    Z = np.where(Z > -5, Z, np.nan)
    cs = ax.contourf(XX, YY, Z, levels=np.linspace(-0.11, 0.0, 23), cmap='copper'); fig.colorbar(cs, ax=ax, label='wood below the board-top surface (in)')
    ax.plot(X, width(X) / 2, 'k', lw=1.2, label='board edge (side wall)')
    ax.plot(X, width(X) / 2 - nm.roll_a(X), 'k--', lw=0.8, label='roll start')
    ax.plot(X, nm.string_y(5, X), color='tab:red', lw=1.6, label='low E (vintage spread)')
    for n in (12, 13):
        xf = float(fret_x(n)); hwf = float(width(xf)) / 2; yc = hwf - float(nm.roll_a(xf)); yf = yc - V3['end_c']
        tt = np.linspace(np.pi, 0, 60); poly_x = np.r_[xf - 0.04, xf + 0.04 * np.cos(tt), xf + 0.04]; poly_y = np.r_[0.69, yf + V3['end_c'] * np.sin(tt), 0.69]
        ax.fill(poly_x, poly_y, color=STEEL, ec='0.3', lw=0.8, label='crown, ellipsoid end 0.040 x 0.025' if n == 12 else None)
        yt = yc - V3['tang_back']; ax.plot([xf, xf], [0.69, yt], color='0.2', lw=2, label='tang (nipped)' if n == 12 else None)
        yse = yc - V3['slot_back']; sw = P['slot_w'] / 2; tt2 = np.linspace(np.pi, 0, 30)
        ax.plot(np.r_[xf - sw, xf - sw, xf + sw * np.cos(tt2), xf + sw, xf + sw], np.r_[0.69, yse - sw, yse - sw + sw * np.sin(tt2), yse - sw, 0.69],
                color='w', lw=0.8, ls='--', label='stopped slot outline (under the crown)' if n == 12 else None)
        ax.annotate(f'apex {float(nm.roll_a(xf)):.3f} from edge\nslot end {float(nm.roll_a(xf)) + V3["slot_back"]:.3f}', (xf + 0.05, yc - 0.01), fontsize=7)
    ax.set_aspect('equal'); ax.set_xlim(x0, x1); ax.set_ylim(0.69, float(width(x1)) / 2 + 0.01); ax.plot(X, width_v(X) / 2, color='tab:blue', lw=0.8, ls=':', label='vintage board edge (for comparison)')
    ax.set_xlabel('x (in)'); ax.set_ylabel('y (in, bass side)'); ax.legend(fontsize=7, loc='lower left')
    ax.set_title('v3 top view, bass edge, frets 12-13: fret ends stop on the full-height nib at the roll start; scallop runs out through the edge', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v3_fret_end_top.png'), dpi=130); plt.close(fig)

    # 4. 3-D render, frets 11-15, bass half
    from mpl_toolkits.mplot3d import Axes3D  # noqa
    fig = plt.figure(figsize=(12, 7)); ax = fig.add_subplot(111, projection='3d')
    xa, xb = float(fret_x(11)) - 0.05, float(fret_x(15)) + 0.05
    X = np.linspace(xa, xb, 360); U = np.linspace(-0.05, 1.0, 120)
    XX, UU = np.meshgrid(X, U, indexing='ij'); YY = UU * width(XX) / 2
    Z = nm.top_z(XX, YY); Z = np.where(Z > -5, Z, np.nan)
    ax.plot_surface(XX, YY, Z, color='#6a4428', rstride=2, cstride=2, linewidth=0, antialiased=True, shade=True)
    # side wall down to the glue line and maple below
    xs = X; hw = width(xs) / 2
    zs_top = np.array([float(nm.top_z(x, h - 1e-3)) if float(nm.top_z(x, h - 1e-3)) > -5 else np.nan for x, h in zip(xs, hw)])
    zrb = -sag(xs, hw) - nm.planed(xs) - np.array([float(roll_geom(np.array([x]), np.array([h - 1e-4]))[1][0]) for x, h in zip(xs, hw)])
    zg = np.array([float(v2.glue_z(x, h)) for x, h in zip(xs, hw)])
    for zlo, zhi, c in ((zg, zrb, '#6a4428'), (zg - 0.12, zg, MAPLE)):
        ZZ = np.vstack([zlo, zhi]); ax.plot_surface(np.vstack([xs, xs]), np.vstack([hw, hw]), ZZ, color=c, shade=True, linewidth=0)
    for n in range(11, 16):
        xf = float(fret_x(n)); hwf = float(width(xf)) / 2; yc = hwf - float(nm.roll_a(xf)); yf = yc - V3['end_c']
        tt = np.linspace(0, np.pi, 30); yv = np.linspace(-0.05 * hwf, yc, 80)
        TT, YV = np.meshgrid(tt, yv, indexing='ij')
        dy = np.maximum(YV - yf, 0); rr = np.sqrt(np.clip(1 - (dy / V3['end_c']) ** 2, 0, None))
        Xc = xf + P['crown_w'] / 2 * rr * np.cos(TT); Zc = -sag(xf, YV) - nm.planed(xf) + P['crown_h'] * rr * np.sin(TT)
        ax.plot_surface(Xc, YV, Zc, color='0.80', linewidth=0, shade=True)
    ax.set_box_aspect((xb - xa, 1.15, 0.6)); ax.view_init(elev=24, azim=-62)
    ax.set_xlabel('x'); ax.set_ylabel('y (bass)'); ax.set_zlabel('z'); ax.set_zlim(-0.35, 0.08)
    ax.set_title('v3 render, frets 11-15, bass half: proud frets, domes stop at the roll start, scallops run out through the rolled edge', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v3_render.png'), dpi=140); plt.close(fig)

    # 5. sections along the neck (shape law with the new A)
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw=dict(width_ratios=[1.6, 1]))
    FR = (1, 5, 9, 12, 17); cols = plt.cm.viridis(np.linspace(0.05, 0.9, len(FR)))
    for n, c in zip(FR, cols):
        x = float(fret_x(n)); yy, zz = nm.section_polygon(x, scallops=False)
        axs[0].plot(np.r_[yy, yy[:1]], np.r_[zz, zz[:1]], color=c, lw=1.4, ls='--' if n == 17 else '-', label=f'fret {n}' + (' (heel loft governs)' if n == 17 else ''))
        yg = np.linspace(-width(x) / 2 + 0.06, width(x) / 2 - 0.06, 200); axs[0].plot(yg, v2.glue_z(x, yg), color=c, lw=0.5, ls=':')
        ys_, zs_ = v2.section_back(x); axs[1].plot(2 * ys_ / width(x), zs_ / v2.D2(x), color=c, ls='--' if n == 17 else '-', label=f'fret {n}')
    axs[0].set_aspect('equal'); axs[0].legend(fontsize=7, loc='lower left'); axs[0].axvline(0, color='0.85', lw=0.6)
    axs[0].set_title('v3 sections (MOD depth, ruled loft A -> B, A = fuller bass shoulder only); dotted = glue line', fontsize=9)
    axs[0].set_xlabel('y (in), bass side right'); axs[0].set_ylabel('z (in), board top = 0')
    axs[1].axvline(0, color='0.85', lw=0.6); axs[1].legend(fontsize=7); axs[1].set_xlabel('u = 2y/W (bass +)'); axs[1].set_ylabel('z / D')
    axs[1].set_title('Normalised: fuller bass shoulder at the nut -> symmetric C', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, 'v3_profile_sections.png'), dpi=130); plt.close(fig)

def hand_girth(x):
    """Full perimeter and hand-contact girth (perimeter minus the flat top between the roll starts) of the plain section."""
    yy, zz = nm.section_polygon(x, scallops=False); n = len(yy) // 2
    P_ = np.r_[np.c_[yy, zz], [[yy[0], zz[0]]]]; seg = np.hypot(np.diff(P_[:, 0]), np.diff(P_[:, 1]))
    yc = float(width(x)) / 2 - float(nm.roll_a(x))
    top = np.arange(len(seg)) < n - 1; mid = 0.5 * (P_[:-1, 0] + P_[1:, 0])
    return float(seg.sum()), float(seg[~(top & (np.abs(mid) < yc))].sum())
FW = (0, 1, 5, 12, 17, 21)
def width_study():
    out = dict(rule={}, girth={}, widths={}, vibrato={})
    for n in range(12, 18):
        x = float(fret_x(n)); out['rule'][n] = V3['finger_side'] - (float(width_v(x)) / 2 - float(nm.spread(x)) / 2)
    out['widen_needed_per_side'] = max(out['rule'].values())
    # v2 baseline girth
    v2.V2['A'] = (0.06, 2.40, 1.90); v2.TB[0] = 0.140; v2.V2['roll_margin'] = 0.025
    v2.install(True)
    g2 = {n: hand_girth(float(fret_x(n)) if n else 0.02) for n in FW}
    v2.install(False)
    install()
    g3 = {n: hand_girth(float(fret_x(n)) if n else 0.02) for n in FW}
    for n in FW:
        out['girth'][n] = dict(v2_perim=g2[n][0], v3_perim=g3[n][0], v2_hand=g2[n][1], v3_hand=g3[n][1])
        x = float(fret_x(n)) if n else 0.0
        out['widths'][n] = dict(v3=float(width(x)), vintage=float(width_v(x)), roll_a=float(nm.roll_a(x)),
                                 string_to_edge=float(width(x)) / 2 - float(nm.spread(x)) / 2,
                                 usable_margin=float(width(x)) / 2 - float(nm.roll_a(x)) - end_usable_t() - float(nm.spread(x)) / 2,
                                 usable_margin_vintage=float(vint_margin(x, 0)))
    for lab, x in (('x_h', v2.XH), ('pocket datum 15.69', 15.69), ('tongue end 21.7', 21.7)):
        out['widths'][lab] = dict(v3=float(width(x)), vintage=float(width_v(x)))
    # edge-ward vibrato before the string leaves the usable crown; inward displacement for a 2-step bend (reference)
    T = nm.tensions(-1, 0) * 4.448
    for i, core in ((0, 1.0), (5, 0.40)):          # low E: hex core ~0.40 d [judged]
        d = STR[i][1] * core * IN; EA = 200e9 * math.pi * d * d / 4
        for n in (12, 17):
            x = float(fret_x(n)); m = out['widths'].get(n, {}).get('usable_margin') or 0.0
            m = float(width(x)) / 2 - float(nm.roll_a(x)) - end_usable_t() - float(nm.spread(x)) / 2
            k = 0.5 * (1 / x + 1 / (P['scale'] - x))
            def cents(dl): return 1200 * math.log2(math.sqrt(1 + EA * (k * dl * dl / P['scale']) / T[i]))
            mv = float(vint_margin(x, 0))
            need2 = math.sqrt((2 ** (8 / 12) - 1) * T[i] / EA * P['scale'] / k)
            out['vibrato'][f'{STR[i][0]} fret {n}'] = dict(v3_cents=cents(m), vintage_cents=cents(mv), inward_disp_2step=need2)
    return out

def main():
    R = {'V3': V3}
    R['width'] = width_study()
    R['shape'] = []
    for n in (1, 5, 9, 12, 17):
        s = v2.shape_metrics(float(fret_x(n))); s['fret'] = n; R['shape'].append(s)
    R['ruled_dev'] = v2.ruled_check2()
    R['edge'] = edge_rows(); R['slot_wall'] = slot_wall_checks(); R['ball'] = ball_limit(); R['wood'] = wood_min()
    R['glue_fin'] = glue_and_fin_checks(); R['catch'] = catch_v3(); R['edge_slide'] = edge_slide()
    R['relief'] = nm.relief_design()
    R['modes'] = dict(plain=nm.neck_modes(False).tolist(), scalloped=nm.neck_modes(True).tolist())
    R['scallop_removed_in3'] = v2.scallop_volume2.__wrapped__() if hasattr(v2.scallop_volume2, '__wrapped__') else None
    xs = np.linspace(0, X22, 3000); vol = 0.0; dx = xs[1] - xs[0]
    for x in xs:
        hw = float(width(x)) / 2; y = np.linspace(-hw, hw, 81); dy = y[1] - y[0]; vol += float((-scallop_z3(np.full_like(y, x), y)).sum() * dy * dx)
    R['scallop_removed_in3'] = vol
    R['EI'] = {n: v2.EI_section2(float(fret_x(n)))[0] for n in (1, 5, 9, 12)}
    figures(R)
    with open(os.path.join(HERE, 'results_v3.json'), 'w') as fh: json.dump(R, fh, indent=1, default=float)
    report(R)
def report(R):
    W = R['width']; print('== width rule', {k: round(v, 4) for k, v in W['rule'].items()}, 'needed per side', round(W['widen_needed_per_side'], 4))
    for k, v in W['widths'].items(): print('   W', k, {kk: round(vv, 4) for kk, vv in v.items()})
    for k, v in W['girth'].items(): print('   girth', k, {kk: round(vv, 4) for kk, vv in v.items()})
    for k, v in W['vibrato'].items(): print('   vib', k, {kk: round(vv, 3) for kk, vv in v.items()})
    print('== shape'); [print('  ', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()}) for s in R['shape']]
    print('== ruled dev', R['ruled_dev'])
    print('== edge rows'); [print('  ', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}) for r in R['edge']]
    print('== slot wall'); [print('  ', r) for r in R['slot_wall']]
    print('== ball', R['ball']); print('== wood', R['wood']); print('== glue/fin', R['glue_fin'])
    print('== catch'); [print('  ', round(c['catch'], 1), round(c['flat'], 1), c['cell'], round(c['d'], 3)) for c in R['catch']]
    print('== edge slide', R['edge_slide'])
    rl = R['relief']; print('== relief planed sag %.4f gap %.4f need %.4f per100 %.4f F %.0f' % (rl['planed_sag'], rl['planed_gap'], rl['rod_need_in'], rl['rod_in_per_100lb'], rl['rod_F_lb']))
    for k, r in rl['rows'].items(): print('  ', k, {kk: round(vv, 4) for kk, vv in r.items()})
    print('== modes', R['modes'], 'vol', R['scallop_removed_in3']); print('== EI', R['EI'])

if __name__ == '__main__':
    main()
