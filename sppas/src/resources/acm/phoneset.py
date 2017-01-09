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
# File: phoneset.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

from resources.dictpron import DictPron
from resources.vocab import Vocabulary

# ---------------------------------------------------------------------------


class PhoneSet( Vocabulary ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Manager of the list of phonemes.

    This class allows to manage the list of phonemes:

    - get it from a pronunciation dictionary,
    - read it from a file,
    - write it into a file,
    - check if a phone string is valid to be used with HTK toolkit.

    """
    def __init__(self, filename=None):
        """
        Constructor.
        Add events to the list: laughter, dummy, noise, silence.

        @param filename (str) is the phoneset file name, i.e. a file with 1 column.

        """
        Vocabulary.__init__(self, filename, nodump=True, casesensitive=True)
        self.add("@@")
        self.add("dummy")
        self.add("gb")
        self.add("sil")

    # -----------------------------------------------------------------------

    def add_from_dict(self, dictfilename):
        """
        Add the list of phones from a pronunciation dictionary.

        @param dictfilename (str) is the name of an HTK-ASCII pronunciation dictionary

        """
        d = DictPron( dictfilename ).get_dict()
        for value in d.values():
            variants = value.split("|")
            for variant in variants:
                phones = variant.split("-")
                for phone in phones:
                    self.add( phone )

    # -----------------------------------------------------------------------

    def check(self, phone):
        """
        Check if a phone is correct to be used with HTK toolkit.
        A phone can't start by a digit nor '-' nor '+', and must be ASCII.

        @param phone (str) the phone to be checked

        """
        # Must contain characters!
        if len(phone) == 0:
            return False

        if phone[0] in ['-', '+']:
            return False
        try:
            int(phone[0])
            str(phone)
        except Exception:
            return False

        return True

    # -----------------------------------------------------------------------
