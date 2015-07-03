#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
import getopt
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.annotation import Annotation
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.utils.tierutils import TierUtils
from annotationdata.utils.trsutils import overlaps
from annotationdata.utils.trsutils import TrsUtils
from annotationdata.transcription import Transcription
from annotationdata.tier import Tier
import annotationdata.io

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.a0= Annotation(TimeInterval(TimePoint(0), TimePoint(0.5)))
        self.a1= Annotation(TimeInterval(TimePoint(0.5), TimePoint(1)))
        self.a2= Annotation(TimeInterval(TimePoint(1), TimePoint(2)))
        self.a3= Annotation(TimeInterval(TimePoint(2), TimePoint(3)))
        self.a4= Annotation(TimeInterval(TimePoint(3), TimePoint(4)))
        self.a5= Annotation(TimeInterval(TimePoint(4), TimePoint(5)))
        self.a = Annotation(TimeInterval(TimePoint(0.5), TimePoint(3.5)))
        self.tier = Tier()
        self.tier.Add(self.a0)
        self.tier.Add(self.a1)
        self.tier.Add(self.a2)
        self.tier.Add(self.a3)
        self.tier.Add(self.a4)
        self.tier.Add(self.a5)


    def test_overlaps(self):
        new_tier = TierUtils.Select(self.tier, lambda x: overlaps(self.a, x))

        self.assertEqual(len(new_tier), 4)
        self.assertEqual(new_tier[0].Time, self.a1.Time)
        self.assertEqual(new_tier[1].Time, self.a2.Time)
        self.assertEqual(new_tier[2].Time, self.a3.Time)
        self.assertEqual(new_tier[3].Time, self.a4.Time)

    def test_Shift(self):
        transcription = Transcription()
        new_tier1 = TierUtils.Select(self.tier, lambda x: overlaps(self.a, x))
        new_tier2 = TierUtils.Select(self.tier, lambda x: overlaps(self.a, x))
        transcription.Append(new_tier1)
        transcription.Append(new_tier2)
        TrsUtils.Shift(transcription, 0.5)

        self.assertEqual(transcription[0][0].BeginValue, self.a1.BeginValue - 0.5)
        self.assertEqual(transcription[0][1].BeginValue, self.a2.BeginValue - 0.5)
        self.assertEqual(transcription[0][2].BeginValue, self.a3.BeginValue - 0.5)
        self.assertEqual(transcription[0][3].BeginValue, self.a4.BeginValue - 0.5)

        self.assertEqual(transcription[0][0].EndValue, self.a1.EndValue - 0.5)
        self.assertEqual(transcription[0][1].EndValue, self.a2.EndValue - 0.5)
        self.assertEqual(transcription[0][2].EndValue, self.a3.EndValue - 0.5)
        self.assertEqual(transcription[0][3].EndValue, self.a4.EndValue - 0.5)

        self.assertEqual(transcription[1][0].BeginValue, self.a1.BeginValue - 0.5)
        self.assertEqual(transcription[1][1].BeginValue, self.a2.BeginValue - 0.5)
        self.assertEqual(transcription[1][2].BeginValue, self.a3.BeginValue - 0.5)
        self.assertEqual(transcription[1][3].BeginValue, self.a4.BeginValue - 0.5)

        self.assertEqual(transcription[1][0].EndValue, self.a1.EndValue - 0.5)
        self.assertEqual(transcription[1][1].EndValue, self.a2.EndValue - 0.5)
        self.assertEqual(transcription[1][2].EndValue, self.a3.EndValue - 0.5)
        self.assertEqual(transcription[1][3].EndValue, self.a4.EndValue - 0.5)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite

if __name__ == '__main__':
    unittest.main()
