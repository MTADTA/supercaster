#!/usr/bin/env python3
"""Supercaster II fret ends, round 2: drawings, charts and the summary sheet.

Same surfaces and numbers as FRET-ENDS-R2.md: geometry_r2.json (fe_r2_model.py) and feel_r2.json
(fe_r2_contact.py). Round-1 drawing helpers are imported from fe_fig.py, unchanged.

Run:  python -I -B fe_r2_fig.py                 -> every figure
      python -I -B fe_r2_fig.py sections|charts|renders|summary
"""
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, Polygon  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fe_fig as ff  # noqa: E402
import fe_r2_model as r2  # noqa: E402

fm, n4 = r2.fm, r2.fm.n4
FX, HF, CW = fm.FX, fm.HF, fm.CW
FIG = ff.FIG
INK, INK2, MUTED, GRID, SURF = ff.INK, ff.INK2, ff.MUTED, ff.GRID, ff.SURF

KEYS = ['vintage', 'v4', 'rec', 'A_wrap', 'B_dome', 'C_short', 'C_long', 'C_graded']
SHOW = ['vintage', 'v4', 'rec', 'A_wrap', 'B_dome', 'C_short', 'C_long']          # the shapes, drawn at fret 12
COL = dict(vintage='#2a78d6', v4='#eb6834', rec='#1baf7a', B_dome='#eda100', A_wrap='#e87ba4', C_short='#008300',
           C_long='#6250d6', C_graded='#e34948', A_twin='#898781')
NAME = dict(vintage='Vintage: 35° bevel', v4='v4: 72° face', rec='Round 1: quarter-sphere', A_wrap='(a) Wrap-over',
            B_dome='(b) Stretched dome', C_short='(c) Flow end, short', C_long='(c) Flow end, long',
            C_graded='(c) Flow end, graded', A_twin='(a) shape without the leg')
for k in r2.R2:
    ff.NAME.setdefault(k, NAME.get(k, k))
    ff.TANG_END[k], ff.SLOT_END[k], ff.END_NOTE[k] = 0.085, 0.075, ''
SCEN = ff.SCEN


def _geo():
    return json.load(open(os.path.join(HERE, 'geometry_r2.json')))


def _feel():
    return json.load(open(os.path.join(HERE, 'feel_r2.json')))


def _crown_toe(key, side, n):
    """Where steel first stands above the board surface, and where full height starts."""
    x = float(FX[n])
    s = np.linspace(0, 0.14, 7001)
    z, st, wood = fm.surface(np.full_like(s, x), s, side, fm.CANDS[key])
    land = n4.board(x, fm.side_y(x, s, side))
    up = st & (z - land > 2e-4)
    toe = float(s[np.argmax(up)])
    full = float(s[np.argmax(land + HF - z < 1e-5)]) if key != 'vintage' else HF * np.tan(np.radians(35))
    return toe, full


# ------------------------------------------------------------------------------------------ sections ----
def along(ax, key, side='T', n=12, frame=(-0.060, 0.175, -0.095, 0.085), labels=True):
    """Section along the fret through its centreline. Left is outboard; the board side is at 0."""
    c = fm.CANDS[key]
    x = float(FX[n])
    s = np.linspace(0, frame[1], 4301)
    z, st, wood = fm.rel(np.full_like(s, x), s, side, c)
    cz = float(fm.corner_z(x))
    y = fm.side_y(x, s, side)
    land, glue = n4.board(x, y) - cz, n4.glue(x, y) - cz
    ff._bare(ax, *frame)
    ff._wood_fill(ax, s, wood, glue, frame[2])
    ax.plot([0, 0], [frame[2], wood[0]], color=INK, lw=0.9)
    xm = float((FX[n] + FX[n + 1]) / 2)
    _, _, wm = fm.rel(np.full_like(s, xm), s, side, c)
    ax.plot(s, wm, color='white', lw=1.0, ls=(0, (4, 3)))
    sl = s >= ff.SLOT_END[key]
    ax.fill_between(s[sl], land[sl] - (n4.P['tang_depth'] + n4.P['slot_extra']), land[sl], color=ff.SLOT, lw=0)
    tg = s >= ff.TANG_END[key]
    ax.fill_between(s[tg], land[tg] - n4.P['tang_depth'], land[tg], color=ff.TANG, lw=0)
    i = np.where(st)[0]
    low = np.where(z < land - 1e-6, wood, land)                  # a wrapped leg lies in its pocket, the crown on the board
    poly = np.concatenate([np.c_[s[i], z[i]], np.c_[s[i][::-1], low[i][::-1]]])
    ax.add_patch(Polygon(poly, closed=True, facecolor=ff.STEEL, edgecolor=INK, lw=0.9, zorder=3))
    e = ff._string_to_side(key, side, n)
    dia = 0.010 if side == 'T' else 0.046
    le = float(n4.board(x, fm.side_y(x, e, side)) - cz)
    ax.add_patch(Circle((e, le + HF + dia / 2), dia / 2, facecolor='#e9b44c', edgecolor=INK, lw=0.7, zorder=4))
    toe, full = _crown_toe(key, side, n)
    if labels:
        top = float(np.interp(full, s, land)) + HF
        ax.plot([full, full], [top, 0.072], color=INK2, lw=0.6)
        ax.plot([e, e], [le + HF + dia, 0.072], color=INK2, lw=0.6)
        ff._dim(ax, full, e, 0.067, '', fs=9)
        if dia > 0.02:                                           # a wound string would cover a centred label
            ax.text(e - dia / 2 - 0.003, 0.0705, '%.3f full height' % (e - full), ha='right', va='bottom', fontsize=9, color=INK)
        else:
            ax.text((full + e) / 2, 0.0705, '%.3f full height' % (e - full), ha='center', va='bottom', fontsize=9, color=INK)
        ax.text(frame[0] + 0.003, 0.070, 'steel from %.3f\nfull from %.3f' % (toe, full) if toe > 0.002 else
                'steel flush with\nthe side, full\nfrom %.3f' % full, fontsize=8.5, va='top')
        ff._scalebar(ax, frame[0] + 0.004, frame[2] + 0.008)


