"""Compare longitudinal scallop ramps on the R2 graded rail. All distances in inches."""
import json
from pathlib import Path
import sys

import numpy as np
from scipy.ndimage import grey_dilation, grey_erosion

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'fret-ends'))
import fe_r2_model as edge

n = edge.n4
end = edge.FINAL['C_graded']
cells = np.arange(1, n.NF + 1)


def transverse(x,y):
    width = n.width(x)
    s = width/2 - abs(y)
    r = edge.par(end, 'r', x, 'T')
    v = np.clip((s-r)/(edge.S_RAIL1-r), 0, 1)
    rail = np.where(v < edge.RAIL_A, v*v/edge.RAIL_A, 1-(1-v)**2/(1-edge.RAIL_A))
    tilt = 1-n.P['tilt']*(y/width+0.5)
    return tilt*rail


def depth(x, y, warp, offset, calibrate=True, symmetric=False, bowl=0.1):
    """Depth below the local board cone. The R2 roll and steel sit on this surface."""
    k = n.cell_of(x)
    xa, xb, length, _, _, _ = n.cell_geometry(k)
    floor = xb - np.minimum(length / 2, offset)
    land = n.P['land']
    u = np.clip(np.where(x < floor, (x-xa-land)/(floor-xa-land),
                         (xb-x-land)/(xb-floor-land)), 0, 1)
    g = n.S5(u + warp*u*(1-u))
    amplitude = transverse(x,y)
    if symmetric:
        mid = (xa+xb)/2
        run = np.minimum(x-xa, xb-x) - land
        def ramp(span):
            u = np.clip(run/span,0,1)
            return n.S5(u + warp*u*(1-u))
        # A shallow central bowl joins two mirrored shoulders, including in the long low cells.
        g = (1-bowl)*ramp(np.minimum(length/2,offset)-land) + bowl*ramp(length/2-land)
        # Evaluate the transverse depth on each string line at the cell midpoint.
        # Outside the string fan, ease back to the physical edge roll.
        half_spread = lambda pos: (n.P['nut_spread']+(n.P['bridge_spread']-n.P['nut_spread'])*pos/n.S)/2
        mid_y = y * half_spread(mid)/half_spread(x)
        r = edge.par(end, 'r', x, 'T')
        blend = n.S5((n.width(x)/2-abs(y)-r)/(n.width(x)/2-half_spread(x)-r))
        amplitude += blend*(transverse(mid,mid_y)-amplitude)
    # Anchor the first-cell owner's dimension on the string, taper correction to zero by fret 12.
    x1 = n.FX[1]/2 if symmetric else n.FX[1]-offset
    y1 = n.string_y(np.array([x1]))[0, 0]
    first_factor = 1-n.P['tilt']*(y1/n.width(x1)+0.5)
    correction = 1 + (1/first_factor-1)*np.clip((12-k)/11, 0, 1) if calibrate else 1
    return n.DK[k]*correction*amplitude*g


def surface(x, y, warp, offset, bowl=0.1):
    """Finished surface, steel mask and pre-fretting wood, on the board footprint."""
    s = n.width(x)/2 - abs(y)
    # The chosen graded end is symmetric in the local edge frame.
    baseline, steel, wood = edge.surface(x, s, 'T', end)
    ys = edge.fm.side_y(x, s, 'T')
    # Recover the unscalloped rail and nose from the treble-side reference.
    wood = wood + depth(x, ys, 0, 0.33, False) - depth(x, y, warp, offset, symmetric=True, bowl=bowl)
    return np.where(steel, baseline, wood), steel, wood


def cutter_check(pick, step=0.004):
    """Vertical ball-end envelope over the treble rail and hollow, before fretting."""
    radius = 0.0625
    x, y = np.meshgrid(np.arange(-0.15, n.X22+0.16, step),
                       np.arange(-1.34, -0.32, step), indexing='ij')
    s = n.width(x)/2+y
    _, _, wood = surface(x, y, pick['warp'], pick['offset'], pick['bowl'])
    # Free space outside the outline allows the tool centre to overhang the edge.
    wood = np.where(s >= 0, wood, -1)
    a = np.arange(-int(radius/step), int(radius/step)+1)*step
    d2 = a[:, None]**2+a**2
    mask = d2 <= radius**2
    ball = np.sqrt(np.maximum(0, radius**2-d2))
    centers = grey_dilation(wood, footprint=mask, structure=ball)
    cut = grey_erosion(centers, footprint=mask, structure=ball)
    roi = (x >= 0) & (x <= n.X22) & (s >= edge.par(end, 'r', x, 'T')) & (s <= 0.32)
    residual = np.where(roi, cut-wood, -1)
    i = np.unravel_index(np.argmax(residual), residual.shape)
    return dict(step_in=step, tool_radius_in=radius, residual_in=float(residual[i]),
                x_in=float(x[i]), in_from_side=float(s[i]))


