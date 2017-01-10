# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              the automatic
#           \__   |__/  |__/  |___| \__             annotation and
#              \  |     |     |   |    \             analysis
#           ___/  |     |     |   | ___/              of speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2017  Brigitte Bigi
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
# File: src.presenters.tiermapping.py
# ----------------------------------------------------------------------------

from annotationdata.tier import Tier
from resources.mapping import Mapping, DEFAULT_SEP

# ----------------------------------------------------------------------------


class TierMapping(Mapping):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Class that is able to map labels from a table.

    A conversion table is used to map symbols of labels of a tier with new
    symbols. This class can convert either individual symbols or strings of
    symbols (syllables, words, ...) if a separator is given.
    Any symbols in the transcription tier which are not in the conversion
    table are replaced by a specific symbol (by default '*').
    """
    def __init__(self, dict_name=None):
        """
        Create a TierMapping instance.

        :param tier (Tier) is the tier name.

        """
        Mapping.__init__(self, dict_name)
        self._delimiters = DEFAULT_SEP

    # ------------------------------------------------------------------

    def set_delimiters(self, delimit_list):
        """
        Fix the list of characters used as symbol delimiters.
        If delimit_list is an empty list, the mapping system will map with a
        longest matching algorithm.

        :param delimit_list: List of characters like for example [" ", ".", "-"]

        """
        # Each element of the list must contain only one character
        for i, c in enumerate(delimit_list):
            delimit_list[i] = str(c)[0]

        # Set the delimiters as Iterable() and not as List()
        self._delimiters = tuple(delimit_list)

    # ------------------------------------------------------------------

    def map_tier(self, tier):
        """
        Run the TierMapping process on an input tier.

        :param tier: (Tier) The tier instance to map label symbols.
        :returns: a new tier, with the same name as the given tier

        """
        # Create the output tier
        new_tier = tier.Copy()

        # if nothing to do
        if tier.GetSize() == 0 or self.get_size() == 0:
            return new_tier

        # map
        for ann in new_tier:
            for text in ann.GetLabel().GetLabels():
                if text.IsEmpty() is False and text.IsSilence() is False:
                    l = self.map(text.GetValue(), self._delimiters)
                    text.SetValue(l)

        return new_tier

    # ------------------------------------------------------------------------
