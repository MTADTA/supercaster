"""Design definitions for run_case.py.

A design is a dict of overrides on BASE. Lengths: mm for skins, liners and walls; inches for positions.
Add a design by adding an entry to DESIGNS (or pass --set key=value on the command line).

Reference builds (from the surviving reports, body/acoustics/):
  final_narrowed  the build in acoustic-hybrid.md section 0: 5.0 mm top + 0.6 mm cross-grain maple veneer under the roof,
                  7 mm back, solid tail, narrowed liner 0.75 in deep, inner wall inset 2.7 mm, 2 mm outer wall.
  final_plain     same build, plain liner (no inset).
  final_bare      same build, no liner.
  current         the sim3d 'baseline': 4 mm top, no veneer, 7 mm back, plain 0.75 in liner.
  solid           no chamber, no f-hole (the solid reference). Same hardware.
  *_locked        tremolo locked to the body (hard-tail proxy, for comparison with published solid-body bridge data).
"""
import copy

BASE = dict(
    # --- body interior (hidden) ---
    chamber=True,            # bass-wing chamber per final_carve.chamber_interior
    top_skin_mm=5.0,         # top skin over the chamber, perpendicular to the finished top
    back_skin_mm=7.0,        # back skin (the carve's own back_skin is 7 mm; other values shift the floor)
    veneer_mm=0.6,           # cross-grain maple veneer glued under the chamber roof (0 = none)
    fhole=True,
    liner='narrowed',        # 'narrowed' | 'plain' | 'bare'
    liner_depth_mm=19.05,    # below the underside of the roof (veneer)
    liner_inset_mm=2.7,      # inner wall inset from the traced outline (narrowed only)
    liner_tool_radius_mm=0.0, # optional single rounded pocket in the compliant insert
    liner_wall_mm=2.0,       # liner wood outside the outline
    liner_structural=False,  # False: liner is mass only (as in the reference study); True: wood elements glued to the roof
    tongue_end_x=21.7,       # set-neck tongue end (maple elements in the centre block)
    # --- hardware ---
    trem='floating',         # 'floating' | 'locked'
    trem_mass_kg=0.36,
    pivot_k=5.0e6,           # N/m per pivot screw, along-string and vertical (study's guess)
    pivot_eta=0.05,          # pivot loss factor (study's guess; check suggests 0.05-0.30)
    n_springs=3, spring_k=2.0e3,  # N/m per trem spring [judged]
    tuner_g=30.0,            # per tuner
    guard=True,
    guard_contact=2.0e8,     # N/m^3 normal contact stiffness between guard and top away from the screws [judged]
    # --- player ---
    hold='held',             # 'held' | 'free' | 'firm' (contacts x3)
    # --- materials ---
    wood='reference',        # 'reference': the reference study's values (E_R = E_T = 0.07 E_L); 'json': acoustics/inputs/wood-properties.json
    # --- material scale factors (Monte Carlo and sensitivity) ---
    alder_E=1.0, alder_rho=1.0, alder_cross=1.0, maple_E=1.0, maple_rho=1.0, wood_eta=1.0,
    air_mass=1.0,            # multiplies the exterior end correction of the f-hole
    air_eta=0.008,           # base air loss factor added to every cavity mode (wall heat conduction, leaks) [judged]
    liner_friction=1.0,      # multiplies the computed boundary-layer resistance of hole and throat
    # --- neck / trem / guard study options (STUDIES-neck-trem-guard.md). Defaults reproduce the validated-run models. ---
    neck_curly=False,        # wood='json' only: neck and tenon from hard_maple_roasted_curly_neck instead of straight roasted maple
    truss_rod='none',        # 'none' | 'oneway_steel' | 'twoway_steel' | 'twoway_ti'
    rod_coupling='tendon',   # 'mass' (mass only) | 'tendon' (mass + own bending + anchored axial spring) | 'bonded' (full composite)
    carbon_rods=False,       # two 1/8 x 3/8 in pultruded carbon bars epoxied either side of the rod
    trem_block='default',    # 'default' (0.36 kg scaled as before) | 'steel' | 'ti' | 'brass' (same dimensions, block mass by density)
    guard_bosses='none',     # 'none' | 'hanging' (19 mm deep solid boss under each chamber screw) | 'post' (boss to the floor)
    guard_screws='all',      # 'all' (13, plan file) | 'no_chamber' (drop the screws over the chamber)
    guard_screw_k=0.0,       # 0 = screws rigidly merged (as before); >0 = screw joint spring N/m (torque proxy)
    # --- numerics ---
    h_struct=1 / 6,          # structural plan mesh (in)
    h_air=0.1,               # air finite-volume plan grid (in)
    fmax_modes=2200.0,       # structural modes kept (Hz)
)

DESIGNS = {
    'final_narrowed': {},
    'final_plain': dict(liner='plain'),
    'final_bare': dict(liner='bare'),
    'current': dict(top_skin_mm=4.0, veneer_mm=0.0, liner='plain'),
    'current_bare': dict(top_skin_mm=4.0, veneer_mm=0.0, liner='bare'),
    'solid': dict(chamber=False, fhole=False, veneer_mm=0.0, liner='bare'),
    'final_narrowed_locked': dict(trem='locked'),
    'solid_locked': dict(chamber=False, fhole=False, veneer_mm=0.0, liner='bare', trem='locked'),
    'final_narrowed_free': dict(hold='free'),
    'final_narrowed_liner_wood': dict(liner_structural=True),
    'final_narrowed_fine': dict(h_struct=1 / 8, h_air=0.05),
}


def get(name, overrides=None):
    if name not in DESIGNS:
        raise KeyError(f'unknown design {name!r}; known: {sorted(DESIGNS)}')
    d = copy.deepcopy(BASE)
    d.update(DESIGNS[name])
    if overrides:
        for k, v in overrides.items():
            if k not in BASE:
                raise KeyError(f'unknown design key {k!r}')
            d[k] = type(BASE[k])(v) if not isinstance(BASE[k], bool) else (str(v).lower() in ('1', 'true', 'yes'))
    d['name'] = name
    return d
