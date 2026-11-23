# Supercaster II neck v4

This document replaces `neck/DESIGN.md` (v1 to v3.1) in full. Nothing from the earlier patch chain is carried over. The model is one file, `neck_v4.py`; every number below marked [C] is written by it into `results.json` or `interface.json`.

Tags: **[G]** given by the owner's brief. **[C]** computed by `neck_v4.py`. **[L: source]** literature or published dimension. **[J]** judged by me, open to change. Inches, pounds and degrees unless stated.

**Depth convention (assumed, please confirm):** every depth figure is wood only, from the top of the board on the centreline to the deepest point of the back. No frets, no finish. If the owner's 0.90 was measured over a fret, subtract 0.043.

---

## 1. One page for the luthier

**What it is.** A 1962-style Stratocaster neck: roasted maple, round-laminate rosewood board, 22 vintage-small stainless frets, reverse six-in-line head, set into the body. Nothing on it should look like a feature. The differences from a vintage neck are all in the surfaces.

| Item | Value | Tag |
|---|---|---|
| Scale, frets | 25.5, 22 | [G] |
| Width | 1.6875 at the nut, 2.079 at fret 12, 2.238 at fret 21; straight taper, 0.0375 wider than vintage all the way | [G][C] |
| String spacing | that of a vintage 1.650 nut: 1.375 E to E at the nut, 2-7/32 at the saddles | [L: vintage Fender] |
| Board radius | 7.25 at the nut, 8.38 at fret 12, 9.5 at the saddles (cone) | [G][C] |
| Depth | 0.900 at fret 1, 0.960 at fret 12, straight line between (0.892 at the nut, 0.971 at fret 15) | [G][C] |
| Back shape | full round C, no V, deepest point 0.062 toward the bass side at fret 1, drifting to the centre by fret 15 | [J], calipers pending |
| Board | rosewood 0.140 thick everywhere, underside milled concave (not bent), glue line curved across, straight along the side | [J] |
| Frets | Jescar FW43080-S, 0.043 x 0.080, in blind slots that stop 0.075 short of each side; pressed loose into glue | [G][J] |
| Scallops | 0.030 deep under the high E in cell 1, rising to 0.053 at cells 12 to 14, easing to 0.017 at cell 22; half that depth at the bass edge; deepest 0.33 behind the fret | [G][J][C] |
| Board edge | roll starts 0.110 below the corner on a straight line; on top it is 0.048 wide at each fret and 0.062 between (treble), 0.058 and 0.085 (bass) | [J] |
| Fret ends | steel starts 0.015 (treble) / 0.018 (bass) in from the side, 72 degree face, ridge rounded to 0.015; ground steel only | [C][J] |
| Relief | 0.009 machined into the neck as an arc of 2925 radius; with strings and the rod at 130 lb it reads 0.012 | [J][C] |
| Rod | single-acting 3/16, curved channel cut from the top under a maple spline, fixed anchor under fret 1, spoke-wheel nut at the body end | [G][J] |
| Head | straight string pull, face 0.44 below the board top, 0.56 thick, staggered posts, no string tree | [J] |

**Build order.**

1. Maple blank, flat-sawn, roasted. Two dowel holes in the waste for flipping.
2. Top side up: rod channel 0.200 wide with a 3/16 end mill, floor on the parabola in section 8; anchor pocket at 0.80; wheel pocket at 18.70. Fit the sleeved rod, glue the maple spline.
3. Same setup: mill the convex cone on the maple (1/2 ball nose), including the relief arc. Headstock face.
4. Rosewood blank: mill the underside concave to match (1/2 ball nose). Glue to the neck under a radiused caul.
5. Top side up again: board top, scallops and edge roll in one pass set with a 1/4 ball nose at 0.005 stepover; blind fret slots with a 0.023 end mill, 0.058 deep; nut slot; neck outline.
6. Flip: back carve with a 1/2 ball nose; back of head; heel and tenon per the body drawing.
7. By hand: sand the back to the six gauges in `gauges.pdf`; break the faint line where the roll meets the board top beside each fret; nothing else on the board needs shaping.
8. Finish. Then frets: radius, cut to length, nip the tang back 0.065 each end, shape both ends on a jig before fitting, press into glue, kiss-level, crown, polish.
9. Nut, tuners, set-up to 0.012 relief.

