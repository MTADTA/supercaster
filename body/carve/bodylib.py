"""Shared Supercaster body geometry + carve metrics. Coordinates: inches, x from nut along neck, y across (bass +).
Top face plane z=0 (flat-top reference); a carve is drop(x,y) >= 0 measured DOWN from that plane.
Usage: from bodylib import *  (Python 3.11 with numpy and scipy)."""
import math, json, os, sys, numpy as np
# PUBLIC TREE: the plan data (body outline, pickguard, jack recess, screw, hardware and landmark positions, tremolo
# routes) is NOT in this repository, because it was traced or measured from third-party plans of a commercial guitar.
# It is read from a JSON file instead:
#   SUPERCASTER_PLAN=<path>   your own plan file, or
#   body/plan.json            (not tracked), or
#   body/plan.sample.json     SYNTHETIC SAMPLE DATA made by tools/make_sample_plan.py. It is not the design and
#                             every number computed from it is meaningless; it only shows the file format.
_HERE=os.path.dirname(os.path.abspath(__file__))
_BODY=os.path.dirname(_HERE)
PLAN_PATH=os.environ.get('SUPERCASTER_PLAN') or os.path.join(_BODY,'plan.json')
if not os.path.exists(PLAN_PATH):
    PLAN_PATH=os.path.join(_BODY,'plan.sample.json')
    print('bodylib: no body/plan.json; using SYNTHETIC SAMPLE DATA (body/plan.sample.json). Results are not the design.',file=sys.stderr)
_plan=json.load(open(PLAN_PATH))
PLAN_IS_SAMPLE=bool(_plan.get('sample'))
OUTLINE=np.array(_plan['OUTLINE'],float); GUARD=np.array(_plan['GUARD'],float); JACK=np.array(_plan['JACK'],float)
SCREWS=[tuple(map(float,q)) for q in _plan['SCREWS']]
THICK=1.75
FHOLE_B1=tuple(_plan['FHOLE_B1']); FHOLE_B2=tuple(_plan['FHOLE_B2'])
NECK_PU=float(_plan['NECK_PU']); MID_PU=float(_plan['MID_PU']); BRIDGE_PU=tuple(_plan['BRIDGE_PU'])
PLATE=dict(_plan['PLATE'])
KNOBS=[tuple(q) for q in _plan['KNOBS']]
ARM_LINE=tuple(tuple(q) for q in _plan['ARM_LINE'])
# Landmarks on (or tuned to) the outline, and the tremolo routes. Both come from the plan file, never from this code.
#   LANDMARKS: jack_center, horn_c, belly_guide (first vertex, last vertex), tail_x, horn_button, waist,
#              control_cavity (polyline, optional), jack_channel_end (optional)
#   TREM:      pivot_x, pivot_pitch, and the slot / block / spring route boxes (x0, x1, hw, yc, r, z_top, z_bot)
LANDMARKS={k:(tuple(tuple(p) for p in v) if isinstance(v,list) and v and isinstance(v[0],list) else tuple(v) if isinstance(v,list) else float(v))
           for k,v in _plan['LANDMARKS'].items()}
TREM={k:(dict(v) if isinstance(v,dict) else float(v)) for k,v in _plan['TREM'].items()}
#   STATIONS:  named points on or near the outline where final_carve reports the edge roll
STATIONS={k:tuple(v) for k,v in _plan['STATIONS'].items()}
BODY_EDGE_AT_NECK=16.0   # approx where the neck meets the body
def _inside(P,x,y):
    x=np.asarray(x,float);y=np.asarray(y,float);c=np.zeros(x.shape,bool);n=len(P)
    for i in range(n):
        xi,yi=P[i];xj,yj=P[i-1]
        cond=((yi>y)!=(yj>y))&(x<(xj-xi)*(y-yi)/((yj-yi)+1e-300)+xi);c^=cond
    return c
