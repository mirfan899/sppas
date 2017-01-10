#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest

from annotationdata.tier import Tier
from annotationdata.transcription import Transcription
from annotationdata.ctrlvocab import CtrlVocab
from annotationdata.media import Media

# ---------------------------------------------------------------------------


class TestTranscription(unittest.TestCase):

    def setUp(self):
        self.trs = Transcription()
        self.tier1 = self.trs.NewTier(name="tier")
        self.tier2 = self.trs.NewTier(name=" Tier")
        self.tier3 = self.trs.NewTier(name=" Tier2")

    def test_Find(self):
        self.assertEquals(self.trs.Find(name="Tier "), self.tier2)
        self.assertEquals(self.trs.Find(name="tier2 ", case_sensitive=True), None)
        self.assertEquals(self.trs.Find(name="tier2 ", case_sensitive=False), self.tier3)

    def test_rename(self):
        trs = Transcription()
        trs.Add(Tier("tier"))
        trs.Add(Tier("tier"))
        trs.Append(Tier("tier"))
        trs.NewTier(name="tier")
        self.assertEquals(trs[0].GetName(), u"tier")
        self.assertEquals(trs[1].GetName(), u"tier-2")
        self.assertEquals(trs[2].GetName(), u"tier-3")
        self.assertEquals(trs[3].GetName(), u"tier-4")

    def test_ctrlvocab(self):
        voc1 = CtrlVocab("Verbal Strategies")
        self.assertTrue(voc1.Append("definition"))
        self.assertTrue(voc1.Append("example"))
        self.assertTrue(voc1.Append("comparison"))
        self.assertTrue(voc1.Append("gap filling with sound"))
        self.assertTrue(voc1.Append("contrast"))
        voc2 = CtrlVocab("N'importe quoi")
        self.assertTrue(voc2.Append("toto"))
        self.assertTrue(voc2.Append("titi"))
        self.assertTrue(voc2.Append("tutu"))
        trs = Transcription()
        t1 = Tier("tier1")
        t2 = Tier("tier2")
        trs.Add(t1)
        trs.Add(t2)

        trs.AddCtrlVocab(voc1)
        trs.AddCtrlVocab(voc2)
        t1.SetCtrlVocab( voc1 )
        t2.SetCtrlVocab( trs.GetCtrlVocabFromId("N'importe quoi") )

        self.assertEquals( t1.GetCtrlVocab(), voc1 )
        self.assertEquals( t2.GetCtrlVocab(), voc2 )

        voc1.Append('New entry')
        self.assertTrue( t1.GetCtrlVocab().Contains('New entry') )

        t2.GetCtrlVocab().Append('Hello')
        self.assertTrue( t2.GetCtrlVocab().Contains('Hello') )
        self.assertTrue( trs.GetCtrlVocabFromId("N'importe quoi").Contains('Hello') )

        self.assertEquals(trs.GetCtrlVocabFromId("N'importe quoi"),voc2)

    def test_media(self):
        m1 = Media('abc', 'filename', 'mime')
        self.trs.AddMedia(m1)
        self.assertEquals(len(self.trs.GetMedia()), 1)
        m2 = Media('def', 'filename.avi', 'video/avi')
        self.trs.AddMedia(m2)
        self.assertEquals(len(self.trs.GetMedia()), 2)
        #with self.assertRaises(ValueError):
        #    self.trs.AddMedia(m1)

        self.tier1.SetMedia( m1 )
        self.assertEquals(self.tier1.GetMedia(), m1)
        self.trs.RemoveMedia( m1 )
        self.assertEquals(self.tier1.GetMedia(), None)
