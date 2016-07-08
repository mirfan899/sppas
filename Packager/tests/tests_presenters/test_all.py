#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_tiermapping         import TestTierMapping

testsuite = unittest.TestSuite()

testsuite.addTest(unittest.makeSuite(TestTierMapping))

unittest.TextTestRunner(verbosity=2).run(testsuite)

