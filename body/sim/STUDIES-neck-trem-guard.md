# Supercaster II: neck, trem, pickguard and room studies (2026-11-13)

**Model status: NOT VALIDATED** (MODEL.md section 3: 18 of 28 checks pass). These parts can be trusted:
- the 80–300 Hz and 500–1000 Hz bands;
- the air resonance A0, but read it 2.5 % low: here it is 278.7 Hz against 285.8 Hz;
- rankings that rest on clear mechanisms: a mode that moves onto a note, a mass change, a post that pins the roof.

These cannot be trusted:
- the 300–500 Hz band (validation off by −6.5 to +2.7 dB) and the body twist mode (+29 Hz);
- absolute bridge conductance, which runs 7–10× above published solid-body values;
- absolute decay times.

Every effect below gets a trust grade. Anything that rests mainly on 300–500 Hz, the guard contact or the pivots is graded low.

Tags:
- [computed] means this model;
- [literature: source] means a number read in that source;
- [judged] means my choice.

## 0. Bottom line

Every recommendation is hidden; none changes the traditional look of the guitar. **Nothing in these studies gives a new audible gain. The audible gain is the one the plan already has: the bass-wing chamber with the narrowed liner.** These studies mostly confirm the plan and add two "don't" rules.

| Rank | Finding | Audible? (≥1 dB broadband, ≥3 dB on a note, ≥15 % decay) | Trust | Action |
|---|---|---|---|---|
| 1 | Chamber + narrowed liner vs a solid body of the same build: +3.2 dB broadband radiated power, +6.8 dB at 200–300 Hz; +3.1 dB broadband in the room at 2–3 m. At the player's ear (9 head positions), +3.0 to +5.9 dB broadband in the room [computed] | Yes | Medium at 80–300 Hz, low at 300–500 Hz | Keep (already decided) |
| 2 | **Don't use a titanium trem block.** Its rocking mode moves from 66 Hz to 81.6 Hz, onto open E2. The result is unevenness: unplugged, E2 is +7.4 dB and F2 next to it −6.5 dB, there is more felt vibration, and E2 decays faster (−13 % at the computed frequency, −10 % averaged over ±10 %; below the 15 % bar on its own). At resonance the E2 bridge conductance is 7.5e-3 s/kg, 7.5× the low-E halving budget. With 5 springs the mode sits at 86.6 Hz, on F2 [computed] | Yes on level evenness; decay borderline | Medium | Keep the steel block |
| 3 | **Bosses under the three chamber guard screws must hang, not post to the back.** Hanging 19 mm bosses: ≤0.2 dB, no note changes. Posts to the floor: −3.9 dB at 200–300 Hz, −2.2 dB at 500–1000 Hz, C#4 notes −5 to −8 dB (they cancel the liner's C#4/D4 gain) [computed] | Yes (harm avoided) | Medium | Hanging bosses, as planned |
| 4 | Truss rod: one-way vs two-way, steel vs Ti. Mean neck-limited decay changes ≤2 %; expected dead notes 6.4–6.8 of 78 [computed] | No | Medium | Two-way steel, as planned. Ti is acoustically neutral and saves 54 g |
| 5 | Carbon rods: weaken the ~282 Hz neck mode 3× but move it to ~305 Hz. Seven notes change by 15–46 % in both directions; net mean decay +1–2 % [computed] | Per-note only, mixed sign | Medium | Not for tone. Decide on stability alone |
| 6 | Trem springs 3 vs 5 (steel block): rocking mode 66.3 → 70.3 Hz, no level, decay or note change ≥0.1 dB / 15 % [computed] | No | Medium | Set by feel and setup |
| 7 | Brass block: rocking mode −2.9 %, ≤0.5 dB [computed] | No | Low | None |
| 8 | Guard screw torque / stiffness: ≤0.6 dB. How flat the guard bears on the top (contact ×0.1 or ×10): +1.3 to +2.4 dB in some bands, in both directions [computed] | Borderline, sign uncertain | Low | Fit the guard flat with no rattle and normal torque. Measure before tuning |

