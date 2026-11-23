#!/usr/bin/env python3
"""Chosen head-end rod path: relief table and where the adjuster hole leaves the headstock face.
Run: body/sim/cache/venv/bin/python -I -B neck/v4/optimize/rod_final.py   (imports rod_opt.py; edits nothing)"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rod_opt as R
N = R.N
HOLE = 9 / 32          # access hole for a 3/16 rod's hex-socket adjusting nut (ASSUMED 1/4 OD nut, VERIFY on the part)
F_STEP, T_HEAD, BOARD = 0.352, 0.54, 0.140
out = {}
for zh in (-0.36, -0.40):
    xh, xa, za, skew = 0.45, 17.5, -0.50, 0.3
    sag = R.max_sag(xh, zh, xa, za, skew)
    R.set_rod(xh, zh, xa, za, sag, skew)
    eta, rel, season = R.authority()
    x = np.arange(xh, xa, 0.02); z = R.rod_z(x); d1 = np.gradient(z, x); d2 = np.gradient(d1, x)
    slope = float(-d1[0])                       # rise toward the head, in per in
    z_nut = zh + slope * xh                     # hole axis at the nut line (z = 0 is the board top at the nut)
    row = dict(zh=zh, sag=sag, eta_per_100lb=eta * 100, relief_Eb=rel['Eb'][0], relief_dropCs=rel['dropCs'][0], season=season,
               slope_head=slope, R_min=float(1 / np.abs(d2).max()), z_deepest=float(z.min()), x_deepest=float(x[z.argmin()]),
               under_min=float(R.under_wood(np.arange(xh, N.XC, 0.05)).min()), axis_at_nut=z_nut,
               web_under_glue_line=float(-BOARD - (z_nut + HOLE / 2)))
    for tilt in (2.0, 2.5):
        tt = math.tan(math.radians(tilt))
        # behind the nut (distance s toward the head): face z = -F_STEP - tt s ; hole bottom z = z_nut - HOLE/2 + slope s
        s_exit = (-F_STEP - (z_nut - HOLE / 2)) / (slope + tt)
        row[f'trough_len_tilt{tilt}'] = s_exit
        row[f'trough_depth_at_nut_tilt{tilt}'] = -F_STEP - (z_nut - HOLE / 2)
        row[f'head_left_under_trough_tilt{tilt}'] = T_HEAD - row[f'trough_depth_at_nut_tilt{tilt}']
    row['table'] = R.table(eta, rel['Eb'][0], season)
    out[str(zh)] = row
    print(f"\nzh {zh}: sag {sag:.3f}, {eta*100:.5f} in per 100 lb, string relief Eb {rel['Eb'][0]:.4f} / drop C# {rel['dropCs'][0]:.4f}, season +/-{season:.4f}")
    print(f"  deepest {row['z_deepest']:.3f} at x {row['x_deepest']:.2f}, min bend radius {row['R_min']:.0f}, maple under channel {row['under_min']:.3f}")
    print(f"  head-end slope {slope:.3f} ({math.degrees(math.atan(slope)):.1f} deg), hole axis at nut line {z_nut:.3f}, maple between hole and glue line {row['web_under_glue_line']:.3f}")
    for tilt in (2.0, 2.5):
        print(f"  tilt {tilt}: trough {row[f'trough_depth_at_nut_tilt{tilt}']:.3f} deep at the nut, runs out {row[f'trough_len_tilt{tilt}']:.2f} behind it, head left under it {row[f'head_left_under_trough_tilt{tilt}']:.3f}")
    print("  built-in  slack   F@0.012  F dry  F wet   max relief (dry, 40 lb)")
    for t in row['table']:
        print(f"  {t['built_in']:.3f}    {t['slack']:.4f}  {t['F_target']:6.0f}  {t['F_dry']:6.0f} {t['F_wet']:6.0f}   {t['max_relief_worst']:.4f}")
json.dump(out, open(os.path.join(HERE, 'rod_final.json'), 'w'), indent=1, default=float)
