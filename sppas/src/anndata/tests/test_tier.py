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

    def test_append(self):
        # Without radius value
        tier = sppasTier()
        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(9))))
        a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7), sppasPoint(11))))
        a4 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(9), sppasPoint(11))))
        tier.append(a1)
        self.assertEqual(len(tier), 1)
        tier.append(a2)
        self.assertEqual(len(tier), 2)
        with self.assertRaises(ValueError):
            tier.append(a3)
        self.assertEqual(len(tier), 2)
        tier.append(a4)
        # With radius value
        tier = sppasTier()
        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1, 1), sppasPoint(3, 1))))
        a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2, 1), sppasPoint(9, 1))))
        tier.append(a1)
        tier.append(a2)

    def test_intervals_index(self):
        tier = sppasTier()
        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(9))))
        a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(11))))
        a4 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(11), sppasPoint(12))))
        a5 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(11), sppasPoint(15))))
        a6 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(11), sppasPoint(20))))
        a7 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(15), sppasPoint(20))))
        tier.append(a1)
        tier.append(a2)
        tier.add(a3)
        tier.add(a4)
        tier.add(a5)
        tier.add(a6)
        tier.add(a7)
        self.assertEqual(0, tier.lindex(sppasPoint(1)))
        self.assertEqual(1, tier.lindex(sppasPoint(3)))
        self.assertEqual(3, tier.lindex(sppasPoint(11)))
        self.assertEqual(-1, tier.lindex(sppasPoint(0)))
        self.assertEqual(-1, tier.lindex(sppasPoint(9)))
        self.assertEqual(-1, tier.lindex(sppasPoint(12)))
        self.assertEqual(0, tier.rindex(sppasPoint(3)))
        self.assertEqual(3, tier.rindex(sppasPoint(12)))
        self.assertEqual(4, tier.rindex(sppasPoint(15)))
        self.assertEqual(6, tier.rindex(sppasPoint(20)))
        tier.pop(4)
        self.assertEqual(0, tier.mindex(sppasPoint(2), bound=-1))
        self.assertEqual(0, tier.mindex(sppasPoint(2)))
        self.assertEqual(0, tier.mindex(sppasPoint(2), bound=1))
        self.assertEqual(0, tier.mindex(sppasPoint(1), bound=-1))
        self.assertEqual(-1, tier.mindex(sppasPoint(1), bound=0))
        self.assertEqual(-1, tier.mindex(sppasPoint(1), bound=1))
        self.assertEqual(1, tier.mindex(sppasPoint(3), bound=-1))
        self.assertEqual(-1, tier.mindex(sppasPoint(3), bound=0))
        self.assertEqual(0, tier.mindex(sppasPoint(3), bound=1))

    def test_remove(self):
        tier = sppasTier()
        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(9))))
        a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7), sppasPoint(11))))
        a4 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(9), sppasPoint(11))))
        tier.append(a1)
        nb = tier.remove(sppasPoint(1), sppasPoint(3))
        self.assertEqual(nb, 1)
        self.assertEqual(len(tier), 0)
        tier.append(a1)
        tier.append(a2)
        nb = tier.remove(sppasPoint(1), sppasPoint(3))
        self.assertEqual(nb, 1)
        self.assertEqual(len(tier), 1)
        nb = tier.remove(sppasPoint(3), sppasPoint(9))
        self.assertEqual(nb, 1)
        self.assertEqual(len(tier), 0)
        tier.append(a1)
        tier.append(a2)
        nb = tier.remove(sppasPoint(1), sppasPoint(9))
        self.assertEqual(nb, 2)
        self.assertEqual(len(tier), 0)
        tier.append(a1)
        tier.append(a2)
        tier.add(a3)
        nb = tier.remove(sppasPoint(10), sppasPoint(10))
        self.assertEqual(nb, 0)
        self.assertEqual(len(tier), 3)

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
            self.assertTrue(a is ar)

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

    def test_find_interval(self):
        tier = sppasTier()
        for i in range(0, 5):
            tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))))

        annotations = tier.find(sppasPoint(0), sppasPoint(5))
        self.assertEqual(len(annotations), len(tier))
        for x, y in zip(tier, annotations):
            self.assertTrue(x is y)

        annotations = tier.find(sppasPoint(0), sppasPoint(5), overlaps=False)
        self.assertEqual(len(annotations), len(tier))
        for x, y in zip(tier, annotations):
            self.assertTrue(x is y)

        annotations = tier.find(sppasPoint(0.5), sppasPoint(5))
        self.assertEqual(len(annotations), len(tier))
        for x, y in zip(tier, annotations):
            self.assertTrue(x is y)

        annotations = tier.find(sppasPoint(0.5), sppasPoint(5), overlaps=False)
        self.assertEqual(len(annotations), len(tier)-1)

        annotations = tier.find(sppasPoint(0.5), sppasPoint(5.5))
        self.assertEqual(len(annotations), len(tier))
        for x, y in zip(tier, annotations):
            self.assertTrue(x is y)

        annotations = tier.find(sppasPoint(0.5), sppasPoint(4.5), overlaps=False)
        self.assertEqual(len(annotations), len(tier)-2)

        annotations = tier.find(sppasPoint(3.5), sppasPoint(4.5))
        self.assertEqual(len(annotations), 2)
        self.assertTrue(annotations[0] is tier[-2])
        self.assertTrue(annotations[1] is tier[-1])

        annotations = tier.find(sppasPoint(3.5), sppasPoint(3.8))
        self.assertEqual(len(annotations), 1)

        annotations = tier.find(sppasPoint(3.5), sppasPoint(3.8), overlaps=False)
        self.assertEqual(annotations, [])

        annotations = tier.find(sppasPoint(3), sppasPoint(4))
        self.assertTrue(annotations[0] is tier[-2])

        annotations = tier.find(sppasPoint(3), sppasPoint(4), overlaps=False)
        self.assertTrue(annotations[0] is tier[-2])

        annotations = tier.find(sppasPoint(6), sppasPoint(7), overlaps=True)
        self.assertEqual(annotations, [])

        annotations = tier.find(sppasPoint(6), sppasPoint(7), overlaps=False)
        self.assertEqual(annotations, [])

    # -----------------------------------------------------------------------

    def test_find_overlapped_intervals(self):
        tier = sppasTier("IntervalsTier")
        localizations = [sppasInterval(sppasPoint(1.), sppasPoint(2.)),    # 0
                         sppasInterval(sppasPoint(1.5), sppasPoint(2.)),   # 1
                         sppasInterval(sppasPoint(1.8), sppasPoint(2.)),   # 2
                         sppasInterval(sppasPoint(1.8), sppasPoint(2.5)),  # 3
                         sppasInterval(sppasPoint(2.), sppasPoint(2.3)),   # 4
                         sppasInterval(sppasPoint(2.), sppasPoint(2.5)),   # 5
                         sppasInterval(sppasPoint(2.), sppasPoint(3.)),    # 6
                         sppasInterval(sppasPoint(2.4), sppasPoint(4.)),   # 7
                         sppasInterval(sppasPoint(2.5), sppasPoint(3.))    # 8
                         ]
        annotations = [sppasAnnotation(sppasLocation(t), sppasLabel(sppasTag(i))) for i, t in enumerate(localizations)]
        for i, a in enumerate(annotations):
            tier.add(a)
            self.assertEqual(len(tier), i + 1)

        anns = tier.find(sppasPoint(1.0), sppasPoint(1.5), overlaps=True)
        self.assertEqual(len(anns), 1)  # 0
        anns = tier.find(sppasPoint(1.5), sppasPoint(1.8), overlaps=True)
        self.assertEqual(len(anns), 2)  # 0 1
        anns = tier.find(sppasPoint(1.8), sppasPoint(2.0), overlaps=True)
        self.assertEqual(len(anns), 4)  # 0 1 2 3
        anns = tier.find(sppasPoint(2.0), sppasPoint(2.3), overlaps=False)
        self.assertEqual(len(anns), 1)  # 4
        anns = tier.find(sppasPoint(2.0), sppasPoint(2.3), overlaps=True)
        self.assertEqual(len(anns), 4)  # 3 4 5 6
        anns = tier.find(sppasPoint(2.3), sppasPoint(2.4), overlaps=True)
        self.assertEqual(len(anns), 3)  # 3 5 6
        anns = tier.find(sppasPoint(2.4), sppasPoint(2.5), overlaps=True)
        self.assertEqual(len(anns), 4)  # 3 5 6 7
        anns = tier.find(sppasPoint(2.5), sppasPoint(3.0), overlaps=True)
        self.assertEqual(len(anns), 3)  # 6 7 8
        anns = tier.find(sppasPoint(3.0), sppasPoint(4.0), overlaps=True)
        self.assertEqual(len(anns), 1)  # 7

    # -----------------------------------------------------------------------

    def test_find_point(self):
        tier = sppasTier("PointsTier")
        for i in range(5):
            tier.create_annotation(sppasLocation(sppasPoint(i)))
            print(tier[i])

        # annotations = tier.find(sppasPoint(0), sppasPoint(5))
        # self.assertEqual(len(annotations), len(tier))
        # for x, y in zip(tier, annotations):
        #     self.assertTrue(x is y)

        annotations = tier.find(sppasPoint(0.5), sppasPoint(5))
        self.assertEqual(len(annotations), 4)
        self.assertTrue(annotations[0].contains_localization(sppasPoint(1)))
        self.assertTrue(annotations[1].contains_localization(sppasPoint(2)))
        self.assertTrue(annotations[2].contains_localization(sppasPoint(3)))
        self.assertTrue(annotations[3].contains_localization(sppasPoint(4)))

        annotations = tier.find(sppasPoint(0.5), sppasPoint(2.5))
        self.assertEqual(len(annotations), 2)
        self.assertTrue(annotations[0].contains_localization(sppasPoint(1)))
        self.assertTrue(annotations[1].contains_localization(sppasPoint(2)))

        annotations = tier.find(sppasPoint(0.5), sppasPoint(0.8))
        self.assertEqual(len(annotations), 0)

        annotations = tier.find(sppasPoint(6), sppasPoint(10))
        self.assertEqual(len(annotations), 0)

        annotations = tier.find(sppasPoint(0), sppasPoint(4), overlaps=False)
        self.assertEqual(len(annotations), len(tier))
        for x, y in zip(tier, annotations):
            self.assertTrue(x is y)

        annotations = tier.find(sppasPoint(0), sppasPoint(5), overlaps=False)
        self.assertEqual(len(annotations), 5)

        annotations = tier.find(sppasPoint(0.5), sppasPoint(5), overlaps=False)
        self.assertEqual(len(annotations), 4)

        annotations = tier.find(sppasPoint(0.5), sppasPoint(2.5), overlaps=False)
        self.assertEqual(len(annotations), 2)

        annotations = tier.find(sppasPoint(0.5), sppasPoint(0.8), overlaps=False)
        self.assertEqual(len(annotations), 0)

        annotations = tier.find(sppasPoint(6), sppasPoint(10), overlaps=False)
        self.assertEqual(len(annotations), 0)

    def test_rindex(self):
        tier = sppasTier()
        for i in range(1, 11):
            a = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))))
            tier.append(a)
        for a in tier:
            index = tier.rindex(a.get_highest_localization())
            self.assertEqual(tier[index].get_highest_localization(), a.get_highest_localization())
        self.assertEqual(tier.rindex(sppasPoint(5.5)), -1)
        self.assertEqual(tier.rindex(sppasPoint(0)), -1)
        self.assertEqual(tier.rindex(sppasPoint(1000)), -1)

        tier = sppasTier()
        self.assertEqual(tier.rindex(sppasPoint(2)), -1)
        tier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2)))))
        self.assertEqual(tier.rindex(sppasPoint(2)), 0)

    def test_lindex(self):
        tier = sppasTier()
        for i in range(1, 11):
            a = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))))
            tier.append(a)
        for a in tier:
            index = tier.lindex(a.get_lowest_localization())
            self.assertEqual(tier[index].get_lowest_localization(), a.get_lowest_localization())
        self.assertEqual(tier.lindex(sppasPoint(5.5)), -1)
        self.assertEqual(tier.lindex(sppasPoint(0)), -1)
        self.assertEqual(tier.lindex(sppasPoint(1000)), -1)

        tier = sppasTier()
        tier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2)))))
        tier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3)))))
        tier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(4)))))
        self.assertEqual(tier.lindex(sppasPoint(1)), 0)

    def test_mindex(self):
        # frames
        tier = sppasTier()
        for i in range(1, 11):
            a = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))))
            tier.append(a)
        for a in tier:
            index = tier.mindex(a.get_lowest_localization(), sppasPoint(0))
            self.assertEqual(index, -1)
        for a in tier:
            index = tier.mindex(a.get_highest_localization(), sppasPoint(0))
            self.assertEqual(index, -1)
        # times
        tier = sppasTier()
        for i in range(1, 11):
            a = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(float(i)), sppasPoint(float(i)+1.))))
            tier.append(a)
        for i, a in enumerate(tier):
            time = sppasPoint((a.get_lowest_localization().get_midpoint() + a.get_highest_localization().get_midpoint()) / 2.)
            index = tier.mindex(time, 0)
            self.assertEqual(index, i)

    def test_index(self):
        tier = sppasTier()
        self.assertEqual(tier.index(sppasPoint(2)), -1)
        tier.add(sppasAnnotation(sppasLocation(sppasPoint(2))))
        self.assertEqual(tier.index(sppasPoint(2)), 0)

    def test_equal_annotation(self):
        tier = sppasTier()
        a = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(3))))
        tier.append(a)
        self.assertTrue(tier[0] is a)
        self.assertEqual(tier[0], a)

    def test_near(self):
        # IntervalTier
        tier = sppasTier()
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(0.1), sppasPoint(1.)))))
        tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3.), sppasPoint(4.)))))

        index = tier.near(sppasPoint(0), direction=1)
        self.assertEqual(index, 0)
        index = tier.near(sppasPoint(0), direction=0)
        self.assertEqual(index, 0)

        index = tier.near(sppasPoint(0.5), direction=1)
        self.assertEqual(index, 1)
        index = tier.near(sppasPoint(0.5), direction=0)
        self.assertEqual(index, 0)

        index = tier.near(sppasPoint(1), direction=0)
        self.assertEqual(index, 0)
        index = tier.near(sppasPoint(1.), direction=-1)
        self.assertEqual(index, 0)
        index = tier.near(sppasPoint(1), direction=1)
        self.assertEqual(index, 1)

        index = tier.near(sppasPoint(2), direction=1)
        self.assertEqual(index, 1)
        index = tier.near(sppasPoint(2), direction=-1)
        self.assertEqual(index, 0)
        index = tier.near(sppasPoint(2), direction=0)
        # same distance between both annotations, both should be ok!
        self.assertEqual(index, 0)
        #self.assertEqual(index, 1)

        index = tier.near(sppasPoint(2.5), direction=0)
        self.assertEqual(index, 1)

        # PointTier
        tier = sppasTier()
        tier.append(sppasAnnotation(sppasLocation(sppasPoint(1.))))
        tier.append(sppasAnnotation(sppasLocation(sppasPoint(2.))))

        index = tier.near(sppasPoint(1.2), direction=1)
        self.assertEqual(index, 1)

        index = tier.near(sppasPoint(1.4), direction=-1)
        self.assertEqual(index, 0)
        index = tier.near(sppasPoint(1.4), direction=0)
        self.assertEqual(index, 0)
        index = tier.near(sppasPoint(1.4), direction=1)
        self.assertEqual(index, 1)

        index = tier.near(sppasPoint(1.7), direction=0)
        self.assertEqual(index, 1)
        index = tier.near(sppasPoint(1.7), direction=-1)
        self.assertEqual(index, 0)
        index = tier.near(sppasPoint(1.7), direction=1)
        self.assertEqual(index, 1)

    def test_start_end(self):
        tier = sppasTier()
        self.assertEqual(tier.get_first_point(), None)
        self.assertEqual(tier.get_last_point(), None)
        a = sppasAnnotation(sppasLocation(sppasPoint(2.4)))
        tier.append(a)
        self.assertEqual(tier.get_first_point(), 2.4)
        a = sppasAnnotation(sppasLocation(sppasPoint(3.)))
        tier.add(a)
        self.assertEqual(tier.get_last_point(), 3.)

    def test_get_all_points(self):
        tier = sppasTier()
        self.assertEqual(tier.get_all_points(), [])
        a = sppasAnnotation(sppasLocation(sppasPoint(2.4)))
        tier.append(a)
        self.assertEqual(tier.get_all_points(), [sppasPoint(2.4)])
        a = sppasAnnotation(sppasLocation(sppasPoint(3.)))
        tier.append(a)
        self.assertEqual(tier.get_all_points(), [sppasPoint(2.4), sppasPoint(3.)])
        # with alternative localizations
        tier = sppasTier()
        l = sppasLocation(sppasPoint(2.4), score=0.5)
        l.append(sppasPoint(3.), score=0.5)
        tier.append(sppasAnnotation(l))
        self.assertEqual(tier.get_all_points(), [sppasPoint(2.4), sppasPoint(3.)])

    def test_has_point(self):
        tier = sppasTier()
        a0 = sppasAnnotation(sppasLocation(sppasPoint(2.4)))
        tier.append(a0)
        a1 = sppasAnnotation(sppasLocation(sppasPoint(3.)))
        tier.append(a1)
        self.assertTrue(tier.has_point(sppasPoint(2.4)))
        self.assertTrue(tier.has_point(sppasPoint(3.)))
        self.assertFalse(tier.has_point(sppasPoint(3.4)))

        tier = sppasTier()
        l = sppasLocation(sppasPoint(2.4), score=0.5)
        l.append(sppasPoint(3.), score=0.5)
        tier.append(sppasAnnotation(l))
        self.assertTrue(tier.has_point(sppasPoint(2.4)))
        self.assertTrue(tier.has_point(sppasPoint(3.)))
        self.assertFalse(tier.has_point(sppasPoint(3.4)))

    def test_is_superset(self):
        tier = sppasTier()
        a0 = sppasAnnotation(sppasLocation(sppasPoint(2.4)))
        tier.append(a0)
        a1 = sppasAnnotation(sppasLocation(sppasPoint(3.)))
        tier.append(a1)
        other = sppasTier()
        other.append(sppasAnnotation(sppasLocation(sppasPoint(2.4))))
        self.assertTrue(tier.is_superset(other))
        self.assertFalse(other.is_superset(tier))
        other.append(sppasAnnotation(sppasLocation(sppasPoint(3.))))
        self.assertTrue(tier.is_superset(other))
        self.assertTrue(other.is_superset(tier))

        reftier = sppasTier()
        subtier = sppasTier()
        self.assertTrue(reftier.is_superset(subtier))
        self.assertTrue(subtier.is_superset(reftier))
        reftier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(1.5)))))
        reftier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(2.)))))
        reftier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2.), sppasPoint(2.5)))))
        reftier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2.5), sppasPoint(3.)))))
        self.assertTrue(reftier.is_superset(subtier))
        self.assertFalse(subtier.is_superset(reftier))
        subtier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        subtier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2.), sppasPoint(3.)))))
        self.assertTrue(reftier.is_superset(subtier))
        self.assertFalse(subtier.is_superset(reftier))

    def test_search(self):
        # search strings
        tier = sppasTier()
        for i in range(10):
            a = sppasAnnotation(
                    sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))),
                    sppasLabel(sppasTag("tag %s" % i))
            )
            tier.append(a)
        for i in range(10):
            index = tier.search([sppasTag("tag %s" % i)], forward=False, pos=i)
            self.assertEqual(index, i)
        index = tier.search([sppasTag("toto")], forward=False, pos=i)
        self.assertEqual(index, -1)
        index = tier.search([sppasTag("tag 9")], function="contains", forward=True, pos=5)
        self.assertEqual(index, 9)
        index = tier.search([sppasTag("tag 0")], function="exact", forward=True, pos=5)
        self.assertEqual(index, -1)
        index = tier.search([sppasTag("tag 0")], function="iexact", forward=False, pos=9)
        self.assertEqual(index, 0)
        index = tier.search([sppasTag("0"), sppasTag("1")], function="contains", forward=True, pos=0, reverse=True)
        self.assertEqual(index, 0)
        index = tier.search([sppasTag("label"), sppasTag("9")], function="contains", any_tag=True, forward=True, pos=5)
        self.assertEqual(index, 9)
        index = tier.search([sppasTag("label"), sppasTag("9")], function="contains", any_tag=False, forward=True, pos=5)
        self.assertEqual(index, -1)
        # search int
        tier = sppasTier()
        for i in range(10):
            a = sppasAnnotation(
                    sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))),
                    sppasLabel(sppasTag(i, "int"))
            )
            tier.append(a)
        for i in range(10):
            index = tier.search([sppasTag(i, "int")], forward=False, pos=i)
            self.assertEqual(index, i)
        index = tier.search([sppasTag(3, "int")], function="greater", forward=True, pos=0)
        self.assertEqual(index, 4)
        index = tier.search([sppasTag(3, "int")], function="lower", forward=True, pos=0)
        self.assertEqual(index, 0)
