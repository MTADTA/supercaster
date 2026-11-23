"""Compare results/*.json with the reference numbers of the earlier study (reports in body/acoustics/) and write
results/validation.json. Some reference numbers cite reports under final/ (liner-RESULT.md, liner-CHECK.md); those reports
are not in the public tree. Run the cases first (run_case.py for each design named below), or pass --run.

Tolerances (set before the comparison, not tuned): A0 +-2 %, twisting mode +-10 Hz, absolute band levels +-1.5 dB,
design-to-design differences +-1 dB.
"""
import sys, os, json, subprocess
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results')

REF = dict(
    A0={'final_narrowed': (285.8, 'final/liner-RESULT.md (ROM); rigid FV 286.8-288.8 in liner-CHECK.md'),
        'final_plain': (325.7, 'final/liner-RESULT.md'), 'final_bare': (377.1, 'final/liner-RESULT.md'),
        'current': (319.6, 'sim3d-REPORT.md section 2 (320 Hz, ROM 319.6)')},
    bands={'final_narrowed': ([45.7, 56.2, 65.5, 67.3], 'final/liner-RESULT.md nominal'),
           'final_plain': ([45.7, 52.4, 69.5, 67.1], 'final/liner-RESULT.md nominal'),
           'final_bare': ([45.7, 52.1, 62.3, 67.7], 'final/liner-RESULT.md nominal'),
           'current': ([45.9, 53.0, 67.4, 67.8], 'final/liner-RESULT.md nominal (sim3d baseline 45.3/52.7/67.0/68.0)')},
    diffs=[('final_narrowed', 'final_plain', [None, 3.8, None, None], 'final/liner-RESULT.md'),
           ('solid', 'current', [-2.2, -3.6, -8.7, -2.5], 'sim3d-REPORT.md (solid reference vs baseline)')],
    twist={'current': (287.9, 'sim3d-CHECK.md (287.4 free, 287.9 held)'), 'final_narrowed': (287.9, 'liner study: twisting mode 283-288 Hz')},
    mass={'current': (2.938, 'sim3d-REPORT.md section 2')},
    bridge_peak={'current': (1.8e-2, 'sim3d-REPORT.md section 3.3 (659 Hz)')},
    notes_past={'current': (21, 'sim3d-REPORT.md section 3.3 (20.8 in the MC mean)')},
)
TOL = dict(A0=0.02, twist=10.0, band=1.5, diff=1.0)


def load(name):
    fn = os.path.join(RES, name + '.json')
    return json.load(open(fn)) if os.path.exists(fn) else None


def main():
    if '--run' in sys.argv:
        for d in ('final_narrowed', 'final_plain', 'final_bare', 'current', 'solid', 'final_narrowed_locked', 'solid_locked',
                  'final_narrowed_free'):
            subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'run_case.py'), '--design', d, '--quiet'], check=True)
    rows = []
    for d, (ref, src) in REF['A0'].items():
        R = load(d)
        if R and R['A0']:
            v = R['A0']['f_coupled']; ok = abs(v / ref - 1) <= TOL['A0']
            rows.append(dict(item=f'A0 {d}', ref=ref, model=v, err=f'{100 * (v / ref - 1):+.1f} %', ok=ok, src=src,
                             extra=f"rigid {R['A0']['f_rigid']}, Q {R['A0']['Q_coupled']}"))
    for d, (ref, src) in REF['bands'].items():
        R = load(d)
        if R:
            v = R['power_dB_re_1pW_per_N2']
            for b, (r, m) in enumerate(zip(ref, v)):
                rows.append(dict(item=f'band {R["bands_Hz"][b]} {d}', ref=r, model=m, err=f'{m - r:+.1f} dB', ok=abs(m - r) <= TOL['band'], src=src))
    for a, b, ref, src in REF['diffs']:
        Ra, Rb = load(a), load(b)
        if Ra and Rb:
            for k, r in enumerate(ref):
                if r is None: continue
                m = Ra['power_dB_re_1pW_per_N2'][k] - Rb['power_dB_re_1pW_per_N2'][k]
                rows.append(dict(item=f'{a} - {b} band {Ra["bands_Hz"][k]}', ref=r, model=round(m, 2), err=f'{m - r:+.1f} dB',
                                 ok=abs(m - r) <= TOL['diff'], src=src))
    for d, (ref, src) in REF['twist'].items():
        R = load(d)
        if R and R['twist_mode']:
            v = R['twist_mode']['f']
            rows.append(dict(item=f'twisting mode {d}', ref=ref, model=v, err=f'{v - ref:+.1f} Hz', ok=abs(v - ref) <= TOL['twist'], src=src,
                             extra=f"twist index {R['twist_mode']['twist']}, shares {R['twist_mode']['shares']}"))
    for d, (ref, src) in REF['mass'].items():
        R = load(d)
        if R: rows.append(dict(item=f'mass {d}', ref=ref, model=round(R['mass_kg'], 3), err=f'{100 * (R["mass_kg"] / ref - 1):+.1f} %', ok=None, src=src))
    for d, (ref, src) in REF['bridge_peak'].items():
        R = load(d)
        if R:
            v = R['bridge_conductance_mean_6']['peak']
            rows.append(dict(item=f'bridge peak Gz {d}', ref=ref, model=v, err=f'x{v / ref:.2f}', ok=None, src=src,
                             extra=f"at {R['bridge_conductance_mean_6']['peak_Hz']} Hz"))
    for d, (ref, src) in REF['notes_past'].items():
        R = load(d)
        if R: rows.append(dict(item=f'notes past halving {d}', ref=ref, model=R['notes_past_halving'], err='', ok=None, src=src))
    for d in ('final_narrowed_locked', 'solid_locked'):
        R = load(d)
        if R:
            rows.append(dict(item=f'bridge peak Gz {d} (published solid-body max 1.8e-3, as quoted in sim3d-REPORT 3.3, not re-read)',
                             ref=1.8e-3, model=R['bridge_conductance_mean_6']['peak'], err='', ok=None, src='published, via report'))
    R = load('final_narrowed')
    if R:
        rows.append(dict(item='fret conductance peak final_narrowed (published neck up to ~0.1 s/kg, as quoted in sim3d-REPORT 3.3, not re-read)',
                         ref=0.1, model=R['fret_conductance_s_per_kg']['peak'], err='', ok=None, src='published, via report'))
        rows.append(dict(item='sum rule final_narrowed (integral / modal sum)', ref=1.0, model=R['sum_rule']['ratio'], err='',
                         ok=abs(R['sum_rule']['ratio'] - 1) < 0.1, src='internal check'))
    if not rows:
        sys.exit('validate.py: no case results in results/ (they are generated files and are not in the repository). Nothing '
                 'compared, and the stored results/validation.json is left as it is. Run the cases first (run_case.py, or pass '
                 '--run); that needs the real plan file, see the README.')
    graded = [r for r in rows if r['ok'] is not None]
    out = dict(rows=rows, n_pass=sum(r['ok'] for r in graded), n_graded=len(graded), tolerances=TOL)
    json.dump(out, open(os.path.join(RES, 'validation.json'), 'w'), indent=1, default=str)
    for r in rows:
        flag = '' if r['ok'] is None else ('PASS' if r['ok'] else 'FAIL')
        print(f"{flag:4s} {r['item']}: ref {r['ref']} model {r['model']} {r['err']} {r.get('extra', '')}")
    print(f"{out['n_pass']} of {out['n_graded']} graded checks pass")


if __name__ == '__main__':
    main()
