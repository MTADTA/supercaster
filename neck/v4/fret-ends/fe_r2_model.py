#!/usr/bin/env python3
"""Supercaster II fret ends, round 2: ends that blend into the wood, on an even edge roll.

Builds on fe_model.py (round 1) without changing it: adds one new kind of candidate, 'flow', registers the
round-2 candidates in fe_model.CANDS and teaches fe_model.surface to draw them, so the round-1 contact model,
renderer and checks work on them unchanged. Reads neck_v4.py only. Everything here is a proposal.

The 'flow' end, on the fret centreline, from the board side inward (s) and up (z):
    1. the edge roll: a quarter circle of radius r, the SAME roll at the fret and between frets (an even roll)
    2. a straight face leaving the roll tangentially at the blend angle th (measured from level), wood below
       the board surface and steel above it, one line
    3. an arc of radius rho turning that face over to level at the crown top (full height from there inboard)
Across the fret the face is the crown with a bevel through it and the bevel's edges rounded ('bevel'), or the
crown tapered in plan to a rounded nose ('ogive': half width = crown half width x (height / full height)^p;
p = 0.5 gives a parabola in plan, a round tip).
'wrap' carries the steel on down the roll in a relieved pocket (the wrap-over). Same outer surface.

A hand held flatter than the face (more side-on than 90 - th degrees) touches the roll only: wood, no steel.

Run:  python -I -B fe_r2_model.py            -> geometry checks, writes geometry_r2.json
      python -I -B fe_r2_model.py family     -> the trade table: blend angle and roll radius against bending room
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fe_model as fm  # noqa: E402  (round 1, unchanged)

n4 = fm.n4
HF, CW, FX, NF = fm.HF, fm.CW, fm.FX, fm.NF
S_RAIL1 = 0.140          # the scallop is back to full depth here: under the outer strings
POCKET = 0.014           # depth of the pocket under a wrapped leg (wrap-over only)
RAIL_A = 0.30
RHO_NOSE = 0.020         # the wood crease beside each fret end is broken to this radius


def flow(name, r, th, rho, edge='rail', sig=0.060, across='bevel', k=2.0, p=0.5, wrap=None, rB=None, label=None):
    """r roll radius, th blend angle (deg from level, true angle as a hand sees it), rho top radius.
    edge: 'rail' = no scallop under the roll, rising to full depth under the outer string;
          'dish' = round 1's dished run-out. wrap: None, or the angle (deg) the steel is carried down to."""
    return dict(kind='flow', name=name, label=label or name, r=dict(T=r, B=rB or r), th=th, rho=rho, edge=edge, sig=sig,
                across=across, k=k, p=p, wrap=wrap)


def grade(x):
    """0 at fret 1, 1 at the last fret: for ends that change along the neck."""
    return np.clip((np.asarray(x, float) - FX[1]) / (FX[NF] - FX[1]), 0, 1)


def par(c, key, x, side=None):
    """A candidate's parameter at station x. A pair (a, b) runs from a at fret 1 to b at the last fret."""
    v = c[key]
    if isinstance(v, dict):
        v = v[side]
    if isinstance(v, tuple):
        return v[0] + (v[1] - v[0]) * grade(x)
    return v


# The round-2 candidates. All are rounded in plan ('ogive') except the wrap-over, whose crown has to stay full
# width where it turns over the edge.
FINAL = {
    # (a) wrap-over: the long end's line, the steel carried on down the roll in a pocket to 78 degrees
    'A_wrap': flow('A_wrap', 0.040, 50, 0.040, across='bevel', k=1.2, wrap=78, label='(a) Wrap-over: steel carried down over the roll'),
    'A_twin': flow('A_twin', 0.040, 50, 0.040, across='bevel', k=1.2, label='The wrap-over shape stopped at the board surface (no leg)'),
    # (b) stretched dome on a steep flowing line, at vintage bending room
    'B_dome': flow('B_dome', 0.030, 65, 0.025, across='ogive', label='(b) Stretched dome: 65 deg line, vintage bending room'),
    # (c) the flow end: the same idea, longer and lower
    'C_short': flow('C_short', 0.040, 60, 0.030, across='ogive', label='(c) Flow end, short: 60 deg line'),
    'C_long': flow('C_long', 0.040, 50, 0.040, across='ogive', label='(c) Flow end, long: 50 deg line'),
    'C_graded': flow('C_graded', (0.040, 0.030), (50, 65), (0.040, 0.025), across='ogive',
                     label='(c) Flow end, graded: long at the nut, short at the body'),
}

