#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import shutil
from paths import TEMP

from test_audioutils         import TestAudioUtils
from test_audio              import TestAudioPCM
from test_audio_io           import TestInformation, TestData
from test_channel            import TestChannel
from test_channelformatter   import TestChannelFormatter
from test_channelframes      import TestChannelFrames
from test_channelsmixer      import TestChannelsMixer
from test_volume             import TestVolume

if os.path.exists( TEMP ) is False:
    os.mkdir( TEMP )

testsuite = unittest.TestSuite()
testsuite.addTest(unittest.makeSuite(TestAudioUtils))
testsuite.addTest(unittest.makeSuite(TestAudioPCM))
testsuite.addTest(unittest.makeSuite(TestInformation))
testsuite.addTest(unittest.makeSuite(TestData))
testsuite.addTest(unittest.makeSuite(TestChannel))
testsuite.addTest(unittest.makeSuite(TestChannelFormatter))
testsuite.addTest(unittest.makeSuite(TestChannelFrames))
testsuite.addTest(unittest.makeSuite(TestChannelsMixer))
testsuite.addTest(unittest.makeSuite(TestVolume))
unittest.TextTestRunner(verbosity=2).run(testsuite)

shutil.rmtree( TEMP )
