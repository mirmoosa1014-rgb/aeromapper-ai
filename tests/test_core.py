import json,unittest
from pathlib import Path
from aeromapper.vision import patch,predict,features
from aeromapper.simulation import footprint,cells_visible,choose,route,run,world
class Invariants(unittest.TestCase):
 def test_footprint(self):
  self.assertAlmostEqual(footprint(12),13.856406460551018);self.assertEqual(cells_visible((5,5)),[(5,5)])
 def test_route(self):
  blocked={(1,0),(1,1)};path=route((0,0),(2,0),blocked);previous=(0,0)
  for p in path:self.assertNotIn(p,blocked);self.assertEqual(abs(p[0]-previous[0])+abs(p[1]-previous[1]),1);previous=p
  self.assertEqual(path[-1],(2,0))
 def test_pose_mapping(self):self.assertEqual(cells_visible((0,0)),[(0,0)])
 def test_observation(self):self.assertEqual(patch(12,True),patch(12,True))
 def test_detector(self):self.assertTrue(0<=predict(patch(23,True))<=1);self.assertEqual(len(features(patch(1,False))),5)
 def test_hidden_state_isolation(self):
  import inspect
  signature=str(inspect.signature(choose));self.assertNotIn('target',signature);self.assertNotIn('world',signature)
 def test_replay_battery_collisions_and_return(self):
  for family in ['test','ood']:
   for policy in ['adaptive','lawnmower']:
    a=run(2000,policy,220,family);b=run(2000,policy,220,family)
    self.assertEqual(a['trace'],b['trace']);self.assertEqual(a['trace'][-1]['position'],[0,0]);self.assertLessEqual(a['metrics']['time_s'],220+1e-8);self.assertLessEqual(a['metrics']['energy_proxy'],220*.85+1e-8)
    obstacle={tuple(c) for c in a['obstacles']};self.assertTrue(all(tuple(t['position']) not in obstacle for t in a['trace']));self.assertTrue(all(v['time_s']<w['time_s'] for v,w in zip(a['trace'],a['trace'][1:])))
 def test_same_conditions(self):
  a=run(2001,'adaptive');b=run(2001,'lawnmower');self.assertEqual(a['terrain'],b['terrain']);self.assertEqual(a['targets'],b['targets']);self.assertEqual(a['obstacles'],b['obstacles']);self.assertEqual(a['trace'][0],b['trace'][0])
 def test_split_family(self):
  model=json.loads(Path('models/detector.json').read_text());self.assertEqual(model['train_family'],'train');self.assertNotEqual(patch(12,True,'train'),patch(12,True,'test'));self.assertNotEqual(world(2,'test')['height'],world(2,'ood')['height'])
 def test_missing_model_fallback(self):
  from unittest.mock import patch as mock
  from aeromapper.vision import template
  image=patch(11,True)
  with mock('aeromapper.vision.MODEL',Path('/missing/aeromapper-model.json')):self.assertEqual(predict(image),template(image))
 def test_invalid(self):
  for b in [0,601]:
   with self.assertRaises(ValueError):run(budget=b)
