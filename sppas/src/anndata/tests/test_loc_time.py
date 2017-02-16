#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from ..annloc.timepoint import sppasTimePoint, sppasLocTimePoint
from ..annloc.timeinterval import sppasTimeInterval, sppasLocTimeInterval
#from ..annloc.timedisjoint import sppasTimeDisjoint
from ..anndataexc import AnnDataTypeError
from ..anndataexc import AnnDataNegValueError

# ---------------------------------------------------------------------------


class TestTimePoint(unittest.TestCase):

    def setUp(self):
        self.point0 = sppasTimePoint(0)
        self.pointV = sppasTimePoint(1.000, 0.001)
        self.pointW = sppasTimePoint(1.001, 0.001)
        self.pointX = sppasTimePoint(1.002, 0.001)
        self.pointY = sppasTimePoint(1.003, 0.003)
        self.pointZ = sppasTimePoint(1.003, 0.001)

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
        point0 = sppasLocTimePoint(0.1, 0.2)
        self.assertEqual(point0.get_midpoint(), 0.1)
        self.assertEqual(point0.get_radius(),   0.1)
        point1 = point0
        self.assertEqual(point0.get_midpoint(), point1.get_midpoint())
        self.assertEqual(point0.get_radius(), point1.get_radius())
        self.assertTrue(point1 is point0)
        point2 = point0.copy()
        self.assertEqual(point0.get_midpoint(), point2.get_midpoint())
        self.assertEqual(point0.get_radius(), point2.get_radius())
        self.assertFalse(point2 is point0)
        point3 = sppasLocTimePoint(0.1, 0.2)
        point2.set(point3)
        self.assertFalse(point2 is point3)
        self.assertEqual(point0.duration(), 0.)
        pointd = sppasLocTimePoint(0.3, 0.1)
        self.assertEqual(pointd.duration(), 0.)
        self.assertEqual(pointd.duration(), 0.1)

        # now, test errors
        point0 = sppasLocTimePoint(0.1)
        with self.assertRaises(AnnDataTypeError):
            point0.set([9])
        with self.assertRaises(AnnDataTypeError):
            point0.set_midpoint([9])
        with self.assertRaises(AnnDataTypeError):
            point0.set_radius([9])
        with self.assertRaises(AnnDataNegValueError):
            point0.set_midpoint(-5)
        with self.assertRaises(AnnDataNegValueError):
            point0.set_radius(-5)

# ---------------------------------------------------------------------------

