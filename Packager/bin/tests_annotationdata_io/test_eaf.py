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
from annotationdata.io.elan        import Elan
from annotationdata.io.xra         import XRA
from annotationdata.transcription  import Transcription
from annotationdata.label.label    import Label
from annotationdata.label.text     import Text
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint
from annotationdata.ptime.disjoint import TimeDisjoint
from annotationdata.annotation     import Annotation

SAMPLES=os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")
XRADEF = os.path.join(dirname(dirname(dirname(dirname(abspath(__file__))))), "sppas", "etc", "xra")


class TestEAF(unittest.TestCase):
    """
    TestEAF.
    """
    def setUp(self):
        self.test_transcription = Transcription()

    def test_Read_Write_Read(self):
        tg1 = Elan()
        tg2 = Elan()
        tg1.read(os.path.join(SAMPLES,"sample.eaf"))
        tg1.write(os.path.join(SAMPLES,"sample2.eaf"))
        tg2.read(os.path.join(SAMPLES,"sample2.eaf"))

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

        os.remove( os.path.join(SAMPLES, "sample2.eaf") )

    def test_Import_XRA(self):
        tg1 = annotationdata.io.read(os.path.join(XRADEF, "sample-1.2.xra"))
        annotationdata.io.write(os.path.join(SAMPLES,"sample-1.2.eaf"),tg1)
        tg2 = Elan()
        tg2.read(os.path.join(SAMPLES, "sample-1.2.eaf"))
        annotationdata.io.write(os.path.join(SAMPLES,"sample-1.2.xra"),tg2)

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
                    # Elan uses milliseconds.
                    # ELAN radius is 0.02 seconds
                    p = round( a1.GetLocation().GetPoint().GetMidpoint()-0.02, 3)
                    self.assertEqual(p, round(a2.GetLocation().GetBegin().GetMidpoint(),3))

        os.remove( os.path.join(SAMPLES, "sample-1.2.xra") )
        os.remove( os.path.join(SAMPLES, "sample-1.2.eaf") )

# End TestEAF
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEAF)
    unittest.TextTestRunner(verbosity=2).run(suite)


