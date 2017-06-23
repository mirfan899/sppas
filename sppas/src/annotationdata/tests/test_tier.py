#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from ..tier import Tier
from ..label.label import Label
from ..ptime.point import TimePoint
from ..ptime.interval import TimeInterval
from ..annotation import Annotation
from ..media import Media
from ..ctrlvocab import CtrlVocab

# ---------------------------------------------------------------------------


class TestTier(unittest.TestCase):
    """
        A Tier is made of:
            - a name
            - a set of metadata
            - an array of annotations.
    """
    def setUp(self):
        self.tierP = Tier("PointTier")
        self.tierI = Tier("IntervalTier")
        for i in range(10):
            self.tierP.Append(Annotation(TimePoint(i), Label("label"+str(i))))
            self.tierI.Append(Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)), Label("label"+str(i))))

    def test_Metadata(self):
        self.tierP.metadata['key']="value"
        self.tierI.SetMetadata('key',"value")
        self.assertEqual(self.tierI.GetMetadata('key'), self.tierP.GetMetadata('key'))
        self.assertEqual(self.tierI.GetMetadata('toto'), '')

    def test_CtrlVocab(self):
        tiercv = Tier("CtrlVocabTier")

        a1 = Annotation(TimeInterval(TimePoint(1), TimePoint(3)), Label("definition"))
        a2 = Annotation(TimeInterval(TimePoint(6), TimePoint(7)), Label("gap filling with sound"))
        a3 = Annotation(TimeInterval(TimePoint(7), TimePoint(9)), Label("biz"))

        voc = CtrlVocab("Verbal Strategies")
        self.assertTrue(voc.Append("definition"))
        self.assertTrue(voc.Append("example"))
        self.assertTrue(voc.Append("comparison"))
        self.assertTrue(voc.Append("gap filling with sound"))

        tiercv.SetCtrlVocab(voc)
        tiercv.Append(a1)
        tiercv.Append(a2)
        with self.assertRaises(ValueError):
            tiercv.Append(a3)

    def test_Media(self):
        m = Media('abcd', '/path/file.wav', 'audio/wav')
        self.tierP.SetMedia(m)
        self.tierI.SetMedia(m)
        self.assertEqual(self.tierI.GetMedia(), self.tierP.GetMedia())

    def test_GetName(self):
        tier = Tier("être être")
        self.assertIsInstance(tier.GetName(), unicode)

    def test_SetName(self):
        tier = Tier("être être")
        tier.SetName( "foo" )
        self.assertIsInstance(tier.GetName(), unicode)

    def test_IsEmpty(self):
        tier = Tier()
        self.assertTrue(tier.IsEmpty())
        self.assertFalse(self.tierI.IsEmpty())

    def test_GetBegin(self):
        tier = Tier()
        self.assertEqual(tier.GetBeginValue(), 0)

        a = Annotation(TimePoint(2.4))
        tier.Add(a)
        self.assertEqual(tier.GetBeginValue(), 2.4)

    def test_GetEnd(self):
        tier = Tier()
        self.assertEqual(tier.GetEndValue(), 0)

        a = Annotation(TimePoint(2.4))
        tier.Add(a)
        self.assertEqual(tier.GetEndValue(), 2.4)

    def test_IsInterval(self):
        self.assertTrue(self.tierI.IsInterval())
        self.assertFalse(self.tierP.IsInterval())

    def test_IsPoint(self):
        self.assertTrue(self.tierP.IsPoint())
        self.assertFalse(self.tierI.IsPoint())

    def test_Remove(self):
        tier = Tier()
        times = [TimeInterval(TimePoint(1), TimePoint(2)),
                 TimeInterval(TimePoint(2), TimePoint(3)),
                 TimeInterval(TimePoint(4), TimePoint(5)),
                 TimeInterval(TimePoint(5), TimePoint(6))
                ]

        annotations = [Annotation(t) for t in times]

        for a in annotations:
            tier.Append(a)

        tier.Remove(TimePoint(2), TimePoint(3))
        self.assertEquals(tier.GetSize(), 3)
        self.assertEquals(tier[0].GetLocation().GetValue().GetPlace(), TimeInterval(TimePoint(1), TimePoint(2)))
        self.assertEquals(tier[1].GetLocation().GetValue().GetPlace(), TimeInterval(TimePoint(4), TimePoint(5)))
        self.assertEquals(tier[2].GetLocation().GetValue().GetPlace(), TimeInterval(TimePoint(5), TimePoint(6)))

        #with self.assertRaises(IndexError):
        #    tier.Remove(TimePoint(2), TimePoint(3))

        tier = Tier()
        for i in range(1, 5):
            tier.Append(Annotation(TimePoint(i)))

        tier.Remove(TimePoint(2), TimePoint(3))
        self.assertEquals(tier.GetSize(), 2)
        self.assertEquals(tier[0].GetLocation().GetValue().GetPlace(), TimePoint(1))
        self.assertEquals(tier[1].GetLocation().GetValue().GetPlace(), TimePoint(4))

        with self.assertRaises(ValueError):
            tier.Remove(TimePoint(3), TimePoint(3))

    def test_Append(self):
        tier = Tier()
        a1 = Annotation(TimeInterval(TimePoint(1), TimePoint(3)), Label("foo"))
        a2 = Annotation(TimeInterval(TimePoint(6), TimePoint(7)), Label("biz"))
        a3 = Annotation(TimeInterval(TimePoint(6.5), TimePoint(7)), Label("biz"))

        tier.Append(a1)
        tier.Append(a2)

        with self.assertRaises(ValueError):
            tier.Append(a3)

    # TODO when a tier is mixed, it can not insert annotation correctly.
    def test_Add(self):
        tier = Tier()
        times = [TimeInterval(TimePoint(1), TimePoint(2)),
                 TimeInterval(TimePoint(1.5), TimePoint(2)),
                 TimeInterval(TimePoint(1.8), TimePoint(2)),
                 TimeInterval(TimePoint(2), TimePoint(3)),
                 TimeInterval(TimePoint(2.5), TimePoint(3)),
                 TimeInterval(TimePoint(2), TimePoint(2.3)),
                 TimeInterval(TimePoint(2), TimePoint(2.5)),
                 TimeInterval(TimePoint(1.8), TimePoint(2.5)),
                 TimeInterval(TimePoint(2.4), TimePoint(4))]

        annotations = [Annotation(t) for t in times]

        for a in annotations:
            tier.Add(a)

        import random
        random.shuffle(annotations)

        tier = Tier()
        a1 = Annotation(TimeInterval(TimePoint(1), TimePoint(2)), Label("foo"))
        a2 = Annotation(TimeInterval(TimePoint(2), TimePoint(3)), Label("bar"))
        tier.Add(a1)
        tier.Add(a2)
        tier[-1].GetLabel().SetValue(tier[-1].GetLabel().GetValue() + "bar")

    def test_Add2(self):
        tier = Tier()
        import random
        l = range(1, 10)
        random.shuffle(l)
        for i in l:
            tier.Add(Annotation(TimeInterval(TimePoint(0), TimePoint(i))))

        for i, a in enumerate(tier, 1):
            self.assertEqual(a.GetLocation().GetEnd(), TimePoint(i))

    def test_Copy(self):
        tier = Tier()
        copy = tier.Copy()
        self.assertIsNot(tier, copy)
        self.assertIs(tier, tier)

    def test_FindInterval(self):
        tier = Tier()
        _anns = [
                Annotation(TimeInterval(TimePoint(0), TimePoint(1))),
                Annotation(TimeInterval(TimePoint(1), TimePoint(2))),
                Annotation(TimeInterval(TimePoint(2), TimePoint(3))),
                Annotation(TimeInterval(TimePoint(4), TimePoint(5)))
                ]
        for a in _anns:
            tier.Append(a)

        annotations = tier.Find(TimePoint(0), TimePoint(5))
        self.assertEquals(len(annotations), tier.GetSize())
        for x, y in zip(tier, annotations):
            self.assertEquals(x.GetLocation().GetValue(), y.GetLocation().GetValue())

        annotations = tier.Find(TimePoint(0), TimePoint(5), overlaps=False)
        self.assertEquals(len(annotations), tier.GetSize())
        for x, y in zip(tier, annotations):
            self.assertEquals(x.GetLocation().GetValue(), y.GetLocation().GetValue())

        annotations = tier.Find(TimePoint(0.5), TimePoint(5))
        self.assertEquals(len(annotations), tier.GetSize())
        for x, y in zip(tier, annotations):
            self.assertEquals(x.GetLocation().GetValue(), y.GetLocation().GetValue())

        annotations = tier.Find(TimePoint(0.5), TimePoint(5), overlaps=False)
        self.assertEquals(annotations, [])

        annotations = tier.Find(TimePoint(0.5), TimePoint(4.5))
        self.assertEquals(len(annotations), tier.GetSize())
        for x, y in zip(tier, annotations):
            self.assertEquals(x.GetLocation().GetValue(), y.GetLocation().GetValue())

        annotations = tier.Find(TimePoint(0.5), TimePoint(4.5), overlaps=False)
        self.assertEquals(annotations, [])

        annotations = tier.Find(TimePoint(3.5), TimePoint(4.5))
        self.assertEquals(len(annotations), 1)
        self.assertEquals(annotations[0], tier[-1])

        annotations = tier.Find(TimePoint(0.5), TimePoint(4.5), overlaps=False)
        self.assertEquals(annotations, [])

        annotations = tier.Find(TimePoint(3.5), TimePoint(3.8))
        self.assertEquals(annotations, [])

        annotations = tier.Find(TimePoint(3.5), TimePoint(3.8), overlaps=False)
        self.assertEquals(annotations, [])

        annotations = tier.Find(TimePoint(3), TimePoint(4))
        self.assertEquals(annotations, [])

        annotations = tier.Find(TimePoint(3), TimePoint(4), overlaps=False)
        self.assertEquals(annotations, [])

        annotations = tier.Find(TimePoint(6), TimePoint(7), overlaps=True)
        self.assertEquals(annotations, [])

        annotations = tier.Find(TimePoint(6), TimePoint(7), overlaps=False)
        self.assertEquals(annotations, [])

    def test_FindPoint(self):
        tier = Tier()
        _anns = [
                Annotation(TimePoint(0)),
                Annotation(TimePoint(1)),
                Annotation(TimePoint(2)),
                Annotation(TimePoint(4))
                ]
        for a in _anns:
            tier.Append(a)

        annotations = tier.Find(TimePoint(0), TimePoint(5))
        self.assertEquals(len(annotations), tier.GetSize())
        for x, y in zip(tier, annotations):
            self.assertEquals(x.GetLocation().GetValue(), y.GetLocation().GetValue())

        annotations = tier.Find(TimePoint(0.5), TimePoint(5))
        self.assertEquals(len(annotations), 3)
        self.assertEquals(annotations[0].GetLocation().GetValue().GetPlace(), TimePoint(1))
        self.assertEquals(annotations[1].GetLocation().GetValue().GetPlace(), TimePoint(2))
        self.assertEquals(annotations[2].GetLocation().GetValue().GetPlace(), TimePoint(4))

        annotations = tier.Find(TimePoint(0.5), TimePoint(2.5))
        self.assertEquals(len(annotations), 2)
        self.assertEquals(annotations[0].GetLocation().GetValue().GetPlace(), TimePoint(1))
        self.assertEquals(annotations[1].GetLocation().GetValue().GetPlace(), TimePoint(2))

        annotations = tier.Find(TimePoint(0.5), TimePoint(0.8))
        self.assertEquals(len(annotations), 0)

        annotations = tier.Find(TimePoint(6), TimePoint(10))
        self.assertEquals(len(annotations), 0)

        annotations = tier.Find(TimePoint(0), TimePoint(4), overlaps=False)
        self.assertEquals(len(annotations), tier.GetSize())
        for x, y in zip(tier, annotations):
            self.assertEquals(x.GetLocation().GetValue(), y.GetLocation().GetValue())

        annotations = tier.Find(TimePoint(0), TimePoint(5), overlaps=False)
        self.assertEquals(len(annotations), 0)

        annotations = tier.Find(TimePoint(0.5), TimePoint(5), overlaps=False)
        self.assertEquals(len(annotations), 0)

        annotations = tier.Find(TimePoint(0.5), TimePoint(2.5), overlaps=False)
        self.assertEquals(len(annotations), 0)

        annotations = tier.Find(TimePoint(0.5), TimePoint(0.8), overlaps=False)
        self.assertEquals(len(annotations), 0)

        annotations = tier.Find(TimePoint(6), TimePoint(10), overlaps=False)
        self.assertEquals(len(annotations), 0)

    def test_Rindex(self):
        tier = Tier()
        for i in range(1, 11):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)))
            tier.Append(a)

        for a in tier:
            index = tier.Rindex(a.GetLocation().GetEnd())
            self.assertEquals(tier[index].GetLocation().GetEnd(), a.GetLocation().GetEnd())

        self.assertEquals(tier.Rindex(TimePoint(5.5)), -1)
        self.assertEquals(tier.Rindex(TimePoint(0)), -1)
        self.assertEquals(tier.Rindex(TimePoint(1000)), -1)

    def test_Rindex2(self):
        tier = Tier()
        self.assertEquals(tier.Rindex(TimePoint(2)), -1)

        tier.Add(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))
        self.assertEquals(tier.Rindex(TimePoint(2)), 0)

        tier.Add(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))
        self.assertEquals(tier.Rindex(TimePoint(2)), 0)

        tier.Add(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))
        self.assertEquals(tier.Rindex(TimePoint(2)), 0)

    def test_Lindex(self):
        tier = Tier()
        for i in range(1, 11):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)))
            tier.Append(a)

        for a in tier:
            index = tier.Lindex(a.GetLocation().GetBegin())
            self.assertEquals(tier[index].GetLocation().GetBegin(), a.GetLocation().GetBegin())

        self.assertEquals(tier.Lindex(TimePoint(5.5)), -1)
        self.assertEquals(tier.Lindex(TimePoint(0)), -1)
        self.assertEquals(tier.Lindex(TimePoint(1000)), -1)

    def test_Lindex2(self):
        tier = Tier()
        tier.Add(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))
        tier.Add(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))
        tier.Add(Annotation(TimeInterval(TimePoint(1), TimePoint(3))))
        tier.Add(Annotation(TimeInterval(TimePoint(1), TimePoint(4))))

        self.assertEquals(tier.Lindex(TimePoint(1)), 0)

    def test_Index(self):
        tier = Tier()
        self.assertEquals(tier.Index(TimePoint(2)), -1)

        tier.Add(Annotation(TimePoint(2)))
        self.assertEquals(tier.Index(TimePoint(2)), 0)

        tier.Add(Annotation(TimePoint(2)))
        self.assertEquals(tier.Index(TimePoint(2)), 0)

        tier.Add(Annotation(TimePoint(2)))
        self.assertEquals(tier.Index(TimePoint(2)), 0)

        tier.Add(Annotation(TimePoint(2)))
        self.assertEquals(tier.Index(TimePoint(2)), 0)

    def test_Mindex(self):
        tier = Tier()
        for i in range(1, 11):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)))
            tier.Append(a)

        for a in tier:
            index = tier.Mindex(a.GetLocation().GetBegin(), 0)
            self.assertEquals(index, -1)

        for a in tier:
            index = tier.Mindex(a.GetLocation().GetEnd(), 0)
            self.assertEquals(index, -1)

        for i, a in enumerate(tier):
            time = TimePoint((a.GetLocation().GetBegin().GetValue() + a.GetLocation().GetEnd().GetValue()) / 2)
            index = tier.Mindex(time, 0)
            self.assertEquals(index, i)

    def test_Near(self):
        # IntervalTier
        tier = Tier()
        tier.Append(Annotation(TimeInterval(TimePoint(0.1), TimePoint(1))))
        tier.Append(Annotation(TimeInterval(TimePoint(3), TimePoint(4))))

        index = tier.Near(time=0, direction=1)
        self.assertEquals(index, 0)

        index = tier.Near(time=0, direction=0)
        self.assertEquals(index, 0)

        index = tier.Near(time=0.5, direction=1)
        self.assertEquals(index, 1)
        index = tier.Near(time=0.5, direction=0)
        self.assertEquals(index, 0)

        index = tier.Near(time=1, direction=0)
        self.assertEquals(index, 0)

        index = tier.Near(time=1, direction=-1)
        #self.assertEquals(index, -1)
        self.assertEquals(index, 0)

        index = tier.Near(time=1, direction=1)
        self.assertEquals(index, 1)

        index = tier.Near(time=2, direction=1)
        self.assertEquals(index, 1)

        index = tier.Near(time=2, direction=-1)
        self.assertEquals(index, 0)

        index = tier.Near(time=2, direction=0)
        # same distance between both annotations, both should be ok!
        self.assertEquals(index, 0)
        #self.assertEquals(index, 1)

        index = tier.Near(time=2.5, direction=0)
        self.assertEquals(index, 1)

        # PointTier (not fully implemented)
        tier = Tier()
        tier.Append(Annotation(TimePoint(1)))
        tier.Append(Annotation(TimePoint(2)))

        index = tier.Near(time=1.2, direction=1)
        self.assertEquals(index, 1)

        index = tier.Near(time=1.4, direction=-1)
        self.assertEquals(index, 0)

        index = tier.Near(time=1.4, direction=0)
        self.assertEquals(index, 0)

#        index = tier.Near(time=1.7, direction=0)
#        self.assertEquals(index, 1)

    def test_Search(self):
        tier = Tier()
        for i in range(10):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)),
                           Label("label %s" % i))
            tier.Append(a)

        index = tier.Search(["label 9"], function="exact", forward=True, pos=0)
        self.assertEquals(index, 9)

        index = tier.Search(["label 0"], function="exact", forward=True, pos=5)
        self.assertEquals(index, -1)

        index = tier.Search(["label 0"], function="exact", forward=False, pos=9)
        self.assertEquals(index, 0)

        for i in range(10):
            index = tier.Search(["label"], function="contains", forward=False, pos=i)
            self.assertEquals(index, i)

        index = tier.Search(["0", "1"], function="contains", forward=True, pos=0, reverse=True)
        self.assertEquals(index, 2)
