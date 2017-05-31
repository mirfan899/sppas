# -*- coding:utf-8 -*-

import unittest
import os.path
import time

from sppas import BASE_PATH
from ..param import sppasPluginParam
from ..process import sppasPluginProcess

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
sample = os.path.join(os.path.dirname(BASE_PATH), "samples", "samples-eng", "oriana1.wav")

# ---------------------------------------------------------------------------


class TestPluginProcess(unittest.TestCase):

    def setUp(self):
        param = sppasPluginParam(DATA, "plugin.ini")
        self.process = sppasPluginProcess(param)

    def test_run(self):
        self.process.run(sample)
        time.sleep(0.3)
        self.process.stop()
        line = self.process.communicate()
        self.assertGreater(len(line), 0)
