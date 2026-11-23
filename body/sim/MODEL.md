# Supercaster II vibroacoustic model (body/sim)

**Status: NOT VALIDATED.** Air (A0), the 80-200, 200-300 and 500-1000 Hz bands, and the solid-versus-chambered
differences in those three bands reproduce the earlier study. The body's twisting mode (+29 Hz) and the 300-500 Hz band
(-6.5 to +2.7 dB) do not. Those two numbers carry the liner tuning argument, so the model is not validated for it.
Section 3 has the full table.

Tags: [computed] = this model; [literature: source] = a number actually read in that source; [judged] = my choice;
"as quoted in X, not re-read" = a published number taken second-hand from the earlier reports.

## 1. How to run

```
cd body/sim
cache/venv/bin/python -I -B run_case.py --list                      # designs in designs.py
cache/venv/bin/python -I -B run_case.py --design final_narrowed     # about 65 s first time, a few s from cache
cache/venv/bin/python -I -B run_case.py --design final_narrowed --set top_skin_mm=4.5 --set liner_inset_mm=2.9 --tag t45
cache/venv/bin/python -I -B validate.py                              # compares results/*.json with the reference numbers
cache/venv/bin/python -I -B validate.py --run                        # runs the eight validation designs first
```

- Python 3.11 venv in `cache/venv` (numpy 2.4, scipy 1.17, pymetis). Always run with `-I -B`.
- Never set `SC_*` environment variables; `geom.py` refuses to run if any is set.
- Output: `results/<design>[_<tag>].json`, with spectra in a `.npz` next to it (f, mean radiated power, saddle and
  fret conductance, port flow).
- Peak memory is about 4.2 GB at the working mesh (h_struct 1/6 in). Do not run two cases in parallel on this machine.
- **Adding a design:** add an entry to `DESIGNS` in `designs.py` (it overrides `BASE`), or use `--set key=value` with any
  `BASE` key. Unknown keys are refused.
- **Caching.** Structural modes and their projections go in `cache/modes_<key>.npz`, keyed on every structural input
  (`model.struct_key`). Air-only and damping-only keys re-run in a few seconds: `liner_friction`, `air_eta`, `air_mass`,
  `wood_eta`, `pivot_eta`, `h_air`. The exterior BEM (`cache/bem_body_v1.npz`, 335 MB) is shared by every design,
  because the outside of the body never changes. The cache is 0.7 GB now, about 20 MB per new structural design. Delete
  `cache/modes_*.npz` if it nears 3 GB.
- **Materials.** `wood='reference'` (the default) uses the earlier study's values, E_R = E_T = 0.07 E_L. Use it to
  compare with the old numbers. `wood='json'` uses `acoustics/inputs/wood-properties.json`: roasted alder and roasted
  hard maple with their full orthotropic sets, a 0.6 mm maple veneer, and rosewood. Its loss factor is eta_L [judged].

### Main JSON fields

| Field | Meaning |
|---|---|
| `power_dB_re_1pW_per_N2` | Radiated power, 80-200 / 200-300 / 300-500 / 500-1000 Hz. Band mean of W on a 0.5 Hz grid, then the mean over six vertical unit saddle forces, in dB re 1 pW/N² |
| `power_dB_per_saddle` | The same, for each saddle |
| `A0` | Coupled air resonance and its Q from the complex eigenvalues. Also the rigid-wall value, the boundary-layer-corrected value, the port-flow peak, volume, open hole and throat area |
| `modes` | Structural modes to 1.1 kHz: f, modal loss, kinetic-energy shares (body, bass wing, guard, neck, trem), twist index (share of top-plate uz explained by an x·y term after removing the rigid plane), rigid share, label = largest share |
| `twist_mode` | Body mode with the highest twist index between 200 and 400 Hz |
| `bridge_conductance_s_per_kg` | Vertical driving-point Re(Y) per saddle: peak, frequency, median, band means; along-string and sideways peaks |
| `fret_conductance_s_per_kg` | Vertical Re(Y) on the board at the nut and frets 1-12 under each string |
| `notes` | 78 fundamentals (6 strings × open to fret 12): level, bridge and fret conductance, body-only T60 = 6.91 L/(T G), and whether G passes the halving budget |
| `velocity_dB_re_1mps_per_N` | Band velocity at the belly patch, forearm patch, neck back at fret 7, and mid-chamber top |
| `sum_rule` | Integral of the mean saddle conductance against the uncoupled modal sum; it should be about 1 |
| `mass_kg`, `balance_x_in` | From the mass matrix |

## 2. What is modelled and how

