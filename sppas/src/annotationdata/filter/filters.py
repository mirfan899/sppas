#!/usr/bin/env python
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
#
# ---------------------------------------------------------------------------
# File: filters.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Tatsuya Watanabe, Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

from annotationdata.tier import Tier

from predicate import Predicate,RelationPredicate,Sel,Rel

# ----------------------------------------------------------------------------

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
            predicate = Sel(**kwargs)
        elif kwargs:
            predicate = Sel(**kwargs)
        elif not isinstance(predicate[0], Predicate):
            raise Exception("Invalid argument %s" % predicate[0])
        else:
            predicate = predicate[0]

        f = Filter(tier)
        return f.Label(predicate)

# ----------------------------------------------------------------------------


class Filter(object):
    """
    Create an empty Filter.

    >>> f = Filter(tier)
    >>> copytier = f.Filter()

    """
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
        return SingleFilter(predicate, self)

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
        Filter the given tier without any predicate: simply copy the tier!

        @return: (Tier)

        """
        tier = Tier()
        for x in self.tier:
            try:
                tier.Add(x.Copy())
            except:
                pass
        return tier

# ----------------------------------------------------------------------------


class SingleFilter(Filter):
    """
    Create a filter on a single filter.

    >>> f = Filter(tier)
    >>> p = Sel(exact='foo') | Sel(exact='bar') & Sel(duration_le=0.2)
    >>> sf = SingleFilter(p,f)
    >>> newtier = sf.Filter()

    """
    def __init__(self, predicate, filter):
        """
        Constructor for SingleFilter, a filter on a single tier.

        @param predicate (Predicate)
        @param filter (either: Filter, SingleFilter, RelationFilter)

        """
        self.filter = filter
        self.predicate = predicate


    def __iter__(self):
        for x in self.filter:
            if self.predicate(x):
                yield x

    # -----------------------------------------------------------------------

    def Filter(self):
        """
        Apply the predicate on all annotations of the tier defined in the filter.

        @return: (Tier)

        """
        tier = Tier()
        for x in self:
            try:
                tier.Add(x.Copy())
            except:
                pass
        return tier

    # -----------------------------------------------------------------------

# ----------------------------------------------------------------------------


class RelationFilter(Filter):
    """
    Create a filter on relations between 2 filters.

    >>> fX = Filter(tier1)
    >>> fY = Filter(tier2)
    >>> p = Rel("overlaps") | Rel("overlappedby")
    >>> rf = RelationFilter(p,fX,fY)
    >>> newtier = rf.Filter()

    """

    def __init__(self, relation, filter1, filter2):
        """
        Constructor for RelationFilter, a filter on relations between 2 filters.

        @param relation: (RelationPredicate)
        @param filter1: (either: Filter, SingleFilter, RelationFilter)
        @param filter2: (either: Filter, SingleFilter, RelationFilter)

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

    # -----------------------------------------------------------------------

    def Filter(self, replace=False):
        """
        Apply the predicate on all annotations of the tier defined in the filter.

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

    # -----------------------------------------------------------------------

# ----------------------------------------------------------------------------
