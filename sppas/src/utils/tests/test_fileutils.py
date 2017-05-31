# -*- coding:utf-8 -*-

import unittest
import os.path
import sys

from sppas import SAMPLES_PATH

from ..fileutils import sppasFileUtils, sppasDirUtils

# ---------------------------------------------------------------------------


class TestFileUtils(unittest.TestCase):

    def setUp(self):
        self.sample_1 = os.path.join(SAMPLES_PATH, "samples-eng", "oriana1.wav")
        self.sample_2 = os.path.join(SAMPLES_PATH, "samples-fra", "AG_éàç_0460.TextGrid")

    def test_set_random(self):
        sf = sppasFileUtils()
        f = os.path.basename(sf.set_random())
        self.assertTrue(f.startswith("sppas_tmp_"))
        f = os.path.basename(sf.set_random(add_today=False, add_pid=False))
        self.assertEqual(len(f), 14)
        f = os.path.basename(sf.set_random(root="toto", add_today=False, add_pid=False))
        self.assertTrue(f.startswith("toto_"))
        self.assertEqual(len(f), 9)

    def test_exists(self):
        sf = sppasFileUtils(self.sample_1)
        self.assertEqual(sf.exists(), self.sample_1)

    def test_format(self):
        sf = sppasFileUtils(" filename with some   whitespace ")
        f = sf.clear_whitespace()
        self.assertEqual(f, "filename_with_some_whitespace")
        sf = sppasFileUtils(self.sample_2)
        f = sf.to_ascii()
        if sys.version_info < (3,):
            self.assertTrue(f.endswith("AG________0460.TextGrid"))
        else:
            self.assertTrue(f.endswith("AG_____0460.TextGrid"))

class TestDirUtils(unittest.TestCase):

    def test_dir(self):
        sd = sppasDirUtils(os.path.join(SAMPLES_PATH, "samples-yue"))
        fl = sd.get_files("wav")
        self.assertEqual(len(fl), 1)
