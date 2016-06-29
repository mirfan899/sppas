#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import shutil

from paths import TEMP
from test_ngrams import TestNgramCounter
from test_ngrams import TestNgramsModel

if os.path.exists( TEMP ) is False:
    os.mkdir( TEMP )

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestNgramCounter))
testsuite.addTest(unittest.makeSuite(TestNgramsModel))

unittest.TextTestRunner(verbosity=2).run(testsuite)

shutil.rmtree( TEMP )
