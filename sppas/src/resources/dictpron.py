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
# File: dictpron.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import codecs
import logging
import rutils

# ---------------------------------------------------------------------------

class DictPron:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Pronunciation dictionary.

    A pronunciation dictionary contains a list of words, each one with a
    list of possible pronunciations. DictPron gets the dictionary from an
    HTK-ASCII file, as for example, the following lines:
        acted [] { k t e d
        acted(2) [] { k t i d
    The second column (with brackets) is ignored.
    There is also the possibility to add new entries.

    DictPron is instantiated as:

        >>> d = DictPron('eng.dict')
        >>> d.add_pron( 'acted', '{ k t e d' )
        >>> d.add_pron( 'acted', '{ k t i d' )

    In this class, the following convention is adopted to represent the
    pronunciation variants:

        - '.' separates the phonemes
        - '|' separates the variants

    Then, the pronunciation can be accessed with get_pron:

        >>> print d.get_pron('acted')
        >>> {.k.t.e.d|{.k.t.i.d

    """

    def __init__(self, dictfilename, unkstamp=u"UNK", nodump=False):
        """
        Constructor.

        @param dictfilename is the dictionary file name (HTK-ASCII format)
        @param unkstamp is the string used to represent a missing pronunciation

        """
        self._filename = dictfilename
        # Symbol to represent missing entries in the dictionary
        # (also called unknown entries)
        self._unkstamp = unkstamp

        # The pronunciation dictionary
        self._dict = {}

        # Either read the dictionary from a dumped file or from the original
        # ASCII one.
        if dictfilename is not None:

            data = None
            if nodump is False:
                # Try first to get the dict from a dump file (at least 2 times faster)
                data = rutils.load_from_dump( dictfilename )

            # Load from ascii if:
            # 1st load, or, dump load error, or dump older than ascii
            if data is None:
                self.load_from_ascii( dictfilename )
                if nodump is False:
                    rutils.save_as_dump( self._dict, dictfilename )
                logging.info('Get dictionary from ASCII file.')

            else:
                self._dict = data
                logging.info('Get dictionary from dumped file.')

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_pron(self, entry):
        """
        Return the phonetization of an entry in the dictionary.

        """
        return self._dict.get( rutils.ToLower(entry),self._unkstamp )

    # -----------------------------------------------------------------------

    def is_unk(self,entry):
        """
        Return True if entry is unknown (not in the dictionary).

        """
        return not self._dict.has_key( rutils.ToLower(entry) )

    # -----------------------------------------------------------------------

    def get_dictsize(self):
        """
        Return the number of entries in the dictionary.
        (without the number of pronunciation variants)

        """
        return len(self._dict)

    # -----------------------------------------------------------------------

    def get_dict(self):
        """
        Return the pronunciation dictionary.

        """
        return self._dict

    # -----------------------------------------------------------------------

    def get_keys(self):
        """
        Return the list of entries of the dictionary.

        """
        return self._dict.keys()

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def add_pron(self, token, pron):
        """
        Add a token/pron to the dict.

        @param token (string) unicode string of the token to add
        @param pron (string) the pronunciation with phonemes separated by spaces

        """
        # Remove multiple spaces and replace spaces with '.'
        variant = " ".join(pron.split()).replace(" ", ".")

        # Remove multiple spaces
        token = " ".join(token.split())

        previous_value = self._dict.get(token, "")
        separator = "|" if previous_value else ""
        new_value = previous_value + separator + variant
        self._dict[token] = new_value

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # File
    # -----------------------------------------------------------------------

    def load_from_ascii(self, filename):
        """
        Load a dict from an HTK-ASCII file.

        """
        try:
            with codecs.open(filename, 'r', rutils.ENCODING) as fd:
                lines = fd.readlines()
        except ValueError as e:
            raise ValueError('Expected HTK ASCII dictionary format, in UTF-8 encoding. Error while trying to open and read the file: %s'%e)

        for l,line in enumerate(lines):
            if len(line.strip()) == 0:
                continue
            try:
                line.index(u"[")
                line.index(u"]")
            except ValueError:
                raise ValueError('Expected HTK ASCII dictionary format. Error at line number %d: %s'%(l,line))

            # The entry is before the "[" and the pronunciation is after the "]"
            __entry = line[:line.find(u"[")]
            __pron  = line[line.find(u"]")+1:]

            # Remove the CR/LF, tabs, multiple spaces and others...
            __entry = rutils.ToStrip(__entry)
            __pron  = rutils.ToStrip(__pron)

            # Find if it is a new entry or a phonetic variant
            i = __entry.find(u"(")
            if( i>-1 and __entry.find(u"(")>-1 ):
                # Phonetic variant of an entry (i.e. entry ended with (XX))
                entry = rutils.ToLower(__entry[:i])
            else:
                entry = rutils.ToLower(__entry)

            # Find a previous pronunciation in the dictionary... or not!
            if self._dict.has_key(entry):
                pron = self.get_pron( entry ) + "|"
            else:
                pron = ""

            # Get the current pronunciation
            pron = pron + __pron.replace(" ",".")
            # Add (or change) the entry in the dict
            self._dict[entry] = pron

    # -----------------------------------------------------------------------

    def save_as_ascii(self, filename):
        """
        Save the pronunciation dictionary in HTK-ASCII format, encoding=utf8.

        @param filename (string)

        """
        try:
            with codecs.open(filename, 'w', encoding=rutils.ENCODING) as output:
                for entry, value in sorted(self._dict.iteritems(), key=lambda x:x[0]):
                    variants = value.split("|")
                    for i, variant in enumerate(variants, 1):
                        variant = variant.replace(".", " ")
                        if i > 1:
                            line = u"%s(%d) [%s] %s\n" % (entry, i, entry, variant)
                        else:
                            line = u"%s [%s] %s\n" % (entry, entry, variant)
                        output.write(line)

        except Exception as e:
            logging.debug('Save an ascii dict failed: %s'%str(e))
            return False

        return True

    # -----------------------------------------------------------------------
