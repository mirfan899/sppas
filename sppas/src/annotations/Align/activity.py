"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.annotations.Align.activity.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO: Migrate Activity into a plugin of SPPAS.

"""
from sppas import unk_stamp
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.aio.utils import fill_gaps, unfill_gaps

from sppas.src.utils.makeunicode import sppasUnicode

from .. import SYMBOLS
from ..searchtier import sppasSearchTier

# ---------------------------------------------------------------------------


class Activity(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Create an activity tier from time-aligned tokens.

    """
    def __init__(self, trs):
        """ Create an Activity instance.

        :param trs: (Transcription) a Transcription containing a tier
        with exactly the name 'TokensAlign'.

        """
        self.activities = dict()
        self.set_activities()
 
        tokens_tier = sppasSearchTier.aligned_tokens(trs)
        self.tokens = fill_gaps(tokens_tier, trs.GetMinTime(), trs.GetMaxTime())

    # -----------------------------------------------------------------------

    def set_activities(self, activities=SYMBOLS):
        """ Fix the dictionary of possible non-speech activities.

        :param activities: (dict) A dictionary of activities.
        The key is the token; the value is the name of the activity.

        """
        self.activities = dict()
        for token, activity in activities:
            self.append_activity(token, activity)

        # For empty intervals... activity is unknown
        self.append_activity(unk_stamp, "")

    # -----------------------------------------------------------------------

    def append_activity(self, token, activity):
        """ Append a new activity.

        :param token: (str) The token of the tier TokensAlign
        :param activity: (str) Name of the activity

        """
        sp = sppasUnicode(token)
        token = sp.to_strip()

        sp = sppasUnicode(activity)
        activity = sp.to_strip()
        
        if self.activities.get(token, None) is None:
            self.activities[token] = activity

    # -----------------------------------------------------------------------

    def get_tier(self):
        """ Create and return the activity tier.

        :returns: Tier

        """
        new_tier = Tier('Activity')
        activity = "<INIT>"  # initial activity

        for ann in self.tokens:

            # Fix the activity name of this new token
            if ann.GetLabel().IsEmpty():
                l = unk_stamp
            else:
                l = ann.GetLabel().GetValue()
            new_activity = self.activities.get(l, "speech")

            # The activity has changed
            if activity != new_activity and activity != "<INIT>":
                new_tier.Append(Annotation(TimeInterval(new_tier.GetEnd(), ann.GetLocation().GetBegin()), 
                                           Label(activity)))

            # In any case, update current activity
            activity = new_activity

        # Last interval
        if new_tier.GetEnd() < self.tokens.GetEnd():
            new_tier.Append(Annotation(TimeInterval(new_tier.GetEnd(), self.tokens.GetEnd()), Label(activity)))

        return unfill_gaps(new_tier)