def sample(warp, offset, dx, radii, calibrate=True, symmetric=False, bowl=0.1):
    # Extra flat board beyond the last wire allows the rolling pad to finish its crossing.
    x = np.arange(-0.5, n.X22+0.51, dx)
    y = n.string_y(x)[0]
    cut = depth(x, y, warp, offset, calibrate, symmetric, bowl)
    xf, idx = n.nearest_fret(x)
    rel = (x-xf)/n.CW
    z = np.where((idx > 0) & (abs(rel) <= 1), n.HF*np.sqrt(np.maximum(0, 1-rel**2)), -cut)
    climbs = []
    by_fret = []
    directions = []
    for r in radii:
        offsets = np.arange(-int(r/dx), int(r/dx)+1)*dx
        path = grey_dilation(z, structure=np.sqrt(np.maximum(0, r*r-offsets**2)), mode='nearest')
        sl = np.gradient(path, dx)
        if r == 0.30:
            middle = (n.FX[:-1]+n.FX[1:])/2
            for left, right in zip(middle, np.r_[middle[1:], n.X22+0.22]):
                region = sl[(x>=left) & (x<right)]
                directions.append(np.degrees(np.arctan([max(region),-min(region)])).tolist())
                by_fret.append(float(np.degrees(np.arctan(abs(sl[(x>=left) & (x<right)]).max()))))
        climbs.append(float(np.degrees(np.arctan(abs(sl[(x>0.5) & (x<n.X22+0.22)]).max()))))
    xa, xb, length, *_ = n.cell_geometry(cells)
    probe = xb - np.minimum(0.25, length/2)
    floor = (xa+xb)/2 if symmetric else xb-np.minimum(offset,length/2)
    return dict(warp=warp, offset=offset, symmetric=symmetric, bowl=bowl, direction_bridge_nut_deg=directions, climbs_deg=climbs, climbs_by_fret_deg=by_fret,
                probe_in=depth(probe, n.string_y(probe)[0], warp, offset, calibrate, symmetric, bowl).tolist(),
                floor_high_E_in=depth(floor, n.string_y(floor)[0], warp, offset, calibrate, symmetric, bowl).tolist())


def run():
    radii = [0.20, 0.30, 0.40]
    control = sample(-0.4, 0.30, 0.0005, radii)
    trials = [sample(-0.4, 0.30, 0.0005, radii, symmetric=True, bowl=b)
              for b in (0, 0.1, 0.25, 0.5, 1)]
    def clearance(row):
        return float(np.min(np.array(row['probe_in'])/control['probe_in']))
    # Keep the roundest centered bowl retaining 90% of the previous near-fret clearance.
    pick = max((r for r in trials if clearance(r)>=0.90), key=lambda row: row['bowl'])
    check = sample(pick['warp'],pick['offset'],0.00025,radii,symmetric=True,bowl=pick['bowl'])
    assert max(abs(np.array(check['climbs_deg'])-pick['climbs_deg'])) < 0.25
    assert abs(pick['floor_high_E_in'][0]-0.030) < 1e-8
    xa, xb, length, *_ = n.cell_geometry(cells)
    floor = (xa+xb)/2
    for fraction in np.linspace(0.01,0.49,41):
        left, right = xa+fraction*length, xb-fraction*length
        for yl,yr in zip(n.string_y(left),n.string_y(right)):
            args = dict(warp=pick['warp'],offset=pick['offset'],symmetric=True,bowl=pick['bowl'])
            assert np.allclose(depth(left,yl,**args),depth(right,yr,**args),atol=1e-12,rtol=0)
    ends = [edge.numbers(end, 'T', int(k)) for k in cells]
    e = n.width(xb)/2+ n.string_y(xb)[0]
    margins = [float(v-row['full_from_side']) for v, row in zip(e, ends)]
    assert min(margins) > 0
    for x in (xa+n.P['land']/2, xb-n.P['land']/2):
        assert np.all(depth(x, n.string_y(x)[0], pick['warp'], pick['offset'], symmetric=True,bowl=pick['bowl']) == 0)
    x = np.linspace(0, n.X22, 2000)
    y = n.string_y(x)[0]
    s = n.width(x)/2+y
    assert np.allclose(depth(x,y,0,0.33,False), edge.scallop(x,y,s,'rail',edge.par(end,'r',x,'T')))
    result = dict(radii_in=radii, control=control, trials=trials, selected=pick,
                  fine_grid_deg=check['climbs_deg'], min_clearance_fraction=clearance(pick),
                  floor_from_nut_in=floor.tolist(), full_height_margin_in=margins, end_geometry=ends, treble_cutter=cutter_check(pick))
    (HERE/'results.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result


if __name__ == '__main__':
    run()
