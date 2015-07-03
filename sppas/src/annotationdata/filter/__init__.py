#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2013-2014  Tatsuya Watanabe
#       Copyright (C) 2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------------
#

import itertools
import operator
from annotationdata.tier import Tier
from annotationdata.ptime.interval import TimeInterval

import _bools
import _relations


class Predicate(object):

    def __init__(self, pred):
        """
        >>> pred = Predicate(lambda x: x % 3 == 0) | Predicate(lambda x: x % 5 == 0)
        >>> [x for x in range(16) if pred(x)]
        [0, 3, 5, 6, 9, 10, 12, 15]

        >>> pred = Predicate(lambda x: x % 3 == 0) & Predicate(lambda x: x % 5 == 0)
        >>> [x for x in range(16) if pred(x)]
        [0, 15]
        """
        self.pred = pred

    def __call__(self, *args, **kwargs):
        return self.pred(*args, **kwargs)

    def __or__(self, other):
        def func(*args, **kwargs):
            return self(*args, **kwargs) or other(*args, **kwargs)
        func.__name__ = "%s OR %s" % (str(self), str(other))
        return Predicate(func)

    def __and__(self, other):
        def func(*args, **kwargs):
            return self(*args, **kwargs) and other(*args, **kwargs)
        func.__name__ = "%s AND %s" % (str(self), str(other))
        return Predicate(func)

    def __invert__(self):
        def func(*args, **kwargs):
            return not self(*args, **kwargs)
        func.__name__ = "NOT (%s)" % (str(self),)
        return Predicate(func)

    def __str__(self):
        return self.pred.__name__


class RelationPredicate(Predicate):
    def __init__(self, pred):
        Predicate.__init__(self, pred)

    def __and__(self, other):
        raise Exception("& operator exception.")


class Bool(object):
    """
    Predicate Factory.
    """
    def __new__(cls, **kwargs):
        """
        Create a Predicate.

        @param kwargs:
            exact (str): exact match
            iexact (str): Case-insensitive exact match
            startswith (str):
            istartswith (str): Case-insensitive startswith
            endswith (str):
            iendswith: Case-insensitive endswith
            contains (str):
            icontains: Case-insensitive contains
            regexp (str): regular expression
            begin_lt (float):
            begin_le (float):
            begin_gt (float):
            begin_ge (float):
            begin_eq (float):
            end_lt (float):
            end_le (float):
            end_gt (float):
            end_ge (float):
            end_eq (float):
            duration_lt (float):
            duration_le (float):
            duration_gt (float):
            duration_ge (float):
            duration_eq (float):

        @returns: (Predicate)

        >>> # extract pauses.
        >>> pred = Bool(exact="#") | Bool(exact="+")
        >>> annotations = [a for a in tier if pred(a)]
        >>> # extract long pauses.
        >>> pred = Bool(exact="#") & Bool(duration_gt=200)
        >>> annotations = [a for a in tier if pred(a)]

        """
        functions = []
        if not kwargs:
            functions.append(lambda a: True)
        for func_name, param in kwargs.items():
            function = _bools.create(func_name, param)
            functions.append(function)
        return reduce(operator.and_, (Predicate(f) for f in functions))


class Rel(object):
    """
    RelationPredicate Factory.
    """
    def __new__(cls, *args, **kwargs):
        """
        Create a RelationPredicate.
        @param args:
            meets (str):
            meets_eq (str):
            meets_ge (str):
            meets_gt (str):
            meets_le (str):
            meets_lt (str):
            metby (str):
            metby_eq (str):
            metby_ge (str):
            metby_gt (str):
            metby_le (str):
            metby_lt (str):
            overlaps (str):
            overlaps_eq (str):
            overlaps_ge (str):
            overlaps_gt (str):
            overlaps_le (str):
            overlaps_lt (str):
            overlappedby (str):
            overlappedby_eq (str):
            overlappedby_ge (str):
            overlappedby_gt (str):
            overlappedby_le (str):
            overlappedby_lt (str):
            starts (str):
            startedby (str):
            contains (str):
            during (str):
            finishes (str):
            finishedby (str):
            disjoint (str):
            convergent (str):
            equals (str):

        @param kwargs:
            after (float):
            after_eq (float):
            after_ge (float):
            after_gt (float):
            after_le (float):
            after_lt (float):
            before (float):
            before_eq (float):
            before_ge (float):
            before_gt (float):
            before_le (float):
            before_lt (float):

        @return: predicate (RelationPredicate)

        >>> f = tier1.Link(tier2, Rel("overlaps") | Rel("overlappedby"))
        >>> new_tier = f.Filter()
        """
        functions = []
        for r in args:
            func = _relations.create(r)
            functions.append(func)
        for k, v in kwargs.items():
            func = _relations.create(k, v)
            functions.append(func)
        return reduce(operator.or_, (RelationPredicate(f) for f in functions))



