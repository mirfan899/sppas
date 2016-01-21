#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import unittest
import os
import sys
import getopt
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas'))

from annotations.Align.tiedlist import Tiedlist

class TestTiedlist(unittest.TestCase):

    def test_tiedlist(self):
        tiedfile = os.path.join(SPPAS, 'models', 'models-FR', 'tiedlist')
        t = Tiedlist( tiedfile )
        self.assertFalse(t.is_observed( "eu-jj+ww" ))
        self.assertFalse(t.is_observed( "eu-jj+uy" ))
        self.assertFalse(t.is_tied( "eu-jj+uy" ))
        self.assertFalse(t.is_tied( "eu-jj+ww" ))
        t.add( "ss-au+ai" )
        t.add( "ss-au+aa" )
        t.add( "sp-ff+au" )
        t.add( "ai+au" )
        t.add( "au+ai" )
        t.save("toto")

    def tearDown(self):
        os.remove('toto')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTiedlist))
    return suite

if __name__ == '__main__':
    unittest.main()
