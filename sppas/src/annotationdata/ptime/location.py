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
# File: location.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------


from baseplacement import BasePlacement
from localization import Localization
import copy

# ----------------------------------------------------------------------------

class Location(object):
    """
    @authors: Brigitte Bigi, Tatsuya Watanabe
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Base class for the Location of an annotation.

    """

    def __init__(self, entry):
        """
        Create a new Location instance and add the entry.

        @param entry (one of the Placements or Localization or Location)
        is the entry to add for this location.

        """
        self.__locs = list()
        self.__fct = max

        if entry is not None:
            self.AddValue(entry)

    # End __init__
    # ------------------------------------------------------------------------------------

    def Copy(self):
        return copy.deepcopy(self)

    def Set(self, place):
        """
        Set a new location.

        @param place (Location)

        """
        self.SetValue(place)
        self.__fct = place.GetFunctionScore()

    # End Set
    # ------------------------------------------------------------------------------------

    def AddValue(self, place):
        """
        Add an entry into the list of possible localizations.

        @param place is the new placement/localization

        """
        if isinstance(place, (BasePlacement, Localization)) is False:
            raise TypeError("One placement argument required, not %r" % place)

        if isinstance(place, BasePlacement) is True:
            place = Localization(place, 1)

        if place not in self.__locs:
            self.__locs.append(place)

    # End AddValue
    # ------------------------------------------------------------------------------------

    def SetValue(self, entry):
        """
        Remove all localizations and append the new one.

        @param entry is the new placement/localization

        """
        self.UnsetValue()
        self.AddValue(entry)

    # End SetValue
    # ------------------------------------------------------------------------------------

    def UnsetValue(self):
        """
        Remove all localizations.

        """
        self.__locs = []

    # End UnsetValue
    # ------------------------------------------------------------------------------------

    def GetFunctionScore(self):
        """
        Return the function used to compare scores.

        """
        return self.__fct

    # End GetFunctionScore
    # ------------------------------------------------------------------------------------

    def SetFunctionScore(self, fctname):
        """
        Set a new function to compare scores.

        @param fctname is one of min or max.

        """
        if fctname not in (min, max):
            raise TypeError('Expected min or max not %r' % fctname)

        self.__fct = fctname

    # End SetFunctionScore
    # ------------------------------------------------------------------------------------

    def GetLocalizations(self):
        """
        Return a copy of all placements included into this location.

        """
        return self.__locs

    # End GetLocalizations
    # ------------------------------------------------------------------------------------

    def GetPlaces(self):
        """
        Return a copy of all placements included into this location.

        """
        return [l.GetPlace() for l in self.__locs]

    # End GetPlaces
    # ------------------------------------------------------------------------------------

    def GetValue(self):
        """
        Return the best Localization, i.e.
        the localization with the better score.

        @return Localization instance

        """
        if len(self.__locs) == 0:
            return None

        return self.__fct(self.__locs, key=lambda x: x.GetScore())

    # End GetValue
    # ------------------------------------------------------------------------------------

    def GetDuration(self):
        return self.GetValue().Duration()

    # End GetDuration
    # ------------------------------------------------------------------------------------

    def GetBeginMidpoint(self):
        """
        Return the begin midpoint value of the best localization
        (the localization with the better score), except for points.

        """
        return self.GetValue().GetBegin().GetMidpoint()

    # End GetBeginMidpoint
    # ------------------------------------------------------------------------------------

    def GetEndMidpoint(self):
        """
        Return the end instance of the best localization (the localization
        with the better score), except for points.

        """
        return self.GetValue().GetEnd().GetMidpoint()

    # End GetEndMidpoint
    # ------------------------------------------------------------------------------------

    def GetBeginRadius(self):
        """
        Return the begin radius value of the best localization
        (the localization with the better score), except for points.

        """
        return self.GetValue().GetBegin().GetRadius()

    # End GetBeginRadius
    # ------------------------------------------------------------------------------------

    def GetEndRadius(self):
        """
        Return the end instance of the best localization (the localization
        with the better score), except for points.

        """
        return self.GetValue().GetEnd().GetRadius()

    # End GetEndRadius
    # ------------------------------------------------------------------------------------

    def GetBegin(self):
        """
        Return the begin instance of the best localization (the localization
        with the better score), except for points.

        """
        return self.GetValue().GetBegin()

    # End GetBegin
    # ------------------------------------------------------------------------------------

    def GetEnd(self):
        """
        Return the end instance of the best localization (the localization
        with the better score), except for points.

        """
        return self.GetValue().GetEnd()

    # End GetEnd
    # ------------------------------------------------------------------------------------

    def SetBegin(self, point):
        """
        Set the begin instance of the best localization (the localization
        with the better score), except for points.

        """
        self.GetValue().SetBegin(point)

    # End SetBegin
    # ------------------------------------------------------------------------------------

    def SetBeginMidpoint(self, value):
        """
        Set the begin midpoint value of the best localization (the localization
        with the better score), except for points.

        """
        self.GetValue().GetBegin().SetMidpoint(value)


    def SetBeginRadius(self, value):
        """
        Set the begin midpoint value of the best localization (the localization
        with the better score), except for points.

        """
        self.GetValue().GetBegin().SetRadius(value)

    def SetEnd(self, point):
        """
        Set the end instance of the best localization (the localization
        with the better score), except for points.

        """
        self.GetValue().SetEnd(point)

    # End SetEnd
    # ------------------------------------------------------------------------------------

    def SetEndMidpoint(self, value):
        """
        Set the end midpoint value of the best localization (the localization
        with the better score), except for points.

        """
        self.GetValue().GetEnd().SetMidpoint(value)

    def SetEndRadius(self, value):
        """
        Set the end midpoint value of the best localization (the localization
        with the better score), except for points.

        """
        self.GetValue().GetEnd().SetRadius(value)

    def GetPoint(self):
        """
        Return the point instance of the best localization (the localization
        with the better score), except for intervals.

        """
        return self.GetValue().GetPoint()

    # End GetPoint
    # ------------------------------------------------------------------------------------

    def GetPointMidpoint(self):
        """
        Return the midpoint value of the best localization (the localization
        with the better score), except for intervals.

        """
        return self.GetValue().GetPoint().GetMidpoint()

    # End GetPointMidpoint
    # ------------------------------------------------------------------------------------

    def GetPointRadius(self):
        """
        Return the radius value of the best localization (the localization
        with the better score), except for intervals.

        """
        return self.GetValue().GetPoint().GetRadius()

    # End GetPointRadius
    # ------------------------------------------------------------------------------------

    def SetPoint(self, point):
        """
        Set the point instance of the best localization (the localization
        with the better score), except for intervals.

        """
        self.GetValue().SetPoint(point)

    # End SetPoint
    # ------------------------------------------------------------------------------------

    def SetPointMidpoint(self, value):
        """
        Set the point value of the best localization (the localization
        with the better score), except for intervals.

        """
        self.GetValue().GetPoint().SetMidpoint(value)


    def SetPointRadius(self, value):
        """
        Set the point radius of the best localization (the localization
        with the better score), except for intervals.

        """
        self.GetValue().GetPoint().SetRadius(value)

    # ------------------------------------------------------------------------

    def IsPoint(self):
        """
        Check if the Localization attribute is
        an instance of TimePoint or FramePoint.

        """
        return self.GetValue().IsTimePoint() or self.GetValue().IsFramePoint()

    # End IsPoint
    # ------------------------------------------------------------------------------------

    def IsInterval(self):
        """
        Check if the Localization attribute is
        an instance of TimeInterval or FrameInterval.

        """
        return (self.GetValue().IsTimeInterval() or
                self.GetValue().IsFrameInterval())

    # End IsInterval
    # ------------------------------------------------------------------------------------

    def IsDisjoint(self):
        """
        Check if the attribute Localization is
        an instance of TimeDisjoint or FrameDisjoint.

        """
        return (self.GetValue().IsTimeDisjoint() or
                self.GetValue().IsFrameDisjoint())

    # End IsDisjoint
    # ------------------------------------------------------------------------------------

    def IsTimePoint(self):
        """
        Check if the best location is an instance of TimePoint.

        """
        return self.GetValue().IsTimePoint()

    # End IsTimePoint
    # ------------------------------------------------------------------------------------

    def IsTimeInterval(self):
        """
        Check if the best location is an instance of TimeInterval.

        """
        return self.GetValue().IsTimeInterval()

    # End IsTimeInterval
    # ------------------------------------------------------------------------------------

    def IsTimeDisjoint(self):
        """
        Check if the best location is an instance of TimeDisjoint.

        """
        return self.GetValue().IsTimeDisjoint()

    # End IsTimeDisjoint
    # ------------------------------------------------------------------------------------

    def IsFramePoint(self):
        """
        Check if the best location is an instance of FramePoint.

        """
        return self.GetValue().IsFramePoint()

    # End IsFramePoint
    # ------------------------------------------------------------------------------------

    def IsFrameInterval(self):
        """
        Check if the best location is an instance of FrameInterval.

        """
        return self.GetValue().IsFrameInterval()

    # End IsFrameInterval
    # ------------------------------------------------------------------------------------

    def IsFrameDisjoint(self):
        """
        Check if the best location is an instance of TimeDisjoint.

        """
        return self.GetValue().IsFrameDisjoint()

    # End IsFrameDisjoint
    # ------------------------------------------------------------------------------------

    def __repr__(self, *args, **kwargs):
        return "Locations:%s" % ("; ".join([str(i) for i in self.__locs]))

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------


    def __repr__(self, *args, **kwargs):
        return "%s" % ("; ".join([str(i) for i in self.__locs]))

    # End __repr__
    # ------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "Locations:%s" % ("; ".join([str(i) for i in self.__locs]))

    def __iter__(self):
        for a in self.__locs:
            yield a

    # End __iter__
    # ------------------------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__locs[i]

    # End __getitem__
    # ------------------------------------------------------------------------------------

    def __len__(self):
        return len(self.__locs)

    # End __len__
    # ------------------------------------------------------------------------------------

# End Location
# ------------------------------------------------------------------------------------
