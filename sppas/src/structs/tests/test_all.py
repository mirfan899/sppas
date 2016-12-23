#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import shutil

from paths           import TEMP
from test_lang       import TestLang
from test_confparser import TestAnnotationConfigParser

if os.path.exists( TEMP ) is False:
    os.mkdir( TEMP )

testsuite = unittest.TestSuite()

testsuite.addTest(unittest.makeSuite(TestLang))
testsuite.addTest(unittest.makeSuite(TestAnnotationConfigParser))

unittest.TextTestRunner(verbosity=2).run(testsuite)

shutil.rmtree( TEMP )
