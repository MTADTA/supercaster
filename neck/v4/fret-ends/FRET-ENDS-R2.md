# Supercaster II fret ends, round 2: the end that blends into the wood

Status: proposal for the owner to choose from. Nothing in SPEC.md, neck_v4.py, SURVEY.md or the round-1 files has been changed.
All dimensions in inches. Every number is marked **[C]** computed by the scripts in this folder, **[S]** sourced, or **[J]** judgment.

Summary sheet: [fret-ends-r2-summary.png](fret-ends-r2-summary.png)

## 1. Verdict

**Pick: the flow end, candidate (c).** It is new in this round. The board edge gets one small even roll, the same at a fret and between frets. At each fret a straight line leaves that roll without a kink, wood first and then steel, and turns over into the fret top. Seen from above the end is rounded like a fingertip. Between frets the edge stays level, because the scallop now starts inboard of the edge instead of running out through it.

How long that line is sets how soft the end feels and how much bending room it costs. That is one dial, and it is the owner's:

| Setting | Bending room given up against a vintage neck [C] | Full-height fret left outside the string, frets 1 / 12 / 21 [C] | Hardest spot, index finger sliding at 45°, fret 12 [C] | Steel proud of the wood at 45° [C] |
|---|---|---|---|---|
| Vintage 35° bevel, for reference | none | 0.106 / 0.092 / 0.086 | 9.11 | 0.016 |
| Round-1 quarter-sphere, for reference | none | 0.105 / 0.092 / 0.086 | 5.29 | 0.017 |
| (b) Stretched dome | none | 0.107 / 0.094 / 0.087 | 5.31 | 0.017 |
| (c) Flow end, short | 0.012 at every fret | 0.094 / 0.081 / 0.074 | 4.88 | 0.013 |
| (c) Flow end, graded | 0.030 at fret 1, 0.008 at fret 12, none at fret 21 | 0.075 / 0.084 / 0.087 | 4.29 at fret 2, 4.92 at fret 12, 5.24 at fret 20 | 0.005 at the nut, 0.014 mid-neck, 0.017 at the body |
| **(c) Flow end, long** | **0.030 at every fret** | **0.075 / 0.062 / 0.055** | **4.19** | **0.005** |

"Hardest spot" is the peak pressure under the skin as a multiple of a flat board; lower is softer.

**The best-feeling end is the long flow end.** It is the softest in five of the six hand positions at every fret checked (in the sixth, a fingertip landing on a fret end, only the wrap-over is softer, 3.30 against 3.41), it has the least catch of any end here and the least rise and fall of the new ends, and apart from the wrap-over it is the only end where the steel is nearly flush for a hand at 45° (0.005 proud against 0.016 for a vintage bevel). **It costs exactly 0.030 of bending room at every fret**: at fret 12 the high E has 0.062 of full-height fret outside it instead of 0.092, and at fret 21 it has 0.055 instead of 0.086 [C]. That is a third of the reserve. Whether a hard bender can live with it is the owner's call, and section 7 gives what I can say about it.

One fact should steer the order of work: **a short end can be filed into a long one later; a long one can never be made short again** (the long shape lies entirely inside the short one [C], section 9). So if the owner is unsure, build graded or short, play it, and lengthen the ends by hand if more softness is wanted.

**The wrap-over (a) is not worth building.** It was modelled as asked. Its outer surface is the same line as the long flow end, so when everything is flush it feels the same as that shape without the leg, to two decimals [C]. It gains nothing when the board dries, gets clearly worse when the board swells, needs 44 pockets no ball-nose cutter can reach, and has a thin glued steel tab ending at the board side where the hand slides. Section 10.

**What only the owner can settle**

1. How much bending room to trade: none (b), 0.012 (short), graded, or 0.030 (long).
2. The level rail at the edge. It is what stops the rise and fall when sliding, and it changes the v4 scallop: the scallop starts 0.040 in from the side and reaches full depth 0.140 in, under the outer strings, instead of running out through the edge. Section 11.
3. The smaller, even roll: a plain quarter round of 0.040 radius (0.030 for the dome) in place of v4's breathing roll (0.048 to 0.085 wide, 0.110 tall). From the side the board looks more like a plain vintage board edge.
4. The look. From above, these ends are rounded like a fingertip instead of cut square like a vintage bevel. Close-ups in [fig/r2_render_treble_fret_12_macro.png](fig/r2_render_treble_fret_12_macro.png).
5. A test piece before the real board (section 14).

**Does the pick give one continuous playing surface?** Along the edge, mostly yes. A hand lower than 40° above side-on (long end) touches wood only, and that wood is level to 0.001 from fret to fret [C]. At 45° the long end leaves a bump 0.005 high at each fret, against 0.016 on a vintage neck. On top of the board, no: a fingertip running along the high E still crosses 21 frets standing 0.043 above scalloped wood. No fret end changes that.

## 2. Was round 1 wrong?

Partly. Round 1 said no fret end can be flush with the wood and keep vintage bending room. That holds, but the reason I gave (the steel must end in a wall above the board) was too narrow, and the round-1 design made things worse than they had to be.

What the computation shows this round [C]:

