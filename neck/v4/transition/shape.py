"""Prototype fingerboard: the true shape of one scallop, drawn from the model (study.py), with a rounder form for comparison.
Writes renders/neck-proto/shape.png and shape.json.   Run:  <venv>/python -I -B shape.py

Solid   the Nov 18 spec: 90 % short ramp + 10 % full-span bowl along the string; level rail, full depth 0.140 in from the side
Dashed  not adopted, shown only to compare the look: one full-span bowl per cell (bowl = 1) along the string, and across the
        board the R2 'dish' run-out (the hollow carried out to the edge roll) in place of the rail
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study as st
n = st.n; e = st.edge; fm = e.fm
OUT = os.path.join(HERE, '..', '..', '..', 'renders', 'neck-proto')
PICK = (-0.4, 0.30, 0.1)
SURF, INK, INK2, MUTED, GRID = '#1a1a19', '#f0efec', '#c3c2b7', '#8d8c85', '#2e2d2b'
S1, S2, WOOD, STEEL = '#3987e5', '#d95926', '#3b2a22', '#a9adb3'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.facecolor': SURF, 'figure.facecolor': SURF,
                     'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': MUTED, 'ytick.color': MUTED,
                     'text.color': INK, 'axes.grid': False})
VX = 3.0                                                          # vertical exaggeration, both rows
J = {}


def along(ax, k):
    xa, xb, L, *_ = n.cell_geometry(np.array([k])); xa, xb, L = float(xa[0]), float(xb[0]), float(L[0])
    x = np.linspace(xa - 0.09, xb + 0.09, 6001); y = n.string_y(x)[0]
    cur = -st.depth(x, y, PICK[0], PICK[1], symmetric=True, bowl=PICK[2])
    rnd = -st.depth(x, y, PICK[0], PICK[1], symmetric=True, bowl=1.0)
    t = x - xb                                                    # distance from fret k, negative = toward the nut
    ax.fill_between(t, cur, -0.085, color=WOOD, lw=0)
    ax.plot(t, cur, color=S1, lw=2.4); ax.plot(t, rnd, color=S2, lw=1.8, ls=(0, (5, 3)))
    for xf in (xa, xb):
        if xf > 0:
            a = np.linspace(0, np.pi, 80); ax.fill(xf - xb + n.CW * np.cos(a), n.HF * np.sin(a), color=STEEL, lw=0)
    inside = (x > xa) & (x < xb)
    sl = np.degrees(np.arctan(np.abs(np.gradient(cur, x))))[inside]; slr = np.degrees(np.arctan(np.abs(np.gradient(rnd, x))))[inside]
    flat = float(np.ptp(x[inside][cur[inside] < 0.95 * cur[inside].min()]))
    probe = xb - min(0.25, L / 2); yp = n.string_y(np.array([probe]))[0]
    d = lambda b: float(st.depth(np.array([probe]), yp, PICK[0], PICK[1], symmetric=True, bowl=b)[0])
    J['cell_%d' % k] = dict(length=L, depth=float(-cur.min()), floor_within_5pct_long=flat, ramp_peak_deg=float(sl.max()),
                            round_ramp_peak_deg=float(slr.max()), depth_quarter_inch_behind_fret=d(PICK[2]),
                            round_depth_quarter_inch_behind_fret=d(1.0))
    ax.set_xlim(t[0], t[-1]); ax.set_ylim(-0.085, 0.06); ax.set_aspect(1 / VX)
    ax.set_title('Along the high E, cell %d (fret %d on the right): %.3f deep, floor %.2f long, ramps up to %.0f°'
                 % (k, k, -cur.min(), flat, sl.max()), loc='left', fontsize=12.5, color=INK)
    ax.set_xlabel('inches from fret %d' % k)


def across(ax, k):
    xa, xb, L, *_ = n.cell_geometry(np.array([k])); xm = float((xa[0] + xb[0]) / 2); W = float(n.width(xm))
    s = np.linspace(0, 0.62, 4001); y = -(W / 2 - s)              # treble side, v4 frame (treble -)
    _, _, wood = st.surface(np.full_like(s, xm), y, *PICK)
    cone = n.board(xm, y); edge_z = float(n.board(xm, -W / 2))
    cur = wood - edge_z
    r = float(e.par(st.end, 'r', xm, 'T'))
    dfull = float(st.depth(np.array([xm]), np.array([-(W / 2 - 0.30)]), PICK[0], PICK[1], symmetric=True, bowl=PICK[2])[0])
    tilt = 1 - n.P['tilt'] * (y / W + 0.5); tilt = tilt / tilt[np.argmin(np.abs(s - 0.30))]
    dish = dfull * tilt * (1 - (np.clip(fm.S_DISH - s, 0, None) / fm.S_DISH) ** 2)
    roll = np.where(s < r, -r + np.sqrt(np.clip(r * r - (r - s) ** 2, 0, None)), 0.0)
    rnd = cone + roll - dish * n.fq(s / r) - edge_z
    ax.fill_between(s, cur, -0.11, color=WOOD, lw=0)
    ax.plot(s, cone - edge_z, color=MUTED, lw=1, ls=(0, (1, 3)))
    ax.plot(s, cur, color=S1, lw=2.4); ax.plot(s, rnd, color=S2, lw=1.8, ls=(0, (5, 3)))
    yE = float(n.string_y(np.array([xm]))[0, 0]); sE = W / 2 + yE
    ax.plot([sE, sE], [np.interp(sE, s, cur), 0.052], color='#e0b040', lw=1.2, ls=(0, (2, 2)))
    ax.annotate('high E', (sE, 0.052), textcoords='offset points', xytext=(5, -4), color='#e0b040', fontsize=10.5)
    ax.annotate('rail', (0.04, np.interp(0.04, s, cur)), textcoords='offset points', xytext=(-4, 12), color=INK2, fontsize=10.5, ha='center')
    m = s > r
    sl = np.degrees(np.arctan(-np.gradient(cur - (cone - edge_z), s)))[m]
    slr = np.degrees(np.arctan(-np.gradient(rnd - (cone - edge_z), s)))[m]
    under = lambda z: float(np.interp(sE, s, cone - edge_z - z))
    J['across_cell_%d' % k] = dict(high_E_from_side=sE, roll_radius=r, wall_peak_deg=float(sl.max()), round_wall_peak_deg=float(slr.max()),
                                   depth_under_high_E=under(cur), round_depth_under_high_E=under(rnd),
                                   depth_0p06_outside_high_E=float(np.interp(sE - 0.06, s, cone - edge_z - cur)),
                                   round_depth_0p06_outside_high_E=float(np.interp(sE - 0.06, s, cone - edge_z - rnd)))
    ax.set_xlim(-0.02, 0.62); ax.set_ylim(-0.11, 0.09); ax.set_aspect(1 / VX)
    ax.set_title('Across cell %d from the treble side:\nroll r %.3f, level rail, wall up to %.0f°' % (k, r, sl.max()), loc='left', fontsize=12.5, color=INK)
    ax.set_xlabel('inches in from the side of the board')


SC = 8.5                                                          # drawing inches per board inch, the same in all three panels
FW, FH = 15.0, 10.9
fig = plt.figure(figsize=(FW, FH))
def axes(left, bottom, xr, yr):
    return fig.add_axes([left / FW, bottom / FH, xr * SC / FW, yr * VX * SC / FH])
YR = 0.145
a3 = axes(0.9, 5.6, 1.275 + 0.18, YR); a12 = axes(0.9, 0.75, 0.758 + 0.18, YR); ac = axes(0.9 + 0.938 * SC + 1.0, 0.75, 0.52, YR)
along(a3, 3); along(a12, 12); across(ac, 12)
for a in (a3, a12, ac):
    a.set_aspect('auto'); a.set_ylim(-0.085, 0.06)
    a.set_yticks([-0.05, 0, 0.043]); a.set_yticklabels(['-.050', '0', '.043']); a.axhline(0, color=GRID, lw=0.8, zorder=0)
ac.set_xlim(-0.02, 0.50)
a3.plot([], [], color=S1, lw=2.4, label='Nov 18 spec (what the renders show)')
a3.plot([], [], color=S2, lw=1.8, ls=(0, (5, 3)), label='Rounder form, for comparison only: one bowl per cell, hollow carried out to the edge roll')
fig.legend(*a3.get_legend_handles_labels(), loc='upper left', frameon=False, fontsize=11.5, labelcolor=INK2, bbox_to_anchor=(0.9 / FW, 1 - 0.62 / FH))
fig.text(0.9 / FW, 1 - 0.42 / FH, 'The shape of one scallop, from the model. Heights drawn %d× so the form shows; inches.' % VX, fontsize=16, fontweight='bold')
fig.savefig(os.path.join(OUT, 'shape.png'), dpi=160)
json.dump(J, open(os.path.join(OUT, 'shape.json'), 'w'), indent=1)
print(json.dumps(J, indent=1))
