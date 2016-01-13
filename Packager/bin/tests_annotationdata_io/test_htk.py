#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import sys
from os.path import dirname, abspath

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

import annotationdata.io
from annotationdata.io.htk         import HTKLabel, MasterLabel
from annotationdata.io.xra         import XRA
from annotationdata.transcription  import Transcription


SAMPLES=os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")
XRADEF = os.path.join(dirname(dirname(dirname(dirname(abspath(__file__))))), "sppas", "etc", "xra")


class TestHTK(unittest.TestCase):
    """
    TestHTK.
    """
    def setUp(self):
        self.test_transcription = Transcription()

    def test_Import_XRA(self):
        tg1 = annotationdata.io.read(os.path.join(XRADEF, "sample-1.2.xra"))
        annotationdata.io.write(os.path.join(SAMPLES,"sample-1.2.mlf"),tg1)
        tg2 = annotationdata.io.read(os.path.join(SAMPLES, "sample-1.2.mlf"))

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
                    p1 = a1.GetLocation().GetPoint().GetMidpoint()
                    p2 = a2.GetLocation().GetPoint().GetMidpoint()
                    self.assertEqual(p1,p2)

        os.remove(os.path.join(SAMPLES,"sample-1.2.mlf"))

# End TestHTK
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHTK)
    unittest.TextTestRunner(verbosity=2).run(suite)
