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

    src.annotations.Repet.datastructs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Data structures to store repetitions.
    
"""
import sys
import re

# ----------------------------------------------------------------------------


class DataRepetition(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Class to store one repetition (the source and the echos).
    
    The source of a repetition is represented as a tuple (start, end).
    The echos of this latter are stored as a list of tuples (start, end).

    """
    def __init__(self, s1, s2, r1=-1, r2=-1):
        """ Create a DataRepetition data structure.

        :param s1: start position of the source.
        :param s2: end position of the source.
        :param r1: start position of an echo (or -1)
        :param r2: end position of an echo (or -1)

        """
        self.__source = None
        self.set_source(s1, s2)
        self.__echos = list()
        try:
            self.add_echo(r1, r2)
        except ValueError:
            pass

    # -----------------------------------------------------------------------

    def set_source(self, start, end):
        """ Set the positions of the source.

        :param start: Start position of the source.
        :param end: End position of the source.
        :raises: ValueError

        """
        s1 = int(start)
        s2 = int(end)
        if s1 > s2:
            raise ValueError
        if s1 < 0 or s2 < 0:
            raise ValueError
        self.__source = (s1, s2)

    # -----------------------------------------------------------------------

    def get_source(self):
        """ Return the tuple (start, end) of the source. """

        return self.__source

    # -----------------------------------------------------------------------

    def get_echos(self):
        """ Return the list of echos. """

        return self.__echos

    # -----------------------------------------------------------------------

    def add_echo(self, start, end):
        """ Add an entry in the list of echos.

        :param start: Start position of the echo.
        :param end: End position of the source.
        :raises: ValueError

        """
        r1 = int(start)
        r2 = int(end)
        if r1 > r2:
            raise ValueError
        if r1 < 0 or r2 < 0:
            raise ValueError

        if (r1, r2) not in self.__echos:
            self.__echos.append((r1, r2))

    # -----------------------------------------------------------------------

    def print_repetition(self):
        """ Print the repetition: the source and the echos on stdout. """

        sys.stdout.write("source: ({:d}, {:d}) ; ".format(self.__source[0], self.__source[1]))
        sys.stdout.write("repetitions: ")
        for rep in self.__echos:
            sys.stdout.write("({:d}, {:d}) ".format(rep[0], rep[1]))
        sys.stdout.write("\n")

# ---------------------------------------------------------------------------


class DataSpeaker(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Class to store data of a speaker.
    
    Data stored are:
    
        - a list of entries (tokens, lemmas, ...)
        - a list of stop-entries

    """
    def __init__(self, entries, stop_entries=None):
        """ Create a DataSpeaker instance.
        
        :param entries: (list)
        :param stop_entries: (Vocabulary)
        
        """
        self.__stoplist = stop_entries
        self.__entries = entries

    # -----------------------------------------------------------------------

    def get_token(self, idx):
        """ Return the "token" at the given index or None.

        :param idx: (int) Index of the entry to get
        :returns: (str) formatted entry or None

        """
        if idx < 0:
            return None
        if idx >= len(self.__entries):
            return None

        return self.__clean(self.__entries[idx])

    # -----------------------------------------------------------------------

    def is_stopword(self, token):
        """ Check if the given token is in the stop-list.

        :param token: (str)
        :returns: (bool)

        """
        if self.__stoplist is None:
            return False
        return not self.__stoplist.is_unk(token)

    # -----------------------------------------------------------------------

    def is_token(self, entry):
        """ Ask a string to be a token or not.
        Hesitations, silences, pauses and laughs are not considered as
        tokens.

        :param entry: (str)

        """
        if entry is None:
            return False

        # Ensure all regexp will be efficient
        __tok = " " + self.__clean(entry) + " "

        # Breaks, laughs...
        __tok = __tok.replace(" # ", " ")
        __tok = __tok.replace(" + ", " ")
        __tok = __tok.replace(" * ", " ")
        __tok = __tok.replace(" @@ ", " ")
        __tok = __tok.replace(" @ ", " ")
        __tok = __tok.replace(" __ ", " ")
        __tok = __tok.replace(" sp ", " ")
        __tok = __tok.replace(" dummy ", " ")

        # Hesitations
        __tok = __tok.replace(" [m]?euh ", " ")
        __tok = __tok.replace(" euh ", " ")
        __tok = __tok.replace(" heu ", " ")
        __tok = __tok.replace(" hum ", " ")
        __tok = __tok.replace(" eeh ", " ")
        __tok = __tok.replace(" pff ", " ")
        __tok = __tok.replace(" pf ", " ")

        # Others
        __tok = self.__clean(__tok)

        if len(__tok) == 0:
            return False
        return True

    # ------------------------------------------------------------------

    def get_next_token(self, current):
        """ Ask for the index of the next token in entries.
        Return -1 if the next token can't be found.

        :param current (int) Current position for finding the next token
        :returns: (int)

        """
        if current < 0:
            raise ValueError
        if current >= len(self.__entries):
            raise ValueError

        c_next = current + 1
        while c_next < len(self.__entries):
            if self.is_token(self.__entries[c_next]) is True:
                return c_next
            c_next += 1

        return -1

    # ------------------------------------------------------------------

    def is_token_repeated(self, current, other_current, other_speaker):
        """ Ask for a token to be repeated by the other speaker.
        Return the index of the repetition or -1.

        :param current: (int)
        :param other_current: (int)
        :param other_speaker: (DataSpeaker)

        """
        # the token to search
        __c1 = self.__clean(self.__entries[current])
        # is it a token?
        if self.is_token(__c1) is False:
            return -1

        while 0 < other_current < len(other_speaker):
            other_token = other_speaker.get_token(other_current)
            __c2 = self.__clean(other_token)
            if __c1 == __c2:
                return other_current
            # try next one
            other_current = other_speaker.get_next_token(other_current)

        return -1

    # ------------------------------------------------------------------

    def __clean(self, entry):
        """ Clean a string by removing tabs, CR/LF, and some punctuation.

        :param entry: (str) unicode string to clean
        :returns: unicode string without special chars

        """
        # Remove multiple whitespace
        __str = re.sub("[\s]+", " ", entry)

        # Punctuation at end or beginning
        __str = re.sub("\-+$", "", __str)
        __str = re.sub(">$", "", __str)
        __str = re.sub("^<", "", __str)

        # Whitespace at beginning and end
        __str = re.sub("^[ ]+", "", __str)
        __str = re.sub("[ ]+$", "", __str)

        return __str.strip()

    # ------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------

    def __str__(self):
        return " ".join(self.__entries)

    def __iter__(self):
        for a in self.__entries:
            yield a

    def __getitem__(self, i):
        return self.get_token(i)

    def __len__(self):
        return len(self.__entries)
