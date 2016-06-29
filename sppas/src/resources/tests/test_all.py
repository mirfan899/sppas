#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import shutil

from paths import TEMP
from test_ngrams import TestNgramCounter
from test_ngrams import TestNgramsModel
from test_slm import TestSLM

if os.path.exists( TEMP ) is False:
    os.mkdir( TEMP )

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestNgramCounter))
testsuite.addTest(unittest.makeSuite(TestNgramsModel))
testsuite.addTest(unittest.makeSuite(TestSLM))

unittest.TextTestRunner(verbosity=2).run(testsuite)

shutil.rmtree( TEMP )
