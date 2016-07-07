#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os

from resources.wordslst import WordsList
from sp_glob import RESOURCES_PATH
from paths import TEMP

# ---------------------------------------------------------------------------

VOCAB  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vocab.txt")
ITA = os.path.join(RESOURCES_PATH, "vocab", "ita.vocab")

VOCAB_TEST = os.path.join(TEMP, "vocab.txt")

# ---------------------------------------------------------------------------

class TestWordsList(unittest.TestCase):

    def test_all(self):
        l = WordsList( VOCAB, nodump=True )
        self.assertEqual(l.get_size(), 20 )
        self.assertTrue( l.is_unk('toto') )
        self.assertFalse( l.is_unk('normale') )
        self.assertFalse( l.is_unk("isn't") )
        self.assertFalse( l.is_unk(u"đ") )
        l.add(u"être")
        self.assertTrue( l.is_in(u"être") )
        self.assertTrue( l.is_unk("être") )

    def test_save(self):
        l = WordsList( VOCAB, nodump=True )
        l.save( VOCAB_TEST )
        l2 = WordsList( VOCAB_TEST, nodump=True )
        self.assertEqual(l.get_size(), l2.get_size())
        for w in l.get_list():
            self.assertTrue(l2.is_in(w))

    def test_ita(self):
        l = WordsList( ITA, nodump=True )
        self.assertTrue( l.is_unk('toto') )
        self.assertFalse( l.is_unk(u'perché') )

# ---------------------------------------------------------------------------
