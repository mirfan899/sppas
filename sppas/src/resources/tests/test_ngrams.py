#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import math

from paths import TEMP

from resources.slm.ngramsmodel import START_SENT_SYMBOL, END_SENT_SYMBOL, UNKSTAMP
from resources.slm.ngramsmodel import NgramCounter
from resources.slm.ngramsmodel import NgramsModel
from resources.wordslst import WordsList

# ---------------------------------------------------------------------------

class TestNgramCounter(unittest.TestCase):

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

    def testAppendSentence1(self):
        ngramcounter = NgramCounter() # default is unigram
        ngramcounter.append_sentence( self.sent1 )
        self.assertEqual(ngramcounter.get_count('a'), 6)
        self.assertEqual(ngramcounter.get_count('b'), 4)
        self.assertEqual(ngramcounter.get_count('c'), 1)
        self.assertEqual(ngramcounter.get_count('d'), 0)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 1)
        self.assertEqual(ngramcounter.get_ncount(), 12)
        ngramcounter.append_sentence( self.sent2 )
        ngramcounter.append_sentence( self.sent3 )
        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 3)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)

    def testAppendSentence2(self):
        ngramcounter = NgramCounter(2) # bigram
        ngramcounter.append_sentence( self.sent1 )
        self.assertEqual(ngramcounter.get_count('a b'), 3)
        self.assertEqual(ngramcounter.get_count('b a'), 2)
        self.assertEqual(ngramcounter.get_count('a c'), 1)
        self.assertEqual(ngramcounter.get_count('a d'), 0)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' a'), 1)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' b'), 0)
        self.assertEqual(ngramcounter.get_count('a '+END_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count('b '+END_SENT_SYMBOL), 1)
        ngramcounter.append_sentence( self.sent2 )
        ngramcounter.append_sentence( self.sent3 )
        self.assertEqual(ngramcounter.get_count('a b'), 7)
        self.assertEqual(ngramcounter.get_count('b a'), 4)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' a'), 3)
        self.assertEqual(ngramcounter.get_count('b '+END_SENT_SYMBOL), 3)

    def testCount1(self):
        ngramcounter = NgramCounter() # default is unigram
        ngramcounter.count( self.corpusfile )
        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 3)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)
        ngramcounter = NgramCounter(1)
        ngramcounter.count( self.corpusfile, self.corpusfile )
        self.assertEqual(ngramcounter.get_count('a'), 30)
        self.assertEqual(ngramcounter.get_count('b'), 20)
        self.assertEqual(ngramcounter.get_count('c'), 8)
        self.assertEqual(ngramcounter.get_count('d'), 6)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 6)

    def testCount2(self):
        ngramcounter = NgramCounter(2)
        ngramcounter.count( self.corpusfile )
        self.assertEqual(ngramcounter.get_count('a b'), 7)
        self.assertEqual(ngramcounter.get_count('b a'), 4)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' a'), 3)
        self.assertEqual(ngramcounter.get_count('b '+END_SENT_SYMBOL), 3)

    def testShave(self):
        ngramcounter = NgramCounter(1)
        ngramcounter.count( self.corpusfile )
        ngramcounter.shave(4)
        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 0)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)

    def testVocab(self):
        wds = WordsList()
        wds.add("a")
        wds.add("b")
        wds.add("c")
        ngramcounter = NgramCounter(1,wds)
        ngramcounter.count( self.corpusfile )

        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 0)
        self.assertEqual(ngramcounter.get_count(UNKSTAMP), 3)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)

# End TestNgramCounter
# ---------------------------------------------------------------------------

