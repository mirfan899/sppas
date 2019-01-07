# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas.src.config import paths

from ..cfgparser import sppasAnnotationConfigParser

INITOK = os.path.join(paths.etc, "TextNorm.ini")
INIMOMEL = os.path.join(paths.etc, "Momel.ini")

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
        self.assertEqual(len(opt), 7)
        self.assertEqual(len(res), 0)
