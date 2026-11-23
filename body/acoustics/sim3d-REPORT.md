# Supercaster II: 3-D structure + air simulation and hidden-interior optimisation

Date: 2026-11-10. All work is in this folder; nothing in the project was changed.

**How to read the tags on numbers**

| Tag | Meaning |
|---|---|
| `[cv]` | computed, and the 1/6 in and 1/8 in meshes agree (converged) |
| `[c]` | computed on the working mesh only (1/6 in), not re-run on the finer mesh |
| `[mc]` | computed as mean and 5-95 % range of 40 paired uncertainty draws (not mesh-checked draw by draw) |
| `[pub+]` | agrees with a published measurement or formula |
| `[pub-]` | disagrees with, or lies outside, published values |
| `[nv]` | not validated against any measurement |

Nothing here has been checked against a measurement of this instrument, so every acoustic number is `[nv]` in the absolute sense unless marked `[pub+]`. Differences between designs are more trustworthy than absolute levels.

Units: inches for positions (x from the nut, y positive on the bass side, z up from the top face), mm for skins. Sound power is dB re 1 pW per N² of vertical force at the saddle, mean of six strings, player holding the guitar.

---

## 1. Recommended build

**Design B' (hidden changes only):**

1. **Back skin of the wing chamber: 7.0 mm to 5.0 mm.**
2. **Top skin of the chamber: 4.0 mm to 5.0 mm**, for strength (section 1.4). It costs about 1 dB of the 200-300 Hz gain `[c]`.
3. **Tail pocket joined to the wing chamber:** x 29.5 to 31.0, y -3.2 to +6.0, same 5 mm skins, 0.30 in rim to the outline, open to the chamber across the centre line behind the spring cavity. Leave a solid boss for the strap button: x 30.35 to the tail, |y| < 0.50. Chamber volume goes from 55.5 to 68.0 in³.
4. **f-hole liner 0.75 in deep following the traced outline, tuned on the bench** so the air resonance lands on the body's twisting mode. The model puts that mode at 283-288 Hz `[cv]` and the tuned air resonance at 275-285 Hz. Tune to the measured body mode, not to these numbers (section 5).
5. **Cross-grain cleats under both f-hole ends** (about 0.9 x 0.7 in, 1.5 mm maple, grain across the body). The cleats were not modelled; they are there because the f-hole ends are the highest-stress spots.

Unchanged: spine |y| < 1.9, all routes, tongue, f-hole, outline, 1.75 in thickness. Drawing: `fig_plan_recommended.png`.

**Conservative alternative, design A':** items 1, 2, 4 and 5 without the tail pocket. It needs a liner with about 1.4 to 1.6 times the air mass of the plain 0.75 in liner (an inward lip below the top surface narrowing the throat by roughly 35-45 %), because there is no extra volume to do the tuning.

### 1.1 Expected gain over the current design

Mean and 5-95 % range, 40 paired draws, liner trimmed on the bench `[mc]`. In brackets: liner left as built.

| Band | B' radiated power | B' belly | B' neck back | A' radiated power | A' belly |
|---|---|---|---|---|---|
| 80-200 Hz | +1.2 dB (1.2 to 1.3) | +1.4 | +3.5 (2.3 to 4.6) | +0.2 | +0.4 |
| 200-300 Hz | **+6.2 dB (5.0 to 7.9)** [as built +5.9 (4.4 to 7.6)] | +2.6 (2.2 to 3.1) | +1.4 (0.7 to 2.0) | **+5.4 dB (4.1 to 7.3)** [as built +4.4 (2.8 to 6.3)] | +1.3 (0.9 to 1.6) |
| 300-500 Hz | **-5.1 dB (-6.8 to -3.5)** | +2.0 (1.1 to 3.0) | +1.3 (-0.6 to 3.4) | -2.7 dB (-3.9 to -1.2) | +1.8 |
| 500-1000 Hz | +0.7 dB (-0.5 to 2.0) | +2.6 (1.4 to 3.8) | -1.4 (-2.0 to -0.5) | -0.7 dB (-2.0 to 0.4) | +1.8 |

