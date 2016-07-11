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
        self.t.set_extdelay(1.)
        self.t.set_outdelay(0.2)

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


    def test_near(self):
        self.t = AnchorTier()
        self.t.set_duration(17.8)
        self.t.set_windelay(4.)
        self.t.set_extdelay(1.)
        self.t.set_outdelay(0.2)

        self.assertIsNone( self.t.near_indexed_anchor(1., -1) )

        self.t.Append( Annotation(TimeInterval(TimePoint(0.),  TimePoint(1.5)),  Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(1.5), TimePoint(2.)),   Label(Text(1,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(3.),  TimePoint(3.5)),  Label(Text(-1,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(4.5), TimePoint(6.3)),  Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(7.),  TimePoint(8.)),   Label(Text(2,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(9.7), TimePoint(11.3)), Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(11.3),TimePoint(12.)),  Label(Text(-1,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(14.), TimePoint(14.6)), Label(Text(3,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(14.6),TimePoint(17.8)), Label("#")))

        a = self.t.near_indexed_anchor(1., 1)
        self.assertEqual( a.GetLabel().GetTypedValue(),1 )
        a = self.t.near_indexed_anchor(1.5, 1)
        self.assertEqual( a.GetLabel().GetTypedValue(),1 )
        a = self.t.near_indexed_anchor(2., 1)
        self.assertEqual( a.GetLabel().GetTypedValue(),2 )
        a = self.t.near_indexed_anchor(11., 1)
        self.assertEqual( a.GetLabel().GetTypedValue(),3 )
        a = self.t.near_indexed_anchor(15., 1)
        self.assertIsNone( a )

        a = self.t.near_indexed_anchor(1., -1)
        self.assertIsNone( a )
        a = self.t.near_indexed_anchor(3., -1)
        self.assertEqual( a.GetLabel().GetTypedValue(),1 )
        a = self.t.near_indexed_anchor(3.5, -1)
        self.assertEqual( a.GetLabel().GetTypedValue(),1 )
        a = self.t.near_indexed_anchor(5., -1)
        self.assertEqual( a.GetLabel().GetTypedValue(),1 )
        a = self.t.near_indexed_anchor(7., -1)
        self.assertEqual( a.GetLabel().GetTypedValue(),1 )
        a = self.t.near_indexed_anchor(8., -1)
        self.assertEqual( a.GetLabel().GetTypedValue(),2 )
        a = self.t.near_indexed_anchor(9.7, -1)
        self.assertEqual( a.GetLabel().GetTypedValue(),2 )
        a = self.t.near_indexed_anchor(11., -1)
        self.assertEqual( a.GetLabel().GetTypedValue(),2 )
        a = self.t.near_indexed_anchor(12., -1)
        self.assertEqual( a.GetLabel().GetTypedValue(),2 )
        a = self.t.near_indexed_anchor(14., -1)
        self.assertEqual( a.GetLabel().GetTypedValue(),2 )
        a = self.t.near_indexed_anchor(18., -1)
        self.assertEqual( a.GetLabel().GetTypedValue(),3 )
