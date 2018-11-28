#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os

from ..Align.aligners.alignerio import AlignerIO
from ..Chunks.anchors import AnchorTier
from sppas.src.anndata import sppasLocation, sppasInterval, sppasPoint, sppasLabel, sppasTag
from sppas.src.resources.patterns import sppasPatterns
from sppas.src.annotations.Chunks.spkrate import SpeakerRate

# --------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestSpeakerRate(unittest.TestCase):

    def setUp(self):
        self._s = SpeakerRate()

    def test_set(self):
        self._s.set_value(12.)
        self.assertEqual(self._s.get_value(), 12.)
        self._s.set_value(5.)
        self.assertEqual(self._s.get_value(), 5.)
        self._s.mul(10.)
        self.assertEqual(self._s.get_value(), 50.)
        with self.assertRaises(ValueError):
            self._s.set_value(300)
            self._s.set_value("dfbzhb")
            self._s.mul(100)

    def test_evaluators(self):
        self._s.set_value(12.)
        self._s.eval_from_duration(10., 100)
        self.assertEqual(self._s.get_value(), 10.)
        self.assertEqual(self._s.ntokens(10.), 100)
        self.assertEqual(self._s.duration(20), 2.)

# ---------------------------------------------------------------------------


class TestAnchorTier(unittest.TestCase):

    def test_window(self):
        tier = AnchorTier()
        tier.set_duration(12.)
        tier.set_win_delay(4.)
        f, t = tier.fix_window(0.)
        self.assertEqual(f, 0.)
        self.assertEqual(t, 4.)

        tier.set_duration(18.)
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(13.), sppasPoint(13.5))),
                               sppasLabel(sppasTag(18, "int")))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.), sppasPoint(14.6))),
                               sppasLabel(sppasTag(20, "int")))
        tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.6), sppasPoint(15.6))),
                               sppasLabel(sppasTag(21, "int")))
        f, t = tier.fix_window(14.)
        self.assertEqual(f, 15.6)
        self.assertEqual(t, 18.)

    # -----------------------------------------------------------------------

    def test_window_sil(self):
        t = AnchorTier()
        t.set_duration(17.8)
        t.set_win_delay(4.)
        t.set_ext_delay(1.)
        t.set_out_delay(0.2)

        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(0.), sppasPoint(1.5))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(4.5), sppasPoint(6.3))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(9.7), sppasPoint(11.3))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.6), sppasPoint(17.8))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))

        f, x = t.fix_window(0.)
        self.assertEqual(f, 1.5)
        self.assertEqual(x, 4.5)
        f, x = t.fix_window(0.5)
        self.assertEqual(f, 1.5)
        self.assertEqual(x, 4.5)
        f, x = t.fix_window(1.5)
        self.assertEqual(f, 1.5)
        self.assertEqual(x, 4.5)

        f, x = t.fix_window(3.5)
        self.assertEqual(f, 3.5)
        self.assertEqual(x, 4.5)

        f, x = t.fix_window(4.5)
        self.assertEqual(f, 6.3)
        self.assertEqual(x, 9.7)

        f, x = t.fix_window(9.)
        self.assertEqual(f, 9.)
        self.assertEqual(x, 9.7)

        f, x = t.fix_window(9.6)
        self.assertEqual(f, 11.3)
        self.assertEqual(x, 14.6)

        f, x = t.fix_window(14.6)
        self.assertEqual(f, 17.8)
        self.assertEqual(x, 17.8)

        t.set_win_delay(10.)
        f, x = t.fix_window(0)
        self.assertEqual(f, 1.5)
        self.assertEqual(x, 4.5)

        t.set_win_delay(2.)
        f, x = t.fix_window(0)
        self.assertEqual(f, 1.5)
        self.assertEqual(x, 3.5)

        t.set_win_delay(1.)
        f, x = t.fix_window(0)
        self.assertEqual(f, 1.5)
        self.assertEqual(x, 2.5)

    # ------------------------------------------------------------------------

    def test_fill_evident_holes(self):
        t = AnchorTier()
        t.set_duration(17.8)

        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(11.3), sppasPoint(12.))),
                            sppasLabel(sppasTag(15, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(13.), sppasPoint(13.5))),
                            sppasLabel(sppasTag(18, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.), sppasPoint(14.6))),
                            sppasLabel(sppasTag(20, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.6), sppasPoint(15.6))),
                            sppasLabel(sppasTag(21, "int")))

        # between 18 and 20... there is 19!
        self.assertEqual(t.fill_evident_holes(), 1)
        self.assertEqual(19, t[2].get_best_tag().get_typed_content())
        self.assertEqual(sppasPoint(13.5), t[2].get_lowest_localization())
        self.assertEqual(sppasPoint(14.), t[2].get_highest_localization())

    # ------------------------------------------------------------------------

    def test_near(self):
        t = AnchorTier()
        t.set_duration(17.8)
        t.set_win_delay(4.)
        t.set_ext_delay(1.)
        t.set_out_delay(0.2)

        #self.assertIsNone(t.near_indexed_anchor(1., -1))

        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(0.), sppasPoint(1.5))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(2.))),
                            sppasLabel(sppasTag(1, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(3.), sppasPoint(3.5))),
                            sppasLabel(sppasTag(-1, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(4.5), sppasPoint(6.3))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(7.), sppasPoint(8.))),
                            sppasLabel(sppasTag(2, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(9.7), sppasPoint(11.3))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(11.3), sppasPoint(12.))),
                            sppasLabel(sppasTag(-1, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.), sppasPoint(14.6))),
                            sppasLabel(sppasTag(3, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.6), sppasPoint(17.8))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))

        a = t.near(13., 1)
        self.assertEqual(a, 7)
        a = t.near(17., 1)
        self.assertEqual(a, -1)
        a = t.near(17.8, 1)
        self.assertEqual(a, -1)

        a = t.near_indexed_anchor(1.5, 1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 1)
        a = t.near_indexed_anchor(1.5, -1)
        self.assertIsNone(a)

        a = t.near_indexed_anchor(1., 1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 1)
        a = t.near_indexed_anchor(2., 1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 2)
        a = t.near_indexed_anchor(11., 1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 3)
        self.assertIsNone(t.near_indexed_anchor(15., 1))

        a = t.near_indexed_anchor(1., -1)
        self.assertIsNone(a)
        a = t.near_indexed_anchor(3., -1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 1)
        a = t.near_indexed_anchor(3.5, -1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 1)
        a = t.near_indexed_anchor(5., -1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 1)
        a = t.near_indexed_anchor(7., -1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 1)
        a = t.near_indexed_anchor(8., -1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 2)
        a = t.near_indexed_anchor(9.7, -1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 2)
        a = t.near_indexed_anchor(11., -1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 2)
        a = t.near_indexed_anchor(12., -1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 2)
        a = t.near_indexed_anchor(14., -1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 2)
        a = t.near_indexed_anchor(18., -1)
        self.assertEqual(a.get_best_tag().get_typed_content(), 3)

    # ------------------------------------------------------------------------

    def test_holes(self):
        t = AnchorTier()
        t.set_duration(17.8)
        t.set_win_delay(4.)
        t.set_ext_delay(1.)
        t.set_out_delay(0.2)

        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(0.), sppasPoint(1.5))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(2.))),
                            sppasLabel(sppasTag(0, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(3.), sppasPoint(3.5))),
                            sppasLabel(sppasTag(-1, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(4.5), sppasPoint(6.3))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(7.), sppasPoint(8.))),
                            sppasLabel(sppasTag(8, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(11.3), sppasPoint(12.))),
                            sppasLabel(sppasTag(-1, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(13.), sppasPoint(13.5))),
                            sppasLabel(sppasTag(18, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.), sppasPoint(14.6))),
                            sppasLabel(sppasTag(20, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.6), sppasPoint(15.6))),
                            sppasLabel(sppasTag(21, "int")))

        self.assertTrue(t.check_holes_ntokens(10))
        self.assertFalse(t.check_holes_ntokens(9))

    # ------------------------------------------------------------------------

    def test_export(self):
        t = AnchorTier()
        t.set_duration(17.8)
        t.set_win_delay(4.)
        t.set_ext_delay(1.)
        t.set_out_delay(0.2)

        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(2.))),
                            sppasLabel(sppasTag(3, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(4.5), sppasPoint(6.3))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(7.), sppasPoint(8.))),
                            sppasLabel(sppasTag(8, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(13.), sppasPoint(13.5))),
                            sppasLabel(sppasTag(12, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.), sppasPoint(14.6))),
                            sppasLabel(sppasTag(13, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(14.6), sppasPoint(15.2))),
                            sppasLabel(sppasTag(14, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(15.2), sppasPoint(15.6))),
                            sppasLabel(sppasTag(AnchorTier.SIL, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(16.), sppasPoint(16.60))),
                            sppasLabel(sppasTag(16, "int")))
        t.create_annotation(sppasLocation(sppasInterval(sppasPoint(16.63), sppasPoint(17.))),
                            sppasLabel(sppasTag(17, "int")))

        toklist = [u"w0", u"w1", u"w2", u"w3", u"w4", u"w5", u"w6", u"w7", u"w8",
                   u"w9", u"w10", u"w11", u"w12", u"w13", u"w14", u"w15", u"w16", u"w17"]

        newtier = t.export(toklist)
        for ann in newtier:
            print(ann)