- **Audibility (3 dB rule):** B' clears 3 dB at 200-300 Hz in 100 % of draws, trimmed or not. A' clears it in 100 % of draws when trimmed and 88 % as built.
- **Felt vibration:** the belly gain reaches 3 dB at 200-300 Hz in only 10 % of draws for B' and never for A'. The clearest felt change in B' is at the back of the neck below 200 Hz.
- **This is tone shaping, not more volume.** Averaged over all 78 notes (open to fret 12, four partials) the level change is 0.0 dB for B' and -0.2 dB for A' `[mc]`. In B', 7 notes gain more than 3 dB and 10 lose more than 3 dB. The 200-300 Hz gain is paid for at 300-500 Hz, and in B' that loss is itself audible.
- **Mesh check:** B with a 4 mm top gives +7.0 to +7.6 dB at 200-300 Hz on the 1/8 in mesh against +7.5 dB on the working mesh `[cv]`. The 5 mm-top variants were not re-run on the fine mesh `[c]`.
- **Player contact:** with a wide belly contact (five damped patches) B keeps +6.9 dB at 200-300 Hz, also with three times firmer contact `[c]`. The belly gain itself falls from +2.5 to +0.7 dB with the firm hold.

### 1.2 Cost in sustain

Judged per note with the Woodhouse/Paté relation, T60 = 6.91 L / (T G), on each note's fundamental, with G the bridge-plus-fret conductance. "Halving" conductance per string: 1.0e-3 (low E), 1.5e-3 (A), 2.0e-3 (D), 3.0e-3 s/kg (G, B, high E). The A, D and B values are my interpolation.

| | Notes whose decay shortens > 25 % | Notes whose decay lengthens > 25 % | Notes past the halving conductance (baseline 20.8) |
|---|---|---|---|
| B' `[mc]` | 2.8 (0 to 6) | 4.4 | 21.6 |
| A' `[mc]` | 1.1 (0 to 3) | 2.0 | 21.4 |

- The only note that shortens in more than half the draws is **C#5 (high E, fret 9): about -30 %** in 55-57 % of draws, in both designs.
- The low E and A strings are essentially untouched (changes under 5 %, except A-string frets 6-7 which trade +35 % / -27 % in B).
- Peak bridge conductance is unchanged: ratio to baseline 0.98 (0.83 to 1.08) for B, 0.96 (0.85 to 1.02) for A `[mc]`.
- No new neck dead spot: 0.1 per draw on average `[mc]`.
- Other costs of B': 85 g lighter, balance point 0.33 in toward the neck `[c]`. A': 13 g lighter, no balance change.

### 1.3 Optional, after the build: a 40-60 g mass on the wing

A 40 g mass at (24.0, 5.9) on the back skin lowers the bass-wing flap mode onto the tuned air resonance.

- Gain at 200-300 Hz: +14.7 dB (10.7 to 17.8) with the tail pocket, +13.7 dB (9.7 to 17.0) without `[mc]`, 4 mm top.
- It is touchy. With a wide, firm belly contact it falls to +7.5 dB, no better than B without the mass `[c]`.
- It shortens D4 by about 50 % in 92-95 % of draws, C#4 by about 45 %, and C5 by about 40 % `[mc]`.
- Note levels become uneven (-7 to +10 dB note to note), and the back of the neck loses 4.5 dB at 500-1000 Hz.
- 20 g does almost nothing (+7.3 dB, same as no mass); the effect needs the mass matched to the wood.

Do not build it in. It can be tried reversibly by taping the mass to the outside of the back at that spot.

### 1.4 Strength of the top skin

Load case: 50 N on 1 in², scanned over the chamber. Stress is cross-grain tension in the skin.

| Top skin | Field peak, MPa | At the f-hole ends, MPa | Deflection, mm | Safety factor, plain alder (2.9 MPa) | Safety factor, roasted (assumed 2.0 MPa) |
|---|---|---|---|---|---|
| 4.0 mm (current) | 2.00 / 2.08 `[cv]` | 2.27 / 2.17 | 0.96 / 1.10 | 1.4 / 1.3 | 1.0 / 0.9 |
| 4.5 mm | 1.58 `[c]` | 1.88 | 0.71 | 1.8 / 1.5 | 1.3 / 1.1 |
| 5.0 mm | 1.28 / 1.30 `[cv]` | 1.60 / 1.47 | 0.55 / 0.62 | 2.2 / 1.8-2.0 | 1.6 / 1.3 |
| 5.5 mm | 1.06 `[c]` | 1.37 | 0.44 | 2.7 / 2.1 | 1.9 / 1.5 |
| 6.0 mm | 0.89 `[c]` | 1.20 | 0.36 | 3.3 / 2.4 | 2.2 / 1.7 |
| 4.0 mm + 0.6 mm cross-grain maple veneer inside | 1.53 `[c]` | 1.31 | 0.57 | 1.9 / 2.2 | 1.3 / 1.5 |
| 5.0 mm + the same veneer | 0.97 `[c]` | 0.90 | 0.34 | 3.0 / 3.2 | 2.1 / 2.2 |

