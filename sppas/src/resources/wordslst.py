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
# File: wordslst.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import codecs
import logging
import rutils

# ---------------------------------------------------------------------------

class WordsList( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Class to represent a simple list of words.

    """

    def __init__(self, filename=None, nodump=False, casesensitive=False):
        """
        Create a new WordsList instance.

        @param filename (str) is the word list file name, i.e. a file with 1 column.
        @param nodump (Boolean) allows to disable the creation of a dump file.

        """

        self._stw = {}
        # a list is relevant but a dictionary is used because:
        # a dictionary is faster to read tokens from a file and is also
        # faster to find a token in it.

        # Do the list of word is case-sensitive or not.
        self.casesensitive = casesensitive

        if filename is not None:

            data = None
            if nodump is False:
                # Try first to get the dict from a dump file
                # (at least 2 times faster than the ascii one)
                data = rutils.load_from_dump( filename )

            # Load from ascii if: 1st load, or, dump load error, or dump older than ascii
            if data is None:
                self.load_from_ascii( filename )
                if nodump is False:
                    rutils.save_as_dump( self._stw, filename )
                logging.info('Got word list from ASCII file.')

            else:
                self._stw = data
                logging.info('Got word list from dumped file.')

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Data management
    # -----------------------------------------------------------------------

    def add(self, entry):
        """
        Add an entry into the list except if the entry is already inside.

        @param entry (str) the entry to add in the word list.
        @return (Boolean)

        """

        entry = entry.strip()
        if self.casesensitive is False:
            entry = rutils.ToLower(entry)

        if self._stw.has_key( entry ) is False:
            self._stw[ entry ] = 0
            return True

        return False

    # -----------------------------------------------------------------------

    def get_size(self):
        """
        Return the number of entries in the list.

        """
        return len(self._stw)

    # -----------------------------------------------------------------------

    def get_list(self):
        """
        Return the list of words, sorted in alpha-numeric order.

        @return (list)

        """
        return sorted(self._stw.keys())

    # -----------------------------------------------------------------------

    def is_in(self,entry):
        """
        Return True if entry is in the list.

        @param entry is a string

        """
        return self._stw.has_key( entry )

    # -----------------------------------------------------------------------

    def is_unk(self,entry):
        """
        Return True if entry is unknown (not in the list).

        @param entry is a string

        """
        return not self.is_in(entry)

    # -----------------------------------------------------------------------

    def copy(self):
        """
        Make a deep copy of the instance.

        @return WordsList

        """
        s = WordsList()
        for i in self._stw:
            s.add(i)

        return s

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # File management
    # -----------------------------------------------------------------------

    def load_from_ascii(self, filename):
        """
        Read words from a file: one per line.

        @param filename (str) is the file name.
        @raise Exception

        """
        with codecs.open(filename, 'r', rutils.ENCODING) as fd:
            for nbl, line in enumerate(fd, 1):
                try:
                    self.add( line )
                except Exception as e:
                    raise Exception("Read file failed due to the following error at line %s: %s" % (nbl,str(e)))

    # -----------------------------------------------------------------------

    def save(self, filename):
        """
        Save the list of words in a file.

        @param filename (str)
        @return (Boolean)

        """
        try:
            with codecs.open(filename, 'w', rutils.ENCODING) as fd:
                for word in sorted( self._stw.keys() ):
                    fd.write("%s\n"%word)

        except Exception as e:
            logging.debug('Save file failed due to the following error: %s'%str(e))
            return False

        return True

    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------
