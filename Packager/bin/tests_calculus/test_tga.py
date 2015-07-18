#!/usr/bin/env python
# -*- coding:utf-8 -*-

import unittest
import os
import sys
import operator
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.annotation     import Annotation
from annotationdata.label.label    import Label
from annotationdata.label.text     import Text
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint
from annotationdata.tier           import Tier
import annotationdata.io

from calculus.timegroupanalysis import TimeGroupAnalysis
from presenters.tiertga import TierTGA

SAMPLES=os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")


class TestStatistics(unittest.TestCase):

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
        tg1 = map(operator.itemgetter(0), occurrences).index('tg_1')
        tg2 = map(operator.itemgetter(0), occurrences).index('tg_2')

        self.assertEqual(2, occurrences[tg1][1])
        self.assertEqual(2, occurrences[tg2][1])

        total = tga.total()
        self.assertEqual(2.0, total[tg1][1])
        self.assertEqual(4.5, total[tg2][1])

        mean = tga.mean()
        self.assertEqual(1.0, mean[tg1][1])
        self.assertEqual(2.25, mean[tg2][1])

    def testTGA(self):
        path = os.path.join(SAMPLES,"tga.TextGrid")
        trs = annotationdata.io.read(path)
        tier = trs.Find('Syllables')
        t = TierTGA( tier )
        t.append_separator('_')
        tga = t.tga()

        occurrences = tga.len()
        self.assertEqual(34, len(occurrences))
        total  = tga.total()
        mean   = tga.mean()
        median = tga.median()
        stdev  = tga.stdev()# there are differences because we estimate the unbiased variance
        npvi   = tga.nPVI()
        reglin = tga.intercept_slope_original()

        tg1 = map(operator.itemgetter(0), occurrences).index('tg_1')
        self.assertEqual(3,    occurrences[tg1][1])
        self.assertEqual(0.57, round(total[tg1][1],2))
        self.assertEqual(0.19, round(mean[tg1][1],2))
        self.assertEqual(0.14, round(median[tg1][1],2))
        #self.assertEqual(0.13928, round(stdev[tg1][1],5))
        self.assertEqual(94, round(npvi[tg1][1],0))
        i,s = reglin[tg1][1]
        self.assertEqual(0.025, round(i,3))
        self.assertEqual(0.165, round(s,3))

        tg33 = map(operator.itemgetter(0), occurrences).index('tg_33')
        self.assertEqual(4,     occurrences[tg33][1])
        self.assertEqual(0.78,  round(total[tg33][1],2))
        self.assertEqual(0.195, round(mean[tg33][1],3))
        #self.assertEqual(0.06062, round(stdev[tg33][1],5))
        self.assertEqual(53,    round(npvi[tg33][1],0))
        i,s = reglin[tg33][1]
        self.assertEqual(0.156, round(i,3))
        self.assertEqual(0.026, round(s,3))


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStatistics)
    unittest.TextTestRunner(verbosity=2).run(suite)
