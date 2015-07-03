#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from resources.dictpron import DictPron
import resources.rutils as rutils
from sp_glob import RESOURCES_PATH

DICT_FRA = os.path.join(RESOURCES_PATH, "dict", "fra.dict")

# ---------------------------------------------------------------------------
class TestDictPron(unittest.TestCase):

    def test_dict(self):
        d = DictPron( DICT_FRA )
        self.assertTrue( d.is_unk('azerty') )
        self.assertFalse( d.is_unk('il_y_a') )
        self.assertFalse( d.is_unk(u'être') )
        self.assertEqual( d.get_pron(u'sil'), "s.i.l" )
        self.assertEqual( d.get_pron(u'azerty'), "UNK" )

    def test_save(self):
        d = DictPron( DICT_FRA )
        d.save_as_ascii( DICT_FRA+".copy" )
        d2 = DictPron( DICT_FRA+".copy", nodump=True )
        for w in d.get_keys():
            self.assertEqual( d.get_pron(w), d2.get_pron(w) )
        os.remove( DICT_FRA+".copy" )

# End TestDictPron
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDictPron)
    unittest.TextTestRunner(verbosity=2).run(suite)

