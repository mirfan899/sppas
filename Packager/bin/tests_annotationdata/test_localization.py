#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.ptime.localization import Localization
from annotationdata.ptime.point import TimePoint

# ---------------------------------------------------------------------------

class TestLocalization(unittest.TestCase):

    def test_equal(self):
        loc1 = Localization(TimePoint(1.8), score=0.5)
        loc2 = Localization(TimePoint(1.8))
        self.assertEqual(loc1, loc2)
        self.assertTrue(loc1 == loc2 )
        self.assertFalse(loc1.StrictEqual( loc2 ))
        self.assertEqual(loc1.GetScore(), 0.5)
        self.assertEqual(loc2.GetScore(), 1)



# End TestText
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLocalization)
    unittest.TextTestRunner(verbosity=2).run(suite)

