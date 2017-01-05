#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import time

from plugins.param import sppasPluginParam
from plugins.process import sppasPluginProcess
from sp_glob import BASE_PATH

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

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(TestPluginProcess))
    unittest.TextTestRunner(verbosity=2).run(testsuite)
