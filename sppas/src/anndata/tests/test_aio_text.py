# -*- coding:utf-8 -*-

import unittest
import os.path
import shutil

from sppas.src.utils.fileutils import sppasFileUtils

from ..anndataexc import AioMultiTiersError
from ..aio.text import sppasRawText
from ..aio.text import sppasCSV

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestRawText(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

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

    def test_read1(self):
        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample-irish-1.txt"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 6)

    def test_read2(self):
        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample-irish-2.txt"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 5)

    def test_read3(self):
        txt = sppasCSV()
        txt.read(os.path.join(DATA, "sample-irish.csv"))
        self.assertEqual(len(txt), 2)
        self.assertEqual(len(txt[0]), 5)
        self.assertEqual(len(txt[1]), 5)

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

        csv = sppasCSV()
        csv.write(os.path.join(TEMP, "sample.csv"))
        self.assertFalse(os.path.exists(os.path.join(TEMP, "sample.csv")))
        csv.create_tier()
        csv.write(os.path.join(TEMP, "sample.csv"))
        self.assertTrue(os.path.exists(os.path.join(TEMP, "sample.csv")))
        self.assertEqual(os.stat("file").st_size, 0)

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
