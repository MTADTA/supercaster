# Supercaster II: weight and balance, in hand and seated

Date: 2026-11-12. Nothing is built or weighed yet. Every figure is a model of parts that have not been put on a scale.

**Tags**
- **[computed]**: from `balance.py`, `body_fields.py` or `vibration.py` in this folder.
- **[literature: source]**: a published or vendor figure (sources at the end).
- **[judged]**: my estimate.

Ranges are 5–95 % of 4000 Monte Carlo draws, paired: shared parts use the same random draws in every configuration. Each part's mass is drawn from a triangular low/likely/high range; wood densities are drawn the same way.

## 1. Answer

**There is no neck dive to fix, so nothing needs to be added or moved for balance.** Keep the strap buttons in their vintage positions. Use the lightest vintage-look locking tuner (Gotoh SD91 MG-T). Don't add ballast or move a button, and don't change the contours for balance.

- **On a strap the guitar stays body-heavy.**
  - Hanging from the horn button alone, the neck settles **53° above horizontal** (52.6–54.0). A stock pre-CBS Strat settles at 58° (57.1–58.7) [computed].
  - The guitar would only start to dive at a 30° neck angle with **about 550 g more on the headstock**. A stock Strat needs about 760 g [computed].
  - The chamber and the set neck take away 4.6° of that margin. That is about what 140 g on the headstock of a stock Strat would do [computed].
- **The guitar is lighter.**
  - **2.92 kg (2.83–3.01), or 6.4 lb**, against 3.31 kg (3.16–3.48), or 7.3 lb, for the stock reference. The same guitar with a solid body would be 3.25 kg [computed].
  - Original 1960s alder Strats weighed about 7–8 lb [literature: dealer listings]. The stock model lands at the light end of that range.
- **Seated, the one real difference is small.**
  - The chambered body sits slightly neck-heavy on the leg: 0.50 N·m (0.39–0.61) about the treble waist, where the stock Strat balances almost exactly (−0.02 N·m).
  - The forearm cancels it with about **2.3 N (about 230 g-force)** at the contour [computed]. A resting forearm presses down much harder than that [judged], so it will read as "sits a touch neck-forward", not as dive.
- **The hidden levers are all small.** The largest realistic one is about 1° of strap angle, against a 23° margin (table in section 4). None of them is needed.

## 2. Model

### Body (computed from the carve)

`body_fields.py` imports `carve/final_carve.py` and `bodylib.py` read-only and takes:
- the finished top and back, including the 1/8" edge roll;
- the bass-wing chamber as cut, including the v3.2 roof bosses: **53.6 in³** [computed];
- the f-hole through the roof.

Those columns are voxelised at 0.025". `balance.py` then subtracts the routes:

| Route | Size | Volume, in³ |
|---|---|---|
| Neck and middle single coils | 0.80 × 3.50 × 0.625 deep [judged] | |
| Bridge humbucker | 1.56 × 2.84 × 0.75 deep [judged] | |
| Control pocket (3 pots, 5-way, 3 minis, slide switch), 1.45 deep | | 17.3 [computed] |
| Same pocket on the stock reference | | 13.0 |
| Trem slot, block cavity and spring cavity | from `P['trem']` (v3.2 carve; numbers in the unpublished plan file). Not the old placeholder box | |
| Jack bore and wiring channel | | |
| **All routes** | | **36.6** (30.7 on the stock reference) [computed] |

- The heel occupies the pocket, 15.69–18.69 × 2.19 × 0.625 deep, as roasted maple.
- The hidden tongue (18.72–21.7, 1.9 wide) is maple replacing alder. Its depth band, z −0.625 to −0.875, is [judged]; the carve does not model its z section.

### Neck

