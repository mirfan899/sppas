#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_singlefilter     import TestSingleFilter
from test_relationfilter   import TestRelationFilter
from test_kappa      import TestVectorKappa, TestTierKappa
from test_statistics import TestStatistics


testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestSingleFilter))
testsuite.addTest(unittest.makeSuite(TestRelationFilter))
testsuite.addTest(unittest.makeSuite(TestVectorKappa))
testsuite.addTest(unittest.makeSuite(TestTierKappa))
testsuite.addTest(unittest.makeSuite(TestStatistics))

unittest.TextTestRunner(verbosity=2).run(testsuite)
