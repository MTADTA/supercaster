"""Prototype fingerboard: what changes going up the neck.  Writes into renders/neck-proto/:
  params.json   every per-fret number used on the sheets (from study.py / fe_r2_model.py / neck_v4.py, nothing re-derived)
  params.png    small multiples, one measure per panel, cells/frets 1-22
  plan.png      plan view of the whole board, colour = depth below the board cone (scallop + rail + roll), frets and strings drawn
Run:  <venv>/python -I -B sheet.py
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study as st
n = st.n; e = st.edge
OUT = os.path.join(HERE, '..', '..', '..', 'renders', 'neck-proto'); os.makedirs(OUT, exist_ok=True)
PICK = (-0.4, 0.30, 0.1)
R = json.load(open(os.path.join(HERE, 'results.json')))

# ---------------------------------------------------------------- numbers
k = np.arange(1, n.NF + 1)
xa, xb, length, *_ = n.cell_geometry(k)
mid = (xa + xb) / 2
ys = n.string_y(mid)                                  # (6, 22), v4 frame (bass +)
dep = lambda y: st.depth(mid, y, PICK[0], PICK[1], symmetric=True, bowl=PICK[2])
d_hiE, d_loE = dep(ys[0]), dep(ys[5])
eg = R['end_geometry']
P = dict(
    fret=k.tolist(), fret_x=n.FX[1:].tolist(), cell_length=length.tolist(), trough_behind_fret=(xb - mid).tolist(),
    depth_high_E=d_hiE.tolist(), depth_low_E=d_loE.tolist(),
    width_at_fret=n.width(n.FX[1:]).tolist(), radius_at_fret=n.radius(n.FX[1:]).tolist(),
    roll_radius=[g['roll_radius'] for g in eg], face_angle=[g['blend_angle'] for g in eg], turnover_radius=[g['top_radius'] for g in eg],
    steel_from_side=[g['seam_from_side'] for g in eg], full_height_from_side=[g['full_from_side'] for g in eg],
    back_depth=[float(n.depth(x)) for x in n.FX[1:]],
    hidden_below_deg=[g['hidden_below_deg'] for g in eg], full_steel_outside_high_E=R['full_height_margin_in'],
    constants=dict(land_each_side=n.P['land'], wire='Jescar FW43080-S 0.080 x 0.043 stainless', board=0.140,
                   rail_full_depth_in_from_side=e.S_RAIL1, scale=n.S, frets=int(n.NF)))
u = np.linspace(-1, 1, 4001)
P['back_offset_bass'] = [float(u[np.argmin(n.back(x, u))] * n.width(x) / 2) for x in n.FX[1:]]
assert abs(P['depth_high_E'][0] - 0.030) < 1e-6 and np.allclose(P['depth_high_E'], R['selected']['floor_high_E_in'])
json.dump(P, open(os.path.join(OUT, 'params.json'), 'w'), indent=1)

# ---------------------------------------------------------------- style (dark surface, reference palette dark steps)
SURF, INK, INK2, MUTED, GRID = '#1a1a19', '#f0efec', '#c3c2b7', '#8d8c85', '#2e2d2b'
S1, S2 = '#3987e5', '#d95926'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.facecolor': SURF, 'figure.facecolor': SURF,
                     'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'xtick.color': MUTED, 'ytick.color': MUTED,
                     'text.color': INK, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8})


def panel(ax, title, series, fmt, unit=''):
    for i, (lab, y, col) in enumerate(series):
        y = np.asarray(y)
        ax.plot(k, y, color=col, lw=2, solid_capstyle='round')
        for j in (0, 11, 21):
            ax.plot(k[j], y[j], 'o', ms=6, color=col, mec=SURF, mew=1.5)
            ax.annotate(fmt % y[j], (k[j], y[j]), textcoords='offset points',
                        xytext=(0, 9 if i == 0 else -16), ha='center', color=INK2, fontsize=10)
        if len(series) > 1:
            ax.annotate(lab, (k[-1], y[-1]), textcoords='offset points', xytext=(8, 0), va='center', color=INK2, fontsize=10)
    ax.set_title(title, loc='left', color=INK, fontsize=12, pad=8)
    ax.set_xlim(-0.6, 25.8 if len(series) > 1 else 23.2)
    ax.set_xticks([1, 5, 9, 12, 15, 17, 22])
    lo = min(np.min(s[1]) for s in series); hi = max(np.max(s[1]) for s in series); pad = (hi - lo) * 0.28 or abs(hi) * 0.1
    ax.set_ylim(lo - pad, hi + pad)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)


fig, axs = plt.subplots(3, 4, figsize=(20, 12.6))
panel(axs[0, 0], 'Scallop depth at the trough (in)', [('high E', d_hiE, S1), ('low E', d_loE, S2)], '%.3f')
panel(axs[0, 1], 'Trough behind the fret = half the cell (in)', [('', P['trough_behind_fret'], S1)], '%.3f')
panel(axs[0, 2], 'Board width at the fret (in)', [('', P['width_at_fret'], S1)], '%.3f')
panel(axs[0, 3], 'Board radius at the fret (in)', [('', P['radius_at_fret'], S1)], '%.2f')
panel(axs[1, 0], 'Fret-end face angle above level (deg)', [('', P['face_angle'], S1)], '%.0f°')
panel(axs[1, 1], 'Edge roll and turnover radius (in)', [('roll', P['roll_radius'], S1), ('turnover', P['turnover_radius'], S2)], '%.3f')
panel(axs[1, 2], 'Steel starts / full height, from the side (in)', [('full ht', P['full_height_from_side'], S1), ('steel', P['steel_from_side'], S2)], '%.3f')
panel(axs[1, 3], 'Full-height steel outside the high E (in)', [('', P['full_steel_outside_high_E'], S1)], '%.3f')
kb = slice(0, 15)
for ax, key, ttl, fm_ in ((axs[2, 0], 'back_depth', 'Neck depth on the centreline, wood only (in)', '%.3f'),
                          (axs[2, 1], 'back_offset_bass', 'Deepest point of the back, toward bass (in)', '%.3f')):
    y = np.asarray(P[key])
    ax.plot(k[kb], y[kb], color=S1, lw=2)
    ax.plot(k[14:], y[14:], color=S1, lw=2, ls=(0, (2, 3)), alpha=0.5)
    for j in (0, 11, 14):
        ax.plot(k[j], y[j], 'o', ms=6, color=S1, mec=SURF, mew=1.5)
        ax.annotate(fm_ % y[j], (k[j], y[j]), textcoords='offset points', xytext=(0, 9), ha='center', color=INK2, fontsize=10)
    ax.set_title(ttl, loc='left', color=INK, fontsize=12, pad=8); ax.set_xlim(-0.6, 23.2); ax.set_xticks([1, 5, 9, 12, 15, 17, 22])
    lo, hi = y.min(), y.max(); pad = (hi - lo) * 0.3 or 0.01; ax.set_ylim(lo - pad, hi + pad)
    ax.annotate('heel carve from fret 15', (17.5, lo + 0.15 * (hi - lo)), color=MUTED, fontsize=10, ha='center')
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
for ax in axs[2, 2:]:
    ax.axis('off')
axs[2, 2].text(0.0, 0.92, 'Back carve (neck v4, unchanged)', color=INK, fontsize=12, transform=axs[2, 2].transAxes, va='top')
axs[2, 2].text(0.0, 0.78, 'One rule nut to heel: full round C, fullness m 0.45,\n'
               'bass side fuller (eps 0.08 at the nut, 0 by fret 15),\n'
               'no shoulder corner: the back meets the side vertically.\n\n'
               'Not yet checked for thumb feel: there is no contact\n'
               'model of the back, and the shape waits on caliper\n'
               'readings of the reference neck (SPEC section 3).', color=INK2, fontsize=11, transform=axs[2, 2].transAxes, va='top', linespacing=1.5)
for ax in axs[2, :2]:
    ax.set_xlabel('fret', color=MUTED, fontsize=10)
for ax in axs[1]:
    ax.set_xlabel('fret (cell k = the space on the nut side of fret k)', color=MUTED, fontsize=10)
fig.suptitle('Supercaster II prototype fingerboard  ·  what changes from fret 1 to fret 22', x=0.01, ha='left', fontsize=16, color=INK)
fig.text(0.01, 0.925, 'Fixed everywhere: 25.5 scale, 22 frets, 0.140 rosewood, 0.055 flat land each side of every fret, '
         '0.080 × 0.043 stainless wire, level rail reaching full scallop depth 0.140 in from the side, scallop at the bass edge = half the treble.',
         ha='left', fontsize=11, color=INK2)
fig.tight_layout(rect=(0, 0, 1, 0.91), h_pad=2.2, w_pad=2.0)
fig.savefig(os.path.join(OUT, 'params.png'), dpi=110)
plt.close(fig)

# ---------------------------------------------------------------- plan view: depth below the cone
X, Yn = np.meshgrid(np.linspace(-0.05, n.X_BOARD_END, 2400), np.linspace(-0.5, 0.5, 361), indexing='ij')
W = n.width(X); Y = Yn * W
z, steel, wood = st.surface(X, Y, *PICK)
D = n.board(X, Y) - wood
D = np.where(steel, np.nan, D)
D = np.where(X < 0, np.nan, D)
cmap = LinearSegmentedColormap.from_list('seq', ['#26272a', '#1f4f86', '#3987e5', '#9cc3f2', '#eef5fd'])
fig, ax = plt.subplots(figsize=(22, 4.6))
# draw in board coordinates: x along, y as plotted (treble at the top)
m = ax.pcolormesh(X, -Y, D, cmap=cmap, vmin=0, vmax=0.055, shading='gouraud', rasterized=True)
for f in range(1, n.NF + 1):
    w = n.width(n.FX[f]) / 2
    ax.plot([n.FX[f]] * 2, [-w + 0.012, w - 0.012], color='#c9ccd1', lw=1.6)
xs = np.linspace(0, n.X_BOARD_END, 50); sy = n.string_y(xs)
for i in range(6):
    ax.plot(xs, -sy[i], color=INK2, lw=0.6 + 0.25 * i, alpha=0.45)
ax.plot(xs, n.width(xs) / 2, color=MUTED, lw=1); ax.plot(xs, -n.width(xs) / 2, color=MUTED, lw=1)
for f in (1, 3, 5, 7, 9, 12, 15, 17, 19, 21, 22):
    ax.text(n.FX[f], -n.width(n.FX[f]) / 2 - 0.09, str(f), ha='center', va='top', color=INK2, fontsize=10)
for kk in (1, 6, 12, 17, 22):
    x0 = 0.5 * (n.FX[kk - 1] + n.FX[kk])
    ax.annotate('%.3f' % d_hiE[kk - 1], (x0, -n.string_y(np.array([x0]))[0, 0]), textcoords='offset points', xytext=(0, 12),
                ha='center', color=INK, fontsize=10)
ax.text(-0.15, 0.62, 'treble', ha='right', va='center', color=INK2, fontsize=10)
ax.text(-0.15, -0.62, 'bass', ha='right', va='center', color=INK2, fontsize=10)
ax.set_aspect('equal'); ax.set_xlim(-0.9, n.X_BOARD_END + 0.2); ax.set_ylim(-1.35, 1.32); ax.axis('off')
cb = fig.colorbar(m, ax=ax, fraction=0.012, pad=0.01); cb.set_label('depth below the board radius (in)', color=INK2)
cb.ax.tick_params(colors=MUTED)
ax.set_title('Plan view, whole board, nut at left.  Colour = wood removed below the compound radius (scallop, rail and edge roll).  '
             'Numbers = depth under the high E at the trough.', loc='left', color=INK, fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'plan.png'), dpi=110)
print('wrote', OUT)
