#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os

from plugins.cfgparser import PluginConfigParser

from paths import DATA

configfile = os.path.join(DATA, "plugin.ini")

# ---------------------------------------------------------------------------

class TestPluginConfigParser(unittest.TestCase):

    def setUp(self):
        self.cfg = PluginConfigParser()

    def test_parsetok(self):
        self.cfg.parse( configfile )

        conf = self.cfg.get_config()
        opt = self.cfg.get_options()
        com = self.cfg.get_command()

        self.assertEqual(len(conf), 3) # id, name, descr
        self.assertEqual(len(opt), 3)  # input, -v, show-progress
        self.assertEqual(len(com), 3)

        self.assertEqual(conf['id'], "pluginid")

# ---------------------------------------------------------------------------
