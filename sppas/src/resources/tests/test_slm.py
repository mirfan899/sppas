#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os

from paths import TEMP

from resources.slm.statlangmodel import SLM
from resources.slm.ngramsmodel import NgramsModel
from resources.slm.arpaio import ArpaIO
from utils.type import compare

# ---------------------------------------------------------------------------

class TestSLM(unittest.TestCase):

    def setUp(self):
        self.corpusfile = os.path.join(TEMP,"corpus.txt")
        self.sent1 = "a a b a c a b b a a b"
        self.sent2 = "a a d c a b b a a b"
        self.sent3 = "a c a b d c d b a a b"
        f = open( self.corpusfile, "w" )
        f.write( self.sent1+"\n")
        f.write( self.sent2+"\n")
        f.write( self.sent3+"\n")
        f.close()


    def tearDown(self):
        os.remove( self.corpusfile )


    def testARPA(self):
        fn1 = os.path.join(TEMP,"model1.arpa")
        fn2 = os.path.join(TEMP,"model2.arpa")
        model = NgramsModel(3)
        model.count( self.corpusfile )
        probas = model.probabilities("logml")
        arpaio = ArpaIO()
        arpaio.set( probas )
        arpaio.save( fn1 )

        slm1 = SLM()
        slm1.load_from_arpa( fn1 )
        slm1.save_as_arpa( fn2 )

        slm2 = SLM()
        slm2.load_from_arpa( fn2 )

        m1 = slm1.model
        m2 = slm2.model
        self.assertTrue( compare(m1,m2) )

# ---------------------------------------------------------------------------
