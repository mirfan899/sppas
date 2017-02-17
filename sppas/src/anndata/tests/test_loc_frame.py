#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from ..annlocation.framepoint import sppasFramePoint
from ..annlocation.frameinterval import sppasFrameInterval
from ..annlocation.framedisjoint import sppasFrameDisjoint
from ..anndataexc import AnnDataTypeError, IntervalBoundsError

# ---------------------------------------------------------------------------


class TestFramePoint(unittest.TestCase):

    def setUp(self):
        self.point0 = sppasFramePoint(0)
        self.pointV = sppasFramePoint(1, 0)
        self.pointW = sppasFramePoint(1, 1)
        self.pointX = sppasFramePoint(1, 1)
        self.pointY = sppasFramePoint(2, 1)
        self.pointZ = sppasFramePoint(3, 1)

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
        point0 = sppasFramePoint(1, 0)
        self.assertEqual(point0.get_midpoint(), 1)
        self.assertEqual(point0.get_radius(), 0)
        point0 = sppasFramePoint(1, 2)
        self.assertEqual(point0.get_midpoint(), 1)
        self.assertEqual(point0.get_radius(), 1)
        point1 = point0
        point2 = point0.copy()
        self.assertEqual(point0, point1)
        self.assertEqual(point0, point2)
        self.assertTrue(point1 is point0)
        self.assertFalse(point2 is point0)

    def test_duration(self):
        point0 = sppasFramePoint(10, 1)
        self.assertEqual(point0.duration().get_value(), 0)
        self.assertEqual(point0.duration().get_margin(), 2)

# ---------------------------------------------------------------------------


class TestFrameInterval(unittest.TestCase):

    def setUp(self):
        self.point1000 = sppasFramePoint(0, 1)
        self.point1001 = sppasFramePoint(1, 1)
        self.point1002 = sppasFramePoint(2, 0)
        self.point1003 = sppasFramePoint(3, 0)
        self.point1004 = sppasFramePoint(4, 0)
        self.point1005 = sppasFramePoint(5, 0)
        self.point1006 = sppasFramePoint(6, 0)
        self.point1007 = sppasFramePoint(7, 1)

    def test__init__(self):
        """
        Raise ValueError if end < begin
        """
        with self.assertRaises(IntervalBoundsError):
            sppasFrameInterval(self.point1000, self.point1000)

    def test_set_begin(self):
        """
        Raise ValueError if the given FramePoint >= self.End
        """
        interval = sppasFrameInterval(self.point1000, self.point1002)
        with self.assertRaises(IntervalBoundsError):
            interval.set_begin(self.point1003)

        with self.assertRaises(AnnDataTypeError):
            interval.set_begin(1)

    def test_set_end(self):
        """
        Raise ValueError if self.Begin >= the given FramePoint.
        """
        interval = sppasFrameInterval(self.point1000, self.point1002)
        with self.assertRaises(IntervalBoundsError):
            interval.set_end(self.point1000)

        with self.assertRaises(AnnDataTypeError):
            interval.set_end(1)

    def test__eq__(self):
        """
        x = y iff
        x.begin = y.begin && x.end = y.end
        """
        interval1 = sppasFrameInterval(self.point1000, self.point1003)
        interval2 = sppasFrameInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 == interval2)

    def test__lt__(self):
        """
        x < y iff
        x.begin < y.begin && x.end < y.end
        """
        interval1 = sppasFrameInterval(self.point1000, self.point1002)
        interval2 = sppasFrameInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 < interval2)

        interval1 = sppasFrameInterval(self.point1000, self.point1002)
        interval2 = sppasFrameInterval(self.point1001, self.point1004)
        self.assertFalse(interval1 < interval2)

        # interval |-----|
        # point            |
        self.assertTrue(interval1 < 4)
        self.assertTrue(interval1 < self.point1005)
        self.assertTrue(interval1 < 3)

        interval1 = sppasFrameInterval(sppasFramePoint(2), sppasFramePoint(3))
        interval2 = sppasFrameInterval(sppasFramePoint(1), sppasFramePoint(3))
        # 1      |----|
        # 2 |---------|
        self.assertFalse(interval1 < interval2)

    def test__gt__(self):
        """
        x > y iff
        x.begin > y.begin && x.end > y.end
        """
        interval1 = sppasFrameInterval(self.point1004, self.point1006)
        interval2 = sppasFrameInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 > interval2)

        # interval   |-----|
        # point    |
        self.assertTrue(interval1 > 2)
        self.assertTrue(interval1 > 3)
        self.assertTrue(interval1 > sppasFramePoint(3, 0))
        self.assertTrue(interval1 > sppasFramePoint(3))
        self.assertFalse(interval1 > 6)

    def test__ne__(self):
        interval1 = sppasFrameInterval(self.point1000, self.point1002)
        interval2 = sppasFrameInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 != interval2)

    def test__le__(self):
        interval1 = sppasFrameInterval(self.point1000, self.point1002)
        interval2 = sppasFrameInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 <= interval2)

        interval1 = sppasFrameInterval(self.point1000, self.point1003)
        interval2 = sppasFrameInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 <= interval2)

        # self  |-------|
        # other |----|
        # False
        interval1 = sppasFrameInterval(self.point1000, self.point1006)
        interval2 = sppasFrameInterval(self.point1000, self.point1003)
        self.assertFalse(interval1 <= interval2)

        # self  |----|
        # other |-------|
        # True
        interval1 = sppasFrameInterval(self.point1000, self.point1003)
        interval2 = sppasFrameInterval(self.point1000, self.point1006)
        self.assertFalse(interval1 <= interval2)

    def test__ge__(self):
        interval1 = sppasFrameInterval(self.point1000, self.point1003)
        interval2 = sppasFrameInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 >= interval2)

        interval1 = sppasFrameInterval(self.point1004, self.point1006)
        interval2 = sppasFrameInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 >= interval2)

        interval1 = sppasFrameInterval(self.point1000, self.point1002)
        interval2 = sppasFrameInterval(self.point1002, self.point1004)
        self.assertFalse(interval1 >= interval2)

    def test_Duration(self):
        interval1 = sppasFrameInterval(self.point1000, self.point1007)
        self.assertEqual(interval1.duration().get_value(), 7)
        self.assertEqual(interval1.duration(), 6)
        self.assertEqual(interval1.duration(), 7)
        self.assertEqual(interval1.duration(), 8)

    def test_others(self):
        point0 = sppasFramePoint(0)
        point1 = sppasFramePoint(1, 1)
        point2 = sppasFramePoint(2)
        point3 = sppasFramePoint(3, 1)
        interval01 = sppasFrameInterval(point0, point1)
        toto = sppasFrameInterval(sppasFramePoint(2, 1), sppasFramePoint(3, 2))
        with self.assertRaises(ValueError):
            tata = sppasFrameInterval(sppasFramePoint(2, 1), sppasFramePoint(3, 3))

        interval001 = interval01
        self.assertEqual(interval01, interval001)
        self.assertTrue(interval01 is interval001)
        interval0001 = interval01.copy()
        self.assertEqual(interval01, interval0001)
        self.assertFalse(interval01 is interval0001)
        interval23 = sppasFrameInterval(point2, point3)
        interval23.set(interval01)
        self.assertFalse(interval23 is interval001)