class TestNgramsModel(unittest.TestCase):

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


    def testCount(self):
        model = NgramsModel(2)
        model.count( self.corpusfile )
        self.assertEqual(len(model.ngramcounts), 2)
        ngramcounter = model.ngramcounts[0]
        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 3)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)
        ngramcounter = model.ngramcounts[1]
        self.assertEqual(ngramcounter.get_count('a b'), 7)
        self.assertEqual(ngramcounter.get_count('b a'), 4)
        self.assertEqual(ngramcounter.get_count('d b'), 1)
        self.assertEqual(ngramcounter.get_count('d c'), 2)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' a'), 3)
        self.assertEqual(ngramcounter.get_count('b '+END_SENT_SYMBOL), 3)


    def testShave(self):
        model = NgramsModel(2)
        model.count( self.corpusfile )
        self.assertEqual(len(model.ngramcounts), 2)
        model.set_min_count(2)
        ngramcounter = model.ngramcounts[0]
        self.assertEqual(ngramcounter.get_count('a'), 15)
        self.assertEqual(ngramcounter.get_count('b'), 10)
        self.assertEqual(ngramcounter.get_count('c'), 4)
        self.assertEqual(ngramcounter.get_count('d'), 3)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL), 0)
        self.assertEqual(ngramcounter.get_count(END_SENT_SYMBOL), 3)
        ngramcounter = model.ngramcounts[1]
        self.assertEqual(ngramcounter.get_count('a b'), 7)
        self.assertEqual(ngramcounter.get_count('b a'), 4)
        self.assertEqual(ngramcounter.get_count('d b'), 0)
        self.assertEqual(ngramcounter.get_count('d c'), 2)
        self.assertEqual(ngramcounter.get_count(START_SENT_SYMBOL+' a'), 3)
        self.assertEqual(ngramcounter.get_count('b '+END_SENT_SYMBOL), 3)


    def testRawProbabilities(self):
        model = NgramsModel(2)
        model.count( self.corpusfile )
        probas = model.probabilities( method="raw" )
        self.assertEqual(len(probas), 2)

        unigram = probas[0]
        for token,value,bo in unigram:
            if token=="a":
                self.assertEqual(value, 15)
            if token=='b':
                self.assertEqual(value, 10)
            if token=='c':
                self.assertEqual(value, 4)
            if token=='d':
                self.assertEqual(value, 3)
            if token==START_SENT_SYMBOL:
                self.assertEqual(value, 0)
            if token==END_SENT_SYMBOL:
                self.assertEqual(value, 3)

        bigram = probas[1]
        for token,value,bo in bigram:
            if token=="a b":
                self.assertEqual(value, 7)
            if token=="b a":
                self.assertEqual(value, 4)
            if token==START_SENT_SYMBOL+' a':
                self.assertEqual(value, 3)
            if token=='b '+END_SENT_SYMBOL:
                self.assertEqual(value, 3)

        probas = model.probabilities( method="lograw" )
        self.assertEqual(len(probas), 2)

        unigram = probas[0]
        for token,value,bo in unigram:
            if token=="a":
                self.assertEqual(value, math.log(15, 10))
            if token=='b':
                self.assertEqual(value, math.log(10, 10))
            if token=='c':
                self.assertEqual(value, math.log(4, 10))
            if token=='d':
                self.assertEqual(value, math.log(3, 10))
            if token==START_SENT_SYMBOL:
                self.assertEqual(value, -99)
            if token==END_SENT_SYMBOL:
                self.assertEqual(value, math.log(3, 10))

        bigram = probas[1]
        for token,value,bo in bigram:
            if token=="a b":
                self.assertEqual(value, math.log(7, 10))
            if token=="b a":
                self.assertEqual(value, math.log(4, 10))
            if token==START_SENT_SYMBOL+' a':
                self.assertEqual(value, math.log(3, 10))
            if token=='b '+END_SENT_SYMBOL:
                self.assertEqual(value, math.log(3, 10))


    def testMaximumLikelihoodProbabilities(self):
        model = NgramsModel(3)
        model.count( self.corpusfile )
        probas = model.probabilities( method="ml" )
        self.assertEqual(len(probas), 3)

        unigram = probas[0]
        for token,value,bo in unigram:
            if token=="a":
                self.assertEqual(round(value,6), 0.428571)
            if token=="b":
                self.assertEqual(round(value,6), 0.285714)
            if token=="c":
                self.assertEqual(round(value,6), 0.114286)
            if token=="d":
                self.assertEqual(round(value,6), 0.085714)
            if token==START_SENT_SYMBOL:
                self.assertEqual(round(value,6), 0.)
            if token==END_SENT_SYMBOL:
                self.assertEqual(round(value,6), 0.085714)

        bigram = probas[1]
        for token,value,bo in bigram:
            if token=="a b":
                self.assertEqual(round(value,6), 0.466667)
            if token=="b a":
                self.assertEqual(round(value,6), 0.400000)

        trigram = probas[2]
        for token,value,bo in trigram:
            if token=="a b a":
                self.assertEqual(round(value,6), 0.142857)
            if token==START_SENT_SYMBOL+"a a":
                self.assertEqual(round(value,6), 0.500000)
            if token=="a b"+END_SENT_SYMBOL:
                self.assertEqual(round(value,6), 0.428571)

        probas = model.probabilities( method="logml" )
        self.assertEqual(len(probas), 3)

        unigram = probas[0]
        for token,value,bo in unigram:
            if token=="a":
                self.assertEqual(round(value,6), round(math.log(0.42857143,10),6))
            if token=="b":
                self.assertEqual(round(value,6), round(math.log(0.28571429,10),6))
            if token=="c":
                self.assertEqual(round(value,6), round(math.log(0.11428571,10),6))
            if token=="d":
                self.assertEqual(round(value,6), round(math.log(0.08571429,10),6))
            if token==START_SENT_SYMBOL:
                self.assertEqual(round(value,6), -99.000000)
            if token==END_SENT_SYMBOL:
                self.assertEqual(round(value,6), round(math.log(0.08571429,10),6))

        bigram = probas[1]
        for token,value,bo in bigram:
            if token=="a b":
                self.assertEqual(round(value,6), round(math.log(0.466667,10),6))
            if token=="b a":
                self.assertEqual(round(value,6), round(math.log(0.400000,10),6))

        trigram = probas[2]
        for token,value,bo in trigram:
            if token=="a b a":
                self.assertEqual(round(value,6), round(math.log(0.142857,10),6))
            if token==START_SENT_SYMBOL+"a a":
                self.assertEqual(round(value,6), round(math.log(0.500000,10),6))
            if token=="a b"+END_SENT_SYMBOL:
                self.assertEqual(round(value,6), round(math.log(0.428571,10),6))

# End TestNgramsModel
# ---------------------------------------------------------------------------
