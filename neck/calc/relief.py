"""Neck relief under string tension (Supercaster II). Quick beam estimate, 2026-11-13.
Neck geometry from body/carve/final_carve.py (depth 0.82" at fret 1 incl. 0.20" slab board, scaled with radius;
width 1.65 -> 2.2"; C section, superellipse p=2.3). Clamped where the body starts (fret 16, x~15.7").
Relief = max gap under a straightedge from fret 1 to fret 16 (feeler-gauge style)."""
import numpy as np
S=25.5; fx=lambda n:S*(1-2**(-n/12))
r=lambda x:7.25+2.25*x/25.5
depth=lambda x:0.82*r(x)/r(fx(1)); width=lambda x:1.65+0.55*x/fx(21)
IN=0.0254
# 10.5-48 nickel round core; unit weights lb/in (plain = 0.2226 d^2; wound ~ D'Addario NW interpolated)
g=[('E',.0105,329.63,0.2226*.0105**2),('B',.0135,246.94,0.2226*.0135**2),('G',.017,196.00,0.2226*.017**2),
   ('D',.026,146.83,1.297e-4),('A',.036,110.00,2.404e-4),('E',.048,82.41,4.18e-4)]
def tension(semis, drop6=0):
    T=0
    for i,(n,d,f,uw) in enumerate(g):
        ff=f*2**(semis/12)*(2**(-drop6/12) if i==5 else 1)
        T+=uw*(2*S*ff)**2/386.4
    return T  # lb
def EI(x,E):
    D=depth(x)*IN; w=width(x)*IN; tb=0.20*IN
    y=np.linspace(-(D-tb),tb,400); dy=y[1]-y[0]
    b=np.where(y>=0,w,w*np.clip(1-np.abs(y/(D-tb))**2.3,0,1)**(1/2.3))
    b=b-np.where((y<0)&(y>-0.40*IN),0.25*IN*0.5,0)  # rod channel ~1/4" wide, partly refilled by rod/fillet: count half
    A=(b*dy).sum(); yc=(b*y*dy).sum()/A; I=(b*(y-yc)**2*dy).sum()
    return E*I, yc
def relief(Tlb,E,e_above=0.09):
    T=Tlb*4.448; xs=np.linspace(0,15.7,600); k=[]
    for x in xs:
        ei,yc=EI(x,E); e=(0.20*IN+e_above*IN-yc); k.append(T*e/ei)  # 2026-11-13 fix: y=0 is the GLUE line, the string is e_above over the BOARD TOP (was inside the board)
    k=np.array(k); X=xs*IN
    # clamp at x=15.7: integrate curvature back toward the nut
    th=np.zeros_like(X); v=np.zeros_like(X)
    for i in range(len(X)-2,-1,-1):
        dx=X[i+1]-X[i]; th[i]=th[i+1]-k[i]*dx; v[i]=v[i+1]-th[i]*dx
    a,b_=fx(1)*IN,fx(16)*IN; m=(X>=a)&(X<=b_)
    chord=np.interp(X,[a,b_],[np.interp(a,X,v),np.interp(b_,X,v)])
    return (np.abs(chord-v)[m].max())/IN
for name,s,d in [('E std',0,0),('Eb std',-1,0),('Eb drop C#',-1,2)]:
    T=tension(s,d); print(f"{name:12s} total tension {T:5.1f} lb  relief(E=11/12.5/14 GPa) = "+
        " / ".join(f"{relief(T,E*1e9):.4f}" for E in (11,12.5,14))+' in')