Where two values are given they are the 1/6 in and 1/8 in meshes.

- **Target safety factor: 2.** Cross-grain strength varies about ±25 % board to board and the failure is brittle, so a factor of 2 on the mean keeps a weak board above the load with a small margin.
- **Minimum:** plain alder 5.0 mm with cleats at the f-hole ends. Roasted alder: 5.0 mm plus a 0.6 mm cross-grain veneer under the chamber roof, or 6.0 mm plus cleats.
- The 4.0 mm skin has a safety factor of 1.3-1.4 in plain alder and about 1.0 if roasted. That is not enough.
- The earlier plate estimate of 5.83 MPa was about 2.8 times too high; the skin spans both ways and the load spreads.
- The field peak sits on the outer face over the chamber wall next to the control cavity, near (23.3, 2.7). It scales as thickness to the power -2.
- The f-hole-end values depend on the stair-stepped mesh edge; treat them as ±20 %.
- The 2.9 MPa strength is the handbook value for red alder tension perpendicular to grain `[nv]` for this board; the 30 % loss for roasting is an assumption.
- Back skin at 5.0 mm: 0.82 MPa `[c]`, safety factor 3.5 plain, 2.4 roasted (7.0 mm: 0.50 MPa).
- The acoustic effect of the veneer and cleats was not computed. Top thickness itself costs about 0.45 dB per 0.5 mm at 200-300 Hz `[c]`.

### 1.5 What the model cannot tell, and the bench test that settles each

| Open question | Why the model cannot settle it | Bench test on the dry-clamped body |
|---|---|---|
| Where the air resonance really sits (model: 364-365 Hz bare, 320-324 Hz with liner; a hand formula says 400-456 Hz) | The 20 % lowering comes from air inertia inside a long shallow cavity, resolved by only four air layers in depth; never measured | Small speaker or tap near the f-hole, microphone at the hole, f-hole open and taped shut. Read the air resonance with and without the liner. Then tap the wing tip with the body hung at the waist to find the twisting mode near 285 Hz, and trim the liner until the two coincide within about 5 Hz. |
| Whether the bridge-conductance peaks at 440-690 Hz (0.6e-2 to 1.8e-2 s/kg) are real | Knife-edge friction and spring damping are not modelled; values are 3-10 times published solid-body peaks | Trem and neck fitted: accelerometer at a saddle, tap beside it with an instrumented hammer (or a small shaker), 100-1000 Hz. Compare peak heights with the table in section 4. |
| Skin stiffness and strength of this board | Handbook cross-grain properties, ±15 % stiffness and more on strength | 5 kg on a 1 in² pad at (23.8, 3.6), dial gauge: model predicts 0.55-0.62 mm at 5.0 mm (1.0-1.1 mm at 4.0 mm). Break-test an offcut skin of the same board with an f-hole end cut in it. |
| Whether the wing mass is worth having | Depends on how the back is held | Tape 40-60 g to the outside of the back at (24.0, 5.9) and listen, held normally. |

Also not modelled: string-to-string coupling beyond the conductance, room acoustics, humidity, glue-line compliance, non-linear behaviour, the finish beyond a thin film, and the player's body beyond five spring-damper contacts.

---

## 2. Stage 1: the model and its convergence

- Layered hexahedral mesh of body, neck, fingerboard, tongue, tremolo (rigid body on pivots and springs), pickguard with screws and contact, pickups, finish film, strings as tension springs.
- Air in the chamber as acoustic elements, coupled to the walls. The f-hole is a plug with wall thickness, liner length and an exterior end correction.
- Radiation from a boundary-element resistance matrix of the exterior surface (`bem.py`, checked against analytic cases in `verify_bem.json`). Element checks in `verify_elements.json`.
- Reduced model: 150 structural modes plus static corrections, 40 air modes, group loss factors.

| Mesh size | Unknowns | Air resonance (liner) | Band levels 80-200 / 200-300 / 300-500 / 500-1000, dB |
|---|---|---|---|
| 1/4 in | 63,420 | 322 Hz | 45.2 / 52.3 / 67.7 / 69.1 |
| 1/6 in (working) | 136,299 | 320 Hz | 45.3 / 52.7 / 67.0 / 68.0 |
| 1/8 in | 236,730 | 320 Hz | 45.3 / 53.0 / 66.5 / 68.8 |

