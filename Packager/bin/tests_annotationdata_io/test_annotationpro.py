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
from annotationdata.io.annotationpro import Antx
from annotationdata.io.elan import Elan
from annotationdata.io.xra import XRA

SAMPLES = os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")


class TestAntx(unittest.TestCase):
    """
    Represents an antx file, the stand-alone format of annotation pro.
    """

    def test_Read(self):
        tg1 = Antx()
        tg1.read(os.path.join(SAMPLES, "Example_with_TGA.antx"))

    def test_Read_Write_Read(self):
        tg1 = Antx()
        tg1.read(os.path.join(SAMPLES, "Example_with_TGA.antx"))
        annotationdata.io.write( os.path.join(SAMPLES, "Example.antx"), tg1 )
        tg2 = Antx()
        tg2.read(os.path.join(SAMPLES, "Example.antx"))

        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                self.assertEqual(a1.GetLocation().GetEnd(), a2.GetLocation().GetEnd())

        #os.remove( os.path.join(SAMPLES, "Example.antx") )

    def test_Read_ExportSppas_Read(self):
        tg1 = Antx()
        tg1.read(os.path.join(SAMPLES, "Example_with_TGA.antx"))
        annotationdata.io.write( os.path.join(SAMPLES, "Example.xra"), tg1 )
        tg2 = XRA()
        tg2.read(os.path.join(SAMPLES, "Example.xra"))

        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                self.assertEqual(a1.GetLocation().GetEnd(), a2.GetLocation().GetEnd())

        os.remove( os.path.join(SAMPLES, "Example.xra") )

    def test_Read_ExportElan_Read(self):
        tg1 = Antx()
        tg1.read(os.path.join(SAMPLES, "Example_with_TGA.antx"))
        annotationdata.io.write( os.path.join(SAMPLES, "Example.eaf"), tg1 )
        tg2 = Elan()
        tg2.read(os.path.join(SAMPLES, "Example.eaf"))

        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(),    a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                self.assertEqual(a1.GetLocation().GetEnd(),   a2.GetLocation().GetEnd())

        #os.remove( os.path.join(SAMPLES, "Example.eaf") )

# End TestAntx
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAntx)
    unittest.TextTestRunner(verbosity=2).run(suite)
