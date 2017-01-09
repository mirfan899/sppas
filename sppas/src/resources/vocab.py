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
# File: src.resources.vocab.py
# ---------------------------------------------------------------------------

import codecs
import logging

import rutils

# ---------------------------------------------------------------------------


class Vocabulary(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Class to represent a simple list of words.

    """
    def __init__(self, filename=None, nodump=False, case_sensitive=False):
        """
        Create a Vocabulary instance.

        :param filename: (str) The word list file name, i.e. a file with 1 column.
        :param nodump: (bool) Allows to disable the creation of a dump file.
        :param case_sensitive: (bool) the list of word is case-sensitive or not

        """
        self._stw = {}
        # with a dictionary it is faster to read tokens from a file and is
        # also faster to find a token in it!

        # Set the list of word to be case-sensitive or not.
        self.case_sensitive = case_sensitive

        if filename is not None:

            # Try first to get the dict from a dump file
            # (at least 2 times faster than the ascii one)
            data = rutils.load_from_dump(filename)

            # Load from ascii if: 1st load, or, dump load error, or dump older than ascii
            if data is None:
                self.load_from_ascii(filename)
                if nodump is False:
                    rutils.save_as_dump(self._stw, filename)
                logging.info('Got word list from ASCII file.')

            else:
                self._stw = data
                logging.info('Got word list from dumped file.')

    # -----------------------------------------------------------------------
    # Data management
    # -----------------------------------------------------------------------

    def add(self, entry):
        """
        Add an entry into the list except if the entry is already inside.

        :param entry: (str) The entry to add in the word list
        :return: (bool)

        """
        entry = entry.strip()
        if self.case_sensitive is False:
            entry = rutils.ToLower(entry)

        if entry not in self._stw:
            self._stw[entry] = 0
            return True

        return False

    # -----------------------------------------------------------------------

    def get_size(self):
        """ Return the number of entries in the list. """

        return len(self._stw)

    # -----------------------------------------------------------------------

    def get_list(self):
        """ Return the list of words, sorted in alpha-numeric order. """

        return sorted(self._stw.keys())

    # -----------------------------------------------------------------------

    def is_in(self, entry):
        """
        Return True if entry is in the list.

        :param entry: (str - IN)

        """
        return entry in self._stw

    # -----------------------------------------------------------------------

    def is_unk(self, entry):
        """
        Return True if entry is unknown (not in the list).

        :param entry: (str - IN)

        """
        return entry not in self._stw

    # -----------------------------------------------------------------------

    def copy(self):
        """
        Make a deep copy of the instance.

        :return: Vocabulary

        """
        s = Vocabulary()
        for i in self._stw:
            s.add(i)

        return s

    # -----------------------------------------------------------------------
    # File management
    # -----------------------------------------------------------------------

    def load_from_ascii(self, filename):
        """
        Read words from a file: one per line.

        :param filename: (str - IN)

        """
        with codecs.open(filename, 'r', rutils.ENCODING) as fd:
            for nbl, line in enumerate(fd, 1):
                try:
                    self.add(line)
                except Exception as e:
                    raise Exception("Read file failed due to the following error at line %s: %s" % (nbl, str(e)))

    # -----------------------------------------------------------------------

    def save(self, filename):
        """
        Save the list of words in a file.

        :param filename (str - OUT)
        :return (bool)

        """
        try:
            with codecs.open(filename, 'w', rutils.ENCODING) as fd:
                for word in sorted(self._stw.keys()):
                    fd.write("%s\n" % word)

        except Exception as e:
            logging.info('Save file failed due to the following error: %s' % str(e))
            return False

        return True

# ---------------------------------------------------------------------------
