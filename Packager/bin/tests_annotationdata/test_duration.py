#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.ptime.duration import Duration

class TestDuration(unittest.TestCase):

    def setUp(self):
        self.point0 = Duration(0)
        self.pointV = Duration(1.000, 0.001)
        self.pointW = Duration(1.001, 0.001)
        self.pointX = Duration(1.002, 0.001)
        self.pointY = Duration(1.003, 0.003)
        self.pointZ = Duration(1.003, 0.001)

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
        self.assertGreater(self.pointX, self.pointV)
        self.assertGreaterEqual(self.pointX, self.pointV)

        self.assertEqual(self.pointV, 1)
        self.assertEqual(self.pointV, 1.001)
        self.assertGreaterEqual(self.pointV, 1.001)
        self.assertGreaterEqual(self.pointV, 1.002)
        self.assertEqual(self.pointV, self.pointW)
        self.assertGreaterEqual(self.pointV, self.pointV)
        self.assertGreaterEqual(self.pointV, self.pointW)


    def test_others(self):
        point0 = Duration(0.1, 0.2)
        self.assertEqual(point0.GetValue(), 0.1)
        self.assertEqual(point0.GetMargin(),0.1)
        point1 = point0
        self.assertEqual(point0,point1)
        self.assertTrue(point1 is point0)
        point2 = point0.Copy()
        self.assertEqual(point0,point2)
        self.assertFalse(point2 is point0)
        point3 = Duration(0.1, 0.2)
        point2.Set( point3 )
        self.assertFalse(point2 is point3)

# End TestDuration
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDuration)
    unittest.TextTestRunner(verbosity=2).run(suite)

