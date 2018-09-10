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
import os.path

from sppas.src.config import paths

from ..Align.aligners import sppasAligners
from ..Align.aligners.basealigner import BaseAligner
from ..Align.aligners.basicalign import BasicAligner
from ..Align.aligners.juliusalign import JuliusAligner
from ..Align.aligners.hvitealign import HviteAligner

# ---------------------------------------------------------------------------

MODELDIR = os.path.join(paths.resources, "models")
sample_1 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")  # mono; 16000Hz; 16bits

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

    def setUp(self):
        self._aligner = BasicAligner()

    def test_run_basic(self):

        self._aligner.set_phones("")
        a = self._aligner.run_basic(0.)
        self.assertEquals(a, [(0, 0, "")])

        a = self._aligner.run_basic(0.01)
        self.assertEquals(a, [(0, 1, "")])

        a = self._aligner.run_basic(0.02)
        self.assertEquals(a, [(0, 2, "")])

        a = self._aligner.run_basic(0.2)
        self.assertEquals(a, [(0, 20, "")])

        a = self._aligner.run_basic(10.)
        self.assertEquals(a, [(0, 1000, "")])

        self._aligner.set_phones("a")
        a = self._aligner.run_basic(0.)
        self.assertEquals(a, [(0, 0, "")])

        a = self._aligner.run_basic(0.02)
        self.assertEquals(a, [(0, 1, "a")])

        a = self._aligner.run_basic(0.02)
        self.assertEquals(a, [(0, 1, "a")])

        self._aligner.set_phones("a b c")
        a = self._aligner.run_basic(0.02)
        self.assertEquals(a, [(0, 2, "")])

        self._aligner.set_phones("a b")
        a = self._aligner.run_basic(0.2)
        self.assertEquals(a, [(0, 9, "a"),(10, 19, "b")])

        self._aligner.set_phones("a|aa b|bb")
        a = self._aligner.run_basic(0.2)
        self.assertEquals(a, [(0, 9, "a"),(10, 19, "b")])

        self._aligner.set_phones("a|A b|B")
        a = self._aligner.run_basic(0.2)
        self.assertEquals(a, [(0, 9, "a"),(10, 19, "b")])

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
