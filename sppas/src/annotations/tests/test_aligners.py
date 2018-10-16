# -*- coding: utf8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.annotations.tests.test_aligners.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os

from sppas.src.config import paths

from ..Align.aligners import sppasAligners
from ..Align.aligners.basealigner import BaseAligner
from ..Align.aligners.basicalign import BasicAligner
from ..Align.aligners.juliusalign import JuliusAligner
from ..Align.aligners.hvitealign import HviteAligner
from ..Align.aligners.alignerio import BaseAlignersReader
from ..Align.aligners.alignerio import palign, walign, mlf

# ---------------------------------------------------------------------------

MODELDIR = os.path.join(paths.resources, "models")
sample_1 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")  # mono; 16000Hz; 16bits
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestAlignersIO(unittest.TestCase):
    """Readers/writer of the output files of the aligners."""

    def test_BaseAlignersReader(self):
        b = BaseAlignersReader()
        self.assertEqual('', b.extension)
        with self.assertRaises(NotImplementedError):
            b.read('toto')

    def test_getlines(self):
        b = BaseAlignersReader()
        lines = b.get_lines(os.path.join(DATA, "track_000002.palign"))
        self.assertEqual(311, len(lines))

    def test_get_time_units_palign(self):
        b = BaseAlignersReader()
        lines = b.get_lines(os.path.join(DATA, "track_000002.palign"))
        expected_units = [(0, 2), (3, 5), (6, 15), (16, 22), (23, 31),\
                          (32, 34), (35, 37), (38, 40), (41, 60), (61, 63),\
                          (64, 69), (70, 75), (76, 80), (81, 84), (85, 102),\
                          (103, 108), (109, 120), (121, 127), (128, 137),\
                          (138, 141), (142, 145), (146, 155), (156, 167),\
                          (168, 175), (176, 187), (188, 193), (194, 196),\
                          (197, 208), (209, 214), (215, 227), (228, 236),\
                          (237, 240), (241, 252), (253, 264), (265, 282)]

        units = b.get_units_julius(lines)
        self.assertEqual(expected_units, units)
        units = b.units_to_time(units, 100)
        self.assertEqual(0., units[0][0])
        self.assertEqual(0.03, units[0][1])
        self.assertEqual(2.65, units[-1][0])
        self.assertEqual(2.82, units[-1][1])

    def test_get_words_julius_phonemes(self):
        b = BaseAlignersReader()
        lines = b.get_lines(os.path.join(DATA, "track_000002.palign"))
        phonemes = b.get_phonemes_julius(lines)
        words = b.get_words_julius(lines)
        scores = b.get_word_scores_julius(lines)
        self.assertEqual(11, len(words))
        self.assertEqual(11, len(phonemes))
        self.assertEqual(11, len(scores))

    def test_read_palign(self):
        b = palign()
        self.assertEqual("palign", b.extension)
        expected_tokens = \
            [(0.0, 0.06, 'the', '0.618'), (0.06, 0.35, 'flight', '1.000'),\
             (0.35, 0.61, 'was', '0.432'), (0.61, 0.85, 'twelve', '1.000'),\
             (0.85, 1.21, 'hours', '0.746'), (1.21, 1.42, 'long', '1.000'),\
             (1.42, 1.56, 'and', '0.510'), (1.56, 1.76, 'we', '1.000'),\
             (1.76, 2.09, 'really', '0.808'), (2.09, 2.37, 'got', '1.000'),\
             (2.37, 2.82, 'bored', '1.000')]

        phones, tokens = b.read(os.path.join(DATA, "track_000002.palign"))
        self.assertEqual(expected_tokens, tokens)
        self.assertEqual(35, len(phones))

    def test_read_walign(self):
        b = walign()
        self.assertEqual("walign", b.extension)
        phones, tokens = b.read(os.path.join(DATA, "track_000000.walign"))
        self.assertEqual(21, len(tokens))
        self.assertEqual((0.2, 0.37, '感', '0.306'), tokens[1])

    def test_get_time_units_mlf(self):
        b = mlf()
        lines = b.get_lines(os.path.join(DATA, "track_sample.mlf"))
        expected_units = [
            (0, 200000), (200000, 400000), (400000, 800000),\
            (800000, 1200000), (1200000, 1500000), (1500000, 1800000),\
            (1800000, 1900000), (1900000, 2400000), (2400000, 2800000)]
        units = b.get_units(lines)
        self.assertEqual(expected_units, units)
        units = b.units_to_time(units, 10e6)
        self.assertEqual(0., units[0][0])
        self.assertEqual(0.02, units[0][1])
        self.assertEqual(0.28, units[-1][1])

    def test_get_phonemes_mlf(self):
        b = mlf()
        lines = b.get_lines(os.path.join(DATA, "track_sample.mlf"))
        phonemes = b.get_phonemes(lines)
        words = b.get_words(lines)
        self.assertEquals(3, len(phonemes))
        self.assertEquals(3, len(words))

    def test_read_mlf(self):
        b = mlf()
        self.assertEqual("mlf", b.extension)
        phones, tokens = b.read(os.path.join(DATA, "track_sample.mlf"))
        expected_tokens = \
            [(0.0, 0.08, 'w_1', None),\
             (0.08, 0.18, 'w_2', None),\
             (0.18, 0.28, 'w_3', None)]
        self.assertEqual(expected_tokens, tokens)
        self.assertEqual(9, len(phones))