**The three places a careful builder will want to argue.** The relief arc (section 8), the fret ends being shaped before they go in (section 6), and the 0.140 board (section 5). The reasoning is in those sections.

---

## 2. Critique of v1 to v3.1

I recomputed each item from first principles rather than reading the old numbers.

1. **The nut analysis was built on the wrong headstock.** The earlier model put the tuner row parallel to the neck axis (post offset 0.016 per string) with the face only 0.20 below the board. That geometry gives a sideways string splay of 11.6 degrees at the nut, and the earlier conclusions ("angle the slots", the string-tree argument) follow from that artefact. A straight-pull row and a 0.44 face drop give zero sideways angle and vertical break angles of 8.6 degrees (high E) falling to 3.2 degrees (low E) [C].
2. **Relief magnitude is now right, but the design could not reach the owner's relief.** The earlier 1.7x error came from placing the string inside the board; after that fix the earlier figure agrees with mine. String pull alone gives 0.0085 (Eb standard), 0.0082 (drop C#), 0.0095 (E standard) [C]. A single-acting rod can only take relief away, so a straight-machined neck this stiff tops out at 0.0085 and can never show the 0.012 the owner asked for. The earlier rod also ran close to the neutral axis at both ends, so it needed 241 to 275 lb to do its work. The body documents still assume a two-way rod adjusted at the headstock.
3. **The edge conflict was self-inflicted.** v3.1 stacked a flared shoulder, a 0.024 corner and a steel tip 0.004 thick at the fret end. A 0.004 steel tip is a feather edge, exactly what the buildability rule forbids. The neck had also grown to 1.710 at the nut against the 1.6875 asked for. The constraints fought because three separate rules each claimed the same 0.05 of board.
4. **The profile was not one rule.** Two superellipse halves joined at an offset apex have a jump in curvature at the join, and any exponent above 2 gives zero curvature at the apex, which the hand reads as a flat spot. The claim that the surface was "exactly ruled" does not matter for a ball-nose cutter.
5. **The scallop law was a proxy.** The depth numbers were really a minimum-concave-radius limit, and the symmetric ramp put the deepest point mid-cell, where the finger is not. The finger presses just behind the fret. The earlier "crown-tangent" scallop that relied on filler, and the rosewood rail left standing at the board edge, are both dropped: v4 has no filler anywhere and the scallop runs through the edge.
6. **The 0.140 board was right for the wrong reason.** Scallops do not set it. The roll has to finish inside the rosewood with a visible band left under it; that sets it (section 5).
7. **The owner's back-bowed neck is explained.** Each 0.001 of tang interference per fret, across 22 frets, back-bows this neck by 0.0156 [C]. That is more than the whole string relief. Tight stainless frets on a stiff neck will always overpower a single-acting rod.

---

## 3. The profile law

One rule gives width, radius, depth and asymmetry at every station. Seven named parameters.

- Width: `W(x) = 1.6875 + 0.550 * x / 17.919` [G][L: vintage 1.650 to 2.200 at fret 21].
- Board radius: `R(x) = 7.25 + 2.25 * x / 25.5` [G]. Board top: `z = -(R - sqrt(R^2 - y^2))`.
- Depth: `D(x)` linear through 0.900 at fret 1 and 0.960 at fret 12 [G].
- Back: with `u = 2y / W` and `w = u - eps * (1 - u^2)`,
  `z_back = z_sh - (D + z_sh) * (1 - w^2)^m`, where `z_sh` is the glue line at the board edge.
