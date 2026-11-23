# final_carve.py v3.4: rounder edge, graduated for ergonomics (2026-11-13)

Owner follow-up: "more curved, and graduated where it helps ergonomically". The crisp 1/8 in thinline look from v3.3 is withdrawn.

What stays the same:
- The outline, the carve surfaces (top_drop, back_total, forearm), the pickguard flat zone, the neck-pocket ease and the heel.
- `SC_EDGE_MODE=varedge` still gives v3.3: the check output is unchanged apart from the two added stations.

All numbers are setbacks `a`. The smallest radius of the roll is about 0.834 a.

**Files**
- Backup: `body/carve/final_carve.pre-v34-2026-11-13.py`
- Model: `body/carve/final_carve.py`
  - New default `edge_mode='ergo'`, built by `_ergo_law()` with its parameters in `edge_ergo`.
  - New helper `_segments_to_raw()`.
  - New check `R['ergo']`, which reports each place where a zone was capped below its target.
  - Two new stations: `thigh_rest` and `rib_contact`.
- Render script: `body/carve/render_v34.py`. `render_io.py` gains a treble-waist view and more section stations in its `SC_SHOT=views` branch.
- Render: `renders/carve-v3.4-edge-ergo.png`, v3.3 against v3.4. It shows:
  - views: front, back, forearm crossing, treble waist from below, f-hole flank;
  - the front and back setback laws round the outline;
  - 12 true-scale sections.

## 1. Law

Every change in setback is an S5 ramp. Its length is 1.875 |Δa| / 0.33, and it sits on the higher side, so each smaller zone keeps its full length. A C2 smoothing pass at the same 0.33/in limit follows. The largest change actually reached is 0.281/in on the front and 0.352/in on the back. The 0.352 is the untouched neck-pocket ease, the same as in v3.2.

| Zone | Target | Reached | Limited by / note |
|---|---|---|---|
| Front, default (bass and treble bouts, waists, horn tips, cutaways) | 3/8 | 0.375 | Horn tips are smooth at 3/8; the plan cap at the tips is 0.41-0.46, so it never binds. |
| Front, f-hole flank: 1.0 in before the upper eye's rim foot (x, y withheld) to the lower eye (x, y withheld) | 1/4 | 0.250 | 0.614 in of flat top between the hole and the start of the roll (≥ 0.6) |
| Front, forearm crossing: lower eye to the thinnest rim spot (x, y withheld) | as now, ~0.33 | 0.3125, held constant | Kept at v3.3's value; see the glue-seam rule below. No swell: the bass lower bout has 0 local minima. |
| Front, tail and lower bout: thinnest spot round the tail to the guard tail (x, y withheld) | 1/2 | 0.50 | **Capped** over 3.5 in, (x, y withheld) to (x, y withheld). Edge thickness and the glue seam hold it to 0.31-0.43; 0.434 at (x, y withheld), full 0.50 from y ≈ +0.8 round to the treble side. |
| Back, tail and lower bout | 1/2 | 0.50 | **Capped** over 5.6 in, (x, y withheld) to (x, y withheld), by edge thickness: 0.33 at the thinnest spot. |
| Back, treble waist (thigh rest) | 1/2 | 0.50 | full |
| Back, bass upper bout and belly (rib contact) | 1/2 | 0.494 at the rib station; 0.405 through the belly | **Capped** over 7.3 in, (x, y withheld) to (x, y withheld), by the glue plane. See below. |
| Back, both cutaways | 1/2 | 0.50 | The pocket ease is untouched (0.125 at the mouths). |
| Back, elsewhere: within 0.5 in of each horn tip, and the treble horn from x 18.5 to the tip | 3/8 | 0.375 | |

**Glue-seam rule (front).** The front roll is held to max((0.90 − top_drop − 0.005)/ROLL_SIDE, 5/16).
- Wherever the wall top could stay above the glue plane, it does.
- Where it could not, the roll is held at v3.3's 5/16.
- So the run where the wall top falls below the glue line can never be longer than in v3.3. That is why the tail starts below 1/2.

**Belly (back).** v3.1 deliberately eased the back roll to 0.30 where the belly bevel meets the rim. v3.4 lets it grow to the glue-plane limit, with a 0.10 clearance kept below the seam: margin 0.100 against the 0.06 required.
- 0.445 would just pass, at margin 0.060. I held 0.04 in reserve for machining and sanding.

## 2. Checks: v3.3 (varedge) vs v3.4 (ergo)

Both runs were made with `_final_fields.npz` deleted first, one process at a time.

