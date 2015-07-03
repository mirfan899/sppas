#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_singlefilter     import TestSingleFilter
from test_relationfilter   import TestRelationFilter


testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestSingleFilter))
testsuite.addTest(unittest.makeSuite(TestRelationFilter))

unittest.TextTestRunner(verbosity=2).run(testsuite)
