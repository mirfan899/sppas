#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
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
# File: predicate.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Tatsuya Watanabe, Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------


import operator

import _bools
import _relations

# ----------------------------------------------------------------------------

class Predicate(object):
    """

    Predicate allows to fix if an assumption is True or False.

    """
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

# ----------------------------------------------------------------------------

class RelationPredicate(Predicate):
    def __init__(self, pred):
        Predicate.__init__(self, pred)

    def __and__(self, other):
        raise Exception("& operator exception.")

# ----------------------------------------------------------------------------



# ----------------------------------------------------------------------------
# Predicates to filter Annotations
# ----------------------------------------------------------------------------


class Sel(object):
    """
    Predicate Factory.

    Sel is used to fix whether a label is valid or not.
    It is used on a text, a duration or on a time values.

    """
    def __new__(cls, **kwargs):
        """
        Create a Predicate.

        @param kwargs:

            exact (str):  label exact match
            iexact (str): label case-insensitive exact match
            startswith (str):
            istartswith (str): Case-insensitive startswith
            endswith (str):
            iendswith: Case-insensitive endswith
            contains (str):
            icontains: Case-insensitive contains
            regexp (str): regular expression

            begin_eq (float): begin time value equal to
            begin_lt (float): begin time value lower than
            begin_le (float):
            begin_gt (float):
            begin_ge (float):
            end_eq (float): end time value equal to
            end_lt (float): end time value lower than
            end_le (float):
            end_gt (float):
            end_ge (float):

            duration_eq (float): duration equal to
            duration_lt (float):
            duration_le (float):
            duration_gt (float):
            duration_ge (float):

            opt: option to be used while creating the function:
                "best": search on the best label only, and return true if it is matching the expected function
                "any": search in all labels, and return true if one of them is matching the expected function

        @returns: (Predicate)

        >>> # extract all pauses
        >>> pred = Sel(exact="#") | Sel(exact="+")

        >>> # extract long pauses
        >>> pred = (Sel(exact="#") | Sel(exact="+")) & Sel(duration_gt=200)

        """
        functions = []

        if not kwargs:
            functions.append(lambda a: True)

        opt="best"
        for func_name, param in kwargs.items():
            if func_name == "opt":
                opt = param

        for func_name, param in kwargs.items():
            if func_name != "opt":
                function = _bools.create(func_name, arg=param, opt=opt)
                functions.append(function)

        return reduce(operator.and_, (Predicate(f) for f in functions))

# ----------------------------------------------------------------------------


class Rel(object):
    """
    RelationPredicate Factory.

    Rel is used to fix whether an annotation is valid or not.
    It is used on the time-relation with another annotation.

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

        >>> p1 = Rel("overlaps") | Rel("overlappedby")
        >>> p2 = Rel("after", 0.5)

        """
        functions = []

        for r in args:
            func = _relations.create(r)
            functions.append(func)

        for k, v in kwargs.items():
            func = _relations.create(k, v)
            functions.append(func)

        return reduce(operator.or_, (RelationPredicate(f) for f in functions))

# ----------------------------------------------------------------------------
