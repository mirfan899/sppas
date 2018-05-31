#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from ..label.text import Text
from ..label.label import Label

# ---------------------------------------------------------------------------


class TestText(unittest.TestCase):

    def test_decode(self):
        text = Text("\têtre   \r   être être  \n  ")
        self.assertTrue(isinstance(text.GetTypedValue(), unicode))

    def test_value(self):
        # string value
        text = Text(" test ", score=0.5)
        self.assertEquals(text.GetValue(), u"test")
        self.assertEqual(text.GetScore(), 0.5)
        text = Text("test", score=1)
        self.assertTrue(isinstance(text.GetScore(), float))

        # int value
        text = Text(2, data_type="int")
        textstr = Text("2")
        self.assertEquals(text.GetTypedValue(), 2)
        self.assertEquals(text.GetValue(), u"2")
        self.assertNotEquals(text.GetTypedValue(), textstr.GetTypedValue())
        self.assertEquals(text.GetValue(), textstr.GetValue())

        # float value
        text = Text(2.10, data_type="float")
        textstr = Text("2.1")
        self.assertEquals(text.GetTypedValue(), 2.1)
        self.assertEquals(text.GetValue(), u"2.1")
        self.assertNotEquals(text.GetTypedValue(), textstr.GetTypedValue())
        self.assertEquals(text.GetValue(), textstr.GetValue())

        # boolean value
        text = Text("1", data_type="bool")
        textstr = Text("True")
        self.assertEquals(text.GetTypedValue(), True)
        self.assertEquals(text.GetValue(), u"True")
        self.assertNotEquals(text.GetTypedValue(), textstr.GetTypedValue())
        self.assertEquals(text.GetValue(), textstr.GetValue())

    def test_set(self):
        text = Text("test", score=1)
        text.SetValue("toto")
        text.SetScore(0.4)

    def test__eq__(self):
        text1 = Text(" test ", score=0.5)
        text2 = Text("test\n", score=1)
        self.assertEqual(text1, text2)
        self.assertTrue(text1.Equal(text2))
        self.assertFalse(text1.StrictEqual(text2))

# ---------------------------------------------------------------------------


class TestEvents(unittest.TestCase):
    """
    Events are labels with a specific text.
    This is a SPPAS convention!
    Test recognized events: silences, pauses, noises, etc.

    """
    def test_IsSilence(self):
        text = Label("sil")
        self.assertTrue(text.IsSilence())
        self.assertFalse(text.IsSilence() is False)
        text = Label("#")
        self.assertTrue(text.IsSilence())
        self.assertFalse(text.IsSilence() is False)
        text.UnsetValue()
        self.assertFalse(text.IsSilence())

    def test_IsPause(self):
        text = Label("+")
        self.assertTrue(text.IsPause())
        self.assertFalse(text.IsPause() is False)

    def test_IsNoise(self):
        text = Label("*")
        self.assertTrue(text.IsNoise())
        self.assertFalse(text.IsNoise() is False)

# ---------------------------------------------------------------------------


class TestLabel(unittest.TestCase):

    def test_decode(self):
        text = Label("être")
        self.assertIsInstance(text.GetValue(), unicode)

    def test_encode(self):
        text = Label("être")
        self.assertIsInstance(str(text), str)

    def test_labeltype(self):
        text = Label(2, "int")
        self.assertIsInstance(str(text), str)
        self.assertIsInstance(text.GetValue(), unicode)
        self.assertIsInstance(text.GetTypedValue(), int)

    def test_IsLabel(self):
        text = Label("#")
        self.assertFalse(text.IsSpeech())
        text = Label("+")
        self.assertFalse(text.IsSpeech())
        text = Label("*")
        self.assertFalse(text.IsSpeech())
        text = Label("@")
        self.assertFalse(text.IsSpeech())
        text = Label("dummy")
        self.assertFalse(text.IsSpeech())

        text.UnsetValue()
        self.assertTrue(text.IsSpeech())

    def test_AddText(self):
        text = Label(Text("score0.5", score=0.5))
        self.assertEqual(text.GetValue(), u"score0.5")

        text.AddValue(Text("score0.8", score=0.8))
        self.assertEqual(text.GetValue(), u"score0.8")

        text.AddValue(Text("score1.0", score=1.0))
        self.assertEqual(text.GetValue(), u"score1.0")

    def test_IsEmpty(self):
        text = Label(Text("", score=0.5))
        self.assertTrue(text.IsEmpty())

        text.AddValue(Text("text", score=0.8))
        self.assertFalse(text.IsEmpty())

    def test_Unset(self):
        text = Label(Text("", score=0.5))
        self.assertTrue(text.IsEmpty())
        text.UnsetValue()
        self.assertTrue(text.IsEmpty())
