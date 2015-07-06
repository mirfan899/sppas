#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.tier import Tier
from annotationdata.transcription import Transcription
#from annotationdata.ctrlvocab import CtrlVocab


class TestTranscription(unittest.TestCase):

    def test_Find(self):
        trs = Transcription()
        tier1 = trs.NewTier(name="tier")
        tier2 = trs.NewTier(name=" Tier")
        tier3 = trs.NewTier(name=" Tier2")

        tier = trs.Find(name="Tier ")
        self.assertEquals(tier, tier2)

        tier = trs.Find(name="tier2 ", case_sensitive=True)
        self.assertEquals(tier, None)

        tier = trs.Find(name="tier2 ", case_sensitive=False)
        self.assertEquals(tier, tier3)

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

#     def test_ctrlvocab(self):
#         voc1 = CtrlVocab("Verbal Strategies")
#         self.assertTrue(voc1.Append("definition"))
#         self.assertTrue(voc1.Append("example"))
#         self.assertTrue(voc1.Append("comparison"))
#         self.assertTrue(voc1.Append("gap filling with sound"))
#         self.assertTrue(voc1.Append("contrast"))
#         voc2 = CtrlVocab("N'importe quoi")
#         self.assertTrue(voc2.Append("toto"))
#         self.assertTrue(voc2.Append("titi"))
#         self.assertTrue(voc2.Append("tutu"))
#         trs = Transcription()
#         t1 = Tier("tier1")
#         t2 = Tier("tier2")
#         trs.Add(t1)
#         trs.Add(t2)
#
#         trs.AddCtrlVocab(voc1)
#         trs.AddCtrlVocab(voc2)
#         t1.SetCtrlVocab( voc1 )
#         t2.SetCtrlVocab( trs.GetCtrlVocab("N'importe quoi") )
#
#         self.assertEquals( t1.GetCtrlVocab(), voc1 )
#         self.assertEquals( t2.GetCtrlVocab(), voc2 )
#
#         voc1.Append('New entry')
#         self.assertEquals( t1.GetCtrlVocab(), voc1 )
#
#         t2.GetCtrlVocab().Append('Hello')
#         self.assertEquals( t2.GetCtrlVocab(), voc2 )
#
#         self.assertEquals(trs.GetCtrlVocab("N'importe quoi"),voc2)

# End TestTranscription
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTranscription)
    unittest.TextTestRunner(verbosity=2).run(suite)

