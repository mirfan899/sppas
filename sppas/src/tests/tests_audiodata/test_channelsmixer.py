#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
from paths import SAMPLES
import audiodata
from audiodata.channelsequalizer import ChannelsEqualizer
from audiodata.channelformatter  import ChannelFormatter
from audiodata.channelsmixer     import ChannelsMixer


class TestChannelsMixer(unittest.TestCase):
    _sample_path_1 = os.path.join(SAMPLES, "oriana1.WAV") # mono file at 16000Hz, 16bits
    _sample_path_2 = os.path.join(SAMPLES, "F_F_B003-P9.wav")

    def setUp(self):
        self._sample_1 = audiodata.open(TestChannelsMixer._sample_path_1)
        self._sample_2 = audiodata.open(TestChannelsMixer._sample_path_2)

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

        equalizer = ChannelsEqualizer()
        equalizer.append_channel(formatter1.channel)
        equalizer.append_channel(formatter2.channel)
        equalizer.equalize()

        mixer = ChannelsMixer()
        mixer.append_channel(equalizer.get_channel(0))
        mixer.append_channel(equalizer.get_channel(1))
        newchannel = mixer.mix()

        self.assertEqual(newchannel.get_nframes(), equalizer.get_channel(0).get_nframes())
        self.assertEqual(newchannel.get_nframes(), equalizer.get_channel(1).get_nframes())
