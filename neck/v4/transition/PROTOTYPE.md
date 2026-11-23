# Supercaster prototype • acoustic trim and fret transition

**Build the first test piece with the centred, longitudinally symmetric scallop, vintage-small stainless crown and graded rounded ends. Use the V1 Vintage dome for the body prototype. See the [plate and port comparison](../../../body/optimize/carve-v2-acoustics/LIVELINESS.md) for the open and inserted voices.** Matching the two ramps gives a finger approaching from either direction the same wood profile within each cell. V1 and V2 deliver similar modeled acoustic output. V1 has the smaller chamber reduction and less exposed forearm glue seam.

## Geometry for the test piece

All neck dimensions below are inches. Use the 25.5-inch scale, 22 frets, 0.140 round-lam board, compound radius and string spacing in [neck v4](../SPEC.md). The profile below is a prototype overlay on the v4 board and [R2 graded end](../fret-ends/FRET-ENDS-R2.md). The legacy interactive neck viewer depicts an earlier design.

| Station | High E scallop at trough | Distance of trough behind fret | Board edge roll radius | Fret-end face angle from level | Turnover radius into fret top | Full-height steel outside high E centre |
|---|---:|---:|---:|---:|---:|---:|
| 1 | .0300 | .716 | .040 | 50° | .040 | .0746 |
| 12 | .0511 | .379 | .033 | 60° | .030 | .0829 |
| 22 | .0168 | .213 | .030 | 65° | .025 | .0861 |

The trough is halfway between consecutive fret stations in every cell, including the nut to fret 1. [All 22 stations](results.json)

- **Along the string.** Centre the .080 × .043 Jescar crown on a flat land extending .055 each side of the fret station. For either half of a cell, measure distance inward from its nearest land boundary. Use the same eased ramp from both ends. The depth is 90% of a short ramp (full depth .300 from the fret centre or at mid-cell, whichever comes first) plus 10% of a ramp extending all the way to mid-cell. Each ramp uses fractional distance u clipped to [0,1], v = u − 0.4u(1−u), and 10v³ − 15v⁴ + 6v⁵. Both terms have zero slope and curvature at their endpoints. Wide cells get a broad curved bottom and close frets get a single symmetric bowl.
- **Across the strings.** Use the v4 per-cell depth law, bassward reduction and R2 rail. Calibrate the .030 first-cell depth on the actual high E line, then taper that correction to zero by cell 12. Locating the nominal depth at the extreme board edge gives a different result because the rail rises there. Keep the rail level between frets. Fade the hollow in from the end of the edge roll to .140 inboard. At the outermost positions up the neck the high E lies within this fade.
- **At the fret end.** Use the same graded roll on both sides. Interpolate roll radius, face angle and turnover radius linearly with distance from fret 1 to 22. The wood nose and steel end share a tangent in the fret-centre cross-section. In plan, narrow the crown half-width in proportion to the square root of the remaining height fraction. The R2 forming sequence preserves the supported seat and blind tang slot. Its uniformly long option is softer in the prior contact model but leaves only about .062 full-height reserve at fret 12. The graded end preserves about .083 there. These distances run from the string centre and actual alignment consumes part of the reserve.
- **Machining check.** A sampled vertical ball-tool envelope for a 1/8-inch-diameter ball nose left at most .00016 excess wood over the treble-side hollow and rail blend (.004 grid, roll tangent to .320 inboard, frets 1–22 including the first cell). Use a scrap cut to check the actual tool and finish the fret-end nose with the R2 jig and hand dress. That screen excludes the outer roll, tang slots, toolholder, sanding and process error. The executable wood and steel surfaces are in [study.py](study.py).

## How much the transition changes

I compared five mirrored profiles with 0%, 10%, 25%, 50% and 100% full-span bowl contribution. The 10% choice is the roundest tested that preserves at least 90% of the previous offset design’s depth .250 behind every fret (mid-cell where closer). Its minimum was 90.8%. A pure full-span bowl preserved only 7.7% at the worst position, so moving the old trough to the middle without redesigning the shoulders would remove much of the useful clearance.

The selected cut mirrors to within 1e−12 inch in the model at 41 paired positions on each of six string lines in all 22 cells. The treble-to-bass taper still gives more depth under the plain strings. The median absolute difference in modeled climb angle between slide directions at frets 1–21 fell from 1.67° to 0.11° for a .30-radius rigid pad. The last fret has flat wood beyond it. Adjacent fret spacings and depths vary, so even a mirror-symmetric cell can give slightly different crossings at its two ends.

| Pad radius | Worst climb, previous offset | Worst climb, centred |
|---|---:|---:|
| .20 | 36.51° | 36.51° |
| .30 | 31.97° | 31.96° |
| .40 | 29.26° | 29.26° |

