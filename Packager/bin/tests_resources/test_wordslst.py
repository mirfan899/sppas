#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from resources.wordslst import WordsList
from sp_glob import RESOURCES_PATH

VOCAB  = join(dirname(abspath(__file__)), "vocab.txt")
VOCAB2 = join(dirname(abspath(__file__)), "vocab2.txt")
ITA = os.path.join(RESOURCES_PATH, "vocab", "ita.vocab")

class TestWordsList(unittest.TestCase):

    def test_all(self):
        l = WordsList( VOCAB )
        self.assertEqual(l.get_size(), 20 )
        self.assertTrue( l.is_unk('toto') )
        self.assertFalse( l.is_unk('normale') )
        self.assertFalse( l.is_unk("isn't") )
        self.assertFalse( l.is_unk(u"đ") )
        l.add(u"être")
        self.assertTrue( l.is_in(u"être") )
        self.assertTrue( l.is_unk("être") )

    def test_save(self):
        l = WordsList( VOCAB )
        l.save( VOCAB2 )
        l2 = WordsList( VOCAB2 )
        self.assertEqual(l.get_size(), l2.get_size())
        for w in l.get_list():
            self.assertTrue(l2.is_in(w))

    def test_ita(self):
        l = WordsList( ITA )
        self.assertTrue( l.is_unk('toto') )
        self.assertFalse( l.is_unk(u'perché') )


# End TestWordsList
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWordsList)
    unittest.TextTestRunner(verbosity=2).run(suite)

