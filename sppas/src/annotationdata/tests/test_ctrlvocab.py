# -*- coding:utf-8 -*-

import unittest

from ..ctrlvocab import CtrlVocab
from ..tier import Tier
from ..label.label import Label
from ..label.text import Text
from ..ptime.point import TimePoint
from ..ptime.interval import TimeInterval
from ..annotation import Annotation

# ---------------------------------------------------------------------------


class TestCtrlVocab(unittest.TestCase):

    def setUp(self):
        pass

    def test_Identifier(self):
        voc = CtrlVocab(u"être être")
        self.assertEquals(voc.id, u"être être")

    def test_Contains(self):
        tiercv = Tier("CtrlVocabTier")

        a1 = Annotation(TimeInterval(TimePoint(1), TimePoint(3)), Label("definition"))
        a2 = Annotation(TimeInterval(TimePoint(6), TimePoint(7)), Label("example"))
        a3 = Annotation(TimeInterval(TimePoint(7), TimePoint(9)), Label("biz"))

        voc = CtrlVocab("Verbal Strategies")
        self.assertTrue(voc.Append("definition"))
        self.assertTrue(voc.Append("example"))
        self.assertTrue(voc.Append("comparison"))
        self.assertTrue(voc.Append("gap filling with sound"))

        tiercv.SetCtrlVocab(voc)
        tiercv.Append(a1)
        tiercv.Append(a2)
        with self.assertRaises(ValueError):
            tiercv.Append(a3)

        self.assertTrue(tiercv.GetCtrlVocab().Contains("   \t  definition\r\n"))
        self.assertTrue(tiercv.GetCtrlVocab().Contains(a1.GetLabel().GetValue()))
        self.assertTrue(tiercv.GetCtrlVocab().Contains(Text("   \t  definition\r\n")))

    def test_Append(self):
        voc = CtrlVocab("Verbal Strategies")
        self.assertTrue(voc.Append("definition"))
        self.assertTrue(voc.Append("example"))
        self.assertTrue(voc.Append("comparison"))
        self.assertTrue(voc.Append("gap filling with sound"))
        self.assertFalse(voc.Append(" gap filling with sound "))
        self.assertTrue(voc.Append("contrast"))
        self.assertFalse(voc.Append("definition"))
        self.assertTrue(voc.Contains("   \t  definition\r\n"))

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
