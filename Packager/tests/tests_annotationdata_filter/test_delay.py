#!/usr/bin/env python2
# vim: set fileencoding=UTF-8 ts=4 sw=4 expandtab:

import unittest
import os
import sys
from os.path import *
import random

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.filter.delay_relations import Delay
#import annotationdata.filter.delay_relations as delay_relations

# some import to build intervals/Annotation
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.label.label import Label
from annotationdata.annotation import Annotation


class TestDelay(unittest.TestCase):
    """ Test Delay class
    """

    #------------------------------------------------------------------------------------------
    # an optional random.sample method
    def _random_sample(self, list_, sample, testall=None):
        if testall is None: # testall=None => use self._testall, but testall=False => avoid exhaustive test
            testall = self._testall
        if testall or sample > len(list_):   # the full list
            return list_;
        else:
            return random.sample(list_, sample)

    #------------------------------------------------------------------------------------------
    def setUp(self):
        pass

    #------------------------------------------------------------------------------------------
    def test__newSelf(self):
        """
        Test _newSelf() method : creation of an object of the same class
        """
        # a child class
        class DChild(Delay):
            pass

        d1 = Delay(4.5, .3)
        c1 = DChild(25.2, .5)
        # d1 <op> c1 return a Delay
        d1_mul_c1 = d1 * c1
        t_d1_mul_c1 = type(d1_mul_c1)
        self.assertEqual(t_d1_mul_c1, type(d1))
        self.assertNotEqual(t_d1_mul_c1, type(c1))
        # c1 <op> d1 return a DChild
        c1_mul_d1 = c1 * d1
        t_c1_mul_d1 = type(c1_mul_d1)
        self.assertEqual(t_c1_mul_d1, type(c1))
        self.assertNotEqual(t_c1_mul_d1, type(d1))
        self.assertEqual(c1_mul_d1, d1_mul_c1)  # d1 * c1 == c1 * d1

        # c1 <op> float return a DChild
        c1_mul_1f = c1 * 1.
        t_c1_mul_1f = type(c1_mul_1f)
        self.assertEqual(t_c1_mul_d1, type(c1))
        self.assertNotEqual(t_c1_mul_d1, type(d1))
        self.assertEqual(c1_mul_1f, c1)  # c1 * 1. == c1
        self.assertIs(c1_mul_1f, c1)  # c1 * d1 is c1
        
        
        # another child class with a one parameter init
        class DOtherChild(Delay):
            def __init__(self, value):
                Delay.__init__(self, value, 0.2)    # fixed margin

        oc1 = DOtherChild(25.2)
        # oc1 <op> d1 return a Delay (as we can't build a DOtherChild(value, margin))
        #TODO: fix it in class Delay, i.e. use a (shalow) copy
        oc1_mul_d1 = oc1 * d1
        t_oc1_mul_d1 = type(oc1_mul_d1)
        self.assertEqual(t_oc1_mul_d1, type(d1))
        self.assertNotEqual(t_oc1_mul_d1, type(oc1))

        # a grandson class
        class DGrandson(DChild):
            def __init__(self, value, margin=None, name="Jo"):
                DChild.__init__(self, value, margin)    # fixed margin
                DChild.name=name

        gs1 = DGrandson(25.2, .4, "toto")
        # gs1 <op> d1 return a DGrandson (as we can build a DGrandson(value, margin))
        gs1_mul_d1 = gs1 * d1
        t_gs1_mul_d1 = type(gs1_mul_d1)
        self.assertEqual(t_gs1_mul_d1, type(gs1))
        self.assertNotEqual(t_gs1_mul_d1, type(d1))

# End TestDelay
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDelay)
    unittest.TextTestRunner(verbosity=2).run(suite)