- Fullness `m = 0.45` [J]. 0.50 is a true ellipse; lower is fuller in the shoulders.
- Asymmetry `eps(x) = eps_nut * (1 - x / 14.779)`, `eps_nut = 0.08`, positive = bass side fuller [J]. It reaches zero at fret 15 where the heel begins, so the heel is symmetric.

The asymmetry is a smooth sideways shift of one curve, so curvature is continuous everywhere and there is no join line. The back meets the side wall with a vertical tangent, so there is no shoulder corner.

| Station | x | Width | Depth | Radius | Deepest point toward bass | Thickness 0.5 bass of centre | 0.5 treble of centre | EI, N m2 |
|---|---|---|---|---|---|---|---|---|
| Nut | 0.000 | 1.688 | 0.892 | 7.25 | 0.067 | 0.774 | 0.724 | 357 |
| Fret 1 | 1.431 | 1.731 | 0.900 | 7.38 | 0.062 | 0.786 | 0.741 | 372 |
| Fret 5 | 6.397 | 1.884 | 0.926 | 7.81 | 0.043 | 0.823 | 0.795 | 429 |
| Fret 9 | 10.338 | 2.005 | 0.947 | 8.16 | 0.024 | 0.849 | 0.835 | 488 |
| Fret 12 | 12.750 | 2.079 | 0.960 | 8.38 | 0.011 | 0.864 | 0.858 | 530 |
| Fret 15 | 14.779 | 2.141 | 0.971 | 8.55 | 0.000 | 0.876 | 0.876 | 570 |
| Fret 17 | 15.948 | 2.177 | 0.977 | 8.66 | 0.000 | 0.885 | 0.885 | 593 |

All [C]. Fret 17 is inside the heel: the board, edge and width follow the law there, the back belongs to the body's heel carve.

**Re-fitting from calipers.** Four readings on the SRV reference neck fix all four free parameters: depth on the centreline at fret 1 and at fret 12 (subtract the fret if it is on), and thickness square to the board 0.5 to the bass side and 0.5 to the treble side of centre at fret 1. Then:

```
python -I -B -c "import neck_v4 as n; print(n.fit_from_calipers(0.90, 0.96, bass_t=0.786, treble_t=0.741))"
```

returns `d1, d12, fullness, eps_nut`. Put them in `PARAMS` and re-run `calc`, `fig`, `gauges`. Whichever side reads thicker is the fuller side; I have assumed bass, since the thumb-over hand fills there [J].

**Gauges.** `gauges.pdf` holds six full-size cards (nut, frets 1, 5, 9, 12, 17) with a 6.000 inch and a 150 mm check bar. Print at 100 %. Bass is on the left as seen from the nut.

---

## 4. Scallops

**Law.** Cell k is the space behind fret k. A flat land 0.055 wide stays each side of every fret centreline [J]. The deepest point sits 0.33 behind the fret (mid-cell where the cell is too short) [J]. Quintic ramps both ways, so slope and curvature are zero at the land and at the bottom. Depth under the treble edge:

`d_k = min( 0.030 + 0.025 * s_k , 0.70 * (shorter ramp)^2 )`, with `s_k` running 0 to 1 from cell 1 to x = 13.3.

Across the board the depth falls linearly to half at the bass edge [J]: wound strings need less room under them, and the thumb-over hand wraps that edge.

| Cell | 1 | 4 | 8 | 12 | 13 | 14 | 16 | 18 | 20 | 22 |
|---|---|---|---|---|---|---|---|---|---|---|
| Treble edge | .030 | .038 | .046 | .053 | .053 | .053 | .042 | .032 | .024 | .017 |
| Centre | .023 | .028 | .035 | .040 | .040 | .040 | .032 | .024 | .018 | .013 |
| Bass edge | .015 | .019 | .023 | .026 | .026 | .026 | .021 | .016 | .012 | .009 |

