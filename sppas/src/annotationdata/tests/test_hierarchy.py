#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from annotationdata.label.label import Label
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation
from annotationdata.transcription import Transcription
from annotationdata.tier import Tier

# ---------------------------------------------------------------------------


class TestHierarchy(unittest.TestCase):

    def test_Superset(self):
        """
        Return True if the tier contains all timepoints of the given tier.
        """
        reftier = Tier()
        subtier = Tier()

        self.assertTrue(reftier.IsSuperset(subtier))
        self.assertTrue(subtier.IsSuperset(reftier))

        reftier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(1.5))))
        reftier.Append(Annotation(TimeInterval(TimePoint(1.5), TimePoint(2))))
        reftier.Append(Annotation(TimeInterval(TimePoint(2), TimePoint(2.5))))
        reftier.Append(Annotation(TimeInterval(TimePoint(2.5), TimePoint(3))))

        self.assertTrue(reftier.IsSuperset(subtier))
        self.assertFalse(subtier.IsSuperset(reftier))

        subtier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))
        subtier.Append(Annotation(TimeInterval(TimePoint(2), TimePoint(3))))

        self.assertTrue(reftier.IsSuperset(subtier))
        self.assertFalse(subtier.IsSuperset(reftier))

    def test_Hierarchy(self):
        transcription = Transcription()
        reftier = transcription.NewTier('reftier')
        subtier = transcription.NewTier('subtier')
        outtier = Tier('Out')

        reftier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(1.5))))
        reftier.Append(Annotation(TimeInterval(TimePoint(1.5), TimePoint(2))))
        reftier.Append(Annotation(TimeInterval(TimePoint(2), TimePoint(2.5))))
        reftier.Append(Annotation(TimeInterval(TimePoint(2.5), TimePoint(3))))  # reftier[3]

        subtier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))  # subtier[0]
        subtier.Append(Annotation(TimeInterval(TimePoint(2), TimePoint(3))))  # subtier[1]

        outtier.Append(Annotation(TimeInterval(TimePoint(1.1), TimePoint(2.1))))

        # Errors:
        with self.assertRaises(TypeError):
            transcription.GetHierarchy().add_link("Toto", reftier, subtier)
        with self.assertRaises(Exception):
            transcription.GetHierarchy().add_link("TimeAlignment", reftier, reftier)
        with self.assertRaises(Exception):
            transcription.GetHierarchy().add_link("TimeAlignment", reftier, outtier)
        with self.assertRaises(Exception):
            transcription.GetHierarchy().add_link("TimeAssociation", reftier, outtier)

        # Normal:
        transcription.GetHierarchy().add_link("TimeAlignment", reftier, subtier)

        reftier[3].GetLocation().SetEnd(TimePoint(4))
        self.assertEquals(reftier[3].GetLocation().GetEnd(), TimePoint(4))
        # this is something we have to do: guaranty of the hierarchy when modif!!!!!!
        #self.assertEquals(subtier[1].GetLocation().GetEndMidpoint(), 4.0)

        #IDEM: Modif of parent's/children locations must be validated!!!!!
        #with self.assertRaises(TypeError):
        #    subtier[1].GetLocation().SetEnd(TimePoint(5))
        #self.assertEquals(subtier[1].GetLocation().GetEnd(), TimePoint(4))

    def test_Append(self):
        trs = Transcription()
        reftier = trs.NewTier('reftier')
        subtier = trs.NewTier('subtier')

        trs.GetHierarchy().add_link("TimeAlignment", reftier, subtier)

        with self.assertRaises(Exception):
            subtier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))

        reftier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(1.5))))
        reftier.Append(Annotation(TimeInterval(TimePoint(1.5), TimePoint(2))))
        self.assertEqual(reftier.GetSize(), 2)

        self.assertTrue(subtier.IsEmpty())
        subtier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))
        self.assertEqual(subtier.GetSize(), 1)

    def test_Add(self):
        transcription = Transcription()
        reftier = transcription.NewTier('reftier')
        subtier = transcription.NewTier('subtier')

        transcription.GetHierarchy().add_link("TimeAlignment", reftier, subtier)

        self.assertTrue(reftier.Add(Annotation(TimeInterval(TimePoint(1), TimePoint(1.5)))))
        self.assertTrue(reftier.Add(Annotation(TimeInterval(TimePoint(1.5), TimePoint(2)))))
        self.assertTrue(reftier.GetSize(), 2)

        self.assertTrue(subtier.Add(Annotation(TimeInterval(TimePoint(1), TimePoint(2)))))
        self.assertEqual(subtier.GetSize(), 1)

    def test(self):
        transcription = Transcription("test")
        phonemes = transcription.NewTier('phonemes')
        tokens = transcription.NewTier('tokens')
        syntax = transcription.NewTier('syntax')

        transcription.GetHierarchy().add_link("TimeAlignment", phonemes, tokens)

        for i in range(0, 11):
            phonemes.Append(Annotation(TimeInterval(TimePoint(i * 0.1, 0.001),
                                                    TimePoint(i * 0.1 + 0.1, 0.001)),
                                       Label("p%d" % i)))

        for i in range(0, 5):
            tokens.Append(Annotation(TimeInterval(TimePoint(i * 0.2, 0.001),
                                                  TimePoint(i * 0.2 + 0.2, 0.0001)),
                                     Label("token label")))
            syntax.Add(Annotation(TimeInterval(TimePoint(i * 0.2, 0.001),
                                                  TimePoint(i * 0.2 + 0.2, 0.0001)),
                                    Label("syntax label")))
        transcription.GetHierarchy().add_link("TimeAssociation", tokens, syntax)

        self.assertTrue(phonemes.IsSuperset(tokens))
        self.assertTrue(tokens.IsSuperset(syntax))

        self.assertTrue(phonemes.IsSuperset(tokens))
        self.assertTrue(tokens.IsSuperset(syntax))

# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHierarchy)
    unittest.TextTestRunner(verbosity=2).run(suite)
