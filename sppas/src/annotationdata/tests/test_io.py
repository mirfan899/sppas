# -*- coding: utf8 -*-

import unittest
import os.path
import shutil

from ..aio import read as read_trs
from ..aio import write as write_trs

from ..transcription import Transcription
from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestIO(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        return
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_IO_XRA(self):
        tg1 = read_trs(os.path.join(DATA, "sample-1.2.xra"))
        write_trs(os.path.join(TEMP, "sample-1.4.xra"), tg1)
        tg2 = read_trs(os.path.join(TEMP, "sample-1.4.xra"))
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

    def test_IO_TextGrid_intervals_long(self):
        tg1 = read_trs(os.path.join(DATA, "sample.TextGrid"))
        write_trs(os.path.join(TEMP, "sample.TextGrid"), tg1)
        tg2 = read_trs(os.path.join(TEMP, "sample.TextGrid"))

        self.assertEqual(tg1.GetName(), tg2.GetName())
        self.assertEqual(tg1.GetSize(), tg2.GetSize())
        for tier1, tier2 in zip(tg1, tg2):
            self.assertEqual(tier1.GetName(), tier2.GetName())
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            for a1, a2 in zip(tier1, tier2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_IO_TextGrid_points_long(self):
        tg1 = read_trs(os.path.join(DATA, "sample_points.TextGrid"))
        write_trs(os.path.join(TEMP, "sample_points.TextGrid"), tg1)
        tg2 = read_trs(os.path.join(TEMP, "sample_points.TextGrid"))
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(),
                                 a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(),
                                 a2.GetLocation().GetValue())

    def test_IO_Xtrans(self):
        tg1 = read_trs(os.path.join(DATA, "sample-irish.tdf"))
        write_trs(os.path.join(TEMP, "sample-irish.xra"), tg1)
        tg2 = read_trs(os.path.join(TEMP, "sample-irish.xra"))

        self.assertEqual(tg1.GetName(), tg2.GetName())
        self.assertEqual(tg1.GetSize(), tg2.GetSize())
        for tier1, tier2 in zip(tg1, tg2):
            self.assertEqual(tier1.GetName(), tier2.GetName())
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            for a1, a2 in zip(tier1, tier2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_IO_Ascii(self):
        tg1 = read_trs(os.path.join(DATA, "sample.TextGrid"))
        write_trs(os.path.join(TEMP, "sample.csv"), tg1)
        tg2 = read_trs(os.path.join(TEMP, "sample.csv"))

        self.assertEqual(tg1.GetName(), tg2.GetName())
        self.assertEqual(tg1.GetSize(), tg2.GetSize())
        for tier1, tier2 in zip(tg1, tg2):
            self.assertEqual(tier1.GetName(), tier2.GetName())
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            for a1, a2 in zip(tier1, tier2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_IO_Pitch(self):
        tg1 = read_trs(os.path.join(DATA, "sample.PitchTier"))
        write_trs(os.path.join(TEMP, "sample.PitchTier"), tg1)
        tg2 = read_trs(os.path.join(TEMP, "sample.PitchTier"))
        tg2.SetName('Pitch')

        self.assertEqual(tg1.GetName(), tg2.GetName())
        self.assertEqual(tg1.GetSize(), tg2.GetSize())
        for tier1, tier2 in zip(tg1, tg2):
            self.assertEqual(tier1.GetName(), tier2.GetName())
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            tier1.SetRadius(0.0001)
            tier2.SetRadius(0.0001)
            for a1, a2 in zip(tier1, tier2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_IO_Antx(self):
        tg1 = read_trs(os.path.join(DATA, "sample-TGA.antx"))
        write_trs(os.path.join(TEMP, "sample.antx"), tg1)
        tg2 = read_trs(os.path.join(TEMP, "sample.antx"))

        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            self.assertEqual(t1.GetName(), t2.GetName())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                self.assertEqual(a1.GetLocation().GetEnd(), a2.GetLocation().GetEnd())

    def test_I_Phonedit(self):
        tg1 = read_trs(os.path.join(DATA, "sample-1.2.xra"))
        write_trs(os.path.join(TEMP, "sample-1.2.mrk"), tg1)
        tg2 = read_trs(os.path.join(TEMP, "sample-1.2.mrk"))

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
                    p1 = a1.GetLocation().GetPoint()
                    p2 = a2.GetLocation().GetPoint()
                    self.assertEqual(p1, p2)

    def test_IO_Elan(self):
        tg1 = read_trs(os.path.join(DATA, "sample.eaf"))
        write_trs(os.path.join(TEMP, "sample.eaf"), tg1)
        tg2 = read_trs(os.path.join(TEMP, "sample.eaf"))

        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            self.assertEqual(t1.GetName(), t2.GetName())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(),    a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                self.assertEqual(a1.GetLocation().GetEnd(),   a2.GetLocation().GetEnd())

        # Compare controlled vocabularies
        for t1, t2 in zip(tg1, tg2):
            ctrl1 = t1.GetCtrlVocab()  # a CtrlVocab() instance or None
            ctrl2 = t2.GetCtrlVocab()  # a CtrlVocab() instance or None
            if ctrl1 is None and ctrl2 is None:
                continue
            self.assertEqual(ctrl1.GetSize(), ctrl2.GetSize())
            for entry in ctrl1:
                self.assertTrue(ctrl2.Contains(entry.Text))
