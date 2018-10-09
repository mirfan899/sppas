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

"""
from sppas.src.config import symbols

from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.label.label import Label
from sppas.src.annotationdata.aio.utils import fill_gaps, unfill_gaps
from sppas.src.utils.makeunicode import sppasUnicode

from ..searchtier import sppasSearchTier

# ---------------------------------------------------------------------------


class sppasActivity(object):
    """Create an activity tier from time-aligned tokens.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self):
        """Create a sppasActivity instance with the default symbols."""

        self._activities = dict()
        self.set_activities()

    # -----------------------------------------------------------------------

    def set_activities(self, activities=symbols.all):
        """Fix the dictionary of possible non-speech activities.

        :param activities: (dict) A dictionary of activities.
        The key is the token; the value is the name of the activity.

        """
        self._activities = dict()
        for token in activities:
            self.append_activity(token, activities[token])

        # For empty intervals... activity is unknown
        self.append_activity(symbols.unk, "")

    # -----------------------------------------------------------------------

    def append_activity(self, token, activity):
        """Append a new activity.

        :param token: (str) The token of the tier TokensAlign
        :param activity: (str) Name of the activity

        """
        sp = sppasUnicode(token)
        token = sp.to_strip()

        sp = sppasUnicode(activity)
        activity = sp.to_strip()

        if token not in self._activities:
            self._activities[token] = activity

    # -----------------------------------------------------------------------

    def get_tier(self, trs):
        """Create and return the activity tier.

        :param trs: (Transcription) a Transcription containing a tier
        with exactly the name 'TokensAlign'.
        :returns: Tier
        :raises: NoInputError

        """
        tokens_tier = sppasSearchTier.aligned_tokens(trs)
        tokens = fill_gaps(tokens_tier, trs.GetMinTime(), trs.GetMaxTime())

        new_tier = Tier('Activity')
        activity = "<INIT>"  # initial activity

        for ann in tokens:

            # Fix the activity name of this new token
            if ann.GetLabel().IsEmpty():
                l = symbols.unk
            else:
                l = ann.GetLabel().GetValue()
            new_activity = self._activities.get(l, "speech")

            # The activity has changed
            if activity != new_activity and activity != "<INIT>":
                new_tier.Append(Annotation(TimeInterval(new_tier.GetEnd(),
                                                        ann.GetLocation().GetBegin()),
                                           Label(activity)))

            # In any case, update current activity
            activity = new_activity

        # Last interval
        if new_tier.GetEnd() < tokens.GetEnd():
            new_tier.Append(Annotation(TimeInterval(new_tier.GetEnd(), tokens.GetEnd()),
                                       Label(activity)))

        return unfill_gaps(new_tier)

    # -----------------------------------------------------------------------
    # overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        return str(self._activities)

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._activities)

    # -----------------------------------------------------------------------

    def __contains__(self, item):
        return item in self._activities

    # ------------------------------------------------------------------------

    def __iter__(self):
        for a in self._activities:
            yield a
