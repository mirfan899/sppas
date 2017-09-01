#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os.path

from sppas import RESOURCES_PATH

from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotations.Syll.syllabification import Syllabification

# -------------------------------------------------------------------------

POL_SYLL = os.path.join(RESOURCES_PATH, "syll", "syllConfig-pol.txt")
FRA_SYLL = os.path.join(RESOURCES_PATH, "syll", "syllConfig-fra.txt")

# -------------------------------------------------------------------------


def labels2tier(phonemes):
    # Convert a list of strings into a tier.
    if len(phonemes) == 0:
        return None
    tier = Tier('Phonemes')
    for time, p in enumerate(phonemes):
        begin = TimePoint(time)
        end = TimePoint(time+1)
        label = Label(p)
        a = Annotation(TimeInterval(begin, end), label)
        tier.Append(a)
    return tier

# -------------------------------------------------------------------------


def get_syll(trs):
    tierS = trs.Find("Syllables")
    if tierS is None: return ""
    if tierS.GetSize()==0: return ""
    line = ""
    for s in tierS:
        text = s.GetLabel().GetValue()
        line = line+text + "|"
    return line[:-1]

# -------------------------------------------------------------------------


class TestSyll(unittest.TestCase):

    def setUp(self):
        self.syllabifierPOL = Syllabification(POL_SYLL, None)
        self.syllabifierFRA = Syllabification(FRA_SYLL, None)

    def testVV(self):
        tierP = labels2tier(['a', 'a'])
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify( tierP )
        syll = get_syll(trsS)
        self.assertEqual("a|a", syll)

    def testVCV(self):
        tierP = labels2tier(['a', 'b', 'a'])
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify(tierP)
        syll = get_syll(trsS)
        self.assertEqual("a|ba", syll)

    def testVCCV(self):
        # general rule
        tierP = labels2tier(['a', 'n', 'c', 'a'])
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify(tierP)
        syll = get_syll(trsS)
        self.assertEqual("an|ca", syll)

        # exception rule
        tierP = labels2tier(['a', 'g', 'j', 'a'])
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify( tierP )
        syll = get_syll(trsS)
        self.assertEqual("a|gja", syll)

        # specific (shift to left)
        tierP = labels2tier(['a', 'd', 'g', 'a'])
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify( tierP )
        syll = get_syll(trsS)
        self.assertEqual("a|dga", syll)

        # do not apply the previous specific rule if not VdgV
        tierP = labels2tier( ['a','x','d','g','a'] )
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify( tierP )
        syll = get_syll(trsS)
        self.assertEqual("ax|dga", syll)

        # specific (shift to right)
        tierP = labels2tier( ['a','z','Z','a'] )
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify( tierP )
        syll = get_syll(trsS)
        self.assertEqual("az|Za", syll)

    def testVCCCV(self):
        # general rule
        tierP = labels2tier( ['a','m','m','n','a'] )
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify( tierP )
        syll = get_syll(trsS)
        self.assertEqual("am|mna", syll)

        # exception rule
        tierP = labels2tier( ['a','dz','v','j','a'] )
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify( tierP )
        syll = get_syll(trsS)
        self.assertEqual("a|dzvja", syll)

        # specific (shift to left)
        tierP = labels2tier( ['a','b','z','n','a'] )
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify( tierP )
        syll = get_syll(trsS)
        self.assertEqual("a|bzna", syll)

        # specific (shift to right)
        tierP = labels2tier( ['a','r','w','S','a'] )
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify( tierP )
        syll = get_syll(trsS)
        self.assertEqual("arw|Sa", syll)

    def testVCCCCV(self):
        tierP = labels2tier(['a', 'b', 'r', 'v', 'j', 'a'])
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierPOL.syllabify( tierP )
        syll = get_syll(trsS)
        self.assertEqual("a|brvja", syll)

    def testVCCCCCV(self):
        tierP = labels2tier(['a', 'p', 's', 'k', 'm', 'w', 'a'])
        self.assertIsNotNone(tierP)
        trsS = self.syllabifierFRA.syllabify(tierP)
        syll = get_syll(trsS)
        self.assertEqual("apsk|mwa", syll)