- Bands agree within ±0.6 dB and main modes within 2 % between the two finer meshes `[cv]`.
- Main modes (1/6 in): 58 (first bending), 62 (trem rocking), 107, 159 (second bending), 288 (whole-body twisting), 314, 406 (bass-wing flap), 441 (trem on its pivot strip), 574, 639 Hz (first top-skin mode). Shapes in `fig_modes_baseline.png`.
- Baseline mass 2.938 kg, balance point x = 15.51 `[c]`.
- An exterior-surface mapping error leaks 3-4 % of the gross flow of rigid-body motion into a spurious net volume flow. Removing it changes band totals by at most 0.07 dB `[c]`.

## 3. Stage 2: validation and the reviewer's checks

### 3.1 f-hole conductance (Nia et al.)

- **The hole is modelled as a slot, not as an equal-area circle.** The exterior end correction uses an ellipse of the hole's length and area.
- I checked this against the traced outline directly (integral-equation solve on the 240-point polygon, `checks.py`): one-sided conductance 0.1428 m for the traced shape, 0.1386 m for the model's ellipse, 0.1034 m for the equal-area circle `[c]`.
- So the traced slot conducts 1.38 times better than the circle (perimeter ratio 2.28), which agrees with Nia's direction `[pub+]`. The model is within 3 % of the traced value, worth 1 Hz on the air resonance.
- **Bare-hole, rigid-wall air resonance in the model: 364-365 Hz** `[cv]`; with flexible walls 362-363 Hz; with the 0.75 in liner 324-325 Hz rigid, 320 Hz flexible.
- **Reconciliation with 400-425 Hz:** the compact-cavity hand formula with my own hole conductance gives 456 Hz (395 Hz for the circle; the reviewer got 385 Hz). The hole is therefore not the reason the model is lower. The difference is the cavity: 16 in long and about 1 in deep, so the air has to travel along it and squeeze under the hole. A rough estimate of the lengthwise inertia alone gives about 387 Hz.
- This interior effect is converged in plan (326 / 324 / 325 Hz on three meshes) but the air has only four layers in depth, and it is `[nv]`. I would put the real bare-hole value between 360 and 400 Hz.
- **Consequence:** every liner length here is uncertain by about ±10 % in frequency. The recommendation is therefore a target (air resonance on the body mode), not a liner dimension. If the real resonance is 10 % higher than modelled, B' still tunes with a modest inward lip; A' may run out of liner.
- Putting the liner mass directly on the plug instead of meshing the liner gives the same result (+7.5 dB at 200-300 Hz either way) `[c]`.

### 3.2 Weinreich/Gough sum rule

- Inside the chamber the rule holds: hole flow against chamber-wall flow is 1.02 at 60-80 Hz, in antiphase (179-180 degrees) `[c]`. These chamber-side numbers are printed by `t_sum.py` and are not stored in `checks.json`, which holds the exterior-surface version.
- The net flow relative to the wall flow rises roughly as frequency squared: 0.02 at 60 Hz, 0.05 at 100 Hz, 0.15 at 160 Hz, 0.27 at 200 Hz, 0.46 at 230 Hz `[c]`.
- It rises more slowly than a single-resonance formula with 324 Hz would give. The wall motion is concentrated near the hole, so it vents with less inertia than uniform compression would.
- The exterior monopole share falls toward low frequency as required: monopole 35.1 / 46.7 / 65.1 / 63.6 dB against totals 45.3 / 52.7 / 67.0 / 68.0 dB. Below 250 Hz the baseline radiates as a dipole.
- **A flaw to declare:** the exterior surface map also leaks a few percent of the gross flow of the bending modes into the monopole, so the low-frequency monopole is partly numerical. Bound on baseline band levels: 0.4 dB at 80-200 Hz, 1.2 dB at 200-300 Hz. The tuned designs are dominated by the genuine hole flow at 200-300 Hz (monopole 58.9 of 60.2 dB).

### 3.3 Bridge conductance and the sustain budget

- **What "Gz 1.3e-2 to 1.8e-2" in the logs is:** the single highest value, over 70-1050 Hz and over the six saddles, of the vertical driving-point conductance Re(Y) at a saddle. In the baseline it is 1.8e-2 s/kg at 659 Hz on the low-E saddle `[c]`. It is a peak, not a band mean.
- Baseline per saddle `[c]`:

