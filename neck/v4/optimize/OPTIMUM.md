# Supercaster II neck and headstock: optimisation pass (proposal, 2026-11-22)

**Nothing here is approved and no existing file was changed.** `SPEC.md`, `neck_v4.py` and the CAD still show the old rod and headstock. Dimensions are inches unless marked. Strings are listed high E to low E.

## The four results

| Question | Answer | Confidence |
|---|---|---|
| Headstock tilt and tuners | Gotoh staggered locking set, head 0.54 thick, back flush with the neck at the nut, face tilted back **2.5°** from the nut line | Calculated; tuner post heights must be measured on the set in hand |
| Truss rod with the adjuster at the head | Works with **no loss of rod authority**. Same 0.009 built-in relief, about 130 lb at 0.012 | Calculated with the v4 beam model |
| How much relief | **0.011–0.012 at 0.070 action is the optimum**, not a compromise. More than 0.013 buzzes sooner | Calculated, ideal-string model |
| Shape of the relief | v4's arc is within **3%** of the best possible fret line. No fall-away or compound shape is worth adding | Calculated |

## 1. Headstock

The tuners are back-mounted, so the string height at each post depends only on the head thickness plus how far the face sits below the board. Tilt is the only free lever that helps the low E, whose post is 6.38 from the nut on the reverse head.

**Rule found:** each 0.5° of tilt adds 0.5° of break angle on every string and costs 0.27 cents of worst-case trem return error (nut friction 0.20, full dive).

| Tilt | Break angle, E1 / B / G / D / A / E6 | Weakest | Worst return error (friction 0.20 / 0.10) |
|---|---|---|---|
| 0° | 4.4 / 3.4 / 2.8 / 3.1 / 2.6 / 2.0 | 2.0° (below the floor) | 1.4 / 0.7 cents |
| 1.5° | 5.9 / 4.9 / 4.3 / 4.6 / 4.1 / 3.4 | 3.4° | 2.2 / 1.1 cents |
| 2.0° | 6.4 / 5.4 / 4.8 / 5.1 / 4.6 / 3.9 | 3.9° | 2.4 / 1.2 cents |
| **2.5°** | **6.9 / 5.9 / 5.3 / 5.6 / 5.1 / 4.4** | **4.4°** | **2.7 / 1.4 cents** |
| 3.0° | 7.4 / 6.4 / 5.8 / 6.1 / 5.6 / 4.9 | 4.9° | 3.0 / 1.5 cents |

- **Floor:** a string needs 2.6–3.3° to stay seated in its slot under a hard pick (2.6 N of vertical pick force, 1.25 safety factor, 0.5 mm of slot depth error).
- **Why 2.5° and not 2.0°:** tolerance. With no wraps on the post the weakest string drops to 4.2° (3.7° at 2.0°). If the posts turn out 1 mm taller than the catalogue figure it drops to 4.1° (3.6° at 2.0°). At 2.0° the low E sits only 0.3° above the floor in that case.
- **Fallback if 2.5° looks wrong on the template:** 2.0°. Do not go below 1.5°.
- **Height-adjustable posts (Gotoh HAP-M) instead:** posts set to 20.5 / 20.5 / 19.5 / 18.5 / 17.5 / 16.0 mm equalise all six strings, and then 1.25–1.75° of tilt is enough (4.0–4.5° on every string). This is the option if the head should look flatter.
- **Do not over-refine this.** A rough estimate of friction at the saddles and trem block gives a return error of several cents, as large as the nut's (not yet verified). Past 4° of break angle the nut is no longer the weak link.

Files: [head_opt.py](head_opt.py), [head_opt.json](head_opt.json). They import the earlier [break_opt.py](../headstock/break_opt.py) and confirm its recommendation.

## 2. Truss rod, adjusted at the headstock

