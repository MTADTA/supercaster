# Supercaster II fret ends: proposal

Status: proposal for the owner to approve. Nothing in SPEC.md, neck_v4.py or SURVEY.md has been changed.
All dimensions in inches. Every number is marked: **[C]** computed by the scripts in this folder, **[S]** sourced (SURVEY.md, SPEC.md or a maker's or repairer's published statement), **[J]** judgment.

Summary sheet: [fret-ends-summary.png](fret-ends-summary.png)

## 1. Verdict

**v4 was wrong to drop the hemisphere.** You asked for semi-hemispherical ends and v4 gave you a flat 72° face, justified by a measure that only counts how far the steel stands above the wood. That measure cannot see roundness, so it was never able to favour a round end. Measured by what a finger actually receives (the pressure under the skin), a true quarter-sphere end is softer than v4's face in five of six hand positions and equal in the sixth, with the same bending room as a vintage neck on both edges.

v4 was right about one thing, and it still holds: **no fret end can be flush with the wood and keep vintage bending room.** A bar 0.043 tall that is at full height 0.049 from the side has to stand up somewhere. The proposal does not make the steel vanish. It makes the steel round, makes the wood under it round, and puts the joint between them in a crease where neither tolerance nor humidity can raise an edge.

Answers to the four questions in the brief:

| Question | Answer |
|---|---|
| Can the fret blend into the fretboard? | By shape, yes: round steel on a round wood nose, seam in a crease. Flush, no, unless the fret ends 0.04 to 0.065 further inboard, and then strings come off. |
| Are semi-hemisphere frets possible? | Yes. A real quarter-sphere, radius 0.040, cut with a cup cutter before the fret goes in. |
| Scallops, rolled edges and round frets that disappear into the side? | All three together, yes. The scallop should stop short of the side instead of running out through it (section 7). |
| Will the strings fall off? | Bending room equals a vintage neck at frets 1, 12 and 21, both edges (section 6). |

## 2. How v4's argument was tested

v4 judged fret ends by "protrusion": seen from a given angle, how far does the steel stand above the wood? On that measure the sphere loses [C]:

| Step above the wood, viewed from | 30° | 45° | 60° |
|---|---|---|---|
| Vintage bevel | 0.004 | 0.016 | 0.029 |
| v4 72° face | 0.004 | 0.014 | 0.026 |
| Proposed quarter-sphere | 0.007 | 0.017 | 0.027 |

So by v4's own yardstick, v4 wins by 0.003. But a 0.017 step with a 0.037 radius on it is a different thing under a finger from a 0.014 step with a 0.007 ridge on it, and the yardstick scores them the wrong way round.

The better measure used here is a contact calculation (fe_contact.py): a soft finger is pressed onto the true 3-D edge with a fixed force and slid past the fret. It reports three things:

- **Hardest spot**: peak pressure under the skin, as a multiple of the same touch on a flat board. This is what "sharp" means to a hand.
- **Catch**: how steeply the edge pushes back along the neck as the finger slides (degrees).
- **Rise and fall**: how far the finger goes up and down as it travels one fret space (thousandths).

Six hand positions: side of the index finger sliding with the hand low and at 45°, fingertip sliding along the high E, fingertip landing on a fret end from above, thumb sliding the bass edge at 45°, and thumb wrapped over and gripping.

Limits, stated plainly:

- It is a model, not a measurement. The finger is a uniform soft solid (stiffness 20 psi [J]), no friction, no fingernail, no bone. Trust the comparisons, not the absolute values. The check against the textbook ball-on-flat answer agrees within 2.3 % [C].
- The grid is 0.004. Features sharper than about 0.008 are blurred, which flatters the vintage arris and v4's 0.007 ridge. The sphere's advantage is, if anything, understated [J].
- v4 is modelled as drawn. As drawn it has a wood crease beside each fret (radius 0.0012 [C]) that SPEC step 7 says to break by hand. In two hand positions that crease, not the steel, is v4's hardest spot. To be fair to v4, the headline comparison below uses v4's steel-only figure in those two positions, as if the hand work were perfect.

## 3. Comparison

Fret 12. Hardest spot in the six hand positions in the order listed above. "s" or "w" says whether steel or wood makes it. Figures: [fig/feel_fret_12.png](fig/feel_fret_12.png), [fig/feel_fret_2.png](fig/feel_fret_2.png), [fig/pressure_maps.png](fig/pressure_maps.png).

