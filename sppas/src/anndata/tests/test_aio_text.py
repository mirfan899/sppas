# -*- coding:utf-8 -*-

import unittest
import os.path
import shutil

from sppas.src.utils.fileutils import sppasFileUtils

from ..anndataexc import AioMultiTiersError
from ..aio.text import sppasRawText
from ..aio.text import sppasCSV
from ..aio.text import sppasBaseText
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestBaseText(unittest.TestCase):
    """
    Base text is mainly made of utility methods.
    """
    def test_members(self):
        txt = sppasBaseText()
        self.assertTrue(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
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
        self.assertTrue(txt.gaps_support())
        self.assertTrue(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_make_point(self):
        """ Convert data into the appropriate digit type, or not. """

        self.assertEqual(sppasPoint(3., 0.001), sppasBaseText.make_point("3.0"))
        self.assertEqual(sppasPoint(3., 0.001), sppasBaseText.make_point("3."))
        self.assertEqual(sppasPoint(3), sppasBaseText.make_point("3"))
        with self.assertRaises(TypeError):
            sppasBaseText.make_point("3a")

    # -----------------------------------------------------------------

    def test_format_quotation_marks(self):
        """ Remove initial and final quotation mark. """

        self.assertEqual("ab", sppasBaseText.format_quotation_marks("ab"))
        self.assertEqual("ab", sppasBaseText.format_quotation_marks('"ab"'))
        self.assertEqual("ab", sppasBaseText.format_quotation_marks("'ab'"))
        self.assertEqual("", sppasBaseText.format_quotation_marks(""))
        self.assertEqual("'", sppasBaseText.format_quotation_marks("'"))

    # -----------------------------------------------------------------

    def test_split_lines(self):
        """ Split the lines with the given separator. """

        self.assertEqual(list(), sppasBaseText.split_lines(list()))
        self.assertEqual([['a']], sppasBaseText.split_lines(['a']))
        self.assertEqual([['a'], ['b']], sppasBaseText.split_lines(['a', 'b']))
        self.assertEqual([['a', 'a'], ['b', 'b']], sppasBaseText.split_lines(['a a', 'b b']))
        self.assertEqual([['a', 'a'], ['b', 'b']], sppasBaseText.split_lines(['a;a', 'b;b'], ";"))
        self.assertIsNone(sppasBaseText.split_lines(['a;a;a', 'b;b'], ";"))

        lines = list()
        lines.append("7.887	10.892	Go maith anois a mhac. Anois cé acub?	0")
        lines.append("11.034	12.343	Tá neart ábhair ansin anois agat.	1")
        columns = sppasBaseText.split_lines(lines, separator=" ")
        self.assertIsNone(columns)
        columns = sppasBaseText.split_lines(lines, separator="\t")
        self.assertEqual(len(columns), 2)     # 2 lines
        self.assertEqual(len(columns[0]), 4)  # 4 columns in each line
        self.assertEqual(columns[1][0], "11.034")
        self.assertEqual(columns[1][1], "12.343")
        self.assertEqual(columns[1][2], "Tá neart ábhair ansin anois agat.")
        self.assertEqual(columns[1][3], "1")
        lines.append(' ')
        columns = sppasBaseText.split_lines(lines, separator="\t")
        self.assertEqual(len(columns), 2)     # 2 lines
        self.assertEqual(len(columns[0]), 4)  # 4 columns in each line

    # -----------------------------------------------------------------

    def test_location(self):
        """ Fix the location from the content of the data. """

        # Point/Interval (int)
        self.assertEqual(sppasLocation(sppasPoint(3)), sppasBaseText.fix_location("3", "3"))
        self.assertEqual(sppasLocation(sppasPoint(3)), sppasBaseText.fix_location('"3"', '"3"'))
        self.assertEqual(sppasLocation(sppasPoint(3)), sppasBaseText.fix_location('"3"', ''))
        self.assertEqual(sppasLocation(sppasPoint(3)), sppasBaseText.fix_location('', '3'))
        self.assertEqual(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(4))),
                         sppasBaseText.fix_location("3", "4"))
        # Point/Interval (float)
        self.assertEqual(sppasLocation(sppasPoint(3.)), sppasBaseText.fix_location("3.0", "3."))
        self.assertEqual(sppasLocation(sppasInterval(sppasPoint(3.), sppasPoint(4.))),
                         sppasBaseText.fix_location("3.0", "4.0"))
        # Errors
        with self.assertRaises(TypeError):
            sppasBaseText.fix_location("a", "b")
        with self.assertRaises(ValueError):
            sppasBaseText.fix_location("4", "3")

        # None
        self.assertIsNone(sppasBaseText.fix_location("", ""))

