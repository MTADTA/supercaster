# Tap tests and prototype measurements

2026-11-12. Part A is for each blank before CNC. Part B is one page for the finished guitar.

The targets come from `../../acoustic-hybrid.md` §0 and §7. The expected values come from `wood-properties.json`.

Tags:
- **[computed]** arithmetic.
- **[literature]** taken from a source.
- **[judged]** an estimate.

**Kit**
- A phone, or a measurement mic (UMM-6 / EMM-6 class) into any USB interface.
- Audacity, free: record mono WAV at 48 kHz.
- `tap_analyze.py`, in this folder (Python 3, standard library only):
  - `python3 -I tap_analyze.py tap.wav` lists the strongest peaks, each with its loss factor η.
  - `python3 -I tap_analyze.py tap.wav 330` tracks only the peak nearest 330 Hz.
  - It was checked on a synthetic three-mode recording and returned η 0.0081 / 0.0119 / 0.0058 against 0.0080 / 0.0120 / 0.0060 [computed].
- A kitchen scale (0.1 g for strips, 1 g for blanks).
- Digital calipers and a steel rule.
- A foam pad or two rubber bands.
- A light tapper: a wooden dowel, or a pencil eraser for the thin strips.

## Part A. Each blank, before CNC

### A1. Moisture first, because every other number depends on it

- **Stable-weight check.** Weigh the blank every 2–3 days in the shop where the guitar will be built. It is acclimated when the mass changes by less than 0.1% over a week.
- **Moisture content.** Measure it on an offcut of the same board:
  1. Weigh it, giving m.
  2. Dry it at 103 °C until two weighings 2 h apart agree, giving m₀.
  3. MC = (m − m₀)/m₀.
- Don't trust a pin meter on roasted wood [judged].
- Expect about 8% for unroasted wood and 4.5–5.5% for roasted at 40–45% RH [judged from literature equilibrium moisture data].
- Record the room's RH and temperature with every measurement.

### A2. Whole-blank, non-destructive: density and E from the longitudinal ring

1. Weigh the blank and measure L × W × T at 3 places each. ρ = m/(L·W·T).
2. Lay the blank on foam. Tap one end face squarely, along the length, with the dowel. Hold the mic near the opposite end.
3. The strongest high peak is the first longitudinal mode, f_L. Then **E_L = 4·ρ·L²·f_L²** [literature: rod theory; no shear correction needed].
4. Repeat across the width: tap a long edge and record at the opposite edge. This gives **E across the grain in the plane of the top**: E_x = 4·ρ·W²·f_W².
   - That is the stiffness the top skin actually has, whatever the ring angle.
   - It is the number to compare with the 0.67 GPa used in the models.
5. η from each ring-down, using `tap_analyze.py tap.wav <f>`.

Expected values for the roasted alder body blank (21 × 14 × 1-15/16 in) [computed from the central values]:

| Measurement | Expected |
|---|---|
| f_L | ≈ 4.8 kHz |
| f_W, flatsawn | ≈ 1.5 kHz |
| f_W, quartersawn | ≈ 2.1 kHz |

Roasted maple neck blank (30 in): f_L ≈ 3.0 kHz.

The width ring on a 1.94 in thick blank is a plate mode with some Poisson coupling, and a thick 21 × 14 plate has bending modes near 1.5 kHz too. To pick the right peak, tap once on the edge (in-plane) and once on the face. The in-plane mode is strong only in the edge tap and should sit near the predicted 1.5 kHz (flatsawn) or 2.1 kHz (quartersawn). Treat E_x from it as ±10% [judged]. The strips in A3 are the precise check.

### A3. Strips from offcuts: E_L, E_cross, η along and across the grain

