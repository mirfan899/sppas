# -*- coding:utf-8 -*-

import unittest

from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.ptime.point import TimePoint
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.utils.tierutils import TierConverter

from ..kappa import Kappa

# ---------------------------------------------------------------------------


class TestVectorKappa(unittest.TestCase):

    def setUp(self):
        self.p = [(1.0, 0.0), (0.0, 1.0), (0.0, 1.0), (1.0, 0.0), (1.0, 0.0)]
        self.q = [(1.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 0.0), (1.0, 0.0)]

    def test_kappa(self):
        kappa = Kappa(self.p, self.q)
        self.assertTrue(kappa.check())  # check both p and q
        self.assertFalse(kappa.check_vector([(0., 1.), (0., 1., 0.)]))
        self.assertFalse(kappa.check_vector([(0.0, 0.1)]))
        v = kappa.evaluate()
        self.assertEqual(0.54545, round(v, 5))

    def test_kappa3(self):
        p = [(1., 0., 0.), (0., 0., 1.), (0., 1., 0.), (1., 0., 0.), (0., 0., 1.)]
        q = [(0., 0., 1.), (0., 0., 1.), (1., 0., 0.), (0., 1., 0.), (0., 0., 1.)]
        kappa = Kappa(p, q)
        v = kappa.evaluate()
        self.assertEqual(0.0625, round(v, 5))

# ---------------------------------------------------------------------------
#
#
# class TestTierKappa(unittest.TestCase):
#
#     def setUp(self):
#         self.x = Annotation(TimeInterval(TimePoint(1,0.),   TimePoint(2,0.01)),    Label('toto'))
#         self.y = Annotation(TimeInterval(TimePoint(3,0.01), TimePoint(4, 0.01 )),  Label('titi'))
#         self.a = Annotation(TimeInterval(TimePoint(5,0.01), TimePoint(6.5,0.005)), Label('toto'))
#         self.b = Annotation(TimeInterval(TimePoint(6.5,0.005), TimePoint(9.5,0.)), Label('toto'))
#         self.tier = Tier()
#         self.tier.Append(self.x)
#         self.tier.Append(self.y)
#         self.tier.Append(self.a)
#         self.tier.Append(self.b)
#
#     def testLabelValue(self):
#         d = TierConverter( self.tier )
#         items1 = d.tier_to_items( )
#         items2 = d.tier_to_items( )  # ... !!! with same tier, expect kappa=1
#         items = sorted(list(set(items1+items2)))
#
#         p = d.labels_to_vector( items )
#         q = d.labels_to_vector( items )
#
#         k = Kappa(p, q)
#         self.assertTrue(k.check_vector(p))
#         self.assertTrue(k.check_vector(q))
#         self.assertTrue(k.check())  # check both p and q
#         self.assertEqual(k.evaluate(), 1.)
#
#     def testBoundValue(self):
#         d = TierConverter( self.tier )
#         p, q = d.bounds_to_vector( self.tier )
#
#         k = Kappa(p, q)
#         self.assertTrue(k.check_vector(p))
#         self.assertTrue(k.check_vector(q))
#         self.assertTrue(k.check())  # check both p and q
#         self.assertEqual(k.evaluate(), 1.)
#
#         othertier = Tier()
#         othertier.Append(self.x)
#         othertier.Append(self.y)
#         othertier.Append(self.b)
#         p, q = d.bounds_to_vector( othertier )
#
#         kb = Kappa(p, q)
#         self.assertTrue(kb.check_vector(p))
#         self.assertTrue(kb.check_vector(q))
#         self.assertTrue(kb.check())  # check both p and q
#         self.assertEqual(kb.evaluate(), 0.)
