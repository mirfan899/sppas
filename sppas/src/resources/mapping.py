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
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------

import re

from resources.dictrepl  import DictRepl

# ----------------------------------------------------------------------------


class Mapping(object):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Mapping of any string.


    """

    def __init__(self, dictname=None):
        """
        Create a new Mapping instance.

        @param dictname (string) is the file name with the mapping table (2 columns),

        """

        try:
            self.repl = DictRepl(dictname, nodump=True)
        except Exception:
            self.repl = DictRepl()

        self.keepmiss = True  # remove or not missing values
        self.reverse  = False # replace value by key instead of replacing key by value

    # End __init__
    # ------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------


    def fix_options(self, options):
        """
        Fix all options.

        Available options are:
            - keepmiss

        @param options (option)

        """

        for opt in options:

            key = opt.get_key()

            if key == "getmiss":
                self.set_keepmiss(opt.get_value())

            elif key == "reverse":
                self.set_reverse(opt.get_value())

            else:
                raise Exception('Unknown key option: %s'%key)

    # End fix_options
    # -----------------------------------------------------------------------


    def set_keepmiss(self, keepmiss):
        """
        Fix the keepmiss option.
        If keepmiss is set to True, each missing entry is kept without change.
        If keepmiss is set to False, each missing entry is deleted.

        @param keepmiss (Boolean)

        """
        self.keepmiss = keepmiss

    # End set_keepmiss
    # ----------------------------------------------------------------------


    def set_reverse(self, reverse):
        """
        Fix the reverse option.
        If replace is set to True, mapping will replace value by key
        instead of replacing key by value.

        @param reverse (Boolean)

        """
        self.reverse = reverse

    # End set_reverse
    # ----------------------------------------------------------------------


    def map_entry(self, entry):
        """
        Map an entry (a key or a value).

        @param entry is the input string to map
        @return a string

        """
        if self.repl.get_dictsize() == 0:
            return entry

        if self.reverse is False:
            if self.repl.is_key( entry ):
                return self.repl.replace( entry )
        else:
            if self.repl.is_value( entry ):
                return self.repl.replace_reversed( entry )

        if self.keepmiss is False:
            return ''
        return entry

    # End map_entry
    # ----------------------------------------------------------------------


    def map( self, str ):
        """
        Run the Mapping process on an input string.

        @param str is the input string to map
        @return a string

        """
        if self.repl.get_dictsize() == 0:
            return str

        # suppose that some punctuation are like a separator
        # and we have to replace all strings between them
        tab = re.split(r'(;|,|\s|\.|\|)\s*', str)

        for i,v in enumerate(tab):
            if v in [';', ',', '\s', '.', '|']:
                continue
            tab[i] = self.map_entry(v)

        return ''.join(tab)

    # End map
    # ----------------------------------------------------------------------

# End Mapping
# ---------------------------------------------------------------------------
