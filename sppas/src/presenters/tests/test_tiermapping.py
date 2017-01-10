#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os

from presenters.tiermapping import TierMapping
from annotationdata.aio.praat import TextGrid
from annotationdata.tier import Tier
from annotationdata.annotation import Annotation
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.label.label import Label
from resources.dictpron import DictPron

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
        self.tiermap = TierMapping()
        self.tiermap.add( "1", "un" )
        self.tiermap.add( "2", "deux" )
        self.tiermap.add( "3", "trois" )
        self.tiermap.add( "4", "quatre" )
        self.tiermap.add( "5", "cinq" )
        self.tiermap.add( "6", "six" )
        self.tiermap.add( "7", "sept" )
        self.tiermap.add( "8", "huit" )
        self.tiermap.add( "9", "neuf" )
        self.tiermap.add( "10", "dix" )
        self.tiermap.add( "20", "vingt" )
        self.tiermap.add( "30", "trente" )
        self.tiermap.add( "40", "quarante" )
        self.tiermap.add( "50", "cinquante" )
        self.tiermap.add( "60", "soixante" )
        self.tiermap.add( "70", "septante" )
        self.tiermap.add( "70", "soixante-dix" )
        self.tiermap.add( "80", "octante" )
        self.tiermap.add( "80", "quatre-vingts" )

    def test_run(self):
        self.tiermap.set_keep_miss( True )
        self.tiermap.set_reverse( False )
        t1 = self.tiermap.map_tier( self.tierP )
        t2 = self.tiermap.map_tier( self.tierI )
        self.tiermap.set_reverse( True )
        tP = self.tiermap.map_tier( t1 )
        tI = self.tiermap.map_tier( t2 )
        for a1, a2 in zip(tP, self.tierP):
            self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
            self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())
        for a1, a2 in zip(tI, self.tierI):
            l1 = a1.GetLabel().GetValue().split(DictPron.VARIANTS_SEPARATOR)
            l2 = a2.GetLabel().GetValue().split(DictPron.VARIANTS_SEPARATOR)
            self.assertEqual(sorted(list(set(l1))), sorted(l2))
            self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_phonetized_sample(self):
        tg = TextGrid()
        tg.read(os.path.join(DATA, "DGtdA05Np1_95-phon.TextGrid"))
        self.tier = tg.Find('Phonetization')
        tiermap = TierMapping( os.path.join(DATA, "ita_mapping.repl") )

        tiermap.set_keep_miss( True )
        tiermap.set_reverse( False )
        t = tiermap.map_tier( self.tier )

        tiermap.set_reverse( True )
        tp = tiermap.map_tier( t )
        for a1, a2 in zip(tp, self.tier):
            self.assertEqual(a1.GetLabel().GetValue(),a2.GetLabel().GetValue())
            self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

    def test_aligned_sample(self):
        tg = TextGrid()
        tg.read(os.path.join(DATA, "DGtdA05Np1_95-palign.TextGrid"))
        self.tier = tg.Find('PhonAlign')
        tiermap = TierMapping( os.path.join(DATA, "ita_mapping.repl") )

        tiermap.set_keep_miss( True )
        t1 = tiermap.map_tier( self.tier )
        tiermap.set_keep_miss( False )
        t2 = tiermap.map_tier( self.tier )
        for a1, a2 in zip(t1, t2):
            if a1.GetLabel().IsNoise() is True:
                self.assertNotEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertNotEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())
            else:
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTierMapping)
    unittest.TextTestRunner(verbosity=2).run(suite)
