# -*- coding:utf-8 -*-
import sys
import unittest
import os.path
import shutil
import io

import sppas
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
        self.tier2 = self.trs.create_tier(name="tier2")
        self.tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))

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
        """ Write the creator, etc. in the header of the ARFF file.
        """
        output = io.BytesIO()
        arff = sppasARFF()
        arff.set(self.trs)
        arff._write_header(output)
        lines = output.getvalue()
        self.assertEqual(len(lines.split("\n")), 7)
        self.assertTrue("creator" in lines)
        self.assertTrue("version" in lines)
        self.assertTrue("date" in lines)
        self.assertTrue("author" in lines)
        self.assertTrue("license" in lines)

    def test_validate(self):
        arff = sppasARFF()
        t = sppasTranscription()
        arff.set(t)
        with self.assertRaises(ValueError):   # Empty transcription
            arff.validate()
        tier1 = t.create_tier(name="tier1")
        with self.assertRaises(ValueError):   # Not enough tiers
            arff.validate()
        tier2 = t.create_tier(name="tier2")
        with self.assertRaises(ValueError):   # No class
            arff.validate()
        tier1.set_meta("weka_class", "")
        with self.assertRaises(ValueError):   # No attribute
            arff.validate()
        tier2.set_meta("weka_attribute", "")
        with self.assertRaises(ValueError):   # Empty class tier
            arff.validate()
        tier1.set_ctrl_vocab(None)
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(4))),
                                     sppasLabel(sppasTag('a'))))
        with self.assertRaises(ValueError):   # Not enough annotations in class tier
            arff.validate()
        tier1.set_ctrl_vocab(None)
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4), sppasPoint(6))),
                                     sppasLabel(sppasTag('b'))))

        with self.assertRaises(ValueError):   # Empty attribute tier
            arff.validate()
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))

        with self.assertRaises(ValueError):  # No instance time step nor anchor
            arff.validate()

        arff.set_meta("weka_instance_step", "0.04")

        # yes! it sounds good!
        arff.validate()

    def test_write_meta(self):
        """ Write the metadata of the Transcription object
        in the header of the ARFF file.
        """
        arff = sppasARFF()
        arff.set(self.trs)
        output = io.BytesIO()
        arff._write_metadata(output)
        lines = output.getvalue()
        self.assertEqual(len(lines.split("\n")), 3)  # 2 blank lines

        arff.set_meta("weka_instance_step", "0.04")
        output = io.BytesIO()
        arff._write_metadata(output)
        lines = output.getvalue()
        self.assertEqual(len(lines.split("\n")), 4)  # 2 blank lines + 1 meta data
        self.assertTrue("weka_instance_step" in lines)
        self.assertTrue("0.04" in lines)

    def test_write_relation(self):
        """ Write the name of the relation. """
        arff = sppasARFF()
        arff.set(self.trs)
        output = io.BytesIO()
        arff._write_relation(output)
        lines = output.getvalue()
        self.assertEqual(len(lines.split("\n")), 3)  # 1 blank line + 1 relation data
        self.assertTrue("@RELATION" in lines)
        self.assertTrue(self.trs.get_name() in lines)

    def test_write_attributes(self):
        """ Write the list of attributes. """
        arff = sppasARFF()
        arff.set(self.trs)
        output = io.BytesIO()
        self.tier1.set_meta("weka_class", "")
        self.tier2.set_meta("weka_attribute", "numeric")
        self.tier1.create_ctrl_vocab()
        self.tier2.create_ctrl_vocab()
        arff._write_attributes(output)
        lines = output.getvalue()
        self.assertTrue("@ATTRIBUTES" in lines)
        self.assertTrue("NUMERIC" in lines)

    def test_write_data(self):
        """ Write the list of attributes. """
        arff = sppasARFF()
        arff.set(self.trs)
        output = io.BytesIO()
        arff._write_data(output)
