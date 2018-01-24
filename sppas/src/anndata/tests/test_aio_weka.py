# -*- coding:utf-8 -*-
import sys
import unittest
import os.path
import shutil
import io

import sppas
from ..aio.weka import sppasWEKA, sppasARFF
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


class TestWEKA(unittest.TestCase):
    """
    Represents a WEKA instance test sets.
    """
    def test_members(self):
        weka = sppasWEKA()
        self.assertTrue(weka.multi_tiers_support())
        self.assertFalse(weka.no_tiers_support())
        self.assertTrue(weka.metadata_support())
        self.assertTrue(weka.ctrl_vocab_support())
        self.assertFalse(weka.media_support())
        self.assertFalse(weka.hierarchy_support())
        self.assertTrue(weka.point_support())
        self.assertTrue(weka.interval_support())
        self.assertTrue(weka.disjoint_support())
        self.assertFalse(weka.alternative_localization_support())
        self.assertTrue(weka.alternative_tag_support())
        self.assertFalse(weka.radius_support())
        self.assertFalse(weka.gaps_support())
        self.assertTrue(weka.overlaps_support())

        self.assertEqual(weka._uncertain_annotation_tag, "?")
        self.assertEqual(weka._epsilon_proba, 0.001)

    def test_setters(self):
        weka = sppasWEKA()
        self.assertEqual(weka.get_max_class_tags(), 10)
        weka.set_max_class_tags(5)
        self.assertEqual(weka.get_max_class_tags(), 5)
        with self.assertRaises(ValueError):
            weka.set_max_class_tags(1)
        with self.assertRaises(ValueError):
            weka.check_max_class_tags(10)

        self.assertEqual(weka._max_attributes_tags, 20)
        weka.set_max_attributes_tags(5)
        self.assertEqual(weka._max_attributes_tags, 5)
        with self.assertRaises(ValueError):
            weka.set_max_attributes_tags(0)
        with self.assertRaises(ValueError):
            weka.check_max_attributes_tags(10)

        self.assertEqual(weka._empty_annotation_tag, "none")
        weka.set_empty_annotation_tag("toto")
        self.assertEqual(weka._empty_annotation_tag, "toto")
        with self.assertRaises(ValueError):
            weka.set_empty_annotation_tag(" \n")

        self.assertEqual(weka._uncertain_annotation_tag, "?")
        weka.set_uncertain_annotation_tag("~")
        self.assertEqual(weka._uncertain_annotation_tag, "~")
        with self.assertRaises(ValueError):
            weka.set_uncertain_annotation_tag(" \n")

    def test_check_metadata(self):
        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        self.assertEqual(weka.get_max_class_tags(), 10)
        self.assertEqual(weka._max_attributes_tags, 20)
        self.assertEqual(weka._empty_annotation_tag, "none")
        self.assertEqual(weka._uncertain_annotation_tag, "?")
        weka.set_meta("weka_max_class_tags", "50")
        weka.set_meta("weka_max_attributes_tags", "30")
        weka.set_meta("weka_empty_annotation_tag", "~")
        weka.set_meta("weka_uncertain_annotation_tag", "%")
        weka.check_metadata()
        self.assertEqual(weka.get_max_class_tags(), "50")
        self.assertEqual(weka._max_attributes_tags, "30")
        self.assertEqual(weka._empty_annotation_tag, "~")
        self.assertEqual(weka._uncertain_annotation_tag, "%")
        weka.set_meta("weka_max_class_tags", "0")
        with self.assertRaises(ValueError):
            weka.check_metadata()
        weka.set_meta("weka_max_attributes_tags", "0")
        with self.assertRaises(ValueError):
            weka.check_metadata()
        weka.set_meta("weka_empty_annotation_tag", "")
        with self.assertRaises(ValueError):
            weka.check_metadata()
        weka.set_meta("weka_uncertain_annotation_tag", "")
        with self.assertRaises(ValueError):
            weka.check_metadata()

    def test_validate_annotations(self):
        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier1 = t.create_tier("The name")
        # TODO

    def test_validate(self):
        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        with self.assertRaises(ValueError):   # Empty transcription
            weka.validate()
        tier1 = t.create_tier(name="tier1")
        with self.assertRaises(ValueError):   # Not enough tiers
            weka.validate()
        tier2 = t.create_tier(name="tier2")
        with self.assertRaises(ValueError):   # No class
            weka.validate()
        tier1.set_meta("weka_class", "")
        with self.assertRaises(ValueError):   # No attribute
            weka.validate()
        tier2.set_meta("weka_attribute", "")
        with self.assertRaises(ValueError):   # Empty class tier
            weka.validate()
        tier1.set_ctrl_vocab(None)
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(4))),
                                     sppasLabel(sppasTag('a'))))
        tier1.create_ctrl_vocab()
        with self.assertRaises(ValueError):   # Not enough annotations in class tier
            weka.validate()
        tier1.set_ctrl_vocab(None)
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4), sppasPoint(6))),
                                     sppasLabel(sppasTag('b'))))
        tier1.create_ctrl_vocab()
        with self.assertRaises(ValueError):   # Empty attribute tier
            weka.validate()
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))

        with self.assertRaises(ValueError):  # No instance time step nor anchor
            weka.validate()

        weka.set_meta("weka_instance_step", "0.04")

        # yes! it sounds good!
        weka.validate()

    def test_tier_is_attribute(self):
        t = sppasTranscription()
        tier1 = t.create_tier(name="tier1")
        is_att, is_num = sppasWEKA._tier_is_attribute(tier1)
        self.assertFalse(is_att)
        self.assertFalse(is_num)
        tier1.set_meta("weka_attribute", "")
        is_att, is_num = sppasWEKA._tier_is_attribute(tier1)
        self.assertTrue(is_att)
        self.assertFalse(is_num)
        tier1.set_meta("weka_attribute", "numeric")
        is_att, is_num = sppasWEKA._tier_is_attribute(tier1)
        self.assertTrue(is_att)
        self.assertTrue(is_num)

    def test_get_class_tier(self):
        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier1 = t.create_tier(name="tier1")
        self.assertIsNone(weka._get_class_tier())
        tier1.set_meta("weka_class", "")
        self.assertEqual(weka._get_class_tier(), tier1)

    def test_get_anchor_tier(self):
        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier1 = t.create_tier(name="tier1")
        self.assertIsNone(weka._get_anchor_tier())
        tier1.set_meta("weka_instance_anchor", "")
        self.assertEqual(weka._get_anchor_tier(), tier1)

    def test_get_label(self):
        # TODO
        pass

    def test_get_tag(self):
        # TODO
        pass

    def test_fix_instance_steps(self):
        # TODO
        pass

    def test_scores_to_probas(self):
        # TODO
        pass

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
        self.tier2.set_meta("weka_attribute", "string")
        self.tier1.create_ctrl_vocab()
        self.tier2.create_ctrl_vocab()
        arff._write_attributes(output)
        lines = output.getvalue()
        self.assertTrue("@ATTRIBUTES" in lines)
        # self.assertTrue(self.tier1.get_name() in lines)
        # self.assertTrue(self.tier2.get_name() in lines)

    def test_write_data(self):
        """ Write the list of attributes. """
        arff = sppasARFF()
        arff.set(self.trs)
        arff.set_meta("weka_instance_step", "0.04")
        self.tier1.set_meta("weka_class", "")
        self.tier2.set_meta("weka_attribute", "numeric")
        output = io.BytesIO()
        arff._write_data(output)
