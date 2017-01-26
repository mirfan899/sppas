#!/usr/bin/env python
# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas.src.annotationdata.aio import read as trsread
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.tier import Tier

from ..tiertga import TierTGA

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestTGA(unittest.TestCase):

    def test_TierStats(self):
        tier = Tier()
        tier.Append( Annotation(TimeInterval(TimePoint(0,0.),   TimePoint(1,0.0)),    Label('#')) )
        tier.Append( Annotation(TimeInterval(TimePoint(1,0.),   TimePoint(2,0.01)),   Label('toto')) )
        tier.Append( Annotation(TimeInterval(TimePoint(3,0.01), TimePoint(4, 0.01 )), Label('titi')) )
        tier.Append( Annotation(TimeInterval(TimePoint(4,0.01), TimePoint(5, 0.01 )), Label('#')) )
        tier.Append( Annotation(TimeInterval(TimePoint(5,0.01), TimePoint(6.5,0.005)), Label('toto')) )
        tier.Append( Annotation(TimeInterval(TimePoint(6.5,0.005), TimePoint(9.5,0.)), Label('toto')) )

        t = TierTGA( tier )
        tga = t.tga()

        occurrences = tga.len()
        self.assertEqual(2, occurrences['tg_1'])
        self.assertEqual(2, occurrences['tg_2'])

        total = tga.total()
        self.assertEqual(2.0, total['tg_1'])
        self.assertEqual(4.5, total['tg_2'])

        mean = tga.mean()
        self.assertEqual(1.0, mean['tg_1'])
        self.assertEqual(2.25, mean['tg_2'])

    def testTGA(self):
        # This is one of the samples proposed in-line by Dafydd
        path = os.path.join(DATA, "tga.TextGrid")
        trs = trsread(path)
        tier = trs.Find('Syllables')
        t = TierTGA( tier )
        t.append_separator('_')
        tga = t.tga()

        occurrences = tga.len()
        self.assertEqual(34, len(occurrences))
        total  = tga.total()
        mean   = tga.mean()
        median = tga.median()
        stdev  = tga.stdev()
        npvi   = tga.nPVI()
        reglin = tga.intercept_slope_original()

        self.assertEqual(3,    occurrences['tg_1'])
        self.assertEqual(0.57, round(total['tg_1'],2))
        self.assertEqual(0.19, round(mean['tg_1'],2))
        self.assertEqual(0.14, round(median['tg_1'],2))
        self.assertEqual(0.13928, round(stdev['tg_1'],5))
        self.assertEqual(94, round(npvi['tg_1'],0))
        i,s = reglin['tg_1']
        self.assertEqual(0.025, round(i,3))
        self.assertEqual(0.165, round(s,3))

        self.assertEqual(4,     occurrences['tg_33'])
        self.assertEqual(0.78,  round(total['tg_33'],2))
        self.assertEqual(0.195, round(mean['tg_33'],3))
        self.assertEqual(0.06062, round(stdev['tg_33'],5))
        self.assertEqual(53,    round(npvi['tg_33'],0))
        i,s = reglin['tg_33']
        self.assertEqual(0.156, round(i,3))
        self.assertEqual(0.026, round(s,3))