All [C]. Smallest concave radius anywhere: 0.247 [C], so a 1/4 ball nose (0.125 radius) cuts every scallop with no hand work.

**Slides.** I roll a rigid fingertip of 0.30 radius along the high E and take the steepest slope it has to climb [C]:

| Surface | Climb angle |
|---|---|
| Vintage 0.043 fret, flat board | 29.1 |
| Medium 0.047 x 0.104, flat board | 29.7 |
| Tall narrow 0.055 x 0.090, flat board | 32.9 |
| Jumbo 0.058 x 0.110, flat board | 33.2 |
| v4, worst cell | 33.3 |
| v4, cells 1 to 14 going up / coming down | 31.6 to 32.8 / 29.2 to 32.6 |

So slides on v4 feel like a medium-jumbo fret. They cannot feel like a vintage fret on a flat board, because the scallop is, to the finger, extra fret height. This is the one place where two of the owner's wishes pull against each other:

| Peak depth | Worst climb | Rosewood left under the scallop | Cell 22 |
|---|---|---|---|
| 0.038 | 32.3 | 0.102 | 0.012 |
| **0.053 (v4)** | **33.3** | **0.087** | **0.017** |
| 0.064 (earlier law) | 34.5 | 0.076 | 0.025 |

All [C]. I recommend 0.053: the last 0.011 of depth buys nothing the fingertip can reach and costs 1.2 degrees of catch.

**At its ceiling:** scallop shape. The ramps are already curvature-continuous and the catch is set by fret height plus depth, not by ramp shape.

---

## 5. Board, edge and the breathing-roll test

**Board thickness: 0.140 confirmed** [J]. What sets it [C]:

- deepest scallop leaves 0.087 of rosewood; the 0.058 slot leaves 0.082;
- the roll starts 0.110 below the corner, leaving a flat rosewood band 0.030 tall above the glue line.

A real 1962 veneer board is thinner (about 0.10 [L: commonly quoted for 1962-63 round-laminate boards, not verified here]), so from the side this board shows a slightly taller rosewood band. At 0.125 the band under the roll falls to 0.015 and reads as a thin line; I would not go there.

**Mill it, do not bend it.** Bending 0.140 to a 7.25 radius needs 0.97 % surface strain [C], about the breaking strain of dry rosewood [J]. Both faces are milled, as the originals were.

**Edge construction.** At every station the edge is a quarter ellipse. It starts on a straight line 0.110 below the nominal board corner and rises to meet the top. Its width on top is driven by the same per-cell function as the scallop, so the two move together:

| | At a fret | Between frets |
|---|---|---|
| Treble | 0.048 | 0.062 |
| Bass | 0.058 | 0.085 |

All [J]. Beside each fret the wood is left standing up to crown height and falls away into the cell, so the steel end is backed by wood on both sides.

**Test of the hypothesis.** I compared three edges with one metric: how far the surface stands out when approached at a given angle above side-on, traced along frets 9 to 16 [C].

| | Vintage (broken corner, 35 degree bevel) | v4 breathing roll, treble / bass | Uniform heavy roll, fret ends domed inboard, treble / bass |
|---|---|---|---|
| Fret end stands above the wood beside it, hand at 15 degrees | 0.003 | 0 / 0 | 0 / 0 |
| at 30 degrees | 0.004 | 0.004 / 0.002 | 0 / 0 |
| at 45 degrees | 0.016 | 0.014 / 0.011 | 0.008 / 0.001 |
| at 60 degrees | 0.029 | 0.026 / 0.023 | 0.024 / 0.022 |
| Wave in the wood edge along the neck, at 45 degrees | 0 | 0.052 / 0.041 | 0.031 / 0.015 |
| Full fret height begins, from the side | 0.030 | 0.048 / 0.057 | 0.091 / 0.114 |
| String centre to full-height fret, fret 12 | 0.092 | 0.093 / 0.084 | 0.050 / 0.027 |

