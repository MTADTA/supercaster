# Supercaster II body and whole instrument: critique and optimisation (2026-11-13)

Nothing here has been applied. `final_carve.py`, `acoustic-hybrid.md`, `src/`, `site/` and `neck/` are untouched. Section 6 lists the changes to apply after the owner approves.

**Tags.** Every number carries one of: [computed] (from a script in this folder, named nearby), [computed: sim] (the 3-D model in `body/sim`), [literature: source], [judged]. A tag at the end of a sentence or table row covers every number in it.

**How far to trust the model.** The 3-D model is not validated (18 of 28 checks pass). I report differences between cases only. A difference under about 1 dB is inside model error, and I say so each time.

---

## 1. Verdict

**Change four things before anything is cut.**

1. **The f-hole liner must not be a solid ring glued to the roof.** Every earlier gain figure treated the liner as added weight with no stiffness. Glued on as drawn, it is a deep rib round the most mobile part of the roof. The model takes back 2.7 dB at 200 to 300 Hz, 1.5 dB at 300 to 500 Hz and 2.4 dB at 500 to 1000 Hz [computed: sim]. That is about 40 % of the 6.8 dB the chamber was credited with at 200 to 300 Hz. Keep the liner for its tuning job, but cut it like a kerfed lining so it adds no stiffness.
2. **Roof: 6.0 mm bare alder, no veneer, no cleats, with a 6 mm wood lip left round each end of the f-hole.** The cross-grain veneer loads the alder to 1.3 to 2.2 MPa every dry season before any knock, against a strength of 1.9 MPa [computed]. The 6 mm bare roof costs under 0.5 dB [computed: sim, inside model error]. The lips cut the stress at the hole ends from 1.90 to 0.89 MPa [computed].
3. **Do not machine the liner integrally as a chimney.** It is the strongest roof (0.88 MPa) and the quietest (item 1). The traced hole is also only 0.29 in wide in its thin arms, which leaves a 1.9 mm slot 19 mm deep [computed]. That cannot be machined reliably in either the integral or the separate version, so the throat shape needs redrawing either way.
4. **Tune the air resonance to D4, about 294 Hz, not 279 Hz.** 279 Hz sits 10 cents from C#4 (277.2 Hz), which is a harmonic of two open strings in both of the owner's tunings. At 294 Hz the resonance responds 11.6 dB less to those open strings [computed]. It costs nothing and uses the dry-clamp trim that already exists.

**Keep.** The chamber and narrowed-throat idea, the narrow frame fillet round the roof, hanging guard bosses, the 0.85 in forearm, the "blended" belly cut with its 0.04 in reserve, the current heel loft, steel trem block with three springs, hidden trim under the tuners.

**Already at the physical ceiling.**

- **Loudness.** The chamber is 0.84 litre under a 46 in² roof. About +3 dB broadband over a solid body is what this size gives [computed: sim, earlier study]. No hidden feature adds another 3 dB.
- **Balance.** The new neck changes the hang angle by 0.3° [computed]. Nothing to do.
- **Heel stiffness.** Every heel shape studied changes total neck-to-body compliance by 1.25 % or less [computed]. Choose the heel by hand and eye.
- **Tremolo.** With real masses the rocking mode is about 45 Hz, 7.5 semitones under C#2 [computed]. The 62 to 66 Hz worry came from a light bridge in the model.
- **Edge.** The forearm and tail rolls are limited by the 0.80 in edge thickness there, not by choice.

**Honest expected result.**

| Where | What the owner gets | Tag |
|---|---|---|
| In hand | Belly and forearm vibration at or just over the threshold of feeling (about 0.5 µm per newton at 250 Hz); neck-back vibration at the palm's threshold. A firmly seated guard is the main lever for feel: +6 to +9 dB at the neck back and forearm at 300 to 500 Hz. Balance as the stock guitar or better: hangs at 53°. | [computed: sim], guard contact values guessed |
| In a room | About 3 dB louder than a solid Strat overall, about 7 dB in the 200 to 300 Hz band, most of it one resonance near D4. The player hears more of the gain than a listener across the room. It is a satisfying unplugged guitar, not an acoustic guitar. | [computed: sim, earlier study] |
| Plugged in | A three-pickup S-style guitar. A handful of notes decay faster (the model flags 14 to 20 of 132; do not trust which). More willing, more musical feedback near 280 to 300 Hz, up to 10 dB more sensitive there than a solid body. | [computed: sim] |

---

## 2. Ranked risks and changes

Ranked by consequence first, then by whether the choice can be undone after CNC and glue-up.

