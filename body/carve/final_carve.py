"""FINAL CARVE - Supercaster II (all-alder CNC clamshell thinline, set neck, S-style offset double-cutaway body).

Comparison values named 'precbs' or 'pre-CBS' refer to published measurements of early-1960s production bodies of that
style. They are reference points for comparison, not this design.

Merged from the three concepts (judge's pick):
  * TOP  = Concept C "f-hole framed" architecture (best G2 smoothness, a traditional forearm contour, level plateau
           around the f-hole), with an optional bass-horn emphasis borrowed from Concept B.
  * BACK = Concept A belly geometry (smooth max-y bass-edge spline + S5 windows; C's belly polyline cut across the
           neck pocket and left a 0.006" concave crease at the centreline). Default depth is CAPPED to the clamshell.
  * EDGE = Concept A curvature-continuous 1/8" edge fillet law, re-solved here from THIS surface.
  * HEEL = Concept A heel loft (explicit height field) with every MACHINED concave fillet >= 0.25" (1/2" ball nose).

Coordinates: inches. x from the nut along the neck, y across (bass +). Top plane z = 0, back plane z = -THICK.
  top_drop(x, y)            drop DOWN from the top plane (>= 0), excluding the 1/8" edge fillet -> evaluate(top_drop, 0.125)
  back_drop(x, y, mode)     belly cut, height UP from the back plane (>= 0)
  heel_back_z(x, y)         lowest material surface of neck + heel + body (explicit height field, z up)
  HEEL_BLEND                parametric description of the set-neck heel / body junction
  edge_fillet(theta, kappa) G2 1/8" edge-fillet profile solver
  chamber_masks()           nominal and RETREATED wing chamber (the retreat is how the 0.55" rule is met)
  chamber_interior()        the cut chamber incl. (v3.2) pickguard bosses, the liner seat and the liner solid
  route_sdf / rear_mouth_sdf   (v3.2) vintage trem routes;  trem_checks / boss_checks / liner_checks  their checks
  checks()                  every hard-constraint check, printed

PARAMS (every number used; "derived" ones are computed below, not free):
  --- clamshell / set neck ---
  THICK               1.75   body thickness (pre-CBS consensus, medium confidence)
  insertion_depth     0.625  HOW FAR THE NECK GOES INTO THE BODY = mortise floor depth below the BODY TOP.
                             Open parameter (Jordan measures it). Default = vintage 5/8" pocket depth.
                             Same quantity in the other conventions: heel depth below the BOARD top = insertion_depth + 0.375
                             (Concept A's H=1.05 <-> 0.675; Concept B's heel_depth=1.10 <-> 0.725).
  board_height        0.375  fretboard top above the body top (0 deg neck angle)
  split_margin        0.15   minimum wood between mortise floor and the clamshell split
  top_half_pref       0.90   preferred top-half thickness; actual top_half = max(pref, insertion_depth + split_margin)  [derived]
  top_skin            0.197  5 mm chamber skin under the top carve (was 4 mm until 2026-11-11: strength, 3-D sim + check), measured PERPENDICULAR to the finished top (v3.1 merge)
  back_skin           0.276  7 mm stiff back skin, measured PERPENDICULAR to the finished back (v3.1)
  wood_min_3d         0.190  least true 3-D wood allowed anywhere round the chamber (4.8 mm; was 0.155 for the 4 mm top; roasted alder confirmed 2026-11-11). Checked by
                             chamber_wood_3d(): top skin, back skin and rim, each with its location.
  belly_margin        0.10   extra margin between belly and back skin (design note)
  chamber_carve_limit 0.55   max top drop wherever a chamber lies under it (hard constraint)
  frame               0.22   5-6 mm frame fillet: chamber stays this far inside any solid boundary
  rim                 0.30   solid rim width
  spine_y / solid_tail_x 1.9 / 29.6   design-note wing chamber: y > spine_y, x < solid_tail_x, sdf > rim
  --- flat zones (drop identically 0) ---
  guard_pad           0.05   guard footprint dilation kept planar (= evaluate()'s flat zone)
  jack_center/jack_pad (plan file)/0.20  JACK polygon dilated by pad; a 1.2x0.75 football plate fits anywhere in it
  neck_seat           x 15.3-18.30, |y|<1.25   set-neck seat (pocket + board overhang + root break), planar
  plate box           PLATE x0-0.1 .. x1+0.4, |y| < hw+0.1 (trem plate; same box evaluate() checks)
  --- f-hole plateau ---
  plateau_r           0.45   level plateau = f-hole dilated by this; slope exactly 0 inside
  blur_sigma          0.12   Gaussian smoothing of distance fields (kills medial-axis creases)
  zone_margin         0.16   carve starts this far outside any flat zone
  --- subtle edge carve (the soft roll that the 1/8" fillet blends into) ---
  edge_A              0.13   max depth of the edge carve at the rim
  edge_W              1.30   max inward reach
  edge_A_gap          1.30   amplitude reaches edge_A once the free gap (flat zone -> rim) is at least this
  horn_boost          0.5    extra edge-carve amplitude on the bass horn (Concept B idea; ~0.2" at the horn rim), Gaussian;
                             kept because G2, concave radius, f-hole slope and margin all stay within limits
  horn_c / horn_sig   centre and radius of that Gaussian
  --- forearm contour (v3.1: one convex crowned surface, no wrap around the f-hole) ---
  The drop is f(s), s = distance past a STRAIGHT zero line, so the surface is a cylinder over a convex profile: no concave
  valley can exist anywhere in it. The zero line is the tangent from arm_tail to bodylib.FHOLE_POLY (it follows the
  f-hole when the trace or SC_FHOLE_SHIFT moves it), so the whole f-hole lies on the level side.
  arm_tail            (tail_x from the plan file, -2.0)  where the zero line meets the tail rim (env SC_ARM_TAIL_Y). The drop only becomes visible
                             (0.005) about 1.8 further up the tail, at y = -0.2, i.e. at the strap button like v3 (y = +0.1)
  arm_clear           0.0    extra distance between the zero line and the f-hole polygon
  arm_keep            0.42   the profile reaches 3 degrees this far past the f-hole polygon (>= 0.38 level-top rule)
  arm_depth           0.85   drop at the thinnest rim spot (leaves ~0.80; 1.00 before 2026-11-10, which put the glue plane through
                             the top skin once the forearm became a ramp). env SC_ARM_DEPTH
  arm_kappa_max       None   optional cap on the peak section curvature (1/in), env SC_ARM_KMAX. The profile is: curvature
                             ramps 0 -> peak (S5, so the surface is C4 at the zero line), then holds (a crown of radius
                             1/peak all the way to the rim; no dead plane). With a cap set, the DEPTH gives way (_arm_depth).
  arm_crown / arm_crown_from  1.0 / 0.5   curvature kept at the rim as a fraction of the peak (1 = pure arc), relaxing from
                             this fraction of the arc length on. < 1 flattens the outer bevel at the price of a higher peak.
  arm_A / arm_B       derived: the two points where the zero line crosses the outline (for drawings)
  arm_plane           1.5    (2026-11-10, Jordan: stock vintage forearm with a soft onset) length of the onset blend; past it the
                             forearm is a flat ramp to the rim, as on a pre-CBS body. 0 = the earlier continuous arc (arm_keep,
                             arm_crown and arm_kappa_max then apply; they are ignored while arm_plane > 0). env SC_ARM_PLANE
  arm_blend_p         3      p-norm that joins the forearm and the perimeter roll (drop = (forearm^p + roll^p)^(1/p)).
                             Merge: 4 -> 3. Grid peak curvature at the two joins 0.357 / 0.299 -> 0.298 / 0.307 per in (the
                             roll alone is 0.448 / 0.295 there); p = 2 and p >= 6 are both worse.
  smax_eps            0.06   softness of the perimeter roll's own onset (unchanged from v3)
  --- belly (back) ---
  belly_mode          'blended' (default, v3.1) | 'whisper' | 'full'   -- env override SC_BELLY --   legacy: 'swell' (v3) | 'blend' |
                      'capped' (v2) | 'precbs'.
                             v3.1: ONE height field for the whole back,
                                 back = (1 - w) perimeter(E) + w B(q)
                                 perimeter = A 2 I5(1 - E/Wp) hf        E = distance in from the whole outline (back_edge_A x back_edge_W;
                                                                       on the two horns Wp shrinks to back_edge_fit x the half-width, so
                                                                       the carve from the two edges never meets on the medial axis)
                                 B         = k on I5((W - q)/on)       q = EXACT distance in from the outer bass edge ONLY (smooth guide
                                                                       spline through the outline vertices), k = D/(W - on/2)
                                 w         = S5 window along x (and a y ramp that lies entirely in flat ground)
                             B is a straight bevel (slope k) from the rim that lands on the back plane over the last `on` inches with
                             zero slope, curvature and third derivative. Nothing is measured from the cutaway side of the bass horn,
                             so there is no two-sided medial axis there (v3's ridge), and no amplitude window fades across the bevel.
  belly_variants      D = depth at the rim, W = reach, on = landing length, roll = back edge-roll setback through the belly
                             whisper  0.30  / 2.60 / 1.60 / 0.40   v3's section (0.22 / 0.13 / 0.01 at 0.5 / 1 / 2 in), crease-free
                             blended  0.345 / 3.30 / 1.00 / 0.30   default: 0.28 / 0.22 / 0.10 at 0.5 / 1 / 2 in, under 0.001 by 3.1
                             full     0.485 / 3.30 / 1.00 / 0.25   the most the flat split allows: any deeper and back_total passes the
                                                                   0.474 cap less than `frame` from the chamber wall, and the chamber retreats
                             roll: on the traditional S-style body the belly cut replaces the back roundover along the waist. The full 0.50 roll would put the
                             top of the roll 0.50 above the belly rim (glue line exposed from D = 0.29), so the back setback is eased to
                             `roll` where the belly is at the rim (edge_law: back_raw capped by a_max + (roll - a_max) S5((w B/D - 0.15)/0.6) at the outline).
  belly_win           (13.7, 5.2, 21.4, 5.5)  window along x: rises 13.7->18.9 (up the back of the bass horn), full 18.9-21.4, out by 26.9
  belly_win_y         (0.0, 1.2)  y ramp of the window (both terms are identically 0 there; it only keeps the treble side out)
  belly_guide         first vertex, last vertex and smoothing tolerance of the outer-bass-edge guide spline
  back_edge_fit       (0.80, 0.30, 0.15)  horn fit of the perimeter carve: reach <= 0.80 x half-width on the medial axis, growing 0.30 per
                             inch away from it, Gaussian 0.15
  (v3.2 removed trem_cavity / trem_cover_lip: v3's spring-cavity box x 20.4-26.1, |y| < 1.15 and a cover lip; both wrong)
  glue_margin_min     0.06   the top of the back roll must stay this far below the glue plane (z = -top_half)
  belly_A / belly_W / belly_xw   legacy v3 'swell' numbers (0.34 / 3.0 / window), kept so v3 can be drawn for comparison
  back_blend_p        2.0    ('blend' mode only) p-norm that merges a separate belly roll with the back perimeter carve
  heel_fade           (0.30, 1.8)  back carve is zero within 0.30" of the heel footprint and full 1.8" further out
  belly_depth_precbs  1.10   comparison value only: early-1960s production bodies (5/8" remaining rule; low-medium confidence). NOT buildable over the wing chamber.
  belly_depth_capped  derived = back_half - back_skin - belly_margin (0.474 for top_half 0.90). CAPPED, NOT pre-CBS.
  belly_reach / belly_onset 3.0 / 0.8   inward reach from the bass edge, C3 onset at the inner end (long sweep, no scoop)
  belly_x             (16.2, 2.2, 24.0, 3.2)  rises 16.2->18.4, holds to 24.0, falls out by 27.2 ('54-style long sweep)
  belly_y             (1.2, 1.0)  rises y 1.2 -> 2.2 (keeps the heel landing and the trem cover flat)
  --- edge ---
  edge_mode           'ergo' (default since v3.4, 2026-11-13: Jordan withdrew the crisp 1/8" look) | 'varedge' (v3.3) | 'compound' (v3-v3.2)
                             | 'uniform'.  v3.4 'ergo' (_ergo_law, edge_ergo dict), setbacks a (radius ~0.834 a):
                               FRONT  front 3/8 default (horn tips and cutaways too); fhole 1/4 from fhole_ahead (1.0) before the upper eye's
                                      rim foot to the lower eye's; arm 5/16 held constant from the lower eye to the thinnest rim spot (no swell);
                                      lower 1/2 from there round the tail and treble lower bout to the guard tail (edge_tlb_guard), capped by
                                      thin and by the glue seam: a <= max((top_half - top_drop - seam_eps)/ROLL_SIDE, arm), so the wall-top
                                      seam run can never be longer than v3.3's.
                               BACK   back_ergo 1/2 everywhere except back 3/8 within tip_half (0.5) of each horn tip and on the treble horn
                                      from waist_end_x (18.5) to the tip; the belly is limited by the glue plane + glue_clear (0.10) instead
                                      of v3.1's 0.30 belly roll; thin and plan cap as before.
                               Every level change is an S5 ramp of 1.875 |da| / lip (lip 0.33/in) on the HIGHER side, then the C2 limiter
                               (same lip). Pocket ease and heel untouched. Env SC_EDGE_MODE=varedge reproduces v3.3.
                             Env override SC_EDGE_MODE / SC_EDGE_R (comparison renders).
                             'varedge': 1/8" (edge_R) all round the front silhouette as seen from the front, incl. beside the f-hole and past
                             its lower eye; the FRONT roll grows to edge_hid_a only inside hidden_window(): the two cutaway insides (pocket
                             mouth -> horn tip, back to 1/8" AT each tip), and the lower bout from edge_arm_after past the arc foot of the
                             f-hole's aft-most vertex (already on the forearm ramp, rim drop ~0.3) round the tail and the treble lower bout to
                             where the guard comes within edge_tlb_guard of the outline. Windows are S5 ramps of edge_hid_ramp arc
                             (max |da/ds| 0.33/in), then the same min() with f-hole / guard / jack / thin / plan-cap terms, the C2 rate limiter
                             (lip edge_hid_lip, so it only smooths), and the pocket ease. Back: min(edge_back_a_max, thin, cap, glue, belly ease).
  edge_hid_a          0.3125 front setback where hidden (min radius 0.26 = 1/4"). Held constant through the forearm facet: thin at the
                             thinnest rim spot is 0.33, so it never swells and dips there. env SC_EDGE_HID_A
  edge_back_a_max     0.3125 back setback all round (Fender thinline backs ~1/4" R; the belly already eases the back roll to 0.30). env SC_EDGE_BACK_A
  edge_arm_after      1.0    front roll starts growing no earlier than this arc past the f-hole lower eye's foot on the rim
  edge_hid_ramp       1.0    S5 ramp length (arc) of every hidden window;  edge_horn_margin 0.0 (window is 0 at the horn tip itself)
  edge_tlb_guard      0.75   treble lower-bout window ends where the guard edge comes within this of the outline (guard tail, x ~27.3)
  edge_hid_lip        0.40   rate-limiter lip for varedge top (above the ramps' 0.33/in, so it only adds C2 smoothing and never raises a)
                             'compound': the roll setback a(s) varies round the outline. Stock-Strat-size roll wherever nothing is
                             in the way, 1/8" only where the f-hole needs its level margin:
                                 a_top  = min(edge_a_max, (dist_to_fhole - edge_F_keep)/k3, dist_to_guard - edge_guard_clear,
                                              dist_to_jack_flat, thin),   floored at edge_R
                                 a_back = min(edge_a_max, thin)
                                 thin   = edge_share (T_edge - edge_w_min) / ROLL_SIDE     (T_edge = thickness at the outline)
                             both also <= edge_plan_cap x plan feature radius, a_back <= glue-plane limit, edge_neck_a under the
                             neck; then |da/ds| <= edge_lip and Gaussian edge_sig, constrained to stay <= the raw law.
  edge_R              0.125  minimum setback (Jordan: 1/8" beside the f-hole); also the uniform-mode setback
  edge_a_max          0.50   full setback (plateau radius 0.83 a = 0.42": contact width of a stock 7/16" arc)
  edge_F_keep         0.40   level (< 3 deg) top kept between the f-hole edge and the start of the roll
  edge_guard_clear    0.06   the roll starts no closer than this to the pickguard
  edge_w_min/share    0.14 / 0.5   thin rim: straight wall kept (measured ON the outline), and each roll's share of what is left
  edge_lip/sig        0.10 / 0.30  max rate of change of a along the outline (in/in); half-width of the C2 smoothing kernel
                             (flat erosion + triweight kernel, so a never exceeds its raw law and smoothing adds no dips).
  edge_neck_a         0.125  setback under the neck and at the pocket mouths. The outline under the neck is a placeholder, so
                             the roll does not die to a sharp arris there: it arrives 1/8" wide and is cut off by the neck side.
                             The rate limit spreads the change over >= (a - edge_neck_a)/edge_lip of arc.
  edge_neck_ease      2.0    v3.1 merge (edge checker's fix, now the default; env SC_NECK_EASE, 0 = the plain rate limiter): the
                             roll grows from edge_neck_a at each pocket mouth to its full law through an S5 blend over this
                             many inches of outline, so the cutaway roundover is back to 0.50" within 2" of the mouth
                             (the plain 0.10/in limiter needed 3.75"). max |da/ds| 0.352.
  edge_plan_cap       0.90   a <= 0.90 x plan feature radius (radius of the largest inscribed circle touching the outline there =
                             convex plan radius, or half the width of a horn), so the roll band never reaches the medial axis.
                             v3.1 merge: 0.80 -> 0.90 for fuller horn tips (treble tip 0.372 -> 0.418, bass tip 0.426 ->
                             0.477); roll band stays 0.050" clear of the medial axis, slope-jump scan at h 0.004 / 0.002 /
                             0.001 halves with h at both tips (no crease). env SC_EDGE_PLAN_CAP (0.8 = as audited).
  edge_glue_clear     0.06   back roll ends at least this far below the glue plane z = -top_half (limits a_back along the belly)
  edge_fit_sigma/ds   0.0025 / 0.005  v3.1 outline curve: periodic C2 smoothing spline through the plan outline points (rms
                             tolerance), resampled every 0.005" of arc. Distance, foot point and a(s) all come from this curve
                             (edge_foot / outline_sdf); a(s) is interpolated continuously at the foot point.
  (v3.1) on the bass lower bout the f-hole term is made unimodal about the pinch (it only rises with distance from it), so
                             the roll has one minimum beside the f-hole and no forward dip.
  edge_rho            0.20   roll profile: curvature ramps up over the first 20%, holds, ramps down over the last 20%
                             (roll_drop(): an ADDITIVE height field a rho(d/a) whose value, slope and curvature are 0 at d = a,
                             so top + roll is curvature-continuous on any face, and it ends vertical with zero curvature)
  fhole_shift         0.0    option: f-hole moved this far inboard along (0.179, -0.984). Env override SC_FHOLE_SHIFT.
                             (applied in bodylib; 0 = Jordan's trace exactly)
  --- heel ---
  scale 25.5, heel_start_fret 15, pocket_datum_x 15.6875 (at the pocket sides, not the centreline point of the outline),
  pocket_len 3.0, pocket_w 2.1875, board_end 18.17, tenon_end 18.72 (0.10 before the neck-PU route), tenon_w 1.90,
  flank_r_min / flank_r_max 0.25 / 0.375  heel-flank fillet radius law (>= 0.25 = 1/2" ball nose)
  root_break          1/32   optional edge break on the pocket wall top (glue seam is NOT a machined fillet)
  heel_lead           0.5    loft parameter starts this far before fret 15 (visible departure at fret 15 stays ~0.01")
  heel_law_depth      (5,2)  Beta(m,n) law for heel depth: flat concave onset, G2 landing on the back plane
  heel_law_shape      (8,2)  Beta(m,n) law for the section morph (C -> squared foot, half-width -> pocket width)
  heel_p              (2.3, 4.0)  superellipse exponent at the neck C / at the body
  --- v3.2 (2026-11-12): trem routes, pickguard bosses, liner seat, tongue (hidden; nothing visible changes) ---
  trem                vintage-style synchronized trem routes. NOT in this file: read from the plan file (TREM), because my
                             numbers were measured from third-party plan sheets. Rounded rectangles; z from the top (0).
    pivot_x           pivot line from the nut; six pivot screws at pivot_pitch on the CL
    slot              top through-slot (x0, x1, hw, yc, r, z_top, z_bot)
    block             rear block cavity, from the back up to just below the top
    spring            spring cavity on the CL, from the back
  rear_cover          None   no rear cover plate: the back opening is spring + block cavity (rear_mouth_sdf)
  trem_mouth_pad      0.35   the back carve must be ~0 this far round the open mouth (check belly_on_trem_mouth_pad)
  guard_bosses        r 0.25 / root_r 0.125 / z_bot -0.65   solid 0.50"-diameter column hanging from the chamber roof to z -0.65 under
                             every pickguard screw (GUARD_SCREWS = SCREWS in the plan file) whose boss + root fillet reaches the
                             chamber (four of them with my plan). Roof only, no post to the back.
                             z_bot: #4 x 1/2" screw through a 0.06-0.09 guard bites <= 0.44; 0.2 extra wood below the tip [judged]
  liner               veneer 0.6 mm / depth 0.75 / inset 2.7 mm / wall_out 2.0 mm / land 0.06   narrowed f-hole liner (section 0):
                             inner wall = f-hole outline inset 2.7 mm, outer wall 2 mm outside it, square ledge at the veneer
                             underside (top_skin + veneer = 5.6 mm below the top), 0.75 deep below that. The SEAT is the roof over the
                             footprint + land held at exactly top_skin (no frame swell or corner fillet); nothing is recessed.
  tongue_end / tongue_w   21.7 / 1.90   hidden set-neck tongue: plan footprint only (tenon_end .. tongue_end, |y| < tongue_w/2);
                             its z section is not modelled (see HEEL_BLEND). tenon_end stays the heel-fade box of the back carve.
  --- derived (computed at import, do not set) ---
  top_half            max(top_half_pref, insertion_depth + split_margin)          -> 0.90
  back_half           THICK - top_half                                            -> 0.85
  belly_depth_capped  back_half - back_skin - belly_margin                        -> 0.474
  mortise_floor_z     -insertion_depth (z of the mortise floor, body top = 0)      -> -0.625
  heel_depth_below_board  insertion_depth + board_height (Concept A/B convention)  -> 1.000
  _arm_depth          forearm drop actually reached at the thinnest rim spot (= arm_depth unless arm_kappa_max bites)
  _arm_kappa_peak / _arm_ramp   peak section curvature and the length of its S5 ramp (solved)
  _arm_slope_deg      slope of the forearm profile at the thinnest rim spot
  _arm_width_to_rim   zero line -> thinnest rim spot distance;  _arm_rim_at  that spot;  _arm_touch  f-hole tangent vertex

Run:  <cad venv>/bin/python -I final_carve.py     (prints all metrics and checks)
"""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bodylib import *
from bodylib import _inside, _segdist
import bodylib as BL
import numpy as np
from scipy import ndimage
from scipy.interpolate import UnivariateSpline
from scipy.optimize import fsolve
from scipy.special import betainc

