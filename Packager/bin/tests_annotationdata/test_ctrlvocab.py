#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))


from annotationdata.ctrlvocab import CtrlVocab
from annotationdata.tier import Tier
from annotationdata.label.label import Label
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation

class TestCtrlVocab(unittest.TestCase):

    def setUp(self):
        pass
    

    def test_Identifier(self):
        voc = CtrlVocab(u"être être")
        self.assertEquals(voc.GetIdentifier(), u"être être")

    def test_Description(self):
        voc = CtrlVocab("être être")
        voc.SetDescription("description être")
        self.assertIsInstance(voc.GetDescription(), unicode)

    def test_Append(self):
        voc = CtrlVocab("Verbal Strategies")
        self.assertTrue(voc.Append("definition"))
        self.assertTrue(voc.Append("example"))
        self.assertTrue(voc.Append("comparison"))
        self.assertTrue(voc.Append("gap filling with sound"))
        self.assertFalse(voc.Append(" gap filling with sound "))
        self.assertTrue(voc.Append("contrast"))
        self.assertFalse(voc.Append("definition"))
        self.assertTrue(voc.In("   \t  definition\r\n"))

    def test_Add(self):
        voc = CtrlVocab("Verbal Strategies")
        self.assertTrue(voc.Add(3,"definition"))
        self.assertFalse(voc.Add(-1, "example"))
        self.assertFalse(voc.Add(1, "definition"))

    def test_Remove(self):
        voc = CtrlVocab("Verbal Strategies")
        self.assertTrue(voc.Append("definition"))
        self.assertTrue(voc.Append("example"))
        self.assertTrue(voc.Remove("example"))
        self.assertFalse(voc.Remove("example"))

    def test_Pop(self):
        voc = CtrlVocab("Verbal Strategies")
        self.assertTrue(voc.Append("definition"))
        self.assertTrue(voc.Pop())
        self.assertFalse(voc.Pop())
        self.assertTrue(voc.Append("definition"))
        self.assertTrue(voc.Append("gap filling with sound"))
        self.assertTrue(voc.Pop(0))

    def test_GetSize(self):
        voc = CtrlVocab("Verbal Strategies")
        self.assertEquals(voc.GetSize(), 0)
        self.assertTrue(voc.Append("definition"))
        self.assertEquals(voc.GetSize(), len(voc))

# End TestTier
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCtrlVocab)
    unittest.TextTestRunner(verbosity=2).run(suite)

# ---------------------------------------------------------------------------
