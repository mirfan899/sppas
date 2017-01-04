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
# File: src.resources.dictpron.py
# ---------------------------------------------------------------------------

import codecs
import logging
import rutils
from sp_glob import UNKSTAMP

# ---------------------------------------------------------------------------


class DictPron:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Pronunciation dictionary manager.

    A pronunciation dictionary contains a list of words, each one with a list
    of possible pronunciations. DictPron gets the dictionary from an HTK-ASCII
    file, as for example, the following lines:
        acted [] { k t e d
        acted(2) [] { k t i d
    The first columns indicates the tokens, eventually followed by the variant
    number into braces. The second column (with brackets) is ignored. It can
    contain the token. Other columns are the phones separated by whitespace.

    DictPron is instantiated as:

        >>> d = DictPron('eng.dict')
        >>> d.add_pron( 'acted', '{ k t e' )
        >>> d.add_pron( 'acted', '{ k t i' )

    In this class, the following convention is adopted to represent the
    pronunciation variants:

        - '-' separates the phones
        - '|' separates the variants

    Then, the pronunciation can be accessed with get_pron() method:

        >>> print d.get_pron('acted')
        {.k.t.e.d|{.k.t.i.d|{ k t e|{ k t i

    """
    def __init__(self, dictfilename=None, unkstamp=UNKSTAMP, nodump=False):
        """
        Constructor.

        :param dictfilename: (str) The dictionary file name (HTK-ASCII format)
        :param unkstamp: (str) Represent a missing pronunciation
        :param nodump: (bool) Create or not a dump file (binary version of the
        dictionary)

        """
        self._filename = dictfilename

        # Symbol to represent missing entries in the dictionary
        self.unkstamp = unkstamp

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
    # Getters
    # -----------------------------------------------------------------------

    def get_pron(self, entry):
        """
        Return the phonetization of an entry in the dictionary.

        :param entry: (str) A token to find in the dictionary
        :return: pronunciations of the given token or the unknown symbol

        """
        return self._dict.get(rutils.ToLower(entry), self.unkstamp)

    # -----------------------------------------------------------------------

    def is_unk(self, entry):
        """
        Return True if entry is unknown (not in the dictionary).

        :param entry: (str) A token to find in the dictionary

        """
        return rutils.ToLower(entry) not in self._dict

    # -----------------------------------------------------------------------

    def is_pron_of(self, entry, pron):
        """
        Return True if pron is a pronunciation of entry.

        :param entry: (str) A token to find in the dictionary
        :param pron: (str) A pronunciation

        """
        prons = self._dict.get( rutils.ToLower(entry),None )
        if prons is None:
            return False

        return pron in prons.split('|')

    # -----------------------------------------------------------------------

    def get_dictsize(self):
        """ Return the number of entries in the dictionary. """

        return len(self._dict)

    # -----------------------------------------------------------------------

    def get_dict(self):
        """ Return the pronunciation dictionary. """

        return self._dict

    # -----------------------------------------------------------------------

    def get_keys(self):
        """ Return the list of entries of the dictionary. """

        return self._dict.keys()

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def add_pron(self, token, pron):
        """
        Add a token/pron to the dict.

        :param token: (str) Unicode string of the token to add
        :param pron: (str) The pronunciation with phonemes separated by spaces

        """
        # Remove the CR/LF, tabs, multiple spaces and others... and lowerise
        entry   = rutils.ToStrip(token)
        entry   = rutils.ToLower(entry)
        newpron = rutils.ToStrip(pron)
        newpron = newpron.replace(" ", "-")

        # Already a pronunciation for this token?
        curpron = ""
        if self._dict.has_key(entry):
            # and don't append an already known pronunciation
            if self.is_pron_of(entry, pron) is False:
                curpron = self.get_pron(entry) + "|"

        # Get the current pronunciation and append the new one
        newpron = curpron + newpron

        # Add (or change) the entry in the dict
        self._dict[entry] = newpron

    # -----------------------------------------------------------------------

    def map_phones(self, map_table):
        """
        Create a new dictionary by changing the phoneme strings
        depending on a mapping table.

        :param map_table: (Mapping) A mapping table
        :return: a DictPron with mapped phones

        """
        map_table.set_reverse(True)
        delimiters = ['-', '|']
        newdict = DictPron()

        for key, value in self._dict.items():
            newdict._dict[key] = map_table.map(value, delimiters)

        return newdict

    # -----------------------------------------------------------------------
    # File management
    # -----------------------------------------------------------------------

    def load_from_ascii(self, filename):
        """
        Load a pronunciation dictionary from an HTK-ASCII file.

        :param filename: (str) Pronunciation dictionary file name.

        """
        try:
            with codecs.open(filename, 'r', rutils.ENCODING) as fd:
                lines = fd.readlines()
        except ValueError as e:
            raise ValueError('Expected HTK ASCII dictionary format. Error while trying to open and read the file: %s' % str(e))

        for l, line in enumerate(lines):
            if len(line.strip()) == 0:
                continue
            try:
                line.index(u"[")
                line.index(u"]")
            except ValueError:
                raise ValueError('Expected HTK ASCII dictionary format. Error at line number %d: %s' % (l, line))

            # The entry is before the "[" and the pronunciation is after the "]"
            entry = line[:line.find(u"[")]
            newpron  = line[line.find(u"]")+1:]

            # Find if it is a new entry or a phonetic variant
            i = entry.find("(")
            if i > -1:
                if ")" in entry[i:]:
                    # Phonetic variant of an entry (i.e. entry ends with (XX))
                    entry = entry[:i]

            self.add_pron(entry, newpron)

    # -----------------------------------------------------------------------

    def save_as_ascii(self, filename, withvariantnb=True):
        """
        Save the pronunciation dictionary in HTK-ASCII format.

        :param filename: (str) Dictionary file name
        :param withvariantnb: (bool) Write the variant number or not.

        """
        try:
            with codecs.open(filename, 'w', encoding=rutils.ENCODING) as output:

                for entry, value in sorted(self._dict.iteritems(), key=lambda x:x[0]):
                    variants = value.split("|")

                    for i, variant in enumerate(variants, 1):
                        variant = variant.replace("-", " ")
                        if i > 1 and withvariantnb is True:
                            line = u"%s(%d) [%s] %s\n" % (entry, i, entry, variant)
                        else:
                            line = u"%s [%s] %s\n" % (entry, entry, variant)
                        output.write(line)

        except Exception as e:
            logging.info('Save the dict in ASCII failed: %s' % str(e))
            return False

        return True

    # -----------------------------------------------------------------------
