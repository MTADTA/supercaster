#!/usr/bin/env python3
"""Supercaster II fret ends: shaded close views of the edge, built from the same surfaces the numbers use.

Wood is one mesh (board top, roll, side, start of the back). Each fret is its own closed-topped mesh sitting on
the wood, so anything floating or cutting through would show.

Run:  python -I -B fe_render.py            -> fig/render_*.png
      python -I -B fe_render.py test       -> one panel, for checking
"""
import math
import os
import sys

import numpy as np
import pyvista as pv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fe_model as fm  # noqa: E402

n4 = fm.n4
FIG = os.path.join(HERE, 'fig')
os.makedirs(FIG, exist_ok=True)
pv.OFF_SCREEN = True
HF, CW, FX = fm.HF, fm.CW, fm.FX
ROSE = np.array([0.33, 0.185, 0.125])
MAPLE = np.array([0.74, 0.55, 0.33])
STEEL = (0.80, 0.81, 0.83)


def _noise(a, b, seed):
    r = np.random.default_rng(seed)
    out = np.zeros_like(a)
    for f, amp in ((38.0, 0.5), (95.0, 0.3), (230.0, 0.2)):
        ph = r.uniform(0, 6.28, 3)
        out += amp * np.sin(f * b + ph[0] + 1.3 * np.sin(1.9 * a + ph[1]) + 0.6 * np.sin(5.3 * a + ph[2]))
    return out


def _sg(X, Y, Z):
    return pv.StructuredGrid(X, Y, Z)


def wood_mesh(c, side, x0, x1, dx=0.0025):
    x0, x1 = max(x0, 0.0), min(x1, float(n4.X_BOARD_END))
    x = np.arange(x0, x1 + dx / 2, dx)
    W = n4.width(x)
    s_in = float(W.min()) - 0.03                      # the top runs right across to just short of the far edge
    s_top = np.concatenate([np.arange(0, 0.14, 0.0005), np.arange(0.14, 0.30, 0.003), np.linspace(0.30, s_in, 260)])
    X, Sg = np.meshgrid(x, s_top, indexing='ij')
    _, _, wood = fm.surface(X, Sg, side, c)
    sign = -1.0 if side == 'T' else 1.0
    Y = sign * (W[:, None] / 2 - Sg)
    z_sh = n4.shoulder(x)
    f = np.linspace(0, 1, 40)[1:]
    wall_z = wood[:, :1] + (z_sh[:, None] - wood[:, :1]) * f[None, :]
    wall_y = sign * (W[:, None] / 2) + 0 * wall_z
    u = 1 - np.linspace(0, 1, 90)[1:] ** 2 * 0.40
    back_z = n4.back(x[:, None], (sign * u)[None, :])
    back_y = sign * u[None, :] * W[:, None] / 2
    Yall = np.concatenate([Y[:, ::-1], wall_y, back_y], axis=1)
    Zall = np.concatenate([wood[:, ::-1], wall_z, back_z], axis=1)
    Xall = x[:, None] + 0 * Yall
    grid = _sg(Xall, Yall, Zall)
    glue_edge = n4.glue(x, W / 2)[:, None]
    ntop = Y.shape[1]
    is_top = np.zeros(Yall.shape, bool)
    is_top[:, :ntop] = True
    rw = is_top | (Zall > glue_edge)
    across = np.where(is_top, Yall, Zall + 3.0)
    g = _noise(Xall, across, 7)
    col = np.where(rw[..., None], ROSE[None, None, :] * (1 + 0.13 * g[..., None]), MAPLE[None, None, :] * (1 + 0.05 * g[..., None]))
    line = (~is_top) & (np.abs(Zall - glue_edge) < 0.003)
    col = np.clip(np.where(line[..., None], col * 0.7, col), 0, 1)
    grid.point_data['rgb'] = np.stack([col[..., k].ravel(order='F') for k in range(3)], 1)
    return grid.extract_surface(algorithm='dataset_surface')