- Built from the carve's `heel_back_z` loft (C-neck, then the round heel), the repo headstock outline at 0.55" thick less six 10 mm holes, and a 0.20" slab rosewood board on the 7.25–9.5" cone.
- 22 frets; the board ends at 18.59 [computed].
- Wood volumes: maple 26.9 in³ (headstock 7.4), rosewood 6.5 in³ [computed].

### Densities, g/cm³

| Wood | Range used | Basis |
|---|---|---|
| Roasted alder | 0.36 / 0.40 / 0.44 | [judged]: red alder about 0.41 SG, 0.45 air-dry [literature: Wood Handbook], less a few % for thermal modification |
| Stock plain alder | 0.40 / 0.45 / 0.52 | [judged] |
| Roasted maple | 0.60 / 0.65 / 0.70 | [judged] |
| Stock plain maple | 0.66 / 0.70 / 0.74 | [judged] |
| Rosewood | 0.75 / 0.83 / 0.90 | [judged] |

### Strap and seated models

- **Strap.** Hanging from the horn button alone, the guitar settles where its centre of mass (CoM) lies straight below the button. At a steeper playing angle the rear strap goes slack, and the fretting hand must hold the torque m·g·d·sin(θ_free − α); a positive value means the guitar is body-heavy.
- **Buttons, traditional positions.** Horn button at the bass horn tip, tail button at the tail on the centreline (coordinates from the plan file). Both at mid-thickness.
- **Limits of the strap model.** It is a single-pivot criterion. It ignores the shoulder geometry and the friction of a real strap and the player's body. Treat it as a ranking and a no-dive test, not as a predicted hang angle [judged].
- **Seated.** The pivot is the treble waist; the neck is at 15°; the forearm rests at about (28.0, 3.5).

## 3. Results

### Mass breakdown, nominal

All masses in g. Totals are the nominal sums (every part at its likely value); the Monte Carlo medians are in the next table.

| Group | This guitar | Same guitar, solid body | Stock pre-CBS, solid | Source |
|---|---|---|---|---|
| Body wood, routed (incl. liner 13, roof veneer 12, cleats) | 1176 | 1507 | 1691 | [computed] |
| Body finish (nitro, 0.08–0.25 mm film) | 53 | 53 | 53 | [judged] |
| Neck wood, frets, nut, tree, finish | 453 | 453 | 459 (21 frets) | [computed] wood; frets 0.45 g/in [judged] |
| Truss rod | 110 (two-way steel) | 110 | 63 (one-way steel) | [literature: StewMac, Maderas Barber]; one-way [computed] |
| Tuners ×6 | 168 (Gotoh SD91 MG-T) | 168 | 144 (Kluson) | [literature: Rockinger 27 g/pc] + bushings [judged] |
| Neck plate + 4 screws | — | — | 53 | [judged] |
| Trem: block, plate, saddles, arm, pivots, springs, claw | 469 | 469 | 481 (+ cover) | [literature: Seymour Duncan forum, vintage trem about 375 g]; rest [judged] |
| Pickups | 217 (HSS, bridge humbucker 145) | 217 | 108 (SSS) | [judged] |
| Pickguard + screws | 90 | 90 | 90 | [computed] area 44.6 in² × 0.06–0.09" × 1.38 |
| Electronics (pots, switches, minis, jack cup, piezo) | 151 | 151 | 116 | [judged] |
| Strap buttons, strings | 19 | 19 | 19 | [judged] |
| **Total, nominal** | **2906** | **3236** | **3277** | [computed] |

### Mass, balance and feel

