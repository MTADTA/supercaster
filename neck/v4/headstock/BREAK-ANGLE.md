# Nut break angle and headstock status (2026-11-19)

## Review (2026-11-19): read this first

An independent check reproduced the arithmetic, the four corrections to neck_v4 and the 15.1 deg straight-pull row, but **rejected the recommended setting in section 4 below** (B 0.89, wraps 0/0.5/2.5/0.5/1.5/2). It saves only 0.33 cents of trem return error (inaudible, and smaller than the friction uncertainty, mu 0.10 to 0.30). To get that, it leaves B through low E at 2.6 to 3.3 deg, just 0.01 to 0.1 deg above a floor the model derived and nobody has validated. Published no-tree practice is 3 to 6 deg, with about 5 deg as a minimum (sources in the workflow literature pass). Neck relief or the post-hole reference could wipe out that margin, and it fails low E in drop C#. Return error stays between 1.3 and 2.3 cents (mu 0.20) across every option tried, so **friction is not a reason to choose a shallow break. Use the steepest break the look allows.**

Other corrections:
- Head thickness must be 0.54 or less. The MG-T is listed for heads up to 13.75 mm (retailer figure), and 0.56 is 14.2 mm. B stays the same, so the face drop becomes 0.35.
- The MG-T is a locking tuner. Use 0 to 1 wrap; wraps are not a free lever on a trem guitar.
- A reverse head on a right-handed guitar takes a 6R set. Check the gear direction and which side of each post the string passes.
- The 3.4 deg outline edge comes from neck_v4's mass-only cartoon outline, not from a traced vintage reverse template.