#
# class TestTimeInterval(unittest.TestCase):
#
#     def setUp(self):
#         self.point1000 = sppasTimePoint(1.000, 0.0005)
#         self.point1001 = sppasTimePoint(1.001, 0.0005)
#         self.point1002 = sppasTimePoint(1.002, 0.0005)
#         self.point1003 = sppasTimePoint(1.003, 0.0005)
#         self.point1004 = sppasTimePoint(1.004, 0.0005)
#         self.point1005 = sppasTimePoint(1.005, 0.0005)
#         self.point1006 = sppasTimePoint(1.006, 0.0005)
#         self.point1007 = sppasTimePoint(1.007, 0.0005)
#
#     def test__init__(self):
#         """
#         Raise ValueError if end < begin
#         """
#         with self.assertRaises(ValueError):
#             sppasTimeInterval(self.point1000, self.point1000)
#
#     def test_set_begin(self):
#         """
#         Raise ValueError if the given TimePoint >= self.End
#         """
#         interval = sppasTimeInterval(self.point1000, self.point1002)
#         with self.assertRaises(ValueError):
#             interval.set_begin(self.point1003)
#         with self.assertRaises(ValueError):
#             interval.set_begin(self.point1002)
#
#         with self.assertRaises(AnnDataTypeError):
#             interval.set_begin(1.0)
#
#     def test_set_end(self):
#         """
#         Raise ValueError if self.Begin >= the given TimePoint.
#         """
#         interval = sppasTimeInterval(self.point1000, self.point1002)
#         with self.assertRaises(ValueError):
#             interval.set_end(self.point1000)
#
#         with self.assertRaises(AnnDataTypeError):
#             interval.set_end(1.00)
#
#     def test__eq__(self):
#         """
#         x = y iff
#         x.begin = y.begin && x.end = y.end
#         """
#         interval1 = sppasTimeInterval(self.point1000, self.point1002)
#         interval2 = sppasTimeInterval(self.point1001, self.point1003)
#         self.assertTrue(interval1 == interval2)
#
#     def test__lt__(self):
#         """
#         x < y iff
#         x.begin < y.begin && x.end < y.end
#         """
#         interval1 = sppasTimeInterval(self.point1000, self.point1002)
#         interval2 = sppasTimeInterval(self.point1002, self.point1004)
#         self.assertTrue(interval1 < interval2)
#
#         interval1 = sppasTimeInterval(self.point1000, self.point1002)
#         interval2 = sppasTimeInterval(self.point1001, self.point1004)
#         self.assertFalse(interval1 < interval2)
#
#         # interval |-----|
#         # point            |
#         self.assertTrue(interval1 < 1.004)
#         self.assertTrue(interval1 < self.point1005)
#         self.assertTrue(interval1 < 1.003)
#
#         interval1 = sppasTimeInterval(sppasTimePoint(1.5), sppasTimePoint(2))
#         interval2 = sppasTimeInterval(sppasTimePoint(1.0), sppasTimePoint(2))
#         # 1      |----|
#         # 2 |---------|
#         self.assertFalse(interval1 < interval2)
#
#     def test__gt__(self):
#         """
#         x > y iff
#         x.begin > y.begin && x.end > y.end
#         """
#         interval1 = sppasTimeInterval(self.point1004, self.point1006)
#         interval2 = sppasTimeInterval(self.point1000, self.point1002)
#         self.assertTrue(interval1 > interval2)
#
#         # interval   |-----|
#         # point    |
#         self.assertTrue(interval1 > 1.002)
#         self.assertTrue(interval1 > 1.003)
#         self.assertTrue(interval1 > sppasTimePoint(1.003, 0))
#         self.assertTrue(interval1 > sppasTimePoint(1.003))
#         self.assertFalse(interval1 > 1.006)
#
#     def test__ne__(self):
#         interval1 = sppasTimeInterval(self.point1000, self.point1002)
#         interval2 = sppasTimeInterval(self.point1002, self.point1004)
#         self.assertTrue(interval1 != interval2)
#
#     def test__le__(self):
#         interval1 = sppasTimeInterval(self.point1000, self.point1002)
#         interval2 = sppasTimeInterval(self.point1002, self.point1004)
#         self.assertTrue(interval1 <= interval2)
#
#         interval1 = sppasTimeInterval(self.point1000, self.point1002)
#         interval2 = sppasTimeInterval(self.point1001, self.point1003)
#         self.assertTrue(interval1 <= interval2)
#
#         # self  |-------|
#         # other |----|
#         # False
#         interval1 = sppasTimeInterval(self.point1000, self.point1006)
#         interval2 = sppasTimeInterval(self.point1000, self.point1003)
#         self.assertFalse(interval1 <= interval2)
#
#         # self  |----|
#         # other |-------|
#         # True
#         interval1 = sppasTimeInterval(self.point1000, self.point1003)
#         interval2 = sppasTimeInterval(self.point1000, self.point1006)
#         self.assertFalse(interval1 <= interval2)
#
#     def test__ge__(self):
#         interval1 = sppasTimeInterval(self.point1000, self.point1002)
#         interval2 = sppasTimeInterval(self.point1001, self.point1003)
#         self.assertTrue(interval1 >= interval2)
#
#         interval1 = sppasTimeInterval(self.point1004, self.point1006)
#         interval2 = sppasTimeInterval(self.point1000, self.point1002)
#         self.assertTrue(interval1 >= interval2)
#
#         interval1 = sppasTimeInterval(self.point1000, self.point1002)
#         interval2 = sppasTimeInterval(self.point1002, self.point1004)
#         self.assertFalse(interval1 >= interval2)
#
#     def test_Duration(self):
#         point1 = sppasTimePoint(1, 0.001)
#         point3 = sppasTimePoint(3, 0.001)
#         interval13 = sppasLocTimeInterval(point1, point3)
#         self.assertEqual(interval13.duration(), 2)
#         self.assertEqual(interval13.duration(), 2.0)
#         self.assertEqual(interval13.duration(), 1.999)
#         self.assertEqual(interval13.duration(), 2.001)
#         self.assertGreaterEqual(interval13.duration(), 2.002)
#
#     def test_others(self):
#         point0 = sppasTimePoint(0)
#         point1 = sppasTimePoint(1, 0.001)
#         point2 = sppasTimePoint(2)
#         point3 = sppasTimePoint(3, 0.001)
#         interval01 = sppasLocTimeInterval(point0, point1)
#         interval001 = interval01
#         self.assertEqual(interval01.get_begin(), interval001.get_begin())
#         self.assertEqual(interval01.get_end(), interval001.get_end())
#         self.assertTrue(interval01 is interval001)
#         interval0001 = interval01.copy()
#         self.assertEqual(interval01.get_begin(), interval0001.get_begin())
#         self.assertEqual(interval01.get_end(), interval0001.get_end())
#         self.assertFalse(interval01 is interval0001)
#         interval23 = sppasLocTimeInterval(point2, point3)
#         interval23.set(interval01)
#         self.assertFalse(interval23 is interval001)

