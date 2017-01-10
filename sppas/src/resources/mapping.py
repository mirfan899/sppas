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
# File: src.resources.mapping.py
# ----------------------------------------------------------------------------

import re

from dictrepl import DictRepl

# ----------------------------------------------------------------------------

DEFAULT_SEP = (";", ",", " ", ".", "|", "+", "-")

# ----------------------------------------------------------------------------


class Mapping(DictRepl):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Mapping table of any set of strings.

    A mapping is an extended replacement dictionary.

    """
    def __init__(self, dict_name=None):
        """
        Create a new Mapping instance.

        :param dict_name: (string) is the file name with the mapping data (2 columns)

        """
        DictRepl.__init__(self, dict_name, nodump=True)

        self._keep_miss = True  # remove or not missing values
        self._reverse = False   # will replace value by key instead of replacing key by value
        self._miss_symbol = ""  # Symbol to be used if keep_miss is False

    # -----------------------------------------------------------------------

    def get_reverse(self):
        """ Return the boolean value of reverse member. """

        return self._reverse

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def set_keep_miss(self, keep_miss):
        """
        Fix the keep_miss option.

        :param keep_miss: (bool) If keep_miss is set to True, each missing
        entry is kept without change; instead each missing entry is replaced
        by a specific symbol.

        """
        self._keep_miss = keep_miss

    # -----------------------------------------------------------------------

    def set_reverse(self, reverse):
        """
        Fix the reverse option.

        :param reverse (bool) If replace is set to True, mapping will replace
        value by key instead of replacing key by value.

        """
        self._reverse = reverse

    # -----------------------------------------------------------------------

    def set_miss_symbol(self, symbol):
        """
        Fix the symbol to be used if keep_miss is False.

        :param symbol: (str) US-ASCII symbol to be used in case of a symbol
        is missing of the mapping table.

        """
        self._miss_symbol = str(symbol)

    # -----------------------------------------------------------------------
    # Mapping entries
    # -----------------------------------------------------------------------

    def map_entry(self, entry):
        """
        Map an entry (a key or a value).

        :param entry: (str) is the input string to map
        :returns: mapped entry is a string

        """
        if self.get_size() == 0:
            return entry

        if self._reverse is False:
            if self.is_key(entry):
                return self.replace(entry)
        else:
            s = self.replace_reversed(entry)
            if len(s) > 0:
                return s

        if self._keep_miss is False:
            return self._miss_symbol

        return entry

    # -----------------------------------------------------------------------

    def map(self, mstr, delimiters=DEFAULT_SEP):
        """
        Run the Mapping process on an input string.

        :param mstr: is the input string to map
        :param delimiters: (list) list of character delimiters. Default is:
               [';', ',', ' ', '.', '|', '+', '-']
        @return a string

        """
        if self.get_size() == 0:
            return mstr

        tab = []
        # suppose that some punctuation are like a separator
        # and we have to replace all strings between them
        if len(delimiters) > 0:
            pattern = "|".join(map(re.escape, delimiters))
            pattern = "("+pattern+")\s*"
            tab = re.split(pattern, mstr)

        else:
            s = self._miss_symbol
            k = self._keep_miss
            self._miss_symbol = "UNKNOWN"
            self._keep_miss = False
            i = 0
            j = 0
            maxi = len(mstr)
            while i < maxi:
                i = maxi
                mapped = self.map_entry(mstr[j:i])
                while mapped == self._miss_symbol and j < (i-1):
                    i -= 1
                    mapped = self.map_entry(mstr[j:i])
                tab.append(mstr[j:i])
                j = i
            self._miss_symbol = s
            self._keep_miss = k

        map_tab = []
        for v in tab:
            if v in delimiters:
                map_tab.append(v)
            else:
                map_tab.append(self.map_entry(v))

        return "".join(map_tab)

    # -----------------------------------------------------------------------
