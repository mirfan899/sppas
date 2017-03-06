# -*- coding:utf-8 -*-

import unittest
import os.path
import shutil

from ..aio.xra import sppasXRA
from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestXRA(unittest.TestCase):
    """
    Represents an XRA file, the native format of SPPAS.
    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_read1(self):
        xra3 = sppasXRA()
        xra3.read(os.path.join(DATA, "sample-1.1.xra"))
        # Tiers
        self.assertEqual(len(xra3), 3)
        # ... First Tier
        self.assertEqual(len(xra3[0]), 2)
        self.assertEqual(xra3.get_tier_index("Intonation"), 0)
        self.assertEqual(xra3[0].get_meta("id"), "t1")
        self.assertTrue(xra3[0].is_point())
        # ... Second Tier
        self.assertEqual(len(xra3[1]), 3)
        self.assertEqual(xra3.get_tier_index("TokensAlign"), 1)
        self.assertEqual(xra3[1].get_meta("id"), "t2")
        self.assertTrue(xra3[1].is_interval())
        # ... 3rd Tier
        self.assertEqual(len(xra3[2]), 1)
        self.assertEqual(xra3.get_tier_index("IPU"), 2)
        self.assertEqual(xra3[2].get_meta("id"), "t3")
        self.assertTrue(xra3[2].is_interval())
        # Controlled vocabulary
        self.assertEqual(len(xra3.get_ctrl_vocab_list()), 1)
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("v0"))
        # Hierarchy
        #self.assertEqual(len(xra3.hierarchy), 2)

    def test_read2(self):
        xra3 = sppasXRA()
        xra3.read(os.path.join(DATA, "sample-1.2.xra"))
        # Metadata
        self.assertEqual(xra3.get_meta("created"), "2015-08-03")
        self.assertEqual(xra3.get_meta("license"), "GPL v3")
        # Media
        self.assertEqual(len(xra3.get_media_list()), 3)
        self.assertIsNotNone(xra3.get_media_from_name("m1"))
        self.assertIsNotNone(xra3.get_media_from_name("m2"))
        self.assertIsNotNone(xra3.get_media_from_name("m3"))
        # Tiers
        self.assertEqual(len(xra3), 3)
        # ... First Tier
        self.assertEqual(len(xra3[0]), 2)
        self.assertEqual(xra3.get_tier_index("Intonation"), 0)
        self.assertEqual(xra3[0].get_meta("id"), "t1")
        self.assertTrue(xra3[0].is_point())
        # ... Second Tier
        self.assertEqual(len(xra3[1]), 3)
        self.assertEqual(xra3.get_tier_index("TokensAlign"), 1)
        self.assertEqual(xra3[1].get_meta("id"), "t2")
        self.assertTrue(xra3[1].is_interval())
        # ... 3rd Tier
        self.assertEqual(len(xra3[2]), 1)
        self.assertEqual(xra3.get_tier_index("IPU"), 2)
        self.assertEqual(xra3[2].get_meta("id"), "t3")
        self.assertTrue(xra3[2].is_interval())
        # Controlled vocabulary
        self.assertEqual(len(xra3.get_ctrl_vocab_list()), 1)
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("v0"))
        # Hierarchy
        #self.assertEqual(len(xra3.hierarchy), 2)

    def test_read3(self):
        xra3 = sppasXRA()
        xra3.read(os.path.join(DATA, "sample-1.3.xra"))
        # Metadata
        self.assertEqual(xra3.get_meta("created"), "2017-03-06")
        self.assertEqual(xra3.get_meta("license"), "GPL v3")
        # Media
        self.assertEqual(len(xra3.get_media_list()), 3)
        self.assertIsNotNone(xra3.get_media_from_name("m1"))
        self.assertIsNotNone(xra3.get_media_from_name("m2"))
        self.assertIsNotNone(xra3.get_media_from_name("m3"))
        # Tiers
        self.assertEqual(len(xra3), 3)
        # ... First Tier
        self.assertEqual(len(xra3[0]), 2)
        self.assertEqual(xra3.get_tier_index("Intonation"), 0)
        self.assertEqual(xra3[0].get_meta("id"), "t1")
        self.assertTrue(xra3[0].is_point())
        # ... Second Tier
        self.assertEqual(len(xra3[1]), 3)
        self.assertEqual(xra3.get_tier_index("TokensAlign"), 1)
        self.assertEqual(xra3[1].get_meta("id"), "t2")
        self.assertTrue(xra3[1].is_interval())
        # ... 3rd Tier
        self.assertEqual(len(xra3[2]), 1)
        self.assertEqual(xra3.get_tier_index("IPU"), 2)
        self.assertEqual(xra3[2].get_meta("id"), "t3")
        self.assertTrue(xra3[2].is_interval())
        # Controlled vocabulary
        self.assertEqual(len(xra3.get_ctrl_vocab_list()), 1)
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("v0"))
        # Hierarchy
        #self.assertEqual(len(xra3.hierarchy), 2)

    def test_read_write(self):
        xra = sppasXRA()
        xra.read(os.path.join(DATA, "sample-1.3.xra"))
        xra.write(os.path.join(TEMP, "sample-1.3.xra"))

        xra2 = sppasXRA()
        xra2.read(os.path.join(TEMP, "sample-1.3.xra"))

        # Compare annotations of original xra and xra2
        for t1, t2 in zip(xra, xra2):
            self.assertEqual(len(t1), len(t2))
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.get_label().get_best().get_typed_content(), a2.get_label().get_best().get_typed_content())
                self.assertEqual(a1.get_highest_localization().get_midpoint(), a2.get_highest_localization().get_midpoint())
                self.assertEqual(a1.get_lowest_localization().get_midpoint(), a2.get_lowest_localization().get_midpoint())
        # Compare media
        # Compare hierarchy
        # Compare controlled vocabularies
        for t1, t2 in zip(xra, xra2):
            ctrl1 = t1.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
            ctrl2 = t2.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
            if ctrl1 is None and ctrl2 is None:
                continue
            self.assertEqual(len(ctrl1), len(ctrl2))
            for entry in ctrl1:
                self.assertTrue(ctrl2.contains(entry))
