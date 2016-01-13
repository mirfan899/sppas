#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from presenters.tiermapping import TierMapping
from annotationdata.io.praat import TextGrid
from annotationdata.tier import Tier
from annotationdata.annotation import Annotation
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.label.label import Label

SAMPLES=os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")

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
        self.tiermap.repl.add( "1", "un" )
        self.tiermap.repl.add( "2", "deux" )
        self.tiermap.repl.add( "3", "trois" )
        self.tiermap.repl.add( "4", "quatre" )
        self.tiermap.repl.add( "5", "cinq" )
        self.tiermap.repl.add( "6", "six" )
        self.tiermap.repl.add( "7", "sept" )
        self.tiermap.repl.add( "8", "huit" )
        self.tiermap.repl.add( "9", "neuf" )
        self.tiermap.repl.add( "10", "dix" )
        self.tiermap.repl.add( "20", "vingt" )
        self.tiermap.repl.add( "30", "trente" )
        self.tiermap.repl.add( "40", "quarante" )
        self.tiermap.repl.add( "50", "cinquante" )
        self.tiermap.repl.add( "60", "soixante" )
        self.tiermap.repl.add( "70", "soixante-dix" )
        self.tiermap.repl.add( "70", "septante" )
        self.tiermap.repl.add( "80", "quatre-vingts" )
        self.tiermap.repl.add( "80", "octante" )


    def test_run(self):
        self.tiermap.set_keepmiss( True )
        self.tiermap.set_reverse( False )
        t1 = self.tiermap.run( self.tierP )
        t2 = self.tiermap.run( self.tierI )
        self.tiermap.set_reverse( True )
        tP = self.tiermap.run( t1 )
        tI = self.tiermap.run( t2 )
        for a1, a2 in zip(tP, self.tierP):
            self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
            self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())
        for a1, a2 in zip(tI, self.tierI):
            self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
            self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())


    def test_phonetized_sample(self):
        tg = TextGrid()
        tg.read(os.path.join(SAMPLES,"DGtdA05Np1_95-phon.TextGrid"))
        self.tier = tg.Find('Phonetization')
        tiermap = TierMapping( os.path.join(SAMPLES,"ita_mapping.repl") )

        tiermap.set_keepmiss( True )
        tiermap.set_reverse( False )
        t = tiermap.run( self.tier )
        tiermap.set_reverse( True )
        tp = tiermap.run( t )
        for a1, a2 in zip(tp, self.tier):
            self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
            self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())


    def test_aligned_sample(self):
        tg = TextGrid()
        tg.read(os.path.join(SAMPLES,"DGtdA05Np1_95-palign.TextGrid"))
        self.tier = tg.Find('PhonAlign')
        tiermap = TierMapping( os.path.join(SAMPLES,"ita_mapping.repl") )

        tiermap.set_keepmiss( True )
        t1 = tiermap.run( self.tier )
        tiermap.set_keepmiss( False )
        t2 = tiermap.run( self.tier )
        for a1, a2 in zip(t1, t2):
            if a1.GetLabel().IsSilence() is True:
                self.assertNotEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertNotEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())
            else:
                self.assertEqual(a1.GetLabel().GetValue(), a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(), a2.GetLocation().GetValue())

# End TestAnnotation
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTierMapping)
    unittest.TextTestRunner(verbosity=2).run(suite)



