# -*- coding: utf8 -*-

import unittest
import os.path

from sppas import RESOURCES_PATH
from sppas import SAMPLES_PATH

from ..Align.aligners import instantiate as aligners_instantiate
from ..Align.aligners import check as aligners_check
from ..Align.aligners import aligner_names
from ..Align.aligners.basealigner import BaseAligner
from ..Align.aligners.basicalign import BasicAligner
from ..Align.aligners.juliusalign import JuliusAligner
from ..Align.aligners.hvitealign import HviteAligner

# ---------------------------------------------------------------------------

MODELDIR = os.path.join(RESOURCES_PATH, "models")
sample_1 = os.path.join(SAMPLES_PATH, "samples-eng", "oriana1.wav")  # mono; 16000Hz; 16bits

# ---------------------------------------------------------------------------


class TestBaseAligner( unittest.TestCase ):

    def setUp(self):
        self._aligner = BaseAligner( None )

    def test_outext(self):
        self.assertEqual( self._aligner.get_outext(),"" )
        with self.assertRaises(NotImplementedError):
            self._aligner.set_outext( "palign" )

    def test_infersp(self):
        self.assertFalse( self._aligner.get_infersp() )
        self._aligner.set_infersp( True )
        self.assertTrue( self._aligner.get_infersp() )
        self._aligner.set_infersp( "ejzkjreg" )
        self.assertFalse( self._aligner.get_infersp() )

    def test_options(self):
        self.assertFalse( self._aligner.get_infersp())
        self._aligner.set_infersp(True)
        self.assertTrue( self._aligner.get_infersp())
        self._aligner.set_infersp(False)
        self.assertFalse( self._aligner.get_infersp())
        with self.assertRaises(NotImplementedError):
            self._aligner.run_alignment( "audio", "output")

# ---------------------------------------------------------------------------


class TestBasicAlign( unittest.TestCase ):

    def setUp(self):
        self._aligner = BasicAligner( None )

    def test_run_basic(self):

        self._aligner.set_phones("")
        a = self._aligner.run_basic( 0. )
        self.assertEquals(a, [(0, 0, "")] )

        a = self._aligner.run_basic( 0.01 )
        self.assertEquals(a, [(0, 1, "")] )

        a = self._aligner.run_basic( 0.02 )
        self.assertEquals(a, [(0, 2, "")] )

        a = self._aligner.run_basic( 0.2 )
        self.assertEquals(a, [(0, 20, "")] )

        a = self._aligner.run_basic( 10. )
        self.assertEquals(a, [(0, 1000, "")] )

        self._aligner.set_phones("a")
        a = self._aligner.run_basic( 0. )
        self.assertEquals(a, [(0, 0, "")] )

        a = self._aligner.run_basic( 0.02 )
        self.assertEquals(a, [(0, 1, "a")] )

        a = self._aligner.run_basic( 0.02 )
        self.assertEquals(a, [(0, 1, "a")] )

        self._aligner.set_phones("a b c")
        a = self._aligner.run_basic( 0.02 )
        self.assertEquals(a, [(0, 2, "")] )

        self._aligner.set_phones("a b")
        a = self._aligner.run_basic( 0.2 )
        self.assertEquals(a, [(0, 9, "a"),(10, 19, "b")] )

        self._aligner.set_phones("a|aa b|bb")
        a = self._aligner.run_basic( 0.2 )
        self.assertEquals(a, [(0, 9, "a"),(10, 19, "b")] )

        self._aligner.set_phones("a|A b|B")
        a = self._aligner.run_basic( 0.2 )
        self.assertEquals(a, [(0, 9, "a"),(10, 19, "b")] )

# ---------------------------------------------------------------------------


class TestJuliusAlign( unittest.TestCase ):

    def setUp(self):
        self._modeldir = os.path.join(MODELDIR, "models-fra")
        self._aligner = JuliusAligner( self._modeldir )

# ---------------------------------------------------------------------------


class TestHviteAlign( unittest.TestCase ):

    def setUp(self):
        self._modeldir = os.path.join(MODELDIR, "models-fra")
        self._aligner = HviteAligner( self._modeldir )

# ---------------------------------------------------------------------------


class TestAlignersPackage(unittest.TestCase):

    def test_check(self):
        for a in aligner_names():
            self.assertEqual(aligners_check(a), a)
        with self.assertRaises(ValueError):
            aligners_check("invalid")

    def test_instantiate(self):
        aligner = aligners_instantiate(None,"basic")
        self.assertTrue(isinstance(aligner, BasicAligner))

# ---------------------------------------------------------------------------