- **The rise and fall came from the wood, not the steel.** Round 1 and v4 both had a roll that grows between frets and a scallop that runs out through the edge. Sliding along that edge at 45°, the finger rose and fell 0.026 (round 1) and 0.036 (v4) at fret 12. With an even roll and a level rail the same slide rises and falls 0.006 to 0.008, the same as a vintage edge (0.007). Same steel shape, dished run-out instead of the rail: 0.015.
- **The catch came from the same place.** Catch at 45°: round-1 sphere 9.4°, v4 12.4°, vintage 4.1°, the new ends 2.1° to 3.3°.
- **With the steel leaving the roll in one line, the end is flush for any hand lower than (90° minus the line's angle).** That is 25° for the dome, 30° for the short flow end, 40° for the long one. Round 1's sphere stood 0.004 proud even at 20°.
- **At vintage bending room the hardest spot is no better than the round-1 sphere.** The stretched dome scores 5.31 against the sphere's 5.29 (index finger at 45°). To get softer than that the line has to get longer, and a longer line starts further inboard. Across 25 rounded variants the trade is steady: about 5.3 at no cost, 4.9 for 0.012, 4.2 for 0.030 ([fig/r2_trade.png](fig/r2_trade.png)).
- **Truly flush at 45° needs a 45° line**, which costs 0.032 (variant og45: steel 0.000 proud at 45°, hardest spot 4.38, room at fret 12 0.060). The long flow end at 50° with a bigger top radius is softer (4.19) and costs slightly less (0.030), so I carried that one forward.

So the corrected statement is: an end can be flush and continuous for a low hand at vintage bending room; an end that is also soft and nearly flush at 45° costs about 0.030.

## 3. The candidates

Sections to scale: [fig/r2_sections_treble_fret_12.png](fig/r2_sections_treble_fret_12.png), [fig/r2_sections_bass_fret_1.png](fig/r2_sections_bass_fret_1.png).
Renders: [fig/r2_render_treble_frets_12-13.png](fig/r2_render_treble_frets_12-13.png), [fig/r2_render_treble_fret_12_macro.png](fig/r2_render_treble_fret_12_macro.png), [fig/r2_render_bass_fret_1_macro.png](fig/r2_render_bass_fret_1_macro.png), [fig/r2_render_graded.png](fig/r2_render_graded.png).

Three references, unchanged from round 1: the vintage 35° bevel on a plain board, v4's 72° face, and round 1's quarter-sphere.

The new ends share one construction. On the fret's centreline: (1) a quarter-round roll of radius r at the board edge; (2) a straight line leaving the roll at the blend angle, wood up to the board surface and steel above it; (3) an arc of the top radius turning over to the level fret top. Across the fret, the crown narrows toward the tip as the square root of its height, so the outline from above is a parabola with a round tip.

All values at fret 12, treble side [C] unless marked. The shapes are the same on both edges.

| | (a) Wrap-over | (b) Stretched dome | (c) Short | (c) Long | (c) Graded, fret 1 / 12 / 21 |
|---|---|---|---|---|---|
| Edge roll radius [J] | 0.040 | 0.030 | 0.040 | 0.040 | 0.040 / 0.033 / 0.030 |
| Blend angle from level [J] | 50° | 65° | 60° | 50° | 50° / 60° / 65° |
| Top radius [J] | 0.040 | 0.025 | 0.030 | 0.040 | 0.040 / 0.030 / 0.025 |
| Steel starts, from the board side | 0.001 (leg) | 0.011 | 0.018 | 0.023 | 0.023 / 0.015 / 0.012 |
| Wood under the line, above the roll | none | 0.006 high | 0.007 | 0.004 | 0.004 / 0.006 / 0.006 |
| Length of the steel line | 0.042 + 0.039 leg | 0.032 | 0.034 | 0.042 | 0.041 / 0.034 / 0.033 |
| Full height from, from the board side | 0.080 | 0.048 | 0.061 | 0.080 | 0.080 / 0.058 / 0.049 |
| Steel hidden from a hand lower than | 40° | 25° | 30° | 40° | 40° / 30° / 25° |
| Crown overhang past the tang end | 0.062 | 0.074 | 0.067 | 0.062 | 0.062 / 0.070 / 0.073 |
| Sharpest radius on the steel | 0.006 | 0.016 | 0.020 | 0.017 | 0.020 |
| Sharpest radius on the wood | 0.007 | 0.008 | 0.009 | 0.011 | 0.009 |
| Gap under the crown | 0 | 0 | 0 | 0 | 0 |
| Left uncut by a 1/8 ball-nose | 0.014 (the pocket) | 0.0003 | 0.0003 | 0.0002 | 0.0004 |

For comparison the vintage bevel's sharpest steel radius is 0.001 and v4's wood has a 0.001 crease [C].

Notes on each:

- **(a) Wrap-over.** The long flow line, but the steel carries on down the roll as a leg 0.014 thick let into a pocket, ending 0.001 from the board side. To turn over the edge the crown has to keep nearly its full width, so its end is less rounded from above than (c). "A_twin" in the data is this same shape without the leg, used to isolate what the leg does.
- **(b) Stretched dome.** v4's flowing line with the cross-section rounded, on a 0.030 roll, at vintage bending room. The brief asked for the seam tucked below the wood line; I tested tuck as a board-swell case instead of building it in (section 8), because tuck is set by the humidity at which the ends are dressed.
- **(c) Flow end.** Same construction as (b), with the line lowered and lengthened. Short and long are two points on the dial; graded runs from long at fret 1 to the dome at fret 21, changing a little at every fret.

The steel's edge where it meets the wood is a wedge of 43° (long) to 58° (dome) between the fret's underside and its face [C]. A vintage bevel's is about 50°. None of these is a feather edge.

## 4. Feel: hardest spot under the skin

Computed with the round-1 contact model (soft finger on a rigid neck). Units: times the pressure on a flat board. "w" means the hardest spot is on wood, not steel. Chart: [fig/r2_feel.png](fig/r2_feel.png).

Hand positions [J]: index finger side sliding with the hand low (20° above side-on); index finger side sliding at 45°; fingertip sliding along the high E; fingertip landing on a fret end; thumb sliding on the bass edge at 45°; thumb wrapped over and gripping.

**Fret 2** [C]

| | Index, low | Index, 45° | Tip sliding | Tip landing | Thumb, 45° | Thumb over |
|---|---|---|---|---|---|---|
| Vintage 35° bevel | 8.30 | 9.15 | 5.69 | 5.07 | 8.89 | 7.48 |
| v4 72° face | 7.31 w | 6.92 | 4.25 | 4.34 w | 6.38 | 5.34 |
| Round-1 quarter-sphere | 4.16 | 5.30 | 3.50 | 3.58 | 5.33 | 5.36 w |
| (a) Wrap-over | 3.63 | 5.51 | 3.55 | 3.31 | 5.27 | 4.67 |
| (b) Stretched dome | 3.88 | 5.31 | 3.58 | 3.89 | 5.20 | 4.56 |
| (c) Flow, short | 3.14 w | 4.90 | 3.41 | 3.67 | 4.77 | 4.33 |
| (c) Flow, long | 3.09 w | 4.20 | 3.14 | 3.41 | 4.04 | 4.01 |
| (c) Flow, graded | 3.11 w | 4.29 | 3.18 | 3.44 | 4.13 | 4.04 |

**Fret 12** [C]

| | Index, low | Index, 45° | Tip sliding | Tip landing | Thumb, 45° | Thumb over |
|---|---|---|---|---|---|---|
| Vintage 35° bevel | 8.30 | 9.11 | 5.67 | 5.03 | 8.85 | 7.42 |
| v4 72° face | 7.90 w | 6.95 | 4.27 | 4.42 w | 6.42 | 5.39 |
| Round-1 quarter-sphere | 4.14 | 5.29 | 3.50 | 3.56 | 5.32 | 5.38 w |
| (a) Wrap-over | 3.61 | 5.47 | 3.54 | 3.30 | 5.24 | 4.66 |
| (b) Stretched dome | 3.86 | 5.31 | 3.57 | 3.86 | 5.19 | 4.56 |
| (c) Flow, short | 3.13 w | 4.88 | 3.40 | 3.65 | 4.76 | 4.33 |
| (c) Flow, long | 3.11 w | 4.19 | 3.13 | 3.41 | 4.02 | 4.00 |
| (c) Flow, graded | 3.28 w | 4.92 | 3.41 | 3.65 | 4.80 | 4.33 |

**Fret 20** [C]

| | Index, low | Index, 45° | Tip sliding | Tip landing | Thumb, 45° | Thumb over |
|---|---|---|---|---|---|---|
| Vintage 35° bevel | 8.38 | 9.14 | 5.67 | 5.06 | 8.87 | 7.42 |
| v4 72° face | 7.57 w | 7.58 | 4.42 | 4.35 w | 6.91 | 5.41 |
| Round-1 quarter-sphere | 4.13 | 5.29 | 3.50 | 3.56 | 5.32 | 5.28 w |
| (a) Wrap-over | 3.68 w | 5.47 | 3.53 | 3.30 | 5.23 | 4.65 |
| (b) Stretched dome | 3.87 | 5.29 | 3.57 | 3.86 | 5.18 | 4.56 |
| (c) Flow, short | 3.13 w | 4.88 | 3.40 | 3.65 | 4.75 | 4.32 |
| (c) Flow, long | 3.09 w | 4.18 | 3.13 | 3.40 | 4.02 | 4.00 |
| (c) Flow, graded | 3.74 | 5.24 | 3.54 | 3.82 | 5.12 | 4.51 |

Reading it:

- Every new end is less than half as hard as a vintage bevel when the hand is on the edge.
- With the hand low, the flow ends put the hardest spot on wood (about 3.1). The steel alone would be 2.1 for the long end at fret 12 [C]: the hand barely finds it.
- The long flow end is softest everywhere except a fingertip landing square on a fret end, where the wrap-over's wider end scores 3.30 against 3.41.
- The wrap-over is harder than the long flow end at 45° (5.47 against 4.19) although the line is the same, because its end is not rounded from above. Rounding from above is the biggest single softening step found this round: for the same 50° line, a square-cut end scores 6.07, a square end with rounded corners 5.46, a rounded one 4.73 [C].

## 5. Sliding: catch, and rise and fall

Chart: [fig/r2_slide.png](fig/r2_slide.png). The edge as a flat hand meets it, frets 9 to 15: [fig/r2_edge_line.png](fig/r2_edge_line.png).

**Catch**: the steepest push back along the neck as the finger passes a fret, in degrees [C].

Fret 2

| | Index, low | Index, 45° | Tip sliding | Tip landing | Thumb, 45° | Thumb over |
|---|---|---|---|---|---|---|
| Vintage 35° bevel | 2.6 | 4.1 | 7.3 | 9.6 | 3.4 | 3.6 |
| v4 72° face | 5.0 | 10.1 | 13.8 | 15.2 | 7.9 | 7.2 |
| Round-1 quarter-sphere | 4.6 | 8.5 | 12.1 | 14.2 | 7.8 | 7.0 |
| (a) Wrap-over | 0.6 | 2.7 | 6.2 | 10.0 | 2.1 | 4.2 |
| (b) Stretched dome | 1.0 | 3.3 | 7.1 | 10.7 | 2.5 | 4.5 |
| (c) Flow, short | 0.7 | 2.8 | 6.5 | 10.2 | 2.1 | 4.3 |
| (c) Flow, long | 0.3 | 2.0 | 5.6 | 9.4 | 1.5 | 4.0 |
| (c) Flow, graded | 0.3 | 2.1 | 5.7 | 9.6 | 1.6 | 4.0 |

Fret 12

| | Index, low | Index, 45° | Tip sliding | Tip landing | Thumb, 45° | Thumb over |
|---|---|---|---|---|---|---|
| Vintage 35° bevel | 2.5 | 4.1 | 7.3 | 9.6 | 3.4 | 3.6 |
| v4 72° face | 6.0 | 12.4 | 17.1 | 18.5 | 9.0 | 8.4 |
| Round-1 quarter-sphere | 4.8 | 9.4 | 13.9 | 16.4 | 8.3 | 8.0 |
| (a) Wrap-over | 0.6 | 2.7 | 6.4 | 10.5 | 2.1 | 4.7 |
| (b) Stretched dome | 1.0 | 3.3 | 7.4 | 11.3 | 2.5 | 5.1 |
| (c) Flow, short | 0.7 | 2.8 | 6.8 | 10.8 | 2.1 | 4.8 |
| (c) Flow, long | 0.3 | 2.1 | 5.8 | 10.0 | 1.6 | 4.5 |
| (c) Flow, graded | 0.7 | 2.8 | 6.9 | 10.9 | 2.1 | 4.9 |

Fret 20

| | Index, low | Index, 45° | Tip sliding | Tip landing | Thumb, 45° | Thumb over |
|---|---|---|---|---|---|---|
| Vintage 35° bevel | 2.5 | 4.2 | 7.3 | 9.6 | 3.4 | 2.7 |
| v4 72° face | 5.3 | 9.4 | 13.6 | 15.6 | 6.7 | 3.9 |
| Round-1 quarter-sphere | 4.5 | 8.1 | 11.9 | 14.4 | 7.1 | 4.2 |
| (a) Wrap-over | 0.6 | 2.7 | 6.3 | 10.3 | 2.1 | 3.1 |
| (b) Stretched dome | 1.0 | 3.3 | 7.2 | 11.1 | 2.5 | 3.3 |
| (c) Flow, short | 0.7 | 2.8 | 6.7 | 10.6 | 2.2 | 3.2 |
| (c) Flow, long | 0.3 | 2.1 | 5.7 | 9.8 | 1.5 | 3.0 |
| (c) Flow, graded | 0.9 | 3.2 | 7.2 | 11.0 | 2.5 | 3.2 |

**Rise and fall**: how far the finger rides up and down passing a fret, in thousandths of an inch [C].

Fret 2

| | Index, low | Index, 45° | Tip sliding | Tip landing | Thumb, 45° | Thumb over |
|---|---|---|---|---|---|---|
| Vintage 35° bevel | 3.1 | 7.4 | 10.1 | 12.4 | 6.4 | 7.0 |
| v4 72° face | 19.0 | 33.8 | 43.0 | 45.9 | 26.2 | 24.5 |
| Round-1 quarter-sphere | 12.4 | 23.6 | 33.9 | 38.7 | 20.2 | 21.0 |
| (a) Wrap-over | 1.4 | 6.0 | 13.6 | 23.3 | 4.8 | 14.2 |
| (b) Stretched dome | 2.5 | 7.4 | 15.5 | 25.2 | 6.0 | 14.8 |
| (c) Flow, short | 2.1 | 6.6 | 14.2 | 23.9 | 5.4 | 14.4 |
| (c) Flow, long | 1.1 | 5.6 | 13.3 | 22.8 | 4.5 | 14.1 |
| (c) Flow, graded | 1.2 | 5.8 | 13.5 | 23.0 | 4.7 | 14.2 |

Fret 12

| | Index, low | Index, 45° | Tip sliding | Tip landing | Thumb, 45° | Thumb over |
|---|---|---|---|---|---|---|
| Vintage 35° bevel | 3.1 | 7.4 | 10.1 | 12.5 | 6.4 | 7.0 |
| v4 72° face | 20.4 | 35.8 | 50.1 | 54.9 | 23.4 | 20.1 |
| Round-1 quarter-sphere | 13.6 | 26.3 | 40.1 | 46.8 | 21.4 | 20.0 |
| (a) Wrap-over | 1.4 | 6.1 | 14.6 | 26.2 | 4.9 | 15.4 |
| (b) Stretched dome | 2.5 | 7.6 | 16.7 | 28.8 | 6.1 | 15.9 |
| (c) Flow, short | 2.1 | 6.7 | 15.1 | 26.9 | 5.5 | 15.5 |
| (c) Flow, long | 1.1 | 5.8 | 14.3 | 25.7 | 4.6 | 15.3 |
| (c) Flow, graded | 2.1 | 7.0 | 15.9 | 27.7 | 5.7 | 15.7 |

Fret 20

| | Index, low | Index, 45° | Tip sliding | Tip landing | Thumb, 45° | Thumb over |
|---|---|---|---|---|---|---|
| Vintage 35° bevel | 3.2 | 6.7 | 10.0 | 12.5 | 3.7 | 3.6 |
| v4 72° face | 7.8 | 12.8 | 20.8 | 24.2 | 6.4 | 5.4 |
| Round-1 quarter-sphere | 6.8 | 11.5 | 19.9 | 23.1 | 5.5 | 5.6 |
| (a) Wrap-over | 1.3 | 5.8 | 11.8 | 16.6 | 4.4 | 3.1 |
| (b) Stretched dome | 2.4 | 7.0 | 13.1 | 17.9 | 4.0 | 3.8 |
| (c) Flow, short | 2.0 | 6.2 | 12.3 | 17.1 | 4.2 | 3.5 |
| (c) Flow, long | 1.0 | 5.4 | 11.5 | 16.2 | 4.3 | 3.0 |
| (c) Flow, graded | 2.4 | 7.0 | 13.0 | 17.9 | 4.1 | 3.8 |

Reading it:

- In the three positions that slide along the edge (index low, index 45°, thumb 45°), every new end now beats a vintage edge for catch, and matches it to within 0.001 or beats it for rise and fall. Round 1's pick rose and fell 2 to 4 times as far as vintage; at frets 2 and 12 the long flow end rises and falls less than vintage.
- The two fingertip positions and the wrapped thumb still rise and fall more than vintage at frets 2 and 12 (about 0.014 to 0.029). That is not the fret end. Those hands reach inboard past the rail into the v4 scallop, which is up to 0.053 deep at fret 12. At fret 20, where the scallop is about half as deep, the wrapped thumb matches vintage (3.0 to 3.8 against 3.6) and the fingertip positions are much closer to it. Only a shallower scallop, or a wider rail on the bass side, would change the low frets. I have not computed either; they would be changes to v4's scallop, outside this brief.

## 6. Steel standing proud of the wood

How far the steel end stands above the wood beside it for a flat hand held at the given angle above side-on, treble edge, frets 9 to 16 [C].

| | 20° | 30° | 45° | 60° | 70° |
|---|---|---|---|---|---|
| Vintage 35° bevel | 0.003 | 0.004 | 0.016 | 0.029 | 0.036 |
| v4 72° face | 0.000 | 0.004 | 0.014 | 0.026 | 0.033 |
| Round-1 quarter-sphere | 0.004 | 0.007 | 0.017 | 0.027 | 0.034 |
| (a) Wrap-over | 0 | 0 | 0.004 | 0.018 | 0.029 |
| (b) Stretched dome | 0 | 0.004 | 0.017 | 0.028 | 0.035 |
| (c) Flow, short | 0 | 0 | 0.013 | 0.025 | 0.033 |
| (c) Flow, long | 0 | 0 | 0.005 | 0.020 | 0.030 |
| (c) Flow, graded, mid-neck | 0 | 0.002 | 0.014 | 0.026 | 0.034 |

How much the wood edge itself waves from fret to fret, seen at 45° [C]: vintage 0, v4 0.052 (treble) and 0.041 (bass), round 1 0.032, the new ends 0.001 to 0.003.

At 60° and above every end stands 0.02 to 0.035 proud. That hand is over the top of the board and is meeting the fret itself, which stands 0.043.

## 7. Bending room, slip and choke

Chart: [fig/r2_bending_room.png](fig/r2_bending_room.png).

The v4 board is about 0.019 wider per side than a vintage board at the same string spacing [C, from neck_v4.py]. That is why ends that start inboard can still match vintage room.

**Full-height fret outside the string at rest** [C]. Both edges are alike except v4, shown treble / bass.

| | Fret 1 | Fret 12 | Fret 21 | Given up at fret 12 |
|---|---|---|---|---|
| Vintage 35° bevel | 0.106 | 0.092 | 0.086 | none |
| v4 72° face | 0.107 / 0.097 | 0.094 / 0.084 | 0.087 / 0.077 | none / 0.009 |
| Round-1 quarter-sphere | 0.105 | 0.092 | 0.086 | none |
| (a) Wrap-over | 0.075 | 0.062 | 0.055 | 0.030 |
| (b) Stretched dome | 0.107 | 0.094 | 0.087 | none |
| (c) Flow, short | 0.094 | 0.081 | 0.074 | 0.012 |
| (c) Flow, long | 0.075 | 0.062 | 0.055 | 0.030 |
| (c) Flow, graded | 0.075 | 0.084 | 0.087 | 0.008 |

String centre to the board side at rest: 0.155 / 0.141 / 0.135 at frets 1 / 12 / 21 [C].

**Where a string starts to slide off.** A string pushed past full height rides down the descending part. I take it to start sliding outward on its own where the fret top slopes more than 10° [J: steel on polished steel; the real angle depends on string, polish and how the finger pushes]. Distance from the string at rest to that point [C given the 10° rule]:

| | Fret 1 | Fret 12 | Fret 21 |
|---|---|---|---|
| Vintage 35° bevel | 0.103 | 0.089 | 0.083 |
| v4 72° face | 0.109 / 0.100 | 0.096 / 0.087 | 0.089 / 0.081 |
| Round-1 quarter-sphere | 0.111 | 0.098 | 0.091 |
| (b) Stretched dome | 0.111 | 0.097 | 0.091 |
| (c) Flow, short | 0.099 | 0.085 | 0.079 |
| (c) Flow, long and (a) wrap-over | 0.082 | 0.068 | 0.061 |
| (c) Flow, graded | 0.082 | 0.088 | 0.090 |

The rounded ends hold a string slightly past full height (0.004 to 0.006 further) because the turn-over is gentle. The vintage bevel lets go slightly before full height because its corner is polished round.

On the long flow end at fret 12, the fret top is 0.001 low at 0.070 from the board side (slope 15°), 0.006 low at 0.060 (30°) and 0.014 low at 0.050 (47°) [C].

**Can a string choke on the descending part?** Not before it slips, by this estimate [C by hand, simple geometry, not in the contact model]. A string pushed 0.068 outward at fret 12 is pushed about 0.064 at fret 13, so it crosses fret 13 about 0.003 further from that fret's end. Up to the slide-off point the fretted fret is therefore lower than the next fret by under 0.001, well inside the clearance a fretted string has over the next fret (0.004 to 0.006 at a normal action [J]). Past the slide-off point the difference grows to about 0.003 and the note would buzz, but by then the string is on its way off.

**What 0.030 means in playing** [J]. Finger vibrato and pull-offs move an outer string roughly 0.03 to 0.05 toward the edge; hard bends on the outer strings normally go toward the middle of the board, away from the edge. With the long end the high E at fret 12 can travel 0.062 before the fret starts to fall away and 0.068 before it slides. That covers the usual movement with little to spare; a vintage neck has 0.092. At fret 21 the figures are 0.055 and 0.061 against 0.086. The owner has said plainly that strings must not fall off, so this is the number to weigh. I have no measurement of how far this owner pulls the high E; a strip of tape on a present guitar marking 0.06 in from the high E at fret 12 would show it in a minute.

## 8. When the board shrinks and swells

Chart: [fig/r2_shrink_swell.png](fig/r2_shrink_swell.png). The board side moves in or out against the steel, which does not move. 0.004 is roughly a 4 % change in moisture content across a quartersawn rosewood board of this width [J, as in round 1].

Hardest spot at fret 12 [C]. "Dried 0.004" means the wood has shrunk, leaving the steel 0.004 further out. "w": hardest spot on wood.

| | | Index, low | Index, 45° | Thumb, 45° | Thumb over |
|---|---|---|---|---|---|
| Vintage 35° bevel | dried 0.004 | 9.23 | 9.82 | 9.60 | 8.00 |
| | as dressed | 8.30 | 9.11 | 8.85 | 7.42 |
| | swollen 0.004 | 7.31 | 8.54 | 8.35 | 7.03 |
| | swollen 0.008 | 7.02 | 8.24 | 7.95 | 6.74 |
| Round-1 quarter-sphere | dried 0.004 | 4.40 | 5.44 | 5.47 | 5.15 w |
| | as dressed | 4.14 | 5.29 | 5.32 | 5.38 w |
| | swollen 0.004 | 4.46 w | 5.15 | 5.17 | 5.51 w |
| | swollen 0.008 | 4.89 w | 5.02 w | 5.09 w | 5.61 w |
| (a) Wrap-over | dried 0.004 | 4.60 | 5.91 | 5.71 | 5.05 |
| | as dressed | 3.61 | 5.47 | 5.24 | 4.66 |
| | swollen 0.004 | 5.35 w | 5.05 | 4.90 w | 4.44 |
| | swollen 0.008 | 6.66 w | 6.19 w | 6.09 w | 4.74 w |
| (a) shape without the leg | dried 0.004 | 4.77 | 5.99 | 5.79 | 4.95 |
| | as dressed | 3.61 | 5.47 | 5.24 | 4.66 |
| | swollen 0.004 | 4.15 w | 4.97 | 4.70 | 4.40 |
| | swollen 0.008 | 4.62 w | 4.49 | 4.17 | 4.17 |
| (b) Stretched dome | dried 0.004 | 4.21 | 5.45 | 5.33 | 4.64 |
| | as dressed | 3.86 | 5.31 | 5.19 | 4.56 |
| | swollen 0.004 | 4.05 w | 5.16 | 5.04 | 4.48 |
| | swollen 0.008 | 4.34 w | 5.03 | 4.91 | 4.41 |
| (c) Flow, short | dried 0.004 | 3.36 | 5.03 | 4.91 | 4.39 |
| | as dressed | 3.13 w | 4.88 | 4.76 | 4.33 |
| | swollen 0.004 | 4.27 w | 4.75 | 4.62 | 4.27 |
| | swollen 0.008 | 4.74 w | 4.61 | 4.47 | 4.21 |
| (c) Flow, long | dried 0.004 | 3.19 | 4.46 | 4.39 | 4.05 |
| | as dressed | 3.11 w | 4.19 | 4.02 | 4.00 |
| | swollen 0.004 | 3.29 w | 4.05 | 3.88 | 3.95 |
| | swollen 0.008 | 4.18 w | 3.90 | 3.74 w | 3.91 |
| (c) Flow, graded (fret 12) | dried 0.004 | 3.48 | 5.06 | 4.94 | 4.40 |
| | as dressed | 3.28 w | 4.92 | 4.80 | 4.33 |
| | swollen 0.004 | 4.05 w | 4.79 | 4.66 | 4.27 |
| | swollen 0.008 | 5.15 w | 4.64 | 4.50 | 4.21 |

Steel proud of the wood at 45° [C]:

| | Dried 0.004 | As dressed | Swollen 0.004 | Swollen 0.008 |
|---|---|---|---|---|
| Vintage 35° bevel | 0.019 | 0.016 | 0.014 | 0.011 |
| Round-1 quarter-sphere | 0.020 | 0.017 | 0.014 | 0.011 |
| (a) Wrap-over | 0.007 | 0.004 | 0.001 | 0.000 |
| (b) Stretched dome | 0.019 | 0.017 | 0.014 | 0.011 |
| (c) Flow, short | 0.016 | 0.013 | 0.010 | 0.007 |
| (c) Flow, long | 0.008 | 0.005 | 0.002 | 0.001 |
| (c) Flow, graded, mid-neck | 0.017 | 0.014 | 0.011 | 0.008 |

Reading it:

- **The flow ends hardly care.** The long end stays between 3.0 and 4.5 in every position across the whole range. In the edge positions a vintage bevel moves between 7.0 and 9.8.
- **No sprout.** The classic winter fault is steel standing past the board side. A vintage fret ends at the side, so any shrinkage exposes it. The new ends start 0.011 (dome), 0.018 (short) or 0.023 (long) in from the side [C], so the board would have to shrink by that much before steel reached the side. 0.004 does not come close.
- **Tuck is mildly good at 45° and mildly bad for a low hand.** When the board swells the steel sits slightly below the wood line. At 45° everything gets a little softer. With the hand low, the hardest spot moves to the small wood corner at the toe of the fret and rises (short end 3.13 to 4.74 at 0.008). It stays near the round-1 sphere's level (4.2 to 5.2 against 4.9) and far under vintage.
- **So dress the ends flush when the board is on the dry side of its normal range** [J], which leaves the steel flush to slightly tucked for most of the year. That gives the tucked seam the brief asked for in (b) without cutting a fixed step into the wood.
- **The wrap-over is the one end that gets worse when the board swells**: 6.66 with the hand low and 6.19 at 45° at 0.008, on the wood edges of the pocket, against 4.62 and 4.49 for the same shape without the leg.

## 9. How each end is made in stainless, and how a refret works

All of this section is judgment [J] based on ordinary fretting practice; none of it has been tried on this neck. Times are for 22 frets, 44 ends, in Jescar stainless, which files at roughly half the speed of nickel silver and wants diamond files and rubber-bonded abrasive wheels.

**Flow ends (b) and (c): short, long, graded, and the dome.** The method is the vintage one with a different angle and one extra step.

1. CNC the board: even roll, level rail, scallops, and the small wood ramp at each fret, with a 1/8 ball-nose finishing pass along the edge and rail (a 1/8 ball-nose leaves at most 0.0004 uncut [C]). Fret slots stay blind, ending 0.075 from the board side.
2. Cut each fret to length. Nip or grind the tang back so the crown overhangs the tang end by 0.062 to 0.074. This is what a bound fretboard already needs.
3. Rough each end off the neck: hold the fret in a small angle block and grind the end face at the blend angle on a diamond plate, leaving it about 0.005 long.
4. Press the frets, with thin glue under the overhanging crown ends.
5. Dress in place: a bevel file in a block set to the blend angle (50°, 60° or 65°), run along the edge exactly as for a vintage bevel. It rides on the steel ends. Stop when it just touches the wood: colour the roll with pencil and stop when the file first marks it. The wood ramp cut by the CNC is the gauge for every end.
6. Round each end from above with a safe-edged diamond fret-end file, then a small rubber abrasive wheel, then polish. This is the extra step: about 2 to 3 minutes an end.

Time: about 3.5 to 4.5 hours for the ends, against about 1 hour for a plain vintage bevel in stainless and the 2 to 2.5 hours v4 already allows. The graded end needs the bevel block reset in three or four groups along the neck, or a block that follows the CNC ramps; allow half an hour more.

**Why short can become long but not the reverse** [C, geometry]. The long shape is the short one with more removed: the 50° line touches the same roll further up and lies inside the 60° line everywhere. Filing a short end down to the long line by hand takes wood and steel together, as in step 5. Nothing can put the room back.

**Refret.** Pull the frets as usual; blind slots and glued overhangs need heat. New frets go through steps 2 to 6. The board's ramps are still there, so the file has the same gauge as the first time. No special tooling beyond the angle block. Expect an hour or two more than a vintage refret.

**(a) Wrap-over.**

1. CNC the board as above, then cut 44 pockets 0.014 deep and about 0.080 wide down the roll. A ball-nose from above cannot reach them (0.014 left uncut [C]); they need a 1/32 end mill with the neck turned on its side in two setups, or a chisel.
2. For each fret end: remove the tang for 0.10, thin the crown from below to a tab 0.014 thick and 0.039 long, anneal it, and bend it about 31° over a 0.040 radius. The outside of that bend stretches about 20 % [C by hand], which hard-drawn stainless will not take without annealing, and heat at the tab softens and discolours the crown end beside it.
3. Fit each leg to its pocket, glue it (nothing mechanical holds it), then dress steel and wood to one curve.

Time: 10 to 15 minutes an end, 8 to 11 hours, plus the pockets. A refret means making and fitting 44 new legs to pockets whose edges were torn getting the old ones out.

**Round-1 quarter-sphere**, for comparison: 2.5 to 3 hours with the cup cutter, plus the jig (round 1's figure). v4 allows 2 to 2.5 hours for shaping its ends [S: round 1, from SPEC.md].

## 10. The wrap-over: what could go wrong

A quick sweep found no maker documenting this (given in the brief); treat everything here as unverified practice.

- **It buys nothing in feel.** Flush, it equals the same shape without the leg in all six positions at all three frets [C]. The hand cannot tell steel from wood when the surface is one curve.
- **It loses to the rounded end.** Because the crown must stay wide to fold over the edge, it cannot be rounded from above, and that rounding is worth more than the leg (5.47 against 4.19 at 45°) [C].
- **Swelling exposes the pocket.** The wood rises around a leg that does not, leaving pocket edges proud: 6.66 against 4.62 [C]. Shrinking leaves the leg proud of the wood by the same 0.004 as any other end.
- **The leg end is a hook waiting to lift.** It is 0.014 thick, held by glue alone, sitting across wood that moves 0.004 a season, and it ends 0.001 from the board side, exactly where the hand slides. A lifted leg end is the worst fault any of these designs can produce.
- **The only steel that naturally wraps the edge is a through-slot tang end**, and that is the classic place for fret sprout.
- **The bend may crack or spring back**, and the pocket has to be cut to the leg, not the other way round.

If the owner still wants steel visibly carried over the edge for the look, one fret on the test piece would settle it.

## 11. The even roll and the edge rail: what changes in v4

Both are needed by every new end, and both are changes to the v4 board for the owner to accept.

- **Even roll.** A quarter round of 0.040 radius (0.030 for the dome, 0.040 falling to 0.030 for the graded end), the same at a fret and between frets. v4's roll is 0.048 wide at a fret and 0.062 between on the treble side, 0.058 and 0.085 on the bass, and 0.110 tall [S: SPEC.md]. The new roll is smaller and does not breathe. A bigger roll was tried: 0.055 instead of 0.040 softens the low-hand position slightly and costs 0.009 more bending room; not worth it [C].
- **Edge rail.** The scallop depth is zero under the roll, rises over a rounded shoulder, and reaches full depth 0.140 in from the side. The outer strings sit 0.135 to 0.155 from the side [C], so the scallop is at full depth under them (within 1 % at fret 21). The curve is two parabolas so a 1/8 ball-nose can cut it [C].
- **What it costs** [J]. A fingertip on the high E has full scallop depth under and inboard of the string, but on the outboard side it now meets wood rising to normal board height at the edge, as on an unscalloped board. v4 let the hollow run out through the edge on purpose. Round 1 already recommended stopping it short; this round shows why, in numbers: it is the difference between 0.006 and 0.015 of rise and fall at 45°.
- **The shading in the renders.** The dark band between frets on the new ends is the shoulder where the hollow starts. The edge itself is level.

## 12. Variants tried

46 shapes were run at fret 12 (a few are the final ones under working names), 25 of them rounded from above on the rail; all are in feel_r2.json, and the final ones in geometry_r2.json. What they showed [C]:

| Lever | Result |
|---|---|
| Rounded from above against square-cut, same 50° line | 4.73 against 6.07 (index, 45°). The biggest step. |
| How round from above (exponent 0.4 to 1.0) | 4.72 to 4.79. Nearly no effect, so the shape is forgiving to file. |
| Blend angle 72° to 45° on the rail | 6.57 falling to 4.38, room 0.101 falling to 0.060. This is the dial. |
| Top radius 0.012 to 0.040 at 50° | 5.16 falling to 4.19, costing 0.012 of room. Worth it on a rounded end, useless on a square one. |
| Roll radius 0.030 / 0.040 / 0.050 | 4.83 / 4.73 / 4.67. Minor. |
| Level rail against dished run-out | Rise and fall at 45°: 0.006 against 0.015. |
| Wrap-over leg | No change flush; worse swollen. |

## 13. What is computed and what is judgment

Computed [C]: every shape, section and render; bending room; where the fret top passes any given slope; steel proud of the wood; sharpest radii; gap under the crown; what a 1/8 ball-nose leaves; and all contact results (hardest spot, catch, rise and fall), including the shrink and swell cases.

Judgment [J]: the six hand positions, their angles and loads; finger softness (the same value for every candidate); the 10° slide-off rule; the 0.004 movement per season; how far a player moves a string in vibrato; every workshop method and time; whether the rail's effect on scallop feel matters.

Limits of the model, unchanged from round 1: the neck is rigid, the finger is a uniform soft layer with no bone, friction is not modelled, and the grid is 0.004, so features smaller than that (the 0.001 corner of a vintage bevel, the wrap-over's leg end) are smoothed. Differences of a few percent between candidates are within the noise; the ranking of vintage, round 1, and the short and long flow ends is not.

Render flaw, labelled on the sheets: a small dark fleck at the toe of the wrap-over leg and the dome in the side close-ups is the coarser wood mesh of the picture, not a gap. The computed gap under every crown is zero.

## 14. The one test piece

A rosewood offcut on maple, 6 in long, cut with the fret 10 to 14 spacing, even 0.040 roll and rail on both edges [J]:

- one edge with the 60° ramps (short), the other with the 50° ramps (long);
- five stainless frets, dressed as in section 9;
- on one spare end, the wrap-over, if the owner wants to see it.

It answers by hand what the model can only estimate: whether long really feels better than short, whether 0.062 holds the owner's vibrato (string a high E across it at the real spacing), how long the rounding takes in stainless, and whether the rail changes the scallop feel under the high E.

## 15. Files in this folder (round 2)

| File | What it is |
|---|---|
| [FRET-ENDS-R2.md](FRET-ENDS-R2.md) | This report |
| [fret-ends-r2-summary.png](fret-ends-r2-summary.png) | One-sheet summary |
| [fig/r2_render_treble_frets_12-13.png](fig/r2_render_treble_frets_12-13.png) | Renders, two frets, three views |
| [fig/r2_render_treble_fret_12_macro.png](fig/r2_render_treble_fret_12_macro.png) | Close-ups, treble edge at fret 12 |
| [fig/r2_render_bass_fret_1_macro.png](fig/r2_render_bass_fret_1_macro.png) | Close-ups, bass edge at fret 1 |
| [fig/r2_render_graded.png](fig/r2_render_graded.png) | The graded end at frets 1, 7, 12, 17, 21, both edges |
| [fig/r2_sections_treble_fret_12.png](fig/r2_sections_treble_fret_12.png) | Sections to scale: along, across, from above |
| [fig/r2_sections_bass_fret_1.png](fig/r2_sections_bass_fret_1.png) | The same at fret 1, bass side |
| [fig/r2_feel.png](fig/r2_feel.png) | Hardest spot, six positions, frets 2, 12, 20 |
| [fig/r2_slide.png](fig/r2_slide.png) | Rise and fall, and catch |
| [fig/r2_edge_line.png](fig/r2_edge_line.png) | The edge as a flat hand meets it, frets 9 to 15 |
| [fig/r2_bending_room.png](fig/r2_bending_room.png) | Fret top against distance from the string |
| [fig/r2_shrink_swell.png](fig/r2_shrink_swell.png) | Shrink and swell |
| [fig/r2_trade.png](fig/r2_trade.png) | Softness against bending room, all rounded variants |
| fe_r2_model.py | Round-2 shapes, built on the round-1 model |
| fe_r2_contact.py | Contact runs; writes feel_r2.json and feel_maps_r2.npz |
| fe_r2_fig.py | All round-2 figures |
| geometry_r2.json, feel_r2.json, feel_maps_r2.npz | Results |

Round 1's files (FRET-ENDS.md, fret-ends-summary.png, fe_model.py, fe_contact.py, fe_render.py, fe_fig.py, their data and figures) are unchanged.