# ---------------------------------------------------------------------------


class TestAligners(unittest.TestCase):
    """Manager of the aligners implemented in the package."""

    def test_check(self):
        """Check whether the aligner name is known or not."""
        aligners = sppasAligners()
        for a in aligners.names():
            self.assertEqual(a, aligners.check(a))

        with self.assertRaises(ValueError):
            aligners.check("invalid")

    # -----------------------------------------------------------------------

    def test_instantiate(self):
        """Instantiate an aligner to the appropriate Aligner system."""
        aligners = sppasAligners()
        for a in aligners.names():
            aligner = aligners.instantiate(None, a)
            self.assertTrue(isinstance(aligner,
                                       aligners.classes(a)))

# ---------------------------------------------------------------------------


class TestBaseAligner(unittest.TestCase):
    """Base class for any automatic alignment system."""

    def setUp(self):
        self._aligner = BaseAligner()

    def test_get_members(self):
        self.assertEqual("", self._aligner.outext())
        self.assertEqual(list(), self._aligner.extensions())
        self.assertEqual("", self._aligner.name())

    def test_infersp(self):
        self.assertFalse(self._aligner.get_infersp())
        self._aligner.set_infersp(True)
        self.assertTrue(self._aligner.get_infersp())
        self._aligner.set_infersp("ejzkjreg")
        self.assertFalse(self._aligner.get_infersp())

    def test_norun(self):
        with self.assertRaises(NotImplementedError):
            self._aligner.run_alignment("audio", "output")

    def test_set_data(self):
        # tokens and phones must be strings
        with self.assertRaises(Exception):
            self._aligner.set_phones(3)
        with self.assertRaises(Exception):
            self._aligner.set_tokens(3)

        # tokens matching phones
        self._aligner.set_phones("a b c")
        self._aligner.set_tokens("w1 w2 w3")
        self.assertEqual("", self._aligner.check_data())  # no error msg
        self.assertEqual("w1 w2 w3", self._aligner._tokens)

        # tokens not matching phones
        self._aligner.set_tokens("w1www")
        self.assertTrue(len(self._aligner.check_data()) > 20)  # error msg
        self.assertEqual("w_0 w_1 w_2", self._aligner._tokens)

# ---------------------------------------------------------------------------


class TestBasicAlign(unittest.TestCase):
    """Basic automatic alignment system."""

    def setUp(self):
        self._aligner = BasicAligner()

    def test_run_basic(self):

        self._aligner.set_phones("")
        self.assertEqual([(0, 0, "")], self._aligner.run_basic(0.))
        self.assertEqual([(0, 1, "")], self._aligner.run_basic(0.01))
        self.assertEqual([(0, 2, "")], self._aligner.run_basic(0.02))
        self.assertEqual([(0, 20, "")], self._aligner.run_basic(0.2))
        self.assertEqual([(0, 1000, "")], self._aligner.run_basic(10.))

        self._aligner.set_phones("a")
        self.assertEqual([(0, 0, "")], self._aligner.run_basic(0.))
        self.assertEqual([(0, 1, "a")], self._aligner.run_basic(0.02))
        self.assertEqual([(0, 1, "a")], self._aligner.run_basic(0.02))

        self._aligner.set_phones("a b c")
        self.assertEqual([(0, 2, "")], self._aligner.run_basic(0.02))

        self._aligner.set_phones("a b")
        self.assertEqual([(0, 9, "a"), (10, 19, "b")],
                          self._aligner.run_basic(0.2))

        self._aligner.set_phones("a|aa b|bb")
        self.assertEqual([(0, 9, "a"), (10, 19, "b")],
                          self._aligner.run_basic(0.2))

        self._aligner.set_phones("a|A b|B")
        self.assertEqual([(0, 9, "a"), (10, 19, "b")],
                          self._aligner.run_basic(0.2))

# ---------------------------------------------------------------------------


class TestJuliusAlign(unittest.TestCase):

    def setUp(self):
        self._modeldir = os.path.join(MODELDIR, "models-fra")
        self._aligner = JuliusAligner(self._modeldir)

# ---------------------------------------------------------------------------


class TestHviteAlign(unittest.TestCase):

    def setUp(self):
        self._modeldir = os.path.join(MODELDIR, "models-fra")
        self._aligner = HviteAligner(self._modeldir)
