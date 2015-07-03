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
#
# ---------------------------------------------------------------------------
# File: _bools.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Tatsuya Watanabe, Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------


#---------------------------------------------------------------
# Allen's interval relations
#---------------------------------------------------------------
# James Allen, in 1983, proposed an algebraic framework named Interval Algebra
# (IA), for qualitative reasoning with time intervals where the binary
# relationship between a pair of intervals is represented  by a subset of 13
# atomic relation.
#---------------------------------------------------------------


def before(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X precedes Y.
        X  |-------|
        Y                |-------|
    """
    return x2 < y1


def after(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X follows Y.
        X               |--------|
        Y |-------|
    """
    return y2 < x1


def meets(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X meets Y.
        X  |-------|
        Y          |-------|
    """
    return not equals(x1, x2, y1, y2) and x2 == y1


def metby(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X is met by Y.
        X         |-------|
        Y |-------|
    """
    return not equals(x1, x2, y1, y2) and x1 == y2


def overlaps(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X overlaps with Y.
        X |-------|
        Y     |------|
    """
    return x1 < y1 and y1 < x2 and x2 < y2


def overlappedby(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X overlapped by Y.
        X      |-------|
        Y |-------|
    """
    return y1 < x1 and x1 < y2 and y2 < x2


def starts(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X starts at the start of Y and finishes within it.
        X |----|
        Y |---------|
    """
    return x1 == y1 and x2 < y2


def startedby(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X is started at the start of Y interval.
        X |--------|
        Y |----|
    """
    return x1 == y1 and y2 < x2


def finishes(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X finishes at the y2 and within of Y.
        X     |----|
        Y |--------|
    """
    return y1 < x1 and x2 == y2


def finishedby(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X finished at the y2 of Y.
        X  |--------|
        Y      |----|
    """
    return x1 < y1 and x2 == y2


def during(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X is located during Y.
        X     |----|
        Y |------------|
    """
    return y1 < x1 and x2 < y2


def contains(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X contains Y.
        X  |------------|
        Y      |----|
    """
    return x1 < y1 and y2 < x2


def equals(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X equals Y.
        X |-------|
        Y |-------|
    """
    return x1 == y1 and x2 == y2

#---------------------------------------------------------------


#---------------------------------------------------------------
# INDU
#---------------------------------------------------------------
# Pujari, Kumari and Sattar proposed INDU: an Interval & Duration network.
# They extended the IA to model qualitative information about intervals and
# durations in a single binary constraint network.
# INDU comprises of 25 basic relations between a pair of two intervals.
#---------------------------------------------------------------


def lt(x1, x2, y1, y2):
    return (x2.GetMidpoint() - x1.GetMidpoint()) < (y2.GetMidpoint() - y1.GetMidpoint())


def gt(x1, x2, y1, y2):
    return (y2.GetMidpoint() - y1.GetMidpoint()) < (x2.GetMidpoint() - x1.GetMidpoint())


def eq(x1, x2, y1, y2):
    return (x2.GetMidpoint() - x1.GetMidpoint()) == (y2.GetMidpoint() - y1.GetMidpoint())

#---------------------------------------------------------------


#---------------------------------------------------------------
# Extension with meta-relations (just for convenience reasons)
#---------------------------------------------------------------


def disjoint(x1, x2, y1, y2):
    """
    Meta-relation for before, after, meets and metby.

    Before:
        X  |-------|
        Y              |-------|

    After:
        X              |--------|
        Y |-------|


    Meets:
        X  |-------|
        Y          |-------|

    Met by:
        X         |-------|
        Y |-------|

    """
    return before(x1, x2, y1, y2) or\
           after(x1, x2, y1, y2) or\
           meets(x1, x2, y1, y2) or\
           metby(x1, x2, y1, y2)


def convergent(x1, x2, y1, y2):
    """
    Meta-relation for starts, startedby, finishes, finishedby, overlaps,
    overlappedby, contains, during.

    Starts:
        X |--------|
        Y |----|

    Startedby:
        X |----|
        Y |---------|

    Finishes:
        X     |----|
        Y |--------|

    Finishedby:
        X  |-------|
        Y     |----|

    Contains:
        X  |------------|
        Y     |-----|

    During:
        X    |-----|
        Y |------------|

    Overlaps:
        X     |-------|
        Y |------|

    Overlappedby:
        X |-------|
        Y    |--------|

    """
    return startedby(x1, x2, y1, y2) or\
           finishedby(x1, x2, y1, y2) or\
           contains(x1, x2, y1, y2) or\
           overlaps(x1, x2, y1, y2) or\
           overlappedby(x1, x2, y1, y2) or\
           starts(x1, x2, y1, y2) or\
           finishes(x1, x2, y1, y2) or \
           during(x1, x2, y1, y2)

#---------------------------------------------------------------


#---------------------------------------------------------------
# Extension about duration (just for convenience reasons)
#---------------------------------------------------------------

def le(x1, x2, y1, y2):
    return (x2.GetMidpoint() - x1.GetMidpoint()) <= (y2.GetMidpoint() - y1.GetMidpoint())


def ge(x1, x2, y1, y2):
    return (y2.GetMidpoint() - y1.GetMidpoint()) <= (x2.GetMidpoint() - x1.GetMidpoint())

#---------------------------------------------------------------


#---------------------------------------------------------------
# Utils
#---------------------------------------------------------------

def split(x, y):
    """ x,y (Annotation) """
    if x.GetLocation().IsPoint():
        x1 = x.GetLocation().GetPoint()
        x2 = x.GetLocation().GetPoint()
    else:
        x1 = x.GetLocation().GetBegin()
        x2 = x.GetLocation().GetEnd()
    if y.GetLocation().IsPoint():
        y1 = y.GetLocation().GetPoint()
        y2 = y.GetLocation().GetPoint()
    else:
        y1 = y.GetLocation().GetBegin()
        y2 = y.GetLocation().GetEnd()
    return x1, x2, y1, y2


def min_overlap(x1, x2, y1, y2, minoverlap):
    if x1 > y1:
        x1, x2, y1, y2 = y1, y2, x1, x2
    if x2 <= y1:
        return False
    return x2.GetMidpoint() - y1.GetMidpoint() >= minoverlap


def max_delay(x1, x2, y1, y2, maxdelay):
    if x1 > y1:
        x1, x2, y1, y2 = y1, y2, x1, x2
    if x2 >= y1:
        return False
    return y1.GetMidpoint() - x2.GetMidpoint() <= maxdelay


#---------------------------------------------------------------
# Predicate factory function
#---------------------------------------------------------------


def create(name, *args):
    """
       @param name: (str)
            'before'
            'before_eq'
            'before_ge'
            'before_gt'
            'before_le'
            'before_lt'
            'after'
            'after_eq'
            'after_ge'
            'after_gt'
            'after_le'
            'after_lt'
            'meets'
            'meets_eq'
            'meets_ge'
            'meets_gt'
            'meets_le'
            'meets_lt'
            'metby'
            'metby_eq'
            'metby_ge'
            'metby_gt'
            'metby_le'
            'metby_lt'
            'overlaps'
            'overlaps_eq'
            'overlaps_ge'
            'overlaps_gt'
            'overlaps_le'
            'overlaps_lt'
            'overlappedby'
            'overlappedby_eq'
            'overlappedby_ge'
            'overlappedby_gt'
            'overlappedby_le'
            'overlappedby_lt'
            'starts'
            'startedby'
            'contains'
            'during'
            'finishes'
            'finishedby'
            'disjoint'
            'convergent'
            'equals'
        @param args:

    """
    module = globals()
    functions = name.split('_')
    q = []
    extra = None

    if len(functions) == 2:
        func = functions[0]
        indu = functions[1]
    else:
        func = functions[0]
        indu = None

    allen = module.get(func, None)
    if not allen:
        raise Exception("Unknown relation: %s" % name)
    else:
        q.append(allen)

    if indu:
        indu = module.get(indu, None)
        if not indu:
            raise Exception("Unknown relation: %s" % name)
        q.append(indu)

    if args:
        if allen.__name__ in ("before", "after"):
            extra = max_delay
        elif allen.__name__ in ("overlaps", "overlappedby"):
            extra = min_overlap

    def wrap(X, Y, *opt, **kwopt):
        x1, x2, y1, y2 = split(X, Y)
        ret = all(f(x1, x2, y1, y2) for f in q)
        if extra:
            ret = ret and extra(x1, x2, y1, y2, *args)

        # Return relation name if ret
        return allen.__name__ if ret else ret

    wrap.__name__ = allen.__name__
    wrap.__doc__ = allen.__doc__
    return wrap

#---------------------------------------------------------------
