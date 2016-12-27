#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
from plugins.param import sppasPluginParam
from paths import DATA

# ---------------------------------------------------------------------------


class TestPluginParam(unittest.TestCase):

    def setUp(self):
        self.param = sppasPluginParam(DATA, "plugin.ini")

    def test_getters(self):
        self.assertEqual(self.param.get_key(), "pluginid")
        self.assertEqual(self.param.get_name(), "The Plugin Name")
        self.assertEqual(self.param.get_descr(), "Performs something on some files.")
        self.assertEqual(self.param.get_icon(), "")

        opt = self.param.get_options()
        self.assertEqual(len(opt), 3)
        self.assertEqual(opt["Option1"].get_key(), "-b")
        self.assertEqual(opt["Option2"].get_key(), "--show-progress")

