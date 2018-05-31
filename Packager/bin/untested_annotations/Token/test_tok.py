#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
import getopt
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))
sys.path.append(os.path.join(SPPAS, 'sppas'))

from annotations.TextNorm.tok import sppasTextNorm
from annotationdata.annotation import Annotation
from annotationdata.tier import Tier
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.label.label import Label


class TestSPPASTok(unittest.TestCase):

    def test_align(self):
        dictdir  = os.path.join(SPPAS, "resources", "vocab")
        vocabfile = os.path.join(dictdir, "FR.vocab")
        tok = sppasTok(vocabfile, "FR")
        tier = Tier()
        lines = (
                 u"pa(r)ce que j'ai euh",
                 u"un p(e)tit peu",
                 u"[i(l)s, iz] ont pas d(e) culture",
                 u"d'aut(re)",
                 u"(e)st-ce qu'elle a l'air bien ou pas",
                 u"p(eu)t-êt(re) moins évident",
                 u"[pa(r)ce que, passe] c'est euh",
                 u"t(out) ça",
                 u"j'(ai) euh",
                 u"[entre-elles, entrèl]"
                 )
        for i, line in enumerate(lines):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)),
                           Label(line))
            tier.Append(a)

        faked, std = tok.convert(tier)
        tok.align(std, faked)

        self.assertEqual(std[0].TextValue, u"parce_que j' ai euh")
        self.assertEqual(faked[0].TextValue, u"pace_que j' ai euh")

        self.assertEqual(std[1].TextValue, u"un_petit_peu")
        self.assertEqual(faked[1].TextValue, u"un_ptit_peu")

        self.assertEqual(std[2].TextValue, u"ils_ont pas de culture")
        self.assertEqual(faked[2].TextValue, u"iz ont_pas d culture")

        self.assertEqual(std[3].TextValue, u"d'autre")
        self.assertEqual(faked[3].TextValue, u"d'aut")

        self.assertEqual(std[4].TextValue,u"est-ce_qu' elle a l' air bien ou pas")
        self.assertEqual(faked[4].TextValue, u"st-ce_qu' elle a l' air bien ou pas")

        self.assertEqual(std[5].TextValue, u"peut-être moins évident")
        self.assertEqual(faked[5].TextValue, u"ptêt moins évident")

        self.assertEqual(std[6].TextValue, u"parce_que c'est euh")
        self.assertEqual(faked[6].TextValue, u"passe c'est euh")

        self.assertEqual(std[7].TextValue, u"tout_ça")
        self.assertEqual(faked[7].TextValue, u"t_ça")

        self.assertEqual(std[8].TextValue, u"j' euh")
        self.assertEqual(faked[8].TextValue, u"j' euh")



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSPPASTok))
    return suite

if __name__ == '__main__':
    unittest.main()
