#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
from shutil import copyfile

from plugins.cfgparser import sppasPluginConfigParser

from paths import DATA

configfile = os.path.join(DATA, "plugin.ini")

# ---------------------------------------------------------------------------

class TestPluginConfigParser(unittest.TestCase):

    def setUp(self):
        self.cfg = sppasPluginConfigParser( configfile )

    def test_parse(self):

        conf = self.cfg.get_config()
        opt = self.cfg.get_options()
        com = self.cfg.get_command()

        self.assertEqual(len(conf), 3) # id, name, descr
        self.assertEqual(len(opt), 3)  # input, -v, show-progress
        self.assertEqual(len(com), 3)

        self.assertEqual(conf['id'], "pluginid")


    def test_save(self):
        self.cfg.save()
        self.assertTrue( os.path.exists( configfile+".backup") )
        self.assertTrue( os.path.exists( configfile) )
        newcfg = sppasPluginConfigParser( configfile )

        # restore (for next tests!)
        copyfile(configfile+".backup", configfile)
        os.remove(configfile+".backup")


        conf = newcfg.get_config()
        opt  = newcfg.get_options()
        com  = newcfg.get_command()

        self.assertEqual(len(conf), 3) # id, name, descr
        self.assertEqual(len(opt), 3)  # input, -v, show-progress
        self.assertEqual(len(com), 3)

# ---------------------------------------------------------------------------
