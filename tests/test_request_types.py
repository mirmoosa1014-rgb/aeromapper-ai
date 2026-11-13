import unittest
from fastapi.testclient import TestClient
from aeromapper.api import app
class RequestTypes(unittest.TestCase):
 def test_boolean_and_string_seeds_are_not_coerced(self):
  with TestClient(app) as client:
   for value in [True,False,'2000',2000.0]:
    with self.subTest(value=value):self.assertEqual(client.post('/api/compare',json={'seed':value,'budget':40}).status_code,422)
 def test_numeric_budget_remains_supported(self):
  with TestClient(app) as client:self.assertEqual(client.post('/api/compare',json={'seed':2000,'budget':40}).status_code,200)
