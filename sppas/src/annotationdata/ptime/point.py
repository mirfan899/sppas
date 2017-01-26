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
# File: point.py
# ----------------------------------------------------------------------------

from .baseplacement import BasePlacement
from .duration import Duration
from ..utils.deprecated import deprecated

# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------


class TimePoint(BasePlacement):
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

    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------

    def GetPoint(self):
        """
        Return myself.

        """
        return self

    # -----------------------------------------------------------------------

    @deprecated
    def GetValue(self):
        return self.GetMidpoint()

    # -----------------------------------------------------------------------

    def GetMidpoint(self):
        """
        Return the time value (float) of the midpoint.

        """
        return self.__midpoint

    # -----------------------------------------------------------------------

    @deprecated
    def SetValue(self, time):
        self.SetMidpoint(time)

    # -----------------------------------------------------------------------

    def SetMidpoint(self, time):
        """
        Set the time to a new value, in seconds.

        @param time (float) is the new time to set the midpoint.
        @raise ValueError

        """
        if time < 0.:
            raise ValueError("A time point can't be negative: %r" % time)

        self.__midpoint = float(time)

    # -----------------------------------------------------------------------

    def GetRadius(self):
        """
        Return the radius value, in seconds (float).

        """
        return self.__radius

    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------

    def IsPoint(self):
        """
        Return True, because self is representing a Point.

        """
        return True

    # -----------------------------------------------------------------------

    def IsTimePoint(self):
        """
        Return True, because self is an instance of TimePoint.

        """
        return True

    # -----------------------------------------------------------------------

    def Duration(self):
        """
        Return the duration of the time point, in seconds.

        @return (Duration) the duration and its vagueness
        """

        return Duration(0., 2.0*self.__radius)

    # -----------------------------------------------------------------------

    def Copy(self):
        """
        Return a deep copy of self.

        """
        t = self.__midpoint
        r = self.__radius
        return TimePoint(t, r)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return "TimePoint: %f,%f" % (self.__midpoint, self.__radius)

    # -----------------------------------------------------------------------

    def __str__(self):
        return "(%f,%f)" % (self.GetMidpoint(), self.GetRadius())

    # -----------------------------------------------------------------------

    def __hash__(self):
        return hash((self.__midpoint, self.__radius))

    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """
        LowerThan is required to use '<' between 2 TimePoint instances
        or between a TimePoint and an other time object.

        @param other (TimePoint, float, int)
        is the other time point to compare with.

        """
        if isinstance(other, TimePoint) is True:
            return self != other and self.__midpoint < other.GetMidpoint()

        return (self != other) and (self.__midpoint < other)

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """
        GreaterThan is required to use '>' between 2 TimePoint instances
        or between a TimePoint and an other time object.

        @param other (TimePoint, float, int)
        is the other time point to compare with.

        """
        if isinstance(other, TimePoint) is True:
            return self != other and self.__midpoint > other.GetMidpoint()

        return (self != other) and (self.__midpoint > other)

    # -----------------------------------------------------------------------
