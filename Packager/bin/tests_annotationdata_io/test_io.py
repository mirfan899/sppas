#!/usr/bin/env python2
# -*- coding: utf8 -*-


import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

import annotationdata.io

SAMPLES=os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")

class TestIO(unittest.TestCase):


    def test_IOTextGrid(self):
        tg1 = annotationdata.io.read(os.path.join(SAMPLES,"sample.TextGrid"))
        annotationdata.io.write(os.path.join(SAMPLES,"sample2.TextGrid"), tg1)
        tg2 = annotationdata.io.read(os.path.join(SAMPLES,"sample.TextGrid"))

        self.assertEqual(tg1.GetName(), tg2.GetName())
        self.assertEqual(tg1.GetSize(), tg2.GetSize())
        for tier1, tier2 in zip(tg1, tg2):
            self.assertEqual(tier1.GetName(), tier2.GetName())
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            for a1, a2 in zip(tier1, tier2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())
        os.remove(os.path.join(SAMPLES,"sample2.TextGrid"))

    def test_IOAscii(self):
        tg1 = annotationdata.io.read(os.path.join(SAMPLES,"sample.TextGrid"))
        # save as txt.
        annotationdata.io.write(os.path.join(SAMPLES,"sampleascii.csv"), tg1)
        # load from txt.
        tg2 = annotationdata.io.read(os.path.join(SAMPLES,"sampleascii.csv"))

        self.assertEqual(tg1.GetName(), tg2.GetName())
        self.assertEqual(tg1.GetSize(), tg2.GetSize())
        for tier1, tier2 in zip(tg1, tg2):
            self.assertEqual(tier1.GetName(), tier2.GetName())
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            for a1, a2 in zip(tier1, tier2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())
        os.remove(os.path.join(SAMPLES,"sampleascii.csv"))


    def test_IOPitch(self):
        tg1 = annotationdata.io.read(os.path.join(SAMPLES,"sample.PitchTier"))
        annotationdata.io.write(os.path.join(SAMPLES,"sample2.PitchTier"), tg1)
        tg2 = annotationdata.io.read(os.path.join(SAMPLES,"sample2.PitchTier"))
        tg2.SetName( 'Pitch' )

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

        os.remove(os.path.join(SAMPLES,"sample2.PitchTier"))

    def test_Interval(self):
        tg = annotationdata.io.read(os.path.join(SAMPLES,"sample3.TextGrid"))

        self.assertEqual(tg.GetMinTime(), 0.0)
        self.assertEqual(tg.GetMaxTime(), 3.0)

        tier = tg[0]
        tier.Pop(0)
        tier.Pop()

        annotationdata.io.write(os.path.join(SAMPLES,"sample3-1.TextGrid"), tg)

        tg2 = annotationdata.io.read(os.path.join(SAMPLES,"sample3-1.TextGrid"))

        tier = tg2[0]
        self.assertTrue(tier.GetSize() == 3)
        a1 = tier[0]
        self.assertTrue(a1.GetLabel().GetValue() == "")
        a2 = tier[1]
        self.assertTrue(a2.GetLabel().GetValue() == "text2")
        a3 = tier[2]
        self.assertTrue(a3.GetLabel().GetValue() == "")

        tier = tg2[1]
        self.assertEqual(tier.GetSize(), 5)
        a1 = tier[0]
        self.assertTrue(a1.GetLabel().GetValue() == "")
        a2 = tier[1]
        self.assertTrue(a2.GetLabel().GetValue() == "text1")
        a3 = tier[2]
        self.assertTrue(a3.GetLabel().GetValue() == "text2")
        a4 = tier[3]
        self.assertTrue(a4.GetLabel().GetValue() == "text3")
        #a5 = tier[4]
        #self.assertTrue(a5.GetLabel().GetValue() == "")

        os.remove(os.path.join(SAMPLES,"sample3-1.TextGrid"))


    # def test_IOTrs(self):
    #     # load from trs.
    #     tg1 = annotationdata.io.read("samples/sampleBAv5AlphaG1.trs")
    #     # save as txt.
    #     annotationdata.io.write("samples/sampleascii.txt", tg1)
    #     # laad from txt.
    #     tg2 = annotationdata.io.read("samples/sampleascii.txt")

    #     self.assertEqual(tg1.GetName(), tg2.GetName())
    #     self.assertEqual(tg1.GetSize(), tg2.GetSize())
    #     for tier1, tier2 in zip(tg1, tg2):
    #         self.assertEqual(tier1.GetName(), tier2.GetName())
    #         self.assertEqual(tier1.GetSize(), tier2.GetSize())
    #         for a1, a2 in zip(tier1, tier2):
    #             self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
    #             self.assertEqual(a1.Time, a2.Time)


    # def test_Trs2TextGrid(self):
    #     # load from trs.
    #     tg1 = annotationdata.io.read("samples/sampleBAv5BetaF1.trs")
    #     # save trs as textgrid
    #     annotationdata.io.write("samples/sampleBAv5BetaF1.TextGrid", tg1)
    #     # load from textgrid
    #     tg2 = annotationdata.io.read("samples/sampleBAv5AlphaG1.TextGrid")
    #     # save textgrid as csv
    #     annotationdata.io.write("samples/sampleBAv5BetaF1.csv", tg1)
    #     # load from csv.
    #     tg2 = annotationdata.io.read("samples/sampleBAv5BetaF1.csv")

    #     self.assertEqual(tg1.GetName(), tg2.GetName())
    #     self.assertEqual(tg1.GetSize(), tg2.GetSize())
    #     for tier1, tier2 in zip(tg1, tg2):
    #         self.assertEqual(tier1.GetName(), tier2.GetName())
    #         self.assertEqual(tier1.GetSize(), tier2.GetSize())
    #         for a1, a2 in zip(tier1, tier2):
    #             self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
    #             self.assertEqual(a1.Time, a2.Time)


    # def test_Eaf(self):
    #     # load from eaf.
    #     tg1 = annotationdata.io.read("samples/sample.eaf")
    #     # save as txt.
    #     annotationdata.io.write("samples/sampleeaf.txt", tg1)
    #     # load from txt.
    #     tg2 = annotationdata.io.read("samples/sampleeaf.txt")

    #     tiers = [tier for tier in tg1 if not tier.IsEmpty()]
    #     tg1.Set(tiers, tg1.GetName())

    #     self.assertEqual(tg1.GetName(), tg2.GetName())
    #     self.assertEqual(tg1.GetSize(), tg2.GetSize())
    #     for tier1, tier2 in zip(tg1, tg2):
    #         self.assertEqual(tier1.GetName(), tier2.GetName())
    #         self.assertEqual(tier1.GetSize(), tier2.GetSize())
    #         for a1, a2 in zip(tier1, tier2):
    #             self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
    #             self.assertEqual(a1.Time, a2.Time)


# End TestIO
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIO)
    unittest.TextTestRunner(verbosity=2).run(suite)