def across(ax, key, side='T', n=12, frame=(-0.115, 0.115, -0.060, 0.062)):
    """Cuts across the fret, seen from the side of the neck: where the end begins, a third and two thirds of the
    way up it, and the full crown."""
    c = fm.CANDS[key]
    x = float(FX[n])
    toe, full = _crown_toe(key, side, n)
    xi = np.linspace(frame[0], frame[1], 2301)
    cz = fm.corner_z(x + xi)
    cuts = [toe + f * (full - toe) for f in (0.33, 0.66)] + [full + 0.004]
    s0 = cuts[0]
    z, st, wood = fm.rel(x + xi, np.full_like(xi, s0), side, c)
    y = fm.side_y(x + xi, s0, side)
    land, glue = n4.board(x + xi, y) - cz, n4.glue(x + xi, y) - cz
    ff._bare(ax, *frame)
    ff._wood_fill(ax, xi, wood, glue, frame[2])
    i = np.where(st & (z > land + 1e-5))[0]
    if len(i):
        poly = np.concatenate([np.c_[xi[i], z[i]], np.c_[xi[i][::-1], land[i][::-1]]])
        ax.add_patch(Polygon(poly, closed=True, facecolor=ff.STEEL, edgecolor=INK, lw=0.9, zorder=3))
    for sk, ls in zip(cuts[1:], ('--', '-')):
        zk, stk, _ = fm.rel(x + xi, np.full_like(xi, sk), side, c)
        lk = n4.board(x + xi, fm.side_y(x + xi, sk, side)) - cz
        j = np.where(stk & (zk > lk + 1e-5))[0]
        if len(j):
            ax.plot(xi[j], (zk - lk + land)[j], color=INK, lw=0.8, ls=ls, zorder=4)
    ax.text(frame[0] + 0.004, frame[3] - 0.003, 'cut %.3f in from the side (filled),\n%.3f (dashes), full crown (line)' % (cuts[0], cuts[1]),
            fontsize=7.8, va='top')


def fig_sections(side='T', n=12):
    K = 15.0
    wA, wB, wC, h = 0.235 * K, 0.23 * K, 0.34 * K, 0.21 * K
    gap, left, topm, rowgap, bot = 0.4, 0.35, 1.3, 0.5, 0.3
    Wf = left * 2 + wA + wB + wC + 2 * gap
    Hf = topm + len(SHOW) * h + (len(SHOW) - 1) * rowgap + bot
    fig = plt.figure(figsize=(Wf, Hf))
    sn = 'treble' if side == 'T' else 'bass'
    fig.text(left / Wf, 1 - 0.42 / Hf, 'Round 2 fret ends at fret %d, %s side, drawn to scale' % (n, sn), fontsize=17, weight='bold')
    fig.text(left / Wf, 1 - 0.78 / Hf, 'Rosewood dark, maple light, steel grey, string yellow. White dashes: the wood midway to the next fret. '
             'The bar is 0.050 in.', fontsize=11, color=INK2)
    heads = ['cut along the fret', 'Cuts across the fret, seen from the side', 'From straight above']
    for r, key in enumerate(SHOW):
        y0 = (bot + (len(SHOW) - 1 - r) * (h + rowgap)) / Hf
        x0 = left
        for q, (w, fn) in enumerate(((wA, along), (wB, across), (wC, ff.plan))):
            ax = fig.add_axes([x0 / Wf, y0, w / Wf, h / Hf])
            fn(ax, key, side, n)
            ax.set_title(('%s  |  ' % NAME[key] if q == 0 else '') + heads[q], fontsize=10.5, loc='left', pad=4,
                         weight='bold' if q == 0 else 'normal')
            x0 += w + gap
    fname = 'r2_sections_%s_fret_%d.png' % (sn, n)
    fig.savefig(os.path.join(FIG, fname), dpi=100)
    plt.close(fig)
    return fname


