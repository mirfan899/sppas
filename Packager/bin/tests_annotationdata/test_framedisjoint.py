#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.ptime.frameinterval import FrameInterval
from annotationdata.ptime.framepoint    import FramePoint
from annotationdata.ptime.framedisjoint import FrameDisjoint

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
        t_disjoint.SetBegin( FramePoint(0) )
        self.assertEquals(t_disjoint.GetBegin(), FramePoint(0))

        with self.assertRaises(ValueError):
            t_disjoint.SetBegin( FramePoint(1) )

        t_disjoint.SetEnd( FramePoint(11) )
        self.assertEquals(t_disjoint.GetEnd(), FramePoint(11))
        with self.assertRaises(ValueError):
            t_disjoint.SetEnd( FramePoint(9) )

# End TestFrameDisjoint
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFrameDisjoint)
    unittest.TextTestRunner(verbosity=2).run(suite)

