#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from sppas.src.utils.makeunicode import u, b, text_type
from ..annlabel.tag import sppasTag
from ..annlabel.label import sppasLabel

# ---------------------------------------------------------------------------


class TestTag(unittest.TestCase):

    def test_unicode(self):
        text = sppasTag("\têtre   \r   être être  \n  ")
        self.assertIsInstance(str(text), str)

    def test_value(self):
        # string value
        text = sppasTag(" test ")
        self.assertEqual(text.get_content(), u("test"))

        # int value
        text = sppasTag(2, tag_type="int")
        textstr = sppasTag("2")
        self.assertEqual(text.get_typed_content(), 2)
        self.assertEqual(text.get_content(), u("2"))
        self.assertNotEqual(text.get_typed_content(), textstr.get_typed_content())
        self.assertEqual(text.get_content(), textstr.get_content())

        # float value
        text = sppasTag(2.10, tag_type="float")
        textstr = sppasTag("2.1")
        self.assertEqual(text.get_typed_content(), 2.1)
        self.assertEqual(text.get_content(), u("2.1"))
        self.assertNotEqual(text.get_typed_content(), textstr.get_typed_content())
        self.assertEqual(text.get_content(), textstr.get_content())

        # boolean value
        text = sppasTag("1", tag_type="bool")
        textstr = sppasTag("True")
        self.assertEqual(text.get_typed_content(), True)
        self.assertEqual(text.get_content(), u("True"))
        self.assertNotEqual(text.get_typed_content(), textstr.get_typed_content())
        self.assertEqual(text.get_content(), textstr.get_content())

    def test_set(self):
        text = sppasTag("test")
        text.set_content("toto")

    def test__eq__(self):
        text1 = sppasTag(" test    ")
        text2 = sppasTag("test\n")
        self.assertEqual(text1, text2)
        self.assertTrue(text1 == text2)

# ---------------------------------------------------------------------------


class TestEvents(unittest.TestCase):
    """ Events are labels with a specific text.
    This is a SPPAS convention!
    Test recognized events: silences, pauses, noises, etc.

    """
    def test_is_silence(self):
        label = sppasLabel(sppasTag("sil"))
        text = label.get_best()
        self.assertTrue(text.is_silence())
        self.assertFalse(text.is_silence() is False)
        label = sppasLabel(sppasTag("#"))
        text = label.get_best()
        self.assertTrue(text.is_silence())
        self.assertFalse(text.is_silence() is False)

    def test_IsPause(self):
        label = sppasLabel(sppasTag("+"))
        self.assertTrue(label.get_best().is_pause())
        self.assertFalse(label.get_best().is_pause() is False)

    def test_IsNoise(self):
        label = sppasLabel(sppasTag("*"))
        self.assertTrue(label.get_best().is_noise())
        self.assertFalse(label.get_best().is_noise() is False)

# ---------------------------------------------------------------------------


class TestLabel(unittest.TestCase):

    def test_unicode(self):
        label = sppasLabel(sppasTag("être"))

    def test_labeltype(self):
        label = sppasLabel(sppasTag(2, "int"))
        self.assertIsInstance(str(label.get_best()), str)
        self.assertIsInstance(label.get_best().get_content(), text_type)
        self.assertIsInstance(label.get_best().get_typed_content(), int)

    def test_is_label(self):
        label = sppasLabel(sppasTag("#"))
        text = label.get_best()
        self.assertFalse(text.is_speech())

    def test_add_tag(self):
        label = sppasLabel(sppasTag("score0.5"), score=0.5)
        self.assertEqual(label.get_best().get_content(), u("score0.5"))

        label.append(sppasTag("score0.8"), score=0.8)
        self.assertEqual(label.get_best().get_content(), u("score0.8"))

        label.append(sppasTag("score1.0"), score=1.0)
        self.assertEqual(label.get_best().get_content(), u("score1.0"))

    def test_is_empty(self):
        label = sppasLabel(sppasTag(""), score=0.5)
        self.assertTrue(label.get_best().is_empty())

        label.append(sppasTag("text"), score=0.8)
        self.assertFalse(label.get_best().is_empty())

    def test_equal(self):
        label = sppasLabel(sppasTag(""), score=0.5)
        self.assertTrue(label == label)
        self.assertEqual(label, label)
        self.assertTrue(label == sppasLabel(sppasTag(""), score=0.5))
        self.assertFalse(label == sppasLabel(sppasTag(""), score=0.7))
        self.assertFalse(label == sppasLabel(sppasTag("a"), score=0.5))