**Cut the strips**
- **Along the grain:** 2 strips, about 300–400 mm × 25 mm × 6–10 mm. Keep **L/t ≥ 40.**
- **Across the grain:** 2 strips, about 120–150 mm × 20–25 mm × 4–5 mm. Cut them **in the plane of the top** (the board's face), not through the thickness.
- Plane all strips flat and parallel to ±0.05 mm.

**Free-free bending**
1. Support the strip on two rubber bands or thin foam ridges at **0.224·L from each end**. These are the nodes of mode 1.
2. Tap at the centre. Hold the mic 5–10 mm above one end.
3. Read f₁, the lowest strong peak.
4. Check: f₂/f₁ should be about 2.76. If it isn't, you have picked a torsion or plate mode.
5. Take 3 taps per strip, then turn the strip over and take 3 more.

**E_L = 0.9465 · (m·f₁²/b) · (L³/t³) · T**

- m, L, b and t are in kg and m; the result is in Pa [literature: ASTM E1876 free-free bending].
- T corrects for shear. ASTM's T₁ ≈ 1 + 6.585(t/L)² assumes an isotropic material. Wood along the grain has E/G ≈ 14–18, so use instead:
  **T ≈ 1 + (4.730·t/L)²·(1 + E/(κG))/12**, with κ = 5/6 [computed: Timoshenko first-order correction]. Take E/G_LT ≈ 17 for alder and 16 for maple.
- At L/t = 40, T = 1.026 along the grain; at L/t = 25, T = 1.067.
- For the cross-grain strips E/G_RT ≈ 3, so T ≈ 1.01 at L/t 30 and the correction can be ignored [computed].
- Longitudinal cross-check on the along-grain strips: tap the end and use E = 4ρL²f². Expect about 6.4 kHz for a 400 mm roasted alder strip [computed]. The two E values should agree within about 3%.

**Expected f₁ for roasted alder** [computed]:

| Strip | f₁ |
|---|---|
| 400 × 25 × 10 mm, along the grain | ≈ 330 Hz |
| 150 × 25 × 5 mm, across the grain, flatsawn | ≈ 240 Hz |

Roasted maple across the grain, 150 × 25 × 5 mm: ≈ 260 Hz.

**Damping**
- **η = ln(A₁/A₂)/(π·n)**, from two amplitudes n cycles apart. Equivalently η = 2.2/(f·T60), or η = Δf₋₃dB/f from the peak's half-power width. The script uses the T60 slope.
- Use the median of 6 taps.
- Supports, air and radiation all add loss. A thin cross-grain strip reads high by perhaps 10–30% [judged]. Use the same strip size for every board so the boards rank correctly.

**Density** of each strip: weigh it and measure it. This checks the blank figure from A2.

### A4. Break test: top-skin decision, §0 bench step 1

- **Strips:** 5 mm thick × 25 mm wide, across the grain, from the roasted board. Glue the 0.6 mm veneer with the build glue, veneer grain across the strip's length.
- **Setup:** 3-point bend over a 3.00 in (76.2 mm) span. Use 6 mm dowels as supports and as the loading nose. Load at mid-span by adding water to a hanging bottle until the strip breaks, then weigh the bottle.
- **Three groups of 3 strips:**
  1. **Plain**, show face down (in tension).
  2. **Veneer down**, veneer in tension. This is the mid-panel (field) case: a press in the middle of the roof stretches the underside.
  3. **Veneer up**, show face in tension, veneer in compression. This is the case at the spine and rim walls, where a press bends the clamped skin the other way and the show face carries the tension. `sim3d-CHECK.md` §7 found the stress there is the highest: about 2.4 MPa against about 1.7 MPa in the field at 50 N. **This group governs.** A veneer-down result alone would overstate the margin at the wall.
- **Cross-grain bending stress at failure (plain strip):** σ = 3·P·L/(2·b·t²) [literature: beam theory].
- **Expected plain failure load** [computed]:
  - about 10 N at the 1.9 MPa central roasted tension value
  - about 16 N at the 2.9 MPa unroasted handbook value
  - bending strength across the grain is usually above the tension value, so the real loads may be higher (`sim3d-CHECK.md` §7)
- **Veneered strips:** report the failure load P directly for groups 2 and 3 and compare them with group 1. The model can compare loads; a stress needs the transformed section.
- Record whether the break followed the rings, the rays or the glue line.

### A5. What to log, one row per blank

Board ID, date, RH, temperature, MC, mass, dimensions, ρ, f_L, f_W, E_L, E_x, η_L, η_x, and strip results (f₁, f₂/f₁, E, η, ρ). Add an end-grain photo with a ruler.

**Ranking boards.** If there is a choice, prefer high √(E/ρ³) and low η for the alder [literature: radiation ratio, §5 of the plan]. For the neck, prefer high E_L and low η.

## Part B. Finished-guitar measurement plan (one page)

**General rules**
- Strung at pitch, 10–46, the same strings throughout, floating trem set.
- Same room, same mic spot, RH logged.
- Strapped on, or held the same way each time. A stand distorts the low peaks [literature: Fleischer, via plan §7].
- **What a phone can and can't give.** A phone gives frequencies, Q/η and relative level only. Mobility in s/kg needs force and velocity, so it needs an impact hammer and an accelerometer (B2).

**B1. Air resonance at the f-hole.** Do this twice: dry-clamped before glue-up (§0 bench step 2), then on the finished guitar.
1. Mic 10–20 mm outside the f-hole, strings muted with foam.
2. Tap the top lightly beside the f-hole with a fingertip or a rubber-tipped dowel, 6 taps.
3. Tape the f-hole shut and repeat. The peak that vanishes or drops a lot is the air resonance A0. Peaks that stay are wood modes (T1 is expected at 480–560 Hz).
4. **Dry-clamp target:** 280–292 Hz.
   - Below about 278 Hz, open the throat: +2.4 Hz per 0.1 mm.
   - Above about 295 Hz, add a 0.5 mm strip on one long wall: −6 Hz.
   - (Rules from §0.)
5. Log A0 frequency and η.
6. **Finished guitar:** expect within a few Hz of the dry-clamp reading. Finish and hardware lower it slightly [judged].

**B2. Bridge tap mobility, trem floating** (optional; the model predicts > 5e-3 s/kg at 440–700 Hz)
- **Kit:** a miniature impact hammer and a ≤ 2 g accelerometer into a 2-channel interface. A cheap substitute is two piezo discs, one glued to a small hammer head and one waxed to the saddle.
- **Calibrate the substitute** by tapping a free 100–200 g steel block hung on string. Its mobility is exactly 1/(2π·f·m), which turns the uncalibrated ratio into s/kg [literature: rigid-mass mobility].
- **Measurement:** strings muted. Tap the top of each saddle next to the string slot, normal to the top, 5 taps per saddle. Mobility = velocity/force, with velocity = acceleration/(2πf), over 100–1000 Hz.
- **Flag** any peak above 3e-3 s/kg. Compare the 440–700 Hz band with the model.
- **Optional A/B:** spring-cavity foam in and out. It is not visible.

**B3. Neck dead-spot sweep** (plan §7)
- **Quick method (no hammer):**
  1. Pluck each note at frets 0–15 on the D and G strings, then all strings to fret 12, with the same pick at the same spot (B4).
  2. Record the bridge humbucker DI into Audacity.
  3. Run `tap_analyze.py note.wav <f0>` for the fundamental's T60, then repeat for partials 2–3.
  4. A dead spot is a note whose fundamental T60 is under about half of its neighbours' [judged]. The main risk is D3–B3 (neck mode 2 at 150–250 Hz).
- **With the B2 kit:** tap at each fret beside the D and G strings and record peaks above 3e-3 s/kg. Trim with the ±45 g headstock slug (plan §3), then re-run the D/G sweep.

**B4. Unplugged recording in a room at 1 m**
- **Setup:**
  - Mic at 1.0 m, in front of the guitar, aimed at the body centre between the bridge and the f-hole, at body height.
  - The player seated, in the same chair and the same spot, the room unchanged.
  - Fixed gain. Record a 1 kHz tone from a phone speaker at 0.5 m at the start of each session as a level reference.
- **Repeatable pluck:**
  - Best: the wire-break method. Loop 0.1 mm copper wire under the string 30 mm from the saddle and pull it perpendicular to the top until the wire breaks.
  - Otherwise: the same pick and spot, with a light, consistent stroke, which gives a ±1–2 dB scatter [judged].
- **Notes:** all open strings plus C#4, D4, A4 (high E 5th fret) and open E4. These are the notes §0 predicts change. Then frets 0–12 on the G and B strings. Take 3 takes each.
- **Reference:** the same session, mic and procedure on a solid alder Strat.
- **Report, per note:**
  - level in the 200–300 Hz and 300–500 Hz bands, relative to the reference Strat
  - T60 of the fundamental
- **Expected (plan §0):**
  - +1.3 to +2 dB at 200–300 Hz versus the solid Strat, mostly C#4/D4
  - A4 and open E tamed
  - roughly the same sustain
- Differences under about 1 dB in band level are within take-to-take scatter unless averaged over 3 or more takes [judged].