def _segdist(P,x,y):
    x=np.asarray(x,float);y=np.asarray(y,float);d=np.full(x.shape,np.inf)
    for i in range(len(P)):
        ax,ay=P[i-1];bx,by=P[i];dx,dy=bx-ax,by-ay
        t=np.clip(((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy),0,1)
        d=np.minimum(d,np.hypot(x-ax-t*dx,y-ay-t*dy))
    return d
def sdf_outline(x,y):
    """signed distance to body outline, + inside (inches)"""
    d=_segdist(OUTLINE,x,y);return np.where(_inside(OUTLINE,x,y),d,-d)
def in_guard(x,y): return _inside(GUARD,x,y)
def sdf_guard(x,y):
    d=_segdist(GUARD,x,y);return np.where(_inside(GUARD,x,y),d,-d)
# --- first-pass forearm contour (placed by eye) ---
_l=math.hypot(ARM_LINE[1][0]-ARM_LINE[0][0],ARM_LINE[1][1]-ARM_LINE[0][1])
_nx=-(ARM_LINE[1][1]-ARM_LINE[0][1])/_l;_ny=(ARM_LINE[1][0]-ARM_LINE[0][0])/_l
def arm_s(x,y): return (np.asarray(x)-ARM_LINE[0][0])*_nx+(np.asarray(y)-ARM_LINE[0][1])*_ny
def arm_drop_repo(x,y): return 0.55*np.clip(arm_s(x,y)/3.6,0,1)**1.5
# --- f-hole loop, first version (two end points and a parametric loop) ---
def fhole_mask_v0(x,y):
    ax,ay=FHOLE_B1;bx,by=FHOLE_B2;L=math.hypot(bx-ax,by-ay);ux,uy=(bx-ax)/L,(by-ay)/L
    x=np.asarray(x,float);y=np.asarray(y,float)
    u=(x-ax)*ux+(y-ay)*uy; v=-(x-ax)*uy+(y-ay)*ux
    hook=lambda t:np.exp(-((t/0.09)**2))
    M=32;ts=np.linspace(0,1,M+1);cx=ts*L;cy=-0.045*L*np.sin(np.pi*ts)-0.26*hook(ts)+0.26*hook(1-ts)
    hw=lambda t:0.15+0.1*np.sin(np.pi*t)**0.7
    d=np.minimum(np.hypot(u+0.06,v+0.3)-0.37,np.hypot(u-L-0.06,v-0.3)-0.35)
    for k in range(M):
        x0,y0,x1,y1=cx[k],cy[k],cx[k+1],cy[k+1];dx,dy=x1-x0,y1-y0
        t=np.clip(((u-x0)*dx+(v-y0)*dy)/(dx*dx+dy*dy),0,1)
        d=np.minimum(d,np.hypot(u-x0-t*dx,v-y0-t*dy)-hw((k+t)/M))
    return d<0
# --- f-hole v2: traced from my photo of my own guitar (fhole_trace.json) ---
import json as _json, os as _os
FHOLE_POLY=np.array(_json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'fhole_trace.json')))['poly'])
FHOLE_SHIFT=float(_os.environ.get('SC_FHOLE_SHIFT',0))   # option: inches inboard along (0.179,-0.984); 0 = the trace exactly
FHOLE_POLY=FHOLE_POLY+FHOLE_SHIFT*np.array([0.179,-0.984])
def fhole_mask(x,y): return _inside(FHOLE_POLY,x,y)
# --- evaluation grid ---
G=0.04
gx=np.arange(13.0,31.4,G); gy=np.arange(-6.6,6.6,G)
X,Y=np.meshgrid(gx,gy,indexing='ij')
INSIDE=_inside(OUTLINE,X,Y); SDF=None
def _sdf():
    global SDF
    if SDF is None: SDF=sdf_outline(X,Y)
    return SDF
FH=fhole_mask(X,Y)
def evaluate(drop_fn, edge_radius=0.125, slope_thresh_deg=3.0, verbose=True):
    """drop_fn(x,y)->drop in inches (>=0), applied to the top surface, excluding the edge roundover itself.
    Returns dict of metrics."""
    D=np.where(INSIDE,drop_fn(X,Y),np.nan)
    gxD,gyD=np.gradient(D,G,G); slope=np.degrees(np.arctan(np.hypot(gxD,gyD)))
    sdf=_sdf()
    # flat-required zones: pickguard footprint (+0.05in), trem plate area, jack recess
    guard=sdf_guard(X,Y)>-0.05
    plate=(X>PLATE['x0']-0.1)&(X<PLATE['x1']+0.4)&(abs(Y)<PLATE['hw']+0.1)
    guard_dev=np.nanmax(np.where(guard&INSIDE,D,np.nan))-np.nanmin(np.where(guard&INSIDE,D,np.nan))
    guard_slope=np.nanmax(np.where(guard&INSIDE&(sdf>0.3),slope,np.nan))
    # f-hole margin: distance from f-hole edge to nearest point with slope>thresh or within edge roll band
    steep=(INSIDE&(slope>slope_thresh_deg))|(INSIDE&(sdf<edge_radius))
    fpts=np.argwhere(FH); spts=np.argwhere(steep & (np.hypot(X-22.8,Y-3.9)<4.5))
    if len(spts):
        fp=np.c_[gx[fpts[:,0]],gy[fpts[:,1]]];sp=np.c_[gx[spts[:,0]],gy[spts[:,1]]]
        md=min(np.min(np.hypot(sp[:,0]-a,sp[:,1]-b)) for a,b in fp[::3])
    else: md=np.inf
    fh_slope=np.nanmax(np.where(FH,slope,np.nan))
    # curvature smoothness: max |second difference| jump (G2 proxy) away from f-hole and edge
    dxx=np.gradient(gxD,G,axis=0);dyy=np.gradient(gyD,G,axis=1)
    k=dxx+dyy; jk=np.abs(np.diff(k,axis=0))/G
    zone=(sdf[:-1]>0.15)&INSIDE[:-1]
    g2=np.nanpercentile(np.where(zone,jk,np.nan),99.5)
    res=dict(max_drop=float(np.nanmax(D)),max_slope_deg=float(np.nanmax(np.where(sdf>edge_radius,slope,np.nan))),
             fhole_margin_in=float(md),slope_at_fhole_deg=float(fh_slope),
             guard_flatness_in=float(guard_dev),guard_max_slope_deg=float(guard_slope),
             curvature_jump_p995=float(g2))
    if verbose: print({k:round(v,3) for k,v in res.items()})
    return res
if __name__=='__main__':
    print('baseline: repo forearm contour only, 0.3 edge'); evaluate(arm_drop_repo,0.3)
    print('repo contour, 1/8 edge'); evaluate(arm_drop_repo,0.125)
