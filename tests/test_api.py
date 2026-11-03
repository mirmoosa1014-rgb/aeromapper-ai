import unittest
from fastapi.testclient import TestClient
from aeromapper.api import app
class API(unittest.TestCase):
 def test_loopback_cors_preflight(self):
  with TestClient(app) as client:
   for origin in ['http://127.0.0.1:5105','http://localhost:5105','http://localhost:8105']:
    with self.subTest(origin=origin):
     response=client.options('/api/compare',headers={'Origin':origin,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'Content-Type'})
     self.assertEqual(response.status_code,200)
     self.assertEqual(response.headers['access-control-allow-origin'],origin)
   response=client.options('/api/compare',headers={'Origin':'https://example.com','Access-Control-Request-Method':'POST'})
   self.assertEqual(response.status_code,400)
   self.assertNotIn('access-control-allow-origin',response.headers)
 def test_round_trip_and_validation(self):
  with TestClient(app) as client:
   self.assertFalse(client.get('/api/health').json()['hardware_connected']);r=client.post('/api/compare',json={'seed':2000,'budget':80,'family':'test'});self.assertEqual(r.status_code,200);self.assertEqual(set(r.json()),{'adaptive','lawnmower'});self.assertEqual(client.post('/api/compare',json={'budget':9999}).status_code,422);self.assertEqual(client.post('/api/compare',json={'family':'invalid'}).status_code,422)
