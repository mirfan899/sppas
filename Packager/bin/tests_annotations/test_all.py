#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_num2letter import TestNum2Letter
from test_tokenize   import TestDictTok
from test_phon       import TestDictPhon, TestDAGPhon, TestSppasPhon, TestPhonUnk
from test_align      import TestBaseAligner, TestBasicAlign, TestJuliusAlign, TestHviteAlign, TestModelMixer

# ---------------------------------------------------------------------------

testsuite = unittest.TestSuite()

# tokenize
testsuite.addTest(unittest.makeSuite(TestNum2Letter))
testsuite.addTest(unittest.makeSuite(TestDictTok))

# phonetize
testsuite.addTest(unittest.makeSuite(TestDictPhon))
testsuite.addTest(unittest.makeSuite(TestDAGPhon))
testsuite.addTest(unittest.makeSuite(TestSppasPhon))
testsuite.addTest(unittest.makeSuite(TestPhonUnk))

# alignment
testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestBaseAligner))
testsuite.addTest(unittest.makeSuite(TestBasicAlign))
testsuite.addTest(unittest.makeSuite(TestJuliusAlign))
testsuite.addTest(unittest.makeSuite(TestHviteAlign))
testsuite.addTest(unittest.makeSuite(TestModelMixer))

unittest.TextTestRunner(verbosity=2).run(testsuite)
