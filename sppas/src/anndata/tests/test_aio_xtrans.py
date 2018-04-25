# -*- coding:utf-8 -*-

import unittest
import os.path

from ..aio.xtrans import sppasTDF
from ..annlocation.point import sppasPoint

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestTDF(unittest.TestCase):
    """
    TDF reader.
    """
    def test_members(self):
        txt = sppasTDF()
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

        self.assertEqual(sppasPoint(3., 0.005), sppasTDF.make_point("3.0"))
        self.assertEqual(sppasPoint(3., 0.005), sppasTDF.make_point("3"))
        with self.assertRaises(TypeError):
            sppasTDF.make_point("a")

    # -----------------------------------------------------------------

    def test_read(self):
        """ Read a TDF file. """

        sample = os.path.join(DATA, "sample-irish.tdf")
        tdf = sppasTDF()
        tdf.read(sample)
        self.assertEqual(len(tdf), 2)     # 2 tiers (one per channel)
        self.assertEqual(len(tdf[0]), 5)  # 5 annotations in each tier
        self.assertEqual(len(tdf[1]), 5)  # 5 annotations in each tier
        self.assertEqual(sppasPoint(5.79874657439, 0.005), tdf[0].get_first_point())
        self.assertEqual(sppasPoint(7.88732394366, 0.005), tdf[1].get_first_point())
        self.assertTrue(tdf[0].is_meta_key('speaker_name'))
        self.assertTrue(tdf[1].is_meta_key('speaker_name'))
        # should be extended to test media, annotations, etc.
