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
# File: storage.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
from os.path import *
import re

# ######################################################################### #


class DataRepetition(object):
    """
    Class to store a repetition (the source and the echo).
    """

    def __init__(self, s1, s2, r1, r2):
        self.s = (s1, s2)

        self.r = list()
        if r1 != -1 and r2 != -1:
            self.r.append((r1, r2))

    # ------------------------------------------------------------------

    def get_source(self):
        return self.s

    def get_repetition(self):
        return self.r

    def add_repetition(self, r1, r2):
        if (r1,r2) not in self.r:
            self.r.append((r1,r2))

    def print_echo(self):
        sys.stdout.write( "source: (%d,%d) ; " % (self.s[0],self.s[1]))
        sys.stdout.write( "repetitions: ")
        for rep in self.r:
            sys.stdout.write("(%d,%d)" % (rep[0],rep[1]))
        print

    # ------------------------------------------------------------------


class DataSpeaker(object):
    """
    Class to store data of a speaker.
    """

    def __init__(self, tokens, stopwords=None):
        self._stopwords  = stopwords
        self._tokens     = tokens

    # ------------------------------------------------------------------

    def get_token(self, idx):
        if idx >= len(self._tokens):
            return None
        return self.__clean( self._tokens[idx] )

    def get_size(self):
        return len(self._tokens)

    # ------------------------------------------------------------------

    def is_stopword(self, token):
        if self._stopwords is None:
            return False
        return not self._stopwords.is_unk( token )

    # ------------------------------------------------------------------

    def is_token(self, token):
        """
        Ask a string to be a token or not.

        Hesitations, silences, pauses and laughs are not considered as
        tokens.

        :param token (String)

        """
        if token is None:
            return False

        # Ensure all regexp will be efficient
        __tok = " " + self.__clean(token) + " "

        # Breaks, laughs...
        __tok = __tok.replace(u" # ", u" ")
        __tok = __tok.replace(u" + ", u" ")
        __tok = __tok.replace(u" * ", u" ")
        __tok = __tok.replace(u" @@ ", u" ")
        __tok = __tok.replace(u" @ ", u" ")
        __tok = __tok.replace(u" __ ", u" ")
        __tok = __tok.replace(u" sp ", u" ")
        __tok = __tok.replace(u" dummy ", u" ")

        # Hesitations
        __tok = __tok.replace(u" [m]?euh ", u" ")
        __tok = __tok.replace(u" euh ", u" ")
        __tok = __tok.replace(u" heu ", u" ")
        __tok = __tok.replace(u" hum ", u" ")
        __tok = __tok.replace(u" eeh ", u" ")
        __tok = __tok.replace(u" pff ", u" ")

        # Others
        __tok = self.__clean(__tok)

        if len(__tok)==0:
            return False
        return True

    # ------------------------------------------------------------------

    def get_next_token(self, current):
        """
        Ask for the index of the next token in an array of tokens.
        Return -1 if the next token cannot be found.

        :param current (int)

        """
        cnext = current + 1
        while cnext < len(self._tokens):
            if self.is_token(self._tokens[cnext]) is True:
                return cnext
            cnext = cnext + 1

        return -1

    # ------------------------------------------------------------------

    def is_token_repeat(self, current, othercurrent, otherspeaker):
        """
        Ask for a token to be repeated by the otherspeaker.
        Return the index of the repetition or -1.

        :param current (int)

        """

        # the token to search
        __c1 = self.__clean(self._tokens[current])
        # is it a token?
        if self.is_token( __c1 ) == False:
            return -1

        while othercurrent >= 0 and othercurrent < otherspeaker.get_size():
            othertoken = otherspeaker.get_token(othercurrent)
            __c2 = self.__clean(othertoken)
            if __c1 == __c2:
                return othercurrent
            # try next one
            othercurrent = otherspeaker.get_next_token(othercurrent)

        return -1

    # ------------------------------------------------------------------

    def __clean(self, entry):
        """ Clean a string by removing tabs, CR/LF, and some punctuation.
            Parameters:
                - entry is the string to clean
            Return:      A string without special chars
        """
        # Remove multiple spaces
        __str = re.sub(u"[\s]+", ur" ", entry)
        # Punct at end (or beginning)
        __str = re.sub(u"\-+$", ur"", __str)
        __str = re.sub(u">$", ur"", __str)
        __str = re.sub(u"^<", ur"", __str)

        # Spaces at beginning and end
        __str = re.sub(u"^[ ]+", ur"", __str)
        __str = re.sub(u"[ ]+$", ur"", __str)

        return __str.strip()

    # ------------------------------------------------------------------

    def __str__(self):
        return ' '.join(self._tokens).encode('utf8')

    # ------------------------------------------------------------------
