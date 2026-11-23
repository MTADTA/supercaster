"""Run one design through the coupled vibroacoustic model and write JSON (plus spectra .npz).

  cache/venv/bin/python -I -B run_case.py --design final_narrowed
  cache/venv/bin/python -I -B run_case.py --design final_narrowed --set top_skin_mm=4.5 --set liner_inset_mm=2.9 --tag t45
  cache/venv/bin/python -I -B run_case.py --list

Output: results/<design>[_<tag>].json and .npz. Structural modes are cached in cache/ by structural key, so a change
of air-only or damping-only keys (liner_friction, air_eta, air_mass, wood_eta, pivot_eta, h_air) re-runs in seconds.
"""
import sys, os, json, argparse, time, resource
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import designs


def _clean(o):
    if isinstance(o, dict): return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_clean(v) for v in o]
    if isinstance(o, np.ndarray): return _clean(o.tolist())
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, float) and not np.isfinite(o): return None
    return o


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--design', default='final_narrowed')
    ap.add_argument('--set', action='append', default=[], help='key=value override of a design key (see designs.BASE)')
    ap.add_argument('--tag', default='')
    ap.add_argument('--out', default=None, help='output JSON path (default results/<design>[_tag].json)')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args(argv)
    if a.list:
        for k in designs.DESIGNS: print(k, designs.DESIGNS[k])
        return
    ov = dict(s.split('=', 1) for s in a.set)
    D = designs.get(a.design, ov)
    import rom
    t0 = time.time()
    R = rom.run(D, verbose=not a.quiet)
    spec = R.pop('_spectra')
    R['peak_rss_GB'] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9, 2)
    R['overrides'] = ov
    name = a.design + (('_' + a.tag) if a.tag else '')
    out = a.out or os.path.join(HERE, 'results', name + '.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(_clean(R), open(out, 'w'), indent=1)
    np.savez_compressed(out[:-5] + '.npz', **spec)
    p = R['power_dB_re_1pW_per_N2']
    a0 = R['A0']['f_coupled'] if R['A0'] else None
    tm = R['twist_mode']['f'] if R['twist_mode'] else None
    print(f'{name}: bands {p} dB, A0 {a0} Hz, twist {tm} Hz, mass {R["mass_kg"]:.3f} kg, notes past halving '
          f'{R["notes_past_halving"]}, {time.time() - t0:.0f}s -> {out}', flush=True)
    return R


if __name__ == '__main__':
    main()
