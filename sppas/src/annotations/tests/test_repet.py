# -*- coding:utf-8 -*-

import os
import unittest

from sppas import RESOURCES_PATH

from ..Repet.datastructs import DataRepetition, Entry, DataSpeaker
from ..Repet.rules import Rules
from ..Repet.detectrepet import Repetitions
from ..Repet.sppasrepet import sppasRepet

# ---------------------------------------------------------------------------

STOP_LIST = ["ah", "aller", "alors", "après", "avec", "avoir", "bon", "ce", "comme", "c'est", "dans", "de", "de+le", "dire", "donc", "eeh", "eh", "en", "en_fait", "et", "etc", "euh", "hein", "heu", "hum", "hm", "il", "le", "lui", "là", "mais", "meuh", "mh", "mhmh", "mmh", "moi", "mon", "ne", "non", "null", "on", "ou", "ouais", "oui", "où", "pas", "peu", "pf", "pff", "plus", "pour", "quand", "que", "qui", "quoi", "se", "si", "sur", "tout", "très", "un", "voilà", "voir", "y", "à", "ça", "être"]
STOP_LIST_FRA = os.path.join(RESOURCES_PATH, "vocab", "fra.stp")

# ---------------------------------------------------------------------------


class TestDataRepetition(unittest.TestCase):

    def test_init(self):
        r = DataRepetition(1, 2)
        self.assertEqual(r.get_source(), (1, 2))
        self.assertEqual(len(r.get_echos()), 0)
        r = DataRepetition(1, 2, 3, 4)
        self.assertEqual(r.get_source(), (1, 2))
        self.assertEqual(r.get_echos(), [(3, 4)])
        with self.assertRaises(ValueError):
            r = DataRepetition(-1, 2)

    def test_add_echo(self):
        r = DataRepetition(1, 2)
        r.add_echo(3, 4)
        self.assertEqual(r.get_source(), (1, 2))
        self.assertEqual(r.get_echos(), [(3, 4)])
        with self.assertRaises(ValueError):
            r.add_echo(-3, 4)

# ---------------------------------------------------------------------------


class TestEntry(unittest.TestCase):

    def test_is_token(self):
        e = Entry('token')
        self.assertTrue(e.is_token())
        e = Entry('   \t token')
        self.assertTrue(e.is_token())
        e = Entry('dummy')
        self.assertFalse(e.is_token())
        e = Entry('     dummy   \t')
        self.assertFalse(e.is_token())
        e = Entry('*')
        self.assertFalse(e.is_token())

# ---------------------------------------------------------------------------


class TestDataSpeaker(unittest.TestCase):

    def test_init(self):
        d = DataSpeaker([])
        self.assertEqual(len(d), 0)

    def test_entries(self):
        d = DataSpeaker(["tok1", "tok2"])
        self.assertEqual(len(d), 2)
        self.assertEqual(d[0], "tok1")
        self.assertEqual(d[1], "tok2")
        d = DataSpeaker(["    é  tok1 \t "])
        self.assertEqual(d[0], "é tok1")

    def test_get_next_token(self):
        d = DataSpeaker(["tok1", "tok2"])
        self.assertEqual(d.get_next_token(0), 1)
        self.assertEqual(d.get_next_token(1), -1)
        d = DataSpeaker(["tok1", "*", "tok2"])
        self.assertEqual(d.get_next_token(0), 2)
        self.assertEqual(d.get_next_token(1), 2)
        with self.assertRaises(ValueError):
            d.get_next_token(-1)
        with self.assertRaises(ValueError):
            d.get_next_token(3)

    def test_is_token_repeated(self):
        d = DataSpeaker(["tok1", "tok2", "tok1"])
        self.assertEqual(d.is_token_repeated(0, 1, d), 2)
        self.assertEqual(d.is_token_repeated(1, 2, d), -1)

# ---------------------------------------------------------------------------


