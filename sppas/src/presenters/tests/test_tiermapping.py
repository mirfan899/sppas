#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas import VARIANTS_SEPARATOR
from sppas.src.annotationdata.aio.praat import TextGrid
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.label.label import Label

from ..tiermapping import TierMapping

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestTierMapping(unittest.TestCase):

    def setUp(self):
        # Create tiers
        self.tierP = Tier("PointTier")
        self.tierI = Tier("IntervalTier")
        for i in range(8):
            self.tierP.Append(Annotation(TimePoint(i), Label(str(i))))
            self.tierI.Append(Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)), Label(str(i*10))))

        self.tierI.Append(Annotation(TimeInterval(TimePoint(9), TimePoint(10)), Label("quatre-vingts-dix|nonante")))

        # Create TierMapping
        self.tier_map = TierMapping()
        self.tier_map.add("1", "un")
        self.tier_map.add("2", "deux")
        self.tier_map.add("3", "trois")
        self.tier_map.add("4", "quatre")
        self.tier_map.add("5", "cinq")
        self.tier_map.add("6", "six")
        self.tier_map.add("7", "sept")
        self.tier_map.add("8", "huit")
        self.tier_map.add("9", "neuf")
        self.tier_map.add("10", "dix")
        self.tier_map.add("20", "vingt")
        self.tier_map.add("30", "trente")
        self.tier_map.add("40", "quarante")
        self.tier_map.add("50", "cinquante")
        self.tier_map.add("60", "soixante")
        self.tier_map.add("70", "septante")
        self.tier_map.add("70", "soixante-dix")
        self.tier_map.add("80", "octante")
        self.tier_map.add("80", "quatre-vingts")

    def test_run(self):
        self.tier_map.set_keep_miss(True)
        self.tier_map.set_reverse(False)
        t1 = self.tier_map.map_tier(self.tierP)
        t2 = self.tier_map.map_tier(self.tierI)
        self.tier_map.set_reverse(True)
        tP = self.tier_map.map_tier(t1)
        tI = self.tier_map.map_tier(t2)
        for a1, a2 in zip(tP, self.tierP):
            self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
            self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())
        for a1, a2 in zip(tI, self.tierI):
            l1 = a1.GetLabel().GetValue().split(VARIANTS_SEPARATOR)
            l2 = a2.GetLabel().GetValue().split(VARIANTS_SEPARATOR)
            self.assertEqual(sorted(list(set(l1))), sorted(l2))
            self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_phonetized_sample(self):
        tg = TextGrid()
        tg.read(os.path.join(DATA, "DGtdA05Np1_95-phon.TextGrid"))
        self.tier = tg.Find('Phonetization')
        tiermap = TierMapping(os.path.join(DATA, "ita_mapping.repl"))

        tiermap.set_keep_miss(True)
        tiermap.set_reverse(False)
        t = tiermap.map_tier(self.tier)

        tiermap.set_reverse(True)
        tp = tiermap.map_tier(t)
        for a1, a2 in zip(tp, self.tier):
            self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
            self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_aligned_sample(self):
        tg = TextGrid()
        tg.read(os.path.join(DATA, "DGtdA05Np1_95-palign.TextGrid"))
        self.tier = tg.Find('PhonAlign')
        tiermap = TierMapping(os.path.join(DATA, "ita_mapping.repl"))

        tiermap.set_keep_miss(True)
        t1 = tiermap.map_tier(self.tier)
        tiermap.set_keep_miss(False)
        t2 = tiermap.map_tier(self.tier)
        for a1, a2 in zip(t1, t2):
            if a1.GetLabel().IsNoise() is True:
                self.assertNotEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertNotEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())
            else:
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())
