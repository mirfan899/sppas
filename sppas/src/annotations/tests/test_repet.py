# -*- coding:utf-8 -*-

import unittest

from ..Repet.datastructs import DataRepetition, DataSpeaker

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

    def test_is_token(self):
        d = DataSpeaker([])
        self.assertTrue(d.is_token('token'))
        self.assertFalse(d.is_token('euh'))
        self.assertFalse(d.is_token('    euh '))
        self.assertFalse(d.is_token(' * '))

    def test_get_next_token(self):
        d = DataSpeaker(["tok1", "tok2"])
        self.assertEqual(d.get_next_token(0), 1)
        self.assertEqual(d.get_next_token(1), -1)
        d = DataSpeaker(["tok1", "euh", "tok2"])
        self.assertEqual(d.get_next_token(0), 2)
        self.assertEqual(d.get_next_token(1), 2)
        with self.assertRaises(ValueError):
            d.get_next_token(-1)
        with self.assertRaises(ValueError):
            d.get_next_token(3)

