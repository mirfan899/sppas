#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_io       import TestIO
from test_textgrid import TestTextGrid
from test_phonedit import TestPhonedit
from test_xra      import TestXRA

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestIO))
testsuite.addTest(unittest.makeSuite(TestTextGrid))
testsuite.addTest(unittest.makeSuite(TestPhonedit))
testsuite.addTest(unittest.makeSuite(TestXRA))

unittest.TextTestRunner(verbosity=2).run(testsuite)

