#!/usr/bin/env python3
"""Supercaster II headstock: best nut break angle as a constrained optimum.

Run:  body/sim/cache/venv/bin/python -I -B neck/v4/headstock/break_opt.py   -> results.json beside this file
Reads neck_v4.py (imported, not edited). Inches, lb, degrees unless a name says otherwise.
Frame as neck_v4: x from the nut toward the bridge (posts at negative x), y + bass, z up, z = 0 board-top centreline.
"""
import functools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V4 = os.path.dirname(HERE)
sys.path.insert(0, V4)
import neck_v4 as N  # noqa: E402

P, S, MM = N.P, N.S, 1 / 25.4
DEG = math.degrees
NAMES = [s[0] for s in N.STRINGS]
DIA = np.array([s[1] for s in N.STRINGS])
T_EB = N.tensions(-1, 0)
T_DC = N.tensions(-1, 2)                        # drop C#: only E6 changes
K_CENT = 600 / math.log(2)                       # 865.6 cents per unit relative tension change, times 1/2 already

# ------------------------------------------------------------------ assumptions (flagged in BREAK-ANGLE.md) ----
A = dict(
    F_pluck_N=2.6,        # vertical pick force; = the force implied by neck_v4's own pluck (0.15 in at S/5 on E1)
    F_range_N=(1.5, 4.0), # assumed span of hard-pick vertical force [assumption]
    SF=1.25,              # safety factor on the pluck lift
    dz_tol=0.5 * MM,      # post height / slot floor / winding tolerance on the exit height
    bush_proud=1.0 * MM,  # SD91 press bushing top above the face [assumption, measure: 0.5 to 1.5 mm]
    r_post=6.35 / 2 * MM, # post radius [lit, DESIGN 6.1]
    flange_od=10.0 * MM,  # bushing flange OD [assumption 9.5 to 10.5 mm]
    edge_wood=0.125,      # least wood from flange to outline edge, normal practice [assumption]
    look_B=None,          # filled below: head back no deeper than the neck back at the nut (no volute, SPEC 9)
    hole_ref='centre',    # Gotoh base-to-hole figure taken to the hole centre [assumption]
    blank_t=1.5, flatten=0.06, head_len=7.3,
)
D_NUT = float(N.depth(0.0))                      # wood depth at the nut, board top to back
A['look_B'] = D_NUT
R_RISE = math.atan((P['action_12'] - P['nut_clear']) / N.X12)   # playing-side rise at the nut

POSTS = {  # base-plate (back of head) to string hole, mm, per string E1..E6
    'gotoh_stag_20_18.5': [20, 20, 20, 18.5, 18.5, 18.5],   # SPEC 7 [lit, retailer]
    'rockinger_stag_19_18': [19, 19, 19, 18, 18, 18],      # DESIGN 6.1 [lit]
    'flat_18.5': [18.5] * 6,
    'all_tall_20': [20] * 6,
}
HAPM = (16.0, 20.5)  # SD91 HAP-M base-to-hole range, mm [lit: Rockinger listing, not a Gotoh drawing]


# ------------------------------------------------------------------ 1. reproduce SPEC section 7 ----
def reproduce():
    ref = json.load(open(os.path.join(V4, 'results.json')))['nut_head']['strings']
    got = N.nut_and_head()['strings']
    err = max(abs(a[k] - b[k]) for a, b in zip(ref, got) for k in ('break_deg', 'downforce_lb', 'seat_margin', 'return_error_cents'))
    assert err < 1e-5, err
    return got, err


