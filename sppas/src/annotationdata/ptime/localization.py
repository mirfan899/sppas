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
# File: localization.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__ = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

from .baseplacement import BasePlacement

# ----------------------------------------------------------------------------


class Localization(object):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, version 3
    @summary: This class represents a Localization of an annotation.

    """
    def __init__(self, placement, score=1.0):
        """
        Create a Localization instance.
        """
        self.SetPlace(placement)
        self.SetScore(score)

    # ------------------------------------------------------------------------------------

    def GetPlace(self):
        """
        Return the placement.

        """
        return self.__place

    # ------------------------------------------------------------------------------------

    def GetScore(self):
        """
        Return the score.

        """
        return self.__score

    # ------------------------------------------------------------------------------------

    def SetPlace(self, placement):
        """
        Set a new placement.

        """
        if not isinstance(placement, BasePlacement):
            raise TypeError("Localization: Placement argument required, not %r"
                            % placement)

        self.__place = placement

    # ------------------------------------------------------------------------------------

    def SetScore(self, score):
        """
        Set a new score.

        """
        try:
            self.__score = float(score)
        except Exception:
            raise TypeError("Localization: float argument required, not %r"
                            % score)

    # ------------------------------------------------------------------------------------

    def StrictEqual(self, other):
        """
        Return True if self is strictly equal to other (Placement and Score).

        @param other (Localization) to compare.

        """
        return (self.__place == other.GetPlace() and
                self.__score == other.GetScore())

    # ------------------------------------------------------------------------------------

    def GetBegin(self):
        """
        Return the begin instance of the localization, except for points.

        """
        if self.__place.IsTimePoint() or self.__place.IsFramePoint():
            raise AttributeError(
                "The localization of this object has no attribute Begin.")

        return self.__place.GetBegin()

    # ------------------------------------------------------------------------------------

    def GetEnd(self):
        """
        Return the end instance of the localization, except for points.

        """
        if self.__place.IsTimePoint() or self.__place.IsFramePoint():
            raise AttributeError(
                "The localization of this object has no attribute End.")

        return self.__place.GetEnd()

    # ------------------------------------------------------------------------------------

    def SetBegin(self, point):
        """
        Set the begin instance of the localization, except for points.

        """
        if self.__place.IsTimePoint() or self.__place.IsFramePoint():
            raise AttributeError(
                "The localization of this object has no attribute Begin.")

        return self.__place.SetBegin(point)

    # ------------------------------------------------------------------------------------

    def SetEnd(self, point):
        """
        Set the end instance of the localization, except for points.

        """
        if self.__place.IsTimePoint() or self.__place.IsFramePoint():
            raise AttributeError(
                "The location of this object has no attribute End.")

        return self.__place.SetEnd(point)

    # ------------------------------------------------------------------------------------

    def GetPoint(self):
        """
        Return the point instance of the localization, except for intervals.

        """
        if not (self.__place.IsTimePoint() or self.__place.IsFramePoint()):
            raise AttributeError(
                "The localization of this object has no attribute Point.")

        return self.__place

    # ------------------------------------------------------------------------------------

    def SetPoint(self, point):
        """
        Set the point instance of the localization, except for intervals.

        """
        if not self.__place.IsPoint():
            raise AttributeError(
                "The localization of this object has no attribute Point.")

        return self.__place.Set(point)

    # ------------------------------------------------------------------------------------

    def IsTimePoint(self):
        """
        Check if the localization is an instance of TimePoint.

        """
        return self.__place.IsTimePoint()

    # ------------------------------------------------------------------------------------

    def IsTimeInterval(self):
        """
        Check if the localization is an instance of TimeInterval.

        """
        return self.__place.IsTimeInterval()

    # ------------------------------------------------------------------------------------

    def IsTimeDisjoint(self):
        """
        Check if the localization is an instance of TimeDisjoint.

        """
        return self.__place.IsTimeDisjoint()

    # ------------------------------------------------------------------------------------

    def IsFramePoint(self):
        """
        Check if the localization is an instance of FramePoint.

        """
        return self.__place.IsFramePoint()

    # ------------------------------------------------------------------------------------

    def IsFrameInterval(self):
        """
        Check if the localization is an instance of FrameInterval.

        """
        return self.__place.IsFrameInterval()

    # ------------------------------------------------------------------------------------

    def IsFrameDisjoint(self):
        """
        Check if the localization is an instance of TimeDisjoint.

        """
        return self.__place.IsFrameDisjoint()

    # ------------------------------------------------------------------------------------

    def Duration(self):
        """
        Return the duration of the localization.
        """
        return self.__place.Duration()

    # ------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------

    def __repr__(self):
        return ("Localization(value=%s, score=%s)" %
                (self.__place, self.__score))

    def __str__(self):
        return "(%s,%s)" % (self.__place, self.__score)

    def __eq__(self, other):
        return self.__place == other.GetPlace()

# ------------------------------------------------------------------------------------
