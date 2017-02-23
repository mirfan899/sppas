# -*- coding:utf-8 -*-

import unittest

from ..annlabel.label import sppasLabel
from ..annlocation.sppasTimePoint import sppasTimePoint
from ..annlocation.sppasTimeInterval import sppasTimeInterval
from ..sppasAnnotation import sppasAnnotation
from ..sppasTranscription import sppasTranscription
from ..tier import sppasTier

# ---------------------------------------------------------------------------


class TestHierarchy(unittest.TestCase):

    def test_Superset(self):
        """
        Return True if the sppasTier contains all sppasTimePoints of the given sppasTier.
        """
        reftier = sppasTier()
        subtier = sppasTier()

        self.assertTrue(reftier.IsSuperset(subtier))
        self.assertTrue(subtier.IsSuperset(reftier))

        reftier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1), sppasTimePoint(1.5))))
        reftier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1.5), sppasTimePoint(2))))
        reftier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(2), sppasTimePoint(2.5))))
        reftier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(2.5), sppasTimePoint(3))))

        self.assertTrue(reftier.IsSuperset(subtier))
        self.assertFalse(subtier.IsSuperset(reftier))

        subtier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1), sppasTimePoint(2))))
        subtier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(2), sppasTimePoint(3))))

        self.assertTrue(reftier.IsSuperset(subtier))
        self.assertFalse(subtier.IsSuperset(reftier))

    def test_Hierarchy(self):
        sppasTranscription = sppasTranscription()
        reftier = sppasTranscription.NewTier('reftier')
        subtier = sppasTranscription.NewTier('subtier')
        outtier = sppasTier('Out')

        reftier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1), sppasTimePoint(1.5))))
        reftier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1.5), sppasTimePoint(2))))
        reftier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(2), sppasTimePoint(2.5))))
        reftier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(2.5), sppasTimePoint(3))))  # reftier[3]

        subtier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1), sppasTimePoint(2))))  # subtier[0]
        subtier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(2), sppasTimePoint(3))))  # subtier[1]

        outtier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1.1), sppasTimePoint(2.1))))

        # Errors:
        with self.assertRaises(TypeError):
            sppasTranscription.GetHierarchy().add_link("Toto", reftier, subtier)
        with self.assertRaises(Exception):
            sppasTranscription.GetHierarchy().add_link("TimeAlignment", reftier, reftier)
        with self.assertRaises(Exception):
            sppasTranscription.GetHierarchy().add_link("TimeAlignment", reftier, outtier)
        with self.assertRaises(Exception):
            sppasTranscription.GetHierarchy().add_link("TimeAssociation", reftier, outtier)

        # Normal:
        sppasTranscription.GetHierarchy().add_link("TimeAlignment", reftier, subtier)

        reftier[3].GetLocation().SetEnd(sppasTimePoint(4))
        self.assertEquals(reftier[3].GetLocation().GetEnd(), sppasTimePoint(4))
        # this is something we have to do: guaranty of the hierarchy when modif!!!!!!
        #self.assertEquals(subtier[1].GetLocation().GetEndMidpoint(), 4.0)

        #IDEM: Modif of parent's/children locations must be validated!!!!!
        #with self.assertRaises(TypeError):
        #    subtier[1].GetLocation().SetEnd(sppasTimePoint(5))
        #self.assertEquals(subtier[1].GetLocation().GetEnd(), sppasTimePoint(4))

    def test_Append(self):
        trs = sppasTranscription()
        reftier = trs.NewTier('reftier')
        subtier = trs.NewTier('subtier')

        trs.GetHierarchy().add_link("TimeAlignment", reftier, subtier)

        with self.assertRaises(Exception):
            subtier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1), sppasTimePoint(2))))

        reftier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1), sppasTimePoint(1.5))))
        reftier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1.5), sppasTimePoint(2))))
        self.assertEqual(reftier.GetSize(), 2)

        self.assertTrue(subtier.IsEmpty())
        subtier.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1), sppasTimePoint(2))))
        self.assertEqual(subtier.GetSize(), 1)

    def test_Add(self):
        sppasTranscription = sppasTranscription()
        reftier = sppasTranscription.NewTier('reftier')
        subtier = sppasTranscription.NewTier('subtier')

        sppasTranscription.GetHierarchy().add_link("TimeAlignment", reftier, subtier)

        self.assertTrue(reftier.Add(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1), sppasTimePoint(1.5)))))
        self.assertTrue(reftier.Add(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1.5), sppasTimePoint(2)))))
        self.assertTrue(reftier.GetSize(), 2)

        self.assertTrue(subtier.Add(sppasAnnotation(sppasTimeInterval(sppasTimePoint(1), sppasTimePoint(2)))))
        self.assertEqual(subtier.GetSize(), 1)

    def test(self):
        sppasTranscription = sppasTranscription("test")
        phonemes = sppasTranscription.NewTier('phonemes')
        tokens = sppasTranscription.NewTier('tokens')
        syntax = sppasTranscription.NewTier('syntax')

        sppasTranscription.GetHierarchy().add_link("TimeAlignment", phonemes, tokens)

        for i in range(0, 11):
            phonemes.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(i * 0.1, 0.001),
                                                    sppasTimePoint(i * 0.1 + 0.1, 0.001)),
                                       Label("p%d" % i)))

        for i in range(0, 5):
            tokens.Append(sppasAnnotation(sppasTimeInterval(sppasTimePoint(i * 0.2, 0.001),
                                                  sppasTimePoint(i * 0.2 + 0.2, 0.0001)),
                                     Label("token label")))
            syntax.Add(sppasAnnotation(sppasTimeInterval(sppasTimePoint(i * 0.2, 0.001),
                                                  sppasTimePoint(i * 0.2 + 0.2, 0.0001)),
                                    Label("syntax label")))
        sppasTranscription.GetHierarchy().add_link("TimeAssociation", tokens, syntax)

        self.assertTrue(phonemes.IsSuperset(tokens))
        self.assertTrue(tokens.IsSuperset(syntax))

        self.assertTrue(phonemes.IsSuperset(tokens))
        self.assertTrue(tokens.IsSuperset(syntax))
