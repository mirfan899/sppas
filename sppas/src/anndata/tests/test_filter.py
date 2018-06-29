# -*- coding:utf-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.anndata.tests.test_filter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the filter system.

"""
import unittest
import os.path
import time

from sppas.src.utils.makeunicode import u
from ..aio.readwrite import sppasRW
from ..tier import sppasTier
from ..annlocation.location import sppasLocation
from ..annlocation.interval import sppasInterval
from ..annlocation.point import sppasPoint
from ..annlabel.label import sppasTag
from ..annlabel.label import sppasLabel
from ..annotation import sppasAnnotation

from ..filter import sppasFilters
from ..filter import sppasAnnSet

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestSetFilter(unittest.TestCase):
    """ Test filter result. """

    def setUp(self):
        self.p1 = sppasPoint(1)
        self.p2 = sppasPoint(2)
        self.p4 = sppasPoint(4)
        self.p9 = sppasPoint(9)
        self.it1 = sppasInterval(self.p1, self.p2)
        self.it2 = sppasInterval(self.p2, self.p4)
        self.it3 = sppasInterval(self.p4, self.p9)
        self.a1 = sppasAnnotation(sppasLocation(self.it1),
                                  sppasLabel(sppasTag(" \t\t  être être   être  \n ")))
        self.a2 = sppasAnnotation(sppasLocation(self.it2),
                                  sppasLabel([sppasTag("toto"),
                                              sppasTag("titi")]))
        self.a3 = sppasAnnotation(sppasLocation(self.it3),
                                  [sppasLabel(sppasTag("tata")),
                                   sppasLabel(sppasTag("titi"))])

    # -----------------------------------------------------------------------

    def test_append(self):
        """ Append an annotation and values. """

        d = sppasAnnSet()
        self.assertEqual(0, len(d))

        d.append(self.a1, ['contains = t'])
        self.assertEqual(1, len(d))
        self.assertEqual(1, len(d.get_value(self.a1)))

        # do not append the same value
        d.append(self.a1, ['contains = t'])
        self.assertEqual(1, len(d))
        self.assertEqual(1, len(d.get_value(self.a1)))

        d.append(self.a1, ['contains = o'])
        self.assertEqual(1, len(d))
        self.assertEqual(2, len(d.get_value(self.a1)))

    # -----------------------------------------------------------------------

    def test_copy(self):
        """ Test the copy of a data set. """

        d = sppasAnnSet()
        d.append(self.a1, ['contains = t', 'contains = o'])
        d.append(self.a2, ['exact = titi'])

        dc = d.copy()
        self.assertEqual(len(d), len(dc))
        for ann in d:
            self.assertEqual(d.get_value(ann), dc.get_value(ann))

    # -----------------------------------------------------------------------

    def test_or(self):
        """ Test logical "or" between two data sets. """

        d1 = sppasAnnSet()
        d2 = sppasAnnSet()

        d1.append(self.a1, ['contains = t'])
        d2.append(self.a1, ['contains = t'])

        res = d1 | d2
        self.assertEqual(1, len(res))
        self.assertEqual(1, len(res.get_value(self.a1)))

        d2.append(self.a1, ['contains = o'])
        res = d1 | d2
        self.assertEqual(1, len(res))
        self.assertEqual(2, len(res.get_value(self.a1)))

        d2.append(self.a2, ['exact = toto'])
        res = d1 | d2
        self.assertEqual(2, len(res))
        self.assertEqual(1, len(res.get_value(self.a2)))

        d2.append(self.a2, ['exact = toto', 'istartswith = T'])
        res = d1 | d2
        self.assertEqual(2, len(res))
        self.assertEqual(2, len(res.get_value(self.a2)))

        d1.append(self.a3, ['istartswith = t'])
        res = d1 | d2
        self.assertEqual(3, len(res))
        self.assertEqual(2, len(res.get_value(self.a1)))
        self.assertEqual(2, len(res.get_value(self.a2)))
        self.assertEqual(1, len(res.get_value(self.a3)))

    # -----------------------------------------------------------------------

    def test_and(self):
        """ Test logical "and" between two data sets. """

        d1 = sppasAnnSet()
        d2 = sppasAnnSet()

        d1.append(self.a1, ['contains = t'])
        d2.append(self.a1, ['contains = o'])

        res = d1 & d2
        self.assertEqual(1, len(res))
        self.assertEqual(2, len(res.get_value(self.a1)))

        # nothing changed. a2 is only in d1.
        d1.append(self.a2, ['exact = toto'])
        res = d1 & d2
        self.assertEqual(1, len(res))
        self.assertEqual(2, len(res.get_value(self.a1)))

        # ok. add a2 in d2 too...
        d2.append(self.a2, ['exact = toto'])
        res = d1 & d2
        self.assertEqual(2, len(res))
        self.assertEqual(2, len(res.get_value(self.a1)))
        self.assertEqual(1, len(res.get_value(self.a2)))

# ---------------------------------------------------------------------------


class TestFilterTier(unittest.TestCase):
    """ Test filters on a single tier. """

    def setUp(self):
        parser = sppasRW(os.path.join(DATA, "grenelle.antx"))
        self.trs = parser.read(heuristic=False)

    # -----------------------------------------------------------------------

    def test_tag(self):
        """ Test tag is matching str. """

        tier = self.trs.find('P-Phonemes')

        with self.assertRaises(KeyError):
            f = sppasFilters(tier)
            f.tag(function="value")

        print('FILTER ======= f.tag(startswith=u("l")) | f.tag(endswith=u("l")) ====== ')
        start_time = time.time()
        f = sppasFilters(tier)
        d1 = f.tag(startswith=u("l"))
        d2 = f.tag(endswith=u("l"))
        res = d1 | d2
        end_time = time.time()
        print("  - elapsed time: {:f} seconds".format(end_time - start_time))
        print("  - res size = {:d}".format(len(res)))

        print('FILTER ======= f.tag(startswith=u("l"), endswith=u("l"), logic_bool="and") ====== ')
        start_time = time.time()
        f = sppasFilters(tier)
        res = f.tag(startswith=u("l"), endswith=u("l"), logic_bool="and")
        end_time = time.time()
        print("  - elapsed time: {:f} seconds".format(end_time - start_time))
        print("  - res size = {:d}".format(len(res)))

        print('FILTER ======= f.tag(startswith=u("l"), endswith=u("l"), logic_bool="or") ====== ')
        start_time = time.time()
        f = sppasFilters(tier)
        res = f.tag(startswith=u("l"), endswith=u("l"), logic_bool="or")
        end_time = time.time()
        print("  - elapsed time: {:f} seconds".format(end_time - start_time))
        print("  - res size = {:d}".format(len(res)))

    # -----------------------------------------------------------------------

    def test_dur(self):
        """ Test localization duration. """

        tier = self.trs.find('P-Phonemes')
        f = sppasFilters(tier)

        # phonemes during 30ms
        res = f.dur(eq=0.03)
        self.assertEqual(2, len(res))

        # phonemes during more than 200ms
        res = f.dur(ge=0.2)

    # -----------------------------------------------------------------------

    def test_loc(self):
        """ Test localization range. """

        tier = self.trs.find('P-Phonemes')
        f = sppasFilters(tier)

        # the first 10 phonemes
        res = f.loc(rangeto=0.858)
        self.assertEqual(10, len(res))

        # the last 9 phonemes
        res = f.loc(rangefrom=241.977)
        self.assertEqual(9, len(res))

        # phonemes ranging from .. seconds of speech to .. seconds
        res1 = f.loc(rangefrom=219.177) & f.loc(rangeto=sppasPoint(221.369, 0.002))
        self.assertEqual(34, len(res1))

        res2 = f.loc(rangefrom=219.177, rangeto=sppasPoint(221.369, 0.002), logic_bool="and")
        self.assertEqual(34, len(res2))

        self.assertEqual(res1, res2)

    # -----------------------------------------------------------------------

    def test_combined(self):
        """ Test both tag and duration. """

        tier = self.trs.find('P-Phonemes')
        f = sppasFilters(tier)

        # silences or pauses during more than 200ms
        res = (f.tag(exact=u("#")) or f.tag(exact=u("+"))) and f.dur(ge=0.2)

# ---------------------------------------------------------------------------


class TestFilterRelationTier(unittest.TestCase):
    """ Test relations.

    Example:
    ========

        tier1:      0-----------3-------5-------7-------9---10---11
        tier2:      0---1---2---3-------5-----------8------------11

    Relations:
    ----------

    tier1                     tier2
    interval    relation      interval

    [0,3]       started by    [0,1]
    [0,3]       contains      [1,2]
    [0,3]       finished by   [2,3]
    [0,3]       meets         [3,5]
    [0,3]       before        [5,8], [8,11]

    [3,5]       after         [0,1], [1,2]
    [3,5]       met by        [2,3]
    [3,5]       equals        [3,5]
    [3,5]       meets         [5,8]
    [3,5]       before        [8,11]

    [5,7]       after         [0,1], [1,2], [2,3]
    [5,7]       met by        [3,5]
    [5,7]       starts        [5,8]
    [5,7]       before        [8,11]

    [7,9]       after         [0,1], [1,2], [2,3], [3,5]
    [7,9]       overlapped by [5,8]
    [7,9]       overlaps      [8,11]

    [9,10]      after         [0,1], [1,2], [2,3], [3,5], [5,8]
    [9,10]      during        [8,11]

    [10,11]     after         [0,1], [1,2], [2,3], [3,5], [5,8]
    [10,11]     finishes      [8,11]

    """
    def setUp(self):
        self.tier = sppasTier("Tier")
        self.tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(0), sppasPoint(3))))
        self.tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(5))))
        self.tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(5), sppasPoint(7))))
        self.tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(7), sppasPoint(9))))
        self.tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(9), sppasPoint(10))))
        self.tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(10), sppasPoint(11))))

        self.rtier = sppasTier("RelationTier")
        self.rtier.create_annotation(sppasLocation(sppasInterval(sppasPoint(0), sppasPoint(1))))
        self.rtier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2))))
        self.rtier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2), sppasPoint(3))))
        self.rtier.create_annotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(5))))
        self.rtier.create_annotation(sppasLocation(sppasInterval(sppasPoint(5), sppasPoint(8))))
        self.rtier.create_annotation(sppasLocation(sppasInterval(sppasPoint(8), sppasPoint(11))))

    def test_one_relation(self):

        f = sppasFilters(self.tier)

        # 'equals': [3,5]
        res = f.rel(self.rtier, "equals")
        self.assertEquals(1, len(res))
        ann = [a for a in res][0]
        self.assertEquals(self.tier[1], ann)
        values = res.get_value(ann)
        self.assertEquals(1, len(values))
        self.assertEquals("equals", values[0])

        # 'contains': [0,3]
        res = f.rel(self.rtier, "contains")
        self.assertEquals(1, len(res))
        ann = [a for a in res][0]
        self.assertEquals(self.tier[0], ann)
        values = res.get_value(ann)
        self.assertEquals(1, len(values))
        self.assertEquals("contains", values[0])

        # 'during': [9,10]
        res = f.rel(self.rtier, "during")
        self.assertEquals(1, len(res))
        ann = [a for a in res][0]
        self.assertEquals(self.tier[4], ann)
        values = res.get_value(ann)
        self.assertEquals(1, len(values))
        self.assertEquals("during", values[0])

        # 'starts': [5,7]
        res = f.rel(self.rtier, "starts")
        self.assertEquals(1, len(res))
        ann = [a for a in res][0]
        self.assertEquals(self.tier[2], ann)
        values = res.get_value(ann)
        self.assertEquals(1, len(values))
        self.assertEquals("starts", values[0])

        # 'startedby': [0,3]
        res = f.rel(self.rtier, "startedby")
        self.assertEquals(1, len(res))
        ann = [a for a in res][0]
        self.assertEquals(self.tier[0], ann)
        values = res.get_value(ann)
        self.assertEquals(1, len(values))
        self.assertEquals("startedby", values[0])

        # 'finishedby': [0,3]
        res = f.rel(self.rtier, "finishedby")
        self.assertEquals(1, len(res))
        ann = [a for a in res][0]
        self.assertEquals(self.tier[0], ann)
        values = res.get_value(ann)
        self.assertEquals(1, len(values))
        self.assertEquals("finishedby", values[0])

        # 'finishes': [10,11]
        res = f.rel(self.rtier, "finishes")
        self.assertEquals(1, len(res))
        ann = [a for a in res][0]
        self.assertEquals(self.tier[5], ann)
        values = res.get_value(ann)
        self.assertEquals(1, len(values))
        self.assertEquals("finishes", values[0])

        # 'meets': [0,3]; [3,5]
        res = f.rel(self.rtier, "meets")
        self.assertEquals(2, len(res))
        self.assertTrue(self.tier[0] in res)
        self.assertTrue(self.tier[1] in res)
        values = res.get_value(self.tier[0])
        self.assertEquals(1, len(values))
        self.assertEquals("meets", values[0])
        values = res.get_value(self.tier[1])
        self.assertEquals(1, len(values))
        self.assertEquals("meets", values[0])

        # 'metby': [3,5]; [5,7]
        res = f.rel(self.rtier, "metby")
        self.assertEquals(2, len(res))
        self.assertTrue(self.tier[1] in res)
        self.assertTrue(self.tier[2] in res)
        values = res.get_value(self.tier[1])
        self.assertEquals(1, len(values))
        self.assertEquals("metby", values[0])
        values = res.get_value(self.tier[2])
        self.assertEquals(1, len(values))
        self.assertEquals("metby", values[0])

        # 'overlaps': [7,9]
        res = f.rel(self.rtier, "overlaps")
        self.assertEquals(1, len(res))
        ann = [a for a in res][0]
        self.assertEquals(self.tier[3], ann)
        values = res.get_value(ann)
        self.assertEquals(1, len(values))
        self.assertEquals("overlaps", values[0])

        # 'overlappedby': [7,9]
        res = f.rel(self.rtier, "overlappedby")
        self.assertEquals(1, len(res))
        ann = [a for a in res][0]
        self.assertEquals(self.tier[3], ann)
        values = res.get_value(ann)
        self.assertEquals(1, len(values))
        self.assertEquals("overlappedby", values[0])

        # 'after': all except the first interval
        res = f.rel(self.rtier, "after")
        self.assertEquals(5, len(res))
        self.assertFalse(self.tier[0] in res)
        self.assertTrue(self.tier[1] in res)
        self.assertTrue(self.tier[2] in res)
        self.assertTrue(self.tier[3] in res)
        self.assertTrue(self.tier[4] in res)
        self.assertTrue(self.tier[5] in res)

        # 'before': [0,3], [3,5], [5,7]
        res = f.rel(self.rtier, "before")
        self.assertEquals(3, len(res))
        self.assertTrue(self.tier[0] in res)
        self.assertTrue(self.tier[1] in res)
        self.assertTrue(self.tier[2] in res)
        self.assertFalse(self.tier[3] in res)
        self.assertFalse(self.tier[4] in res)
        self.assertFalse(self.tier[5] in res)

        with self.assertRaises(KeyError):
            f.rel(self.rtier, "relation")

    # -----------------------------------------------------------------------

    def test_combined_relations(self):

        f = sppasFilters(self.tier)
        res = f.rel(self.rtier, "overlaps", "overlappedby")
        self.assertEquals(1, len(res))
        ann = [a for a in res][0]
        self.assertEquals(self.tier[3], ann)
        values = res.get_value(ann)
        self.assertTrue(2, len(values))
        self.assertTrue("overlaps" in values)
        self.assertTrue("overlappedby" in values)

        f = sppasFilters(self.tier)
        res = f.rel(self.rtier, "overlaps", "overlappedby", overlap_min=1)
        self.assertEquals(1, len(res))
        values = res.get_value(ann)
        self.assertTrue(2, len(values))

        f = sppasFilters(self.tier)
        res = f.rel(self.rtier, "overlaps", "overlappedby", overlap_min=2)
        self.assertEquals(0, len(res))

        f = sppasFilters(self.tier)
        res = f.rel(self.rtier, "overlaps", "overlappedby", overlap_min=50, percent=True)
        self.assertEquals(1, len(res))

        # Add tests with after/before for a better testing of options and results
        # after/before: max_delay

