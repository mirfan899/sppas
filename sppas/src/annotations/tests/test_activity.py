# -*- coding: utf8 -*-

import unittest

from sppas import unk_stamp
from sppas import SYMBOLS
from sppas.src.annotationdata import Transcription
from ..Align.activity import sppasActivity

# ---------------------------------------------------------------------------


class TestActivity(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create(self):

        # create an instance with the default symbols
        a = sppasActivity()
        for s in SYMBOLS:
            self.assertTrue(s in a)
        self.assertTrue(unk_stamp in a)
        self.assertEqual(len(a), len(SYMBOLS)+1)

        # try to add again the same symbols - they won't
        for s in SYMBOLS:
            a.append_activity(s, SYMBOLS[s])
        self.assertEqual(len(a), len(SYMBOLS) + 1)

    def test_get_tier(self):
        a = sppasActivity()
        trs = Transcription()

        # No tokensTier
        with self.assertRaises(IOError):
            a.get_tier(trs)

        # Test with an empty Tokens tier
        trs.NewTier('TokensAlign')
        tier = a.get_tier(trs)
        self.assertEqual(len(tier), 0)

        # now, test with a real TokensTier
        # ...
