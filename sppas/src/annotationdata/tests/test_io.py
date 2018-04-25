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

        # Compare controlled vocabularies
        for t1, t2 in zip(tg1, tg2):
            ctrl1 = t1.GetCtrlVocab()  # a CtrlVocab() instance or None
            ctrl2 = t2.GetCtrlVocab()  # a CtrlVocab() instance or None
            if ctrl1 is None and ctrl2 is None:
                continue
            self.assertEqual(ctrl1.GetSize(), ctrl2.GetSize())
            for entry in ctrl1:
                self.assertTrue(ctrl2.Contains(entry.Text))

        # Compare media
        for t1, t2 in zip(tg1, tg2):
            m1 = t1.GetMedia()
            m2 = t2.GetMedia()
            if m1 is None and m2 is None:
                continue
            self.assertEqual(m1.id, m2.id)
            self.assertEqual(m1.url, m2.url)
            self.assertEqual(m1.mime, m2.mime)

        # Compare hierarchy

    # -----------------------------------------------------------------------

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
