#!/usr/bin/env python2
# vim: set fileencoding=UTF-8 ts=4 sw=4 expandtab:

import unittest
import os
import sys
from os.path import *

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

from annotationdata.filter.delay_relations import IntervalsDelay, Delay
#import annotationdata.filter.delay_relations as delay_relations

# some import to build intervals/Annotation
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.label.label import Label
from annotationdata.annotation import Annotation


class TestIntervalsDelay(unittest.TestCase):
    """ Test delays between 2 intervals/annotation
    """

    # some usefull values
    PERCENTs={'start':0, 'end':1, 'middle':0.5, '25%':0.25, '75%':0.75, '50%':50./100, '100%':1.}
    PERCENTsORDER=('start', '25%', 'middle', '75%', 'end')
    PERCENTsSAME=[('middle', '50%'), ('end', '100%')]
    MINs={'2':2, '0':0, '-infinity':None, '-2':-2, '1':1, 'one':1}
    MINsORDER=('-infinity', '-2', '0', '1', '2')
    MINsSAME=[('1', 'one')]
    MAXs={'2':2, '0':0, '+infinity':None, '-2':-2, 'two':2}
    MAXsORDER=('-2', '0', '2', '+infinity')
    MAXsSAME=[('2', 'two')]
    TIMEPOINTS=range(0,10)

    #------------------------------------------------------------------------------------------
    def validMinMaxDelay(cls, mindelay, maxdelay):
        """
        Check if the min/max is a valid combination,
         i.e. min <= max, considering None as -/+infinity
        """
        if mindelay is None: # -infinity
            return maxdelay is not None; # every value execept None
        if maxdelay is None: # +infinity
            return mindelay is not None; # every value execept None
        return mindelay <= maxdelay # min < max

    #------------------------------------------------------------------------------------------
    def setUp(self):
        #Delay._NUMERIC = 'Decimal'  # change Delay numeric value
        self.p1 = TimePoint(1)
        self.p2 = TimePoint(2)
        self.p3 = TimePoint(3)
        self.it = TimeInterval(self.p1, self.p2)
        self.annotationI = Annotation(self.it, Label(" \t\t  être être   être  \n "))
        self.annotationP= Annotation(self.p1, Label("mark"))
        # Create some IntervalsDelay
        self.intervalsDelays = {}
        for xk, xpercent in self.PERCENTs.items():
            for yk, ypercent in self.PERCENTs.items():
                for mk, mindelay in self.MINs.items():
                    for Mk, maxdelay in self.MAXs.items():
                        if self.validMinMaxDelay(mindelay, maxdelay):
                            self.intervalsDelays[(xk, yk, mk, Mk)] = IntervalsDelay(mindelay, maxdelay, xpercent, ypercent)
                            

    #------------------------------------------------------------------------------------------
    def test___init__(self):
        """
        Test the IntervalsDelay constructor
        """

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
        self.assertGreater(seM1,  ssM1) # start_end > start_start
        
        # build an end_start IntervalsDelay
        esM1 = IntervalsDelay(0, 2, 1, 0)
        self.assertEqual(esM1, self.intervalsDelays[('end', 'start', '0', '2')])
        self.assertGreater(esM1,  seM1) # end_start > start_end

        # build an end_end IntervalsDelay
        eeM1 = IntervalsDelay(0, 2, 1, 1)
        self.assertEqual(eeM1, self.intervalsDelays[('end', 'end', '0', '2')])
        self.assertGreater(eeM1,  esM1) # end_end > end_start

        # build some middle_middle IntervalsDelay (default values of xpercent/ypercent)
        mmM1 = IntervalsDelay(0, 2)
        self.assertEqual(mmM1, self.intervalsDelays[('middle', 'middle', '0', '2')])
        mmM2 = IntervalsDelay(maxdelay=2)
        self.assertEqual(mmM1, mmM2)
        self.assertGreater(mmM1,  seM1) # middle_middle > start_end > start_start
        self.assertLess(mmM1,  esM1) # middle_middle < end_start < end_end

        # build some percent_percent IntervalsDelay
        ppM1 = IntervalsDelay(0, 2, 0.25, 0.75)
        self.assertEqual(ppM1, self.intervalsDelays[('25%', '75%', '0', '2')])
        ppM2 = IntervalsDelay(mindelay=0, maxdelay=2, xpercent=0.25, ypercent=75./100) # /!\ 75/100=0 or 1 (int), 75./100 = 0.75
        self.assertEqual(ppM1, ppM2)

        # raise ValueError on invalid min/max delay
        for mk, mindelay in self.MINs.items():
            for Mk, maxdelay in self.MAXs.items():
                if not self.validMinMaxDelay(mindelay, maxdelay): # use invald pairs
                    for xk, xpercent in self.PERCENTs.items():
                        for yk, ypercent in self.PERCENTs.items():
                            with self.assertRaises(ValueError):
                                IntervalsDelay(mindelay, maxdelay, xpercent, ypercent)

    #------------------------------------------------------------------------------------------
    def test___cmp__(self):
        """
        Test the IntervalsDelay comparator
        """

        # Compare the IntervalsDelay with same mindelay (but different keys)
        checked = 0
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk1, mk2 in self.MINsSAME:
                    for Mk in self.MAXs.keys():
                        if self.validMinMaxDelay(self.MINs[mk1], self.MAXs[Mk]):
                            id1 = self.intervalsDelays[(xk, yk, mk1, Mk)]
                            id2 = self.intervalsDelays[(xk, yk, mk2, Mk)]
                            self.assertEqual(id1, id2, "NOT {} == {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
                            checked+=1
        self.assertGreater(checked, 0, "Any checks for same mindelay")
        # Compare the IntervalsDelay with same maxdelay (but different keys)
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    for Mk1, Mk2 in self.MAXsSAME:
                        if self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk1]):
                            id1=self.intervalsDelays[(xk, yk, mk, Mk1)]
                            id2=self.intervalsDelays[(xk, yk, mk, Mk2)]
                            self.assertEqual(id1, id2, "NOT {} == {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
        # Compare the IntervalsDelay with same xpercent (but different keys)
        for xk1, xk2 in self.PERCENTsSAME:
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    for Mk in self.MAXs.keys():
                        if self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk]):
                            id1=self.intervalsDelays[(xk1, yk, mk, Mk)]
                            id2=self.intervalsDelays[(xk2, yk, mk, Mk)]
                            self.assertEqual(id1, id2 , "NOT {} == {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
        # Compare the IntervalsDelay with same ypercent (but different keys)
        for xk in self.PERCENTs.keys():
            for yk1, yk2 in self.PERCENTsSAME:
                for mk in self.MINs.keys():
                    for Mk in self.MAXs.keys():
                        if self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk]):
                            id1=self.intervalsDelays[(xk, yk1, mk, Mk)]
                            id2=self.intervalsDelays[(xk, yk2, mk, Mk)]
                            self.assertEqual(id1, id2, "NOT {} == {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
        
        # Check the order based on xpercent
        for i in range(1,len(self.PERCENTsORDER)):
            xk1, xk2 = self.PERCENTsORDER[i-1:i+1]
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    for Mk in self.MAXs.keys():
                        if self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk]):
                            id1 = self.intervalsDelays[(xk1, yk, mk, Mk)]
                            id2 = self.intervalsDelays[(xk2, yk, mk, Mk)]
                            self.assertLess(id1, id2, "NOT {} < {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
        # Check the order based on ypercent
        for xk in self.PERCENTs.keys():
            for i in range(1,len(self.PERCENTsORDER)):
                yk1, yk2 = self.PERCENTsORDER[i-1:i+1]
                for mk in self.MINs.keys():
                    for Mk in self.MAXs.keys():
                        if self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk]):
                            id1 = self.intervalsDelays[(xk, yk1, mk, Mk)]
                            id2 = self.intervalsDelays[(xk, yk2, mk, Mk)]
                            self.assertLess(id1, id2, "NOT {} < {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
        # Check the order based on mindelay
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for i in range(1,len(self.MINsORDER)):
                    mk1, mk2 = self.MINsORDER[i-1:i+1];
                    for Mk in self.MAXs.keys():
                        try:
                            id1=self.intervalsDelays[(xk, yk, mk1, Mk)]
                            id2=self.intervalsDelays[(xk, yk, mk2, Mk)]
                            self.assertLess(id1, id2 , "NOT {} < {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
                        except KeyError:
                            self.assertFalse( self.validMinMaxDelay(self.MINs[mk1], self.MAXs[Mk])
                                and self.validMinMaxDelay(self.MINs[mk2], self.MAXs[Mk])
                                )
        # Check the order based on maxdelay
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    for i in range(1,len(self.MAXsORDER)):
                        Mk1, Mk2 = self.MAXsORDER[i-1:i+1];
                        try:
                            id1=self.intervalsDelays[(xk, yk, mk, Mk1)]
                            id2=self.intervalsDelays[(xk, yk, mk, Mk2)]
                            self.assertLess(id1, id2 , "NOT {} < {} : id1.cmp(id2) = {}".format(id1, id2, id1.__cmp__(id2)))
                        except KeyError:# some invalid min/max combination, like max<min OR -infinity/+infinity
                            self.assertFalse( self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk1])
                                and self.validMinMaxDelay(self.MINs[mk], self.MAXs[Mk2])
                                )

    #------------------------------------------------------------------------------------------
    def test_create(self):
        """
        Test the IntervalsDelay.create() method
        """

        # some easy case
        ssM1 = IntervalsDelay.create('start_start_max', 2)
        ssM2 = IntervalsDelay.create(start_start_max=2)
        self.assertEquals(ssM1,ssM2)
        self.assertEquals(ssM1,self.intervalsDelays[('start', 'start', '0', '2')])

        # create with a couple of min/max values, i.e create(<xpt>_<ypt>, (min, max)), create(<xpt>_<ypt>=(min, max)), etc.
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    mink=self.MINs[mk];
                    for Mk in self.MAXs.keys():
                        Maxk=self.MAXs[Mk];
                        if self.validMinMaxDelay(mink, Maxk):
                            # (a) create(<xpt>_<ypt>, (min, max))
                            id1 = IntervalsDelay.create("{}_{}".format(xk, yk), (mink, Maxk))
                            id2 = self.intervalsDelays[(xk, yk, mk, Mk)]
                            self.assertEqual(id1, id2
                                , "[{xk},{yk},{mk},{Mk}] (a) create('{xk}_{yk}', ({mink},{Maxk})) NOT {id1} == {id2}".format(**locals())
                                )
                            # (b) create(<xpt>_<ypt>=(min, max))
                            kwargs={"{}_{}".format(xk, yk) : (mink, Maxk)}
                            id1 = IntervalsDelay.create(**kwargs)
                            self.assertEqual(id1, id2
                                , "[{xk},{yk},{mk},{Mk}] (b) create({kwargs}) NOT {id1} == {id2}".format(**locals())
                                )
                            # (c) create(<xpt>_<ypt>, {mindelay=min, maxdelay=max})
                            v={'mindelay':mink, 'maxdelay':Maxk}
                            id1 = IntervalsDelay.create("{}_{}".format(xk, yk),v)
                            self.assertEqual(id1, id2
                                , "[{xk},{yk},{mk},{Mk}] (c) create('{xk}_{yk}',{v}) NOT {id1} == {id2}".format(**locals())
                                )
                            # (d) create('and', <xpt>_<ypt>, (min, max))
                            id1 = IntervalsDelay.create('and', "{}_{}".format(xk, yk), (mink, Maxk))
                            self.assertEqual(id1, id2
                                , "[{xk},{yk},{mk},{Mk}] (d) create('and', '{xk}_{yk}', ({mink},{Maxk})) NOT {id1} == {id2}".format(**locals())
                                )
                            # (e) create('or', <xpt>_<ypt>, (min, max))
                            id1 = IntervalsDelay.create('or', "{}_{}".format(xk, yk), (mink, Maxk))
                            self.assertEqual(id1, id2
                                , "[{xk},{yk},{mk},{Mk}] (e) create('or', '{xk}_{yk}', ({mink},{Maxk})) NOT {id1} == {id2}".format(**locals())
                                )
                            # (f) create('join', 'or', <xpt>_<ypt>, (min, max))
                            id1 = IntervalsDelay.create('join','or', "{}_{}".format(xk, yk), (mink, Maxk))
                            self.assertEqual(id1, id2
                                , "[{xk},{yk},{mk},{Mk}] (f) create('join','or', '{xk}_{yk}', ({mink},{Maxk})) NOT {id1} == {id2}".format(**locals())
                                )
        
        # create with min==max values, i.e create(<xpt>_<ypt>_eq, min), create(<xpt>_<ypt>=(min, min)), etc.
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    mink=self.MINs[mk];
                    if mink is None: continue; # skip -infinity/+infinity
                    for Mk in self.MAXs.keys():
                        Maxk=self.MAXs[Mk];
                        if Maxk != mink: continue; # skip Max!=min
                        # (a) create(<xpt>_<ypt>_eq, min)
                        id1 = IntervalsDelay.create("{}_{}_eq".format(xk, yk), mink)
                        id2 = self.intervalsDelays[(xk, yk, mk, Mk)]
                        self.assertEqual(id1, id2
                            , "[{xk},{yk},{mk},{Mk}] (a) create('{xk}_{yk}_eq', {mink}) NOT {id1} == {id2}".format(**locals())
                            )
                        # (b) create(<xpt>_<ypt>_eq, {delay=min})
                        v={'delay':mink}
                        id1 = IntervalsDelay.create("{}_{}_eq".format(xk, yk), v)
                        self.assertEqual(id1, id2
                            , "[{xk},{yk},{mk},{Mk}] (b) create('{xk}_{yk}_eq', {v}) NOT {id1} == {id2}".format(**locals())
                            )
                        # (c) create(<xpt>_<ypt>_eq=min)
                        kwargs={"{}_{}_eq".format(xk, yk):mink}
                        id1 = IntervalsDelay.create(**kwargs)
                        self.assertEqual(id1, id2
                            , "[{xk},{yk},{mk},{Mk}] (c) create({kwargs}) NOT {id1} == {id2}".format(**locals())
                            )
                        # (d) create(<xpt>_<ypt>_eq={delay=min})
                        kwargs={"{}_{}_eq".format(xk, yk):{'delay':mink}}
                        id1 = IntervalsDelay.create(**kwargs)
                        self.assertEqual(id1, id2
                            , "[{xk},{yk},{mk},{Mk}] (d) create({kwargs}) NOT {id1} == {id2}".format(**locals())
                            )
                        # (e) create(%_%, {xpercent, ypercent, delay})
                        v={'xpercent':self.PERCENTs[xk], 'ypercent':self.PERCENTs[yk], 'delay':mink}
                        id1 = IntervalsDelay.create('%_%_eq',v)
                        self.assertEqual(id1, id2
                            , "[{xk},{yk},{mk},{Mk}] (e) create('%_%', {v}) NOT {id1} == {id2}".format(**locals())
                            )
                        # (f) create(<xpt>_<ypt>, min) ('eq' is the default relation)
                        id1 = IntervalsDelay.create("{}_{}".format(xk, yk), mink)
                        self.assertEqual(id1, id2
                            , "[{xk},{yk},{mk},{Mk}] (c) create('{xk}_{yk}', {mink}) NOT {id1} == {id2}".format(**locals())
                            )
                        # (g) create(%_%, {xpercent, ypercent, delay}) ('eq' is the default relation)
                        v={'xpercent':self.PERCENTs[xk], 'ypercent':self.PERCENTs[yk], 'delay':Maxk}
                        id1 = IntervalsDelay.create('%_%',v)
                        self.assertEqual(id1, id2
                            , "[{xk},{yk},{mk},{Mk}] (d) create('%_%', {v}) NOT {id1} == {id2}".format(**locals())
                            )
        # create with min values, i.e create(<xpt>_<ypt>_min, min) => Max = (min>=0 ? +infinity : 0)
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for mk in self.MINs.keys():
                    mink=self.MINs[mk];
                    Mk = '0' if (mink is None or mink<0) else '+infinity' # Max = (min>=0 ? +infinity : 0)
                    Maxk = self.MAXs[Mk];
                    # (a) create(<xpt>_<ypt>_min, min)
                    id1 = IntervalsDelay.create("{}_{}_min".format(xk, yk), mink)
                    id2 = self.intervalsDelays[(xk, yk, mk, Mk)]
                    self.assertEqual(id1, id2
                        , "[{xk},{yk},{mk},{Mk}] (a) create('{xk}_{yk}_min', {mink}) NOT {id1} == {id2}".format(**locals())
                        )
                    # (b) create(<xpt>_<ypt>_min=min)
                    kwargs={"{}_{}_min".format(xk, yk):mink}
                    id1 = IntervalsDelay.create(**kwargs)
                    self.assertEqual(id1, id2
                        , "[{xk},{yk},{mk},{Mk}] (b) create({kwargs}) NOT {id1} == {id2}".format(**locals())
                        )
                    # (c) create(%_%_min, {xpercent, ypercent, mindelay})
                    v={'xpercent':self.PERCENTs[xk], 'ypercent':self.PERCENTs[yk], 'mindelay':mink}
                    id1 = IntervalsDelay.create('%_%_min',v)
                    self.assertEqual(id1, id2
                        , "[{xk},{yk},{mk},{Mk}] (b) create('%_%_min', {v}) NOT {id1} == {id2}".format(**locals())
                        )
        # create with Max values, i.e create(<xpt>_<ypt>_max, Max) => min = (Max>=0 ? 0 : -infinity)
        for xk in self.PERCENTs.keys():
            for yk in self.PERCENTs.keys():
                for Mk in self.MAXs.keys():
                    Maxk = self.MAXs[Mk];
                    mk = '0' if (Maxk is None or Maxk>=0) else '-infinity' # min = (Max>=0 ? 0 : -infinity)
                    mink=self.MINs[mk];
                    # (a) create(<xpt>_<ypt>_max, max)
                    id1 = IntervalsDelay.create("{}_{}_max".format(xk, yk), Maxk)
                    id2 = self.intervalsDelays[(xk, yk, mk, Mk)]
                    self.assertEqual(id1, id2
                        , "[{xk},{yk},{mk},{Mk}] (a) create('{xk}_{yk}_max', {Maxk}) NOT {id1} == {id2}".format(**locals())
                        )
                    # (b) create(<xpt>_<ypt>_max=max)
                    kwargs={"{}_{}_max".format(xk, yk):Maxk}
                    id1 = IntervalsDelay.create(**kwargs)
                    self.assertEqual(id1, id2
                        , "[{xk},{yk},{mk},{Mk}] (b) create({kwargs}) NOT {id1} == {id2}".format(**locals())
                        )
                    # (d) create(%_%_max, {xpercent, ypercent, maxdelay})
                    v={'xpercent':self.PERCENTs[xk], 'ypercent':self.PERCENTs[yk], 'maxdelay':Maxk}
                    id1 = IntervalsDelay.create('%_%_max',v)
                    self.assertEqual(id1, id2
                        , "[{xk},{yk},{mk},{Mk}] (d) create('%_%_max', {v}) NOT {id1} == {id2}".format(**locals())
                        )

        # create joined IntervalsDelay
        from annotationdata.filter.delay_relations import AndPredicates, OrPredicates
        import random
        for (xk1, yk1, mk1, Mk1) in random.sample(self.intervalsDelays.keys(),15): # get only 15 random values
            min1 = self.MINs[mk1]; Max1 = self.MAXs[Mk1];
            id1 = self.intervalsDelays[(xk1, yk1, mk1, Mk1)]
            for (xk2, yk2, mk2, Mk2) in random.sample(self.intervalsDelays.keys(),15): # get only 15 random values

                min2 = self.MINs[mk2]; Max2 = self.MAXs[Mk2];
                id2 = self.intervalsDelays[(xk2, yk2, mk2, Mk2)]
                idAnd = AndPredicates(id1, id2)
                # (a) implicit AND
                cargs=("{}_{}".format(xk1, yk1), (min1, Max1), "{}_{}".format(xk2, yk2), (min2, Max2));
                ckwargs={};
                idc = IntervalsDelay.create(*cargs, **ckwargs);
                self.assertEqual(idc, idAnd
                        , "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (a) create({cargs},{ckwargs}) NOT {idc} == {idAnd}".format(**locals())
                        )
                # (b) explicit AND : create("and", ...)
                cargs=("AND", "{}_{}".format(xk1, yk1), (min1, Max1)) # mixing args and kwargs
                ckwargs={"{}_{}".format(xk2, yk2):(min2, Max2)};
                idc = IntervalsDelay.create(*cargs, **ckwargs);
                self.assertEqual(idc, idAnd
                        , "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (b) create({cargs},{ckwargs}) NOT {idc} == {idAnd}".format(**locals())
                        )
                # (c) explicit AND with 'join' : create(..., join="and", ...)
                cargs=("{}_{}".format(xk1, yk1), (min1, Max1)) # mixing args and kwargs
                ckwargs={'join':"AND", "{}_{}".format(xk2, yk2):(min2, Max2)};
                idc = IntervalsDelay.create(*cargs, **ckwargs);
                self.assertEqual(idc, idAnd
                        , "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (c) create({cargs},{ckwargs}) NOT {idc} == {idAnd}".format(**locals())
                        )
                # (d) explicit AND with 'join' : create(..., join="and", ...)
                cargs=("{}_{}".format(xk1, yk1), (min1, Max1), "{}_{}".format(xk2, yk2), (min2, Max2))
                ckwargs={'join':"AND"};
                idc = IntervalsDelay.create(*cargs, **ckwargs);
                self.assertEqual(idc, idAnd
                        , "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (d) create({cargs},{ckwargs}) NOT {idc} == {idAnd}".format(**locals())
                        )
                # (e) (explicit) OR (as 1st parameter)
                idOr = OrPredicates(id1, id2)
                cargs=("or", "{}_{}".format(xk1, yk1), (min1, Max1), "{}_{}".format(xk2, yk2), (min2, Max2)) 
                ckwargs={};
                try:
                    idc = IntervalsDelay.create(*cargs, **ckwargs);
                except:
                    e = sys.exc_info()[0]
                    print("Error with [{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] create({cargs},{ckwargs}) : {e}".format(**locals()))
                self.assertEqual(idc, idOr
                    , "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (e) create({cargs},{ckwargs}) NOT {idc} == {idOr}".format(**locals())
                    )
                # (f) (explicit) OR with 'join' key
                cargs=("join", "Or", "{}_{}".format(xk1, yk1), (min1, Max1), "{}_{}".format(xk2, yk2), (min2, Max2)) 
                ckwargs={};
                try:
                    idc = IntervalsDelay.create(*cargs, **ckwargs);
                except:
                    e = sys.exc_info()[0]
                    print("Error with [{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] create({cargs},{ckwargs}) : {e}".format(**locals()))
                self.assertEqual(idc, idOr
                    , "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (f) create({cargs},{ckwargs}) NOT {idc} == {idOr}".format(**locals())
                    )
                # (g) (explicit) OR in kwargs
                cargs=("{}_{}".format(xk1, yk1), (min1, Max1), "{}_{}".format(xk2, yk2), (min2, Max2)) 
                ckwargs={'join':'OR'};
                try:
                    idc = IntervalsDelay.create(*cargs, **ckwargs);
                except:
                    e = sys.exc_info()[0]
                    print("Error with [{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] create({cargs},{ckwargs}) : {e}".format(**locals()))
                self.assertEqual(idc, idOr
                    , "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (g) create({cargs},{ckwargs}) NOT {idc} == {idOr}".format(**locals())
                    )
                # (h) Using kwargs for id1 AND id2 /!\ order can change
                #import traceback
                if (xk1, yk1) != (xk2, yk2): # (!) if (xk1, yk1) == (xk2, yk2), the "{}_{}" keys have the same value => the first is ignored
                    idOrReverse = OrPredicates(id2, id1)
                    cargs=("OR",) # /!\ the comma is important, else cargs=("OR") <=> cargs="OR"
                    ckwargs={"{}_{}".format(xk1, yk1): (min1, Max1), "{}_{}".format(xk2, yk2):(min2, Max2)}; # /!\ not sur of the resulting order
                    try:
                        idc = IntervalsDelay.create(*cargs, **ckwargs);
                        #print("With [{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}]\n\tidc={idc}\n\tidOr={idOr}\n\tidOrReverse={idOrReverse}".format(**locals()))
                        self.assertTrue( (idc == idOr) or (idc == idOrReverse) 
                            , "[{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] (h) create({cargs},{ckwargs}) NOT {idc} == {idOr} (or {idOrReverse})".format(**locals())
                            )
                    except:
                        e = sys.exc_info()[0]
                        print("Error with [{xk1},{yk1},{mk1},{Mk1}][{xk2},{yk2},{mk2},{Mk2}] create({cargs},{ckwargs}) : {e}'".format(**locals()))
                        #traceback.print_exception(*sys.exc_info())

    #------------------------------------------------------------------------------------------
    def test___call__(self):
        import random
        # Create some TimePoint, TimeInterval and Annotation
        # - create the TimePoints:  self.timePoints[i] = TimePoint(i) (0<=i<=9) (=> 10)
        self.timePoints = {i:TimePoint(i) for i in self.TIMEPOINTS }
        # - create the TimeInterval:  [timePoints[i], timePoints[j]] 0<=i<j<=9 (=> 45)
        self.timeIntervals = dict();
        for i in self.timePoints.keys():
            for j in self.timePoints.keys():
                if i<j:
                    self.timeIntervals[(i,j)] = TimeInterval(self.timePoints[i], self.timePoints[j])
        # - create the point annotations:
        self.pointAnnotations = {i:Annotation(self.timePoints[i], Label("point at {:.3f}s".format(i))) for i in self.timePoints.keys()}
        # - create the intervals annotations:
        self.intervalAnnotations = {(i,j):Annotation(self.timeIntervals[(i,j)], Label("interval [{:.3f}, {:.3f}]s".format(i,j))) for (i,j) in self.timeIntervals.keys()}
        
        # check the start_start_max predicate
        nbAsserts=0
        for Mk in self.MAXsORDER:
            Maxd = self.MAXs[Mk]
            #if Maxd<0: continue; # TODO
            for mk in self.MINsORDER:
                mind = self.MINs[mk]
                if Maxd is None and mind is None: break; # => invalid interval
                if mind>Maxd: break; # mind > Maxd => invalid interval
                for xk in ['start']:
                    yk=xk; # same reference point
                    idc = self.intervalsDelays[(xk, yk, mk, Mk)]
                    # compare 2 point annotations
                    for i in self.pointAnnotations.keys():
                        for j in self.pointAnnotations.keys():
                            pai = self.pointAnnotations[i]
                            paj = self.pointAnnotations[j]
                            pred = idc(pai, paj)
                            if (j-i) > Maxd:
                                self.assertFalse(pred
                                        , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({j}-{i}) > {Maxd} (pred={pred}; pred.delay={pred_delay}, idc.delay()={idc_delay:r})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None, idc_delay=idc.delay(*IntervalsDelay.splitAnnotations(pai, paj)), **locals())
                                    ); nbAsserts+=1
                            elif (mind is None or mind<=(j-i)):
                                self.assertTrue(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't true when {mind} <= ({j}-{i}) < {Maxd} (pred={pred}; pred.delay={pred_delay}, idc.delay()={idc_delay:r})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None, idc_delay=idc.delay(*IntervalsDelay.splitAnnotations(pai, paj)), **locals())
                                    ); nbAsserts+=1
                            else: # (j-i) < min
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({j}-{i}) < {mind} (pred={pred}; pred.delay={pred_delay}, idc.delay()={idc_delay:r})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None, idc_delay=idc.delay(*IntervalsDelay.splitAnnotations(pai, paj)), **locals())
                                    ); nbAsserts+=1
                    # compare a point and an interval annotations
                    for start1 in self.pointAnnotations.keys():
                        for (start2, end2) in random.sample(self.intervalAnnotations.keys(),15):
                            a1 = self.pointAnnotations[start1]
                            a2 = self.intervalAnnotations[(start2, end2)]
                            pred = idc(a1, a2)
                            if (start2-start1) > Maxd:
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({start2}-{start1}) > {Maxd} (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                            elif (mind is None or mind<=(start2-start1)):
                                self.assertTrue(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't true when {mind} <= ({start2}-{start1}) < {Maxd} (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                            else: # (start2-start1) < min
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({start2}-{start1}) < {mind} (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                    # compare 2 interval annotations
                    for (start1, end1) in random.sample(self.intervalAnnotations.keys(),15):
                        for (start2, end2) in random.sample(self.intervalAnnotations.keys(),15):
                            a1 = self.intervalAnnotations[(start1, end1)]
                            a2 = self.intervalAnnotations[(start2, end2)]
                            pred = idc(a1, a2)
                            if (start2-start1) > Maxd:
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({start2}-{start1}) > {Maxd} (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                            elif (mind is None or mind<=(start2-start1)):
                                self.assertTrue(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't true when {mind} <= ({start2}-{start1}) < {Maxd} (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                            else: # (start2-start1) < min
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({start2}-{start1}) < {mind} (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
        if nbAsserts<=0: raise Warning("Any assertion in the test loop");

        # check the start_end predicates
        nbAsserts=0
        for Mk in self.MAXsORDER:
            Maxd = self.MAXs[Mk]
            #if Maxd<0: continue; # TODO
            for mk in self.MINsORDER:
                mind = self.MINs[mk]
                if Maxd is None and mind is None: break; # => invalid interval
                if mind>Maxd: break; # mind > Maxd => invalid interval
                for (xk, yk) in [('start','end'), ('start', '100%')]:
                    idc = self.intervalsDelays[(xk, yk, mk, Mk)]
                    # compare 2 interval annotations
                    for (start1, end1) in random.sample(self.intervalAnnotations.keys(),15):
                        for (start2, end2) in random.sample(self.intervalAnnotations.keys(),15):
                            a1 = self.intervalAnnotations[(start1, end1)]
                            a2 = self.intervalAnnotations[(start2, end2)]
                            pred = idc(a1, a2)
                            delay = (end2-start1)
                            if delay > Maxd:
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({delay} > {Maxd}) (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                            elif (mind is None or mind<=delay):
                                self.assertTrue(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't true when ({mind} <= {delay}) < {Maxd}) (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                            else: # (start2-start1) < min
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({delay} < {mind}) (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
        if nbAsserts<=0: raise Warning("Any assertion in the test loop");

        # check the end_start predicates
        nbAsserts=0
        for Mk in self.MAXsORDER:
            Maxd = self.MAXs[Mk]
            #if Maxd<0: continue; # TODO
            for mk in self.MINsORDER:
                mind = self.MINs[mk]
                if Maxd is None and mind is None: break; # => invalid interval
                if mind>Maxd: break; # mind > Maxd => invalid interval
                for (xk, yk) in [('end','start'), ('100%', 'start')]:
                    idc = self.intervalsDelays[(xk, yk, mk, Mk)]
                    # compare 2 interval annotations
                    for (start1, end1) in random.sample(self.intervalAnnotations.keys(),15):
                        for (start2, end2) in random.sample(self.intervalAnnotations.keys(),15):
                            a1 = self.intervalAnnotations[(start1, end1)]
                            a2 = self.intervalAnnotations[(start2, end2)]
                            pred = idc(a1, a2)
                            delay = (start2-end1)
                            if delay > Maxd:
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({delay} > {Maxd}) (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                            elif (mind is None or mind<=delay):
                                self.assertTrue(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't true when ({mind} <= {delay}) < {Maxd}) (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                            else: # (start2-start1) < min
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({delay} < {mind}) (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
        if nbAsserts<=0: raise Warning("Any assertion in the test loop");

        # check some percent/percent predicates
        nbAsserts=0
        for Mk in self.MAXsORDER:
            Maxd = self.MAXs[Mk]
            #if Maxd<0: continue; # TODO
            for mk in self.MINsORDER:
                mind = self.MINs[mk]
                if Maxd is None and mind is None: break; # => invalid interval
                if mind>Maxd: break; # mind > Maxd => invalid interval
                for (xk, yk) in [('middle','25%'), ('50%', '75%')]:
                    idc = self.intervalsDelays[(xk, yk, mk, Mk)]
                    # compare 2 interval annotations
                    for (start1, end1) in random.sample(self.intervalAnnotations.keys(),15):
                        for (start2, end2) in random.sample(self.intervalAnnotations.keys(),15):
                            a1 = self.intervalAnnotations[(start1, end1)]
                            a2 = self.intervalAnnotations[(start2, end2)]
                            pred = idc(a1, a2)
                            delay = ( ( start2 + self.PERCENTs[yk] * (end2-start2))
                                    - ( start1 + self.PERCENTs[xk] * (end1-start1))
                                    )
                            if delay > Maxd:
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({delay} > {Maxd}) (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                            elif (mind is None or mind<=delay):
                                # pred is a CheckedIntervalsDelay
                                self.assertTrue(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't true when ({mind} <= {delay}) < {Maxd}) (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                                # pred.delay == delay
                                self.assertEqual(delay, pred.delay
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) {delay}) != pred.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
                            else: # (start2-start1) < min
                                self.assertFalse(pred
                                    , "IntervalsDelays[{xk},{yk},{mk},{Mk}]({pai}, {paj}) isn't false when ({delay} < {mind}) (pred={pred}; ped.delay={pred_delay})".format(pred_delay=pred.delay if (hasattr(pred,'delay')) else None,**locals())
                                    ); nbAsserts+=1
        if nbAsserts<=0: raise Warning("Any assertion in the test loop");
        
        # check some AND/OR predicate
        from annotationdata.filter.delay_relations import AndPredicates, OrPredicates
        nbAsserts=0
        for (xk1, yk1, mk1, Mk1) in random.sample(self.intervalsDelays.keys(),10): # get only 10 random values
            min1 = self.MINs[mk1]; Max1 = self.MAXs[Mk1];
            id1 = self.intervalsDelays[(xk1, yk1, mk1, Mk1)]
            #for (xk2, yk2, mk2, Mk2) in random.sample([k for k in self.intervalsDelays.keys() if (k[0], k[1])==(xk1, yk1)],10): # get only 10 random values, with same xk, yk
            for (xk2, yk2, mk2, Mk2) in random.sample(self.intervalsDelays.keys(),10): # get only 10 random values
                min2 = self.MINs[mk2]; Max2 = self.MAXs[Mk2];
                id2 = self.intervalsDelays[(xk2, yk2, mk2, Mk2)]
                idAnd = AndPredicates(id1, id2)
                idOr = OrPredicates(id1, id2)
                # compare 2 interval annotations
                for (start1, end1) in random.sample(self.intervalAnnotations.keys(),10):
                    for (start2, end2) in random.sample(self.intervalAnnotations.keys(),10):
                        a1 = self.intervalAnnotations[(start1, end1)]
                        a2 = self.intervalAnnotations[(start2, end2)]
                        # compute delay and value
                        # - for the first IntervalsDelay
                        delay1 = ( ( start2 + self.PERCENTs[yk1] * (end2-start2))
                                - ( start1 + self.PERCENTs[xk1] * (end1-start1))
                                )
                        v1 = (Max1 is None or (delay1<=Max1)) and (min1 is None or (min1<=delay1))
                        # - for the second IntervalsDelay
                        delay2 = ( ( start2 + self.PERCENTs[yk2] * (end2-start2))
                                - ( start1 + self.PERCENTs[xk2] * (end1-start1))
                                )
                        v2 = (Max2 is None or (delay2<=Max2)) and (min2 is None or (min2<=delay2))
                        # compute each predicate (for error message)
                        pred1 = id1(a1, a2);
                        pred2 = id2(a1, a2)
                        # (a) AND
                        predAnd = idAnd(a1, a2)
                        if (v1 and v2):
                            self.assertTrue(predAnd
                                , "AndPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) isn't true predAnd={predAnd} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(**locals())
                                ); nbAsserts+=1
                            # check the AND predicate return the list of predicate
                            self.assertEqual(predAnd, [pred1, pred2]
                                , "AndPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) isn't equals to list of predicate predAnd={predAnd} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(**locals())
                                )
                        else:
                            self.assertFalse(predAnd
                                , "AndPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) isn't false predAnd={predAnd} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(**locals())
                                ); nbAsserts+=1
                        # (b) OR
                        predOr = idOr(a1, a2)
                        if (v1 or v2):
                            self.assertTrue(predOr
                                , "OrPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) isn't true predOr={predOr} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(**locals())
                                ); nbAsserts+=1
                            # check the OR predicate return the 1st true value
                            if v1:
                                self.assertEqual(predOr, pred1
                                    , "OrPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) string isn't equals to first true predicate predOr={predOr} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(**locals())

                                    )
                            else:
                                self.assertEqual(predOr, pred2
                                    , "OrPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) string isn't equals to first true predicate predOr={predOr} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(**locals())

                                    )
                        else:
                            self.assertFalse(predOr
                                , "OrPredicates[[{xk1},{yk1},{mk1},{Mk1}],[{xk2},{yk2},{mk2},{Mk2}]]({a1}, {a2}) isn't false predOr={predOr} (delay1={delay1}, pred1={pred1}, delay2={delay2}, pred2={pred2}, v1={v1}, v2={v2}))".format(**locals())
                                ); nbAsserts+=1
        if nbAsserts<=0: raise Warning("Any assertion in the test loop");

            

# End TestIntervalsDelay
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalsDelay)
    unittest.TextTestRunner(verbosity=2).run(suite)

