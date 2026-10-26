"""Bounded survey simulator. Static no-fly cells known; targets stay sensor-private."""
import math,random,time
from collections import deque
from .vision import patch,predict
N=12;CELL=8.;MAX_SPEED=8.;MAX_ACCEL=2.;ALT=12.;FOV=60.
def footprint(altitude=ALT):return 2*altitude*math.tan(math.radians(FOV/2))
def world(seed,family='test'):
 r=random.Random(seed);targets=set(r.sample([(x,y) for y in range(N) for x in range(N) if (x,y)!=(0,0)],14));obstacles=set(r.sample([(x,y) for y in range(N) for x in range(N) if (x,y) not in targets and (x,y)!=(0,0)],13 if family!='ood' else 22));height=[[2+(1.3 if family!='ood' else 2.2)*math.sin(x*.45)+.8*math.cos(y*.5)+(1.5*math.sin((x+y)*.7) if family=='ood' else 0) for x in range(N)] for y in range(N)]
 return {'seed':seed,'family':family,'targets':targets,'obstacles':obstacles,'height':height}
def cells_visible(pos,altitude=ALT):
 radius=footprint(altitude)/2
 return [(x,y) for y in range(N) for x in range(N) if abs((x-pos[0])*CELL)<=radius and abs((y-pos[1])*CELL)<=radius]
def route(a,b,obstacles):
 q=deque([a]);previous={a:None}
 while q:
  c=q.popleft()
  if c==b:
   path=[]
   while c!=a:path.append(c);c=previous[c]
   return list(reversed(path))
  for n in [(c[0]+1,c[1]),(c[0]-1,c[1]),(c[0],c[1]+1),(c[0],c[1]-1)]:
   if 0<=n[0]<N and 0<=n[1]<N and n not in obstacles and n not in previous:previous[n]=c;q.append(n)
 return None
def choose(policy,pos,seen,belief,blocked,step):
 order=[(x,y) for y in range(N) for x in (range(N) if y%2==0 else reversed(range(N)))];candidates=[p for p in order if p not in seen and p not in blocked]
 if policy=='lawnmower':return (candidates[0] if candidates else None),'Next unobserved serpentine cell'
 best=None;score_best=-1e9
 for p in candidates:
  unknown=sum(c not in seen for c in cells_visible(p));uncertainty=sum(1-abs(2*belief.get(c,.5)-1) for c in cells_visible(p) if c in seen);score=unknown+.15*uncertainty-.085*math.dist(pos,p)*CELL
  if score>score_best:best,score_best=p,score
 return best,'Expected unseen footprint / travel cost; no hidden target input'
def segment(a,b):return route(a,b,set())
def leg_cost(path):
 duration=len(path)*2*math.sqrt(CELL/MAX_ACCEL)
 return duration,.7*duration+len(path)*CELL*.06
def run(seed=2000,policy='adaptive',budget=220.,family='test'):
 if policy not in ['adaptive','lawnmower']:raise ValueError('Unknown policy')
 if not 40<=budget<=600:raise ValueError('Budget must be 40–600 seconds')
 start=time.perf_counter();w=world(seed,family);pos=(0,0);seen=set();blocked=set(w['obstacles']);belief={};trace=[];elapsed=energy=length=0.;unsafe=0;last_frame=[]
 def observe():
  nonlocal last_frame
  obs=[]
  for c in cells_visible(pos):
   seen.add(c)
   if c in w['obstacles']:continue
   visibility=.35 if c[0]>7 and c[1]>5 else .9;frame=patch(seed*10000+c[1]*N+c[0],c in w['targets'],family,size=1+(c[0]+c[1])%3,noise=.1 if family!='ood' else .19,visibility=visibility);p=predict(frame);belief[c]=p;obs.append({'x':c[0],'y':c[1],'confidence':p});last_frame=frame
  return obs
 def record(rationale,observations,heading=0):trace.append({'step':len(trace),'time_s':elapsed,'energy_proxy':energy,'position':list(pos),'heading_rad':heading,'coverage':len(seen)/(N*N),'belief':[[x,y,p] for (x,y),p in belief.items()],'observations':observations,'rationale':rationale,'camera':last_frame})
 record('Initial camera observation',observe())
 for step in range(200):
  target,rationale=choose(policy,pos,seen,belief,blocked,step)
  if target is None:break
  path=route(pos,target,w['obstacles'])
  if path is None:blocked.add(target);unsafe+=1;continue
  home=route(target,(0,0),w['obstacles']);duration,cost=leg_cost(path);reserve,reserve_energy=leg_cost(home)
  if elapsed+duration+reserve>budget or energy+cost+reserve_energy>budget*.85:break
  for waypoint in path:
   heading=math.atan2(waypoint[1]-pos[1],waypoint[0]-pos[0]);elapsed+=leg_cost([waypoint])[0];energy+=leg_cost([waypoint])[1];length+=CELL;pos=waypoint;record(rationale,observe(),heading)
 home=route(pos,(0,0),w['obstacles'])
 for waypoint in home:
  heading=math.atan2(waypoint[1]-pos[1],waypoint[0]-pos[0]);elapsed+=leg_cost([waypoint])[0];energy+=leg_cost([waypoint])[1];length+=CELL;pos=waypoint;record('Return to base on obstacle-free reserved route',observe(),heading)
 detected={c for c,p in belief.items() if p>=.5};tp=len(detected&w['targets']);fp=len(detected-w['targets']);metrics={'policy':policy,'seed':seed,'family':family,'coverage':len(seen)/(N*N),'recall':tp/len(w['targets']),'precision':tp/max(1,len(detected)),'false_discoveries':fp,'path_m':length,'time_s':elapsed,'energy_proxy':energy,'blocked_proposals':unsafe,'runtime_ms':(time.perf_counter()-start)*1000,'targets':len(w['targets']),'detected':tp,'budget_s':budget,'returned_to_base':pos==(0,0)}
 return {'metrics':metrics,'trace':trace,'terrain':w['height'],'obstacles':[list(c) for c in sorted(w['obstacles'])],'targets':[list(c) for c in sorted(w['targets'])],'footprint_m':footprint(),'cell_m':CELL,'model':'trained logistic image-feature detector','synthetic':True}