| Saddle | Peak, s/kg | At | Median 70-1050 Hz | Mean 80-200 / 200-300 / 300-500 / 500-1000 Hz |
|---|---|---|---|---|
| E2 | 1.8e-2 | 659 Hz | 3.1e-4 | 1.7e-4 / 3.4e-4 / 1.0e-3 / 1.9e-3 |
| A2 | 6.7e-3 | 659 Hz | 2.3e-4 | 1.4e-4 / 2.5e-4 / 6.9e-4 / 1.0e-3 |
| D3 | 5.6e-3 | 519 Hz | 1.7e-4 | 1.2e-4 / 1.8e-4 / 5.4e-4 / 6.2e-4 |
| G3 | 5.5e-3 | 519 Hz | 1.5e-4 | 1.0e-4 / 1.3e-4 / 6.0e-4 / 6.5e-4 |
| B3 | 5.5e-3 | 519 Hz | 1.4e-4 | 9.2e-5 / 1.1e-4 / 8.5e-4 / 1.1e-3 |
| E4 | 1.5e-2 | 659 Hz | 1.4e-4 | 8.9e-5 / 1.0e-4 / 1.3e-3 / 2.1e-3 |

- Peaks above 2e-3 (worst saddle): 406 Hz 3.3e-3, 442 Hz 1.0e-2, 519 Hz 6.0e-3, 587 Hz 7.0e-3, 659 Hz 1.8e-2, 685 Hz 8.8e-3. Along-string peak 1.8e-2, sideways 1.2e-2.
- Across the uncertainty draws the baseline peak is 1.5e-2 (0.96e-2 to 2.3e-2) at 595-750 Hz `[mc]`.
- **Against published values:** below 300 Hz the bridge is inside the budget (mean 1.4e-4; solid reference 7.6e-5) `[pub+]`. The peaks at 440-690 Hz are 3-10 times the published solid-body maximum of 1.8e-3 and about twice the 8e-3 quoted for a Strat tremolo `[pub-]`. I expect them to be too high because trem friction is missing. They are the same in the solid reference (1.4e-2 at 708 Hz), so they come from the tremolo and neck, not the chamber.
- **Per string, baseline fundamentals** `[c]`:

| String | Notes past halving (of 13) | Notes past the 25 % limit | Which notes, and why |
|---|---|---|---|
| E2 | 1 | 10 | B2 (1.0e-3) |
| A2 | 3 | 11 | D3, D#3, E3: neck (fret term up to 6.7e-3) |
| D3 | 4 | 9 | D3 to F3: neck dead spot, 2.3e-2 at D#3 and 2.1e-2 at E3 |
| G3 | 2 | 9 | D#4, F4: neck |
| B3 | 5 | 10 | B3, C4, D#4, F4: neck; A4: bridge 4.1e-3 |
| E4 | 6 | 10 | E4, F4: neck; A4, D5, E5: bridge 0.7e-2 to 1.5e-2 |

- So 21 of 78 fundamentals are past halving in the baseline, and 59 are past the "inaudible" limit. The solid reference also has 21. On this budget the baseline is already over, and the body design is not the cause.
- **Finalists per note:** see section 1.2 and `fig_notes.png`. Full per-string lists for every finalist are in `report_numbers.txt`.

### 3.4 Dead region at 500-800 Hz and below 300 Hz (Zollner)

- **Agree.** The model has tremolo modes at 518, 587, 660 and 686 Hz and the first top-skin mode at 639 Hz (71 % of its strain energy in the top skin), all inside 500-700 Hz `[c]`. Mean bridge conductance at 500-800 Hz is 1.7e-3 in the baseline and 1.5e-3 in the solid body.
- The notes hit are A4, D5 and E5 on the high E string and A4 on the B string, plus second partials of notes at 250-350 Hz.
- The top-skin mode adds little: the region is the same in the solid body. With the 5 mm top it moves to 712-750 Hz, out of the densest tremolo cluster.
- **Neck below about 350 Hz: agree.** Largest neck conductances `[c]`: 4.4e-2 (B3 open, a partial), 2.3e-2 at D#3 and 2.1e-2 at E3 on the D string (the 159 Hz second bending mode), 1.4e-2 at F4 on the high E. Published dead spots reach about 0.1 s/kg `[pub+]` in order of magnitude.

### 3.5 Set neck and tongue

- **Agree with the controlled test.** Tongue length 19.5 to 22.0, depth and width change every band by 0.3 dB or less `[c]`, and the neck dead spots are identical in the solid reference. The model shows no mechanism by which the tongue adds sustain, so none is credited.

### 3.6 Against the earlier reduced models and other published data

