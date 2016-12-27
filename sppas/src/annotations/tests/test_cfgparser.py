#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os

from annotations.cfgparser import AnnotationConfigParser
from sp_glob import RESOURCES_PATH

from paths import SPPAS

INITOK   = os.path.join(SPPAS, "sppas", "etc", "Token.ini")
INIMOMEL = os.path.join(SPPAS, "sppas", "etc", "Momel.ini")

# ---------------------------------------------------------------------------

class TestAnnotationConfigParser(unittest.TestCase):

    def setUp(self):
        self.cfg = AnnotationConfigParser()

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

# ---------------------------------------------------------------------------

