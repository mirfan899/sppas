# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas import BASE_PATH
from ..manager import sppasPluginsManager

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
soxplugin = os.path.join(DATA, "soxplugin.zip")
sample = os.path.join(os.path.dirname(BASE_PATH), "samples", "samples-eng", "oriana1.wav")

# ---------------------------------------------------------------------------


class TestPluginsManager(unittest.TestCase):

    def setUp(self):
        self.manager = sppasPluginsManager()

    def test_all(self):
        self.assertEqual(len(self.manager.get_plugin_ids()), 0)

        # Install a plugin
        soxid = self.manager.install(soxplugin, "SoX")
        self.assertEqual(len(self.manager.get_plugin_ids()), 1)

        # Use it!
        output = sample.replace('.wav', '-converted.wav')
        p = self.manager.get_plugin(soxid)

        message = self.manager.run_plugin(soxid, [sample])
        self.assertTrue(os.path.exists(output))
        os.remove(output)

        # Delete it...
        self.manager.delete(soxid)
        self.assertEqual(len(self.manager.get_plugin_ids()), 0)