PARAMS = dict(
    THICK=1.75, insertion_depth=0.625, board_height=0.375, split_margin=0.15, top_half_pref=0.90,
    top_skin=0.197, back_skin=0.276, wood_min_3d=0.190, belly_margin=0.10, chamber_carve_limit=0.55, frame=0.22, rim=0.30,
    spine_y=1.9, solid_tail_x=29.6,
    guard_pad=0.05, jack_center=BL.LANDMARKS['jack_center'], jack_pad=0.20, neck_seat=dict(x0=15.3, x1=18.30, hw=1.25),
    plateau_r=0.45, blur_sigma=0.12, zone_margin=0.16,
    edge_A=0.13, edge_W=1.30, edge_A_gap=1.30, horn_boost=0.5, horn_c=BL.LANDMARKS['horn_c'], horn_sig=1.4,
    arm_tail=(BL.LANDMARKS['tail_x'], float(os.environ.get('SC_ARM_TAIL_Y', -2.0))), arm_clear=0.0, arm_keep=float(os.environ.get('SC_ARM_KEEP', 0.42)), arm_depth=float(os.environ.get('SC_ARM_DEPTH', 0.85)),
    arm_kappa_max=(float(os.environ.get('SC_ARM_KMAX', 0)) or None), arm_plane=float(os.environ.get('SC_ARM_PLANE', 1.5)), arm_crown=1.0, arm_crown_from=0.5, arm_blend_p=3, smax_eps=0.06,
    belly_mode=os.environ.get('SC_BELLY', 'blended'),
    belly_variants=dict(whisper=dict(D=0.30, W=2.60, on=1.60, roll=0.40),
                        blended=dict(D=0.345, W=3.30, on=1.00, roll=0.30),
                        full=dict(D=0.485, W=3.30, on=1.00, roll=0.25)),
    belly_win=(13.7, 5.2, 21.4, 5.5), belly_win_y=(0.0, 1.2), belly_guide=(BL.LANDMARKS['belly_guide'][0], BL.LANDMARKS['belly_guide'][1], 0.003),
    back_edge_fit=(0.80, 0.30, 0.15), glue_margin_min=0.06,
    # v3.2 (2026-11-12): vintage-style trem routes, no rear cover. The numbers come from the plan file (see bodylib.py)
    trem=BL.TREM,
    trem_mouth_pad=0.35, rear_cover=None,
    guard_bosses=dict(r=0.25, root_r=0.125, z_bot=-0.65),
    liner=dict(veneer=0.6 / 25.4, depth=0.75, inset=2.7 / 25.4, wall_out=2.0 / 25.4, land=0.06),
    tongue_end=21.7, tongue_w=1.90,
    belly_A=0.34, belly_W=3.0, belly_xw=(14.0, 3.6, 21.4, 5.2), back_blend_p=2.0, heel_fade=(0.30, 1.8),
    belly_depth_precbs=1.10, belly_reach=3.0, belly_onset=0.8,
    belly_x=(16.2, 2.2, 24.0, 3.2), belly_y=(1.2, 1.0),
    edge_mode=os.environ.get('SC_EDGE_MODE', 'ergo'), edge_R=float(os.environ.get('SC_EDGE_R', 0.125)),
    # v3.3 (2026-11-13) variable edge: 1/8" wherever the front silhouette is seen, larger only where it is hidden
    edge_hid_a=float(os.environ.get('SC_EDGE_HID_A', 0.3125)), edge_back_a_max=float(os.environ.get('SC_EDGE_BACK_A', 0.3125)),
    edge_arm_after=1.0, edge_hid_ramp=1.0, edge_horn_margin=0.0, edge_tlb_guard=0.75, edge_hid_lip=0.40,
    # v3.4 (2026-11-13) 'ergo': rounder all round, graduated where the body touches the player (setbacks; radius ~0.834 a)
    edge_ergo=dict(front=0.375, fhole=0.25, fhole_ahead=1.0, arm=0.3125, lower=0.50, back=0.375, back_ergo=0.50,
                   tip_half=0.5, waist_end_x=18.5, lip=0.33, seam_eps=0.005, glue_clear=0.10),
    edge_a_max=0.50, edge_F_keep=0.40, edge_guard_clear=0.06, edge_w_min=0.14, edge_share=0.5, edge_lip=0.10, edge_sig=0.30,
    edge_neck_a=0.125, edge_neck_ease=float(os.environ.get('SC_NECK_EASE', 2.0)), edge_plan_cap=float(os.environ.get('SC_EDGE_PLAN_CAP', 0.90)),
    edge_glue_clear=0.06, edge_fit_sigma=0.0025, edge_ds=0.005,
    edge_rho=0.20, fhole_shift=BL.FHOLE_SHIFT,
    back_edge_A=0.10, back_edge_W=1.30,
    scale=25.5, heel_start_fret=15, pocket_datum_x=15.6875, pocket_len=3.0, pocket_w=2.1875, board_end=18.17,
    tenon_end=18.72, tenon_w=1.90, flank_r_min=0.25, flank_r_max=0.375, root_break=1 / 32,
    heel_lead=0.5, heel_law_depth=(5, 2), heel_law_shape=(8, 2), heel_p=(2.3, 4.0),
)
P = PARAMS
BELLY_MODES = tuple(P['belly_variants']) + ('swell', 'blend', 'capped', 'precbs')      # v3.1 one-surface modes, then the legacy ones
assert P['belly_mode'] in BELLY_MODES, f"unknown belly_mode {P['belly_mode']!r} (env SC_BELLY): choose one of {BELLY_MODES}"
# ---- derived construction numbers
P['top_half'] = max(P['top_half_pref'], P['insertion_depth'] + P['split_margin'])
P['back_half'] = P['THICK'] - P['top_half']
P['belly_depth_capped'] = round(P['back_half'] - P['back_skin'] - P['belly_margin'], 4)
P['mortise_floor_z'] = -P['insertion_depth']
P['heel_depth_below_board'] = P['insertion_depth'] + P['board_height']
# v3.2: pickguard screw positions
GUARD_SCREWS = list(BL.SCREWS)      # public tree: from the plan file (see bodylib.py)

# ---------------------------------------------------------------------------------------------- helpers
def S5(u):
    u = np.clip(u, 0, 1); return u ** 3 * (u * (6 * u - 15) + 10)
def I5(u):
    """Integral of S5 from 0 (C3-flat onset), linear continuation beyond 1."""
    u = np.asarray(u, float); uu = np.clip(u, 0, 1)
    return np.where(u < 1, uu ** 6 - 3 * uu ** 5 + 2.5 * uu ** 4, 0.5 + (u - 1))
def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1); return b * (1 - h) + a * h - k * h * (1 - h)
def smax(a, b, eps):
    return 0.5 * (a + b + np.sqrt((a - b) ** 2 + eps ** 2)) - 0.5 * eps

# ---------------------------------------------------------------------------------------------- distance fields
H = 0.02
FX = np.arange(12.6, 31.8 + 1e-9, H); FY = np.arange(-7.0, 7.0 + 1e-9, H)
_cache = os.path.join(HERE, '_final_fields.npz' if not BL.FHOLE_SHIFT else f'_final_fields_fh{BL.FHOLE_SHIFT:.3f}.npz')
_KEY = np.array([P['guard_pad'], P['jack_pad'], P['plateau_r'], P['neck_seat']['x0'], P['neck_seat']['x1'], P['neck_seat']['hw'], 3.1,
                 len(FHOLE_POLY), float(FHOLE_POLY.sum())])      # v3.1 merge: the cached fields depend on the f-hole trace too
def _box_dist(x, y, x0, x1, hw):
    dx = np.maximum(np.maximum(x0 - x, x - x1), 0); dy = np.maximum(np.abs(y) - hw, 0); return np.hypot(dx, dy)
def _build():
    GX, GY = np.meshgrid(FX, FY, indexing='ij')
    e = sdf_outline(GX, GY)
    dg = np.maximum(0, -sdf_guard(GX, GY) - P['guard_pad'])
    dj = np.where(_inside(JACK, GX, GY), 0, _segdist(JACK, GX, GY)); dj = np.maximum(0, dj - P['jack_pad'])
    dp = _box_dist(GX, GY, PLATE['x0'] - 0.1, PLATE['x1'] + 0.4, PLATE['hw'] + 0.1)
    ns = P['neck_seat']; dn = _box_dist(GX, GY, ns['x0'], ns['x1'], ns['hw'])
    fh = fhole_mask(GX, GY)
    dfh = ndimage.distance_transform_edt(~fh) * H
    dF = np.minimum.reduce([dg, dj, dp, dn]); dPl = np.maximum(0, dfh - P['plateau_r'])
    np.savez_compressed(_cache, e=e, dZ=np.minimum(dF, dPl), dfh=dfh, dF=dF, key=_KEY)
def _stale():
    if not os.path.exists(_cache): return True
    k = np.load(_cache)['key']; return k.shape != _KEY.shape or not np.allclose(k, _KEY)
if _stale(): _build()
_f = np.load(_cache)
_sg = P['blur_sigma'] / H
_FIELDS = dict(E=ndimage.gaussian_filter(_f['e'], 0.5 * _sg, mode='nearest'),
               DZ=ndimage.gaussian_filter(_f['dZ'], _sg, mode='nearest'),
               DFH=ndimage.gaussian_filter(_f['dfh'], _sg, mode='nearest'))
_HARD = (_f['dF'] <= 0).astype(float)      # v3.1: guard / jack / plate / neck seat only. The f-hole plateau needs no mask:
                                           # forearm() is exactly 0 on the f-hole side of its zero line and edge_carve() is 0 there.
_SPL = {k: ndimage.spline_filter(v, order=3) for k, v in _FIELDS.items()}
def _coords(x, y):
    return np.stack([(np.asarray(x, float) - FX[0]) / H, (np.asarray(y, float) - FY[0]) / H]).reshape(2, -1)
def _f3(k, x, y):
    x = np.asarray(x, float)
    return ndimage.map_coordinates(_SPL[k], _coords(x, y), order=3, mode='nearest', prefilter=False).reshape(x.shape)
def _hard(x, y):
    x = np.asarray(x, float)
    return ndimage.map_coordinates(_HARD, _coords(x, y), order=0, mode='nearest').reshape(x.shape) > 0.5

# ---------------------------------------------------------------------------------------------- forearm (v3.1)
def _arm_line():
    """Zero line: the tangent from arm_tail to the f-hole polygon with the whole polygon on the level side.
    Returns (unit normal toward the bass/tail corner, the polygon vertex it touches)."""
    tx, ty = P['arm_tail']; ph = np.arctan2(FHOLE_POLY[:, 1] - ty, FHOLE_POLY[:, 0] - tx); k = int(np.argmin(ph))
    return (math.sin(ph[k]), -math.cos(ph[k])), FHOLE_POLY[k]
(_nx, _ny), _ARM_TOUCH = _arm_line()
def arm_s(x, y):
    """Distance past the forearm zero line, + toward the bass/tail corner. The drop is 0 for arm_s <= 0."""
    return (np.asarray(x, float) - P['arm_tail'][0]) * _nx + (np.asarray(y, float) - P['arm_tail'][1]) * _ny - P['arm_clear']
_GX, _GY = np.meshgrid(FX, FY, indexing='ij')
def _outline_dense(ds=0.01):
    Pc = np.vstack([OUTLINE, OUTLINE[:1]]); t = np.r_[0, np.cumsum(np.hypot(*np.diff(Pc, axis=0).T))]
    ti = np.arange(0, t[-1], ds); return np.c_[np.interp(ti, t, Pc[:, 0]), np.interp(ti, t, Pc[:, 1])]
_OD = _outline_dense(); _so = arm_s(_OD[:, 0], _OD[:, 1]); _k = int(np.argmax(_so))
S_MAX = float(_so[_k])                                             # zero line -> thinnest spot on the rim
def _arm_curve(kp, a, n=20001):
    """Section of the forearm: curvature kp S5(sigma / a), held (times the optional crown relaxation) to the rim and beyond.
    Returns horizontal s, drop z, slope angle theta, curvature k along arc length sigma."""
    sg = np.linspace(0, 1.9 * (S_MAX + 0.6), n); c0 = P['arm_crown_from'] * S_MAX
    k = kp * S5(sg / a) * (1 - (1 - P['arm_crown']) * S5((sg - c0) / max(1.15 * S_MAX - c0, 1e-6)))
    if P['arm_plane']:                              # vintage ramp: curvature only inside the onset blend, a flat plane from there to the rim
        u = np.clip(sg / P['arm_plane'], 0, 1); k = kp * np.where(u < 0.5, S5(2 * u), S5(2 * (1 - u)))
    th = np.minimum(np.r_[0, np.cumsum((k[1:] + k[:-1]) / 2 * np.diff(sg))], math.radians(75)); ds = np.diff(sg)
    s = np.r_[0, np.cumsum((np.cos(th[1:]) + np.cos(th[:-1])) / 2 * ds)]; z = np.r_[0, np.cumsum((np.sin(th[1:]) + np.sin(th[:-1])) / 2 * ds)]
    return s, z, th, k
def _arm_solve():
    """Peak curvature and ramp length so that (1) the drop at the thinnest rim spot is the depth and (2) the slope is
    3 degrees exactly arm_keep past the f-hole polygon. If the peak exceeds arm_kappa_max the depth is reduced until it fits."""
    keep = max(P['arm_keep'] - P['arm_clear'], 0.05)
    def solve(depth):
        def res(v):
            s, z, th, k = _arm_curve(abs(v[0]), abs(v[1]) + 0.02)
            return [np.interp(S_MAX, s, z) - depth, np.degrees(np.interp(keep, s, th)) - 3.0]
        v = fsolve(res, [0.3, 0.5]); return abs(v[0]), abs(v[1]) + 0.02
    if P['arm_plane']:                              # one unknown: the blend's peak curvature that lands the depth at the rim
        from scipy.optimize import brentq
        kp = brentq(lambda v: np.interp(S_MAX, *_arm_curve(v, 1.0)[:2]) - P['arm_depth'], 1e-3, 5.0, xtol=1e-7); return P['arm_depth'], kp, P['arm_plane']
    depth = P['arm_depth']; kp, a = solve(depth)
    if P['arm_kappa_max'] and kp > P['arm_kappa_max']:
        from scipy.optimize import brentq
        depth = brentq(lambda d: solve(d)[0] - P['arm_kappa_max'], 0.2, P['arm_depth'], xtol=1e-5); kp, a = solve(depth)
    return depth, kp, a
