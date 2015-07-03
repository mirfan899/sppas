#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import paths
import signals
from signals.channelformatter import ChannelFormatter


class TestChannelFormatter(unittest.TestCase):
    _sample_path_1 = os.path.join(paths.samples, "oriana1.WAV") # mono file at 16000Hz, 16bits
    _sample_path_2 = os.path.join(paths.samples, "F_F_B003-P9.wav")

    def setUp(self):
        self._sample_1 = signals.open(TestChannelFormatter._sample_path_1)
        self._sample_2 = signals.open(TestChannelFormatter._sample_path_2)

    def tearDown(self):
        self._sample_1.close()
        self._sample_2.close()
        
    def test_Sync(self):
        self._sample_1.extract_channel(0)
        self._sample_2.extract_channel(0)
        
        channel = self._sample_1.get_channel(0)
        
        formatter = ChannelFormatter(self._sample_2.get_channel(0))
        formatter.sync(channel)
        
        self.assertEqual(channel.get_framerate(), formatter.channel.get_framerate())  
        self.assertEqual(channel.get_sampwidth(), formatter.channel.get_sampwidth())
        
        # ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestChannelFormatter)
    unittest.TextTestRunner(verbosity=2).run(suite)      
        