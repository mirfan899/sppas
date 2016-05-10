#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import paths
import signals
from signals.monofragment import MonoFragment


class TestMonoFragment(unittest.TestCase):
    _sample_path_1 = os.path.join(paths.samples, "oriana1.WAV") # mono file at 16000Hz, 16bits
    _sample_path_2 = os.path.join(paths.samples, "F_F_B003-P9.wav")

    def setUp(self):
        self._sample_1 = signals.open(TestMonoFragment._sample_path_1)
        self._sample_2 = signals.open(TestMonoFragment._sample_path_2)

    def tearDown(self):
        self._sample_1.close()
        self._sample_2.close()
        
    def test_CreateSilence(self):
        self._sample_1.extract_channel(0)
        self._sample_2.extract_channel(0)
        
        channel = self._sample_1.get_channel(0)
        monofrag = MonoFragment(channel.frames)
        monofrag.create_silence(1000)
        self.assertEqual(channel.get_nframes()+1000, len(monofrag.get_frames())/channel.get_sampwidth())
        
        
        # ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMonoFragment)
    unittest.TextTestRunner(verbosity=2).run(suite)      
        