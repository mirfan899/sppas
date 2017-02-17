#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from ..annlocation.timepoint import sppasTimePoint
from ..annlocation.timeinterval import sppasTimeInterval
from ..annlocation.location import sppasLocation

# ---------------------------------------------------------------------------


class TestLocation(unittest.TestCase):

    def test_equal(self):
        loc0 = sppasTimePoint(1)
        loc1 = sppasTimePoint(1.8)
        loc2 = sppasTimePoint(1.8)

        location0 = sppasLocation(loc0)
        location1 = sppasLocation(loc1, score=0.5)
        self.assertEqual(len(location0), 1)
        location0.append(loc2)
        self.assertEqual(len(location0), 2)
        self.assertEqual(location0.get_best(), loc0)

    def test_get(self):
        location = sppasLocation(sppasTimePoint(1))
        location.append(sppasTimePoint(1.8), score=0.5)
        with self.assertRaises(AttributeError):
            location.get_best().get_begin()

        p1 = sppasTimePoint(1.8)
        p2 = sppasTimePoint(2.4)
        location = sppasLocation(p1)

        i = sppasTimeInterval(p1, p2)
        location = sppasLocation(i)
        self.assertEqual(p1, location.get_best().get_begin())
        self.assertEqual(p2, location.get_best().get_end())
        with self.assertRaises(AttributeError):
            location.get_best().get_point()
