# -*- coding:utf-8 -*-

import unittest

from ..compare import sppasCompare

# ---------------------------------------------------------------------------


class TestCompare(unittest.TestCase):

    def setUp(self):
        self.cmp = sppasCompare(verbose=False, case_sensitive=False)

    def test_equals_items(self):
        # Compare numeric values
        self.assertTrue(self.cmp.equals_items(5, 5))
        self.assertTrue(self.cmp.equals_items(5, 5.0))
        self.assertFalse(self.cmp.equals_items(4, 4.1))
        self.assertTrue(self.cmp.equals_items(4.00001, 4.00002))
        # Compare strings
        self.assertTrue(self.cmp.equals_items("aéè", "aéè"))
        self.assertTrue(self.cmp.equals_items("Aéè", "aéè"))
        self.cmp.set_case_sensitive(True)
        self.assertFalse(self.cmp.equals_items("Aéè", "aéè"))
        self.assertFalse(self.cmp.equals_items(u"Aéè", u"aéè"))
        self.cmp.set_case_sensitive(False)
        self.assertTrue(self.cmp.equals_items(u"Aéè", u"aéè"))
        #self.assertTrue(self.cmp.equals_items("Aéè", u"aéè"))

    def test_equals_lists(self):
        l1 = [1, 2, 3, 4]
        l2 = [1, 3, 4, 2]
        self.assertTrue(self.cmp.equals_lists(l1, l1))
        self.assertTrue(self.cmp.equals_lists(l2, l2))
        self.assertFalse(self.cmp.equals_lists(l1, l2))

    def test_equals_dicts(self):
        d1 = {1: "one", 2: "two"}
        d2 = {2: "TWO", 1: "ONE"}
        self.assertTrue(self.cmp.equals(d1, d2))