| Quantity | Earlier | This model | Verdict |
|---|---|---|---|
| Air resonance with 0.75 in liner | 311-331 Hz | 320 Hz `[cv]` | agrees |
| Air resonance, bare hole | 387 Hz | 362 Hz `[cv]` | 6 % lower; cavity shape (3.1) |
| First top-skin mode | 540-583 Hz | 639 Hz (674 Hz on the 1/4 in mesh) `[c]` | 10-15 % higher; the 3-D skin has filleted walls, the guard and its screws on it. Not validated. |
| Chamber level (the two models disagreed by 11 dB) | rigid-spine model about 38-47 dB SPL; flexible-spine model about 55-56 dB | 59-60 dB SPL at 1 m per N above 300 Hz `[cv]` | agrees with the flexible-spine model. The rigid spine removed the wing-flap and whole-body motion that actually radiates. |
| Passive tweaks worth about +1 dB | +1 dB total | single tweaks all within ±1-2 dB `[c]` | agrees for single tweaks. It misses tuning the air resonance onto the 285 Hz body mode, which the earlier models did not contain. |
| Trem bearing on the top: +7 dB | +7 dB at 3-5 times the sustain budget | coupler: +3.5 to +6.3 dB at 500-1000 Hz, +0.4 to +2 dB at 200-300 Hz `[c]` | partly agrees: loud, but above 300 Hz, not where wanted |
| Top skin stress, 50 N on 1 in² | 5.83 MPa | 2.0-2.3 MPa `[cv]` | earlier value 2.8 times too high |
| Free-body modes | Epiphone Coronet (Russell): 55, 160, 189, 300, 370 Hz | 58, 159, 196, 288-314, 340-367 Hz `[cv]` | same family and spacing `[pub+]`; a different guitar, so only a plausibility check |

## 4. Stage 3: baseline outputs

Per unit saddle force, player holding `[c]` unless tagged.

| | 80-200 Hz | 200-300 Hz | 300-500 Hz | 500-1000 Hz |
|---|---|---|---|---|
| Radiated power, vertical force, dB re 1 pW/N² `[cv]` | 45.3 | 52.7 | 67.0 | 68.0 |
| Same, body free | 45.2 | 53.6 | 68.8 | 69.5 |
| Radiated power, along-string force | 39.8 | 43.5 | 65.0 | 74.8 |
| Radiated power, sideways force | 35.3 | 45.9 | 56.6 | 66.8 |
| Belly velocity, dB re 1 (m/s/N)² | -63.6 | -63.3 | -56.2 | -55.7 |
| Forearm | -58.6 | -58.1 | -50.9 | -52.4 |
| Back of the neck | -69.9 | -68.3 | -61.6 | -54.6 |
| Top at the pickups | -59.3 | -65.5 | -67.9 | -76.9 |
| Top skin mid-chamber | -61.3 | -61.7 | -52.8 | -43.6 |

- Radiation peaks: 317 Hz (60.3 dB), 343 (59.9), 427 (75.3), 438 (74.0), 515 (69.5). The strong peak is the wing-flap mode at 427-438 Hz; the air resonance at 320 Hz is weakly driven.
- Solid body against the baseline: -2.2 / -3.6 / -8.7 / -2.5 dB radiated, -5.5 / -7.1 / -14.4 / -9.3 dB at the belly. f-hole closed: -0.1 / -1.2 / -6.5 / -1.3 dB.
- Note-by-note level and decay tables (6 strings x 13 frets), neck conductance at every fret, and all per-string budgets: `report_numbers.txt` and `summary.json`.
- Shortest fundamental decay times in the baseline: about 1-2 s at D#3/E3 on the D string and at D5/E5 on the high E `[nv]`.

## 5. Stage 4: sensitivity of the hidden variables

Gain over baseline in the four bands, nominal model, one variable at a time `[c]`. Differences under about 1 dB are inside the model's own uncertainty (contact stiffness alone moves bands ±1-2 dB).