# ------------------------------------------------------------------ 2. pluck: end slope at the nut ----
def pluck_check(A_in=0.15, beta=0.2, nmodes=4000):
    """Ideal plucked string, apex at distance beta*S from the saddle. Fourier sum of y_x(0, t) over one period."""
    a = (1 - beta) * S                                          # apex distance from the nut
    n = np.arange(1, nmodes + 1)
    bn = 2 * A_in * S ** 2 / (np.pi ** 2 * n ** 2 * a * (S - a)) * np.sin(n * np.pi * a / S)
    t = np.linspace(0, 1, 4001)                                 # fraction of a period
    slope = (bn[:, None] * (n[:, None] * np.pi / S) * np.cos(2 * np.pi * n[:, None] * t[None, :])).sum(0)
    return dict(A_in=A_in, beta=beta, near_segment_slope_deg=DEG(A_in / a), far_segment_slope_deg=DEG(A_in / (S - a)),
                fourier_max_up_deg=DEG(slope.max()), fourier_max_down_deg=DEG(-slope.min()),
                note='upstroke lifts at A/a (neck_v4 lift); a downstroke lifts at A/(S-a), reached half a period later')


def implied_force_lb(A_in=0.15, beta=0.2, T=None):
    T = T_EB[0] if T is None else T
    d = beta * S
    return A_in * T * S / (d * (S - d))


def floor_eff(L, T, F_N=None, SF=None):
    """Least effective (vertical, net of the playing-side rise) wrap angle, rad: T*theta >= SF*F, plus height tolerance."""
    F = (A['F_pluck_N'] if F_N is None else F_N) / 4.4482216
    SFv = A['SF'] if SF is None else SF
    return SFv * F / T + A['dz_tol'] / L


# ------------------------------------------------------------------ 3. geometry ----
def string_lines():
    yn = np.linspace(-P['nut_spread'] / 2, P['nut_spread'] / 2, 6)
    yb = np.linspace(-P['bridge_spread'] / 2, P['bridge_spread'] / 2, 6)
    return yn, (yb - yn) / S                                   # y at nut, lateral slope toward the bridge


@functools.lru_cache(maxsize=None)
def row_layout(x1, mode='straight', side=-1):
    """Post centres (x<0, y) and tangent points. mode 'v4': centres on nut-spacing lines (neck_v4).
    'straight': tangent points on the extended (fanned) string lines, centres offset (r_post + d/2) to side
    (-1 = treble/button side, the mirror of a standard Fender wind), centres on one straight row at 15/16 pitch."""
    yn, k = string_lines()
    p = P['post_pitch']
    off = side * (A['r_post'] + DIA / 2)
    if mode == 'v4':
        step = math.sqrt(p ** 2 - (P['nut_spread'] / 5) ** 2)
        xc = -(x1 + step * np.arange(6))
        yc = yn.copy()
        return dict(xc=xc, yc=yc, xt=xc, yt=yc - off, row_deg=DEG(math.atan2(P['nut_spread'] / 5, step)),
                    resid=np.zeros(6), off=off, tangent_on_centre=True)
    best = None
    for al in np.radians(np.linspace(10, 20, 2001)):
        xc = -(x1 + p * math.cos(al) * np.arange(6))
        want = yn + k * xc + off                                # centre needed for exact straight pull
        line = p * math.sin(al) * np.arange(6)
        y0 = np.mean(want - line)
        res = (y0 + line) - want
        sc = np.sqrt(np.mean(res ** 2))
        if best is None or sc < best[0]:
            best = (sc, al, xc, y0 + line, res)
    sc, al, xc, yc, res = best
    return dict(xc=xc, yc=yc, xt=xc, yt=yc - off, row_deg=DEG(al), resid=res, rms_resid=sc, off=off, tangent_on_centre=False)


