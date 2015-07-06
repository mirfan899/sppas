#!/usr/bin/env python2
# -*- coding: utf8 -*-

from os.path import abspath, dirname, join
import sys

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(join(SPPAS, 'sppas', 'src'))
samples = join(dirname(dirname(dirname(abspath(__file__)))), 'samples')

import unittest
import os
import signals
from presenters.audiosppaspresenter import AudioSppasPresenter

class TestExport(unittest.TestCase):
    _sample_path_1 = os.path.join(samples, "oriana1.WAV")
    _sample_path_2 = os.path.join(samples, "F_F_B003-P9.wav")
    
    def setUp(self):
        self._converter = AudioSppasPresenter()
        
        self._sample_1 = signals.open(TestExport._sample_path_1)
        self._sample_2 = signals.open(TestExport._sample_path_2)
        
        self._sample_path_new = os.path.join(samples, "converted.wav")
        if os.path.exists(self._sample_path_new):
            os.remove(self._sample_path_new)
        
    def tearDown(self):
        if os.path.exists(self._sample_path_new):
            os.remove(self._sample_path_new)
        self._sample_1.close()
        self._sample_2.close()
        
    def test_Diagnosis(self):
        toconvert = self._converter.diagnosis( self._sample_path_2 )
        self.assertEqual(toconvert, True)

    def test_Export_NonConvert(self):
        self._converter.export(self._sample_path_1, self._sample_path_new)
        self.assertEqual(os.path.exists(self._sample_path_new), False)
        
    def test_Export_Change_Framerate(self):
        converted = self._converter.export(self._sample_path_2, self._sample_path_new)
        self.assertEqual(converted, True)
        self.assertEqual(os.path.exists(self._sample_path_new), True)

        newaudio = signals.open(self._sample_path_new)
        self.assertEqual(newaudio.get_framerate(), self._converter.get_framerate())
        self.assertEqual(newaudio.get_sampwidth(), self._converter.get_sampwidth())
        self.assertEqual(newaudio.get_nchannels(), 1)
        self.assertEqual(newaudio.get_nframes()/newaudio.get_framerate(), self._sample_2.get_nframes()/self._sample_2.get_framerate())
        
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestExport)
    unittest.TextTestRunner(verbosity=2).run(suite)

