#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.disjoint import TimeDisjoint

# ---------------------------------------------------------------------------


class TestTimePoint(unittest.TestCase):

    def setUp(self):
        self.point0 = TimePoint(0)
        self.pointV = TimePoint(1.000, 0.001)
        self.pointW = TimePoint(1.001, 0.001)
        self.pointX = TimePoint(1.002, 0.001)
        self.pointY = TimePoint(1.003, 0.003)
        self.pointZ = TimePoint(1.003, 0.001)

    def test__eq__(self):
        """
        x = y iff
        |x - y| < dx + dy
        """
        # abs(1.000 - 1.001) < 0.001 + 0.001
        self.assertEqual(self.pointV, self.pointW)

        # abs(1.000 - 1.003) < 0.001 + 0.003
        self.assertEqual(self.pointV, self.pointY)

        # abs(1.000 - 1.002) < 0.001 + 0.001
        self.assertNotEqual(self.pointV, self.pointX)

    def test__lt__(self):
        """
        x < y iff:
        x != y && x < y
        """
        # 1.000 + (0.001 + 0.001) < 1.003
        # self.assertTrue(self.pointV < self.pointZ)
        self.assertLess(self.pointV, self.pointZ)

        # 1.000 + (0.001 + 0.001) < 1.002
        self.assertLess(self.pointV, self.pointX)

    def test__gt__(self):
        """
        x > y iff:
        x != y && x > y
        """
        # 1.003 - (0.001 + 0.001) > 1.001
        self.assertGreater(self.pointZ, self.pointV)

        # 1.002 - (0.001 + 0.001) > 1.001
        self.assertGreater(self.pointX, self.pointV)

    def test__ne__(self):
        self.assertNotEqual(self.pointV, self.pointX)

    def test__le__(self):
        self.assertLessEqual(self.pointV, self.pointZ)
        self.assertLessEqual(self.pointV, self.pointW)

    def test__ge__(self):
        self.assertGreaterEqual(self.pointX, self.pointV)
        self.assertGreaterEqual(self.pointV, self.pointW)

    def test_others(self):
        point0 = TimePoint(0.1, 0.2)
        self.assertEqual(point0.GetMidpoint(), 0.1)
        self.assertEqual(point0.GetRadius(),   0.1)
        point1 = point0
        self.assertEqual(point0, point1)
        self.assertTrue(point1 is point0)
        point2 = point0.Copy()
        self.assertEqual(point0, point2)
        self.assertFalse(point2 is point0)
        point3 = TimePoint(0.1, 0.2)
        point2.Set(point3)
        self.assertFalse(point2 is point3)
        self.assertEqual(point0.Duration(),0.)
        pointd = TimePoint(0.3, 0.1)
        self.assertEqual(pointd.Duration(), 0.)
        self.assertEqual(pointd.Duration(), 0.1)

# ---------------------------------------------------------------------------


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
            interval.SetBegin(self.point1003)
        with self.assertRaises(ValueError):
            interval.SetBegin(self.point1002)

        with self.assertRaises(TypeError):
            interval.SetBegin(1.00)

    def test_SetEnd(self):
        """
        Raise ValueError if self.Begin >= the given TimePoint.
        """
        interval = TimeInterval(self.point1000, self.point1002)
        with self.assertRaises(ValueError):
            interval.SetEnd(self.point1000)

        with self.assertRaises(TypeError):
            interval.SetEnd(1.00)

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
        self.assertTrue(interval1 <= interval2)

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
        self.assertTrue(interval1 >= interval2)

        interval1 = TimeInterval(self.point1004, self.point1006)
        interval2 = TimeInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 >= interval2)

        interval1 = TimeInterval(self.point1000, self.point1002)
        interval2 = TimeInterval(self.point1002, self.point1004)
        self.assertFalse(interval1 >= interval2)

    def test_Duration(self):
        point1 = TimePoint(1, 0.001)
        point3 = TimePoint(3, 0.001)
        interval13 = TimeInterval(point1, point3)
        self.assertEqual(interval13.Duration(), 2)
        self.assertEqual(interval13.Duration(), 2.0)
        self.assertEqual(interval13.Duration(), 1.999)
        self.assertEqual(interval13.Duration(), 2.001)
        self.assertGreaterEqual(interval13.Duration(), 2.002)

    def test_others(self):
        point0 = TimePoint(0)
        point1 = TimePoint(1, 0.001)
        point2 = TimePoint(2)
        point3 = TimePoint(3, 0.001)
        interval01 = TimeInterval(point0, point1)
        interval001 = interval01
        self.assertEqual(interval01, interval001)
        self.assertTrue(interval01 is interval001)
        interval0001 = interval01.Copy()
        self.assertEqual(interval01,interval0001)
        self.assertFalse(interval01 is interval0001)
        interval23 = TimeInterval(point2, point3)
        interval23.Set(interval01)
        self.assertFalse(interval23 is interval001)

# ---------------------------------------------------------------------------


class TestTimeDisjoint(unittest.TestCase):

    def test__init__(self):
        with self.assertRaises(TypeError):
            TimeDisjoint(10)

    def test__eq__(self):
        intervals1 = TimeDisjoint(*[TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(10)])
        intervals2 = TimeDisjoint(*[TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(10)])
        self.assertEquals(intervals1, intervals2)

    def test_Duration(self):
        intervals = [TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(5)]
        t_disjoint = TimeDisjoint(*intervals)
        self.assertEquals(t_disjoint.Duration().GetValue(), 5)
        self.assertEquals(t_disjoint.Duration().GetMargin(), 0)

    def test_GetInterval(self):
        t_disjoint = TimeDisjoint(*[TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(10)])
        for i in range(10):
            self.assertEquals(t_disjoint.GetInterval(i), TimeInterval(TimePoint(i), TimePoint(i+1)))

    def test_Is(self):
        t_disjoint = TimeDisjoint(*[TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(10)])
        self.assertFalse(t_disjoint.IsTimePoint())
        self.assertFalse(t_disjoint.IsTimeInterval())
        self.assertTrue(t_disjoint.IsDisjoint())
        self.assertTrue(t_disjoint.IsTimeDisjoint())

    def test_Set(self):
        t_disjoint= TimeDisjoint(*[TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(10)])
        t_disjoint.SetBegin(TimePoint(0.5))
        self.assertEquals(t_disjoint.GetBegin(), TimePoint(0.5))

        with self.assertRaises(ValueError):
            t_disjoint.SetBegin(TimePoint(1))

        t_disjoint.End = TimePoint(11)
        self.assertEquals(t_disjoint.End, TimePoint(11))
        with self.assertRaises(ValueError):
            t_disjoint.SetEnd(TimePoint(9))

# ---------------------------------------------------------------------------

if __name__ == '__main__':
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(TestTimePoint))
    testsuite.addTest(unittest.makeSuite(TestTimeInterval))
    testsuite.addTest(unittest.makeSuite(TestTimeDisjoint))
    unittest.TextTestRunner(verbosity=2).run(testsuite)

