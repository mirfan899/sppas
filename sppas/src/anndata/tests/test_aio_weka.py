# -*- coding:utf-8 -*-
import unittest
import os.path
import shutil
import io

from ..aio.weka import sppasWEKA, sppasARFF, sppasXRFF
from ..transcription import sppasTranscription
from ..annlocation.interval import sppasInterval
from ..annlocation.point import sppasPoint
from ..annlabel.label import sppasTag
from ..annlabel.label import sppasLabel
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation

from sppas.src.utils.fileutils import sppasFileUtils
from sppas.src.utils.makeunicode import u

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

    # -----------------------------------------------------------------

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

    # -----------------------------------------------------------------

    def test_check_metadata(self):
        """ Check the metadata and fix the variable members. """

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

    # -----------------------------------------------------------------

    def test_validate_annotations(self):
        """ Prepare data to be compatible. """

        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier1 = t.create_tier("The name")

        # TODO: unittest of validate_annotations() method.

    # -----------------------------------------------------------------

    def test_validate(self):
        """ Check the tiers to verify if everything is ok. """

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

    # -----------------------------------------------------------------

    def test_tier_is_attribute(self):
        """ Check if a tier is an attribute for the classification. """

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

    # -----------------------------------------------------------------

    def test_get_class_tier(self):
        """ Return the tier which is the class. """

        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier1 = t.create_tier(name="tier1")
        self.assertIsNone(weka._get_class_tier())
        tier1.set_meta("weka_class", "")
        self.assertEqual(weka._get_class_tier(), tier1)

    # -----------------------------------------------------------------

    def test_get_anchor_tier(self):
        """ Return the tier which will be used to create the instances. """

        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier1 = t.create_tier(name="tier1")
        self.assertIsNone(weka._get_anchor_tier())
        tier1.set_meta("weka_instance_anchor", "")
        self.assertEqual(weka._get_anchor_tier(), tier1)

    # -----------------------------------------------------------------

    def test_get_label(self):
        """ Return the sppasLabel() at the given time in the given tier.
            Return the empty label if no label was assigned at the given time.
        """

        empty = sppasLabel(sppasTag("none"))
        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)

        # Interval tier
        tier = t.create_tier(name="tierIntervals")
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.)))))
        tier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2.5), sppasPoint(4.))),
                                 sppasLabel(sppasTag('toto'))))
        self.assertEqual(weka._get_label(sppasPoint(0.), tier), empty)
        self.assertEqual(weka._get_label(sppasPoint(1.), tier), empty)
        self.assertEqual(weka._get_label(sppasPoint(2.), tier), empty)
        self.assertEqual(weka._get_label(sppasPoint(3.), tier), sppasLabel(sppasTag('toto')))
        self.assertEqual(weka._get_label(sppasPoint(4.), tier), empty)
        self.assertEqual(weka._get_label(sppasPoint(5.), tier), empty)
        tier[0].add_tag(sppasTag('titi'))
        self.assertEqual(weka._get_label(sppasPoint(2.), tier), sppasLabel(sppasTag('titi')))
        self.assertEqual(weka._get_label(sppasPoint(2.5), tier), sppasLabel(sppasTag('titi')))
        self.assertEqual(weka._get_label(sppasPoint(2.6), tier), sppasLabel(sppasTag('titi')))
        self.assertEqual(weka._get_label(sppasPoint(3.), tier), sppasLabel(sppasTag('toto')))

        # Point tier
        tierp = t.create_tier(name="tierPoints")
        tierp.append(sppasAnnotation(sppasLocation(sppasPoint(1.))))
        tierp.append(sppasAnnotation(sppasLocation(sppasPoint(5.)),
                                     sppasLabel(sppasTag('H*'))))
        tierp.append(sppasAnnotation(sppasLocation(sppasPoint(12.)),
                                     sppasLabel()))
        self.assertEqual(weka._get_label(sppasPoint(0.), tierp), empty)
        self.assertEqual(weka._get_label(sppasPoint(1.), tierp), empty)
        self.assertEqual(weka._get_label(sppasPoint(12.), tierp), empty)
        self.assertEqual(weka._get_label(sppasPoint(5.), tierp), sppasLabel(sppasTag('H*')))

    # -----------------------------------------------------------------

    def test_get_tag(self):
        """ Return the sppasTag() of at the given time in the given tier. """

        empty = sppasTag("none")
        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier = t.create_tier(name="tier")
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.)))))
        self.assertEqual(weka._get_tag(sppasPoint(2.), tier), empty)
        tier[0].add_tag(sppasTag('titi'))
        self.assertEqual(weka._get_tag(sppasPoint(2.), tier), sppasTag('titi'))
        tier[0].add_tag(sppasTag('toto'))
        self.assertEqual(weka._get_tag(sppasPoint(2.), tier), sppasTag('titi'))
        tier[0].add_tag(sppasTag('tata'), score=0.5)
        self.assertEqual(weka._get_tag(sppasPoint(2.), tier), sppasTag('tata'))
        tier[0].get_label().set_score(sppasTag('titi'), 1.)
        self.assertEqual(weka._get_tag(sppasPoint(2.), tier), sppasTag('titi'))
        tier[0].get_label().set_score(sppasTag('titi'), "a")
        tier[0].get_label().set_score(sppasTag('tata'), "b")
        tier[0].get_label().set_score(sppasTag('toto'), "c")
        self.assertEqual(weka._get_tag(sppasPoint(2.), tier), sppasTag('toto'))

    # -----------------------------------------------------------------

    def test_fix_all_possible_instance_steps(self):
        """ Fix all the possible time-points of the instances. """

        t = sppasTranscription()
        tier = t.create_tier(name="tier")
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4.), sppasPoint(5.))),
                                    sppasLabel(sppasTag("toto"))))
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
                                    sppasLabel(sppasTag("none"))))

        all_points = sppasWEKA._fix_all_possible_instance_steps(0., 10., time_step=0.01)  # phoneme frames
        self.assertEqual(len(all_points), 1000)
        all_points = sppasWEKA._fix_all_possible_instance_steps(0., 10., time_step=0.04)  # video frames
        self.assertEqual(len(all_points), 250)

        all_points = sppasWEKA._fix_all_possible_instance_steps(0., 10., anchor_tier=tier)
        self.assertEqual(len(all_points), 2)
        self.assertTrue(sppasPoint(4.5, 0.5) in all_points)
        self.assertTrue(sppasPoint(5.5, 0.5) in all_points)

    # -----------------------------------------------------------------

    def test_fix_instance_steps(self):
        """ Fix the time-points to create the instances and the
            tag of the class to predict by the classification system.
        """

        weka = sppasWEKA()
        t = sppasTranscription()
        weka.set(t)
        tier = t.create_tier(name="tier")
        tier.set_meta('weka_class', '')
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4.), sppasPoint(5.))),
                                    sppasLabel(sppasTag("toto"))))
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
                                    sppasLabel(sppasTag("none"))))

        weka.set_meta('weka_instance_step', '0.1')
        all_points = sppasWEKA._fix_all_possible_instance_steps(1., 6., time_step=0.1)
        self.assertEqual(len(all_points), 50)
        instances = weka._fix_instance_steps()
        self.assertEqual(len(instances), 10)  # only "toto", with 10 steps

        weka.pop_meta('weka_instance_step')
        instances = weka._fix_instance_steps()
        self.assertEqual(len(instances), 0)

        tier.set_meta('weka_instance_anchor', '')
        instances = weka._fix_instance_steps()
        self.assertEqual(len(instances), 1)  # only "toto
        self.assertEqual(instances[0], (sppasPoint(4.5, 0.5), "toto"))

    # -----------------------------------------------------------------

    def test_scores_to_probas(self):
        """ Convert scores of a label to probas. """

        self.assertFalse(sppasWEKA._scores_to_probas(None))
        self.assertFalse(sppasWEKA._scores_to_probas(sppasLabel()))

        # only one tag, without score (the most common situation)
        tag = sppasTag("")
        label = sppasLabel(tag)
        self.assertTrue(sppasWEKA._scores_to_probas(label))
        self.assertEqual(label.get_score(tag), 1.)

        # only one tag, with a score (numerical or string)
        tag = sppasTag("")
        label = sppasLabel(tag, 3)
        self.assertTrue(sppasWEKA._scores_to_probas(label))
        self.assertEqual(label.get_score(tag), 1.)
        label = sppasLabel(tag, "A")
        self.assertTrue(sppasWEKA._scores_to_probas(label))
        self.assertEqual(label.get_score(tag), 1.)

        # several tags, all with scores
        tag1 = sppasTag("a")
        tag2 = sppasTag("b")
        tag3 = sppasTag("c")
        label = sppasLabel(tag1, 3)
        label.append(tag2, 2)
        label.append(tag3, 5)
        self.assertTrue(sppasWEKA._scores_to_probas(label))
        self.assertEqual(label.get_score(tag1), 0.3)
        self.assertEqual(label.get_score(tag2), 0.2)
        self.assertEqual(label.get_score(tag3), 0.5)

        # several tags, all without scores
        label = sppasLabel(tag1)
        label.append(tag2)
        self.assertTrue(sppasWEKA._scores_to_probas(label))
        self.assertEqual(label.get_score(tag1), 0.5)
        self.assertEqual(label.get_score(tag2), 0.5)

        # several tags, some without scores
        label = sppasLabel(tag1, 7)
        label.append(tag2, 2)
        label.append(tag3)    # score will be 1
        self.assertTrue(sppasWEKA._scores_to_probas(label))
        self.assertEqual(label.get_score(tag1), 0.7)
        self.assertEqual(label.get_score(tag2), 0.2)
        self.assertEqual(label.get_score(tag3), 0.1)

        # several tags, with "min" function
        # several tags, some without scores
        label = sppasLabel(tag1, 7)
        label.append(tag2, 2)
        label.append(tag3)    # score will be 1
        label.set_function_score(min)

        self.assertTrue(sppasWEKA._scores_to_probas(label))
        self.assertEqual(round(label.get_score(tag1), 2), 0.2)
        self.assertEqual(round(label.get_score(tag2), 2), 0.7)
        self.assertEqual(round(label.get_score(tag3), 2), 0.1)

    # -----------------------------------------------------------------

    def test_fix_data_instance(self):
        """ Fix the data content of an instance. """

        weka = sppasWEKA()
        t = sppasTranscription()
        tier1 = t.create_tier(name="tier1")
        tier2 = t.create_tier(name="tier2")
        tier3 = t.create_tier(name="tier3")
        weka.set(t)
        weka.set_meta("weka_instance_step", "0.1")
        tier1.set_meta("weka_class", "")
        tier2.set_meta("weka_attribute", "string")
        tier3.set_meta("weka_attribute", "numeric")

        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4.), sppasPoint(5.))),
                                     sppasLabel(sppasTag("toto"))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
                                     sppasLabel(sppasTag("none"))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7.), sppasPoint(10.))),
                                     sppasLabel(sppasTag("titi"))))

        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(5))),
                                     sppasLabel(sppasTag('a'))))
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(8), sppasPoint(10))),
                                     sppasLabel(sppasTag('b'))))

        tier3.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))),
                                     sppasLabel(sppasTag('b'))))
        tier3.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(5))),
                                     sppasLabel(sppasTag('a'))))
        tier3.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(8), sppasPoint(10))),
                                     sppasLabel(sppasTag('b'))))
        tier1.create_ctrl_vocab()
        tier2.create_ctrl_vocab()
        tier3.create_ctrl_vocab()

        instance_steps = weka._fix_instance_steps()
        for point, class_str in instance_steps:
            data = weka._fix_data_instance(point)
            if 4. < point < 5.:
                self.assertEqual(class_str, "toto")
                self.assertEqual(data[0], u("a"))
            elif 7. < point < 8.:
                self.assertEqual(class_str, "titi")
                self.assertEqual(data[0], u("none"))
            elif 8. < point < 10.:
                self.assertEqual(class_str, "titi")
                self.assertEqual(data[0], u("b"))

