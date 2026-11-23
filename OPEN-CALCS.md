# Open calculations and decisions (2026-11-19)

This list comes from a sweep of `body/`, `neck/` and `pickups/`, then an independent fact check (corrections folded in) and the carve checks run on Mock-up V3 today. It is a working list; nothing in it is approved.

## Decisions only Jordan can make (these block the calculations)

1. **Truss rod adjustment.** The rod adjusts at the headstock (decided 2026-11-16, per `mock_v3.py` and `construction.py`). But `neck/v4/SPEC.md` and `neck_v4.py` still put a spoke wheel at x 18.70, which is past the rounded neck end at 18.65.
   - Pick the rod type (single-acting or two-way) and the head-end access.
   - A visible nut or plug conflicts with "nothing looks like a feature".
   - Then redo the rod path, the relief table (0.009 machined relief assumes single-acting) and the nut-area strength.
2. **Trem unit:** vintage synchronized or Vega-Trem VT1. This sets the routes, block size, slot coverage and pocket depth.
3. **Open f-hole or glued liner.** A liner must go in before the back is glued, so decide before chamber CAM.
4. **Headstock look vs low-E break angle.** See `neck/v4/headstock/BREAK-ANGLE.md`. A flush back can't give the low E enough break in drop C#. Choose one:
   - accept about 2.7 deg on the low E;
   - a deeper head back of about 0.16 in (a small volute);
   - a 2 to 3 deg tilt-back (staggered Gotoh at 2.5 deg gives 4.4 to 6.8 on every string; see BREAK-ANGLE.md, 2026-11-22);
   - a retainer on the low E.
5. **Centre layer wood:** alder (likely) or maple. Once confirmed, update `construction.py`, which still draws maple with a 7/8 in liner and a 7 mm back.
6. **Carve items still open from CARVE-ARCH and HEEL:** arch depth A or B, heel approval (crotch fillets not modelled), treble horn ramp or crown, knob tilt, keel kept or dropped.

## Measurements needed from Jordan

- Saddle crest heights, for the vintage trem and the VT1 (they set the neck pocket depth).
- Trem block length, plate and slot size (they set the spring cavity depth on the 2.0 in body and the slot coverage).
- Bridge humbucker height (sets pickup route depth against the tongue and the spring roof).
- Neck calipers: 4 readings, plus confirmation of the depth convention (SPEC.md line 7).
- Fret tang dimensions.
- Nut string spread.
- Neck blank thickness after flattening.
- On the tuner set in hand:
  - post string-hole heights, and whether they are measured to the centre or the bottom of the hole;
  - bushing protrusion;
  - maximum head thickness;
  - gear direction (a reverse head on a right-handed guitar takes a 6R set).

## Calculations, before cutting wood

| # | Calculation | Why | Effort |
|---|---|---|---|
| 1 | Trem slot vs real plate and guard (carve check fails: 0.178 in² of slot not covered) | Visible gap | 2 h after measurements |
| 2 | Pocket depth from measured saddle heights | Action and neck angle | 1 h |
| 3 | Pocket heel end: the reference plan ends 0.33 short of the carve's 18.6875, neck end now 18.65 | Must agree before CAM | 1 h |
| 4 | Pickup route depths vs tongue and spring roof (0.375 in left if routes are 0.75 deep) | Wood between cavities | 1 h |
| 5 | Chamber floor-to-wall fillet kept by the real toolpath | 6 mm back strength (0.65 vs 0.891 MPa) | 2 h |
| 6 | 6 mm roof strength on V3 with the open f-hole (only the back has been checked on V3) | The open 6/6 pick depends on it | half day |
| 7 | Heel: bass pocket wall 0.63 at the mouth, bass flank radius 0.37 vs 1/2, smooth the 0.01 polyline | Look and CAM | 2 h |
| 8 | Headstock template: straight-pull row at **15.1 deg** (SPEC's 17.1 ignores the string fan and post tangent), traced reverse outline, scoop and back blend, rod access, head ≤ 0.54 thick | Neck CAM | half day |
| 9 | Rod path and relief redo once decision 1 is made | Neck CAM | 1 day |
| 10 | The −1.15 seam where it crosses the forearm and belly round-overs; the carve model checks only −0.90 | Shows only under a clear finish; under opaque white it is a witness-line risk | half day |

## Before glue-up

- Glue shear test blocks for roasted alder (and maple, if used).

## For confidence only (not blocking)

- Rebuild the sim neck and joint from `neck/v4/interface.json`, make the sim trem mass realistic (real mode about 45 Hz), and rebuild the BEM mesh for the 2.0 in body. Every cross-body dB and decay figure so far depends on these.
- Weight and balance with the 2.0 in body (+169 g), the v4 head and the staggered tuners. `balance.py` still copies the old `src/` tuner positions.
- Through-hole insert retention and seal; insert modelled without the 2 mm ring.
- Feedback when plugged in; retest the 1.75 in insert row.
- Bridge humbucker hum check on the bench.
- Refresh the stale mock-up renders.

## Documents that disagree

- Rod: SPEC/neck_v4 put a wheel at 18.70; mock_v3/construction say adjust at the headstock.
- Centre layer: construction.py says maple; V3-LIVELINESS says alder.
- construction.py draws a liner and a 7 mm back; the pick is an open f-hole with a 6 mm back.
- `src/neck-geometry.js` puts posts at 1.75 + 0.98 pitch, a row at about 1.75 deg and a 0.55 head. SPEC has 1.85, 15/16, 17.1 deg and 0.56. The corrected row is 15.1 deg and the head ≤ 0.54.
- The plan data has a guard notch at the neck end; mock_v3's guard follows the round neck end with no notch.
