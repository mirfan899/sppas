#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
import getopt
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas'))

from annotations.Phon.phonetize import DictPhon
from resources.dictpron import DictPron

class TestDictPhon(unittest.TestCase):

    def test_phonetizeFR(self):
        dictdir  = os.path.join(SPPAS, "resources", "dict")
        dictfile = os.path.join(dictdir, "fra.dict")
        dd = DictPron(dictfile)
        grph = DictPhon(dd)
        result = grph.phonetize('pas_encore', phonunk=False)
        self.assertEqual(result, 'UNK')

        result = grph.phonetize('pas_encore', phonunk=True)
        self.assertEqual(result,
                         "p.a.a~.k.o.r|p.a.z.a~.k.o.r|p.a.a~.k.o.r.eu|p.a.z.a~.k.o.r.eu")

        result = grph.phonetize(u'/lemot/', phonunk=True)
        self.assertEqual(result, u"lemot")
        result = grph.phonetize(u'/lemot/', phonunk=False)
        self.assertEqual(result, u"lemot")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDictPhon))
    return suite

if __name__ == '__main__':
    unittest.main()
