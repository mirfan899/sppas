# -*- coding:utf-8 -*-

import unittest
import random

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
        pass

    # def test_metadata(self):
    #     tierP = sppasTier()
    #     tierI = sppasTier()
    #     tierP.set_meta("key", "value")
    #     tierI.set_meta('key', "value")
    #     self.assertEqual(tierI.get_meta('key'), tierP.get_meta('key'))
    #     self.assertEqual(tierI.get_meta('toto'), '')
    #
    # def test_name(self):
    #     tierP = sppasTier()
    #     self.assertEqual(len(tierP.get_name()), 36)
    #     tierP.set_name('test')
    #     self.assertEqual(tierP.get_name(), 'test')
    #     tierP.set_name('    \r\t\ntest    \r\t\n')
    #     self.assertEqual(tierP.get_name(), 'test')
    #     tierP = sppasTier('    \r\t\ntest    \r\t\n')
    #     self.assertEqual(tierP.get_name(), 'test')
    #
    # def test_media(self):
    #     m = sppasMedia("toto.wav")
    #     tierP = sppasTier()
    #     tierP.set_media(m)
    #     tierI = sppasTier(media=m)
    #     self.assertEqual(tierI.get_media(), tierP.get_media())
    #     with self.assertRaises(AnnDataTypeError):
    #         tierI = sppasTier(media="media")
    #
    # def test_ctrl_vocab(self):
    #     voc = sppasCtrlVocab("Verbal Strategies")
    #     self.assertTrue(voc.add(sppasTag("definition")))
    #     self.assertTrue(voc.add(sppasTag("example")))
    #     self.assertTrue(voc.add(sppasTag("comparison")))
    #     self.assertTrue(voc.add(sppasTag("gap filling with sound")))
    #     a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))), sppasLabel(sppasTag("definition")))
    #     a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(6), sppasPoint(7))), sppasLabel(sppasTag("gap filling with sound")))
    #     a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7), sppasPoint(9))), sppasLabel(sppasTag("biz")))
    #     # assign a ctrl_vocab after appending annotations
    #     tiercv = sppasTier()
    #     tiercv.set_ctrl_vocab(voc)
    #     tiercv.append(a1)
    #     tiercv.append(a2)
    #     with self.assertRaises(ValueError):
    #         tiercv.append(a3)
    #     with self.assertRaises(CtrlVocabContainsError):
    #         tiercv[0].set_best_tag(sppasTag("error"))
    #     # assign a ctrl_vocab before appending annotations
    #     tiercv = sppasTier(ctrl_vocab=voc)
    #     tiercv.append(a1)
    #     tiercv.append(a2)
    #     with self.assertRaises(ValueError):
    #         tiercv.append(a3)
    #     with self.assertRaises(ValueError):
    #         tiercv.add(a3)
    #     with self.assertRaises(CtrlVocabContainsError):
    #         tiercv[0].set_best_tag(sppasTag("error"))
    #     with self.assertRaises(CtrlVocabContainsError):
    #         tiercv[0].add_tag(sppasTag("error"))
    #
    # def test_ann_is_empty(self):
    #     tier = sppasTier()
    #     self.assertTrue(tier.is_empty())
    #     tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))
    #     self.assertFalse(tier.is_empty())
    #
    # def test_type(self):
    #     tier = sppasTier()
    #     self.assertFalse(tier.is_point())
    #     self.assertFalse(tier.is_interval())
    #     self.assertFalse(tier.is_disjoint())
    #     tierP = sppasTier()
    #     tierP.append(sppasAnnotation(sppasLocation(sppasPoint(1))))
    #     self.assertTrue(tierP.is_point())
    #     self.assertFalse(tierP.is_interval())
    #     self.assertFalse(tierP.is_disjoint())
    #     with self.assertRaises(TypeError):
    #         tierP.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1),sppasPoint(2)))))
    #     tierI = sppasTier()
    #     tierI.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2)))))
    #     self.assertFalse(tierI.is_point())
    #     self.assertTrue(tierI.is_interval())
    #     self.assertFalse(tierI.is_disjoint())
    #     tierD = sppasTier()
    #     tierD.append(sppasAnnotation(sppasLocation(sppasDisjoint([sppasInterval(sppasPoint(1), sppasPoint(2))]))))
    #     self.assertFalse(tierD.is_point())
    #     self.assertFalse(tierD.is_interval())
    #     self.assertTrue(tierD.is_disjoint())
    #
    # def test_append(self):
    #     # Without radius value
    #     tier = sppasTier()
    #     a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
    #     a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(9))))
    #     a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7), sppasPoint(11))))
    #     a4 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(9), sppasPoint(11))))
    #     tier.append(a1)
    #     self.assertEqual(len(tier), 1)
    #     tier.append(a2)
    #     self.assertEqual(len(tier), 2)
    #     with self.assertRaises(ValueError):
    #         tier.append(a3)
    #     self.assertEqual(len(tier), 2)
    #     tier.append(a4)
    #     # With radius value
    #     tier = sppasTier()
    #     a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1, 1), sppasPoint(3, 1))))
    #     a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2, 1), sppasPoint(9, 1))))
    #     tier.append(a1)
    #     tier.append(a2)
    #
    # def test_intervals_index(self):
    #     tier = sppasTier()
    #     a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
    #     a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(9))))
    #     a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(11))))
    #     a4 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(11), sppasPoint(12))))
    #     a5 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(11), sppasPoint(15))))
    #     a6 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(11), sppasPoint(20))))
    #     a7 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(15), sppasPoint(20))))
    #     tier.append(a1)
    #     tier.append(a2)
    #     tier.add(a3)
    #     tier.add(a4)
    #     tier.add(a5)
    #     tier.add(a6)
    #     tier.add(a7)
    #     self.assertEqual(0, tier.lindex(sppasPoint(1)))
    #     self.assertEqual(1, tier.lindex(sppasPoint(3)))
    #     self.assertEqual(3, tier.lindex(sppasPoint(11)))
    #     self.assertEqual(-1, tier.lindex(sppasPoint(0)))
    #     self.assertEqual(-1, tier.lindex(sppasPoint(9)))
    #     self.assertEqual(-1, tier.lindex(sppasPoint(12)))
    #     self.assertEqual(0, tier.rindex(sppasPoint(3)))
    #     self.assertEqual(3, tier.rindex(sppasPoint(12)))
    #     self.assertEqual(4, tier.rindex(sppasPoint(15)))
    #     self.assertEqual(6, tier.rindex(sppasPoint(20)))
    #     tier.pop(4)
    #     self.assertEqual(0, tier.mindex(sppasPoint(2), bound=-1))
    #     self.assertEqual(0, tier.mindex(sppasPoint(2)))
    #     self.assertEqual(0, tier.mindex(sppasPoint(2), bound=1))
    #     self.assertEqual(0, tier.mindex(sppasPoint(1), bound=-1))
    #     self.assertEqual(-1, tier.mindex(sppasPoint(1), bound=0))
    #     self.assertEqual(-1, tier.mindex(sppasPoint(1), bound=1))
    #     self.assertEqual(1, tier.mindex(sppasPoint(3), bound=-1))
    #     self.assertEqual(-1, tier.mindex(sppasPoint(3), bound=0))
    #     self.assertEqual(0, tier.mindex(sppasPoint(3), bound=1))
    #
    # def test_remove(self):
    #     tier = sppasTier()
    #     a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
    #     a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(9))))
    #     a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7), sppasPoint(11))))
    #     a4 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(9), sppasPoint(11))))
    #     tier.append(a1)
    #     nb = tier.remove(sppasPoint(1), sppasPoint(3))
    #     self.assertEqual(nb, 1)
    #     self.assertEqual(len(tier), 0)
    #     tier.append(a1)
    #     tier.append(a2)
    #     nb = tier.remove(sppasPoint(1), sppasPoint(3))
    #     self.assertEqual(nb, 1)
    #     self.assertEqual(len(tier), 1)
    #     nb = tier.remove(sppasPoint(3), sppasPoint(9))
    #     self.assertEqual(nb, 1)
    #     self.assertEqual(len(tier), 0)
    #     tier.append(a1)
    #     tier.append(a2)
    #     nb = tier.remove(sppasPoint(1), sppasPoint(9))
    #     self.assertEqual(nb, 2)
    #     self.assertEqual(len(tier), 0)
    #     tier.append(a1)
    #     tier.append(a2)
    #     tier.add(a3)
    #     nb = tier.remove(sppasPoint(10), sppasPoint(10))
    #     self.assertEqual(nb, 0)
    #     self.assertEqual(len(tier), 3)

    def test_add(self):
        tier = sppasTier()
        localizations = [sppasInterval(sppasPoint(1.), sppasPoint(2.)),
                         sppasInterval(sppasPoint(1.5), sppasPoint(2.)),
                         sppasInterval(sppasPoint(1.8), sppasPoint(2.)),
                         sppasInterval(sppasPoint(1.8), sppasPoint(2.5)),
                         sppasInterval(sppasPoint(2.), sppasPoint(2.3)),
                         sppasInterval(sppasPoint(2.), sppasPoint(2.5)),
                         sppasInterval(sppasPoint(2.), sppasPoint(3.)),
                         sppasInterval(sppasPoint(2.4), sppasPoint(4.)),
                         sppasInterval(sppasPoint(2.5), sppasPoint(3.))
                         ]
        annotations = [sppasAnnotation(sppasLocation(t)) for t in localizations]
        for i, a in enumerate(annotations):
            tier.add(a)
            self.assertEqual(len(tier), i+1)
        tierrandom = sppasTier()
        random.shuffle(annotations)
        for i, a in enumerate(annotations):
            tierrandom.add(a)
            self.assertEqual(len(tierrandom), i+1)
        self.assertEqual(len(tier), len(tierrandom))
        for a, ar in zip(tier, tierrandom):
            self.assertEqual(a, ar)

    def test_pop(self):
        tier = sppasTier()
        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(9))))
        tier.append(a1)
        tier.pop()
        self.assertEqual(len(tier), 0)
        tier.append(a1)
        tier.append(a2)
        tier.pop(0)
        a = tier.find(sppasPoint(0), sppasPoint(3))
        self.assertEqual(len(a), 0)
        a = tier.find(sppasPoint(2), sppasPoint(7))
        self.assertEqual(len(a), 1)


