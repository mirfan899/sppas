#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import unittest
import test_lemmadict
import test_phonetize
import test_tiedlist
import test_tokenize

suite = unittest.TestSuite()
suite.addTest(test_lemmadict.suite())
suite.addTest(test_phonetize.suite())
suite.addTest(test_tiedlist.suite())
suite.addTest(test_tokenize.suite())

unittest.TextTestRunner(verbosity=2).run(suite)
