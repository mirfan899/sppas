#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_dictpron  import TestDictPron
from test_rutils    import TestRutils
from test_wordslst  import TestWordsList

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestDictPron))
testsuite.addTest(unittest.makeSuite(TestRutils))
testsuite.addTest(unittest.makeSuite(TestWordsList))

unittest.TextTestRunner(verbosity=2).run(testsuite)

