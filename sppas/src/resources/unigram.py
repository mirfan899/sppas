#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# File: unigram.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------


class Unigram:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Class to represent a simple unigram: a serie of token/count.

    """

    def __init__(self):
        """
        Constructor.

        """
        self._sum  = 0
        self._dict = {}

    # End __init__
    # -------------------------------------------------------------------------


    def add(self, token):
        """
        Add or increment a token in the unigram.

        @param token

        """
        v = 1
        if self._dict.has_key(token):
            v = self._dict[token] + 1
        self._dict[token] = v
        self._sum = self._sum + 1

    # End add
    # -------------------------------------------------------------------------


    def get_value(self, token):
        """
        Get the count of a token.

        @param token

        """
        if self._dict.has_key(token):
            return self._dict[token]
        return 0

    # End get_value
    # -------------------------------------------------------------------------


    def get_sum(self):
        """
        Get the sum of all counts (of all tokens).

        """
        return self._sum

    # End get_sum
    # -------------------------------------------------------------------------


    def get_tokens(self):
        """
        Get a list with all tokens.

        """
        return self._dict.keys()

    # End get_tokens
    # -------------------------------------------------------------------------


    def get_size(self):
        """
        Get the number of tokens (vocab size).

        """
        return len(self._dict.keys())

    # End get_size
    # -------------------------------------------------------------------------

