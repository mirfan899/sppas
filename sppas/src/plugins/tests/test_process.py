# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas.src.config import paths
from ..param import sppasPluginParam
from ..process import sppasPluginProcess

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
sample = os.path.join(paths.samples, "samples-eng", "oriana1.wav")

# ---------------------------------------------------------------------------


class TestPluginProcess(unittest.TestCase):

    def setUp(self):
        param = sppasPluginParam(DATA, "plugin.json")
        self.process = sppasPluginProcess(param)

    def test_run(self):
        self.process.run(sample)
        # time.sleep(0.8)
        # self.process.stop()
        line = self.process.communicate()
        # we'll get the usage of the sox command:
        self.assertGreater(len(line), 10)
