#!/usr/bin/env python2

import unittest
import os

import audiodata.io
from audiodata.channelformatter import ChannelFormatter

from paths import SPPASSAMPLES
sample_1 = os.path.join(SPPASSAMPLES, "samples-eng", "oriana1.wav")  # mono; 16000Hz; 16bits
sample_2 = os.path.join(SPPASSAMPLES, "samples-fra", "F_F_B003-P9.wav")  # mono; 44100Hz; 32bits


class TestChannelFormatter(unittest.TestCase):

    def setUp(self):
        self._sample_1 = audiodata.io.open(sample_1)
        self._sample_2 = audiodata.io.open(sample_2)

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
