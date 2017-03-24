"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.resources.vocab.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
import codecs
import logging

from sppas import encoding
from sppas.src.utils.makeunicode import sppasUnicode

from .resourcesexc import FileFormatError
from .dumpfile import DumpFile

# ---------------------------------------------------------------------------


class Vocabulary(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Class to represent a list of words.

    """
    def __init__(self, filename=None, nodump=False, case_sensitive=False):
        """ Create a Vocabulary instance.

        :param filename: (str) Name of the file with the list of words.
        :param nodump: (bool) Allows to disable the creation of a dump file.
        :param case_sensitive: (bool) the list of word is case-sensitive or not

        """
        # A list of (unicode) entries
        self.__entries = dict()

        # Set the list of entries to be case-sensitive or not.
        self.__case_sensitive = case_sensitive

        if filename is not None:

            dp = DumpFile(filename)

            # Try first to get the dict from a dump file
            # (at least 2 times faster than the ascii one)
            data = dp.load_from_dump()

            # Load from ascii if: 1st load, or, dump load error, or dump older than ascii
            if data is None:
                self.load_from_ascii(filename)
                if nodump is False:
                    dp.save_as_dump(self.__entries)
                logging.info('Vocabulary loaded from ASCII file.')

            else:
                self.__entries = data
                logging.info('Vocabulary loaded from dump file.')

    # -----------------------------------------------------------------------
    # Data management
    # -----------------------------------------------------------------------

    def add(self, entry):
        """ Add an entry into the list except if the entry is already inside.

        :param entry: (str) The entry to add in the word list
        :returns: (bool)

        """
        s = sppasUnicode(entry)
        entry = s.to_strip()
        if self.__case_sensitive is False:
            s = sppasUnicode(entry)
            entry = s.to_lower()

        if entry not in self.__entries:
            self.__entries[entry] = None
            return True

        return False

    # -----------------------------------------------------------------------

    def get_size(self):
        """ Return the number of entries in the list. """

        return len(self.__entries)

    # -----------------------------------------------------------------------

    def get_list(self):
        """ Return the list of entries, sorted in alpha-numeric order. """

        return sorted(self.__entries.keys())

    # -----------------------------------------------------------------------

    def is_in(self, entry):
        """ Return True if entry is in the list.

        :param entry: (str)

        """
        return entry in self.__entries

    # -----------------------------------------------------------------------

    def is_unk(self, entry):
        """ Return True if entry is unknown (not in the list).

        :param entry: (str)

        """
        return entry not in self.__entries

    # -----------------------------------------------------------------------

    def copy(self):
        """ Make a deep copy of the instance.

        :returns: Vocabulary

        """
        s = Vocabulary()
        for i in self.__entries:
            s.add(i)

        return s

    # -----------------------------------------------------------------------
    # File management
    # -----------------------------------------------------------------------

    def load_from_ascii(self, filename):
        """ Read words from a file: one per line.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', encoding) as fd:
            for nbl, line in enumerate(fd, 1):
                try:
                    self.add(line)
                except Exception:
                    raise FileFormatError(nbl, line)

    # -----------------------------------------------------------------------

    def save(self, filename):
        """ Save the list of words in a file.

        :param filename (str)
        :returns: (bool)

        """
        try:
            with codecs.open(filename, 'w', encoding) as fd:
                for word in sorted(self.__entries.keys()):
                    fd.write("{:s}\n".format(word))

        except Exception as e:
            logging.info('Save file failed due to the following error: {:s}'.format(str(e)))
            return False

        return True

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__entries)

    # ------------------------------------------------------------------------

    def __contains__(self, item):
        return item in self.__entries