# Variants used to choose them (fret 12 only in feel_r2.json).
R2 = {
    # (b) the stretched dome: v4's steep flowing line, rounded in plan, on an even roll. Vintage bending room.
    'dome65': flow('dome65', 0.050, 65, 0.015, across='ogive', label='(b) Stretched dome on the v4 line: 65 deg face, rounded in plan'),
    # (c) the flow end, from no cost in bending room to flush at 45 degrees
    'flow60': flow('flow60', 0.040, 60, 0.020, label='(c) Flow end, 60 deg face'),
    'flow55': flow('flow55', 0.040, 55, 0.020, label='(c) Flow end, 55 deg face'),
    'flow50': flow('flow50', 0.040, 50, 0.020, label='(c) Flow end, 50 deg face'),
    'flow45': flow('flow45', 0.040, 45, 0.020, label='(c) Flow end, 45 deg face: flush to a hand at 45'),
    # (a) the wrap-over: the same outer surface as flow50, the steel carried down the roll to 78 degrees
    'wrap50': flow('wrap50', 0.040, 50, 0.020, wrap=78, label='(a) Wrap-over: steel carried down the roll'),
    # design variants used to choose
    'flow65b': flow('flow65b', 0.050, 65, 0.015, label='65 deg face, bevel form'),
    'flow45_r30': flow('flow45_r30', 0.030, 45, 0.020, label='45 deg face on a tighter roll, r 0.030'),
    'flow45_rho40': flow('flow45_rho40', 0.040, 45, 0.040, label='45 deg face, top radius 0.040'),
    'flow50_rho40': flow('flow50_rho40', 0.040, 50, 0.040, label='50 deg face, top radius 0.040'),
    'flow50_og': flow('flow50_og', 0.040, 50, 0.020, across='ogive', label='50 deg face, rounded in plan'),
    'flow50_dish': flow('flow50_dish', 0.040, 50, 0.020, edge='dish', label='50 deg face, dished scallop run-out instead of the rail'),
    'flow50_r55': flow('flow50_r55', 0.055, 50, 0.020, label='50 deg face on a bigger roll, r 0.055'),
    'flow55_rho35': flow('flow55_rho35', 0.040, 55, 0.035, label='55 deg face, top radius 0.035'),
    'flow50_k4': flow('flow50_k4', 0.040, 50, 0.020, k=4.0, label='50 deg face, crisper bevel edges'),
    'flow50_k1': flow('flow50_k1', 0.040, 50, 0.020, k=1.2, label='50 deg face, rounder bevel edges'),
    'og60p': flow('og60p', 0.036, 60, 0.012, across='ogive', label='ogive, 60 deg, r 0.036, top radius 0.012'),
    'og60': flow('og60', 0.040, 60, 0.020, across='ogive', label='ogive, 60 deg'),
    'og55': flow('og55', 0.040, 55, 0.020, across='ogive', label='ogive, 55 deg'),
    'og55s': flow('og55s', 0.040, 55, 0.012, across='ogive', label='ogive, 55 deg, top radius 0.012'),
    'og50s': flow('og50s', 0.040, 50, 0.012, across='ogive', label='ogive, 50 deg, top radius 0.012'),
    'og45': flow('og45', 0.040, 45, 0.020, across='ogive', label='ogive, 45 deg'),
    'og45s': flow('og45s', 0.040, 45, 0.012, across='ogive', label='ogive, 45 deg, top radius 0.012'),
    'og50_p5': flow('og50_p5', 0.040, 50, 0.020, across='ogive', p=0.40, label='ogive 50, blunter plan'),
    'og50_p6': flow('og50_p6', 0.040, 50, 0.020, across='ogive', p=0.60, label='ogive 50, slightly pointed plan'),
    'og50_p8': flow('og50_p8', 0.040, 50, 0.020, across='ogive', p=0.8, label='ogive 50, sharper plan'),
    'og50_r50': flow('og50_r50', 0.050, 50, 0.020, across='ogive', label='ogive 50 on r 0.050'),
    'og55_r50': flow('og55_r50', 0.050, 55, 0.012, across='ogive', label='ogive 55 on r 0.050, top radius 0.012'),
    'og72': flow('og72', 0.060, 72, 0.012, across='ogive', label='ogive on the v4 72 deg line, r 0.060'),
    'og60_r30': flow('og60_r30', 0.030, 60, 0.020, across='ogive', label='ogive 60 on r 0.030'),
    'og55_r30': flow('og55_r30', 0.030, 55, 0.020, across='ogive', label='ogive 55 on r 0.030'),
    'og50_r30': flow('og50_r30', 0.030, 50, 0.020, across='ogive', label='ogive 50 on r 0.030'),
    'og45_r30': flow('og45_r30', 0.030, 45, 0.020, across='ogive', label='ogive 45 on r 0.030'),
    'og60_rho30': flow('og60_rho30', 0.040, 60, 0.030, across='ogive', label='ogive 60, top radius 0.030'),
    'og55_rho30': flow('og55_rho30', 0.040, 55, 0.030, across='ogive', label='ogive 55, top radius 0.030'),
    'og50_rho30': flow('og50_rho30', 0.040, 50, 0.030, across='ogive', label='ogive 50, top radius 0.030'),
    'og50_rho40': flow('og50_rho40', 0.040, 50, 0.040, across='ogive', label='ogive 50, top radius 0.040'),
    'og65_rho30': flow('og65_rho30', 0.040, 65, 0.030, across='ogive', label='ogive 65, top radius 0.030'),
    'og65_r30': flow('og65_r30', 0.030, 65, 0.025, across='ogive', label='ogive 65 on r 0.030, top radius 0.025'),
    'flow50_og1': flow('flow50_og1', 0.040, 50, 0.020, across='ogive', p=1.0, label='50 deg face, pointed in plan'),
}
R2.update(FINAL)
fm.CANDS.update(R2)