| Check | v3.3 | v3.4 | |
|---|---|---|---|
| evaluate (carve: max drop / slope / f-hole margin / guard flatness / G2 jump p99.5) | 0.849 / 20.07° / 0.501 / 0.000 / 1.457 | identical | carve unchanged |
| **wood_min_3d** (≥ 0.190) | 0.196 ok | 0.196 ok | |
| top skin / back skin / rim, 3-D | 0.196 / 0.275 / 0.300 | 0.196 / 0.275 / 0.296 | rim minimum moves to (x, y withheld) |
| back skin, perpendicular minimum | 0.271 | 0.251 | at (x, y withheld); floor to split 0.253 (≥ 0.10 required) |
| chamber floor to split (chamber_wood_3d) | 0.181 | 0.144 | Information only. The bigger back roll lifts the chamber floor near the rim; no limit is set on it. |
| chamber volume | 53.418 in³ | 53.364 in³ | -0.05 in³ |
| f-hole to outline | 0.864 | 0.864 | |
| f-hole: flat top to the start of the roll | 0.739 | **0.614** | ≥ 0.6 target met |
| f-hole level margin, finished, 3° / 2° | 0.467 / 0.408 | 0.467 / 0.408 | unchanged. Both are set by the forearm's onset at (x, y withheld), not by the edge roll. |
| **glue_line_margin** (≥ 0.06) | 0.205 ok | **0.100 ok** | at (x, y withheld) |
| glue plane, wall bottom ok all round | True (highest -1.105) | True (highest -1.000) | |
| **wall-top seam** (forearm) | fails, 5.03 in, lowest -1.164 | fails, **5.03 in**, lowest -1.164 | not worse, by construction |
| top_glue_breakthrough / top_below_glue_rim_arc | 0 / 0 | 0 / 0 | |
| edge_wall_min | 0.174 | 0.157 | ≥ 0.14 floor, at the thinnest forearm spot |
| edge crease top / back (at h, then at h/2) | 0.035 → 0.006 | 0.035 → 0.006 | no crease; G2 holds |
| edge_min_convex_R top / back | 0.101 / 0.104 (0.093 at the treble horn tip station) | 0.104 / 0.104 | Both minimums are at the pocket mouth. The treble horn tip is now 0.294. |
| guard_clear_of_roll | 0.241 | 0.171 | the guard flat zone is untouched |
| a_top max / a_back max | 0.3125 / 0.3125 | 0.50 / 0.50 | |
| belly, trem routes, guard bosses, liner seat | — | identical to v3.3 | trem slot 0.178 in² uncovered is the pre-existing v3.2 conflict |

**Edge sections at the stations (setback top / back):**

| Station | v3.3 | v3.4 |
|---|---|---|
| bass horn | 0.125 / 0.312 | 0.375 / 0.50 |
| rib contact (x, y withheld) | 0.125 / 0.30 | 0.375 / 0.494 |
| bass upper bout | 0.125 / 0.30 | 0.375 / 0.448 |
| f-hole side | 0.125 / 0.306 | 0.25 / 0.50 |
| f-hole lower eye | 0.125 / 0.312 | 0.25 / 0.50 |
| forearm start | 0.125 / 0.312 | 0.312 / 0.50 |
| facet full | 0.287 / 0.312 | 0.312 / 0.466 |
| forearm deepest | 0.312 / 0.312 | 0.312 / 0.329 |
| tail | 0.312 / 0.312 | 0.404 / 0.499 |
| treble lower bout | 0.312 / 0.312 | 0.50 / 0.50 |
| thigh rest (x, y withheld) | 0.125 / 0.312 | 0.375 / 0.50 |
| treble waist | 0.125 / 0.312 | 0.375 / 0.50 |
| treble cutaway (horn-tip station) | 0.127 / 0.312 | 0.375 / 0.375 |
| bass cutaway | 0.312 / 0.312 | 0.375 / 0.50 |

## 3. For the owner's eye

1. **The f-hole band.** The front steps 3/8 → 1/4 about 1 in before the upper eye and stays 1/4 to the lower eye. It then rises only to 5/16 through the forearm, so the bass side reads a little crisper than the rest of the front (see the front-law plot and the f-hole view). It keeps 0.614 in of flat top beside the hole.
2. **The tail front can't reach 1/2 next to the forearm.** It is 0.31-0.43 for about 3.5 in, from the thinnest spot round to about y +0.8, then full 1/2. A bigger roll there would lengthen the glue-seam failure or cut the edge wall below 0.14.
3. **The belly back is 0.405, not 1/2.** It is limited by the glue plane, with a 0.10 clearance kept. That is larger than v3.1-v3.3's 0.30 and, by the glue limit alone, could go to 0.445 (margin 0.06). Say if the 0.04 reserve should go.
4. **The forearm back is 0.33 at its thinnest spot,** because of edge thickness. Elsewhere on the lower bout it is 1/2.
5. **The level margins are unchanged at 0.467 (3°) and 0.408 (2°).** They are set by the forearm onset near the lower eye, not by the edge. The 0.6 in "flat top" target is met on the roll side (0.614), but not against the forearm, which is a pre-existing forearm question.
6. **The forearm glue seam still fails** over the same 5.03 in. It needs a forearm or glue-plane decision.
7. **Back roll at the horns.** The treble horn back is 3/8 from x 18.5 to the tip, between the 1/2 waist and the 1/2 cutaway, as specified. If the 3/8 dip there looks fussy, it could run at 1/2 through the horn; the plan cap allows about 0.41-0.46 at the tip.
