#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os

from structs.lang import LangResource
from sp_glob import RESOURCES_PATH

# ---------------------------------------------------------------------------

class TestLang(unittest.TestCase):

    def setUp(self):
        self.lr = LangResource()

    def test_set(self):
        self.assertEqual(self.lr.get_lang(), "und")

        with self.assertRaises(IOError):
            self.lr.set("file", "wrongpath")

        with self.assertRaises(TypeError):
            self.lr.set("wrongtype", "vocab")

        self.lr.set("file", "vocab")
        langlist = self.lr.get_langlist()
        self.assertEqual(0, len(langlist))

        # Tokenization:
        self.lr.set("file", "vocab", "", ".vocab")
        self.assertEqual(os.path.join(RESOURCES_PATH,"vocab"), self.lr.get_langresource())
        self.lr.set_lang("fra")
        self.assertEqual("fra", self.lr.get_lang())
        self.assertEqual(os.path.join(RESOURCES_PATH,"vocab","fra.vocab"), self.lr.get_langresource())
        with self.assertRaises(ValueError):
            self.lr.set_lang("wrong")

        # Syllabification:
        self.lr.set("file", "syll", "syllConfig-", ".txt")
        self.lr.set_lang("fra")
        self.assertEqual(os.path.join(RESOURCES_PATH,"syll","syllConfig-fra.txt"), self.lr.get_langresource())
        with self.assertRaises(ValueError):
            self.lr.set_lang("wrong")

        # Alignment
        self.lr.set("directory", "models", "models-")
        self.lr.set_lang("fra")
        self.assertEqual(os.path.join(RESOURCES_PATH,"models","models-fra"), self.lr.get_langresource())
        with self.assertRaises(ValueError):
            self.lr.set_lang("wrong")

        self.lr.set("directory", "models", "models-", ".txt")
        self.lr.set_lang("fra")
        self.assertEqual(os.path.join(RESOURCES_PATH,"models","models-fra"), self.lr.get_langresource())
        with self.assertRaises(ValueError):
            self.lr.set_lang("wrong")


