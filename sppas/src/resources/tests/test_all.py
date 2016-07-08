#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import shutil

from paths         import TEMP
from test_ngrams   import TestNgramCounter
from test_ngrams   import TestNgramsModel
from test_slm      import TestSLM
from test_rutils   import TestRutils
from test_wordslst import TestWordsList
from test_dict     import TestDictPron, TestDictRepl, TestMapping
from test_patterns import TestPatterns

if os.path.exists( TEMP ) is False:
    os.mkdir( TEMP )

testsuite = unittest.TestSuite()

# testsuite.addTest(unittest.makeSuite(TestRutils))
# testsuite.addTest(unittest.makeSuite(TestWordsList))
# testsuite.addTest(unittest.makeSuite(TestDictPron))
# testsuite.addTest(unittest.makeSuite(TestDictRepl))
# testsuite.addTest(unittest.makeSuite(TestMapping))
# testsuite.addTest(unittest.makeSuite(TestNgramCounter))
# testsuite.addTest(unittest.makeSuite(TestNgramsModel))
# testsuite.addTest(unittest.makeSuite(TestSLM))
testsuite.addTest(unittest.makeSuite(TestPatterns))

unittest.TextTestRunner(verbosity=2).run(testsuite)

shutil.rmtree( TEMP )
