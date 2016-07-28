#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os

from structs.confparser import ConfigParser
from sp_glob import RESOURCES_PATH

from paths import SPPAS

INITOK   = os.path.join(SPPAS, "sppas", "src", "annotations", "Token", "Token.ini")
INIMOMEL = os.path.join(SPPAS, "sppas", "src", "annotations", "Momel", "Momel.ini")

# ---------------------------------------------------------------------------

class TestConfigParser(unittest.TestCase):

    def setUp(self):
        self.cfg = ConfigParser()

    def test_parsetok(self):
        self.cfg.parse(INITOK)

        conf = self.cfg.get_config()
        opt = self.cfg.get_options()
        res = self.cfg.get_resources()

        self.assertEqual(len(conf), 3)
        self.assertEqual(len(opt), 1)
        self.assertEqual(len(res), 1)

        self.assertEqual(conf['id'], "tok")

    def test_parsemomel(self):

        self.cfg.parse(INIMOMEL)
        conf = self.cfg.get_config()
        opt = self.cfg.get_options()
        res = self.cfg.get_resources()

        self.assertEqual(len(conf), 3)
        self.assertEqual(len(opt), 9)
        self.assertEqual(len(res), 0)
