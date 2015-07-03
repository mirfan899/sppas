#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import sys
from os.path import dirname, abspath
import xml.sax

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

import annotationdata.io
from annotationdata.io.xra import XRAHandler
from annotationdata.io.xra import XRA
from annotationdata.transcription import Transcription
from annotationdata.label.label import Label
from annotationdata.label.text import Text
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.disjoint import TimeDisjoint
from annotationdata.annotation import Annotation

SAMPLES=os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")


DOCUMENT1 = """<?xml version="1.0" encoding="UTF-8"?>

<Document
    Author="Me"
    Date="2014-02-25"
    Format="1.0"
    Version="1.0"
    Any="This is a simple sample"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema" xsi:noNamespaceSchemaLocation="XRAv1.0.xsd">
  <Head />
  <Tier ID="t1" tiername="Intonation" locale="fr">
     <Media URL="file:///file.wav" MimeType="audio/wav" />
     <Annotation>
         <Time>
             <Point midpoint="0.2345" radius="0.0005" />
         </Time>
         <Label>
             <Text>
                H*
             </Text>
         </Label>
     </Annotation>
  </Tier>

  <Tier ID="t2" tiername="TokensAlign" locale="fr">
    <Media URL="file:///file.wav" MimeType="audio/wav" />
     <Annotation>
         <Time>
             <Interval>
                 <Begin midpoint="0.1234" radius="0.0001" />
                 <End   midpoint="0.3600" radius="0.005" />
             </Interval>
         </Time>
          <Label >
              <Text>le</Text>
         </Label>
     </Annotation>
     <Annotation>
         <Time>
             <Interval>
                 <Begin midpoint="0.3600" radius="0.005" />
                 <End   midpoint="0.4000" radius="0.005" />
             </Interval>
         </Time>
          <Label >
              <Text>petit</Text>
         </Label>
     </Annotation>
     <Annotation>
         <Time>
             <Interval>
                 <Begin midpoint="0.5"  radius="0.005" />
                 <End   midpoint="0.87" radius="0.005" />
             </Interval>
         </Time>
          <Label>
              <Text score="1.0">label</Text>
         </Label>
     </Annotation>
     <Annotation>
         <Time>
             <Interval>
                 <Begin midpoint="0.8700" radius="0.005" />
                 <End   midpoint="0.9"    radius="0.0001" />
             </Interval>
         </Time>
          <Label>
              <Text score="1.0">supposé</Text>
         </Label>
     </Annotation>
  </Tier>

  <Tier ID="t3" tiername="IPU" locale="fr">
     <Media URL="file:///file.wav" MimeType="audio/wav" />
     <Annotation>
         <Time>
             <Disjoint>
                 <Interval>
                     <Begin midpoint="0.1234" radius="0.0001" />
                     <End   midpoint="0.36"   radius="0.005" />
                 </Interval>
                 <Interval>
                     <Begin midpoint="0.5" radius="0.005" />
                     <End   midpoint="0.9" radius="0.0001" />
                 </Interval>
              </Disjoint>
         </Time>
          <Label>
             <Text score="0.8">le petit texte supposé</Text>
             <Text score="0.2">le petit texte alternatif</Text>
         </Label>
     </Annotation>
  </Tier>

  <SubDivision link="TimeAlignment" reftier="t2" subtier="t3" />

</Document>
"""


