#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
import shutil
from os.path import dirname,abspath

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from utils.type import compare

from sp_glob import RESOURCES_PATH
from sp_glob import SAMPLES_PATH

from resources.mapping     import Mapping
from resources.acm.acmodel import AcModel
from resources.acm.hmm     import HMM

from annotations.Align.basealigner    import BaseAligner
from annotations.Align.basicalign     import BasicAligner
from annotations.Align.juliusalign    import JuliusAligner
from annotations.Align.hvitealign     import HviteAligner
from annotations.Align.modelmixer     import ModelMixer

MODELDIR = os.path.join(RESOURCES_PATH, "models")

# ---------------------------------------------------------------------------

class TestBaseAligner( unittest.TestCase ):

    def setUp(self):
        self._aligner = BaseAligner( None, None )

    def test_init(self):
        with self.assertRaises(TypeError):
            BaseAligner( None, "mapping_as_str")
        BaseAligner( None )

    def test_others(self):
        self.assertFalse(self._aligner.get_infersp())
        self._aligner.set_infersp(True)
        self.assertTrue(self._aligner.get_infersp())
        self._aligner.set_infersp(False)
        self.assertFalse(self._aligner.get_infersp())
        with self.assertRaises(NotImplementedError):
            self._aligner.run_alignment( "audio", "dependencies", "output")

# ---------------------------------------------------------------------------

class TestBasicAlign( unittest.TestCase ):

    def setUp(self):
        self._aligner = BasicAligner( None, None )

    def test_init(self):
        with self.assertRaises(TypeError):
            BasicAligner( None, "mapping_as_str")
        BasicAligner( None )

    def test_run_basic(self):

        a = self._aligner.run_basic( 0., "" )
        self.assertEquals(a, [(0, 0, "")] )

        a = self._aligner.run_basic( 0.01, "" )
        self.assertEquals(a, [(0, 1, "")] )

        a = self._aligner.run_basic( 0.02, "" )
        self.assertEquals(a, [(0, 2, "")] )

        a = self._aligner.run_basic( 0.2, "" )
        self.assertEquals(a, [(0, 20, "")] )

        a = self._aligner.run_basic( 10., "" )
        self.assertEquals(a, [(0, 1000, "")] )

        a = self._aligner.run_basic( 0., "a" )
        self.assertEquals(a, [(0, 0, "")] )

        a = self._aligner.run_basic( 0.02, "a" )
        self.assertEquals(a, [(0, 1, "a")] )

        a = self._aligner.run_basic( 0.02, "a" )
        self.assertEquals(a, [(0, 1, "a")] )

        a = self._aligner.run_basic( 0.02, "a b c" )
        self.assertEquals(a, [(0, 2, "")] )

        a = self._aligner.run_basic( 0.2, "a b" )
        self.assertEquals(a, [(0, 9, "a"),(10, 19, "b")] )

        a = self._aligner.run_basic( 0.2, "a|aa b|bb" )
        self.assertEquals(a, [(0, 9, "a"),(10, 19, "b")] )

        a = self._aligner.run_basic( 0.2, "a|A b|B" )
        self.assertEquals(a, [(0, 9, "a"),(10, 19, "b")] )

# ---------------------------------------------------------------------------

class TestJuliusAlign( unittest.TestCase ):

    def setUp(self):
        self._modeldir = os.path.join(MODELDIR, "models-fra")
        self._mapping  = Mapping(os.path.join(self._modeldir, "monophones.repl"))
        self._aligner  = JuliusAligner( self._modeldir, self._mapping )

# ---------------------------------------------------------------------------

class TestHviteAlign( unittest.TestCase ):

    def setUp(self):
        self._modeldir = os.path.join(MODELDIR, "models-fra")
        self._mapping  = Mapping(os.path.join(self._modeldir, "monophones.repl"))
        self._aligner  = HviteAligner( self._modeldir, self._mapping )

# ---------------------------------------------------------------------------

class TestModelMixer( unittest.TestCase ):

    def setUp(self):
        # a French speaker reading an English text...
        self._modelL2dir = os.path.join(MODELDIR, "models-eng")
        self._modelL1dir = os.path.join(MODELDIR, "models-fra")

    def testMix(self):
        acmodel1 = AcModel()
        hmm1 = HMM()
        hmm1.create_proto( 25 )
        hmm1.name = "y"
        acmodel1.append_hmm( hmm1 )
        acmodel1.repllist.add("y","j")

        acmodel2 = AcModel()
        hmm2 = HMM()
        hmm2.create_proto( 25 )
        hmm2.name = "j"
        hmm3 = HMM()
        hmm3.create_proto( 25 )
        hmm3.name = "y"
        acmodel2.hmms.append( hmm2 )
        acmodel2.hmms.append( hmm3 )
        acmodel2.repllist.add("y","y")
        acmodel2.repllist.add("j","j")

        modelmixer = ModelMixer()
        modelmixer.set_models( acmodel1,acmodel2 )

        outputdir = os.path.join(MODELDIR, "models-test")
        (appended,interpolated,keeped,changed) = modelmixer.mix( outputdir, gamma=1. )
        mixedh1 = AcModel()
        mixedh1.load( outputdir )
        shutil.rmtree( outputdir )

    def testMixData(self):
        modelmixer = ModelMixer()
        modelmixer.load(self._modelL2dir, self._modelL1dir )
        outputdir = os.path.join(MODELDIR, "models-eng-fra")
        modelmixer.mix( outputdir, gamma=0.5 )
        self.assertTrue( os.path.exists( outputdir ) )
        acmodel1 = AcModel()
        acmodel1.load_htk( os.path.join(self._modelL2dir, "hmmdefs") )
        acmodel1 = acmodel1.extract_monophones()
        acmodel2 = AcModel()
        acmodel2.load_htk( os.path.join(os.path.join(MODELDIR, "models-eng-fra"), "hmmdefs") )
#         shutil.rmtree( outputdir )

# ---------------------------------------------------------------------------

if __name__ == '__main__':

    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(TestBaseAligner))
    testsuite.addTest(unittest.makeSuite(TestBasicAlign))
    testsuite.addTest(unittest.makeSuite(TestJuliusAlign))
    testsuite.addTest(unittest.makeSuite(TestHviteAlign))
    testsuite.addTest(unittest.makeSuite(TestModelMixer))

    unittest.TextTestRunner(verbosity=2).run(testsuite)