| Variable | 80-200 | 200-300 | 300-500 | 500-1000 | Note |
|---|---|---|---|---|---|
| Back skin 5 mm (from 7) | +0.2 | +1.1 | -1.2 | +1.2 | belly +0.7 to +2.0 |
| Back skin 6 mm | +0.1 | +0.4 | -0.5 | +0.7 | |
| Top skin 3.0 to 5.0 mm | within ±1 | within ±1 | -2.1 to +0.9 | within ±1 | thickness barely matters acoustically |
| Edge-thinned top (3.0 / 2.6 mm) | | | -1.5 / -2.4 | | no gain |
| Spine narrower (1.75) | | up to +0.5 | | | not buildable at the humbucker route |
| Spine wider (2.2 / 2.5) | | -0.3 to -1.3 | | | |
| Tail pocket joined (air resonance to 290 Hz) | +0.9 | +3.2 | -6.0 | +1.6 | -73 g |
| Tail pocket sealed off | up to +0.6 | | | | volume must be connected to matter |
| Large U-shaped pocket | +2.6 | +2.8 | -4.0 | +0.8 | -233 g, 10 new notes over the conductance limit |
| Treble-side or horn pockets | up to +0.6 | | | | |
| Braces (long, cross, both) | -0.8 to +2.1 | | cross bars +2.1 | | |
| Posts between skins | about 0 | | | | |
| Baffle across the chamber | | | -3.7 | | air resonance to 402 Hz |
| 20 g on the top at (27.3, 4.0) | | | | +4.7 | |
| Liner length 0 / 0.375 / 0.75 / 1.0 in | air resonance 362 / 342 / 320 / 303 Hz | | | | the tuning knob |
| Tongue length, depth, width | 0.3 or less | | | | |
| Spring count, claw position | 0.3 or less | | | | |
| Coupler from trem to top | | +0.4 | +0.9 to +4.9 | +3.5 to +4.3 | conflicts with a floating trem |
| Guard screws moved or removed | | | -2.5 to +1.0 | | |
| Poly instead of nitro | -0.5 | -0.8 | +0.7 | +1.3 | belly -0.7 to -1.2 |
| Plain instead of roasted alder | -0.5 | -0.4 | -0.4 | +1.0 | +92 g |
| Thickness 1.80 in | about 0 | | | | |
| No pickguard | | | | +5.3 | not allowed (visible) |

Full table for 63 variants: `sensitivity_table.json`.

## 6. Stage 5: optimisation

### 6.1 What can put real output at 200-300 Hz, and what each costs

1. **Tuning the air resonance onto the body's twisting mode (283-288 Hz), with a 5 mm back skin to pump more air.** +5 to +8 dB. Cost: 3-5 dB at 300-500 Hz, and one or two notes near C#5 lose about 30 % of their decay. Two ways to tune: more volume (tail pocket) or more air mass in the hole (longer or narrower liner).
2. **A tuned mass on the wing** bringing the wing-flap mode down to the same frequency. +10 to +18 dB on top of nothing else, but it needs the back to be free, shortens D4/C#4/C5 by 40-50 %, and makes note levels uneven.
3. **Nothing else.** Skin thickness, braces, posts, spine width, treble pockets, tongue and springs are all worth 1 dB or less at 200-300 Hz. Below about 250 Hz the body radiates as a small dipole whose level is set by its size and mass, not by anything inside.

### 6.2 Candidates

Nominal model, each at its best liner tuning `[c]`.

| Design | Liner air-mass factor | Air resonance | 80-200 | 200-300 | 300-500 | 500-1000 | Belly 200-300 | Mass | Balance |
|---|---|---|---|---|---|---|---|---|---|
| A: 5 mm back, 4 mm top | 1.40 | 287 Hz | +0.3 | +6.6 | -3.9 | +0.9 | +1.9 | -25 g | -0.05 in |
| **A': 5 mm back, 5 mm top** | 1.40 | 289 Hz | +0.2 | +5.9 | -3.0 | +0.2 | +1.3 | -13 g | -0.03 in |
| B: A + tail pocket, 4 mm top | 1.12 | 277 Hz | +1.4 | +7.5 | -5.5 | +2.0 | +3.3 | -99 g | -0.36 in |
| **B': B with 5 mm top** | 1.12 | 278 Hz | +1.2 | +6.6 | -5.9 | +1.7 | +2.4 | -85 g | -0.33 in |
| B with 7 mm back | 1.12 | 283 Hz | +1.0 | +4.3 | -6.1 | +1.0 | +0.8 | -69 g | -0.29 in |
| A with 6 mm back | 1.55 | 281 Hz | +0.2 | +5.4 | -3.5 | +0.4 | +0.7 | -12 g | -0.03 in |
| 7 mm back, 5 mm top, liner only | 1.55 | 286 Hz | -0.1 | +4.0 | -1.5 | -0.3 | -0.3 | +12 g | +0.02 in |
| C: A + 40 g wing mass | 1.25 | 293 Hz | -0.2 | +14.2 | -0.1 | +1.7 | +6.8 | +15 g | +0.27 in |
| D: B + 40 g wing mass | 1.00 | 284 Hz | +0.8 | +15.8 | -2.8 | +3.6 | +8.7 | -59 g | -0.03 in |
| A + 20 g wing mass | 1.40 | 286 Hz | +0.1 | +7.3 | -3.7 | +1.7 | +3.0 | -5 g | +0.11 in |
| B + trem-to-top coupler | 1.12 | 278 Hz | +1.4 | +9.7 | -4.8 | +6.3 | +3.3 | -99 g | -0.36 in |
| A + large U pocket | 1.00 | 221 Hz | +3.3 | +3.9 | -1.6 | +2.2 | +4.5 | -269 g | -1.04 in |
| Solid body (reference) | | | -2.2 | -3.6 | -8.7 | -2.5 | -7.1 | +378 g | +0.69 in |

