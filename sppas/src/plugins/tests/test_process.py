#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import time
from plugins.param import sppasPluginParam
from plugins.process import sppasPluginProcess

from paths import DATA, SPPASSAMPLES
sample = os.path.join(SPPASSAMPLES, "samples-eng", "oriana1.wav")

# ---------------------------------------------------------------------------

class TestPluginProcess(unittest.TestCase):

    def setUp(self):
        param = sppasPluginParam( directory=DATA, cfgfile="plugin.ini")
        self.process = sppasPluginProcess(param)

    def test_run(self):
        self.process.run( sample )
        time.sleep(0.3)
        self.process.stop()
        line = self.process.communicate()
        self.assertGreater(len(line), 0)
