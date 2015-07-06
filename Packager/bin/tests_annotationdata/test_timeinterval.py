#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint

class TestTimeInterval(unittest.TestCase):

    def setUp(self):
        self.point1000 = TimePoint(1.000, 0.0005)
        self.point1001 = TimePoint(1.001, 0.0005)
        self.point1002 = TimePoint(1.002, 0.0005)
        self.point1003 = TimePoint(1.003, 0.0005)
        self.point1004 = TimePoint(1.004, 0.0005)
        self.point1005 = TimePoint(1.005, 0.0005)
        self.point1006 = TimePoint(1.006, 0.0005)
        self.point1007 = TimePoint(1.007, 0.0005)

    def test__init__(self):
        """
        Raise ValueError if end < begin
        """
        with self.assertRaises(ValueError):
            TimeInterval(self.point1000, self.point1000)

    def test_SetBegin(self):
        """
        Raise ValueError if the given TimePoint >= self.End
        """
        interval = TimeInterval(self.point1000, self.point1002)
        with self.assertRaises(ValueError):
            interval.SetBegin( self.point1003 )
        with self.assertRaises(ValueError):
            interval.SetBegin( self.point1002 )

        with self.assertRaises(TypeError):
            interval.SetBegin( 1.00 )

    def test_SetEnd(self):
        """
        Raise ValueError if self.Begin >= the given TimePoint.
        """
        interval = TimeInterval(self.point1000, self.point1002)
        with self.assertRaises(ValueError):
            interval.SetEnd( self.point1000 )

        with self.assertRaises(TypeError):
            interval.SetEnd( 1.00 )

    def test__eq__(self):
        """
        x = y iff
        x.begin = y.begin && x.end = y.end
        """
        interval1 = TimeInterval(self.point1000, self.point1002)
        interval2 = TimeInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 ==  interval2)

    def test__lt__(self):
        """
        x < y iff
        x.begin < y.begin && x.end < y.end
        """
        interval1 = TimeInterval(self.point1000, self.point1002)
        interval2 = TimeInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 < interval2)

        interval1 = TimeInterval(self.point1000, self.point1002)
        interval2 = TimeInterval(self.point1001, self.point1004)
        self.assertFalse(interval1 < interval2)

        # interval |-----|
        # point            |
        self.assertTrue(interval1 < 1.004)
        self.assertTrue(interval1 < self.point1005)
        self.assertTrue(interval1 < 1.003)

        interval1 = TimeInterval(TimePoint(1.5), TimePoint(2))
        interval2 = TimeInterval(TimePoint(1.0), TimePoint(2))
        # 1      |----|
        # 2 |---------|
        self.assertFalse(interval1 < interval2)

    def test__gt__(self):
        """
        x > y iff
        x.begin > y.begin && x.end > y.end
        """
        interval1 = TimeInterval(self.point1004, self.point1006)
        interval2 = TimeInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 > interval2)

        # interval   |-----|
        # point    |
        self.assertTrue(interval1 > 1.002)
        self.assertTrue(interval1 > 1.003)
        self.assertTrue(interval1 > TimePoint(1.003, 0))
        self.assertTrue(interval1 > TimePoint(1.003))
        self.assertFalse(interval1 > 1.006)

    def test__ne__(self):
        interval1 = TimeInterval(self.point1000, self.point1002)
        interval2 = TimeInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 != interval2)

    def test__le__(self):
        interval1 = TimeInterval(self.point1000, self.point1002)
        interval2 = TimeInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 <= interval2)

        interval1 = TimeInterval(self.point1000, self.point1002)
        interval2 = TimeInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 <=  interval2)

        # self  |-------|
        # other |----|
        # False
        interval1 = TimeInterval(self.point1000, self.point1006)
        interval2 = TimeInterval(self.point1000, self.point1003)
        self.assertFalse(interval1 <= interval2)

        # self  |----|
        # other |-------|
        # True
        interval1 = TimeInterval(self.point1000, self.point1003)
        interval2 = TimeInterval(self.point1000, self.point1006)
        self.assertFalse(interval1 <= interval2)

    def test__ge__(self):
        interval1 = TimeInterval(self.point1000, self.point1002)
        interval2 = TimeInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 >=  interval2)

        interval1 = TimeInterval(self.point1004, self.point1006)
        interval2 = TimeInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 >= interval2)

        interval1 = TimeInterval(self.point1000, self.point1002)
        interval2 = TimeInterval(self.point1002, self.point1004)
        self.assertFalse(interval1 >= interval2)

    def test_Duration(self):
        interval1 = TimeInterval(self.point1000, self.point1002)
        self.assertEqual(round(interval1.Duration(), 3), 0.002)


    def test_others(self):
        point0 = TimePoint(0)
        point1 = TimePoint(1, 0.001)
        point2 = TimePoint(2)
        point3 = TimePoint(3, 0.001)
        interval01 = TimeInterval(point0,point1)
        interval001 = interval01
        self.assertEqual(interval01,interval001)
        self.assertTrue(interval01 is interval001)
        interval0001 = interval01.Copy()
        self.assertEqual(interval01,interval0001)
        self.assertFalse(interval01 is interval0001)
        interval23 = TimeInterval(point2,point3)
        interval23.Set( interval01 )
        self.assertFalse(interval23 is interval001)

# End TestTimeInterval
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTimeInterval)
    unittest.TextTestRunner(verbosity=2).run(suite)

