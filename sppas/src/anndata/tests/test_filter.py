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


class TestTagMatching(unittest.TestCase):
    """ Test pattern matching on tags. """

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
        start_time = time.time()
        res = f.dur(eq=0.03)
        end_time = time.time()

        # phonemes during more than 200ms
        start_time = time.time()
        res = f.dur(ge=0.2)
        end_time = time.time()

    # -----------------------------------------------------------------------

    def test_combined(self):
        """ Test both tag and duration. """

        tier = self.trs.find('P-Phonemes')
        f = sppasFilters(tier)

        # silences or pauses during more than 200ms
        res = (f.tag(exact=u("#")) or f.tag(exact=u("+"))) and f.dur(ge=0.2)

# ---------------------------------------------------------------------------

