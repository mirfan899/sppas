#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.label.label import Label

class TestSilence(unittest.TestCase):

    def setUp(self):
        self.text = Label("sil")

    def test_decode(self):
        text = Label("être")
        self.assertTrue(isinstance(text.GetValue(), unicode))

    def test_encode(self):
        text = Label("être")
        self.assertTrue(isinstance(str(text), str))

    def test_IsSilence(self):
        self.assertTrue(self.text.IsSilence())
        self.assertFalse(self.text.IsSilence() is False)

# End TestSilence
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSilence)
    unittest.TextTestRunner(verbosity=2).run(suite)

