#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from annotations.Chunks.spkrate import SpeakerRate

# ---------------------------------------------------------------------------


class TestSpeakerRate( unittest.TestCase ):

    def setUp(self):
        self._s = SpeakerRate()

    def test_set(self):
        self._s.set_value( 12. )
        self.assertEqual(self._s.get_value(), 12.)
        self._s.set_value(5.)
        self.assertEqual( self._s.get_value(), 5. )
        self._s.mul(10.)
        self.assertEqual( self._s.get_value(), 50. )
        with self.assertRaises(ValueError):
            self._s.set_value( 300 )
            self._s.set_value( "dfbzhb" )
            self._s.mul( 100 )

    def test_evaluators(self):
        self._s.set_value( 12. )
        self._s.eval_from_duration( 10., 100 )
        self.assertEqual( self._s.get_value(), 10. )
        self.assertEqual( self._s.ntokens( 10. ), 100 )
        self.assertEqual( self._s.duration( 20 ), 2. )
