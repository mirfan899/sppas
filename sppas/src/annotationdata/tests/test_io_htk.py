#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os.path
import shutil

from ..aio import read as trsread
from ..aio import write as trswrite
from ..transcription import Transcription
from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestHTK(unittest.TestCase):

    def setUp(self):
        self.test_transcription = Transcription()
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_Import_XRA(self):
        tg1 = trsread(os.path.join(DATA, "sample-1.2.xra"))
        trswrite(os.path.join(TEMP, "sample-1.2.mlf"), tg1)
        tg2 = trsread(os.path.join(TEMP, "sample-1.2.mlf"))

        self.assertEqual(tg2.GetSize(), 1)  # only lab files... so 1 tier

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