| End | Bending room, high E / low E | Steel starts in from side | Sharpest steel radius | Hardest spot, six positions (× flat) | Edge wave at 45°, treble / bass | Buildable |
|---|---|---|---|---|---|---|
| Vintage bevel, vintage-width neck | 0.092 / 0.092 | 0 | arris, hand-dressed | 8.3s 9.1s 5.7s 5.0s 8.9s 7.4s | 0 / 0 | yes |
| v4 72° face | 0.094 / 0.084 | 0.015 / 0.018 | 0.007 | 7.9w 6.9s 4.3s 4.4w 6.4s 5.4s (5.8 and 4.1 with the wood crease broken) | 0.052 / 0.041 | yes |
| **Recommended: quarter-sphere** | **0.092 / 0.092** | **0.010 / 0.010** | **0.037** | **4.1s 5.3s 3.5s 3.6s 5.3s 5.4w** | **0.032 / 0.033** | yes |
| Fallback: hand-filed dome | 0.092 / 0.092 | 0.016 / 0.016 | 0.028 | 4.0s 5.5s 3.6s 3.7s 5.5s 4.9w | 0.030 / 0.031 | yes |
| Rosewood pocket | 0.088 / 0.088 | 0.014 | 0.037 | 6.5w 5.4w 3.5s 3.5s 5.4w 4.6w | 0.052 / 0.042 | **no** (section 8) |
| Dome set inboard, uniform roll | 0.050 / 0.027 | 0.062 / 0.085 | 0.014 | 2.6w 4.6s 3.4s 3.9s 3.9s 4.3s | 0.031 / 0.015 | yes, but strings come off |

All [C] except the vintage arris note [J].

What the table says:

- **Against v4 with its wood crease perfectly broken**, the proposal's hardest spot is lower by 29, 24, 18, 14 and 17 % in the first five positions and level in the sixth (thumb wrapped over) [C]. Against v4 as drawn the first figure is 48 %. Frets 2 and 20 give the same picture (14 to 31 %) [C].
- **Against a vintage bevel** it is lower by 28 to 50 % in every position [C].
- **Catch and rise and fall** are also lower than v4: catch by 6 to 24 %, rise and fall by 1 to 33 % at fret 12 [C]. Both remain two to four times a vintage straight edge. That is the scallops, not the fret ends, and it is true of every scalloped candidate.
- **Thumb wrapped over is level** with v4 (5.4 against 5.4). There the hardest spot is no longer steel; it is the small wood nose at the bass edge. The fallback's larger nose does 8 % better in that one position [C].
- **Tolerance**: moving the proposal's steel 0.004 in or out changes its figures by at most 6 % [C]. It does not depend on perfect placement.

## 4. The recommended end

**A true quarter-sphere on the end of each fret, radius 0.040, starting 0.010 in from the board side on both edges. The board's edge roll narrows to a small rounded nose under each fret end, so the round steel sits on round wood and the seam lies in a crease.**

Sections to scale: [fig/sections_treble_fret_12.png](fig/sections_treble_fret_12.png), [fig/sections_bass_fret_1.png](fig/sections_bass_fret_1.png).

### Dimensions

Steel:

| Item | Value | Mark |
|---|---|---|
| Wire | Jescar FW43080-S, 0.043 × 0.080, stainless (unchanged) | [S] |
| End shape | quarter of a sphere, radius 0.040 (half the crown width); modelled 0.040 × 0.040 × 0.043 high | [C] |
| Steel starts (toe) | 0.010 in from the board side, both edges, every fret | [C] |
| Full height reached | 0.049 in from the board side | [C] |
| Toe | vertical where it meets the wood; no thin steel lip | [C] |
| Sharpest radius anywhere on the steel | 0.037 (v4: 0.007) | [C] |
| Crown length | board width at that fret minus 0.020 (cut list, section 11) | [C] |
| Tang | nipped back 0.075 from each crown end; tang length = board width minus 0.170 | [C] |
| Slot | unchanged: 0.023 wide, 0.058 deep, stops 0.075 from each side | [S] |
| Tang end to slot end | 0.010 clear each side | [C] |
| Crown overhang past the slot end | 0.065 each end, resting on solid wood, no gap under it | [C] |

