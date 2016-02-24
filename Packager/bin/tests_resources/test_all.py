#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_dictpron  import TestDictPron
from test_rutils    import TestRutils
from test_wordslst  import TestWordsList
from test_tiedlist  import TestTiedList

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestDictPron))
testsuite.addTest(unittest.makeSuite(TestRutils))
testsuite.addTest(unittest.makeSuite(TestWordsList))
testsuite.addTest(unittest.makeSuite(TestTiedList))

unittest.TextTestRunner(verbosity=2).run(testsuite)