## 1. Set-up

**Study baseline (S0)**
- `final_narrowed` (section 0 build) with `wood=json` (roasted alder, roasted maple);
- curly roasted maple neck (`neck_curly`: E_L 12.4 GPa, η 0.0099 [literature: wood-properties.json]);
- locking tuners at 37 g each [literature: Schaller F-series 37 g, Rockinger 35.5 g and Graph Tech 38 g per tuner, retailer listings read through a web-search summary];
- two-way steel truss rod.

S0 mass 2.841 kg, balance 18.08 in from the nut [computed]; the model still omits finish, strings and electronics.

Model additions, all off by default (MODEL.md section 6); validation reproduces 18/28 and the baseline bands to the printed digit:
- **Truss rod.** Rods sit in the neck beam with their slot of maple removed. Coupling has three brackets: mass only, "tendon" (mass + the rod's own bending + an axial spring EA/L between the anchors at rod height; nominal), and fully bonded. Two-way steel is modelled as two 3/16 in rods in a 7/32 × 7/16 in slot. Its weight is set to the listed 139 g for an 18 in Hot Rod [literature: stewmac.com listing, read through a search summary]. Ti-6Al-4V uses E 114 GPa and 4430 kg/m³ [literature: standard alloy data]. The one-way rod is a single 3/16 in steel rod, 0.45 in deep [judged geometry]. The rod part inside the body tenon is not modelled: it sits in the rigid joint block.
- **Carbon bars.** Two pultruded bars, 1/8 × 3/8 in, bonded, E 135 GPa, 1550 kg/m³ [judged].
- **Trem block.** Same dimensions as before (0.45 × 2.25 × 1.55 in). Steel 0.202 kg, Ti 0.114 kg, brass 0.219 kg [computed]. The trem is a rigid body, so only mass and inertia change. Metal stiffness and damping are not modelled.
- **Guard bosses.** 1/2 in alder, either hanging 19 mm or as posts to the floor; the screws can also be finite springs. The boss volume is not removed from the air network (0.3 in³ of 53.6, about 0.3 % on A0 [computed]).
- **Room.** Field pressure from the BEM panel pressures through the Kirchhoff–Helmholtz integral (exact near field, free field), plus a diffuse field for a 50 m³ room with RT60 0.5 s [judged].
  - On pulsating and oscillating spheres it is within 0.07 dB of the exact result [computed].
  - Its radiated power matches `run_case` within 0.6 dB in every band [computed].

**Decay metric.** A string's decay is set by the conductance G at the bridge plus at the fret: T60_body = 6.91 L/(T G) [literature: Paté, Le Carrou & Fabre 2014, as used in rom.py]. I combine it with the string's own decay, taken as 8 s [judged]: 1/T_eff = 1/T_body + 1/8. A note counts as "dead" when T_body < 8 s, which halves its decay or worse.

**Sensitivity to the 8 s figure.** Re-running every decay ranking with the string's own decay at 4 s and at 15 s changes no ranking [computed].

**The ±10 % window.** A neck mode is uncertain by about ±10 %: from board-to-board variation (acoustic-hybrid.md section 1) and from this unvalidated model. So I read each note's fret and bridge conductance over f × [1/1.1, 1.1] and average the decay over that window (`study_deadspots.py`). Trem and guard modes are no better known than neck modes, so the bridge side gets the same window. Single-note numbers swing by hundreds of percent when a mode moves 2 %, and those swings are noise for a build decision. The windowed numbers are the ones I rank on.

## 2. Neck and headstock: dead spots, truss rod, carbon

**Where the dead spots are (S0)** [computed]
- **Neck mode 2: 177 Hz**, fret-conductance peak 0.063 s/kg. This is the main dead-spot zone, F3–F#3: D string frets 3–4 and A string frets 8–9. F3 on the D string, fret 3, has T_body 1.6 s.
- **Neck mode at 282 Hz**: peak 0.148 s/kg, the largest on the neck. It hits C#4–D4: G string frets 6–7, B string frets 2–3, D string frets 11–12. This is the same 288 Hz mode that MODEL.md calls 77–79 % neck strain.
- **Lower modes at 64 Hz and 109 Hz**, and a floating-trem mode at 65 Hz.
- **Point-estimate dead notes: 11 of 78.**
  - Neck-driven: D3/3, D3/4, B3/2, B3/8, B3/9, G3/12.
  - Bridge-driven: high E frets 10–12 (D5–E5), from the 600–676 Hz trem/guard modes. **Low trust**, because bridge peaks run 7–10× published values.
- **Windowed expected dead notes from neck loss alone: 6.4.**

The fret-conductance peak (0.15–0.18 s/kg) is the same order as Paté's measured neck maximum of about 0.10 s/kg (as quoted in sim3d-REPORT 3.3, not re-read).

**Rod options.** All runs use json wood, curly neck and 37 g tuners. Neck-only columns use fret conductance alone, windowed ±10 %.

| Option | Mass (kg) | Balance (in) | Mode 2 (Hz) | 282-type mode (Hz) | Peak G_fret, mode 2 / 282 (s/kg) | Neck-only T_eff geo-mean (s) | Worst note T_eff (s) | Expected dead (neck) |
|---|---|---|---|---|---|---|---|---|
| no rod (reference only) | 2.731 | 18.50 | 187.5 | 290.8 | 0.062 / 0.135 | 6.33 | 2.79 | 6.84 |
| one-way steel | 2.787 | 18.28 | 181.8 | 286.3 | 0.063 / 0.142 | 6.39 | 2.99 | 6.78 |
| **two-way steel (S0)** | 2.841 | 18.08 | 177.3 | 281.6 | 0.063 / 0.148 | 6.45 | 3.03 | 6.44 |
| two-way Ti | 2.787 | 18.28 | 181.9 | 283.2 | 0.064 / 0.153 | 6.38 | 2.99 | 6.77 |
| two-way steel + carbon | 2.862 | 18.01 | 180.8 | 305.3 | 0.056 / 0.050 | 6.53 | 3.29 | 6.14 |
| two-way Ti + carbon | 2.808 | 18.21 | 185.1 | 306.9 | 0.057 / 0.052 | 6.48 | 3.16 | 6.35 |

**Brackets** [computed]

| Bracket | Neck-only T_eff geo-mean (s) |
|---|---|
| Steel, mass-only / tendon / bonded coupling | 6.44 / 6.45 / 6.53 (mode 2 at 175.7 / 177.3 / 183.8 Hz) |
| Ti bonded | 6.41 |
| Steel, neck E −10 % / +10 % | 6.40 / 6.49 |
| Ti, neck E −10 % / +10 % | 6.34 / 6.43 |
| Steel + carbon, neck E −10 % / +10 % | 6.52 / 6.56 |
| Reference wood set: steel / Ti / steel + carbon | 6.39 / 6.33 / 6.51 |

Tuners at 30 g instead of 37 g: 6.46, and mode 2 moves +1.8 %.

**Reading**
- **Rod type moves mode 2 by about 45–100 cents.** No rod to two-way steel is −97 cents; Ti to steel is −45 cents. A ±10 % change in neck stiffness moves it −47/+39 cents, so the choice of rod is no bigger than normal board variation [computed].
- **No rod changes mean decay by ≥15 %.** Two-way steel and one-way or Ti are within 1–2 %. Steel is a hair more even in every bracket (about 1 %, inaudible) [computed].
- **Ti saves 54 g** and moves the balance 0.2 in toward the body, so less neck dive [computed]. Plan section 3 already wants a two-way rod adjusted at the headstock, so keep two-way steel. Ti is fine if weight matters, but it carries a known thread-galling risk [literature: forum and vendor notes, via search, not verified].
- **Carbon bars do one robust thing:** they cut the 282 Hz neck mode's fret conductance about 3× (0.148 → 0.050; the same in all four brackets) and move it to about 305 Hz. The effect on notes is a trade, consistent across the json, reference and E ±10 % brackets:
  - **better:** C4 on B/1 +35–46 %, C#4 on B/2 +13–34 %, E3 on D/2 +15–25 %, C4 on G/5 +12–18 %, F#4/G4 on B/7–8 +12–19 %;
  - **worse:** D#4 on B/4 −13 to −28 %, E4 on B/5 −12 to −29 %, G4 on E/3 −11 to −19 %.
  - Net mean +1–2 %, expected dead notes −0.1 to −0.6 overall. The dead spot becomes shallower and moves; it does not go away. The fret-7 neck-back velocity drops 14 dB at 200–300 Hz, so it would feel calmer in the hand there [computed].
  - **Not recommended for tone.** Decide on stability only, as the plan says.
- **Best rod for evenness and sustain:** none is audibly better. Two-way steel is marginally best without carbon, and it is the planned part.

## 3. Trem: block metal, spring count, rocking mode

Each case is S0 plus that block. Notes nearby: C2 65.4, D2 73.4 (drop-D), E2 82.4 and F2 87.3 Hz.

| Block | Trem mass (kg) | Rocking mode (3 springs) | With 5 springs | Bands vs steel (80–200 / 200–300 / 300–500 / 500–1000 dB) | Notes ≥15 % or ≥3 dB |
|---|---|---|---|---|---|
| steel (vintage) | 0.347 | **66.3 Hz** (+24 cents above C2; −182 cents below drop-D) | 70.3 Hz (−74 cents below drop-D) | 0 | 5 springs: none |
| titanium | 0.259 | **81.6 Hz (−17 cents from E2)** | **86.6 Hz (−14 cents from F2)** | +0.5 / −0.4 / −2.0 / +0.7 | E2 +7.4 dB, T_eff −13 %; F2 −6.5 dB; ~10 bridge-driven high-E notes ±3–9 dB. With 5 springs: F2 −19 % and +9.2 dB |
| brass | 0.364 | 64.4 Hz | not run (scaled estimate about 68 Hz [judged]) | 0 / +0.1 / −0.5 / −0.2 | 2 bridge-driven notes (G#4) −16/−23 % (low trust) |

All [computed].

**Rocking-mode frequency.** The model's 66 Hz falls inside the plan's 63–77 Hz band, but that band also came from a model, so this is model-against-model, not a check against measurement. The spring share of rocking stiffness, worked back from 3 → 5 springs, is 19 %; a hand estimate from string axial stiffness and spring rates gives 17 % [computed]. So the strings, not the springs, set most of the rocking stiffness, and spring count barely matters.

**Where the rocking mode can land.** Read with ±10 % uncertainty [computed]:
- Steel, 3 springs: 60–73 Hz. Stays below standard E2 but reaches drop-D.
- Steel, 5 springs: 63–77 Hz. Sits closer to drop-D (73.4 Hz).
- Ti: 74–90 Hz. Overlaps E2 and F2.

In standard tuning a steel block never reaches a played note. If Jordan plays in drop-D a lot, 3 springs keep the mode about 180 cents under the low D, against about 75 cents with 5.

**Decay and unplugged level**
- **Steel and brass:** E2 body-T60 about 140 s (G_bridge 3.4e-4); the rocking mode sits between notes.
- **Titanium:** at the computed frequency, E2 G_bridge rises to 1.4e-3 s/kg; at the rocking-mode peak it reaches 7.5e-3. Both are past the 1.0e-3 low-E halving budget [literature: as quoted in sim3d-REPORT 1.2, not re-read]. The open E is louder unplugged and dies faster (T_eff −13 % at the computed frequency, −10 % averaged over ±10 %). F2 next to it is 6.5 dB quieter, and the belly and forearm feel +3–4 dB more vibration at 80–200 Hz [computed]. That is a step in evenness right at the bottom of the neck.
  - Plugged in, the pickups read the string, and its decay is shorter by the same 13 %.
  - Ti's −2 dB at 300–500 Hz comes from the low-trust band, and its sign depends on the pivots. With pivot stiffness ×4: Ti −0.9 dB, brass +1.75 dB. **Treat block-metal changes above 300 Hz as unknown.**
- **Pivot stiffness ×4** (steel) changes the bands −0.1 / −0.3 / −1.5 / −0.6 dB and leaves the rocking mode alone (66.5 Hz) [computed]. Pivot fit matters more than block metal above 300 Hz. The plan's "firm pivots" stays.

**Recommendation:** keep the vintage steel block. Use 3 or 5 springs as setup requires; both are acoustically equal. Never pair a lightweight block with a floating setup: it walks the rocking mode up onto E2/F2.

## 4. Pickguard coupling to the chamber roof

All cases are S0 variants. The guard is the 13-screw guard from the plan file (a vintage guard has 11; screw count is visible, so it is studied but not recommended).

| Case | Bands vs S0 (80–200 / 200–300 / 300–500 / 500–1000 dB) | A0 | Notes ≥15 % or ≥3 dB |
|---|---|---|---|
| S0: screws rigid, no bosses | 45.93 / 56.21 / 60.72 / 66.99 | 278.7 Hz | |
| **hanging bosses, 19 mm (plan)** | −0.02 / +0.15 / −0.20 / −0.02 | 278.9 | none |
| bosses as posts to the back | −0.13 / **−3.88** / −1.16 / **−2.22** | 280.6 | C#4 (D/11, G/6, B/2) −5 to −8 dB; F#4 −25 to −35 % decay |
| no screws over the chamber | 0 / −0.18 / −0.72 / −0.92 | 278.6 | (visible change) |
| hanging bosses, screws 1e6 N/m (loose) | −0.02 / +0.27 / −0.18 / −0.62 | 278.8 | — |
| hanging bosses, screws 1e7 N/m | −0.02 / +0.16 / −0.19 / −0.06 | 278.8 | — |
| hanging bosses, guard contact ×0.1 (bears lightly) | **+2.37** / +0.26 / **+2.30** / +1.33 | 278.9 | — |
| hanging bosses, guard contact ×10 (pulled hard flat) | −0.01 / +0.13 / **+1.90** / **+2.14** | 278.9 | — |
| no guard at all (also removes 0.24 kg of pickups and controls) | +1.03 / +0.11 / +3.65 / +6.31 | 278.7 | — |

All [computed].

**Damping or shifting the roof modes?** Mostly damping [computed].
- **Without the guard**, the chamber-roof (wing) modes have loss factors of 0.008–0.012, at 362, 584, 609, 657 and 740 Hz.
- **With the guard** screwed down and bearing on the top:
  - The first roof mode moves only 362 → 357 Hz (−1.3 %), but its loss rises to 0.023, about 2×.
  - The roof modes from 580 to 660 Hz merge with guard modes into mixed modes (623 and 673 Hz) with loss 0.03–0.06, 3–6×.
- **The guard, with the hardware on it, is the main damping layer on the roof**, and it costs 3.7–6.3 dB above 300 Hz compared with a bare roof. That is the price of this style of guitar, with its large loaded pickguard, and it is not up for change.

**Screws and torque** [computed]
- The plan's hanging bosses are acoustically neutral.
- Screw-joint stiffness from 1e6 N/m to rigid moves the bands by ≤0.6 dB.
- What matters is how the guard bears on the top between the screws: the contact model gives ±2 dB, and both directions raise the level above 300 Hz. The nominal contact (2e8 N/m³, loss 0.10, both [judged]) happens to give the most damping. **Low trust:** the sign depends on two judged numbers.
- **Practical rule [judged]:** fit the guard flat to the carved top with no rattle and normal torque, then measure (plan section 7). Do not shim or space it for tone.
- **Posts are the one clear "don't".** A post ties the roof to the back, stops the roof's piston motion that drives the air resonance (A0 +1.9 Hz), and takes away the liner's 200–300 Hz gain.

## 5. Room: unplugged level and direction, final build vs solid

**Comparison.** "Solid" is this same build without the chamber or f-hole: same set neck, two-way rod and floating trem; 3.193 kg, 0.35 kg heavier. It is not a bolt-on vintage Strat; for that, the earlier reports' solid figures are the nearest [judged].

**Field points** [judged]
- Player's ear, nominal: 0.40 m above the bass edge, 0.12 m behind the top plane. A 3 × 3 grid around it (0.3–0.5 m up, 0.05–0.20 m back) tests sensitivity. No torso or head is modelled.
- Listener: on the top normal at 1, 2 and 3 m.

Levels are band means per unit vertical saddle force, averaged over the six saddles, in dB re 20 µPa/N. Treat them as relative, not absolute SPL. The room is a diffuse field in 50 m³ with RT60 0.5 s [judged]; its critical distance is about 0.7 m [computed, standard formula], so at 2–3 m a listener mostly hears radiated power. All rows below are [computed].

| Point | Final: 80–200 / 200–300 / 300–500 / 500–1000 / 80–1000 | Solid | Final − solid |
|---|---|---|---|
| radiated power (dB re 1 pW/N²) | 45.4 / 56.0 / 60.5 / 67.3 / 62.5 | 43.1 / 49.2 / 57.8 / 64.1 / 59.3 | **+2.3 / +6.8 / +2.8 / +3.2 / +3.2** |
| player's ear (nominal), direct | 37.0 / 52.9 / 53.3 / 62.8 / 57.7 | 33.5 / 38.1 / 50.2 / 56.3 / 51.5 | +3.5 / +14.8 / +3.1 / +6.4 / +6.2 |
| player's ear (nominal), in room | 41.4 / 54.7 / 57.0 / 65.1 / 60.2 | 38.8 / 44.4 / 54.1 / 60.4 / 55.6 | +2.7 / +10.3 / +2.9 / +4.8 / +4.7 |
| player's ear, 9-position range, direct | | | +3.1–4.4 / **+9.5–25.6** / +2.1–6.2 / +2.6–8.1 / **+2.9–8.0** |
| player's ear, 9-position range, in room | | | +2.3–3.1 / **+8.8–13.1** / +2.8–4.8 / +2.8–5.9 / **+3.0–5.9** |
| front 1 m, direct | 39.7 / 46.9 / 54.1 / 60.6 / 55.7 | 37.5 / 43.3 / 50.8 / 58.2 / 53.3 | +2.2 / +3.6 / +3.2 / +2.3 / +2.5 |
| front 45°, 1 m, direct | 37.9 / 45.6 / 52.0 / 55.1 / 51.1 | 35.7 / 41.2 / 48.5 / 52.1 / 48.0 | +2.2 / +4.5 / +3.4 / +3.0 / +3.1 |
| front 2 m, in room | 40.4 / 50.6 / 55.5 / 62.2 / 57.4 | 38.2 / 44.3 / 52.7 / 59.2 / 54.3 | +2.3 / +6.3 / +2.8 / +3.0 / +3.1 |
| front 3 m, in room | 39.9 / 50.3 / 55.0 / 61.8 / 57.0 | 37.7 / 43.7 / 52.2 / 58.7 / 53.8 | +2.3 / +6.6 / +2.8 / +3.1 / +3.1 |

**Direction** [computed]
- **The solid body radiates as a dipole.** At 200–300 Hz, 1 m: front 43.3, back 43.4, in-plane "up" 18.2 dB. So a solid Strat throws almost nothing toward the player's head.
- **The f-hole adds a monopole and makes 200–300 Hz nearly omnidirectional:** front 46.9, back 48.8, up 44.1.
- **So the player gains most.** At 200–300 Hz the ear hears the final build 6 dB above a listener at 1 m, where the solid build is 5 dB below.
- **Treat the ear deltas as a range, not a number.** The final build's level at the ear is steady across the 9 positions (50.9–55.6 dB at 200–300 Hz). What varies is how deep the solid body's dipole null is, and a real head and torso partly fill that null. The robust numbers are the radiated power and the room level at 2–3 m: +3.1 to +3.2 dB broadband and +6.3 to +6.8 dB at 200–300 Hz.

**In hand.** Belly-patch velocity is +5 / +9 / +12 / +16 dB over solid by band, and the forearm +3.6 / +3.4 / +4.3 / +11.6 dB [computed]. You will feel the chambered body more.

**Sustain cost of the chamber vs solid** [computed], fret and bridge windowed
- Mean T_eff −1.0 % (6.08 → 6.02 s); −0.6 % with the string's own decay at 4 s, −2.1 % at 15 s.
- Expected dead notes 8.6 → 9.4 of 78; most of the difference is the low-trust bridge-driven high-E notes.
- Neck-only expected dead notes: 6.9 (solid) vs 6.4.

**Trust**
- Medium at 80–300 Hz and 500–1000 Hz.
- Low at 300–500 Hz: the solid-minus-current difference failed validation there.
- The 200–300 Hz ear figure depends on A0, which the model puts 2.5 % low.
- Floor and wall reflections, the torso, and radiation from the neck are not modelled.

## 6. Recommendations (hidden only, nothing visible changes)

1. **Keep the planned chamber and narrowed liner.** It is the only lever here above the audibility line: about +3 dB broadband in the room (+6–7 dB at 200–300 Hz), and +3 to +6 dB broadband at the player's ear depending on head position, for about −1 % mean decay [computed].
2. **Steel trem block, vintage dimensions.** No titanium; brass is optional and does nothing. Choose 3 or 5 springs for setup alone [computed].
3. **Hanging bosses (about 19 mm) under the three chamber guard screws, never posts to the back** [computed].
4. **Two-way steel truss rod adjusted at the headstock**, as planned. Ti only for weight. Carbon bars only if wanted for stability: they move the dead spots, they don't remove them [computed].
5. **Fit the guard flat with no rattle and normal torque**, then measure. Don't tune it [judged; model trust low].
6. **Unchanged:** dead spots are set by neck modes that no hidden part moves by more than about ±100 cents. The plan's measure-then-trim step (section 3) remains the only way to place them. Its tool is a headstock slug, which is visible, so it is Jordan's call and outside this brief.

## 7. What Fable should study next (ribs and graduated roof)

- **First, settle the twist mode (288 vs 320 Hz)** with the tap test (sim3d-CHECK item 1) or a measured neck free-free test. Every roof-graduation result depends on which body mode A0 lands near.
- **Roof graduation and ribs.** Work against the first roof mode, 357 Hz with the guard on (362 Hz bare), and A0, 279 Hz in this model (about 286 Hz in the earlier study). Goal: raise the 200–300 Hz coupling without new modes on the high E (580–680 Hz, where the bridge-driven dead notes already sit).
  - Keep the guard in the model as a damping layer: it sets the roof losses 2–6×.
  - Keep the bosses hanging.
  - Check the 4 mm top-strength margin, which is still unresolved.
- **Rib direction across the grain under the 0.6 mm veneer.** Roasted alder E_T 0.47 GPa against E_L 10.9 GPa [literature: wood-properties.json].
- **Before trusting any absolute decay, model pivot friction and measure the guard contact.** Bridge conductance peaks are 7–10× published values, and the 600–680 Hz trem/guard modes drive most of the "dead" high-E notes here.

## 8. Files and how to re-run

All files are in `body/sim/`:
- **Results:** `results/st_*.json` and `.npz` (36 cases), `results/study_room.json`, `results/study_room_eargrid.json` and `results/study_deadspots.json`.
- **Scripts:** `study_summary.py`, `study_deadspots.py` and `study_room.py`.
- **Batches:** `cache/batch_studies.sh` and `cache/batch2.sh`.
- **Options:** MODEL.md section 6.

Peak memory was 4.2–4.6 GB per case and runs went one at a time; the room study ran on its own. Example:

```
cache/venv/bin/python -I -B run_case.py --design final_narrowed --set wood=json --set neck_curly=1 --set tuner_g=37 \
    --set truss_rod=twoway_steel --set trem_block=ti --out results/st_T2_ti.json
cache/venv/bin/python -I -B study_deadspots.py st_N2_S0 st_N4_steel_cf
cache/venv/bin/python -I -B study_room.py --verify
```
