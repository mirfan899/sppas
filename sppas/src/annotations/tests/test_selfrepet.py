# -*- coding: utf8 -*-
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

    src.annotations.tests.test_selfrepet.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os
import shutil
import codecs

from ..SelfRepet.datastructs import DataRepetition
from ..SelfRepet.datastructs import Entry
from ..SelfRepet.datastructs import DataSpeaker
from ..SelfRepet.rules import SelfRules

# ---------------------------------------------------------------------------


class TestDataRepetition(unittest.TestCase):
    """Class to store one repetition (the source and the echos)."""

    def test_init(self):
        # normal situation: init with a source
        r = DataRepetition(1, 2)
        self.assertEqual(r.get_source(), (1, 2))
        self.assertEqual(len(r.get_echos()), 0)

        # normal situation: init with a source and an echo
        r = DataRepetition(1, 2, 3, 4)
        self.assertEqual((1, 2), r.get_source())
        self.assertEqual([(3, 4)], r.get_echos())

        # no negative values
        with self.assertRaises(ValueError):
            DataRepetition(-1, 2)
        with self.assertRaises(ValueError):
            DataRepetition(1, -1)

    # -----------------------------------------------------------------------

    def test_add_echo(self):
        # normal situation, everything is correct
        r = DataRepetition(1, 2)
        r.add_echo(3, 4)
        self.assertEqual(r.get_source(), (1, 2))
        self.assertEqual(r.get_echos(), [(3, 4)])

        # no negative values
        with self.assertRaises(ValueError):
            r.add_echo(-3, 4)

        # do not add an echo if no was source defined
        r = DataRepetition(None, 2)
        with self.assertRaises(Exception):
            r.add_echo(3, 4)

    # -----------------------------------------------------------------------

    def test_set_source(self):
        # normal situation, everything is correct
        r = DataRepetition(1, 2)
        r.add_echo(3, 4)
        self.assertEqual(r.get_source(), (1, 2))
        self.assertEqual(r.get_echos(), [(3, 4)])

        # set a new source: it invalidates the existing echos
        r.set_source(2, 3)
        self.assertEqual(r.get_source(), (2, 3))
        self.assertEqual(r.get_echos(), [])

# ---------------------------------------------------------------------------


class TestEntry(unittest.TestCase):
    """Class to store a formatted unicode entry."""

    def test_get_set(self):
        e = Entry(None)
        self.assertEqual(0, len(e.get()))
        e = Entry("\t-")
        self.assertEqual(0, len(e.get()))

        e = Entry('token')
        e.set("toto")
        self.assertEqual("toto", e.get())

# ---------------------------------------------------------------------------


class TestDataSpeaker(unittest.TestCase):

    def test_init(self):
        d = DataSpeaker([])
        self.assertEqual(len(d), 0)

    # -----------------------------------------------------------------------

    def test_entries(self):
        d = DataSpeaker(["tok1", "tok2"])
        self.assertEqual(len(d), 2)
        self.assertEqual(d[0], "tok1")
        self.assertEqual(d[1], "tok2")
        d = DataSpeaker(["    é  tok1 \t "])
        self.assertEqual(d[0], "é tok1")

    # -----------------------------------------------------------------------

    def test_get_next_word(self):
        d = DataSpeaker(["tok1", "tok2"])
        self.assertEqual(d.get_next_word(0), 1)
        self.assertEqual(d.get_next_word(1), -1)
        d = DataSpeaker(["tok1", "*", "tok2"])
        self.assertEqual(d.get_next_word(0), 2)
        self.assertEqual(d.get_next_word(1), 2)

        with self.assertRaises(IndexError):
            d.get_next_word(-1)
        with self.assertRaises(IndexError):
            d.get_next_word(3)

    # -----------------------------------------------------------------------

    def test_is_word(self):
        d = DataSpeaker(["tok1", "euh", "*", "\t"])
        self.assertTrue(d.is_word(0))
        self.assertTrue(d.is_word(1))
        self.assertFalse(d.is_word(2))
        self.assertFalse(d.is_word(3))

    # -----------------------------------------------------------------------

    def test_is_token_repeated(self):
        d = DataSpeaker(["tok1", "tok2", "tok1"])
        self.assertEqual(d.is_word_repeated(0, 1, d), 2)
        self.assertEqual(d.is_word_repeated(1, 2, d), -1)

# ---------------------------------------------------------------------------


class TestSelfRules(unittest.TestCase):

    def test_is_relevant(self):
        # without stop-words
        r = SelfRules()
        self.assertTrue(r.is_relevant(0, DataSpeaker(["word"])))
        self.assertFalse(r.is_relevant(0, DataSpeaker(["*"])))

        # with stop-words
        r = SelfRules(["toto"])
        self.assertTrue(r.is_relevant(0, DataSpeaker(["word"])))
        self.assertFalse(r.is_relevant(0, DataSpeaker(["#"])))
        self.assertFalse(r.is_relevant(0, DataSpeaker(["toto"])))

    def test_count_relevant(self):
        # without stop-words
        r = SelfRules()
        self.assertEqual(0, r.count_relevant_tokens(0, 0, DataSpeaker(["#"])))
        self.assertEqual(1, r.count_relevant_tokens(0, 0, DataSpeaker(["word"])))
        self.assertEqual(1, r.count_relevant_tokens(0, 1, DataSpeaker(["word", "#"])))
        self.assertEqual(0, r.count_relevant_tokens(0, 0, DataSpeaker(["*", "word"])))

        # with stop-words
        r = SelfRules(["toto"])
        self.assertEqual(1, r.count_relevant_tokens(0, 2, DataSpeaker(["word", "#", "toto"])))
        self.assertEqual(0, r.count_relevant_tokens(0, 1, DataSpeaker(["#", "toto", "word"])))

        r = SelfRules(['euh'])
        d = DataSpeaker(["tok1", "euh", "tok1", "*"])
        self.assertEqual(2, r.count_relevant_tokens(0, 3, d))

    def test_rule_one_token(self):
        # no list of stop words
        r = SelfRules()
        d = DataSpeaker(["tok1", "tok2", "tok1"])
        self.assertTrue(r.rule_one_token(0, d))
        self.assertFalse(r.rule_one_token(1, d))
        r = SelfRules()
        d = DataSpeaker(["tok1", "*", "tok1", "*"])
        self.assertTrue(r.rule_one_token(0, d))
        self.assertFalse(r.rule_one_token(1, d))

        # with a list of stop words
        r = SelfRules(['euh'])
        d = DataSpeaker(["tok1", "euh", "tok1", "euh"])
        self.assertTrue(r.rule_one_token(0, d))
        self.assertFalse(r.rule_one_token(1, d))

        r = SelfRules(["toto"])
        self.assertFalse(r.rule_one_token(0, DataSpeaker(["#"])))
        self.assertFalse(r.rule_one_token(0, DataSpeaker(["toto"])))
        self.assertFalse(r.rule_one_token(0, DataSpeaker(["word"])))
        self.assertFalse(r.rule_one_token(0, DataSpeaker(["#", "#"])))
        self.assertFalse(r.rule_one_token(0, DataSpeaker(["toto", "toto"])))
        self.assertTrue(r.rule_one_token(0, DataSpeaker(["word", "word"])))

    def test_rule_syntagme(self):
        r = SelfRules(['euh'])
        d = DataSpeaker(["tok1", "euh", "tok1", "*"])
        self.assertTrue(r.rule_syntagme(0, 3, d))
