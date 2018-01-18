# -*- coding:utf-8 -*-

import unittest

from sppas.src.utils.makeunicode import u
from ..anndataexc import AnnDataTypeError
from ..ctrlvocab import sppasCtrlVocab
from ..annlabel.tag import sppasTag

# ---------------------------------------------------------------------------


class TestCtrlVocab(unittest.TestCase):

    def setUp(self):
        pass

    def test_identifier(self):
        voc = sppasCtrlVocab("être être")
        self.assertEqual(voc.get_name(), u("être_être"))

    def test_add(self):
        voc = sppasCtrlVocab("Verbal Strategies")
        self.assertEqual(len(voc), 0)
        self.assertTrue(voc.add(sppasTag("definition")))
        self.assertTrue(voc.add(sppasTag("example")))
        self.assertTrue(voc.add(sppasTag("comparison")))
        self.assertTrue(voc.add(sppasTag("gap filling with sound")))
        self.assertFalse(voc.add(sppasTag("definition")))
        self.assertEqual(len(voc), 4)
        with self.assertRaises(AnnDataTypeError):
            voc.add("bla")

        voc_int = sppasCtrlVocab("Intensity")
        self.assertTrue(voc_int.add(sppasTag(1, "int")))
        self.assertTrue(voc_int.add(sppasTag(2, "int")))
        self.assertFalse(voc_int.add(sppasTag(1, "int")))
        self.assertTrue(voc_int.add(sppasTag(1)))  # 1 is converted into str by sppasTag.
        with self.assertRaises(AnnDataTypeError):
            voc_int.add(2)

    def test_contains(self):
        voc = sppasCtrlVocab("Verbal Strategies")
        self.assertTrue(voc.add(sppasTag("definition")))
        self.assertTrue(voc.add(sppasTag("example")))
        self.assertTrue(voc.add(sppasTag("comparison")))
        self.assertTrue(voc.add(sppasTag("gap filling with sound")))
        self.assertFalse(voc.add(sppasTag(" gap filling with sound ")))
        self.assertTrue(voc.add(sppasTag("contrast")))
        self.assertFalse(voc.add(sppasTag("definition")))
        self.assertTrue(voc.contains(sppasTag("definition")))
        self.assertTrue(voc.contains(sppasTag("   \t  definition\r\n")))
        with self.assertRaises(AnnDataTypeError):
            voc.contains("definition")

        voc_int = sppasCtrlVocab("Intensity")
        self.assertTrue(voc_int.add(sppasTag(1, "int")))
        self.assertTrue(voc_int.add(sppasTag(2, "int")))
        self.assertTrue(voc_int.contains(sppasTag(2, "int")))
        self.assertFalse(voc_int.contains(sppasTag(2, "str")))
        self.assertFalse(voc_int.contains(sppasTag(2)))

    def test_remove(self):
        voc = sppasCtrlVocab("Verbal Strategies")
        self.assertTrue(voc.add(sppasTag("definition")))
        self.assertTrue(voc.add(sppasTag("example")))
        self.assertTrue(voc.remove(sppasTag("example")))
        self.assertFalse(voc.remove(sppasTag("example")))
        with self.assertRaises(AnnDataTypeError):
            voc.remove("definition")
