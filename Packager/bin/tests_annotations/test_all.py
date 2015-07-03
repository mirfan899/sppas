#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_phonetize  import TestPhonetize
from test_num2letter import TestNum2Letter
from test_tokenize   import TestDictTok

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestPhonetize))
testsuite.addTest(unittest.makeSuite(TestNum2Letter))
testsuite.addTest(unittest.makeSuite(TestDictTok))

unittest.TextTestRunner(verbosity=2).run(testsuite)

