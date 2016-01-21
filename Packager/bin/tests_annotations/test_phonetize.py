#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotations.Phon.phonetize import DictPhon
from resources.dictpron import DictPron
from sp_glob import RESOURCES_PATH

DICT_FRA = os.path.join(RESOURCES_PATH, "dict", "fra.dict")

# ---------------------------------------------------------------------------
class TestPhonetize(unittest.TestCase):

    def test_phon(self):

        dd = DictPron( DICT_FRA )

        grph = DictPhon(dd)
        result = grph.phonetize('pas_de', phonunk=False)
        self.assertEqual(result, u'UNK')

        result = grph.phonetize('pas_de', phonunk=True)
        self.assertEqual(result, "p.a.t|p.a.d|p.a.z.t|p.a.z.d")

        result = grph.phonetize(u'/lemot/', phonunk=True)
        self.assertEqual(result, u"lemot")
        result = grph.phonetize(u'/lemot/', phonunk=False)
        self.assertEqual(result, u"lemot")

# End TestPhonetize
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhonetize)
    unittest.TextTestRunner(verbosity=2).run(suite)