def fret_mesh(c, side, n):
    """One fret from the far side out to its end, as a surface that sits on (and dips just into) the wood."""
    xf = float(FX[n])
    s_in = float(n4.width(xf)) - 0.035
    th = np.linspace(0, np.pi, 61)
    if c['kind'] == 'dome':
        t0, a = c['t0'][side], c['a'][side]
        sc = t0 + a
        s_body = np.linspace(s_in, sc, int((s_in - sc) / 0.004))
        psi = np.linspace(0, np.pi / 2, 46)
        rows = []
        for s in s_body:
            rows.append((CW * np.cos(th), np.full_like(th, s), HF * np.sin(th)))
        for p in psi[1:]:
            rows.append((CW * np.cos(th) * math.cos(p), np.full_like(th, sc - a * math.sin(p)), HF * np.sin(th) * math.cos(p)))
        XI = np.array([r[0] for r in rows])
        S = np.array([r[1] for r in rows])
        Hh = np.array([r[2] for r in rows])
    else:
        xi = CW * np.cos(th)
        s = np.concatenate([np.arange(0, 0.11, 0.0004), np.linspace(0.11, s_in, int(s_in / 0.004))])
        XI, S = np.meshgrid(xi, s, indexing='ij')
        z, steel, wood = fm.surface(xf + XI, S, side, c)
        land = n4.board(xf + XI, fm.side_y(xf + XI, S, side))
        Hh = np.where(steel, z - land, wood - land - 0.004)
    X = xf + XI
    Y = fm.side_y(X, S, side)
    Z = n4.board(X, Y) + Hh - 0.0006 * (Hh <= 1e-9)
    return _sg(X, Y, Z).extract_surface(algorithm='dataset_surface').compute_normals(auto_orient_normals=False, split_vertices=False)


def camera(side, view, xm, span):
    """Camera position, focal point, view-up and half-height of the frame for a view of the edge centred at xm."""
    W = float(n4.width(xm))
    sign = -1.0 if side == 'T' else 1.0
    ye = sign * W / 2
    zc = float(fm.corner_z(xm))
    d = 6.0
    if view == 'above':
        foc = np.array([xm, ye - sign * 0.19 * span, zc])
        return foc + np.array([0, 0, d]), foc, (0, sign, 0), span * 0.30
    if view == 'side':
        el = math.radians(14)
        foc = np.array([xm, ye, zc - 0.035 * span])
        return foc + d * np.array([0.0, sign * math.cos(el), math.sin(el)]), foc, (0, 0, 1), span * 0.30
    # the player's eye. Bass edge: the near edge, seen from outboard and above, looking toward the body.
    # Treble edge: the far edge, seen across the board from above the bass side.
    foc = np.array([xm, ye - sign * 0.05 * span, zc])
    if side == 'B':
        el, az = math.radians(46), math.radians(-24)
        v = np.array([math.sin(az) * math.cos(el), sign * math.cos(az) * math.cos(el), math.sin(el)])
    else:
        el, az = math.radians(50), math.radians(-24)
        v = np.array([math.sin(az) * math.cos(el), -sign * math.cos(az) * math.cos(el), math.sin(el)])
    return foc + d * v, foc, (0, 0, 1), span * 0.30