**Verdict.** The hypothesis is right on playability and buildability, and only partly right on feel.

- Right: the steel can come within 0.015 of the side and still be rounded, so the string keeps as much fret under it as on a vintage neck. No feather edges: the wood corner at the fret is 108 degrees and the steel toe 72 degrees [C].
- Partly right: with the hand low on the side (up to about 30 degrees) the fret ends are gone. From 45 degrees up they stand 0.011 to 0.014 proud, a little better than vintage (0.016), not zero.
- Cost: the edge is no longer a straight line. It rises and falls 0.04 to 0.05 per cell at 45 degrees. Roughly half of that belongs to the roll breathing; the rest is the scallop running out through the edge.

The uniform roll hides the ends better at 45 degrees but gives away 0.044 of fret at each end, which is the string slipping off the board in a bend. That is the wrong trade for someone who plays hard, so **I recommend keeping the breathing roll.**

**Ceiling.** A steel bar 0.043 tall that stops 0.05 from the side cannot vanish to a hand coming over the top. Any design that makes it vanish does so by moving the steel inboard. v4 sits at the point where further rounding starts costing string margin.

**Slip-off margins against a vintage neck with the same strings** [C]:

| | String centre to board side, v4 / vintage | To full-height fret, treble v4 / vintage | Bass v4 / vintage |
|---|---|---|---|
| Nut | 0.156 / 0.138 | n/a | n/a |
| Fret 1 | 0.155 / 0.136 | 0.107 / 0.106 | 0.097 / 0.106 |
| Fret 12 | 0.141 / 0.122 | 0.093 / 0.092 | 0.084 / 0.092 |
| Fret 21 | 0.135 / 0.116 | 0.087 / 0.086 | 0.077 / 0.086 |

Treble is at vintage parity or slightly better. Bass gives up 0.0085 of full-height fret by choice, in return for the softer roll under the thumb; counting fret that is within 0.005 of full height, bass is 0.002 better than vintage. Setting the bass edge to the treble numbers recovers it if the owner prefers.

---

## 6. Fret ends

**Shape.** The end is simply the crown cut off by the same curve as the wood below it, with the ridge between crown and end face rounded. No dome, no filler.

| | Treble | Bass | Tag |
|---|---|---|---|
| Steel begins, from the board side | 0.015 | 0.018 | [C] |
| Full crown height reached, from the side | 0.048 | 0.057 | [C] |
| End face angle at the toe | 72 | 72 | [C] |
| Radius on the ridge after dressing | 0.015 | 0.015 | [C] from a [J] blend |
| Crown length at fret n | W(x_n) - 0.033 | | [C] |
| Tang length at fret n | W(x_n) - 0.160 | | [C] |

**A simpler end, same feel.** The owner asked for semi-hemispherical ends. The plan-view rounding of a hemisphere does no work here: the crown already tapers to nothing at its two flanks, so the corners seen from above are at zero height. What the hand meets is the toe position and the face angle. A flat 72 degree face with a rounded ridge scores the same on the edge metric and is roughly half the filing. That is what v4 specifies.

**Order and tools.**

1. Radius the wire slightly tighter than the board so the ends seat first.
2. Cut each fret to its crown length (all 22 are listed under `derived.frets` in `results.json`). Nip the tang back 0.065 (treble end) and 0.062 (bass end) with a hardened tang nipper; file the underside flat.
3. Shape both ends off the neck: 72 degree face on a disc sander with an angle fence, then round the ridge with a 300 then 600 grit diamond file. Polish.
4. Press into glue with a radius caul, located by a stop against the board side. Placement tolerance 0.005.
5. On the neck: three or four strokes of a safe-edge file and an abrasive stick to marry steel to wood. Kiss-level, crown, polish.

This is the bound-board method without the binding. Doing the steel work off the neck is what keeps the rosewood roll untouched.

