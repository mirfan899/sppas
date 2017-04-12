# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas import BASE_PATH

from ..cfgparser import sppasAnnotationConfigParser

INITOK = os.path.join(BASE_PATH, "etc", "TextNorm.ini")
INIMOMEL = os.path.join(BASE_PATH, "etc", "Momel.ini")

# ---------------------------------------------------------------------------


class TestAnnotationConfigParser(unittest.TestCase):

    def setUp(self):
        self.cfg = sppasAnnotationConfigParser()

    def test_parse_tok(self):
        self.cfg.parse(INITOK)

        conf = self.cfg.get_config()
        opt = self.cfg.get_options()
        res = self.cfg.get_resources()

        self.assertEqual(len(conf), 3)
        self.assertEqual(len(opt), 3)
        self.assertEqual(len(res), 1)

        self.assertEqual(conf['id'], "textnorm")

    def test_parse_momel(self):

        self.cfg.parse(INIMOMEL)
        conf = self.cfg.get_config()
        opt = self.cfg.get_options()
        res = self.cfg.get_resources()

        self.assertEqual(len(conf), 3)
        self.assertEqual(len(opt), 9)
        self.assertEqual(len(res), 0)
