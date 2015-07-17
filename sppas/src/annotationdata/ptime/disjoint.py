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
# File: disjoint.py
# ----------------------------------------------------------------------------

import baseplacement

from point import TimePoint
from interval import TimeInterval

__docformat__ = """epytext"""
__authors__ = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


class TimeDisjoint(baseplacement.BasePlacement):
    """
    @author:  Brigitte Bigi, Tatsuya Watanabe
    @contact: brigitte.bigi@gmail.com
    @license: GPL, version 3
    @summary: This class is the TimeDisjoint representation.

    Represents a sequence of time intervals.

    """

    def __init__(self, *intervals):
        """
        Creates a new TimeDisjoint instance.

        @param intervals (sequence of TimeInterval)

        @raise TypeError

        """

        if not intervals:
            raise TypeError(
                "TimeDisjoint constructor requires a sequence of TimeInterval")

        if not all(isinstance(i, TimeInterval) for i in intervals):
            raise TypeError(
                "TimeDisjoint constructor requires a sequence of TimeInterval")

        self.__intervals = list(intervals)

    # End __init__
    # --------------------------------------------------------------------------------

    def GetSize(self):
        """
        Return the number of time intervals (int).

        """
        return len(self.__intervals)

    # End GetSize
    # ------------------------------------------------------------------------------------

    def GetBegin(self):
        """
        Return the begin TimePoint instance.

        """
        # get the first interval (interval starting the first)
        _min = min(interval for interval in self.__intervals)

        return _min.GetBegin()

    # End GetBegin
    # ------------------------------------------------------------------------------------

    def SetBegin(self, time):
        """
        Set the begin TimePoint instance to new TimePoint.

        @param time (TimePoint)

        """
        _min = min(interval for interval in self.__intervals)

        _min.SetBegin(time)

    # End SetBegin
    # ------------------------------------------------------------------------------------

    def GetEnd(self):
        """
        Return the end TimePoint instance.

        """
        # get the last interval (interval ending the last)
        _max = max(interval for interval in self.__intervals)

        return _max.GetEnd()

    # End GetEnd
    # ------------------------------------------------------------------------------------

    def SetEnd(self, time):
        """
        Set the end TimePoint instance to new TimePoint.

        @param time (TimePoint)

        """
        # get the last interval (interval ending the last)
        _max = max(interval for interval in self.__intervals)

        _max.SetEnd(time)

    # End SetEnd
    # ------------------------------------------------------------------------------------

    def GetInterval(self, index):
        """
        Return the TimeInterval corresponding to the given index.

        @param index (int)

        """
        return self.__intervals[index]

    # End GetInterval
    # ------------------------------------------------------------------------------------

    def IsDisjoint(self):
        """
        Return True as this object is representing Disjoint intervals.

        """
        return True

    # End IsDisjoint
    # ------------------------------------------------------------------------------------

    def IsTimeDisjoint(self):
        """
        Return True as this object is an instance of TimeDisjoint.

        """
        return True

    # End IsTimeDisjoint
    # ------------------------------------------------------------------------------------

    def Duration(self):
        """
        Return the duration, in seconds, from Begin to End,
        without taking radius into account.

        """
        return sum(interval.Duration() for interval in self.__intervals)

    # End Duration
    # ------------------------------------------------------------------------------------

    def Append(self, interval):
        self.__intervals.append(interval)

    # End Append
    # ------------------------------------------------------------------------------------

    def __repr__(self):
        return "TimeDisjoint: {%s}" % ("".join([str(i)
                                                for i in self.__intervals]))

        return "{%s}" % ("".join([str(i) for i in self.__intervals]))

    # End __repr__
    # ------------------------------------------------------------------------------------

    def __eq__(self, other):
        """
        Equal is required to use '==' between 2 TimeDisjoint instances.
        Two disjoint instances are equals iff all its intervals are equals.

        @param other (TimeDisjoint) is the other time disjoint to compare with.

        """
        if not isinstance(other, TimeDisjoint):
            return False

        if self.GetSize() != other.GetSize():
            return False

        return all(self.GetInterval(i) == other.GetInterval(i)
                   for i in range(self.GetSize()))

    # End __eq__
    # ------------------------------------------------------------------------------------

    def __lt__(self, other):
        """
        LowerThan is required to use '<' between 2 TimeDisjoint instances.

        @param  other: (TimeDisjoint) is the other time point to compare with.

        """
        if isinstance(other, (TimePoint, float, int)):
            return self.GetEnd() < other

        if isinstance(other, (TimeInterval, TimeDisjoint)) is False:
            return False

        return self.GetBegin() < other.GetBegin()

    # End __lt__
    # ------------------------------------------------------------------------------------

    def __gt__(self, other):
        """
        GreaterThan is required to use '>' between 2 TimeDisjoint instances.

        @param other: (TimeDisjoint) is the other time point to compare with.

        """
        if isinstance(other, (int, float, TimePoint)):
            return self.GetBegin() > other

        if isinstance(other, (TimeInterval, TimeDisjoint)) is False:
            return False

        return self.GetBegin() > other.GetBegin()

    # End __gt__
    # ------------------------------------------------------------------------------------

    def __iter__(self):
        for a in self.__intervals:
            yield a

    # End __iter__
    # ------------------------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__intervals[i]

    # End __getitem__
    # ------------------------------------------------------------------------------------

    def __len__(self):
        return len(self.__intervals)

    # End __len__
    # ------------------------------------------------------------------------------------

# End TimeDisjoint
# ------------------------------------------------------------------------------------