# ------------------------------------------------------------------------------------------ profile ----
def tilt(x, side):
    """Slope of the board surface at the edge (the radius makes the land rise about 7 degrees going inboard)."""
    return (n4.board(x, fm.side_y(x, 0.04, side)) - n4.board(x, fm.side_y(x, 0.0, side))) / 0.04


def local_angle(th_deg, t):
    """Blend angle measured from the land, for a true (as the hand sees it) angle th_deg."""
    return np.arctan(np.tan(np.radians(th_deg)) - t)


def prof_pts(r, thl, rho):
    """Seam on the roll (sb, zb), start of the top arc (sa, za), full-height point, toe of the steel (z = 0)."""
    sb = r * (1 - np.sin(thl))
    zb = -r * (1 - np.cos(thl))
    za = HF - rho * (1 - np.cos(thl))
    sa = sb + (za - zb) / np.tan(thl)
    sfull = sa + rho * np.sin(thl)
    s0 = sb - zb / np.tan(thl)
    return sb, zb, sa, za, sfull, s0


def prof(s, r, thl, rho):
    """Centreline profile E(s) and the plain roll, both as height above the land (local frame)."""
    sb, zb, sa, za, sfull, s0 = prof_pts(r, thl, rho)
    s = np.clip(s, 0, None)
    roll = np.where(s < r, -r + np.sqrt(np.clip(r * r - (r - s) ** 2, 0, None)), 0.0)
    line = zb + (s - sb) * np.tan(thl)
    arc = HF - rho + np.sqrt(np.clip(rho * rho - (sfull - s) ** 2, 0, None))
    E = np.where(s < sb, roll, np.where(s < sa, line, np.where(s < sfull, arc, HF)))
    return E, roll


