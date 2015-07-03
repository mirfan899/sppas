#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.tier import Tier
from annotationdata.label.label import Label
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation
from annotationdata.transcription import Transcription
from annotationdata.tier import Tier

class TestHierarchy(unittest.TestCase):
    """

      la gestion d'une Hierarchy() :

      - Association :
        par exemple Tokens (tier référente) et Lemmas (tier enfant)

        Tokens:      | le | chat  | est |  là   |
        Lemmas:      | le | chat  | être|  là   |

        Lemmas a exactement les mêmes frontières que Tokens


      - Alignement :
        par exemple Phoneme (tier référente) et Tokens (tier enfant)

        Phonemes:    | l  | S | a |  e  | l | a |
        Tokens:      | le | chat  | est |  là   |

        un Tokens ne peut pas avoir une frontière qui n'existe pas dans Phonemes


      - Constituence :
        par exemple Phoneme (tier référente) et Syllabes (tier enfant)

        Phonemes:    | l | S | a | e | l | a |
        Syllabes:    |           |   |       |

        une Syllabe ne peut pas avoir une frontière qui n'existe pas dans Phonemes
        une Syllabe n'a pas de Label (GetTextValue ira chercher dans les phonèmes).


    """
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
        reftier.Append(Annotation(TimeInterval(TimePoint(2.5), TimePoint(3)))) # reftier[3]

        subtier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(2)))) # subtier[0]
        subtier.Append(Annotation(TimeInterval(TimePoint(2), TimePoint(3)))) # subtier[1]

        outtier.Append(Annotation(TimeInterval(TimePoint(1.1), TimePoint(2.1))))

        # Errors:
        with self.assertRaises(ValueError):
            transcription.AddInHierarchy(reftier, outtier, type=transcription.TIME_ALIGNMENT)
        with self.assertRaises(TypeError):
            transcription.AddInHierarchy(reftier, subtier, type=transcription.TIME_ASSOCIATION)
        with self.assertRaises(TypeError):
            transcription.AddInHierarchy(reftier, subtier, type="toto")

        # Normal:
        transcription.AddInHierarchy(reftier, subtier, type=transcription.TIME_ALIGNMENT)

        reftier[3].GetLocation().SetEnd(TimePoint(4))
        self.assertEquals(reftier[3].GetLocation().GetEnd(), TimePoint(4))
        self.assertEquals(subtier[1].GetLocation().GetEndMidpoint(), 4.0)

        with self.assertRaises(TypeError):
            subtier[1].GetLocation().SetEnd(TimePoint(5))
        self.assertEquals(subtier[1].GetLocation().GetEnd(), TimePoint(4))


    def test_Append(self):
        trs = Transcription()
        reftier = trs.NewTier('reftier')
        subtier = trs.NewTier('subtier')

        trs.AddInHierarchy(reftier, subtier, type=trs.TIME_ALIGNMENT)

        with self.assertRaises(ValueError):
            subtier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))
        self.assertTrue(subtier.IsEmpty())

        reftier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(1.5))))
        reftier.Append(Annotation(TimeInterval(TimePoint(1.5), TimePoint(2))))
        self.assertEqual(reftier.GetSize(), 2)

        subtier.Append(Annotation(TimeInterval(TimePoint(1), TimePoint(2))))
        self.assertEqual(subtier.GetSize(), 1)


    def test_Add(self):
        transcription = Transcription()
        reftier = transcription.NewTier('reftier')
        subtier = transcription.NewTier('subtier')

        transcription.AddInHierarchy(reftier, subtier, type=transcription.TIME_ALIGNMENT)

        self.assertFalse(subtier.Add(Annotation(TimeInterval(TimePoint(1), TimePoint(2)))))
        self.assertTrue(subtier.IsEmpty())

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

        transcription.AddInHierarchy(phonemes, tokens, "TimeAlignment")
        transcription.AddInHierarchy(tokens,   syntax, "TimeAssociation")

        for i in range(0, 11):
            phonemes.Append(Annotation(TimeInterval(TimePoint(i * 0.1, 0.001),
                                                    TimePoint(i * 0.1 + 0.1, 0.001)),
                                       Label("p%d" % i)))

        for i in range(0, 5):
            tokens.Append(Annotation(TimeInterval(TimePoint(i * 0.2, 0.001),
                                                  TimePoint(i * 0.2 + 0.2, 0.0001)),
                                     Label("token label")))
            syntax.Append(Annotation(TimeInterval(TimePoint(i * 0.2, 0.001),
                                                  TimePoint(i * 0.2 + 0.2, 0.0001)),
                                    Label("syntax label")))
            tokens.Add(Annotation(TimeInterval(TimePoint(i * 0.2, 0.001),
                                                  TimePoint(i * 0.2 + 0.2, 0.0001)),
                                     Label("token label")))
            syntax.Add(Annotation(TimeInterval(TimePoint(i * 0.2, 0.001),
                                                  TimePoint(i * 0.2 + 0.2, 0.0001)),
                                    Label("syntax label")))

        for i, p in enumerate(phonemes):
            p.GetLocation().SetEnd( TimePoint(i * 0.1 +  0.1 + 0.011) )

        # phonemes:
        #Annotation: ([(0.000000,0.000000),(0.111000,0.000000)],1.0) / p0
        #Annotation: ([(0.100000,0.001000),(0.211000,0.000000)],1.0) / p1
        #Annotation: ([(0.200000,0.001000),(0.311000,0.000000)],1.0) / p2
        #Annotation: ([(0.300000,0.001000),(0.411000,0.000000)],1.0) / p3
        #Annotation: ([(0.400000,0.001000),(0.511000,0.000000)],1.0) / p4
        #Annotation: ([(0.500000,0.001000),(0.611000,0.000000)],1.0) / p5
        #Annotation: ([(0.600000,0.001000),(0.711000,0.000000)],1.0) / p6
        #Annotation: ([(0.700000,0.001000),(0.811000,0.000000)],1.0) / p7
        #Annotation: ([(0.800000,0.001000),(0.911000,0.000000)],1.0) / p8
        #Annotation: ([(0.900000,0.001000),(1.011000,0.000000)],1.0) / p9
        #Annotation: ([(1.000000,0.001000),(1.111000,0.000000)],1.0) / p10

        # tokens:
        #Annotation: ([(0.000000,0.000000),(0.200000,0.000100)],1.0) / token label
        #Annotation: ([(0.200000,0.001000),(0.400000,0.000100)],1.0) / token label
        #Annotation: ([(0.400000,0.001000),(0.600000,0.000100)],1.0) / token label
        #Annotation: ([(0.600000,0.001000),(0.800000,0.000100)],1.0) / token label
        #Annotation: ([(0.800000,0.001000),(1.000000,0.000100)],1.0) / token label

        self.assertTrue(phonemes.IsSuperset(tokens))
        self.assertTrue(tokens.IsSuperset(syntax))

        for i, p in enumerate(phonemes):
            p.GetLocation().SetEnd( TimePoint(i * 0.1 + 0.011) )

        self.assertTrue(phonemes.IsSuperset(tokens))
        self.assertTrue(tokens.IsSuperset(syntax))


    def test_constituency(self):
        transcription = Transcription()
        syllables = transcription.NewTier('syllables')
        phonemes = transcription.NewTier('phonemes')
        transcription.AddInHierarchy(phonemes, syllables, type="Constituency")
        for i in range(0, 10):
            phonemes.Append(Annotation(TimeInterval(TimePoint(i * 0.1, 0.001),
                                                    TimePoint(i * 0.1 + 0.1, 0.001)),
                                       Label("%d" % i)))
        for i in range(0, 5):
            syllables.Append(Annotation(TimeInterval(TimePoint(i * 0.2, 0.001),
                                                    TimePoint(i * 0.2 + 0.2, 0.001))
                                                    ))

        j = 0
        for i, a in enumerate(syllables):
            self.assertEqual(a.GetLabel().GetValue(), "%d%d" % (i+j, i+j+1))
            j += 1

        phonemes[0].GetLabel().SetValue("A")
        phonemes[1].GetLabel().SetValue("B")

        self.assertEqual(syllables[0].GetLabel().GetValue(), "AB")

        transcription.RemoveOfHierarchy(phonemes, syllables)
        for a in syllables:
            self.assertEqual(a.GetLabel().GetValue(), "")


# End TestSubDivision
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHierarchy)
    unittest.TextTestRunner(verbosity=2).run(suite)

