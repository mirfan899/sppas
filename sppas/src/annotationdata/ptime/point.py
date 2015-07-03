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
# File: point.py
# ----------------------------------------------------------------------------

import baseplacement
from ..utils.deprecated import deprecated


__docformat__ = """epytext"""
__authors__ = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


class TimePoint(baseplacement.BasePlacement):
    """
    @author:  Brigitte Bigi, Tatsuya Watanabe
    @contact: brigitte.bigi@gmail.com
    @license: GPL, version 3
    @summary: This class is the TimePoint representation.

    Represents a time point identified by a time value and a radius value.
    Generally, time is represented in seconds, as a float value.

    In the TimePoint instance, the 3 relations <, = and > take into
    account a radius value,
    that represents the uncertainty of the localization.
    For a point x, with a radius value of dx, and a point y with a radius
    value of dy, these relations are defined as:
        - x = y iff |x - y| <= dx + dy
        - x < y iff not(x = y) and x < y
        - x > y iff not(x = y) and x > y

    Examples:

        - Strictly equals:

            - x = 1.000, dx=0.
            - y = 1.000, dy=0.
            - x = y is true

            - x = 1.00000000000, dx=0.
            - y = 0.99999999675, dy=0.
            - x = y is false

        - Using the radius:

            - x = 1.0000000000, dx=0.0005
            - y = 1.0000987653, dx=0.0005
            - x = y is true  (accept a margin of 1ms between x and y)

            - x = 1.0000000, dx=0.0005
            - y = 1.0011235, dx=0.0005
            - x = y is false

    """

    def __init__(self, time, radius=0.0):
        """
        Create a new TimePoint instance.

        @param time (float) time value in seconds.
        @param radius (float) represents the vagueness of the point.

        @raise TypeError
        @raise ValueError

        """
        self.__midpoint = 0.0
        self.__radius = 0.0

        self.SetMidpoint(time)
        self.SetRadius(radius)

    # End __init__
    # ------------------------------------------------------------------------------------

    def Set(self, other):
        """
        Set the time/radius of another TimePoint instance.

        @param other (TimePoint)

        @raise TypeError:

        """
        if isinstance(other, TimePoint) is False:
            raise TypeError("TimePoint argument required, not %r" % other)

        other = other.Copy()  # FIXME: is deepcopy really necessary?
        self.__midpoint = other.__midpoint
        self.__radius = other.__radius

    # End Set
    # ------------------------------------------------------------------------------------

    def GetPoint(self):
        """
        Return myself.

        """
        return self

    # End GetPoint
    # ------------------------------------------------------------------------------------

    @deprecated
    def GetValue(self):
        """
        Return the Time value (float), in seconds.

        """
        return self.GetMidpoint()

    # End GetValue
    # ------------------------------------------------------------------------------------

    def GetMidpoint(self):
        """
        Return the Time value (float) of the midpoint.

        """
        return self.__midpoint

    # End GetMidpoint
    # ------------------------------------------------------------------------------------

    def SetValue(self, time):
        """
        @deprecated: replaced by SetMidpoint
        Set the Time to a new value.

        @param time (float) is the new time to set the midpoint.

        @raise TypeError (if time is not float)

        """
        self.SetMidpoint(time)

    # End SetValue
    # ------------------------------------------------------------------------------------

    def SetMidpoint(self, time):
        """
        Set the Time to a new value.

        @param time (float) is the new time to set the midpoint.

        """
        if time < 0.:
            raise ValueError("A time point can't be negative: %r" % time)

        self.__midpoint = float(time)

    # End SetMidpoint
    # ------------------------------------------------------------------------------------

    def GetRadius(self):
        """
        Return the radius, in seconds (float).

        """
        return self.__radius

    # End GetRadius
    # ------------------------------------------------------------------------------------

    def SetRadius(self, radius):
        """
        Fix the radius, in seconds.

        @param radius (float) is the radius (in seconds)

        @raise TypeError (if radius is not float)

        """
        if radius < 0.:
            raise ValueError(
                "The vagueness of a time point can't be negative: %r" % radius)

        if self.__midpoint < radius:
            radius = self.__midpoint

        self.__radius = radius

    # End SetRadius
    # ------------------------------------------------------------------------------------

    def IsPoint(self):
        """
        Return True, as this object is representing a Point.

        """
        return True

    # End IsPoint
    # ------------------------------------------------------------------------------------

    def IsTimePoint(self):
        """
        Return True, as this object is an instance of TimePoint.

        """
        return True

    # End IsTimePoint
    # ------------------------------------------------------------------------------------

    def Duration(self):
        """
        Return the duration of the time point, in seconds.
        Represents the duration of the vagueness.

        """

        return 2.0*self.__radius

    # End Duration
    # ------------------------------------------------------------------------------------

    def Copy(self):
        """
        Return a deep copy of self.

        """
        t = self.__midpoint
        r = self.__radius
        return TimePoint(t, r)

    # End Copy
    # ------------------------------------------------------------------------------------

    def __repr__(self):
        return "TimePoint: %f,%f" % (self.__midpoint, self.__radius)

    # End __repr__
    # ------------------------------------------------------------------------------------

    def __str__(self):
        return "(%f,%f)" % (self.GetMidpoint(), self.GetRadius())

    # End __str__
    # ------------------------------------------------------------------------------------

    def __hash__(self):
        return hash((self.__midpoint, self.__radius))

    # End __hash__
    # ------------------------------------------------------------------------------------

    def __eq__(self, other):
        """
        Equal is required to use '==' between 2 TimePoint instances or
        between a TimePoint and an other object representing time.
        This relationship takes into account the radius.

        @param other (TimePoint, float, int) is
        the other time point to compare with.

        """
        if isinstance(other, (int, float, TimePoint)) is False:
            return False

        if isinstance(other, TimePoint) is True:
            delta = abs(self.__midpoint - other.GetMidpoint())
            radius = self.__radius + other.GetRadius()
            return delta <= radius

        if isinstance(other, (int, float)):
            delta = abs(self.__midpoint - other)
            radius = self.__radius
            return delta <= radius

    # End __eq__
    # ------------------------------------------------------------------------------------

    def __lt__(self, other):
        """
        LowerThan is required to use '<' between 2 TimePoint instances
        or between a TimePoint and an other time object.

        @param other (TimePoint, float, int)
        is the other time point to compare with.

        """
        if isinstance(other, TimePoint) is True:
            return self != other and self.__midpoint < other.GetMidpoint()

        return self != other and self.__midpoint < other

    # End __lt__
    # ------------------------------------------------------------------------------------

    def __gt__(self, other):
        """
        GreaterThan is required to use '>' between 2 TimePoint instances
        or between a TimePoint and an other time object.

        @param other (TimePoint, float, int)
        is the other time point to compare with.

        """
        if isinstance(other, TimePoint) is True:
            return self != other and self.__midpoint > other.GetMidpoint()

        return self != other and self.__midpoint > other

    # End __gt__
    # ------------------------------------------------------------------------------------