**Cost in stainless** [J]: about 2 minutes per end to pre-shape and 1 minute to blend, 44 ends, so 2 to 2.5 hours on top of a normal stainless fret job. One nipper edge per neck is a fair allowance.

**Seating and glue.** Slot 0.023 wide for a nominal 0.020 tang, 0.058 deep for a 0.050 tang (**measure the wire first**: the tang figures are from an earlier transcription I could not verify) [J]. Knock the barbs down until a fret presses home with a caul and light hand pressure. Medium cyanoacrylate along the slot and under the overhanging ends. The glue holds the fret; the slot does not. A soldering iron on the crown releases it for a refret. With the steel 0.015 inside the wood, the board would have to shrink 1.4 % across its width (at fret 12; 1.8 % at the nut) before an end could stand proud [C], several times any seasonal movement [J], so fret sprout will not happen.

---

## 7. Nut and headstock

| String | Post distance from nut | Break angle | Down-force on nut, lb | Margin against a hard pluck lifting it | Return error at mu 0.20, cents |
|---|---|---|---|---|---|
| E1 | 1.85 | 8.6 | 2.47 | 20x | 1.8 |
| B | 2.75 | 5.9 | 1.58 | 14x | 1.8 |
| G | 3.64 | 4.5 | 1.21 | 11x | 1.8 |
| D | 4.54 | 4.4 | 1.32 | 10x | 2.1 |
| A | 5.44 | 3.7 | 1.20 | 9x | 2.1 |
| E6 | 6.33 | 3.2 | 1.02 | 7.7x | 2.1 |

All [C], with tall posts (string hole 20 mm above the base) on the three nearest the nut and short posts (18.5 mm) on D, A and low E [L: Gotoh staggered post heights, to be checked on the set in hand].

- **No string tree.** Every string has enough down-force without one.
- **The trem return error is set by friction, not geometry.** It works out to roughly the same 2 cents for every string whatever the post distance, and it scales directly with the friction coefficient: 0.5 cents at 0.05, 1.1 at 0.10, 2.1 at 0.20, 3.2 at 0.30 [C]. So the gain is in the nut material and the polish of the slots, and nowhere else. Changing the face drop from 0.38 to 0.50 moves the low E break from 2.7 to 3.8 degrees and the error from 1.8 to 2.4 cents: no free lunch there.
- **Nut:** unbleached bone, slots polished to 2000 grit, floors falling toward the head, lubricated [J]. A PTFE-loaded synthetic halves the error and looks slightly less vintage; owner's call (section 12).
- **Straight pull** needs the tuner row at 17.1 degrees to the neck axis [C]. Check this against the headstock template; the reverse outline in `src/` has its edge parallel to the axis.
- **Headstock numbers for the body model** [C]: wood 0.089 kg, six tuners 0.168 kg (28 g each with bushing [L: Gotoh SD91 MG-T about 27 g]), total 0.257 kg, centre of mass 3.90 behind the nut, 0.32 toward treble, 1.00 below the board top. The outline used is approximate and affects only mass.

---

## 8. Relief and the truss rod

**The conflict.** The owner wants (a) 0.012 or more relief, (b) a neck that sits near that with little rod load, (c) adjustment both ways across the seasons, (d) a single-acting rod that never rattles. A 0.90 neck gives 0.0085 from string pull [C], and a single-acting rod only subtracts. So relief must be built in, and the more is built in, the harder the rod works:

| Relief machined in | Relief with strings, rod slack | Rod load at 0.012 | Rod load, dry to humid season | Most relief available in the worst season | Works both ways |
|---|---|---|---|---|---|
| 0 | 0.0085 | cannot reach | n/a | 0.004 | no |
| 0.006 | 0.0145 | 59 lb | -3 to 121 lb | 0.010 | no |
| **0.009** | **0.0175** | **130 lb** | **68 to 192 lb** | **0.013** | **yes** |
| 0.012 | 0.0205 | 201 lb | 139 to 263 lb | 0.016 | yes |

