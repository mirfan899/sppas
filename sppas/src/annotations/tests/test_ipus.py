# -*- coding: UTF-8 -*-
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

    src.annotations.tests.test_normalize.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the SPPAS IPUs Segmentation

"""
import unittest
import os.path

from sppas.src.config import paths

from sppas.src.anndata import sppasTranscription
from ..IPUs.ipustrs import IPUsTrs

# ---------------------------------------------------------------------------


class TestIPUsTRS(unittest.TestCase):
    """Test of the class IPUsTrs.

    Extract IPUs from an already annotated data file.

    """

    def test_without_trs(self):
        o = IPUsTrs()
        self.assertEqual(0, len(o.get_names()))
        self.assertEqual(0, len(o.get_units()))
        o.set_transcription(None)
        self.assertEqual(0, len(o.get_names()))
        self.assertEqual(0, len(o.get_units()))
        self.assertEqual((False, False), o.extract_bounds())
        self.assertEqual(([], []), o.extract())

    def test_with_trs_not_correct(self):
        trs = sppasTranscription()
        o = IPUsTrs(trs)
        self.assertEqual((False, False), o.extract_bounds())
        self.assertEqual(([], []), o.extract())
