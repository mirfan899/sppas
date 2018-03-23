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

    src.anndata.tests.test_aio_annotationpro
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the reader of SPPAS for ÃnnotationPro files.

"""
import unittest
import os.path
import xml.etree.cElementTree as ET

from ..aio.annotationpro import sppasANTX
from ..annlocation.point import sppasPoint
from ..annlabel.tag import sppasTag
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlocation.location import sppasLocation

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestANTX(unittest.TestCase):
    """
    Test reader of Audacity project files.

    """
    def test_detect(self):
        """ Test the file format detection method. """

        for filename in os.listdir(DATA):
            f = os.path.join(DATA, filename)
            if filename.endswith('.antx'):
                self.assertTrue(sppasANTX.detect(f))
            else:
                self.assertFalse(sppasANTX.detect(f))

    # -----------------------------------------------------------------------

    def test_members(self):
        txt = sppasANTX()
        self.assertTrue(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertTrue(txt.metadata_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertTrue(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertFalse(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertFalse(txt.overlaps_support())

    # -----------------------------------------------------------------------

    def test_make_point(self):
        """ Convert data into the appropriate digit type, or not. """

        self.assertEqual(sppasPoint(3., 0.005), sppasANTX.make_point("132300"))
        with self.assertRaises(TypeError):
            sppasANTX.make_point("3a")
        with self.assertRaises(TypeError):
            sppasANTX.make_point("3.")

    # -----------------------------------------------------------------------