# -------------------------------------------------------------------------------------------- charts ----
def dots(ax, F, fret, metric, keys, scale=1.0, xlabel='', xmax=None, names=True):
    """One row per hand position, one dot per end. Hollow dot: the hardest spot is on wood, not steel."""
    rows = len(SCEN)
    for r, (sc, title) in enumerate(SCEN):
        yb = rows - 1 - r
        if r % 2 == 0:
            ax.axhspan(yb - 0.5, yb + 0.5, color='#f3f2ee', lw=0)
        for q, k in enumerate(keys):
            d = F[k][fret][sc]
            yy = yb + 0.36 - 0.72 * q / (len(keys) - 1)
            v = d[metric] * scale
            hollow = metric == 'peak' and d['on'] == 'wood'
            ax.plot([0, v], [yy, yy], color=COL[k], lw=1.0, alpha=0.35, solid_capstyle='butt')
            ax.plot([v], [yy], 'o', ms=6.5, mfc=SURF if hollow else COL[k], mec=COL[k], mew=1.6, zorder=3)
    ax.set_ylim(-0.5, rows - 0.5)
    ax.set_xlim(0, xmax)
    ax.set_yticks(range(rows))
    ax.set_yticklabels([t.replace('\n', ' ') if not names else t for _, t in SCEN][::-1] if names else [''] * rows, fontsize=9.5, color=INK)
    ax.tick_params(axis='y', length=0)
    ax.tick_params(axis='x', labelsize=9)
    ax.grid(axis='x', color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.spines['left'].set_visible(False)


def legend(fig, keys, x, y, ncol=4, fs=10.5, extra=True):
    hs = [plt.Line2D([], [], marker='o', ls='', ms=8, mfc=COL[k], mec=COL[k], label=NAME[k]) for k in keys]
    if extra:
        hs.append(plt.Line2D([], [], marker='o', ls='', ms=8, mfc=SURF, mec=INK2, mew=1.6, label='hollow: hardest spot is on wood'))
    fig.legend(handles=hs, loc='upper left', bbox_to_anchor=(x, y), ncol=ncol, frameon=False, fontsize=fs, handletextpad=0.3, columnspacing=1.4)


def fig_feel():
    F = _feel()['feel']
    fig, axs = plt.subplots(1, 3, figsize=(19, 8.2))
    fig.subplots_adjust(left=0.105, right=0.985, top=0.80, bottom=0.085, wspace=0.07)
    for q, (ax, fret) in enumerate(zip(axs, ('fret_2', 'fret_12', 'fret_20'))):
        dots(ax, F, fret, 'peak', KEYS, xlabel='hardest spot under the skin, times a flat board', xmax=9.8, names=q == 0)
        ax.set_title(fret.replace('_', ' ').capitalize(), fontsize=13, loc='left', weight='bold')
    fig.text(0.012, 0.955, 'Hardest spot under the skin, six hand positions, three frets: further left is softer', fontsize=17, weight='bold')
    fig.text(0.012, 0.918, 'Computed with the round-1 contact model (soft finger on a rigid neck). The graded end is long at fret 2 and short at fret 20.',
             fontsize=11.5, color=INK2)
    legend(fig, KEYS, 0.008, 0.895, ncol=5)
    fig.savefig(os.path.join(FIG, 'r2_feel.png'), dpi=100)
    plt.close(fig)
    return 'r2_feel.png'


def fig_slide():
    F = _feel()['feel']
    fig, axs = plt.subplots(2, 3, figsize=(19, 14.5))
    fig.subplots_adjust(left=0.105, right=0.985, top=0.875, bottom=0.05, wspace=0.07, hspace=0.2)
    for q, fret in enumerate(('fret_2', 'fret_12', 'fret_20')):
        dots(axs[0, q], F, fret, 'lift', KEYS, scale=1000, xlabel='rise and fall of the finger passing a fret, thousandths of an inch', xmax=58, names=q == 0)
        dots(axs[1, q], F, fret, 'catch_deg', KEYS, xlabel='catch: steepest push back along the neck, degrees', xmax=20, names=q == 0)
        axs[0, q].set_title(fret.replace('_', ' ').capitalize() + ': rise and fall', fontsize=13, loc='left', weight='bold')
        axs[1, q].set_title(fret.replace('_', ' ').capitalize() + ': catch', fontsize=13, loc='left', weight='bold')
    fig.text(0.012, 0.972, 'Sliding along the edge: how far the finger rises and falls at each fret, and how hard the fret pushes back', fontsize=17, weight='bold')
    fig.text(0.012, 0.951, 'Computed, same model. The even roll and the level edge rail bring both to vintage levels or below; the fingertip rows still cross the frets themselves.',
             fontsize=11.5, color=INK2)
    legend(fig, KEYS, 0.008, 0.938, ncol=8, extra=False)
    fig.savefig(os.path.join(FIG, 'r2_slide.png'), dpi=100)
    plt.close(fig)
    return 'r2_slide.png'


RIDGE_KEYS = ['vintage', 'v4', 'rec', 'B_dome', 'C_short', 'C_long', 'C_graded']


def ridge(ax, n=12, side='T', keys=RIDGE_KEYS):
    """Height of the fret ridge against distance from the string toward the edge."""
    x = float(FX[n])
    s = np.linspace(0, 0.16, 3201)
    G = _geo()['margins']
    for k in keys:
        if k == 'vintage':
            lost = np.clip(HF - s / np.tan(np.radians(35)), 0, HF)
            e = G[k]['fret_%d' % n][side]['string_to_side']
        else:
            z, st, wood = fm.surface(np.full_like(s, x), s, side, fm.CANDS[k])
            lost = np.clip(n4.board(x, fm.side_y(x, s, side)) + HF - z, 0, HF)
            e = G[k]['fret_%d' % n][side]['string_to_side']
        ax.plot((e - s) * 1000, (HF - lost) * 1000, color=COL[k], lw=2, label=NAME[k], ls=(0, (4, 2)) if k == 'C_graded' else '-', zorder=3 if k == 'C_graded' else 2)
        hold = G[k]['fret_%d' % n][side]['to_hold']
        ax.plot([hold * 1000], [np.interp(e - hold, s, HF - lost) * 1000], 'o', ms=7, mfc=SURF, mec=COL[k], mew=1.8, zorder=4)
    ax.set_xlim(40, 128)
    ax.set_ylim(0, 47)
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel('distance from the string at rest toward the board edge, thousandths', fontsize=10)
    ax.set_ylabel('height of the fret top, thousandths', fontsize=10)
    ax.tick_params(labelsize=9)


def fig_ridge():
    fig, axs = plt.subplots(1, 3, figsize=(19, 6.6), sharey=True)
    fig.subplots_adjust(left=0.05, right=0.985, top=0.77, bottom=0.10, wspace=0.05)
    for ax, n in zip(axs, (1, 12, 21)):
        ridge(ax, n)
        ax.set_title('Fret %d' % n, fontsize=13, loc='left', weight='bold')
        if n != 1:
            ax.set_ylabel('')
    fig.text(0.012, 0.945, 'Bending room: how far a string can be pushed toward the edge before the fret top starts to fall away', fontsize=17, weight='bold')
    fig.text(0.012, 0.900, 'Computed. Ring: where the fret top passes 10° of slope and a string begins to slide outward (the 10° is a judgment). '
             'The wrap-over (a) is the same as the long flow end. The graded end (dashed) is the long end at fret 1.', fontsize=11.5, color=INK2)
    legend(fig, RIDGE_KEYS, 0.008, 0.875, ncol=8, extra=False)
    fig.savefig(os.path.join(FIG, 'r2_bending_room.png'), dpi=100)
    plt.close(fig)
    return 'r2_bending_room.png'


def fig_edge():
    keys = ['vintage', 'v4', 'rec', 'B_dome', 'C_long', 'C_graded']
    fig, axs = plt.subplots(3, 1, figsize=(17, 11.5), sharex=True)
    fig.subplots_adjust(left=0.06, right=0.985, top=0.865, bottom=0.06, hspace=0.16)
    for ax, phi, cap in zip(axs, (20, 45, 70), ('hand low, nearly side-on (20°)', 'hand at 45°', 'hand high, wrapped over the edge (70°)')):
        for k in keys:
            x, sup, supw = ff.edge_line(fm.CANDS[k], 'T', phi, 9, 15)
            base = np.median(sup)
            ax.plot(x - FX[12], (sup - base) * 1000, color=COL[k], lw=1.8, label=NAME[k])
        for n in range(9, 16):
            ax.axvline(FX[n] - FX[12], color=GRID, lw=0.8, zorder=0)
        ax.set_ylabel('edge height, thousandths', fontsize=10)
        ax.set_title('Treble edge as a flat ' + cap + ' meets it, frets 9 to 15', fontsize=12, loc='left', weight='bold')
        ax.grid(axis='y', color=GRID, lw=0.8)
        ax.set_ylim(-48, 30)
        ax.tick_params(labelsize=9)
    axs[-1].set_xlabel('distance along the neck from fret 12, inches (vertical lines: frets)', fontsize=10)
    fig.text(0.012, 0.965, 'The line a hand slides along: rise and fall of the edge, each end measured from its own typical level', fontsize=17, weight='bold')
    fig.text(0.012, 0.935, 'Computed from the surfaces (a rigid flat hand; the contact model in r2_slide.png adds the soft finger). '
             'Flat is best: every bump is a fret end, every dip a scallop running out through the edge. Peaks above 30 are cut off.', fontsize=11.5, color=INK2)
    legend(fig, keys, 0.008, 0.918, ncol=6, extra=False)
    fig.savefig(os.path.join(FIG, 'r2_edge_line.png'), dpi=100)
    plt.close(fig)
    return 'r2_edge_line.png'


STATES = [('+4', 'board dried\n0.004 since\ndressing'), ('', 'as dressed,\nflush'), ('-4', 'board swollen\n0.004'), ('-8', 'board swollen\n0.008')]


def shrink(ax, F, sc, keys, ymax=9.9):
    for k in keys:
        v = [F[k + a]['fret_12'][sc]['peak'] if (k + a) in F else np.nan for a, _ in STATES]
        on = [F[k + a]['fret_12'][sc]['on'] if (k + a) in F else 'steel' for a, _ in STATES]
        ax.plot(range(4), v, color=COL[k], lw=2, ls='--' if k == 'A_twin' else '-')
        for i, (vv, o) in enumerate(zip(v, on)):
            ax.plot([i], [vv], 'o', ms=7, mfc=SURF if o == 'wood' else COL[k], mec=COL[k], mew=1.6, zorder=3)
    ax.set_xticks(range(4))
    ax.set_xticklabels([t for _, t in STATES], fontsize=8.5, color=INK)
    ax.set_ylim(0, ymax)
    ax.set_xlim(-0.3, 3.3)
    ax.grid(axis='y', color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis='y', labelsize=9)


def fig_shrink():
    F = _feel()['feel']
    keys = ['vintage', 'rec', 'A_wrap', 'A_twin', 'B_dome', 'C_short', 'C_long', 'C_graded']
    fig, axs = plt.subplots(1, 3, figsize=(19, 7.4), sharey=True)
    fig.subplots_adjust(left=0.05, right=0.985, top=0.76, bottom=0.12, wspace=0.05)
    for ax, sc in zip(axs, ('index_side', 'index_45', 'thumb_45')):
        shrink(ax, F, sc, keys)
        ax.set_title(dict(SCEN)[sc].replace('\n', ' '), fontsize=12.5, loc='left', weight='bold')
    axs[0].set_ylabel('hardest spot, times a flat board', fontsize=10)
    fig.text(0.012, 0.945, 'When the board shrinks and swells: hardest spot at fret 12 in the three sliding positions', fontsize=17, weight='bold')
    fig.text(0.012, 0.900, 'Computed. The board side moves against the steel; 0.004 is about a 4 % change in moisture content on a quartersawn board. '
             'Hollow dot: the hardest spot has moved onto wood.', fontsize=11.5, color=INK2)
    hs = [plt.Line2D([], [], marker='o', ls='--' if k == 'A_twin' else '-', lw=2, ms=7, color=COL[k], label=NAME[k]) for k in keys]
    fig.legend(handles=hs, loc='upper left', bbox_to_anchor=(0.008, 0.875), ncol=8, frameon=False, fontsize=10.5)
    fig.savefig(os.path.join(FIG, 'r2_shrink_swell.png'), dpi=100)
    plt.close(fig)
    return 'r2_shrink_swell.png'


def trade_points():
    """Every rounded-in-plan variant tried: where full height starts against the hardest spot (fret 12)."""
    F = _feel()['feel']
    pts = []
    for k, c in r2.R2.items():
        if c['kind'] == 'flow' and c['across'] == 'ogive' and c['edge'] == 'rail' and k in F and k != 'C_graded' and c['p'] == 0.5:
            full = fm.end_profile(12, 'T', c)['full']
            pts.append((k, full, F[k]['fret_12']))
    return pts


def _halo():
    import matplotlib.patheffects as pe
    return [pe.withStroke(linewidth=3.5, foreground=SURF)]


def trade(ax, sc='index_45', label=True):
    F = _feel()['feel']
    pts = trade_points()
    par = 0.0491
    ax.plot([(p[1] - par) * 1000 for p in pts], [p[2][sc]['peak'] for p in pts], 'o', ms=6, mfc='#c3c2b7', mec='#c3c2b7', zorder=2)
    for k in ('B_dome', 'C_short', 'C_long'):
        full = fm.end_profile(12, 'T', fm.CANDS[k])['full']
        ax.plot([(full - par) * 1000], [F[k]['fret_12'][sc]['peak']], 'o', ms=10, mfc=COL[k], mec=SURF, mew=1.5, zorder=4)
        if label:
            off, ha = dict(B_dome=((4, 13), 'left'), C_short=((9, 17), 'left'), C_long=((-2, -17), 'right'))[k]
            ax.annotate(NAME[k], ((full - par) * 1000, F[k]['fret_12'][sc]['peak']), xytext=off, textcoords='offset points', fontsize=9.5, ha=ha, zorder=6, path_effects=_halo())
    for k, yv in (('rec', F['rec']['fret_12'][sc]['peak']), ('vintage', F['vintage']['fret_12'][sc]['peak'])):
        ax.plot([0], [yv], 's', ms=9, mfc=COL[k], mec=SURF, mew=1.5, zorder=4)
        if label:
            ax.annotate(NAME[k], (0, yv), xytext=(9, -15 if k == 'rec' else -3), textcoords='offset points', fontsize=9.5, zorder=6, path_effects=_halo())
    ax.set_xlim(-4, 36)
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=9)
    ax.set_xlabel('bending room given up against a vintage neck, thousandths', fontsize=10)


