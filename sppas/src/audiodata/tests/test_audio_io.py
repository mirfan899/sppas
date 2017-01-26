# -*- coding: utf8 -*-

import unittest
import os.path
import shutil

from ..aio import open as audio_open
from ..aio import save as audio_save
from ..aio import save_fragment as audio_save_fragment

from sppas.src.sp_glob import SAMPLES_PATH
from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
sample_1 = os.path.join(SAMPLES_PATH, "samples-eng", "oriana1.wav")
sample_2 = os.path.join(SAMPLES_PATH, "samples-fra", "F_F_B003-P9.wav")
sample_3 = os.path.join(SAMPLES_PATH, "samples-eng", "oriana3.wave")
sample_4 = os.path.join(SAMPLES_PATH, "samples-eng", "oriana1.aiff")

# ---------------------------------------------------------------------------


class TestInformation(unittest.TestCase):

    def setUp(self):
        self._sample_1 = audio_open(sample_1)
        self._sample_2 = audio_open(sample_2)
        self._sample_3 = audio_open(sample_3)
        self._sample_4 = audio_open(sample_4)

    def tearDown(self):
        self._sample_1.close()
        self._sample_2.close()
        self._sample_3.close()
        self._sample_4.close()

    def test_GetSampwidth(self):
        self.assertEqual(self._sample_1.get_sampwidth(), 2)
        self.assertEqual(self._sample_2.get_sampwidth(), 2)
        self.assertEqual(self._sample_3.get_sampwidth(), 2)
        self.assertEqual(self._sample_4.get_sampwidth(), 2)

    def test_GetChannel(self):
        self.assertEqual(self._sample_1.get_nchannels(), 1)
        self.assertEqual(self._sample_2.get_nchannels(), 1)
        self.assertEqual(self._sample_3.get_nchannels(), 2)
        self.assertEqual(self._sample_4.get_nchannels(), 1)

    def test_GetFramerate(self):
        self.assertEqual(self._sample_1.get_framerate(), 16000)
        self.assertEqual(self._sample_2.get_framerate(), 44100)
        self.assertEqual(self._sample_3.get_framerate(), 16000)
        self.assertEqual(self._sample_4.get_framerate(), 16000)

# ---------------------------------------------------------------------------


class TestData(unittest.TestCase):

    def setUp(self):
        self._sample_1 = audio_open(sample_1)
        self._sample_2 = audio_open(sample_2)
        self._sample_3 = audio_open(sample_3)
        self._sample_4 = audio_open(sample_4)
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        self._sample_1.close()
        self._sample_2.close()
        self._sample_3.close()
        self._sample_4.close()
        shutil.rmtree(TEMP)

    def test_ReadFrames(self):
        self.assertEqual(len(self._sample_1.read_frames(self._sample_1.get_nframes())),(self._sample_1.get_nframes()*self._sample_1.get_sampwidth()*self._sample_1.get_nchannels()))
        self.assertEqual(len(self._sample_2.read_frames(self._sample_2.get_nframes())),(self._sample_2.get_nframes()*self._sample_2.get_sampwidth()*self._sample_2.get_nchannels()))
        self.assertEqual(len(self._sample_3.read_frames(self._sample_3.get_nframes())),(self._sample_3.get_nframes()*self._sample_3.get_sampwidth()*self._sample_3.get_nchannels()))
        #self.assertEqual(len(self._sample_4.read_frames(self._sample_4.get_nframes())),(self._sample_4.get_nframes()*self._sample_4.get_sampwidth()*self._sample_4.get_nchannels()))

    def test_ReadSamples(self):
        samples = self._sample_1.read_samples(self._sample_1.get_nframes())
        self.assertEqual(len(samples), 1)
        self.assertEqual(len(samples[0]), self._sample_1.get_nframes())

        samples = self._sample_2.read_samples(self._sample_2.get_nframes())
        self.assertEqual(len(samples), 1)
        self.assertEqual(len(samples[0]), self._sample_2.get_nframes())

        samples = self._sample_3.read_samples(self._sample_3.get_nframes())
        self.assertEqual(len(samples), 2)
        self.assertEqual(len(samples[0]), self._sample_3.get_nframes())
        self.assertEqual(len(samples[1]), self._sample_3.get_nframes())

