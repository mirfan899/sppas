#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.label.label import Label
from annotationdata.annotation import Annotation


class TestAnnotation(unittest.TestCase):
    """ Represents an annotation.
        An annotation in SPPAS is:
            - a time object (a TimePoint or a TimeInterval instance);
            - a textentry (a Label instance).
    """
    def setUp(self):
        self.p1 = TimePoint(1)
        self.p2 = TimePoint(2)
        self.p3 = TimePoint(3)
        self.it = TimeInterval(self.p1, self.p2)
        self.annotationI = Annotation(self.it, Label(" \t\t  être être   être  \n "))
        self.annotationP= Annotation(self.p1, Label("mark"))

    def test___init__(self):
        pass

    def test_GetBegin(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimePoint.
        """
        with self.assertRaises(AttributeError):
            self.annotationP.GetLocation().GetBegin()

    def test_SetBegin(self):
        """
        Raise ValueError if the given time point is greater than the end time value
        of the annotation.
        Raise AttributeError if the attribute Time is an instance of TimePoint.
        """
        with self.assertRaises(ValueError):
            self.annotationI.GetLocation().SetBegin( self.p3 )

        with self.assertRaises(AttributeError):
            self.annotationP.GetLocation().SetBegin( self.p2 )

    def test_GetBeginValue(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimePoint.
        Raise ValueError if the the given time is greater than the end time.
        """
        with self.assertRaises(AttributeError):
            self.annotationP.GetLocation().GetBeginValue()

        with self.assertRaises(ValueError):
            self.annotationI.GetLocation().SetBegin( TimePoint(4) )
        self.annotationI.GetLocation().GetBegin().SetMidpoint( 4 ) #### MUST BE FORBIDDEN...

    def test_GetEnd(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimePoint.
        """
        with self.assertRaises(AttributeError):
            self.annotationP.GetLocation().GetEnd()

    def test_GetEndValue(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimePoint.
        """
        with self.assertRaises(AttributeError):
            self.annotationP.GetLocation().GetEnd().SetMidpoint()

    def test_SetEnd(self):
        """
        Raise ValueError if the given time point is less than the begin time value of the annotation.
        Raise AttributeError if the attribute Time is not an instance of TimeInterval.
        """
        with self.assertRaises(ValueError):
            self.annotationI.GetLocation().SetEnd( self.p1 )

        with self.assertRaises(AttributeError):
            self.annotationP.GetLocation().SetEnd( self.p2 )

    def test_GetPoint(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimeInterval.
        """
        with self.assertRaises(AttributeError):
            self.annotationI.GetLocation().GetPoint()

    def test_GetPointValue(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimeInterval.
        """
        with self.assertRaises(AttributeError):
            self.annotationI.GetLocation().GetPointValue()

    def test_SetPoint(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimeInterval.
        """
        with self.assertRaises(AttributeError):
            self.annotationI.GetLocation().SetPoint( self.p3 )

    def test_IsPoint(self):
        """
        Return True if the attribute Time is an instance of TimePoint.
        """
        self.assertFalse(self.annotationI.GetLocation().IsPoint())
        self.assertTrue(self.annotationP.GetLocation().IsPoint())

    def test_IsInterval(self):
        """
        Return True if the attribute Time is an instance of TimeInterval.
        """
        self.assertTrue(self.annotationI.GetLocation().IsInterval())
        self.assertFalse(self.annotationP.GetLocation().IsInterval())

    def test_IsSilence(self):
        """
        Return True if the attribute Text is an instance of Silence.
        """
        self.assertFalse(self.annotationP.GetLabel().IsSilence())
        self.assertFalse(self.annotationI.GetLabel().IsSilence())

        self.annotationI.GetLabel().Set( Label("#") )
        self.annotationP.GetLabel().Set( Label("sil"))
        self.assertTrue(self.annotationI.GetLabel().IsSilence())
        self.assertTrue(self.annotationP.GetLabel().IsSilence())

    def test_Copy(self):
        p1 = TimePoint(1)
        p2 = TimePoint(2)
        it = TimeInterval(p1, p2)
        label = Label("#")
        a = Annotation(it, label)
        clone = a.Copy()
        a.GetLocation().SetEnd(TimePoint(10))
        self.assertTrue(clone.GetLocation().GetEnd().GetValue(), 2)

# End TestAnnotation
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnnotation)
    unittest.TextTestRunner(verbosity=2).run(suite)