def fig_trade():
    fig, axs = plt.subplots(1, 3, figsize=(19, 6.8))
    fig.subplots_adjust(left=0.05, right=0.985, top=0.80, bottom=0.10, wspace=0.14)
    for ax, sc in zip(axs, ('index_45', 'thumb_45', 'thumb_over')):
        trade(ax, sc)
        ax.set_ylim(3.4, 9.6 if sc != 'thumb_over' else 7.9)
        ax.set_title(dict(SCEN)[sc].replace('\n', ' '), fontsize=12.5, loc='left', weight='bold')
    axs[0].set_ylabel('hardest spot at fret 12, times a flat board', fontsize=10)
    fig.text(0.012, 0.945, 'What bending room buys: every thousandth given up makes the end longer and softer', fontsize=17, weight='bold')
    fig.text(0.012, 0.895, 'Computed. Grey dots: the %d rounded-in-plan variants tried (blend angle 45 to 72°, roll radius 0.030 to 0.050, top radius 0.012 to 0.040). '
             'Coloured: the three carried forward. Squares: ends at vintage room from round 1.' % len(trade_points()), fontsize=11.5, color=INK2)
    fig.savefig(os.path.join(FIG, 'r2_trade.png'), dpi=100)
    plt.close(fig)
    return 'r2_trade.png'


