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
# File: mapping.py
# ----------------------------------------------------------------------------

import re

from dictrepl  import DictRepl

# ----------------------------------------------------------------------------

class Mapping( DictRepl ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Mapping table of any set of strings.

    A mapping is an extended replacement dictionary.

    """
    def __init__(self, dictname=None):
        """
        Create a new Mapping instance.

        @param dictname (string) is the file name with the mapping data (2 columns),

        """
        DictRepl.__init__( self,dictname,nodump=True )

        self.keepmiss = True  # remove or not missing values
        self.reverse  = False # will replace value by key instead of replacing key by value

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        Available options are:
            - keepmiss (bool)
            - reverse (bool)

        @param options (option)

        """
        for opt in options:

            key = opt.get_key()

            if key == "getmiss":
                self.set_keepmiss(opt.get_value())

            elif key == "reverse":
                self.set_reverse(opt.get_value())

            else:
                raise ValueError('Unknown option: %s'%key)

    # -----------------------------------------------------------------------

    def set_keepmiss(self, keepmiss):
        """
        Fix the keepmiss option.

        @param keepmiss (bool) If keepmiss is set to True, each missing entry
        is kept without change; instead each missing entry is deleted.

        """
        self.keepmiss = keepmiss

    # -----------------------------------------------------------------------

    def set_reverse(self, reverse):
        """
        Fix the reverse option.

        @param reverse (bool) If replace is set to True, mapping will replace value by key
        instead of replacing key by value.

        """
        self.reverse = reverse

    # -----------------------------------------------------------------------

    def map_entry(self, entry):
        """
        Map an entry (a key or a value).

        @param entry is the input string to map
        @return a string

        """
        if self.get_size() == 0:
            return entry

        if self.reverse is False:
            if self.is_key( entry ):
                return self.replace( entry )
        else:
            s = self.replace_reversed( entry )
            if len(s)>0:
                return s

        if self.keepmiss is False:
            return ''
        return entry

    # -----------------------------------------------------------------------

    def map( self, mstr, delimiters=None ):
        """
        Run the Mapping process on an input string.

        @param str is the input string to map
        @param delimiters (list) list of character delimiters. Default is:
               [';', ',', ' ', '.', '|', '+', '-']
        @return a string

        """
        if self.get_size() == 0:
            return mstr

        # suppose that some punctuation are like a separator
        # and we have to replace all strings between them
        if delimiters is None:
            delimiters = [";", ",", " ", ".", "|", "+", "-"]
        pattern = "|".join(map(re.escape, delimiters))
        pattern = "("+pattern+")\s*"
        tab = re.split(pattern, mstr)
        maptab = []

        for v in tab:
            if v in delimiters:
                maptab.append(v)
            else:
                maptab.append( self.map_entry(v) )

        return "".join(maptab)

    # -----------------------------------------------------------------------
