#!/usr/bin/env python
# -*- coding:utf-8 -*-

import unittest
import os
import sys
import operator
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.annotation  import Annotation
from annotationdata.label.label import Label
from annotationdata.label.text  import Text
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.tier        import Tier

from stats.descriptivesstats  import DescriptiveStatistics

from presenters.tierstats import TierStats


class TestStatistics(unittest.TestCase):

    def setUp(self):
        self.x = Annotation(TimeInterval(TimePoint(1,0.),   TimePoint(2,0.01)),    Label('toto'))
        self.y = Annotation(TimeInterval(TimePoint(3,0.01), TimePoint(4, 0.01 )),  Label('titi'))
        self.a = Annotation(TimeInterval(TimePoint(5,0.01), TimePoint(6.5,0.005)), Label('toto'))
        self.b = Annotation(TimeInterval(TimePoint(6.5,0.005), TimePoint(9.5,0.)), Label('toto'))
        self.tier = Tier()
        self.tier.Append(self.x)
        self.tier.Append(self.y)
        self.tier.Append(self.a)
        self.tier.Append(self.b)

    def test_TierStats(self):
        t = TierStats( self.tier )
        ds = t.ds()

        occurrences = ds.len()
        totoidx = map(operator.itemgetter(0), occurrences).index('toto')
        titiidx = map(operator.itemgetter(0), occurrences).index('titi')
        self.assertEqual(3, occurrences[totoidx][1])
        self.assertEqual(1, occurrences[titiidx][1])

        total = ds.total()
        self.assertEqual(5.5, total[totoidx][1])
        self.assertEqual(1.0, total[titiidx][1])

        mean = ds.mean()
        self.assertEqual(1.833, round(mean[totoidx][1],3))
        self.assertEqual(1.0, mean[titiidx][1])

        median = ds.median()
        self.assertEqual(1.5, median[totoidx][1])
        self.assertEqual(1.0, median[titiidx][1])

        variance = ds.variance()
        self.assertEqual(1.083, round(variance[totoidx][1],3))

        stdev = ds.stdev()
        self.assertEqual(1.041, round(stdev[totoidx][1],3))

        coefvariation = ds.coefvariation()
        self.assertEqual(56.773, round(coefvariation[totoidx][1],3))

        for i,item in enumerate(total):
            print "ITEM:", item
            print item[0], item[1], mean[i][1], median[i][1]

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStatistics)
    unittest.TextTestRunner(verbosity=2).run(suite)
