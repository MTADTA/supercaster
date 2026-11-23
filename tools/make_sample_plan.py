"""Write body/plan.sample.json: SYNTHETIC SAMPLE DATA for the body scripts.

The real plan data (body outline, pickguard, jack recess, screw, hardware and landmark positions, tremolo routes) is not
published, because it was traced or measured from third-party plans of a commercial guitar. This script invents a
stand-in from a handful of made-up control points and made-up layout numbers, so the file format is documented and the
code has something to load. It is a generic double-cutaway blob. It is NOT the Supercaster outline or layout, and
nothing computed from it describes the design.

Frame: inches, x from the nut along the neck, y across (bass side +).
Run: python3 tools/make_sample_plan.py        (standard library only)
"""
import json, math
from pathlib import Path

C = (23.0, 0.0)   # pole of the polar outline
# (angle in degrees from the direction of the nut, + toward the bass side; radius in inches). Made-up values.
CTRL = [(0, 7.3), (7, 7.3), (15, 6.0), (22, 5.6), (30, 9.0), (36, 10.2), (43, 9.2), (58, 6.4), (78, 5.6), (100, 5.9),
        (125, 7.6), (150, 8.3), (180, 8.1), (210, 8.2), (235, 7.5), (260, 5.8), (282, 5.4), (302, 6.2), (316, 7.6),
        (323, 8.2), (330, 7.6), (338, 5.6), (346, 6.0), (353, 7.3)]


def radius(deg):
    """Periodic Catmull-Rom spline through CTRL."""
    n = len(CTRL)
    for i in range(n):
        a0, r1 = CTRL[i]; a1, r2 = CTRL[(i + 1) % n]
        if a1 <= a0: a1 += 360
        d = deg if deg >= a0 else deg + 360
        if a0 <= d <= a1:
            am, r0 = CTRL[i - 1]; ap, r3 = CTRL[(i + 2) % n]
            if am > a0: am -= 360
            if ap < a1: ap += 360
            t = (d - a0) / (a1 - a0)
            m1 = (r2 - r0) / (a1 - am) * (a1 - a0); m2 = (r3 - r1) / (ap - a0) * (a1 - a0)
            return ((2 * t**3 - 3 * t**2 + 1) * r1 + (t**3 - 2 * t**2 + t) * m1
                    + (-2 * t**3 + 3 * t**2) * r2 + (t**3 - t**2) * m2)
    raise ValueError(deg)


def ellipse(cx, cy, a, b, rot_deg=0.0, n=48):
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    out = []
    for k in range(n):
        t = 2 * math.pi * k / n; u, v = a * math.cos(t), b * math.sin(t)
        out.append([round(cx + u * c - v * s, 3), round(cy + u * s + v * c, 3)])
    return out


outline = []
for k in range(180):
    deg = 2.0 * k; r = radius(deg); t = math.radians(deg)
    outline.append([round(C[0] - r * math.cos(t), 3), round(C[1] + r * math.sin(t), 3)])

# Landmarks are read off the made-up outline, so they are consistent with it.
tail = max(outline, key=lambda p: p[0]); horn = min(outline, key=lambda p: p[0])
waist = max((p for p in outline if p[1] < 0 and 20.0 < p[0] < 23.0), key=lambda p: p[1])
JACK_C = [27.4, -3.9]
KNOBS = [[24.0, -2.4], [24.9, -3.4], [25.8, -4.1]]

plan = dict(
    sample=True,
    note='SYNTHETIC SAMPLE DATA from tools/make_sample_plan.py. Not the Supercaster outline. Format example only.',
    units='in, x from the nut along the neck, y across (bass +)',
    OUTLINE=outline,
    GUARD=ellipse(22.3, -1.3, 4.3, 2.9),
    JACK=ellipse(JACK_C[0], JACK_C[1], 1.0, 0.5, -45, 32),
    SCREWS=[[round(22.3 + 4.0 * math.cos(2 * math.pi * k / 8), 2), round(-1.3 + 2.6 * math.sin(2 * math.pi * k / 8), 2)] for k in range(8)],
    FHOLE_B1=[21.1, 3.3], FHOLE_B2=[24.5, 4.5],
    NECK_PU=18.9, MID_PU=21.2, BRIDGE_PU=[23.4, 0.0],
    PLATE=dict(x0=24.7, x1=26.2, hw=1.5),
    KNOBS=KNOBS,
    ARM_LINE=[[23.8, 5.1], [30.4, -1.3]],
    # Landmarks on (or tuned to) the outline. belly_guide = first and last outline vertex of the outer bass edge guide.
    LANDMARKS=dict(
        jack_center=JACK_C, horn_c=[15.2, 5.3], belly_guide=[outline[24], outline[75]], tail_x=tail[0],
        horn_button=horn, waist=waist,
        control_cavity=[[20.2, -2.9], [21.6, -3.0], [22.9, -3.5]] + KNOBS,      # optional: centre line of the control cavity
        jack_channel_end=[26.6, -4.4],                                           # optional: jack channel runs from jack_center to here
    ),
    # Named report stations: here simply outline vertices picked by index.
    STATIONS={name: outline[k] for name, k in dict(
        bass_horn=20, bass_upper_bout=35, fhole_side=60, forearm_start_edge=72, forearm_deepest=80, tail=92,
        treble_waist=130, treble_cutaway=165, fhole_pinch=66, facet_full=75, treble_lower_bout=105, bass_cutaway=10,
        thigh_rest=125, rib_contact=30).items()},
    # Tremolo routes: pivot line and three rounded boxes (x0, x1, half-width hw about yc, corner r, z from the body top).
    TREM=dict(
        pivot_x=25.0, pivot_pitch=0.42,
        slot=dict(x0=25.4, x1=26.0, hw=1.5, yc=-0.15, r=0.25, z_top=0.0, z_bot=-1.1),
        block=dict(x0=25.4, x1=26.4, hw=1.5, yc=-0.15, r=0.25, z_top=-0.2, z_bot=-1.75),
        spring=dict(x0=21.6, x1=25.4, hw=1.1, yc=0.0, r=0.25, z_top=-1.1, z_bot=-1.75),
    ),
)
out = Path(__file__).resolve().parent.parent / 'body' / 'plan.sample.json'
out.write_text(json.dumps(plan, indent=1) + '\n')
print('wrote', out, '(synthetic sample data)')
