#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import paths

from test_cfgparser import TestPluginConfigParser


testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestPluginConfigParser))

# run the test...
unittest.TextTestRunner(verbosity=2).run(testsuite)
