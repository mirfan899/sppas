# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas.src.sp_glob import RESOURCES_PATH

from ..lang import sppasLangResource
from ..structsexc import LangTypeError, LangNameError, LangPathError

# ---------------------------------------------------------------------------


class TestLang(unittest.TestCase):

    def setUp(self):
        self.lr = sppasLangResource()

    def test_set(self):
        self.assertEqual(self.lr.get_lang(), "und")

        with self.assertRaises(LangPathError):
            self.lr.set("file", "wrongpath")

        with self.assertRaises(LangTypeError):
            self.lr.set("wrongtype", "vocab")

        self.lr.set("file", "vocab")
        langlist = self.lr.get_langlist()
        self.assertEqual(0, len(langlist))

        # Tokenization:
        self.lr.set("file", "vocab", "", ".vocab")
        self.assertEqual(os.path.join(RESOURCES_PATH, "vocab"), self.lr.get_langresource())
        self.lr.set_lang("fra")
        self.assertEqual("fra", self.lr.get_lang())
        self.assertEqual(os.path.join(RESOURCES_PATH, "vocab", "fra.vocab"), self.lr.get_langresource())
        with self.assertRaises(LangNameError):
            self.lr.set_lang("wrong")

        # Syllabification:
        self.lr.set("file", "syll", "syllConfig-", ".txt")
        self.lr.set_lang("fra")
        self.assertEqual(os.path.join(RESOURCES_PATH, "syll", "syllConfig-fra.txt"), self.lr.get_langresource())
        with self.assertRaises(LangNameError):
            self.lr.set_lang("wrong")

        # Alignment
        self.lr.set("directory", "models", "models-")
        self.lr.set_lang("fra")
        self.assertEqual(os.path.join(RESOURCES_PATH, "models", "models-fra"), self.lr.get_langresource())
        with self.assertRaises(LangNameError):
            self.lr.set_lang("wrong")

        self.lr.set("directory", "models", "models-", ".txt")
        self.lr.set_lang("fra")
        self.assertEqual(os.path.join(RESOURCES_PATH, "models", "models-fra"), self.lr.get_langresource())
        with self.assertRaises(LangNameError):
            self.lr.set_lang("wrong")