# ---------------------------------------------------------------------------

# 
# class TestTimeDisjoint(unittest.TestCase):
# 
#     def test__init__(self):
#         with self.assertRaises(TypeError):
#             sppasTimeDisjoint(10)
# 
#     def test__eq__(self):
#         intervals1 = sppasTimeDisjoint(*[sppasTimeInterval(TimePoint(i), sppasTimePoint(i+1)) for i in range(10)])
#         intervals2 = sppasTimeDisjoint(*[sppasTimeInterval(TimePoint(i), sppasTimePoint(i+1)) for i in range(10)])
#         self.assertEquals(intervals1, intervals2)
# 
#     def test_Duration(self):
#         intervals = [sppasTimeInterval(sppasTimePoint(i), sppasTimePoint(i+1)) for i in range(5)]
#         t_disjoint = sppasTimeDisjoint(*intervals)
#         self.assertEquals(t_disjoint.duration().GetValue(), 5)
#         self.assertEquals(t_disjoint.duration().GetMargin(), 0)
# 
#     def test_GetInterval(self):
#         t_disjoint = sppasTimeDisjoint(*[sppasTimeInterval(sppasTimePoint(i), sppasTimePoint(i+1)) for i in range(10)])
#         for i in range(10):
#             self.assertEquals(t_disjoint.GetInterval(i), sppasTimeInterval(sppasTimePoint(i), sppasTimePoint(i+1)))
# 
#     def test_Is(self):
#         t_disjoint = sppasTimeDisjoint(*[sppasTimeInterval(sppasTimePoint(i), sppasTimePoint(i+1)) for i in range(10)])
#         self.assertFalse(t_disjoint.IsTimePoint())
#         self.assertFalse(t_disjoint.IsTimeInterval())
#         self.assertTrue(t_disjoint.IsDisjoint())
#         self.assertTrue(t_disjoint.IsTimeDisjoint())
# 
#     def test_Set(self):
#         t_disjoint = sppasTimeDisjoint(*[sppasTimeInterval(sppasTimePoint(i), sppasTimePoint(i+1)) for i in range(10)])
#         t_disjoint.set_begin(sppasTimePoint(0.5))
#         self.assertEquals(t_disjoint.GetBegin(), sppasTimePoint(0.5))
# 
#         with self.assertRaises(ValueError):
#             t_disjoint.set_begin(sppasTimePoint(1))
# 
#         t_disjoint.End = sppasTimePoint(11)
#         self.assertEquals(t_disjoint.End, sppasTimePoint(11))
#         with self.assertRaises(ValueError):
#             t_disjoint.set_end(sppasTimePoint(9))
