#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.label.label import Label
from annotationdata.label.text import Text

class TestLabel(unittest.TestCase):

    def test_decode(self):
        text = Label("être")
        self.assertIsInstance(text.GetValue(), unicode)

    def test_encode(self):
        text = Label("être")
        self.assertIsInstance(str(text), str)

    def test_labeltype(self):
        text = Label(2,"int")
        self.assertIsInstance(str(text), str)
        self.assertIsInstance(text.GetValue(), unicode)
        self.assertIsInstance(text.GetTypedValue(), int)

    def test_IsSilence(self):
        text = Label("#")
        self.assertTrue(text.IsSilence())

        text.UnsetValue()
        self.assertFalse(text.IsSilence())

    def test_IsLabel(self):
        text = Label("#")
        self.assertFalse(text.IsSpeech())
        text = Label("+")
        self.assertFalse(text.IsSpeech())
        text = Label("*")
        self.assertFalse(text.IsSpeech())
        text = Label("@@")
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

# End TestLabel
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLabel)
    unittest.TextTestRunner(verbosity=2).run(suite)

