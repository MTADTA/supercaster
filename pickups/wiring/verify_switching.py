"""Enumerate every control state on the lug-level netlist and check it.

5 positions x series (off/on) x phase (normal/flip) x piezo (off/blend/solo)
= 60 states. For each one, solve the circuit with each source switched on in
turn (superposition) and read each coil's signed share of the output.

Topology run: every coil 1 kohm, piezo 10 kohm (resistive stand-in), 1M pot at
full, output open (1 Gohm). Then a two-coil parallel pair reads 0.5/0.5, a
series pair 1/1, and a reversed coil reads negative.

Hum: each coil's leads are named so that its string signal is + at its '+'
lead. Its hum EMF then has the sign of its magnet polarity m (coil B is the
humbucker partner, m_B = -m_A). Quiet = hum shares cancel.
"""
import sys
import wiring_model as wm
from wiring_model import circuit

POS_NAME = {1: "Bridge HB (A+B)", 2: "Bridge A + Middle", 3: "Neck + bridge coil (Tele)",
            4: "Neck + Middle", 5: "Neck"}
EXPECT = {1: {"A", "B"}, 2: {"A", "M"}, 4: {"N", "M"}, 5: {"N"}}
def expect(pos, flip):
    if pos != 3:
        return EXPECT[pos]
    coil = {"A": "A", "B": "B", "auto": "A" if flip else "B"}[wm.VARIANT]
    return {coil, "N"}
POLARITY = {  # magnet polarity per pickup; B is always -A
    "classic (N and M are a normal RWRP pair; A opposite M)": {"N": 1, "M": -1, "A": 1},
    "tele-first (A opposite both N and M)": {"N": -1, "M": -1, "A": 1},
}

def load(R):
    return [("Z", R("OUT"), R("GND"), 1e9)]

def shares(state):
    cz = {k: 1000.0 for k in "NMAB"}
    return {s: circuit(state, cz, 10e3, 1e6, load, s).real for s in "NMABP"}

def describe(state, c):
    pos, series, flip, pz = state
    act = {k: v for k, v in c.items() if k in "NMAB" and abs(v) > 1e-6}
    return act

def run():
    errors, rows = [], []
    for pos in range(1, 6):
        for series in (False, True):
            for flip in (False, True):
                for pz in ("off", "blend", "solo"):
                    st = (pos, series, flip, pz)
                    c = shares(st)
                    act = describe(st, c)
                    tag = f"pos{pos} series={int(series)} flip={int(flip)} piezo={pz}"
                    # ---- checks
                    if pz == "solo":
                        if act: errors.append(f"{tag}: magnetics leak in solo {act}")
                        if not 0.9 < c["P"] < 1.01: errors.append(f"{tag}: piezo share {c['P']:.3f}")
                    else:
                        want = expect(pos, flip)
                        if set(act) != want:
                            errors.append(f"{tag}: coils {sorted(act)} != {sorted(want)}")
                        pair = pos in (2, 3, 4)
                        mag = sorted(abs(v) for v in act.values())
                        if pos == 1 and not all(abs(m - 1) < 1e-3 for m in mag):
                            errors.append(f"{tag}: HB not full series {act}")
                        if pair:
                            target = 1.0 if series else 0.5
                            if not all(abs(m - target) < 1e-3 for m in mag):
                                errors.append(f"{tag}: pair shares {act}, want {target}")
                        for k, v in act.items():
                            neg = (k == "N" and flip)
                            if (v < 0) != neg:
                                errors.append(f"{tag}: coil {k} sign {v:+.3f}")
                        if pz == "off" and abs(c["P"]) > 1e-6:
                            errors.append(f"{tag}: piezo leaks when off ({c['P']:.4f})")
                        if pz == "blend" and not 0.9 < c["P"] < 1.01:
                            errors.append(f"{tag}: piezo share in blend {c['P']:.3f}")
                    rows.append((st, c, act))

    print("STATE TABLE (shares of each source at the output; open-circuit, equal 1k coils)\n")
    print(f"{'pos':<3} {'ser':<3} {'phs':<3} {'piezo':<5}  {'N':>6} {'M':>6} {'A':>6} {'B':>6} {'Pz':>6}")
    for (pos, s, f, pz), c, act in rows:
        print(f"{pos:<3} {int(s):<3} {int(f):<3} {pz:<5}  " +
              " ".join(f"{c[k]:6.3f}" for k in "NMABP"))

    pols = POLARITY.items() if wm.VARIANT == "A" else list(POLARITY.items())[:1]
    for label, m in pols:
        mm = dict(m, B=-m["A"])
        print(f"\nHUM with magnet polarity: {label}")
        print("  (string = summed signal share, hum = summed hum share; 1.0 = one single coil)")
        for pos in range(1, 6):
            for series in (False, True):
                for flip in (False, True):
                    if pos in (1, 5) and (series or flip): continue
                    if pos == 2 and flip: continue   # phase flips the neck only
                    c = shares((pos, series, flip, "off"))
                    string = sum(c[k] for k in "NMAB")
                    hum = sum(c[k] * mm[k] for k in "NMAB")
                    oop = any(v < -1e-6 for v in c.values())
                    word = "QUIET" if abs(hum) < 1e-6 else "hums like a single coil"
                    print(f"  {pos} {POS_NAME[pos]:<24} {('alone   ' if pos in (1, 5) else 'series  ' if series else 'parallel')} "
                          f"{'out-of-phase' if oop else 'in-phase    '}  hum {hum:+.2f}  -> {word}")

    print("\nCHECKS:", "all 60 states pass" if not errors else f"{len(errors)} FAIL")
    for e in errors: print("  ", e)
    return errors

VARIANT_NAME = {"auto": "auto (4PDT PHASE: position 3 = neck + coil B, flipped = neck + coil A)",
                "A": "A (position 3 always neck + coil A)", "B": "B (position 3 always neck + coil B)"}

def main():
    bad = 0
    for v in ("auto", "A", "B"):
        wm.VARIANT = v
        print("#" * 78 + f"\nVARIANT {VARIANT_NAME[v]}\n" + "#" * 78)
        bad += len(run())
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
