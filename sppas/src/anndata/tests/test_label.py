#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from sppas.src.utils.makeunicode import u
from ..annlabel.text import sppasText
from ..annlabel.label import sppasLabel

# ---------------------------------------------------------------------------


class TestText(unittest.TestCase):

    def test_unicode(self):
        text = sppasText("\têtre   \r   être être  \n  ")
        self.assertIsInstance(str(text), str)

    def test_value(self):
        # string value
        text = sppasText(" test ")
        self.assertEqual(text.get_value(), u("test"))

        # int value
        text = sppasText(2, data_type="int")
        textstr = sppasText("2")
        self.assertEqual(text.get_typed_value(), 2)
        self.assertEqual(text.get_value(), u("2"))
        self.assertNotEquals(text.get_typed_value(), textstr.get_typed_value())
        self.assertEqual(text.get_value(), textstr.get_value())

        # float value
        text = sppasText(2.10, data_type="float")
        textstr = sppasText("2.1")
        self.assertEqual(text.get_typed_value(), 2.1)
        self.assertEqual(text.get_value(), u("2.1"))
        self.assertNotEquals(text.get_typed_value(), textstr.get_typed_value())
        self.assertEqual(text.get_value(), textstr.get_value())

        # boolean value
        text = sppasText("1", data_type="bool")
        textstr = sppasText("True")
        self.assertEqual(text.get_typed_value(), True)
        self.assertEqual(text.get_value(), u("True"))
        self.assertNotEquals(text.get_typed_value(), textstr.get_typed_value())
        self.assertEqual(text.get_value(), textstr.get_value())

    def test_set(self):
        text = sppasText("test")
        text.set_value("toto")

    def test__eq__(self):
        text1 = sppasText(" test    ")
        text2 = sppasText("test\n")
        self.assertEqual(text1, text2)
        self.assertTrue(text1 == text2)

# ---------------------------------------------------------------------------


class TestEvents(unittest.TestCase):
    """ Events are labels with a specific text.
    This is a SPPAS convention!
    Test recognized events: silences, pauses, noises, etc.

    """
    def test_is_silence(self):
        label = sppasLabel(sppasText("sil"))
        text = label.get_best()
        self.assertTrue(text.is_silence())
        self.assertFalse(text.is_silence() is False)
        label = sppasLabel(sppasText("#"))
        text = label.get_best()
        self.assertTrue(text.is_silence())
        self.assertFalse(text.is_silence() is False)

    def test_IsPause(self):
        label = sppasLabel(sppasText("+"))
        self.assertTrue(label.get_best().is_pause())
        self.assertFalse(label.get_best().is_pause() is False)

    def test_IsNoise(self):
        label = sppasLabel(sppasText("*"))
        self.assertTrue(label.get_best().is_noise())
        self.assertFalse(label.get_best().is_noise() is False)

# ---------------------------------------------------------------------------


class TestLabel(unittest.TestCase):

    def test_unicode(self):
        label = sppasLabel(sppasText("être"))

    def test_labeltype(self):
        label = sppasLabel(sppasText(2, "int"))
        self.assertIsInstance(str(label.get_best()), str)
        self.assertIsInstance(label.get_best().get_value(), unicode)
        self.assertIsInstance(label.get_best().get_typed_value(), int)

    def test_IsLabel(self):
        label = sppasLabel(sppasText("#"))
        text = label.get_best()
        self.assertFalse(text.is_speech())

    def test_AddText(self):
        label = sppasLabel(sppasText("score0.5"), score=0.5)
        self.assertEqual(label.get_best().get_value(), u("score0.5"))

        label.append(sppasText("score0.8"), score=0.8)
        self.assertEqual(label.get_best().get_value(), u("score0.8"))

        label.append(sppasText("score1.0"), score=1.0)
        self.assertEqual(label.get_best().get_value(), u("score1.0"))

    def test_IsEmpty(self):
        label = sppasLabel(sppasText(""), score=0.5)
        self.assertTrue(label.get_best().is_empty())

        label.append(sppasText("text"), score=0.8)
        self.assertFalse(label.get_best().is_empty())
