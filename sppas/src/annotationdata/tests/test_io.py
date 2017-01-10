#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import shutil

import annotationdata.aio
#import utils.fileutils

#TEMP = utils.fileutils.gen_name()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TEMP = os.path.join(DATA, "Temp")

# ---------------------------------------------------------------------------


class TestIO(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_IOTextGrid(self):
        tg1 = annotationdata.aio.read(os.path.join(DATA, "sample.TextGrid"))
        annotationdata.aio.write(os.path.join(TEMP, "sample.TextGrid"), tg1)
        tg2 = annotationdata.aio.read(os.path.join(TEMP, "sample.TextGrid"))

        self.assertEqual(tg1.GetName(), tg2.GetName())
        self.assertEqual(tg1.GetSize(), tg2.GetSize())
        for tier1, tier2 in zip(tg1, tg2):
            self.assertEqual(tier1.GetName(), tier2.GetName())
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            for a1, a2 in zip(tier1, tier2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_IOXtrans(self):
        tg1 = annotationdata.aio.read(os.path.join(DATA, "sample-irish.tdf"))
        annotationdata.aio.write(os.path.join(TEMP, "sample-irish.xra"), tg1)
        tg2 = annotationdata.aio.read(os.path.join(TEMP, "sample-irish.xra"))

        self.assertEqual(tg1.GetName(), tg2.GetName())
        self.assertEqual(tg1.GetSize(), tg2.GetSize())
        for tier1, tier2 in zip(tg1, tg2):
            self.assertEqual(tier1.GetName(), tier2.GetName())
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            for a1, a2 in zip(tier1, tier2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_IOAscii(self):
        tg1 = annotationdata.aio.read(os.path.join(DATA, "sample.TextGrid"))
        # save as txt.
        annotationdata.aio.write(os.path.join(TEMP, "sample.csv"), tg1)
        # load from txt.
        tg2 = annotationdata.aio.read(os.path.join(TEMP, "sample.csv"))

        self.assertEqual(tg1.GetName(), tg2.GetName())
        self.assertEqual(tg1.GetSize(), tg2.GetSize())
        for tier1, tier2 in zip(tg1, tg2):
            self.assertEqual(tier1.GetName(), tier2.GetName())
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            for a1, a2 in zip(tier1, tier2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_IOPitch(self):
        tg1 = annotationdata.aio.read(os.path.join(DATA, "sample.PitchTier"))
        annotationdata.aio.write(os.path.join(TEMP, "sample.PitchTier"), tg1)
        tg2 = annotationdata.aio.read(os.path.join(TEMP, "sample.PitchTier"))
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

    # TODO: test heuristic

# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIO)
    unittest.TextTestRunner(verbosity=2).run(suite)

