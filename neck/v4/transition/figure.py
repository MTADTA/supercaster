"""Draw the selected neck sections and the matched body comparison."""
import json
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import study

report = json.loads((HERE/'results.json').read_text())
body = json.loads((HERE.parents[2]/'body/optimize/carve-v2-acoustics/results/prototype_trim.json').read_text())
pick = report['selected']
n = study.n
fig, axes = plt.subplots(3, 1, figsize=(8, 8.6), constrained_layout=True)
wood, steel, blue = '#925333', '#354656', '#217f89'
ax = axes[0]
x = np.linspace(n.FX[11], n.FX[12]+0.10, 1400)
y = n.string_y(x)[0]
z, mask, w = study.surface(x, y, pick['warp'], pick['offset'],pick['bowl'])
land = n.board(x,y)
mm = 25.4
ax.fill_between((x-n.FX[12])*mm,-1.7, (w-land)*mm,color='#e4c6a8')
ax.fill_between((x-n.FX[12])*mm,(w-land)*mm,(z-land)*mm,color=steel)
ax.plot((x-n.FX[12])*mm,(w-land)*mm,color=wood,label='Centred scallop')
ax.plot((x-n.FX[12])*mm,-study.depth(x,y,-0.4,0.30)*mm,'--',color=blue,label='Offset scallop')
ax.set(xlabel='Distance from fret 12 toward the bridge (mm)',ylabel='Height (mm)',ylim=(-1.7,1.35))
ax.legend(loc='upper center',ncols=2,frameon=False)
ax.set_title('Along the high E  ·  scallop, flat seat and steel crown',loc='left')
ax = axes[1]
s = np.linspace(0,0.18,600)
x = np.full_like(s,n.FX[12])
y = -n.width(x)/2+s
z, mask, w = study.surface(x,y,pick['warp'],pick['offset'],pick['bowl'])
datum = n.board(x,-n.width(x)/2)
ax.fill_between(s*mm,-1.2,(w-datum)*mm,color='#e4c6a8',label='Rosewood')
ax.fill_between(s*mm,(w-datum)*mm,(z-datum)*mm,color=steel,label='Stainless')
string_s = n.string_y(x[:1])[0,0]+n.width(x[0])/2
ax.axvline(string_s*mm,color=blue,ls='--',label='High E centre')
ax.set(xlabel='Distance inboard from treble side (mm)',ylabel='Height (mm)',ylim=(-1.2,1.85))
ax.legend(loc='upper left',ncols=3,frameon=False,fontsize=9)
ax.set_title('Across fret 12  ·  graded fret end',loc='left')
ax=axes[2]
for i,(name,label,color) in enumerate([('vintage','V1 Vintage',blue),('hollow','V2 Hollow','#bd7832'),('deep','V3 Deep',steel)]):
    row = next(r for r in body if r['carve']==name and r['target_Hz']==294)
    ax.bar(np.arange(4)+(i-1)*0.23,row['dB_vs_flat_294'],0.22,color=color,label=label)
ax.axhline(0,c='#737373',lw=0.7)
ax.set_xticks(range(4),['80–200','200–300','300–500','500–1000'])
ax.set(ylabel='Δ power (dB)',xlabel='Frequency band (Hz)',ylim=(-1,1))
ax.legend(loc='lower left',ncols=3,frameon=False,fontsize=9)
ax.set_title('Body simulation  ·  radiated power relative to flat at 294 Hz',loc='left')
for ax in axes:
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=0.16)
fig.savefig(HERE/'prototype.png',dpi=160)
