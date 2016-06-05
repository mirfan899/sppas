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
# File: activity.py
# ---------------------------------------------------------------------------

from annotationdata.tier import Tier
from annotationdata.ptime.interval import TimeInterval
from annotationdata.ptime.point    import TimePoint
from annotationdata.annotation     import Annotation
from annotationdata.label.label    import Label

# ---------------------------------------------------------------------------

class Activity(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Create an activity tier from tokens.

    """
    def __init__(self, trs):
        self.tokens = trs.Find('TokensAlign')
        self.set_activities()

    def set_activities(self):
        """
        TODO... with a better solution!
        """
        self.activities = {}  # Non-speech activities
        self.activities['dummy'] = "dummy"  # un-transcribed
        self.activities['#'] = "silence"
        self.activities['+'] = "pause"
        self.activities['euh'] = "filled pause"
        self.activities['*'] = "noise"
        self.activities['@'] = "laughter"


    def get_tier(self):
        """
        """
        if self.tokens is None:
            return None

        newtier = Tier('Activity')
        activity = ""

        for ann in self.tokens:

            l = ann.GetLabel().GetValue()

            # Non-speech activity
            if l in self.activities.keys():
                newactivity = self.activities[l]
                if activity != newactivity:
                    if len(activity) > 0:
                        # the activity has changed.
                        newtier.Append(Annotation(TimeInterval(newtier.GetEnd(),ann.GetLocation().GetBegin()), Label(activity)))
                    activity = newactivity
            # Speech
            else:
                # token!
                if activity != "speech":
                    if len(activity) > 0:
                        # the activity has changed.
                        newtier.Append(Annotation(TimeInterval(newtier.GetEnd(),ann.GetLocation().GetBegin()), Label(activity)))
                    activity = "speech"

        # last interval
        if newtier.GetEnd() < self.tokens.GetEnd():
            newtier.Append(Annotation(TimeInterval(newtier.GetEnd(),self.tokens.GetEnd()), Label(activity)))

        return newtier

# ---------------------------------------------------------------------------
