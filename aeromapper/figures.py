"""Actual experiment figures; these are plots, never claimed as app screenshots."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from .vision import patch,predict
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/images';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'figure.facecolor':'#0c171e','axes.facecolor':'#11232b','axes.edgecolor':'#39515a','text.color':'#d7eae6','axes.labelcolor':'#a5c0c0','xtick.color':'#8aa7ae','ytick.color':'#8aa7ae','grid.color':'#35505a','font.family':'DejaVu Sans','font.size':10,'savefig.facecolor':'#0c171e'})
def generate():
 demo=json.loads((ROOT/'results/demo.json').read_text());rows=list(csv.DictReader((ROOT/'results/missions.csv').open()));fig=plt.figure(figsize=(15,9));gs=fig.add_gridspec(2,3,width_ratios=[1.3,1,1],hspace=.40,wspace=.3)
 ax=fig.add_subplot(gs[:,0],projection='3d');m=demo['adaptive'];x,y=np.meshgrid(np.arange(12)*8,np.arange(12)*8);z=np.array(m['terrain']);ax.plot_surface(x,y,z,cmap='winter',alpha=.65,linewidth=.15,edgecolor='#3d6c74');trace=m['trace'];xx=[t['position'][0]*8 for t in trace];yy=[t['position'][1]*8 for t in trace];zz=[z[t['position'][1],t['position'][0]]+3 for t in trace];ax.plot(xx,yy,zz,color='#b2f5d4',lw=2,label='Adaptive executed path');ax.scatter([t[0]*8 for t in m['targets']],[t[1]*8 for t in m['targets']],[z[t[1],t[0]]+.8 for t in m['targets']],color='#f191a7',s=22,label='Hidden target truth');ax.set(xlabel='East (m)',ylabel='North (m)',zlabel='Elevation (m)',title='3D survey reconstruction\nSynthetic terrain · seed '+str(m['metrics']['seed']));ax.view_init(30,-55);ax.legend(loc='upper left',fontsize=8,facecolor='#11232b',labelcolor='white');ax.set_box_aspect((1,1,.5))
 ax=fig.add_subplot(gs[0,1]);colors={'adaptive':'#9cedcf','lawnmower':'#92a6c4'}
 for p in colors:
  t=demo[p]['trace'];ax.plot([a['time_s'] for a in t],[a['coverage']*100 for a in t],color=colors[p],label=p,lw=2)
 ax.set(xlabel='Mission time (s)',ylabel='Observed cells (%)',title='Coverage is not target recall');ax.grid(alpha=.3);ax.legend(fontsize=8)
 ax=fig.add_subplot(gs[0,2]);groups=[[float(r['recall'])*100 for r in rows if r['policy']==p and r['family']==f] for f in ['test','ood'] for p in ['lawnmower','adaptive']];bp=ax.boxplot(groups,patch_artist=True,tick_labels=['Base\nTest','Adapt\nTest','Base\nOOD','Adapt\nOOD'])
 for patch_,c in zip(bp['boxes'],['#92a6c4','#9cedcf']*2):patch_.set_facecolor(c)
 ax.set(ylabel='Target recall (%)',title='24 paired scenes per family');ax.grid(axis='y',alpha=.25)
 ax=fig.add_subplot(gs[1,1]);bins=[[] for _ in range(10)]
 for i in range(500):
  y=i%2;p=predict(patch(10000+i,y,'test',size=1+i%3,noise=.1,visibility=.65));bins[min(9,int(p*10))].append((p,y))
 calibration=[]
 for b in bins:
  if b:calibration.append({'confidence':sum(v[0] for v in b)/len(b),'frequency':sum(v[1] for v in b)/len(b),'n':len(b)})
 ax.plot([0,1],[0,1],color='#6f8d95',ls='--');ax.plot([b['confidence'] for b in calibration],[b['frequency'] for b in calibration],marker='o',color='#9cedcf');ax.set(xlabel='Predicted probability',ylabel='Observed target fraction',title='Held-out detector calibration',xlim=(0,1),ylim=(0,1));ax.grid(alpha=.25);(ROOT/'results/calibration.json').write_text(json.dumps(calibration,indent=2))
 ax=fig.add_subplot(gs[1,2]);ds=list(csv.DictReader((ROOT/'results/detector.csv').open()))
 for p,c in [('logistic','#9cedcf'),('template','#92a6c4')]:
  points=[(noise,np.mean([float(r['recall']) for r in ds if r['detector']==p and r['family']=='test' and float(r['noise_sigma'])==noise])) for noise in [.05,.15,.25]];ax.plot([v[0] for v in points],[v[1] for v in points],marker='o',color=c,label=p)
 ax.set(xlabel='Pixel noise standard deviation',ylabel='Recall (mean over sizes)',title='Detector versus feature baseline',ylim=(0,1.05));ax.grid(alpha=.25);ax.legend(fontsize=8)
 fig.suptitle('AEROMAPPER AI  /  OBSERVE · INFER · REPLAN',fontsize=20,x=.07,ha='left');fig.text(.07,.025,'Software-only evidence · 96 paired missions · 220 s time budget · 0.85 × budget energy proxy · values measured from saved traces',color='#8aa7ae',fontsize=10);fig.savefig(OUT/'research-overview.png',dpi=155,bbox_inches='tight');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(10,4));writer=PillowWriter(fps=6)
 with writer.saving(fig,str(OUT/'mission-replay.gif'),85):
  maximum=max(len(demo[p]['trace']) for p in colors)
  for i in range(0,maximum,max(1,maximum//36)):
   for ax,p in zip(axes,colors):
    ax.clear();mission=demo[p];t=mission['trace'];f=t[min(i,len(t)-1)];a=np.full((12,12),np.nan)
    for xx,yy,prob in f['belief']:a[int(yy),int(xx)]=prob
    ax.imshow(a,cmap='YlGn',vmin=0,vmax=1,origin='lower');ax.plot([v['position'][0] for v in t[:i+1]],[v['position'][1] for v in t[:i+1]],color=colors[p],lw=1.4);ax.set_title(f"{p} · {f['time_s']:.0f} s · {f['coverage']*100:.0f}% covered");ax.set(xlabel='East cell (8 m)',ylabel='North cell (8 m)')
   fig.tight_layout();writer.grab_frame()
 plt.close(fig)
if __name__=='__main__':generate()
