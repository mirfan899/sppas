#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
from plugins.manager import sppasPluginsManager

from paths import DATA, SPPASSAMPLES
soxplugin=os.path.join(DATA, "soxplugin.zip")
sample = os.path.join(SPPASSAMPLES, "samples-eng", "oriana1.wav")

# ---------------------------------------------------------------------------

class TestPluginsManager(unittest.TestCase):

    def setUp(self):
        self.manager = sppasPluginsManager()

    def test_all(self):
        self.assertEqual(len(self.manager.get_plugin_ids()), 0)

        # Install a plugin
        soxid = self.manager.install( soxplugin, "SoX" )
        self.assertEqual(len(self.manager.get_plugin_ids()), 1)

        # Use it!
        output=os.path.join(DATA,"testsox.wav")
        p = self.manager.get_plugin( soxid )
        options = p.get_options()
        for opt in options:
            if opt.get_key() == "output":
                opt.set_value( output )
        p.set_options(options)
        message = self.manager.run_plugin( soxid, [sample] )
        self.assertTrue(os.path.exists(output))
        os.remove( output )

        # Delete it...
        self.manager.delete( soxid )
        self.assertEqual(len(self.manager.get_plugin_ids()), 0)
