# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas.src.config import paths
from ..manager import sppasPluginsManager

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
soxplugin = os.path.join(DATA, "soxplugintest.zip")
sample = os.path.join(paths.samples, "samples-eng", "oriana1.wav")

# ---------------------------------------------------------------------------


class TestPluginsManager(unittest.TestCase):

    def setUp(self):
        self.manager = sppasPluginsManager()

    def test_all(self):

        # 5 plugins are already installed in the package of SPPAS
        plg = 5
        self.assertEqual(plg, len(self.manager.get_plugin_ids()))

        # Install a plugin
        soxid = self.manager.install(soxplugin, "SoX")
        self.assertEqual(plg+1, len(self.manager.get_plugin_ids()))

        # Use it!
        output = sample.replace('.wav', '-converted.wav')
        p = self.manager.get_plugin(soxid)

        message = self.manager.run_plugin(soxid, [sample])
        self.assertGreater(len(message), 0)
        self.assertTrue(os.path.exists(output))
        os.remove(output)

        # Delete it...
        self.manager.delete(soxid)
        self.assertEqual(plg, len(self.manager.get_plugin_ids()))
