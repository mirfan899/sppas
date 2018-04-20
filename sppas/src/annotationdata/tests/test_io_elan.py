#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os.path
import shutil

from ..aio import read as trsread
from ..aio import write as trswrite
from ..aio.elan import Elan
from ..transcription import Transcription
from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestEAF(unittest.TestCase):
    """
    TestEAF. Test the native format of Elan annotation software.

    """
    def setUp(self):
        self.test_transcription = Transcription()
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_Read_Write_Read(self):
        tg1 = Elan()
        tg2 = Elan()
        tg1.read(os.path.join(DATA, "sample.eaf"))
        tg1.write(os.path.join(TEMP, "sample.eaf"))
        tg2.read(os.path.join(TEMP, "sample.eaf"))

        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            self.assertEqual(t1.GetName(), t2.GetName())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(),    a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                self.assertEqual(a1.GetLocation().GetEnd(),   a2.GetLocation().GetEnd())
        # Compare media

        # Compare controlled vocabularies
        for t1, t2 in zip(tg1, tg2):
            ctrl1 = t1.GetCtrlVocab() # a CtrlVocab() instance or None
            ctrl2 = t2.GetCtrlVocab() # a CtrlVocab() instance or None
            if ctrl1 is None and ctrl2 is None:
                continue
            self.assertEqual(ctrl1.GetSize(), ctrl2.GetSize())
            for entry in ctrl1:
                self.assertTrue(ctrl2.Contains(entry.Text))
