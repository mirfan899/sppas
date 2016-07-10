#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from annotations.Align.anchors import AnchorTier
from annotationdata import Tier, Annotation, TimeInterval, TimePoint, Label, Text

# --------------------------------------------------------------------------

class TestAnchorTier( unittest.TestCase ):

    def setUp(self):
        self.t = AnchorTier()

    def test_window(self):
        self.t = AnchorTier()
        self.t.set_duration(12.)
        self.t.set_windelay(4.)
        f,t = self.t.fix_window( 0. )
        self.assertEqual(f, 0.)
        self.assertEqual(t, 4.)

    def test_window_sil(self):
        self.t = AnchorTier()
        self.t.set_duration(17.8)

        self.t.set_windelay(4.)
        self.t.Append( Annotation(TimeInterval(TimePoint(0.), TimePoint(1.5)), Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(4.5),TimePoint(6.3)), Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(9.7),TimePoint(11.3)), Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(14.6),TimePoint(17.8)), Label("#")))

        f,t = self.t.fix_window( 0. )
        self.assertEqual(f, 1.5)
        self.assertEqual(t, 4.5)
        f,t = self.t.fix_window( 0.5 )
        self.assertEqual(f, 1.5)
        self.assertEqual(t, 4.5)
        f,t = self.t.fix_window( 1.5 )
        self.assertEqual(f, 1.5)
        self.assertEqual(t, 4.5)

        f,t = self.t.fix_window( 3.5 )
        self.assertEqual(f, 3.5)
        self.assertEqual(t, 4.5)

        f,t = self.t.fix_window( 4.5 )
        self.assertEqual(f, 6.3)
        self.assertEqual(t, 9.7)

        f,t = self.t.fix_window( 9. )
        self.assertEqual(f, 9.)
        self.assertEqual(t, 9.7)

        f,t = self.t.fix_window( 9.6 )
        self.assertEqual(f, 11.3)
        self.assertEqual(t, 14.6)

        f,t = self.t.fix_window( 14.6 )
        self.assertEqual(f, 17.8)
        self.assertEqual(t, 17.8)

        self.t.set_windelay( 10. )
        f,t = self.t.fix_window( 0 )
        self.assertEqual(f, 1.5)
        self.assertEqual(t, 4.5)

        self.t.set_windelay( 2. )
        f,t = self.t.fix_window( 0 )
        self.assertEqual(f, 1.5)
        self.assertEqual(t, 3.5)

        self.t.set_windelay( 1. )
        f,t = self.t.fix_window( 0 )
        self.assertEqual(f, 1.5)
        self.assertEqual(t, 2.5)
