#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlocation.location import sppasLocation

# ---------------------------------------------------------------------------


class TestLocation(unittest.TestCase):

    def test_apppend(self):
        loc0 = sppasPoint(1)
        loc1 = sppasPoint(1.8)
        loc2 = sppasPoint(1.8)

        location0 = sppasLocation(loc0)
        self.assertEqual(len(location0), 1)
        location0.append(loc2)
        self.assertEqual(len(location0), 2)
        self.assertEqual(location0.get_best(), loc0)

        location1 = sppasLocation(loc0, score=0.5)

        # expect error (types inconsistency)
        with self.assertRaises(TypeError):
            location1.append(sppasInterval(loc0, loc2), score=0.5)

    def test_get(self):
        location = sppasLocation(sppasPoint(1))
        location.append(sppasPoint(1.8), score=0.5)
        with self.assertRaises(AttributeError):
            location.get_best().get_begin()

        p1 = sppasPoint(1.8)
        p2 = sppasPoint(2.4)
        location = sppasLocation(p1)

        i = sppasInterval(p1, p2)
        location = sppasLocation(i)
        self.assertEqual(p1, location.get_best().get_begin())
        self.assertEqual(p2, location.get_best().get_end())
        with self.assertRaises(AttributeError):
            location.get_best().get_point()

    def test_equal(self):
        loc = sppasLocation(sppasPoint(0), score=0.5)
        self.assertTrue(loc == loc)
        self.assertEqual(loc, loc)
        self.assertEqual(loc, sppasLocation(sppasPoint(0), score=0.5))
        self.assertFalse(loc == sppasLocation(sppasPoint(0), score=1.))
        self.assertFalse(loc == sppasLocation(sppasPoint(1), score=0.5))
