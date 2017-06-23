#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os.path
import shutil

from ..aio import read as trsread
from ..aio import write as trswrite
from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestPhonedit(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_io(self):
        path = os.path.join(DATA, "sample-irish.tdf")
        trs = trsread(path)
        trswrite(os.path.join(TEMP, "sample.mrk"), trs)
        trs2 = trsread(os.path.join(TEMP, "sample.mrk"))
        self.compare(trs, trs2)

    def compare(self, trs1, trs2):
        self.assertEqual(trs1.GetSize(), trs2.GetSize())
        for tier1, tier2 in zip(trs1, trs2):
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            self.assertEqual(tier1.GetName(), tier2.GetName())
            tier1.SetRadius(0.00001)
            tier2.SetRadius(0.00001)
            for an1, an2 in zip(tier1, tier2):
                self.assertEqual(an1.GetLocation().GetValue(), an2.GetLocation().GetValue())
                texts1 = an1.GetLabel().Get()
                texts2 = an2.GetLabel().Get()
                for text1, text2 in zip(texts1, texts2):
                    self.assertEqual(text1.Score, text2.Score)
                    self.assertEqual(text1.Value, text2.Value)

    def test_Import_XRA(self):
        tg1 = trsread(os.path.join(DATA, "sample-1.2.xra"))
        trswrite(os.path.join(TEMP, "sample-1.2.mrk"), tg1)
        tg2 = trsread(os.path.join(TEMP, "sample-1.2.mrk"))

        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            self.assertEqual(t1.GetName(), t2.GetName())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                if t1.IsInterval():
                    self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                    self.assertEqual(a1.GetLocation().GetEnd(),   a2.GetLocation().GetEnd())
                else:
                    p1 = round(a1.GetLocation().GetPoint().GetMidpoint(),4)
                    p2 = round(a2.GetLocation().GetPoint().GetMidpoint(),4)
                    self.assertEqual(p1,p2)