def render(c, side, n_lo, n_hi, view, size=(1500, 900), pad=0.16, zoom=1.0, centre=None, span=None):
    if centre is None:
        x0, x1 = float(FX[n_lo]) - pad, float(FX[n_hi]) + pad
        xm, span = (x0 + x1) / 2, (x1 - x0)
    else:
        xm = centre
    pl = pv.Plotter(off_screen=True, window_size=size, lighting='none')
    pl.set_background('#ecebe7')
    pl.add_mesh(wood_mesh(c, side, xm - span * 1.6 - 0.4, xm + span * 1.6 + 0.4), scalars='rgb', rgb=True, smooth_shading=True,
                specular=0.22, specular_power=22, ambient=0.26, diffuse=0.86)
    for n in range(1, fm.NF + 1):
        if xm - span * 1.6 - 0.3 < FX[n] < xm + span * 1.6 + 0.3:
            pl.add_mesh(fret_mesh(c, side, n), color=STEEL, smooth_shading=True, specular=0.9, specular_power=50,
                        ambient=0.24, diffuse=0.60)
    pos, foc, up, half = camera(side, view, xm, span)
    pl.camera.position, pl.camera.focal_point, pl.camera.up = tuple(pos), tuple(foc), up
    pl.camera.parallel_projection = True
    pl.camera.parallel_scale = half / zoom
    pl.camera.clipping_range = (3.5, 9.5)
    sign = -1.0 if side == 'T' else 1.0
    for dvec, inten in (((-0.55, sign * 0.55, 0.62), 1.0), ((0.7, -sign * 0.25, 0.66), 0.40), ((0.25, sign * 0.9, 0.12), 0.25)):
        lt = pv.Light(position=tuple(np.array(foc) + 8 * np.array(dvec)), focal_point=tuple(foc), intensity=inten, light_type='scene light')
        lt.positional = False
        pl.add_light(lt)
    try:
        # a wide radius and a generous bias: a tighter setting draws false contour lines on these shallow surfaces
        pl.enable_ssao(radius=0.10, bias=0.004, kernel_size=128, blur=True)
        pl.enable_anti_aliasing('ssaa')
    except Exception:
        pass
    img = pl.screenshot(return_img=True)
    pl.close()
    return img


DESIGNS = [('vintage', 'Vintage: square edge, 35 degree bevel'), ('v4', 'v4: flat 72 degree face'),
           ('rec', 'Proposed: quarter-sphere on a wrapped nose')]
VIEWN = [('eye', "player's eye"), ('side', 'from the side'), ('above', 'from above')]


def _font(sz):
    from PIL import ImageFont
    for f in ('/System/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/Supplemental/Arial.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def sheet(side, n_lo, n_hi, fname, title, zoom=1.0, centre=None, span=None, views=VIEWN, size=(1200, 720)):
    from PIL import Image, ImageDraw
    w, h = size
    top, lab = 110, 54
    im = Image.new('RGB', (w * len(views) + 20 * (len(views) + 1), top + (h + lab) * len(DESIGNS) + 20), 'white')
    dr = ImageDraw.Draw(im)
    dr.text((24, 22), title, fill='black', font=_font(40))
    for r, (k, kn) in enumerate(DESIGNS):
        for q, (v, vn) in enumerate(views):
            img = render(fm.CANDS[k], side, n_lo, n_hi, v, size=size, zoom=zoom, centre=centre, span=span)
            x, y = 20 + q * (w + 20), top + r * (h + lab)
            dr.text((x + 4, y + 8), '%s  |  %s' % (kn, vn), fill=(40, 40, 40), font=_font(28))
            im.paste(Image.fromarray(img), (x, y + lab))
    im.save(os.path.join(FIG, fname))
    return fname


if __name__ == '__main__':
    from PIL import Image
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        sheet('T', 12, 13, '_test_sheet.png', 'test: treble edge, frets 12 and 13')
        print('ok')
        sys.exit()
    only = [a for a in sys.argv[1:] if a in ('T', 'B')]            # optional: render one edge at a time
    for side, sn in (('T', 'treble'), ('B', 'bass')):
        if only and side not in only:
            continue
        for lo, hi in ((1, 2), (12, 13)):
            print(sheet(side, lo, hi, 'render_%s_frets_%d-%d.png' % (sn, lo, hi),
                        '%s edge, frets %d and %d. Top row a vintage edge, middle v4, bottom the proposal.' % (sn.capitalize(), lo, hi)))
        for n in (1, 12):
            print(sheet(side, n, n, 'render_%s_fret_%d_macro.png' % (sn, n),
                        '%s edge at fret %d, one fret end close up (frame about 0.45 in wide)' % (sn.capitalize(), n),
                        centre=float(FX[n]), span=0.45))
