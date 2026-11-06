import unittest
from pathlib import Path
from unittest.mock import patch
from aeromapper.simulation import run
from aeromapper import vision


class ModelLoading(unittest.TestCase):
    def test_missing_detector_is_reported_as_fallback(self):
        with patch.object(vision, 'MODEL', Path('/missing/detector.json')):
            result = run(budget=40)
        self.assertEqual(result['model'], 'template fallback')

    def test_mission_reads_one_detector_snapshot(self):
        original = Path.read_text
        reads = []
        def read(path, *args, **kwargs):
            if path == vision.MODEL:
                reads.append(path)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read):
            result = run(budget=80)
        self.assertEqual(len(reads), 1)
        self.assertEqual(result['model'], 'trained logistic image-feature detector')
