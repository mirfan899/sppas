#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.ptime.frameinterval import FrameInterval
from annotationdata.ptime.framepoint    import FramePoint

class TestFrameInterval(unittest.TestCase):

    def setUp(self):
        self.point1000 = FramePoint(0, 1)
        self.point1001 = FramePoint(1, 1)
        self.point1002 = FramePoint(2, 0)
        self.point1003 = FramePoint(3, 0)
        self.point1004 = FramePoint(4, 0)
        self.point1005 = FramePoint(5, 0)
        self.point1006 = FramePoint(6, 0)
        self.point1007 = FramePoint(7, 1)

    def test__init__(self):
        """
        Raise ValueError if end < begin
        """
        with self.assertRaises(ValueError):
            FrameInterval(self.point1000, self.point1000)

    def test_SetBegin(self):
        """
        Raise ValueError if the given FramePoint >= self.End
        """
        interval = FrameInterval(self.point1000, self.point1002)
        with self.assertRaises(ValueError):
            interval.SetBegin( self.point1003 )

        with self.assertRaises(TypeError):
            interval.SetBegin( 1 )

    def test_SetEnd(self):
        """
        Raise ValueError if self.Begin >= the given FramePoint.
        """
        interval = FrameInterval(self.point1000, self.point1002)
        with self.assertRaises(ValueError):
            interval.SetEnd( self.point1000 )

        with self.assertRaises(TypeError):
            interval.SetEnd( 1 )

    def test__eq__(self):
        """
        x = y iff
        x.begin = y.begin && x.end = y.end
        """
        interval1 = FrameInterval(self.point1000, self.point1003)
        interval2 = FrameInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 ==  interval2)

    def test__lt__(self):
        """
        x < y iff
        x.begin < y.begin && x.end < y.end
        """
        interval1 = FrameInterval(self.point1000, self.point1002)
        interval2 = FrameInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 < interval2)

        interval1 = FrameInterval(self.point1000, self.point1002)
        interval2 = FrameInterval(self.point1001, self.point1004)
        self.assertFalse(interval1 < interval2)

        # interval |-----|
        # point            |
        self.assertTrue(interval1 < 4)
        self.assertTrue(interval1 < self.point1005)
        self.assertTrue(interval1 < 3)

        interval1 = FrameInterval(FramePoint(2), FramePoint(3))
        interval2 = FrameInterval(FramePoint(1), FramePoint(3))
        # 1      |----|
        # 2 |---------|
        self.assertFalse(interval1 < interval2)

    def test__gt__(self):
        """
        x > y iff
        x.begin > y.begin && x.end > y.end
        """
        interval1 = FrameInterval(self.point1004, self.point1006)
        interval2 = FrameInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 > interval2)

        # interval   |-----|
        # point    |
        self.assertTrue(interval1 > 2)
        self.assertTrue(interval1 > 3)
        self.assertTrue(interval1 > FramePoint(3, 0))
        self.assertTrue(interval1 > FramePoint(3))
        self.assertFalse(interval1 > 6)

    def test__ne__(self):
        interval1 = FrameInterval(self.point1000, self.point1002)
        interval2 = FrameInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 != interval2)

    def test__le__(self):
        interval1 = FrameInterval(self.point1000, self.point1002)
        interval2 = FrameInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 <= interval2)

        interval1 = FrameInterval(self.point1000, self.point1003)
        interval2 = FrameInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 <=  interval2)

        # self  |-------|
        # other |----|
        # False
        interval1 = FrameInterval(self.point1000, self.point1006)
        interval2 = FrameInterval(self.point1000, self.point1003)
        self.assertFalse(interval1 <= interval2)

        # self  |----|
        # other |-------|
        # True
        interval1 = FrameInterval(self.point1000, self.point1003)
        interval2 = FrameInterval(self.point1000, self.point1006)
        self.assertFalse(interval1 <= interval2)

    def test__ge__(self):
        interval1 = FrameInterval(self.point1000, self.point1003)
        interval2 = FrameInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 >=  interval2)

        interval1 = FrameInterval(self.point1004, self.point1006)
        interval2 = FrameInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 >= interval2)

        interval1 = FrameInterval(self.point1000, self.point1002)
        interval2 = FrameInterval(self.point1002, self.point1004)
        self.assertFalse(interval1 >= interval2)

    def test_Duration(self):
        interval1 = FrameInterval(self.point1000, self.point1007)
        self.assertEqual(interval1.Duration(), 7)
        self.assertEqual(interval1.TotalDuration(), 8)

    def test_others(self):
        point0 = FramePoint(0)
        point1 = FramePoint(1, 1)
        point2 = FramePoint(2)
        point3 = FramePoint(3, 1)
        interval01 = FrameInterval(point0,point1)
        toto = FrameInterval(FramePoint(2, 1), FramePoint(3, 2))
        with self.assertRaises(ValueError):
            tata = FrameInterval(FramePoint(2, 1), FramePoint(3, 3))

        interval001 = interval01
        self.assertEqual(interval01,interval001)
        self.assertTrue(interval01 is interval001)
        interval0001 = interval01.Copy()
        self.assertEqual(interval01,interval0001)
        self.assertFalse(interval01 is interval0001)
        interval23 = FrameInterval(point2,point3)
        interval23.Set( interval01 )
        self.assertFalse(interval23 is interval001)


# End TestFrameInterval
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFrameInterval)
    unittest.TextTestRunner(verbosity=2).run(suite)