| # | Item | What is wrong or open | Consequence | Undo after CNC? | Recommendation | Confidence |
|---|---|---|---|---|---|---|
| 1 | Liner glued on as a solid ring | Adds a rib the gain figures never included | −1.5 to −3 dB, 200 to 1000 Hz [computed: sim] | No, the box is closed | Kerfed, non-structural liner | Direction high, size low |
| 2 | Roof layup | Veneer creates seasonal stress; cleats are a second cross-grain part | Top crack at an f-hole end | No | 6.0 mm bare + end lips | Medium-high |
| 3 | Liner throat shape | 1.9 mm slot in the hole's thin arms | Cannot be cut; lossy | Yes, before cutting | Close the arms, open the middle | High |
| 4 | Air resonance on C#4 | Coincides with open-string harmonics | Open-string howl at stage volume | Only before glue-up | Trim to 294 ± 4 Hz | Medium |
| 5 | Trem top slot 0.178 in² uncovered | v3.2 blocker, needs the real plate and block | Visible slot or re-route | No | Decide trem unit, measure it | High |
| 6 | Neck pocket width | Pocket 2.1875 in; new neck is 2.170 in at the datum and 2.262 in at the pocket end [computed] | Joint does not fit | No | Refit when neck v4 is final | High |
| 7 | Guard seat | Flat zone or developable crown; contact is the model's weakest guess | Feel, ±2 dB at 300 to 1000 Hz, edge lifting | Top surface: no | Full seat, guard formed slightly flat; prototype test decides | Low |
| 8 | Forearm glue seam | Seam runs onto the edge roll for 5.03 in | Cosmetic, under white | No | Accept and seal | High |
| 9 | Heel relief | Access against a vintage read | Comfort at frets 18 to 22 | Yes, more can be carved later | CNC the current loft; carve relief in the white | High |
| 10 | Trem rocking mode | Was thought close under C#2 | Weak low note if it landed on one | Yes (block, slug, springs) | Steel block, 3 springs, flick test | Medium-high |
| 11 | Dead spots | Neck modes move with the deeper neck | A few short notes | Partly (trim mass) | Build in trim points; voice after assembly | Low on notes |
| 12 | Edge and belly choices | Two open v3.4 items | Comfort | Only toward larger rolls | See 3.6 | Medium |
| 13 | Balance | None | None | n/a | No change | High |

---

## 3. Critique: what is wrong, overstated, unresolved or needlessly complicated

**Wrong or overstated**

- **The chamber gain.** "+6.8 dB at 200 to 300 Hz" assumes the liner adds no stiffness (item 1). With the liner as a glued ring the figure is nearer +4 dB [computed: sim]. A second model agrees in direction: a thin-plate model of the real roof plan gives 6.6 dB less volume compliance with the ring glued on [computed, `calc_roof.py`].
- **The liner makes the guitar louder.** It does not. It moves the air resonance from 373 Hz to 279 Hz: +2.9 dB at 200 to 300 Hz, −4.1 dB at 300 to 500 Hz [computed: sim, existing results `final_bare` and `final_narrowed`]. It is a voicing choice. Glued on stiff, the planned build is level with a bare hole at 200 to 300 Hz and 3 to 5.6 dB quieter above [computed: sim].
- **Trem rocking mode at 62 to 66 Hz.** The model's bridge weighs 0.36 kg with a 202 g block and has no string preload term. A real vintage unit is about 470 g with a 280 g block [judged, BALANCE.md]. My hand model reproduces the model's figure with the model's own geometry (63.8 Hz against 66.3) and gives 44.7 Hz with real masses [computed, `calc_trem.py`].
- **Where the roof is weakest.** Earlier strip calculations gave 1.28 MPa (5 mm) and 0.89 MPa (6 mm) for a 50 N knock. On the real plan with the hole, the peak is at the f-hole ends: 2.72 and 1.90 MPa [computed]. The wall junction comes second at 1.82 and 1.33 MPa.
- **The pickguard as "main absorber".** This rests on three guessed numbers. The nominal contact stiffness happens to be the worst case: both ten times stiffer and ten times softer give more output [computed: sim]. Treat the 6 dB "no guard" figure as an upper bound until the prototype test.

**Unresolved**

- Trem top slot (item 5) and pocket width (item 6) both block CNC.
- `acoustic-hybrid.md` section 0 still says a 1/8 in edge and a two-way rod adjusted at the headstock. Both are superseded.
- The model's trem (mass, preload), its doubled neck beam mass and its 0.6 in rigid neck joint are still open from the 2026-11-12 check. None changes a recommendation here.

**Needlessly complicated**

- Veneer plus cleats: two cross-grain parts to fix a problem that thickness and an integral lip fix with none.
- Graduating the roof broadly. A wide taper (+2 mm over 20 mm) lowers wall stress 7 % and costs 2.2 dB of roof compliance [computed]. The existing narrow fillet (+1.5 mm over 6 mm) lowers wall stress 25 % for 1.3 dB. Keep the narrow fillet; drop the idea of a graduated roof.
- A relief gap under the guard, five springs for tone, a titanium block. None earns its place (sections 3.3 and 3.4).

---

## 4. One integrated design, item by item

### 4.1 Roof layup

**Mechanism.** A one-species roof with the grain all one way shrinks and swells freely. Glue a cross-grain layer under it and the alder is held: stress = movement × cross modulus × the layer's share of stiffness.

| Roof (flatsawn alder, 50 N on 1 in²) | Knock stress, worst | Where | Seasonal stress | Roof compliance |
|---|---|---|---|---|
| 5.0 mm + 0.6 mm veneer, liner as weight only (the plan as modelled) | 1.39 MPa | f-hole end | 1.38 MPa (2.19 quartersawn) | 6.3 |
| 5.0 mm + veneer, liner glued stiff (the plan as built) | 0.58 MPa | wall | 1.38 MPa | 2.9 |
| 6.0 mm bare, no rim | 1.90 MPa | f-hole end | none (see below) | 13.0 |
| **6.0 mm bare, 6 mm lips at the two ends** | **1.17 MPa** | wall | none | **8.9** |
| 6.0 mm bare, 6 mm lip all round | 1.03 MPa | wall | none | 7.8 |
| 6.0 mm bare, full chimney | 0.88 MPa | near hole | none | 5.8 |

