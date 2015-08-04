#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_io            import TestIO
from test_xra           import TestXRA
from test_textgrid      import TestTextGrid
from test_phonedit      import TestPhonedit
from test_annotationpro import TestAntx
from test_eaf           import TestEAF
from test_htk           import TestHTK

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestIO))
testsuite.addTest(unittest.makeSuite(TestXRA))
testsuite.addTest(unittest.makeSuite(TestTextGrid))
testsuite.addTest(unittest.makeSuite(TestPhonedit))
testsuite.addTest(unittest.makeSuite(TestAntx))
testsuite.addTest(unittest.makeSuite(TestEAF))
testsuite.addTest(unittest.makeSuite(TestHTK))

unittest.TextTestRunner(verbosity=2).run(testsuite)
