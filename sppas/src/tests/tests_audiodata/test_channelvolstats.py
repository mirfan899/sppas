#!/usr/bin/env python2
# -*- coding: utf8 -*-

import sys
from os.path import abspath, dirname
SPPAS = dirname(dirname(dirname(abspath(__file__))))
sys.path.append( SPPAS )

import unittest
import os

import audiodata.io
from audiodata.channel import Channel
from audiodata.channelvolstats import ChannelVolumeStats
from audiodata.audio import AudioPCM
from tests.paths import SPPASSAMPLES, TEMP

sample_1 = os.path.join(SPPASSAMPLES, "samples-eng", "oriana1.wav")

class TestChannelStats(unittest.TestCase):

    def setUp(self):
        self._sample_1 = audiodata.io.open(sample_1)

    def tearDown(self):
        self._sample_1.close()

    def test_rms(self):
        cidx = self._sample_1.extract_channel(0)
        channel = self._sample_1.get_channel(cidx)
        chanvol = ChannelVolumeStats(channel)

        self.assertEqual(chanvol.volume(), channel.get_rms())
        self.assertEqual(chanvol.len(), int(channel.get_duration()/0.01) + 1)
        self.assertEqual(chanvol.min(), self._sample_1.get_minvolume())
        self.assertEqual(chanvol.max(), self._sample_1.get_maxvolume())
        self.assertEqual(int(chanvol.mean()), self._sample_1.get_meanvolume())
