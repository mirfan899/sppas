#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os.path
import shutil

from ..aio import write as trswrite
from ..aio.xra import XRA
from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestXRA(unittest.TestCase):
    """
    Represents an XRA file, the native format of SPPAS.
    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_Read1(self):
        tg1 = XRA()
        tg1.read(os.path.join(DATA, "sample-1.1.xra"))

    def test_Read2(self):
        tg2 = XRA()
        tg2.read(os.path.join(DATA, "sample-1.2.xra"))

    def test_ReadWrite(self):
        tg1 = XRA()
        tg1.read(os.path.join(DATA, "sample-1.2.xra"))
        trswrite(os.path.join(TEMP, "sample-1.2.xra"), tg1)
        tg2 = XRA()
        tg2.read(os.path.join(TEMP, "sample-1.2.xra"))
        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                if a1.GetLocation().IsPoint():
                    self.assertEqual(a1.GetLocation().GetPoint(), a2.GetLocation().GetPoint())
                else:
                    self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                    self.assertEqual(a1.GetLocation().GetEnd(), a2.GetLocation().GetEnd())
        # Compare media
        # Compare hierarchy
        # Compare controlled vocabularies
        for t1, t2 in zip(tg1, tg2):
            ctrl1 = t1.GetCtrlVocab()  # a CtrlVocab() instance or None
            ctrl2 = t2.GetCtrlVocab()  # a CtrlVocab() instance or None
            if ctrl1 is None and ctrl2 is None:
                continue
            self.assertEqual(ctrl1.GetSize(), ctrl2.GetSize())
            for entry in ctrl1:
                self.assertTrue(ctrl2.Contains(entry.Text))
