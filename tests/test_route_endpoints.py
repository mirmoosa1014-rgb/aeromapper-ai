import unittest
from aeromapper.simulation import route
class RouteEndpoints(unittest.TestCase):
 def test_blocked_endpoints_are_unreachable(self):
  self.assertIsNone(route((0,0),(1,0),{(0,0)}))
  self.assertIsNone(route((0,0),(0,0),{(0,0)}))
 def test_out_of_grid_endpoints_rejected(self):
  self.assertIsNone(route((-1,0),(0,0),set()))
  self.assertIsNone(route((12,0),(12,0),set()))
 def test_valid_stationary_route(self):self.assertEqual(route((0,0),(0,0),set()),[])
