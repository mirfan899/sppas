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
#       Copyright (C) 2011-2015  Brigitte Bigi
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
# File: framedisjoint.py
# ----------------------------------------------------------------------------

import baseplacement

from framepoint import FramePoint
from frameinterval import FrameInterval

__docformat__ = """epytext"""
__authors__ = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


class FrameDisjoint(baseplacement.BasePlacement):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, version 3
    @summary: This class is the FrameDisjoint representation.

    Represents a sequence of frame intervals.

    """

    def __init__(self, *intervals):
        """
        Creates a new FrameDisjoint instance.

        @param intervals (sequence of FrameInterval)

        @raise TypeError

        """
        if not intervals:
            raise TypeError(
                "FrameDisjoint constructor requires"
                "a sequence of FrameInterval.")

        if not all(isinstance(i, FrameInterval) for i in intervals):
            raise TypeError(
                "FrameDisjoint constructor requires"
                "a sequence of FrameInterval.")

        self.__intervals = list(intervals)

    # End __init__
    # ------------------------------------------------------------------------------------

    def GetSize(self):
        """
        Return the number of intervals (int).

        """
        return len(self.__intervals)

    # End GetSize
    # ------------------------------------------------------------------------------------

    def GetBegin(self):
        """
        Return the begin FramePoint instance.

        """
        # get the first interval (interval starting the first)
        _min = min(interval for interval in self.__intervals)

        return _min.GetBegin()

    # End GetBegin
    # ------------------------------------------------------------------------------------

    def SetBegin(self, frame):
        """
        Set the begin FramePoint instance to new FramePoint.

        @param frame (FramePoint)

        """
        _min = min(interval for interval in self.__intervals)

        _min.SetBegin(frame)

    # End SetBegin
    # ------------------------------------------------------------------------------------

    def GetEnd(self):
        """
        Return the end FramePoint instance.

        """
        # get the last interval (interval ending the last)
        _max = max(interval for interval in self.__intervals)

        return _max.GetEnd()

    # End GetEnd
    # ------------------------------------------------------------------------------------

    def SetEnd(self, frame):
        """
        Set the end FramePoint instance to new FramePoint.

        @param frame (FramePoint)

        """
        # get the last interval (interval ending the last)
        _max = max(interval for interval in self.__intervals)

        _max.SetEnd(frame)

    # End SetEnd
    # ------------------------------------------------------------------------------------

    def GetInterval(self, index):
        """
        Return the FrameInterval corresponding to the given index.

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

    def IsFrameDisjoint(self):
        """
        Return True as this object is an instance of FrameDisjoint.

        """
        return True

    # End IsFrameDisjoint
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
        return "FrameDisjoint: {%s}" % ("".join([str(i)
                                                 for i in self.__intervals]))

    # End __repr__
    # ------------------------------------------------------------------------------------

    def __str__(self):
        return "{%s}" % ("".join([str(i) for i in self.__intervals]))

    # End __str__
    # ------------------------------------------------------------------------------------

    def __eq__(self, other):
        """
        Equal.

        @param other (FrameDisjoint)
        is the other frame disjoint to compare with.

        """
        if not isinstance(other, FrameDisjoint):
            return False

        if self.GetSize() != other.GetSize():
            return False

        return all(self.GetInterval(i) == other.GetInterval(i)
                   for i in range(self.GetSize()))

    # End __eq__
    # ------------------------------------------------------------------------------------

    def __lt__(self, other):
        """
        LowerThan.

        @param  other (FrameDisjoint) is the other frame point to compare with.

        """
        if isinstance(other, (FramePoint, float, int)):
            return self.End < other

        if isinstance(other, (FrameInterval, FrameDisjoint)) is False:
            return False

        return self.GetBegin() < other.GetBegin()

    # End __lt__
    # ------------------------------------------------------------------------------------

    def __gt__(self, other):
        """
        GreaterThan is required to use '>' between 2 FrameDisjoint instances.

        @param other: (FrameDisjoint) is the other frame point to compare with.

        """
        if isinstance(other, (int, FramePoint)):
            return self.GetBegin() > other

        if isinstance(other, (FrameInterval, FrameDisjoint)) is False:
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

# End FrameDisjoint
# ------------------------------------------------------------------------------------