# ---------------------------------------------------------------------


class TestRawText(unittest.TestCase):
    """
    Represents a Text reader/writer.
    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------

    def test_members(self):
        txt = sppasRawText()
        self.assertFalse(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
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
        self.assertTrue(txt.gaps_support())
        self.assertTrue(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_read1(self):
        """ Simple transcription, one utterance a line. """

        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample-irish-1.txt"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 6)

    # -----------------------------------------------------------------

    def test_read2(self):
        """ Column-based transcription. """

        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample-irish-2.txt"))
        self.assertEqual(len(txt), 2)
        self.assertEqual(len(txt[0]), 5)
        self.assertEqual(len(txt[1]), 5)
        self.assertEqual(txt[0].get_name(), "RawTranscription")
        self.assertEqual(txt[1].get_name(), "Tier-1")

    # -----------------------------------------------------------------

    def test_read3(self):
        txt = sppasCSV()
        txt.read(os.path.join(DATA, "sample-irish.csv"))
        self.assertEqual(len(txt), 2)
        self.assertEqual(len(txt[0]), 5)
        self.assertEqual(len(txt[1]), 5)

    # -----------------------------------------------------------------

    def test_write(self):
        txt = sppasRawText()
        txt.write(os.path.join(TEMP, "sample.txt"))
        self.assertTrue(os.path.exists(os.path.join(TEMP, "sample.txt")))
        self.assertEqual(os.stat(os.path.join(TEMP, "sample.txt")).st_size, 0)
        txt.create_tier()
        txt.write(os.path.join(TEMP, "sample-2.txt"))
        self.assertTrue(os.path.exists(os.path.join(TEMP, "sample-2.txt")))
        self.assertEqual(os.stat(os.path.join(TEMP, "sample.txt")).st_size, 0)
        txt.create_tier()
        with self.assertRaises(AioMultiTiersError):
            txt.write(os.path.join(TEMP, "sample.txt"))

        # Empty files:
        csv = sppasCSV()
        csv.write(os.path.join(TEMP, "sample.csv"))
        self.assertTrue(os.path.exists(os.path.join(TEMP, "sample.csv")))
        self.assertEqual(os.stat(os.path.join(TEMP, "sample.csv")).st_size, 0)

        csv.create_tier()
        csv.write(os.path.join(TEMP, "sample2.csv"))
        self.assertTrue(os.path.exists(os.path.join(TEMP, "sample2.csv")))
        self.assertEqual(os.stat(os.path.join(TEMP, "sample2.csv")).st_size, 0)

    # -----------------------------------------------------------------

    def test_read_write(self):
        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample-irish-1.txt"))
        txt.write(os.path.join(TEMP, "sample-1.txt"))
        txt2 = sppasRawText()
        txt2.read(os.path.join(TEMP, "sample-1.txt"))
        # Compare annotations of original and saved-read
        for t1, t2 in zip(txt, txt2):
            self.assertEqual(len(t1), len(t2))
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.get_label().get_best().get_typed_content(),
                                 a2.get_label().get_best().get_typed_content())
                self.assertEqual(a1.get_highest_localization().get_midpoint(),
                                 a2.get_highest_localization().get_midpoint())
                self.assertEqual(a1.get_lowest_localization().get_midpoint(),
                                 a2.get_lowest_localization().get_midpoint())
        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample-irish-2.txt"))
        txt.write(os.path.join(TEMP, "sample-2.txt"))
        txt2 = sppasRawText()
        txt2.read(os.path.join(TEMP, "sample-2.txt"))
        # Compare annotations of original and saved-read
        for t1, t2 in zip(txt, txt2):
            self.assertEqual(len(t1), len(t2))
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.get_label().get_best().get_typed_content(),
                                 a2.get_label().get_best().get_typed_content())
                self.assertEqual(a1.get_highest_localization().get_midpoint(),
                                 a2.get_highest_localization().get_midpoint())
                self.assertEqual(a1.get_lowest_localization().get_midpoint(),
                                 a2.get_lowest_localization().get_midpoint())

# ---------------------------------------------------------------------


class TestCSVText(unittest.TestCase):
    """
    Represents a CSV reader/writer.
    """

    def test_members(self):
        txt = sppasCSV()
        self.assertTrue(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
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
        self.assertTrue(txt.gaps_support())
        self.assertTrue(txt.overlaps_support())