"""Body volume columns from the final carve, for the weight-and-balance model.
Imports body/carve/final_carve.py and bodylib.py READ-ONLY (never edits them). Writes one small .npz per carve variant here.
Run: <venv>/bin/python -I -B body_fields.py <tag>      (env SC_ARM_DEPTH / SC_BELLY select the carve variant, as in final_carve)
Coordinates: inches, x from the nut, y bass +, z up, body top plane z = 0, back plane z = -1.75."""
import sys, os
import numpy as np
CARVE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'carve')
sys.path.insert(0, CARVE)
import final_carve as F
import bodylib as BL
tag = sys.argv[1] if len(sys.argv) > 1 else 'final'
C = F.chamber_interior()                      # h = 0.025 grid, finished top/back incl. edge roll, wing chamber as cut
h = C['h']; X, Y = C['X'], C['Y']; ins = C['sd'] > 0
zt, zb = C['zt'], C['zb']
t = np.where(ins, np.clip(zt - zb, 0, None), 0.0)                 # solid-body column thickness
zc = np.where(ins, 0.5 * (zt + zb), 0.0)
ch = C['ch']; ct = np.where(ch, np.clip(C['zin_top'] - C['zin_back'], 0, None), 0.0)   # chamber column height
cz = np.where(ch, 0.5 * (C['zin_top'] + C['zin_back']), 0.0)
fh = BL.fhole_mask(X, Y) & ch                                      # f-hole cut through the chamber roof
fht = np.where(fh, np.clip(zt - C['zin_top'], 0, None), 0.0); fhz = np.where(fh, 0.5 * (zt + C['zin_top']), 0.0)
roof_z = np.where(ch, C['zin_top'], 0.0)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'body_{tag}.npz')
np.savez_compressed(out, h=h, X=X.astype(np.float32), Y=Y.astype(np.float32), t=t.astype(np.float32), zc=zc.astype(np.float32),
                    ch=ch, ct=ct.astype(np.float32), cz=cz.astype(np.float32), fh=fh, fht=fht.astype(np.float32), fhz=fhz.astype(np.float32),
                    roof_z=roof_z.astype(np.float32), body_end_x0=float(F.body_end_x(0.0)), arm_depth=float(F.P['arm_depth']),
                    belly=str(F.P['belly_mode']), top_skin=float(F.P['top_skin']))
print(tag, 'solid in3 %.1f' % (t.sum() * h * h), 'chamber in3 %.2f' % (ct.sum() * h * h), 'chamber area in2 %.1f' % (ch.sum() * h * h),
      'fhole in3 %.3f' % (fht.sum() * h * h), 'body_end_x0 %.3f' % F.body_end_x(0.0), 'arm', F.P['arm_depth'], 'belly', F.P['belly_mode'])