def scallop(x, y, s, edge, r):
    g, kc = n4.cell_g(x)
    W = n4.width(x)
    dep = n4.DK[kc] * g * (1 - n4.P['tilt'] * (y / W + 0.5))
    if edge == 'rail':
        # level under the roll, then over a rounded shoulder (the first 30 %) and down a long hollow to full depth:
        # the hollow is kept wide so a 1/8 ball-nose can cut it
        u = np.clip((s - r) / (S_RAIL1 - r), 0, 1)
        return dep * np.where(u < RAIL_A, u * u / RAIL_A, 1 - (1 - u) ** 2 / (1 - RAIL_A))
    return dep * (1 - (np.clip(fm.S_DISH - s, 0, None) / fm.S_DISH) ** 2)


def leg_mask(xi, ss, r, thl, rho, c, t):
    """Wrap-over only: plan outline of the steel leg lying on the roll, a tongue with a rounded tip."""
    sb, zb, sa, za, sfull, s0 = prof_pts(r, thl, rho)
    sw = r * (1 - np.sin(local_angle(c['wrap'], t)))
    f = np.clip((s0 - ss) / (s0 - sw), 0, 1)
    return (ss >= sw) & (ss < s0) & (np.abs(xi) < CW * np.sqrt(np.clip(1 - f ** 4, 0, None)))


def flow_parts(x, s, side, c, steel_shift=0.0):
    """Wood, crown steel (nan where none), leg mask and leg surface. Absolute z."""
    x, s = np.broadcast_arrays(np.asarray(x, float), np.asarray(s, float))
    r, rho = par(c, 'r', x, side), par(c, 'rho', x)
    t = tilt(x, side)
    thl = local_angle(par(c, 'th', x), t)
    y = fm.side_y(x, s, side)
    land = n4.board(x, y)
    xf, nf = n4.nearest_fret(x)
    xi = x - xf
    E, roll = prof(s, r, thl, rho)
    # the wood that carries the face. Under the steel the face meets the land in a crease the steel covers;
    # beside the fret that crease is broken to a radius that grows to RHO_NOSE within about 0.02 of the fret
    sb, zb, sa, za, sfull, s0 = prof_pts(r, thl, rho)
    if c['across'] == 'ogive':
        # a rounded-plan end covers the crease only at its tip: everything the steel does not sit on is eased
        with np.errstate(invalid='ignore'):
            rn = 0.9 * HF * np.clip(np.abs(xi) / CW, 0, 1) ** (1 / c['p']) / (np.tan(thl) * np.tan(thl / 2))
        rn = np.minimum(RHO_NOSE, rn) + 1e-6
    else:
        rn = RHO_NOSE * (1 - np.exp(-(np.clip(np.abs(xi) - CW, 0, None) / 0.012) ** 2)) + 1e-6
    half = rn * np.tan(thl / 2)
    arc = -rn + np.sqrt(np.clip(rn * rn - (s0 + half - s) ** 2, 0, None))
    nose = np.where(s < s0 - half * np.cos(thl), np.minimum(E, 0.0), np.where(s < s0 + half, arc, 0.0))
    nose = np.maximum(np.minimum(nose, np.minimum(E, 0.0)), roll)
    w = fm.bell(x, c['sig'], CW + 0.004)                    # 0 across the whole fret, 1 between frets
    w = np.where(nf >= 1, w, 1.0)
    wood = land + roll + (nose - roll) * (1 - w) - scallop(x, y, s, c['edge'], r) * n4.fq(s / r)
    ss = s + steel_shift
    Es, _ = prof(ss, r, thl, rho)
    v = np.clip(Es, 0, HF) / HF
    u = xi / CW
    with np.errstate(invalid='ignore', divide='ignore'):
        if c['across'] == 'ogive':
            G = v * np.sqrt(np.clip(1 - (u / np.clip(v, 1e-9, None) ** c['p']) ** 2, 0, None))
        else:
            cr = np.sqrt(np.clip(1 - u * u, 0, None))
            k = c['k']
            G = cr * v / np.clip(cr ** k + v ** k - (cr * v) ** k, 1e-30, None) ** (1 / k)
    steel = (G > 0) & (nf >= 1)
    zs = np.where(steel, n4.board(x, fm.side_y(x, ss, side)) + HF * G, np.nan)
    if c['wrap']:
        leg = leg_mask(xi, ss, r, thl, rho, c, t) & (nf >= 1)
        zleg = n4.board(x, fm.side_y(x, ss, side)) + np.minimum(Es, 0.0)
    else:
        leg, zleg = np.zeros(x.shape, bool), None
    return wood, zs, leg, zleg


