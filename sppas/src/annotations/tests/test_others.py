#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import dirname,abspath

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotations.infotier import InfoTier

# ---------------------------------------------------------------------------

class TestInfoTier( unittest.TestCase ):

    def setUp(self):
        self.infotier = InfoTier()

    def test_options(self):
        self.assertEqual(self.infotier.get_option('program'), "SPPAS")
        with self.assertRaises(KeyError):
            self.infotier.add_option('program','toto')
        with self.assertRaises(KeyError):
            self.infotier.pop_option('toto')
        self.infotier.pop_option('program')
        with self.assertRaises(KeyError):
            self.infotier.get_option('program')
        self.infotier.add_option('program','SPPAS')
        self.assertEqual(self.infotier.get_option('program'), "SPPAS")

        self.infotier.activate_option('program',False)
        self.assertEqual(self.infotier.is_active_option('program'),False)
        self.infotier.activate_option('program',True)
        self.assertEqual(self.infotier.is_active_option('program'),True)

    def test_tier(self):
        tier = self.infotier.create_time_tier(0.,8.)
        self.assertEqual(tier.GetSize(),8)

# ---------------------------------------------------------------------------

if __name__ == '__main__':

    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(TestInfoTier))
    unittest.TextTestRunner(verbosity=2).run(testsuite)
