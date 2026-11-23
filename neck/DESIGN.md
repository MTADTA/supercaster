# Supercaster II set neck: design study v1

Owner spec (fixed): quartersawn roasted maple set neck with a slab rosewood board. 25.5 in scale, 22 frets. Hidden tongue to x ≈ 21.7 in; the round heel comes later. Vintage Strat nut. Conical 7.25 to 9.5 in compound radius. Stainless "6230" frets, fitted loose. Scalloped board, asymmetric profile with a rule. Reverse headstock with Gotoh SD91 MG-T tuners. Heavy whammy use with a vintage synchronized trem or a Vega-Trem VT1. Extra relief (0.012 in or more). Eb standard and drop C#, on 10.5–48 nickel strings. Single-acting curved truss rod with a spoke wheel at the body end. No carbon bars. Relief partly planed into the board.

Model: `neck/neck_model.py` (parametric; every dimension is in the `P` dict). Running it writes `neck/results.json`, `neck/fig/*.png` and the tables below. Python: viz venv, `-I -W ignore`, about 15 s.

Frame: x runs from the nut toward the bridge, y is positive on the bass side, and z is up. z = 0 is the board-top centreline chord. All lengths are in inches unless marked.

Tags: **[computed]** = from neck_model.py. **[lit: …]** = from a public source (listed at the end). **[judged]** = my engineering choice, so change it if you disagree. A tag on a table caption applies to every number in that table.

---

## 0. Decisions at a glance

