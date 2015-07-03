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
# File: phonetize.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import re

from resources.dictpron import DictPron
from resources.phonunk  import PhonUnk
import resources.rutils as rutils



# ---------------------------------------------------------------------------
# sppasPhon main class
# ---------------------------------------------------------------------------

class DictPhon:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Phonetization automatic annotation.

    Grapheme-to-phoneme conversion is a complex task, for which a number of
    diverse solutions have been proposed. It is a structure prediction task;
    both the input and output are structured, consisting of sequences of
    letters and phonemes, respectively.

    The phonetization system is entirely designed to handle multiple
    languages and/or tasks with the same algorithms and the same tools.
    Only resources are language-specific, and the approach is based on the
    simplest resources as possible:
    This annotation is using a dictionary-based approach.

    The dictionary can contain words with a set of pronunciations (the
    canonical one, and optionally some common reductions, etc).
    In this approach, it is then assumed that most of the words of the speech
    transcription and their phonetic variants are mentioned in
    the pronunciation dictionary. If a word is missing, our system is based
    on the idea that given enough examples it should be possible to predict
    the pronunciation of unseen words purely by analogy.

    See the whole description in the following reference:

    Brigitte Bigi (2013).
    A phonetization approach for the forced-alignment task.
    3rd Less-Resourced Languages workshop,
    6th Language & Technology Conference, Poznan (Poland).

    """

    def __init__(self, pdict, logfile=None):
        """
        Create a new instance.

        @param pdict (DictPron) is the dictionary.
        @param logfile

        """

        # Log output to print warnings
        self._logfile = logfile

        # Symbol to represent missing entries in the dictionary
        # (also called unknown entries)
        self._unk = rutils.UNKNOWN_SYMBOL

        # Assign the dictionary, without loading it.
        self.pdict = pdict

    # End __init__
    # -----------------------------------------------------------------------


    def set_dict(self,pdict):
        """
        Set the dictionary.

        @param pdict is a DictPron().

        """
        self.pdict = pdict

    # -------------------------------------------------------------------------


    def get_phon(self,entry):
        """
        Return the phonetization of an entry or the symbol for unknown entries.

        @param entry (String) The token to phonetize

        """
        entry = rutils.ToStrip(entry)
        entry = re.sub(u"\-+$", ur"", entry)

        # Specific strings... for the italian transcription... (CLIPS-Evalita)
        idx = entry.find(u"<")
        if idx>1 and entry.find(u">")>-1:
            entry = entry[:idx]

        # No entry!!
        if len(entry) == 0:
            return ""

        # Stecific strings... for the CID transcription...
        if entry.find(u"gpd_")>-1 or entry.find(u"gpf_")>-1:
            return ""

        # SPPAS convention for IPU segmentation
        if entry.find(u"ipu_")>-1:
            return ""

        # Find entry in the dict as it is given
        _strphon = self.pdict.get_pron( entry )

        # OK, the entry is in the dictionary
        if _strphon != self._unk:
            return _strphon

        # A missing compound word?
        if entry.find(u"-")>-1 or entry.find(u"'")>-1 or entry.find(u"_")>-1:
            _strphon = ""
            _tabstr = re.split(u"[-'_]",entry)
            # ATTENTION: each part can have variants!
            for _w in _tabstr:
                _strphon = _strphon + " " + self.pdict.get_pron( _w )

        # OK, finally the entry is in the dictionary?
        if _strphon.find( self._unk )>-1:
            return self._unk

        return _strphon

    # End get_phon
    # -----------------------------------------------------------------------


    def phonetize(self, unit, phonunk):
        """
        Return the phonetization of an utterance.

        It is supposed that words of the utterance are separated by spaces.

        @param unit (String) is the utterance to phonetize
        @return A string with the phonetization, with the following convention:
                - spaces separate words,
                - dots separate phones,
                - pipes separate pronunciation variants.

        """
        # Clean the unit
        _s = rutils.ToStrip(unit)

        # Verification
        if len(unit)==0:
            return ""

        # EXCEPTION: specific case of "+", which is phonetized by #...
        if _s=="+": # only one short pause in the unit
            return "sp"

        # Array with each entry to phonetize
        entries = _s.split(" ")
        tabphon = []
        unkinst = PhonUnk( self.pdict.get_dict() )

        # Phonetize each entry
        for entry in entries:
            _phon = ""
            entry = rutils.ToLower(entry)

            # convention TOE: enrty in sampa (the entry is already phonetized)
            if entry.startswith("/") and entry.endswith("/"):
                _phon = entry.strip("/")
                # Must convert SAMPA to SPPAS: phoneset and convention
                # TO DO

            elif self.pdict.is_unk( entry ) is True and phonunk is True:
                # Create an instance to phonetize unknown entries of the unit
                try:
                    _phon = unkinst.get_phon( entry )
                except Exception:
                    _phon = self._unk
                if self._logfile:
                    self._logfile.print_message('Unknown word phonetization: '+entry,indent=3,status=1)
                    self._logfile.print_message('Proposed phonetization is: '+_phon,indent=3,status=3)

            elif self.pdict.is_unk( entry ) is True:
                _phon = self._unk
                if self._logfile:
                    try:
                        self._logfile.print_message('Unknown word phonetization: '+entry,indent=3,status=1)
                    except Exception:
                        pass

            else:
                _phon = self.pdict.get_pron( entry )

            tabphon.append( _phon )
        
        # Concatenate entries into a phonetized string
        _s = " "
        return _s.join(tabphon)

    # End phonetize
    # -----------------------------------------------------------------------

# End DictPhon
# ---------------------------------------------------------------------------