All [C], Eb standard, seasonal swing taken as 0.0001 differential strain between rosewood and roasted maple [J], which moves relief by 0.0026. Constraint (b) is the one that gives: "little rod load" becomes 130 lb. That is still a light load for a 3/16 rod (thread stress 12,500 psi at 250 lb [C]) and it keeps the rod above the 40 lb it needs to stay silent [J]. **I recommend 0.009.** In an average season the owner can dial anything from 0.007 (rod at 250 lb) to 0.016 (rod at 40 lb).

**How it is machined.** Every toolpath, top and back, gets the same height offset: a circular arc of 2925 radius, tangent at the body joint, lifting the nut end by 0.042 [C]. The board stays 0.140 thick and the depth law is untouched. The body drawing needs to know the nut sits 0.042 high.

**Rod.** Axis is a parabola: 0.46 below the board top at the anchor (x 0.80), 0.69 at mid-neck, 0.40 at the wheel (x 18.70) [J]. It runs 0.055 below the neutral axis at the anchor and 0.28 at mid-neck [C], so it has leverage along its whole length: 0.0042 of relief per 100 lb [C].

- Smallest wood left under the channel: 0.142 at x 8.3 [C].
- The rod is sleeved and bedded on three dabs of silicone; the spline is glued over it.
- The channel stops short of the nut. There is no hole and no plug at the weakest section of the neck.
- The wheel is a separate spoke nut on a 10-32 thread with a hardened washer, so a damaged thread means a new nut, not a new neck [J].
- Sensitivity: at most 0.012 of relief per quarter turn [C, rigid-thread upper bound]; expect about half of that in practice.
- Stiffness uncertainty of one blank (15 %) moves string relief by 0.0013 [C]; the rod range absorbs it.

---

## 9. Hidden ideas: kept and rejected

Kept (none visible):

1. Scallop deepest point 0.33 behind the fret, where the finger lands.
2. Scallop half as deep at the bass edge.
3. Blind fret slots: clean rosewood on the side, no tang ends, no sprout.
4. Relief arc machined in, so the rod works mid-range for life.
5. Rod channel ending short of the nut.
6. Asymmetry that fades to nothing at the heel, by the same law as everything else.
7. Staggered posts and straight pull instead of a string tree.

Rejected because they read as features or do not earn their keep:

- Volute or thickened nut area. Not a Stratocaster; unnecessary with no rod hole there.
- Carbon rods. The neck is already stiffer than the relief target wants.
- Compound or shaped fret crowns, zero fret, roller or locking nut, angled nut slots.
- Carved heel transition beyond the body's own heel carve.
- Varying the fret wire along the neck.

Left to the template maker, not modelled: the scoop from the board to the headstock face behind the nut, and the blend of the back into the head. Use the vintage curves. The rod anchor is a 0.5 washer at x 0.80, inside the neck proper, with 0.19 of maple under it and 0.07 over it [C]; the scoop behind the nut does not come near it.

At its practical ceiling: scallop ramp shape, nut geometry for trem return, fret-end concealment, crown shape (a plain round crown on 0.043 wire).

---

## 10. Acoustics, briefly

What can honestly be said from the neck alone:

- Bending stiffness rises from 357 N m2 at the nut to 593 at fret 17; sideways 1264 to 2775; torsion 77 to 132 N m2; mass 0.57 to 0.92 kg/m [C]. The neck from nut to joint weighs 0.31 kg including rod and frets; the head with tuners 0.26 kg [C].
- Dead spots come from the neck and head moving as a beam under a note. Where they fall depends on the head mass, the joint and the body together. I have not predicted them and nobody should from these numbers alone.
- Things that add loss and are within the neck's control: a rod free to touch its channel, a fret not seated at its ends, a thick glue line. All three are designed out (sections 6 and 8).
- Things I cannot support with numbers and therefore do not claim: any tonal effect of the scallops, the asymmetry or the roll.