| | This guitar (final plan) | Same guitar, solid body | Stock pre-CBS solid Strat |
|---|---|---|---|
| Mass, kg (5–95 %) | **2.92 (2.83–3.01)** | 3.25 (3.13–3.36) | 3.31 (3.16–3.48) |
| CoM x from nut, in | 19.38 (19.20–19.55) | 19.72 | 20.02 |
| CoM y (bass +), in | −0.39 | +0.01 | −0.04 |
| CoM z (top = 0), in | −0.55 | −0.58 | −0.63 |
| Free-hang neck angle from the horn button | **53.3° (52.6–54.0)** | 57.1° | 57.9° |
| Balance margin at a 20° neck angle (+ = body-heavy), N·m | +3.16 | +3.89 | +4.17 |
| Same at a 30° neck angle, N·m | +2.27 | +2.94 | +3.18 |
| Neck-dive torque the fretting hand must hold (up to a 50° neck angle) | **0** | 0 | 0 |
| Extra headstock mass to make it dive at 30° | 550 g | — | 760 g |
| Seated moment about the treble waist (+ = neck-down), N·m | +0.50 (0.39–0.61) | +0.20 | −0.02 |
| Forearm force that cancels it | 2.3 N | 0.9 N | 0 |
| Face tilt hanging on the strap (top tips up) | 6.0° | 6.4° | 5.3° |

All rows [computed].

**Paired differences, this guitar minus each reference [computed]:**

| | vs stock | vs solid body |
|---|---|---|
| Mass, g | −390 (−480 to −330) | −330 |
| CoM, in toward the nut | 0.64 | 0.35 |
| Free-hang angle | −4.6° | −3.8° |

**Cross-check against the study.**
- The study says the chamber costs 378 g and the solid reference shifts balance 0.69 in. Here, by the same subtraction, the chamber nets **−330 g** after the 25 g of veneer, liner and cleats, with a **0.35 in** shift [computed].
- The study's baseline mass was 2.938 kg. On the same basis (4 mm top, no veneer, plain liner, about 36 g less than the final plan) this model gives about 2.87 kg, so the two differ by about 70 g [computed].
- **The study's balance point does not reconcile.** It gives x = 15.51; this part-by-part sum gives 19.4.
- Moving the CoM from 19.4 to 15.5 at 2.9 kg means shifting about 11 kg·in. That is roughly 600 g moved from the tail to the headstock, so the study's figure cannot describe this part list [computed].
- At x = 15.5 the free-hang angle would be about 28°, and the guitar would dive at steeper playing angles. Strats are known not to dive, so I trust the part-by-part sum [judged].
- The study's code was deleted, so I can't find the cause.
- **Five-minute check:** balance the assembled guitar, or any Strat, across a dowel. It should balance between the neck and middle pickups, at x ≈ 19–20.

## 4. Hidden levers, each evaluated against the final plan

All [computed], deterministic nominal. "Seat" is the forearm force needed seated.

| Lever | Δ mass | Strap angle | Seat | Verdict |
|---|---|---|---|---|
| **Final plan as specified** (Gotoh SD91 MG-T, two-way steel rod) | 0 | 53.3° | 2.24 N | baseline |
| Kluson vintage, non-locking (reference only) | −24 g | +0.8° | 1.61 N | not locking |
| Hipshot Grip-Lock | +18 g | −0.6° | 2.71 N | heavier, and the look is less vintage |
| Sperzel Trim-Lok | +48 g | −1.6° | 3.49 N | heavier, modern look |
| Two-way hybrid rod (Ti/steel) | −18 g | +0.3° | 2.01 N | marginal |
| **Two-way titanium rod** | −42 g | +0.6° | 1.71 N | real but small: 42 g off the guitar, 0.6° |
| One-way titanium rod | −72 g | +1.1° | 1.34 N | conflicts with the decided two-way rod |
| Headstock trim slug +45 g (design note §3) | +45 g | −1.7° | 3.54 N | balance does not rule it out; what limits it is that the slug shows (hidden-only rule) |
| Tail mass +40 g in the solid tail (x 30.6) | +40 g | +0.7° | 1.77 N | not needed; it adds shoulder weight |
| +40 g at the trem block | +40 g | +0.4° | 1.97 N | don't: the block mass sets the 440–690 Hz pivot peaks |
| Forearm depth 0.70 / 1.00 (from 0.85) | 0 g | 0.0° | 2.24 N | balance-neutral |
| Belly "whisper" / "full" (from "blended") | +0.2 / −1.6 g | 0.0° | 2.24 N | balance-neutral |
| Horn button 0.25" back along the horn underside | 0 | −0.5° | — | worse; leave it |
| Horn button 0.25" toward the bass edge | 0 | −1.4° | — | worse; leave it |
| Roasted alder board at 0.36 / 0.44 | −116 / +116 g | −0.8 / +0.7° | 2.71 / 1.77 N | the biggest unknown; weigh the board |
| Neck blank at 0.60 / 0.70 | −26 / +26 g | +0.4 / −0.4° | — | weigh it |