def room_table(ax, fs=11):
    G = _geo()['margins']
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    cols = [0.0, 0.33, 0.47, 0.61, 0.75, 0.89]
    heads = ['', 'fret 1', 'fret 12', 'fret 21', 'given up\nat fret 12', 'slides off\nat, fret 12']
    for xq, hq in zip(cols, heads):
        ax.text(xq + (0.0 if xq == 0 else 0.10), 0.97, hq, fontsize=fs, weight='bold', va='top', ha='left' if xq == 0 else 'right', linespacing=1.15)
    ax.plot([0, 1], [0.845, 0.845], color='#c3c2b7', lw=1)
    v12 = G['vintage']['fret_12']['T']['to_full']
    for r, k in enumerate(KEYS):
        yy = 0.79 - r * 0.103
        m = G[k]
        ax.plot([0.012], [yy], 'o', ms=9, mfc=COL[k], mec=COL[k])
        ax.text(0.035, yy, NAME[k], fontsize=fs, va='center')

        def cell(n, q='to_full'):
            a, b = m['fret_%d' % n]['T'][q], m['fret_%d' % n]['B'][q]
            return '%.3f' % a if abs(a - b) < 5e-4 else '%.3f / %.3f' % (a, b)
        for xq, n in zip(cols[1:4], (1, 12, 21)):
            ax.text(xq + 0.10, yy, cell(n), fontsize=fs, va='center', ha='right')
        d = v12 - m['fret_12']['T']['to_full']
        ax.text(cols[4] + 0.10, yy, 'none' if abs(d) < 0.002 else '%.3f' % d, fontsize=fs, va='center', ha='right')
        ax.text(cols[5] + 0.10, yy, cell(12, 'to_hold'), fontsize=fs, va='center', ha='right')


