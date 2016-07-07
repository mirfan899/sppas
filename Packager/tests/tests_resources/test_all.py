#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_model     import TestInterpolate, TestAcModel

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestInterpolate))
testsuite.addTest(unittest.makeSuite(TestAcModel))

unittest.TextTestRunner(verbosity=2).run(testsuite)

