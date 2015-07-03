#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint
from annotationdata.ptime.disjoint import TimeDisjoint

class TestTimeDisjoint(unittest.TestCase):

    def test__init__(self):
        """
        Raise TypeError
        """
        with self.assertRaises(TypeError):
            TimeDisjoint(10)

    def test__eq__(self):
        intervals1 = TimeDisjoint(*[TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(10)])
        intervals2 = TimeDisjoint(*[TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(10)])
        self.assertEquals(intervals1, intervals2)

    def test_Duration(self):
        intervals = [TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(5)]
        t_disjoint = TimeDisjoint(*intervals)
        self.assertEquals(t_disjoint.Duration(), 5)

    def test_GetInterval(self):
        t_disjoint = TimeDisjoint(*[TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(10)])
        for i in range(10):
            self.assertEquals(t_disjoint.GetInterval(i), TimeInterval(TimePoint(i), TimePoint(i+1)))

    def test_Is(self):
        t_disjoint = TimeDisjoint(*[TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(10)])
        self.assertFalse(t_disjoint.IsTimePoint())
        self.assertFalse(t_disjoint.IsTimeInterval())
        self.assertTrue(t_disjoint.IsDisjoint())
        self.assertTrue(t_disjoint.IsTimeDisjoint())

    def test_Set(self):
        t_disjoint= TimeDisjoint(*[TimeInterval(TimePoint(i), TimePoint(i+1)) for i in range(10)])
        t_disjoint.SetBegin( TimePoint(0.5) )
        self.assertEquals(t_disjoint.GetBegin(), TimePoint(0.5))

        with self.assertRaises(ValueError):
            t_disjoint.SetBegin( TimePoint(1) )

        t_disjoint.End = TimePoint(11)
        self.assertEquals(t_disjoint.End, TimePoint(11))
        with self.assertRaises(ValueError):
            t_disjoint.SetEnd( TimePoint(9) )

# End TestTimeDisjoint
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTimeDisjoint)
    unittest.TextTestRunner(verbosity=2).run(suite)