The main gain is directional consistency. Grid refinement from .0005 to .00025 changed the selected .30-radius maximum by 0.10°. The pad model excludes skin deformation, friction and the string. Use a strung test to decide whether the directional change is perceptible.

## Acoustic result at the prototype trim

Six fresh coupled air, body and radiation solves reused the existing structural mode caches and a 6.0 mm bare alder roof. Four geometries shared the 294 Hz target. Two additional V1 trims checked the ends of the provisional ±4 Hz range. The flat reference reached 293.96 Hz. Values below compare mean radiated power per unit saddle-force squared, averaged over six equal saddle drives. They do not predict the sound pressure at the player's ear.

| Carve | Air mode (Hz) | Model liner inset (mm) | 80–200 Hz | 200–300 Hz | 300–500 Hz | 500–1000 Hz |
|---|---:|---:|---:|---:|---:|---:|
| Flat | 293.96 | 1.96 | reference | reference | reference | reference |
| V1 Vintage | 293.90 | 2.40 | +0.47 dB | +0.38 dB | −0.16 dB | −0.39 dB |
| V2 Hollow | 294.09 | 2.58 | +0.67 dB | +0.26 dB | −0.24 dB | −0.41 dB |
| V3 Deep | 294.01 | 2.35 | +0.28 dB | −0.74 dB | −0.62 dB | −0.79 dB |

Keep the V1 throat adjustable. Its modeled inset ran from 2.57 mm at 290.32 Hz to 2.24 mm at 297.99 Hz. The trim near 298 Hz gave about 1.06 dB less in the 200–300 Hz band than the nominal V1, with the top of the band only 2 Hz away from the air mode. Over the combined 200–500 Hz band the same change was only −0.17 dB. Halving the frequency step from 0.5 to 0.25 Hz changed every reported V1 band by less than 0.011 dB across the three trims. Machine the final throat to the measured assembled response. The 6 mm figure is a finished prototype roof thickness subject to stock qualification. Actual liner stiffness, wood variability and player coupling still limit the comparison.

Both intended tunings were evaluated on the existing open-through-fret-12 conductance grid. The shortest modeled body-loss-only decay on V1 occurred at about 185 Hz on the fourth string, fret 5, in both tunings. Include it and its neighbours in the tap/pluck test. This acoustic calculation still uses the legacy simulated neck and its tension assumptions. It establishes neither a sustain gain from scalloping nor the dead spots of a finished v4 instrument. Experimental electric-guitar work relates string decay to measured neck conductance and isolated-string damping. [Paté, Le Carrou and Fabre, JASA](https://pubmed.ncbi.nlm.nih.gov/24815284/)

## Physical decision

1. Cut two matched rosewood-on-maple samples at frets 10–14 for the queued comparison. Include a low-position sample around frets 2–5 to feel the larger difference in the wider cells. Give both the same graded ends, wire, finish, crown height and rail. Give A the previous .300-setback offset scallop and B the selected one. Record actual land widths, trough depths and high E margin after leveling. Compare them in a full-scale strung jig with Jordan's 10.5–48 set, matched action and relief.
2. Mask their identities and alternate the order over ten pairs. Play the same slow slide in both directions, a whole-step inward bend, outward vibrato and a light versus usual-pressure fretted note. Record catches, roll-offs, tuner error in cents and preference by pair. Advance B if the slide preference repeats and pitch control and string retention hold up. Record the observed differences if the choice is unclear. On a separate short offcut, compare graded and long ends if edge softness is still limiting.
3. Dry-clamp the body with a reversible throat insert. Record temperature, mic position and bridge impulse response, then trim toward 294 Hz. Recheck after glue, finish and hardware. On the assembled, player-held instrument, use repeatable plucks in E♭ standard and drop C♯, keeping string gauge, pluck point, pickup height and gain fixed. Compare note decay on adjacent frets and record clean pickup output separately from the microphone. The fretted coupon answers the hand-feel question. The assembled guitar answers the acoustic one.

## Reproduction

From the project root, using the project simulation environment:

```sh
body/sim/cache/venv/bin/python -I -B body/optimize/carve-v2-acoustics/prototype_trim.py
body/sim/cache/venv/bin/python -I -B neck/v4/transition/study.py
body/sim/cache/venv/bin/python -I -B neck/v4/transition/figure.py
```

[Acoustic results](../../../body/optimize/carve-v2-acoustics/results/prototype_trim.json) · [Cross-sections and band comparison](prototype.png) · [Construction review and physical interfaces](../../../body/optimize/ENGINEERING-STATUS-2026-11-15.md)