**Sensitivity: change in free-hang angle per +10 g [computed].**

| Where | Change |
|---|---|
| At the tuners | −0.33° |
| At the rod centre | −0.15° |
| At the trem block | +0.10° |
| In the tail | +0.17° |

- So 1 g saved at the tuners is worth about 2 g of tail ballast.
- Restoring the stock Strat's free-hang angle with tail ballast alone would take about 265 g. That is plainly not worth carrying.

**Notes on the levers**
- **Tuners.**
  - The v1 note's cap of "≤ 140 g per set" can't be met by any locking tuner with the vintage Kluson look that I found. The Gotoh SD91 MG-T is 27 g each [literature: Rockinger], about 162–168 g a set with bushings.
  - The cap isn't needed for balance.
  - The v1 claim "balance = stock + about 60 g at the headstock" is replaced here: the whole package (chamber + set neck + lockers + two-way rod) **balances like a stock Strat with about 140 g on the headstock**, still 23° from diving at 30° [computed].
  - In the 3-D study, ±30 g per tuner moved the body twisting mode by about ±6 Hz [computed: sim3d-CHECK; the project's own model, unvalidated]. The SD91's 28 g against the study's 30 g is about +0.4 Hz, which is negligible for the liner target.
- **Truss rod.**
  - The rod's centroid is only about 4.5 in from the horn button, against about 17 in for the tuners. So titanium is a weak balance lever.
  - Ti-6Al-4V and steel have nearly the same stiffness-to-density ratio (about 25.7 against 25.5 GPa per g/cm³), so a titanium rod should move the neck modes very little. But it gives less correction per turn [judged].
  - Choose the rod on adjustment and stability. The decided two-way steel rod is fine.
- **Ballast.** If ballast were ever wanted, it would go only in the solid spine or tail, fitted before the bench air-resonance reading. Never on the wing or the chamber roof: in the study, 40 g on the wing changed the voice and cost 40–50 % of the decay on D4, C#4 and C5 [computed: sim3d-REPORT §1.3; unvalidated].
- **Contour depth is a feel decision, not a balance one.** The variants change the chamber volume by −2.4 % (full belly) to +2.9 % (whisper belly), and the forearm depth by ±1.3 %. That moves the air resonance by about ±2–4 Hz, inside the bench-trim window [computed volume; Hz judged from A0 ∝ V^−½].
  - So pick the forearm depth from the edge-thickness measurement and the belly depth by feel.
  - Cut the contours before the dry-clamp air-resonance reading.
- **Strap buttons.** The horn button already sits at the horn tip, which is the best place for it in plan. Moving it is worse or impossible. Keep the tail button on the centreline (vintage). The v1 rule still stands: never move it toward the bass side.

## 5. Where the player feels vibration

The levels are the 3-D study's, per newton of vertical saddle force, with the guitar held:
- study baseline, `sim3d-REPORT.md` §4;
- plus the final-build changes, `final/liner-RESULT.md` §4 (its "current design" is that same baseline).

They are converted to displacement at each band centre [computed, `vibration.py`]. The saddle force is about 0.1 N for a soft pluck and about 1 N for a hard pluck [judged].

| Contact | 80–200 Hz | 200–300 Hz | 300–500 Hz | 500–1000 Hz | Final vs study baseline |
|---|---|---|---|---|---|
| Forearm on the contour, µm per N | **1.5** | 0.8 | **1.2** | 0.5 | not reported for the final; judged within ±1 dB |
| Belly / chest through the back, µm per N | 0.8 | 0.4 | 0.6 | 0.35 | −0.5 to −0.8 dB |
| Back of the neck (fretting hand), µm per N | 0.4 | 0.26 | 0.3 | 0.4 | +0.2 / +0.4 / −1.3 / 0.0 dB |
| Belly, same guitar with a solid body, µm per N | 0.44 | 0.20 | 0.12 | 0.13 | solid is 5.5 / 7.1 / 14.4 / 9.3 dB below the chambered body |

Displacement thresholds, read approximately from published vibrotactile threshold curves (Verrillo; Gescheider) [judged]:

| Skin | Threshold near 250 Hz | At 100–150 Hz and above 500 Hz |
|---|---|---|
| Palm or fingertip | about 0.1–0.3 µm | several times higher |
| Hairy skin of the forearm or chest | about 0.5–2 µm, higher through clothing | |

**What that means at the strings**
- **The forearm feels the most.** It reaches threshold on a firm pluck, and most clearly at 300–500 Hz, where the bass-wing flap mode (406–438 Hz) sits.
- **The belly feels about half as much as the forearm** (−5 to −6 dB), and through a shirt it sits near threshold. It is clearly livelier than a solid body: +5.5 to +14 dB at the belly, with the largest gain at 300–500 Hz [computed: sim3d-REPORT §4; the project's own model, unvalidated].
- **The fretting hand feels it as clearly as the forearm**, even though the neck moves least: glabrous skin is about 10 dB more sensitive. This agrees with the study, which found the back of the neck to be the clearest felt change.
- **The final liner, veneer and 5 mm top change felt vibration by under 1.3 dB everywhere.** The just-noticeable change in vibration intensity is about 1–2 dB [judged], so the player will not feel a difference from the study baseline. The chamber is what makes this guitar feel more alive than a solid Strat, and it is kept.
- **Nothing hidden that is worth doing raises the felt vibration.** The 40 g wing mass would add +7 to +9 dB at the belly, at 200–300 Hz only. But it costs 40–50 % of the decay on three notes and makes note levels uneven. It is not recommended [computed: sim3d-REPORT §1.3; unvalidated].

## 6. Weigh these, then rerun `balance.py`

Each one takes a single edit to the corresponding range in `balance.py`.

1. **The roasted alder board** (density): ±116 g, ±0.8°. This is the largest unknown.
2. **The neck blank:** ±26 g.
3. **The trem as assembled:** block, plate and saddles.
4. **The tuner set,** with bushings and screws.
5. **The bridge humbucker.**

Then do the dowel balance check from section 3 on the finished guitar.

## 7. Files and reproducibility

| File | Content |
|---|---|
| `body_fields.py` | imports the carve read-only and writes `body_<variant>.npz`: final, arm070, arm100, bellywhisper, bellyfull, precbs (stock belly) |
| `balance.py` | part list, routes, neck loft, Monte Carlo, levers; writes `balance_results.json` and `balance_output.txt` |
| `vibration.py` | felt-vibration conversion; writes `vibration_results.json` |

- **To run:** make a python3.11 venv with numpy and scipy, then run `python -I -B body_fields.py final` (with `SC_ARM_DEPTH` and `SC_BELLY` set for the variants), then `python -I -B balance.py`. Peak memory is about 0.6 GB.
- **Carve used:** v3.2, the live file on 2026-11-12. `final_carve.py` md5 `63385b0bcc9aa8268000d299310caf3e`; `bodylib.py` md5 `fa5cf5c6d09a7abf6f169f2801d2bddc`. The carve is being edited by other work; rerun `body_fields.py` if it changes.
- **Cache note:** importing `final_carve` rewrites its own `carve/_final_fields.npz` cache whenever the stored key doesn't match the code. The cache was rewritten at 22:50 and again at 22:58 while this work, and possibly other agents, were importing the module. The contents are deterministic for a given carve version. `-B` only stops `__pycache__` writes; it does not protect the cache.

## Sources

- Gotoh SD91 MG-T, 27 g per piece: [Rockinger](https://www.rockinger.com/en/parts/hardware/tuning-machines/guitar-tuners-6-left/2007/gotoh-vintage-back-lock-sd91-mg-t)
- Hipshot Grip-Lock, 27.2 g closed / 27.8 g open without buttons: [Hipshot support](https://hipshot.zendesk.com/hc/en-us/articles/15015136157588-What-is-the-weight-of-guitar-tuner-buttons)
- Sperzel Trim-Lok 3+3 set weights: [StewMac](https://www.stewmac.com/shop-by-brand/sperzel/sperzel-trim-lok-33-guitar-machines)
- Kluson-style tuner, 22 g: [Rockinger, Kluson Traditional](https://www.rockinger.com/en/parts/hardware/tuning-machines/guitar-tuners-6-left/1736/kluson-traditional-no-line-tuner?c=17)
- StewMac Hot Rod two-way, listed 0.09–0.17 kg by length (18": 0.13 kg): [StewMac](https://www.stewmac.com/luthier-tools-and-supplies/materials/truss-rods/adjustable-truss-rods/4mm-allen-nut-hot-rod-truss-rod/). Weighed at 86 g: [Luthiers Forum](https://www.luthiersforum.com/forum/viewtopic.php?p=675953)
- Titanium and hybrid two-way rods:
  - [Maderas Barber, hybrid 360 mm](https://maderasbarber.com/tonewood/en/neck-reinforcements-truss-rod/7491-dual-action-truss-rod-hybrid-titanium-steel-360mm.html): regular 108 g, full Ti 56 g, hybrid 76 g
  - [Boston TRD-420-HY](https://tma-benelux.com/pl/product/646909/double-action-truss-rod-lightweight-hybrid-titanium-420mm-length--90-grams-weight)
  - [Philadelphia Luthier Tools, full Ti](https://philadelphialuthiertools.com/truss-rods-washers-and-nuts/two-way-truss-rod-full-titanium-extremely-lightweight)
- Vintage Strat trem about 375 g, Callaham brass block 305 g: [Seymour Duncan forum](https://forum.seymourduncan.com/threads/trem-block-weights.56794/), [Reverb, Callaham block](https://reverb.com/item/627077-callaham-brass-trem-block-vintage-pre-cbs-spec-r-h-specialty-guitars-exclusive)
- Roasted-maple neck about 510 g without tuners: [Reverb, Warmoth neck](https://reverb.com/item/80122792-warmoth-vortex-roasted-maple-rosewood-electric-guitar-neck-rh-stainless-steel-6150-frets-wolfgang-neck-profile)
- 1960s Strat weights, 7 to 8 lb: [Carter Vintage 1961](https://cartervintage.com/shop/fender-stratocaster-1961-sunburst/2dMyIqQNf60PFJ6zGHhD9j6gQ5U), [Guitar World](https://www.guitarworld.com/gear/electric-guitars/fender-cbs-era-changes)
- Red alder density: USDA Forest Products Laboratory, *Wood Handbook*
- Vibrotactile thresholds: R. T. Verrillo (1960s Pacinian threshold curves); G. A. Gescheider et al. (hairy versus glabrous skin). Values read approximately, tagged [judged].
- Body vibration, chamber, tuner and twisting-mode figures: `body/acoustics/sim3d-REPORT.md`, `sim3d-CHECK.md`, `final/liner-RESULT.md`. These are the project's own simulations, not literature, and none is validated by measurement.
