# -*- coding:utf-8 -*-

import unittest
import os.path
import shutil

from ..aio.text import sppasRawText
from ..aio.text import sppasCSV

from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestRawText(unittest.TestCase):
    # def setUp(self):
    #     if os.path.exists(TEMP) is False:
    #         os.mkdir(TEMP)
    #
    # def tearDown(self):
    #     shutil.rmtree(TEMP)

    def test_read1(self):
        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample-irish-1.txt"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 6)

    def test_read2(self):
        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample-irish-2.txt"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 5)

    def test_read3(self):
        txt = sppasCSV()
        txt.read(os.path.join(DATA, "sample-irish.csv"))
        self.assertEqual(len(txt), 2)
        self.assertEqual(len(txt[0]), 5)
        self.assertEqual(len(txt[1]), 5)
