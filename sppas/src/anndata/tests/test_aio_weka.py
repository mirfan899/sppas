# -*- coding:utf-8 -*-
import sys
import unittest
import os.path
import shutil

from ..aio.weka import sppasARFF
from ..transcription import sppasTranscription
from ..annlocation.interval import sppasInterval
from ..annlocation.point import sppasPoint
from ..annlabel.label import sppasTag
from ..annlabel.label import sppasLabel
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation

from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestARFF(unittest.TestCase):
    """
    Represents an ARFF file, the native format of WEKA.
    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)
        self.trs = sppasTranscription()
        self.tier1 = self.trs.create_tier(name="tier1")
        self.tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))

    def tearDown(self):
        shutil.rmtree(TEMP)
    
    def test_members(self):
        arff = sppasARFF()
        self.assertTrue(arff.multi_tiers_support())
        self.assertFalse(arff.no_tiers_support())
        self.assertTrue(arff.metadata_support())
        self.assertTrue(arff.ctrl_vocab_support())
        self.assertFalse(arff.media_support())
        self.assertFalse(arff.hierarchy_support())
        self.assertTrue(arff.point_support())
        self.assertTrue(arff.interval_support())
        self.assertTrue(arff.disjoint_support())
        self.assertFalse(arff.alternative_localization_support())
        self.assertTrue(arff.alternative_tag_support())
        self.assertFalse(arff.radius_support())
        self.assertFalse(arff.gaps_support())
        self.assertTrue(arff.overlaps_support())

    def test_write_header(self):
        arff = sppasARFF()
        arff.set(self.trs)
        arff.set_meta("weka_instance_step", "0.04")
        arff._write_header(sys.stdout)
        arff._write_metadata(sys.stdout)
        arff._write_relation(sys.stdout)
        arff._write_attributes(sys.stdout)
        arff._write_data(sys.stdout)
