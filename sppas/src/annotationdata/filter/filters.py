#!/usr/bin/env python2
# vim: set fileencoding=UTF-8 ts=4 sw=4 expandtab:
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
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

__authors__   = """Tatsuya Watanabe, Brigitte Bigi (brigitte.bigi@gmail.com), Grégoire Montcheuil"""
__copyright__ = """Copyright (C) 2011-2017 Brigitte Bigi"""

# ----------------------------------------------------------------------------

from ..tier import Tier

from .predicate import Sel
from .predicate import Rel

# ----------------------------------------------------------------------------


class Filter(object):
    """ Create an empty Filter.

    >>> f = Filter(tier)
    >>> copytier = f.Filter()

    """
    def __init__(self, tier, unfill=False):
        """
        :param tier: (Tier)
        :param unfill: (bool) Remove empty labels.

        """
        self.tier = tier
        self.unfill = unfill

    def __iter__(self):
        for x in self.tier:
            if self.unfill is False:
                yield x
            else:
                if x.GetLabel().IsEmpty() is False:
                    yield x

    def Filter(self):
        """ Filter the given tier without any predicate: simply copy the tier!

        :returns: (Tier)

        """
        tier = Tier()
        tier.SetSherableProperties(self.tier)
        for x in self:
            try:
                tier.Add(x.Copy())
            except:
                pass
        return tier

# ----------------------------------------------------------------------------


class SingleFilter(Filter):
    """ Create a filter on a single filter.

    >>> f = Filter(tier)
    >>> p = Sel(exact='foo') | Sel(exact='bar') & Sel(duration_le=0.2)
    >>> sf = SingleFilter(p, f)
    >>> newtier = sf.Filter()

    """
    def __init__(self, predicate, filter):
        """ Constructor for SingleFilter, a filter on a single tier.

        :param predicate: (Predicate)
        :param filter: (either: Filter, SingleFilter, RelationFilter)

        """
        Filter.__init__(self, filter.tier)
        self.filter = filter
        self.predicate = predicate

    def __iter__(self):
        for x in self.filter:
            if self.predicate(x):
                yield x

    # -----------------------------------------------------------------------

    def Filter(self):
        """ Apply the predicate on all annotations of the tier defined in the filter.

        :returns: (Tier)

        """
        tier = Tier(self.filter.tier.GetName()+"SingleFilter")
        tier.SetSherableProperties(self.filter.tier)
        for x in self:
            try:
                tier.Add(x.Copy())
            except:
                pass
        return tier

# ----------------------------------------------------------------------------


class RelationFilter():
    """ Create a filter on relations between 2 filters.

    >>> fX = Filter(tier1)
    >>> fY = Filter(tier2)
    >>> p = Rel("overlaps") | Rel("overlappedby")
    >>> rf = RelationFilter(p, fX, fY)
    >>> newtier = rf.Filter()	# the new tier annotations have X's label
    >>> newtier2 = rf.Filter(annotformat="{x} {rel} {y}")	# the new tier annotations' labels show the X-Y relation

    """
    def __init__(self, relation, filter1, filter2):
        """ Constructor for RelationFilter, a filter on relations between 2 filters.

        :param relation: (RelationPredicate)
        :param filter1: (either: Filter, SingleFilter, RelationFilter)
        :param filter2: (either: Filter, SingleFilter, RelationFilter)

        """
        self.pred = relation
        self.filter1 = filter1
        self.filter2 = filter2

    # -----------------------------------------------------------------------

    def __iter__(self):
        """ Iterator

        :returns: a tuple (x, rel, y) with the annotations and their relation (type: (Annotation, string, Annotation))

        """
        if isinstance(self.filter1, RelationFilter) is False:
            f1 = [x for x in self.filter1 if not x.GetLabel().IsEmpty()]
        else:  # as RelationFilter iterator return a tuple (x, rel, y), we get the 1st value
            f1 = [x[0] for x in self.filter1]

        if isinstance(self.filter2, RelationFilter) is False:
            f2 = [x for x in self.filter2 if not x.GetLabel().IsEmpty()]
        else:  # as RelationFilter iterator return a tuple (x, rel, y), we get the 1st value
            f2 = [x[0] for x in self.filter2]

        for x in f1:
            for y in f2:
                ret = self.pred(x, y)
                if ret:
                    yield x, ret, y

    # -----------------------------------------------------------------------

    def Filter(self, annotformat="{x}"):
        """ Apply the predicate on all annotations of the tier defined in the filter.

        :type annotformat:	str
        :param annotformat:	format of the resulting annotation label.
            Use {x}, {y} for each annotation's label and {rel} for the relation.
            By default we keep the x label (equivalent to "{x}").

        :returns: (Tier)

        """
        n = ""
        if isinstance(self.filter1, RelationFilter) is False:
            n = self.filter1.tier.GetName()
        n += "Relation"
        if isinstance(self.filter2, RelationFilter) is False:
            n += self.filter2.tier.GetName()
        tier = Tier(n)
        if isinstance(self.filter1, RelationFilter) is False:
            tier.SetSherableProperties(self.filter1.tier)

        i = 0
        # feed the tier
        for x, rel, y in self:
            a = x.Copy()
            annot_label = annotformat.format(x=x.GetLabel(), rel=rel, y=y.GetLabel())
            a.GetLabel().SetValue(annot_label)
            try:
                tier.Append(a)
            except:
                if "{rel}" in annotformat and i > 1:
                    annot_label = annotformat.format(x=x.GetLabel(), rel=rel, y=y.GetLabel())
                    e = tier[-1]
                    label = e.GetLabel().GetValue()
                    e.GetLabel().SetValue(label + " | %s" % annot_label)
                pass
            i += 1
        return tier

# ----------------------------------------------------------------------------
