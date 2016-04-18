#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import dirname,abspath

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from sp_glob import RESOURCES_PATH
from sp_glob import SAMPLES_PATH

from resources.mapping  import Mapping

from annotations.Align.basealigner    import BaseAligner
from annotations.Align.basicalign     import BasicAligner
from annotations.Align.juliusalign    import JuliusAligner
from annotations.Align.hvitealign     import HviteAligner

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
        self._model   = os.path.join(MODELDIR, "models-fra")
        self._mapping = Mapping(os.path.join(self._model, "monophones.repl"))
        self._aligner = JuliusAligner( self._model, self._mapping )

# ---------------------------------------------------------------------------

class TestHviteAlign( unittest.TestCase ):

    def setUp(self):
        self._model   = os.path.join(MODELDIR, "models-fra")
        self._mapping = Mapping(os.path.join(self._model, "monophones.repl"))
        self._aligner = HviteAligner( self._model, self._mapping )

# ---------------------------------------------------------------------------

if __name__ == '__main__':

    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(TestBaseAligner))
    testsuite.addTest(unittest.makeSuite(TestBasicAlign))
    testsuite.addTest(unittest.makeSuite(TestJuliusAlign))
    testsuite.addTest(unittest.makeSuite(TestHviteAlign))

    unittest.TextTestRunner(verbosity=2).run(testsuite)
