#!/usr/bin/env python2
# -*- coding: utf8 -*-

import paths
import unittest
import os

import audiodata.io
from audiodata.channelformatter  import ChannelFormatter
from audiodata.channelsmixer     import ChannelsMixer

from paths import SPPASSAMPLES
sample_1 = os.path.join(SPPASSAMPLES, "samples-eng", "oriana1.wav")
sample_2 = os.path.join(SPPASSAMPLES, "samples-fra", "F_F_B003-P9.wav")

class TestChannelsMixer(unittest.TestCase):

    def setUp(self):
        self._sample_1 = audiodata.io.open(sample_1)
        self._sample_2 = audiodata.io.open(sample_2)

    def tearDown(self):
        self._sample_1.close()
        self._sample_2.close()

    def test_Mix(self):
        self._sample_1.extract_channel(0)
        self._sample_2.extract_channel(0)

        formatter1 = ChannelFormatter(self._sample_1.get_channel(0))
        formatter1.set_framerate(16000)
        formatter1.set_sampwidth(2)
        formatter1.convert()

        formatter2 = ChannelFormatter(self._sample_2.get_channel(0))
        formatter2.set_framerate(16000)
        formatter2.set_sampwidth(2)
        formatter2.convert()

        mixer = ChannelsMixer()
        mixer.append_channel(formatter1.get_channel())
        mixer.append_channel(formatter2.get_channel())
        mixer.norm_length()

        self.assertEqual(mixer.get_channel(0).get_nframes(), mixer.get_channel(1).get_nframes())

        newchannel = mixer.mix()

        self.assertEqual(newchannel.get_nframes(), mixer.get_channel(0).get_nframes())
        self.assertEqual(newchannel.get_nframes(), mixer.get_channel(1).get_nframes())
