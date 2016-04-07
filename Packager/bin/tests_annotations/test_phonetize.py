#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotations.Phon.phonetize import DictPhon
from annotations.Phon.dagphon   import DAGPhon

from resources.dictpron import DictPron

from sp_glob import RESOURCES_PATH
from sp_glob import UNKSTAMP

from sp_glob import ERROR_ID, WARNING_ID, OK_ID

# ---------------------------------------------------------------------------

class TestPhonetize(unittest.TestCase):

    def setUp(self):
        self.dd   = DictPron()
        self.grph = DictPhon(self.dd)
        self.dd.add_pron("a","a")
        self.dd.add_pron("b","b")
        self.dd.add_pron("c","c")
        self.dd.add_pron("+","sp")

    def test_get_phon_entry(self):
        self.assertEqual(self.grph.get_phon_entry("<>"), "")
        self.assertEqual(self.grph.get_phon_entry("<a>"), "a")
        self.assertEqual(self.grph.get_phon_entry("gpd_1"), "")
        self.assertEqual(self.grph.get_phon_entry("gpf_1"), "")
        self.assertEqual(self.grph.get_phon_entry("ipu_1"), "")
        self.assertEqual(self.grph.get_phon_entry("ipu"), UNKSTAMP)
        self.assertEqual(self.grph.get_phon_entry("gpd"), UNKSTAMP)
        self.assertEqual(self.grph.get_phon_entry("gpf"), UNKSTAMP)

        self.assertEqual(self.grph.get_phon_entry("a"), "a")
        self.assertEqual(self.grph.get_phon_entry("a-b"), "a.b")
        self.assertEqual(self.grph.get_phon_entry("a_b"), "a.b")
        self.assertEqual(self.grph.get_phon_entry("a'b"), "a.b")
        self.assertEqual(self.grph.get_phon_entry("a'd"), UNKSTAMP)

    def test_get_phon_tokens(self):
        self.assertEqual(self.grph.get_phon_tokens([' \n \t']), [(' \n \t', '', OK_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a']), [('a','a',OK_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a','b']), [('a','a',OK_ID),('b','b',OK_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a-a','b']), [('a-a','a.a',OK_ID),('b','b',OK_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['A','B']), [('A','a',OK_ID),('B','b',OK_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a','aa']), [('a','a',OK_ID),('aa','a.a',WARNING_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a','aa'], phonunk=False), [('a','a',OK_ID),('aa',UNKSTAMP,ERROR_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a','d']), [('a','a',OK_ID),('d',UNKSTAMP,ERROR_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['/a/','d']), [('/a/','a',OK_ID),('d',UNKSTAMP,ERROR_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['/A.a/','d']), [('/A.a/','A.a',OK_ID),('d',UNKSTAMP,ERROR_ID)])

    def test_phonetize(self):
        with self.assertRaises(TypeError):
            self.grph.phonetize('A',delimiter="_-")
        self.assertEqual( self.grph.phonetize(' \n \t'), "" )
        self.assertEqual( self.grph.phonetize('a'), "a" )
        self.assertEqual( self.grph.phonetize('a b a c'), "a b a c" )
        self.assertEqual( self.grph.phonetize('a b a c d'), "a b a c "+UNKSTAMP )
        self.assertEqual( self.grph.phonetize('a + a'), "a sp a" )
        self.assertEqual( self.grph.phonetize('A B C'), "a b c" )
        self.assertEqual( self.grph.phonetize('A_B_C',delimiter="_"), "a_b_c" )
        self.assertEqual( self.grph.phonetize("a'b-a c"), "a.b.a c" )
        self.assertEqual( self.grph.phonetize("ipu_4 a'b-a c"), "a.b.a c" )
        self.assertEqual( self.grph.phonetize("gpd_4 a'b-a + c"), "a.b.a sp c" )
        self.assertEqual( self.grph.phonetize("gpd_4 aa'b-a"), "a.a.b.a" )

# ---------------------------------------------------------------------------

class TestDAGPhon(unittest.TestCase):

    def setUp(self):
        self.dd = DAGPhon()

    def test_decompose(self):
        self.assertEqual(self.dd.decompose("a","b"), "a|b")
        self.assertEqual(self.dd.decompose("a|A b"), "a.b|A.b")
        self.assertEqual(self.dd.decompose("a|A","b|B"), "a|A|B|b")
        self.assertEqual(self.dd.decompose("p1 p2|x2 p3|x3"), "p1.p2.p3|p1.p2.x3|p1.x2.x3|p1.x2.p3")
        self.assertEqual(self.dd.decompose("p1 p2 p3", "x1 x2 x3"), 'p1.p2.p3|x1.x2.x3')
        self.assertEqual(self.dd.decompose("p1 p2|x2 p3", "x1 x2 x3"), 'p1.p2.p3|p1.x2.p3|x1.x2.x3')

# ---------------------------------------------------------------------------

if __name__ == '__main__':

    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(TestPhonetize))
    testsuite.addTest(unittest.makeSuite(TestDAGPhon))
    unittest.TextTestRunner(verbosity=2).run(testsuite)
