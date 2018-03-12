# -*- coding:utf-8 -*-

import unittest
import os.path
import shutil

from sppas.src.utils.fileutils import sppasFileUtils

from ..anndataexc import AioMultiTiersError
from ..aio.subtitle import sppasBaseSubtitles
from ..aio.subtitle import sppasSubRip
from ..aio.subtitle import sppasSubViewer

from ..annlocation.interval import sppasInterval
from ..annlocation.point import sppasPoint
from ..annlabel.label import sppasTag
from ..annlabel.label import sppasLabel
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestBaseSubtitle(unittest.TestCase):
    """
    Base text is mainly made of utility methods.

    """
    def test_members(self):
        txt = sppasBaseSubtitles()
        self.assertFalse(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertFalse(txt.metadata_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertFalse(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertFalse(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertFalse(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_make_point(self):
        """ Convert data into the appropriate digit type, or not. """

        self.assertEqual(sppasPoint(3., 0.02), sppasBaseSubtitles.make_point("3.0"))
        self.assertEqual(sppasPoint(3., 0.02), sppasBaseSubtitles.make_point("3."))
        self.assertEqual(sppasPoint(3), sppasBaseSubtitles.make_point("3"))
        with self.assertRaises(TypeError):
            sppasBaseSubtitles.make_point("3a")

    # -----------------------------------------------------------------

    def test_serialize_location(self):
        """ Test location -> timestamps. """

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        self.assertEqual(sppasSubRip._serialize_location(a1),
                         "00:00:01,000 --> 00:00:03,500\n")

        a2 = sppasAnnotation(sppasLocation(sppasPoint(1.)))
        self.assertEqual(sppasSubRip._serialize_location(a2),
                         "00:00:01,000 --> 00:00:02,000\n")

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        self.assertEqual(sppasSubRip._serialize_location(a1),
                         "00:00:01,000 --> 00:00:03,000\n")

        a2 = sppasAnnotation(sppasLocation(sppasPoint(1)))
        self.assertEqual(sppasSubRip._serialize_location(a2),
                         "00:00:01,000 --> 00:00:02,000\n")

    # -----------------------------------------------------------------

    def test_serialize_label(self):
        """ Test label -> caption. """

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))),
                             sppasLabel(sppasTag("")))
        self.assertEqual(sppasSubRip._serialize_label(a1), "\n")

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))),
                             sppasLabel(sppasTag("label")))
        self.assertEqual(sppasSubRip._serialize_label(a1), "label\n")

# ---------------------------------------------------------------------


class TestSubRip(unittest.TestCase):
    """
    Represents a SubRip reader/writer.

    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------

    def test_read(self):
        """ Test of reading a SRT sample file. """

        txt = sppasSubRip()
        txt.read(os.path.join(DATA, "sample.srt"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 4)
        self.assertEqual(sppasPoint(0.), txt[0].get_first_point())
        self.assertEqual(sppasPoint(15.), txt[0].get_last_point())
        self.assertTrue(txt[0][2].is_meta_key('position_pixel_X1'))
        self.assertFalse("<i>" in txt[0][1].get_label().get_best().get_content())
        self.assertTrue("une classe" in txt[0][1].get_label().get_best().get_content())

    # -----------------------------------------------------------------

    def test_serialize_metadata(self):
        """ Test metadata -> position. """

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        self.assertEqual(sppasSubRip._serialize_metadata(a1), "")
        a1.set_meta("position_pixel_X1", "10")
        a1.set_meta("position_pixel_Y1", "20")
        self.assertEqual(sppasSubRip._serialize_metadata(a1), "")
        a1.set_meta("position_pixel_X2", "100")
        a1.set_meta("position_pixel_Y2", "200")
        self.assertEqual(sppasSubRip._serialize_metadata(a1), "X1:10 Y1:20 X2:100 Y2:200\n")

    # -----------------------------------------------------------------

    def test_write(self):
        """ Test of writing a SRT sample file. """

        sub = sppasSubRip()
        tier = sub.create_tier(name="tierIntervals")

        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.)))))
        tier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2.5), sppasPoint(4.))),
                                 sppasLabel(sppasTag('toto'))))

        sub.write(os.path.join(TEMP, "sample.srt"))
        self.assertTrue(os.path.exists(os.path.join(TEMP, "sample.srt")))
        self.assertGreater(os.stat(os.path.join(TEMP, "sample.srt")).st_size, 0)

        with open(os.path.join(TEMP, "sample.srt")) as fp:
            lines = fp.readlines()
            fp.close()

        self.assertEqual(len(lines), 4)

# ---------------------------------------------------------------------


class TestSubViewer(unittest.TestCase):
    """
    Represents a SubViewer reader/writer.

    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------

    def test_read(self):
        """ Test of reading a SUB sample file. """

        txt = sppasSubViewer()
        txt.read(os.path.join(DATA, "sample.sub"))
        self.assertEqual(txt.get_meta('annotator_name'), "FK")

        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 6)
        self.assertEqual(sppasPoint(22.5), txt[0].get_first_point())
        self.assertEqual(sppasPoint(34.80), txt[0].get_last_point())
        self.assertFalse("[br]" in txt[0][0].get_label().get_best().get_content())
        self.assertTrue("amet, consectetur" in txt[0][0].get_label().get_best().get_content())

    # -----------------------------------------------------------------

    def test_serialize_header(self):
        """ Test metadata -> header. """

        txt = sppasSubViewer()
        header = txt._serialize_header()
        self.assertEqual(len(header.split('\n')), 14)

    # -----------------------------------------------------------------

    def test_write(self):
        """ """
        sub = sppasSubViewer()
        tier = sub.create_tier(name="tierIntervals")

        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.)))))
        tier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2.5), sppasPoint(4.))),
                                 sppasLabel(sppasTag('toto'))))

        sub.write(os.path.join(TEMP, "sample.sub"))
        self.assertTrue(os.path.exists(os.path.join(TEMP, "sample.sub")))
        self.assertGreater(os.stat(os.path.join(TEMP, "sample.sub")).st_size, 0)

        with open(os.path.join(TEMP, "sample.sub")) as fp:
            lines = fp.readlines()

        self.assertEqual(len(lines), 16)
