"""Geometry for the Supercaster II vibroacoustic model.

Everything comes from body/carve/final_carve.py, imported READ-ONLY (no bytecode, no SC_* environment variables, so the
carve never rewrites its field cache). Coordinates: inches, x from the nut, y across (bass +), z up, body top plane z = 0.

The carve's chamber_interior() is keyed on h only, not on top_skin, so this module sets P['top_skin'], clears
final_carve._CHAMBER, evaluates, and restores the parameter. Results are cached in sim/cache/geom_*.npz.
"""
import os, sys, json, hashlib
import numpy as np

sys.dont_write_bytecode = True
for _k in list(os.environ):
    if _k.startswith('SC_'):
        raise RuntimeError(f'environment variable {_k} is set; it would change the carve and make it rewrite its cache')
SIM = os.path.dirname(os.path.abspath(__file__))
CARVE = os.path.join(os.path.dirname(SIM), 'carve')
CACHE = os.path.join(SIM, 'cache')
os.makedirs(CACHE, exist_ok=True)
IN = 0.0254

_FC = None
def fc():
    """The carve module (imported once, read-only)."""
    global _FC
    if _FC is None:
        if CARVE not in sys.path:
            sys.path.insert(0, CARVE)
        import final_carve as m
        _FC = m
    return _FC


def _key(d):
    return hashlib.sha1(json.dumps(d, sort_keys=True).encode()).hexdigest()[:12]


def chamber_floor(z_nominal, back_skin_mm):
    """Interior floor height in inches, relative to the 7 mm reference (z up)."""
    return z_nominal + (back_skin_mm - 7.0) / 25.4


def chamber_fields(top_skin_in=0.197, h=0.025):
    """Finished top/back and wing-chamber ceiling/floor on the carve's own grid at spacing h (inches).
    Returns dict: gx, gy, zt, zb, ch, zin_top, zin_back, sd (signed distance to the outline, + inside)."""
    key = dict(v=2, ts=round(top_skin_in, 5), h=h)
    fn = os.path.join(CACHE, f'geom_chamber_{_key(key)}.npz')
    if os.path.exists(fn):
        z = np.load(fn)
        return {k: z[k] for k in z.files}
    F = fc()
    old = F.P['top_skin']
    try:
        F.P['top_skin'] = top_skin_in
        F._CHAMBER.clear()
        C = F.chamber_interior(h=h)
        out = dict(gx=C['gx'], gy=C['gy'], zt=C['zt'], zb=C['zb'], ch=C['ch'], zin_top=C['zin_top'],
                   zin_back=C['zin_back'], sd=C['sd'])
    finally:
        F.P['top_skin'] = old
        F._CHAMBER.clear()
    np.savez_compressed(fn, **out)
    return out


def static_geometry():
    """Outline, guard, f-hole, jack, screws, routes (inches). Everything here comes from the carve module, which reads
    the plan file (see body/carve/bodylib.py)."""
    F = fc()
    g = dict(
        outline=np.asarray(F.OUTLINE), guard=np.asarray(F.GUARD), fhole=np.asarray(F.FHOLE_POLY), jack=np.asarray(F.JACK),
        thick=float(F.P['THICK']), top_half=float(F.P['top_half']),
        neck_pu=F.NECK_PU, mid_pu=F.MID_PU, bridge_pu=F.BRIDGE_PU, knobs=list(F.KNOBS),
        screws=list(F.SCREWS),                       # pickguard screws, from the plan file
        pivot_x=float(F.P['trem']['pivot_x']),       # nut to the trem pivot line, from the plan file
        trem={k: dict(F.P['trem'][k]) for k in ('slot', 'block', 'spring')},
        jack_center=tuple(F.P['jack_center']),
        control_cavity=[tuple(p) for p in F.BL.LANDMARKS.get('control_cavity', ())],
        jack_channel_end=tuple(F.BL.LANDMARKS.get('jack_channel_end', ())),
    )
    return g


def inside_poly(P, x, y):
    return fc()._inside(np.asarray(P), x, y)


def neck_tables():
    F = fc()
    return dict(fret_x=F.fret_x, neck_depth=F.neck_depth, neck_width=F.neck_width, body_end_x=F.body_end_x)
