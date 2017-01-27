# -*- coding:utf-8 -*-

import unittest
import os.path

from ..Phon.phonetize import DictPhon
from ..Phon.dagphon import DAGPhon
from ..Phon.phonunk import PhonUnk
from ..Phon.sppasphon import sppasPhon

from sppas.src.resources.dictpron import DictPron
from sppas.src.resources.mapping import Mapping

from sppas.src.sp_glob import RESOURCES_PATH
from sppas.src.sp_glob import UNKSTAMP
from sppas.src.sp_glob import ERROR_ID, WARNING_ID, OK_ID

# ---------------------------------------------------------------------------


class TestDictPhon( unittest.TestCase ):

    def setUp(self):
        self.dd = DictPron()
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
        self.assertEqual(self.grph.get_phon_entry("aa"), UNKSTAMP)
        self.assertEqual(self.grph.get_phon_entry("a-a"), UNKSTAMP)

    def test_get_phon_tokens(self):
        self.assertEqual(self.grph.get_phon_tokens([' \n \t']), [(' \n \t', '', OK_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a']), [('a','a',OK_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a','b']), [('a','a',OK_ID),('b','b',OK_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a-a','b']), [('a-a','a-a',WARNING_ID),('b','b',OK_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a-']), [('a-','a',WARNING_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['A','B']), [('A','a',OK_ID),('B','b',OK_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a','aa']), [('a','a',OK_ID),('aa','a-a',WARNING_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a','aa'], phonunk=False), [('a','a',OK_ID),('aa',UNKSTAMP,ERROR_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['a','d']), [('a','a',OK_ID),('d',UNKSTAMP,ERROR_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['/a/','d']), [('/a/','a',OK_ID),('d',UNKSTAMP,ERROR_ID)])
        self.assertEqual(self.grph.get_phon_tokens(['/A-a/','d']), [('/A-a/','A-a',OK_ID),('d',UNKSTAMP,ERROR_ID)])

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
        self.assertEqual( self.grph.phonetize("a'b-a c"), "a-b-a c" )
        self.assertEqual( self.grph.phonetize("ipu_4 a'b-a c"), "a-b-a c" )
        self.assertEqual( self.grph.phonetize("gpd_4 a'b-a + c"), "a-b-a sp c" )
        self.assertEqual( self.grph.phonetize("gpd_4 aa'b-a"), "a-a-b-a" )

    def test_map_entry(self):
        mapt = Mapping()
        mapt.add('a','A')
        mapt.add('b','B')
        mapt.add('b','v')
        mapt.add('a-c','a-C')
        self.grph.set_maptable( mapt )
        self.assertEqual(self.grph._map_phonentry("c"), "c")
        self.assertEqual(self.grph._map_phonentry("a"), "a|A")
        self.assertEqual(self.grph._map_phonentry("b"), "B|b|v")
        self.assertEqual(self.grph._map_phonentry("c.c"), 'c.c')
        result = 'a-b|a-B|A-b|A-B|A-v|a-v'
        self.assertEqual(set(self.grph._map_phonentry("a-b").split("|")), set(result.split("|")))
        result = "a-c|a-C"
        self.assertEqual(set(self.grph._map_phonentry("a-c").split("|")), set(result.split("|")))
        result = "a-c-A|a-c-a|a-C-A|a-C-a"
        self.assertEqual(set(self.grph._map_phonentry("a-c-a").split("|")), set(result.split("|")))
        result = "c-a-c|c-a-C"
        self.assertEqual(set(self.grph._map_phonentry("c-a-c").split("|")), set(result.split("|")))
        mapt.add('a','a')
        mapt.add('b','b')
        mapt.add('c','c')
        self.assertEqual(self.grph._map_phonentry("c"), "c")
        self.assertEqual(self.grph._map_phonentry("a"), "a|A")
        self.assertEqual(self.grph._map_phonentry("b"), "B|b|v")
        self.grph.set_maptable( None )

    def test_data(self):
        dictfile  = os.path.join(RESOURCES_PATH, "dict", "eng.dict")
        map_table = os.path.join(RESOURCES_PATH, "dict", "eng-fra.map")
        mapt = Mapping( map_table )
        dd   = DictPron(dictfile)
        grph = DictPhon(dd)
        self.assertEqual(grph.get_phon_entry("THE"), "D-@|D-V|D-i:")
        self.assertEqual(grph.get_phon_entry("UR"), "3:r|U-r")
        self.assertEqual(grph.get_phon_entry("ARE"), "A-r|3:r")
        self.assertEqual(grph.get_phon_entry("BANC"), "b-{-N-k")

        grph.set_maptable( mapt )
        the = "z-@|D-@|v-@|v-V|D-V|z-V|z-9|D-9|v-9|z-i:|z-i|D-i|v-i|D-i:|v-i:"
        ur = "3:r|9-R|u-r|U-w|u-w|U-R|U-r|u-R"
        are = "a-R|A-R|a-w|A-w|a-r|A-r|3:r|9-R"
        self.assertEqual(set(grph.get_phon_entry("THE").split("|")), set(the.split("|")))
        self.assertEqual(set(grph.get_phon_entry("UR").split("|")), set(ur.split("|")))
        self.assertEqual(set(grph.get_phon_entry("ARE").split("|")), set(are.split("|")))

# ---------------------------------------------------------------------------


class TestDAGPhon(unittest.TestCase):

    def setUp(self):
        self.dd = DAGPhon()

    def test_decompose(self):
        self.assertEqual(self.dd.decompose("a","b"), "a|b")
        self.assertEqual(self.dd.decompose("a|A b"), "a-b|A-b")
        self.assertEqual(self.dd.decompose("a|A","b|B"), "a|A|B|b")

        result = "p1-p2-x3|p1-x2-x3|p1-p2-p3|p1-x2-p3"
        self.assertEqual(set(self.dd.decompose("p1 p2|x2 p3|x3").split("|")), set(result.split("|")))

        result = 'p1-p2-p3|x1-x2-x3'
        self.assertEqual(set(self.dd.decompose("p1 p2 p3", "x1 x2 x3").split("|")), set(result.split("|")))

        result = 'p1-p2-p3|p1-x2-p3|x1-x2-x3'
        self.assertEqual(set(self.dd.decompose("p1 p2|x2 p3", "x1 x2 x3").split("|")), set(result.split("|")))

# ---------------------------------------------------------------------------


class TestSppasPhon(unittest.TestCase):

    def setUp(self):
        dictfile = os.path.join(RESOURCES_PATH, "dict", "eng.dict")
        mapfile  = os.path.join(RESOURCES_PATH, "dict", "eng-fra.map")
        self.sp  = sppasPhon( dictfile )
        self.spl = sppasPhon( dictfile, mapfile )

    def test_phonetize(self):
        self.sp.set_unk(True)
        self.assertEqual(self.sp.phonetize("THE"), "D-@|D-V|D-i:")
        self.assertEqual(self.sp.phonetize("HE"),  "h-i:")
        self.assertEqual(self.sp.phonetize("THE BANC"), "D-@|D-V|D-i: b-{-N-k")
        self.assertEqual(self.sp.phonetize("THE BANCI THE"), "D-@|D-V|D-i: b-{-N-k-aI D-@|D-V|D-i:")
        self.assertEqual(self.sp.phonetize("#"), "sil")
        self.assertEqual(self.sp.phonetize("+"), "sil")
        self.assertEqual(self.sp.phonetize("é à"), UNKSTAMP)
        self.sp.set_unk(False) # do not try to phonetize if missing of the dict
        self.assertEqual(self.sp.phonetize("THE BANCI THE"), UNKSTAMP)

    def test_phonetize_learners(self):
        self.sp.set_unk(True)
        self.assertEqual(self.spl.phonetize("THE"), "D-@|z-@|v-@|z-9|D-V|v-9|v-V|D-9|z-V|D-i:|z-i|v-i|D-i|v-i:|z-i:")
        result = "i|h-i:|h-i|i:"
        self.assertEqual(set(self.spl.phonetize("HE").split("|")), set(result.split("|")))

# ---------------------------------------------------------------------------


class TestPhonUnk(unittest.TestCase):

    def setUp(self):
        d = { 'a':'a|aa', 'b':'b', 'c':'c|cc', 'abb':'abb', 'bac':'bac' }
        self.p = PhonUnk(d)

    def test_phon(self):
        self.assertEqual(self.p.get_phon('abba'), "abb-a|abb-aa")
        self.assertEqual(self.p.get_phon('abba-'), "abb-a|abb-aa")
        self.assertEqual(self.p.get_phon("abba'"), "abb-a|abb-aa")
        self.assertEqual(self.p.get_phon("<abba>"), "abb-a|abb-aa")
        self.assertEqual(self.p.get_phon("<>"), "")
        self.assertEqual(self.p.get_phon("abb-a"), "abb-a|abb-aa")

        self.assertEqual(self.p.get_phon('abc'), 'a-b-c|a-b-cc|aa-b-c|aa-b-cc')
        self.assertEqual(self.p.get_phon('abd'), 'a-b|aa-b')