# ---------------------------------------------------------------------------


class TestFrameDisjoint(unittest.TestCase):

    def test__init__(self):
        """
        Raise TypeError
        """
        with self.assertRaises(AnnDataTypeError):
            sppasFrameDisjoint(10)

    def test__eq__(self):
        intervals1 = sppasFrameDisjoint([sppasFrameInterval(sppasFramePoint(i), sppasFramePoint(i+1)) for i in range(10)])
        intervals2 = sppasFrameDisjoint([sppasFrameInterval(sppasFramePoint(i), sppasFramePoint(i+1)) for i in range(10)])
        self.assertEqual(intervals1, intervals2)

    def test_Duration(self):
        intervals = [sppasFrameInterval(sppasFramePoint(i), sppasFramePoint(i+1)) for i in range(5)]
        t_disjoint = sppasFrameDisjoint(intervals)
        self.assertEqual(t_disjoint.duration().get_value(), 5)
        self.assertEqual(t_disjoint.duration().get_margin(), 0)

    def test_GetInterval(self):
        t_disjoint = sppasFrameDisjoint([sppasFrameInterval(sppasFramePoint(i), sppasFramePoint(i+1)) for i in range(10)])
        for i in range(10):
            self.assertEqual(t_disjoint.get_interval(i), sppasFrameInterval(sppasFramePoint(i), sppasFramePoint(i+1)))

    def test_Is(self):
        t_disjoint = sppasFrameDisjoint([sppasFrameInterval(sppasFramePoint(i), sppasFramePoint(i+1)) for i in range(10)])
        self.assertFalse(t_disjoint.is_frame_point())
        self.assertFalse(t_disjoint.is_frame_interval())
        self.assertTrue(t_disjoint.is_disjoint())
        self.assertTrue(t_disjoint.is_frame_disjoint())

    def test_Set(self):
        t_disjoint = sppasFrameDisjoint([sppasFrameInterval(sppasFramePoint(i), sppasFramePoint(i+1)) for i in range(10)])
        t_disjoint.set_begin(sppasFramePoint(0))
        self.assertEqual(t_disjoint.get_begin(), sppasFramePoint(0))

        with self.assertRaises(ValueError):
            t_disjoint.set_begin(sppasFramePoint(1))
        t_disjoint.set_end(sppasFramePoint(11))
        self.assertEqual(t_disjoint.get_end(), sppasFramePoint(11))
        with self.assertRaises(ValueError):
            t_disjoint.set_end(sppasFramePoint(9))
