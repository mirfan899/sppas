# -*- coding:utf-8 -*-

import unittest

from ..annlocation.location import sppasLocation
from ..annlocation.timeinterval import sppasTimeInterval
from ..annlocation.timepoint import sppasTimePoint
from ..annlabel.label import sppasText
from ..annlabel.label import sppasLabel
from ..annotation import sppasAnnotation

# ---------------------------------------------------------------------------


class TestAnnotation(unittest.TestCase):
    """
    An annotation in SPPAS is:
        - a location;
        - a label (or not!).
    """
    def setUp(self):
        self.p1 = sppasTimePoint(1)
        self.p2 = sppasTimePoint(2)
        self.p3 = sppasTimePoint(3)
        self.it = sppasTimeInterval(self.p1, self.p2)
        self.annotationI = sppasAnnotation(sppasLocation(self.it), sppasLabel(sppasText(" \t\t  être être   être  \n ")))
        self.annotationP = sppasAnnotation(sppasLocation(self.p1), sppasLabel(sppasText("mark")))

    def test_get_begin(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimePoint.
        """
        with self.assertRaises(AttributeError):
            self.annotationP.get_location().get_begin()

    def test_set_begin(self):
        """
        Raise ValueError if the given time point is greater than the end time value
        of the annotation.
        Raise AttributeError if the attribute Time is an instance of TimePoint.
        """
        with self.assertRaises(ValueError):
            self.annotationI.get_location().set_begin(self.p3)

        with self.assertRaises(AttributeError):
            self.annotationP.get_location().set_begin(self.p2)

    def test_get_begin_value(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimePoint.
        Raise ValueError if the the given time is greater than the end time.
        """
        with self.assertRaises(AttributeError):
            self.annotationP.get_location().get_begin().get_value()

        with self.assertRaises(ValueError):
            self.annotationI.get_location().set_begin(sppasTimePoint(4))
        self.annotationI.get_location().get_begin().set_midpoint(4) #### MUST BE FORBIDDEN...

    def test_get_end(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimePoint.
        """
        with self.assertRaises(AttributeError):
            self.annotationP.get_location().get_end()

    def test_get_end_value(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimePoint.
        """
        with self.assertRaises(AttributeError):
            self.annotationP.get_location().get_end().set_midpoint()

    def test_set_end(self):
        """
        Raise ValueError if the given time point is less than the begin time value of the annotation.
        Raise AttributeError if the attribute Time is not an instance of TimeInterval.
        """
        with self.assertRaises(ValueError):
            self.annotationI.get_location().set_end(self.p1)

        with self.assertRaises(AttributeError):
            self.annotationP.get_location().set_end(self.p2)

    def test_get_point(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimeInterval.
        """
        with self.assertRaises(AttributeError):
            self.annotationI.get_location().get_point()

    def test_get_point_value(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimeInterval.
        """
        with self.assertRaises(AttributeError):
            self.annotationI.get_location().get_point().get_value()

    def test_set_point(self):
        """
        Raise AttributeError if the attribute Time is an instance of TimeInterval.
        """
        with self.assertRaises(AttributeError):
            self.annotationI.get_location().set_point(self.p3)

    def test_is_point(self):
        """
        Return True if the attribute Time is an instance of TimePoint.
        """
        self.assertFalse(self.annotationI.get_location().is_point())
        self.assertTrue(self.annotationP.get_location().is_point())

    def test_is_interval(self):
        """
        Return True if the attribute Time is an instance of TimeInterval.
        """
        self.assertTrue(self.annotationI.get_location().is_interval())
        self.assertFalse(self.annotationP.get_location().is_interval())

    def test_is_silence(self):
        """
        Return True if the attribute Text is an instance of Silence.
        """
        self.assertFalse(self.annotationP.get_label().is_silence())
        self.assertFalse(self.annotationI.get_label().is_silence())

        self.annotationI.get_label().set(sppasLabel("#"))
        self.annotationP.get_label().set(sppasLabel("sil"))
        self.assertTrue(self.annotationI.get_label().is_silence())
        self.assertTrue(self.annotationP.get_label().is_silence())

    def test_copy(self):
        p1 = sppasTimePoint(1)
        p2 = sppasTimePoint(2)
        it = sppasTimeInterval(p1, p2)
        label = sppasLabel("#")
        a = sppasAnnotation(it, label)
        clone = a.copy()
        a.get_location().set_end(sppasTimePoint(10))
        self.assertTrue(clone.get_location().get_end().get_value(), 2)
