# -*- coding:utf-8 -*-

import unittest
import os.path
import shutil

from sppas.src.utils.fileutils import sppasFileUtils
from sppas.src.utils.makeunicode import u

from ..anndataexc import AioEncodingError
from ..aio.readwrite import sppasRW
from ..aio.praat import sppasTextGrid

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestAIO(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_read_write(self):
        parser = sppasRW(os.path.join(DATA, "sample-1.1.xra"))
        trs_r = parser.read(heuristic=False)
        parser.set_filename(os.path.join(TEMP, "sampléà-1.3.xra"))
        parser.write(trs_r)
        self.assertTrue(os.path.exists(os.path.join(TEMP, u("sampléà-1.3.xra"))))
        trs_w = parser.read(heuristic=False)
        # Compare annotations of reader and writer
        for t1, t2 in zip(trs_r, trs_w):
            self.assertEqual(len(t1), len(t2))
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.get_label().get_best().get_typed_content(), a2.get_label().get_best().get_typed_content())
                self.assertEqual(a1.get_highest_localization().get_midpoint(), a2.get_highest_localization().get_midpoint())
                self.assertEqual(a1.get_lowest_localization().get_midpoint(), a2.get_lowest_localization().get_midpoint())
        # Compare media
        # Compare hierarchy
        # Compare controlled vocabularies
        for t1, t2 in zip(trs_r, trs_w):
            ctrl1 = t1.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
            ctrl2 = t2.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
            if ctrl1 is None and ctrl2 is None:
                continue
            self.assertEqual(len(ctrl1), len(ctrl2))
            for entry in ctrl1:
                self.assertTrue(ctrl2.contains(entry))

    def test_read_write_with_errors(self):
        parser = sppasRW(os.path.join(DATA, "sample-utf16.TextGrid"))
        with self.assertRaises(AioEncodingError):
            trs = parser.read()

    def test_read_heuristic(self):
        parser = sppasRW(os.path.join(DATA, "sample.heuristic"))
        trs = parser.read(heuristic=True)
        self.assertTrue(isinstance(trs, sppasTextGrid))
        self.assertEqual(len(trs), 2)
        self.assertEqual(len(trs[0]), 1)
        self.assertEqual(len(trs[1]), 2)
