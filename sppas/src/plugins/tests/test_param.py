# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas.src.utils.makeunicode import u
from ..param import sppasPluginParam

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

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
        self.assertEqual(len(opt), 4)
        self.assertEqual(opt["Option1"].get_key(), "-b")
        self.assertEqual(opt["Option2"].get_key(), "--show-progress")
        self.assertEqual(opt["Option3"].get_key(), "-i")
        self.assertEqual(opt["Option3"].get_value(), u('C:\Windows'))