class TestRules(unittest.TestCase):

    def test_is_relevant(self):
        # no list of stop words
        r = Rules()
        self.assertTrue(r.is_relevant_token("token"))
        self.assertFalse(r.is_relevant_token("*"))
        self.assertTrue(r.is_relevant_token("euh"))
        # with a list of stop words
        r = Rules(['euh'])
        self.assertTrue(r.is_relevant_token("token"))
        self.assertFalse(r.is_relevant_token("*"))
        self.assertFalse(r.is_relevant_token("euh"))

    def test_apply_rules_one_token(self):
        # no list of stop words
        r = Rules()
        d = DataSpeaker(["tok1", "tok2", "tok1"])
        self.assertTrue(r.apply_rules_one_token(0, d))
        self.assertFalse(r.apply_rules_one_token(1, d))
        r = Rules()
        d = DataSpeaker(["tok1", "*", "tok1", "*"])
        self.assertTrue(r.apply_rules_one_token(0, d))
        self.assertFalse(r.apply_rules_one_token(1, d))

        # with a list of stop words
        r = Rules(['euh'])
        d = DataSpeaker(["tok1", "euh", "tok1", "euh"])
        self.assertTrue(r.apply_rules_one_token(0, d))
        self.assertFalse(r.apply_rules_one_token(1, d))

    def test_count_relevant_tokens(self):
        r = Rules(['euh'])
        d = DataSpeaker(["tok1", "euh", "tok1", "*"])
        self.assertEqual(r.count_relevant_tokens(0, 3, d), 2)

    def test_apply_rules_syntagme(self):
        r = Rules(['euh'])
        d = DataSpeaker(["tok1", "euh", "tok1", "*"])
        self.assertTrue(r.apply_rules_syntagme(0, 3, d))

    def test_apply_rules_strict(self):
        r = Rules(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok3", "euh", "ok"])
        d2 = DataSpeaker(["bla", "tok1", "tok2"])
        d3 = DataSpeaker(["bla", "tok1", "tok2", "tok3"])
        d4 = DataSpeaker(["tok1", "euh", "tok2", "tok3"])
        self.assertFalse(r.apply_rules_strict(0, 1, d1, d2))
        self.assertFalse(r.apply_rules_strict(0, 2, d1, d2))
        self.assertTrue(r.apply_rules_strict(0, 2, d1, d3))
        self.assertFalse(r.apply_rules_strict(0, 2, d1, d4))

# ---------------------------------------------------------------------------


class TestRepetitions(unittest.TestCase):

    def test_longest(self):
        r = Repetitions(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok1"])
        self.assertEqual(r.get_longest(0, d1), 0)   # tok1 is repeated
        self.assertEqual(r.get_longest(1, d1), -1)  # tok2 is not repeated
        d1 = DataSpeaker(["tok1", "tok2", "tok2"])
        self.assertEqual(r.get_longest(0, d1), -1)  # tok1 is repeated
        self.assertEqual(r.get_longest(1, d1), 1)   # tok2 is repeated
        d1 = DataSpeaker(["tok1", "tok2", "tok2", "tok2", "euh", "tok1", "euh"])
        self.assertEqual(r.get_longest(0, d1), 2)   # tok1 & tok2 & tok2 are repeated
        self.assertEqual(r.get_longest(1, d1), 2)   # tok2 & tok2 are repeated
        self.assertEqual(r.get_longest(2, d1), 2)   # tok2 is repeated
        self.assertEqual(r.get_longest(3, d1), -1)  # tok2 is not repeated
        self.assertEqual(r.get_longest(4, d1), 4)   # euh is repeated
        self.assertEqual(r.get_longest(5, d1), -1)  # tok1 is not repeated
        d1 = DataSpeaker(["tok1", "*", "tok2", "tok1"])
        self.assertEqual(r.get_longest(0, d1), 0)   # tok1 is repeated

    def test_select_self_repetition(self):
        r = Repetitions(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok1"])
        self.assertIsNone(r.get_source())
        self.assertEqual(r.select_self_repetition(0, 0, d1), 1)  # tok1 is stored
        self.assertEqual(r.get_source(), (0, 0))

        r = Repetitions(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok2", "tok2", "euh", "tok1", "euh"])
        n = r.get_longest(0, d1)  # n=2
        self.assertEqual(r.select_self_repetition(0, n, d1), 3)   # "tok1 tok2 tok2" is a source
        self.assertEqual(r.get_source(), (0, 2))
        n = r.get_longest(4, d1)  # n=4
        self.assertEqual(r.select_self_repetition(4, n, d1), 5)   # "euh" is not accepted as source
        self.assertEqual(r.get_source(), (0, 2))

        r = Repetitions(['euh'])
        d1 = DataSpeaker(["tok1", "euh", "euh", "euh", "tok2", "euh", "*", "tok1"])
        n = r.get_longest(0, d1)  # n=3
        self.assertEqual(r.select_self_repetition(0, n, d1), 4)  # "tok1 euh euh euh" is a source
        self.assertEqual(r.get_source(), (0, 3))

        r = Repetitions(['euh'])
        d1 = DataSpeaker(["tok1", "euh", "euh", "euh", "tok2", "euh"])
        n = r.get_longest(1, d1)  # n=3
        self.assertEqual(r.select_self_repetition(1, n, d1), 4)  # "euh euh euh" is not accepted as source
        self.assertIsNone(r.get_source())

    def test_select_other_repetition(self):
        r = Repetitions(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok2", "tok2", "blah", "tok1", "blah"])
        d2 = DataSpeaker(["tok1", "euh", "euh", "tok1", "tok2", "euh"])
        n = r.get_longest(1, d1, d2)
        self.assertEqual(r.select_other_repetition(0, n, d1, d2), 4)
        self.assertEqual(r.get_source(), (0, 3))

    def test_find_echos(self):
        pass
        # TODO

    def test_detect_sr(self):
        d = DataSpeaker(["tok1", "tok2", "tok2", "tok2", "euh", "tok1", "euh"])
        r = Repetitions(['euh'])
        r.detect(d)
        self.assertEqual(r.get_source(), (0, 2))
        self.assertEqual(len(r.get_echos()), 2)
        self.assertTrue((3, 3) in r.get_echos())
        self.assertTrue((5, 5) in r.get_echos())

        d = DataSpeaker(["sur", "la", "bouffe", "#", "après", "etc", "la", "etc", "#", "etc", "bouffe", "etc"])
        r = Repetitions(STOP_LIST)
        r.detect(d, limit=3)
        self.assertEqual(r.get_source(), (1, 2))

    def test_detect_or(self):

        r = Repetitions(STOP_LIST)
        s_AB = "le petit feu de artifice ouais ce être le tout petit truc là"
        s_CM = "le feu # ah le petit machin de ouais ouais ouais ouais ouais d'accord ouais + ouais ouais ouais ouais + hum hum ouais hum hum @@ # ouais # ouais ouais ouais ouais + hum # ouais oui oui ce être pas le le ouais ah ouais ouais @@"
        d_AB = DataSpeaker(s_AB.split())
        d_CM = DataSpeaker(s_CM.split())
        r.detect(d_AB, 15, d_CM)
        self.assertEqual(r.get_source(), (0, 3))
        self.assertTrue((4, 5) in r.get_echos())  # le petit
        self.assertTrue((1, 1) in r.get_echos())  # feu
        self.assertTrue((7, 7) in r.get_echos())  # de

        s_AB = "ils voulaient qu'on fasse un feu d'artifice en_fait dans un voy- un foyer un foyer catho un foyer de bonnes soeurs"
        s_CM = "un feu d'artifice # dans un foyer de bonnes soeurs"
        d_AB = DataSpeaker(s_AB.split())
        d_CM = DataSpeaker(s_CM.split())
        r.detect(d_AB, 10, d_CM)
        self.assertEqual(r.get_source(), (4, 6))

        s_AB = "en_fait dans un voy- un foyer un foyer catho un foyer de bonnes soeurs"
        s_CM = "un feu d'artifice # dans un foyer de bonnes soeurs"
        d_AB = DataSpeaker(s_AB.split())
        d_CM = DataSpeaker(s_CM.split())
        r.detect(d_AB, 10, d_CM)
        self.assertEqual(r.get_source(), (4, 7))
        self.assertEqual(len(r.get_echos()), 1)
        self.assertTrue((5, 6) in r.get_echos())  # un foyer

        s_AB = "catho un foyer de bonnes soeurs"
        s_CM = "un feu d'artifice # dans un foyer de bonnes soeurs"
        d_AB = DataSpeaker(s_AB.split())
        d_CM = DataSpeaker(s_CM.split())
        r.detect(d_AB, 10, d_CM)
        self.assertEqual(r.get_source(), (1, 5))
        self.assertEqual(len(r.get_echos()), 1)
        self.assertTrue((5, 9) in r.get_echos())  # un foyer

# ---------------------------------------------------------------------------


class TestsppasRepet(unittest.TestCase):

    def test_init(self):
        s = sppasRepet()
        self.assertEqual(s.stop_words.get_size(), 0)
        self.assertEqual(s.lemmatizer.get_size(), 0)
        s = sppasRepet(STOP_LIST_FRA)
        self.assertEqual(s.stop_words.get_size(), 65)
        self.assertGreater(s.lemmatizer.get_size(), 0)

    def test_set_options(self):
        s = sppasRepet()
        with self.assertRaises(ValueError):
            s.set_span(0)
        with self.assertRaises(ValueError):
            s.set_span(30)
        with self.assertRaises(ValueError):
            s.set_alpha(-2)
        with self.assertRaises(ValueError):
            s.set_alpha(10)
