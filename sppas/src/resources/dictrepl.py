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
# File: dictrepl.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import codecs
import rutils

# ----------------------------------------------------------------------------

class DictRepl:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Replacements dictionary.

    This is an extended version of a dictionary.
    Values are "accumulated".
    Example:
        >>>d = DictRepl()
        >>>d.add("key","v1")
        >>>d.add("key","v2")
        >>>print d.get("key")
        >>>v1|v2
        >>>print d.is_value("v1")
        >>>True
        >>>print d.is_value("v1|v2")
        >>>False

    """

    def __init__(self, dictfilename=None, nodump=False):
        """
        Constructor.

        @param dictfilename is the dictionary file name (2 columns)
        @param nodump (Boolean) disable the creation of a dump file

        """
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

            else:
                self._dict = data

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def is_key(self,entry):
        """
        Return True if entry is a key in the dictionary.

        """
        return self._dict.has_key( entry )

    # ------------------------------------------------------------------------

    def is_value(self,entry):
        """
        Return True if entry is a value in the dictionary.

        """
        for v in self._dict.values():
            values = v.split('|')
            for val in values:
                if val == entry:
                    return True

        return False

    # ------------------------------------------------------------------------

    def is_value_of(self,key,entry):
        """
        Return True if entry is a value of a given key in the dictionary.

        """
        v = self._dict.get(key, "")
        values = v.split('|')
        for val in values:
            if val == entry:
                return True

        return False

    # ------------------------------------------------------------------------

    def is_unk(self,entry):
        """
        Return True if entry is not a key in the dictionary.

        """
        return not self.is_key( entry )

    # ------------------------------------------------------------------------

    def is_empty(self):
        """
        Return True if there is no entry in the dictionary.

        """
        return len(self._dict) == 0

    # ------------------------------------------------------------------------

    def get_size(self):
        """
        Return the number of entries in the dictionary.

        """
        return len(self._dict)

    # ------------------------------------------------------------------------

    def get_dict(self):
        """
        Return the replacements dictionary.

        """
        return self._dict

    # ------------------------------------------------------------------------

    def get_keys(self):
        """
        Return the list of keys of the dictionary.

        """
        return self._dict.keys()

    # ------------------------------------------------------------------------

    def get(self, key):
        """
        Return the value of a key of the dictionary or None.

        """
        return self._dict.get(key, None)

    # ------------------------------------------------------------------------

    def replace(self, key):
        """
        Return the replacement value of a key or None if key has no replacement.

        """
        return self._dict.get(key, None)

    # ------------------------------------------------------------------------

    def replace_reversed(self, value):
        """
        Return the replacement key of a value or an empty
        if value does not exists.

        @return a string with all keys, separated by '_'.

        """
        # hum... of course, a value can have more than 1 key!
        keys = []
        for k,v in self._dict.items():
            values = v.split('|')
            for val in values:
                if val == value:
                    keys.append( k )
        if len(keys) == 0:
            return ''
        return "|".join(keys)

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def add(self, token, repl):
        """
        Add a new key,value into the dict, or append value to the existing
        one with a "|" used as separator.

        @param token (string) unicode string of the token to add
        @param repl (string) the replacement token

        """
        # Remove multiple spaces
        key    = " ".join(token.split())
        value  = " ".join(repl.split())

        # Add in the dict
        if self._dict.has_key(key):
            if self.is_value_of(key,value) is False:
                value = u"{0}|{1}".format(self._dict.get(key), value)
        self._dict[key] = value

    # ------------------------------------------------------------------------

    def remove(self, entry):
        """
        Remove an entry, as key or value.

        @param token (string) unicode string of the entry to remove

        """

        for k in self._dict.keys():
            if k == entry or self.is_value_of(k,entry):
                self._dict.pop( k )

    # ------------------------------------------------------------------------
    # File
    # ------------------------------------------------------------------------

    def load_from_ascii(self, filename):
        """
        Load a replacement dictionary from an ascii file.

        @param filename (str)

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
            value = "|".join(tabline[1:])
            self.add( key,value )

    # ------------------------------------------------------------------------

    def save_as_ascii(self, filename):
        """
        Save the replacement dictionary.

        @param filename (string)

        """
        try:
            with codecs.open(filename, 'w', encoding=rutils.ENCODING) as output:
                for entry, value in sorted(self._dict.iteritems(), key=lambda x:x[0]):
                    values = value.split('|')
                    for v in values:
                        output.write("%s %s\n"%(entry,v.strip()))
        except Exception:
            return False

        return True

    # ------------------------------------------------------------------------

    def __str__(self):
        return str(self._dict)
