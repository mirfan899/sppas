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

from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.aio.utils import fill_gaps, unfill_gaps

# ---------------------------------------------------------------------------


class Activity(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Create an activity tier from time-aligned tokens.

    """
    UNKNOWN="<UNK>"

    def __init__(self, trs):
        """
        Initialize activities.

        @param trs (Transcription - IN) a Transcription that contains a tier with exactly the name 'TokensAlign'

        """
        tokenstier = trs.Find('TokensAlign')
        self.tokens = fill_gaps(tokenstier, trs.GetMinTime(), trs.GetMaxTime() )
        self.set_activities()

    # -----------------------------------------------------------------------

    def set_activities(self, activities=None):
        """
        Fix the dictionary of possible non-speech activities.

        @param activities (dict - IN) A dictionary of activities.
        The key is the token and the value is the activity name.

        """
        if activities is None:
            self.activities = {}  # Non-speech activities
            self.activities['dummy'] = "dummy"  # un-transcribed
            self.activities['#']     = "silence"
            self.activities['+']     = "pause"
            self.activities['euh']   = "filled pause"
            self.activities['*']     = "noise"
            self.activities['@']     = "laughter"
        else:
            self.activities=activities

        # For empty intervals... activity is unknown
        self.append_activity(Activity.UNKNOWN, "")

    # -----------------------------------------------------------------------

    def append_activity(self, token, activity):
        """
        Append a new activity.

        @param token (str) String of the token
        @param activity (str) String of the activity name

        """
        token    = str(token).strip()
        activity = str(activity).strip()
        if self.activities.get(token,None) is None:
            self.activities[token] = activity

    # -----------------------------------------------------------------------

    def get_tier(self):
        """
        Create and return the activity tier.

        @return Tier

        """
        if self.tokens is None:
            raise Exception('No time-aligned tokens tier...')

        newtier = Tier('Activity')
        activity = "<INIT>" # initial activity

        for ann in self.tokens:

            # Fix the activity name of this new token
            if ann.GetLabel().IsEmpty():
                l = Activity.UNKNOWN
            else:
                l = ann.GetLabel().GetValue()
            newactivity = self.activities.get(l, "speech")

            # The activity has changed.
            if activity != newactivity and activity != "<INIT>":
                newtier.Append(Annotation(TimeInterval(newtier.GetEnd(),ann.GetLocation().GetBegin()), Label(activity)))

            # In any case, update current activity
            activity = newactivity

        # Last interval
        if newtier.GetEnd() < self.tokens.GetEnd():
            newtier.Append(Annotation(TimeInterval(newtier.GetEnd(),self.tokens.GetEnd()), Label(activity)))

        return unfill_gaps(newtier)

# ---------------------------------------------------------------------------