_ARM_DEPTH, _ARM_KP, _ARM_RAMP = _arm_solve()
def _arm_table():
    from scipy.interpolate import CubicSpline
    s, z, th, k = _arm_curve(_ARM_KP, _ARM_RAMP); m = s <= S_MAX + 0.6; j = np.arange(0, int(m.sum()), 8)
    return CubicSpline(s[j], z[j], bc_type=((1, 0.0), (2, 0.0))), float(s[j][-1]), float(np.degrees(np.interp(S_MAX, s, th)))
_ARM_F, _ARM_SEND, _rs = _arm_table()
P['_arm_depth'] = round(float(_ARM_DEPTH), 4); P['_arm_kappa_peak'] = round(float(_ARM_KP), 4); P['_arm_ramp'] = round(float(_ARM_RAMP), 3)
P['_arm_slope_deg'] = round(_rs, 2); P['_arm_width_to_rim'] = round(S_MAX, 3)
P['_arm_rim_at'] = (round(float(_OD[_k, 0]), 2), round(float(_OD[_k, 1]), 2)); P['_arm_touch'] = tuple(float(v) for v in np.round(_ARM_TOUCH, 2))
_z = np.where(np.sign(_so) != np.sign(np.roll(_so, 1)))[0]; _zp = _OD[_z][np.argsort(_OD[_z][:, 0])]
P['arm_A'], P['arm_B'] = tuple(float(v) for v in np.round(_zp[0], 2)), tuple(float(v) for v in np.round(_zp[-1], 2))      # zero line on the bass rim / on the tail
def forearm(x, y):
    """Convex crowned forearm contour: f(arm_s). Exactly 0 on the f-hole side of the zero line; C2 everywhere (C4 at the
    zero line); no plane and no concave region anywhere (the Hessian is f'' n n^T with f'' > 0)."""
    s = arm_s(x, y); return np.where(s > 0, _ARM_F(np.clip(s, 0, _ARM_SEND)), 0.0)

# ---------------------------------------------------------------------------------------------- edge carve
def edge_carve(x, y):
    """Subtle perimeter roll, width/depth adapt to the free gap between flat zones and the rim; C3-flat onset."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    e = _f3('E', x, y); free = np.maximum(_f3('DZ', x, y) - P['zone_margin'], 0)
    gap = np.maximum(e, 0) + free
    W = smin(P['edge_W'], gap, 0.25)
    t = np.clip(1 - np.maximum(e, 0) / np.maximum(W, 1e-6), 0, 1)
    hx, hy = P['horn_c']
    boost = 1 + P['horn_boost'] * np.exp(-((x - hx) ** 2 + (y - hy) ** 2) / (2 * P['horn_sig'] ** 2))
    A = P['edge_A'] * boost * S5(gap / P['edge_A_gap'])
    return A * 2 * I5(t) * (free > 0)

def top_drop(x, y):
    """Top-surface drop (in) below the top plane, excluding the 1/8 edge fillet. Flat zones are identically 0."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    # v3.1: the perimeter roll is exactly v3's (smax against 0 with smax_eps, as it was tuned), and it meets the forearm
    # through a p-norm: equal to the forearm where there is no roll and to the roll where there is no forearm, and convex
    # wherever both are (v3 put the forearm itself through smax, which halved its slope at the onset and added curvature).
    a = np.maximum(forearm(x, y), 0.0); b = np.maximum(smax(0.0, edge_carve(x, y), P['smax_eps']), 0); p = P['arm_blend_p']
    d = (a ** p + b ** p) ** (1.0 / p)
    return np.where(_hard(x, y), 0.0, d)

# ---------------------------------------------------------------------------------------------- belly (back)
def _bass_edge_spline():
    xs = np.arange(15.6, 29.8, 0.02); ye = []
    for xv in xs:
        ys = [y0 + (xv - x0) * (y1 - y0) / (x1 - x0) for (x0, y0), (x1, y1) in zip(np.roll(OUTLINE, 1, 0), OUTLINE)
              if (x0 - xv) * (x1 - xv) <= 0 and x0 != x1]
        ye.append(max(ys))
    return UnivariateSpline(xs, np.array(ye), k=5, s=len(xs) * 0.0004 ** 2)
_YE = _bass_edge_spline(); _YE1 = _YE.derivative()
def bass_edge_dist(x, y):
    x = np.asarray(x, float); xc = np.clip(x, 15.6, 29.8)
    return (_YE(xc) - np.asarray(y, float)) / np.sqrt(1 + _YE1(xc) ** 2)
def _bmode(mode=None):
    """The belly mode to use (argument, else PARAMS), checked: an unknown name must fail loudly, not fall through to 'capped'."""
    mode = P['belly_mode'] if mode is None else mode
    if mode not in BELLY_MODES: raise ValueError(f'unknown belly_mode {mode!r}: choose one of {BELLY_MODES}')
    return mode
def belly_depth(mode=None):
    mode = _bmode(mode)
    if mode in P['belly_variants']: return P['belly_variants'][mode]['D']
    return dict(precbs=P['belly_depth_precbs'], blend=P['belly_A'], swell=P['belly_A']).get(mode, P['belly_depth_capped'])
def back_drop(x, y, mode=None):
    """Belly's share of the back, height UP from the back plane (back_total minus the plain perimeter carve for the one-surface
    modes). Legacy modes: 'capped' (v2: bevel to back_half - back_skin - margin), 'precbs' (1.10"), 'blend', 'swell' (v3)."""
    x = np.asarray(x, float); y = np.asarray(y, float); mode = _bmode(mode)
    if mode in P['belly_variants']:                                 # v3.1 one-surface belly
        return back_total(x, y, mode) - back_edge_carve(x, y)
    if mode == 'swell':                                             # v3: the belly's share of the one-law back
        return back_total(x, y, 'swell') - _back_edge_v3(x, y)
    if mode == 'blend':
        x0, dx0, x1, dx1 = P['belly_xw']; w = S5((x - x0) / dx0) * (1 - S5((x - x1) / dx1))
        return P['belly_A'] * w * 2 * I5(np.clip(1 - np.maximum(bass_edge_dist(x, y), 0) / P['belly_W'], 0, 1)) * (y > 0)
    q = bass_edge_dist(x, y); Rb, on = P['belly_reach'], P['belly_onset']
    g = (on * I5((Rb - q) / on)) / (on * I5((Rb - P['edge_R']) / on))
    x0, dx0, x1, dx1 = P['belly_x']; wx = S5((x - x0) / dx0) * (1 - S5((x - x1) / dx1))
    y0, dy0 = P['belly_y']; wy = S5((y - y0) / dy0)
    return belly_depth(mode) * g * wx * wy

# ---- v3.1 belly: a bevel measured from the OUTER bass edge only (one-sided, so no medial axis on the horn)
def _bass_guide():
    """Smooth guide along the outer bass edge: quintic smoothing spline y(x) through the outline VERTICES from the back of the
    bass horn round the waist to the lower bout (tolerance belly_guide[2]; it stays within 0.01" of the outline polygon)."""
    (xa, ya), (xb, yb), tol = P['belly_guide']
    i0 = int(np.argmin(np.hypot(OUTLINE[:, 0] - xa, OUTLINE[:, 1] - ya))); i1 = int(np.argmin(np.hypot(OUTLINE[:, 0] - xb, OUTLINE[:, 1] - yb)))
    pts = OUTLINE[i0:i1 + 1]
    return UnivariateSpline(pts[:, 0], pts[:, 1], k=5, s=len(pts) * tol ** 2), float(pts[0, 0]), float(pts[-1, 0])
_GS, _GX0, _GX1 = _bass_guide(); _GS1 = _GS.derivative(1); _GS2 = _GS.derivative(2)
_GXA = _GX0 - 0.6                                                # the spline is continued (same polynomial) this far past its first vertex
_GT = np.arange(_GXA, _GX1 + 1e-9, 0.02)
from scipy.spatial import cKDTree as _KD0
_GTREE = _KD0(np.c_[_GT, _GS(_GT)])
def bass_guide_dist(x, y, foot=False):
    """EXACT signed normal distance (+ inside) from the smooth outer-bass-edge guide: nearest sample, then Newton on the foot point.
    Smooth (C3) wherever the foot is interior to the guide and q is short of the guide's centre of curvature."""
    x = np.asarray(x, float); y = np.broadcast_to(np.asarray(y, float), x.shape); sh = x.shape; x = x.ravel(); y = y.ravel()
    t = _GT[_GTREE.query(np.c_[x, y])[1]]
    for _ in range(4):
        f = _GS(t); f1 = _GS1(t); g = (t - x) + (f - y) * f1; dg = 1 + f1 * f1 + (f - y) * _GS2(t)
        t = np.clip(t - g / np.where(dg > 0.05, dg, 1.0), _GXA, _GX1)
    f = _GS(t); f1 = _GS1(t); q = ((f - y) - f1 * (t - x)) / np.sqrt(1 + f1 * f1)
    return (q.reshape(sh), t.reshape(sh)) if foot else q.reshape(sh)
def belly_w(x, y):
    """Belly window 0..1 (C2): rises up the back of the bass horn, holds through the waist, falls into the lower bout.
    The y ramp lies wholly where the back is flat (it only keeps the treble side out)."""
    x = np.asarray(x, float)
    if P['belly_mode'] not in P['belly_variants']: return _belly_w_v3(x, y)
    x0, dx0, x1, dx1 = P['belly_win']; y0, dy0 = P['belly_win_y']
    return S5((x - x0) / dx0) * (1 - S5((x - x1) / dx1)) * S5((np.asarray(y, float) - y0) / dy0)
def _belly_w_v3(x, y):
    x0, dx0, x1, dx1 = P['belly_xw']; y0, dy0 = P['belly_y']
    return S5((x - x0) / dx0) * (1 - S5((x - x1) / dx1)) * S5((np.asarray(y, float) - y0) / dy0)
def belly_bevel(x, y, mode=None):
    """The belly section law, before windowing: B(q) = k on I5((W - q)/on), k = D / (W - on/2).
    q = distance in from the outer bass edge. A straight bevel of slope k from the rim (depth D) that lands on the back plane
    with a C3-flat quartic over the last `on` inches and is exactly 0 beyond q = W."""
    v = P['belly_variants'][P['belly_mode'] if mode is None else mode]; k = v['D'] / (v['W'] - v['on'] / 2)
    x = np.asarray(x, float); y = np.asarray(y, float)
    return k * v['on'] * I5(np.clip((v['W'] - bass_guide_dist(x, y)) / v['on'], 0, None))
def _heel_fade(x, y):
    f0, f1 = P['heel_fade']   # the heel loft lands on the back PLANE: no carve on or right beside its footprint
    return S5((_box_dist(x, y, 0.0, P['tenon_end'], P['pocket_w'] / 2) - f0) / f1)
def _edge_fit_field():
    """Local reach of the back perimeter carve. Where the body is narrower than 2 x back_edge_W (both horns) the plain carve from
    the two edges met on the medial axis with a slope jump (a ridge). Here the reach is the lower envelope
        W(p) = min(back_edge_W, min over medial-axis points a of [c hw(a) + g |p - a|]),   (c, g, blur) = back_edge_fit
    so on the axis the reach is at most c x the local half-width and the carve is already flat (C3) before the two sides meet."""
    c, g, sig = P['back_edge_fit']; e = _f['e']; g0, g1 = np.gradient(e, H, H)
    ax = (e > 0.2) & (np.hypot(g0, g1) < 0.8) & (c * e < P['back_edge_W'])
    A = np.c_[_GX[ax], _GY[ax], c * e[ax]][::3]
    st = 5; cx = FX[::st]; cy = FY[::st]; CX, CY = np.meshgrid(cx, cy, indexing='ij'); W = np.full(CX.shape, P['back_edge_W'])
    for i in range(0, len(A), 400):
        a = A[i:i + 400]
        W = np.minimum(W, np.min(a[:, 2] + g * np.hypot(CX[..., None] - a[:, 0], CY[..., None] - a[:, 1]), axis=-1))
    from scipy.interpolate import RegularGridInterpolator
    Wf = RegularGridInterpolator((cx, cy), W, bounds_error=False, fill_value=None)(np.c_[_GX.ravel(), _GY.ravel()]).reshape(_GX.shape)
    return ndimage.gaussian_filter(np.minimum(Wf, P['back_edge_W']), sig / H, mode='nearest')
_SPL['WB'] = ndimage.spline_filter(_edge_fit_field(), order=3)
def back_edge_reach(x, y):
    """Local inward reach of the back perimeter carve (= back_edge_W except on the two horns)."""
    return np.clip(_f3('WB', x, y), 0.05, P['back_edge_W'])
def back_edge_carve(x, y, w=0.0):
    """Perimeter carve on the BACK, height UP from the back plane, C3-flat onset: A 2 I5(1 - E/W) with W = back_edge_reach and
    A = back_edge_A W / back_edge_W (same section, scaled, on the horns). `w` is kept for the v3 signature and ignored."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    W = back_edge_reach(x, y); A = P['back_edge_A'] * W / P['back_edge_W']
    return A * 2 * I5(np.clip(1 - np.maximum(_f3('E', x, y), 0) / W, 0, 1)) * _heel_fade(x, y)
def _back_edge_v3(x, y, w=0.0):
    """v3 law (kept so the v3 'swell' back can still be drawn for comparison)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    A = P['back_edge_A'] + (P['belly_A'] - P['back_edge_A']) * w; W = P['back_edge_W'] + (P['belly_W'] - P['back_edge_W']) * w
    t = np.clip(1 - np.maximum(_f3('E', x, y), 0) / W, 0, 1)
    return A * 2 * I5(t) * _heel_fade(x, y)
def back_total(x, y, mode=None):
    """The whole back carve, ONE height field (up from the back plane):
        back = (1 - w) perimeter(E) + w B(q),   w = belly_w(x, y)
    perimeter = back_edge_carve (distance E in from the whole outline), B = belly_bevel (distance q from the outer bass edge only).
    w, perimeter and B are each C2, so there is no separate scoop and no seam. The perimeter carve carries the heel fade; B needs
    none (it is exactly 0 beyond q = W, which is short of the heel footprint), so nothing fades ACROSS the bevel. mode: 'whisper' | 'blended' | 'full' (v3.1),
    or the legacy 'swell' (v3), 'blend', 'capped' (v2), 'precbs'."""
    mode = _bmode(mode)
    x = np.asarray(x, float); y = np.asarray(y, float)
    if mode in P['belly_variants']:
        x0, dx0, x1, dx1 = P['belly_win']; y0, dy0 = P['belly_win_y']
        w = S5((x - x0) / dx0) * (1 - S5((x - x1) / dx1)) * S5((y - y0) / dy0)
        return (1 - w) * back_edge_carve(x, y) + w * belly_bevel(x, y, mode)
    if mode == 'swell': return _back_edge_v3(x, y, _belly_w_v3(x, y))
    if mode == 'blend':
        p = P['back_blend_p']; return (back_drop(x, y, mode) ** p + _back_edge_v3(x, y) ** p) ** (1 / p)
    return smax(back_drop(x, y, mode), _back_edge_v3(x, y), P['smax_eps'])
