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
# File: duration.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

class Duration( object ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, version 3
    @summary: This class is a Duration representation.

    Represents a duration identified by 2 float values:
    the value and the margin.

    """

    def __init__(self, value, vagueness=0.0):
        """
        Create a new Duration instance.

        @param value (float)  value in seconds.
        @param margin (float) represents the vagueness of the value.
        @raise TypeError
        @raise ValueError

        """
        self.__value  = 0.0
        self.__margin = 0.0

        self.SetValue(value)
        self.SetMargin(vagueness)

    # -----------------------------------------------------------------------

    def Set(self, other):
        """
        Set the value/vagueness of another Duration instance.

        @param other (Duration)
        @raise TypeError

        """
        if isinstance(other, Duration) is False:
            raise TypeError("Duration argument required, not %r" % other)

        other = other.Copy()  # FIXME: is deepcopy really necessary?
        self.__value  = other.GetValue()
        self.__margin = other.GetMargin()

    # -----------------------------------------------------------------------

    def GetDuration(self):
        """
        Return myself.

        """
        return self

    # -----------------------------------------------------------------------

    def GetValue(self):
        """
        Return the duration value (float), in seconds.

        """
        return self.__value

    # -----------------------------------------------------------------------

    def SetValue(self, value):
        """
        Set the duration to a new value.

        @param value (float) is the new duration value.
        @raise TypeError

        """
        if value < 0.:
            raise ValueError("A duration can't be negative: %r" % value)

        self.__value = float( value )

    # -----------------------------------------------------------------------

    def GetMargin(self):
        """
        Return the vagueness of the duration, in seconds (float).

        """
        return self.__margin

    # -----------------------------------------------------------------------

    def SetMargin(self, vagueness):
        """
        Fix the vagueness of the duration, in seconds.

        @param vagueness (float) is the margin (in seconds)
        @raise TypeError

        """
        if vagueness < 0.:
            raise ValueError(
                "The vagueness of a duration can't be negative: %r" % vagueness)

        self.__margin = vagueness

    # -----------------------------------------------------------------------

    def Copy(self):
        """
        Return a deep copy of self.

        """
        t = self.__value
        r = self.__margin
        return Duration(t, r)

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "Duration: %f,%f" % (self.__value, self.__margin)

    # -----------------------------------------------------------------------

    def __str__(self):
        return "(%f,%f)" % (self.GetValue(), self.GetMargin())

    # -----------------------------------------------------------------------

    def __hash__(self):
        return hash((self.__value, self.__margin))

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """
        Equal is required to use '==' between 2 Duration instances or
        between a Duration and an other object representing time.
        This relationship takes into account the vagueness.

        @param other (Duration, float, int) is
        the other duration to compare with.

        """
        if isinstance(other, (int, float, Duration)) is False:
            return False

        if isinstance(other, Duration) is True:
            delta = abs(self.__value - other.GetValue())
            radius = self.__margin + other.GetMargin()
            return delta <= radius

        if isinstance(other, (int, float)):
            delta = abs(self.__value - other)
            radius = self.__margin
            return delta <= radius

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """
        LowerThan is required to use '<' between 2 Duration instances
        or between a Duration and an other time object.

        @param other (Duration, float, int)
        is the other duration to compare with.

        """
        if isinstance(other, Duration) is True:
            return self != other and self.__value < other.GetValue()

        return (self != other) and (self.__value < other)

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """
        GreaterThan is required to use '>' between 2 Duration instances
        or between a Duration and an other time object.

        @param other (Duration, float, int)
        is the other duration to compare with.

        """
        if isinstance(other, Duration) is True:
            return self != other and self.__value > other.GetValue()

        return (self != other) and (self.__value > other)

    # ------------------------------------------------------------------------

    def __ne__(self, other):
        """
        Not equals.
        """
        return not (self == other)

    # ------------------------------------------------------------------------

    def __le__(self, other):
        """
        Lesser or equal.
        """
        return (self < other) or (self == other)

    # ------------------------------------------------------------------------

    def __ge__(self, other):
        """
        Greater or equal.
        """
        return (self > other) or (self == other)

    # ------------------------------------------------------------------------
