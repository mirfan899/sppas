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

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import re

from resources.dictrepl  import DictRepl

# ----------------------------------------------------------------------------

class Mapping( DictRepl ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Mapping of any string.

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
            - keepmiss
            - reverse

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
        If keepmiss is set to True, each missing entry is kept without change.
        If keepmiss is set to False, each missing entry is deleted.

        @param keepmiss (Boolean)

        """
        self.keepmiss = keepmiss

    # -----------------------------------------------------------------------

    def set_reverse(self, reverse):
        """
        Fix the reverse option.
        If replace is set to True, mapping will replace value by key
        instead of replacing key by value.

        @param reverse (Boolean)

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
               [';', ',', '\s', '.', '|', '+', '-']
        @return a string

        """
        if self.get_size() == 0:
            return mstr

        # suppose that some punctuation are like a separator
        # and we have to replace all strings between them
        if delimiters is None:
            delimiters = [';', ',', ' ', '.', '|', '+', '-']
        pattern = '|'.join(map(re.escape, delimiters))
        pattern = "("+pattern+")\s*"
        tab = re.split(pattern, mstr)

        for i,v in enumerate(tab):
            if v in delimiters:
                continue
            tab[i] = self.map_entry(v)

        return ''.join(tab)

    # -----------------------------------------------------------------------
