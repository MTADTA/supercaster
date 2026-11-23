# final_carve.py v3.3: variable edge roll (2026-11-13)

Approved by Jordan, informed by `body/reference/thinline-compare/COMPARE.md` §5.

**What changes:**
- The front edge stays a crisp 1/8 in wherever the silhouette is seen from the front.
- The roll grows only where it is hidden from the front.
- The back roll is 5/16 in all round.

The carve surfaces (top_drop, back_total, forearm) and the pickguard flat zone are unchanged. The outline is unchanged, so the f-hole still has 0.864 in of clear wood to the edge.

**This is a visible reduction from v3.2.** The v3.2 "compound" law ran a 0.50 in setback (a stock-Strat-size roll) on about 69% of the top outline, including beside the f-hole: its f-hole term never switched on. v3.3 cuts that to 1/8 in on the visible front and to 5/16 in on the back.

**Setback versus radius.** The model's numbers are setbacks `a`: how far in from the outline the roll reaches. The roll's smallest radius is 0.834 a:

| Setback a | Smallest radius |
|---|---|
| 1/8 in (0.125) | 0.104 in |
| 5/16 in (0.3125) | 0.26 in (about 1/4 in) |

**Files**
- Backup: `body/carve/final_carve.pre-varedge-2026-11-13.py`
- Model: `body/carve/final_carve.py`
  - New default `edge_mode='varedge'`.
  - `SC_EDGE_MODE=compound` still gives v3.2 exactly.
  - New function `hidden_window()`.
  - New `R['varedge']` check, plus four new edge stations.
- Render:
  - New render script: `body/carve/render_varedge.py`.
  - `render_io.py` gets a new `SC_SHOT=views` branch. It is additive; the other shots are unchanged.
- Render: `renders/carve-v3.3-variable-edge.png`
  - Before and after, side by side: front, back, forearm crossing (from over the tail), and the f-hole flank close-up.
  - The setback law round the whole outline.
  - True-scale edge sections at six stations.

## 1. Parameters

| Param | Value | Meaning / why |
|---|---|---|
| `edge_mode` | `'varedge'` | New default. `'compound'` (v3.2) and `'uniform'` are still available. |
| `edge_R` | 0.125 | 1/8 in front roll wherever the front silhouette is seen. Unchanged value. |
| `edge_hid_a` | 0.3125 | Front setback where hidden: both cutaway insides, the forearm crossing, the tail and the treble lower bout. Env `SC_EDGE_HID_A`. |
| `edge_back_a_max` | 0.3125 | Back setback all round. Env `SC_EDGE_BACK_A`. |
| `edge_arm_after` | 1.0 | The front roll may not start growing until this far (in, along the outline) past the rim foot of the f-hole's aft-most vertex at (x, y withheld). |
| `edge_hid_ramp` | 1.0 | Length of the S5 ramp at each end of every hidden window. The steepest change is 0.33 in of setback per inch of outline, below the 0.352/in the pocket ease already passed. |
| `edge_horn_margin` | 0.0 | The cutaway windows reach 1/8 exactly at each horn tip (the point of greatest plan curvature). |
| `edge_tlb_guard` | 0.75 | The treble-lower-bout window ends where the guard edge comes within 0.75 in of the outline: the guard tail, at (x, y withheld). |
| `edge_hid_lip` | 0.40 | Rate-limiter cap for the varedge top. It sits above the ramps' 0.33/in, so the limiter only adds C2 smoothing and never raises the setback. |

`edge_a_max` stays at 0.50. It no longer sets any roll size in varedge mode. It still sets how far from the outline the model looks for the roll and the width of the crease-scan band. An assert keeps it at or above every zone maximum.

**Why 5/16 in, for both the hidden front and the back:**
- **Forearm.** "As much as the edge thickness allows" is 0.33 here. At the thinnest rim spot, (x, y withheld), the edge is 0.799 thick and the existing thickness limit gives 0.33.
  - A constant 5/16 sits just under that, so the roll holds one size through the whole facet.
  - With a higher cap (0.4-0.5), the roll would swell to about 0.45 just after the facet boundary and shrink back to 0.33 at the deepest point. That swelling roll is what COMPARE says to avoid, and it would deepen the glue-seam failure.
  - With 5/16 top and 5/16 back, the straight wall left at the thinnest spot is 0.174 (it was 0.140).
