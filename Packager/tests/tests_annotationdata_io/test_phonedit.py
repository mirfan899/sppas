#!/usr/bin/env python2
# -*- coding: utf8 -*-


import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

import annotationdata.io
from annotationdata.io.xra import XRA

SAMPLES=os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")
XRADEF = os.path.join(dirname(dirname(dirname(dirname(abspath(__file__))))), "sppas", "etc", "xra")

class TestPhonedit(unittest.TestCase):

    def test_io(self):
        path = os.path.join(SAMPLES,"sample3.TextGrid")
        trs = annotationdata.io.read(path)
        annotationdata.io.write(os.path.join(SAMPLES,"sample3.mrk"), trs)
        trs2 = annotationdata.io.read(os.path.join(SAMPLES,"sample3.mrk"))

        self.compare(trs, trs2)
        os.remove(os.path.join(SAMPLES,"sample3.mrk"))

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
        tg1 = annotationdata.io.read(os.path.join(XRADEF, "sample-1.2.xra"))
        annotationdata.io.write(os.path.join(SAMPLES,"sample-1.2.mrk"),tg1)
        tg2 = annotationdata.io.read(os.path.join(SAMPLES, "sample-1.2.mrk"))

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

        os.remove(os.path.join(SAMPLES,"sample-1.2.mrk"))

# End TestPhonedit
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhonedit)
    unittest.TextTestRunner(verbosity=2).run(suite)