class TestXRA(unittest.TestCase):
    """
    TestXRA.
    """
    def setUp(self):
        self.test_transcription = Transcription()
        test_intonation_tier = self.test_transcription.NewTier("Intonation")
        an = Annotation(TimePoint(0.2345, 0.0005), Label("H*"))
        test_intonation_tier.Add(an)

        test_tokens_tier = self.test_transcription.NewTier("TokensAlign")
        time = TimeInterval(TimePoint(0.1234, 0.0001), TimePoint(0.36, 0.005))
        an = Annotation(time, Label("le"))
        test_tokens_tier.Add(an)

        time = TimeInterval(TimePoint(0.36, 0.005), TimePoint(0.40, 0.005))
        an = Annotation(time, Label("petit"))
        test_tokens_tier.Add(an)

        time = TimeInterval(TimePoint(0.5, 0.005), TimePoint(0.87, 0.005))
        an = Annotation(time, Label("label"))
        test_tokens_tier.Add(an)
        
        time = TimeInterval(TimePoint(0.87, 0.005), TimePoint(0.9, 0.0001))
        an = Annotation(time, Label("supposé"))
        test_tokens_tier.Add(an)

        test_ipu_tier = self.test_transcription.NewTier("IPU")
        time = TimeDisjoint(*[TimeInterval(TimePoint(0.1234, 0.0001),
                              TimePoint(0.36, 0.005)),
                              TimeInterval(TimePoint(0.5, 0.005),
                              TimePoint(0.9, 0.0001))])
        text = Label(Text("le petit texte supposé", 0.8))
        text.AddValue(Text("le petit texte alternatif", 0.2))
        an = Annotation(time, text)
        test_ipu_tier.Add(an)
        self.test_transcription.AddInHierarchy(test_tokens_tier, test_ipu_tier, "TimeAlignment")


    def test_xrahandler(self):
        trs = Transcription()
        xrahandler = XRAHandler(trs)
        xml.sax.parseString(string=DOCUMENT1, handler=xrahandler)
        self.compare(trs, self.test_transcription)

    def test_conversion(self):
        trs = annotationdata.io.read(os.path.join(SAMPLES, "reference", "samples-FR", "F_F_B003-P8-merge.TextGrid"))
        annotationdata.io.write(os.path.join(SAMPLES,"sample.xra"), trs)
        xra = annotationdata.io.read(os.path.join(SAMPLES,"sample.xra"))
        self.compare(trs, xra)

    def test_write(self):
        trs = XRA()
        xrahandler = XRAHandler(trs)
        xml.sax.parseString(string=DOCUMENT1, handler=xrahandler)
        trs.write(os.path.join(SAMPLES,'sample.xra'))

    def test(self):
        trs1 = annotationdata.io.read(os.path.join(SAMPLES, "reference", "samples-FR", "BX_track_0451-merge.TextGrid"))

        phon = trs1.Find('PhonAlign')
        tok  = trs1.Find('TokensAlign')
        syll = trs1.Find('Syllables')

        trs1.AddInHierarchy(phon, tok, "TimeAlignment")
        trs1.AddInHierarchy(phon, syll, 'Constituency')

        annotationdata.io.write(os.path.join(SAMPLES,"test_xra.xra"), trs1)

        trs2 = annotationdata.io.read(os.path.join(SAMPLES,"test_xra.xra"))

        self.compare(trs1, trs2)

        phon = trs2.Find('PhonAlign')
        tok  = trs2.Find('TokensAlign')
        syll = trs2.Find('Syllables')

        #self.assertEqual(phon.GetAlignedTiers(), [tok, syll])
        #self.assertEqual(tok.GetAlignedTiers(), [])
        #self.assertEqual(syll.GetAlignedTiers(), [])
        #self.assertEqual(syll.GetReferenceTier(), phon)
        #self.assertEqual(tok.GetReferenceTier(), phon)
        #self.assertEqual(syll.GetConstituentTier(), phon)

        annotationdata.io.write(os.path.join(SAMPLES,"test_xra.xra"), trs2)
        trs3 = annotationdata.io.read(os.path.join(SAMPLES,"test_xra.xra"))

        self.compare(trs2, trs3)
        #phon = trs3.Find('PhonAlign')
        #tok  = trs3.Find('TokensAlign')
        #syll = trs3.Find('Syllables')

        #self.assertEqual(phon.GetAlignedTiers(), [tok, syll])
        #self.assertEqual(tok.GetAlignedTiers(), [])
        #self.assertEqual(syll.GetAlignedTiers(), [])
        #self.assertEqual(syll.GetReferenceTier(), phon)
        #self.assertEqual(tok.GetReferenceTier(), phon)
        #self.assertEqual(syll.GetConstituentTier(), phon)


    def compare(self, trs1, trs2):
        self.assertEqual(trs1.GetSize(), trs2.GetSize())
        for tier1, tier2 in zip(trs1, trs2):
            self.assertEqual(tier1.GetSize(), tier2.GetSize())
            self.assertEqual(tier1.GetName(), tier2.GetName())
            tier1.SetRadius(0.00004)
            tier2.SetRadius(0.00004)
            for an1, an2 in zip(tier1, tier2):
                self.assertEqual(an1.GetLocation().GetValue(), an2.GetLocation().GetValue())
                texts1 = an1.GetLabel().Get()
                texts2 = an2.GetLabel().Get()
                for text1, text2 in zip(texts1, texts2):
                    self.assertEqual(text1.Score, text2.Score)
                    self.assertEqual(text1.Value, text2.Value)

# End TestXRA
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestXRA)
    unittest.TextTestRunner(verbosity=2).run(suite)