def evaluate(B, H_mm, wraps, x1=1.85, t=0.56, mode='straight', side=-1, radius_nut=True, mu=(0.10, 0.20),
             tilt_deg=0.0, rise_sign=-1, ideal=False):
    """Per-string nut geometry. B = head back below the board top (face drop + head thickness).
    rise_sign -1: the playing-side rise opens the wrap (correct); +1 reproduces neck_v4."""
    lay = row_layout(x1, mode, side)
    yn, k = string_lines()
    H = np.array(H_mm) * MM
    n = np.array(wraps, float)
    rows = []
    for i in range(6):
        L = -lay['xt'][i]
        y_nut = yn[i]
        z_nut = (float(N.board(0.0, y_nut)) if radius_nut else 0.0) + N.HF + P['nut_clear'] + DIA[i] / 2
        if tilt_deg:
            al = math.radians(tilt_deg)
            face = -(B - t) - L * math.sin(al)                  # B - t = face below board top at the nut
            z_exit = face + (H[i] - t) * math.cos(al) - n[i] * DIA[i] * math.cos(al)
        else:
            z_exit = -B + H[i] - n[i] * DIA[i]
        h = z_nut - z_exit
        dy = 0.0 if ideal else lay['yt'][i] - y_nut           # ideal: neck_v4's string to the post centre, no fan
        ki = 0.0 if ideal else k[i]
        u = np.array([1.0, ki, math.tan(R_RISE)]); u /= np.linalg.norm(u)
        v = np.array([L, -dy, h]); v /= np.linalg.norm(v)       # direction continuing from post through nut
        phi = math.acos(np.clip(u @ v, -1, 1))                  # 3-D deviation at the nut (wrap angle)
        th_v = math.atan(h / L)
        if rise_sign > 0:
            phi = th_v + R_RISE                                 # neck_v4's sign, for the step-by-step table only
        th_eff = th_v + rise_sign * R_RISE                      # vertical seating angle
        lat = math.atan2(dy, L) + math.atan(ki)               # lateral deviation
        Ti = T_EB[i]
        f = floor_eff(L, Ti); f_dc = floor_eff(L, T_DC[i])
        room = (H[i] - t) - A['bush_proud'] - DIA[i] / 2
        rows.append(dict(string=NAMES[i], L_in=L, post_xy=[float(lay['xc'][i]), float(lay['yc'][i])], H_mm=float(H_mm[i]),
                         wraps=float(n[i]), wraps_max=math.floor(room / DIA[i] * 2) / 2, exit_z_in=z_exit,
                         exit_above_face_in=z_exit + (B - t), nut_z_in=z_nut, drop_in=h,
                         break_vert_deg=DEG(th_v), break_eff_deg=DEG(th_eff), lateral_deg=DEG(lat), wrap3d_deg=DEG(phi),
                         floor_eff_deg=DEG(f), floor_eff_dropCs_deg=DEG(f_dc), clear_deg=DEG(th_eff - max(f, f_dc)),
                         downforce_lb=Ti * (math.sin(th_v) + rise_sign * math.sin(R_RISE)),
                         downforce_dropCs_lb=T_DC[i] * (math.sin(th_v) + rise_sign * math.sin(R_RISE)),
                         seat_margin=Ti * th_eff / (A['F_pluck_N'] / 4.4482216),
                         seat_margin_dropCs=T_DC[i] * th_eff / (A['F_pluck_N'] / 4.4482216),
                         unseat_A_mm_beta8=th_eff * S / 8 / MM, unseat_A_mm_beta5=th_eff * S / 5 / MM,
                         **{'err_mu%.2f_c' % m: K_CENT * m * phi * L / (S + L) for m in mu},
                         feasible_wraps=n[i] <= math.floor(room / DIA[i] * 2) / 2 + 1e-9))
    return dict(rows=rows, row_deg=lay['row_deg'], row_rms_resid_in=lay.get('rms_resid', 0.0), B=B, t=t, x1=x1)


def wraps_for(B, H_mm, x1, t, target_pad_deg=0.0):
    """Least half-wraps per string that lift each effective angle to its floor (Eb, and drop C# for E6)."""
    n = []
    for i in range(6):
        best = None
        for w in np.arange(0, 12.01, 0.5):
            r = evaluate(B, H_mm, [w if j == i else 0 for j in range(6)], x1, t)['rows'][i]
            if w > r['wraps_max'] + 1e-9:
                break
            best = w
            if r['clear_deg'] >= target_pad_deg:
                break
        n.append(best)
    return n


def seat_N(r, i):
    """Pick force (N) this string resists at SF, worst of Eb and drop C#."""
    th = math.radians(r['break_eff_deg']) - A['dz_tol'] / r['L_in']
    return min(T_EB[i], T_DC[i]) * th / A['SF'] * 4.4482216


