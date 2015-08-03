#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import sys
from os.path import dirname, abspath

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

import annotationdata.io
from annotationdata.label.label    import Label
from annotationdata.ptime.point    import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation     import Annotation
from annotationdata.io.xra         import XRA

SAMPLES = os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")
XRADEF  = os.path.join(dirname(dirname(dirname(dirname(abspath(__file__))))), "sppas", "etc", "xra")


class TestXRA(unittest.TestCase):
    """
    Represents an XRA file, the native format of SPPAS.
    """
    def test_Read1(self):
        tg1 = XRA()
        tg1.read(os.path.join(XRADEF, "sample-1.1.xra"))

    def test_Read2(self):
        tg2 = XRA()
        tg2.read(os.path.join(XRADEF, "sample-1.2.xra"))

    def test_ReadWrite(self):
        tg1 = XRA()
        tg1.read(os.path.join(XRADEF, "sample-1.2.xra"))
        annotationdata.io.write(os.path.join(SAMPLES, "sample-1.2.xra"), tg1)
        tg2 = XRA()
        tg2.read(os.path.join(SAMPLES, "sample-1.2.xra"))
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
        os.remove( os.path.join(SAMPLES, "sample-1.2.xra") )

# End TestXRA
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestXRA)
    unittest.TextTestRunner(verbosity=2).run(suite)