Effective break angle, E1 / B / G / D / A / E6 (deg), head 0.54, Eb tuning. Floors are 3.2 / 3.2 / 3.1 / 2.8 / 2.6 deg, and 2.7 (Eb) or 3.3 (drop C#) on E6. Worst error is at mu 0.20.

| Option | Angles | E6 vs drop C# floor | Worst error | Look |
|---|---|---|---|---|
| SPEC as drawn (B 1.00, t 0.56, 0 wraps) | 7.4 5.4 4.2 4.1 3.3 2.7 | -0.60 | 1.89 c | 0.11 in volute |
| Flush back (B 0.89), staggered MG-T, 1 wrap | 4.4 3.4 2.7 3.1 2.6 2.1 | -1.16 | 1.41 c | vintage |
| Flush, HAP-M 18/17.5/17/16.5/16.5/16.5 mm, 1 wrap (E6 0.5) | 6.8 5.4 4.6 4.0 3.4 2.6 | -0.7 | 1.86 c | vintage |
| Flush, staggered MG-T, wraps 4/4/3.5/3/3/2.5 | 5.3 4.2 3.4 3.7 3.3 2.8 | -0.51 | 1.77 c | vintage, many wraps |
| B 1.05 (0.16 in step behind the nut), staggered, 1 wrap | 9.2 6.7 5.2 5.1 4.2 3.6 | +0.28 | 2.32 c | small volute |

Conclusion:
- **Height-adjustable locking posts (Gotoh SD91 HAP-M) set low on the bass side** give the best break with a flush, vintage-looking head: about 5 to 7 deg on E1/B and 4 to 4.6 on G/D.
- **Low E is the one string that cannot reach its floor with a flush back.** It tops out at about 2.6 to 2.9 deg: it is 6.4 in from the nut and the post leaves no wrap room.
  - It meets the Eb floor only marginally and misses the drop C# floor by about 0.5 to 0.7 deg.
  - Only three things fix it: a deeper head back (about 0.16 in, which reads as a volute), a 2 to 3 deg tilt-back, or a retainer on the low E.
- Each of the three is a change to the look, so it is the owner's call.
- The HAP-M height range is a retailer figure, and the listings disagree (16.5 to 21.5 mm vs 16 to 20.5 mm). Either range covers the 16.5 to 18 mm settings above; confirm on the set in hand.


Model: `break_opt.py` (imports `../neck_v4.py`, edits nothing). Numbers: `results.json`. Inches, lb, degrees, cents. Tuning is Eb standard; drop C# is checked on E6.
Run: `body/sim/cache/venv/bin/python -I -B neck/v4/headstock/break_opt.py` (30 s).

## 1. SPEC section 7 reproduced, and its physics

`neck_v4.nut_and_head()` matches `results.json` to 5e-7.

| Column | What neck_v4 computes |
|---|---|
| Break | atan((z_nut - z_post)/L). The nut height is fret height + 0.020 + d/2, on the centreline. The post height is -face_drop + (base-to-hole - head_t). L = 1.85 + i x 0.896. |
| Down-force | 2T sin((theta + r)/2), where r = 0.225 deg is the playing-side rise to fret 12 |
| Margin | theta / (0.15 / (0.8 S)): the break angle over the nut-side slope of a 0.15 in pluck at S/5 from the saddle (0.42 deg) |
| Return error | 865.6 mu (theta + r) L/(S + L). Nut friction holds a tension step of mu x theta x T, which is shared over S + L of string; cents = (600/ln 2) dT/T. |

**Four corrections.** Each one makes the bass look worse than SPEC says.

1. **Sign of the rise.**
   - The string climbs on both sides of the nut, so the wrap is theta - r, not theta + r.
   - This removes 0.45 deg from every string.
2. **Board radius.**
   - On the 7.25 radius the outer strings sit 0.033 (E1, E6) and 0.012 (B, A) below the centreline at the nut.
   - At 1.85 in this costs E1 1.0 deg.
3. **Pluck lift.**
   - A pick stroke toward the body lifts the nut end at A/(S - a), not A/a.
   - For the same 0.15 in pluck that is 1.68 deg, not 0.42 deg. A 4000-mode Fourier sum confirms both values.
   - SPEC's margins of 20x down to 7.7x are therefore about 4x optimistic.
   - A cleaner form: the string stays seated while T x theta_eff exceeds the vertical pick force F. neck_v4's own pluck is F = 2.6 N.
4. **Straight pull.**
   - The string runs tangent to the post, so the centre sits r_post + d/2 (0.13 to 0.15) off the string line.
   - The strings also fan. Including both, the best straight row is **15.1 deg**, not 17.1, with 0.017 rms residual (under 0.7 deg of lateral wrap).
   - If posts are drilled as neck_v4 places them, the lateral wrap raises the bass error by 0.3 to 0.5 cents.

SPEC geometry after the corrections (face 0.44, head 0.56, Gotoh staggered posts, no wraps):

| | E1 | B | G | D | A | E6 |
|---|---|---|---|---|---|---|
| Effective break, deg | 7.42 | 5.38 | 4.19 | 4.11 | 3.34 | 2.70 |
| Seat margin (T x theta_eff / 2.6 N) | 3.5 | 2.4 | 1.9 | 2.0 | 1.7 | 1.36 (1.08 in drop C#) |
| Return error, mu 0.20, cents | 1.52 | 1.59 | 1.59 | 1.89 | 1.78 | 1.64 |

## 2. What "best" means

**Seating floor, per string:**

theta_eff >= SF x F / T_i + dz / L_i

- SF = 1.25.
- F = 2.6 N, the force implied by neck_v4's own pluck. **[assumption: hard-pick vertical force 1.5 to 4 N]**
- dz = 0.5 mm, the tolerance on post height, winding and slot floor.

That puts the floor at 2.6 to 3.3 deg. Each newton of F adds about 1.0 deg. For comparison:

| Pick force F | Floor, deg |
|---|---|
| 1.5 N | 1.6 to 2.2 |
| 2.6 N | 2.6 to 3.3 |
| 4 N | 3.9 to 4.8 |

**[assumption: the common luthier rule of thumb is 4 to 8 deg. Fender B/E strings at about 2 deg without a tree are reported to sitar. Both are unverified here.]**

**Bends and dive slack set slot depth and wall shape, not the break angle.**
- The seating ratio does not depend on tension.
- A ringing string's end slope grows only as T^-1/4 in a dive. That is 1.4x per octave on a fundamental-dominated slope about 8x smaller than the pick corner, so it never binds.
- A fully slack string re-seats only if the slot is about half a diameter deep.

**Return error.**
- error_i is about 865.6 mu x drop_i / (S + L_i).
- The error is set by the vertical drop, not by the angle. Moving a post costs nothing, and every 0.01 in of drop costs about 0.06 cents at mu 0.20.
- So the minimum-error design puts every string at the same seating margin, as low as is safe.
- Evenness follows from that.

**Optimum:** maximise the weakest string's seating force, then minimise the worst return error.

The search covered:
- 4 fixed post sets plus HAP-M;
- head back B from 0.80 to 1.10;
- post_x1 of 1.70, 1.85 and 2.00;
- head thickness t of 0.56 and 0.50;
- half-wraps up to the room on each post. Room = hole above the face - bushing (1.0 mm) - d/2.

## 3. The levers

- **Face drop alone is not a lever.**
  - The SD91 mounts from the back, so string height depends only on **B = face_drop + head_t** (the head back below the board top).
  - B is bounded by the look. The neck is 0.892 deep at the nut, and SPEC's B = 1.00 puts the head back **0.108 below the neck back**. That is a swelling behind the nut, i.e. a volute, which SPEC 9 rejects.
  - The 1.5 blank is not the limit: it allows B up to 1.58.
  - So the look sets **B <= 0.89**.
- **Head thickness** only changes wrap room. At 0.50 instead of 0.56 there is 1.5 mm more post above the face, which gives E6 a third wrap (+0.43 deg). It costs about 30% of head bending stiffness and a tuner fit outside the vintage 0.55 to 0.56.
- **post_x1** is weak: +0.1 in changes the angle by -0.04 to -0.22 deg and the error by -0.006 cents.
- **Wraps.** One wrap lowers the exit by one diameter.
  - Per string, one wrap adds: E1 +0.32, B +0.28, G +0.27, D +0.33, A +0.38, E6 +0.43 deg.
  - On the short posts there is room for only 2 (E6), 3 (A) and 4 (D).
  - The lowest exit any listed post gives E6 is about 16 mm above the back. That holds for an 18.5 post with 2 wraps, an 18 post with 1.5, and HAP-M at its 16 mm minimum, so E6's angle is set by B.
- **Post sets.**
  - On the look-limited B with t 0.56, the seating force each set reaches: Gotoh staggered 20/18.5 and flat 18.5 both 2.00 N; Rockinger 19/18 1.96 N; all-tall 20 1.91 N.
  - Staggered gives the lowest total error of the four.
  - HAP-M (16 to 20.5 mm, retailer figure) only trims E1 and B. It cannot get E6 lower than wraps already do.
- **Tilt-back (alternative only).**
  - One piece from the 1.5 blank allows at most **6.9 deg** over a 7.3 head (0.06 for flattening).
  - All strings then sit near 7 deg and the error reaches **4.1 cents** on E6 at mu 0.20, about twice the flat head.
  - Short grain at the transition leaves 0.78 to 0.88 of the strength at 7 deg, and 0.47 to 0.66 at 14 deg **[assumption: cross-grain to along-grain strength ratio 0.05 to 0.10]**.
  - A scarf allows any angle, but the glue line shows on roasted maple.
  - Both read as a feature. Rejected.

## 4. Recommended setting

- Head back **B = 0.89**, flush with the neck back: face 0.33 below the board top, head 0.56 thick.
- Gotoh SD91 MG-T staggered: tall 20 mm on E1, B and G; short 18.5 mm on D, A and E6.
- x1 = 1.85.
- Straight row at **15.1 deg**.
- **Wraps, E1 to E6: 0, 0.5, 2.5, 0.5, 1.5, 2.** Each string is wrapped up to its floor. These are locking tuners, so leave enough slack for those turns before locking.
- E6 is already at its maximum and still misses the floor by 0.08 deg (Eb) and 0.72 deg (drop C#).
- Under B <= 0.89 no listed post set can do better on E6: about 16 mm above the back is the lowest exit any of them gives.

| String | Post (base to hole) | Wraps (max) | Exit above face | L | Break, vertical / effective (floor) | Down-force (drop C#) | Seats a pick of | Error mu 0.10 / 0.20 |
|---|---|---|---|---|---|---|---|---|
| E1 | 20.0 mm | 0 (17) | 0.227 | 1.85 | 4.27 / 4.05 (3.22) | 1.13 lb | 3.4 N | 0.42 / 0.84 c |
| B | 20.0 | 0.5 (13) | 0.221 | 2.76 | 3.48 / 3.25 (3.23) | 0.84 | 2.6 N | 0.48 / 0.96 |
| G | 20.0 | 2.5 (10.5) | 0.185 | 3.66 | 3.37 / 3.14 (3.13) | 0.81 | 2.6 N | 0.60 / 1.20 |
| D | 18.5 | 0.5 (4) | 0.155 | 4.57 | 3.13 / 2.90 (2.80) | 0.83 | 2.7 N | 0.67 / 1.34 |
| A | 18.5 | 1.5 (3) | 0.114 | 5.47 | 2.98 / 2.76 (2.61) | 0.84 | 2.8 N | 0.74 / 1.47 |
| E6 | 18.5 | **2** (2) | 0.072 | 6.38 | 2.80 / 2.58 (2.66; 3.30 in drop C#) | 0.76 (0.60) | 2.0 N | 0.78 / 1.56 |

"Seats a pick of" is the pick force at SF 1.25, taking the worse of Eb and drop C#. A 2.6 N floor means every string except E6 clears it. Effective angles span 2.6 to 3.3 deg on B to E6, with only E1 higher at 4.05.

Against SPEC as corrected (mu 0.20):
- Worst error falls from 1.89 to 1.56 cents.
- Total error falls from 10.0 to 7.4 cents.
- E6's drop C# seating falls from 1.08 to 1.03 of a 2.6 N pick (SF 1, no tolerance).
- You buy the vintage back and 0.3 cents on the worst string. That costs about 0.12 deg of seating on E6 against SPEC's swollen back, and it's your call.

**Alternative, lowest total error:** wraps 0, 0, 0, 0, 0, 2. That pulls every string down to E6's 2.0 N, with a total of 6.7 cents and the same worst-string error.

**Sensitivities** (per string, E1 to E6):

| Change | Angle, deg | Error at mu 0.20, cents |
|---|---|---|
| B +0.01 | +0.31 / +0.21 / +0.16 / +0.13 / +0.11 / +0.09 | +0.06 each |
| Posts +0.5 mm | -0.61 to -0.18 | -0.12 to -0.11 |
| One more wrap | +0.32 to +0.43 | +0.07 to +0.26 |
| x1 +0.1 | -0.22 to -0.04 | -0.006 |

Error is linear in mu.

**Ways to get more seating, in order of cost:**
1. Measure the bushing. At 0.5 mm proud it gives E6 a 2.5th wrap (about +0.2 deg).
2. A 0.50 head: wraps G 1.5, A 1, E6 3 (an equal margin of 2.35 N), worst error 1.82 cents.
3. Accept a swell at the back: B = 0.96 with HAP-M meets the full 2.6 N / SF 1.25 floor on every string, including drop C#. Worst error is 1.97 cents and the head back sits 0.07 below the neck back.

## 5. Is the headstock fully designed? No.

1. **Outline against the row.**
   - Straight pull needs posts on a 15.1 deg row (17.1 in SPEC).
   - The placeholder head outline (neck_v4.py HEAD_OUTLINE, mirrored, read as a Catmull-Rom spline) has its button edge at 3.4 deg to the axis.
   - **Narrow side: fits.**
     - Wood from flange to edge at E1 to E6: 0.54, 0.79, 0.48, 0.27, 0.22, 0.18 in. All are at least 0.125 **[assumption: flange 10 mm OD]**.
     - That holds only if each string passes on the bass side of its post with the centres offset toward the treble side, and the fan is included.
     - With centres on the nut-spacing lines (as neck_v4 draws them) the E6 flange hangs 0.05 over the edge. If the strings pass on the treble side of the posts, D, A and E6 overhang.
   - **Button side: does not fit.**
     - Post to edge grows from 0.81 (E1) to 1.62 (A), a 0.81 spread, so the far buttons would sit over wood.
     - The tuner edge must be redrawn about 12 deg off the vintage line, parallel to the row. Equivalently, give up straight pull and accept about 10 deg of lateral wrap on the bass (DESIGN 6.2: 3.3 / 8.3 cents at mu 0.10 / 0.25).
     - This is an owner decision about the look.
2. **Scoop and back blend.**
   - Not modelled.
   - With B = 0.89 the back blend is vintage (flush); at SPEC's 1.00 it is a 0.11 swell.
   - The scoop drops 0.33 instead of 0.44.
3. **Truss rod.**
   - Body/heel/flow/FLOW.md (2026-11-16) records "Truss rod adjust is at the headstock", so the body-end wheel is gone.
   - SPEC 9's "scoop does not come near it" is stale. Access to the adjuster must now pass through the scoop or the nut on the centreline.
   - Not designed.
4. **Real post heights.**
   - Gotoh base-to-hole is a retailer figure (20 / 18.5, or 19 / 18 at Rockinger), assumed to be measured to the hole centre.
   - Bushing protrusion and flange OD are assumed. Measure the set in hand.
5. **Tuner hole positions** on the redrawn outline. Post centres for straight pull are in results.json `recommended.rows[].post_xy`.
6. **Mass and balance:** 0.257 kg, centre of mass 3.90 behind the nut, from an approximate outline (+/-10%). Recompute once the outline is drawn.

**Literature and assumptions to check** (another agent is gathering literature):
- Pick force 1.5 to 4 N.
- The 4 to 8 deg rule of thumb.
- Grain strength ratio.
- SD91 bushing dimensions.
- HAP-M range 16 to 20.5 mm (Rockinger / Thomann listings).
- mu 0.10 to 0.30 (neck_v4).

## Hipshot Grip-Lock staggered (2026-11-21)

No Hipshot drawing was found (hipshotproducts.com returned 429). Retailer figures only:
- Staggered post lengths are quoted as 19/20 mm (Reverb listing) or 19/20/21 mm (Fender DirectFit set). What "post length" is measured to is not stated anywhere.
- Max head thickness: staggered 14.25 mm (0.561 in), non-staggered 16.25 mm (NextGen). This would keep SPEC's 0.56 head, unlike the MG-T at 13.75 mm.
- Reverse head: order the treble-side staggered version (NextGen orientation guide).

`evaluate(B=0.89, flush)`, treating the quoted length as base-to-hole like the Gotoh figures, 1 wrap (E6 0.5), E1..E6 deg:
| Set | Angles | Worst error |
|---|---|---|
| Gotoh staggered 20/18.5 | 4.4 3.4 2.7 3.1 2.6 1.9 | 1.41 c |
| Hipshot 20/19 | 4.4 3.4 2.7 2.8 2.4 1.8 | 1.30 c |
| Hipshot 20/19/18 (if three steps) | 4.4 3.4 3.4 2.8 2.8 2.1 | 1.48 c |
| Hipshot 21/20/19 (DirectFit lengths) | 3.2 2.6 2.7 2.3 2.4 1.8 | 1.26 c |
| HAP-M 18/17.5/17/16.5/16.5/16.5 | 6.8 5.4 4.6 4.0 3.4 2.6 | 1.86 c |

Head thickness does not change these: the tuners sit on the back, so the hole height depends only on B and the post. On the quoted lengths Hipshot staggered is no better than the Gotoh staggered set. It would only match HAP-M if its "post length" is measured to the post top, putting the hole about 2 to 3 mm lower. Measure a set (back of head to the string-hole centre) before choosing.

## Staggered posts with a slight tilt-back (2026-11-22)

`evaluate(B=0.89, t=0.54, wraps 1/1/1/1/1/0.5, tilt_deg=a)`, checked three ways: an independent recomputation without `evaluate()`, a geometry critic, and a build/look review. All matched to 0.01 to 0.04 deg. Each degree of tilt adds about 1 deg to every string.

Gotoh staggered 20/20/20/18.5/18.5/18.5, E1..E6 deg, worst error at mu 0.20:
| Tilt | Angles | Worst error | Head tip below a flat Fender back |
|---|---|---|---|
| 0 | 4.4 3.4 2.7 3.1 2.6 1.9 | 1.41 c | 0 |
| 1.5 | 5.9 4.9 4.2 4.6 4.1 3.4 | 2.17 c | 0.19 in |
| 2 | 6.4 5.4 4.7 5.1 4.6 3.9 | 2.43 c | 0.26 in |
| 2.5 | 6.8 5.9 5.2 5.5 5.1 4.4 | 2.70 c | 0.32 in |
| 3 | 7.3 6.4 5.7 6.0 5.6 4.9 | 2.97 c | 0.38 in |

Smallest tilt, pivot at the nut line (0.25 deg steps):
| Posts | All floors incl. drop C# | Every string at least 4 deg |
|---|---|---|
| Gotoh staggered | 1.5 | 2.25 |
| Hipshot 20/19 or 21/20/19 (retailer lengths) | 1.75 | 2.5 |
| HAP-M 18 to 16.5 | about 0.75 | about 1.5 |

Conditions the numbers depend on:
- **The face must keep the 0.35 in drop at the nut** (0.21 below the glue plane, like a Fender step), with the tilt on top. If the face instead starts at the neck surface under the board (-0.14), E1/B/G fall to 0.9/2.0/2.5 deg at 3 deg tilt and fail. The step is what makes the trebles work.
- **Pivot location.** The model pivots exactly at the nut line. Starting the tilt 0.5 in behind the nut costs 0.1 to 0.6 deg; reaching E6 4.0 then needs about 2.25 deg (2.5 for a 1 in pivot). Reference the face plane so it passes 0.35 below the board top at the nut line.
- Table row above (flush staggered, 1 wrap, E6 2.1) uses a full wrap on E6; the 1.9 here uses half a wrap. Both are feasible (E6 has room for 2.5).

Build: one piece covers it (correct one-piece limit for this face is about 5.4 deg, not the 6.85 from `tilt()`, which assumes the face at the glue plane and t 0.56). Short-grain strength 0.95 to 0.99 of straight grain at 1.5 to 3 deg. Head thickness, the 15.1 deg row and the nut seat are unchanged; posts lean about 0.013 in. blank_t 1.5 / flatten 0.06 / head_len 7.3 are assumptions; check against the real blank.

Look: invisible from the front and player's view. In side profile the tip sits 0.19 to 0.38 in below a flat head, and the back has a convex kink of tilt + 0.3 deg at the nut rather than a volute bump.

Recommendation if a tilt is acceptable: Gotoh staggered MG-T, 2.5 deg, face 0.35 below the board top at the nut, tilt starting at the nut line: 6.8/5.9/5.2/5.5/5.1/4.4 deg, worst 2.7 c. HAP-M plus 1.5 to 2 deg reaches about 5 deg on every string except E6 (4.1 to 4.6).
