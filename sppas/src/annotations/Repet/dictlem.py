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
# File: dictlem.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import re
import codecs

from sppas.src.config import sg
from sppas.src.config import symbols

# ----------------------------------------------------------------------------


class LemmaDict(object):
    """Perform a simple dictionary-based lemmatization."""

    def __init__(self):
        """Create a new LemmaDict instance."""
        
        # Load the dictionary:
        self.lemdict = dict()

    # ------------------------------------------------------------------

    def load(self, dictfilename):
        """Load a dictionary with "token occurrence lemma" as columns.

        :param dictfilename: the dictionary file name.

        """
        with codecs.open(dictfilename, 'r', sg.__encoding__) as fd:

            dictfreq = {}
            for line in fd:
                tabline = line.split()
                if len(tabline) < 3:
                    break
                # The token is the first column
                __entry = self.__lower(tabline[0])
                __freq = int(tabline[1])
                # The lemma is at the last column
                __lemma = tabline[len(tabline)-1]
                # Remove the CR/LF, tabs, multiple spaces and others...
                __entry = self.__clean(__entry)
                __lemma = self.__clean(__lemma)

                # Add (or change) the entry in the dict
                # Find a previous token in the dictionary... or not!
                if __entry in dictfreq:
                    # a token already exists
                    if dictfreq[__entry] < __freq:
                        # the new one is more frequent
                        dictfreq[__entry] = __freq
                        self.lemdict[__entry] = __lemma
                else:
                    self.lemdict[__entry] = __lemma
                    dictfreq[__entry] = __freq

    # ------------------------------------------------------------------

    def __get(self, entry):
        """Return the lemmatization of an entry in the dictionary or "UNK".
            Parameters:  None
            Return:      int
            Exception:   None
        """
        return self.lemdict.get(self.__lower(entry), symbols.unk)

    # ------------------------------------------------------------------

    def is_unk(self, entry):
        """Return True if entry is unknown (not in the dictionary).
            Parameters:
                - entry is a string
            Return:      Boolean
        """
        return self.__lower(entry) not in self.lemdict

    # ------------------------------------------------------------------

    def get_lem(self, entry):
        """Return the lemmatization of an entry.
            Parameters:
                - entry is the string to lemmatize
            Return:      A string with the lemmatization
        """
        entry = self.__clean(entry)

        # Specific strings... for the italian transcription...
        idx = entry.find(u"<")
        if idx > 1 and entry.find(u">") > -1:
            entry = entry[:idx]
        # Specific strings... for the CID transcription...
        if len(entry) == 0 or \
                entry.find(u"gpd_") > -1 or \
                entry.find(u"gpf_") > -1 or \
                entry.find(u"ipu_") > -1:
            return ""

        # Find entry in the dict as it is given
        _strlem = self.__get(entry)

        # OK, the entry is in the dictionary
        if _strlem != symbols.unk:
            return _strlem

        # a missing compound word
        if entry.find(u"-") > -1 or entry.find(u"'") > -1:
            _strlem = ""
            _tabstr = re.split(u"[-']", entry)

            for _w in _tabstr:
                _strlem = _strlem + " " + self.__get(_w)

        # OK, finally the entry is in the dictionary?
        if _strlem.find(symbols.unk)>-1:
            return entry
        else:
            return _strlem

    # ------------------------------------------------------------------

    def __lower(self,entry):
        """Lower a string.
            TO DO TO DO from a dictionary for accentuated upper chars.
        """
        __str = entry.lower()
        #__str = __str.replace('À', 'à')
        #__str = __str.replace('È', 'è')
        #__str = __str.replace('Ì', 'í')
        #__str = __str.replace('É', 'é')
        #__str = __str.replace('Ù', 'ù')
        return __str

    # ------------------------------------------------------------------

    def __clean(self,entry):
        """Clean a string by removing tabs, CR/LF, and some punctuation.
            Parameters:
                - entry is the string to clean
            Return:      A string without special chars
        """
        # Remove multiple spaces
        __str = re.sub(u"[\s]+", ur" ", entry)
        # Punct at end
        __str = re.sub(u"\-+$", ur"", __str)
        # Spaces at beginning and end
        __str = re.sub(u"^[ ]+", ur"", __str)
        __str = re.sub(u"[ ]+$", ur"", __str)

        return __str.strip()

    # ------------------------------------------------------------------

    def lemmatize(self, unit, unk=False):
        """Return the lemmatization of an utterrance.
            Words in the utterrance are separated by spaces.
            Parameters:
                - unit is the utterrance to lemmatize
            Return:      A string with the lemmatization.
        """
        # Clean the unit
        _s = self.__clean(unit)

        # Array with each entry to lemmatize
        entries = _s.split(" ")
        tablem = []

        # lemmatize each entry
        for entry in entries:
            entry = self.__lower(entry)
            _lem = self.get_lem(entry)
            if len(_lem)>0 and _lem.find(symbols.unk)>-1:
                if unk is True:
                    _lem = entry
            tablem.append(_lem)

        # Concatenate entries into a lemmatized string
        _s = " "
        return _s.join(tablem)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.lemdict)
