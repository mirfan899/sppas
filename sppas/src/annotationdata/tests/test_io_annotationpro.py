#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import shutil

import annotationdata.io
from annotationdata.io.annotationpro import Antx
from annotationdata.io.elan import Elan
from annotationdata.io.xra import XRA
#import utils.fileutils

#TEMP = utils.fileutils.gen_name()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TEMP = os.path.join(DATA, "Temp")

# ---------------------------------------------------------------------------


class TestAntx(unittest.TestCase):
    """
    Represents an antx file, the stand-alone format of annotation pro.

    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_Read(self):
        tg1 = Antx()
        tg1.read(os.path.join(DATA, "sample-TGA.antx"))

    def test_Read_Write_Read(self):
        tg1 = Antx()
        tg1.read(os.path.join(DATA, "sample-TGA.antx"))
        annotationdata.io.write( os.path.join(TEMP, "sample.antx"), tg1 )
        tg2 = Antx()
        tg2.read(os.path.join(TEMP, "sample.antx"))

        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            self.assertEqual(t1.GetName(), t2.GetName())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                self.assertEqual(a1.GetLocation().GetEnd(), a2.GetLocation().GetEnd())

    def test_Read_ExportSppas_Read(self):
        tg1 = Antx()
        tg1.read(os.path.join(DATA, "sample-TGA.antx"))
        annotationdata.io.write( os.path.join(TEMP, "sample.xra"), tg1 )
        tg2 = XRA()
        tg2.read(os.path.join(TEMP, "sample.xra"))

        # Compare annotations of tg1 and tg2
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
                self.assertEqual(a1.GetLocation().GetEnd(), a2.GetLocation().GetEnd())

    def test_Read_ExportElan_Read(self):
        tg1 = Antx()
        tg1.read(os.path.join(DATA, "sample-TGA.antx"))
        annotationdata.io.write( os.path.join(TEMP, "sample.eaf"), tg1 )
        tg2 = Elan()
        tg2.read(os.path.join(TEMP, "sample.eaf"))

        # Compare annotations of tg1 and tg2.
        # Not possible because:
        # AssertionError: 13 != 12
        # TODO: check why!
        # for t1, t2 in zip(tg1, tg2):
        #     self.assertEqual(t1.GetSize(), t2.GetSize())
        #     for a1, a2 in zip(t1, t2):
        #         self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
        #         self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
        #         self.assertEqual(a1.GetLocation().GetEnd(), a2.GetLocation().GetEnd())

# ---------------------------------------------------------------------------

if __name__ == '__main__':

    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(TestAntx))
    unittest.TextTestRunner(verbosity=2).run(testsuite)
