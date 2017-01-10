#!/usr/bin/env python
# -*- coding:utf-8 -*-

import unittest

from annotationdata.annotation import Annotation
from annotationdata.label.label import Label
from annotationdata.label.text import Text
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.tier import Tier
from annotationdata import Filter, SingleFilter, Sel

# ---------------------------------------------------------------------------


class TestSingleFilter(unittest.TestCase):

    def setUp(self):
        self.x = Annotation(TimeInterval(TimePoint(1), TimePoint(2)), Label('toto'))
        self.y = Annotation(TimeInterval(TimePoint(3), TimePoint(4)), Label('titi'))

    def test_predicate(self):
        p = Sel(exact='toto')
        self.assertTrue(p(self.x))

        p = Sel(iexact='TOTO')
        self.assertTrue(p(self.x))

        p = Sel(startswith='t') & Sel(endswith='o')
        self.assertTrue(p(self.x))
        self.assertFalse(p(self.y))

        p = Sel(startswith='t') | Sel(endswith='o')
        self.assertTrue(p(self.x))
        self.assertTrue(p(self.x))

        p = Sel(duration_le=1)
        self.assertTrue(p(self.x))

    def test_filter_label(self):
        tier = Tier()
        for i in range(10):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)), Label("label-%s" % i))
            tier.Append(a)

        ft = Filter(tier)
        ltr = SingleFilter( Sel(regexp='label-[1,3,5]'),ft )
        ans = [a for a in ltr.Filter()]

        self.assertEqual(ans[0].GetLabel().GetValue(), tier[1].GetLabel().GetValue())
        self.assertEqual(ans[1].GetLabel().GetValue(), tier[3].GetLabel().GetValue())
        self.assertEqual(ans[2].GetLabel().GetValue(), tier[5].GetLabel().GetValue())

        ltc = SingleFilter( Sel(contains='0'),ft )
        ans = [a for a in ltc]
        self.assertEqual(len(ans), 1)
        self.assertEqual(ans[0].GetLabel().GetValue(), tier[0].GetLabel().GetValue())

        lte = SingleFilter( Sel(endswith='9'),ft )
        ans = [a for a in lte]
        self.assertEqual(len(ans), 1)
        self.assertEqual(ans[0].GetLabel().GetValue(), tier[9].GetLabel().GetValue())

        lts = SingleFilter( Sel(startswith='l'),ft )
        ans = [a for a in lts]
        self.assertEqual(len(ans), 10)
        for i in range(10):
            self.assertEqual(ans[i].GetLabel().GetValue(), tier[i].GetLabel().GetValue())

        lteq = SingleFilter( Sel(duration_eq=1),ft )
        ans = [a for a in lteq]
        self.assertEqual(len(ans), 10)
        for i in range(10):
            self.assertEqual(ans[i].GetLabel().GetValue(), tier[i].GetLabel().GetValue())

        ltle = SingleFilter( Sel(duration_le=1),ft )
        ans = [a for a in ltle]
        self.assertEqual(len(ans), 10)
        for i in range(10):
            self.assertEqual(ans[i].GetLabel().GetValue(), tier[i].GetLabel().GetValue())

        ltlt = SingleFilter( Sel(duration_lt=1),ft )
        ans = [a for a in ltlt]
        self.assertEqual(len(ans), 0)

        ltge = SingleFilter( Sel(begin_ge=5),ft )
        ans = [a for a in ltge]
        self.assertEqual(len(ans), 5)
        for i in range(5):
            self.assertEqual(ans[i].GetLabel().GetValue(), tier[i+5].GetLabel().GetValue())

    def test_filter_typedlabel(self):

        # int
        typetier = Tier()
        for i in range(10):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)), Label(i, data_type="int"))
            typetier.Append(a)

        ftt = Filter(typetier)
        ltge = SingleFilter( Sel(lower=5),ftt )
        ans = [a for a in ltge]
        self.assertEqual(len(ans), 5)
        for i in range(5):
            self.assertEqual(ans[i].GetLabel().GetTypedValue(), typetier[i].GetLabel().GetTypedValue())

        # bool
        typetier = Tier()
        for i in range(10):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)), Label((i%2), data_type="bool"))
            typetier.Append(a)

        ftt = Filter(typetier)
        ltge = SingleFilter( Sel(bool=True),ftt )
        ans = [a for a in ltge]
        self.assertEqual(len(ans), 5)

    def test_filter_alternativeslabel(self):
        tier = Tier()
        for i in range(10):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)), Label(Text("main-%s" % i,0.6)) )
            a.GetLabel().AddValue( Text("alt-%s" % (i+1),0.4) )
            tier.Append(a)

        ft = Filter(tier)
        ltc = SingleFilter( Sel(contains='2'),ft )
        ans = [a for a in ltc]
        self.assertEqual(len(ans), 1)
        self.assertEqual(ans[0].GetLabel().GetValue(), tier[2].GetLabel().GetValue())

        ltc = SingleFilter( Sel(contains='2', opt="any"),ft )
        ans = [a for a in ltc]
        self.assertEqual(len(ans), 2)
        self.assertEqual(ans[1].GetLabel().GetValue(), tier[2].GetLabel().GetValue())
