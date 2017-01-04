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
# File: src.resources.unigram.py
# ----------------------------------------------------------------------------

import codecs
import logging

import rutils

# ----------------------------------------------------------------------------


class Unigram(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Class to represent a simple unigram: a set of token/count.

    """
    def __init__(self, filename=None, nodump=True):
        """
        Constructor.

        :param filename: (str) The unigram file name (2 columns)
        :param nodump: (bool) Disable the creation of a dump file

        """
        self._sum = 0
        self._dict = {}

        if filename is not None:

            data = None
            if nodump is False:
                # Try first to get the dict from a dump file (at least 2 times faster)
                data = rutils.load_from_dump(filename)

            # Load from ascii if: 1st load, or, dump load error, or dump older than ascii
            if data is None:
                self.load_from_ascii(filename)
                if nodump is False:
                    rutils.save_as_dump(self._dict, filename)
            else:
                self._dict = data

    # -------------------------------------------------------------------------

    def add(self, token, value=1):
        """
        Add or increment a token in the unigram.

        :param token: (str) The string of the token to add
        :param value: (int) The value to increment

        """
        self._dict[token] = self._dict.get(token, 0) + value
        self._sum += value

    # -------------------------------------------------------------------------

    def get_count(self, token):
        """
        Return the count of a token.

        :param token: (str) The string of the token

        """
        return self._dict.get(token, 0)

    # -------------------------------------------------------------------------

    def get_sum(self):
        """ Return the sum of all counts (of all tokens). """

        return self._sum

    # -------------------------------------------------------------------------

    def get_tokens(self):
        """ Return a list with all tokens. """

        return self._dict.keys()

    # -------------------------------------------------------------------------

    def get_size(self):
        """ Return the number of tokens (vocab size). """

        return len(self._dict)

    # ------------------------------------------------------------------------
    # File
    # ------------------------------------------------------------------------

    def load_from_ascii(self, filename):
        """
        Load a unigram from a file with two columns: word freq.

        :param filename (str)

        """
        with codecs.open(filename, 'r', rutils.ENCODING) as fd:
            lines = fd.readlines()

        for line in lines:
            line = " ".join(line.split())
            if len(line) == 0:
                continue

            tabline = line.split()
            if len(tabline) < 2:
                continue

            # Add (or modify) the entry in the dict
            key = tabline[0]
            value = int(tabline[1])
            self.add(key, value)

    # -------------------------------------------------------------------------

    def save_as_ascii(self, filename):
        """
        Save a unigram into a file with two columns: word freq.

        :param filename (str)
        :return: (bool)

        """
        try:
            with codecs.open(filename, 'w', encoding=rutils.ENCODING) as output:
                for entry, value in sorted(self._dict.iteritems(), key=lambda x:x[0]):
                    output.write("%s %d\n"%(entry,value))
        except Exception as e:
            logging.info('Save file failed due to the following error: %s' % str(e))
            return False

        return True

    # ------------------------------------------------------------------------