The 2026-11-16 decision puts the adjuster at the head. The v4 rod has its spoke wheel at the heel, so the roles are reversed here: adjusting nut just inside the nut line, fixed anchor in the heel. Same single-acting 3/16 compression rod in a curved channel under a spline.

**Proposed path** (depth below the board top, x from the nut):

| Point | x | Depth of rod axis |
|---|---|---|
| Adjuster bearing face | 0.45 | 0.40 |
| Deepest | 8.6 | 0.687 |
| Anchor (in the heel) | 17.5 | 0.50 |

- **Authority:** 0.00416 of relief per 100 lb. v4 has 0.00422. Thirty-six other paths gave 0.0035–0.0043, so the head-end adjuster costs nothing.
- **Wood under the channel:** 0.142 minimum, the same limit as v4. Smallest bend radius 81.
- **Relief table is unchanged:** machine in 0.009; with strings (0.0085 in E♭, 0.0082 in drop C♯) the slack neck shows 0.0175; the rod carries about 131 lb at 0.012, 68 lb in a dry season, 194 lb in a humid one.
- **Access hole:** the rod rises toward the head at 4.5°. A 9/32 hole on that line passes 0.084 under the board glue line at the nut and leaves the headstock face as a trough 0.154 deep at the nut that runs out 1.26 behind it (2.5° tilt). The head keeps 0.386 under the trough. This is the familiar Fender head-adjust notch.
  - A shallower start (0.36 deep) shortens the trough to 0.84 but leaves only 0.040 of maple between the hole and the glue line. Not recommended.
- **Strength at the nut:** the hole sits on the neutral axis, so the loss of bending stiffness there is about 0.5% (estimate, not a stress analysis).
- **To check on the part:** the adjusting nut's outside diameter and length set the hole size. 9/32 assumes a 1/4 nut.

Files: [rod_opt.py](rod_opt.py), [rod_final.py](rod_final.py), [rod_final.json](rod_final.json).

## 3. Relief: how much and what shape

New calculation. Half a period after a pick the string is the mirror image of the pluck triangle, so its lowest point at each fret is known exactly for an ideal string. The buzz margin is the hardest pick (force ÷ tension) that clears every fret from every fretted position. Finding the best fret line is then a linear programme.

At 0.070 action at fret 12:

| Fret line | Buzz margin | Compared with straight |
|---|---|---|
| Dead straight | 0.00556 | — |
| Even arc, 0.008 relief | 0.00698 | +26% |
| **v4 as played (0.012)** | **0.00719** | **+29%** |
| Even arc, 0.016 | 0.00603 | +8% |
| Even arc, 0.020 | 0.00431 | −22% |
| Best possible line | 0.00743 | +34% |

- **The best even arc is 0.011.** v4's 0.012 loses 1.4% against it. 0.013 loses 4%; 0.016 loses 17%.
- **Rule for set-up:** best relief ≈ 0.16 × action at fret 12. That is 0.008 at 0.055 action, 0.011 at 0.070, 0.014 at 0.085. At each action the right relief buys about 31% more pick force than a straight neck.
- **The best possible line** bends between frets 2 and 11 and is straight above that. It beats v4 by 3%, which is less than fret-levelling error. Keep the simple arc.
- **Limits:** ideal string, no stiffness, no string-to-fret damping, pick force square to the board. Good for ranking shapes; the absolute pick force is not a prediction.

Files: [relief_shape.py](relief_shape.py), [relief_shape.json](relief_shape.json).

## What I need from you

1. **Tilt look:** 2.5° with the staggered Gotohs, or 1.25–1.75° with height-adjustable HAP-M posts.
2. **The tuner set in hand:** post heights (string hole above the base) for all six. One millimetre changes the answer.
3. **The rod part:** adjusting nut diameter and length, so the access hole can be drawn.
4. **Approval to update** `SPEC.md` and `neck_v4.py` (rod roles, head thickness 0.54, tilt), which still disagree with the 2026-11-16 decisions.