Wood, all cut in the same 1/4 ball-nose pass as the rest of the board:

| Item | Value | Mark |
|---|---|---|
| Roll width on top, at a fret | 0.010 (v4: 0.048 treble, 0.058 bass) | [C] |
| Roll width on top, between frets | 0.062 treble, 0.085 bass (as v4) | [S] |
| Roll depth down the side, at a fret | 0.010 | [C] |
| Roll depth down the side, between frets | 0.110 (as v4) | [S] |
| How it changes along the neck | width = 0.010 + (between-fret width − 0.010) × w, depth = 0.010 + 0.100 × w, with w = 1 − exp(−(d / 0.100)²) and d the distance to the nearest fret centreline. The roll is at full width from about 0.2 either side of a fret. | [C] |
| Roll section | quarter-ellipse, as v4 | [S] |
| Scallop near the edge | full depth out to 0.140 from the side, then easing to nothing at the side: depth × (1 − ((0.140 − s) / 0.140)²), s = distance in from the side | [C] |
| Sharpest wood radius | 0.011, the nose (v4: 0.0012, the crease to be hand-broken) | [C] |
| Roll to glue line | 0.030 of rosewood left between frets, more at each fret; the maple line stays straight | [C] |
| Left uncut by a 1/4 ball nose | under 0.0001 at frets 2, 12 and 21, both edges | [C] |

### Why this shape

