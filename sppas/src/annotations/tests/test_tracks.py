#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os

from annotations.Align.aligners.alignerio import AlignerIO
from annotations.Chunks.anchors   import AnchorTier
from annotationdata import Tier, Annotation, TimeInterval, TimePoint, Label, Text
from resources.patterns import Patterns

# --------------------------------------------------------------------------

from paths import DATA

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

        self.t.set_duration(18.)
        self.t.Append( Annotation(TimeInterval(TimePoint(13.), TimePoint(13.5)), Label(Text(18,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(14.), TimePoint(14.6)), Label(Text(20,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(14.6), TimePoint(15.6)), Label(Text(21,data_type="int"))))
        f,t = self.t.fix_window( 14. )
        self.assertEqual(f, 15.6 )
        self.assertEqual(t, 18. )

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

    # ------------------------------------------------------------------------

    def test_holes(self):
        self.t = AnchorTier()
        self.t.set_duration(17.8)
        self.t.set_windelay(4.)
        self.t.set_extdelay(1.)
        self.t.set_outdelay(0.2)

        self.t.Append( Annotation(TimeInterval(TimePoint(0.),  TimePoint(1.5)),  Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(1.5), TimePoint(2.)),   Label(Text(0,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(3.),  TimePoint(3.5)),  Label(Text(-1,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(4.5), TimePoint(6.3)),  Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(7.),  TimePoint(8.)),   Label(Text(8,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(11.3),TimePoint(12.)),  Label(Text(-1,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(13.), TimePoint(13.5)), Label(Text(18,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(14.), TimePoint(14.6)), Label(Text(20,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(14.6), TimePoint(15.6)), Label(Text(21,data_type="int"))))

        self.assertTrue(self.t.check_holes_ntokens(10))
        self.assertFalse(self.t.check_holes_ntokens(9))

        self.assertEqual(self.t.fill_evident_holes(),1)

    # ------------------------------------------------------------------------

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

        a = self.t.Near( 13., 1 )
        self.assertEqual( a, 7 )
        a = self.t.Near( 17., 1 )
        self.assertEqual( a, -1 )
        a = self.t.Near( 17.8, 1 )
        self.assertEqual( a, -1 )

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

    def test_export(self):
        self.t = AnchorTier()
        self.t.set_duration(17.8)
        self.t.set_windelay(4.)
        self.t.set_extdelay(1.)
        self.t.set_outdelay(0.2)
        #self.t.Append( Annotation(TimeInterval(TimePoint(0.),  TimePoint(1.)),   Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(1.5), TimePoint(2.)),   Label(Text(3,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(4.5), TimePoint(6.3)),  Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(7.),  TimePoint(8.)),   Label(Text(8,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(13.), TimePoint(13.5)), Label(Text(12,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(14.), TimePoint(14.6)), Label(Text(13,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(14.6), TimePoint(15.2)), Label(Text(14,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(15.2), TimePoint(15.6)), Label("#")))
        self.t.Append( Annotation(TimeInterval(TimePoint(16.), TimePoint(16.60)), Label(Text(16,data_type="int"))))
        self.t.Append( Annotation(TimeInterval(TimePoint(16.63), TimePoint(17.)), Label(Text(17,data_type="int"))))

        toklist=[u"w0", u"w1", u"w2", u"w3", u"w4", u"w5", u"w6", u"w7", u"w8", u"w9", u"w10", u"w11", u"w12", u"w13", u"w14", u"w15", u"w16", u"w17"]

        newtier = self.t.export(toklist)
        #for ann in newtier:
        #    print ann

# --------------------------------------------------------------------------

class TestTracksAlign( unittest.TestCase ):

    def setUp(self):
        self._alignerio = AlignerIO()

    def test_matching(self):
        filename = os.path.join(DATA, "track_000000")
        wordalign = self._alignerio.read_aligned( filename )[1]
        self.assertEqual(len(wordalign), 21)

        ref = [u"好", u"感", u"啦 @", u"好似", u"梁", u"安", u"琪", u"咁", u"係", u"啦", u"係", u"我", u"以前", u"都", u"聽", u"過", u"佢", u"", u"節目", u"喀", u"覺得", u"佢", u"講", u"", u"非常之", u"膚", u"淺", u"及", u"幼稚", u"呀", u"哦", u"即", u"khut6", u"嘩", u"咁"]
        hyp = [(token,score) for (start,end,token,score) in wordalign]

        pattern = Patterns()
        pattern.set_ngram(3)
        m3 = pattern.ngram_matchings( ref,hyp )

        # Search for the lowest value in ref:
        minr = min( [ v[0] for v in m3 ] )
        maxr = max( [ v[0] for v in m3 ] )
        newref = ref[minr:maxr+1]
        minh = min( [ v[1] for v in m3 ] )
        maxh = max( [ v[1] for v in m3 ] )
        newhyp = hyp[minh:maxh+1]

        pattern = Patterns()
        pattern.set_ngram(3)
        newm3 = pattern.ngram_alignments( newref,newhyp )

        newm3 = [ (v[0]+minr,v[1]+minh) for v in newm3 ]

        self.assertEqual(newm3,[(5, 5), (6, 6), (7, 7), (17, 16), (18, 17), (19, 18)])

        pattern = Patterns()
        pattern.set_score(0.6)
        pattern.set_ngram(1)
        m1 = pattern.ngram_alignments( newref,newhyp )
        newm1 = [ (v[0]+minr,v[1]+minh) for v in m1 ]
        self.assertEqual(newm1,[(6, 6)])