| Item | Decision | Tag |
|---|---|---|
| Profile rule | **C, "cone-coupled":** depth ∝ board radius, with the section shape fixed in normalised coordinates. The back is an exact ruled surface. Depth runs 0.820 at fret 1 to 0.931 at fret 12, identical to `final_carve.neck_depth`. | [computed] |
| Asymmetry | Apex 0.08·W/2 toward the bass; superellipse exponent 2.30 bass, 1.70 treble. The shoulder ratio is a constant 1.37. | [judged] (repo defaults) |
| Fret wire | Jescar FW43080-S (stainless): crown 0.080 × 0.043, tang 0.020, barb 0.032, tang depth 0.050. ~~No stainless Dunlop 6230 exists~~ **Erratum (v2): a stainless 6230 does exist** (Allparts LT-0891-005 ≈ SS6230, 2.00 × 1.00 mm); see §v2.5. The nickel 6230 is 0.078 × 0.043. | [lit: Jescar guide; lutherie.net] |
| Fret fit | Slot 0.025 wide × 0.060 deep, leaving 0.007 barb interference (Jescar recommends 0.023 for 0.009). Loose, so the frets don't wedge against the rod. | [judged] |
| Scallop law | d_k = min(0.030 + 0.045·ξ_k, 0.15·L_k²) per cell. The profile is a full-span quintic (S5) blend with zero slope **and** zero curvature at the crown foot. Peak depth is 0.064 at cell 14. | [computed] (law), [judged] (end depths) |
| Fret ends | Hemispherical dome r = 0.040 (a true half-sphere). The tang is nipped back 0.05 (about 1/16 in). Slots are stopped (blind), ending 0.02 inside the dome apex. | [computed] |
| Edge roll | A heavy quarter-ellipse roll, 0.061 to 0.040 across the top (fret 1 to 22) by 0.14 down the side on the bass. It is shorter on the trimmed treble shoulder (0.080 to 0.032). It is continuous with the scallops, which keep 40 % of their depth at the roll. | [computed] / [judged] |
| Relief | Parabolic sagitta 0.0083 planed into the board between the nut and x = 15.7, plus a 0.006 fall-away from fret 15. With the rod slack, Eb standard gives about 0.017. The rod only ever removes relief. | [computed] |
| Truss rod | Single-acting 3/16 rod in a curved channel. The anchor sits under the nut end; the spoke wheel is at x = 18.45, 0.065 above the body top. The rod needs up to 275 lb. | [computed] |
| Nut | No string tree. Use the LH tuner set (mandatory for the button direction), with the **short staggered posts on the high E, B and G (the posts nearest the nut)**. Cut slots along each string's 3-D path. Use a low-friction nut (bone with graphite, or Tusq XL). Option: a 0.10 face drop. | [computed] / [judged] |
| Neck angle | 0° at board height 0.375 (the body's value). Saddle break is never short (38–51° total). Trim with the pocket depth after the saddles are measured. | [computed] |

---

## 1. Profile rule: one rule for depth, width, asymmetry and board radius

### 1.1 The observation that decides it

Fret positions are x_n = S(1 − 2^(−n/12)), so 2^(−n/12) = 1 − x/S. Any law that is **geometric in fret number** is therefore **linear in x** [computed]. A "golden" or constant-ratio progression per fret is also a linear-in-x law. Of the requested candidates, only "equal step per fret" (rule F) is a genuinely different family.

The board radius is already linear in x, R(x) = 7.25 + 2.25·x/25.5 (a true cone) [judged: owner spec]. The width is too, W(x) = 1.650 + 0.550·x/x₂₁ [lit: body/carve/final_carve.py neck_width]. So any depth law that is linear in x, paired with a fixed normalised shape, makes the back of the neck a **ruled surface**: straight lines join the same normalised point u on every section. A ruled surface can be cut exactly with a flank or swarf toolpath, and its CAD loft is exact with two sections.

### 1.2 Governing equations of the recommended rule C [computed]

```
R(x)  = 7.25 + 2.25 x / 25.5                     board radius (cone)
W(x)  = 1.650 + 0.550 x / 17.919                 board/neck width (x21 = 25.5(1 − 2^(−21/12)) = 17.919)
D(x)  = 0.82 · R(x) / R(x1) = 0.11117 · R(x)     centreline depth incl. board, x1 = 1.431, R(x1) = 7.376
u     = 2y / W(x)                                normalised lateral coordinate, −1 (treble) … +1 (bass)
z_back(x, y) = −D(x) · Φ(u)
Φ(u)  = s(u) / s(0)
s(u)  = (1 − v^pb)^(1/pb),  v = (u − u0)/(1 − u0)   for u ≥ u0 (bass)
      = (1 − v^pt)^(1/pt),  v = (u0 − u)/(1 + u0)   for u < u0 (treble)
u0 = 0.08, pb = 2.30, pt = 1.70                  (constant along x)
board top z_top(x, y) = −[R − √(R² − y²)] − p(x) − d(x)·w(x, y) − roll(x, y)   (§2, §3)
```

In words, **depth is a fixed fraction (0.111) of the local board radius.** Width, depth, radius and the absolute shoulder offsets (u0·W/2 and so on) are all affine in x, so the section is the same shape scaled by D in z and W in y. The section thickens exactly as fast as the board flattens.

This is identical to the existing `final_carve.neck_depth` law. The heel loft starts at D = 0.946, which matches the body model exactly [computed], so the interface to the body does not change.

### 1.3 The four candidates [computed]

The depth D includes the board. "Asym" is the shoulder ratio: the bass half-width over the treble half-width at 75 % depth.

| Rule | Fret 1 D / W / asym | Fret 5 | Fret 9 | Fret 12 | Fret 17 | dD/dx (thou/in) | Ruled? (dev) | Heel-loft start D (body 0.946) |
|---|---|---|---|---|---|---|---|---|
| L: linear in x (asym fades) | 0.820 / 1.694 / 1.37 | 0.864 / 1.846 / 1.27 | 0.899 / 1.967 / 1.21 | 0.920 / 2.041 / 1.17 | 0.948 / 2.140 / 1.12 | 8.8 const | no (1.7 thou) | 0.934 |
| F: equal step per fret | 0.820 / 1.694 / 1.37 | 0.856 / 1.846 / 1.29 | 0.893 / 1.967 / 1.23 | 0.920 / 2.041 / 1.18 | 0.965 / 2.140 / 1.11 | 6.5 → 14.7 (accelerates) | no (15.7 thou) | 0.940 |
| **C: depth ∝ radius** | 0.820 / 1.694 / 1.37 | 0.869 / 1.846 / 1.37 | 0.907 / 1.967 / 1.37 | **0.931** / 2.041 / 1.37 | 0.962 / 2.140 / 1.37 | 9.8 const | **yes (0)** | **0.946** |
| G: constant D/W ("golden", true cone) | 0.820 / 1.694 / 1.37 | 0.894 / 1.846 / 1.37 | 0.952 / 1.967 / 1.37 | 0.988 / 2.041 / 1.37 | 1.036 / 2.140 / 1.37 | 14.9 const | yes (0) | 1.011 |

Qualitative comparison [judged]:

- **L** is smooth, but it is not exactly ruled once the asymmetry is interpolated. The asymmetry fades toward the body, which is a choice you could make. Its depth also stops 12 thou short of the body loft.
- **F** is the only rule whose slope rises toward the body: a 2.3× faster thickening per inch above fret 12. That is the "sudden thickening" to avoid, and it is the least CNC-friendly.
- **C** has a constant thickening of about 10 thou per inch, the same feel everywhere. It is exactly ruled and joins the heel without a step. The fixed asymmetry means the bass shoulder stays full all the way up.
- **G** keeps the vintage proportion D/W = 0.484 all the way, but that is +57 thou at fret 12. It feels like a baseball bat at the 12th, and it misses the heel loft by 65 thou.

Interaction with scallops and relief [computed]:

- None of the rules touch the board top, so the scallop law (§3) is the same for all of them.
- The flexural stiffness EI rises with D³. Relative to C, rule G would be about 19 % stiffer at fret 12 ((0.988/0.931)³, [computed]), which lowers tension bow by the same fraction. L and F would differ from C by under 4 % [computed].
- The relief numbers in §5 use rule C.

**Recommendation: rule C.**

Figures:
- `fig/profile_rules_sections.png`: sections at frets 1, 5, 9, 12, 17 and 22 for each rule.
- `fig/profile_rules_curves.png`: D, D/W, shoulder ratio and dD per fret.
- `fig/profile_3d_taper.png`: the rule-C back with its straight rulings (y and z exaggerated 2.2×).

The plain law runs past fret 15 for comparison only; the body's heel loft takes over there.

---

## 2. Frets, fret ends and edge roll

### 2.1 Wire [lit]

| Wire | Crown w × h | Tang | Barb | Tang depth | Source |
|---|---|---|---|---|---|
| Dunlop 6230 (nickel; **erratum v2:** a stainless SS6230 also exists, see §v2.5) | 0.078 × 0.043 | — | 0.035 | — | [lit: lutherie.net fret chart] |
| **Jescar FW43080-S (stainless)** | **0.080 × 0.043** | **0.020** | **0.032** | **0.050** | [lit: Jescar dimension guide, PLT] |

The Jescar PDF labels the tang "5.08 mm". That is a typo for 0.51 mm (0.020 in) [judged].

Slot: 0.025 × 0.060 [judged]. It leaves 0.007 barb interference against Jescar's recommended 0.009 at a 0.023 slot [lit: Jescar guide]. This keeps the "loose" fit you asked for, so the frets do not wedge the board into back-bow against the rod. The relief model gives the frets no stiffness.

Seat each fret with a light press and a wick of thin glue at the ends [judged].

### 2.2 Domed ends [computed]

- The crown half-width is 0.040, so the end can be a **true hemisphere r = 0.040**.
- The full-height crown ends 0.040 inside the dome apex.
- The outer strings stay **0.030 inside the full-height crown** at every fret with the vintage spacing. That margin sets the roll width (§2.3). The VT1's narrower spacing gives 0.033 to 0.071.
- **Tang:** it must be nipped back r + 0.010 = 0.050 from the apex. Otherwise it would poke out of the dome's underside.
- **Slots:** stopped (blind), ending 0.020 inside the apex, at the start of the roll. This leaves 0.072 to 0.097 of rosewood beyond the slot end (fret 22 to fret 1). The slot never cuts through the roll, so the vintage edge stays continuous and no fret-end fill is needed.

### 2.3 Edge roll law [computed]

```
a(x) = clip( W/2 − s_vint(x)/2 − d_E/2 − r_dome − 0.030 , 0.03, 0.08 )      top setback (roll width)
b_side = 0.14 (bass); on the treble, min(0.14, depth where the shoulder reaches y_c + 0.6a)
roll profile: quarter ellipse, horizontal semi-axis from y_c = W/2 − a to the actual side wall,
vertical semi-axis b_side; tangent to the top and to the back surface
```

| Fret | 1 | 5 | 9 | 12 | 15 | 17 | 19 | 22 |
|---|---|---|---|---|---|---|---|---|
| a (top setback) | 0.061 | 0.055 | 0.050 | 0.047 | 0.045 | 0.043 | 0.042 | 0.040 |
| treble b | 0.080 | — | — | 0.048 | — | — | — | 0.032 |
| rosewood edge thickness at the roll | 0.148 | 0.137 | 0.133 | 0.132 | 0.133 | 0.133 | 0.128 | 0.125 |

Bass b = 0.14 throughout [judged, "heavy"]. The values above are [computed].

The roll narrows toward the body because the string spread widens faster than the board, by 0.60 against 0.55 between the nut and fret 21 [computed].

The treble side has the trimmed 1.70 shoulder exponent and already curves inward close to the top. So its roll is shorter but still tangent [computed]. That is why the edge looks heavier on the bass.

The scallop fades laterally with an S5 ramp: full depth inboard of the outer string + 0.03, down to 40 % at the roll start [judged]. The roll's top line therefore undulates gently at 40 % of the centre scallop depth (`fig/board_edge_domes.png`, side view). The edge is continuous, and on the edge you can see the scallop "breathing" between the domes.

Figure: `fig/board_edge_domes.png`. It shows the bass and treble sections at fret 12 with the wire, tang, stopped slot and both bridges' outer string; the plan view of the domes; and the side view along the edge.

---

## 3. Scallops designed with the frets

### 3.1 Why the crown foot sets the law

A stock crown meets the board almost vertically, so no scallop can blend *tangentially* into the crown itself. The fingertip slides from the scallop wall onto the crown. A catch happens when the fingertip's centre path has a sudden slope change.

Metric [computed]: roll a rigid R = 0.30 circle (a fingertip proxy [judged]) across the whole cell, crown to crown. Take the largest slope jump of its centre path, in degrees.

- Unscalloped board: about 25.5°. This is the reference you already slide on.
- Goal: no cell worse than the flat board + 1° (but see the noise floor in §3.2).

Findings [computed]:
- A full-span **S5 (quintic smoothstep)** profile, with no flat land, gives the deepest catch-free depth: about 0.168·L², where L is the fret spacing. Adding flat lands (0.12 at high frets) *creates* a catch.
- A full-span sin² profile performs similarly but has non-zero curvature at the foot.
- Depth must therefore shrink with the **square** of the fret spacing. A linear "deeper toward the body" law, as in the classic graduated scallop [lit: Seymour Duncan blog], catches at **53–61°** in cells 17–22.

### 3.2 Depth law [computed / judged]

```
ξ_k  = (x̄_k − x̄_1)/(x̄_22 − x̄_1)            x̄ = cell centre
d_k  = min( 0.030 + 0.045 ξ_k ,  0.15 L_k² )  depth below the land at the centreline   [0.030, 0.075, 0.15: judged; cap from the scan]
z(x) = −d_k · S5(ξ_in) · w(x,y),  S5(t) = t³(10 − 15t + 6t²),  ξ_in = distance from the nearer crown foot / half-cell
w(x,y) = 1 − 0.6·S5((|y| − y_o)/(y_e − y_o)),  y_o = outer string + 0.03,  y_e = roll start
```

| Cell | 1 | 3 | 5 | 7 | 9 | 12 | 14 | 15 | 17 | 19 | 22 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| d (centre) | 0.030 | 0.037 | 0.043 | 0.049 | 0.054 | 0.060 | **0.064** | 0.061 | 0.048 | 0.038 | 0.027 |
| catch, proposed (°) | 26.8 | 23.2 | 26.1 | 23.9 | 20.9 | 19.9 | 18.2 | 16.1 | 14.9 | 26.8 | 24.8 |
| catch, flat board (°) | 25.5 | 25.5 | 26.8 | 25.5 | 25.5 | 25.5 | 25.5 | 25.5 | 26.1 | 25.5 | 25.5 |
| catch, uncapped linear law (°) | 26.8 | 23.2 | 26.1 | 23.9 | 20.9 | 19.9 | 18.2 | 20.1 | **53.5** | **54.8** | **61.2** |

The law deepens to cell 14, then the cap takes over and the depth eases off above the heel.

**Noise floor [computed]:** the flat board itself reads 25.5 to 26.8° from cell to cell, with an identical crown and fingertip. So the metric has about 1.3° of discretisation noise. On that scale the proposed law is indistinguishable from the flat board in cells 1, 5 and 19 (+1.3, −0.7, +1.3°) and lower everywhere else. The stated "+1°" tolerance is below the noise, so read it as "no worse than flat within 1.3°".

For the same reason, the depth-cap bisection is unreliable at the low frets: it returns 0.200 at cell 1. The 0.168·L² fit comes from cells 9 to 22, where the cap actually binds, and there the catch-limited depth is resolved cleanly.

The `0.15` cap is about 10 % under the scanned limit of 0.168 [judged].

Option [computed]: a **0.010 rebated fret seat** (a tiny flat step at the crown foot) lowers the catch to 11–21° at low and mid frets. It costs a little crispness; your call.

Wood checks [computed]:
- Least rosewood left under any scallop is 0.080 (cell 14), against 0.200 nominal.
- The centreline is never thinner than 0.133.
- The 0.060 slot depth is always above the scallop floor (`fig/scallop_law.png`).
- The rod top stays 0.033 (cell 22) to 0.266 below the glue line. The rod channel is in the maple, so scallops never reach it.

Figures:
- `fig/fret_scallop_closeup.png`: the section through fret 12 and its scallop, with the wire, tang, slot and the fingertip at the crown.
- `fig/scallop_law.png`: depth, wood left and the catch per cell.

### 3.3 Playing feel: pressing into the scallop [computed]

The string only ever touches frets, so **scallops cannot cause buzz.** The fret plane, relief and action are identical to an unscalloped board.

What changes is how far a hard player can push the string *below* the fret crown between frets. That pressure sharpens the note. Below, p is the string bottom's depth below the crown top at mid-cell:

| String / cell | p = 0.010 | p = 0.020 | p = 0.043 (limit on a flat board) | pressed to the scallop floor |
|---|---|---|---|---|
| E4, cell 3 | 0.8 ¢ | 3.1 ¢ | 14 ¢ | 41 ¢ |
| E4, cell 12 | 1.3 ¢ | 5.2 ¢ | 24 ¢ | 107 ¢ |
| G3, cell 3 | 2.2 ¢ | 8.8 ¢ | 40 ¢ | 115 ¢ |
| G3, cell 12 | 3.7 ¢ | 14.7 ¢ | 68 ¢ | 302 ¢ |

The "floor" column is an upper bound, because the finger cannot press that far in practice.

This is the known scallop trade-off: the board no longer stops your finger at 0.043. It is moderated here by the shallow depths (0.030–0.064 against the 0.08–0.12 often quoted for full scallops [judged, not found as measured data]).

With the rigid R = 0.30 proxy, the pad still touches wood at mid-cell in every cell [computed]. The "pad floating above wood" feel would need deeper scallops, and those catch at the high frets.

---

## 4. Wood checks for the rod channel and tang

- **Tang:** depth 0.050 in a 0.060 slot. The slot always sits in rosewood at least 0.072 from the edge, so the tang never meets the rod channel [computed].
- **Rod channel:**
  - 3/16 rod; the centre is 0.31 below the board top at the ends, with 0.25 of extra sag mid-channel (a curved channel) [judged].
  - The rod top is 0.033–0.266 below the glue line [computed].
  - **0.033 at cell 22 is thin.** The filler strip there must be maple, glued before the board goes on [judged].

---

## 5. Relief and truss rod

### 5.1 Fix in `calc/relief.py`

In relief.py, y = 0 is the **glue line**, so e_above = 0.09 had put the string inside the board. The lever arm is now `0.20 + e_above − y_c`. Corrected tension bow at Eb, for E = 11 / 12.5 / 14 GPa: **0.0087 / 0.0077 / 0.0069** (previously 0.0051 / 0.0045 / 0.0040) [computed]. Relief was underestimated by about 1.7×.

### 5.2 Model in neck_model.py [computed]

- Euler–Bernoulli beam, clamped at the body from x = 15.7.
- The section is composite: rosewood + maple, the rod hole removed, scallops included.
- The string force acts at its height above the neutral axis.
- Relief is the gap under a fret 1–16 straightedge.

Tension bow, rod slack, flat board:

| Tuning | Total T (lb) | Soft maple (11 GPa) | Nominal (12.4) | Stiff (14) | Scalloped nominal |
|---|---|---|---|---|---|
| E standard | 108.7 | 0.0115 | 0.0109 | 0.0103 | 0.0122 |
| Eb standard | 96.9 | 0.0103 | 0.0097 | 0.0092 | 0.0109 |
| Eb drop C# | 93.4 | 0.0099 | 0.0094 | 0.0089 | 0.0105 |

- **Scallops add about 12 % relief** (0.0109 / 0.0097 at Eb nominal). They help, but not enough on their own.
- **Planed relief:** parabola sagitta 0.0083 between the nut and x = 15.7 (0.0065 gap under the 1–16 chord), plus an S5 fall-away of 0.006 from fret 15 to the board end.
- Slack-rod relief:
  - Eb standard: 0.0109 + 0.0065 ≈ **0.017**;
  - worst low case, drop C# on stiff wood: 0.0098 + 0.0065 ≈ **0.016**;
  - both are above your 0.012 or more. The rod pulls it down to whatever you like.
- **Rod demand:** to reach 0.010 at E standard on soft wood, the rod must remove 0.0094. At 0.0034 per 100 lb, that is **≈ 275 lb** of rod tension. Check the rod's rating (open question).
- A single-acting rod can only *remove* relief. That is fine here, because the planed relief means the neck never needs pushing forward.

Figure: `fig/relief_rod.png`.

### 5.3 Spoke wheel packaging [computed]

The rod end is at x = 18.45 and the wheel centre is 0.065 above the body top. The board ends at 18.594 and the neck pickup route starts at 18.82. That leaves **about 0.23 for the wheel**, so it needs a shallow access notch in the body top and a relief in the pickguard. Flag for the body agent.

---

## 6. Nut: reverse headstock, Gotoh SD91 MG-T

### 6.1 Tuners [lit]

- Staggered SD91 MG-T sets **exist**: 18.5/20 mm (retailer listings) or 18/19 mm baseplate-to-hole (Rockinger). Flat versions are 18.5 mm (Thomann).
- Post 6.35 mm, hole pitch 23.8 mm, vintage 11/32 bushing.
- Hole height above the face = baseplate figure − 0.55 headstock thickness, about 4–6 mm [computed].
- **The LH set is mandatory** on a reverse head for the vintage button direction [judged].

### 6.2 Geometry [computed]

The 3-D wrap at the nut is the angle between the speaking length and the run to the post.

The posts are on the treble side, high E nearest. So the bass strings run back at up to 11.6° *laterally*, while vertical angles are only 0.6–2.2°. **Lateral splay dominates**, which makes the reverse head the mirror of a standard head: there the high E has the steep angle.

| Option | E4 | B3 | G3 | D3 | A2 | E2 | Worst return error, μ = 0.10 / 0.25 |
|---|---|---|---|---|---|---|---|
| Flat posts | 3.1° | 7.2° | 9.1° | 10.0° | 10.4° | 10.6° | 3.3 / 8.3 ¢ (E2) |
| **LH staggered, short posts on E4, B3, G3 (rec.)** | **3.4°** (vertical 2.2°) | 7.3° | 9.1° | 9.9° | 10.4° | 10.6° | 3.3 / 8.3 ¢ |
| LH staggered, short posts on the bass | 2.9° (vertical 1.0°) | 7.2° | 9.0° | 10.0° | 10.4° | 10.6° | 3.3 / 8.3 ¢ |
| rec. + 0.10 face drop | **5.7°** (vertical 5.3°) | 8.0° | 9.4° | 10.1° | 10.5° | 10.7° | 3.4 / 8.4 ¢ |
| rec. + tree on E2/A2 | 3.4° | 7.3° | 9.1° | 9.9° | 10.7° | 10.8° | **4.0 / 10.0 ¢** |
| Standard head, RH staggered (reference) | 10.8° | 10.5° | 10.0° | 9.0° | 7.0° | 2.6° | 3.4 ¢ (E4) |

Down-force on the nut runs from 0.95 lb (E4) to 3.2 lb (E2) [computed].

Return error is the worst-case offset after a dive or return when nut friction holds a tension step [computed]: about 865.6·μθ·L_behind / (L_speaking + L_behind) cents. The locking post fixes the far end.

### 6.3 Recommendations [judged, on the computed numbers]

1. **No string tree.** On a reverse head no string needs one. A tree on E2/A2 only adds friction (+0.7 ¢ at μ 0.10, +1.7 ¢ at μ 0.25).
2. **Install the LH staggered set by string, with the short posts on the trebles.** On a reverse head those are nearest the nut. This raises the high E's vertical seating from 1.6° (flat posts) to 2.2°, at no measurable cost (+0.03 ¢). The other stagger order would give only 1.0°. This puts the set's short tuners in different holes from the positions the set is marked for. That works because all six tuners in an LH set share one gear direction. The bass strings are held by lateral wrap whatever the posts are.
3. **Optionally drop the headstock face 0.10 below the glue plane.** The high E then gets 5.7° of total wrap and 1.6 lb of down-force, against 3.4° and 0.95 lb, for +0.2 ¢. Do it if the high E pings or rattles in the slot.
4. **Nut:**
   - bone with graphite, or Tusq XL (low μ);
   - cut each slot along the string's *plan* path, angled toward its post, with a rounded exit, because the break is mostly sideways;
   - slot floor tilted 1–2° toward the headstock, no pinch, slot depth about half the string diameter on the plain strings.
   - The friction term μ is the lever, so measure it: dive, return and read the tuner.

Figure: `fig/headstock_nut.png`. The outline is the repo's vintage outline, mirrored.

---

## 7. Saddle break and neck angle (both trems)

### 7.1 Inputs

- Pivot at x = 25.25, the scale length less 1/4 in [lit: a retailer's published installation dimension for vintage-style tremolos].
- Plate 0.10 thick, 1.70 from the pivot to the rear, string hole 0.70 behind the pivot [judged].
- Float 1/8 in [lit: Fender support].
- Action at fret 17: 0.078 bass / 0.070 treble [judged, Fender 7.25 in table + hard-player margin].
- Board height at the pocket datum 0.375 [lit: body/carve/final_carve.py].
- **No saddle or knife-edge drawing was found for the VT1.** Its inputs are the vintage ones with a 2.106 spacing [lit: Thomann/Warwick 53.5 mm] and must be measured.

### 7.2 Results [computed]

| Bridge, neck angle | Crest heights above plate (E4 … E2) | Total deflection at saddle | Down-force per string |
|---|---|---|---|
| Vintage, 0° | 0.337 / 0.377 / 0.397 / 0.402 / 0.382 / 0.340 | 38–51° | 10.5–14.1 lb |
| Vintage, −0.22° | 0.299 … 0.364 … 0.301 | 35–47° | 9.5–13.1 lb |
| VT1, 0° | 0.343 / 0.379 / 0.397 / 0.402 / 0.384 / 0.346 | 39–51° | 10.7–14.1 lb |
| Vintage, −0.22°, decked (no float) | 0.321 / 0.365 / 0.387 / 0.389 / 0.371 / 0.332, i.e. 0.022–0.031 **higher** than floated | 39–51°, 4–5° more | — |

- **The saddle break is never short.** The string drops steeply through the plate on both trems, so down-pressure is not a design driver.
- What the neck angle sets is **saddle crest height**:
  - at 0° and H = 0.375, the crests are 0.34–0.40, inside the assumed 0.20–0.45 range;
  - for 0.30 outer crests you would need −0.22° (vintage), −0.26° (VT1), or H = 0.337 at 0°.
- **Recommendation:** keep a **0° (flat) pocket**, which is vintage. After measuring both bridges' saddle ranges, trim with the pocket or insertion depth (H). An angle tilts the hidden tongue 0.105 in per degree at x = 21.7, which costs the body carve [computed].

Figure: `fig/saddle_break.png`.

**Measure:** both bridges' min/max saddle crest above the plate; the VT1's knife-edge height and pivot-to-string-hole distance; the plate thickness; your real action.

---

## 8. Acoustic notes [computed unless tagged]

- **Headstock:** 248 g in all (80 g wood + 168 g tuners [lit: body/ergonomics/BALANCE.md]). The centre of mass is 3.98 in behind the nut and **0.69 in toward the treble side** when reversed, the mirror of a standard head.
  - The same mass gives the same neck-dive moment as a standard head, so BALANCE.md holds.
  - The off-axis mass couples twisting into the neck modes from the opposite side.
- **Neck modes:** clamped cantilever with a rigid headstock; for ranking only, not prediction. Plain 28.5 / 217.6 / 699 Hz; scalloped 27.3 / 211.4 / 681 Hz, about 3 % lower (about −50 ¢).
  - The second mode sits near A3/Ab3, 208–220 Hz.
  - In Eb standard, a mode at 211–218 Hz lands near G-string frets 2–3 (Ab3/A3) and D-string frets 7–8 [computed from the mode and tuning; dead spot itself judged].
  - **Tap-test the finished neck**; the real boundary is the set joint and tongue, which this model does not include.
- **Scallop mass removed:** 0.71 in³, **9.6 g**. That is acoustically minor next to the 248 g headstock. Its stiffness effect (+12 % relief, −3 % mode frequency) matters more than the mass.
- **Stainless loose frets:** about 1 g per fret [computed] and no stiffness contribution, by design.

---

## 9. Interface items for the body agent

1. **The asymmetric section** (u0 0.08, pb 2.30, pt 1.70) must feed the heel loft. The loft currently uses a symmetric p = 2.3. The depth law is unchanged: the loft starts at 0.946, which matches.
2. **Truss-rod type change:** BALANCE.md and STUDIES-neck-trem-guard.md assume a two-way rod adjusted at the headstock. The spec is now a single-acting curved rod with a body-end spoke wheel. This changes the rod mass location (small) and needs the **wheel access notch** (§5.3).
3. **Neck angle:** 0° recommended. Any angle tilts the tongue 0.105 in per degree at x = 21.7.
4. The **edge roll and domed fret ends end at the board end (18.594)**. The pickguard edge must clear the wheel.

---

## 10. Open questions for Jordan

1. **Nut string spread:** 1.375 is assumed. Measure your current nut. It sets the roll width and the edge margin.
2. **Saddle ranges** for both bridges, plus the VT1 knife-edge geometry (§7.2 list). These decide the pocket depth, H.
3. **Scallop feel:** the catch-free law gives 0.030 → 0.064 → 0.027 deep. Is that enough "scallop"? A deeper, Yngwie-style board would catch above about fret 15.
4. **Rebated fret seat** (0.010 step): smoother slides at low and mid frets, slightly softer look. Yes or no?
5. **Headstock face drop 0.10** for a stronger high-E seat: yes or no?
6. **Truss rod part:** which single-acting spoke-wheel rod? It needs about 275 lb of capacity and a 3/16 bar. Is the 0.23 in wheel access notch in the body and pickguard acceptable?
7. **Asymmetry amount:** 1.37 bass/treble shoulder ratio (repo default). Compare in hand against a neck you like, ideally with a 3-D-printed fret-1 and fret-12 section.
8. **Fret wire:** Jescar FW43080-S as the stainless "6230". Is the 0.080 × 0.043 crown OK?
9. **Action targets** at fret 17 (0.078 / 0.070 assumed for hard playing).
10. **Nut material:** bone with graphite, or Tusq XL?

---

## Sources (public spec pages)

- Jescar dimension guide (PLT): https://www.philadelphialuthiertools.com/content/final%20Jescar%20Dimensions%20guide.pdf
- Jescar FW43080-S listing: https://www.philadelphialuthiertools.com/fretwire/jescar-stainless-steel-fretwire-fw43080-s-electric-medium-pre-radiused
- Fret chart (Dunlop 6230): https://lutherie.net/fret.chart.html
- Gotoh SD91 MG-T, Rockinger: https://www.rockinger.com/en/parts/hardware/tuning-machines/guitar-tuners-6-left/2007/gotoh-vintage-back-lock-sd91-mg-t
- Gotoh SD91 MG-T, Thomann: https://www.thomannmusic.com/gotoh_sd91_05m_mg_t_locking_6r_n.htm
- Gotoh SD91 MG-T LH staggered, guitarhey: https://guitarhey.com/en-ca/products/new-gotoh-sd91-05m-mgt-locking-tuners-set-6-in-line-staggered-left-handed-gold
- Vega-Trem VT1: https://vegatrem.com/en/vt1-ultratrem-stratocaster-tremolo/ and https://www.thomannmusic.com/vegatrem_vt1_ultratrem_std_satin_gold.htm
- Fender setup guide: https://jp-support.fender.com/hc/en-us/articles/212774806-How-do-I-set-up-my-Fender-guitar-properly
- Scalloping: https://www.seymourduncan.com/blog/latest-updates/to-scallop-or-not-to-scallop
- Malmsteen neck dimensions (Custom Shop listing): https://willcuttguitars.com/products/fender-custom-shop-malmsteen-strat-snb-144-9235000895-r150144
- Repo, read only: body/carve/final_carve.py, body/acoustic-hybrid.md §0, body/ergonomics/BALANCE.md, body/sim/STUDIES-neck-trem-guard.md

---
---

# v2 (owner answers 2026-11-13)

v1 above is kept as the record. Where v2 and v1 disagree, v2 governs. Code: `neck_v2.py`, which imports `neck_model.py` and patches its depth, section, roll, scallop, EI and string-height functions. Results: `results_v2.json`. Figures: `fig/v2_*.png`.

## v2.0 Decisions at a glance

> **Review note (2026-11-13, after Jordan flagged "some of this looks physically impossible"):** the crown-tangent scallop (§v2.4), the rebated fret seat with filler fillets, and the clean-edge rail (§v2.3) are **WITHDRAWN as not buildable or not durable**.
> - **Filler fillets.** The fillets feather to zero thickness on polished stainless. They cannot be levelled or recrowned without destroying them, and the edges will chip under fingers and strings.
> - **Exposed crown.** The 0.008 exposed crown is smaller than a normal level-and-recrown takes off.
> - **Edge rail.** The rail is a thin rosewood fin sitting 0.008 below the crowns. The fret ends would be buried in it, so the frets could not be installed as drawn.
>
> **Replacement direction, pending a v3 check:**
> - frets fully proud and pressable, so they can be levelled and refretted normally;
> - the scallop meets the fret foot smoothly (v1 S5, optionally with a shallow step);
> - the scallop runs out through the board edge, the classic look, with no rail;
> - heavily rounded crowns and hemispherical ends.
>
> The ruled-loft depth and shape law and the 0.140 round-lam board stand. The bass "V-lean" in section A was the orchestrator's addition, not Jordan's: drop it, so the bass shoulder is fuller only, matched to the Musikraft SRV calipers.

| Item | v2 decision | Tag |
|---|---|---|
| Depth law | **MOD:** 0.90 at fret 1, linear in x to 0.96 at fret 12 (5.3 thou/in). 0.968 at the heel start x_h = 14.279 | [judged on computed options] |
| Shape law | **Ruled loft** between section A (nut: fuller, V-leaning bass) and section B (heel start: symmetric C, p 2.30) | [computed] |
| Board | **Round-laminate rosewood, uniform 0.140**, concentric with the conical radius, both faces CNC | [computed] |
| Scallop | **Crown-tangent.** Exposed crown e = 0.008, blend at h = 0.035 where the crown slope is 37.5°, fillet ρ ≥ 0.33. Leaves a rail at the edge (§v2.3) | [computed] |
| Fret seat | Rebate 0.080 wide × 0.035 deep. Press loose frets, then fill the undercut with CA/epoxy + rosewood dust and shape the fillet | [computed / judged] |
| Wire | **Keep Jescar FW43080-S** (0.080 × 0.043). SS6230 exists (0.079 × 0.039) but has less crown to bury | [lit / judged] |
| Rod | Deeper path: rod_z_end −0.30, sag 0.36. Needs about 241 lb at the MOD depth | [computed] |
| Body flags | New neck_depth law (0.968 at x_h vs 0.946), round-lam glue face at the tenon, crown-plane shift −0.035 | [computed] |

## v2.1 Depth: thick at the nut, the SRV reference, three growth options

### Published SRV and Musikraft numbers [lit]

| Profile | Fret 1 | Fret 12 | Shape note | Source |
|---|---|---|---|---|
| Musikraft SRV (your neck) | .84 | .97 | asymmetric | [lit: Musikraft back-profile chart] |
| Musikraft Chunky C-1 | .90 | .90 | C | [lit: Musikraft chart] |
| Musikraft Chunky C-2 | .90 | .99 | C | [lit: Musikraft chart] |
| Musikraft D | .90 | 1.00 | D | [lit: Musikraft chart] |
| Musikraft Fat C | 1.00 | 1.00 | C | [lit: Musikraft chart] |
| Musikraft AYS | .86 | .90 | — | [lit: Musikraft chart] |
| Warmoth SRV | .835 | .970 | "rounder on the thumb side, slimmer on the finger side" (bass fuller) | [lit: Warmoth neck profiles] |

- The Musikraft chart image is too small to show which side of the SRV is fuller. The bass-fuller claim comes from Warmoth's SRV, which has the same depths. **Confirm it on your neck** (calipers, below).
- Size of the asymmetry: a forum estimate puts the bass side 1–2 mm thicker at a quarter inset [lit: unofficialwarmoth forum, informal]. Warmoth calls the effect subtle.
- Your SRV adds **+0.13 from fret 1 to fret 12**. That is a steep taper.

### Three growth options from 0.90 at fret 1 [computed]

| Option | F1 | F5 | F9 | F12 | F17 | Slope (thou/in) | D at x_h |
|---|---|---|---|---|---|---|---|
| R: radius-proportional (v1 rule C at 0.90) | 0.900 | 0.953 | 0.996 | 1.022 | 1.056 | 10.8 | 1.038 |
| SRV: same +0.13 taper as your neck | 0.900 | 0.957 | 1.002 | 1.030 | 1.067 | 11.5 | 1.048 |
| **MOD: 0.90 → 0.96 (recommended)** | **0.900** | **0.926** | **0.947** | **0.960** | **0.977** | **5.3** | **0.968** |

Recommendation: **MOD** [judged]. You asked for thick where the thumb wraps over, near the nut. Higher up, where the thumb goes behind, MOD lands at about your SRV's absolute 0.97 at fret 12. R and SRV both pass 1.02 by fret 12, which is a baseball bat for thumb-behind playing. MOD is 0.06 fuller than your SRV at fret 1 and about 0.01 slimmer at fret 12.

Figure: `fig/v2_depth_options.png` (left: the three laws, v1 and the Musikraft points; right: asymmetry fading along the neck).

### Caliper readings to take on your Musikraft SRV

1. **Depth at frets 1, 5, 9 and 12.** Measure from the board surface between the D and G strings, just on the nut side of each fret, to the deepest point of the back. Also note the offset of the deepest point from the centreline, toward bass or treble, and by how much.
2. **Shoulder depth 0.25 in from each edge** at frets 1 and 12, bass and treble. This gives the asymmetry directly. The model gives 0.699 / 0.587 at fret 1.
3. **Width** at the nut and at fret 12.
4. **Board radius** (radius gauge), and whether it is compound.
5. Optional: a tracing with a contour gauge at frets 1 and 12. This is the best single input for fitting section A.

## v2.2 One shape rule along the neck: a ruled loft [computed]

With t = x / x_h (clipped to 0..1), u = 2y / W(x) and D(x) the MOD law:

  z(x, u) = −[ (1 − t) · D(0) · Φ_A(u) + t · D(x_h) · Φ_B(u) ]

- Φ_A and Φ_B are v1's normalised section shapes (apex offset u0, bass power pb, treble power pt).
- **A (nut):** u0 0.06, pb 2.40, pt 1.90. Fuller, rounder bass shoulder (apex 0.049 toward bass). **The V-lean is on the treble side** (pt 1.90 < 2), not the bass side.
- Why not a V-leaning bass: in this one-exponent family a V lean (p < 2) *removes* shoulder wood, so "fuller" and "V-leaning" pull opposite ways on the same side [computed]. Example at fret 1: A' = (0.10, 2.00, 2.20) puts the V on the bass side, but the bass is then only 0.3 mm fuller than the treble at the 0.25 inset; (0.10, 1.85, 2.30) makes the bass 0.9 mm *thinner*. If you want a true bass V with a full shoulder, it needs a third shape term (a ridge along the thumb line). That is a question for you (§v2.8 q3).
- **B (heel start, x_h = 14.279):** symmetric, p 2.30. This is **identical to the body loft's start section**, so the shapes join without a step.
- Each straight line from a point on A to the matching u on B lies on the surface. The surface is exactly ruled in normalised coordinates; the check deviation is about 1e-15. It can be cut with a side-of-tool pass along the rulings.
- Note: making the *parameters* (u0, pb, pt) linear in x would **not** be ruled, because Φ is nonlinear in them. That is why the rule blends the two sections, not their parameters.

Section A scan (fret-1 bass − treble depth at 0.25 in inset):

| A (u0, pb, pt) | Inset difference (in) |
|---|---|
| (0.12, 2.5, 1.7) | 0.202 |
| (0.08, 2.3, 1.7) | 0.158 |
| **(0.06, 2.4, 1.9)** | **0.112 (chosen, 2.8 mm)** |
| (0.05, 2.5, 2.0) | 0.099 |
| (0.04, 2.4, 2.0) | 0.082 (2.1 mm) |

The chosen A is deliberately a bit fuller than the 1–2 mm forum estimate for the SRV, because you play thumb-over at the nut [judged]. Your caliper readings should set the final A.

Shape along the neck (MOD) [computed]:

| Fret | t | Max depth | Apex offset (in, bass +) | 0.25 in inset bass / treble | Bass/treble shoulder ratio at 75 % depth |
|---|---|---|---|---|---|
| 1 | 0.10 | 0.902 | +0.049 | 0.699 / 0.587 | 1.216 |
| 5 | 0.45 | 0.927 | +0.044 | 0.683 / 0.613 | 1.121 |
| 9 | 0.72 | 0.948 | +0.032 | 0.671 / 0.635 | 1.056 |
| 12 | 0.89 | 0.960 | +0.018 | 0.663 / 0.649 | 1.021 |
| 17 | 1.00 | 0.977 | 0 | 0.657 / 0.657 | 1.000 |

- At fret 17 the body's heel loft governs. The section shown there is the neck law continued, for reference.
- v1's fixed 1.37 shoulder ratio is replaced: v2 runs from about 1.22 at the nut to 1.00 at the heel.

Figure: `fig/withdrawn_v2/v2_sections.png` (superseded by `fig/v3_profile_sections.png`) (left: true sections at frets 1/5/9/12/17 with the glue line dotted; right: normalised shapes).

### Heel join and body flags

- The neck section at x_h equals the body loft's start section (symmetric p 2.30), so the shape matches. **The depth does not:** the body uses 0.946 at x_h, and v2 needs **0.968** [computed].
- **The body agent must update** neck_depth to the MOD law (0.90 at fret 1, 0.96 at fret 12, linear in x), re-run the fret-15 heel deviation check, and update the tenon and pocket for the round-lam glue face (§v2.3). This agent has not edited body/carve.

## v2.3 Round-laminate rosewood board (1962 look) [computed]

- **Thickness t_b = 0.140**, uniform. It is the deepest scallop floor (0.099 below the board top, cell 14) + 0.040 of rosewood, rounded up to 0.005. That leaves **0.041** of rosewood under the deepest floor and **0.045** below the fret-slot bottom.
- **Glue face:** concentric with the conical top, z_g = −planed(x) − R(x) + √((R(x) − t_b)² − y²). The planed relief is cut into the maple top as well, so the rosewood stays uniform. Both faces are CNC cut.
- **Edge roll vs the glue line:** bass roll b = t_b − 0.025 = 0.115. The roll bottom sits 0.019–0.021 above the glue line at every fret checked (1, 5, 9, 12, 17, 22), so **the roll stays in rosewood and never exposes maple**. The glue line meets the side about 0.140 below the board top.
- **Clean line:** with v1's 40 % edge fade, the board-top line at the edge would wobble by 0.040 between frets. **v2 sets edge fade 0**: the scallop fades out before the edge, the edge line is straight, and the glue line is smooth. Fret ends at the edge are buried by h, with only 0.008 exposed.
- **The price of the clean line: an edge rail** [computed]. Full scallop depth runs to 0.03 outside each outer string. It then fades to zero over a band only **0.045 wide** before the roll starts. So a rosewood rail at full board-top height stands beside the outer strings:
  - lateral wall slope up to **69–76°** (cells 1–22), wall height = the floor depth (0.064–0.099);
  - inside the fade band the fillet radius drops below the fingertip, and the catch along x returns: **13–31°** at 25–75 % depth (cells 1, 7, 12, 14, 17, 22);
  - on the outer strings the finger pad partly rides the rail, which is only 0.008 below the crown tops. Those strings will feel like near-flush frets, not scallops.
- Ways out, all trading the clean line [judged]: keep some depth at the edge (edge fade 10–15 % gives about 0.010–0.015 of wobble and only lowers the wall slightly), or scallop through the edge like a classic scalloped board (wobble up to 0.099 and a roll that must shrink to stay off the glue line). The rail is the 1962-clean-edge choice; **owner question §v2.8 q8**.

Figure: `fig/withdrawn_v2/v2_roundlam_edge.png` (withdrawn) (sections at fret 12 and mid-cell 14, bass-edge close-up, side elevation of frets 9–16).

## v2.4 Crown-tangent scallop [computed unless tagged]

### Law (frets 1–22)

The fret is seated h = 0.043 − e into a rebate; e is the exposed crown. The crown is an ellipse with a = 0.040, b = 0.043.

- Blend point: x_b = a·√(1 − (h/b)²); slope m = b²·x_b / (a²·h); θ = atan m.
- From the blend point the wood follows a circular fillet of radius ρ_k, tangent to the crown, then a flat floor.
- Per cell k: Δ_k = clip(h + d_v1(k), ρ_min·(1 − cos θ), S_k·tan(θ/2)); ρ_k = Δ_k / (1 − cos θ); S_k = L_k/2 − x_b; ρ_min = 0.33. Here d_v1 is v1's depth law, and Δ_k is the floor depth below the board top.
- Lateral fade scales ρ by w(y), which keeps the tangency everywhere.
- **e = 0.008:** h 0.035, θ 37.5°, x_b 0.0232.
- Floor below the board top: 0.068 (cell 1), 0.095 (12), **0.099 (14, max)**, 0.083 (17), 0.064 (22). Fillet radii 0.33–0.48; fillet lengths 0.19–0.29; floor lengths 0.98 (cell 1) falling to 0 (cell 22). Removed volume 2.0 in³ (v1 0.71).

### The undercut, and how to build it

Wood tangent to the crown at h > 0 sits **above the crown's lower flank**. A fret cannot be pressed into it afterwards. The build is:

1. CNC the rebate 0.080 wide × 0.035 deep and the slot 0.025.
2. Press the loose frets.
3. Fill the gap between the crown flank and the fillet with CA or epoxy + rosewood dust: **about 7.1e-5 in² per side**, per unit length, at cell 13.
4. Shape the fillets tangent to the crown, with a radius block, after levelling.

- **Refret:** heat the fret, break out the filler, pull the fret, then repeat from step 2.
- **Levelling** removes crown height only and leaves the tangency. With e = 0.008 the levelling budget is small [judged]. Stainless wears slowly, so that is acceptable, but plan on a light level only.
- Alternative: slide the frets in sideways into a captured groove. This leaves a fragile feather edge; not recommended [judged].

### Choosing e (fingertip catch, rigid R 0.30) [computed]

| | Catch, cells 1–19 | Cell 22 | Max uphill slope |
|---|---|---|---|
| Unscalloped board | 25.5–26.8° | 25.5° | 29.0° |
| v1 S5 (flat at the crown foot) | 14.9–26.8° | 24.8° | 29.6–36.0° |
| v1 + 0.010 rebate | 11.2–26.8° | 24.8° | 25.8–31.0° |
| v2 e 0.006 | 0.2–0.5° | 1.2° | 32.3° |
| **v2 e 0.008** | **0.4–2.3°** | **5.9°** | **37.4°** |
| v2 e 0.010 | 1.0–2.5° | **61.2°** | 41.7° |

- All 22 cells sampled for e 0.008: 0.4–2.3° in cells 1–21 (2.0° at 20, 2.3° at 21), 5.9° at cell 22. e = 0.008 is the largest exposure with no catch up to fret 22. The model's noise floor is about 1.3° (v1). These are centreline values; the edge rail is separate (§v2.3).
- Catch-free requires the fillet radius ≥ the fingertip radius. That is why ρ_min = 0.33.
- At e = 0.010 the top cells are too short to fit a ρ ≥ 0.30 fillet, and the catch returns (51.6° at cell 21, 61.2° at cell 22).

### Fretted-string clearance (v1 action) [computed]

- **Speaking side:** the wood is always at least e below the crown top, so the string can never touch wood before a fret, as long as e > 0.
- **Dead side:** with the finger at mid-cell, the string first touches the fillet at a press depth of 0.051 (cell 1), 0.026 (cell 12) and 0.015 (cell 22). This is on the damped side, so it is harmless.
- **Press-sharp:** pressing all the way to the floor gives E4 cell 12 +136 ¢ and G3 cell 12 +385 ¢ (upper bound). At 0.043 press, +24 ¢ and +68 ¢, the same as v1. As with any scallop, the risk is in the hand.

Figure: `fig/withdrawn_v2/v2_blend.png` (withdrawn) (cell-13 close-up: crown, rebate, filler, fillet and the v1 profile overlaid; catch per cell for v1 and v2).

### Crown-plane shift

The crowns now stand e = 0.008 above the board-top datum, not 0.043. **For the same action, the strings sit 0.035 lower relative to the board top.** The §7 saddle crests and the nut slot heights shift by about −0.035 [computed]. Either the saddles drop by 0.035 or the neck sits 0.035 lower in the pocket; that is a body-agent decision.

## v2.5 Wire [lit / judged]

| Wire | Crown | Tang | Barb | Loose slot | Source |
|---|---|---|---|---|---|
| Allparts LT-0891-005 (≈ Dunlop SS6230, "Used on Vintage Fender®") | 2.00 × 1.00 mm (0.079 × 0.039) | 0.024 | 0.037 | ≈ 0.030 | [lit: Allparts fret wire overview; column labels on the page are garbled] |
| **Jescar FW43080-S** | **0.080 × 0.043** | **0.020** | **0.032** | **0.025** | [lit: Jescar guide] |

- **v1 erratum:** a stainless 6230 does exist.
- **Keep Jescar** [judged]. Its 0.043 crown leaves 0.035 to bury and 0.008 exposed. SS6230's 0.039 crown would give h 0.031 at the same e, a flatter blend (smaller θ) and no extra levelling budget. The loose 0.025 slot is unchanged.

## v2.6 Stiffness, relief, rod and modes [computed]

- **EI v2 / v1:** 1.39 (fret 1), 1.28 (5), 1.21 (9), 1.18 (12). The thicker neck outweighs the deeper scallops.
- **Planed relief:** sagitta 0.0093 (gap 0.0073 under the 1–16 chord).
- **Tension bow, rod slack (MOD, soft / nominal / stiff maple):**

| Tuning | Flat board | Scalloped |
|---|---|---|
| E standard | 0.0092 / 0.0086 / 0.0081 | 0.0126 / 0.0116 / 0.0106 |
| Eb standard | 0.0082 / 0.0077 / 0.0072 | 0.0112 / 0.0103 / 0.0094 |
| Eb drop C# | 0.0079 / 0.0074 / 0.0069 | 0.0108 / 0.0099 / 0.0091 |

- The crown-tangent scallops add about **35 % relief** (v1: about 12 %), because the floors are deeper (up to 0.099 vs 0.064) [judged reason].
- Slack-rod relief at Eb nominal: 0.0103 + 0.0073 ≈ **0.018**. That is above your 0.012.
- **Rod path:** the v1 path was too shallow for the thicker neck (0.0019 per 100 lb, needing about 504 lb). v2 path: rod_z_end −0.30, sag 0.36, about 0.19 of maple under the rod at x = 9. It gives **0.0041 per 100 lb**. Removing 0.0098 needs **about 241 lb** (v1: 275 lb).
- For comparison, depth law R needs about 294 lb on the same path.
- **Modes (free–clamped beam):** plain 31.2 / 238 / 767 Hz; scalloped 28.2 / 222 / 715 Hz, about 7 % lower.

## v2.7 Interface items for the body agent (supersedes v1 §9 item 1)

1. **neck_depth law:** 0.90 at fret 1, 0.96 at fret 12, linear in x; **0.968 at x_h**, not 0.946. The section at x_h is unchanged (symmetric p 2.30). Re-run heel_dev_at_fret15.
2. **Round-lam glue face** (concentric cone, 0.140 below the board top) meets the tenon and pocket. The tongue and pocket floor follow it.
3. **Crown-plane shift −0.035:** saddle crest and pocket height H (§7).
4. **Spoke-wheel packaging (v1 §5.3) is stale:** the rod end moved to −0.30 and the crown plane dropped 0.035. The wheel centre height and the 0.23 access notch must be recomputed with the body geometry.
5. Neck mass changes: thicker maple, and 2.0 in³ of rosewood removed by scallops (about 28 g at 0.85 g/cc [judged density]). Re-run balance.

## v2.8 Questions for Jordan

1. **Caliper readings** on your Musikraft SRV (list in §v2.1). Most important: which side is fuller, and the 0.25 in inset depths at frets 1 and 12.
2. **Depth law:** MOD (0.90 → 0.96) recommended. Do you want more growth (R or SRV, about 1.02–1.03 at fret 12)?
3. **Asymmetry at the nut:** 2.8 mm bass-over-treble at the 0.25 inset, versus about 1–2 mm reported for the SRV. Keep it or tone it down? And the V lean: it is on the treble side now, because a V-leaning bass loses shoulder wood. Do you want the V on the bass (thumb) side instead, accepting a thinner bass shoulder?
4. **Exposed crown e = 0.008:** a near-seamless feel but a small levelling budget. e = 0.006 is even smoother but has less budget still. OK?
5. **Filled-undercut fret seat:** acceptable for refrets (heat, break filler, pull)? The alternative, side-slid frets, is fragile.
6. **Truss rod:** a single-acting rod good for about 250 lb, on the deeper path.
7. **Board thickness 0.140** round-lam: OK for the look? The glue line shows on the neck sides below the roll.
8. **Edge rail vs clean edge:** a straight edge line leaves a 0.045-wide fade and a steep rail beside the outer strings (outer strings feel near-flush). Keep it, keep 10–15 % depth at the edge, or scallop through the edge?
9. **Depth datum:** are your 0.90 and Musikraft's .84/.97 measured over the frets or over the wood? With only 0.008 of crown showing, a v2 neck feels about 0.035 thinner over the frets than a normal neck with the same wood depth.

## v2 sources (public spec pages)

- Musikraft back-profile chart: https://www.musikraft.com/back-profile-guitar-6-string
- Warmoth neck profiles: https://warmoth.com/guitar-neck-profiles
- Warmoth on asymmetric profiles: https://warmoth.com/blog/assymetric-neck-profiles
- Forum SRV asymmetry estimate (informal): https://unofficialwarmoth.com/threads/asymmetric-neck-contour-profiles-srv-wolfgang-why-not-more-popular.33077/latest
- Allparts fret wire overview: https://www.allparts.com/pages/fret-wire-overview

---
---

# v3 (2026-11-13): the buildable scallop, edge and fret ends

v2's crown-tangent scallop, rebated seat, filler fillets and edge rail are withdrawn (note at §v2.0). Their figures are in `fig/withdrawn_v2/`. v3 keeps v2's depth law (0.90 → 0.96), the ruled loft, the 0.140 round-lam board, the deeper rod path and the Jescar FW43080-S wire.

Owner target: "scallops and rolled edges and round frets that disappear into the side of the neck".

Owner inputs after the first v3 brief: the strings must not slip off; keep the vintage nut string spacing but make the **neck slightly wider** along its length, and use the extra width for a bigger roll.

Code: `neck_v3.py`, which imports `neck_v2.py` and `neck_model.py`. Results: `results_v3.json`. Figures: `fig/v3_*.png`.

## v3.0 Decisions at a glance

| Item | v3 decision | Tag |
|---|---|---|
| Neck width | Vintage width law **+0.030 per side**, constant along the neck. Nut 1.710, fret 12 2.101, fret 21 2.260 | [computed from a judged rule] |
| String spread | Vintage: 1.375 at the nut, 2-7/32 at the bridge | [owner] |
| Frets | **Fully proud** on the full-height board top, in normal stopped slots. Pressed and glued; level, recrown and refret as normal. No rebate, no filler | [judged] |
| Fret ends | Ellipsoid end 0.040 (along the neck) × 0.025 (across) × 0.043 high. The apex sits on the full-height land at the roll start, 0.033 from the edge | [computed] |
| Slots | Stopped 0.063 from the edge; tang nipped 0.068 from the edge | [computed] |
| Edge roll | Quarter ellipse, a = 0.033 across × b = 0.105 down, both sides. The roll bottom is 0.035 above the glue line | [computed] |
| Scallop | v1 S5 law from the crown foot (0.030 → 0.064 at cell 14 → 0.027). Full depth to the roll start, then **through the roll**, fading to zero at the roll bottom | [computed] |
| Section A | (u0 0.05, pb 2.60, pt 2.30). Fuller bass shoulder only; the treble is the heel C, with no V | [judged on a scan] |
| CNC | 1/4 in ball end (R 0.125). The smallest concave radius on the board is 0.195 | [computed] |

## v3.1 Width: a bend-room rule, then the slip-off margin

**About the bend directions as stated.** Bending the high E up, or pulling the low E down, moves the string *inward*, away from its edge. A two-step bend at frets 12–17 moves it roughly 1.1 in (high E) or 0.6 in (low E) [computed estimate: steel EA, Eb tension, stretch shared over the scale; the friction model changes the figure, not the direction]. So the edge does not limit those bends. What the edge does do is support the fingertip, which sits *outboard* of the string while it pushes.

- **Rule [judged]:** string centre to board edge ≥ 0.150 at frets 12–17. That is half a fingertip contact patch of about 0.30.
- A vintage neck gives 0.122 at fret 12 and 0.118 at fret 17 [computed: 1.650 → 2.200 width law, vintage spread].
- **Widening needed: 0.028 to 0.032 per side** (fret 12 to fret 17) [computed]. **Chosen: 0.030 per side, constant.** That gives 0.152 at fret 12 and 0.148 at fret 17, within 0.002 of the rule.

Widths [computed]:

| Station | Nut | Fret 1 | Fret 12 | Fret 21 | Heel start x_h | Pocket datum 15.69 | Tongue end 21.7 |
|---|---|---|---|---|---|---|---|
| Vintage | 1.650 | 1.694 | 2.041 | 2.200 | 2.088 | 2.132 | 2.316 |
| **v3** | **1.710** | **1.754** | **2.101** | **2.260** | **2.148** | **2.192** | **2.376** |

- **Nut:** 1.710 wide (about 1-23/32), with vintage 1.375 E-to-E spacing.
- Alternative [judged]: ramp the widening, +0.020 at the nut to +0.035 at fret 21. That gives a 1.690 nut but only 0.147 at fret 17.

### Slip-off margin: string centre to the usable crown end [computed]

"Usable" means the crown is still at least 90 % of its height. The vintage reference is ends bevelled flush with the edge at 35° from vertical [judged bevel]; there, 90 % height is reached 0.027 in from the edge.

| Station | Nut | Fret 1 | Fret 12 | Fret 21 |
|---|---|---|---|---|
| Vintage (1.650 nut), usable margin | 0.110 | 0.109 | 0.095 | 0.089 |
| **v3, usable margin** | **0.120** | **0.119** | **0.105** | **0.099** |
| Vintage, string to edge | 0.138 | 0.136 | 0.122 | 0.116 |
| v3, string to edge | 0.168 | 0.166 | 0.152 | 0.146 |
| v3 with VT1 bridge spacing, usable margin | — | 0.122 | 0.133 | 0.139 |

- v3 keeps **0.010 more usable crown than a vintage Strat** everywhere. The usable crown ends 0.047 from the v3 edge, which is 0.010 further out than on a vintage neck (0.027 from its edge). The other 0.020 of the extra 0.030 per side goes into the roll (a = 0.033). **Playable width lost: none**; the usable crown is +0.010 over vintage at every station.
- Edge-ward vibrato room before the string leaves the usable crown, at frets 12 and 17 [computed]: high E 4.6 ¢ (vintage 3.8 ¢), low E 14.4 ¢ (vintage 11.8 ¢). On any neck an edge-ward bend runs out of fret within a few cents. The margin protects against slip-off during fretting and vibrato, not against edge-ward bends.

### Hand feel vs v2 [computed]

"Hand girth" is the section perimeter minus the flat top between the roll starts, with no scallop.

| Station | Nut | Fret 1 | Fret 5 | Fret 12 | Fret 17 | Fret 21 |
|---|---|---|---|---|---|---|
| v2 hand girth | 2.689 | 2.728 | 2.873 | 3.083 | 3.195 | 3.245 |
| v3 hand girth | 2.769 | 2.804 | 2.933 | 3.124 | 3.228 | 3.281 |
| Change | **+0.080 (2.0 mm)** | +0.076 | +0.061 | +0.041 | +0.033 | +0.036 |
| Full perimeter change | +0.201 | +0.194 | +0.165 | +0.125 | +0.113 | +0.111 |

- Where the extra girth comes from [computed]: the v3 shape *without* widening has a hand girth of 2.706 at the nut and 3.061 at fret 12. So **section A adds +0.017 at the nut** (−0.022 at fret 12), and **the widening adds +0.063** at both.
- **Correction to the brief's intent: the roll is not bigger and does not blend into the back.** Widening scales the whole section, so the extra width goes into girth. The v3 roll (0.033 × 0.105) is *smaller* than v1/v2's (0.047–0.061 × 0.115). It is a rounded top corner over a near-vertical side that runs through the glue line (`fig/v3_sections.png`).
- **Why [computed / judged]:** the constraints fight each other. They are a 0.140 board; a roll that stays in rosewood (b ≤ 0.105, glue 0.035 below); frets reaching to a vintage-or-better usable margin; and a frozen shape law. Together they leave a = widen + 0.027 − margin_extra − 0.564·end_c of room for the roll, and its depth is capped by the board. A roll that truly blends into the neck back needs one of two changes, each breaking a stated rule:
  1. **Continue the round-over through the glue line into the maple shoulder.** This is the 1962 round-lam look, with the glue line visible on the curve. It breaks "the rolled edge never exposes maple".
  2. **Keep the back below the board on the vintage width law and blend a shoulder up to the wider board.** This breaks "shape law unchanged" and gives back most of the girth increase.

Trade-off, verified by rerun [computed] (girth = hand girth; slide = the 45° edge-pad slope jump at frets 5 / 12 / 19):

| widen / side | margin over vintage | end c | roll a | usable margin, nut / f12 | hand girth, nut / f12 | slide (°) |
|---|---|---|---|---|---|---|
| 0 | +0.010 | 0.025 | 0.003 | 0.120 / 0.105 | 2.706 / 3.061 | 16.1 / 9.5 / 12.0 |
| **0.030 (rec.)** | **+0.010** | **0.025** | **0.033** | **0.120 / 0.105** | **2.769 / 3.124** | **14.2 / 14.0 / 12.3** |
| 0.030 | 0 (= vintage) | 0.025 | 0.043 | 0.110 / 0.095 | 2.782 / 3.131 | 8.4 / 11.5 / 11.9 |
| 0.030 | 0 | 0.040 | 0.035 | 0.110 / 0.095 | 2.772 / 3.123 | 12.9 / 11.8 / 11.8 |

- Setting the margin exactly to vintage buys the v2-size roll (0.043) and a softer edge slide. Rounder ends (c 0.040) do not help the slide much.

## v3.2 Section rule (v2 ruled loft, new A) [computed]

- A = (0.05, 2.60, 2.30), B = symmetric p 2.30. The surface is exactly ruled (deviation 6e-16).
- Fret 1: high point +0.035 toward bass; 0.25 in from each edge, bass 0.709 / treble 0.651 deep, i.e. **1.5 mm fuller on the bass**, matching the 1–2 mm forum estimate for the SRV. Shoulder ratio 1.095.
- Fret 12: 0.656 / 0.648 (0.2 mm). Fret 17: symmetric.
- A scan for reference, fret-1 bass over treble: (0.06, 2.4, 2.3) 1.0 mm; (0.05, 2.5, 2.3) 1.2 mm; **(0.05, 2.6, 2.3) 1.5 mm**; (0.04, 2.8, 2.3) 1.9 mm. Set the final value from the owner's caliper readings.
- Figure: `fig/v3_profile_sections.png`.

## v3.3 Scallop, edge roll and fret ends

### Scallop through the edge [computed]

- Centreline law, unchanged from v1 §3.2: d_k = min(0.030 + 0.045 ξ_k, 0.15 L_k²), applied as a full-span S5 from each crown foot. So the wood is at full height under and beside every fret.
- **Across the board:** full depth right out to the roll start; there is no lateral fade on the top.
- **In the roll:** with q = (|y| − y_c)/a_h and cos φ = √(1 − q²),

  drop(x, y) = d(x)·cos φ + b·(1 − cos φ)

  At mid-cell the roll is the same quarter ellipse, squashed to height b − d and starting d lower. At a fret it is the full roll.
- Seen from the side, the edge top line dips the full scallop depth between frets, the classic look. The **roll bottom line stays straight**, and so does the glue line below it. See `fig/v3_side_edge.png`.
- **No rail and no fin:** the surface falls monotonically from the centre outward at every x. The largest outward rise found is 0.000 [computed, 900 stations]. Where the roll would be shallower than the local scallop it is deepened to d + 0.010. That did not happen on either side: b is 0.105 everywhere and d ≤ 0.064.

### Edge roll and the round-lam glue line [computed]

- a = 0.033 across, b = 0.105 down, on both sides. The roll bottom is **0.035 above the glue line** at every station.
- The lowest point of any top surface (flat, scallop or roll) is 0.037 above the glue line, at x = 14.5 on the treble edge. That meets the ≥ 0.030 requirement. The roll never exposes maple.
- The glue line shows on the neck side 0.035 below the roll bottom.

### Fret ends that disappear into the side [computed unless tagged]

| Dimension | Value (from the board edge) |
|---|---|
| End apex (= roll start, on the full-height nib) | 0.033 |
| Usable crown (≥ 90 % height) ends | 0.047 |
| Full-height crown ends | 0.058 |
| Stopped slot ends (0.025 wide, round end) | 0.063 |
| Tang nipped back to | 0.068 (0.035 behind the apex) |

- **End shape:** an ellipsoid with semi-axes 0.040 (= crown half-width) × 0.025 × 0.043. In plan it is a rounded nose; seen from the side it is just the crown profile. The steel stops at the roll start, and the wood "nib" under it is the full-height S5 shoulder at each fret, so the roll continues past the end. See `fig/v3_fret_end_top.png` and `fig/v3_render.png`.
- **No steel on the roll or the side.**
- **Hand sliding along the edge:** I used a rigid R 0.30 pad held at 45° against the edge. Wood alone gives a 0.04–4.4° path slope jump. With the fret ends it is **12–14°**, with a 0.03–0.05 rise. You will feel smooth bumps but no edges. For scale, crossing a fret on top of an unscalloped board is about 25°.
- The extra margin can buy rounder ends instead: each +0.010 of end_c costs 0.0056 of usable margin [computed].

## v3.4 Physical sanity checks [computed unless tagged]

| Check | Result |
|---|---|
| Rosewood under the deepest scallop (cell 14) | 0.076 |
| Rosewood under the slot bottom | 0.080 |
| Any top surface above the glue line (including the roll) | ≥ 0.037 |
| Rosewood between the slot end and the rolled surface | 0.030 at the top; 0.040–0.056 at 0.010–0.060 deep |
| Maple between the rod top and the glue face | ≥ 0.068 (x = 18.35) |
| Maple under the rod, centreline | ≥ 0.185 (x = 8.4) |
| Feather edges | None. The fret sits on full-height land, so the board-to-crown junction is a 90° corner under steel. The S5 starts with zero slope at the crown foot. The roll ends tangent to the side. The slot end is a 90° stopped wall |
| Wood standing within 0.03 of a crown top | None. Wood is 0.043 below the crown top, leaving **0.013 of levelling budget** before this rule is reached |
| Frets installable in the build order | Yes (below) |
| CNC ball end | Smallest concave radius 0.195 (cell 22, S5 foot). **Use a 1/4 in ball (R 0.125).** The roll and the board radius are convex |
| Fingertip catch, v1 law, all 22 cells | 11.5–28.6° against a flat board's 25.5–28.5°. **Cell 20 is +3.1° over flat**, beyond the 1.3° noise. v1 sampled only 11 cells and missed it. Optional fix: κ 0.15 → 0.14 for cells 20–21 [judged] |

### Build order

1. **Maple neck (CNC):** truss-rod channel (v2 path); glue face = the conical radius 0.140 below the top, with the planed relief cut in; rough back.
2. **Rosewood blank (CNC):** concave glue face matching the neck; oversize top. Glue it on with a radius caul and fit the rod and filler first.
3. **Board top (CNC):** compound radius plus planed relief and fall-away.
4. **Stopped slots:** 0.025 end mill, 0.060 deep, ending 0.063 from the edge, indexed off the scale.
5. **Scallops and edge roll in one ball-end pass** (1/4 in ball, fine stepover). Then the neck back and the heel blend. Hand-sand the scallops only along x.
6. **Finish or oil the board.** Mask the slots.
7. **Prepare the wire:** pre-radiused Jescar FW43080-S cut to length with the end shape allowance; nip the tang back 0.035 from each apex.
8. **Press and glue the frets:** radius caul; a wick of thin CA or a dab of epoxy at each end [judged]. The loose 0.025 slot keeps the board from back-bowing.
9. **Dress the ends:** file the ellipsoid ends (0.040 × 0.025) with a concave end file, masking the roll and nib with tape. Then level, crown and polish.
10. **Refret:** heat each fret, pull with flush pullers working from the ends, clean the slots, and reuse them. These are stopped slots with nipped tangs, so the job is the same as on a bound neck.

## v3.5 Stiffness, relief, rod and modes (v3 geometry) [computed]

- Planed relief: sagitta 0.0109 (gap 0.0085). The shallower v1 scallops (0.75 in³ removed, vs 2.0 in v2) need a little more planed relief.
- Tension bow, scalloped, Eb nominal: **0.0088** (flat 0.0079). Slack-rod relief ≈ 0.0088 + 0.0085 ≈ **0.017**, above the owner's 0.012.
- Rod: 0.0036 in per 100 lb; removing 0.0091 needs **about 250 lb** (v2 said 241).
- Modes: plain 31.8 / 241 / 778 Hz; scalloped 30.5 / 235 / 759 Hz.

## v3.6 Body-agent items (supersede v2 §v2.7)

1. **Neck width +0.060** total along the whole neck: heel loft, pocket and tongue (2.148 at x_h, 2.192 at the pocket datum, 2.376 at x = 21.7). Pickguard neck cut-out and pocket CNC as well.
2. **neck_depth** = MOD law (0.968 at x_h). Section B at x_h unchanged (symmetric p 2.30). Re-run heel_dev_at_fret15.
3. **The crown-plane shift is withdrawn.** Frets sit on the board top as in v1, so the §7 saddle and nut heights stand.
4. **Round-lam glue face** (0.140 below the top, concentric) meets the tenon and pocket.
5. **Spoke-wheel packaging** must be rechecked for the v2/v3 rod path (rod end −0.30).
6. Neck mass: wider and thicker, with less scallop removed (0.75 in³). Re-run balance.

## v3.7 Owner decisions

1. **Width +0.030 per side** (1.710 nut, 2.260 at fret 21), or the ramp (+0.020 → +0.035, 1.690 nut)? Hand girth goes up 1–2 mm.
2. **Usable-crown margin vintage + 0.010:** keep it, or spend it on rounder fret ends (smoother edge slide) or a wider roll?
3. **Fret-end feel:** you will feel smooth bumps along the edge (about 12–14° on the pad metric). Acceptable?
4. **Section A:** 1.5 mm fuller bass at fret 1. Confirm with calipers on your Musikraft SRV (§v2.1 list).
5. **Cell 20 catch** (+3° over flat): trim κ to 0.14 there?
6. **Depth datum:** are your 0.90 and Musikraft's .84/.97 measured over the frets or over the wood? (Frets are proud again, so the v2 caveat no longer applies.)
7. **Roll vs constraints:** v3 cannot give a big roll that blends into the back. Choose one: (a) accept the 0.033 roll; (b) margin exactly vintage for a 0.043 roll; (c) round-over through the glue line into maple (1962 look, glue line on the curve); (d) vintage-width back with a shoulder blend up to the wider board (changes the shape law, recovers girth).

# v3.1 revision (2026-11-13): roll option d + fret ends that blend into the board

This revision changes v3 in two ways: the owner chose roll option d, and the fret ends now blend into the board in steel. The section numbers below are §v31.x. They are separate from v3's own "§v3.1 Width". Code: `neck_v31.py`, which imports and patches `neck_v3.py`. Results: `results_v31.json`. Figures: `fig/v31_*.png`. Everything not listed here stays as in v3.

## v31.0 Headline [computed unless tagged]

- **A 0.06–0.08 board-top roll cannot fit at +0.030, whatever the fret end looks like.** The usable crown must reach at least the vintage position. From the board edge to the vintage usable end is only 0.030 + 0.027 = **0.057**. So even a square-cut fret with no taper leaves a ≤ 0.057 − margin = **0.054**.
- **The taper makes the shortfall worse.** With the S5 taper, its run beyond its own 90 % point is 0.743·L, so a = widen + 0.027 − margin − 0.743·L. A 0.06–0.10 taper alone uses 0.045–0.074, the whole budget. A profile that holds full height longer shortens that run but makes the end steeper.
- **Steel cannot follow the roll down.** I tested pre-bending the thinned end over a G2 roll entry (§v31.4). With a 0.06–0.08 roll, a tip that drops only 0.005 needs 4–19 % bending strain. A 0.010 drop needs 6–33 %. Cold-worked stainless wire elongation is 1–8 % [lit: Ulbrich 302/304 data sheets, §v3.1 sources]. So the only buildable end is a **ground-only taper on flat, full-height wood, with the tip at the roll start**. The wood roll then starts where the steel ends. It does not run under the steel.
- **Option d does not bring girth back to v2.** Take any *convex* section that holds the +0.030 board (corners unrolled) and the vintage-width back. Its hand girth is about 2.758 at the nut and 3.114 at fret 12. That is the convex-hull bound; rolled corners can sit up to about 0.02 below it. v3.1 is 2.759 / 3.122. v2 is 2.689 / 3.083. Most of the v3 girth increase comes from the board itself.
- **The roll target ("reads at least as large as v2's") is not met on the board top.**
  - Board-top width: 0.024 against v2's 0.041–0.061.
  - Corner radius: 0.017 against v2's 0.026 at fret 1. That is worse near the nut, though better than v2 at frets 12 and 21 (v2 0.012 and 0.008); the crossover lies between frets 1 and 12.
  - What *is* larger is the shoulder below the board: it comes in 0.15–0.22 over 0.46 of depth.
  - Option: a circular roll (n = 2, a = b) raises the corner radius to 0.024 [computed: a²/b], at the cost of G2 at the top and wall joins (G1 there, as in v1–v3).
- **Recommended (built and checked):**
  - width +0.030 per side, as in v3;
  - usable margin vintage + 0.003;
  - taper L 0.040, tip 0.004;
  - board-top roll 0.024 × 0.024 (superellipse n 2.5, G2 to the top and to the side wall);
  - straight side wall to 0.088;
  - G2 quintic shoulder joining the vintage-width back 0.55 below the edge;
  - κ 0.145.

## v31.1 Section law: option d (one law, both end sections updated) [computed]

- **Back:** the v3 ruled loft is unchanged: MOD depth, A = (0.05, 2.60, 2.30), B = (0, 2.3, 2.3). It now uses u = 2y/W_v(x) on the **vintage width** (1.650 → 2.20 at fret 21), so it is exactly ruled (second difference 1e-15).
- **Edge, in edge coordinates (s = depth below the board-top edge), the same at every x:**
  1. flat top;
  2. superellipse roll, a 0.024 across × b 0.024 down, n 2.5. It has zero curvature at both ends, so it meets the top and the side wall G2. Minimum radius 0.017;
  3. straight side wall at W/2 down to s_v = b + d_max = 0.088. At mid-cell the roll is shifted down by the scallop depth d; at the deepest cell (14) the wall has zero length;
  4. quintic shoulder from s_v to s_j = 0.55, with y′ = y″ = 0 at the top. At the bottom it matches the back's value, slope and curvature, so it is G2;
  5. the back.
- **Why s_j = 0.55:** it is the shallowest join that keeps the outline monotone and convex (y″ ≤ 0) on both sides at every station. Joins at 0.20–0.525 give a waisted, concave shoulder (scan in the results). This follows from the vintage back's tangent lines, not from the quintic: the hull bound above says the same.
- **Ruled check: this is a deviation from "one ruled loft".** The back is exactly ruled. The shoulder band deviates at most **0.008** from straight lines between section A and section B, because its join is at a fixed depth while the back changes along x. It is one law (the same construction at every x) but not exactly ruled. It could be made exactly ruled by joining at fixed u and ruling the shoulder too, then re-checking convexity mid-span. Not done; owner or coordinator call.
- **Figures:**
  - `fig/v31_profile_sections.png`: sections A, fret 12 and B against v2 and v3;
  - `fig/v31_sections.png`: fret 12 and mid-cell 14 with edge close-ups.

| Edge metric [computed] | v2 | v3 | **v3.1** |
|---|---|---|---|
| Board-top roll width (fret 1 / 12 / 21) | 0.061 / 0.047 / 0.041 | 0.033 | **0.024** |
| Roll depth on the side | 0.115 | 0.105 | **0.024 roll + straight wall to 0.088 + shoulder to 0.55** |
| Smallest edge radius (fret 1 / 12 / 21) | 0.026 / 0.012 / 0.008 | 0.008 / 0.006 / 0.005 | **0.017 everywhere** |
| Inset from the board edge to where the shoulder meets the back | none (the back reaches the edge) | none | **0.15–0.22** |
| Side angle where the glue line meets it | (side wall) | (side wall) | 2.6–3.9° from vertical, so no feather edge |

So against v2 the board-top roll is narrower, and its corner radius is smaller near the nut and larger from mid-neck. The extra width goes into the shoulder under the board.

**Hand girth** (perimeter less the flat top between the roll starts) [computed]:

| Station | v2 | v3 | **v3.1** | Convex bound |
|---|---|---|---|---|
| Nut | 2.689 | 2.769 | **2.759** | 2.758 |
| Fret 1 | 2.728 | 2.804 | **2.795** | 2.792 |
| Fret 5 | 2.873 | 2.933 | **2.929** | 2.923 |
| Fret 12 | 3.083 | 3.124 | **3.122** | 3.114 |
| Fret 17 | 3.195 | 3.228 | **3.231** | 3.220 |
| Fret 21 | 3.245 | 3.281 | **3.286** | 3.273 |

## v31.2 Fret end: ground steel taper that blends into the wood [computed unless tagged]

- **Thickness:** along the fret over the last L = 0.040, the thickness is t(y) = 0.004 + 0.039·(1 − S5(ξ)). That is G2 into the full crown and tangent to the wood at the tip.
- **In plan:** the steel ends in a **semicircular nose**, radius 0.040 (= crown half-width) [judged]. The taper runs L back from the nose at every point across the crown.
- **Crown section:** it blends from the ellipse to (1 − q²)², with λ = S5(ξ). It sits on a rim of t_tip·λ with a steep rounded foot, √(1 − q¹⁶). So the steel boundary is everywhere a finite, near-vertical foot like a normal fret foot, never a feather. The steel stays inside the original crown everywhere, so nothing is added (max excess 0.000).
- **Tip and rim:**
  - The tip is 0.004 at the centre [judged].
  - The rim is 0.0028 thick 0.002 inside the side boundary and 0.0030 at the nose [computed].
  - Round and polish the rim edge to about r 0.002 [judged].
  - The nose apex sits tangent to flat wood exactly at the roll start, and the wood roll continues beyond.
  - The slope step at the tip, sliding along the fret, is 0.0007°.
- See `fig/v31_fret_end_blend.png`: (a) section along the fret, (b) top view, (c) side view looking along the fret. The curves in (c) are cuts at fixed y; the nose cuts off their sides.

| Position (from the board edge, every station) | v3.1 |
|---|---|
| Tip = roll start | 0.024 |
| 90 % height (usable end) | 0.054 |
| Full crown ends | 0.064 |
| **Slot stop** | **0.054** (0.030 inside the roll start; steel there is 0.039 thick) |
| **Tang nipped** | **0.059** (0.035 inside the roll start; steel 0.042) |
| Rosewood from the slot end to the rolled surface | 0.030 at the top, 0.052 at 0.010 deep, 0.054 below that |

**String to the usable crown** (outer string, vintage spread) [computed]:

| Station | v3.1 | Vintage | v3 |
|---|---|---|---|
| Nut | **0.113** | 0.110 | 0.120 |
| Fret 1 | **0.112** | 0.109 | 0.119 |
| Fret 12 | **0.098** | 0.095 | 0.105 |
| Fret 21 | **0.092** | 0.089 | 0.099 |

v3.1 beats vintage by 0.003 everywhere. That is 0.007 less than v3, spent on the taper.

**Edge slide** [computed]. The R 0.30 pad is held on the bass edge and slid along x over a fret end. The headline is the steel's extra slope jump over the wood alone:

| Pad angle from vertical | Fret 5 | Fret 12 | Fret 19 |
|---|---|---|---|
| 45° (on the roll) | **+0.0°** | **+0.0°** | **+0.0°** |
| 60° | +0.0° | +0.0° | +0.0° |
| 30° (mostly on the top) | +14.1° | +10.5° | +1.4° (wood alone is 9.5° here) |

- **On the roll (45–60°)**, the steel sits behind the wood's support line, so the fret end adds nothing. That meets the 1.3° noise target. v3's domes added 12–14°.
- **The 45° result has thin margin:** L 0.030 already gives +1.6° (§v31.3).
- **At 30° the pad lies mostly on the board top and rides over the crown.** For reference, the same R 0.30 pad and slope-jump metric crossing a full-height fret on the flat board inboard gives **25.5°** [computed, v1 metric]. So the end is softer than any inboard fret, but it is not invisible. Longer tapers help: L 0.06 at widen 0.045 gives +6.7°; L 0.10 at widen 0.060 gives +3.1°.
- **Wood alone** (the scallop running through the edge) is reported separately: 0.0–0.2° at frets 5 and 12, and 5.2° at 45° / 9.5° at 30° at fret 19.

**Build:**
1. Cut each fret to length and nip the tang 0.035 inside the roll start.
2. **Pre-form the taper on the bench.** Use a jig that holds the wire on its base. Grind or file the top to the t(y) profile with a carbide or diamond file, about 0.040 long. Round the crown into the (1 − ξ²)² section with a crowning file. Keep the steel cool [judged].
3. Press and glue into the stopped slots. The untanged 0.030 beyond the slot end is glued down (CA or epoxy) [judged].
4. After levelling, true the taper with a small flat diamond block run *along the fret* toward the edge. Use tape on the wood and stop at the roll start. Then round the tip edge and polish (micromesh, then compound).

Stainless makes this slower, not harder to get right [judged]:
- it is about 2–3× slower to file and burns files;
- it holds a 0.004 tip without chipping or wear, unlike nickel silver, which would wear a 0.004 tip quickly.

Pre-forming the ends before installing is the reliable route. Dressing installed ends to 0.004 with a "radius file that follows the roll" is not possible, because the steel never reaches the roll.

## v31.3 Trade table (taper length vs roll) [computed]

Closed form a = widen + 0.027 − 0.003 − 0.743·L (taper on flat wood, tip at the roll start), checked by full rerun:

| widen / side | L | Roll a | Nut W | Hand girth, nut / f12 | Steel max slope | Slide f12, extra at 45° / 30° | Shoulder convex at s_j 0.55? |
|---|---|---|---|---|---|---|---|
| 0.030 | 0.030 | 0.032 | 1.710 | 2.772 / 3.134 | 68° | +1.6° / +14.8° | yes |
| **0.030** | **0.040** | **0.024** | **1.710** | **2.759 / 3.121** | **61°** | **0.0° / +10.5°** | **yes** |
| 0.030 | 0.060 | 0.010 | 1.710 | 2.736 / 3.102 | 51° | 0.0° / +10.9° | yes |
| 0.045 | 0.060 | 0.025 | 1.740 | 2.768 / 3.132 | 51° | 0.0° / +6.7° | no (needs a deeper s_j) |
| 0.060 | 0.060 | 0.040 | 1.770 | 2.803 / 3.171 | 51° | 0.0° / +5.5° | no |
| 0.060 | 0.100 | 0.010 | 1.770 | 2.754 / 3.123 | 36° | 0.0° / +3.1° | no |

The widening needed per side for the full brief [computed]:
- roll 0.06 with L 0.06: **0.081** (nut 1.81);
- roll 0.06 with L 0.10: 0.110;
- roll 0.08 with L 0.06: 0.100.

## v31.4 Could the steel follow the roll? (bend study) [computed; strain limit lit]

- **Method:**
  - grind the taper first, then bend the thinned end over a G2 roll entry (superellipse, a 0.06–0.08, b 0.06–0.105);
  - bending strain is 0.62·t·κ_wood (extreme fibre of the blended crown section);
  - usable height counts the wood drop under the steel.
- **Results:**
  - tip drop 0.002: 3–11 %;
  - 0.005: 4–19 %;
  - 0.010: 6–33 %;
  - 0.020: 12–54 %.
- **Limit:** cold-worked 302/304 stainless wire elongation is 1–8 % [lit: Ulbrich 302/304 wire data sheets]. Stainless fret-wire temper is not published [judged: hard drawn]. Bending into the elastic range only (< ~0.6 %) springs back.
- **Verdict:** at most a tip "drop" of about 0.001–0.002 would work, which is invisible. Even then the usable end sits 0.08–0.14 from the edge, which breaks the margin. Rejected.

## v31.5 Sanity checks, all re-run on the v3.1 surface [computed]

| Check | Result |
|---|---|
| Lowest top surface above the glue line (any x, y) | **0.053** (≥ 0.030) |
| Fin or rail (outward rise) | 0.000 |
| Steel boundary | Rim 0.0028–0.0030 thick 0.002 inside the edge; near-vertical rounded foot; no feather; no steel beyond the original crown |
| Roll in rosewood | Roll bottom (incl. the scallop) is at most 0.088 below the edge; the glue is at 0.140 |
| Maple exposed on top | none. The shoulder crosses the glue line at 2.6–3.9° from vertical on the side, as on any neck side |
| CNC ball | smallest concave radius 0.201, so a 1/4 in ball |
| Wood | maple rod-to-glue 0.068; under the rod 0.185; rosewood under the deepest scallop 0.076; under the slot 0.080 |
| Catch (κ 0.145) | **cell 20: 18.2° vs flat 25.5°**. Every cell is ≤ flat except cell 1 (26.8 vs 25.5). Cell 1 is set by the linear term, so it is unchanged from v3 and κ cannot affect it |
| κ trim | 0.15 → 0.145 changes only the κ-bound cells 15–22 (d at most −0.003). 0.145 is the largest κ with cell 20 ≤ flat |
| Relief and rod | planed sag 0.0108; gap 0.0084; rod 242 lb; Eb nominal scalloped 0.0089 |
| Modes | plain 31.6 / 240 / 775 Hz; scalloped 30.3 / 234 / 756 Hz |
| EI (N·m²) | fret 1: 357; fret 5: 401; fret 9: 452; fret 12: 494 |

## v31.6 Body-agent item (supersedes v3.6 item on the heel section)

- The v3.1 shoulder construction applies past x_h as well, including the 15.69 pocket datum.
  - The neck side below the board is now the vintage-width back plus the shoulder.
  - The board is still +0.030 per side.
- Re-fit the pocket walls and the heel blend to the v3.1 section, using `neck_v31.bottom3`. Widths at the pocket datum are unchanged from v3: board 2.192.

## v31.7 Owner decisions

1. **Which constraint gives?** With +0.030 you cannot have a 0.06–0.08 roll, a 0.06–0.10 taper and margin ≥ vintage together. Choose one:
   - (a) **recommended:** L 0.040 / roll 0.024 / corner radius 0.017;
   - (b) a longer, softer taper (L 0.06) with an almost flat edge (a 0.010);
   - (c) widen more: +0.060 per side gives L 0.06 with a 0.040 (nut 1.77);
   - (d) let the usable crown fall below vintage.
2. **Steel ends on flat wood at the roll start**, not running down the roll. OK?
3. **Option d buys girth back only marginally** (−0.010 at the nut against v3). It gives a flared board edge over a long shoulder (`fig/v31_profile_sections.png`). Keep it, or go back to the v3 scaled section?
4. **κ 0.145** (cell 20 fixed). OK?

## v3.1 sources (public spec pages)

- Ulbrich, 304 stainless wire data sheet (temper / elongation): https://www.ulbrich.com/uploads/data-sheets/304-Stainless-Steel-Wire-UNS-S30400-Wire.pdf
- Ulbrich, 302 stainless wire data sheet (1/4 hard to full hard; elongation 20 % down to 1–4 %): https://www.ulbrich.com/uploads/data-sheets/302-Stainless-Steel-Wire-UNS-S30200-Wire.pdf
