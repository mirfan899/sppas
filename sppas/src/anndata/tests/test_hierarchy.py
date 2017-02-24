# -*- coding:utf-8 -*-

import unittest

from ..annlabel.label import sppasLabel
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annotation import sppasAnnotation
from ..tier import sppasTier
from ..transcription import sppasTranscription

# ---------------------------------------------------------------------------


class TestHierarchy(unittest.TestCase):

    def test_Superset(self):
        """
        Return True if the sppasTier contains all sppasPoints of the given sppasTier.
        """
        reftier = sppasTier()
        subtier = sppasTier()

        self.assertTrue(reftier.IsSuperset(subtier))
        self.assertTrue(subtier.IsSuperset(reftier))

        reftier.Append(sppasAnnotation(sppasInterval(sppasPoint(1), sppasPoint(1.5))))
        reftier.Append(sppasAnnotation(sppasInterval(sppasPoint(1.5), sppasPoint(2))))
        reftier.Append(sppasAnnotation(sppasInterval(sppasPoint(2), sppasPoint(2.5))))
        reftier.Append(sppasAnnotation(sppasInterval(sppasPoint(2.5), sppasPoint(3))))

        self.assertTrue(reftier.IsSuperset(subtier))
        self.assertFalse(subtier.IsSuperset(reftier))

        subtier.Append(sppasAnnotation(sppasInterval(sppasPoint(1), sppasPoint(2))))
        subtier.Append(sppasAnnotation(sppasInterval(sppasPoint(2), sppasPoint(3))))

        self.assertTrue(reftier.IsSuperset(subtier))
        self.assertFalse(subtier.IsSuperset(reftier))

    def test_Hierarchy(self):
        sppasTranscription = sppasTranscription()
        reftier = sppasTranscription.NewTier('reftier')
        subtier = sppasTranscription.NewTier('subtier')
        outtier = sppasTier('Out')

        reftier.Append(sppasAnnotation(sppasInterval(sppasPoint(1), sppasPoint(1.5))))
        reftier.Append(sppasAnnotation(sppasInterval(sppasPoint(1.5), sppasPoint(2))))
        reftier.Append(sppasAnnotation(sppasInterval(sppasPoint(2), sppasPoint(2.5))))
        reftier.Append(sppasAnnotation(sppasInterval(sppasPoint(2.5), sppasPoint(3))))  # reftier[3]

        subtier.Append(sppasAnnotation(sppasInterval(sppasPoint(1), sppasPoint(2))))  # subtier[0]
        subtier.Append(sppasAnnotation(sppasInterval(sppasPoint(2), sppasPoint(3))))  # subtier[1]

        outtier.Append(sppasAnnotation(sppasInterval(sppasPoint(1.1), sppasPoint(2.1))))

        # Errors:
        with self.assertRaises(TypeError):
            sppasTranscription.GetHierarchy().add_link("Toto", reftier, subtier)
        with self.assertRaises(Exception):
            sppasTranscription.GetHierarchy().add_link("Alignment", reftier, reftier)
        with self.assertRaises(Exception):
            sppasTranscription.GetHierarchy().add_link("Alignment", reftier, outtier)
        with self.assertRaises(Exception):
            sppasTranscription.GetHierarchy().add_link("Association", reftier, outtier)

        # Normal:
        sppasTranscription.GetHierarchy().add_link("Alignment", reftier, subtier)

        reftier[3].GetLocation().SetEnd(sppasPoint(4))
        self.assertEquals(reftier[3].GetLocation().GetEnd(), sppasPoint(4))
        # this is something we have to do: guaranty of the hierarchy when modif!!!!!!
        #self.assertEquals(subtier[1].GetLocation().GetEndMidpoint(), 4.0)

        #IDEM: Modif of parent's/children locations must be validated!!!!!
        #with self.assertRaises(TypeError):
        #    subtier[1].GetLocation().SetEnd(sppasPoint(5))
        #self.assertEquals(subtier[1].GetLocation().GetEnd(), sppasPoint(4))

    def test_Append(self):
        trs = sppasTranscription()
        reftier = trs.NewTier('reftier')
        subtier = trs.NewTier('subtier')

        trs.GetHierarchy().add_link("Alignment", reftier, subtier)

        with self.assertRaises(Exception):
            subtier.Append(sppasAnnotation(sppasInterval(sppasPoint(1), sppasPoint(2))))

        reftier.Append(sppasAnnotation(sppasInterval(sppasPoint(1), sppasPoint(1.5))))
        reftier.Append(sppasAnnotation(sppasInterval(sppasPoint(1.5), sppasPoint(2))))
        self.assertEqual(reftier.GetSize(), 2)

        self.assertTrue(subtier.IsEmpty())
        subtier.Append(sppasAnnotation(sppasInterval(sppasPoint(1), sppasPoint(2))))
        self.assertEqual(subtier.GetSize(), 1)

    def test_Add(self):
        sppasTranscription = sppasTranscription()
        reftier = sppasTranscription.NewTier('reftier')
        subtier = sppasTranscription.NewTier('subtier')

        sppasTranscription.GetHierarchy().add_link("Alignment", reftier, subtier)

        self.assertTrue(reftier.Add(sppasAnnotation(sppasInterval(sppasPoint(1), sppasPoint(1.5)))))
        self.assertTrue(reftier.Add(sppasAnnotation(sppasInterval(sppasPoint(1.5), sppasPoint(2)))))
        self.assertTrue(reftier.GetSize(), 2)

        self.assertTrue(subtier.Add(sppasAnnotation(sppasInterval(sppasPoint(1), sppasPoint(2)))))
        self.assertEqual(subtier.GetSize(), 1)

    def test(self):
        sppasTranscription = sppasTranscription("test")
        phonemes = sppasTranscription.NewTier('phonemes')
        tokens = sppasTranscription.NewTier('tokens')
        syntax = sppasTranscription.NewTier('syntax')

        sppasTranscription.GetHierarchy().add_link("Alignment", phonemes, tokens)

        for i in range(0, 11):
            phonemes.Append(sppasAnnotation(sppasInterval(sppasPoint(i * 0.1, 0.001),
                                                    sppasPoint(i * 0.1 + 0.1, 0.001)),
                                       sppasLabel("p%d" % i)))

        for i in range(0, 5):
            tokens.Append(sppasAnnotation(sppasInterval(sppasPoint(i * 0.2, 0.001),
                                                  sppasPoint(i * 0.2 + 0.2, 0.0001)),
                                     sppasLabel("token label")))
            syntax.Add(sppasAnnotation(sppasInterval(sppasPoint(i * 0.2, 0.001),
                                                  sppasPoint(i * 0.2 + 0.2, 0.0001)),
                                    sppasLabel("syntax label")))
        sppasTranscription.GetHierarchy().add_link("Association", tokens, syntax)

        self.assertTrue(phonemes.IsSuperset(tokens))
        self.assertTrue(tokens.IsSuperset(syntax))

        self.assertTrue(phonemes.IsSuperset(tokens))
        self.assertTrue(tokens.IsSuperset(syntax))