`interface.json` gives the body model: per-cell bending stiffness both ways, torsional stiffness, axial stiffness, mass per length, neutral axis, fret masses, rod path and mass, headstock mass, centre of mass, inertia and tuner positions, string tensions, and notes on damping. Wood figures are from `body/acoustics/inputs/wood-properties.json` [L]; flat-sawn stock is assumed.

---

## 11. Buildability gate

| Feature | Least wood | Feather edge | Cutter | Later maintenance |
|---|---|---|---|---|
| Back carve | n/a | none, vertical tangent at the side | 1/2 ball nose | refinish only |
| Rod channel | 0.142 under it | none | 3/16 end mill, 0.75 flute | spoke nut replaceable |
| Maple cone and board underside | board 0.140 | none | 1/2 ball nose | n/a |
| Scallops | 0.087 rosewood | none, radius 0.247 minimum | 1/4 ball nose | oil; can be re-sanded |
| Edge roll | 0.030 band to the glue line | none, 108 degree wood corner | same 1/4 ball nose, same pass | none |
| Fret slots | 0.082 under, 0.075 to the side | none | 0.023 end mill | refret with nipped tangs, heat to release |
| Fret ends | steel toe 72 degrees | none | disc sander, diamond files | redone at each refret, off the neck |
| Nut slot | full section, no rod hole | none | 1/8 end mill | nut replaceable |

All dimensions [C]. The one hand operation on the board is breaking the faint line where the roll meets the top beside each fret (it shows in `fig/render_edge_close.png`).

**For the body drawing** (I did not touch `body/`):

- Neck is 0.0375 wider than the pocket was drawn for: 2.169 at the joint [C].
- Board is 22 frets and ends at 18.594, not 18.17.
- Depth at the joint 0.976 [C].
- Rod is single-acting with a spoke nut at x 18.70: it needs a pocket in the tenon top and a notch at the pickguard edge.
- The relief arc lifts the nut 0.042 relative to the joint tangent.

---

## 12. Owner decisions

Each has a default; if nothing comes back, the default is built.

| # | Decision or measurement | Default |
|---|---|---|
| 1 | Caliper the SRV reference neck: four readings (section 3). Confirms depth convention, fullness, and which side is fuller. | bass fuller, 0.900 / 0.960 wood only |
| 2 | Edge: breathing roll, or the uniform roll that hides fret ends better but costs 0.044 of fret at each end. | breathing roll |
| 3 | Scallop peak depth: 0.053, or the earlier 0.064. | 0.053 |
| 4 | Relief machined in: 0.009, giving 130 lb on the rod at 0.012. | 0.009 |
| 5 | Spoke nut at the body end, with a small pickguard notch. It is the only visible departure from 1962. | yes |
| 6 | Nut: polished bone (about 2 cents trem return error) or PTFE-loaded synthetic (about 1). | bone |

Two measurements for the builder before programming: the fret wire tang (depth, width, barb), and the string-hole heights of the tuner set in hand.

---

## Files

- `neck_v4.py`: the model. `selftest`, `calc`, `fig`, `render a|b|cT|cB`, `gauges`. numpy, scipy, matplotlib only.
- `results.json`: every computed number. `interface.json`: for the body model.
- `gauges.pdf`: full-size contour gauges.
- `fig/sections.png`: true-shape cross-sections at the nut and frets 1, 5, 9, 12, 15.
- `fig/edge_side_treble.png`, `fig/edge_side_bass.png`: board edge in side view, frets 9 to 16.
- `fig/fret_ends_top.png`: fret ends from above.
- `fig/render_cells.png`, `fig/render_edge_close.png`: shaded views of cells 12 to 15.
- `fig/edge_detail.png`: the edge at fret 12, enlarged, against vintage.
- `fig/scallop_cells.png`, `fig/edge_feel.png`, `fig/relief_rod.png`: scallop law and slide test, edge metric, rod path and relief.