Compliance is the roof's volume displacement per unit pressure, ×10⁻¹¹ m³/Pa. All rows [computed, `calc_roof.py`, figure `fig_roof_stress.png`]. Strength across the grain is 1.9 MPa, range 0.9 to 3.0 [literature: `wood-properties.md`].

- **Veneer.** Knock plus season is 0.58 + 1.38 = 1.96 MPa with no creep relief, about 1.3 MPa if creep halves the seasonal part [computed; creep factor judged]. That is at or near the typical strength.
- **6.0 mm bare with end lips.** Knock 1.17 MPa: safety factor 1.6 on a typical board, 0.8 on the weakest. A bare roof still sees a short-lived stress when the thin roof dries faster than the thick frame: about 0.46 MPa [judged factors]. One thin coat of shellac inside the chamber before closing slows that.
- **Acoustic cost.** 6 mm bare against the plan: −0.03 / −0.27 / +0.31 / −0.52 dB in the four bands [computed: sim, inside model error]. 5.5 against 6.0 mm: +0.06 to +0.27 dB [computed: sim, inside model error]. Thickness is nearly free; rims are not.
- **Tissue doublers.** Silk or 50 g/m² glass tissue restrains the roof to only 0.27 to 0.48 MPa [computed]. With the lips present they are optional. If used, one 10 × 25 mm patch just beyond each lip.
- **Graduation.** Not worth it (section 3).

**Recommendation.** 6.0 mm bare, frame fillet kept, 6 mm lips at both ends, no veneer, no cleats.
**Benefit.** Removes a seasonal stress of 1.3 to 2.2 MPa; removes two glued parts. **Confidence** medium-high. **Buildability** easier than the plan.
**Smallest test.** Mill one coupon from the body blank's offcut: a 6 mm roof strip across the grain with one f-hole end and its lip. Press with a thumb on a kitchen scale to 10 kg; it must not crack. Then break it, and reject the board if it fails under 1.5 MPa by the existing A4 procedure. If the coupon cracks under 10 kg, go to 6.5 mm (stress −15 %, cost 0.1 to 0.3 dB [computed; computed: sim]).

### 4.2 Liner and f-hole

**Mechanism.** The liner is a port: it lowers the air resonance by narrowing and lengthening the opening. Its wall, 4.7 mm × 19 mm of alder running along the grain, is also a beam five times stiffer than the strip of roof it is glued to [computed, `calc_misc.py`]. The roof's largest motion is at the hole edge, so the beam costs output.

| Liner wall | Stiffness against a 30 mm roof strip | Tag |
|---|---|---|
| Alder ring as drawn, glued on | 5.0 × | [computed] |
| Alder ring, 2 mm wall | 2.1 × | [computed] |
| Integral lip 6 mm deep | 0.16 × | [computed] |
| **Kerfed alder ring (only the 2 mm seat strip continuous)** | **0.01 ×** | [computed] |
| 2.5 mm leather or 2 mm printed sleeve | 0.01 to 0.02 × | [computed; moduli judged] |

**Recommendation.** Keep the liner as a separate alder part with the same seat. Cut saw kerfs through its long walls, 0.5 to 0.8 mm wide at 12 mm pitch or closer, from the free end up to 2 mm from the seat. Seal them with one wrap of silk or tissue and shellac round the outside. Luthiers know this as a kerfed lining.

**Answers to the questions asked.**

- **Integral chimney instead of cleats?** As a full-depth chimney, no (verdict item 3). As two 6 mm lips at the hole ends, yes: they replace the cleats. They need nothing from the glue plane (their underside is at z −0.47, the plane at −0.90). Width 4.7 mm, a 3 mm fillet into the roof, each lip tapered to nothing over 10 mm. They are short-grain, so keep the width; the stress they see is 0.89 MPa [computed]. A 6 mm cutter reaches everywhere: the liner footprint is at least 0.50 in from the chamber wall.
- **Is the dry-clamp adjustment kept?** Yes, in one direction as before. Opening the throat or shortening the liner raises the resonance: 83 Hz per in² of throat, 2.9 Hz per mm of depth, 1.4 Hz per 1 % of chamber volume [computed]. Machine the throat tight (inset 2.8 mm, about 275 Hz) and trim up to 294 Hz. Expect a final inset near 2.5 mm [computed estimate].
- **Throat shape.** The hole's thin arms are 0.29 to 0.34 in wide [computed from the trace]. A uniform 2.7 mm inset leaves a 1.9 mm slot there and the throat splits into pieces at 3.0 mm. Close the liner fully under the arms (it is a black ledge 6 mm down, as now) and take the area from the wide middle and the eyes, with nothing narrower than 4 mm so a 1/8 in cutter does it. Area sets the tuning, not shape. The arms hold roughly 0.15 in² [judged]; recompute in CAD.
- **Is the f-hole near an acoustic optimum?** Its shape and place are set by the look, and that is fine. At 280 Hz the wavelength is 1.2 m, so where the hole sits does not matter to the air resonance. The acoustic variables are throat area and depth, which the liner already separates from the look. The one acoustic point about the hole is structural: its ends are the roof's weak spots, hence the lips.

