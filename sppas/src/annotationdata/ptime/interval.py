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
#       Copyright (C) 2011-2014  Tatsuya Watanabe
#       Copyright (C) 2014-2015  Brigitte Bigi
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
# File: interval.py
# ----------------------------------------------------------------------------

import logging
import baseplacement
import duration
from point import TimePoint

# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

class TimeInterval(baseplacement.BasePlacement):
    """
    @author:  Brigitte Bigi, Tatsuya Watanabe
    @contact: brigitte.bigi@gmail.com
    @license: GPL, version 3
    @summary: This class is the TimeInterval representation.

    A time interval is identified by two TimePoint objects:
        - a begin time;
        - an end time.

    """

    def __init__(self, begin, end):
        """
        Create a new TimeInterval instance.

        @param begin (TimePoint) start time in seconds
        @param end (TimePoint) end time in seconds
        @raise TypeError:
        @raise ValueError

        """

        if isinstance(begin, TimePoint) is False:
            raise TypeError(
                "TimePoint argument required for begin, not %r" % begin)

        if isinstance(end, TimePoint) is False:
            raise TypeError(
                "TimePoint argument required for end, not %r" % end)

        if(
            begin.GetMidpoint() >= end.GetMidpoint() or (
                begin.GetMidpoint()-begin.GetRadius() >
                end.GetMidpoint()-end.GetRadius())
        ):
            raise ValueError(
                "End TimePoint must be greater than Begin TimePoint"
                "(%s, %s)" % (begin, end))
        elif begin >= end:
            logging.info('[WARNING] begin >= end with (%s, %s)' % (begin, end))

        self.__begin = begin
        self.__end = end

    # -----------------------------------------------------------------------

    def Set(self, other):
        """
        Set the TimeInterval instance to new TimeInterval.
        Attention: it is a value assignment (other is copied).

        @param other (TimeInterval)

        """
        if isinstance(other, TimeInterval) is False:
            raise TypeError("TimeInterval argument required, not %r" % other)

        other = other.Copy()
        self.__begin = other.__begin
        self.__end = other.__end

    # -----------------------------------------------------------------------

    def GetBegin(self):
        """
        Return the begin TimePoint instance.
        Recommended to use carefully (not to set something)!

        """
        return self.__begin

    # -----------------------------------------------------------------------

    def SetBegin(self, tp):
        """
        Set the begin TimePoint instance to a new TimePoint.

        Attention: it is a reference assignment.
        Different usage:
            - interval.SetBegin( tp )
            - interval.SetBegin( tp.Copy() )

        @param tp (TimePoint)

        """
        if isinstance(tp, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % tp)

        if(
            tp.GetMidpoint() >= self.__end.GetMidpoint() or (
                tp.GetMidpoint()-tp.GetRadius() >
                self.__end.GetMidpoint()-self.__end.GetRadius())
        ):
            raise ValueError(
                "Begin must be strictly lesser than End in TimeInterval. "
                "(%s, %s)" % (tp, self.__end))

        self.__begin = tp  # assign the reference

    # -----------------------------------------------------------------------

    def GetEnd(self):
        """
        Return the end TimePoint instance.

        """
        return self.__end

    # -----------------------------------------------------------------------

    def SetEnd(self, tp):
        """
        Set the end TimePoint instance to a new TimePoint.

        Attention: it is a reference assignment.
        Usage:
            - interval.SetEnd( tp )
            - interval.SetEnd( tp.Copy() )

        @param time (TimePoint)

        """
        if isinstance(tp, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % tp)

        if (
            self.__begin.GetMidpoint() >= tp.GetMidpoint() or (
                self.__begin.GetMidpoint()-self.__begin.GetRadius() >
                tp.GetMidpoint()-tp.GetRadius())
        ):
            raise ValueError(
                "End must be strictly greater than Begin in TimeInterval."
                " (%s, %s)" % (self.__begin, tp))

        # assign the reference
        self.__end = tp

    # -----------------------------------------------------------------------

    def IsInterval(self):
        """
        Return True, because self is representing an interval.

        """
        return True

    # -----------------------------------------------------------------------

    def IsTimeInterval(self):
        """
        Return True, because self is an instance of TimeInterval.

        """
        return True

    # -----------------------------------------------------------------------

    def Copy(self):
        """
        Return a deep copy of self.

        """
        b = self.__begin.Copy()
        e = self.__end.Copy()
        return TimeInterval(b, e)

    # -----------------------------------------------------------------------

    def Duration(self):
        """
        Return the duration of the interval, in seconds.

        """
        # duration is the difference between the midpoints
        value = self.__end.GetMidpoint() - self.__begin.GetMidpoint()
        # vagueness of the duration is based on begin/end radius values
        vagueness = self.__begin.GetRadius() + self.__end.GetRadius()

        return duration.Duration(value,vagueness)

    # -----------------------------------------------------------------------

    def Combine(self, other):
        """
        Return a TimeInterval, the combination of two intervals.

        @param other (TimeInterval) is the other time interval
        to be combined with.

        """
        if isinstance(other, TimeInterval) is False:
            raise TypeError("TimeInterval argument required, not %r" % other)

        if self > other:
            other, self = self, other

        if self.__end <= other.GetBegin():
            return TimeInterval(self.__begin, other.GetEnd())

        return TimeInterval(other.GetBegin(), self.__end)

    # -----------------------------------------------------------------------

    def Union(self, other):
        """
        Return a TimeInterval representing the union of two intervals.

        @param other (TimeInterval) is the interval to merge with.

        """
        if isinstance(other, TimeInterval) is False:
            raise TypeError("TimeInterval argument required, not %r" % other)

        if self > other:
            other, self = self, other

        return TimeInterval(self.__begin, other.GetEnd())

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return "TimeInterval: [%s,%s]" % (self.__begin, self.__end)

        return "[%s,%s]" % (self.__begin, self.__end)

    # -----------------------------------------------------------------------

    def __contains__(self, other):
        """
        Return True if the given time point is contained in the interval.

        @param other is the other time point to compare with.

        """
        if isinstance(other, (TimeInterval, TimePoint, float, int,)) is False:
            raise TypeError("%r cannot be compared with TimeInterval." % other)

        if isinstance(other, TimeInterval):
            return (self.__begin <= other.GetBegin() and
                    other.GetEnd() <= self.__end)

        return self.__begin <= other <= self.__end

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """
        Equal.

        @param other (TimeInterval) is the other time point to compare with.

        """
        if isinstance(other, TimeInterval) is False:
            return False

        return (self.__begin == other.GetBegin() and
                self.__end == other.GetEnd())

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """
        LowerThan.

        @param other (TimeInterval, TimePoint, float, int)
        is the other time point to compare with.

        """
        if isinstance(other, (TimePoint, float, int)):
            return self.__end < other

        if isinstance(other, TimeInterval) is False:
            return False

        return self.__begin < other.GetBegin()

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """
        GreaterThan.

        @param other (TimeInterval, TimePoint, float, int)
        is the other time point to compare with.

        """
        if isinstance(other, (int, float, TimePoint)):
            return self.__begin > other

        if isinstance(other, TimeInterval) is False:
            return False

        return self.__begin > other.GetBegin()

    # -----------------------------------------------------------------------