Monte-Carlo gains for the 4 mm-top versions, liner trimmed `[mc]`:

| Design | 200-300 Hz power | 300-500 Hz power | Belly 200-300 Hz | Notes shortened > 25 % |
|---|---|---|---|---|
| A | +6.0 (4.7 to 7.8) | -3.3 (-4.9 to -1.6) | +2.0 (1.6 to 2.6) | 2.6 (1 to 5) |
| B | +7.2 (6.0 to 9.0) | -4.6 (-6.4 to -2.7) | +3.7 (3.1 to 4.5) | 3.9 (2 to 6) |
| C | +13.7 (9.7 to 17.0) | -2.0 (-4.7 to +0.2) | +6.9 (4.8 to 8.8) | 7.6 (4 to 10) |
| D | +14.7 (10.7 to 17.8) | -1.9 (-3.5 to 0.0) | +8.3 (6.0 to 10.5) | 7.3 (4 to 10) |

All four clear 3 dB at 200-300 Hz in 100 % of draws, trimmed or as built. Charts: `fig_band_gains.png`, `fig_frf_baseline_vs_best.png`, `fig_notes.png`.

### 6.3 Robust or coincidental

- **Robust:** the tuned air resonance (A, B and the 5 mm-top versions). The gain survives ±15 % wood stiffness, ±6 % density, loss and contact changes, a 1/8 in mesh, a wide belly contact, and roasted or plain alder (+7.3 dB plain). It needs the liner trimmed to the real body; left as built it loses about 0.3 dB (B') to 1 dB (A').
- **Conditional:** the wing mass. Robust to the wood draws when mass and liner are both trimmed (trimmed mass 40-60 g), but it depends on how the back is held and it costs specific notes.
- **Coincidental, discarded:** an early "+15 dB" from a 40 g mass with an untrimmed liner was a lucky alignment; the trimmed result above is the honest one. The trem coupler's +9.7 dB at 200-300 Hz was not Monte-Carlo tested and conflicts with a floating trem.

### 6.4 Design conflicts found on the way

- The spring cavity (from x = 20.4) cuts into the lower part of the tongue (to x = 21.5).
- The web between the humbucker route and the chamber is only about 0.1 in in the CAD (modelled as 0.3 in). A narrower spine is not buildable there.
- The tremolo pivot screws sit on a cross-grain strip nearly isolated by the humbucker route, trem hole, control pocket and chamber. This strip is the source of the 406-690 Hz conductance peaks.
- A full-width tail pocket would leave the strap button on a 0.3 in rim, hence the boss.

## 7. Files

| File | Content |
|---|---|
| `REPORT.md` | this report |
| `summary.json` | consolidated results (baseline tables, budgets, candidates, checks, strength) |
| `report_numbers.txt` | every table quoted here, printed in full |
| `candidates_summary.json` | finalists: nominal, Monte-Carlo, constraints, per-note changes |
| `checks.json` | f-hole conductance, air resonance and sum-rule checks |
| `fine_mesh_check.json`, `belly_contact.json` | 1/8 in mesh and wide-contact robustness |
| `strength3_h0.167.json`, `strength3_h0.125.json` | top and back skin press study |
| `sensitivity_table.json`, `results/`, `results2/`, `results3/` | every variant, with spectra |
| `convergence_0.25_0.16667.json`, `convergence_0.125.json` | mesh convergence |
| `fig_plan_recommended.png` | dimensioned plan and section of design B' |
| `fig_band_gains.png` | band gains with 5-95 % ranges |
| `fig_frf_baseline_vs_best.png` | spectra: baseline, solid, A, B, D |
| `fig_notes.png` | per-note level and decay change |
| `fig_modes_baseline.png` | 24 baseline mode shapes |
| `fe.py`, `mesh.py`, `model.py`, `bem.py`, `rom.py`, `study.py` | the model |
| `sweep.py`, `designs.py`, `opt.py`, `post.py`, `strength.py`, `checks.py`, `figs.py`, `report_data.py` | studies and post-processing |

Run with `S/cad/bin/python -I -W ignore <script>`, one process at a time (a build peaks at about 4 GB on the working mesh, 6.5 GB on the 1/8 in mesh).
