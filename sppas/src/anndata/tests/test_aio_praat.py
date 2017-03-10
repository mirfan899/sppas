# -*- coding:utf-8 -*-

import unittest
import os.path
import shutil

from sppas.src.utils.fileutils import sppasFileUtils

from ..anndataexc import AioEmptyTierError
from ..anndataexc import AioNoTiersError

from ..aio.praat import sppasTextGrid

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestTextGrid(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_members(self):
        tg = sppasTextGrid()
        self.assertTrue(tg.multi_tiers_support())
        self.assertFalse(tg.no_tiers_support())
        self.assertFalse(tg.metadata_support())
        self.assertFalse(tg.ctrl_vocab_support())
        self.assertFalse(tg.media_support())
        self.assertFalse(tg.hierarchy_support())
        self.assertTrue(tg.point_support())
        self.assertTrue(tg.interval_support())
        self.assertFalse(tg.disjoint_support())
        self.assertFalse(tg.alternative_localization_support())
        self.assertFalse(tg.alternative_tag_support())
        self.assertFalse(tg.radius_support())
        self.assertFalse(tg.gaps_support())
        self.assertFalse(tg.overlaps_support())

    def test_read(self):
        txt = sppasTextGrid()
        txt.read(os.path.join(DATA, "sample.TextGrid"))
        self.assertEqual(len(txt), 2)
        self.assertEqual(txt[0].get_name(), "transcription")
        self.assertEqual(txt[1].get_name(), "P-Tones")
        self.assertEqual(len(txt[0]), 1)
        self.assertEqual(len(txt[1]), 2)

    def test_write(self):
        txt = sppasTextGrid()
        with self.assertRaises(AioNoTiersError):
            txt.write(os.path.join(TEMP, "sample.txt"))
        self.assertFalse(os.path.exists(os.path.join(TEMP, "sample.txt")))
        txt.create_tier()
        with self.assertRaises(AioEmptyTierError):
            txt.write(os.path.join(TEMP, "sample.txt"))

    def test_read_write(self):
        txt = sppasTextGrid()
        txt.read(os.path.join(DATA, "sample.TextGrid"))
        txt.write(os.path.join(TEMP, "sample.TextGrid"))
        txt2 = sppasTextGrid()
        txt2.read(os.path.join(TEMP, "sample.TextGrid"))
        self.assertEqual(len(txt), len(txt2))
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