**Benefit.** Recovers 1.5 to 3 dB from 200 to 1000 Hz against the plan as it would have been built [computed: sim; the model's ring is about twice too wide, so the low end of the range is more likely]. **Confidence** high on direction, low on size. **Buildability** one hour of fret-saw work.
**Smallest test.** Glue the kerfed liner and a solid one to two matching 6 mm strips; tap each (`tap_analyze.py`). The kerfed strip's first frequency should be within 10 % of a bare strip's; the solid one will be far higher.
**Fallback if the owner wants the simplest build.** No liner at all: air resonance near 373 Hz (F#4), louder at 300 to 500 Hz, thinner at 200 to 300 Hz [computed: sim].

### 4.3 Pickguard

**Mechanism.** A plate bent over a cylinder by forces near its edges touches along lines: the edge and the screws. Between them the contact pressure is zero unless the seat's curvature changes. So a bent guard gives a repeatable, rattle-free fit. It does not by itself stop the guard absorbing; that depends on whether the guard is held to the top or left to resonate. A 2.3 mm 3-ply panel between screws has its own resonances from about 230 to 610 Hz [computed], right in the band where the model says it absorbs.

| Guard state (all on the 6 mm roof with a stiff liner) | 80–200 | 200–300 | 300–500 | 500–1000 Hz | Tag |
|---|---|---|---|---|---|
| Contact ×10 (firmly seated) | 0.0 | 0.0 | +2.1 | +1.8 dB | [computed: sim] |
| Contact ×0.1 (barely touching) | +2.4 | +1.0 | +1.1 | +1.4 dB | [computed: sim] |

Firm seating also raises felt vibration at 300 to 500 Hz by 8.8 dB at the neck back and 6.2 dB at the forearm, and the count of short notes falls from 20 to 14 [computed: sim]. All of this rests on guessed contact values.

**What to specify.**

- **Yes, a cold-bent 3-ply guard does the job. No bonded aluminium.**
- **Form the guard slightly flatter than the seat** (10 to 20 % less curvature). The screws then press the edge down all round: no gaps, a defined edge line. Formed more curved than the seat, the edges lift.
- **Warm-form rather than force.** Bending a flat guard to a 9 in radius needs 1.2 to 1.8 N per mm of edge, about 90 to 136 N per screw [computed]. That is too much for plastic. Warm-formed to within 20 %, the screws carry under a quarter of that.
- **Bending strain** is 0.50 % at a 9 in radius and 0.70 % at 6.5 in [computed]. Keep the seat radius at 9 in or more.
- **The seat must be developable** (curved one way only). Between screws 75 mm apart the guard edge buckles at 0.077 % compression [computed]. A seat with a 6.5 in radius one way must be flatter than a 205 in radius the other way [computed]. This is the real cost of removing the flat zone: the crown under the guard has to be a ruled surface, not a dome.
- **Keep the flat zone under the pickups, bridge plate and trem.** Curve only toward the lower bout and the control side.
- **Full seat, no relief pocket.** A 0.3 mm air gap damps about 300 times more than a 2 mm one [computed], so a shallow relief is the worst choice.
- **Screws:** the standard eleven. **Bosses:** hanging, as drawn. Posts to the back cost 3.9 dB at 200 to 300 Hz [computed: sim, earlier study].

**Benefit.** 0 to +2 dB at 300 to 1000 Hz and clearly more feel [computed: sim, inside or near model error]. **Confidence** low until measured. **Smallest test:** validation test 6.

### 4.4 Tremolo

**Mechanism.** The bridge rocks on its pivot against the strings' stretch stiffness (about 80 % of the total) and the springs. A note whose fundamental lands on that mode loses its fundamental fast.

| Vintage six-screw, 280 g steel block, 10.5–48 | Rocking mode | Below the lowest note |
|---|---|---|
| Eb standard, 3 springs | 44.7 Hz | 9.6 semitones under Eb2 |
| Drop C#, 3 springs | 44.8 Hz | 7.5 semitones under C#2 |
| 2 / 4 / 5 springs | 43.0 / 46.2 / 47.7 Hz | |
| All inputs across their ranges | 38 to 52 Hz (5 to 95 %) | |
| Light 202 g block / titanium 160 g | 50.7 / 55.2 Hz | |
| + 30 g / 60 g slug low on the block | 42.0 / 39.7 Hz | |

All [computed, `calc_trem.py`, figure `fig_trem.png`]; geometry [judged] until measured.

- **Tuning hardly matters.** The strings' stiffness depends on gauge, not pitch. Eb standard and drop C# differ by 0.1 Hz [computed].
- **Where it should sit.** Below the lowest note, since every semitone above is played. One semitone clear already cuts the coupling 4 to 50 times; three semitones is ample [computed]. Target: under 58 Hz for drop C#.
- **What a coincidence would cost.** The low string's fundamental would decay in 2.5 to 10 s instead of far longer, for mode Q of 60 to 15 [computed]. Unwelcome, not ruinous.
- **Springs.** Three. Five raise the mode 3 Hz and change output by under 0.05 dB [computed: sim]. They add 17 % to the bridge's stiffness, so string bends pull the other strings 14 % less flat [computed]. That is a feel choice for the owner.
- **Block.** Full-size steel. A light or titanium block moves the mode toward the notes for no gain.
- **Vega-Trem VT1.** Published: about 454 g complete six-screw unit, 306 g for the core unit, thin galvanised steel block, a ground blade edge in a fixed frame, 53.5 mm string spread [literature: retailer listings and a Strat-Talk owner's weighing]. Not published: pivot height, block size, moving mass. Depending on those it lands anywhere from 30 to 74 Hz [computed, table in `trem_output.txt`]. A light moving part with saddles 0.45 to 0.50 in above the blade would put it on the low notes.
- **What must be measured on a VT1:** saddle crown height above the blade edge; saddle distance behind it; mass of the moving part and of the block; depth of the spring hooks below the blade. Or fit it to any Strat and do the flick test.

**Benefit.** Removes a worry rather than adding output. **Confidence** medium-high for the vintage unit, low for the VT1. **Smallest test:** validation test 1.
**Built in.** Two M4 tapped holes low on the block's rear face for a slug, inside the spring cavity. Reversible and invisible.

### 4.5 Glue seam on the forearm

**Recommendation: accept it and seal it under the white finish.**

- **Making the forearm shallower** needs an arm depth of 0.58 in to clear a 5/16 roll, or 0.64 in for a 1/4 roll [computed]. That gives away a quarter to a third of the forearm contour to hide a line that is under opaque paint.
- **Moving the glue plane** needs it 1.17 in down [computed]. The back half becomes 0.58 in thick, the belly bevel and back roll then cross the plane instead, and the liner, mortise and chamber floor all move. It trades one seam for another.
- **Why accepting is safe.** The seam already runs round the whole side wall at mid-height, so the body depends on it being invisible under white everywhere. On the forearm it meets the surface at about 53° at its shallowest [computed, circular-arc estimate], so there is no feather edge and the glue line reads at most 1.25 times its true width.
- **Rules.** Glue the halves before the outside is finish-contoured, so no thin edge is ever handled. Seal the seam line with thin epoxy or two extra sealer coats before colour.
- **Knock-on gain.** With the seam accepted, the rule that held the front roll at 5/16 through the forearm can go. The thinnest spot is 0.799 in thick. Front 0.42 + back 0.22 + a 0.157 wall fits [computed]. That takes the roll's smallest radius under the forearm from 0.26 to 0.35 in, where the arm bears hardest, and lets more of the tail reach its 1/2 target.

**Confidence** high. **Test:** none needed; a painted offcut with a glue line if the luthier wants proof.

### 4.6 Edge and contours

- **Treble horn back.** Run it at the plan cap (0.41 to 0.46 at the tip, 1/2 elsewhere) instead of dipping to 3/8. The fretting hand's palm bears on that edge at the top frets, and a constant roll looks less fussy. Back only, so nothing shows from the front.
- **Belly-back reserve.** Keep the 0.04 in. Going from 0.405 to 0.445 cannot be felt. A glue seam breaking out through the back roll after sanding cannot be undone.
- **Is the graduated edge right where the body bears?** Thigh (0.50), ribs (0.49), cutaways (0.50): yes. Forearm front (0.31): the smallest roll is where the pressure is highest. Fix as in 4.5.
- **Belly cut.** Total relief at the belly rim (bevel plus roll) is capped at 0.75 in by the glue plane, whichever way it is split [computed]. A wide shallow bevel spreads rib pressure better than a tight roll, so "blended" (0.345 deep, 3.3 wide, roll 0.405) is the right split.
- **Belly and the chamber.** "Whisper" adds 2.9 % chamber volume, "full" removes 2.4 % [computed, `calc_balance.py`]. Either moves the air resonance about 4 Hz, which the throat trim absorbs. The back's stiffness matters little because the player's body damps it. So the belly choice is free acoustically.

### 4.7 Heel

Study in `calc_heel.py`, figure `fig_heel.png`. Re-run with `--d1 --d12 --dheel --wextra` when neck v4 is final.

| Shape | Thickness at frets 17 / 19 / 21, centre | Under treble board edge, frets 18 / 19 / 21 | Total compliance | Wood under pocket floor |
|---|---|---|---|---|
| H0 current loft | 1.89 / 2.12 / 2.12 in | 1.31 / 1.98 / 2.12 in | 0 | 1.125 in |
| H1 loft starts at fret 15 (most vintage) | 1.72 / 2.12 / 2.12 | 1.08 / 1.91 / 2.12 | +1.1 % | 1.125 |
| H2 loft starts 1 in earlier | 1.98 / 2.12 / 2.12 | 1.50 / 2.03 / 2.12 | −1.1 % | 1.125 |
| H3 current + treble relief 0.25 | 1.84 / 2.06 / 2.10 | 1.20 / 1.76 / 1.89 | +0.1 % | 0.875 |
| H4 current + treble relief 0.40 | 1.80 / 2.02 / 2.08 | 1.13 / 1.62 / 1.75 | +0.2 % | 0.725 |
| H5 current + full-width relief 0.30 | 1.65 / 1.85 / 2.03 | 1.17 / 1.71 / 1.84 | +0.7 % | 0.825 |
| H7 current + full-width relief 0.45 | 1.53 / 1.70 / 1.92 | 1.10 / 1.58 / 1.69 | +1.25 % | 0.675 |

All [computed]. "Relief" is wood carved from the body back behind the joint. Thickness is from the board top to the back.

- **Stiffness does not decide this.** The joint zone is 19 % of the neck-to-body compliance. The largest change, 1.25 %, moves neck modes about 0.6 %, or 10 cents [computed]. The hidden trim covers more than that.
- **What limits access** is the full 2.12 in block from fret 18 on. Only body-back relief reduces it. Starting the loft later (H1) helps the palm at fret 18 and nowhere else.
- **Recommendation.** CNC the current loft (H0). Relief only removes wood, so the luthier can carve it in the white after the owner has played the guitar, up to 0.30 in full width (H5): 0.27 in thinner under the thumb at frets 18 and 19, with 0.825 in left under the pocket floor.
- **Read.** From the front nothing changes. From the back H0 is the round vintage read; H5 looks like a softly contoured heel.

### 4.8 Balance and feel

Redone in `calc_balance.py` with the 0.90 to 0.97 in neck, 1-11/16 nut, 0.140 in board, single-acting rod with spoke wheel, reverse headstock and 27 g tuners.

| | Mass | Hangs at | Margin at 20° / 30° | Seated, forearm force |
|---|---|---|---|---|
| Old neck (BALANCE.md) | 2.906 kg | 53.3° | +3.15 / +2.27 N·m | 2.2 N |
| **New neck** | **2.886 kg** | **53.0°** | **+3.15 / +2.26 N·m** | **2.0 N** |
| Heavy maple 0.70 + light alder 0.36 (worst) | 2.798 kg | 51.7° | +2.86 / +2.02 N·m | 2.9 N |
| + 45 g trim under the tuners | 2.931 kg | 51.3° | +2.93 / +2.05 N·m | 3.3 N |

All [computed].

- The deeper neck adds 3.8 in³ of maple; the thinner board and lighter rod take it back. Net −20 g, 21 g less on the neck [computed].
- The reverse headstock moves the centre of mass 0.13 in toward the treble side [computed]. It will not be felt.
- It would take 517 g at the headstock to make it dive at a 30° playing angle [computed]. The 45 g trim is safe.
- **Feel.** Belly and forearm move about 0.5 µm per newton at 250 Hz, near the forearm's threshold of 0.5 to 2 µm. The neck back moves about 0.3 µm per newton at 400 Hz, at the palm's threshold of 0.1 to 0.3 µm [computed: sim; thresholds literature: earlier study]. The guard's seating is the one lever that moves these by more than 3 dB (4.3).

### 4.9 Feedback at stage volume

More sensitivity near the air resonance is the same physics as the acoustic gain; it cannot be removed without removing the gain. What can be done without a feature:

- **Move the resonance off the open strings** (verdict item 4). Open-string partials near it are 277.2 Hz and 311.1 Hz. At 294 Hz the response to both is 11.6 dB down; at 279 Hz it is 0.6 dB down [computed]. The resonance is 8.6 Hz wide and drifts 0.5 Hz per °C [computed], so ±4 Hz is the tolerance.
- **Pot the pickups fully** and bed the bridge humbucker's baseplate. This is the usual cause of howl, as distinct from musical feedback.
- **Seat the guard firmly** so it cannot buzz at volume.
- **Not a design item:** a strip of black foam pushed into the f-hole for very loud stages. It is removable and all but invisible.

**Confidence** medium. **Test:** validation test 2 gives the prototype's resonance and width.

### 4.10 Dead spots and sustain

No note-level claim is made.

- With the deeper neck, the neck-dominated modes should rise 2 to 9 % [judged scaling, `calc_misc.py`]. The two the model placed at 177 and 282 Hz would land somewhere in 181 to 193 Hz and 287 to 307 Hz. The second range includes the 294 Hz air target, so the two may meet. Only the finished guitar will say.
- **Build in:**
  - 45 g of hidden trim capacity under the tuners (lowers neck modes about 0.4 % per 10 g [computed: sim, earlier study]).
  - The two slug holes on the trem block (4.4).
  - One M5 threaded insert in the tail wall of the spring cavity for a body-side trim mass.
  - The liner trim, which moves the air resonance independently of the neck.
- **Voicing order after assembly.** Find the neck modes by tapping the headstock; find the air resonance; if they sit within 10 Hz, move the neck mode down with tuner trim, since the air resonance is fixed after glue-up.

### 4.11 Other hidden things CNC makes possible

- **Two locating dowels in the solid spine** so the halves register identically at every dry clamp and at glue-up.
- **Wiring channels milled in the glue face** instead of long drilled holes.
- **No open path between the chamber and the control or pickup routes.** A leak lowers the resonance's Q and shifts it. Seal the wire pass.
- **One thin shellac coat inside the chamber** before closing (4.1).
- **The roof coupon** cut from the same blank with the same program (4.1).
- **Rejected as feature creep or no gain:** thinner back skin (saves about 10 g, no acoustic value), posts under the guard, mass island, any second port.

---

## 5. Validation plan on the existing prototype: one hour, a phone

Record with the phone's voice recorder at the highest quality, 30 cm from the guitar unless stated. Say the test name aloud before each take. Convert with `afconvert -f WAVE -d LEI16 in.m4a out.wav`, then `body/acoustics/inputs/tap_analyze.py out.wav`.

**Strings on (30 min)**

| # | Min | Do | Settles |
|---|---|---|---|
| 1 | 5 | **Trem flick.** Damp the strings with a cloth. Flick the bar and let go, five times. Film the bridge in slow motion (240 fps) and also record sound. Count cycles per second. Note the spring count. | Rocking-mode frequency and its ring time. Checks my 45 Hz against the model's 66 Hz; fixes the trem's inertia and stiffness inputs. Decides whether anything is needed at all. |
| 2 | 5 | **Air resonance.** Phone 5 cm over the f-hole. Tap the roof beside the hole with a fingertip, ten times. Tape over the hole and repeat. The peak that disappears is the air resonance. | Its frequency and width on a real thinline. Calibrates the model's air damping and the tuning sensitivities used for the 294 Hz target and the feedback width. |
| 3 | 8 | **Roof taps.** Strings damped. Tap five times each at: roof centre; 1 cm from the chamber wall; beside each f-hole end; between hole and edge; on the solid spine by the bridge. | First roof mode and its damping. With the caliper thickness, this pins the alder's cross-grain stiffness, the model's weakest wood input. |
| 4 | 7 | **Notes.** Pluck every fret from open to 12 on the D and G strings, 4 s each, twice. Then tap the back of the neck at fret 5 and the headstock tip, five times each. | Which notes die early and where the neck modes are. Tests whether the model's dead-spot machinery is believable on a similar guitar. |
| 5 | 3 | **Hang and balance.** Hang the guitar from the horn button alone; lay the phone on the neck with a level app and read the angle. Weigh the guitar. Find the balance point on a finger. | Checks the balance model against a real guitar of this type. |
| 6a | 2 | **Guard, tight against loose.** Tap the bridge plate and the guard centre five times each. Back every guard screw off one turn and repeat. | First reading of guard contact. |

**Strings off (30 min)**

| # | Min | Do | Settles |
|---|---|---|---|
| 6b | 15 | **Guard on against off.** With strings off and screws tight, tap the bridge plate and roof centre five times each. Lift the guard assembly off and lay it aside on its wire; repeat. | The guard's real absorption at 300 to 1000 Hz. Under 1.5 dB difference: the guard is not the main absorber, and 4.3 reduces to "seat it well". Over 3 dB: the firm full seat matters and is worth care. |
| 7 | 15 | **Calipers.** See the list below. | Geometry the hand models rest on. |

**Calipers must capture**

- Roof thickness at the f-hole edge in three places; depth from the top to the chamber floor through the hole; f-hole length and widths at the eyes, the middle and the thin arms.
- Guard thickness. A straightedge across the bent guard in two directions, with the gap at each end: this gives the radius the owner already likes and shows whether it curves one way or two.
- Trem: string height above the body at the saddles; saddle crown distance behind the pivot screws; block length, width, depth; spring count.
- Edge radius at the forearm crossing, the belly side and the treble waist.
- Neck depth at frets 1 and 12 and width at the nut, fret 12 and the heel.

**The LiDAR scan must capture**

- The whole top with the guard off: the carve under the guard and how far the flat zone runs.
- Forearm contour: depth and extent. Back: full surface, since there is no belly cut to compare.
- Heel and both cutaways from the back, at an angle that sees into the treble cutaway.
- F-hole position against the outline and the bridge.
- Both strap buttons.
- Put a ruler and a few masking-tape crosses in view for scale. Phone LiDAR is good to a few millimetres overall, so use it for shapes and the calipers for thicknesses.

---

## 6. Changes to apply after approval

### 6.1 `final_carve.py` PARAMS (proposed, not applied)

| Parameter | Now | Proposed | Note |
|---|---|---|---|
| `top_skin` | 0.197 | 0.236 | 6.0 mm bare |
| `liner['veneer']` | 0.6/25.4 | 0 | no veneer; remove cleats from the build list |
| frame fillet (0.06 over 0.25) | as is | as is | efficient; keep |
| new `fhole_lips` | none | depth 0.236, width as liner wall (2.0 mm out, to the throat edge in), reach 0.9 in from each tip, taper 0.4, root radius 0.125 | integral with the roof |
| `liner['inset']` | 2.7/25.4 | 2.8/25.4 as cut, trimmed toward 2.5 | target 294 ± 4 Hz at dry clamp |
| new `liner['min_throat']` | none | 0.16 | close the throat where narrower; arms closed |
| new `liner['kerf']` | none | width 0.025, pitch ≤ 0.47, stop 0.08 from the seat | long walls only |
| `edge_ergo['arm']` | 0.3125 | 0.42, with the back at the forearm crossing eased to ≥ 0.22 | needs the seam accepted; drop the 5/16 hold in the glue-seam rule |
| `edge_ergo['back']` on the treble horn | 0.375 from x 18.5 | `back_ergo` capped by plan (0.41 to 0.46 at the tip) | no dip |
| `edge_ergo['glue_clear']` | 0.10 | 0.10 | keep the reserve |
| `belly_mode` | 'blended' | 'blended' | no change |
| `arm_depth` | 0.85 | 0.85 | no change |
| `pocket_w`, `tongue_w` | 2.1875, 1.90 | from neck v4 (heel width + 0.002 to 0.004 fit) | blocked on neck v4 |
| heel loft | current | current | relief up to 0.30 by hand in the white |
| `guard_bosses` | hanging | hanging | never posts |
| guard flat zone | whole guard | flat under pickups, bridge and trem; elsewhere a ruled surface, radius ≥ 9 in | blocked on the prototype scan |
| trem routes | v3.2 | from the measured unit | blocked on the trem decision |
| new: block slug holes, spring-cavity M5 insert, two spine dowels, sealed wire pass | none | add | hidden |

### 6.2 `acoustic-hybrid.md` section 0 (proposed, not applied)

1. Roof: replace "5 mm + 0.6 mm cross-grain maple veneer, cleats at the f-hole tips" with "6.0 mm bare alder, 1.5 mm frame fillet, integral 6 mm lips round both f-hole ends; no veneer, no cleats; silk patch beyond each lip optional".
2. Liner: replace the glued solid liner with "separate alder liner, kerfed so it adds no stiffness, sealed with a silk wrap; throat closed under the hole's thin arms; nothing narrower than 4 mm".
3. Air resonance target: "294 ± 4 Hz (D4), trimmed upward at dry clamp", with the reason.
4. Edge: replace "1/8 in" with the v3.4 values and the forearm change in 6.1.
5. Rod: replace "two-way, adjusted at the headstock" with "single-acting, spoke wheel at the body end".
6. Trem: add "full-size steel block, three springs; accept when the flick test shows the rocking mode at least three semitones under the lowest open note; two M4 slug holes on the block".
7. Guard: add "3-ply, warm-formed slightly flatter than the seat, full contact, eleven screws, hanging bosses".
8. Bench steps: add the roof coupon; the kerfed-against-solid liner strip check; one shellac coat inside the chamber; sealed wire pass; glue the halves before finish-contouring; seal the forearm seam line before colour.
9. Voicing: add the order in 4.10.
10. Gains: restate the 200 to 300 Hz gain as conditional on the non-structural liner.
11. "Waiting on Jordan": replace with section 7 below.

---

## 7. Decisions and measurements needed from the owner

| # | Decision | Recommended default |
|---|---|---|
| 1 | Roof: 6.0 mm bare with end lips, no veneer or cleats | Yes |
| 2 | Liner: kerfed and non-structural, tuned to D4 (or no liner at all, the simplest build) | Kerfed liner |
| 3 | Forearm seam: accept under white, and use the freedom for a 0.42 front roll under the forearm | Yes to both |
| 4 | Heel: CNC the current loft; decide relief by hand after playing in the white | Yes, up to 0.30 |
| 5 | Trem unit: vintage six-screw with steel block, or VT1 (this also unblocks the top slot) | Vintage, three springs |
| 6 | Treble horn back roll at the cap; keep the belly reserve | Yes to both |
| 7 | The one-hour prototype session and the LiDAR scan (section 5) | Before any CNC |

---

## 8. Files in this folder

| File | What it is |
|---|---|
| `calc_roof.py`, `roof_results.json`, `roof_output.txt`, `fig_roof_stress.png` | Roof knock stress on the real plan, rims, seasonal stress, f-hole widths |
| `calc_trem.py`, `trem_results.json`, `trem_output.txt`, `fig_trem.png` | Trem rocking mode, both tunings, VT1 grid |
| `calc_heel.py`, `heel_results.json`, `heel_output.txt`, `fig_heel.png` | Heel shapes: clearance and stiffness, parametrised on the neck |
| `calc_balance.py`, `balance_results.json`, `balance_output.txt` | Balance with the new neck |
| `calc_misc.py`, `misc_results.json`, `misc_output.txt` | Liner stiffness and tuning, feedback, guard shell, glue seam, neck-mode scaling |
| `sim/run_cases.sh`, `sim/B*.json`, `sim/runlog.txt` | Eight model cases. B0 is the plan with today's neck hardware |

Model case differences against B0, dB in 80–200 / 200–300 / 300–500 / 500–1000 Hz [computed: sim]:

| Case | Difference | Reading |
|---|---|---|
| B1: 6 mm bare roof | −0.03 / −0.27 / +0.31 / −0.52 | inside model error |
| B6: plan, liner glued stiff | −0.14 / −2.69 / −1.54 / −2.39 | real, size uncertain |
| B2: 6 mm bare, liner glued stiff | −0.17 / −3.11 / −1.53 / −2.06 | as B6 |
| B7: 5.5 mm bare, liner glued stiff | −0.11 / −3.05 / −1.45 / −1.79 | thickness: inside model error |
| B3: B2 + guard contact ×10 | −0.17 / −3.11 / +0.53 / −0.23 | +2 dB over B2 above 300 Hz |
| B4: B2 + guard contact ×0.1 | +2.20 / −2.08 / −0.39 / −0.62 | +1 to +2.4 dB over B2 |
| B5: B2 + five springs | −0.22 / −3.13 / −1.53 / −2.07 | no effect |
