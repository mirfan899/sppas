#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
from paths import SAMPLES
import audiodata
from audiodata.channelformatter import ChannelFormatter


class TestChannelFormatter(unittest.TestCase):
    _sample_path_1 = os.path.join(SAMPLES, "oriana1.WAV") # mono file at 16000Hz, 16bits
    _sample_path_2 = os.path.join(SAMPLES, "F_F_B003-P9.wav")

    def setUp(self):
        self._sample_1 = audiodata.open(TestChannelFormatter._sample_path_1)
        self._sample_2 = audiodata.open(TestChannelFormatter._sample_path_2)

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

