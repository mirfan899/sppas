# -*- coding:utf-8 -*-

import unittest

from ..anndataexc import AnnDataTypeError
from ..anndataexc import CtrlVocabContainsError

from ..annlocation.location import sppasLocation
from ..annlocation.disjoint import sppasDisjoint
from ..annlocation.interval import sppasInterval
from ..annlocation.point import sppasPoint
from ..annlabel.label import sppasTag
from ..annlabel.label import sppasLabel
from ..annotation import sppasAnnotation
from ..tier import sppasTier

from ..media import sppasMedia
from ..ctrlvocab import sppasCtrlVocab

# ---------------------------------------------------------------------------


class TestTier(unittest.TestCase):

    def setUp(self):
        self.tierP = sppasTier("PointTier")
        self.tierI = sppasTier("IntervalTier")
        for i in range(10):
            self.tierP.append(sppasAnnotation(sppasLocation(sppasPoint(i)), sppasLabel(sppasTag("label"+str(i)))))
            self.tierI.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))), sppasLabel(sppasTag("label"+str(i)))))

    def test_metadata(self):
        tierP = sppasTier()
        tierI = sppasTier()
        tierP.set_meta("key", "value")
        tierI.set_meta('key', "value")
        self.assertEqual(tierI.get_meta('key'), tierP.get_meta('key'))
        self.assertEqual(tierI.get_meta('toto'), '')

    def test_name(self):
        tierP = sppasTier()
        self.assertEqual(len(tierP.get_name()), 36)
        tierP.set_name('test')
        self.assertEqual(tierP.get_name(), 'test')
        tierP.set_name('    \r\t\ntest    \r\t\n')
        self.assertEqual(tierP.get_name(), 'test')
        tierP = sppasTier('    \r\t\ntest    \r\t\n')
        self.assertEqual(tierP.get_name(), 'test')

    def test_media(self):
        m = sppasMedia("toto.wav")
        tierP = sppasTier()
        tierP.set_media(m)
        tierI = sppasTier(media=m)
        self.assertEqual(tierI.get_media(), tierP.get_media())
        with self.assertRaises(AnnDataTypeError):
            tierI = sppasTier(media="media")

    def test_ctrl_vocab(self):
        voc = sppasCtrlVocab("Verbal Strategies")
        self.assertTrue(voc.add(sppasTag("definition")))
        self.assertTrue(voc.add(sppasTag("example")))
        self.assertTrue(voc.add(sppasTag("comparison")))
        self.assertTrue(voc.add(sppasTag("gap filling with sound")))
        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))), sppasLabel(sppasTag("definition")))
        a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(6), sppasPoint(7))), sppasLabel(sppasTag("gap filling with sound")))
        a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7), sppasPoint(9))), sppasLabel(sppasTag("biz")))
        # assign a ctrl_vocab after appending annotations
        tiercv = sppasTier()
        tiercv.set_ctrl_vocab(voc)
        tiercv.append(a1)
        tiercv.append(a2)
        with self.assertRaises(ValueError):
            tiercv.append(a3)
        with self.assertRaises(CtrlVocabContainsError):
            tiercv[0].set_best_tag(sppasTag("error"))
        # assign a ctrl_vocab before appending annotations
        tiercv = sppasTier(ctrl_vocab=voc)
        tiercv.append(a1)
        tiercv.append(a2)
        with self.assertRaises(ValueError):
            tiercv.append(a3)
        with self.assertRaises(ValueError):
            tiercv.add(a3)
        with self.assertRaises(CtrlVocabContainsError):
            tiercv[0].set_best_tag(sppasTag("error"))
        with self.assertRaises(CtrlVocabContainsError):
            tiercv[0].add_tag(sppasTag("error"))

    def test_ann_is_empty(self):
        tier = sppasTier()
        self.assertTrue(tier.is_empty())
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))
        self.assertFalse(tier.is_empty())

    def test_type(self):
        tier = sppasTier()
        self.assertFalse(tier.is_point())
        self.assertFalse(tier.is_interval())
        self.assertFalse(tier.is_disjoint())
        tierP = sppasTier()
        tierP.append(sppasAnnotation(sppasLocation(sppasPoint(1))))
        self.assertTrue(tierP.is_point())
        self.assertFalse(tierP.is_interval())
        self.assertFalse(tierP.is_disjoint())
        with self.assertRaises(TypeError):
            tierP.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1),sppasPoint(2)))))
        tierI = sppasTier()
        tierI.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2)))))
        self.assertFalse(tierI.is_point())
        self.assertTrue(tierI.is_interval())
        self.assertFalse(tierI.is_disjoint())
        tierD = sppasTier()
        tierD.append(sppasAnnotation(sppasLocation(sppasDisjoint([sppasInterval(sppasPoint(1), sppasPoint(2))]))))
        self.assertFalse(tierD.is_point())
        self.assertFalse(tierD.is_interval())
        self.assertTrue(tierD.is_disjoint())


