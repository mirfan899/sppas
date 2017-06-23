#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
import getopt
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas'))

from annotations.Repeats.dictlem import LemmaDict

class TestLemmaDict(unittest.TestCase):

    def test_lemmadict(self):
        dictdir  = os.path.join(SPPAS, "vocab")
        dictfile = os.path.join(dictdir, "FR.lem")
        grph = LemmaDict( dictfile )
        self.assertEqual(u"salut il faire un essai plus bref ça marche",
                         grph.lemmatize(u"Salut je fais UN essai plus Bref ça marche"))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLemmaDict))
    return suite

if __name__ == '__main__':
    unittest.main()
