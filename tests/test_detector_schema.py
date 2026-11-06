import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from aeromapper import vision


class DetectorSchema(unittest.TestCase):
    def test_reordered_features_do_not_use_incompatible_weights(self):
        model=json.loads(vision.MODEL.read_text())
        model['feature_schema']=list(reversed(model['feature_schema']))
        image=vision.patch(11,True)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'model.json';path.write_text(json.dumps(model))
            with patch.object(vision,'MODEL',path):
                self.assertEqual(vision.predict(image),vision.template(image))