#         samples = self._sample_4.read_samples(self._sample_4.get_nframes())
#         self.assertEqual(len(samples), 1)
#         self.assertEqual(len(samples[0]), self._sample_4.get_nframes())

    def test_WriteFrames(self):
        _sample_new = os.path.join(TEMP, "newFile.wav")

        # save first
        audio_save( _sample_new, self._sample_1 )
        # read the saved file and compare Audio() instances
        newFile = audio_open( _sample_new )
        self.assertEqual(newFile.get_framerate(), self._sample_1.get_framerate())
        self.assertEqual(newFile.get_sampwidth(), self._sample_1.get_sampwidth())
        self.assertEqual(newFile.get_nchannels(), self._sample_1.get_nchannels())
        self.assertEqual(newFile.get_nframes(), self._sample_1.get_nframes())
        newFile.close()
        os.remove(_sample_new)
        self._sample_1.rewind()

        audio_save_fragment( _sample_new, self._sample_1, self._sample_1.read_frames(self._sample_1.get_nframes()))
        newFile = audio_open( _sample_new )
        self.assertEqual(newFile.get_framerate(), self._sample_1.get_framerate())
        self.assertEqual(newFile.get_sampwidth(), self._sample_1.get_sampwidth())
        self.assertEqual(newFile.get_nchannels(), self._sample_1.get_nchannels())
        self.assertEqual(newFile.get_nframes(), self._sample_1.get_nframes())
        newFile.close()
        os.remove(_sample_new)

        _sample_new = os.path.join(TEMP, "newFile.wav")
        # save first
        audio_save( _sample_new, self._sample_3 )
        # read the saved file and compare Audio() instances
        newFile = audio_open( _sample_new )
        self.assertEqual(newFile.get_framerate(), self._sample_3.get_framerate())
        self.assertEqual(newFile.get_sampwidth(), self._sample_3.get_sampwidth())
        self.assertEqual(newFile.get_nchannels(), self._sample_3.get_nchannels())
        self.assertEqual(newFile.get_nframes(), self._sample_3.get_nframes())
        newFile.close()
        os.remove(_sample_new)
        self._sample_3.rewind()

        audio_save_fragment( _sample_new, self._sample_3, self._sample_3.read_frames(self._sample_3.get_nframes()))
        newFile = audio_open( _sample_new )
        self.assertEqual(newFile.get_framerate(), self._sample_3.get_framerate())
        self.assertEqual(newFile.get_sampwidth(), self._sample_3.get_sampwidth())
        self.assertEqual(newFile.get_nchannels(), self._sample_3.get_nchannels())
        self.assertEqual(newFile.get_nframes(), self._sample_3.get_nframes())
        newFile.close()
        os.remove(_sample_new)

#         _sample_new = os.path.join(TEMP,"newFile.aiff")
#         # save first
#         audio_save( _sample_new, self._sample_4 )
#         # read the saved file and compare Audio() instances
#         newFile = audio_open( _sample_new )
#         self.assertEqual(newFile.get_framerate(), self._sample_4.get_framerate())
#         self.assertEqual(newFile.get_sampwidth(), self._sample_4.get_sampwidth())
#         self.assertEqual(newFile.get_nchannels(), self._sample_4.get_nchannels())
#         self.assertEqual(newFile.get_nframes(), self._sample_4.get_nframes())
#         newFile.close()
#         os.remove(_sample_new)
#         self._sample_4.rewind()
#
#         audio_save_fragment( _sample_new, self._sample_4, self._sample_4.read_frames(self._sample_4.get_nframes()))
#         newFile = audio_open( _sample_new )
#         self.assertEqual(newFile.get_framerate(), self._sample_4.get_framerate())
#         self.assertEqual(newFile.get_sampwidth(), self._sample_4.get_sampwidth())
#         self.assertEqual(newFile.get_nchannels(), self._sample_4.get_nchannels())
#         self.assertEqual(newFile.get_nframes(), self._sample_4.get_nframes())
#         newFile.close()
#         os.remove(_sample_new)

