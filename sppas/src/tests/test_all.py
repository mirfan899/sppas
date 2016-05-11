#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import sys
import unittest
from paths import SPPAS
sys.path.append( SPPAS )


from tests_audiodata.test_audioutils                import TestAudioUtils
from tests_audiodata.test_audio_io                  import TestInformation, TestData
from tests_audiodata.test_channel                   import TestChannel
from tests_audiodata.test_channelsequalizer         import TestChannelsEqualizer
from tests_audiodata.test_channelsmixer             import TestChannelsMixer
from tests_audiodata.test_channelformatter          import TestChannelFormatter
from tests_audiodata.test_channelframes             import TestChannelFrames
from tests_audiodata.test_channelfragmentextracter  import TestChannelFragmentExtracter

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestAudioUtils))
testsuite.addTest(unittest.makeSuite(TestInformation))
testsuite.addTest(unittest.makeSuite(TestData))
testsuite.addTest(unittest.makeSuite(TestChannel))
testsuite.addTest(unittest.makeSuite(TestChannelsEqualizer))
testsuite.addTest(unittest.makeSuite(TestChannelsMixer))
testsuite.addTest(unittest.makeSuite(TestChannelFormatter))
testsuite.addTest(unittest.makeSuite(TestChannelFrames))
testsuite.addTest(unittest.makeSuite(TestChannelFragmentExtracter))


unittest.TextTestRunner(verbosity=2).run(testsuite)

