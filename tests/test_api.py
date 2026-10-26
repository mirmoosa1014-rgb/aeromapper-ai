import unittest
from fastapi.testclient import TestClient
from aeromapper.api import app
class API(unittest.TestCase):
 def test_round_trip_and_validation(self):
  with TestClient(app) as client:
   self.assertFalse(client.get('/api/health').json()['hardware_connected']);r=client.post('/api/compare',json={'seed':2000,'budget':80,'family':'test'});self.assertEqual(r.status_code,200);self.assertEqual(set(r.json()),{'adaptive','lawnmower'});self.assertEqual(client.post('/api/compare',json={'budget':9999}).status_code,422);self.assertEqual(client.post('/api/compare',json={'family':'invalid'}).status_code,422)