# ---------------------------------------------------------------------------


class TestTracksAlign(unittest.TestCase):

    def test_matching(self):
        filename = os.path.join(DATA, "track_000000")
        wordalign = AlignerIO.read_aligned(filename)[1]
        self.assertEqual(21, len(wordalign))

        ref = [u"好", u"感", u"啦 @", u"好似", u"梁", u"安", u"琪", u"咁", u"係",
               u"啦", u"係", u"我", u"以前", u"都", u"聽", u"過", u"佢", u"",
               u"節目", u"喀", u"覺得", u"佢", u"講", u"", u"非常之", u"膚",
               u"淺", u"及", u"幼稚", u"呀", u"哦", u"即", u"khut6", u"嘩", u"咁"]
        hyp = [(token, score) for (start, end, token, score) in wordalign]

        pattern = sppasPatterns()
        pattern.set_ngram(3)
        m3 = pattern.ngram_matches(ref, hyp)

        # Search for the lowest value in ref:
        minr = min([v[0] for v in m3])
        maxr = max([v[0] for v in m3])
        newref = ref[minr:maxr+1]
        minh = min([v[1] for v in m3])
        maxh = max([v[1] for v in m3])
        newhyp = hyp[minh:maxh+1]

        pattern = sppasPatterns()
        pattern.set_ngram(3)
        newm3 = pattern.ngram_alignments(newref, newhyp)

        newm3 = [(v[0]+minr, v[1]+minh) for v in newm3]

        self.assertEqual(newm3, [(5, 5), (6, 6), (7, 7), (17, 16), (18, 17), (19, 18)])

        pattern = sppasPatterns()
        pattern.set_score(0.6)
        pattern.set_ngram(1)
        m1 = pattern.ngram_alignments(newref, newhyp)
        newm1 = [(v[0]+minr, v[1]+minh) for v in m1]
        self.assertEqual(newm1, [(6, 6)])