_surface_r1 = fm.surface


def surface(x, s, side, c, steel_shift=0.0):
    """Finished surface seen from above: z (absolute), steel mask, wood z. Round-1 kinds pass straight through."""
    if c['kind'] != 'flow':
        return _surface_r1(x, s, side, c, steel_shift)
    wood, zs, leg, zleg = flow_parts(x, s, side, c, steel_shift)
    steel = np.nan_to_num(zs, nan=-np.inf) > wood
    z = np.where(steel, zs, wood)
    if c['wrap']:
        z = np.where(leg, zleg, z)
        wood = np.where(leg, np.minimum(wood, zleg) - POCKET, wood)        # the pocket the leg lies in
        steel = steel | leg
    return z, steel, wood


fm.surface = surface


# -------------------------------------------------------------------------------------------- checks ----
def numbers(c, side='T', n=12):
    """The profile in plain numbers at fret n."""
    x = float(FX[n])
    t = float(tilt(x, side))
    th, rho = float(par(c, 'th', x)), float(par(c, 'rho', x))
    thl = float(local_angle(th, t))
    r = float(par(c, 'r', x, side))
    sb, zb, sa, za, sfull, s0 = [float(v) for v in prof_pts(r, thl, rho)]
    out = dict(roll_radius=r, blend_angle=th, top_radius=rho, land_tilt_deg=math.degrees(math.atan(t)), seam_from_side=s0,
               roll_tangent_from_side=sb, roll_tangent_below_land=-zb, nose_height=float(-prof(np.array(s0), r, thl, rho)[1]),
               face_length=float(math.hypot(sa - sb, za - zb)), steel_face_length=float(math.hypot(sa - s0, za)),
               full_from_side=sfull, hidden_below_deg=90 - th, crown_overhang_past_tang=0.085 - s0)
    if c['wrap']:
        sw = float(r * (1 - np.sin(local_angle(c['wrap'], t))))
        a0, a1 = thl, float(local_angle(c['wrap'], t))
        out.update(leg_end_from_side=sw, leg_length=float(r * (a1 - a0) + math.hypot(s0 - sb, zb)), leg_turn_deg=math.degrees(a1 - a0))
    return out


def support_gap(c, side, n=12):
    """Largest air gap under the flat underside of the crown (nominal fit)."""
    xf = FX[n]
    X, Sg = np.meshgrid(xf + np.linspace(-CW, CW, 161), np.linspace(0, 0.12, 961), indexing='ij')
    wood, zs, leg, zleg = flow_parts(X, Sg, side, c)
    land = n4.board(X, fm.side_y(X, Sg, side))
    return float(np.max(np.where(np.isfinite(zs), land - wood, 0.0)))


def slope_at(c, side, n, s_list):
    """Slope of the crown ridge (deg, falling toward the side) at given distances from the side."""
    x = FX[n]
    s = np.linspace(0, 0.16, 16001)
    z, steel, wood = fm.surface(np.full_like(s, x), s, side, c)
    lost = n4.board(x, fm.side_y(x, s, side)) + HF - z
    sl = np.degrees(np.arctan(-np.gradient(lost, s)))
    return {('%.3f' % q): (round(float(np.interp(q, s, sl)), 1), round(float(np.interp(q, s, lost)), 4)) for q in s_list}


def step_shift(c, side, phi, shift):
    return fm.protrusion(c, side, phi, steel_shift=shift)['step']


