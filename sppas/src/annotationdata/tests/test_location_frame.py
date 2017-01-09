#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from annotationdata.ptime.framepoint import FramePoint
from annotationdata.ptime.frameinterval import FrameInterval
from annotationdata.ptime.framedisjoint import FrameDisjoint

# ---------------------------------------------------------------------------


class TestFramePoint(unittest.TestCase):

    def setUp(self):
        self.point0 = FramePoint(0)
        self.pointV = FramePoint(1, 0)
        self.pointW = FramePoint(1, 1)
        self.pointX = FramePoint(1, 1)
        self.pointY = FramePoint(2, 1)
        self.pointZ = FramePoint(3, 1)

    def test__eq__(self):
        """
        x = y iff
        |x - y| < dx + dy
        """
        self.assertEqual(self.pointV, self.pointW)
        self.assertEqual(self.pointV, self.pointY)

    def test__lt__(self):
        """
        x < y iff:
        x != y && x < y
        """
        self.assertLess(self.pointV, self.pointZ)

    def test__gt__(self):
        """
        x > y iff:
        x != y && x > y
        """
        self.assertGreater(self.pointZ, self.pointV)

    def test__ne__(self):
        self.assertNotEqual(self.pointV, self.pointZ)

    def test__le__(self):
        self.assertLessEqual(self.pointV, self.pointY)
        self.assertLessEqual(self.pointV, self.pointZ)

    def test__ge__(self):
        self.assertGreaterEqual(self.pointZ, self.pointW)
        self.assertGreaterEqual(self.pointV, self.pointW)

    def test_others(self):
        point0 = FramePoint(1, 2)
        self.assertEqual(point0.GetMidpoint(), 1)
        self.assertEqual(point0.GetRadius(),   2)
        point1 = point0
        point2 = point0.Copy()
        self.assertEqual(point0,point1)
        self.assertEqual(point0,point2)
        self.assertTrue(point1 is point0)
        self.assertFalse(point2 is point0)

    def test_duration(self):
        point0 = FramePoint(10, 1)
        self.assertEqual(point0.Duration().GetValue(), 0)
        self.assertEqual(point0.Duration().GetMargin(), 2)

# ---------------------------------------------------------------------------


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
            interval.SetBegin(self.point1003)

        with self.assertRaises(TypeError):
            interval.SetBegin(1)

    def test_SetEnd(self):
        """
        Raise ValueError if self.Begin >= the given FramePoint.
        """
        interval = FrameInterval(self.point1000, self.point1002)
        with self.assertRaises(ValueError):
            interval.SetEnd(self.point1000)

        with self.assertRaises(TypeError):
            interval.SetEnd(1)

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
        self.assertEqual(interval1.Duration().GetValue(), 7)
        self.assertEqual(interval1.Duration(), 6)
        self.assertEqual(interval1.Duration(), 7)
        self.assertEqual(interval1.Duration(), 8)

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
        interval23 = FrameInterval(point2, point3)
        interval23.Set(interval01)
        self.assertFalse(interval23 is interval001)

# ---------------------------------------------------------------------------


class TestFrameDisjoint(unittest.TestCase):

    def test__init__(self):
        """
        Raise TypeError
        """
        with self.assertRaises(TypeError):
            FrameDisjoint(10)

    def test__eq__(self):
        intervals1 = FrameDisjoint(*[FrameInterval(FramePoint(i), FramePoint(i+1)) for i in range(10)])
        intervals2 = FrameDisjoint(*[FrameInterval(FramePoint(i), FramePoint(i+1)) for i in range(10)])
        self.assertEquals(intervals1, intervals2)

    def test_Duration(self):
        intervals = [FrameInterval(FramePoint(i), FramePoint(i+1)) for i in range(5)]
        t_disjoint = FrameDisjoint(*intervals)
        self.assertEquals(t_disjoint.Duration().GetValue(), 5)
        self.assertEquals(t_disjoint.Duration().GetMargin(), 0)

    def test_GetInterval(self):
        t_disjoint = FrameDisjoint(*[FrameInterval(FramePoint(i), FramePoint(i+1)) for i in range(10)])
        for i in range(10):
            self.assertEquals(t_disjoint.GetInterval(i), FrameInterval(FramePoint(i), FramePoint(i+1)))

    def test_Is(self):
        t_disjoint = FrameDisjoint(*[FrameInterval(FramePoint(i), FramePoint(i+1)) for i in range(10)])
        self.assertFalse(t_disjoint.IsFramePoint())
        self.assertFalse(t_disjoint.IsFrameInterval())
        self.assertTrue(t_disjoint.IsDisjoint())
        self.assertTrue(t_disjoint.IsFrameDisjoint())

    def test_Set(self):
        t_disjoint= FrameDisjoint(*[FrameInterval(FramePoint(i), FramePoint(i+1)) for i in range(10)])
        t_disjoint.SetBegin(FramePoint(0))
        self.assertEquals(t_disjoint.GetBegin(), FramePoint(0))

        with self.assertRaises(ValueError):
            t_disjoint.SetBegin(FramePoint(1))

        t_disjoint.SetEnd(FramePoint(11))
        self.assertEquals(t_disjoint.GetEnd(), FramePoint(11))
        with self.assertRaises(ValueError):
            t_disjoint.SetEnd(FramePoint(9))

# ---------------------------------------------------------------------------

if __name__ == '__main__':
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(TestFramePoint))
    testsuite.addTest(unittest.makeSuite(TestFrameInterval))
    testsuite.addTest(unittest.makeSuite(TestFrameDisjoint))
    unittest.TextTestRunner(verbosity=2).run(testsuite)
