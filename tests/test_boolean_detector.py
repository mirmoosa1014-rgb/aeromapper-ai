import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from aeromapper import vision
class BooleanDetector(unittest.TestCase):
 def test_boolean_parameters_do_not_load(self):
  for key,value in [('weights',[True]*5),('temperature',True)]:
   model=json.loads(vision.MODEL.read_text());model[key]=value
   with tempfile.TemporaryDirectory() as directory:
    path=Path(directory)/'model.json';path.write_text(json.dumps(model))
    with patch.object(vision,'MODEL',path):self.assertIsNone(vision.load_model())
