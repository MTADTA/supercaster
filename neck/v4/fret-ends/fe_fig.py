#!/usr/bin/env python3
"""Supercaster II fret ends: drawings and charts, from the same surfaces and numbers as the report.

Run:  python -I -B fe_fig.py                 -> every figure in fig/
      python -I -B fe_fig.py sections        -> one of: sections feel room wave maps trade summary
Needs geometry.json (fe_model.py) and feel.json (fe_contact.py). 'summary' also renders (fe_render.py).
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fe_model as fm  # noqa: E402

n4 = fm.n4
FX, HF, CW = fm.FX, fm.HF, fm.CW
FIG = os.path.join(HERE, 'fig')
os.makedirs(FIG, exist_ok=True)

INK, INK2, MUTED, GRID, SURF = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#fcfcfb'
COL = dict(vintage='#2a78d6', v4='#eb6834', rec='#1baf7a', fallback='#eda100', uniform='#e87ba4')
NAME = dict(vintage='Vintage bevel', v4='v4: 72° face', rec='Proposed: quarter-sphere', fallback='Fallback: filed dome',
            uniform='Dome set inboard')
ROSE, MAPLE, STEEL, SLOT, TANG = '#7d5140', '#e2c79c', '#b4b9c0', '#3d261d', '#d9dce0'
END_NOTE = dict(vintage='35° bevel', v4='72° face,\nridge radius 0.015', rec='radius 0.040', fallback='dome 0.034 long')
TANG_END = dict(vintage=0.0, v4=0.080, rec=0.085, fallback=0.085)       # tang end, from the board side
SLOT_END = dict(vintage=0.0, v4=0.075, rec=0.075, fallback=0.075)
SCEN = [('index_side', 'Index finger side,\nsliding, hand low'), ('index_45', 'Index finger side,\nsliding, 45°'),
        ('tip_slide', 'Fingertip sliding\nalong the high E'), ('tip_above', 'Fingertip landing\non a fret end'),
        ('thumb_45', 'Thumb sliding,\nbass edge, 45°'), ('thumb_over', 'Thumb wrapped over,\ngripping')]

plt.rcParams.update({'font.family': 'Helvetica', 'font.size': 10, 'axes.edgecolor': '#c3c2b7', 'axes.labelcolor': INK2,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'text.color': INK, 'figure.facecolor': SURF,
                     'axes.facecolor': SURF, 'savefig.facecolor': SURF, 'axes.spines.top': False, 'axes.spines.right': False})


def _geo():
    return json.load(open(os.path.join(HERE, 'geometry.json')))


def _feel():
    return json.load(open(os.path.join(HERE, 'feel.json')))


def _profile(key, side, n):
    if key == 'vintage':
        return fm.vintage_profile()
    return fm.end_profile(n, side, fm.CANDS[key])


def _string_to_side(key, side, n):
    return fm.margins(fm.CANDS[key])['fret_%d' % n][side]['string_to_side']


def _bare(ax, x0, x1, y0, y1):
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


def _scalebar(ax, x, y, length=0.050):
    ax.plot([x, x + length], [y, y], color=INK, lw=2.0, solid_capstyle='butt')
    ax.text(x + length / 2, y + 0.004, '0.050 in', ha='center', va='bottom', fontsize=8, color=INK)


def _dim(ax, a, b, y, text, fs=8.5, dy=0.0035, color=INK):
    ax.annotate('', xy=(a, y), xytext=(b, y), arrowprops=dict(arrowstyle='<->', color=color, lw=0.8, shrinkA=0, shrinkB=0))
    ax.text((a + b) / 2, y + dy, text, ha='center', va='bottom', fontsize=fs, color=color)


def _wood_fill(ax, u, wood, glue, bottom):
    ax.fill_between(u, bottom, wood, color=MAPLE, lw=0)
    ax.fill_between(u, np.minimum(glue, wood), wood, color=ROSE, lw=0)
    ax.plot(u, wood, color=INK, lw=0.9)


# ------------------------------------------------------------------------------------------ sections ----
def sec_along(ax, key, side='T', n=12, labels=True, frame=(-0.075, 0.170, -0.125, 0.085)):
    """Section along the fret, through its centreline. Left is outboard; the board side is at 0."""
    c = fm.CANDS[key]
    x = float(FX[n])
    s = np.linspace(0, frame[1], 4301)
    z, st, wood = fm.rel(np.full_like(s, x), s, side, c)
    cz = float(fm.corner_z(x))
    y = fm.side_y(x, s, side)
    land = n4.board(x, y) - cz
    glue = n4.glue(x, y) - cz
    _bare(ax, *frame)
    _wood_fill(ax, s, wood, glue, frame[2])
    ax.plot([0, 0], [frame[2], wood[0]], color=INK, lw=0.9)
    # the wood midway to the next fret, to show how far the edge rises to meet the end
    xm = float((FX[n] + FX[n + 1]) / 2)
    _, _, wm = fm.rel(np.full_like(s, xm), s, side, c)
    ax.plot(s, wm, color='white', lw=1.0, ls=(0, (4, 3)))
    # blind slot and tang
    se, te = SLOT_END[key], TANG_END[key]
    sl = s >= se
    ax.fill_between(s[sl], land[sl] - (n4.P['tang_depth'] + n4.P['slot_extra']), land[sl], color=SLOT, lw=0)
    tg = s >= te
    ax.fill_between(s[tg], land[tg] - n4.P['tang_depth'], land[tg], color=TANG, lw=0)
    ax.text(frame[1] - 0.004, float(land[-1]) - 0.026, 'tang', fontsize=8, ha='right', va='center', color=INK2)
    # crown
    i = np.where(st)[0]
    poly = np.concatenate([np.c_[s[i], z[i]], np.c_[s[i][::-1], land[i][::-1]]])
    ax.add_patch(Polygon(poly, closed=True, facecolor=STEEL, edgecolor=INK, lw=0.9, zorder=3))
    # string 1 (or 6) at rest
    e = _string_to_side(key, side, n)
    dia = 0.010 if side == 'T' else 0.046
    le = float(n4.board(x, fm.side_y(x, e, side)) - cz)
    if e < frame[1] - dia:
        ax.add_patch(Circle((e, le + HF + dia / 2), dia / 2, facecolor='#e9b44c', edgecolor=INK, lw=0.7, zorder=4))
    p = _profile(key, side, n)
    if labels:
        top = float(np.interp(p['full'], s, land)) + HF
        ax.plot([p['full'], p['full']], [top, 0.071], color=INK2, lw=0.6)
        ax.plot([0, 0], [wood[0], 0.071], color=INK2, lw=0.6)
        if e < frame[1] - dia:
            ax.plot([e, e], [le + HF + dia, 0.071], color=INK2, lw=0.6)
            _dim(ax, p['full'], e, 0.066, '%.3f full-height fret outside the string' % (e - p['full']))
        ax.annotate('', xy=(0, 0.066), xytext=(p['full'], 0.066), arrowprops=dict(arrowstyle='<->', color=INK, lw=0.8, shrinkA=0, shrinkB=0))
        ax.text(-0.004, 0.066, '%.3f' % p['full'], ha='right', va='center', fontsize=8.5)
        if p['toe'] > 0.002:
            ax.annotate('steel starts\n%.3f in,\n%s' % (p['toe'], END_NOTE[key]), xy=(p['toe'], float(np.interp(p['toe'], s, land))),
                        xytext=(-0.072, 0.030), fontsize=8.5, color=INK, va='center',
                        arrowprops=dict(arrowstyle='-', color=INK2, lw=0.6, relpos=(1.0, 0.3)))
        else:
            ax.text(-0.072, 0.030, 'steel flush\nwith the side,\n%s' % END_NOTE[key], fontsize=8.5, va='center')
        ax.text(frame[1] - 0.004, frame[2] + 0.008, 'white dashes: the wood midway to the next fret', fontsize=7.5,
                ha='right', color='#3a2a22')
        _scalebar(ax, -0.068, frame[2] + 0.010)


def sec_across(ax, key, side='T', n=12, s0=0.020, frame=(-0.17, 0.17, -0.125, 0.085)):
    """Section across the fret (looking in from the side), s0 in from the board side, with slices further in."""
    c = fm.CANDS[key]
    x = float(FX[n])
    xi = np.linspace(frame[0], frame[1], 3401)
    cz = fm.corner_z(x + xi)
    z, st, wood = fm.rel(x + xi, np.full_like(xi, s0), side, c)
    y = fm.side_y(x + xi, s0, side)
    land = n4.board(x + xi, y) - cz
    glue = n4.glue(x + xi, y) - cz
    _bare(ax, *frame)
    _wood_fill(ax, xi, wood, glue, frame[2])
    # slot and tang, which begin further in
    l0 = float(np.interp(0, xi, land))
    ax.add_patch(Rectangle((-0.0115, l0 - 0.058), 0.023, 0.058, facecolor='none', edgecolor='white', lw=0.7, ls=(0, (3, 2))))
    # slices of the steel: s0 filled, others as lines
    i = np.where(st)[0]
    if len(i):
        poly = np.concatenate([np.c_[xi[i], z[i]], np.c_[xi[i][::-1], land[i][::-1]]])
        ax.add_patch(Polygon(poly, closed=True, facecolor=STEEL, edgecolor=INK, lw=0.9, zorder=3))
    for sk, ls in ((0.012, ':'), (0.030, '--'), (0.060, '-')):
        zk, stk, _ = fm.rel(x + xi, np.full_like(xi, sk), side, c)
        lk = n4.board(x + xi, fm.side_y(x + xi, sk, side)) - cz
        j = np.where(stk)[0]
        if len(j):
            ax.plot(xi[j], (zk - lk + land)[j], color=INK, lw=0.8, ls=ls, zorder=4)
    ax.text(frame[0] + 0.006, 0.074, 'filled: %.3f in from the side\nlines: 0.012 (dots), 0.030 (dashes), 0.060 (full crown)' % s0,
            fontsize=7.5, va='top')
    ax.text(0.016, l0 - 0.052, 'slot 0.023, further in', fontsize=7.5, color='white', va='center')
    _scalebar(ax, frame[0] + 0.008, frame[2] + 0.010)


def plan(ax, key, side='T', n=12, frame=(-0.17, 0.17, -0.015, 0.195)):
    """From straight above: height lines every 0.010, steel shaded."""
    c = fm.CANDS[key]
    x = float(FX[n])
    xi = np.linspace(frame[0], frame[1], 681)
    s = np.linspace(0, frame[3], 421)
    XI, S = np.meshgrid(xi, s, indexing='ij')
    z, st, wood = fm.rel(x + XI, S, side, c)
    land = n4.board(x + XI, fm.side_y(x + XI, S, side)) - fm.corner_z(x + XI)
    _bare(ax, *frame)
    ax.add_patch(Rectangle((frame[0], 0), frame[1] - frame[0], frame[3], facecolor=ROSE, edgecolor='none'))
    ax.contourf(XI, S, st.astype(float), levels=[0.5, 1.5], colors=[STEEL])
    ax.contour(XI, S, np.where(st, np.nan, wood - land), levels=np.arange(-0.105, -0.004, 0.010), colors='white', linewidths=0.55,
               linestyles='solid')
    ax.contour(XI, S, np.where(st, z - land, np.nan), levels=np.arange(0.005, 0.045, 0.010), colors=INK, linewidths=0.55)
    ax.contour(XI, S, st.astype(float), levels=[0.5], colors=INK, linewidths=0.9)
    ax.plot([frame[0], frame[1]], [0, 0], color=INK, lw=1.4)
    e = _string_to_side(key, side, n)
    if e < frame[3]:
        ax.plot([frame[0], frame[1]], [e, e], color='#e9b44c', lw=1.6)
        ax.text(frame[1] - 0.004, e + 0.004, 'string at rest', fontsize=7.5, ha='right', color='white')
    p = _profile(key, side, n)
    ax.plot([-0.07, 0.07], [p['full'], p['full']], color=INK, lw=0.7, ls=(0, (2, 2)))
    ax.text(0.074, p['full'], 'full height from here in', fontsize=7.5, va='center', color='white')
    ax.text(frame[0] + 0.004, -0.004, 'board side', fontsize=7.5, va='top')
    ax.text(frame[0] + 0.006, frame[3] - 0.006, 'lines every 0.010: white = wood below\nthe plain board, black = steel above it', fontsize=7.5, va='top', color='white')
    _scalebar(ax, frame[1] - 0.062, -0.012)


def fig_sections(side='T', n=12, fname=None, keys=('vintage', 'v4', 'rec')):
    K = 17.0                                    # drawing inches per real inch, the same in every panel
    wA, wB, wC, h = 0.245 * K, 0.34 * K, 0.34 * K, 0.21 * K
    gap, left, topm, rowgap, bot = 0.45, 0.35, 1.35, 0.55, 0.3
    Wf = left * 2 + wA + wB + wC + 2 * gap
    Hf = topm + len(keys) * h + (len(keys) - 1) * rowgap + bot
    fig = plt.figure(figsize=(Wf, Hf))
    sn = 'treble' if side == 'T' else 'bass'
    fig.text(left / Wf, 1 - 0.42 / Hf, 'Fret end at fret %d, %s side, drawn to scale (%d times full size as saved)' % (n, sn, round(K)),
             fontsize=17, weight='bold')
    fig.text(left / Wf, 1 - 0.78 / Hf, 'Rosewood dark, maple light, steel grey. Every panel is at the same scale; the bar is 0.050 in.',
             fontsize=11, color=INK2)
    heads = ['cut along the fret', 'Cut across the fret, seen from the side of the neck', 'From straight above']
    for r, key in enumerate(keys):
        y0 = (bot + (len(keys) - 1 - r) * (h + rowgap)) / Hf
        x0 = left
        for q, (w, fn) in enumerate(((wA, sec_along), (wB, sec_across), (wC, plan))):
            ax = fig.add_axes([x0 / Wf, y0, w / Wf, h / Hf])
            fn(ax, key, side, n)
            ax.set_title(('%s  |  ' % NAME[key] if q == 0 else '') + heads[q], fontsize=10.5, loc='left', pad=4,
                         weight='bold' if q == 0 else 'normal')
            x0 += w + gap
    fname = fname or 'sections_%s_fret_%d.png' % (sn, n)
    fig.savefig(os.path.join(FIG, fname), dpi=110)
    plt.close(fig)
    return fname


# ---------------------------------------------------------------------------------------------- feel ----
def fig_feel(fret='fret_12', keys=('vintage', 'v4', 'rec', 'fallback', 'uniform')):
    F = _feel()['feel']
    rows = [('peak', 'Hardest spot under the skin\n(times the same touch on a flat board)', '%.1f'),
            ('catch_deg', 'Catch: how hard the edge\npushes back along the neck (degrees)', '%.0f'),
            ('lift', 'Rise and fall of the finger\nalong the edge (thousandths)', '%.0f')]
    fig, axs = plt.subplots(3, 6, figsize=(19, 9.6), sharey=True)
    fig.subplots_adjust(left=0.115, right=0.985, top=0.79, bottom=0.04, wspace=0.10, hspace=0.34)
    yy = np.arange(len(keys))[::-1]
    for r, (m, lab, fmt) in enumerate(rows):
        vmax = max(F[k][fret][s][m] * (1000 if m == 'lift' else 1) for k in keys for s, _ in SCEN)
        for q, (s, title) in enumerate(SCEN):
            ax = axs[r, q]
            vals = [F[k][fret][s][m] * (1000 if m == 'lift' else 1) for k in keys]
            ax.barh(yy, vals, height=0.62, color=[COL[k] for k in keys], edgecolor=SURF, linewidth=1.5)
            for yv, v, k in zip(yy, vals, keys):
                t = fmt % v
                if m == 'peak':
                    t += '  ' + F[k][fret][s]['on']
                ax.text(v + vmax * 0.02, yv, t, va='center', fontsize=8.5, color=INK)
            ax.set_xlim(0, vmax * 1.32)
            ax.set_yticks(yy)
            ax.set_yticklabels([NAME[k] for k in keys], fontsize=9.5, color=INK)
            ax.tick_params(length=0)
            ax.set_xticks([])
            ax.spines['bottom'].set_visible(False)
            if r == 0:
                ax.set_title(title, fontsize=10.5, loc='left', pad=27, color=INK2)
        fig.text(0.008, axs[r, 0].get_position().y1 + 0.008, lab.replace('\n', ' '), fontsize=11, weight='bold', va='bottom')
    fig.text(0.008, 0.955, 'What the hand feels at the fret ends, %s: shorter bars are better in every row' % fret.replace('_', ' '),
             fontsize=17, weight='bold')
    fig.text(0.008, 0.918, 'Computed: a soft finger pressed on each edge and slid past the fret. "steel" or "wood" says which one '
             'makes the hardest spot. The proposal keeps vintage bending room; "dome set inboard" gives up 0.042.',
             fontsize=11, color=INK2)
    fig.text(0.008, 0.893, 'v4 is modelled as drawn. Its spec asks for the wood corner beside each fret to be broken by hand; '
             'done well, that brings its two "wood" bars down to its steel values, %.1f and %.1f.'
             % (F['v4'][fret]['index_side']['peak_steel'], F['v4'][fret]['tip_above']['peak_steel']), fontsize=11, color=INK2)
    fig.savefig(os.path.join(FIG, 'feel_%s.png' % fret), dpi=110)
    plt.close(fig)
    return 'feel_%s.png' % fret


def fig_trade():
    """What a softer end costs: fret given up against the hardest spot."""
    F, G = _feel()['feel'], _geo()['margins']
    pts = [('vintage', 'Vintage bevel\n(on a vintage-width neck)'), ('v4', 'v4 face'), ('short', 'Short dome 0.026'),
           ('mid', 'Filed dome 0.034\n(fallback)'), ('bullet', 'Quarter-sphere 0.040\n(proposed)'),
           ('bullet_t016', 'Quarter-sphere,\nset in 0.006 more'), ('long', 'Long dome 0.052'), ('uniform', 'Dome set\ninboard')]
    tre = ['index_side', 'index_45', 'tip_slide', 'tip_above']
    fig, ax = plt.subplots(figsize=(11, 6.6))
    fig.subplots_adjust(left=0.085, right=0.97, top=0.82, bottom=0.12)
    ref = G['vintage']['fret_12']['T']['to_full']
    for k, lab in pts:
        xv = (G[k]['fret_12']['T']['to_full'] - ref) * 1000
        yv = float(np.mean([F[k]['fret_12'][s]['peak'] for s in tre]))
        col = COL.get({'bullet': 'rec', 'mid': 'fallback'}.get(k, k), MUTED)
        ax.plot([xv], [yv], 'o', ms=10, color=col, mec=SURF, mew=2)
        dx, dyv, ha = {'vintage': (-1.0, 0.0, 'right'), 'mid': (-1.0, 0.16, 'right'), 'short': (1.0, 0.14, 'left'),
                       'bullet': (1.0, -0.20, 'left'), 'bullet_t016': (0.0, -0.33, 'center'), 'long': (-1.0, 0.0, 'right')}.get(k, (1.0, 0.0, 'left'))
        ax.text(xv + dx, yv + dyv, lab, fontsize=9.5, va='center', ha=ha)
    ax.axvline(0, color='#c3c2b7', lw=1)
    ax.set_xlim(-48, 9)
    ax.set_ylim(3.2, 7.6)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_xlabel('Full-height fret outside the high E at fret 12, compared with a vintage neck (thousandths; negative = less bending room)')
    ax.set_ylabel('Hardest spot, mean of the four treble-edge touches (times flat)')
    fig.text(0.02, 0.94, 'What a softer fret end costs in bending room', fontsize=16, weight='bold')
    fig.text(0.02, 0.89, 'Lower is softer. Everything on the grey line keeps vintage bending room; only moving the steel inboard goes further.',
             fontsize=10.5, color=INK2)
    fig.savefig(os.path.join(FIG, 'trade_softness_vs_room.png'), dpi=120)
    plt.close(fig)
    return 'trade_softness_vs_room.png'


# --------------------------------------------------------------------------------------- bending room ----
def fig_room(keys=('vintage', 'v4', 'rec')):
    G = _geo()['margins']
    rows = [('fret_%d' % n, sd) for n in (1, 12, 21) for sd in 'TB']
    fig, axs = plt.subplots(1, 2, figsize=(13.5, 6.4), sharey=True)
    fig.subplots_adjust(left=0.13, right=0.98, top=0.80, bottom=0.10, wspace=0.08)
    hgt = 0.25
    for ax, m, title in ((axs[0], 'to_full', 'String centre to where the fret reaches full height'),
                         (axs[1], 'to_usable', 'String centre to where the fret is within 0.005 of full height')):
        for i, (fr, sd) in enumerate(rows):
            for j, k in enumerate(keys):
                v = G[k][fr][sd][m] * 1000
                yv = -i + (1 - j) * hgt
                ax.barh(yv, v, height=hgt * 0.86, color=COL[k], edgecolor=SURF, linewidth=1.2)
                ax.text(v + 1.2, yv, '%.0f' % v, va='center', fontsize=8.5)
        ax.set_yticks([-i for i in range(len(rows))])
        ax.set_yticklabels(['Fret %s, %s' % (fr.split('_')[1], 'high E' if sd == 'T' else 'low E') for fr, sd in rows], fontsize=10, color=INK)
        ax.tick_params(length=0)
        ax.set_xlim(0, 135)
        ax.grid(axis='x', color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        ax.set_title(title, fontsize=11, loc='left')
        ax.set_xlabel('thousandths of an inch')
        ax.spines['left'].set_visible(False)
    hs = [Rectangle((0, 0), 1, 1, color=COL[k]) for k in keys]
    fig.legend(hs, ['Vintage neck (1.650 nut), 35° bevel', 'v4 (1-11/16 nut), 72° face', 'Proposed (1-11/16 nut), quarter-sphere'],
               loc='upper left', bbox_to_anchor=(0.008, 0.905), ncol=3, frameon=False, fontsize=10)
    fig.text(0.012, 0.945, 'Bending room: fret left outside the outer strings (longer is safer)', fontsize=16, weight='bold')
    fig.savefig(os.path.join(FIG, 'bending_room.png'), dpi=120)
    plt.close(fig)
    return 'bending_room.png'


# ---------------------------------------------------------------------------------------- edge line ----
def edge_line(c, side, phi=45.0, n0=9, n1=16):
    """Height of the edge, as a flat hand held at phi sees it, along the neck (with and without the steel)."""
    x = np.arange(FX[n0] - 0.25, FX[n1] + 0.25, 0.001)
    s = np.concatenate([[0.0], 0.16 * (1 - np.cos(np.linspace(0, np.pi / 2, 320)[1:]))])
    X, Sg = np.meshgrid(x, s, indexing='ij')
    z, steel, wood = fm.rel(X, Sg, side, c)
    ph = math.radians(phi)
    return x, (-Sg * math.cos(ph) + z * math.sin(ph)).max(1), (-Sg * math.cos(ph) + wood * math.sin(ph)).max(1)


def fig_wave(keys=('vintage', 'v4', 'rec', 'bullet_tight')):
    lab = dict(NAME, bullet_tight='Proposed, tighter roll (option)')
    col = dict(COL, bullet_tight='#6250d6')
    fig, axs = plt.subplots(2, 1, figsize=(15, 8.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.065, right=0.80, top=0.84, bottom=0.085, hspace=0.16)
    for ax, side, title in ((axs[0], 'T', 'Treble edge'), (axs[1], 'B', 'Bass edge')):
        for k in keys:
            x, sup, supw = edge_line(fm.CANDS[k], side)
            ax.plot(x, supw * 1000, color=col[k], lw=2.0, ls='--' if k == 'bullet_tight' else '-')
            ax.plot(x, sup * 1000, color=col[k], lw=0.8, ls='--' if k == 'bullet_tight' else '-')
            ax.text(x[-1] + 0.03, supw[-1] * 1000, lab[k], color=INK, fontsize=9.5, va='center')
            ax.plot([x[-1] + 0.005, x[-1] + 0.022], [supw[-1] * 1000] * 2, color=col[k], lw=2.0, ls='--' if k == 'bullet_tight' else '-')
        for n in range(9, 17):
            ax.axvline(FX[n], color=GRID, lw=0.8, zorder=0)
            if side == 'T':
                ax.text(FX[n], 22.5, 'fret %d' % n, fontsize=8, color=MUTED, ha='center')
        ax.set_title(title, loc='left', fontsize=11)
        ax.set_ylabel('edge height (thousandths)')
        ax.grid(axis='y', color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    axs[1].set_xlabel('distance from the nut (in)')
    axs[0].set_ylim(-62, 22)
    fig.text(0.012, 0.95, 'The edge your hand slides along, frets 9 to 16, hand held at 45 degrees', fontsize=16, weight='bold')
    fig.text(0.012, 0.905, 'Thick line: the wood. Thin spikes: the steel fret ends standing above it. Zero is a square, unscalloped board corner.',
             fontsize=10.5, color=INK2)
    fig.savefig(os.path.join(FIG, 'edge_line.png'), dpi=110)
    plt.close(fig)
    return 'edge_line.png'


# ------------------------------------------------------------------------------------ pressure maps ----
def fig_maps(keys=('vintage', 'v4', 'rec'), scens=('index_side', 'index_45', 'thumb_over')):
    Z = np.load(os.path.join(HERE, 'feel_maps.npz'))
    meta = _feel()['meta']
    tit = dict(SCEN)
    fig, axs = plt.subplots(len(keys), len(scens), figsize=(14.5, 12.2))
    fig.subplots_adjust(left=0.035, right=0.93, top=0.895, bottom=0.075, wspace=0.07, hspace=0.10)
    for q, sc in enumerate(scens):
        pf = meta['flat_peak_psi'][sc]
        vmax = max(float(Z['%s__%s__p' % (k, sc)].max()) for k in keys) / pf
        for r, k in enumerate(keys):
            ax = axs[r, q]
            p = Z['%s__%s__p' % (k, sc)] / pf
            st = Z['%s__%s__steel' % (k, sc)]
            nx = p.shape[0]
            dx = meta['grid']
            ext = [-nx * dx / 2, nx * dx / 2, -p.shape[1] * dx / 2, p.shape[1] * dx / 2]
            im = ax.imshow(p.T, origin='lower', extent=ext, cmap='Blues', vmin=0, vmax=vmax, interpolation='bilinear')
            xs = (np.arange(nx) - nx / 2 + 0.5) * dx
            ts = (np.arange(p.shape[1]) - p.shape[1] / 2 + 0.5) * dx
            ax.contour(xs, ts, st.T.astype(float), levels=[0.5], colors='#eb6834', linewidths=1.0)
            ax.set_xlim(-0.26, 0.26)
            ax.set_ylim(-0.26, 0.26)
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(True)
            ax.text(-0.25, 0.235, 'peak %.1f x flat' % p.max(), fontsize=9.5, va='top')
            if q == 0:
                ax.set_ylabel(NAME[k], fontsize=11, color=INK)
            if r == 0:
                ax.set_title(tit[sc].replace('\n', ' '), fontsize=11, loc='left')
            if r == len(keys) - 1:
                ax.plot([-0.24, -0.14], [-0.24, -0.24], color=INK, lw=2)
                ax.text(-0.19, -0.232, '0.100 in', fontsize=8, ha='center', va='bottom')
        cax = fig.add_axes([axs[0, q].get_position().x0, 0.045, axs[0, q].get_position().width * 0.6, 0.008])
        cb = fig.colorbar(im, cax=cax, orientation='horizontal')
        cb.ax.tick_params(labelsize=8, length=2)
        cb.outline.set_visible(False)
        cb.set_label('pressure, times flat', fontsize=8.5)
    fig.text(0.012, 0.965, 'Pressure under the skin at the worst moment of each slide (darker = harder)', fontsize=16, weight='bold')
    fig.text(0.012, 0.935, 'Each square is the finger\'s contact patch, the neck running left to right. Orange outline: where the skin is on steel. '
             'Colour scales are in multiples of the same touch on a flat board, one scale per column.', fontsize=10.5, color=INK2)
    fig.savefig(os.path.join(FIG, 'pressure_maps.png'), dpi=105)
    plt.close(fig)
    return 'pressure_maps.png'


# ------------------------------------------------------------------------------------------ summary ----
def fig_summary():
    import fe_render as fr
    F, G = _feel()['feel'], _geo()['margins']
    keys = ('vintage', 'v4', 'rec')
    fig = plt.figure(figsize=(22, 27))
    fig.text(0.025, 0.978, 'Supercaster II fret ends: proposal', fontsize=30, weight='bold')
    fig.text(0.025, 0.9675, 'A true quarter-sphere end, made off the neck, sitting on a small wood nose that the edge roll wraps around. '
             'Vintage bending room kept.\nThe hardest spot under the skin is 14 to 29 % lower than v4 in five of six hand positions '
             '(up to 48 % against v4 as drawn, before its wood corner is hand-broken), level in the sixth.',
             fontsize=14.5, color=INK2, va='top', linespacing=1.5)
    heads = ['Vintage: square edge, 35° bevel', 'v4: flat 72° face, rounded ridge', 'Proposed: quarter-sphere on a wrapped nose']
    # row 1: treble edge at fret 12, player's eye; row 2: bass edge, frets 1 and 2, from the side
    for r, (side, lo, hi, view, cap, kw) in enumerate((
            ('T', 12, 12, 'eye', 'Treble edge at fret 12, as the player sees it', dict(centre=float(FX[12]), span=0.45)),
            ('B', 1, 2, 'eye', 'Bass edge at frets 1 and 2, as the player sees it', {}))):
        y0 = 0.745 - r * 0.205
        fig.text(0.025, y0 + 0.190, cap, fontsize=15, weight='bold')
        for q, k in enumerate(keys):
            ax = fig.add_axes([0.025 + q * 0.32, y0, 0.31, 0.182])
            ax.imshow(fr.render(fm.CANDS[k], side, lo, hi, view, size=(1300, 780), **kw))
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)
            ax.set_title(heads[q], fontsize=12.5, loc='left', pad=3)
    # row 3: sections along the fret
    fig.text(0.025, 0.522, 'Section along the fret at fret 12, treble side, to scale (yellow: the high E at rest)', fontsize=15, weight='bold')
    for q, k in enumerate(keys):
        ax = fig.add_axes([0.025 + q * 0.32, 0.355, 0.31, 0.155])
        sec_along(ax, k, 'T', 12)
    # row 4: feel bars and bending room
    fig.text(0.025, 0.325, 'Hardest spot under the skin (times a flat board): shorter is softer', fontsize=15, weight='bold')
    for q, (s, title) in enumerate(SCEN):
        ax = fig.add_axes([0.105 + q * 0.148, 0.185, 0.128, 0.105])
        yy = np.arange(3)[::-1]
        vals = [F[k]['fret_12'][s]['peak'] for k in keys]
        ax.barh(yy, vals, height=0.62, color=[COL[k] for k in keys], edgecolor=SURF, linewidth=1.5)
        for yv, v in zip(yy, vals):
            ax.text(v + 0.2, yv, '%.1f' % v, va='center', fontsize=11)
        ax.set_xlim(0, 11.5)
        ax.set_yticks(yy)
        ax.set_yticklabels([NAME[k].split(':')[0] for k in keys] if q == 0 else [], fontsize=12, color=INK)
        ax.tick_params(length=0)
        ax.set_xticks([])
        ax.spines['bottom'].set_visible(False)
        ax.set_title(title, fontsize=11, loc='left')
    fig.text(0.025, 0.150, 'Bending room: full-height fret outside the string centre (in)', fontsize=15, weight='bold')
    cells = [['', 'Fret 1 high E', 'Fret 1 low E', 'Fret 12 high E', 'Fret 12 low E', 'Fret 21 high E', 'Fret 21 low E']]
    for k, nm in zip(keys, ('Vintage neck', 'v4', 'Proposed')):
        cells.append([nm] + ['%.3f' % G[k]['fret_%d' % n][sd]['to_full'] for n in (1, 12, 21) for sd in 'TB'])
    ax = fig.add_axes([0.025, 0.045, 0.62, 0.095])
    ax.axis('off')
    tb = ax.table(cellText=cells, loc='center', cellLoc='center')
    tb.auto_set_font_size(False)
    tb.set_fontsize(12.5)
    tb.scale(1, 1.9)
    for (i, j), cell in tb.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_facecolor(SURF)
        if i == 0 or j == 0:
            cell.set_text_props(weight='bold')
    fig.text(0.67, 0.132, 'What it costs', fontsize=15, weight='bold')
    fig.text(0.67, 0.122, 'No bending room: equal to a vintage neck on both sides, 0.002 less\n'
             'than v4 at the high E and 0.008 more at the low E.\n'
             'Same workflow as v4 (ends shaped off the neck before fitting); the\n'
             'disc-sander face becomes a cup cutter in a drill press, about an\n'
             'hour more for the set, plus cutters. The ends still stand above\n'
             'the wood: no end with this bending room can be flush. From the\n'
             'side the roll now arches up to each fret end.', fontsize=12.5, va='top', color=INK2, linespacing=1.45)
    fig.text(0.025, 0.018, 'Renders and sections come from the same surfaces as the numbers (fe_model.py). Feel figures are computed, not measured: see FRET-ENDS.md.',
             fontsize=11, color=MUTED)
    out = os.path.join(HERE, 'fret-ends-summary.png')
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if what in ('sections', 'all'):
        print(fig_sections('T', 12))
        print(fig_sections('B', 1))
    if what in ('feel', 'all'):
        print(fig_feel('fret_12'))
        print(fig_feel('fret_2'))
    if what in ('trade', 'all'):
        print(fig_trade())
    if what in ('room', 'all'):
        print(fig_room())
    if what in ('wave', 'all'):
        print(fig_wave())
    if what in ('maps', 'all'):
        print(fig_maps())
    if what in ('summary',):
        print(fig_summary())
