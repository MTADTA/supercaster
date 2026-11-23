"""Material data. Reads body/acoustics/inputs/wood-properties.json if present (keys matched loosely), else the defaults
below. Every default is tagged in SOURCES."""
import os, json
import numpy as np
import fe

WOOD_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'acoustics', 'inputs', 'wood-properties.json')

# Elastic constants as E_L and ratios (Wood Handbook ch. 5 style). Units SI.
DEFAULTS = dict(
    alder=dict(rho=420.0, EL=9.5e9, ER_EL=0.07, ET_EL=0.07, GLR_EL=0.075, GLT_EL=0.069, GRT_EL=0.011,
               nLR=0.37, nLT=0.45, nRT=0.70, eta=0.010),
    maple=dict(rho=700.0, EL=12.6e9, ER_EL=0.132, ET_EL=0.065, GLR_EL=0.111, GLT_EL=0.063, GRT_EL=0.020,
               nLR=0.42, nLT=0.48, nRT=0.77, eta=0.008),
    rosewood=dict(rho=830.0, EL=11.5e9, eta=0.010),
    guard=dict(rho=1350.0, E=2.5e9, nu=0.38, eta=0.05, t_mm=2.3),
    steel=dict(rho=7850.0, E=200e9),
)
SOURCES = dict(
    alder='[literature: Wood Handbook FPL-GTR-190 Table 5-3a, red alder E_L 9.5 GPa, SG 0.41] density 420 kg/m3 for roasted '
          'stock [judged]; E_R = E_T = 0.07 E_L as in the reference study [judged]; shear and Poisson ratios: hardwood '
          'analogues, Wood Handbook Table 5-1 [literature]; loss factor 0.010 [judged]',
    maple='[literature: Wood Handbook Table 5-3a sugar maple E_L 12.6 GPa; Table 5-1 ratios] density 700 kg/m3 [judged]',
    rosewood='E_L 11.5 GPa, 830 kg/m3 [judged]',
    guard='3-ply PVC/celluloid 2.3 mm, E 2.5 GPa, 1350 kg/m3, loss 0.05 [judged]',
)


SOURCE = 'reference'      # 'reference' = the values above (as in the reference study); 'json' = wood-properties.json


CURLY = False             # json only: neck maple from hard_maple_roasted_curly_neck


def use(source, curly=False):
    """Select the material set for the following builds ('reference' or 'json')."""
    global SOURCE, CURLY
    if source not in ('reference', 'json'): raise ValueError(source)
    SOURCE = source; CURLY = bool(curly)


def load(source=None):
    source = source or SOURCE
    M = json.loads(json.dumps(DEFAULTS))
    src = dict(SOURCES)
    used_json = False
    if source == 'json':
        if not os.path.exists(WOOD_JSON):
            raise FileNotFoundError(WOOD_JSON)
        J = json.load(open(WOOD_JSON))
        used_json = _from_json(M, J, src)
    M['_sources'] = src; M['_json'] = used_json; M['_source'] = source
    return M


def _from_json(M, J, src):
    """Full orthotropic sets from wood-properties.json (roasted alder body, roasted hard maple neck and tenon, rosewood
    board, unroasted 0.6 mm maple veneer). Loss factor per wood: eta_L [judged: bending along the grain dominates]."""
    mats = J['materials']
    def v(e, k): return float(e[k]['value'])
    pick = dict(alder='red_alder_roasted', maple='hard_maple_roasted_curly_neck' if CURLY else 'hard_maple_roasted',
                veneer='hard_maple_veneer_0p6mm')
    for wood, key in pick.items():
        e = mats[key]; EL = v(e, 'E_L')
        base = M['maple'] if wood == 'veneer' else M[wood]
        d = dict(base)
        d.update(rho=v(e, 'density'), EL=EL, ER_EL=v(e, 'E_R') / EL, ET_EL=v(e, 'E_T') / EL,
                 GLR_EL=v(e, 'G_LR') / EL, GLT_EL=v(e, 'G_LT') / EL, nLR=v(e, 'nu_LR'), nLT=v(e, 'nu_LT'), eta=v(e, 'eta_L'))
        if 'G_RT' in e: d['GRT_EL'] = v(e, 'G_RT') / EL
        if 'nu_RT' in e: d['nRT'] = v(e, 'nu_RT')
        M[wood] = d; src[wood] = f'[literature/computed: wood-properties.json materials.{key}, values as tagged there]'
    r = mats['east_indian_rosewood']; M['rosewood'] = dict(rho=v(r, 'density'), EL=v(r, 'E_L'), eta=v(r, 'eta_L'))
    src['rosewood'] = '[wood-properties.json materials.east_indian_rosewood]'
    return True


def _num(v):
    if isinstance(v, (int, float)): return float(v)
    if isinstance(v, dict):
        for k in ('nominal', 'value', 'mean', 'mid'):
            if k in v and isinstance(v[k], (int, float)): return float(v[k])
    return None


def _merge(M, J, src):
    """Pick up density, E_L and loss for alder and maple from a loosely structured JSON."""
    used = False
    flat = {}
    def walk(d, pre=''):
        if isinstance(d, dict):
            for k, v in d.items():
                if _num(v) is not None and not isinstance(v, (list,)):
                    flat[(pre + '.' + k).lower()] = _num(v)
                if isinstance(v, dict): walk(v, pre + '.' + k)
    walk(J)
    for wood in ('alder', 'maple'):
        for key, names, scale in (('rho', ('density', 'rho'), 1.0), ('EL', ('e_l', 'el', 'modulus_l', 'moe'), None),
                                  ('eta', ('loss', 'eta', 'damping'), 1.0)):
            for fk, v in flat.items():
                if wood in fk and 'roast' in fk and any(n in fk.split('.')[-1] for n in names):
                    val = v
                    if key == 'EL' and val < 1e3: val *= 1e9        # GPa given
                    if key == 'rho' and val < 5: val *= 1000        # g/cm3 given
                    M[wood][key] = val; src[wood + '_' + key] = f'wood-properties.json {fk}'; used = True
                    break
    return used


def D_matrix(mat, axes='LTR', scaleE=1.0, scale_cross=1.0):
    m = mat
    EL = m['EL'] * scaleE
    return fe.wood_D(EL, EL * m['ER_EL'] * scale_cross, EL * m['ET_EL'] * scale_cross, EL * m['GLR_EL'], EL * m['GLT_EL'],
                     EL * m['GRT_EL'], m['nLR'], m['nLT'], m['nRT'], axes=axes)