1. **The seam sits in a crease.** v4's steel face is flush with a sloping wood surface. If the board shrinks 0.004, the steel stands 0.0038 proud of that slope and there is an edge to feel [C]. The sphere meets the wood at a vertical toe on a small flat. If the board moves, the crease moves. Nothing is ever flush, so nothing can ever become un-flush.
2. **The extra neck width is spent on roundness.** The 1-11/16 nut gives 0.019 more wood outside each outer string than a 1.65 neck [C]. The proposal spends it as 0.010 of toe set-in plus 0.009 of longer rounding (0.039 against a bevel's 0.030), and hands back exactly vintage bending room [C].
3. **The wood is shaped by the CNC and the steel off the neck.** Nobody files stainless against rosewood. The hand-break in SPEC step 7 disappears.
4. **It is what was asked for**, and it has the largest steel radius of any candidate that keeps the bending room.

### Build steps

Wood. No new operation. The same 1/4 ball nose at 0.005 stepover cuts the new surface. Wipe the roll with 600 grit. Nothing on the board is shaped by hand.

Frets, all before fitting:

1. Radius the wire as usual. Saw each fret to its crown length from the cut list, square ends, ±0.006 [J]. Measure with calipers now, while the ends are flat. The cutter in step 3 stops when the flat end face just disappears at the toe, so it takes almost nothing off the length [J]; this answers the usual complaint that a domed fret cannot be measured.
2. Nip the tang back 0.075 at each end and file the underside of the overhang flat.
3. Dome the ends. Hold the fret upright in a kerfed block (the kerf takes the tang) with about 0.06 of crown standing out. Clamp a brass backer against the flat underside of the crown so the cutter sees a full circle instead of a half one. Bring a cup cutter down on the end in a drill press, with oil, to a depth stop. Cup cutter: carbide or diamond, inner diameter 2.0 to 2.1 mm, centred on the crown about 0.002 above its base so the cup just swallows the 0.043 × 0.080 section [J]. Carbide cup burs are sold in this size range [S]; whether a given brand's cup is truly spherical is not confirmed [S], which is the first thing the test piece settles.
4. Polish each end on a felt bob with compound, 400 grit rubber point first if the cutter leaves lines [J].
5. Fit. Glue as SPEC (medium cyanoacrylate in the slot and under the two overhangs). Set the treble toe with a 0.010 step gauge held against the board side, so any length error lands on the bass side. Press. Clean the crease with a sharpened brass scraper before the glue hardens.
6. Kiss-level, crown and polish as usual. The domes are below the levelling plane except at their very top.

Tools: drill press, one kerfed block with a brass backer and stop (one to two hours to make, once [J]), cup cutters (a few; life on stainless is unknown [J]), tang nipper, 0.010 step gauge. A diamond fret-end wheel made for the same job costs about $180 to $240 and is reported at under a minute per end on nickel [S]; untested on stainless.

Time: about 3 to 4 minutes per end including polish, 44 ends, so 2.5 to 3 hours [J]. v4 already allows 2 to 2.5 hours for shaping ends off the neck [S], so this is about half an hour to an hour more, plus the jig.

Refret: same as v4. New frets are cut from the cut list and domed in the same jig. The wood under the ends is plain board, nothing to rebuild.

Humidity: with the steel 0.010 inside the wood, a quartersawn board would have to lose about 10 % moisture content before a fret end reached the side (0.001 per side per 1 % [C], from published shrinkage figures [S]). A flat-sawn board moves 2.2 times as much [C]: the board must be quartersawn.

## 5. The simpler fallback

**Same wood, same slots, same lengths rule, but the end is a three-quarter dome filed by hand: 0.034 long, steel starting 0.016 in from the side, full height at 0.049.** Crown length = board width minus 0.032. Tool: a concave fret-end file (0.080 groove) and a jig block, ends still shaped before fitting.

In the model it is within noise of the sphere: 2 % better to 5 % worse across five positions and 8 % better with the thumb wrapped over [C]. Same bending room [C]. Its sharpest steel radius is 0.028 against 0.037 [C].

Why it is the fallback and not the recommendation: the shape depends on the hand holding the file 44 times, where the cup cutter makes the same sphere every time [J]; and it is not quite the hemisphere that was asked for. If the cup cutter does not survive stainless on the test piece, build this and lose nothing a finger is likely to notice [J].

## 6. Bending room

String centre at rest to the start of the full-height fret, in inches [C]. The outer strings on this neck sit 0.155, 0.141 and 0.135 from the board side at frets 1, 12 and 21; on a 1.65-nut vintage neck 0.136, 0.122 and 0.116 [C]. Chart: [fig/bending_room.png](fig/bending_room.png).

| End | F1 high E | F1 low E | F12 high E | F12 low E | F21 high E | F21 low E |
|---|---|---|---|---|---|---|
| Vintage bevel on a vintage-width neck | 0.106 | 0.106 | 0.092 | 0.092 | 0.086 | 0.086 |
| v4: 72° face | 0.107 | 0.097 | 0.094 | 0.084 | 0.087 | 0.077 |
| **Recommended: quarter-sphere, toe 0.010** | **0.105** | **0.105** | **0.092** | **0.092** | **0.086** | **0.086** |
| Fallback: filed dome 0.034, toe 0.016 | 0.105 | 0.105 | 0.092 | 0.092 | 0.086 | 0.086 |
| Short dome 0.026, toe 0.024 | 0.105 | 0.105 | 0.092 | 0.092 | 0.085 | 0.085 |
| Quarter-sphere set in 0.006 more | 0.099 | 0.099 | 0.086 | 0.086 | 0.080 | 0.080 |
| Rosewood pocket (rejected) | 0.101 | 0.101 | 0.088 | 0.088 | 0.082 | 0.082 |
| Long dome 0.052 | 0.094 | 0.094 | 0.080 | 0.080 | 0.074 | 0.074 |
| Dome set inboard on a uniform roll | 0.063 | 0.040 | 0.050 | 0.027 | 0.043 | 0.020 |

Two looser measures for the main four, because a string does not fall off the instant the crown starts to curve:

| End | Measure | F1 high E | F1 low E | F12 high E | F12 low E | F21 high E | F21 low E |
|---|---|---|---|---|---|---|---|
| Vintage | within 0.005 of full height | 0.109 | 0.109 | 0.096 | 0.096 | 0.089 | 0.089 |
| Vintage | crown slope under 10° | 0.103 | 0.103 | 0.089 | 0.089 | 0.083 | 0.083 |
| v4 | within 0.005 of full height | 0.119 | 0.111 | 0.105 | 0.097 | 0.099 | 0.091 |
| v4 | crown slope under 10° | 0.109 | 0.100 | 0.096 | 0.087 | 0.089 | 0.081 |
| **Recommended** | within 0.005 of full height | 0.123 | 0.123 | 0.110 | 0.110 | 0.104 | 0.104 |
| **Recommended** | crown slope under 10° | 0.111 | 0.111 | 0.097 | 0.097 | 0.091 | 0.091 |
| Fallback | within 0.005 of full height | 0.120 | 0.120 | 0.107 | 0.107 | 0.101 | 0.101 |
| Fallback | crown slope under 10° | 0.109 | 0.109 | 0.096 | 0.096 | 0.089 | 0.089 |

Reading it:

- The proposal equals a vintage neck on the strict measure and beats it by 0.008 to 0.015 on the two looser ones, because a sphere gains height faster than a 35° bevel [C].
- Against v4 it gives up 0.002 at the high E and gains 0.008 at the low E. v4 had given the bass side away by choice; the proposal makes the two sides equal.

**The trade on offer.** A softer end than the sphere exists only by giving up fret [C]. Chart: [fig/trade_softness_vs_room.png](fig/trade_softness_vs_room.png).

| Change | Bending room given up per side | Hardest spot, compared with the same sphere at 0.010 |
|---|---|---|
| Sphere set in 0.006 more | 0.006 | 0 to 6 % lower |
| Long dome, 0.052 | 0.012 | 5 to 7 % lower in four positions, level in two |
| Dome set inboard on a uniform roll | 0.042 treble, 0.065 bass | 3 to 37 % lower in five positions, 9 % higher landing on a fret end |

My recommendation is no trade [J]: the first two buy little, and the third costs most of the bending room at the low E. If you want one, the only one worth having is the bass side set in 0.006 more: low E room at fret 12 becomes 0.086, still more than v4's 0.084, for about 6 % under the wrapped thumb and from the side, and nothing elsewhere [C].

## 7. The whole edge

Renders from the player's eye, the side and above: [frets 1-2 treble](fig/render_treble_frets_1-2.png), [frets 12-13 treble](fig/render_treble_frets_12-13.png), [frets 1-2 bass](fig/render_bass_frets_1-2.png), [frets 12-13 bass](fig/render_bass_frets_12-13.png); close-ups [treble fret 1](fig/render_treble_fret_1_macro.png), [treble fret 12](fig/render_treble_fret_12_macro.png), [bass fret 1](fig/render_bass_fret_1_macro.png), [bass fret 12](fig/render_bass_fret_12_macro.png). Edge line chart: [fig/edge_line.png](fig/edge_line.png).

The fret end, the roll, the scallop and the maple line are treated as one surface:

- **Fret end and roll.** The roll is widest and deepest between frets and closes to a 0.010 nose at each fret, so the steel sits on full-height wood right out to 0.010 from the side.
- **Scallop.** In v4 the scallop runs out through the side of the board, so the side line dips in every fret space. In the proposal the scallop is full depth out to 0.140 from the side and then rises to nothing at the side. Under both outer strings it is unchanged [C]. At 0.09 outboard of the high E it is 0.021 shallower at fret 12, and the floor there is still 0.032 below a plain board, 0.075 below the fret tops [C].
- **Maple line.** Straight, unchanged. The roll never comes closer than 0.030 to the glue line [C].

**The wave SPEC section 5 admits to.** SPEC gives 0.04 to 0.05 of rise and fall per fret space at 45°. Computed here [C]:

| Wood wave per fret space, treble / bass | 15° (hand low) | 30° | 45° | 60° |
|---|---|---|---|---|
| v4 | 0.013 / 0.010 | 0.036 / 0.029 | 0.052 / 0.041 | 0.059 / 0.043 |
| Proposed | 0.017 / 0.018 | 0.026 / 0.028 | 0.032 / 0.033 | 0.034 / 0.033 |
| Proposed with a tighter roll (0.045 / 0.060 between frets) | 0.014 / 0.015 | 0.020 / 0.022 | 0.025 / 0.025 | 0.027 / 0.024 |

So the design cuts the wave by about a third at 45° on the treble side and a fifth on the bass side. With the hand very low it is slightly larger than v4, because the roll now rises to each fret.

**Should you want less wave?** In my judgment, partly [J]:

- The part that came from the scallop running out through the side: yes, lose it. It is outboard of the strings, so it does nothing for bending, and a wavy side line is the one thing here that does not read as a vintage neck. The proposal removes it.
- The part that comes from the roll breathing: keep it. It is the price of a soft edge between frets with full-width frets. A uniform roll removes it only by pulling the frets inboard (the last row of the bending table) or by giving up the soft edge.
- One choice left to you: the tighter roll in the table's last row lowers the wave to 0.025 and the finger's rise and fall by a further 5 to 23 % [C], but the rolled edge between frets is then 0.045 wide instead of 0.062 on the treble side and 0.060 instead of 0.085 on the bass side. Softer travel along the neck against a softer edge to rest on. I would keep the wider roll [J].

## 8. Ideas considered and rejected

| Idea | What it was | Why it is out |
|---|---|---|
| Rosewood pocket or bolster | Leave a raised cheek of rosewood around each fret end so the steel nests into wood | The underside of the crown is flat at board level, so wood that continues up around it must either thin to a feather edge or stop at a socket wall. The socket needs a cutter far smaller than the 1/4 ball nose (0.011 left uncut [C]) and a clearance gap for humidity, which is a dirt crevice or a filler joint. Refrets get harder. And it feels worse from the side: 6.5 × flat, on the wood, against 4.3 for the same sphere without the bolster [C]. |
| Ends hidden behind an added edge strip (binding-style) | Hide the steel behind wood | Needs a glue line or filler at every fret, the kind of joint an earlier version was withdrawn for, and it changes the look of a plain rosewood edge [J]. Not modelled. |
| Dome set inboard on a uniform roll | Best feel of everything tested | Costs 0.042 of fret at the high E and 0.065 at the low E [C]. Strings come off. |
| Long dome, 0.052 | Gentler than a sphere | Costs 0.012 of fret for 5 to 7 % in four positions and nothing in two [C]. Not worth it. |
| Short dome, 0.026 | Easier to file | 8 to 15 % harder than the sphere in five positions [C], with no gain in bending room at the toe position tested (0.024). |
| Longer full-height wood nose (0.045 each side of the fret) | More wood around the toe | From the side the hardest spot moves to the wood and rises by a third, 5.7 against 4.3 [C]. The wave grows too. |
| Sphere with no change to the scallop | Keep v4's run-out | Wave stays at 0.050 / 0.040 and rise and fall stays at v4's level [C]. The dished run-out is what makes the edge calmer; the hardest spot barely changes (1 to 3 %) [C]. |
| v4's 72° face | The current spec | Buildable, and its bending-room reasoning was sound, but it is harder under the finger in five of six positions, has a 0.007 ridge, and puts its seam on a slope where movement shows. |

## 9. Risks

1. **Cutter on stainless.** Stainless fret wire is about half again as hard as nickel silver [S]. Cup cutter life, chatter and finish on it are unknown [J]. The fallback exists for this.
2. **Cutter shape.** Some cup burs are conical inside, not spherical [S]. Check the first dome under a loupe against a 2 mm radius gauge.
3. **Length and line-up.** Repairers report that ends shaped off the instrument rarely line up when sighted down the neck [S]. Here the toes are gauged off a CNC-straight board side on the treble edge, and nothing is flush, so ±0.006 is tolerable [J]. On the bass edge the toe line may wander by that much; a close look could see it [J].
4. **The feel figures are computed.** The size of the gain is a model result with a judged finger stiffness. The ranking is likely right; the percentages are not promises.
5. **The look from the side.** The lower edge of the roll now arches up to each fret end instead of following v4's straight line. It is a soft shading change, not a line, but it is new. Judge it on the renders and on the test piece.
6. **The crease.** A crease at each toe can hold glue and dirt. Clean at fitting; it is reachable with a toothpick.
7. **The wood nose** is a 0.010 radius in rosewood. It is a rounded corner, not an edge, and should wear like any rolled board edge [J], but it is the detail the wrapped thumb finds first.
8. **Refret discipline.** Every refret needs the cut list and the jig. Keep both with the guitar's papers.

## 10. The one test piece

One offcut of the board stock glued to maple, machined as fret spaces 11 to 13 of the real program (four fret positions, both edges, about 3 inches long).

- Fret positions: two cup-cut spheres, one hand-filed fallback dome, one v4 72° face made as SPEC describes.
- Edges: one fret space with the dished run-out, one with v4's run-out through the side.

Pass marks:

| Check | Pass |
|---|---|
| Cup cutter | at least 10 stainless ends from one cutter, under 3 minutes each before polish |
| Dome | radius 0.040 ± 0.003, no flat, no line where the dome meets the crown after polish |
| Placement | toe 0.010 ± 0.004 from the side on the gauged edge |
| Seat | a 0.0015 feeler does not enter under any fret end |
| Feel | owner slides index side, fingertip and thumb past all four ends, eyes shut, and ranks them |
| String hold | a plain string held 0.141 from the side at the fret-12 position and pushed toward the edge stays on the crown as far as it does on a vintage neck (0.092) |
| Movement | one dry and one damp week (about ±2 % moisture); re-feel every seam |

If the spheres pass, build the recommendation. If the cutter fails but the filed dome passes, build the fallback. If your hand prefers v4's face, v4 stands and this proposal is withdrawn.

## 11. Changes SPEC.md would need

Not applied. Listed against the current text.

**Section 1, table**

- Row "Scallops": after "half that depth at the bass edge" add "measured 0.140 in from the side; from there the depth eases to nothing at both sides".
- Row "Board edge": replace with "roll starts 0.110 below the corner between frets and rises to 0.010 below it at each fret; on top it is 0.010 wide at each fret and 0.062 between (treble), 0.010 and 0.085 (bass)".
- Row "Fret ends": replace with "steel starts 0.010 in from the side on both edges; quarter-sphere end, radius 0.040, full height 0.049 from the side; cut with a cup cutter before fitting".
- Row "Frets": no change.

**Section 1, build order**

- Step 5: no change to the wording; the program cuts the new edge and run-out.
- Step 7: replace "break the faint line where the roll meets the board top beside each fret; nothing else on the board needs shaping" with "wipe the roll with 600 grit; nothing on the board needs shaping".
- Step 8: replace "nip the tang back 0.065 each end, shape both ends on a jig before fitting" with "nip the tang back 0.075 each end, dome both ends with a cup cutter in the drill-press jig before fitting".

**Section 4, scallops**

- Add the run-out rule: depth × (1 − ((0.140 − s) / 0.140)²) within 0.140 of either side.

**Section 5, board and edge**

- Edge construction table: "at a fret" becomes 0.010 treble and 0.010 bass, with a roll depth of 0.010; "between" stays 0.062 and 0.085 with depth 0.110. Add the blend rule from section 4 of this document.
- Replace "starts on a straight line 0.110 below the nominal board corner" with "starts 0.110 below the corner between frets and arches up to 0.010 below it at each fret".
- Test table and verdict: replace "From 45 degrees up they stand 0.011 to 0.014 proud" with "they stand 0.007 proud at 30°, 0.017 at 45° and 0.027 at 60°", and add the contact results from section 3 of this document as the governing measure.
- Replace "rises and falls 0.04 to 0.05 per cell at 45 degrees. Roughly half of that belongs to the roll breathing; the rest is the scallop running out through the edge." with "rises and falls 0.032 to 0.033 per cell at 45 degrees. All of it belongs to the roll breathing; the scallop no longer runs out through the edge."
- "Ceiling" paragraph: keep the first two sentences. Replace "v4 sits at the point where further rounding starts costing string margin" with "a quarter-sphere of radius 0.040 starting 0.010 from the side is the roundest end that keeps vintage string margin".
- Slip-off margins table: replace the v4 columns with the recommended row of section 6 (0.105, 0.092, 0.086 on both sides). Delete "Bass gives up 0.0085 of full-height fret by choice".
- The bullet beginning "Right: the steel can come within 0.015 of the side" ("the steel can come within 0.015 of the side ... the wood corner at the fret is 108 degrees and the steel toe 72 degrees"): replace with "the steel comes within 0.010 of the side as a quarter-sphere; no feather edges: the steel toe is vertical and the wood beside it is a 0.010 radius".

**Section 6, fret ends**

- Shape table: steel begins 0.010 (both); full height 0.049 (both); "72°" and "ridge 0.015" replaced by "quarter-sphere, radius 0.040"; crown length W − 0.020; tang length W − 0.170.
- Delete the paragraph "A simpler end, same feel. ... The plan-view rounding of a hemisphere does no work here ..." and replace it with the verdict in section 1 of this document.
- Order of work: step 2 nip 0.075 both sides; step 3 "cup cutter, 2.0 to 2.1 mm, in a drill press with the fret upright in a kerfed block and a brass backer; polish"; step 4 "treble toe set with a 0.010 step gauge against the board side. Placement tolerance 0.004"; step 5 delete (no blending on the neck).
- Cost: replace with "3 to 4 minutes per end, 44 ends, 2.5 to 3 hours on top of a normal stainless fret job, plus one to two hours once for the jig".
- Glue: replace "With the steel 0.015 inside the wood, the board would have to shrink 1.4 %" with "With the steel 0.010 inside the wood, the board would have to shrink 1.0 %". Add "the board must be quartersawn".

**Section 11, buildability gate**

- Row "Edge roll": replace "none, 108 degree wood corner" with "none, 0.010 radius nose at each fret".
- Row "Fret ends": replace "steel toe 72 degrees" with "quarter-sphere 0.040, vertical toe" and "disc sander, diamond files" with "cup cutter in a drill-press jig".
- Delete "The one hand operation on the board is breaking the faint line where the roll meets the top beside each fret".

**Section 12, owner decisions**

- Row 2 stays (breathing roll).
- Add: "Fret end: quarter-sphere by cup cutter, or the hand-filed dome, or v4's 72° face. | quarter-sphere, decided on the test piece".
- Add: "Scallop at the edge: dished run-out, or through the side as v4. | dished".
- Add: "Roll between frets: 0.062 / 0.085, or tighter 0.045 / 0.060 for a calmer edge line. | 0.062 / 0.085".
- Add: "Bass side: sphere at 0.010 from the side, or set in 0.006 more for the wrapped thumb. | 0.010".

neck_v4.py would need the matching changes to its edge and scallop functions; fe_model.py here holds the working formulas.

### Cut list for the recommended end [C]

Crown = board width − 0.020. Tang = board width − 0.170. For the fallback, crown = board width − 0.032 and the tang is the same.

| Fret | Board width | Crown length | Tang length |
|---|---|---|---|
| 1 | 1.7314 | 1.7114 | 1.5614 |
| 2 | 1.7729 | 1.7529 | 1.6029 |
| 3 | 1.8120 | 1.7920 | 1.6420 |
| 4 | 1.8490 | 1.8290 | 1.6790 |
| 5 | 1.8838 | 1.8638 | 1.7138 |
| 6 | 1.9167 | 1.8967 | 1.7467 |
| 7 | 1.9478 | 1.9278 | 1.7778 |
| 8 | 1.9771 | 1.9571 | 1.8071 |
| 9 | 2.0048 | 1.9848 | 1.8348 |
| 10 | 2.0309 | 2.0109 | 1.8609 |
| 11 | 2.0556 | 2.0356 | 1.8856 |
| 12 | 2.0788 | 2.0588 | 1.9088 |
| 13 | 2.1008 | 2.0808 | 1.9308 |
| 14 | 2.1215 | 2.1015 | 1.9515 |
| 15 | 2.1411 | 2.1211 | 1.9711 |
| 16 | 2.1596 | 2.1396 | 1.9896 |
| 17 | 2.1770 | 2.1570 | 2.0070 |
| 18 | 2.1935 | 2.1735 | 2.0235 |
| 19 | 2.2090 | 2.1890 | 2.0390 |
| 20 | 2.2237 | 2.2037 | 2.0537 |
| 21 | 2.2375 | 2.2175 | 2.0675 |
| 22 | 2.2506 | 2.2306 | 2.0806 |

## 12. Files in this folder

| File | What it is |
|---|---|
| fret-ends-summary.png | one-page summary |
| fig/render_*.png | eight shaded sheets: vintage, v4 and the proposal, each from the player's eye, the side and above |
| fig/sections_treble_fret_12.png, fig/sections_bass_fret_1.png | true-scale sections along and across the fret, and plan |
| fig/feel_fret_12.png, fig/feel_fret_2.png | contact results |
| fig/pressure_maps.png | where the pressure sits under the finger |
| fig/bending_room.png, fig/trade_softness_vs_room.png | bending room and the trade |
| fig/edge_line.png | the edge wave |
| fe_model.py | every candidate's surface; writes geometry.json |
| fe_contact.py | the finger contact model; writes feel.json and feel_maps.npz |
| fe_render.py, fe_fig.py | renders and figures |
| SURVEY.md | the earlier survey (not changed) |

The renders and sections are drawn from the same surfaces the numbers come from. Each fret is a separate solid resting on the wood, so anything floating or cutting through would show; all sheets were inspected and none does.