def step_bars(ax):
    G = _geo()['protrusion']
    yy = np.arange(len(KEYS))[::-1]
    vals = [G[k]['T']['45']['step'] * 1000 for k in KEYS]
    ax.barh(yy, vals, height=0.6, color=[COL[k] for k in KEYS], edgecolor=SURF, linewidth=1.5)
    for yv, v in zip(yy, vals):
        ax.text(v + 0.4, yv, '%.1f' % v, va='center', fontsize=10)
    ax.set_yticks(yy)
    ax.set_yticklabels([NAME[k] for k in KEYS], fontsize=10, color=INK)
    ax.tick_params(axis='y', length=0)
    ax.tick_params(axis='x', labelsize=9)
    ax.set_xlim(0, 21)
    ax.grid(axis='x', color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('thousandths of an inch', fontsize=10)


# ------------------------------------------------------------------------------------------- renders ----
def _fret_mesh_fine(c, side, n):
    """As fe_render.fret_mesh, sampled four times finer, so a rounded tip or a wrapped leg has a clean outline."""
    import fe_render as fr
    if c['kind'] != 'flow':
        return _fret_mesh_r1(c, side, n)
    xf = float(FX[n])
    s_in = float(n4.width(xf)) - 0.035
    xi = CW * np.cos(np.linspace(0, np.pi, 241))
    # each row of the mesh starts exactly where the steel starts on that line, so the outline is the true one
    sf = np.arange(0, 0.11, 0.00002)
    XF, SF = np.meshgrid(xi, sf, indexing='ij')
    st = fm.surface(xf + XF, SF, side, c)[1]
    has = st.any(axis=1)
    toe = np.where(has, sf[np.argmax(st, axis=1)], np.nan)
    ok = np.flatnonzero(has)
    toe = np.interp(np.arange(len(xi)), ok, toe[ok])
    u = np.linspace(0, 1, 500) ** 1.6
    inner = np.linspace(0.11, s_in, int(s_in / 0.004))[1:]
    S = np.hstack([toe[:, None] + (0.11 - toe[:, None]) * u[None, :], np.tile(inner, (len(xi), 1))])
    XI = np.tile(xi[:, None], (1, S.shape[1]))
    z, steel, wood = fm.surface(xf + XI, S, side, c)
    land = n4.board(xf + XI, fm.side_y(xf + XI, S, side))
    Hh = np.where(steel, z - land, wood - land - 0.004)
    X = xf + XI
    Y = fm.side_y(X, S, side)
    Z = n4.board(X, Y) + Hh - 0.0006 * (Hh <= 1e-9)
    return fr._sg(X, Y, Z).extract_surface(algorithm='dataset_surface').compute_normals(auto_orient_normals=False, split_vertices=False)


def _renderer():
    global _fret_mesh_r1
    import fe_render as fr
    if fr.fret_mesh is not _fret_mesh_fine:
        _fret_mesh_r1 = fr.fret_mesh
        fr.fret_mesh = _fret_mesh_fine
    return fr


def _img(ax, img, title=None, fs=12):
    ax.imshow(img)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    if title:
        ax.set_title(title, fontsize=fs, loc='left', pad=3)


def fig_renders(side='T', n=12, macro=True):
    fr = _renderer()
    sn = 'treble' if side == 'T' else 'bass'
    views = [('eye', "player's eye"), ('side', 'from the side'), ('above', 'from above')]
    fig = plt.figure(figsize=(21, 4.55 * len(SHOW) + 1.0))
    H = 4.55 * len(SHOW) + 1.0
    fig.text(0.012, 1 - 0.45 / H, ('%s edge at fret %d, one fret end close up (frame about 0.45 in wide)' % (sn.capitalize(), n)) if macro
             else ('%s edge, frets %d and %d' % (sn.capitalize(), n, n + 1)), fontsize=18, weight='bold')
    fig.text(0.012, 1 - 0.80 / H, 'The wrap-over is drawn with its leg let into the roll; every other end stops above the roll. A dark fleck at a toe is the coarser wood mesh of the picture, not a gap (computed gap under every crown: 0).' if macro else
             'The dark band between the frets on the four new ends is the shoulder where the hollow starts, inboard of the level edge rail. The edge itself stays level.',
             fontsize=12.5, color=INK2)
    for r, k in enumerate(SHOW):
        for q, (v, vn) in enumerate(views):
            kw = dict(centre=float(FX[n]), span=0.45) if macro else {}
            img = fr.render(fm.CANDS[k], side, n, n if macro else n + 1, v, size=(1200, 720), **kw)
            ax = fig.add_axes([0.012 + q * 0.33, 1 - (1.0 + (r + 1) * 4.55 - 0.25) / H, 0.32, 4.03 / H])
            _img(ax, img, '%s  |  %s' % (NAME[k], vn))
    fname = 'r2_render_%s_fret_%d_macro.png' % (sn, n) if macro else 'r2_render_%s_frets_%d-%d.png' % (sn, n, n + 1)
    fig.savefig(os.path.join(FIG, fname), dpi=80)
    plt.close(fig)
    return fname


def fig_graded():
    """The graded end along the neck: one fret end close up at frets 1, 7, 12, 17 and 21, both edges."""
    fr = _renderer()
    frets = (1, 7, 12, 17, 21)
    fig = plt.figure(figsize=(25, 7.6))
    fig.text(0.01, 0.945, 'The graded flow end along the neck: long and low at the nut, short at the body (close-ups about 0.45 in wide)', fontsize=18, weight='bold')
    for r, (side, sn) in enumerate((('T', 'Treble'), ('B', 'Bass'))):
        for q, n in enumerate(frets):
            img = fr.render(fm.CANDS['C_graded'], side, n, n, 'eye', size=(1000, 600), centre=float(FX[n]), span=0.45)
            ax = fig.add_axes([0.01 + q * 0.198, 0.47 - r * 0.45, 0.193, 0.40])
            nb = r2.numbers(fm.CANDS['C_graded'], side, n)
            _img(ax, img, '%s edge, fret %d: %d° line, full height from %.3f' % (sn, n, round(nb['blend_angle']), nb['full_from_side']), fs=11)
    fig.savefig(os.path.join(FIG, 'r2_render_graded.png'), dpi=80)
    plt.close(fig)
    return 'r2_render_graded.png'


# ------------------------------------------------------------------------------------------- summary ----
def fig_summary():
    fr = _renderer()
    F = _feel()['feel']
    fig = plt.figure(figsize=(28, 31.5))
    L, CWd, GAP = 0.018, 0.1325, 0.0052
    fig.text(L, 0.984, 'Supercaster II fret ends, round 2: the end that blends into the wood', fontsize=31, weight='bold')
    fig.text(L, 0.9745, 'Goal: the softest, most continuous edge to slide along and wrap a thumb over. The new ends sit on an even edge roll and leave it in one line; '
             'the edge is level between frets. They slide like a vintage edge or better\nand are as soft as the round-1 sphere or softer. '
             'Softer still costs bending room: the long flow end gives up 0.030, the graded one 0.030 at the nut falling to nothing at the body.',
             fontsize=14.5, color=INK2, va='top', linespacing=1.5)
    rows = [(0.852, 0.0785, "Treble edge at frets 12 and 13, as the player sees it", 'wide'),
            (0.7485, 0.0785, 'One fret end close up from the side of the neck, treble edge at fret 12 (frame about 0.45 in wide)', 'macro')]
    for y0, h, cap, kind in rows:
        fig.text(L, y0 + h + 0.0125, cap, fontsize=15, weight='bold')
        for q, k in enumerate(SHOW):
            ax = fig.add_axes([L + q * (CWd + GAP), y0, CWd, h])
            kw = dict(centre=float(FX[12]), span=0.45) if kind == 'macro' else {}
            _img(ax, fr.render(fm.CANDS[k], 'T', 12, 12 if kind == 'macro' else 13, 'side' if kind == 'macro' else 'eye', size=(1080, 720), **kw), NAME[k], fs=12.5)
    fig.text(L, 0.734, 'Cut along the fret at fret 12, treble side, to scale. Yellow: the high E at rest. White dashes: the wood midway to the next fret. Bar: 0.050 in.',
             fontsize=15, weight='bold')
    for q, k in enumerate(SHOW):
        ax = fig.add_axes([L + q * (CWd + GAP), 0.640, CWd, 0.0905])
        along(ax, k, 'T', 12)
    fig.text(L, 0.627, 'Cuts across the same fret end, seen from the side of the neck, to the same scale', fontsize=15, weight='bold')
    for q, k in enumerate(SHOW):
        ax = fig.add_axes([L + q * (CWd + GAP), 0.553, CWd, 0.0625])
        across(ax, k, 'T', 12)
    # charts
    y1 = 0.365
    fig.text(L, 0.537, 'Feel at fret 12 (computed): hardest spot under the skin', fontsize=15, weight='bold')
    fig.text(L, 0.5270, 'times a flat board; further left is softer', fontsize=11.5, color=INK2)
    ax = fig.add_axes([L + 0.068, y1, 0.215, 0.152])
    dots(ax, F, 'fret_12', 'peak', KEYS, xmax=9.8)
    fig.text(0.335, 0.537, 'Sliding: rise and fall at each fret', fontsize=15, weight='bold')
    fig.text(0.335, 0.5270, 'thousandths of an inch; left is more continuous', fontsize=11.5, color=INK2)
    ax = fig.add_axes([0.335, y1, 0.150, 0.152])
    dots(ax, F, 'fret_12', 'lift', KEYS, scale=1000, xmax=58, names=False)
    fig.text(0.505, 0.537, 'Sliding: catch', fontsize=15, weight='bold')
    fig.text(0.505, 0.5270, 'push back along the neck, degrees', fontsize=11.5, color=INK2)
    ax = fig.add_axes([0.505, y1, 0.110, 0.152])
    dots(ax, F, 'fret_12', 'catch_deg', KEYS, xmax=20, names=False)
    fig.text(0.640, 0.537, 'What bending room buys', fontsize=15, weight='bold')
    fig.text(0.640, 0.5270, 'hardest spot (index finger at 45°) against room given up', fontsize=11.5, color=INK2)
    ax = fig.add_axes([0.655, y1, 0.130, 0.152])
    trade(ax, 'index_45', label=False)
    ax.set_ylim(3.6, 9.6)
    fig.text(0.815, 0.537, 'Steel standing proud at 45°', fontsize=15, weight='bold')
    fig.text(0.815, 0.5270, 'above the wood beside it, for a flat hand', fontsize=11.5, color=INK2)
    ax = fig.add_axes([0.885, y1, 0.098, 0.152])
    step_bars(ax)
    legend(fig, KEYS, L - 0.004, 0.349, ncol=9, fs=12)
    # bottom row: bending room, shrink and swell, the graded end
    fig.text(L, 0.313, 'Bending room: full-height fret outside the string at rest, inches', fontsize=15, weight='bold')
    fig.text(L, 0.3025, 'both edges alike unless two numbers (treble / bass). Last column: where a string starts to slide outward', fontsize=11.5, color=INK2)
    ax = fig.add_axes([L, 0.135, 0.385, 0.160])
    room_table(ax, fs=12)
    fig.text(0.430, 0.313, 'Fret top against distance from the string, fret 12', fontsize=15, weight='bold')
    fig.text(0.430, 0.3025, 'ring: where a string starts to slide off', fontsize=11.5, color=INK2)
    ax = fig.add_axes([0.445, 0.150, 0.215, 0.142])
    ridge(ax, 12)
    fig.text(0.690, 0.313, 'When the board shrinks and swells (index finger side, hand low)', fontsize=15, weight='bold')
    fig.text(0.690, 0.3025, 'hardest spot at fret 12; hollow: on wood', fontsize=11.5, color=INK2)
    ax = fig.add_axes([0.705, 0.160, 0.278, 0.132])
    shrink(ax, F, 'index_side', ['vintage', 'rec', 'A_wrap', 'B_dome', 'C_short', 'C_long', 'C_graded'], ymax=9.8)
    fig.text(L, 0.113, 'The graded flow end along the neck (treble edge close-ups)', fontsize=15, weight='bold')
    for q, n in enumerate((1, 7, 12, 17, 21)):
        nb = r2.numbers(fm.CANDS['C_graded'], 'T', n)
        ax = fig.add_axes([L + q * 0.118, 0.022, 0.114, 0.0675])
        _img(ax, fr.render(fm.CANDS['C_graded'], 'T', n, n, 'eye', size=(1080, 720), centre=float(FX[n]), span=0.45),
             'fret %d: %d° line, full from %.3f' % (n, round(nb['blend_angle']), nb['full_from_side']), fs=11)
    fig.text(0.625, 0.108, 'How to read this sheet', fontsize=15, weight='bold')
    fig.text(0.625, 0.098,
             'Computed: every shape, section, bending-room figure and chart value (contact model: soft finger, rigid neck, grid 0.004 in).\n'
             'Judgment: the six hand positions and loads, finger softness, the 10° slide-off rule, and all workshop times.\n'
             'The wrap-over (a) has the same outer line as the long flow end; its crown must stay full width to turn over the edge,\n'
             'so it is less rounded in plan, and when the board swells its pocket edges stand proud (hollow dots, right-hand chart).\n'
             'The level rail at the edge is what stops the rise and fall. It means the scallop no longer runs out through the edge:\n'
             'it starts 0.040 in and is full depth under the outer strings. That is a change to the v4 scallop for the owner to accept.\n'
             'The dark band between the frets in the top row is the shoulder where that hollow starts; the edge itself stays level.\n'
             'Renders are the model surfaces, not photographs. Full report: FRET-ENDS-R2.md.',
             fontsize=11.5, color=INK2, va='top', linespacing=1.55)
    fig.savefig(os.path.join(HERE, 'fret-ends-r2-summary.png'), dpi=110)
    plt.close(fig)
    return 'fret-ends-r2-summary.png'


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd in ('sections', 'all'):
        print(fig_sections('T', 12), fig_sections('B', 1), flush=True)
    if cmd in ('charts', 'all'):
        print(fig_feel(), fig_slide(), fig_ridge(), fig_edge(), fig_shrink(), fig_trade(), flush=True)
    if cmd in ('renders', 'all'):
        print(fig_renders('T', 12, True), fig_renders('T', 12, False), fig_renders('B', 1, True), fig_graded(), flush=True)
    if cmd in ('summary', 'all'):
        print(fig_summary(), flush=True)
