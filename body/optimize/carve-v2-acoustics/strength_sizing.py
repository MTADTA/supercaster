"""Strength sensitivity from cached FE samples; no extrapolated build dimensions."""
import math


def thickness_for_strength(samples, target_utilization, strength_pa):
    """Solve stress(t) / strength = target; return None outside sampled bounds.

    Samples store stress in MPa and thickness in mm. Strength is in Pa.
    Interpolate log stress versus log thickness, requiring decreasing stress.
    """
    points = sorted({float(r['t']): float(r['worst_MPa']) for r in samples}.items())
    if len(points) < 2 or target_utilization <= 0 or strength_pa <= 0:
        raise ValueError('Need positive strength, target and at least two samples')
    if any(t <= 0 or s <= 0 for t, s in points):
        raise ValueError('Samples must be positive')
    if any(b[1] >= a[1] for a, b in zip(points, points[1:])):
        raise ValueError('Stress must decrease with thickness')
    allowable_mpa = target_utilization * strength_pa / 1e6
    if not points[-1][1] <= allowable_mpa <= points[0][1]:
        return None
    for (ta, sa), (tb, sb) in zip(points, points[1:]):
        if sb <= allowable_mpa <= sa:
            fraction = math.log(allowable_mpa / sa) / math.log(sb / sa)
            return ta * (tb / ta) ** fraction


def annotate(result):
    """Refresh derived sensitivity and feasibility only; preserve FE samples."""
    for material, shapes in result['materials'].items():
        for shape, case in shapes.items():
            baseline = result['alder'][shape]
            target = baseline['worst_MPa'] * 1e6 / baseline['sperp']
            strength = case['sperp_MPa'] * 1e6
            key = ('core_mm_if_strength_at_range_ends' if material == 'sandwich'
                   else 't_if_strength_at_range_ends_mm')
            bounds = case.get('sperp_rng_MPa', [strength / 1e6] * 2)
            case[key] = {name: thickness_for_strength(case['samples'], target, s * 1e6)
                         for name, s in zip(('weak_board', 'strong_board'), bounds)}
            case['target_utilization'] = target
            case['achieved_utilization'] = case['sized']['worst_MPa'] * 1e6 / strength
            case['meets_equal_strength_within_1pct'] = case['achieved_utilization'] <= target * 1.01
            case['nominal_interpolated_mm'] = thickness_for_strength(case['samples'], target, strength)
    result['sensitivity_note'] = ('Corrected 2026-11-15: stress allowance scales with strength. '
        'Null means target outside sampled thickness bounds, not a passing boundary design. '
        'Equal strength to nominal alder is not a manufacturing safety approval.')
    return result
