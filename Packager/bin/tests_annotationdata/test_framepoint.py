#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.ptime.framepoint import FramePoint

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

    def test_parent(self):
        # normal situations
        self.point0 = FramePoint(0)
        self.pointV = FramePoint(0, 1)
        self.assertEqual(self.pointV.GetParent(), None)
        self.assertEqual(self.point0.GetParent(), None)
        self.pointV.SetParent(self.point0)
        self.pointV.SetParent(self.point0)
        self.assertEqual(self.pointV.GetParent(), self.point0)
        self.assertEqual(self.pointV.GetMidpoint(), self.point0.GetMidpoint())
        self.assertEqual(self.pointV.GetRadius(), self.point0.GetRadius())
        # errors:
        self.point0 = FramePoint(0)
        self.pointV = FramePoint(1, 1)
        # assign myself has parent
        with self.assertRaises(BaseException):
            self.point0.SetParent(point0)
        # not assign a FramePoint...
        with self.assertRaises(TypeError):
            self.point0.SetParent(50)
        # Circular parents....
        self.point0 = FramePoint(0)
        self.pointV.SetParent(None)
        self.pointV = FramePoint(1)
        self.pointV.SetParent(self.point0)
        with self.assertRaises(BaseException):
            self.point0.SetParent(self.pointV)

    def test_others(self):
        point0 = FramePoint(1, 2)
        self.assertEqual(point0.GetMidpoint(), 1)
        self.assertEqual(point0.GetRadius(),   1)
        point1 = point0
        point2 = point0.Copy()
        self.assertEqual(point0,point1)
        self.assertEqual(point0,point2)
        self.assertTrue(point1 is point0)
        self.assertFalse(point2 is point0)


# End TestFramePoint
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFramePoint)
    unittest.TextTestRunner(verbosity=2).run(suite)