| Part | Method |
|---|---|
| Body | Layered 8-node hex mesh on a 1/6 in plan grid, 8 node levels following the real carve (`carve/final_carve.py`, imported read-only): finished top and back, chamber roof and floor, skin and veneer thicknesses. The skins are one QM6 element through the thickness (Wilson-Taylor incompatible modes, Taylor centroid correction). This was checked exact on a cantilever (0.0012796 against beam theory 0.00128) [computed]. Orthotropic alder: L along the body, T across, R through the thickness. Maple set-neck tenon and tongue in the top three layers. The 0.6 mm veneer is cross-grain maple. Routes: neck, middle and humbucker pockets, top slot and block cavity, spring cavity, control capsule, jack. |
| Pickguard | 2.3 mm hex layer [judged], merged to the top at the 13 screws (plan file), with normal contact springs elsewhere (2e8 N/m³ [judged], tangential 0.1×). Pickups and controls are masses on the guard. |
| Neck | 28-node 3-D Timoshenko beam from rasterised composite sections: rosewood board on a maple C, depth and width from the carve tables, headstock plate from `src/neck-geometry.js`. Six 30 g tuners as offset point masses. RBE2 joint into the body block. |
| Tremolo | 6-dof rigid body, 0.36 kg, real part geometry. Six pivot springs (5e6 N/m, eta 0.05 [judged, study's guess]), three springs to the claw, six strings as axial steel springs from saddle to nut. `trem='locked'` stiffens pivots and springs ×100. |
| Player | Spring-dashpot patches at belly, forearm, thigh and chest, plus the fretting hand at fret 5 (the study's contacts). `hold='free'` removes them; `hold='firm'` is ×3. |
| Damping | Modal loss from group strain energy: eta_m = Σ_g eta_g φᵀK_gφ / λ_m. Alder 0.010, maple 0.008 (reference set), guard 0.05, guard contact 0.10, springs 0.01 [judged]. Player dashpots are projected in full (Φᵀ C Φ). |
| Modes | Shift-invert Lanczos, METIS nested-dissection ordering, SuperLU. 132,138 dof; 160 modes to 2.39 kHz in 28 s. |
| Chamber air | Finite-volume network on 0.1 in columns that follow the roof and floor. Separate stacks for the hole neck, the throat inside the liner, the dead air outside it and the chamber below. Throat open fractions come from a 0.004 in raster of the traced f-hole. The exterior is the one-sided radiation conductance of the traced hole, from an integral equation (K1 = 0.1425 m against 0.1428 in the earlier study; 1.377 × an equal-area circle) [computed]. Losses: boundary-layer friction on the hole and throat walls, radiation, wall heat conduction, plus 0.008 base [judged]. The boundary-layer reactance lowers each mode by eta_visc/2. 16 rigid-wall modes. |
| Coupling | Signed moving-wall areas (roof and liner mouth, floor) interpolated from the structural roof and floor nodes, projected on both mode sets. (K − ω²M + iωC)u + Wᵀp = f, (Γ − ω²C)p + ω²Wu = 0. |
| Radiation | Exterior BEM on the closed body surface (top, back, two-row side wall): 2,288 constant triangles, conventional integral equation (no fictitious frequencies below about 3.5 kHz). Radiation resistance matrix R at 34 frequencies (50-1150 Hz), interpolated as R/f². The f-hole panels carry the port volume flow. Panels under the guard move with the guard. The neck and headstock do not radiate. Checked [computed]: pulsating and oscillating sphere within 0.06 dB (100-1000 Hz); thin disc dipole +0.6 / +0.75 dB. A free-field monopole sum would be about 25 dB low for this thin body. |

## 3. Validation

Reference numbers are the earlier study's computed results, read from `acoustics/sim3d-REPORT.md`, `sim3d-CHECK.md`,
`final/liner-RESULT.md` and `final/liner-CHECK.md`. Tolerances were fixed before comparing: A0 ±2 %, twisting mode
±10 Hz, absolute bands ±1.5 dB, design differences ±1 dB. No parameter was tuned to these targets. All model numbers
are [computed] with `wood='reference'` on the working mesh; `results/validation.json` holds the table.

| Check | Reference | This model | Result |
|---|---|---|---|
| A0 bare liner (final build) | 377.1 Hz | 372.6 Hz (rigid 379.0) | pass, −1.2 % |
| A0 plain liner | 325.7 | 321.5 (rigid 325.5) | pass, −1.3 % |
| A0 narrowed liner (2.7 mm inset) | 285.8 (rigid FV 286.8-288.8) | 278.8 (rigid 284.8, Q 32.5) | **fail, −2.5 %** |
| A0 current (4 mm top, plain) | 319.6 | 315.0 | pass, −1.4 % |
| Bands 80-200 Hz, four builds | 45.7-45.9 dB | 46.0-46.4 | pass (+0.3 to +0.5) |
| Bands 200-300 Hz, four builds | narrowed 56.2, plain 52.4, bare 52.1, current 53.0 | 55.6, 53.1, 52.7, 53.5 | pass (−0.6 to +0.6) |
| Bands 300-500 Hz | 65.5, 69.5, 62.3, 67.4 | 60.9, 63.0, 65.0, 64.7 | **fail (−6.5 to +2.7)** |
| Bands 500-1000 Hz | 67.3, 67.1, 67.7, 67.8 | 66.4, 66.1, 67.0, 66.25 | pass except current (−1.55) |
| Narrowed − plain, 200-300 Hz | +3.8 dB | +2.5 | **fail (−1.3)** |
| Solid − current, four bands | −2.2 / −3.6 / −8.7 / −2.5 | −2.6 / −4.0 / −6.2 / −2.55 | pass, pass, **fail (+2.5)**, pass |
| Twisting mode, current build held | 287.9 Hz (287.4 free) | 317.1 Hz (twist index 0.87; body 59 %, neck 24 %, guard 16 %) | **fail, +29 Hz** |
| Twisting mode, final narrowed | 283-288 | 319.8 | **fail** |
| Sum rule (conductance integral / modal sum) | 1 | 1.00 | pass |
| Mass, current build | 2.938 kg | 2.660 kg | −9.5 % (not graded) |
| Bridge peak Gz, current | 1.8e-2 s/kg at 659 Hz | 1.34e-2 at 606 Hz (E2 saddle) | same order (not graded) |
| Bridge band means, current, mean of 6 saddles | about 1.2e-4 / 1.9e-4 / 7.7e-4 / 1.2e-3 (table in sim3d-REPORT 3.3) | 9.4e-5 / 1.1e-4 / 9.1e-4 / 1.4e-3 | same order |
| Notes past halving, current | 21 of 78 | 17 | not graded |
| Locked trem, bridge peak | published solid-body maximum 1.8e-3 (as quoted in sim3d-REPORT 3.3, not re-read) | 1.3e-2 (final narrowed), 1.9e-2 (solid) | **7-10× high**: the peaks are not the floating trem alone |
| Neck fret conductance peak | published up to about 0.1 s/kg (as quoted in sim3d-REPORT 3.3, not re-read) | 0.18 (nut), 0.07 at fret 6 | same order |

18 of 28 graded checks pass.

**Why it is not validated.** In the earlier study the plain liner's A0 (326 Hz) sat on body modes at 288-314 Hz, and
the narrowed liner moved A0 onto the 288 Hz twisting mode. Here the twisting mode is at 317-320 Hz. So the plain liner
already lands on it, and the narrowing moves A0 off it. That one difference explains the failed 300-500 Hz band, the
smaller narrowed-minus-plain gain (+2.5 against +3.8 dB) and the solid-minus-current 300-500 Hz difference. The air side
is not the cause: A0 is within 1.2-1.4 % for three of four builds, and the narrowed build fails mainly because the
softer walls pull it 4.7 Hz below its rigid-wall value.

**How the twisting mode was identified.** The label is the largest kinetic-energy share. The twisting mode is the
body mode (body plus wing kinetic energy > 0.3) with the highest twist index between 200 and 400 Hz. Strain-energy
shares from the group matrices confirm the choice [computed] (`cache/t_twist.py`):

| Build | Mode | Strain energy body / guard / neck beam | Twist index | Coupling to the air mode |Cp0| |
|---|---|---|---|---|
| current | 287.3 Hz | 0.22 / 0.01 / 0.77 | 0.73 | 9.3 |
| current | **317.1 Hz** | 0.61 / 0.15 / 0.23 | 0.87 | 22.0 |
| final narrowed | 288.1 Hz | 0.19 / 0.01 / 0.79 | 0.73 | 6.6 |
| final narrowed | **319.8 Hz** | 0.61 / 0.17 / 0.21 | 0.92 | 19.5 |

The 288 Hz mode lands on the old frequency, but it is a neck mode: 77-79 % of its strain is in the neck, and the
body only twists passively. The earlier check called its 288 Hz mode "95 % body twist". The body twist here is the
317-320 Hz mode, and the air couples to it about twice as strongly. So the twisting-mode check fails. The model has
the same family of modes as the old one, but in a different order around 290-320 Hz.

**Sensitivity, not calibration:** pickguard contact ×0.1 (current build, `results/current_gc01.json`). Guard modes
appear at 150-307 Hz, close to the old model's guard modes (122-261 Hz). The twisting mode moves up, to 322.6 Hz,
where the earlier check saw it go down to 272 Hz. The bands move +2.2 / +1.1 / −0.2 / +0.6 dB [computed].

Other suspects, not tested: the mass is 0.28 kg short (no truss rod, frets, finish, strings, knobs, switch, jack or
strap buttons); the neck's torsion constant J = A⁴/(40 Ip) and the tuner lumping [judged], which control how much of
the twist the neck takes; and alder G_LT. None was changed to chase the target. The earlier check already put the real
mode at "about ±15 Hz", so a tap test (sim3d-CHECK item 1) decides between 288 and 320. The full mass breakdown has
only been run on a 1/4 in mesh, where it gave 2.81 kg; the working mesh gives 2.69 kg for the final build.

## 4. Limits

- Not validated for the twisting-mode and 300-500 Hz results (section 3). The 200-300 Hz liner gain depends on where the
  twisting mode really is, so measure it before trusting any liner gain from this model or the old one.
- Bridge conductance peaks (1e-2 s/kg at 500-650 Hz) are several times the published solid-body values, even with the
  trem locked. Pivot friction is not modelled, and the guard's flapping modes (eta 0.05-0.09) sit in the same range.
  Decay and halving counts are pessimistic.
- Constant modal loss factors (air losses evaluated at each mode's own frequency). No static correction for truncated
  modes; structural modes to 2.4 kHz, 16 air modes.
- The neck, headstock and player do not radiate or load the air. No room. Radiation does not load the structure back.
- One air network grid (0.1 in). It converges to 0.5-1 Hz against 0.05 in for A0 [computed].
- No Monte Carlo yet. The group matrices are available in `model.build` (`B['groups']`) for a Ritz-projected scheme.
- Balance point: 18.8 in from the nut here, against 15.51 reported by the old model. The old figure was not checked.

## 5. Files

`geom.py` carve and static geometry · `materials.py` wood sets · `fe.py` elements · `model.py` structure and modes ·
`air.py` chamber network · `bem.py`, `surface.py` radiation · `rom.py` coupled solve and outputs · `designs.py` ·
`run_case.py` · `validate.py` · `results/` · `cache/` (venv, BEM, mode caches, test scripts `t_*.py`).

## 6. Study options added 2026-11-13 (STUDIES-neck-trem-guard.md)

All default to the behaviour above, and are hashed into the cache key only when not default, so the validation
caches and `results/validation.json` are unchanged (re-checked: 18 of 28).

| Key | Values | What it does |
|---|---|---|
| `neck_curly` | bool | `wood=json` only: neck beam and tenon from `hard_maple_roasted_curly_neck` (E_L 12.4 GPa, eta 0.0099) |
| `truss_rod` | none, oneway_steel, twoway_steel, twoway_ti | rod in the neck beam sections from the nut to the joint (slot maple removed), adjuster and anchor masses |
| `rod_coupling` | mass, tendon (default), bonded | rod as mass only / mass + its own bending + anchored axial spring EA/L at rod height / full composite |
| `carbon_rods` | bool | two bonded 1/8 x 3/8 in pultruded carbon bars beside the rod |
| `trem_block` | default, steel, ti, brass | same block dimensions, block mass from density; plate and saddles unscaled |
| `guard_bosses` | none, hanging, post | 1/2 in alder bosses under the guard screws that land over the chamber: 19 mm deep, or down to the floor |
| `guard_screws` | all, no_chamber | drop the screws over the chamber |
| `guard_screw_k` | 0 or N/m | 0 = rigid merge (as before); otherwise a screw spring (group `screws`, eta 0.05 [judged]) |

**Behaviour change:** `maple_E` and `maple_rho` now scale the neck beam as well as the maple tenon. Before this they
scaled only the tenon, so a ±10 % maple bracket moved the neck modes by about 0.3 %. No validated result used them.

New scripts: `study_summary.py`, `study_deadspots.py` (fret and bridge conductance read over a ±10 % window; `--ts` sets the string decay) and `study_room.py` (field
pressure by the Kirchhoff-Helmholtz integral over the BEM panels plus a diffuse room; checked on pulsating and
oscillating spheres within 0.07 dB, and its radiated power agrees with `run_case` bands within 0.6 dB). Batches:
`cache/batch_studies.sh`, `cache/batch2.sh`.