# ---------------------------------------------------------------------------


class TestFileFormats(unittest.TestCase):
    """
    Represents an ARFF or XRFF file, the native formats of WEKA.

    TODO: test XRFF output.

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

    # -----------------------------------------------------------------

    def test_write_header(self):
        """ Write the creator, etc. in the header of an ARFF file. """

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

    # -----------------------------------------------------------------

    def test_write_meta(self):
        """ Write the metadata of the Transcription object
        in the header of an ARFF file.

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

    # -----------------------------------------------------------------

    def test_write_relation(self):
        """ Write the name of the relation. """

        # test ARFF
        arff = sppasARFF()
        arff.set(self.trs)
        output = io.BytesIO()
        arff._write_relation(output)
        lines = output.getvalue()
        self.assertEqual(len(lines.split("\n")), 3)  # 1 blank line + 1 relation data
        self.assertTrue("@RELATION" in lines)
        self.assertTrue(self.trs.get_name() in lines)

    # -----------------------------------------------------------------

    def test_write_attributes(self):
        """ Write the list of attributes. """

        # test ARFF
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

        # test XRFF
        xrff = sppasXRFF()
        arff.set(self.trs)
        output = io.BytesIO()
        arff._write_relation(output)

    # -----------------------------------------------------------------

    def test_write_data(self):
        """ Write the list of attributes. """

        t = sppasTranscription()
        tier1 = t.create_tier(name="tier1")
        tier2 = t.create_tier(name="tier2")
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4.), sppasPoint(5.))),
                                     sppasLabel(sppasTag("toto"))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
                                     sppasLabel(sppasTag("none"))))
        tier1.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7.), sppasPoint(10.))),
                                     sppasLabel(sppasTag("titi"))))
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(5)))))
        tier2.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(8), sppasPoint(10)))))
        tier1.create_ctrl_vocab()
        tier2.create_ctrl_vocab()

        weka = sppasWEKA()
        weka.set(t)
        weka.set_meta("weka_instance_step", "0.1")
        tier1.set_meta("weka_class", "")
        tier2.set_meta("weka_attribute", "numeric")

        # test ARFF
        arff = sppasARFF()
        arff.set(weka)
        output = io.BytesIO()
        arff._write_data(output)
        # TODO: test output.getvalue() content

        # test XRFF (with the same data exactly!)
        xrff = sppasXRFF()
        xrff.set(weka)
        output = io.BytesIO()
        xrff._write_instances(output)
        # TODO: test output.getvalue() content
