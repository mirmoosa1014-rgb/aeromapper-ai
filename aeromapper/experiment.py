"""Reproducible bounded experiments and evidence from saved measurements."""
import argparse,csv,json,statistics
from pathlib import Path
from .vision import train,patch,predict,template
from .simulation import run
ROOT=Path(__file__).resolve().parents[1]
def experiment(quick=False):
 model=train();out=ROOT/'results';out.mkdir(exist_ok=True);rows=[]
 for family in ['test','ood']:
  for seed in range(2000,2000+(4 if quick else 24)):
   for policy in ['lawnmower','adaptive']:rows.append(run(seed,policy,220,family)['metrics'])
 with (out/'missions.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 detection=[]
 for family in ['test','ood']:
  for size in [1,2,3]:
   for noise in [.05,.15,.25]:
    for detector in ['logistic','template']:
     tp=fp=fn=0;errors=[]
     for i in range(100):
      y=i%2;a=patch(10000+i,y,family,size,noise,.65);p=predict(a,model) if detector=='logistic' else template(a)
      tp+=int(p>=.5 and y==1);fp+=int(p>=.5 and y==0);fn+=int(p<.5 and y==1);errors.append((p-y)**2)
     detection.append({'family':family,'size_pixels':size*2+1,'noise_sigma':noise,'detector':detector,'precision':tp/max(1,tp+fp),'recall':tp/max(1,tp+fn),'brier':statistics.mean(errors)})
 with (out/'detector.csv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(detection[0]));writer.writeheader();writer.writerows(detection)
 summary={}
 for family in ['test','ood']:
  summary[family]={}
  for policy in ['lawnmower','adaptive']:
   subset=[r for r in rows if r['family']==family and r['policy']==policy]
   summary[family][policy]={key:{'mean':statistics.mean(r[key] for r in subset),'sd':statistics.stdev(r[key] for r in subset)} for key in ['coverage','recall','precision','path_m','energy_proxy','runtime_ms']}
 (out/'summary.json').write_text(json.dumps(summary,indent=2));paired=[]
 for seed in range(2000,2000+(4 if quick else 24)):
  a=next(r for r in rows if r['seed']==seed and r['family']=='test' and r['policy']=='adaptive');b=next(r for r in rows if r['seed']==seed and r['family']=='test' and r['policy']=='lawnmower');paired.append((a['recall']-b['recall'],seed))
 counter=min(paired);demo={p:run(counter[1],p,220,'test') for p in ['lawnmower','adaptive']}
 (out/'demo.json').write_text(json.dumps(demo,separators=(',',':')));public=ROOT/'frontend/public';public.mkdir(exist_ok=True);(public/'demo.json').write_text(json.dumps(demo,separators=(',',':')))
 report={'mode':'quick' if quick else 'full bounded','missions':len(rows),'train_seeds':[0,1599],'validation_seeds':[3000,3199],'test_scene_seeds':[2000,2003 if quick else 2023],'detector_test_seeds':[10000,10099],'counterexample_seed':counter[1],'adaptive_minus_baseline_recall':counter[0],'summary':summary}
 (out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--quick',action='store_true');experiment(p.parse_args().quick)
