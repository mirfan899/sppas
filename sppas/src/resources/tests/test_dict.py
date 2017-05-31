#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas import RESOURCES_PATH
from sppas.src.utils.makeunicode import u

from ..dictpron import DictPron
from ..dictrepl import DictRepl
from ..mapping import Mapping
from ..unigram import Unigram

# ---------------------------------------------------------------------------

DICT_TEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dict.txt")
DICT_TEST_OK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dict_ok.txt")

# ---------------------------------------------------------------------------


class TestDictPron(unittest.TestCase):

    def test_dict(self):
        d = DictPron()
        self.assertEqual(len(d), 0)

        d = DictPron(DICT_TEST, nodump=True)
        self.assertTrue(d.is_unk('azerty'))
        self.assertFalse(d.is_unk('ab'))
        self.assertFalse(d.is_unk(u('être')))

        self.assertTrue(d.is_pron_of("abc", "a-b-c"))

        self.assertEqual(d.get_pron(u('sil')), "s-i-l")
        self.assertEqual(d.get_pron(u('azerty')), "<UNK>")
        self.assertEqual(d.get_pron(u('abc')), "a-b-c|a-c")
        self.assertEqual(d.get_pron(u('toto')), "t-o-t-o")
        self.assertEqual(d.get_pron(u('titi')), "t-i-t-i")
        self.assertEqual(d.get_pron(u('tata')), "t-a-t-a")
        self.assertEqual(d.get_pron(u('tutu')), "t-u-t-u")
        self.assertEqual(d.get_pron(u('tyty')), "t-y-t-y")
        self.assertEqual(d.get_pron(u('tete')), "t-e-t-e")

    def test_save(self):
        d = DictPron(DICT_TEST_OK, nodump=True)
        d.save_as_ascii(DICT_TEST+".copy")
        d2 = DictPron(DICT_TEST+".copy", nodump=True)
        for w in d.get_keys():
            self.assertEqual(d.get_pron(w), d2.get_pron(w))
        os.remove(DICT_TEST+".copy")

# ---------------------------------------------------------------------------


class TestUnigram(unittest.TestCase):

    def test_unigram(self):
        gram = Unigram()
        gram.add('a')
        self.assertEqual(gram.get_size(), 1)
        self.assertEqual(gram.get_size(), len(gram))
        self.assertEqual(gram.get_count('a'), 1)
        gram.add('a')
        self.assertEqual(gram.get_size(), 1)
        self.assertEqual(gram.get_count('a'), 2)
        gram.add('  a \t', 3)
        self.assertEqual(gram.get_size(), 1)
        self.assertEqual(gram.get_count('a'), 5)
        with self.assertRaises(ValueError):
            gram.add('b', 0)

# ---------------------------------------------------------------------------


class TestDictRepl(unittest.TestCase):

    def setUp(self):
        self.replfile = os.path.join(RESOURCES_PATH, "repl", "fra.repl")

    def test_init_with_dict(self):
        dict1 = DictRepl(self.replfile, nodump=True)
        dict2 = DictRepl()
        self.assertEqual(len(dict2), 0)

    def test_dict_simple(self):
        d = DictRepl()
        d.add("key1", "v1")
        d.add("key1", "v2")
        d.add("key2", "v2")

        self.assertEqual(d.get("key1"), "v1|v2")
        self.assertTrue(d.is_value("v1"))
        self.assertTrue(d.is_value("v2"))
        self.assertTrue(d.is_value_of("key1", "v1"))
        self.assertTrue(d.is_value_of("key1", "v2"))
        self.assertFalse(d.is_value("v1|v2"))
        self.assertTrue(d.is_value_of("key2", "v2"))
        self.assertFalse(d.is_value_of("key2", "v1"))

        d.add("  éé \t ", "ee")
        self.assertTrue(u("éé") in d)

# ---------------------------------------------------------------------------


class TestMapping(unittest.TestCase):

    def setUp(self):
        self.replfile = os.path.join(RESOURCES_PATH, "models", "models-fra", "monophones.repl")

    def test_init_with_dict(self):
        dict1 = Mapping(self.replfile)

        dict1.set_keep_miss(True)
        dict1.set_reverse(False)
        self.assertEqual("@", dict1.map_entry("@"))
        self.assertEqual("+", dict1.map_entry("sp"))
        self.assertEqual("9", dict1.map_entry("oe"))

        dict1.set_keep_miss(True)
        dict1.set_reverse(True)
        self.assertEqual("@", dict1.map_entry("@"))
        self.assertEqual("sp", dict1.map_entry("+"))
        self.assertEqual("oe", dict1.map_entry("9"))

        dict1.set_keep_miss(True)
        dict1.set_reverse(False)
        self.assertEqual("toto", dict1.map_entry("toto"))
        dict1.set_keep_miss(False)
        self.assertEqual("", dict1.map_entry("toto"))

    def test_init_without_dict(self):
        dict2 = Mapping()
        dict2.set_keep_miss(True)
        dict2.set_reverse(False)
        dict2.add('+',"sp")
        self.assertEqual(dict2.get_size(), 1)
        self.assertEqual("sp", dict2.map_entry("+"))

        dict2.add('+',"+")
        self.assertEqual(dict2.get_size(), 1)
        self.assertEqual("sp|+", dict2.map_entry("+"))
        self.assertEqual("toto", dict2.map_entry("toto"))
        dict2.set_keep_miss(False)
        self.assertEqual("", dict2.map_entry("toto"))

        dict2.set_reverse(True)
        self.assertEqual("+", dict2.map_entry("+"))
        self.assertEqual("+", dict2.map_entry("sp"))
        self.assertEqual("", dict2.map_entry("a"))

    def test_map(self):
        dict1 = Mapping(self.replfile)
        dict1.set_keep_miss(True)
        self.assertEqual("a", dict1.map_entry("a"))
        self.assertEqual("9", dict1.map_entry("oe"))
        self.assertEqual("@", dict1.map_entry("@"))

        self.assertEqual("a-9+@", dict1.map("a-oe+@"))
        self.assertEqual("l|l.eu|l.e k.o~.b.l.eu|k.o~.b.l", dict1.map("l|l.eu|l.e k.o~.b.l.eu|k.o~.b.l"))
        self.assertEqual("l|l-eu|l-e k-o~-b-l-eu|k-o~-b-l", dict1.map("l|l-eu|l-e k-o~-b-l-eu|k-o~-b-l"))

        dict1.set_reverse(True)
        self.assertEqual("l|l.eu|l.e k.o~.b.l.eu|k.o~.b.l", dict1.map("l|l.eu|l.e k.o~.b.l.eu|k.o~.b.l"))
        self.assertEqual("l|l-eu|l-e k-o~-b-l-eu|k-o~-b-l", dict1.map("l|l-eu|l-e k-o~-b-l-eu|k-o~-b-l"))

        dict1.set_reverse(False)
        self.assertEqual("a", dict1.map("a", ()))
        self.assertEqual("9", dict1.map("oe", ()))
        self.assertEqual("a9@", dict1.map("aoe@", ()))
        self.assertEqual("a-9@", dict1.map("a-oe@", ()))
        self.assertEqual("lleu ko~.bl9", dict1.map("lleu ko~.bloe", ()))