class FilterFactory(object):
    """
    @deprecated
    """
    def __new__(cls, tier, *predicate, **kwargs):
        """
        Create a Filter.
        @param tier: (Tier)
        @param predicate: (Predicate)
        @param kwargs:
        @return: (Filter)
        """
        if not predicate and not kwargs:
            predicate = Bool(**kwargs)
        elif kwargs:
            predicate = Bool(**kwargs)
        elif not isinstance(predicate[0], Predicate):
            raise Exception("Invalid argument %s" % predicate[0])
        else:
            predicate = predicate[0]

        f = Filter(tier)
        return f.Label(predicate)



class Filter(object):
    def __init__(self, tier):
        """
        @param tier: (Tier)
        """
        self.tier = tier

    def __iter__(self):
        for x in self.tier:
            yield x

    def Label(self, predicate):
        """
        @deprecated
        """
        return LabelFilter(predicate, self)

    def Link(self, other, relation):
        """
        @deprecated

        @param other:(Filter)
        @param relation: (RelationPredicate)
        @return: (RelationFilter)
        """
        return RelationFilter(relation, self, other)


    def Filter(self):
        """
        @return: (Tier)
        """
        tier = Tier()
        for x in self:
            try:
                tier.Add(x.Copy())
            except:
                pass
        return tier


class LabelFilter(Filter):
    """
    Create a filter on labels of another filter.
    """
    def __init__(self, predicate, filter):
        """
        @param predicate (Predicate)
        @param filter (either: Filter, LabelFilter, RelationFilter)

        """
        self.filter = filter
        self.predicate = predicate

    def __iter__(self):
        for x in self.filter:
            if self.predicate(x):
                yield x

    def Filter(self):
        """
        @return: (Tier)
        """
        tier = Tier()
        for x in self:
            try:
                tier.Add(x.Copy())
            except:
                pass
        return tier


class RelationFilter(Filter):
    """
    Create a filter on relations between 2 filters.
    """
    def __init__(self, relation, filter1, filter2):
        """
        @param relation: (RelationPredicate)
        @param filter1: (Filter)
        @param filter2: (Filter)
        """
        self.pred = relation
        self.filter1 = filter1
        self.filter2 = filter2

    def __iter__(self):
        if not isinstance(self.filter1, RelationFilter):
            f1 = [x for x in self.filter1 if not x.GetLabel().IsEmpty()]
        else:
            f1 = [x[0] for x in self.filter1]
        if not isinstance(self.filter2, RelationFilter):
            f2 = [x for x in self.filter2 if not x.GetLabel().IsEmpty()]
        else:
            f2 = [x[0] for x in self.filter2]
        for x in f1:
            for y in f2:
                ret = self.pred(x, y)
                if ret:
                    yield x, ret

    def Filter(self, replace=False):
        """
        @return: (Tier)
        """
        tier = Tier()
        if replace:
            for x, label in self:
                a = x.Copy()
                a.GetLabel().SetValue( label )
                try:
                    tier.Append(a)
                except:
                    e = tier[-1]
                    e.GetLabel().SetValue( e.GetLabel().GetValue() + " | %s" % label)
        else:
            for x, label in self:
                x = x.Copy()
                try:
                    tier.Append(x)
                except:
                    pass
        return tier

