# -*- coding:utf-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.resources.tests.test_dict.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os.path

from sppas import RESOURCES_PATH
from sppas.src.utils.makeunicode import u

from ..dictpron import sppasDictPron
from ..dictrepl import sppasDictRepl
from ..mapping import sppasMapping
from ..unigram import sppasUnigram

# ---------------------------------------------------------------------------

DICT_TEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dict.txt")
DICT_TEST_OK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "dict_ok.txt")

# ---------------------------------------------------------------------------


class TestDictPron(unittest.TestCase):

    def test_init(self):
        d = sppasDictPron()
        self.assertEqual(len(d), 0)

    def test_add(self):
        # simple and normal situation
        d = sppasDictPron()
        d.add_pron("a", "a")
        d.add_pron("A", "a")
        self.assertEqual(len(d), 1)

        # unicode
        d = sppasDictPron()
        d.add_pron("é", "e")
        d.add_pron("É", "e")
        d.add_pron(u("É"), "e")
        self.assertEqual(len(d), 1)
        self.assertTrue("É" in d)
        self.assertTrue(u("É") in d)

    def test_is_unk(self):
        d = sppasDictPron(DICT_TEST, nodump=True)
        self.assertTrue(d.is_unk('azerty'))
        self.assertFalse(d.is_unk('ab'))
        self.assertFalse(d.is_unk(u('être')))
        self.assertFalse(d.is_unk('être'))

    def test_is_pron_of(self):
        d = sppasDictPron(DICT_TEST, nodump=True)
        self.assertTrue(d.is_pron_of("abc", "a-b-c"))

    def test_get_pron(self):
        d = sppasDictPron(DICT_TEST, nodump=True)
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
        d = sppasDictPron(DICT_TEST_OK, nodump=True)
        d.save_as_ascii(DICT_TEST+".copy")
        d2 = sppasDictPron(DICT_TEST+".copy", nodump=True)
        for token in d:
            self.assertEqual(d.get_pron(token), d2.get_pron(token))
        os.remove(DICT_TEST+".copy")

# ---------------------------------------------------------------------------


class TestUnigram(unittest.TestCase):

    def test_unigram(self):
        gram = sppasUnigram()
        gram.add('a')
        self.assertEqual(len(gram), 1)
        self.assertEqual(gram.get_count('a'), 1)
        gram.add('a')
        self.assertEqual(len(gram), 1)
        self.assertEqual(gram.get_count('a'), 2)
        gram.add('  a \t', 3)
        self.assertEqual(len(gram), 1)
        self.assertEqual(gram.get_count('a'), 5)
        with self.assertRaises(ValueError):
            gram.add('b', 0)

# ---------------------------------------------------------------------------


class TestDictRepl(unittest.TestCase):

    def setUp(self):
        self.replfile = os.path.join(RESOURCES_PATH, "repl", "fra.repl")

    def test_init_with_dict(self):
        dict1 = sppasDictRepl(self.replfile, nodump=True)
        dict2 = sppasDictRepl()
        self.assertEqual(len(dict2), 0)

    def test_is_empty(self):
        d = sppasDictRepl()
        self.assertTrue(d.is_empty())
        d.add("key1", "v1")
        self.assertFalse(d.is_empty())

    def test_getters(self):
        d = sppasDictRepl()
        d.add("key1", "v1")
        self.assertEqual(d.get("key1"), "v1")
        self.assertIsNone(d.get("key2"))
        self.assertEqual(d.get("key2", "unk"), "unk")

        self.assertTrue(d.is_key("key1"))
        self.assertFalse(d.is_key("v1"))
        self.assertTrue("key1" in d)
        self.assertFalse("v1" in d)

        self.assertTrue(d.is_value("v1"))
        self.assertTrue(d.is_value_of("key1", "v1"))
        self.assertFalse(d.is_value("v2"))
        self.assertFalse(d.is_value_of("key1", "v2"))

    def test_unicode_getters(self):
        d = sppasDictRepl()
        d.add("keyé", "éé")
        self.assertEqual(d.get("keyé"), "éé")
        self.assertIsNone(d.get("key2"))
        self.assertEqual(d.get("key2", "unk"), "unk")

        self.assertTrue(d.is_key("keyé"))
        self.assertFalse(d.is_key("éé"))
        self.assertTrue("keyé" in d)
        self.assertFalse("éé" in d)

        self.assertTrue(d.is_value("éé"))
        self.assertTrue(d.is_value_of("keyé", "éé"))
        self.assertFalse(d.is_value("v2"))
        self.assertFalse(d.is_value_of("keyé", "v2"))

    def test_add(self):
        d = sppasDictRepl()
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

        # unicode
        d.add("  éé \t ", "ee")
        d.add("ÉÉ", "ee")
        self.assertTrue("éé" in d)
        self.assertTrue(u("éé") in d)

    def test_remove(self):
        d = sppasDictRepl()
        d.add("key1", "v1")
        d.remove('key1')
        self.assertEqual(len(d), 0)

    def test_reversed(self):
        d = sppasDictRepl()
        d.add("key1", "v1")
        d.add("key1", "v2")
        d.add("key2", "v2")

        self.assertTrue(d.replace_reversed("v1"), "key1")
        self.assertTrue(d.replace_reversed("v2"), "key1|key2")
        self.assertEqual(d.replace_reversed("v0"), "")

# ---------------------------------------------------------------------------


class TestMapping(unittest.TestCase):

    def setUp(self):
        self.replfile = os.path.join(RESOURCES_PATH, "models", "models-fra", "monophones.repl")

    def test_init_with_dict(self):
        dict1 = sppasMapping(self.replfile)

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
        dict2 = sppasMapping()
        dict2.set_keep_miss(True)
        dict2.set_reverse(False)
        dict2.add('+', "sp")
        self.assertEqual(len(dict2), 1)
        self.assertEqual("sp", dict2.map_entry("+"))

        dict2.add('+', "+")
        self.assertEqual(len(dict2), 1)
        self.assertEqual("sp|+", dict2.map_entry("+"))
        self.assertEqual("toto", dict2.map_entry("toto"))
        dict2.set_keep_miss(False)
        self.assertEqual("", dict2.map_entry("toto"))

        dict2.set_reverse(True)
        self.assertEqual("+", dict2.map_entry("+"))
        self.assertEqual("+", dict2.map_entry("sp"))
        self.assertEqual("", dict2.map_entry("a"))

    def test_map(self):
        dict1 = sppasMapping(self.replfile)
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
        self.assertEqual("a", dict1.map("a", delimiters=()))
        self.assertEqual("9", dict1.map("oe", delimiters=()))
        self.assertEqual("a9@", dict1.map("aoe@", delimiters=()))
        self.assertEqual(".", dict1.map(".", delimiters=()))
        self.assertEqual(" ", dict1.map(" ", delimiters=()))
        self.assertEqual("-", dict1.map("-", delimiters=()))
        self.assertEqual("9 ", dict1.map("oe ", delimiters=()))
        self.assertEqual("a-9@", dict1.map("a-oe@", delimiters=()))
        self.assertEqual("lleu ko~.bl9", dict1.map("lleu ko~.bloe", delimiters=()))

    def test_is_key(self):
        d = sppasMapping()
        d.add("a", " & ")
        self.assertTrue(" a " in d)
        self.assertFalse(" A " in d)
        self.assertFalse(d.is_key("a "))
        self.assertFalse(d.is_key("A"))