def family():
    """Blend angle and roll radius against where full height starts (and so against bending room)."""
    x = float(FX[12])
    t = float(tilt(x, 'T'))
    print('full height starts this far from the side (fret 12; vintage-equal room is 0.049). top radius 0.020')
    print('  blend   hidden below   ' + ''.join('r %.3f   ' % r for r in (0.030, 0.040, 0.050, 0.060)))
    for th in (45, 50, 55, 60, 65, 72):
        row = [float(prof_pts(r, local_angle(th, t), 0.020)[4]) for r in (0.030, 0.040, 0.050, 0.060)]
        print('  %2d deg    %2d deg      ' % (th, 90 - th) + ''.join('%.4f    ' % v for v in row))


CORE = ['vintage', 'v4', 'rec'] + list(FINAL)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'family':
        family()
        sys.exit()
    names = [a for a in sys.argv[1:] if a in fm.CANDS] or CORE
    out = dict(margins={}, protrusion={}, sharpest={}, numbers={}, gap={}, shift_step={}, slope={}, machinable={})
    for k in names:
        c = fm.CANDS[k]
        out['margins'][k] = fm.margins(c)
        out['protrusion'][k] = {sd: {str(p): fm.protrusion(c, sd, p) for p in (20, 30, 45, 60, 70)} for sd in 'TB'}
        out['sharpest'][k] = {sd: fm.sharpest(c, sd) for sd in 'TB'}
        out['shift_step'][k] = {sd: {'%+d' % round(sh * 1000): {str(p): step_shift(c, sd, p, sh) for p in (20, 30, 45, 60)}
                                     for sh in (0.004, -0.004, -0.008)} for sd in 'T'}
        out['wave20'] = out.get('wave20', {})
        m = out['margins'][k]['fret_12']
        pr = out['protrusion'][k]['T']
        print('%-13s toe %.4f full %.4f | room T %.4f B %.4f usable %.4f hold %.4f | step 20/30/45/60/70 %.4f %.4f %.4f %.4f %.4f | wood wave 45 T %.4f B %.4f | R steel %.4f wood %.4f'
              % (k, m['T']['toe'], m['T']['full_from_side'], m['T']['to_full'], m['B']['to_full'], m['T']['to_usable'], m['T']['to_hold'],
                 pr['20']['step'], pr['30']['step'], pr['45']['step'], pr['60']['step'], pr['70']['step'], pr['45']['wood_wave'],
                 out['protrusion'][k]['B']['45']['wood_wave'], out['sharpest'][k]['T']['steel'], out['sharpest'][k]['T']['wood']), flush=True)
        if c['kind'] == 'flow':
            out['numbers'][k] = {sd: {('fret_%d' % n): numbers(c, sd, n) for n in (1, 12, 21)} for sd in 'TB'}
            out['gap'][k] = {sd: support_gap(c, sd) for sd in 'TB'}
            out['slope'][k] = {('fret_%d' % n): slope_at(c, 'T', n, [0.030, 0.040, 0.050, 0.060, 0.070, 0.080]) for n in (1, 12, 21)}
            sh = out['shift_step'][k]['T']
            print('              seam %.4f from side, gap under crown %.5f | step at 45 when the board shrinks 0.004: %.4f, swells 0.004: %.4f'
                  % (out['numbers'][k]['T']['fret_12']['seam_from_side'], out['gap'][k]['T'], sh['+4']['45'], sh['-4']['45']), flush=True)
    if 'nomach' not in sys.argv:
        for k in [n for n in names if fm.CANDS[n]['kind'] == 'flow']:
            out['machinable'][k] = {sd: {('fret_%d' % n): fm.ball_nose_check(fm.CANDS[k], sd, n, r=0.0625, h=0.002, span=0.3) for n in (2, 12, 21)} for sd in 'TB'}
            print(k, 'left uncut by a 1/8 ball-nose:', {sd: round(max(v['max_uncut'] for v in out['machinable'][k][sd].values()), 5) for sd in 'TB'}, flush=True)
    if names == CORE:
        json.dump(out, open(os.path.join(HERE, 'geometry_r2.json'), 'w'), indent=1)
        print('wrote geometry_r2.json')