def back_skin_offset(x, y, e=0.01):
    """VERTICAL offset from the finished back up to the chamber floor that leaves back_skin measured PERPENDICULAR to the back:
    back_skin sqrt(1 + |grad back_full|^2). FIRST ORDER ONLY (0.264 true where the back curves): kept for back_checks' estimate;
    the chamber floor itself is the exact 3-D offset in chamber_interior() (grey dilation with a ball, 0.2754 true)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    f = lambda a, b: back_full(a, b)
    return P['back_skin'] * np.sqrt(1 + ((f(x + e, y) - f(x - e, y)) / (2 * e)) ** 2 + ((f(x, y + e) - f(x, y - e)) / (2 * e)) ** 2)

# ---------------------------------------------------------------------------------------------- G2 edge fillet
def edge_fillet(theta_R, kappa_R, R=None):
    """Curvature-continuous edge (Concept A law). Starts on the top surface at d = R with its slope angle theta_R and
    normal curvature kappa_R, ends vertical on the side wall at d = 0 with curvature 0:
        kappa(sigma) = kappa_R (1 - u) + A sin(pi u),  u = sigma / L;   A, L solved so the tangent turns to vertical at d = 0.
    A true 1/8" circular arc cannot be G2 to the top; this is the G2 fillet with a 1/8" setback."""
    R = P['edge_R'] if R is None else R
    turn = math.pi / 2 - theta_R
    def curve(A, L, n=600):
        sg = np.linspace(0, L, n); u = sg / L; k = kappa_R * (1 - u) + A * np.sin(np.pi * u)
        th = theta_R + np.concatenate([[0], np.cumsum((k[1:] + k[:-1]) / 2 * np.diff(sg))])
        dd = -np.concatenate([[0], np.cumsum((np.cos(th[1:]) + np.cos(th[:-1])) / 2 * np.diff(sg))])
        zz = -np.concatenate([[0], np.cumsum((np.sin(th[1:]) + np.sin(th[:-1])) / 2 * np.diff(sg))])
        return sg, k, th, R + dd, zz
    def F(v):
        A, L = v; sg, k, th, d, z = curve(A, L); return [th[-1] - theta_R - turn, d[-1]]
    A, L = fsolve(F, [turn / (4 * R / math.pi), R * 1.6])
    sg, k, th, d, z = curve(A, L)
    return dict(A=A, L=L, kappa_peak=float(k.max()), setback_side=float(-z[-1]), d=d, z=z, k=k,
                min_R=1 / float(k.max()), end_err=(float(th[-1] - math.pi / 2), float(d[-1])))

def _snap_to_R(x, y):
    e = 1e-3
    for _ in range(25):
        d = sdf_outline(np.array([x]), np.array([y]))[0] - P['edge_R']
        gx = (sdf_outline(np.array([x + e]), np.array([y]))[0] - sdf_outline(np.array([x - e]), np.array([y]))[0]) / 2 / e
        gy = (sdf_outline(np.array([x]), np.array([y + e]))[0] - sdf_outline(np.array([x]), np.array([y - e]))[0]) / 2 / e
        l = math.hypot(gx, gy); gx /= l; gy /= l; x -= d * gx; y -= d * gy
    return x, y, gx, gy
def fillet_station(x, y, e=0.004):
    """Slope angle and curvature of the top surface at d = R along the outward normal (one-sided, top side only)."""
    x, y, gx, gy = _snap_to_R(x, y)
    f = lambda s: -top_drop(np.array([x - gx * s]), np.array([y - gy * s]))[0]
    z0, z1, z2 = f(0), f(-e), f(-2 * e)
    d1 = (3 * z0 - 4 * z1 + z2) / (2 * e); d2 = (z0 - 2 * z1 + z2) / e ** 2
    th = math.atan(-d1); kap = -d2 / (1 + d1 * d1) ** 1.5
    return (x, y), th, kap
# Report stations: named points on or near the outline where the edge roll is sampled. From the plan file (STATIONS):
# bass_horn, bass_upper_bout, fhole_side, forearm_start_edge, forearm_deepest, tail, treble_waist, treble_cutaway,
# fhole_pinch, facet_full, treble_lower_bout, bass_cutaway (v3.3: four added), thigh_rest, rib_contact (v3.4: treble-waist
# back on the thigh, bass upper-bout back at the ribs)
STATIONS = dict(BL.STATIONS)

# ---------------------------------------------------------------------------------------------- compound edge (v3)
def _roll_profile(rho, n=4000):
    """Normalised roll on a level face: setback 1, level with zero curvature at d = 1, vertical with zero curvature at d = 0.
    kappa(u) = A T(u): S5 ramp up over [0, rho], plateau, S5 ramp down over [1 - rho, 1]. Returns (d ascending, drop, min R, k3)."""
    def curve(A, L):
        sg = np.linspace(0, L, n); u = sg / L; k = A * S5(u / rho) * (1 - S5((u - (1 - rho)) / rho)); ds = np.diff(sg)
        th = np.r_[0, np.cumsum((k[1:] + k[:-1]) / 2 * ds)]
        d = 1 - np.r_[0, np.cumsum((np.cos(th[1:]) + np.cos(th[:-1])) / 2 * ds)]
        z = np.r_[0, np.cumsum((np.sin(th[1:]) + np.sin(th[:-1])) / 2 * ds)]
        return k, th, d, z
    A, L = fsolve(lambda v: [curve(*v)[1][-1] - math.pi / 2, curve(*v)[2][-1]], [1.2, 1.6])
    k, th, d, z = curve(A, L); d = np.clip(d, 0, 1); d[-1] = 0.0
    k3 = float(np.interp(math.radians(3.0), th, d))             # d/a where the roll first exceeds 3 degrees
    return d[::-1].copy(), z[::-1].copy(), 1 / float(k.max()), k3
_RD, _RZ, ROLL_MINR, ROLL_K3 = _roll_profile(P['edge_rho'])
ROLL_SIDE = float(_RZ[0])                                         # side-wall setback per unit of face setback
def roll_drop(d, a):
    """Additive edge roll (in): d = distance in from the outline, a = local setback. 0 for d >= a; a ROLL_SIDE at d = 0."""
    d = np.maximum(np.asarray(d, float), 0); a = np.broadcast_to(np.asarray(a, float), d.shape)
    return np.where(a > 1e-6, a * np.interp(np.clip(d / np.maximum(a, 1e-6), 0, 1), _RD, _RZ), 0.0)

# ---- v3.1 outline curve: ONE smooth closed C2 curve replaces the 182-vertex polygon for everything the edge roll does
from scipy.interpolate import splprep as _splprep, splev as _splev
from scipy.spatial import cKDTree as _KD
def _fit_outline():
    """Periodic cubic smoothing spline (C2) fitted to the plan outline points (chord-length parameter, rms tolerance
    edge_fit_sigma), resampled at edge_ds of arc. Returns xy, s, ds, unit tangent, INWARD unit normal, plan curvature
    (+ where the body is convex), perimeter, max miss of the 182 points, tck."""
    Pc = np.vstack([OUTLINE, OUTLINE[:1]]); u = np.r_[0, np.cumsum(np.hypot(*np.diff(Pc, axis=0).T))]; u /= u[-1]
    tck, _ = _splprep([Pc[:, 0], Pc[:, 1]], u=u, per=True, k=3, s=len(OUTLINE) * P['edge_fit_sigma'] ** 2)
    uu = np.linspace(0, 1, 400001); x, y = _splev(uu, tck); sa = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]
    n = int(round(sa[-1] / P['edge_ds'])); si = np.arange(n) * (sa[-1] / n); ui = np.interp(si, sa, uu)
    x, y = _splev(ui, tck); dx, dy = _splev(ui, tck, 1); ddx, ddy = _splev(ui, tck, 2); sp = np.hypot(dx, dy)
    t = np.c_[dx, dy] / sp[:, None]; k = (dx * ddy - dy * ddx) / sp ** 3; xy = np.c_[x, y]
    ccw = 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y) > 0
    nrm = np.c_[-t[:, 1], t[:, 0]] * (1 if ccw else -1); k = k if ccw else -k
    miss = float(_KD(xy).query(OUTLINE)[0].max())
    return xy, si, sa[-1] / n, t, nrm, k, float(sa[-1]), miss, tck
EO, ES, EDS, ET, EN, EK, EPER, EFIT_MISS, _ETCK = _fit_outline()
_ETREE = _KD(EO)
def _feature_radius(step=4, chunk=256):
    """Radius of the largest circle that touches the outline at each sample from the inside and contains no other
    outline point: min over q of |q - c|^2 / (2 (q - c).n). It is the convex plan radius of curvature where nothing else
    is near, and half the local width where two branches of the outline face each other (horn tips). A roll whose
    setback stays below it has ONE nearest outline point everywhere in its band, i.e. it never reaches the medial axis."""
    idx = np.arange(0, len(EO), step); out = np.empty(len(idx))
    for a in range(0, len(idx), chunk):
        j = idx[a:a + chunk]; D = EO[None, :, :] - EO[j, None, :]
        den = 2 * (D * EN[j, None, :]).sum(-1); num = (D * D).sum(-1)
        out[a:a + chunk] = np.where(den > 1e-12, num / np.maximum(den, 1e-12), np.inf).min(1)
    r = np.interp(np.arange(len(EO)), np.r_[idx, len(EO)], np.r_[out, out[0]])
    return np.minimum(np.minimum(r, 1 / np.maximum(EK, 1e-9)), 99.0)
EFEAT = _feature_radius()
def edge_foot(x, y, reach=None):
    """Foot point on the smooth outline curve. Returns (d, s): d = signed distance (+ inside the body), s = arc position
    of the foot (continuous, 0 <= s < EPER). Nearest dense sample, then one curvature-corrected Newton step, so d and s are
    continuous with continuous gradient (no facets, no per-sample steps). With reach, points further than reach from the
    curve are skipped and come back d = +inf, s = 0 (the roll is 0 there)."""
    x = np.asarray(x, float); y = np.asarray(y, float); p = np.c_[x.ravel(), y.ravel()]
    if reach is None: i = _ETREE.query(p, workers=-1)[1]; ok = slice(None)
    else:
        i = _ETREE.query(p, distance_upper_bound=reach, workers=-1)[1]; ok = i < len(EO); i = i[ok]; p = p[ok]
    r = p - EO[i]; t = ET[i]; nn = EN[i]; k = EK[i]
    uu = r[:, 0] * t[:, 0] + r[:, 1] * t[:, 1]; v = r[:, 0] * nn[:, 0] + r[:, 1] * nn[:, 1]
    st = np.clip(uu / np.maximum(1 - k * v, 0.15), -EDS, EDS)
    cx = r[:, 0] - t[:, 0] * st - 0.5 * k * st * st * nn[:, 0]; cy = r[:, 1] - t[:, 1] * st - 0.5 * k * st * st * nn[:, 1]
    nx = nn[:, 0] - k * st * t[:, 0]; ny = nn[:, 1] - k * st * t[:, 1]
    dd = (cx * nx + cy * ny) / np.hypot(nx, ny)
    d = np.full(x.size, np.inf); s = np.zeros(x.size); d[ok] = dd; s[ok] = np.mod(ES[i] + st, EPER)
    return d.reshape(x.shape), s.reshape(x.shape)
def outline_sdf(x, y):
    """Signed distance to the smooth outline curve, + inside. Valid everywhere (the nearest point of a closed curve is
    always along its normal). This is the distance the edge roll uses; bodylib.sdf_outline is the raw polygon."""
    return edge_foot(x, y)[0]
_BODY = {}
def body_grid():
    """(sdf, inside) on bodylib's evaluation grid (BL.X, BL.Y), measured from the SMOOTH outline curve. v3.1 merge: every mask
    that is combined with top_full / back_full or with the roll comes from this curve (checks, chamber, render_io), never from
    the bodylib polygon: the curve sits up to 0.0085 in outside the polygon, where the roll is still far from its full depth."""
    if 'sdf' not in _BODY: _BODY['sdf'] = outline_sdf(BL.X, BL.Y); _BODY['ins'] = _BODY['sdf'] > 0
    return _BODY['sdf'], _BODY['ins']
def _at_s(arr, s):
    """Periodic linear interpolation of a per-sample outline quantity at arc position s."""
    q = np.asarray(s, float) / EDS; i0 = np.floor(q).astype(int); f = q - i0; n = len(arr)
    return arr[i0 % n] * (1 - f) + arr[(i0 + 1) % n] * f

def _unimodal(F):
    """Largest function <= F on the circle that only rises with distance (either way) from the global minimum of F."""
    n = len(F); i0 = int(np.argmin(F)); G = np.roll(F, -i0); h = n // 2
    G[:h + 1] = np.minimum.accumulate(G[h::-1])[::-1]; G[h:] = np.minimum.accumulate(G[h:])
    return np.roll(G, i0)
def _rate_limit(raw, lip, w):
    """C2-smooth a <= raw with |da/ds| <= lip, and no new dips: cone (Lipschitz) lower envelope, flat erosion over +-w of
    arc, then a C2 compact (triweight) kernel of half-width w. The kernel only averages values the erosion has already
    made <= the envelope at its centre, so a <= raw holds exactly; plateaus and minima keep their raw value."""
    r = int(math.ceil(max(float(raw.max() - raw.min()), 1e-3) / (lip * EDS))) + 2
    cone = -lip * EDS * np.abs(np.arange(-r, r + 1.0)); nw = max(int(round(w / EDS)), 1)
    m = ndimage.grey_erosion(raw.astype(float), structure=cone, mode='wrap')
    m = ndimage.minimum_filter1d(m, 2 * nw + 1, mode='wrap')
    ker = (1 - (np.arange(-nw, nw + 1) / (nw + 1.0)) ** 2) ** 3; ker /= ker.sum()
    return ndimage.convolve1d(m, ker, mode='wrap')
_ELAW = {}
def edge_law(mode=None):
    """Roll setback round the outline (per dense sample of the smooth curve). Returns dict(s, xy, a_top, a_back, top_raw,
    back_raw, thin, cap, bcap, fh_raw, fh_mono, glue, d_fhole, d_guard, T_edge, neck, R_feat, kappa).
    Cached per (edge mode, belly mode, plan cap, pocket ease): the back roll depends on the belly (T_edge, glue limit, bcap)."""
    mode = P['edge_mode'] if mode is None else mode; key = (mode, _bmode(None), P['edge_plan_cap'], P['edge_neck_ease'])
    if key in _ELAW: return _ELAW[key]
    n = len(EO); ex, ey = EO[:, 0], EO[:, 1]
    T = P['THICK'] - top_drop(ex, ey) - back_total(ex, ey)                  # thickness ON the outline, before the rolls
    thin = np.maximum(P['edge_share'] * (T - P['edge_w_min']) / ROLL_SIDE, 0.04)
    cap = P['edge_plan_cap'] * EFEAT                                          # never reach the medial axis / the centre of plan curvature
    GF = _segdist(FHOLE_POLY, ex, ey); GG = _segdist(GUARD, ex, ey)
    GJ = np.maximum(_segdist(JACK, ex, ey) - P['jack_pad'], 0)
    neck = (np.abs(ey) < P['pocket_w'] / 2) & (ex < 19.0)
    floor = np.minimum.reduce([np.full(n, P['edge_R']), thin, cap])
    amax = P['edge_a_max']
    fh_raw = (GF - P['edge_F_keep']) / ROLL_K3; fh_mono = _unimodal(np.minimum(fh_raw, amax))
    glue = (P['back_half'] - P['edge_glue_clear'] - back_total(ex, ey)) / ROLL_SIDE   # back roll ends below the glue plane
    bcap = np.full(n, amax)                                                   # v3.1 belly: the belly cut replaces the big back roundover
    if P['belly_mode'] in P['belly_variants']:                                # eased to `roll` only where the belly really is at the rim
        v = P['belly_variants'][P['belly_mode']]
        bcap = amax + (v['roll'] - amax) * S5((belly_w(ex, ey) * belly_bevel(ex, ey) / v['D'] - 0.15) / 0.60)
    W = None
    if mode == 'ergo':                                                        # v3.4
        W, top_raw, back_raw, a_top, a_back = _ergo_law(n, neck, cap, thin, fh_mono, GG, GJ, glue, floor, ex, ey)
    elif mode == 'uniform':
        top_raw = back_raw = a_top = a_back = floor
    elif mode == 'varedge':                                                   # v3.3: 1/8" where seen from the front
        W, anchors = hidden_window(GG)
        ab = P['edge_back_a_max']
        if P['belly_mode'] in P['belly_variants']:                            # same belly ease as compound, relative to the back max
            v = P['belly_variants'][P['belly_mode']]
            bcap = ab + (min(v['roll'], ab) - ab) * S5((belly_w(ex, ey) * belly_bevel(ex, ey) / v['D'] - 0.15) / 0.60)
        else: bcap = np.full(n, ab)
        na = np.minimum(P['edge_neck_a'], cap); NE = P['edge_neck_ease']
        sn = ndimage.distance_transform_edt(np.tile(~neck, 3))[n:2 * n] * EDS
        w = S5(sn / NE) if NE > 0 else np.ones(n); capf = np.where(sn < 0.75 * NE, 9.0, cap) if NE > 0 else cap
        target = P['edge_R'] + (P['edge_hid_a'] - P['edge_R']) * W
        top_raw = np.maximum(np.minimum.reduce([target, fh_mono, GG - P['edge_guard_clear'], GJ, thin, capf]), floor)
        back_raw = np.maximum(np.minimum.reduce([np.full(n, ab), thin, capf, glue, bcap]), floor)
        ez = lambda a: np.where(neck, na, np.minimum(a, P['edge_neck_a'] + np.maximum(a - P['edge_neck_a'], 0) * w))
        a_top = ez(_rate_limit(top_raw, P['edge_hid_lip'], P['edge_sig'])); a_back = ez(_rate_limit(back_raw, P['edge_lip'], P['edge_sig']))
        top_raw = np.maximum(top_raw, a_top); back_raw = np.maximum(back_raw, a_back)
        assert float((np.maximum(a_top, a_back) / EFEAT).max()) <= P['edge_plan_cap'] + 1e-9, 'pocket ease exceeds the plan cap'
        assert max(P['edge_hid_a'], ab) <= amax, 'edge_a_max must stay >= every zone maximum (roll reach, crease-scan band)'
    else:
        top_raw = np.minimum.reduce([np.full(n, amax), fh_mono, GG - P['edge_guard_clear'], GJ, thin, cap])
        back_raw = np.minimum.reduce([np.full(n, amax), thin, cap, glue, bcap])
        top_raw = np.maximum(top_raw, floor); back_raw = np.maximum(back_raw, floor)
        na = np.minimum(P['edge_neck_a'], cap)                                # under the neck (placeholder edge) and at the pocket mouth
        NE = P['edge_neck_ease']                                              # default 2.0 (env SC_NECK_EASE); 0 = the plain 0.10/in limiter
        if NE > 0:                                                            # pocket ease = its own C2 blend over NE in of arc, not the 0.10/in limiter
            sn = ndimage.distance_transform_edt(np.tile(~neck, 3))[n:2 * n] * EDS       # arc distance beyond the pocket mouths (periodic)
            w = S5(sn / NE); capf = np.where(sn < 0.75 * NE, 9.0, cap)       # the pocket-corner plan cap is carried by the ease
            top_raw = np.maximum(np.minimum.reduce([np.full(n, amax), fh_mono, GG - P['edge_guard_clear'], GJ, thin, capf]), floor)
            back_raw = np.maximum(np.minimum.reduce([np.full(n, amax), thin, capf, glue, bcap]), floor)
            ez = lambda a: np.where(neck, na, np.minimum(a, P['edge_neck_a'] + np.maximum(a - P['edge_neck_a'], 0) * w))
            a_top = ez(_rate_limit(top_raw, P['edge_lip'], P['edge_sig'])); a_back = ez(_rate_limit(back_raw, P['edge_lip'], P['edge_sig']))
            top_raw = np.maximum(top_raw, a_top); back_raw = np.maximum(back_raw, a_back)
            assert float((np.maximum(a_top, a_back) / EFEAT).max()) <= P['edge_plan_cap'] + 1e-9, 'pocket ease exceeds the plan cap'
        else:
            top_raw = np.where(neck, np.minimum(top_raw, na), top_raw); back_raw = np.where(neck, np.minimum(back_raw, na), back_raw)
            a_top = _rate_limit(top_raw, P['edge_lip'], P['edge_sig']); a_back = _rate_limit(back_raw, P['edge_lip'], P['edge_sig'])
    _ELAW[key] = dict(s=ES, xy=EO, a_top=a_top, a_back=a_back, top_raw=top_raw, back_raw=back_raw, thin=thin, cap=cap, bcap=bcap,
                      fh_raw=fh_raw, fh_mono=fh_mono, glue=glue, d_fhole=GF, d_guard=GG, T_edge=T, neck=neck, R_feat=EFEAT, kappa=EK, W_hid=W)
    return _ELAW[key]
def _segments_to_raw(n, bounds, lip):
    """Piecewise-constant levels round the outline -> S5 ramps. bounds = list of (s, v_before, v_after) in arc order. Each step is
    replaced by an S5 ramp of length 1.875 |dv| / lip placed on the HIGHER side, so every lower-level zone keeps its full extent;
    overlapping ramps take the min. Max slope of each ramp = lip."""
    s = ES; raw = np.empty(n); order = sorted(bounds, key=lambda b: b[0])
    for k, (sb, v0, v1) in enumerate(order):                                  # level after boundary k holds until boundary k+1
        sn = order[(k + 1) % len(order)][0]; m = _arc(sb, s) < _arc(sb, sn) if len(order) > 1 else np.ones(n, bool); raw[m] = v1
    for sb, v0, v1 in order:
        if abs(v1 - v0) < 1e-9: continue
        L = 1.875 * abs(v1 - v0) / lip; lo = min(v0, v1)
        d = _arc(sb, s) if v1 > v0 else _arc(s, sb)                            # distance into the higher side
        ramp = np.where(d <= L, lo + abs(v1 - v0) * S5(d / L), np.inf); raw = np.minimum(raw, ramp)
    return raw
def _ergo_law(n, neck, cap, thin, fh_mono, GG, GJ, glue, floor, ex, ey):
    """v3.4 'ergo' edge law (setbacks; see the PARAMS docstring)."""
    E = P['edge_ergo']; lip = E['lip']; _, an = hidden_window(GG); s_eye, s_end = an['s_eye'], an['s_end']
    k = int(np.argmin(FHOLE_POLY[:, 0])); s_up = float(edge_foot(FHOLE_POLY[k:k + 1, 0], FHOLE_POLY[k:k + 1, 1])[1][0])
    m = (_arc(s_eye, ES) < _arc(s_eye, s_end)); i = np.nonzero(m)[0][np.argmin(thin[m])]; s_thin = float(ES[i])
    bt = np.nonzero((EO[:, 1] > 2) & (EO[:, 0] < 14.5))[0]; s_tb = float(ES[bt[np.argmax(EK[bt])]])
    tt = np.nonzero((EO[:, 1] < -3) & (EO[:, 0] < 16.5))[0]; s_tt = float(ES[tt[np.argmax(EK[tt])]])
    tw = np.nonzero((EO[:, 1] < -3) & (EO[:, 0] < E['waist_end_x']) & (EO[:, 0] > 16.5))[0]; s_we = float(ES[tw[np.argmax(EO[tw, 0])]])
    f, fh, ar, lo = E['front'], E['fhole'], E['arm'], E['lower']
    front = _segments_to_raw(n, [(s_up - E['fhole_ahead'], f, fh), (s_eye, fh, ar), (s_thin, ar, lo), (s_end, lo, f)], lip)
    b, be, h = E['back'], E['back_ergo'], E['tip_half']
    back = _segments_to_raw(n, [(s_tb - h, be, b), (s_tb + h, b, be), (s_we, be, b), (s_tt + h, b, be)], lip)
    tdr = top_drop(ex, ey); seam = np.maximum((P['top_half'] - tdr - E['seam_eps']) / ROLL_SIDE, ar)   # wall top stays above the glue
    na = np.minimum(P['edge_neck_a'], cap); NE = P['edge_neck_ease']                                 # plane wherever v3.3 did
    sn = ndimage.distance_transform_edt(np.tile(~neck, 3))[n:2 * n] * EDS
    w = S5(sn / NE) if NE > 0 else np.ones(n); capf = np.where(sn < 0.75 * NE, 9.0, cap) if NE > 0 else cap
    top_raw = np.maximum(np.minimum.reduce([front, fh_mono, GG - P['edge_guard_clear'], GJ, thin, capf, seam]), floor)
    glue_e = glue - (E['glue_clear'] - P['edge_glue_clear']) / ROLL_SIDE                              # belly: the glue plane (+0.10) is the limit
    back_raw = np.maximum(np.minimum.reduce([back, thin, capf, glue_e]), floor)
    ez = lambda a: np.where(neck, na, np.minimum(a, P['edge_neck_a'] + np.maximum(a - P['edge_neck_a'], 0) * w))
    a_top = ez(_rate_limit(top_raw, lip, P['edge_sig'])); a_back = ez(_rate_limit(back_raw, lip, P['edge_sig']))
    top_raw = np.maximum(top_raw, a_top); back_raw = np.maximum(back_raw, a_back)
    assert float((np.maximum(a_top, a_back) / EFEAT).max()) <= P['edge_plan_cap'] + 1e-9, 'pocket ease exceeds the plan cap'
    assert max(f, fh, ar, lo, b, be) <= P['edge_a_max'] + 1e-9
    _ERGO_AN.update(s_up=s_up, s_eye=s_eye, s_thin=s_thin, s_end=s_end, s_bass_tip=s_tb, s_treble_tip=s_tt, s_waist_end=s_we,
                    front_target=front, back_target=back)
    return None, top_raw, back_raw, a_top, a_back
_ERGO_AN = {}
def _arc(s0, s1):
    """Arc length from s0 forward (increasing s) to s1 on the closed outline."""
    return np.mod(np.asarray(s1, float) - s0, EPER)
def hidden_window(GG=None):
    """v3.3: where the FRONT roll may grow (W = 1) and where it stays edge_R (W = 0), per outline sample, with S5 ramps of
    edge_hid_ramp inches of arc that end exactly at each anchor (W = 0 at the anchor, so the 1/8" frame is untouched up to it).
      bass cutaway inside   bass pocket mouth -> bass horn tip (max plan curvature), W = 0 at tip + edge_horn_margin
      treble cutaway inside treble horn tip -> treble pocket mouth (the pocket ease brings both down to edge_neck_a at the mouths)
      lower bout            from (arc foot of the f-hole's aft-most vertex) + edge_arm_after on the bass rim, round the tail and the
                            treble lower bout, to where the pickguard comes within edge_tlb_guard of the outline (guard tail).
    Returns (W, anchors)."""
    if GG is None: GG = _segdist(GUARD, EO[:, 0], EO[:, 1])
    n = len(EO); Lr = P['edge_hid_ramp']; m = P['edge_horn_margin']; s = ES
    neck = (np.abs(EO[:, 1]) < P['pocket_w'] / 2) & (EO[:, 0] < 19.0)
    e = np.nonzero(np.diff(np.r_[neck[-1], neck].astype(int)))[0]           # samples where the neck zone starts / ends
    mb = int(e[np.argmax(EO[e, 1])]); mt = int(e[np.argmin(EO[e, 1])])     # bass mouth (y > 0), treble mouth (y < 0)
    bt = np.nonzero((EO[:, 1] > 2) & (EO[:, 0] < 14.5))[0]; tb = int(bt[np.argmax(EK[bt])])
    tt = np.nonzero((EO[:, 1] < -3) & (EO[:, 0] < 16.5))[0]; tr = int(tt[np.argmax(EK[tt])])
    k = int(np.argmax(FHOLE_POLY[:, 0])); s_eye = float(edge_foot(FHOLE_POLY[k:k + 1, 0], FHOLE_POLY[k:k + 1, 1])[1][0])
    s0 = s_eye + P['edge_arm_after']
    tl = np.nonzero((EO[:, 1] < -1.0) & (EO[:, 0] > 26.0) & (GG < P['edge_tlb_guard']))[0]   # treble lower bout: guard tail reaches the edge
    s1 = float(ES[tl[np.argmin(_arc(s0, ES[tl]))]])
    def seg(a, b, ra=True, rb=True):                                         # window on the arc a -> b (forward), 0 outside
        u = _arc(a, s); L = _arc(a, b); inn = u <= L
        return np.where(inn, (S5(u / Lr) if ra else 1.0) * (S5((L - u) / Lr) if rb else 1.0), 0.0)
    W = np.maximum.reduce([seg(ES[mb], ES[tb] - m, ra=False), seg(ES[tr] + m, ES[mt], rb=False), seg(s0, s1)])
    return W, dict(s_eye=s_eye, s_start=s0, s_end=s1, eye_foot=tuple(EO[int(round(s_eye / EDS)) % n].round(2)),
                   start_at=tuple(EO[int(round(s0 / EDS)) % n].round(2)), end_at=tuple(EO[int(round(s1 / EDS)) % n].round(2)),
                   bass_tip=tuple(EO[tb].round(2)), treble_tip=tuple(EO[tr].round(2)), bass_mouth=tuple(EO[mb].round(2)), treble_mouth=tuple(EO[mt].round(2)))
def edge_setback(x, y, which='top', mode=None, s=None):
    """Local roll setback a at (x, y): the law interpolated continuously at the foot point on the smooth outline."""
    if s is None: s = edge_foot(x, y)[1]
    return _at_s(edge_law(mode)['a_' + which], s)
def _roll_at(x, y, which):
    d, s = edge_foot(x, y, reach=P['edge_a_max'] + 0.03); return roll_drop(d, edge_setback(x, y, which, s=s))
def top_full(x, y, sd=None):
    """Finished top: carve + edge roll, drop below the top plane. sd is accepted for compatibility and ignored: the roll
    is measured from the smooth outline curve (edge_foot), not from the polygon distance."""
    return top_drop(x, y) + _roll_at(x, y, 'top')
def back_full(x, y, sd=None):
    """Finished back: carve + edge roll, height above the back plane. sd ignored (see top_full)."""
    return back_total(x, y) + _roll_at(x, y, 'back')
def edge_section(i, which='top', n=1500, span=1.2):
    """Normal section through outline sample i: (d, z) of the finished face, plus its minimum radius of curvature in the roll."""
    L = edge_law(); a = float(L['a_' + which][i]); d = np.linspace(0, math.sqrt(span), n) ** 2
    x = EO[i, 0] + EN[i, 0] * d; y = EO[i, 1] + EN[i, 1] * d
    z = (top_drop(x, y) if which == 'top' else back_total(x, y)) + roll_drop(d, a)
    m = (d > 0.002 * a) & (d < 0.995 * a)
    if m.sum() < 20: return d, -z, np.inf, a
    t = np.sqrt(d); d1, z1 = np.gradient(d, t), np.gradient(z, t); d2, z2 = np.gradient(d1, t), np.gradient(z1, t)
    k = np.abs(d1 * z2 - z1 * d2) / np.maximum((d1 * d1 + z1 * z1) ** 1.5, 1e-12)
    return d, -z, 1 / float(np.max(k[m])), a
def edge_crease_scan(which='top', h=0.005, u_lo=0.30, fn=None, box=None, full=False, setback=None, dist=None):
    """Crease detector on the finished face, fine xy grid (spacing h) over the roll band (d >= u_lo a, clear of the
    near-vertical part). Second differences over h, 2h, 3h in 4 directions:
        D_m = (z(p + m h e) - 2 z(p) + z(p - m h e)) / (m h)      smooth surface: m h z''   slope jump J at offset t h: J (1 - t/m)
        jump   = max |D_1|                                         change of slope across ONE cell (curvature + creases)
        crease = max |-2.5 D_1 + 8 D_2 - 4.5 D_3|                  the curvature part cancels; what is left is a real slope jump
    Returns dict(jump, jump_at, crease, crease_at) and, with full=True, the grids (x, y, crease map, jump map).
    fn / setback / dist: another height field with its own setback (x, y) -> a and edge distance (x, y) -> d, to scan an
    older edge with the same detector. A true crease keeps its value when h is halved; curvature residue falls ~8x."""
    fn = (top_full if which == 'top' else back_full) if fn is None else fn
    x0, x1, y0, y1 = (12.9, 31.3, -6.5, 6.5) if box is None else box
    hc = 10 * h; cx = np.arange(x0, x1, hc); cy = np.arange(y0, y1, hc); CX, CY = np.meshgrid(cx + hc / 2, cy + hc / 2, indexing='ij')
    dc = outline_sdf(CX, CY); mc = (dc > -0.75 * hc) & (dc < P['edge_a_max'] + 0.75 * hc + 3 * h)
    mk = np.repeat(np.repeat(mc, 10, 0), 10, 1); fx = x0 + h * (np.arange(mk.shape[0]) + 0.5); fy = y0 + h * (np.arange(mk.shape[1]) + 0.5)
    ii, jj = np.nonzero(mk); px, py = fx[ii], fy[jj]
    d, s = edge_foot(px, py); a = _at_s(edge_law()['a_' + which], s) if setback is None else setback(px, py)
    if dist is not None: d = dist(px, py)
    Z = np.full(mk.shape, np.nan); Z[ii, jj] = np.where(d > 0, fn(px, py), np.nan)
    U = np.full(mk.shape, np.nan); U[ii, jj] = (d - 3.0 * h) / np.maximum(a, 1e-6)
    J = np.zeros(mk.shape); C = np.zeros(mk.shape); c = Z[3:-3, 3:-3]
    def D(m, di, dj):
        sl = lambda q, r: Z[3 + q:Z.shape[0] - 3 + q, 3 + r:Z.shape[1] - 3 + r]
        return (sl(m * di, m * dj) - 2 * c + sl(-m * di, -m * dj)) / (m * h * math.hypot(di, dj))
    for di, dj in ((1, 0), (0, 1), (1, 1), (1, -1)):
        D1, D2, D3 = D(1, di, dj), D(2, di, dj), D(3, di, dj)
        J[3:-3, 3:-3] = np.fmax(J[3:-3, 3:-3], np.where(np.isfinite(D1), np.abs(D1), 0))
        cr = np.abs(-2.5 * D1 + 8 * D2 - 4.5 * D3); C[3:-3, 3:-3] = np.fmax(C[3:-3, 3:-3], np.where(np.isfinite(cr), cr, 0))
    ok = np.isfinite(U) & (U >= u_lo); J = np.where(ok, J, 0); C = np.where(ok, C, 0)
    kj = np.unravel_index(np.argmax(J), J.shape); kc = np.unravel_index(np.argmax(C), C.shape)
    R = dict(jump=float(J[kj]), jump_at=(round(float(fx[kj[0]]), 2), round(float(fy[kj[1]]), 2)),
             crease=float(C[kc]), crease_at=(round(float(fx[kc[0]]), 2), round(float(fy[kc[1]]), 2)), h=h, u_lo=u_lo)
    if full: R.update(x=fx, y=fy, C=np.where(ok, C, np.nan), J=np.where(ok, J, np.nan))
    return R
def _runs(mask):
    """Contiguous True runs of a per-sample outline mask (periodic): list of (arc length, (x, y) start, (x, y) end)."""
    n = len(mask); out = []
    if not mask.any(): return out
    if mask.all(): return [(round(EPER, 2), tuple(EO[0].round(2)), tuple(EO[-1].round(2)))]
    k0 = int(np.argmin(mask)); m = np.roll(mask, -k0); e = np.diff(np.r_[0, m.astype(int), 0]); st = np.nonzero(e == 1)[0]; en = np.nonzero(e == -1)[0]
    for a, b in zip(st, en): out.append((round(float((b - a) * EDS), 2), tuple(EO[(a + k0) % n].round(2)), tuple(EO[(b - 1 + k0) % n].round(2))))
    return out
def edge_checks():
    """v3.1 edge checks (every number is computed here; nothing is assumed)."""
    L = edge_law(); nn = ~L['neck']; n = len(EO); R = {}; xy = lambda i: tuple(EO[int(i)].round(2))
    R['outline_fit'] = dict(max_miss_of_182_points=EFIT_MISS, samples=n, ds=EDS, perimeter=EPER,
                            max_curve_to_polygon=float(_segdist(OUTLINE, EO[:, 0], EO[:, 1]).max()))
    i = int(np.argmin(np.where(nn, L['R_feat'], 9))); R['plan_feature_radius_min'] = dict(R=float(L['R_feat'][i]), at=xy(i), a_top=float(L['a_top'][i]), a_back=float(L['a_back'][i]))
    for w in ('top', 'back'):
        a = L['a_' + w]; i = int(np.argmin(np.where(nn, a, 9))); da = (np.roll(a, -1) - np.roll(a, 1)) / (2 * EDS); j = int(np.argmax(np.abs(da)))
        r = a / L['R_feat']; q = int(np.argmax(r))
        R['edge_a_' + w] = dict(min=float(a[i]), at=xy(i), max=float(a.max()), frac_at_full=float((a[nn] >= P['edge_a_max'] - 5e-4).mean()),
                                frac_ge_045=float((a[nn] >= 0.45).mean()), frac_lt_030=float((a[nn] < 0.30).mean()),
                                over_raw=float(np.max(a - L[w + '_raw'])), max_dads=float(abs(da[j])), max_dads_at=xy(j),
                                max_a_over_plan_radius=float(r[q]), max_a_over_plan_radius_at=xy(q))
    # pocket mouths: first / last sample outside the neck zone
    e = np.nonzero(np.diff(np.r_[L['neck'][-1], L['neck']].astype(int)))[0]
    R['pocket_mouth'] = [dict(at=xy(k), a_top=round(float(L['a_top'][k]), 3), a_back=round(float(L['a_back'][k]), 3)) for k in e]
    for w in ('top', 'back'):                                                # arc from each mouth until a is within 5% of full
        a = L['a_' + w]; far = np.nonzero(nn & (a >= 0.95 * P['edge_a_max']))[0]
        R['pocket_ease_arc_' + w] = [round(float(np.min(np.minimum(np.abs(far - k), n - np.abs(far - k))) * EDS), 2) for k in e] if len(far) else None
    # wall, ON the outline
    wall = L['T_edge'] - ROLL_SIDE * (L['a_top'] + L['a_back']); i = int(np.argmin(wall))
    R['edge_wall_min'] = dict(wall=float(wall[i]), at=xy(i), T_edge=float(L['T_edge'][i]), a_top=float(L['a_top'][i]), a_back=float(L['a_back'][i]),
                              arc_below_0135=float((wall < 0.135).sum() * EDS))
    # bass lower bout: y > 0 from the bass waist (smallest y on the bass side, x 19-22) round to the centreline at the tail
    wv = np.nonzero((EO[:, 1] > 0) & (EO[:, 0] > 19) & (EO[:, 0] < 22))[0]; i0 = int(wv[np.argmin(EO[wv, 1])])
    tl = np.nonzero((EO[:, 0] > 30) & (np.abs(EO[:, 1]) < 0.02))[0]; i1 = int(tl[np.argmin(np.abs(EO[tl, 1]))])
    seg = np.arange(min(i0, i1), max(i0, i1) + 1); a = L['a_top'][seg]
    def extrema(v, tol=5e-4):                                               # plateau-aware local minima / maxima
        out = []; lo = hi = 0; trend = 0
        for k in range(1, len(v)):
            if v[k] > v[lo] + tol and trend <= 0:
                if trend < 0: out.append(('min', lo))
                trend = 1; hi = k
            elif v[k] < v[hi] - tol and trend >= 0:
                if trend > 0: out.append(('max', hi))
                trend = -1; lo = k
            if v[k] < v[lo]: lo = k
            if v[k] > v[hi]: hi = k
        return out
    ext = extrema(a)
    R['bass_lower_bout_a_top'] = dict(span=(xy(seg[0]), xy(seg[-1])), n_local_minima=sum(1 for t, _ in ext if t == 'min'),
                                      extrema=[(t, round(float(a[k]), 3), xy(seg[k])) for t, k in ext],
                                      a_at_ends=(round(float(a[0]), 3), round(float(a[-1]), 3)),
                                      max_dads=float(np.max(np.abs(np.gradient(a, EDS)))))
    fm = L['fh_mono'] < P['edge_a_max'] - 1e-9
    R['fhole_reduced_run'] = dict(arc_fhole_term_active=float(fm.sum() * EDS), runs_a_top_below_045=_runs(nn & (L['a_top'] < 0.45) & (EO[:, 1] > 0) & (EO[:, 0] > 19)),
                                  fhole_to_outline=float(L['d_fhole'].min()), at=xy(int(np.argmin(L['d_fhole']))))
    if P['edge_mode'] == 'ergo' and _ERGO_AN:                                # v3.4: target vs reached, and where a zone was capped
        A = _ERGO_AN; out = {}
        for w, tg in (('top', A['front_target']), ('back', A['back_target'])):
            short = nn & (L[w + '_raw'] < tg - 0.01)                   # capped by wood / glue / guard / pocket, not by ramp smoothing
            out[w] = dict(capped_runs=[(r[0], r[1], r[2]) for r in _runs(short) if r[0] >= 0.05], max=float(L['a_' + w][nn].max()))
        out['anchors'] = {k: round(v, 2) for k, v in A.items() if not hasattr(v, '__len__')}
        R['ergo'] = out
    if L.get('W_hid') is not None:                                           # v3.3: the approved front / hidden rule, tested directly
        W, an = hidden_window(L['d_guard']); g = nn & (L['a_top'] > P['edge_R'] + 1e-3); vis = nn & (W <= 0)
        first = float(np.min(_arc(an['s_eye'], ES[g & (_arc(an['s_eye'], ES) < 15.0)]))) if g.any() else None
        R['varedge'] = dict(anchors=an, front_max_where_seen=float(L['a_top'][vis].max()), front_max_where_seen_at=xy(np.nonzero(vis)[0][np.argmax(L['a_top'][vis])]),
                            growth_runs=_runs(g), growth_outside_window_arc=float((g & (W <= 0)).sum() * EDS),
                            eye_to_first_growth_arc=first, eye_rule_ok=bool(first is not None and first >= P['edge_arm_after'] - 1e-6),
                            front_max=float(L['a_top'][nn].max()), back_max=float(L['a_back'][nn].max()),
                            front_seen_arc=float(vis.sum() * EDS), front_hidden_arc=float((nn & (W > 0)).sum() * EDS))
    # glue plane: where does the straight side wall start and stop, relative to z = -top_half
    zg = -P['top_half']; zb = -P['THICK'] + back_total(EO[:, 0], EO[:, 1]) + ROLL_SIDE * L['a_back']; zt = -top_drop(EO[:, 0], EO[:, 1]) - ROLL_SIDE * L['a_top']
    bb = zb > zg - P['edge_glue_clear'] + 1e-9; bt = zt <= zg
    i = int(np.argmax(zb)); j = int(np.argmin(zt))
    R['glue_plane'] = dict(z_glue=zg, wall_bottom_highest=float(zb[i]), wall_bottom_highest_at=xy(i), wall_bottom_ok_all_round=bool(not bb.any()),
                           wall_bottom_fail_arc=float(bb.sum() * EDS), wall_bottom_fail_runs=_runs(bb),
                           wall_top_lowest=float(zt[j]), wall_top_lowest_at=xy(j), wall_top_ok_all_round=bool(not bt.any()),
                           wall_top_below_glue_arc=float(bt.sum() * EDS), wall_top_below_glue_runs=_runs(bt))
    # smallest convex radius of the finished edge, every 4th sample (0.02"), pocket (neck zone) excluded
    for w in ('top', 'back'):
        best = (np.inf, 0)
        for k in np.nonzero(nn)[0][::4]:
            r = edge_section(int(k), w, n=500)[2]
            if r < best[0]: best = (r, int(k))
        R['edge_min_convex_R_' + w] = dict(R=float(best[0]), at=xy(best[1]), a=float(L['a_' + w][best[1]]))
    for w in ('top', 'back'):
        c = edge_crease_scan(w); R['edge_crease_' + w] = {k: c[k] for k in ('jump', 'jump_at', 'crease', 'crease_at', 'h', 'u_lo')}
        cx, cy = c['crease_at']; c2 = edge_crease_scan(w, h=c['h'] / 2, box=(cx - 0.2, cx + 0.2, cy - 0.2, cy + 0.2))
        R['edge_crease_' + w].update(crease_same_spot_at_half_h=c2['crease'], jump_same_spot_at_half_h=c2['jump'])
    return R

# ---------------------------------------------------------------------------------------------- set neck / heel
def fret_x(n): return P['scale'] * (1 - 2 ** (-n / 12))
def neck_depth(x):
    """Repo neck-geometry.js law: depth1 * radius(x)/radius(fret1) (back of neck below the BOARD top)."""
    r = lambda xx: 7.25 + (9.5 - 7.25) * xx / 25.5
    return 0.82 * r(x) / r(fret_x(1))
def neck_width(x): return 1.65 + (2.2 - 1.65) * x / fret_x(21)
X15 = fret_x(P['heel_start_fret'])
_NE = OUTLINE[(OUTLINE[:, 0] < 17.6) & (np.abs(OUTLINE[:, 1]) < 1.3)]; _NE = _NE[np.argsort(_NE[:, 1])]
def body_end_x(y):
    """x where the body outline closes under the neck at lateral y (repo trace; the treble side runs deeper)."""
    return np.interp(np.asarray(y, float), _NE[:, 1], _NE[:, 0])
def _beta_law(mn):
    """Regularized incomplete beta I_u(m+1, n+1): 0->1, first m and last n derivatives zero at the ends.
    (2,2) is the quintic S5. (5,2) starts very flat (gentle CONCAVE onset under the neck) and lands G2 on the back plane."""
    m, n = mn; return lambda u: betainc(m + 1, n + 1, np.clip(u, 0, 1))
_LAW_D = _beta_law(P['heel_law_depth']); _LAW_S = _beta_law(P['heel_law_shape'])
def heel_back_z(x, y):
    """Lowest material surface (z up, body top = 0) of neck + heel + body. Heel loft (Concept A, re-timed):
        u  = (x - x0) / (x_end(y) - x0),   x0 = x15 - heel_lead
        tD = I_u(6, 3)   (Beta(5,2) law, depth)        tS = I_u(9, 3)   (Beta(8,2) law, section shape)
        D  = Dn(x) + (board_height + THICK - Dn(x)) tD                depth below the board top
        a  = wn(x)/2 + (pocket_w/2 - wn(x)/2) tS                       half-width -> pocket width
        p  = 2.3 + 1.7 tS                                              C neck -> squared foot
        z  = board_height - D ((1 - tS)(1 - |y/a|^p)^(1/p) + tS)
    Inside the outline: z = -THICK + back_drop(x, y)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    x0 = X15 - P['heel_lead']; xe = body_end_x(y); u = (x - x0) / np.maximum(xe - x0, 0.3)
    tD = _LAW_D(u); tS = _LAW_S(u)
    xc = np.minimum(x, fret_x(21)); Dn = neck_depth(xc); wn = neck_width(xc) / 2
    D = Dn + (P['board_height'] + P['THICK'] - Dn) * tD; a = wn + (P['pocket_w'] / 2 - wn) * tS
    p = P['heel_p'][0] + (P['heel_p'][1] - P['heel_p'][0]) * tS
    uu = np.clip(np.abs(y) / a, 0, 1); sh = (1 - tS) * (1 - uu ** p) ** (1 / p) + tS
    zh = np.where(np.abs(y) < a, P['board_height'] - D * sh, np.nan)
    return np.where(sdf_outline(x, y) > 0, -P['THICK'] + back_total(x, y), zh)
def heel_dev_at_fret15():
    """How far the heel surface has left the plain neck back at fret 15 (centreline), in inches."""
    return float(P['board_height'] - neck_depth(X15) - heel_back_z(np.array([X15]), np.array([0.0]))[0])
def flank_r(z):
    """Heel-flank fillet radius vs height (z <= 0): flank_r_min at the body top, flank_r_max at the back plane (C2)."""
    return P['flank_r_min'] + (P['flank_r_max'] - P['flank_r_min']) * S5(-np.asarray(z, float) / P['THICK'])

HEEL_BLEND = f"""
SET-NECK HEEL / BODY JUNCTION (parametric; not part of top_drop).
Datum. Pocket datum x_p = {P['pocket_datum_x']} (outline at the pocket sides). Measuring from the outline
  centreline point would run a 3" pocket into the neck-pickup route.
Pocket. {P['pocket_w']} wide x {P['pocket_len']} long -> ends at {P['pocket_datum_x'] + P['pocket_len']:.3f}; board end {P['board_end']};
  tenon {P['tenon_w']} wide to x = {P['tenon_end']} (0.10 before the neck-PU route). Mortise floor at
  z = -insertion_depth = {-P['insertion_depth']:.3f}. Split at z = -top_half = {-P['top_half']:.3f}
  (>= insertion_depth + {P['split_margin']}). The treble wall is short: the cutaway closes the outline early.
  v3.2: tenon_end ({P['tenon_end']}) now only bounds the heel-fade box of the back carve. The final plan's hidden tongue continues
  {P['tongue_w']} wide to x = tongue_end = {P['tongue_end']} ({P['trem']['spring']['x0'] - P['tongue_end']:.3f} short of the spring-cavity front wall at {P['trem']['spring']['x0']}).
  It is a 2-D footprint only: its z section is NOT modelled. At mortise-floor depth ({-P['insertion_depth']:.3f}) both single-coil
  routes (~0.75 deep) cut through it; run below them and it crosses the split ({-P['top_half']:.3f}) into the back half. The
  That gap to the spring cavity matters only if the tongue goes below the spring roof ({P['trem']['spring']['z_top']}).
Top side. Body top is held planar over the neck seat (x 15.3-18.30, |y|<1.25). The neck rises {P['board_height']} out of a
  crisp pocket line, as on a traditional bolt-on body. The pocket wall / neck side line is a GLUE SEAM, not a machined fillet;
  optional {P['root_break']:.4f}" break. The board overhang to 18.17 hides the top glue line.
Back side (heel loft, heel_back_z). Visibly starts at fret 15 (x15 = {X15:.3f}; plain neck back {neck_depth(X15):.3f} below the
  board top). The loft parameter starts heel_lead = {P['heel_lead']} earlier (x0 = {X15 - P['heel_lead']:.3f}) so the concave onset is
  gentle enough for a 1/2" ball nose; at fret 15 the heel has left the plain neck back by only {{dev15:.3f}}".
    u = (x - x0) / (x_end(y) - x0),  x_end(y) = body_end_x(y)
    tD = I_u(6,3) (Beta(5,2) law)    tS = I_u(9,3) (Beta(8,2) law)
    D = Dn + (0.375 + 1.75 - Dn) tD,  a = wn/2 + (pocket_w/2 - wn/2) tS,  p = 2.3 + 1.7 tS,
    z = 0.375 - D ((1-tS)(1-|y/a|^p)^(1/p) + tS)
  Both laws have zero 1st and 2nd derivatives at u = 1, so the heel bottom lands on the back plane G2 and heel and body
  back read as one surface. Their first 5 (depth) / 8 (shape) derivatives vanish at u = 0, so the heel grows out of the
  neck C without a visible line. The back belly is exactly 0 for y < 1.2, so the landing zone is a plane.
Flank fillet. Where the heel flanks (|y| = a) meet the body end face and horn walls, a rolling-ball fillet
    r_f(z) = {P['flank_r_min']} + ({P['flank_r_max']} - {P['flank_r_min']}) S5(-z / 1.75)
  i.e. 0.25" at the body top, 0.375" at the back plane: every MACHINED concave radius on the heel >= 0.25" (1/2" ball nose).
  Where it reaches the back plane it hands over to the {P['edge_R']}" G2 edge fillet law of the body outline.
Pocket mouths. The outline under the neck is a placeholder. The compound edge roll narrows to edge_neck_a = {P['edge_neck_a']}"
  at the pocket mouths and keeps that width under the neck, so the body edge does not die to a sharp arris; from each mouth
  it eases back to the full roll over edge_neck_ease = {P['edge_neck_ease']}" of outline (S5 blend, v3.1): it meets the neck side as a {P['edge_neck_a']}" roll and is cut off by it (see checks: pocket_mouth).
Machining. Heel loft + flank fillets are cut from the back after glue-up (assembly fixture), 1/2" ball nose, 3-D finishing.
"""

HEEL_BLEND = HEEL_BLEND.replace('{dev15:.3f}', f'{heel_dev_at_fret15():.3f}')

# ---------------------------------------------------------------------------------------------- checks
def chamber_masks(fn=None):
    """Design-note wing chamber (y > 1.9, x < 29.6, sdf > rim) and the RETREATED chamber: wing minus
    (top drop > 0.55 or belly > cap) dilated by the frame. Returns (nominal, retreated, top_bad, belly_bad)."""
    fn = top_drop if fn is None else fn
    sdf, INS = body_grid(); D = np.where(INS, fn(BL.X, BL.Y), 0); Bd = back_total(BL.X, BL.Y)
    wing = INS & (BL.Y > P['spine_y']) & (BL.X < P['solid_tail_x']) & (sdf > P['rim'])
    bad_top = INS & (D > P['chamber_carve_limit'])
    bad_back = INS & (Bd > P['belly_depth_capped'] + 1e-9)
    solid = ndimage.distance_transform_edt(~(bad_top | bad_back)) * G < P['frame']
    return wing, wing & ~solid, bad_top, bad_back
def _ball(r, h):
    """Footprint and cap height sqrt(r^2 - rho^2) of a ball of radius r on a grid of spacing h (for exact offset surfaces)."""
    n = int(np.ceil(r / h)); g0, g1 = np.mgrid[-n:n + 1, -n:n + 1] * h; rho2 = g0 ** 2 + g1 ** 2; fp = rho2 <= r * r
    return fp, np.where(fp, np.sqrt(np.maximum(r * r - rho2, 0)), 0.0)
_CHAMBER = {}
def chamber_interior(h=0.025):
    """The wing chamber as it is cut (v3.1 merge: moved here from render_io.py so the model, the checks and the render share ONE
    interior). Grid x 11.0-31.5, y -6.7-6.7 at h; every mask is measured from the smooth outline curve. Returns a dict:
      X, Y, sd (outline_sdf), a_t, a_b, td, bk, zt (finished top, z), zb (finished back, z), ch (chamber footprint), sch (signed
      distance into it, plan corners rounded 0.30), zin_top (ceiling), zin_back (floor; outside the chamber the back half's glue face).
    Ceiling: the lower of (a) v3's law, finished top - top_skin - 0.06 frame swell - 0.22 corner fillet, and (b) the EXACT 3-D
      offset of the finished top by top_skin (grey erosion with a ball), so the skin is its full thickness measured perpendicular to
      the top wherever the top slopes (forearm, edge roll). v3 used the vertical 0.157 alone: 0.144 true under the forearm.
    Floor: the EXACT 3-D offset of the finished back by back_skin (grey dilation with a ball; the back checker's fix) plus the
      0.125 corner fillet. v3 used the vertical 0.276: 0.252 true on the belly slope."""
    key = (h, _bmode(None), P['edge_mode'])
    if key in _CHAMBER: return _CHAMBER[key]
    gx = np.arange(11.0, 31.5, h); gy = np.arange(-6.7, 6.7, h); X, Y = np.meshgrid(gx, gy, indexing='ij'); TH = P['THICK']; SPLIT = -P['top_half']
    sd, sa = edge_foot(X, Y); a_t = _at_s(edge_law()['a_top'], sa); a_b = _at_s(edge_law()['a_back'], sa)
    td = top_drop(X, Y); bk = back_total(X, Y); zt = -(td + roll_drop(sd, a_t)); zb = -TH + bk + roll_drop(sd, a_b); ins = sd > 0
    sdm = lambda m: (ndimage.distance_transform_edt(m) - ndimage.distance_transform_edt(~m)) * h
    wing = ins & (Y > P['spine_y']) & (X < P['solid_tail_x']) & (sd > P['rim'])
    bad = ins & ((td > P['chamber_carve_limit']) | (bk > P['belly_depth_capped'] + 1e-9))
    keep = wing & ~(ndimage.distance_transform_edt(~bad) * h < P['frame'])
    sch = sdm(sdm(keep) > 0.30) + 0.30; ch = sch > 0; d = np.clip(sch, 0, None)             # plan corners rounded to 0.30
    corner = lambda rc: rc - np.sqrt(np.maximum(rc * rc - np.clip(rc - d, 0, rc) ** 2, 0))
    skin = P['top_skin'] + 0.06 * (1 - S5(d / 0.25))                                         # 5 mm diaphragm, 6.5 mm frame fillet
    fp, cap = _ball(P['top_skin'], h); ceil3 = ndimage.grey_erosion(np.where(ins, zt, 9.0), footprint=fp, structure=cap)
    fp, cap = _ball(P['back_skin'], h); floor3 = ndimage.grey_dilation(np.where(ins, zb, -9.0), footprint=fp, structure=cap)
    # v3.2 liner seat: over the liner footprint + glue land the roof is the plain top_skin offset (no frame swell, no corner fillet),
    # so the 0.6 mm veneer lies flat and the liner's square ledge lands 5.6 mm below the top. Nothing is recessed into the skin.
    Lr = P['liner']; dfo = np.where(_inside(FHOLE_POLY, X, Y), -1.0, 1.0) * _segdist(FHOLE_POLY, X, Y)   # + outside the f-hole outline
    seat = ch & (dfo < Lr['wall_out'] + Lr['land'])
    zin_top = np.where(ch, np.maximum(np.minimum(np.where(seat, zt - P['top_skin'], zt - skin - corner(0.22)), ceil3), SPLIT), SPLIT)
    zin_open = zin_top.copy()
    # v3.2 pickguard-screw bosses: a solid >= 2 r column hanging from the roof to z_bot (root fillet root_r), at every guard screw
    # whose boss + fillet reaches the chamber footprint. Roof only: no post to the back.
    Bo = P['guard_bosses']; bosses = []
    for sx, sy in GUARD_SCREWS:
        i = int(round((sx - gx[0]) / h)); j = int(round((sy - gy[0]) / h)); s_at = float(sch[i, j])
        if s_at <= -(Bo['r'] + Bo['root_r']): continue
        rho = np.hypot(X - sx, Y - sy); zb_ = Bo['z_bot']
        u = np.clip(Bo['r'] + Bo['root_r'] - rho, 0, Bo['root_r'])                 # root fillet: concave quarter round
        fil = Bo['root_r'] - np.sqrt(np.maximum(Bo['root_r'] ** 2 - u ** 2, 0))
        zb_loc = np.where(rho <= Bo['r'], zb_, zin_open - fil * (rho < Bo['r'] + Bo['root_r']))
        zin_top = np.where(ch, np.minimum(zin_top, np.maximum(zb_loc, zb_)), zin_top)
        bosses.append(dict(xy=(sx, sy), sch_at_screw=round(s_at, 3), guard_sdf=round(float(sdf_guard(np.array([sx]), np.array([sy]))[0]), 3)))
    zin_back = np.where(ch, np.minimum(floor3 + corner(0.125), SPLIT), np.minimum(SPLIT, zt))
    liner = (dfo < Lr['wall_out']) & (dfo > -Lr['inset'])                           # liner wood in plan (inner wall = outline inset)
    l_top = zt - P['top_skin'] - Lr['veneer']; l_bot = l_top - Lr['depth']
    _CHAMBER[key] = dict(h=h, gx=gx, gy=gy, X=X, Y=Y, sd=sd, a_t=a_t, a_b=a_b, td=td, bk=bk, zt=zt, zb=zb, ch=ch, sch=sch,
                         zin_top=zin_top, zin_back=zin_back, ceil_vertical=zt - zin_top, floor_vertical=zin_back - zb,
                         zin_top_no_bosses=zin_open, bosses=bosses, dfo=dfo, seat=seat, liner=liner, liner_top=l_top, liner_bot=l_bot)
    return _CHAMBER[key]
def chamber_wood_3d(hf=0.0125, C=None):
    """Minimum TRUE 3-D wood round the chamber, and where: top skin (ceiling -> finished top incl. its roll), back skin (floor ->
    finished back incl. its roll) and rim (chamber wall -> anything outside: top, back, both rolls, side wall). Independent of how
    the interior was built: the outside is re-sampled here on its own finer grid (hf) plus roll strips and the side wall, and
    the distances are nearest-neighbour distances in 3-D. Also the thinnest VERTICAL skins and the chamber volume.
    P['wood_min_3d'] (0.155 in = 3.94 mm, roasted-alder review) is the floor every one of them must clear."""
    from scipy.spatial import cKDTree
    C = chamber_interior() if C is None else C; X, Y, ch, h = C['X'], C['Y'], C['ch'], C['h']; TH = P['THICK']
    x0, x1 = X[ch].min() - 0.8, X[ch].max() + 0.8; y0, y1 = Y[ch].min() - 0.8, Y[ch].max() + 0.8
    fx = np.arange(x0, x1, hf); fy = np.arange(y0, y1, hf); FXg, FYg = np.meshgrid(fx, fy, indexing='ij'); m = outline_sdf(FXg, FYg) > 0
    top = [np.c_[FXg[m], FYg[m], -top_full(FXg[m], FYg[m])]]; back = [np.c_[FXg[m], FYg[m], -TH + back_full(FXg[m], FYg[m])]]
    L = edge_law(); k = np.nonzero((EO[:, 0] > x0) & (EO[:, 0] < x1) & (EO[:, 1] > y0) & (EO[:, 1] < y1))[0][::2]
    u = (np.linspace(0, 1, 60) ** 2)[None, :]                                                # roll strips: dense where the roll is steep
    for w, lst in (('top', top), ('back', back)):
        a = np.maximum(L['a_' + w][k], 1e-3)[:, None]; dd = a * u; px = EO[k, :1] + EN[k, :1] * dd; py = EO[k, 1:] + EN[k, 1:] * dd
        z = -(top_drop(px, py) + roll_drop(dd, a)) if w == 'top' else -TH + back_total(px, py) + roll_drop(dd, a)
        lst.append(np.c_[px.ravel(), py.ravel(), z.ravel()])
    ezt = -(top_drop(EO[k, 0], EO[k, 1]) + ROLL_SIDE * L['a_top'][k]); ezb = -TH + back_total(EO[k, 0], EO[k, 1]) + ROLL_SIDE * L['a_back'][k]
    tz = np.linspace(0, 1, 120)[None, :]; wz = ezb[:, None] + tz * (ezt - ezb)[:, None]
    wall = np.c_[np.repeat(EO[k, 0], 120), np.repeat(EO[k, 1], 120), wz.ravel()]
    top = np.vstack(top); back = np.vstack(back); allp = np.vstack([top, back, wall])
    bnd = ch & ~ndimage.binary_erosion(ch, iterations=1); cz = np.linspace(0, 1, 60)
    cw = np.vstack([np.c_[X[bnd], Y[bnd], C['zin_back'][bnd] + t * (C['zin_top'][bnd] - C['zin_back'][bnd])] for t in cz])
    def near(tree_pts, pts):
        dq, _ = cKDTree(tree_pts).query(pts, workers=-1); i = int(np.argmin(dq))
        return dict(min=float(dq[i]), at=tuple(round(float(v), 2) for v in pts[i]))
    R = dict(top_skin=near(top, np.c_[X[ch], Y[ch], C['zin_top'][ch]]), back_skin=near(back, np.c_[X[ch], Y[ch], C['zin_back'][ch]]),
             rim=near(allp, cw))
    R['min'] = min(R[q]['min'] for q in ('top_skin', 'back_skin', 'rim')); R['required'] = P['wood_min_3d']; R['ok'] = bool(R['min'] >= P['wood_min_3d'])
    i = int(np.argmax(np.where(ch, C['ceil_vertical'], -1)))
    R['top_skin_vertical'] = dict(min=float(C['ceil_vertical'][ch].min()), max=float(C['ceil_vertical'].flat[i]),
                                  max_at=(round(float(X.flat[i]), 2), round(float(Y.flat[i]), 2)), nominal=P['top_skin'])
    R['back_skin_vertical_min'] = float(C['floor_vertical'][ch].min())
    R['floor_to_split_min'] = float((-P['top_half'] - C['zin_back'])[ch].min())
    R['chamber_area_in2'] = float(ch.sum() * h * h); R['chamber_in3'] = float((C['zin_top'] - C['zin_back'])[ch].clip(0).sum() * h * h)
    return R
def jack_plane():
    J = JACK - JACK.mean(0); w, v = np.linalg.eigh(J.T @ J); ax = v[:, -1]; nx = np.array([-ax[1], ax[0]])
    cx, cy = P['jack_center']; uu, vv = np.meshgrid(np.linspace(-0.6, 0.6, 41), np.linspace(-0.375, 0.375, 27))
    px = cx + uu * ax[0] + vv * nx[0]; py = cy + uu * ax[1] + vv * nx[1]; z = top_drop(px, py)
    A = np.c_[px.ravel(), py.ravel(), np.ones(px.size)]; c = np.linalg.lstsq(A, z.ravel(), rcond=None)[0]
    return float(np.max(np.abs(A @ c - z.ravel()))), float(outline_sdf(px, py).min())
def concave_radius(fn, band=0.15, h=0.02, region=None):
    """Min concave principal-curvature radius of z = -fn (tool's view), grid h, sdf > band. Returns (R, (x,y))."""
    cx = np.arange(13.0, 31.4, h); cy = np.arange(-6.6, 6.6, h); CX, CY = np.meshgrid(cx, cy, indexing='ij')
    z = -np.asarray(fn(CX, CY), float)
    fx, fy = np.gradient(z, h, h); fxx = np.gradient(fx, h, axis=0); fyy = np.gradient(fy, h, axis=1); fxy = np.gradient(fx, h, axis=1)
    W = np.sqrt(1 + fx ** 2 + fy ** 2); E = 1 + fx ** 2; F = fx * fy; Gg = 1 + fy ** 2
    L, M, N = fxx / W, fxy / W, fyy / W; det = E * Gg - F * F
    Hm = (E * N - 2 * F * M + Gg * L) / (2 * det); K = (L * N - M * M) / det; k1 = Hm + np.sqrt(np.maximum(Hm * Hm - K, 0))
    m = outline_sdf(CX, CY) > band
    if region is not None: m &= region(CX, CY)
    m[:2] = m[-2:] = False; m[:, :2] = m[:, -2:] = False
    kk = np.where(m, k1, -np.inf); i = np.argmax(kk)
    return (1 / kk.flat[i] if kk.flat[i] > 0 else np.inf), (round(float(CX.flat[i]), 2), round(float(CY.flat[i]), 2))
def heel_concave_radius():
    """Min concave radius (seen from the back-side tool) of the heel-loft bottom along x, swept over |y| <= 1.0.
    Sections across y are superellipse caps (convex from the back) by construction."""
    best = (np.inf, None, None)
    for yv in np.linspace(-1.0, 1.0, 41):
        xs = np.linspace(X15 - P['heel_lead'] - 0.3, float(body_end_x(yv)) - 0.005, 3000)
        w = -heel_back_z(xs, np.full_like(xs, yv)); ok = np.isfinite(w)
        if ok.sum() < 50: continue
        xo = xs[ok]; d1 = np.gradient(w[ok], xo); d2 = np.gradient(d1, xo); k = (d2 / (1 + d1 ** 2) ** 1.5)[3:-3]
        if k.max() > 0 and 1 / k.max() < best[0]: best = (round(1 / k.max(), 3), round(float(yv), 2), round(float(xo[3:-3][np.argmax(k)]), 2))
    return best

def surface_curvature(fn, h=0.02, band=0.15, region=None):
    """Principal curvatures of the back height field fn on a grid. Returns dict with the max slope, the min CONCAVE radius (the
    ball-nose limit), the min CONVEX radius (a ridge) and the tightest BOWL (both curvatures concave = a pocket), each with (x, y).
    Only points more than `band` inside the outline count (the edge roll is not part of fn)."""
    cx = np.arange(13.0, 31.4, h); cy = np.arange(-6.6, 6.6, h); CX, CY = np.meshgrid(cx, cy, indexing='ij')
    z = -np.asarray(fn(CX, CY), float)
    fx, fy = np.gradient(z, h, h); fxx = np.gradient(fx, h, axis=0); fyy = np.gradient(fy, h, axis=1); fxy = np.gradient(fx, h, axis=1)
    W = np.sqrt(1 + fx ** 2 + fy ** 2); E = 1 + fx ** 2; F = fx * fy; Gg = 1 + fy ** 2
    L, M, N = fxx / W, fxy / W, fyy / W; det = E * Gg - F * F
    Hm = (E * N - 2 * F * M + Gg * L) / (2 * det); K = (L * N - M * M) / det; r = np.sqrt(np.maximum(Hm * Hm - K, 0)); k1 = Hm + r; k2 = Hm - r
    m = outline_sdf(CX, CY) > band
    if region is not None: m &= region(CX, CY)
    m[:3] = m[-3:] = False; m[:, :3] = m[:, -3:] = False
    def pick(v):
        vv = np.where(m, v, -np.inf); i = int(np.argmax(vv)); return float(vv.flat[i]), (round(float(CX.flat[i]), 2), round(float(CY.flat[i]), 2))
    sl, sa = pick(np.degrees(np.arctan(np.hypot(fx, fy)))); kc, ca = pick(k1); kv, va = pick(-k2); kb, ba = pick(k2)
    R = lambda k: (round(1 / k, 3) if k > 1e-9 else float('inf'))
    return dict(max_slope_deg=round(sl, 2), slope_at=sa, min_concave_R=R(kc), concave_at=ca, min_convex_R=R(kv), convex_at=va,
                min_bowl_R=R(kb), bowl_at=ba)
def belly_relief(mode=None, stations=(18.0, 20.0, 22.0), depths=(0.5, 1.0, 2.0, 3.0)):
    """Relief (back_total, edge roll not included) at `depths` inches in from the bass edge, measured along the inward normal
    of the outline at the bass rim point of each station x. Returns {x: dict(rim=(x, y), relief=[...], at=[(x, y)...])}."""
    out = {}
    for xs in stations:
        ys = max(y0 + (xs - x0) * (y1 - y0) / (x1 - x0) for (x0, y0), (x1, y1) in zip(np.roll(OUTLINE, 1, 0), OUTLINE)
                 if (x0 - xs) * (x1 - xs) <= 0 and x0 != x1)
        i = int(_ETREE.query((xs, ys))[1]); d = np.array(depths); px = xs + EN[i, 0] * d; py = ys + EN[i, 1] * d
        out[xs] = dict(rim=(xs, round(float(ys), 2)), relief=[round(float(v), 3) for v in back_total(px, py, mode)],
                       at=[(round(float(a), 2), round(float(b), 2)) for a, b in zip(px, py)])
    return out
def back_checks():
    """Every check on the back surface (v3.1)."""
    R = {}; mode = _bmode(None); sdf, INS = body_grid()
    Bd = back_total(BL.X, BL.Y); wing, ret, bt, bb = chamber_masks()
    R['belly_mode'] = mode; R['belly_cap'] = P['belly_depth_capped']
    if mode in P['belly_variants']:
        v = P['belly_variants'][mode]; R['belly_law'] = dict(v, slope_deg=math.degrees(math.atan(v['D'] / (v['W'] - v['on'] / 2))))
    i = int(np.argmax(np.where(ret, Bd, -1))); R['belly_max_over_retreated_chamber'] = dict(belly=float(Bd.flat[i]), at=(round(float(BL.X.flat[i]), 2), round(float(BL.Y.flat[i]), 2)),
                                                                                         margin_to_cap=float(P['belly_depth_capped'] - Bd.flat[i]))
    R['belly_precbs_max_over_wing'] = float(np.max(back_drop(BL.X, BL.Y, 'precbs')[wing]))
    hx = (BL.X < P['tenon_end']) & (abs(BL.Y) < 1.15) & INS; R['belly_on_heel_footprint'] = float(np.max(Bd[hx]))
    # v3.2: the real rear opening (spring cavity + block cavity, rounded, block offset to the treble side), not v3's box; no cover
    # plate, so 'belly_on_trem_mouth_pad' (was 'belly_on_trem_cover') keeps the back flat for trem_mouth_pad round the open mouth
    mouth = rear_mouth_sdf(BL.X, BL.Y)
    for nm, pad in (('belly_on_trem_cavity', 0.0), ('belly_on_trem_mouth_pad', P['trem_mouth_pad'])):
        m = mouth > -pad; j = int(np.argmax(np.where(m, Bd, -1)))
        R[nm] = dict(max=float(Bd.flat[j]), at=(round(float(BL.X.flat[j]), 2), round(float(BL.Y.flat[j]), 2)), pad=pad)
    R['belly_relief'] = {f'x={k}': v for k, v in belly_relief().items()}
    R['back_surface'] = surface_curvature(back_total)                    # whole back, more than 0.15" inside the outline
    # bass horn inboard of the tip wrap (x > 14.6): the v3 medial-axis ridge was R 0.62
    R['back_surface_bass_horn'] = surface_curvature(back_total, region=lambda a, b: (a > 14.6) & (a < 18.6) & (b > 1.2))
    # where the bevel lands on the flat back (the faint y = 2 line of v3): convex here is the designed C3 landing, not a ridge
    R['back_surface_belly_landing'] = surface_curvature(back_total, region=lambda a, b: (a > 15.5) & (a < 27.5) & (b > 0.8) & (b < 3.4))
    # ---- glue line: finished back at the rim (carve + side-wall share of the roll) against the flat split
    L = edge_law(); nn = ~L['neck']; q = EO                                # ON the smooth outline, like the edge law's own glue term
    top_of_roll = back_total(q[:, 0], q[:, 1]) + ROLL_SIDE * L['a_back']; mg = np.where(nn, P['back_half'] - top_of_roll, 9); j = int(np.argmin(mg))
    R['glue_line_margin'] = dict(min=float(mg[j]), at=tuple(EO[j].round(2)), belly_at_rim=float(top_of_roll[j] - ROLL_SIDE * L['a_back'][j]),
                                 a_back=float(L['a_back'][j]), required=P['glue_margin_min'], ok=bool(mg[j] >= P['glue_margin_min']))
    bz = belly_w(EO[:, 0], EO[:, 1]) > 0.999
    if bz.any(): R['back_roll_through_belly'] = dict(a_back_min=float(L['a_back'][bz].min()), a_back_max=float(L['a_back'][bz].max()),
                                                     x_from=float(EO[bz, 0].min()), x_to=float(EO[bz, 0].max()))
    # ---- back skin under the belly: vertical-offset floor vs perpendicular-offset floor
    hq = 0.02; qx = np.arange(13.0, 30.0, hq); qy = np.arange(1.6, 6.6, hq); QX, QY = np.meshgrid(qx, qy, indexing='ij')
    retq = ndimage.map_coordinates(ret.astype(float), [(QX - BL.gx[0]) / G, (QY - BL.gy[0]) / G], order=0) > 0.5
    Bf = back_full(QX, QY); g0, g1 = np.gradient(Bf, hq, hq); sec = np.sqrt(1 + g0 ** 2 + g1 ** 2)
    j = int(np.argmax(np.where(retq, sec, 0)))
    R['back_skin'] = dict(nominal=P['back_skin'], perp_min_with_vertical_offset=float(P['back_skin'] / sec.flat[j]), at=(round(float(QX.flat[j]), 2), round(float(QY.flat[j]), 2)),
                          vertical_offset_needed_max=float(P['back_skin'] * sec.flat[j]),
                          floor_to_split_min=float(np.min((P['back_half'] - Bf - P['back_skin'] * sec)[retq])), floor_to_split_required=P['belly_margin'])
    return R

def top_concavity(fn=None, band=0.15, h=0.02, region=None):
    """Concavity detector for the top: the most negative principal curvature of the surface z = -fn (sign: convex crown +,
    valley / fold -), over the whole top further than band from the rim, and where it is. 0 or a rounding-size number
    means convex-or-flat everywhere. dict(kappa_min, at, R)."""
    R_, at = concave_radius(fn or top_drop, band=band, h=h, region=region)
    return dict(kappa_min=float(-1 / R_) if np.isfinite(R_) else 0.0, at=at, R=float(R_))
def forearm_onset(fracs=(0.3, 0.5, 0.7), band=0.55, ds=0.002, fn=None):
    """Sections perpendicular to the forearm zero line, at fracs of the way arm_A -> arm_B, on top_drop (no edge roll), kept
    band clear of the rim (0.55 = the audit's definition). Per section: max slope, where the slope passes 1 and 3 degrees,
    peak curvature and where. The blend is stated as the curvature ramp (_arm_ramp, 0 -> peak) followed by a constant-
    curvature arc to the rim; the old '1 degree to 95 % of max slope' width is gone (on a constant-curvature section it only
    measures how far the rim is)."""
    fn = fn or top_drop; A = np.array(P['arm_A']); B = np.array(P['arm_B']); n = np.array([_nx, _ny]); out = []
    for f in fracs:
        p0 = A + f * (B - A); s = np.arange(-2.0, 3.4, ds); x = p0[0] + n[0] * s; y = p0[1] + n[1] * s; sd = outline_sdf(x, y)
        z = np.asarray(fn(x, y), float); z1 = np.gradient(z, ds); z2 = np.gradient(z1, ds); sl = np.degrees(np.arctan(z1))
        k = z2 / (1 + z1 ** 2) ** 1.5; m = sd > band; m[:2] = m[-2:] = False; mx = float(sl[m].max())
        def first(v):
            i = np.where(m & (sl >= v))[0][0]; return float(s[i]), (round(float(x[i]), 2), round(float(y[i]), 2))
        s1, p1 = first(1.0); s3, p3 = first(3.0); i = int(np.argmax(np.where(m, k, -9)))
        j = int(np.argmin(np.where(m, k, 9)))
        out.append(dict(p0=(round(float(p0[0]), 2), round(float(p0[1]), 2)), max_slope_deg=mx, deg1_at=p1, deg3_at=p3,
                        deg1_to_deg3=s3 - s1, kappa_peak=float(k[i]),
                        kappa_peak_at=(round(float(x[i]), 2), round(float(y[i]), 2)), kappa_min=float(k[j]),
                        drop_at_end=float(z[m][-1]), end_at=(round(float(x[m][-1]), 2), round(float(y[m][-1]), 2))))
    return out
# ---------------------------------------------------------------------------------------------- v3.2: trem routes, bosses, liner, tongue
def route_sdf(x, y, which):
    """Signed plan distance (+ inside) to a trem route footprint: rounded rectangle (corner r) from P['trem'][which]."""
    t = P['trem'][which]; x = np.asarray(x, float); y = np.asarray(y, float); r = t['r']
    qx = np.abs(x - (t['x0'] + t['x1']) / 2) - ((t['x1'] - t['x0']) / 2 - r); qy = np.abs(y - t['yc']) - (t['hw'] - r)
    d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
    return -d
def rear_mouth_sdf(x, y):
    """The opening in the back (no cover plate): spring cavity + rear block cavity."""
    return np.maximum(route_sdf(x, y, 'spring'), route_sdf(x, y, 'block'))
def control_pocket_sdf(X, Y, h):
    """render_io.py's placeholder control pocket (guard inset 0.35, y < -1.5, x 19.8-27.2, plan corners 0.25), same grid rule."""
    sdm = lambda m: (ndimage.distance_transform_edt(m) - ndimage.distance_transform_edt(~m)) * h
    sg = sdf_guard(X, Y) * np.sign(sdf_guard(np.array([24.28]), np.array([-2.13]))[0])
    return sdm(sdm((sg > 0.35) & (Y < -1.5) & (X > 19.8) & (X < 27.2)) > 0.25) + 0.25
def trem_checks(C=None):
    """Routes against everything round them: chamber web, control-pocket web, top-slot cover (pickguard + plate: no visible
    change), split plane, humbucker route web, tongue."""
    C = chamber_interior() if C is None else C; X, Y, ch, h = C['X'], C['Y'], C['ch'], C['h']; T = P['trem']; R = {}
    dch = ndimage.distance_transform_edt(~ch) * h
    for k in ('slot', 'block', 'spring'):
        m = route_sdf(X, Y, k) > 0; R['web_' + k + '_to_chamber'] = float((dch[m] - 0.0).min()) if m.any() else None
    ctl = control_pocket_sdf(X, Y, h) > 0; dct = ndimage.distance_transform_edt(~ctl) * h
    R['web_block_to_control_pocket'] = float(dct[route_sdf(X, Y, 'block') > 0].min())
    R['web_spring_to_control_pocket'] = float(dct[route_sdf(X, Y, 'spring') > 0].min())
    hf = 0.005; qx = np.arange(T['slot']['x0'] - 0.01, T['slot']['x1'] + 0.01, hf); qy = np.arange(-2.0, 1.7, hf)
    QX, QY = np.meshgrid(qx, qy, indexing='ij'); s = route_sdf(QX, QY, 'slot') > 0
    plate = (QX > PLATE['x0']) & (QX < PLATE['x1']) & (np.abs(QY) < PLATE['hw'])
    bare = s & ~plate & ~in_guard(QX, QY)
    R['slot_uncovered_in2'] = float(bare.sum() * hf * hf)
    R['slot_outside_plate_under_guard_in2'] = float((s & ~plate & in_guard(QX, QY)).sum() * hf * hf)
    R['slot_min_guard_overlap'] = float(np.min(np.where(s & ~plate, sdf_guard(QX, QY), np.inf)))
    R['spring_roof_z'] = T['spring']['z_top']; R['spring_below_split_by'] = round(-P['top_half'] - T['spring']['z_top'], 4)
    R['block_spans_split'] = bool(T['block']['z_top'] > -P['top_half'] > T['block']['z_bot'])
    R['pivot_x'] = T['pivot_x']; R['pivot_to_slot_front'] = round(T['slot']['x0'] - T['pivot_x'], 3)
    R['pivot_wood_above_spring_cavity'] = -T['spring']['z_top']
    R['plate_x0_ahead_of_pivot'] = round(T['pivot_x'] - PLATE['x0'], 3)
    R['hb_route_floor_to_spring_roof_if_0.75_deep'] = round(-0.75 - T['spring']['z_top'], 3)
    R['tongue_end'] = P['tongue_end']; R['tongue_to_spring_front_wall'] = round(T['spring']['x0'] - P['tongue_end'], 3)
    tg = (X > P['tenon_end']) & (X < P['tongue_end']) & (np.abs(Y) < P['tongue_w'] / 2)
    R['tongue_to_chamber'] = float(dch[tg].min())
    R['ok'] = bool(R['slot_uncovered_in2'] == 0 and min(R['web_block_to_control_pocket'], R['web_spring_to_control_pocket']) > 0
                   and min(R[k] for k in R if k.startswith('web_') and k.endswith('_chamber')) >= P['rim'] and R['tongue_to_spring_front_wall'] > 0)
    return R
def boss_checks(C=None):
    """Bosses: which screws, solid diameter, wood round the screw, distance to the liner, volume taken from the chamber air."""
    C = chamber_interior() if C is None else C; X, Y, h, Bo = C['X'], C['Y'], C['h'], P['guard_bosses']
    out = []
    for b in C['bosses']:
        sx, sy = b['xy']; rho = np.hypot(X - sx, Y - sy); m = rho <= Bo['r']
        solid_z = np.max(np.where(m & C['ch'], C['zin_top'], -9))            # boss bottom (highest ceiling inside the 2r disc)
        lin = C['liner'] | (C['dfo'] < P['liner']['wall_out'])
        out.append(dict(b, solid_dia=2 * Bo['r'], bottom_z=round(float(solid_z), 3) if solid_z > -9 else None,
                        wood_below_top=round(-float(solid_z), 3) if solid_z > -9 else None,
                        clear_to_liner=round(float(np.min(np.where(lin, rho, np.inf)) - Bo['r'] - Bo['root_r']), 3)))
    dv = float(((C['zin_top_no_bosses'] - C['zin_top']) * C['ch']).sum() * h * h)
    return dict(bosses=out, n=len(out), volume_removed_in3=round(dv, 3),
                ok=bool(all(o['bottom_z'] is None or o['bottom_z'] <= Bo['z_bot'] + 1e-9 for o in out) and all(o['clear_to_liner'] > 0 for o in out)))
def liner_checks(C=None):
    """Liner seat: roof flat over footprint + land, seat clear of the frame swell, liner inside the chamber, gap to the floor."""
    C = chamber_interior() if C is None else C; Lr = P['liner']; h = C['h']; ch = C['ch']
    foot = C['dfo'] < Lr['wall_out']; seat = C['seat']
    cv = C['ceil_vertical'][seat]; R = dict(seat_area_in2=round(float(seat.sum() * h * h), 3),
                                            seat_skin_min=float(cv.min()), seat_skin_max=float(cv.max()), seat_flat=bool(cv.max() - cv.min() < 1e-6))
    R['footprint_inside_chamber'] = bool(np.all(ch[foot])); R['footprint_to_chamber_wall_min'] = float(C['sch'][foot].min())
    R['veneer_underside_z'] = float(np.max(C['liner_top'][foot])); R['liner_bottom_z'] = float(np.max(C['liner_bot'][foot]))
    R['liner_bottom_below_split'] = round(-P['top_half'] - R['liner_bottom_z'], 4)
    R['gap_to_floor_min'] = float(np.min((C['liner_bot'] - C['zin_back'])[foot]))
    lv = float(C['liner'].sum() * h * h * Lr['depth']); vv = float(ch.sum() * h * h * Lr['veneer'])
    R['liner_wood_in3'] = round(lv, 3); R['veneer_in3'] = round(vv, 3)
    R['throat_area_in2'] = round(float((C['dfo'] < -Lr['inset']).sum() * h * h), 3); R['fhole_area_in2'] = round(float((C['dfo'] < 0).sum() * h * h), 3)
    R['ok'] = bool(R['seat_flat'] and R['footprint_inside_chamber'] and R['footprint_to_chamber_wall_min'] >= 0.25 and R['gap_to_floor_min'] > 0)
    return R
def checks(verbose=True):
    R = {}
    R['evaluate'] = evaluate(top_drop, P['edge_R'], verbose=False)
    R['baseline_0.3'] = evaluate(arm_drop_repo, 0.3, verbose=False)
    sdf, INS = body_grid(); D = np.where(INS, top_drop(BL.X, BL.Y), np.nan)      # smooth-curve mask (bodylib.evaluate keeps its polygon)
    pl = (BL.X > PLATE['x0'] - 0.1) & (BL.X < PLATE['x1'] + 0.4) & (abs(BL.Y) < PLATE['hw'] + 0.1) & INS
    R['plate_flatness'] = float(np.nanmax(D[pl]) - np.nanmin(D[pl]))
    R['jack_plane_residual'], R['jack_min_sdf'] = jack_plane()
    gx, gy = np.gradient(D, G, G); slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    from scipy.spatial import cKDTree
    steep = INS & (slope > 3) & (sdf >= P['edge_R'])
    R['fhole_slope_only_clearance'] = float(cKDTree(np.c_[BL.X[steep], BL.Y[steep]]).query(np.c_[BL.X[BL.FH], BL.Y[BL.FH]])[0].min())
    R['fhole_to_outline'] = float(np.min(sdf[BL.FH]))
    wing, ret, bt, bb = chamber_masks()
    R['wing_nominal_max_top_drop'] = float(np.nanmax(D[wing]))
    R['wing_area_nominal'] = float(wing.sum() * G * G); R['wing_area_retreated'] = float(ret.sum() * G * G)
    R['retreated_max_top_drop'] = float(np.nanmax(D[ret]))
    R['fhole_opens_into_retreated_chamber'] = bool(np.any(ret & BL.FH))
    R.update(back_checks())
    R['top_glue_breakthrough_in2'] = float((INS & (D > P['top_half'])).sum() * G * G)
    cw = chamber_wood_3d(); R['chamber_wood_3d'] = {k: cw[k] for k in ('min', 'required', 'ok', 'floor_to_split_min', 'back_skin_vertical_min', 'chamber_area_in2', 'chamber_in3')}
    for k in ('top_skin', 'back_skin', 'rim', 'top_skin_vertical'): R['chamber_wood_3d_' + k] = cw[k]
    R['trem_routes'] = trem_checks(); R['guard_bosses'] = boss_checks(); R['liner_seat'] = liner_checks()      # v3.2
    R['top_concave_R'] = concave_radius(top_drop)
    # ---- v3.1: concavity detector (whole top, and the forearm area alone), onset sections, glue plane at the rim
    R['top_concavity'] = top_concavity()
    R['top_concavity_forearm'] = top_concavity(region=lambda x, y: (arm_s(x, y) > -1.0) & (y > -2.0))
    on = forearm_onset(); R['forearm_onset_sections'] = on
    R['forearm_onset'] = dict(kappa_peak=max(o['kappa_peak'] for o in on), section_kappa_min=min(o['kappa_min'] for o in on),
                              arm_depth=P['_arm_depth'], kappa_design=P['_arm_kappa_peak'], rim_slope_deg=P['_arm_slope_deg'],
                              curvature_ramp=P['_arm_ramp'], constant_curvature_arc_to_rim=round(P['_arm_width_to_rim'] - P['_arm_ramp'], 3))
    # grid maximum of the convex principal curvature over the whole forearm zone (the three sections miss the two places where
    # the forearm joins the perimeter roll), with the same number for the roll alone so the join's own share can be read off
    _zone = lambda x, y: arm_s(x, y) > 0
    _roll = lambda x, y: np.where(_hard(x, y), 0.0, np.maximum(smax(0.0, edge_carve(x, y), P['smax_eps']), 0))
    _g = surface_curvature(top_drop, h=0.0125, band=0.15, region=_zone); _g0 = surface_curvature(_roll, h=0.0125, band=0.15, region=_zone)
    _gt = surface_curvature(top_drop, h=0.0125, band=0.15, region=lambda x, y: (arm_s(x, y) > 0) & (y < 1.2))
    R['forearm_grid_curvature'] = dict(kappa_max=round(1 / _g['min_convex_R'], 4), at=_g['convex_at'], tail_join=round(1 / _gt['min_convex_R'], 4),
                                       tail_join_at=_gt['convex_at'], roll_alone=round(1 / _g0['min_convex_R'], 4), roll_alone_at=_g0['convex_at'],
                                       max_slope_deg=_g['max_slope_deg'], slope_at=_g['slope_at'],
                                       most_concave=(0.0 if not np.isfinite(_g['min_concave_R']) else round(1 / _g['min_concave_R'], 5)))
    _pi = EO + 0.02 * EN; _dr = top_drop(_pi[:, 0], _pi[:, 1]); _lo = _dr > P['top_half']      # 0.02 in inside the smooth outline
    R['top_below_glue_rim_arc'] = dict(arc=float(_lo.sum() * EDS), x=(float(EO[_lo][:, 0].min()), float(EO[_lo][:, 0].max())) if _lo.any() else None,
                                       y=(float(EO[_lo][:, 1].min()), float(EO[_lo][:, 1].max())) if _lo.any() else None,
                                       max_drop=float(_dr.max()), at=tuple(EO[int(np.argmax(_dr))].round(2)))
    R['heel_concave_R_loft'] = heel_concave_radius()
    R['heel_flank_fillet_R'] = (P['flank_r_min'], P['flank_r_max'])
    R['heel_dev_at_fret15'] = heel_dev_at_fret15()
    # ---- v3.1 edge: setback law, creases, radii, wall and glue plane (edge_checks), level margin beside the f-hole on the FINISHED top
    L = edge_law(); R['edge_mode'] = P['edge_mode']
    R['roll_profile'] = dict(side_per_a=ROLL_SIDE, minR_per_a=ROLL_MINR, k3=ROLL_K3)
    R.update(edge_checks()); R['fhole_to_outline'] = float(edge_law()['d_fhole'].min())   # exact polygon-to-curve distance
    wall = L['T_edge'] - ROLL_SIDE * (L['a_top'] + L['a_back'])
    for thr in (3.0, 2.0):
        hf = 0.005; fx = np.arange(19.4, 27.8, hf); fy = np.arange(1.4, 6.9, hf); QX, QY = np.meshgrid(fx, fy, indexing='ij')
        qs = outline_sdf(QX, QY); Z = np.where(qs > 0, top_full(QX, QY), np.nan); g0, g1 = np.gradient(Z, hf, hf)
        st3 = (qs > 0) & ~(np.degrees(np.arctan(np.hypot(g0, g1))) <= thr)      # steep, or right at the rim (nan gradient)
        dq = _segdist(FHOLE_POLY, QX[st3], QY[st3]); i = int(np.argmin(dq))
        R['fhole_level_margin_finished' + ('' if thr == 3.0 else '_2deg')] = dict(margin=float(dq[i]), at=(round(float(QX[st3][i]), 2), round(float(QY[st3][i]), 2)))
    gb = sdf_guard(EO[:, 0], EO[:, 1]); gq = np.c_[GUARD, np.roll(GUARD, -1, 0)]
    gp = np.vstack([np.c_[np.linspace(q[0], q[2], 40), np.linspace(q[1], q[3], 40)] for q in gq]); gd, gs = edge_foot(gp[:, 0], gp[:, 1])
    gc = gd - _at_s(L['a_top'], gs); i = int(np.argmin(gc)); R['guard_clear_of_roll'] = dict(clear=float(gc[i]), at=tuple(gp[i].round(2)))
    st = {}
    for k, v in STATIONS.items():
        i = int(_ETREE.query(v)[1]); rt = edge_section(i, 'top'); rb = edge_section(i, 'back')
        st[k] = dict(at=tuple(EO[i].round(2)), a_top=round(rt[3], 3), minR_top=round(rt[2], 3), a_back=round(rb[3], 3), minR_back=round(rb[2], 3),
                     wall=round(float(wall[i]), 3))
    R['edge_fillet_stations'] = st
    if verbose:
        for k, v in R.items():
            if k == 'forearm_onset_sections':
                for o in v: print('  onset', {a: (round(b, 3) if isinstance(b, float) else b) for a, b in o.items()})
            elif k == 'belly_relief':
                for a, b in v.items(): print('  relief', a, b)
            elif isinstance(v, dict) and k != 'edge_fillet_stations': print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items()})
            elif k == 'edge_fillet_stations':
                for a, b in v.items(): print('  fillet', a, b)
            else: print(k, round(v, 4) if isinstance(v, float) else v)
    return R

if __name__ == '__main__':
    print('derived:', {k: P[k] for k in ('top_half', 'back_half', 'belly_depth_capped', 'heel_depth_below_board', '_arm_slope_deg', '_arm_width_to_rim', '_arm_depth', '_arm_kappa_peak', '_arm_ramp', '_arm_rim_at', '_arm_touch', 'arm_A', 'arm_B')})
    print('evaluate(top_drop, 0.125):'); evaluate(top_drop, P['edge_R'])
    if BL.PLAN_IS_SAMPLE:
        # The constraint checks look for landmarks of my outline (horn tips, pocket mouths, waist) inside fixed windows.
        print('final_carve: synthetic sample plan loaded. The numbers above are not the design. The hard-constraint checks\n'
              'need the real plan file (body/plan.json or SUPERCASTER_PLAN) and are skipped.')
        sys.exit(0)
    checks()
