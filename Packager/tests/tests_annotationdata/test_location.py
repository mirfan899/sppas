#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.ptime.location import Location
from annotationdata.ptime.localization import Localization
from annotationdata.ptime.point    import TimePoint
from annotationdata.ptime.interval import TimeInterval

# ---------------------------------------------------------------------------

class TestLocation(unittest.TestCase):

    def test_equal(self):
        loc0 = TimePoint(1)
        loc1 = Localization(TimePoint(1.8), score=0.5)
        loc2 = Localization(TimePoint(1.8))
        loc3 = Localization(TimePoint(2.0), score=0.5)

        location0 = Location( loc0 )
        location1 = Location( loc1 )
        self.assertEqual(len(location0),1)
        location0.AddValue(loc2)
        self.assertEqual(len(location0),2)
        self.assertEqual(location0.GetValue().GetPlace(),loc0)

    def test_best_value(self):
        loc0 = TimePoint(1)
        loc1 = Localization(TimePoint(1.8), score=0.5)
        location = Location( loc0 )
        location.AddValue(loc1)
        with self.assertRaises(AttributeError):
            location.GetBegin()


# End TestText
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLocation)
    unittest.TextTestRunner(verbosity=2).run(suite)

