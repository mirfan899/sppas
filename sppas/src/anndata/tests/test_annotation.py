# -*- coding:utf-8 -*-

import unittest

from ..annlocation.location import sppasLocation
from ..annlocation.interval import sppasInterval
from ..annlocation.point import sppasPoint
from ..annlabel.label import sppasTag
from ..annlabel.label import sppasLabel
from ..annotation import sppasAnnotation

# ---------------------------------------------------------------------------


class TestAnnotation(unittest.TestCase):

    def setUp(self):
        self.p1 = sppasPoint(1)
        self.p2 = sppasPoint(2)
        self.p3 = sppasPoint(3)
        self.it = sppasInterval(self.p1, self.p2)
        self.annotationI = sppasAnnotation(sppasLocation(self.it), sppasLabel(sppasTag(" \t\t  être être   être  \n ")))
        self.annotationP = sppasAnnotation(sppasLocation(self.p1), sppasLabel(sppasTag("mark")))

    def test_get_begin(self):
        with self.assertRaises(AttributeError):
            self.annotationP.get_location().get_begin()

    def test_set_begin(self):
        with self.assertRaises(ValueError):
            self.annotationI.get_location().get_best().set_begin(self.p3)

        with self.assertRaises(AttributeError):
            self.annotationP.get_location().get_best().set_begin(self.p2)

    def test_get_begin_value(self):
        with self.assertRaises(AttributeError):
            self.annotationP.get_location().get_best().get_begin().get_content()

        with self.assertRaises(ValueError):
            self.annotationI.get_location().get_best().set_begin(sppasPoint(4))
        self.annotationI.get_location().get_best().get_begin().set_midpoint(4) #### MUST BE FORBIDDEN...

    def test_get_end(self):
        with self.assertRaises(AttributeError):
            self.annotationP.get_location().get_best().get_end()

    def test_get_end_value(self):
        with self.assertRaises(AttributeError):
            self.annotationP.get_location().get_best().get_end().set_midpoint()

    def test_set_end(self):
        with self.assertRaises(ValueError):
            self.annotationI.get_location().get_best().set_end(self.p1)

        with self.assertRaises(AttributeError):
            self.annotationP.get_location().get_best().set_end(self.p2)

    def test_get_point(self):
        with self.assertRaises(AttributeError):
            self.annotationI.get_location().get_best().get_point()

    def test_get_point_value(self):
        with self.assertRaises(AttributeError):
            self.annotationI.get_location().get_best().get_point().get_content()

    def test_set_point(self):
        with self.assertRaises(AttributeError):
            self.annotationI.get_location().get_best().set_point(self.p3)

    def test_is_point(self):
        self.assertFalse(self.annotationI.get_location().get_best().is_point())
        self.assertTrue(self.annotationP.get_location().get_best().is_point())

    def test_is_interval(self):
        self.assertTrue(self.annotationI.get_location().get_best().is_interval())
        self.assertFalse(self.annotationP.get_location().get_best().is_interval())

    def test_is_silence(self):
        self.assertFalse(self.annotationP.get_label().get_best().is_silence())
        self.assertFalse(self.annotationI.get_label().get_best().is_silence())

        self.annotationI.get_label().get_best().set(sppasTag("#"))
        self.annotationP.get_label().get_best().set(sppasTag("sil"))
        self.assertTrue(self.annotationI.get_label().get_best().is_silence())
        self.assertTrue(self.annotationP.get_label().get_best().is_silence())

    def test_copy(self):
        p1 = sppasPoint(1)
        p2 = sppasPoint(2)
        it = sppasLocation(sppasInterval(p1, p2))
        label = sppasLabel(sppasTag("#"))
        a = sppasAnnotation(it, label)
        clone = a.copy()
        a.get_location().get_best().set_end(sppasPoint(10))
        self.assertTrue(clone.get_location().get_best().get_end().get_midpoint(), 2)

    def test_contains(self):
        self.assertTrue(self.annotationI.contains_localization(sppasPoint(1)))
        self.assertFalse(self.annotationI.contains_localization(sppasPoint(10)))

    def test_equal(self):
        p1 = sppasPoint(1)
        p2 = sppasPoint(2)
        it = sppasLocation(sppasInterval(p1, p2))
        label = sppasLabel(sppasTag("#"))
        a = sppasAnnotation(it, label)
        self.assertTrue(a == a)
        self.assertEqual(a, a)
        self.assertEqual(a, sppasAnnotation(it, label))
        self.assertNotEqual(a, sppasAnnotation(it, sppasLabel(sppasTag("#"), score=0.2)))
        self.assertNotEqual(a, sppasAnnotation(sppasLocation(sppasInterval(p1, p2), score=0.3), label))
