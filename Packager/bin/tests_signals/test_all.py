#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from test_audioutils                import TestAudioUtils
from test_audio_io                  import TestInformation, TestData
from test_channel                   import TestChannel
from test_channelsequalizer         import TestChannelsEqualizer
from test_channelsmixer             import TestChannelsMixer
from test_channelformatter          import TestChannelFormatter
from test_monofragment              import TestMonoFragment
from test_channelfragmentextracter  import TestChannelFragmentExtracter

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestAudioUtils))
testsuite.addTest(unittest.makeSuite(TestInformation))
testsuite.addTest(unittest.makeSuite(TestData))
testsuite.addTest(unittest.makeSuite(TestChannel))
testsuite.addTest(unittest.makeSuite(TestChannelsEqualizer))
testsuite.addTest(unittest.makeSuite(TestChannelsMixer))
testsuite.addTest(unittest.makeSuite(TestChannelFormatter))
testsuite.addTest(unittest.makeSuite(TestMonoFragment))
testsuite.addTest(unittest.makeSuite(TestChannelFragmentExtracter))


unittest.TextTestRunner(verbosity=2).run(testsuite)