- **Back.** The thinline references read about 1/4 in on the back. The belly already eases the back roll to 0.30 through the waist, so 5/16 makes the back roll essentially uniform all round.
- **Hidden front.** One number for all hidden zones means the cutaway insides, the tail and the treble lower bout match the back when the guitar is seen at an angle.

**The facet boundary.** The forearm surface is not changed: arm_depth 0.85, arm_plane 1.5, zero line all as Jordan chose on 2026-11-10.
- The "facet boundary" is implemented as the point where the front roll starts to grow.
  - It is 1.30 in of outline past the eye's foot. The window opens at 1.00 in, and the smoothing pushes the first growth a little later.
  - At that point the forearm has already lowered the rim about 0.3 in, so the growth is on the ramp, inside the facet.
- The roll reaches the full 5/16 by x 28.5, where the rim is already 0.6 in down.
- From there it holds 5/16, with no swell and no dip, round the tail and the treble lower bout to the guard tail.
- Between the f-hole and that point, the hole keeps an even 1/8 frame.

## 2. Checks, before (v3.2 compound) and after (v3.3 varedge)

Both runs were made with `_final_fields.npz` deleted first. The after run was repeated after the docstring edit and gave byte-identical output. Running the edited file with `SC_EDGE_MODE=compound` reproduces the baseline output exactly; the only new lines are the four added stations.

| Check | Before | After | |
|---|---|---|---|
| evaluate: max drop / max slope / f-hole margin / slope at f-hole / guard flatness / G2 jump p99.5 | 0.849 / 20.07° / 0.501 / 0.0 / 0.000 / 1.457 | identical | carve unchanged |
| f-hole to outline (clear wood) | 0.864 | 0.864 | not reduced |
| f-hole level margin on the finished top, 3° / 2° | 0.462 / 0.408 | 0.467 / 0.408 | |
| wood_min_3d (`chamber_wood_3d.min`, required 0.190) | 0.196 ok | 0.196 ok | |
| top skin / back skin / rim (3-D) | 0.196 / 0.275 / 0.276 | 0.196 / 0.275 / **0.300** | smaller roll leaves more rim |
| back skin, perpendicular minimum | 0.252 | 0.271 | |
| chamber volume | 53.369 in³ | 53.418 in³ | +0.05 in³, negligible |
| glue_line_margin, back roll (required 0.06) | 0.205 ok | 0.205 ok | |
| glue_plane.wall_bottom_ok_all_round | True | True | |
| **glue_plane.wall_top_ok_all_round** (forearm glue seam) | **False**: 6.79 in failing, lowest -1.181 | **False**: 5.03 in failing, lowest -1.164 | **helps, still fails** |
| top_glue_breakthrough / top_below_glue_rim_arc | 0 / 0 | 0 / 0 | |
| belly on heel / trem cavity / trem mouth pad | 0 / 0 / 0 | identical | |
| liner_seat ok / guard_bosses / trem webs | ok / ok / unchanged | identical | |
| trem_routes slot uncovered | 0.178 in² (known v3.2 conflict) | identical | not touched |
| edge_wall_min (straight wall left at the edge) | 0.140 | 0.174 | |
| edge crease top / back (at h, then at h/2 in the same spot) | 0.035 → 0.006 | 0.035 → 0.006 | no crease: G2 holds |
| edge_min_convex_R top / back | 0.104 / 0.104 | 0.101 / 0.104 | the sampled check reads every 4th point. The treble_cutaway station at the treble horn tip (x, y withheld) shows **0.093** at a = 0.127, the sharpest spot. No threshold applies, but it is under the nominal 0.104 |
| guard_clear_of_roll | 0.060 | 0.241 | guard flat zone untouched |
| a_top max / a_back max | 0.50 / 0.50 | 0.3125 / 0.3125 | |
| bass lower bout a_top local minima | 1 (0.329 at the thinnest spot) | 0 (monotone up, then holds) | no swell or dip |
| **varedge: front maximum where seen** | — | **0.125** | rule met |
| varedge: growth outside the hidden windows | — | 0.0 in | |
| varedge: eye foot to first growth | — | **1.30 in** (≥ 1.0) | rule met |
| varedge: front seen / hidden arc | — | 28.4 / 27.2 in | |

