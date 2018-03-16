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

    src.anndata.tests.test_aio_praat
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the reader/writer of SPPAS for Praat files.

"""
import unittest
import os.path
import shutil

from sppas.src.utils.fileutils import sppasFileUtils

from ..anndataexc import AioLineFormatError
from ..anndataexc import AioEmptyTierError
from ..anndataexc import AioNoTiersError

from ..aio.praat import sppasBasePraat
from ..aio.praat import sppasTextGrid
from ..annlocation.interval import sppasInterval
from ..annlocation.point import sppasPoint
from ..annlabel.tag import sppasTag
from ..annlabel.label import sppasLabel
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestBasePraat(unittest.TestCase):
    """

    """
    def test_members(self):
        txt = sppasBasePraat()
        self.assertTrue(txt.multi_tiers_support())
        self.assertFalse(txt.no_tiers_support())
        self.assertFalse(txt.metadata_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertFalse(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertTrue(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertFalse(txt.gaps_support())
        self.assertFalse(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_make_point(self):
        """ Convert data into the appropriate digit type, or not. """

        self.assertEqual(sppasPoint(3., 0.005), sppasBasePraat.make_point("3.0"))
        self.assertEqual(sppasPoint(3., 0.005), sppasBasePraat.make_point("3."))
        self.assertEqual(sppasPoint(3), sppasBasePraat.make_point("3"))
        with self.assertRaises(TypeError):
            sppasBasePraat.make_point("3a")

    # -----------------------------------------------------------------

    def test_parse_int(self):
        """ Parse an integer value from a line of a Praat formatted file. """

        # long textgrid
        value = sppasBasePraat._parse_int("size = 1")
        self.assertEqual(value, 1)

        value = sppasBasePraat._parse_int("intervals: size = 23")
        self.assertEqual(value, 23)

        value = sppasBasePraat._parse_int("\t\tintervals:    size   =   \t 23")
        self.assertEqual(value, 23)

        # short textgrid
        value = sppasBasePraat._parse_int("1")
        self.assertEqual(value, 1)

        with self.assertRaises(AioLineFormatError):
            sppasBasePraat._parse_int("n'importe quoi")

        with self.assertRaises(AioLineFormatError):
            sppasBasePraat._parse_int("a = b")

    # -----------------------------------------------------------------

    def test_parse_float(self):
        """ Parse a float value from a line of a Praat formatted file. """

        # long textgrid
        value = sppasBasePraat._parse_float("xmax = 21.3471")
        self.assertEqual(value, 21.3471)

        value = sppasBasePraat._parse_float("\t\tmax   =   \t 23")
        self.assertEqual(value, 23.)

        # short textgrid
        value = sppasBasePraat._parse_float("1.098765432")
        self.assertEqual(value, 1.098765432)

        with self.assertRaises(AioLineFormatError):
            sppasBasePraat._parse_float("n'importe quoi")

        with self.assertRaises(AioLineFormatError):
            sppasBasePraat._parse_float("a = b")

    # -----------------------------------------------------------------

    def test_parse_string(self):
        """ Parse a float value from a line of a Praat formatted file. """

        text = sppasBasePraat._parse_string(' \t text = "a b c"\n')
        self.assertEqual(text, "a b c")

        text = sppasBasePraat._parse_string(' \t text = "   "\n')
        self.assertEqual(text, "   ")

    # -----------------------------------------------------------------

    def test_serialize_header(self):
        """ Serialize the header of a Praat file. """

        header = sppasBasePraat._serialize_header("TextGrid", 0., 10.).split("\n")
        self.assertEqual(len(header), 6)
        self.assertTrue('File type = "ooTextFile"' in header[0])
        self.assertTrue('Object class = "TextGrid"' in header[1])
        self.assertTrue('xmin = 0.' in header[3])
        self.assertTrue('xmax = 10.' in header[4])

    # -----------------------------------------------------------------

    def test_serialize_label_text(self):
        """ Convert a label into a text string. """

        line = sppasBasePraat._serialize_label_text(sppasLabel())
        self.assertEqual(line, '\t\ttext = ""\n')

        line = sppasBasePraat._serialize_label_text(sppasLabel(sppasTag("")))
        self.assertEqual(line, '\t\ttext = ""\n')

        line = sppasBasePraat._serialize_label_text(sppasLabel(sppasTag("toto")))
        self.assertEqual(line, '\t\ttext = "toto"\n')

    # -----------------------------------------------------------------

    def test_serialize_label_value(self):
        """ Convert a label with a numerical value into a string. """
        line = sppasBasePraat._serialize_label_value(sppasLabel())
        self.assertEqual(line, '\t\tvalue = \n')

        line = sppasBasePraat._serialize_label_value(sppasLabel(sppasTag("")))
        self.assertEqual(line, '\t\tvalue = ""\n')

        line = sppasBasePraat._serialize_label_value(sppasLabel(sppasTag("2")))
        self.assertEqual(line, '\t\tvalue = "2"\n')

# ---------------------------------------------------------------------------
#
#
# class TestTextGrid(unittest.TestCase):
#
#     def setUp(self):
#         if os.path.exists(TEMP) is False:
#             os.mkdir(TEMP)
#
#     def tearDown(self):
#         shutil.rmtree(TEMP)
#
#     # -----------------------------------------------------------------------
#
#     def test_members(self):
#         tg = sppasTextGrid()
#         self.assertTrue(tg.multi_tiers_support())
#         self.assertFalse(tg.no_tiers_support())
#         self.assertFalse(tg.metadata_support())
#         self.assertFalse(tg.ctrl_vocab_support())
#         self.assertFalse(tg.media_support())
#         self.assertFalse(tg.hierarchy_support())
#         self.assertTrue(tg.point_support())
#         self.assertTrue(tg.interval_support())
#         self.assertFalse(tg.disjoint_support())
#         self.assertFalse(tg.alternative_localization_support())
#         self.assertFalse(tg.alternative_tag_support())
#         self.assertFalse(tg.radius_support())
#         self.assertFalse(tg.gaps_support())
#         self.assertFalse(tg.overlaps_support())
#
#     # -----------------------------------------------------------------------
#
#     def test_read(self):
#         txt = sppasTextGrid()
#         txt.read(os.path.join(DATA, "sample.TextGrid"))
#         self.assertEqual(len(txt), 2)
#         self.assertEqual(txt[0].get_name(), "transcription")
#         self.assertEqual(txt[1].get_name(), "P-Tones")
#         self.assertEqual(len(txt[0]), 4)
#         self.assertEqual(len(txt[1]), 2)
#
#     # -----------------------------------------------------------------------
#
#     def test_write(self):
#         txt = sppasTextGrid()
#         with self.assertRaises(AioNoTiersError):
#             txt.write(os.path.join(TEMP, "sample.txt"))
#         self.assertFalse(os.path.exists(os.path.join(TEMP, "sample.txt")))
#         txt.create_tier()
#         with self.assertRaises(AioEmptyTierError):
#             txt.write(os.path.join(TEMP, "sample.txt"))
#
#     # -----------------------------------------------------------------------
#
#     def test_read_write(self):
#         txt = sppasTextGrid()
#         txt.read(os.path.join(DATA, "sample.TextGrid"))
#         txt.write(os.path.join(TEMP, "sample.TextGrid"))
#         txt2 = sppasTextGrid()
#         txt2.read(os.path.join(TEMP, "sample.TextGrid"))
#         self.assertEqual(len(txt), len(txt2))
#         # Compare annotations of original and saved-read
#         for t1, t2 in zip(txt, txt2):
#             self.assertEqual(len(t1), len(t2))
#             for a1, a2 in zip(t1, t2):
#                 self.assertEqual(a1.get_label().get_best().get_typed_content(),
#                                  a2.get_label().get_best().get_typed_content())
#                 self.assertEqual(a1.get_highest_localization().get_midpoint(),
#                                  a2.get_highest_localization().get_midpoint())
#                 self.assertEqual(a1.get_lowest_localization().get_midpoint(),
#                                  a2.get_lowest_localization().get_midpoint())
