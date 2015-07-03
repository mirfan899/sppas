#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# File: dictrepl.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------

import codecs
import logging

import rutils

# ----------------------------------------------------------------------------


class DictRepl:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Replacements Dictionary.

    """

    def __init__(self, dictfilename=None, nodump=False):
        """
        Constructor.

        @param dictfilename is the dictionary file name (2 columns)
        @param nodump (Boolean) disable the creation of a dump file

        """

        # Symbol to represent missing entries in the dictionary
        # (also called unknown entries)
        self._filename = dictfilename

        # The replacements dictionary
        self._dict = {}

        if dictfilename is not None:

            data = None
            if nodump is False:
                # Try first to get the dict from a dump file (at least 2 times faster)
                data = rutils.load_from_dump( dictfilename )

            # Load from ascii if: 1st load, or, dump load error, or dump older than ascii
            if data is None:
                self.load_from_ascii( dictfilename )
                if nodump is False:
                    rutils.save_as_dump( self._dict, dictfilename )
                logging.info('Get dictionary from ASCII file.')

            else:
                self._dict = data
                logging.info('Get dictionary from dumped file.')

    # End __init__
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------


    def is_key(self,entry):
        """
        Return True if entry is a key in the dictionary.

        """
        return self._dict.has_key( entry )

    # End is_key
    # ------------------------------------------------------------------------


    def is_value(self,entry):
        """
        Return True if entry is a value in the dictionary.

        """
        return entry in self._dict.values()

    # End is_value
    # ------------------------------------------------------------------------


    def is_unk(self,entry):
        """
        Return True if entry is unknown (not in the dictionary).

        """
        return not self._dict.has_key( entry )

    # End is_unk
    # ------------------------------------------------------------------------


    def get_dictsize(self):
        """
        Return the number of entries in the dictionary.

        """
        return len(self._dict)

    # End get_dictsize
    # ------------------------------------------------------------------------


    def get_dict(self):
        """
        Return the replacements dictionary.

        """
        return self._dict

    # End get_dict
    # ------------------------------------------------------------------------


    def get_keys(self):
        """
        Return the list of entries of the dictionary.

        """
        return self._dict.keys()

    # End get_keys
    # ------------------------------------------------------------------------


    def replace(self, key):
        """
        Return the replacement value of a key or None if key has no replacement.

        """
        return self._dict.get(key, None)

    # End replace
    # ------------------------------------------------------------------------


    def replace_reversed(self, value):
        """
        Return the replacement key of a value or None if value does not exists.
        @return a string with all keys, separated by '|'.

        """
        # hum... a value can have more than 1 key!
        keys = [k for k,v in self._dict.items() if v == value]
        if len(keys) == 0:
            return None
        return "_".join(keys)

    # End replace_reversed
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------


    def add(self, token, repl):
        """
        Add a token/repl to the dict.

        @param token (string) unicode string of the token to add
        @param repl (string) the replacement token

        """

        # Remove multiple spaces
        key    = " ".join(token.split())
        value  = " ".join(repl.split())

        # Add in the dict
        if self._dict.has_key(key):
            value = u"{0}{1}".format(self._dict.get(key), value)
        self._dict[key] = value

    # End add
    # ------------------------------------------------------------------------



    # ------------------------------------------------------------------------
    # File
    # ------------------------------------------------------------------------


    def load_from_ascii(self, filename):
        """
        Load a dict from an HTK-ASCII file.

        """

        with codecs.open(filename, 'r', rutils.ENCODING) as fd:
            lines = fd.readlines()

        for line in lines:
            line  = " ".join(line.split())
            if len(line) == 0:
                continue

            tabline = line.split()
            if len(tabline) < 2:
                continue

            # Add (or modify) the entry in the dict
            key = tabline[0]
            value = "_".join(tabline[1:])
            if self._dict.has_key(key):
                value = u"{0}{1}".format(self._dict.get(key), value)
            self._dict[key] = value

    # End load_from_ascii
    # ------------------------------------------------------------------------


    def save_as_ascii(self, filename):
        """
        Save the replacement dictionary.

        @param filename (string)

        """
        try:
            with codecs.open(filename, 'w', encoding=rutils.ENCODING) as output:
                for entry, value in sorted(self._dict.iteritems(), key=lambda x:x[0]):
                    output.write("%s %s"%(entry,value))
        except Exception as e:
            logging.debug('Save an ascii dict failed: %s'%str(e))
            return False

        return True

    # End save_as_ascii
    # ------------------------------------------------------------------------

# End DictRepl
# ----------------------------------------------------------------------------
