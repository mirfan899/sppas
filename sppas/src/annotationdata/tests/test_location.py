#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from ..ptime.point import TimePoint
from ..ptime.interval import TimeInterval
from ..ptime.localization import Localization
from ..ptime.location import Location

# ---------------------------------------------------------------------------


class TestLocalization(unittest.TestCase):

    def test_equal(self):
        loc1 = Localization(TimePoint(1.8), score=0.5)
        loc2 = Localization(TimePoint(1.8))
        self.assertEqual(loc1, loc2)
        self.assertTrue(loc1 == loc2)
        self.assertFalse(loc1.StrictEqual(loc2))
        self.assertEqual(loc1.GetScore(), 0.5)
        self.assertEqual(loc2.GetScore(), 1)

# ---------------------------------------------------------------------------


class TestLocation(unittest.TestCase):

    def test_equal(self):
        loc0 = TimePoint(1)
        loc1 = Localization(TimePoint(1.8), score=0.5)
        loc2 = Localization(TimePoint(1.8))
        loc3 = Localization(TimePoint(2.0), score=0.5)

        location0 = Location(loc0)
        location1 = Location(loc1)
        self.assertEqual(len(location0), 1)
        location0.AddValue(loc2)
        self.assertEqual(len(location0), 2)
        self.assertEqual(location0.GetValue().GetPlace(), loc0)

    def test_best_value(self):
        loc0 = TimePoint(1)
        loc1 = Localization(TimePoint(1.8), score=0.5)
        location = Location(loc0)
        location.AddValue(loc1)
        with self.assertRaises(AttributeError):
            location.GetBegin()

    def test_get(self):
        p1 = TimePoint(1.8)
        p2 = TimePoint(2.4)
        location = Location(p1)
        self.assertEqual(p1, location.GetPoint())
        with self.assertRaises(AttributeError):
            location.GetBegin()
        with self.assertRaises(AttributeError):
            location.GetEnd()

        i = TimeInterval(p1, p2)
        location = Location(i)
        self.assertEqual(p1, location.GetBegin())
        self.assertEqual(p2, location.GetEnd())
        with self.assertRaises(AttributeError):
            location.GetPoint()
