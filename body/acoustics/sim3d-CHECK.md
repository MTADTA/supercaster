# Independent check of the Supercaster II 3-D simulation study

Date: 2026-11-11. Reviewer's work only; nothing in `sim3d/` or the project was changed. Every script and log named here is in this folder (`sim3d-check/`).

Scope note: the owner has since decided to keep the tail and centre block solid, so design B' (tail pocket) is out. It is reported briefly in section 9. The rest is about design A': 5 mm back skin, 5 mm top skin, no pocket, f-hole liner tuned to about 285 Hz.

Tags used below:

- **[computed]** I calculated it myself, with my own post-processing, my own boundary conditions or a separate model.
- **[judged]** my reading of the evidence, not a calculation.
- Claim status: **reproduced**, **different number**, **not reproduced**, **could not check**.

How I worked: I rebuilt the three reduced models (baseline, A', B') from the study's modules once (`b1_build.py`), then did everything else with my own code (`common.py` and the `d*.py` scripts): my own contact sets, my own radiation correction, my own note and decay post-processing. Two checks use no study code at all beyond the carve geometry: a finite-volume solve of the chamber air (`c1lib.py`) and a plate model of the top skin (`c2_plate.py`).

---

## 1. Verdicts

| Item | Verdict |
|---|---|
| Build A' (5 mm back, 5 mm top, tuned liner) | **Yes to the wood changes, with lower expectations.** The gain is real but it is the liner's doing, it sits on two notes (C#4 and D4), and it needs a liner narrowed to about 55 % of the hole area. Expect about +3 to +4 dB at 200-300 Hz rather than +5.4 dB. |
| 5 mm top skin | **Needed, and not enough on its own in roasted alder.** My plate model gives stresses 1.3 to 1.9 times the study's. Add the cross-grain veneer under the roof or go thicker. |
| Liner tuning target | **Aim for the 270-290 Hz window, not for coincidence within 5 Hz.** The band gain is flat across that window. Exact coincidence only makes one note hotter. |
| Tail pocket / B' | Out by the owner's decision. For the record: it does not break through, and its acoustic effect is added air volume. It was the only variant where a plain 0.75 in liner reaches the target. |

---

## 2. Is the gain mechanism physical? (question 1)

**The twisting mode is real and survives being held. [computed]** (`d0_modes.py`, `d1b_bc.py`)

| Condition | Mode frequency | Loss factor |
|---|---|---|
| Free | 287.4 Hz | 0.029 |
| Strap only | 287.5 Hz | 0.033 |
| Held, study's contacts | 287.9 Hz | 0.043 |
| Held three times firmer | 289.2 Hz | 0.070 |
| Wide belly contact | 288.7 Hz | 0.062 |
| Whole back against the body | 289.3 Hz | 0.080 |
| Held ten times firmer | 298.1 Hz | 0.136 |

The mode is 95 % body twist. Its frequency moves with things the study held fixed or varied too little:

| Change | Mode frequency |
|---|---|
| Pickguard-to-top contact stiffness x0.1 / x10 | 272 / 303 Hz |
| Tuners 0 g / 60 g each (study: 30 g) | 291 / 280 Hz |
| Alder stiffness x0.8 / x1.2 | 270 / 304 Hz |
| Maple stiffness x0.8 / x1.25 | 278 / 295 Hz |
| Tremolo mass, pivot stiffness, spring stiffness | 286.7 to 288.9 Hz (no effect) |

So "283-288 Hz" is not a prediction for this instrument. It is good to about ±15 Hz. The report's advice to tune to the measured mode is right.

**Where the radiated power comes from. [computed]** (`d1_gain.py`)

At 200-300 Hz, in dB re 1 pW/N²:

| | Total | Structure only | Hole flow only | Genuine chamber monopole |
|---|---|---|---|---|
| Baseline | 52.7 | 52.2 | 43.4 | 39.7 |
| A' tuned | 58.6 | — | 57.9 | 57.0 |

The baseline radiates from the structure. A' radiates through the hole. The gain is air pumped through the f-hole once the air resonance is moved into the band. It is not the wing skins and not a body dipole.

**The spurious monopole leak does not inflate the gain. [computed]** The study's exterior map gives rigid-body motion a false net volume flow (confirmed: up to 4 % of gross). I replaced it with a map whose net flow equals the true chamber-wall flow for every basis vector. The A' gain went from +5.9 to +6.3 dB. The leak slightly hides the gain; it does not create it. Status of "leak changes totals by at most 0.07 dB": **different number** (about 0.4 to 0.6 dB on the gain, in the favourable direction).

**The exterior radiation model. [judged]** The boundary-element check in `verify_bem.json` is exact for a sphere but 1.8 to 3.3 dB off for a thin disc. That matters for dipole-like structural radiation. It matters little here because the A' gain is a monopole-like hole source, which is the well-validated case. I trust the hole-flow gain more than the baseline level it is measured against.

**The key finding: most of the gain is liner tuning, not wood. [computed]**

The study compares designs with a tuned liner against a baseline with an untuned one. Giving the baseline the same tuning:

| | 200-300 Hz | 300-500 Hz |
|---|---|---|
| Baseline, liner tuned only (factor 1.55, 284 Hz) | +4.5 dB (study's map) / +5.2 (corrected) | -2.7 dB |
| A' tuned (factor 1.40, 289 Hz) | +5.9 / +6.3 | -3.0 |
| A' over the tuned baseline | **+1.4 / +1.2 dB** | -0.3 |

The report does list "7 mm back, 5 mm top, liner only: +4.0 dB", so this is not hidden, but the headline number credits the wood with what the liner does. The thinner back buys about 1 to 2 dB. Across 35 boundary-condition and parameter cases the A' increment over a tuned baseline stayed between +0.6 and +2.4 dB.

**Coincidence is not needed. [computed]** The band gain is flat for air resonances from 266 to 289 Hz (A': +4.9 at 271 Hz, +5.9 at 280 and 289 Hz, +3.0 at 299 Hz). What coincidence changes is the height of one peak about 10 Hz wide.

---

## 3. Is the baseline credible in absolute terms? (question 2)

**Peak bridge conductance 1.8e-2 s/kg at 659 Hz: reproduced (1.77e-2 at 660 Hz), and explained. [computed]** (`d3_cond.py`)

The peaks at 442, 518, 588, 660 and 686 Hz are the 0.36 kg tremolo bouncing on its six pivot screws and the cross-grain ledge they sit in. Evidence:

| Change | Peak conductance |
|---|---|
| Nominal | 1.77e-2 at 660 Hz |
| Pivot stiffness x0.3 | 2.03e-2 at 594 Hz |
| Pivot stiffness x10 | 7.0e-3 at 846 Hz |
| Pivot stiffness x100 (tremolo locked to the top) | 4.4e-3 at 908 Hz |
| Pivot loss factor 0.05 to 0.30 | 6.6e-3 at 660 Hz |
| Light, locked bridge (hard-tail proxy), above 500 Hz | 2.6e-3 |

A hand estimate of the ledge (cross-grain strip, bending plus rolling shear, about 4.4e6 N/m) with 0.36 kg gives about 556 Hz, in the same cluster.

So the ten-fold gap to the published figure is mostly a comparison of unlike things. The published 1.8e-3 is a hard-tail guitar. With the tremolo locked, the model gives 2.6e-3 to 4.4e-3, the same order. Zollner reports that a Strat bridge is mobile at 500-800 Hz but gives no numbers in the notes. The "8e-3 for a Strat trem" comment in `post.py` has no source. Whether a real floating tremolo is as lively as 1.8e-2 depends on pivot stiffness (5e6 N/m per screw) and pivot damping (0.05), both guesses. Status of the absolute level: **could not check** without a measurement.

**21 of 78 fundamentals past the halving budget: reproduced (21 with the study's budget, 23 with a flat string Q of 2500). [computed]** Bridge alone accounts for only 4 or 5 of them; the rest come from the neck end (fret conductance up to 5.5e-2, inside Paté's published neck range of up to 1.0e-1). The baseline's "many notes already past halving" is mostly neck, and is plausible.

**Does this error touch the design conclusions? [computed]** No for the gain: tremolo mass, pivot stiffness and spring changes moved the 200-300 Hz gain by at most ±0.6 dB. No for the decay ranking: raising pivot damping to 0.15 and 0.30 left the A' result unchanged (one note, C#5, -28 to -30 %).

**A misidentified mode. [computed]** The report matches a 196 Hz mode to a published 189 Hz body torsion. In the model that mode is the pickguard (as are 122, 230, 256, 261, 340, 367 and 461 Hz). The first body torsion is at 254 / 288 Hz. This does not change the recommendation but the "agrees with published" tag on it is wrong.

---

## 4. The air resonance and the liner A' needs (question 3)

**Independent solve. [computed]** (`c1lib.py`, `c1_run.py`; logs `c1_*.log`) Rigid-wall finite-volume model of the chamber, the hole through the true skin thickness, and a thin-walled liner, built directly from the carve fields. Outside air is a lumped conductance of the traced hole in a baffle (0.1428 m one-sided). Volume is corrected to the true 55.4 / 57.3 in³.

Grid check, baseline bare hole: 376.3 Hz (0.1 in cells), 378.3 Hz (finer in depth), 377.6 Hz (0.05 in cells in plan). Converged to about 1 %.

| Case (rigid walls) | Mine | Study | Status |
|---|---|---|---|
| Baseline, bare hole | 378 Hz | 364-365 Hz | different number (study 3.5 % low) |
| Baseline, 0.75 in liner | 320-325 Hz | 324 Hz | reproduced |
| A', bare hole | 372 Hz | — | — |
| A', 0.75 in liner | 320 Hz | 320 Hz | reproduced |
| Hand estimate, bare | — | 400-456 Hz | not reproduced: too high |

The hand formula is wrong for this chamber, not the model. The pressure in the lowest mode is five times higher at the neck end of the chamber than under the hole: the chamber is 16 in long and behaves partly like a pipe, not a compact bottle. Exterior end-correction choice moves the bare-hole value from 378 to 387 Hz, so about ±3 % remains from the outside-air assumption. Flexible walls lower everything by about 4 Hz.

**A plain straight liner cannot reach 285 Hz in A'. [computed]**

| Liner depth (full hole area) | Air resonance, rigid | Gap to the chamber floor |
|---|---|---|
| 0.50 in | 338 Hz | 0.64 in |
| 0.75 in | 320 Hz | 0.39 in |
| 0.90 in | 309 Hz | 0.24 in |
| 1.00 in | 300 Hz | 0.14 in |
| 1.05 in | 295 Hz | 0.09 in |

The chamber is only 1.14 to 1.35 in deep under the hole. Even nearly touching the floor the liner stops at about 291 Hz with flexible walls, and at that gap the air losses would kill the resonance.

**What A' actually needs. [computed]**

| 0.75 in liner with a narrowed throat | Air resonance, rigid |
|---|---|
| 75 % of hole area, full depth | 306 Hz |
| 60 %, full depth | 294 Hz |
| 50 %, full depth | 283 Hz |
| Thin lip only (0.15 in deep) at 50 % | 310 Hz |
| Thin lip only at 35 % | 301 Hz |
| 0.90 in liner at 75 %, full depth | 294 Hz |

To put the air resonance at 285 Hz with flexible walls, a 0.75 in liner must be narrowed to **about 55 % of the hole area over its whole depth** (a 45 % reduction). A thin lip will not do it. My model leaves out the extra end effect of the constriction, so the real figure is slightly less narrowing than this; treat 45 % as the upper bound. The report's "35-45 % narrower, 1.4 to 1.6 times the air mass" is **reproduced**.

**Does it fit and stay hidden? [computed geometry, judged visibility]**

- Fit: yes. A 0.75 in liner leaves 0.39 in to the floor at the shallowest point and the hole edge is at least 0.57 in from any chamber wall.
- Shape: the hole is 3.26 in² with a 14.6 in perimeter, so its mean width is about 0.45 in. A 45 % reduction means the liner's inner wall sits about 0.10 to 0.11 in (2.5 to 2.8 mm) inside the hole outline all round, leaving a slot about 0.25 in (6 mm) wide. The narrow ends of the f-hole close up almost completely.
- Hidden: the hole in the top is untouched, and the ledge starts 5 mm down. Blackened, it will not show at playing distance. It will show to anyone who looks into the hole. **[judged]**
- Cost: a 6 mm slot has roughly twice the wall friction of the full-width hole. I estimate the resonance sharpness falls from about 30 to about 22-25, worth about 1 dB of the band gain. **[judged, from the air-loss sensitivity in section 8]**

If the liner is kept plain and only as deep as fits comfortably (up to 0.9 in), A' gains only +0.8 dB (0.0 to +1.6) at 200-300 Hz. **[computed]**

---

## 5. The 300-500 Hz loss and the "unchanged mean level" (question 5)

Both are **reproduced**, and the loss is a real trade, not a band-edge effect. **[computed]** (`a1_spectra.py`, `d2_notes.py`)

Third-octave change, A' against the untuned baseline:

| Band centre | 80-200 | 250 | 315 | 400 | 500 | 630 | 800 | 1000 |
|---|---|---|---|---|---|---|---|---|
| A' | +0.1 to +0.4 | +3.0 | +3.6 | -3.3 | -1.3 | -0.8 | +2.7 | +1.3 |

The baseline's loudest feature is a peak of 74.5 dB at 425-441 Hz (the bass wing flapping against the air). Moving the air resonance down takes energy out of that peak: A' cuts it to 66-73 dB.

The 200-300 Hz number does depend on where the band edges are drawn:

| Band | A' gain |
|---|---|
| 200-300 Hz | +5.9 dB |
| 200-330 Hz | +4.1 |
| 180-360 Hz | +3.2 |
| 200-500 Hz | -2.2 |
| 80-1000 Hz | -0.6 |

About half of the headline gain is the air resonance crossing the 300 Hz line from 320 Hz. Inside the band the gain is one narrow peak at 288 Hz, about 10 Hz wide. From 200 to 255 Hz the gain is only +0.4 to +1 dB.

**Per-note level change, A', fundamental, dB** (rows are strings, columns frets 0 to 12; held, corrected radiation map):

| String | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2 | +0.2 | +0.2 | +0.2 | +0.2 | +0.2 | +0.2 | +0.1 | +0.2 | +0.2 | +0.2 | +0.2 | +0.3 | +0.3 |
| A2 | +0.1 | +0.1 | +0.1 | +0.2 | +0.2 | +0.2 | +0.2 | +0.2 | +0.3 | +0.3 | +0.3 | +0.4 | +0.5 |
| D3 | +0.1 | +0.0 | +0.2 | +0.2 | +0.3 | +0.3 | +0.4 | +0.5 | +0.5 | +0.7 | +1.3 | +4.1 | +8.1 |
| G3 | +0.2 | +0.3 | +0.5 | +0.6 | +0.5 | +0.6 | +3.5 | +7.8 | -3.3 | -1.1 | -1.9 | +0.1 | +0.6 |
| B3 | +0.2 | +0.7 | +3.7 | +8.0 | -2.7 | +0.1 | -1.9 | +1.1 | -2.4 | +3.5 | -5.3 | -0.2 | -0.1 |
| E4 | -4.0 | -1.7 | +0.1 | +0.6 | +2.8 | -7.3 | +0.1 | -0.3 | -0.1 | -0.4 | -3.3 | -3.4 | -2.9 |

- D4 gains about +8 dB wherever it is played; C#4 gains +3.5 to +4.1 dB.
- A4 loses 5 to 7 dB, the open high E loses 4 dB, D#4 loses about 3 dB, and D5 to E5 on the high E lose about 3 dB.
- Every note below B3 (247 Hz) changes by less than 1 dB.
- Mean over the 78 fundamentals: +0.2 dB. Weighted over four partials as the report does: -0.25 dB (report: -0.2). 7 fundamentals gain more than 3 dB and 6 lose more than 3 dB.

**[judged]** This is not "more 200-300 Hz". It is one loud note pair near C#4/D4 bought with a quieter A4. A player will hear D4 jump out unplugged. Whether that is liveliness or a wolf note is a matter of taste, and it argues for placing the air resonance between two notes rather than on one.

---

## 6. Sustain (question 6)

Recomputed with my own code (`d2_notes.py`): added loss factor = 2 Z0 G / (π n), G the combined conductance of both string ends including their cross term, both polarisations, 10-46 set at 25.5 in.

**A': reproduced. [computed]**

| | Mine | Report |
|---|---|---|
| Notes shortened more than 25 % (vertical) | 1 | 1.1 (0 to 3) |
| Worst note | C#5, high E fret 9: -30 % | C#5: about -30 % |
| Next worst | E4 on G string -19 %, E4 open -17 %, G4 on G string -16 % | — |
| Notes shortened more than 25 % (horizontal) | 0 | not reported |
| Notes lengthened more than 25 % | 4 (D5 +115 %, three F4s +37 to +56 %) | 2.0 |

The result holds for string Q from 1500 to 4000 (0 to 2 notes shortened) and for pivot damping from 0.05 to 0.30 (1 note, C#5, -28 to -30 %). Low E and A strings are untouched, as reported.

A liner retuned on the unchanged baseline shortens no note by more than 10 %. So the C#5 loss comes from the thinner back skin, not from the liner.

B' for the record: 4 notes vertical plus 2 horizontal (A2 on two strings, -63 %), against the report's 2.8 (0 to 6). **Different number**, on the unfavourable side.

---

## 7. Top-skin strength (question 7)

**Independent plate model. [computed]** (`c2_plate.py`, `c2b_point.py`) Orthotropic shear-flexible plate on the real chamber plan, clamped at the chamber walls, free at the f-hole edge, uniform thickness, 50 N on 1 in² scanned over 422 positions. Elastic constants as in the study.

| Top skin | Field, MPa | Beside the f-hole | At the clamped wall | Study's "field peak" | Deflection, worst |
|---|---|---|---|---|---|
| 4.0 mm | 2.62 | 2.80 | 3.68 | 2.00 / 2.08 | 1.79 mm |
| 4.5 mm | 2.06 | 2.17 | 2.93 | 1.58 | 1.27 mm |
| 5.0 mm | 1.66 | 1.72 | 2.39 | 1.28 / 1.30 | 0.94 mm |

Like for like:

- The study's peak is over the chamber wall near (23.3, 2.7). Pressing there my model gives 1.85 MPa at 5 mm (1.64 MPa if the wall fillet moves the clamp line in by 0.15 in), against 1.28-1.30. **Different number: mine is 1.3 to 1.4 times higher at the same spot, and 1.8 times higher at the worst spot** (press at (22.1, 3.1), stress at the spine wall).
- Deflection at the report's bench point (23.8, 3.6): mine 0.80 mm at 5 mm (0.66 with the fillet allowance), report 0.55-0.62. **Reproduced within about 10 to 30 %.** Stiffness agrees; the peak stress at the clamped edge does not, which is what one expects from a 1/6 in mesh with one element through the skin.
- Softer cross-grain stiffness (flat-sawn, 0.045 instead of 0.07 of the along-grain value) lowers the stress by 17 %. Stiffer (0.10) raises it by 15 %.
- Rolling shear is 1.0 MPa at 5 mm. Not the governing stress.

Safety factors on my numbers, 5.0 mm, 50 N on 1 in²:

| | Field (1.66 MPa) | Wall (2.39 MPa) |
|---|---|---|
| Plain alder, 2.9 MPa | 1.75 | 1.2 |
| Roasted, 2.0 MPa assumed | 1.2 | 0.85 |

The report's 1.8 to 2.2 (plain) and 1.3 to 1.6 (roasted) are **different numbers: mine are lower.**

**The allowable.** 2.9 MPa is the Wood Handbook figure for red alder, tension perpendicular to grain, at 12 % moisture (FPL-GTR-190, Table 5-3a; same row: modulus of rupture 68 MPa, modulus of elasticity 9.5 GPa). **Reproduced** from the handbook. Two cautions:

- It is a mean of small clear specimens, with board-to-board scatter of about ±25 %.
- The skin fails in bending across the grain, not in uniform tension. Bending strength across the grain is normally higher than the tension figure because only a thin surface layer is at peak stress. I looked for a citable ratio for hardwoods and did not find one. **Could not check.** This probably makes 2.9 MPa conservative for the skin, so the true margin is likely better than the table above. It is not evidence I can put a number on.
- The 30 % loss for roasting is the study's assumption. **Could not check.**

**The load case. [judged]** 50 N on 1 in² is a moderate thumb press. A hard thumb press is 80 to 100 N. The same 50 N on a knuckle or a case latch (0.5 in square) gives 2.5 to 2.8 MPa in a 5 mm skin. The case is on the light side for an instrument that will be gigged.

**Verdict. [judged]** 4.0 mm is not enough: reproduced. 5.0 mm is the least that should be built, and in roasted alder it does not reach a safety factor of 2 on either the study's numbers or mine. The report's own fallback (5.0 mm plus a 0.6 mm cross-grain veneer under the chamber roof, or 6.0 mm with cleats) is the one to build. The spine-wall edge, not only the f-hole ends, deserves a generous fillet.

---

## 8. Uncertainty and ranking (question 8)

**Were the 40 draws wide enough? No. [computed]** (`d4_mc.py`, 24 paired draws)

I widened: alder stiffness ±20 % (study ±15 %), skin cross-grain stiffness a further ±30 % (±8 %), maple ±15 %, hold stiffness x0.3 to x5 (x0.5 to x2), pickguard contact x0.1 to x10, air loss 0.008 to 0.03 (to 0.02), tuner mass, chamber volume ±5 %. The baseline gets its own best liner in every draw. My air-loss and hold ranges lean pessimistic on purpose.

| 200-300 Hz gain over the untuned baseline | Mine, median (5-95 %) | Report |
|---|---|---|
| Liner only, baseline wood | +1.8 dB (+0.6 to +4.4) | +4.0 (single case) |
| A', best liner | **+3.6 dB (+1.7 to +6.7)** | +5.4 (4.1 to 7.3) |
| A', liner fixed at the nominal factor | +2.7 dB (+0.3 to +5.4) | +4.4 (2.8 to 6.3) |
| A', plain liner that fits | +0.8 dB (0.0 to +1.6) | — |
| A' over a tuned baseline | +1.7 dB (+0.8 to +2.7) | — |

| 300-500 Hz change | Mine | Report |
|---|---|---|
| A', best liner | -2.5 dB (-3.6 to -1.2) | -2.7 (-3.9 to -1.2) |

- The 300-500 Hz loss is **reproduced** almost exactly.
- The 200-300 Hz gain is **reproduced at nominal values (+5.9 dB) and comes out lower, +3.6 dB, under wider draws.** The report's claim that A' clears 3 dB in 100 % of draws when trimmed does not hold: in mine it clears 3 dB in 18 of 24 draws with the liner retuned per draw, and in 10 of 24 with the liner left at the nominal factor.
- What drives the spread: how firmly the guitar is held (correlation -0.57 with the gain) and air loss (-0.52). Wood stiffness and wood loss barely matter once the liner is retuned.

**Does anything flip the ranking? [computed]** No. A' beat the tuned baseline in 24 of 24 draws and by more than 1 dB in 88 %. Nothing I varied reverses the order baseline < A' at 200-300 Hz.

**Variables the study held fixed that move the result:**

- Baseline liner tuning (never retuned): worth 4 to 5 dB of the headline.
- Pickguard contact stiffness beyond x0.3 to x3: moves the twisting mode ±15 Hz.
- Tuner mass: ±6 Hz on the mode.
- Cross-grain stiffness ratio of alder: the same value is used for the radial and tangential directions.
- Losses in a narrowed liner: the liner is modelled only as extra air mass, so the extra friction of the 6 mm slot A' needs is not in the study. With air loss x2.5 the A' gain falls from +6.3 to +3.6 dB.
- Skin thickness tolerance, pickup and hardware masses, the boundary-element surface, humidity.

---

## 9. The tail pocket and B' (question 4), brief

Out by the owner's decision. Findings, all **[computed]** (`c3_pocket.py`, `c1_run.py`):

- **No breakthrough.** Least wood between pocket and outside: 4.7 mm. Vertical skins are 5.0 mm top and back everywhere. Rim 0.30 in.
- **Size.** The pocket ends at x = 30.88 (the 0.30 in rim stops it), not 31.0 as reported or 31.3 as coded. It is 9.4 in² and 10.8 in³, and 6.0 in³ of that is in the centre block behind the tremolo.
- **One build problem.** Under the forearm contour 0.41 in² of pocket roof (4 %) falls below the glue plane, where it cannot be routed from the glue face and the top half is only 4.0 mm thick. Trimming it costs 0.2 to 0.6 in³.
- **Strap button.** The boss gives 0.80 in of wood along the screw, 1.0 in wide, and is joined to the rim and skins only; 0.85 in of hollow separates it from the centre block. A 1 in screw nearly reaches the pocket.
- **What it does acoustically.** Added air volume. The air resonance drops from 316 to 287 Hz, which matches the volume ratio (√(57.3/68.0) = 0.917) to 1 %. Body modes barely move (287.5 to 288.8 Hz). At equal air tuning the pocket adds about +0.7 dB at 200-300 Hz and costs about 2.4 dB more at 300-500 Hz.
- **Why it looked best.** With the pocket a plain 0.75 in liner gives 286 Hz (rigid; study 292), so B' needs no narrowed throat. That is its real advantage, and the reason B' leads by +3.7 dB when both designs are limited to liners that fit. With free tuning B' leads A' by only +1.1 dB (+0.5 to +1.6).
- **B' claims.** +6.2 dB: reproduced at nominal (+6.6; +7.2 with the corrected map), +4.7 dB (2.8 to 8.1) under wider draws. -5.1 dB at 300-500: different number, -3.0 (-7.1 to -0.6). Per note it is harsher than A': C#4 +10.8, A4 -12.2, G#4 -9.4 dB.

---

## 10. Code errors and modelling faults (question 9)

None changes the direction of the conclusions. In order of consequence:

| Finding | Effect |
|---|---|
| Designs are tuned, the baseline is not | Headline gain overstated by 4 to 5 dB as a statement about the wood changes. |
| Liner modelled as a multiplier on plug air mass, not as geometry | Hides that A' needs a 45 % narrowed throat with extra friction, and that a plain liner cannot reach the target. |
| Cross-grain modulus equal for radial and tangential (0.07 of along-grain) | Flat-sawn skins would be about 30 % softer across the grain. Skins x0.7 moved the mode to 281 Hz and raised the A' gain to +7.7 dB. |
| Exterior map leaks rigid-body motion into net volume flow | Confirmed. 7 dB of the baseline's apparent monopole at 200-300 Hz is leak or pickguard. Effect on the gain: +0.4 dB, favourable. |
| Pickguard modes read as body modes | The "196 Hz torsion agrees with published" match is a pickguard mode. |
| Tremolo block hole 1.05 in long through all layers | Larger than a real top slot (about 0.55 in). Weakens the pivot ledge and probably raises the 440-690 Hz conductance peaks. No effect on the 200-300 Hz gain. |
| Pivot stiffness and damping are guesses; spring surge not modelled; "8e-3 for a Strat trem" unsourced | Absolute conductance unvalidated. Design comparisons unaffected. |
| Pockets ignore the carve limit and the glue plane | 4 % of the B' pocket roof unbuildable (moot now). |
| Bare-hole air resonance 3.5 % low | Small. The liner values agree with mine. |
| Thin-disc check of the boundary-element code off by 1.8 to 3.3 dB | Baseline structural radiation uncertain by that much; the hole source is not. |

Checked and found sound: units, the orthotropic axes (grain along x), the sign of the air-structure coupling (the port-only and chamber-monopole powers agree within 1 dB), hardware masses, the decay formula, and thin-skin element behaviour (my plate deflection agrees with the study's solid elements within 10 to 30 %).

---

## 11. Claim-by-claim status

| Claim | Status |
|---|---|
| Whole-body twisting mode near 283-288 Hz | Reproduced (287.4 Hz free, 288 Hz held); ±15 Hz in reality |
| A' +5.4 dB at 200-300 Hz (4.1 to 7.3) | Reproduced at nominal (+5.9; +6.3 corrected). Different number under wider draws: +3.6 (1.7 to 6.7) |
| A' -2.7 dB at 300-500 Hz | Reproduced: -2.5 (-3.6 to -1.2) |
| Mean level over all notes unchanged | Reproduced: -0.25 dB |
| A' needs a throat narrowed 35-45 % | Reproduced: about 45 % over the full 0.75 in depth |
| Air resonance 364-365 Hz bare, 320-324 Hz with liner | Different number bare (378 Hz); reproduced with liner (320-325 Hz) |
| Hand estimate 400-456 Hz bare | Not reproduced |
| Leak changes totals by at most 0.07 dB | Different number: 0.4 to 0.6 dB on the gain |
| A' shortens about 1 note by more than 25 %, C#5 about -30 % | Reproduced |
| Baseline 21 of 78 notes past halving | Reproduced (21 to 23) |
| Peak bridge conductance 1.8e-2 s/kg at 659 Hz | Reproduced as a model output; could not check against reality |
| 4.0 mm top: safety factor 1.3-1.4 plain, about 1.0 roasted | Different number: 0.8 to 1.1 plain |
| 5.0 mm top: safety factor 1.8-2.2 plain | Different number: 1.2 to 1.75 plain, 0.85 to 1.2 roasted |
| Alder allowable 2.9 MPa | Reproduced (Wood Handbook Table 5-3a); bending across grain could not check |
| Roasting costs 30 % of cross-grain strength | Could not check |
| B' +6.2 dB / -5.1 dB | Reproduced at nominal; different numbers under wider draws (+4.7 / -3.0) |
| B' about 3 notes shortened | Different number: 4 to 6 |
| Tail pocket does not break through | Reproduced (4.7 mm least wood) |
| 85 g lighter (B') | Reproduced (2.9385 to 2.8533 kg) |

---

## 12. Bench measurements that would settle what the model cannot

1. **Twisting mode of this body.** Neck, tuners and pickguard fitted, hung from the strap buttons. Tap the bass wing tip, microphone or accelerometer at the wing. Read the mode near 270-305 Hz. Repeat with the pickguard screws loose: if it moves by more than 5 Hz the pickguard is part of the mode.
2. **Air resonance, bare and lined.** Halves dry-clamped. Small speaker near the hole, microphone at the hole, hole open then taped. Predictions to test: 372 Hz bare (study 365), 316-320 Hz with a plain 0.75 in liner.
3. **Liner trial pieces.** Three removable liners, 0.75 in deep, at 100 %, 70 % and 55 % of the hole area. Read the air resonance and the width of its peak for each. My predictions: 316, about 300 and about 285 Hz. If the peak is more than about 15 Hz wide with the narrow liner, the gain will be nearer +2 dB than +4.
4. **The audible result.** With each liner, play C#4, D4, A4 and the open high E unplugged and record at 0.5 m. Predictions for the 55 % liner: D4 up about 8 dB, A4 down 5 to 7 dB.
5. **Skin stiffness.** 5 kg on a 1 in² pad at (23.8, 3.6), dial gauge. I predict 0.66 to 0.80 mm at 5.0 mm; the study predicts 0.55 to 0.62 mm.
6. **Skin strength.** Offcut of the same roasted board, 5.0 mm thick, clamped across a 3 in span with the grain along the clamps, loaded to failure through a 1 in pad. This replaces both the 2.9 MPa handbook figure and the 30 % roasting assumption. Repeat with the 0.6 mm cross-grain veneer.
7. **Bridge mobility.** Tremolo fitted and floating, accelerometer at a saddle, instrumented tap beside it, 100 to 1000 Hz. A peak above about 5e-3 s/kg between 440 and 700 Hz confirms the model's lively tremolo; below 2e-3 means the baseline's decay figures are pessimistic.

---

## 13. Files in this folder

| File | What it is |
|---|---|
| `b1_build.py`, `run_builds.sh`, `rom_*.pkl`, `shapes_*.npz` | Reduced models rebuilt from the study's modules |
| `common.py` | My own contacts, radiation correction and spectrum code |
| `a1_spectra.py` | Third-octave and band-edge tables from the stored spectra |
| `d0_modes.py` | Baseline mode table and volume-flow check |
| `d1_gain.py`, `d1_gain.json`, `spec_*.npz` | Gains with three radiation maps; power split; tuned baseline |
| `d1b_bc.py`, `d1b_bc.log`, `d1b_bc.json` | Boundary-condition and parameter sweep |
| `d2_notes.py`, `d2_notes.log`, `notes_nominal.npz` | Per-note level and decay |
| `d3_cond.py`, `d3_cond.log` | Bridge conductance and tremolo sensitivity |
| `d4_mc.py`, `d4_mc.log`, `d4_mc.json` | Wider paired Monte Carlo |
| `c1lib.py`, `c1_run.py`, `c1_*.log`, `c1_*.json` | Independent chamber-air solve, liner and throat cases |
| `c2_plate.py`, `c2b_point.py`, `c2_*.log` | Independent top-skin plate model |
| `c3_pocket.py`, `c3_pocket.log` | Tail-pocket geometry against the real carve |

Sources for the alder strength figure: [Wood Handbook chapter 5, Mechanical Properties of Wood](https://www.cedengineering.com/userfiles/S04-019%20-%20Wood%20as%20An%20Engineering%20Material%20-%20Mechanical%20Properties%20of%20Wood%20-%20US.pdf) (Table 5-3a, red alder, 12 % moisture). On the size effect in tension across the grain: [Aalborg University, size effect in tension perpendicular to the grain](https://vbn.aau.dk/da/publications/size-effect-in-tension-perpendicular-to-the-grain).
