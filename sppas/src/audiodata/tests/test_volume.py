#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os

import audiodata.io
from audiodata.channelvolume import ChannelVolume
from audiodata.audiovolume   import AudioVolume

from paths import SPPASSAMPLES
sample_1 = os.path.join(SPPASSAMPLES, "samples-eng", "oriana1.wav")

class TestVolume(unittest.TestCase):

    def test_rms(self):
        audio = audiodata.io.open(sample_1)
        cidx = audio.extract_channel(0)
        channel = audio.get_channel(cidx)

        chanvol  = ChannelVolume(channel)
        audiovol = AudioVolume(audio)

        self.assertEqual(chanvol.volume(), channel.rms())
        self.assertEqual(audiovol.volume(), audio.rms())
        self.assertEqual(chanvol.len(), int(channel.get_duration()/0.01) + 1)
        self.assertEqual(chanvol.min(), audiovol.min())
        self.assertEqual(chanvol.max(), audiovol.max())
        self.assertEqual(int(chanvol.mean()), int(audiovol.mean()))
        self.assertEqual(int(chanvol.variance()), int(audiovol.variance()))
        self.assertEqual(int(chanvol.stdev()), int(audiovol.stdev()))
