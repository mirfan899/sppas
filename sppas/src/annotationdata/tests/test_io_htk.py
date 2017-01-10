#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os.path
import shutil

import annotationdata.io
from annotationdata.transcription  import Transcription
#import utils.fileutils

#TEMP = utils.fileutils.gen_name()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TEMP = os.path.join(DATA, "Temp")

# ---------------------------------------------------------------------------


class TestHTK(unittest.TestCase):

    def setUp(self):
        self.test_transcription = Transcription()
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_Import_XRA(self):
        tg1 = annotationdata.io.read(os.path.join(DATA, "sample-1.2.xra"))
        annotationdata.io.write(os.path.join(TEMP, "sample-1.2.mlf"), tg1)
        tg2 = annotationdata.io.read(os.path.join(TEMP, "sample-1.2.mlf"))

        self.assertEqual(tg1.GetSize()-1, tg2.GetSize())

        # We can't do that...
        # While writing a mlf file, we loose the location-information....
        # We can only manage time-aligned data

        # Compare annotations of tg1 and tg2
#         for t1, t2 in zip(tg1, tg2):
#
#             self.assertEqual(t1.GetName(), t2.GetName())
#             for a1, a2 in zip(t1, t2):
#                 self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
#                 self.assertEqual(a1.GetLocation().GetBegin(), a2.GetLocation().GetBegin())
#                 self.assertEqual(a1.GetLocation().GetEnd(),   a2.GetLocation().GetEnd())


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHTK)
    unittest.TextTestRunner(verbosity=2).run(suite)
