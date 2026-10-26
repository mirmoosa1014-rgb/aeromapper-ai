"""Seeded synthetic patches and a transparent trained logistic detector."""
import math,random,json
from pathlib import Path
SIZE=12
MODEL=Path(__file__).resolve().parents[1]/'models/detector.json'
def patch(seed,target,family='train',size=2,noise=.08,visibility=1.):
 r=random.Random(seed);base={'train':.30,'validation':.36,'test':.42,'ood':.53}[family]
 a=[[max(0,min(1,base+r.gauss(0,noise)+.06*math.sin(x*.8+y))) for x in range(SIZE)] for y in range(SIZE)]
 cx,cy=r.randrange(4,8),r.randrange(4,8)
 for y in range(SIZE):
  for x in range(SIZE):
   if target and abs(x-cx)<=size and abs(y-cy)<=size:a[y][x]=min(1,a[y][x]+.52*visibility)
   elif not target and r.random()<.30 and (x==cx or y==cy):a[y][x]=min(1,a[y][x]+.35*visibility)
   if x<3:a[y][x]*=.75
 return a
def features(a):
 flat=[v for row in a for v in row];mean=sum(flat)/len(flat);core=[a[y][x] for y in range(3,9) for x in range(3,9)]
 return [1.,sum(core)/len(core)-mean,sum((v-mean)**2 for v in flat),sum(v>mean+.22 for v in flat)/144,max(sum(a[y][x] for y in range(j,j+3) for x in range(i,i+3))/9 for j in range(10) for i in range(10))-mean]
def sigmoid(x):return 1/(1+math.exp(-max(-30,min(30,x))))
def predict(a,model=None):
 if model is None:
  try:
   model=json.loads(MODEL.read_text())
   if len(model['weights'])!=5 or not all(math.isfinite(w) for w in model['weights']) or not math.isfinite(model.get('temperature',1)) or model.get('temperature',1)<=0:raise ValueError('Invalid model schema')
  except (OSError,ValueError,TypeError,KeyError):return template(a)
 f=features(a)
 return sigmoid(sum(w*x for w,x in zip(model['weights'],f))/model.get('temperature',1.))
def template(a):
 f=features(a);return min(1,max(0,(f[4]-.08)*3))
def train():
 data=[]
 for i in range(1600):
  y=i%2;a=patch(i,y,size=1+i%3,noise=.05+(i%5)*.025,visibility=.5+(i%4)*.16);data.append((features(a),y))
 w=[0.]*5
 for epoch in range(350):
  grad=[0.]*5
  for f,y in data:
   e=sigmoid(sum(a*b for a,b in zip(w,f)))-y
   for j in range(5):grad[j]+=e*f[j]
  w=[a-.6*(b/len(data)+.0001*a) for a,b in zip(w,grad)]
 model={'weights':w,'feature_schema':['bias','central_contrast','variance','bright_fraction','max_3x3_contrast'],'train_family':'train','train_seeds':[0,1599],'threshold':.5,'format_version':1}
 val=[(features(patch(3000+i,i%2,'validation',size=1+i%3,noise=.1,visibility=.65)),i%2) for i in range(200)]
 def loss(t):
  total=0.
  for f,y in val:
   p=sigmoid(sum(a*b for a,b in zip(w,f))/t);total-=y*math.log(max(p,1e-9))+(1-y)*math.log(max(1-p,1e-9))
  return total/len(val)
 model['temperature']=min([.5,.75,1.,1.5,2.],key=loss);model['validation_family']='validation';model['validation_seeds']=[3000,3199]
 MODEL.parent.mkdir(exist_ok=True);MODEL.write_text(json.dumps(model,indent=2));return model
