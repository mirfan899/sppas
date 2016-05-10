#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
from paths import SAMPLES
import audiodata
from audiodata.audioutils import samples2frames


class TestAudioUtils(unittest.TestCase):
    _sample_path_1 = os.path.join(SAMPLES, "oriana1.WAV")
    _sample_path_2 = os.path.join(SAMPLES, "F_F_B003-P9.wav")
    _sample_path_3 = os.path.join(SAMPLES, "stereo.wav")

    _newsample_path_1 = os.path.join(SAMPLES, "oriana1new.wav")
    _newsample_path_2 = os.path.join(SAMPLES, "F_F_B003-P9new.wav")
    _newsample_path_3 = os.path.join(SAMPLES, "stereonew.wav")


    def setUp(self):
        self._sample_1 = audiodata.open(TestAudioUtils._sample_path_1)
        self._sample_2 = audiodata.open(TestAudioUtils._sample_path_2)
        self._sample_3 = audiodata.open(TestAudioUtils._sample_path_3)


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