def equal_margin(B, H_mm, x1, t, step=0.5):
    """Wraps that bring every string to the same seating force: the weakest string (wraps maxed) sets the level."""
    nmax, Fmax = [], []
    for i in range(6):
        r0 = evaluate(B, H_mm, [0] * 6, x1, t)['rows'][i]
        nm = r0['wraps_max']
        nmax.append(nm)
        Fmax.append(seat_N(evaluate(B, H_mm, [nm if j == i else 0 for j in range(6)], x1, t)['rows'][i], i))
    Fok = min(Fmax)
    n = []
    for i in range(6):
        w = 0.0
        while w < nmax[i] and seat_N(evaluate(B, H_mm, [w if j == i else 0 for j in range(6)], x1, t)['rows'][i], i) < Fok - 1e-9:
            w += step
        n.append(w)
    return n, Fok, NAMES[int(np.argmin(Fmax))]


def summary(ev):
    r = ev['rows']
    return dict(seat_force_N=min(seat_N(x, i) for i, x in enumerate(r)), weakest=NAMES[int(np.argmin([seat_N(x, i) for i, x in enumerate(r)]))],
                max_err20=max(x['err_mu0.20_c'] for x in r), sum_err20=sum(x['err_mu0.20_c'] for x in r),
                min_clear=min(x['clear_deg'] for x in r), spread_eff=max(x['break_eff_deg'] for x in r) - min(x['break_eff_deg'] for x in r),
                wraps_ok=all(x['feasible_wraps'] for x in r))


# ------------------------------------------------------------------ 4. search ----
def search():
    out = []
    for name, H in POSTS.items():
        for B in np.round(np.arange(0.80, 1.101, 0.01), 3):
            for x1 in (1.70, 1.85, 2.00):
                for t in (0.56, 0.50):
                    n = wraps_for(B, H, x1, t)
                    ev = evaluate(B, H, n, x1, t)
                    s = summary(ev)
                    out.append(dict(mode='floor', posts=name, H_mm=H, B=float(B), face_drop=float(B - t), x1=x1, t=t, wraps=n, **s))
                    n2, Fok, weak = equal_margin(B, H, x1, t)
                    s2 = summary(evaluate(B, H, n2, x1, t))
                    out.append(dict(mode='equal_margin', posts=name, H_mm=H, B=float(B), face_drop=float(B - t), x1=x1, t=t, wraps=n2, **s2))
    # HAP-M: continuous per-string hole height, no wraps; put every string at its floor where the range allows
    for B in np.round(np.arange(0.80, 1.101, 0.01), 3):
        for x1 in (1.70, 1.85, 2.00):
            for t in (0.56, 0.50):
                H = []
                for i in range(6):
                    hs = np.arange(HAPM[0], HAPM[1] + 1e-9, 0.1)
                    ok = [h for h in hs if evaluate(B, [h] * 6, [0] * 6, x1, t)['rows'][i]['clear_deg'] >= 0
                          and (h * MM - t) - A['bush_proud'] - DIA[i] / 2 >= 0]
                    H.append(float(max(ok)) if ok else HAPM[0])
                ev = evaluate(B, H, [0] * 6, x1, t)
                s = summary(ev)
                out.append(dict(mode='floor', posts='hapm_16_20.5', H_mm=H, B=float(B), face_drop=float(B - t), x1=x1, t=t, wraps=[0] * 6, **s))
    return out


def pick_margin(cands, posts=None):
    ok = [c for c in cands if c['mode'] == 'equal_margin' and c['wraps_ok'] and c['B'] <= A['look_B'] + 1e-9 and (posts is None or c['posts'] == posts)]
    ok.sort(key=lambda c: (-round(c['seat_force_N'], 1), round(c['max_err20'], 2), sum(c['wraps']), abs(c['t'] - 0.56), abs(c['x1'] - 1.85)))
    return ok


