#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
from paths import SAMPLES
import audiodata
from audiodata.channelfragmentextracter import ChannelFragmentExtracter


class TestChannelFragmentExtracter(unittest.TestCase):
    _sample_path_1 = os.path.join(SAMPLES, "oriana1.WAV") # mono file at 16000Hz, 16bits
    _sample_path_2 = os.path.join(SAMPLES, "F_F_B003-P9.wav")

    def setUp(self):
        self._sample_1 = audiodata.open(TestChannelFragmentExtracter._sample_path_1)
        self._sample_2 = audiodata.open(TestChannelFragmentExtracter._sample_path_2)

    def tearDown(self):
        self._sample_1.close()
        self._sample_2.close()

    def test_CreateSilence(self):
        self._sample_1.extract_channel(0)
        self._sample_2.extract_channel(0)

        channel = self._sample_1.get_channel(0)
        extracter = ChannelFragmentExtracter(channel)
        newchannel = extracter.extract_fragment(1*channel.get_framerate(),2*channel.get_framerate())
        self.assertEqual(newchannel.get_nframes()/newchannel.get_framerate(), 1)
