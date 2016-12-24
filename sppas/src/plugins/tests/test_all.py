#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import paths

from test_cfgparser import TestPluginConfigParser
from test_param     import TestPluginParam
from test_process   import TestPluginProcess
from test_manager   import TestPluginsManager

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestPluginConfigParser))
testsuite.addTest(unittest.makeSuite(TestPluginParam))
testsuite.addTest(unittest.makeSuite(TestPluginProcess))
testsuite.addTest(unittest.makeSuite(TestPluginsManager))

# run the test...
unittest.TextTestRunner(verbosity=2).run(testsuite)