def pick(cands, look=True):
    ok = [c for c in cands if c['mode'] == 'floor' and c['min_clear'] >= -1e-9 and c['wraps_ok'] and (not look or c['B'] <= A['look_B'] + 1e-9)]
    ok.sort(key=lambda c: (round(c['max_err20'], 2), round(c['sum_err20'], 1), sum(c['wraps']), abs(c['t'] - 0.56), abs(c['x1'] - 1.85), -c['B']))
    return ok


# ------------------------------------------------------------------ 5. outline check ----
HEAD = N.HEAD_OUTLINE * np.array([1, -1])          # mirrored for the reverse head, as neck_v4 does


def catmull(pts, per=60):
    """THREE.SplineCurve (uniform Catmull-Rom, clamped ends) through pts, then the straight closing segment."""
    pts = np.asarray(pts, float)
    m = len(pts)
    out = []
    for s in range(m - 1):
        p0 = pts[max(s - 1, 0)]; p1 = pts[s]; p2 = pts[s + 1]; p3 = pts[min(s + 2, m - 1)]
        for t in np.linspace(0, 1, per, endpoint=False):
            v0 = (p2 - p0) * 0.5; v1 = (p3 - p1) * 0.5
            t2, t3 = t * t, t * t * t
            out.append((2 * p1 - 2 * p2 + v0 + v1) * t3 + (-3 * p1 + 3 * p2 - 2 * v0 - v1) * t2 + v0 * t + p1)
    out.append(pts[-1])
    return np.array(out)


def inside(poly, q):
    x, y = q; c = False
    for (x0, y0), (x1, y1) in zip(poly, np.roll(poly, -1, 0)):
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            c = not c
    return c


def seg_dist(poly, q):
    a = poly; b = np.roll(poly, -1, 0); ab = b - a
    t = np.clip(((q - a) * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-12), 0, 1)
    d = np.linalg.norm(a + ab * t[:, None] - q, axis=1)
    return float(d.min())


def ray_to_edge(poly, q, direction):
    """Distance from q along direction to the outline."""
    best = np.inf
    d = np.asarray(direction, float) / np.linalg.norm(direction)
    for a, b in zip(poly, np.roll(poly, -1, 0)):
        e = b - a
        M = np.array([d, -e]).T
        if abs(np.linalg.det(M)) < 1e-12:
            continue
        s, u = np.linalg.solve(M, a - q)
        if s > 0 and 0 <= u <= 1:
            best = min(best, s)
    return best


def outline_check(layout):
    poly = catmull(HEAD)
    rf = A['flange_od'] / 2
    al = math.radians(layout['row_deg'])
    btn = np.array([-math.sin(al), -math.cos(al)])        # perpendicular to the row, toward the treble/button edge
    btn = btn if btn[1] < 0 else -btn
    rows = []
    for i in range(6):
        q = np.array([layout['xc'][i], layout['yc'][i]])
        d = seg_dist(poly, q) if inside(poly, q) else -seg_dist(poly, q)
        rows.append(dict(string=NAMES[i], post=[float(q[0]), float(q[1])], centre_to_edge_in=d, flange_wood_in=d - rf,
                         ok=bool(d - rf >= A['edge_wood']), to_button_edge_in=ray_to_edge(poly, q, btn)))
    tb = [r['to_button_edge_in'] for r in rows]
    # the button-side edge of the vintage outline, slope along the post zone
    xs = np.linspace(-1.8, -6.4, 40)
    yedge = [min(p[1] for p in poly if abs(p[0] - x) < 0.03) for x in xs]
    edge_deg = DEG(math.atan(np.polyfit(xs, yedge, 1)[0]))
    return dict(rows=rows, row_deg=layout['row_deg'], button_edge_spread_in=max(tb) - min(tb),
                vintage_button_edge_angle_to_axis_deg=abs(edge_deg),
                all_flanges_ok=all(r['ok'] for r in rows))


