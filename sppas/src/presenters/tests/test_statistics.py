#!/usr/bin/env python
# -*- coding:utf-8 -*-

import unittest

from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.tier import Tier

from ..tierstats import TierStats

# ---------------------------------------------------------------------------


class TestStatistics(unittest.TestCase):

    def setUp(self):
        self.x = Annotation(TimeInterval(TimePoint(1, 0.), TimePoint(2, 0.01)), Label('toto'))
        self.y = Annotation(TimeInterval(TimePoint(3, 0.01), TimePoint(4, 0.01)), Label('titi'))
        self.a = Annotation(TimeInterval(TimePoint(5, 0.01), TimePoint(6.5, 0.005)), Label('toto'))
        self.b = Annotation(TimeInterval(TimePoint(6.5, 0.005), TimePoint(9.5, 0.)), Label('toto'))
        self.tier = Tier()
        self.tier.Append(self.x)
        self.tier.Append(self.y)
        self.tier.Append(self.a)
        self.tier.Append(self.b)

    def test_TierStats(self):
        t = TierStats(self.tier)
        ds = t.ds()

        occurrences = ds.len()
        self.assertEqual(3, occurrences['toto'])
        self.assertEqual(1, occurrences['titi'])

        total = ds.total()
        self.assertEqual(5.5, total['toto'])
        self.assertEqual(1.0, total['titi'])

        mean = ds.mean()
        self.assertEqual(1.833, round(mean['toto'], 3))
        self.assertEqual(1.0, mean['titi'])

        median = ds.median()
        self.assertEqual(1.5, median['toto'])
        self.assertEqual(1.0, median['titi'])

        variance = ds.variance()
        self.assertEqual(0.722, round(variance['toto'], 3))

        stdev = ds.stdev()
        self.assertEqual(0.85, round(stdev['toto'], 2))

        #coefvariation = ds.coefvariation()
        #self.assertEqual(56.773, round(coefvariation['toto'],3))
