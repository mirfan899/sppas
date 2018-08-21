# -*- coding:utf-8 -*-

import unittest
import random

from ..filter.delay_relations import Delay
from ..filter.delay_relations import IntervalsDelay
from ..filter.delay_relations import AndPredicates, OrPredicates

from ..ptime.point import TimePoint
from ..ptime.interval import TimeInterval
from ..label.label import Label
from ..annotation import Annotation

# ---------------------------------------------------------------------------


class TestDelay(unittest.TestCase):

    # an optional random.sample method
    def _random_sample(self, list_, sample, testall=None):
        if testall is None:  # testall=None => use self._testall, but testall=False => avoid exhaustive test
            testall = self._testall
        if testall or sample > len(list_):   # the full list
            return list_
        else:
            return random.sample(list_, sample)

    def setUp(self):
        pass

    def test_newSelf(self):
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

# ---------------------------------------------------------------------------


class TestIntervalsDelay(unittest.TestCase):
    """Test delays between 2 intervals/annotation."""

    # some usefull values
    PERCENTs = {'start': 0, 'end': 1, 'middle': 0.5, '25%': 0.25, '75%': 0.75, '50%': 50. / 100, '100%': 1.}
    PERCENTsORDER = ('start', '25%', 'middle', '75%', 'end')
    PERCENTsSAME = [('middle', '50%'), ('end', '100%')]
    MINs = {'2': 2, '0': 0, '-infinity': None, '-2': -2, '1': 1, 'one': 1}
    MINsORDER = ('-infinity', '-2', '0', '1', '2')
    MINsSAME = [('1', 'one')]
    MAXs = {'2': 2, '0': 0, '+infinity': None, '-2': -2, 'two': 2}
    MAXsORDER = ('-2', '0', '2', '+infinity')
    MAXsSAME = [('2', 'two')]
    TIMEPOINTS = range(0, 10)

    # ------------------------------------------------------------------------------------------

    def validMinMaxDelay(cls, mindelay, maxdelay):
        """
        Check if the min/max is a valid combination,
         i.e. min <= max, considering None as -/+infinity
        """
        if mindelay is None:  # -infinity
            return maxdelay is not None;  # every value execept None
        if maxdelay is None:  # +infinity
            return mindelay is not None;  # every value execept None
        return mindelay <= maxdelay  # min < max

    # ------------------------------------------------------------------------------------------
    # an optional random.sample method

    def _random_sample(self, list_, sample, testall=None):
        if testall is None:  # testall=None => use self._testall, but testall=False => avoid exhaustive test
            testall = self._testall
        if testall or sample > len(list_):  # the full list
            return list_;
        else:
            return random.sample(list_, sample)

    # ------------------------------------------------------------------------------------------

    def setUp(self):
        self._testall = False  # run very exhaustive tests, only if you have many time (various hours), the random selection is enough (~6s)
        # Delay._NUMERIC = 'Decimal'  # change Delay numeric value
        self.p1 = TimePoint(1)
        self.p2 = TimePoint(2)
        self.p3 = TimePoint(3)
        self.it = TimeInterval(self.p1, self.p2)
        self.annotationI = Annotation(self.it, Label(" \t\t  être être   être  \n "))
        self.annotationP = Annotation(self.p1, Label("mark"))
        # Create some IntervalsDelay
        self.intervalsDelays = {}
        for xk, xpercent in self.PERCENTs.items():
            for yk, ypercent in self.PERCENTs.items():
                for mk, mindelay in self.MINs.items():
                    for Mk, maxdelay in self.MAXs.items():
                        if self.validMinMaxDelay(mindelay, maxdelay):
                            self.intervalsDelays[(xk, yk, mk, Mk)] = IntervalsDelay(mindelay, maxdelay, xpercent,
                                                                                    ypercent)

    # ------------------------------------------------------------------------------------------

    def test_init(self):
        # build a start_start IntervalsDelay's in various way
        ssM1 = IntervalsDelay(0, 2, 0., 0.)
        self.assertEqual(ssM1, self.intervalsDelays[('start', 'start', '0', '2')])
        ssM2 = IntervalsDelay(mindelay=0, maxdelay=2, xpercent=0., ypercent=0.)
        self.assertEqual(ssM1, ssM2)
        ssM3 = IntervalsDelay(maxdelay=2, xpercent=0, ypercent=0)
        self.assertEqual(ssM1, ssM3)
        ssM4 = IntervalsDelay(0, 2, 0, 0)
        self.assertEqual(ssM1, ssM4)

        # build a start_end IntervalsDelay
        seM1 = IntervalsDelay(0, 2, 0, 1)
        self.assertEqual(seM1, self.intervalsDelays[('start', 'end', '0', '2')])
        self.assertGreater(seM1, ssM1)  # start_end > start_start

        # build an end_start IntervalsDelay
        esM1 = IntervalsDelay(0, 2, 1, 0)
        self.assertEqual(esM1, self.intervalsDelays[('end', 'start', '0', '2')])
        self.assertGreater(esM1, seM1)  # end_start > start_end

        # build an end_end IntervalsDelay
        eeM1 = IntervalsDelay(0, 2, 1, 1)
        self.assertEqual(eeM1, self.intervalsDelays[('end', 'end', '0', '2')])
        self.assertGreater(eeM1, esM1)  # end_end > end_start

        # build some middle_middle IntervalsDelay (default values of xpercent/ypercent)
        mmM1 = IntervalsDelay(0, 2)
        self.assertEqual(mmM1, self.intervalsDelays[('middle', 'middle', '0', '2')])
        mmM2 = IntervalsDelay(maxdelay=2)
        self.assertEqual(mmM1, mmM2)
        self.assertGreater(mmM1, seM1)  # middle_middle > start_end > start_start
        self.assertLess(mmM1, esM1)  # middle_middle < end_start < end_end

        # build some percent_percent IntervalsDelay
        ppM1 = IntervalsDelay(0, 2, 0.25, 0.75)
        self.assertEqual(ppM1, self.intervalsDelays[('25%', '75%', '0', '2')])
        ppM2 = IntervalsDelay(mindelay=0, maxdelay=2, xpercent=0.25,
                              ypercent=75. / 100)  # /!\ 75/100=0 or 1 (int), 75./100 = 0.75
        self.assertEqual(ppM1, ppM2)

        # raise ValueError on invalid min/max delay
        for mk, mindelay in self.MINs.items():
            for Mk, maxdelay in self.MAXs.items():
                if not self.validMinMaxDelay(mindelay, maxdelay):  # use invald pairs
                    for xk, xpercent in self.PERCENTs.items():
                        for yk, ypercent in self.PERCENTs.items():
                            with self.assertRaises(ValueError):
                                IntervalsDelay(mindelay, maxdelay, xpercent, ypercent)

    # ------------------------------------------------------------------------------------------

    def test_cmp(self):
        # Compare the IntervalsDelay with same mindelay (but different keys)
        checked = 0
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk1, mk2 in self.MINsSAME:
                    for Mk in self.MAXs.keys():
                        if self.validMinMaxDelay(self.MINs[mk1], self.MAXs[Mk]):
                            id1 = self.intervalsDelays[(xk, yk, mk1, Mk)]
                            id2 = self.intervalsDelays[(xk, yk, mk2, Mk)]
                            self.assertEqual(id1, id2,
                                             "NOT {} == {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
                            checked += 1
        self.assertGreater(checked, 0, "Any checks for same mindelay")
        # Compare the IntervalsDelay with same maxdelay (but different keys)
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    for Mk1, Mk2 in self.MAXsSAME:
                        if self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk1]):
                            id1 = self.intervalsDelays[(xk, yk, mk, Mk1)]
                            id2 = self.intervalsDelays[(xk, yk, mk, Mk2)]
                            self.assertEqual(id1, id2,
                                             "NOT {} == {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
        # Compare the IntervalsDelay with same xpercent (but different keys)
        for xk1, xk2 in self.PERCENTsSAME:
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    for Mk in self.MAXs.keys():
                        if self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk]):
                            id1 = self.intervalsDelays[(xk1, yk, mk, Mk)]
                            id2 = self.intervalsDelays[(xk2, yk, mk, Mk)]
                            self.assertEqual(id1, id2,
                                             "NOT {} == {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
        # Compare the IntervalsDelay with same ypercent (but different keys)
        for xk in self.PERCENTs.keys():
            for yk1, yk2 in self.PERCENTsSAME:
                for mk in self.MINs.keys():
                    for Mk in self.MAXs.keys():
                        if self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk]):
                            id1 = self.intervalsDelays[(xk, yk1, mk, Mk)]
                            id2 = self.intervalsDelays[(xk, yk2, mk, Mk)]
                            self.assertEqual(id1, id2,
                                             "NOT {} == {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))

        # Check the order based on xpercent
        for i in range(1, len(self.PERCENTsORDER)):
            xk1, xk2 = self.PERCENTsORDER[i - 1:i + 1]
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    for Mk in self.MAXs.keys():
                        if self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk]):
                            id1 = self.intervalsDelays[(xk1, yk, mk, Mk)]
                            id2 = self.intervalsDelays[(xk2, yk, mk, Mk)]
                            self.assertLess(id1, id2,
                                            "NOT {} < {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
        # Check the order based on ypercent
        for xk in self.PERCENTs.keys():
            for i in range(1, len(self.PERCENTsORDER)):
                yk1, yk2 = self.PERCENTsORDER[i - 1:i + 1]
                for mk in self.MINs.keys():
                    for Mk in self.MAXs.keys():
                        if self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk]):
                            id1 = self.intervalsDelays[(xk, yk1, mk, Mk)]
                            id2 = self.intervalsDelays[(xk, yk2, mk, Mk)]
                            self.assertLess(id1, id2,
                                            "NOT {} < {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
        # Check the order based on mindelay
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for i in range(1, len(self.MINsORDER)):
                    mk1, mk2 = self.MINsORDER[i - 1:i + 1];
                    for Mk in self.MAXs.keys():
                        try:
                            id1 = self.intervalsDelays[(xk, yk, mk1, Mk)]
                            id2 = self.intervalsDelays[(xk, yk, mk2, Mk)]
                            self.assertLess(id1, id2,
                                            "NOT {} < {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
                        except KeyError:
                            self.assertFalse(self.validMinMaxDelay(self.MINs[mk1], self.MAXs[Mk])
                                             and self.validMinMaxDelay(self.MINs[mk2], self.MAXs[Mk])
                                             )
        # Check the order based on maxdelay
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    for i in range(1, len(self.MAXsORDER)):
                        Mk1, Mk2 = self.MAXsORDER[i - 1:i + 1];
                        try:
                            id1 = self.intervalsDelays[(xk, yk, mk, Mk1)]
                            id2 = self.intervalsDelays[(xk, yk, mk, Mk2)]
                            self.assertLess(id1, id2,
                                            "NOT {} < {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
                        except KeyError:  # some invalid min/max combination, like max<min OR -infinity/+infinity
                            self.assertFalse(self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk1])
                                             and self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk2])
                                             )

    # ------------------------------------------------------------------------------------------

    def test_create(self):
        # some easy case
        ssM1 = IntervalsDelay.create('start_start_max', 2)
        ssM2 = IntervalsDelay.create(start_start_max=2)
        self.assertEquals(ssM1, ssM2)
        self.assertEquals(ssM1, self.intervalsDelays[('start', 'start', '0', '2')])

        # create with a couple of min/max values,
        # i.e create(<xpt>_<ypt>, (min, max)), create(<xpt>_<ypt>=(min, max)), etc.
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    mink = self.MINs[mk];
                    for Mk in self.MAXs.keys():
                        Maxk = self.MAXs[Mk];
                        if self.validMinMaxDelay(mink, Maxk):
                            # (a) create(<xpt>_<ypt>, (min, max))
                            id1 = IntervalsDelay.create("{}_{}".format(xk, yk), (mink, Maxk))
                            id2 = self.intervalsDelays[(xk, yk, mk, Mk)]
                            self.assertEqual(id1, id2
                                             ,
                                             "[{xk},{yk},{mk},{Mk}] (a) create('{xk}_{yk}', ({mink},{Maxk})) NOT {id1} == {id2}".format(
                                                 **locals())
                                             )
                            # (b) create(<xpt>_<ypt>=(min, max))
                            kwargs = {"{}_{}".format(xk, yk): (mink, Maxk)}
                            id1 = IntervalsDelay.create(**kwargs)
                            self.assertEqual(id1, id2
                                             , "[{xk},{yk},{mk},{Mk}] (b) create({kwargs}) NOT {id1} == {id2}".format(
                                    **locals())
                                             )
                            # (c) create(<xpt>_<ypt>, {mindelay=min, maxdelay=max})
                            v = {'mindelay': mink, 'maxdelay': Maxk}
                            id1 = IntervalsDelay.create("{}_{}".format(xk, yk), v)
                            self.assertEqual(id1, id2
                                             ,
                                             "[{xk},{yk},{mk},{Mk}] (c) create('{xk}_{yk}',{v}) NOT {id1} == {id2}".format(
                                                 **locals())
                                             )
                            # (d) create('and', <xpt>_<ypt>, (min, max))
                            id1 = IntervalsDelay.create('and', "{}_{}".format(xk, yk), (mink, Maxk))
                            self.assertEqual(id1, id2
                                             ,
                                             "[{xk},{yk},{mk},{Mk}] (d) create('and', '{xk}_{yk}', ({mink},{Maxk})) NOT {id1} == {id2}".format(
                                                 **locals())
                                             )
                            # (e) create('or', <xpt>_<ypt>, (min, max))
                            id1 = IntervalsDelay.create('or', "{}_{}".format(xk, yk), (mink, Maxk))
                            self.assertEqual(id1, id2
                                             ,
                                             "[{xk},{yk},{mk},{Mk}] (e) create('or', '{xk}_{yk}', ({mink},{Maxk})) NOT {id1} == {id2}".format(
                                                 **locals())
                                             )
                            # (f) create('join', 'or', <xpt>_<ypt>, (min, max))
                            id1 = IntervalsDelay.create('join', 'or', "{}_{}".format(xk, yk), (mink, Maxk))
                            self.assertEqual(id1, id2
                                             ,
                                             "[{xk},{yk},{mk},{Mk}] (f) create('join','or', '{xk}_{yk}', ({mink},{Maxk})) NOT {id1} == {id2}".format(
                                                 **locals())
                                             )

        # create with min==max values, i.e create(<xpt>_<ypt>_eq, min), create(<xpt>_<ypt>=(min, min)), etc.
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    mink = self.MINs[mk];
                    if mink is None: continue;  # skip -infinity/+infinity
                    for Mk in self.MAXs.keys():
                        Maxk = self.MAXs[Mk];
                        if Maxk != mink: continue;  # skip Max!=min
                        # (a) create(<xpt>_<ypt>_eq, min)
                        id1 = IntervalsDelay.create("{}_{}_eq".format(xk, yk), mink)
                        id2 = self.intervalsDelays[(xk, yk, mk, Mk)]
                        self.assertEqual(id1, id2
                                         ,
                                         "[{xk},{yk},{mk},{Mk}] (a) create('{xk}_{yk}_eq', {mink}) NOT {id1} == {id2}".format(
                                             **locals())
                                         )
                        # (b) create(<xpt>_<ypt>_eq, {delay=min})
                        v = {'delay': mink}
                        id1 = IntervalsDelay.create("{}_{}_eq".format(xk, yk), v)
                        self.assertEqual(id1, id2
                                         ,
                                         "[{xk},{yk},{mk},{Mk}] (b) create('{xk}_{yk}_eq', {v}) NOT {id1} == {id2}".format(
                                             **locals())
                                         )
                        # (c) create(<xpt>_<ypt>_eq=min)
                        kwargs = {"{}_{}_eq".format(xk, yk): mink}
                        id1 = IntervalsDelay.create(**kwargs)
                        self.assertEqual(id1, id2
                                         , "[{xk},{yk},{mk},{Mk}] (c) create({kwargs}) NOT {id1} == {id2}".format(
                                **locals())
                                         )
                        # (d) create(<xpt>_<ypt>_eq={delay=min})
                        kwargs = {"{}_{}_eq".format(xk, yk): {'delay': mink}}
                        id1 = IntervalsDelay.create(**kwargs)
                        self.assertEqual(id1, id2
                                         , "[{xk},{yk},{mk},{Mk}] (d) create({kwargs}) NOT {id1} == {id2}".format(
                                **locals())
                                         )
                        # (e) create(%_%, {xpercent, ypercent, delay})
                        v = {'xpercent': self.PERCENTs[xk], 'ypercent': self.PERCENTs[yk], 'delay': mink}
                        id1 = IntervalsDelay.create('%_%_eq', v)
                        self.assertEqual(id1, id2
                                         , "[{xk},{yk},{mk},{Mk}] (e) create('%_%', {v}) NOT {id1} == {id2}".format(
                                **locals())
                                         )
                        # (f) create(<xpt>_<ypt>, min) ('eq' is the default relation)
                        id1 = IntervalsDelay.create("{}_{}".format(xk, yk), mink)
                        self.assertEqual(id1, id2
                                         ,
                                         "[{xk},{yk},{mk},{Mk}] (c) create('{xk}_{yk}', {mink}) NOT {id1} == {id2}".format(
                                             **locals())
                                         )
                        # (g) create(%_%, {xpercent, ypercent, delay}) ('eq' is the default relation)
                        v = {'xpercent': self.PERCENTs[xk], 'ypercent': self.PERCENTs[yk], 'delay': Maxk}
                        id1 = IntervalsDelay.create('%_%', v)
                        self.assertEqual(id1, id2
                                         , "[{xk},{yk},{mk},{Mk}] (d) create('%_%', {v}) NOT {id1} == {id2}".format(
                                **locals())
                                         )
        # create with min values, i.e create(<xpt>_<ypt>_min, min) => Max = (min>=0 ? +infinity : 0)
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    mink = self.MINs[mk];
                    Mk = '0' if (mink is None or mink < 0) else '+infinity'  # Max = (min>=0 ? +infinity : 0)
                    Maxk = self.MAXs[Mk];
                    # (a) create(<xpt>_<ypt>_min, min)
                    id1 = IntervalsDelay.create("{}_{}_min".format(xk, yk), mink)
                    id2 = self.intervalsDelays[(xk, yk, mk, Mk)]
                    self.assertEqual(id1, id2
                                     ,
                                     "[{xk},{yk},{mk},{Mk}] (a) create('{xk}_{yk}_min', {mink}) NOT {id1} == {id2}".format(
                                         **locals())
                                     )
                    # (b) create(<xpt>_<ypt>_min=min)
                    kwargs = {"{}_{}_min".format(xk, yk): mink}
                    id1 = IntervalsDelay.create(**kwargs)
                    self.assertEqual(id1, id2
                                     ,
                                     "[{xk},{yk},{mk},{Mk}] (b) create({kwargs}) NOT {id1} == {id2}".format(**locals())
                                     )
                    # (c) create(%_%_min, {xpercent, ypercent, mindelay})
                    v = {'xpercent': self.PERCENTs[xk], 'ypercent': self.PERCENTs[yk], 'mindelay': mink}
                    id1 = IntervalsDelay.create('%_%_min', v)
                    self.assertEqual(id1, id2
                                     , "[{xk},{yk},{mk},{Mk}] (b) create('%_%_min', {v}) NOT {id1} == {id2}".format(
                            **locals())
                                     )
        # create with Max values, i.e create(<xpt>_<ypt>_max, Max) => min = (Max>=0 ? 0 : -infinity)
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for Mk in self.MAXs.keys():
                    Maxk = self.MAXs[Mk];
                    mk = '0' if (Maxk is None or Maxk >= 0) else '-infinity'  # min = (Max>=0 ? 0 : -infinity)
                    mink = self.MINs[mk];
                    # (a) create(<xpt>_<ypt>_max, max)
                    id1 = IntervalsDelay.create("{}_{}_max".format(xk, yk), Maxk)
                    id2 = self.intervalsDelays[(xk, yk, mk, Mk)]
                    self.assertEqual(id1, id2
                                     ,
                                     "[{xk},{yk},{mk},{Mk}] (a) create('{xk}_{yk}_max', {Maxk}) NOT {id1} == {id2}".format(
                                         **locals())
                                     )
                    # (b) create(<xpt>_<ypt>_max=max)
                    kwargs = {"{}_{}_max".format(xk, yk): Maxk}
                    id1 = IntervalsDelay.create(**kwargs)
                    self.assertEqual(id1, id2
                                     ,
                                     "[{xk},{yk},{mk},{Mk}] (b) create({kwargs}) NOT {id1} == {id2}".format(**locals())
                                     )
                    # (d) create(%_%_max, {xpercent, ypercent, maxdelay})
                    v = {'xpercent': self.PERCENTs[xk], 'ypercent': self.PERCENTs[yk], 'maxdelay': Maxk}
                    id1 = IntervalsDelay.create('%_%_max', v)
                    self.assertEqual(id1, id2
                                     , "[{xk},{yk},{mk},{Mk}] (d) create('%_%_max', {v}) NOT {id1} == {id2}".format(
                            **locals())
                                     )

        # create joined IntervalsDelay
        testall = False  # if testall=False => no more sample (independant of self._testall); elif testall=None => based on self._testall
        for (xk1, yk1, mk1, Mk1) in self._random_sample(self.intervalsDelays.keys(), 10,
                                                        testall=testall):  # get only 10 random values
            min1 = self.MINs[mk1];
            Max1 = self.MAXs[Mk1];
            id1 = self.intervalsDelays[(xk1, yk1, mk1, Mk1)]
            for (xk2, yk2, mk2, Mk2) in self._random_sample(self.intervalsDelays.keys(), 10,
                                                            testall=testall):  # get only 10 random values (testall=False => never more as it's useless)

                min2 = self.MINs[mk2];
                Max2 = self.MAXs[Mk2];
                id2 = self.intervalsDelays[(xk2, yk2, mk2, Mk2)]
                idAnd = AndPredicates(id1, id2)
                # (a) implicit AND
                cargs = ("{}_{}".format(xk1, yk1), (min1, Max1), "{}_{}".format(xk2, yk2), (min2, Max2));
                ckwargs = {};
                idc = IntervalsDelay.create(*cargs, **ckwargs);
                self.assertEqual(idc, idAnd
                                 ,
                                 "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (a) create({cargs},{ckwargs}) NOT {idc} == {idAnd}".format(
                                     **locals())
                                 )
                # (b) explicit AND : create("and", ...)
                cargs = ("AND", "{}_{}".format(xk1, yk1), (min1, Max1))  # mixing args and kwargs
                ckwargs = {"{}_{}".format(xk2, yk2): (min2, Max2)};
                idc = IntervalsDelay.create(*cargs, **ckwargs);
                self.assertEqual(idc, idAnd
                                 ,
                                 "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (b) create({cargs},{ckwargs}) NOT {idc} == {idAnd}".format(
                                     **locals())
                                 )
                # (c) explicit AND with 'join' : create(..., join="and", ...)
                cargs = ("{}_{}".format(xk1, yk1), (min1, Max1))  # mixing args and kwargs
                ckwargs = {'join': "AND", "{}_{}".format(xk2, yk2): (min2, Max2)};
                idc = IntervalsDelay.create(*cargs, **ckwargs);
                self.assertEqual(idc, idAnd
                                 ,
                                 "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (c) create({cargs},{ckwargs}) NOT {idc} == {idAnd}".format(
                                     **locals())
                                 )
                # (d) explicit AND with 'join' : create(..., join="and", ...)
                cargs = ("{}_{}".format(xk1, yk1), (min1, Max1), "{}_{}".format(xk2, yk2), (min2, Max2))
                ckwargs = {'join': "AND"};
                idc = IntervalsDelay.create(*cargs, **ckwargs);
                self.assertEqual(idc, idAnd
                                 ,
                                 "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (d) create({cargs},{ckwargs}) NOT {idc} == {idAnd}".format(
                                     **locals())
                                 )
                # (e) (explicit) OR (as 1st parameter)
                idOr = OrPredicates(id1, id2)
                cargs = ("or", "{}_{}".format(xk1, yk1), (min1, Max1), "{}_{}".format(xk2, yk2), (min2, Max2))
                ckwargs = {};
                try:
                    idc = IntervalsDelay.create(*cargs, **ckwargs);
                    self.assertEqual(idc, idOr
                                     ,
                                     "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (e) create({cargs},{ckwargs}) NOT {idc} == {idOr}".format(
                                         **locals())
                                     )
                except:
                    e = sys.exc_info()[0]
                    print(
                    "Error with [{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] create({cargs},{ckwargs}) : {e}".format(
                        **locals()))
                # (f) (explicit) OR with 'join' key
                cargs = ("join", "Or", "{}_{}".format(xk1, yk1), (min1, Max1), "{}_{}".format(xk2, yk2), (min2, Max2))
                ckwargs = {};
                try:
                    idc = IntervalsDelay.create(*cargs, **ckwargs);
                    self.assertEqual(idc, idOr
                                     ,
                                     "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (f) create({cargs},{ckwargs}) NOT {idc} == {idOr}".format(
                                         **locals())
                                     )
                except:
                    e = sys.exc_info()[0]
                    print(
                    "Error with [{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] create({cargs},{ckwargs}) : {e}".format(
                        **locals()))
                # (g) (explicit) OR in kwargs
                cargs = ("{}_{}".format(xk1, yk1), (min1, Max1), "{}_{}".format(xk2, yk2), (min2, Max2))
                ckwargs = {'join': 'OR'};
                try:
                    idc = IntervalsDelay.create(*cargs, **ckwargs);
                    self.assertEqual(idc, idOr
                                     ,
                                     "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (g) create({cargs},{ckwargs}) NOT {idc} == {idOr}".format(
                                         **locals())
                                     )
                except:
                    e = sys.exc_info()[0]
                    print(
                    "Error with [{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] create({cargs},{ckwargs}) : {e}".format(
                        **locals()))
                # (h) Using kwargs for id1 AND id2 /!\ order can change
                # import traceback
                if (xk1, yk1) != (xk2,
                                  yk2):  # (!) if (xk1, yk1) == (xk2, yk2), the "{}_{}" keys have the same value => the first is ignored
                    idOrReverse = OrPredicates(id2, id1)
                    cargs = ("OR",)  # /!\ the comma is important, else cargs=("OR") <=> cargs="OR"
                    ckwargs = {"{}_{}".format(xk1, yk1): (min1, Max1),
                               "{}_{}".format(xk2, yk2): (min2, Max2)};  # /!\ not sur of the resulting order
                    try:
                        idc = IntervalsDelay.create(*cargs, **ckwargs);
                        # print("With [{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}]\n\tidc={idc}\n\tidOr={idOr}\n\tidOrReverse={idOrReverse}".format(**locals()))
                        self.assertTrue((idc == idOr) or (idc == idOrReverse)
                                        ,
                                        "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (h) create({cargs},{ckwargs}) NOT {idc} == {idOr} (or {idOrReverse})".format(
                                            **locals())
                                        )
                    except:
                        e = sys.exc_info()[0]
                        print(
                        "Error with [{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] create({cargs},{ckwargs}) : {e}'".format(
                            **locals()))
                        # traceback.print_exception(*sys.exc_info())

    # -----------------------------------------------------------------

    def test_call(self):
        # Create some TimePoint, TimeInterval and Annotation
        # - create the TimePoints:  self.timePoints[i] = TimePoint(i) (0<=i<=9) (=> 10)
        self.timePoints = {i: TimePoint(i) for i in self.TIMEPOINTS}
        # - create the TimeInterval:  [timePoints[i], timePoints[j]] 0<=i<j<=9 (=> 45)
        self.timeIntervals = dict();
        for i in self.timePoints.keys():
            for j in self.timePoints.keys():
                if i < j:
                    self.timeIntervals[(i, j)] = TimeInterval(self.timePoints[i], self.timePoints[j])
        # - create the point annotations:
        self.pointAnnotations = {i: Annotation(self.timePoints[i], Label("point at {:.3f}s".format(i))) for i in
                                 self.timePoints.keys()}
        # - create the intervals annotations:
        self.intervalAnnotations = {
        (i, j): Annotation(self.timeIntervals[(i, j)], Label("interval [{:.3f}, {:.3f}]s".format(i, j))) for (i, j) in
        self.timeIntervals.keys()}

        # check the start_start_max predicate
        nbAsserts = 0
        for Mk in self.MAXsORDER:
            Maxd = self.MAXs[Mk]
            # if Maxd<0: continue; # TODO
            for mk in self.MINsORDER:
                mind = self.MINs[mk]
                if Maxd is None and mind is None: break;  # => invalid interval
                if mind > Maxd: break;  # mind > Maxd => invalid interval
                for xk in ['start']:
                    yk = xk;  # same reference point
                    idc = self.intervalsDelays[(xk, yk, mk, Mk)]
                    # compare 2 point annotations
                    for i in self.pointAnnotations.keys():
                        for j in self.pointAnnotations.keys():
                            pai = self.pointAnnotations[i]
                            paj = self.pointAnnotations[j]
                            pred = idc(pai, paj)
                            pred_delay = pred.delay if (hasattr(pred, 'delay')) else None
                            idc_delay = idc.delay(*IntervalsDelay.splitAnnotations(pai, paj))
                            if (j - i) > Maxd:
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({j}-{i}) > {Maxd} (pred={pred}; pred.delay={pred_delay}, idc.delay()={idc_delay:r})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
                            elif (mind is None or mind <= (j - i)):
                                self.assertTrue(pred
                                                ,
                                                "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't true when {mind} <= ({j}-{i}) < {Maxd} (pred={pred}; pred.delay={pred_delay}, idc.delay()={idc_delay:r})".format(
                                                    **locals())
                                                );
                                nbAsserts += 1
                            else:  # (j-i) < min
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({j}-{i}) < {mind} (pred={pred}; pred.delay={pred_delay}, idc.delay()={idc_delay:r})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
                    # compare a point and an interval annotations
                    testall = False  # if testall=False => no more sample (independant of self._testall); elif testall=None => based on self._testall
                    for start1 in self.pointAnnotations.keys():
                        for (start2, end2) in self._random_sample(self.intervalAnnotations.keys(), 15, testall=testall):
                            a1 = self.pointAnnotations[start1]
                            a2 = self.intervalAnnotations[(start2, end2)]
                            pred = idc(a1, a2)
                            pred_delay = pred.delay if (hasattr(pred, 'delay')) else None
                            if (start2 - start1) > Maxd:
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({start2}-{start1}) > {Maxd} (pred={pred}; pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
                            elif (mind is None or mind <= (start2 - start1)):
                                self.assertTrue(pred
                                                ,
                                                "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't true when {mind} <= ({start2}-{start1}) < {Maxd} (pred={pred}; pred.delay={pred_delay})".format(
                                                    **locals())
                                                );
                                nbAsserts += 1
                            else:  # (start2-start1) < min
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({start2}-{start1}) < {mind} (pred={pred}; pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
                    # compare 2 interval annotations
                    testall = False  # if testall=False => no more sample (independant of self._testall); elif testall=None => based on self._testall
                    for (start1, end1) in self._random_sample(self.intervalAnnotations.keys(), 15, testall=testall):
                        for (start2, end2) in self._random_sample(self.intervalAnnotations.keys(), 15, testall=testall):
                            a1 = self.intervalAnnotations[(start1, end1)]
                            a2 = self.intervalAnnotations[(start2, end2)]
                            pred = idc(a1, a2)
                            pred_delay = pred.delay if (hasattr(pred, 'delay')) else None
                            if (start2 - start1) > Maxd:
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({start2}-{start1}) > {Maxd} (pred={pred}; pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
                            elif (mind is None or mind <= (start2 - start1)):
                                self.assertTrue(pred
                                                ,
                                                "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't true when {mind} <= ({start2}-{start1}) < {Maxd} (pred={pred}; pred.delay={pred_delay})".format(
                                                    **locals())
                                                );
                                nbAsserts += 1
                            else:  # (start2-start1) < min
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({start2}-{start1}) < {mind} (pred={pred}; pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
        if nbAsserts <= 0: raise Warning("Any assertion in the test loop");

        # check the start_end predicates
        nbAsserts = 0
        testall = False  # if testall=False => no more sample (independant of self._testall); elif testall=None => based on self._testall
        for Mk in self.MAXsORDER:
            Maxd = self.MAXs[Mk]
            # if Maxd<0: continue; # TODO
            for mk in self.MINsORDER:
                mind = self.MINs[mk]
                if Maxd is None and mind is None: break;  # => invalid interval
                if mind > Maxd: break;  # mind > Maxd => invalid interval
                for (xk, yk) in [('start', 'end'), ('start', '100%')]:
                    idc = self.intervalsDelays[(xk, yk, mk, Mk)]
                    # compare 2 interval annotations
                    for (start1, end1) in self._random_sample(self.intervalAnnotations.keys(), 15, testall=testall):
                        for (start2, end2) in self._random_sample(self.intervalAnnotations.keys(), 15, testall=testall):
                            a1 = self.intervalAnnotations[(start1, end1)]
                            a2 = self.intervalAnnotations[(start2, end2)]
                            pred = idc(a1, a2)
                            pred_delay = pred.delay if (hasattr(pred, 'delay')) else None
                            delay = (end2 - start1)
                            if delay > Maxd:
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({delay} > {Maxd}) (pred={pred}; pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
                            elif (mind is None or mind <= delay):
                                self.assertTrue(pred
                                                ,
                                                "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't true when ({mind} <= {delay}) < {Maxd}) (pred={pred}; pred.delay={pred_delay})".format(
                                                    **locals())
                                                );
                                nbAsserts += 1
                            else:  # (start2-start1) < min
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({delay} < {mind}) (pred={pred}; pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
        if nbAsserts <= 0: raise Warning("Any assertion in the test loop");

        # check the end_start predicates
        nbAsserts = 0
        testall = False  # if testall=False => no more sample (independant of self._testall); elif testall=None => based on self._testall
        for Mk in self.MAXsORDER:
            Maxd = self.MAXs[Mk]
            # if Maxd<0: continue; # TODO
            for mk in self.MINsORDER:
                mind = self.MINs[mk]
                if Maxd is None and mind is None: break;  # => invalid interval
                if mind > Maxd: break;  # mind > Maxd => invalid interval
                for (xk, yk) in [('end', 'start'), ('100%', 'start')]:
                    idc = self.intervalsDelays[(xk, yk, mk, Mk)]
                    # compare 2 interval annotations
                    for (start1, end1) in self._random_sample(self.intervalAnnotations.keys(), 15, testall=testall):
                        for (start2, end2) in self._random_sample(self.intervalAnnotations.keys(), 15, testall=testall):
                            a1 = self.intervalAnnotations[(start1, end1)]
                            a2 = self.intervalAnnotations[(start2, end2)]
                            pred = idc(a1, a2)
                            pred_delay = pred.delay if (hasattr(pred, 'delay')) else None
                            delay = (start2 - end1)
                            if delay > Maxd:
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({delay} > {Maxd}) (pred={pred}; pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
                            elif (mind is None or mind <= delay):
                                self.assertTrue(pred
                                                ,
                                                "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't true when ({mind} <= {delay}) < {Maxd}) (pred={pred}; pred.delay={pred_delay})".format(
                                                    **locals())
                                                );
                                nbAsserts += 1
                            else:  # (start2-start1) < min
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({delay} < {mind}) (pred={pred}; pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
        if nbAsserts <= 0: raise Warning("Any assertion in the test loop");

        # check some percent/percent predicates
        nbAsserts = 0
        testall = False  # if testall=False => no more sample (independant of self._testall); elif testall=None => based on self._testall
        for Mk in self.MAXsORDER:
            Maxd = self.MAXs[Mk]
            # if Maxd<0: continue; # TODO
            for mk in self.MINsORDER:
                mind = self.MINs[mk]
                if Maxd is None and mind is None: break;  # => invalid interval
                if mind > Maxd: break;  # mind > Maxd => invalid interval
                for (xk, yk) in [('middle', '25%'), ('50%', '75%')]:
                    idc = self.intervalsDelays[(xk, yk, mk, Mk)]
                    # compare 2 interval annotations
                    for (start1, end1) in self._random_sample(self.intervalAnnotations.keys(), 15, testall=testall):
                        for (start2, end2) in self._random_sample(self.intervalAnnotations.keys(), 15, testall=testall):
                            a1 = self.intervalAnnotations[(start1, end1)]
                            a2 = self.intervalAnnotations[(start2, end2)]
                            pred = idc(a1, a2)
                            pred_delay = pred.delay if (hasattr(pred, 'delay')) else None
                            delay = ((start2 + self.PERCENTs[yk] * (end2 - start2))
                                     - (start1 + self.PERCENTs[xk] * (end1 - start1))
                                     )
                            if delay > Maxd:
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({delay} > {Maxd}) (pred={pred}; pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
                            elif (mind is None or mind <= delay):
                                # pred is a CheckedIntervalsDelay
                                self.assertTrue(pred
                                                ,
                                                "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't true when ({mind} <= {delay}) < {Maxd}) (pred={pred}; pred.delay={pred_delay})".format(
                                                    **locals())
                                                );
                                nbAsserts += 1
                                # pred.delay == delay
                                self.assertEqual(delay, pred.delay
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) {delay}) != pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
                            else:  # (start2-start1) < min
                                self.assertFalse(pred
                                                 ,
                                                 "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({delay} < {mind}) (pred={pred}; pred.delay={pred_delay})".format(
                                                     **locals())
                                                 );
                                nbAsserts += 1
        if nbAsserts <= 0: raise Warning("Any assertion in the test loop");

        # check some AND/OR predicate
        nbAsserts = 0
        testall = False  # if testall=False => no more sample (independant of self._testall); elif testall=None => based on self._testall
        for (xk1, yk1, mk1, Mk1) in self._random_sample(self.intervalsDelays.keys(), 10,
                                                        testall=testall):  # get only 10 random values
            min1 = self.MINs[mk1];
            Max1 = self.MAXs[Mk1];
            id1 = self.intervalsDelays[(xk1, yk1, mk1, Mk1)]
            # for (xk2, yk2, mk2, Mk2) in self._random_sample([k for k in self.intervalsDelays.keys() if (k[0], k[1])==(xk1, yk1)],10): # get only 10 random values, with same xk, yk
            for (xk2, yk2, mk2, Mk2) in self._random_sample(self.intervalsDelays.keys(), 10,
                                                            testall=testall):  # get only 10 random values
                min2 = self.MINs[mk2];
                Max2 = self.MAXs[Mk2];
                id2 = self.intervalsDelays[(xk2, yk2, mk2, Mk2)]
                idAnd = AndPredicates(id1, id2)
                idOr = OrPredicates(id1, id2)
                # compare 2 interval annotations
                for (start1, end1) in self._random_sample(self.intervalAnnotations.keys(), 10, testall=testall):
                    for (start2, end2) in self._random_sample(self.intervalAnnotations.keys(), 10, testall=testall):
                        a1 = self.intervalAnnotations[(start1, end1)]
                        a2 = self.intervalAnnotations[(start2, end2)]
                        # compute delay and value
                        # - for the first IntervalsDelay
                        delay1 = ((start2 + self.PERCENTs[yk1] * (end2 - start2))
                                  - (start1 + self.PERCENTs[xk1] * (end1 - start1))
                                  )
                        v1 = (Max1 is None or (delay1 <= Max1)) and (min1 is None or (min1 <= delay1))
                        # - for the second IntervalsDelay
                        delay2 = ((start2 + self.PERCENTs[yk2] * (end2 - start2))
                                  - (start1 + self.PERCENTs[xk2] * (end1 - start1))
                                  )
                        v2 = (Max2 is None or (delay2 <= Max2)) and (min2 is None or (min2 <= delay2))
                        # compute each predicate (for error message)
                        pred1 = id1(a1, a2);
                        pred2 = id2(a1, a2)
                        # (a) AND
                        predAnd = idAnd(a1, a2)
                        if (v1 and v2):
                            self.assertTrue(predAnd
                                            ,
                                            "AndPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) isn't true predAnd={predAnd} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(
                                                **locals())
                                            );
                            nbAsserts += 1
                            # check the AND predicate return the list of predicate
                            self.assertEqual(predAnd, [pred1, pred2]
                                             ,
                                             "AndPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) isn't equals to list of predicate predAnd={predAnd} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(
                                                 **locals())
                                             )
                        else:
                            self.assertFalse(predAnd
                                             ,
                                             "AndPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) isn't false predAnd={predAnd} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(
                                                 **locals())
                                             );
                            nbAsserts += 1
                        # (b) OR
                        predOr = idOr(a1, a2)
                        if (v1 or v2):
                            self.assertTrue(predOr
                                            ,
                                            "OrPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) isn't true predOr={predOr} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(
                                                **locals())
                                            );
                            nbAsserts += 1
                            # check the OR predicate return the 1st true value
                            if v1:
                                self.assertEqual(predOr, pred1
                                                 ,
                                                 "OrPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) string isn't equals to first true predicate predOr={predOr} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(
                                                     **locals())

                                                 )
                            else:
                                self.assertEqual(predOr, pred2
                                                 ,
                                                 "OrPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) string isn't equals to first true predicate predOr={predOr} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(
                                                     **locals())

                                                 )
                        else:
                            self.assertFalse(predOr
                                             ,
                                             "OrPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) isn't false predOr={predOr} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(
                                                 **locals())
                                             );
                            nbAsserts += 1
        if nbAsserts <= 0: raise Warning("Any assertion in the test loop");

    # -----------------------------------------------------------------------

    def test_andorOperators(self):
        nbAsserts = 0
        # combination of 2 IntervalsDelays
        testall = False  # if testall=False => no more sample (independant of self._testall); elif testall=None => based on self._testall
        for id1 in self._random_sample(self.intervalsDelays.values(), 10, testall=testall):  # get only 10 random values
            for id2 in self._random_sample(self.intervalsDelays.values(), 10,
                                           testall=testall):  # get only 10 random values
                # (a) & operator
                idAnd = AndPredicates(id1, id2)
                idAndOp = id1 & id2
                self.assertEquals(idAnd, idAndOp
                                  , "(id1 & id2)={idAndOp} isn't equals to AndPredicates(id1, id2)={idAnd}".format(
                        **locals())
                                  );
                nbAsserts += 1
                # (b) | operator
                idOr = OrPredicates(id1, id2)
                idOrOp = id1 | id2
                self.assertEquals(idOr, idOrOp
                                  , "(id1 | id2)={idOrOp} isn't equals to OrPredicates(id1, id2)={idOr}".format(
                        **locals())
                                  );
                nbAsserts += 1
                # add a 3 value
                for id3 in self._random_sample(self.intervalsDelays.values(), 10,
                                               testall=testall):  # get only 10 random values
                    # (a) & operator
                    idAnd2 = AndPredicates(idAnd, id3)
                    idAndOp2 = id1 & id2 & id3
                    self.assertEquals(idAnd2, idAndOp2
                                      ,
                                      "(id1 & id2 & id3)={idAndOp2} isn't equals to AndPredicates(AndPredicates(id1, id2), id3)={idAnd2}".format(
                                          **locals())
                                      );
                    nbAsserts += 1
                    # with IntervalDelay before
                    idAnd3 = AndPredicates(id3, idAnd)
                    idAndOp3 = id3 & (id1 & id2)
                    self.assertEquals(idAnd3, idAndOp3
                                      ,
                                      "(id3 & (id1 & id2))={idAndOp3} isn't equals to AndPredicates(id3, AndPredicates(id1, id2))={idAnd3}".format(
                                          **locals())
                                      );
                    nbAsserts += 1
                    # (b) | operator
                    idOr2 = OrPredicates(idOr, id3)
                    idOrOp2 = id1 | id2 | id3
                    self.assertEquals(idOr2, idOrOp2
                                      ,
                                      "(id1 | id2 | id3)={idOrOp2} isn't equals to OrPredicates(OrPredicates(id1, id2), id3)={idOr2}".format(
                                          **locals())
                                      );
                    nbAsserts += 1
                    # with IntervalDelay before
                    idOr3 = OrPredicates(id3, idOr)
                    idOrOp3 = id3 | (id1 | id2)
                    self.assertEquals(idOr3, idOrOp3
                                      ,
                                      "(id3 | (id1 | id2))={idOrOp3} isn't equals to OrPredicates(id3, OrPredicates(id1, id2))={idOr3}".format(
                                          **locals())
                                      );
                    nbAsserts += 1

        if nbAsserts <= 0: raise Warning("Any assertion in the test loop");

    # -----------------------------------------------------------------------

    def test_call_after(self):
        # self._testall = True    # test all case
        # Create some TimePoint, TimeInterval and Annotation
        # - create the TimePoints:  self.timePoints[i] = TimePoint(i) (0<=i<=9) (=> 10)
        self.timePoints = {i: TimePoint(i) for i in self.TIMEPOINTS}
        # - create the TimeInterval:  [timePoints[i], timePoints[j]] 0<=i<j<=9 (=> 45)
        self.timeIntervals = dict();
        for i in self.timePoints.keys():
            for j in self.timePoints.keys():
                if i < j:
                    self.timeIntervals[(i, j)] = TimeInterval(self.timePoints[i], self.timePoints[j])
        # - create the point annotations:
        self.pointAnnotations = {i: Annotation(self.timePoints[i], Label("point at {:.3f}s".format(i))) for i in
                                 self.timePoints.keys()}
        # - create the intervals annotations:
        self.intervalAnnotations = {
        (i, j): Annotation(self.timeIntervals[(i, j)], Label("interval [{:.3f}, {:.3f}]s".format(i, j))) for (i, j) in
        self.timeIntervals.keys()}

        # check some predicates
        testall = None  # if testall=False => no more sample (independant of self._testall); elif testall=None => based on self._testall
        nbAsserts = 0
        for Mk in self.MAXsORDER:
            maxdelay = self.MAXs[Mk]
            # if maxdelay<0: continue; # TODO
            for mk in self.MINsORDER:
                mindelay = self.MINs[mk]
                if maxdelay is None and mindelay is None: break;  # => invalid interval
                if mindelay > maxdelay: break;  # mindelay > maxdelay => invalid interval
                for xk in self._random_sample(self.PERCENTs.keys(), 4, testall=testall):
                    xpercent = self.PERCENTs[xk]
                    for yk in self._random_sample(self.PERCENTs.keys(), 4, testall=testall):
                        ypercent = self.PERCENTs[yk]
                        # idc = self.intervalsDelays[(xk, yk, mk, Mk)]
                        idAfter = IntervalsDelay(mindelay, maxdelay, xpercent, ypercent, direction='after')
                        # compare 2 interval annotations
                        for (start1, end1) in self._random_sample(self.intervalAnnotations.keys(), 15, testall=testall):
                            for (start2, end2) in self._random_sample(self.intervalAnnotations.keys(), 15,
                                                                      testall=testall):
                                a1 = self.intervalAnnotations[(start1, end1)]
                                a2 = self.intervalAnnotations[(start2, end2)]
                                # pred = idc(a1, a2)
                                predAfter = idAfter(a1, a2)
                                delayAfter = ((start1 + self.PERCENTs[xk] * (end1 - start1))
                                              - (start2 + self.PERCENTs[yk] * (end2 - start2))
                                              )
                                # delay = -delayAfter
                                predAfter_delay = predAfter.delay if (hasattr(predAfter, 'delay')) else None
                                if delayAfter > maxdelay:  # delayAfter > max
                                    self.assertFalse(predAfter
                                                     ,
                                                     "IntervalsDelays[{xk},{yk},{mk},{Mk},after]({a1}, {a2}) isn't false when ({delayAfter} > {maxdelay}) (predAfter={predAfter}; predAfter.delay={predAfter_delay})".format(
                                                         **locals())
                                                     );
                                    nbAsserts += 1
                                elif (mindelay is None or mindelay <= delayAfter):  # min <= delayAfter <= max
                                    # nota: predAfter is a CheckedIntervalsDelay
                                    self.assertTrue(predAfter
                                                    ,
                                                    "IntervalsDelays[{xk},{yk},{mk},{Mk},after]({a1}, {a2}) isn't true when ({mindelay} <= {delayAfter}) < {maxdelay}) (predAfter={predAfter}; predAfter.delay={predAfter_delay})".format(
                                                        **locals())
                                                    );
                                    nbAsserts += 1
                                    # predAfter.delay == delayAfter
                                    self.assertEqual(delayAfter, predAfter.delay
                                                     ,
                                                     "IntervalsDelays[{xk},{yk},{mk},{Mk},after]({a1}, {a2}) {delayAfter}) != predAfter.delay={predAfter_delay})".format(
                                                         **locals())
                                                     );
                                    nbAsserts += 1
                                else:  # delayAfter < min
                                    self.assertFalse(predAfter
                                                     ,
                                                     "IntervalsDelays[{xk},{yk},{mk},{Mk}]({a1}, {a2}) isn't false when ({delayAfter} < {mindelay}) (predAfter={predAfter}; predAfter.delay={predAfter_delay})".format(
                                                         **locals())
                                                     );
                                    nbAsserts += 1
        if nbAsserts <= 0: raise Warning("Any assertion in the test loop");

    # -----------------------------------------------------------------------

    def test_call_withMargin(self):
        # self._testall = True    # test all case
        margin = 0.3
        # Create some TimePoint and Annotation
        # - create the TimePoints:  self.timePoints[i] = TimePoint(i,margin) (0<=i<=9) (=> 10)
        self.timePoints = {i: TimePoint(i, margin) for i in self.TIMEPOINTS}
        # - create the point annotations:
        self.pointAnnotations = {i: Annotation(self.timePoints[i], Label("Point at {:.0f}s~{:.1f}".format(i, margin)))
                                 for i in self.timePoints.keys()}

        # Create some IntervalsDelay() (as we workds with point, all percents are equivalents)
        testall = False  # if testall=False => no more sample (independant of self._testall); elif testall=None => based on self._testall
        nbAsserts = 0
        for mindelay in [0, 0.5]:  # nota: 1-2*margin=0.4 < 0.5 < 2*margin=0.3
            for maxdelay in [mindelay, (mindelay + 1)]:
                ids = IntervalsDelay(mindelay=mindelay, maxdelay=maxdelay, xpercent=0., ypercent=0.)
                # compare 2 point annotations
                for p1 in self._random_sample(self.pointAnnotations.keys(), 5, testall=testall):
                    for p2 in self._random_sample(self.pointAnnotations.keys(), 5, testall=testall):
                        if (p1 > p2): (p1, p2) = (p2, p1);  # put p1,p2 in order as we consider only positive delay
                        tp1 = self.timePoints[p1]
                        tp2 = self.timePoints[p2]
                        pa1 = self.pointAnnotations[p1]
                        pa2 = self.pointAnnotations[p2]
                        pred = ids(pa1, pa2)
                        delay = p2 - p1
                        # /!\ the sum of the 2 points' margin is not always 2*margin
                        #  because TimePoint at 0. have a 0. margin (i.e TimePoint(0., margin) --> TimePoint(0., 0.))
                        #  nota: looking at TimePoint.SetRadius() TimePoint(v, margin) --> TimePoint(v, v) if (v<margin)
                        # -- tpMargins = 2*margin   # NO
                        # -- tpMargins = (margin if p1>0 else 0) + (margin if p2>0 else 0)  # correct as '0.' is our only point without margin
                        tpMargins = (margin if p1 > margin else p1) + (
                        margin if p2 > margin else p2)  # more exact, for the current version of TimePoint.SetRadius()
                        # -- tpMargins = tp1.GetRadius() + tp2.GetRadius()   # safer
                        delayLow = delay - tpMargins;
                        delayHigh = delay + tpMargins
                        pred_delay = pred.delay if (hasattr(pred, 'delay')) else None
                        ids_delay = repr(ids.delay(tp1, tp1, tp2, tp2))
                        if delayLow > maxdelay:  # delay-2*margin > max
                            self.assertFalse(pred
                                             ,
                                             "IntervalsDelays[{mindelay},{maxdelay}]({pa1}, {pa2}) isn't false when ({delayLow} > {maxdelay}) (pred={pred}; pred.delay={pred_delay})".format(
                                                 **locals())
                                             );
                            nbAsserts += 1
                        elif delayHigh < mindelay:  # delay+2*margin < min
                            self.assertFalse(pred
                                             ,
                                             "IntervalsDelays[{mindelay},{maxdelay}]({pa1}, {pa2}) isn't false when ({delayHigh} < {mindelay}) (pred={pred}; pred.delay={pred_delay})".format(
                                                 **locals())
                                             );
                            nbAsserts += 1
                        else:  # [mindelay,maxdelay] and  [delayLow,delayHigh] overlap
                            self.assertTrue(pred
                                            ,
                                            "IntervalsDelays[{mindelay},{maxdelay}]({pa1}, {pa2}) isn't true when ({mindelay} <= {delayHigh} AND {delayLow} <= {maxdelay}) (pred={pred}; pred.delay={pred_delay}; ids.delay(...)={ids_delay})".format(
                                                **locals())
                                            );
                            nbAsserts += 1
        if nbAsserts <= 0:
            raise Warning("Any assertion in the test loop")