# ------------------------------------------------------------------ 6. tilt-back alternative ----
def tilt():
    usable = A['blank_t'] - A['flatten']           # below the glue plane
    t = 0.56
    f0 = 0.0                                        # face starts at the glue plane at the nut
    al = 0.0
    for a in np.radians(np.arange(0, 20, 0.05)):
        if f0 + A['head_len'] * math.sin(a) + t / math.cos(a) <= usable:
            al = a
    out = dict(one_piece_max_deg=DEG(al), usable_below_glue_in=usable)
    ratio = (0.05, 0.10)                            # cross / along grain strength [assumption]
    out['short_grain_strength_frac'] = {('%g' % r): {('%d' % d): r / (math.sin(math.radians(d)) ** 2 + r * math.cos(math.radians(d)) ** 2)
                                                      for d in (5, 7, 10, 14)} for r in ratio}
    B = P['board_t'] + t
    ev = evaluate(B, POSTS['flat_18.5'], [0] * 6, 1.85, t, tilt_deg=DEG(al))
    out['flat_posts_at_max'] = [dict(string=r['string'], break_eff_deg=r['break_eff_deg'], err20=r['err_mu0.20_c'], err10=r['err_mu0.10_c']) for r in ev['rows']]
    return out


def sens(base):
    B, H, n, x1, t = base['B'], base['H_mm'], base['wraps'], base['x1'], base['t']
    r0 = evaluate(B, H, n, x1, t)['rows']
    def d(**kw):
        a = dict(B=B, H_mm=H, wraps=n, x1=x1, t=t); a.update(kw)
        r = evaluate(a['B'], a['H_mm'], a['wraps'], a['x1'], a['t'])['rows']
        return [round(r[i]['break_eff_deg'] - r0[i]['break_eff_deg'], 3) for i in range(6)], [round(r[i]['err_mu0.20_c'] - r0[i]['err_mu0.20_c'], 3) for i in range(6)]
    out = {}
    out['B_plus_0.01in'] = d(B=B + 0.01)
    out['posts_plus_0.5mm'] = d(H_mm=[h + 0.5 for h in H])
    out['x1_plus_0.10in'] = d(x1=x1 + 0.10)
    out['one_more_wrap_each'] = d(wraps=[w + 1 for w in n])
    out['floor_per_N_pick_force_deg'] = [round(DEG(A['SF'] / 4.4482216 / T_EB[i]), 3) for i in range(6)]
    out['err_scales_with_mu'] = 'linear: err(mu) = err(0.20) * mu / 0.20'
    return out


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return round(float(o), 4)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main():
    R = dict(units='in, lb, deg, cents', assumptions={k: v for k, v in A.items()})
    got, err = reproduce()
    R['spec7_reproduced'] = dict(max_abs_diff=err, rows=got, physics=dict(
        break_angle='atan((z_nut - z_post)/L), z_nut = fret_h + nut_clear + d/2 on the CENTRELINE, z_post = -face_drop + (base_to_hole - head_t), L = post_x1 + i*step',
        downforce='2 T sin((theta + r)/2), r = atan((action_12 - nut_clear)/X12) = %.3f deg added' % DEG(R_RISE),
        margin='theta / (0.15 / (0.8 S)): break over the nut-side slope of a 0.15 in pluck at S/5 from the saddle',
        error='865.6 mu (theta + r) L/(S + L): capstan step mu*theta*T held at the nut, shared over S + L of string, cents = (600/ln2) dT/T',
        tensions='Eb standard only (tensions(-1, 0)); drop C# not used'))
    R['corrections'] = dict(
        rise_sign='the string climbs on both sides of the nut, so the wrap is theta - r, not theta + r (%.3f deg)' % DEG(R_RISE),
        board_radius='outer strings sit %.4f (E) / %.4f (B, A) / %.4f (G, D) below the centreline on the 7.25 radius' % tuple(-float(N.board(0, y)) for y in (0.6875, 0.4125, 0.1375)),
        pluck=pluck_check(), implied_pick_force_N=implied_force_lb() * 4.4482216,
        tangent='posts carry the string on their side: centre must sit r_post + d/2 = 0.13 to 0.15 off the string line, and the strings fan')
    # SPEC geometry with corrections, step by step
    B0 = P['head_face_drop'] + P['head_t']
    H0 = POSTS['gotoh_stag_20_18.5']
    steps = dict(
        v4_as_built=evaluate(B0, H0, [0] * 6, mode='v4', radius_nut=False, rise_sign=+1, ideal=True),
        plus_rise_sign=evaluate(B0, H0, [0] * 6, mode='v4', radius_nut=False, ideal=True),
        plus_radius=evaluate(B0, H0, [0] * 6, mode='v4', ideal=True),
        plus_v4_layout_tangent_and_fan=evaluate(B0, H0, [0] * 6, mode='v4'),
        plus_true_straight_pull=evaluate(B0, H0, [0] * 6),
    )
    R['spec_corrected'] = {k: [dict(string=r['string'], eff=r['break_eff_deg'], lateral=r['lateral_deg'], wrap3d=r['wrap3d_deg'],
                                    floor=r['floor_eff_deg'], floor_dropCs=r['floor_eff_dropCs_deg'], margin=r['seat_margin'],
                                    err20=r['err_mu0.20_c']) for r in v['rows']] for k, v in steps.items()}
    R['look_limit'] = dict(neck_depth_at_nut=D_NUT, spec_head_back=B0, spec_step_below_neck_back=B0 - D_NUT,
                           blank_room_below_board_top=P['board_t'] + A['blank_t'] - A['flatten'],
                           note='posts are back-mounted: string height depends only on B = face_drop + head_t, never on face drop alone')
    cands = search()
    best_look = pick(cands, True)
    best_any = pick(cands, False)
    R['n_candidates'] = len(cands)
    R['best_look_constrained'] = best_look[:8]
    R['best_unconstrained'] = best_any[:5]
    R['best_by_postset_look'] = {name: (pick([c for c in cands if c['posts'] == name], True) or [None])[0] for name in list(POSTS) + ['hapm_16_20.5']}
    R['infeasible_reasons'] = {name: min((c for c in cands if c['posts'] == name and c['B'] <= D_NUT + 1e-9 and c['wraps_ok']), key=lambda c: -c['min_clear'])['min_clear']
                               for name in list(POSTS) + ['hapm_16_20.5']}
    # recommended: staggered Gotoh MG-T (the set already chosen) if feasible under the look limit, else the best look-feasible
    R['look_equal_margin_by_postset'] = {name: pick_margin(cands, name)[:3] for name in POSTS}
    R['look_equal_margin_t056_x185'] = {name: [c for c in pick_margin(cands, name) if c['t'] == 0.56 and c['x1'] == 1.85][:1] for name in POSTS}
    eqm = [c for c in pick_margin(cands, 'gotoh_stag_20_18.5') if c['t'] == 0.56 and c['x1'] == 1.85][0]
    R['alt_equal_margin'] = dict(setting=eqm, note='lowest total error: every string pulled down to the weakest (E6) margin')
    # recommended: look limit B <= neck depth at the nut, SPEC hardware; each string wrapped up to its floor (E6 cannot reach it)
    rec = [c for c in cands if c['mode'] == 'floor' and c['posts'] == 'gotoh_stag_20_18.5' and c['t'] == 0.56 and c['x1'] == 1.85
           and abs(c['B'] - 0.89) < 1e-6][0]
    R['note_floor'] = ('under B <= %.3f no listed post set meets the floor on E6: the lowest exit any of them gives is about 16 mm above '
                       'the head back (short post + max wraps, or HAP-M minimum), so E6 is set by B; recommended wraps every other string to its floor') % D_NUT
    alt = best_any[0]
    eva = evaluate(alt['B'], alt['H_mm'], alt['wraps'], alt['x1'], alt['t'])
    R['alt_unconstrained'] = dict(setting=alt, rows=eva['rows'])
    ev = evaluate(rec['B'], rec['H_mm'], rec['wraps'], rec['x1'], rec['t'])
    R['recommended'] = dict(setting=rec, rows=ev['rows'], row_deg=ev['row_deg'], row_rms_resid_in=ev['row_rms_resid_in'], sensitivities=sens(rec))
    # flush-back with the SPEC hardware, wraps maxed: what you get without changing posts
    R['outline'] = dict(straight=outline_check(row_layout(1.85)), v4_layout=outline_check(row_layout(1.85, 'v4')),
                        straight_other_side=outline_check(row_layout(1.85, 'straight', +1)))
    R['tilt'] = tilt()
    R['floor_vs_force'] = {('%.1fN' % F): [round(DEG(floor_eff(-ev['rows'][i]['L_in'] * -1, T_EB[i], F)), 2) for i in range(6)] for F in (1.5, 2.0, 2.6, 3.0, 4.0)}
    json.dump(clean(R), open(os.path.join(HERE, 'results.json'), 'w'), indent=1)
    # console
    print('reproduce max diff', err)
    print('pluck', clean(R['corrections']['pluck']), 'implied force N %.2f' % R['corrections']['implied_pick_force_N'])
    for k, v in R['spec_corrected'].items():
        print(k, [(r['string'], round(r['eff'], 2), round(r['floor'], 2), round(r['margin'], 2), round(r['err20'], 2)) for r in v])
    print('look', clean(R['look_limit']))
    for name, c in R['look_equal_margin_by_postset'].items():
        for x in c:
            print('EQ', name, {k: x[k] for k in ('B', 'x1', 't', 'wraps', 'seat_force_N', 'weakest', 'max_err20', 'sum_err20')})
    for name, c in R['look_equal_margin_t056_x185'].items():
        for x in c:
            print('EQ056', name, {k: x[k] for k in ('B', 'x1', 't', 'wraps', 'seat_force_N', 'weakest', 'max_err20', 'sum_err20')})
    for name, c in R['best_by_postset_look'].items():
        print('postset', name, c and {k: c[k] for k in ('B', 'x1', 't', 'wraps', 'H_mm', 'max_err20', 'sum_err20', 'min_clear', 'spread_eff')}, 'best clear', round(R['infeasible_reasons'][name], 2))
    print('best any', [{k: c[k] for k in ('posts', 'B', 'x1', 't', 'wraps', 'max_err20', 'min_clear')} for c in best_any[:3]])
    print('REC', {k: rec[k] for k in ('posts', 'B', 'face_drop', 'x1', 't', 'wraps', 'H_mm', 'max_err20', 'seat_force_N', 'weakest')}, 'row', round(ev['row_deg'], 2), 'resid', round(ev['row_rms_resid_in'], 4))
    for r in ev['rows']:
        print(' %s L%.2f H%.1f n%.1f/%.1f exit%.3f eff%.2f fl%.2f/%.2f lat%.2f F%.2f m%.2f e10 %.2f e20 %.2f seatN %.2f' % (
            r['string'], r['L_in'], r['H_mm'], r['wraps'], r['wraps_max'], r['exit_above_face_in'], r['break_eff_deg'], r['floor_eff_deg'],
            r['floor_eff_dropCs_deg'], r['lateral_deg'], r['downforce_lb'], r['seat_margin'], r['err_mu0.10_c'], r['err_mu0.20_c'], seat_N(r, NAMES.index(r['string']))))
    for r in eva['rows']:
        print(' ALT %s L%.2f H%.1f n%.1f exit%.3f eff%.2f fl%.2f/%.2f e10 %.2f e20 %.2f' % (r['string'], r['L_in'], r['H_mm'], r['wraps'], r['exit_above_face_in'], r['break_eff_deg'], r['floor_eff_deg'], r['floor_eff_dropCs_deg'], r['err_mu0.10_c'], r['err_mu0.20_c']))
    print('sens', R['recommended']['sensitivities'])
    for k, o in R['outline'].items():
        print('outline', k, 'row %.2f' % o['row_deg'], 'edge angle %.1f' % o['vintage_button_edge_angle_to_axis_deg'], 'btn spread %.2f' % o['button_edge_spread_in'],
              [(r['string'], round(r['flange_wood_in'], 3), round(r['to_button_edge_in'], 2)) for r in o['rows']])
    print('tilt', clean(R['tilt']))
    print('floor vs force', R['floor_vs_force'])


if __name__ == '__main__':
    main()
