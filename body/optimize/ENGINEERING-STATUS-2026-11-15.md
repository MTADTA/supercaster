# Supercaster II: integrated engineering disposition

2026-11-15. Status: optimized prototype direction, **not a released CNC design**.
This review covers the newest continuous-dome variants in `body/carve/arch-v2`,
neck v4, and the existing construction/acoustic studies. It does not promote an
unvalidated simulation into a build guarantee or overwrite the owner's carve.

## Selected prototype direction

Use V1 “Vintage” as the conservative continuous-dome candidate, with a 6.0 mm
finished bare alder chamber roof, the narrow frame fillet and integral f-hole
end lips specified in `OPTIMIZE.md`. Keep the bridge and trem pivots on the solid
centre. Keep the current neck v4 and heel concept. This is an engineering
recommendation, not a claim that V1 is the unique acoustic optimum.

Do not pursue a thinner roof simply because it is domed. The cached V1 shell
study supports only a small stress reduction. Do not substitute spruce, cedar,
or the proposed sandwich based on low density alone: strength sizing and the
different grain orientation change the required thickness and stiffness.

Keep the f-hole liner acoustically compliant rather than a continuous structural
rib. Kerfs alone do not prove negligible stiffness: retain an airtight throat,
test the actual lined roof, and include its measured stiffness and mass before
making a loudness claim. Redraw the hidden throat with buildable rounded openings;
uniformly insetting the visible f-hole can pinch its narrow arms shut.

Use 294 Hz as the **initial prototype trim target**, following `OPTIMIZE.md`,
with its provisional ±4 Hz tolerance at a recorded temperature. The 290 Hz used
by comparison scripts is a controlled comparison frequency, not a second build
specification. Check the assembled instrument in both intended tunings; no fixed
port frequency guarantees freedom from amplified feedback or neck-mode coupling.
Start with a reversible port insert and trim upward on the dry-clamped body.
Recheck after glue, finish, hardware and strings; do not finalize the insert from
an isolated rigid-cavity calculation.

Keep the serviceable steel trem block and three-spring baseline. Do not undercut
the pivot supports or add the hidden driven soundboard: `driven-top/DRIVEN-TOP.md`
already found unfavorable sustain, feedback, durability and repair tradeoffs.
Test guard seating with the real guard before changing geometry around an assumed
contact stiffness.

## Repairs made in this review

The latest material study's weak/strong-board sensitivity was inverted. For a
fixed target utilization U, allowable stress is **U × strength**, not inversely
proportional to strength. `carve-v2-acoustics/strength_sizing.py` now interpolates
the stored stress/thickness samples with explicit SI/MPa conversion and refuses
to return a thickness outside the sampled range. `size_roofs.py` uses it for new
runs. `results/sizing.json` was reprocessed without changing any FE sample.

The sandwich search previously returned the maximum tested core thickness as
“sized” despite missing the target. Results now include achieved utilization,
target utilization, a pass flag, and an interpolated feasible thickness (null
when unbracketed). The historical `sizing.log` predates this correction and must
not be used for strength sensitivity or feasibility.

Three analytic regression tests cover the bending-law inverse, strength
direction, out-of-range rejection, and nonmonotone input rejection. The cached
sample preservation and ordering checks also passed. A full FE rerun is not
needed to correct this postprocessing error; these repairs do not validate the
underlying FE model or material assumptions.

## Construction requirements before cutting

1. **Unify the CAD baseline.** `final_carve.py` still defaults to a 0.197 in roof
   and a 0.6 mm veneer liner configuration. The dome study installs a 6 mm roof
   in memory. Use an explicit selected build configuration; do not machine the
   historical base file or the visual site mesh by its name.
2. **Fit the actual neck and joint.** Import neck v4's section/taper, 22-fret end,
   relief datum and spoke-wheel access into the body joint. Specify fit allowance
   for the chosen adhesive and process and check alignment at the saddles.
   The old pocket and the v4 neck are not a verified matched pair.
3. **Measure the trem hardware.** Resolve the reported uncovered top slot against
   the actual plate, block and full travel envelope. Confirm pivot engagement,
   spring/claw travel, cavity floors and wood at every route. The carve's route
   plans alone do not establish those floor thicknesses.
4. **Fit the liner to the curved underside.** The inherited planar-seat check
   fails on the dome. A conforming, segmented seat and a floor-clearance check
   are required; copying a liner depth from arch A is not sufficient.
5. **Budget machining and sanding.** Roof thickness is a finished minimum. Stock
   allowance must cover the shop's measured tooling and sanding error. Preserve
   end lips and the narrow fillet, and verify minimum walls on the combined
   route/neck/liner geometry, not on separate visual meshes.
6. **Qualify the wood and glue-up.** Use stock from the intended batch for roof
   coupons and joint trials. The nominal alder comparison is not a lower-bound
   strength design. Inspect grain runout/defects and test the thin roof, hole ends,
   lining and finish under the intended humidity range. Resolve and seal the
   exposed forearm glue seam as part of the finish schedule.

Wood properties vary even in clear stock, and moisture affects mechanical
behavior; species averages are not measured properties of this blank. Primary
reference: [USDA Wood Handbook, mechanical properties](https://research.fs.usda.gov/treesearch/62244)
and [moisture relations](https://research.fs.usda.gov/treesearch/62243).

## Acoustic evidence and release limits

The prior studies already explore arch depth, roof thickness, liner stiffness,
neck/rod options, guard contact, trem masses and springs, and hidden drive paths.
Those establish useful hypotheses and tradeoffs. They do not establish a globally
optimal guitar. `sim/CHECK-2026-11-12.md` records unresolved neck mass/joint,
prestress, damping and free-body issues. The new study also uses the legacy neck
and trem model, not a fully reconciled neck-v4 instrument.

The shell sizing calculation includes the f-hole end lips; the whole-body acoustic
model does not establish the same detailed lip/liner construction. Do not combine
their outputs into a claim that one exact build has passed both tests. Reported
sub-decibel distinctions cannot select a winner reliably; the project's 1 dB
rule is a heuristic, not a measured uncertainty bound.

The radiation calculation also reuses `sim/cache/bem_body_v1.npz` through
`surface.radiation_cache()`. It does not regenerate an exterior radiation mesh
for each dome. Treat the new runs as structural/air comparisons using a shared
radiation approximation, not fully independent acoustic validation of each
exterior. Roasting factors transferred from alder to spruce in `cv2_lib.py` are
assumptions, not measurements of roasted spruce.

Before production release, measure the dry-clamped and assembled air resonance,
roof mobility, mass/balance, trem return, note decay and amplified feedback with
the intended hardware and player contact. Compare repeatable plucks/taps and
microphone positions against a solid-body reference. Use those measurements to
update damping, neck/joint and guard parameters, then rerun only decisions whose
ranking changes. The reusable tap procedure is in
`body/acoustics/inputs/tap-test-procedure.md`.

## New simulation results

The fresh flat control and all three continuous-dome alder variants completed.
See [the study report](carve-v2-acoustics/CARVE-V2-ACOUSTICS.md) and
[reproducible comparison data](carve-v2-acoustics/results/comparison.json).
Every dome-to-flat band change is under 1 dB; this is insufficient evidence to
choose a carve for loudness. V1 is the conservative construction candidate,
not a demonstrated acoustic winner.