**Glue seam.** With the forearm at 0.85 deep, the drop alone at the deepest rim spot is 0.849, which leaves 0.051 for any roll before the wall top passes below the glue plane at z -0.90. So even the 1/8 floor fails there. v3.3 removes the failure from x 27.7-28.4 and shortens the run to (x, y withheld)-(x, y withheld). Fixing it needs a forearm or glue-plane decision, not an edge change.

**Checks whose meaning changed:**
- `frac_at_full` and `pocket_ease_arc_*` are measured against `edge_a_max` = 0.50, so they now read 0 and None.
- In `fhole_reduced_run`, the "below 0.45" runs now cover the whole bass side, as intended.
- `R['varedge']` is the check that tests the approved rule directly.

**Edge sections at the stations (setback top / back):**

| Station | Before | After |
|---|---|---|
| f-hole side | 0.50 / 0.365 | 0.125 / 0.306 |
| f-hole pinch | 0.50 / 0.50 | 0.125 / 0.312 |
| forearm start (x, y withheld) | 0.50 / 0.50 | 0.125 / 0.312 |
| facet full (x, y withheld) | 0.463 / 0.463 | 0.287 / 0.312 |
| forearm deepest | 0.329 / 0.329 | 0.312 / 0.312 |
| tail | 0.50 / 0.50 | 0.312 / 0.312 |
| treble lower bout | 0.50 / 0.50 | 0.312 / 0.312 |
| treble waist | 0.50 / 0.50 | 0.125 / 0.312 |
| bass horn | 0.50 / 0.50 | 0.125 / 0.312 |
| bass cutaway | 0.50 / 0.50 | 0.312 / 0.312 |

## 3. For the owner's eye

1. **The front now reads much crisper than v3.2.**
   - The whole bass bout, the horns, the waists and the f-hole frame go from a 1/2 in roll to 1/8.
   - Compare the front and f-hole rows of the render. This is the change you approved, but it is a big visual step.
2. **NOT IMPLEMENTED: the crisp Artisan-style facet. The forearm contour itself is unchanged.**
   - Its zero line still touches the f-hole's lower eye, and its soft 1.5 in onset shows on the rim about 0.3-0.5 in past the eye. Only the edge roll waits 1.3 in.
   - A truly Artisan-style crisp facet line ≥ 1 in from the eye would mean redesigning the forearm. Moving the zero line clear of the eye shortens the ramp (arm_clear 1.0 moves it only 0.6 in along the rim, and the ramp from 3.14 to 2.14 in), so the arm cut gets steeper for the same 0.85 depth.
   - Not done. Your call.
3. **The subtle perimeter carve is kept.**
   - The roll still sits on the subtle top carve (edge_A 0.13 over 1.3 in) on the bass horn, the upper bout and the treble lower bout. There the face falls about 0.13 toward the edge before the 1/8 roll (see the bass-horn section).
   - That is the "1/8 edge blended into a subtle carve" spec. If the 1/8 should read even crisper, the carve can be reduced there.
4. **The tail is 5/16, continuous with the forearm and the treble lower bout.** This is inside the approved zones: the forearm crossing runs to arm_B at (x, y withheld), and the treble lower bout starts there. Holding 5/16 avoids a dip back to 1/8 between them. Aesthetic check only: the tail end shows as a line from the front.
5. **The cutaway insides grow to 5/16** between the pocket-mouth ease and the horn tips. They are back to 1/8 at each tip.
6. **The forearm glue seam still fails.** It is better than before (see §2).
7. **The pickguard flat zone is unchanged,** for the separate bend-over-carve task.
