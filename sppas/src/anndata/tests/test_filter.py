# -*- coding:utf-8 -*-
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

    src.anndata.tests.test_filter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the filter system.

"""
import unittest
import os.path

from sppas.src.utils.makeunicode import u
from ..filter import PatternMatching
from ..filter import PatternDuration
from ..aio.readwrite import sppasRW

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestPatternMatching(unittest.TestCase):
    """ Test pattern matching: search in label patterns. """

    def setUp(self):
        parser = sppasRW(os.path.join(DATA, "grenelle.antx"))
        self.trs = parser.read(heuristic=False)

    # -----------------------------------------------------------------------

    def test_pattern_exact(self):
        """ Test str == str (case-sensitive)"""

        tier = self.trs.find('P-Phonemes')

        pred = PatternMatching(exact="R") | PatternMatching(exact="l")
        res = [a.get_labels() for a in tier if pred(a)]
        for labels in res:
            texts = list()
            for label in labels:
                for tag, score in label:
                    texts.append(tag.get_typed_content())
            self.assertTrue(any(t in [u("R"), u("l")] for t in texts))

        with self.assertRaises(TypeError):
            pred = PatternMatching(exact=1)
            res = [a for a in tier if pred(a)]

        with self.assertRaises(TypeError):
            pred = PatternMatching(exact=True)
            res = [a for a in tier if pred(a)]

    # -----------------------------------------------------------------------

    def test_pattern_iexact(self):
        """ Test str == str (case-insensitive). """

        tier = self.trs.find('P-Phonemes')

        pred = PatternMatching(iexact="s")
        res = [a.get_labels() for a in tier if pred(a)]
        for labels in res:
            texts = list()
            for label in labels:
                for tag, score in label:
                    texts.append(tag.get_typed_content())
            self.assertTrue(any(t in [u("s"), u("S")] for t in texts))

        with self.assertRaises(TypeError):
            pred = PatternMatching(iexact=1)
            res = [a for a in tier if pred(a)]

        with self.assertRaises(TypeError):
            pred = PatternMatching(iexact=True)
            res = [a for a in tier if pred(a)]

# ---------------------------------------------------------------------------


class TestPatternDuration(unittest.TestCase):
    """ Test pattern matching: search in annotation duration. """

    def test_pattern_eq(self):
        """ """
        pred = PatternDuration(eq=0.2)
