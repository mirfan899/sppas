#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os

from sppas import SAMPLES_PATH
from ..aio import open as audio_open
from ..audioutils import samples2frames

sample_1 = os.path.join(SAMPLES_PATH, "samples-eng", "oriana1.wav")
sample_2 = os.path.join(SAMPLES_PATH, "samples-fra", "F_F_B003-P9.wav")
sample_3 = os.path.join(SAMPLES_PATH, "samples-eng", "oriana3.wave")

# ---------------------------------------------------------------------------


class TestAudioUtils(unittest.TestCase):

    def setUp(self):
        self._sample_1 = audio_open(sample_1)
        self._sample_2 = audio_open(sample_2)
        self._sample_3 = audio_open(sample_3)

    def test_Samples2Frames(self):
        s1 = samples2frames(self._sample_1.read_samples(100), self._sample_1.get_sampwidth(), self._sample_2.get_nchannels())
        s2 = samples2frames(self._sample_2.read_samples(100), self._sample_2.get_sampwidth(), self._sample_2.get_nchannels())
        s3 = samples2frames(self._sample_3.read_samples(100), self._sample_3.get_sampwidth(), self._sample_3.get_nchannels())

        self._sample_1.rewind()
        self._sample_2.rewind()
        self._sample_3.rewind()

        self.assertItemsEqual(self._sample_1.read_frames(100), s1)
        self.assertItemsEqual(self._sample_2.read_frames(100), s2)
        self.assertItemsEqual(self._sample_3.read_frames(100), s3)
