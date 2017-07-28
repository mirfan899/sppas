# -*- coding:utf-8 -*-

import unittest

from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlocation.location import sppasLocation

from ..annotation import sppasAnnotation
from ..tier import sppasTier
from ..transcription import sppasTranscription

# ---------------------------------------------------------------------------


class TestHierarchy(unittest.TestCase):

    def test_hierarchy(self):
        trs = sppasTranscription()
        reftier = trs.create_tier('reftier')
        subtier = trs.create_tier('subtier')
        outtier = sppasTier('Out')

        reftier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(1.5)))))
        reftier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(2.)))))
        reftier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2.), sppasPoint(2.5)))))
        reftier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2.5), sppasPoint(3.)))))  # reftier[3]

        subtier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))  # subtier[0]
        subtier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2.), sppasPoint(3.)))))  # subtier[1]

        outtier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.1), sppasPoint(2.1)))))

        # Errors:
        with self.assertRaises(TypeError):
            trs.hierarchy.add_link("Toto", reftier, subtier)
        with self.assertRaises(Exception):
            trs.hierarchy.add_link("TimeAlignment", reftier, reftier)
        with self.assertRaises(Exception):
            trs.hierarchy.add_link("TimeAlignment", reftier, outtier)
        with self.assertRaises(Exception):
            trs.hierarchy.add_link("TimeAssociation", reftier, outtier)
        # Normal:
        trs.hierarchy.add_link("TimeAlignment", reftier, subtier)

        # this is something we have to do: guaranty of the hierarchy when modifications !!!!!!
        # or to forbid modifications...

        # Modification of parent's/children:
        reftier[3].get_highest_localization().set(sppasPoint(4.))
        self.assertEquals(reftier[3].get_highest_localization(), sppasPoint(4.))
        #self.assertEquals(subtier[1].get_highest_localization(), sppasPoint(4.))
        #with self.assertRaises(TypeError):
        #    subtier[1].get_highest_localization().set(sppasPoint(5))
        #self.assertEquals(subtier[1].get_highest_localization(), sppasPoint(4.))

    def test_append(self):
        trs = sppasTranscription()
        reftier = trs.create_tier('reftier')
        subtier = trs.create_tier('subtier')

        trs.hierarchy.add_link("TimeAlignment", reftier, subtier)

        with self.assertRaises(Exception):
            subtier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))

        reftier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(1.5)))))
        reftier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(2.)))))
        self.assertEqual(len(reftier), 2)

        self.assertTrue(subtier.is_empty())
        subtier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        self.assertEqual(len(subtier), 1)

    def test_add(self):
        trs = sppasTranscription()
        reftier = trs.create_tier('reftier')
        subtier = trs.create_tier('subtier')

        trs.hierarchy.add_link("TimeAlignment", reftier, subtier)

        reftier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(1.5)))))
        reftier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(2.)))))
        self.assertTrue(len(reftier), 2)

        subtier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        self.assertEqual(len(subtier), 1)

    def test_trs(self):
        trs = sppasTranscription("test")
        phonemes = trs.create_tier('phonemes')
        tokens = trs.create_tier('tokens')
        syntax = trs.create_tier('syntax')
        trs.hierarchy.add_link("TimeAlignment", phonemes, tokens)

        for i in range(0, 11):
            phonemes.append(sppasAnnotation(
                sppasLocation(sppasInterval(sppasPoint(i * 0.1), sppasPoint(i * 0.1 + 0.1))),
                sppasLabel(sppasTag("phon %d" % i)))
            )

        for i in range(0, 5):
            syntax.append(sppasAnnotation(
                sppasLocation(sppasInterval(sppasPoint(i * 0.2), sppasPoint(i * 0.2 + 0.2))),
                sppasLabel(sppasTag("syntax label"))))
            tokens.append(sppasAnnotation(
                sppasLocation(sppasInterval(sppasPoint(i * 0.2), sppasPoint(i * 0.2 + 0.2))),
                sppasLabel(sppasTag("token label"))))
        trs.hierarchy.add_link("TimeAssociation", tokens, syntax)

        self.assertTrue(phonemes.is_superset(tokens))
        self.assertTrue(tokens.is_superset(syntax))

        self.assertTrue(phonemes.is_superset(tokens))
        self.assertTrue(tokens.is_superset(syntax))
