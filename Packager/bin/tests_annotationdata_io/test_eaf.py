#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import sys
from os.path import dirname, abspath
#import xml.sax

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

import annotationdata.io
from annotationdata.io.elan import Elan
from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.label.text import Text
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.disjoint import TimeDisjoint
from annotationdata.annotation import Annotation

SAMPLES=os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")


class TestEAF(unittest.TestCase):
    """
    TestEAF.
    """
    def setUp(self):
        self.test_transcription = Transcription()

    def test_ReadWrite_simple(self):
        tg1 = Elan()
        tg2 = Elan()
        tg1.read(os.path.join(SAMPLES,"sample.eaf"))
        tg1.write(os.path.join(SAMPLES,"sample2.eaf"))
        tg2.read(os.path.join(SAMPLES,"sample2.eaf"))

        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(),    a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                self.assertEqual(a1.GetLocation().GetEnd(),   a2.GetLocation().GetEnd())
        # to do: compare controlled vocab

    # def test_ReadWrite(self):
        # tg1 = Elan()
        # tg2 = Elan()
        # tg1.read(os.path.join(SAMPLES,"poio-elan-example3.eaf"))
        # tg1.write(os.path.join(SAMPLES,"sample2.eaf"))
        # tg2.read(os.path.join(SAMPLES,"sample2.eaf"))
        # for t1, t2 in zip(tg1, tg2):
            # self.assertEqual(t1.GetSize(), t2.GetSize())
            # for a1, a2 in zip(t1, t2):
                # self.assertEqual(a1.TextValue, a2.TextValue)
                # self.assertEqual(a1.Time, a2.Time)



# End TestEAF
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEAF)
    unittest.TextTestRunner(verbosity=2).run(suite)


