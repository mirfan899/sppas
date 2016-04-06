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
# File: phonetize.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import re

import resources.rutils as rutils
from phonunk import PhonUnk
from sp_glob import ERROR_ID, WARNING_ID, OK_ID

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

        > Brigitte Bigi (2013).
        > A phonetization approach for the forced-alignment task.
        > 3rd Less-Resourced Languages workshop,
        > 6th Language & Technology Conference, Poznan (Poland).

    DictPhon is using the following convention:
        - dots separate phones,
        - pipes separate pronunciation variants.

    """
    def __init__(self, pdict):
        """
        Constructor.

        @param pdict (DictPron) is the pronunciations dictionary.

        """
        self.set_dict( pdict )

    # -----------------------------------------------------------------------

    def set_dict(self, pdict):
        """
        Set the dictionary.

        @param pdict (DictPron) The pronunciation dictionary.

        """
        self._pdict = pdict
        self._phonunk = PhonUnk( self._pdict.get_dict() )

    # -------------------------------------------------------------------------

    def get_phon_entry(self, entry):
        """
        Return the phonetization of an entry or the symbol for unknown entries.

        @param `entry` (str) The token to phonetize
        @return A string with the phonetization of `entry`

        """
        entry = rutils.ToStrip(entry)
        entry = re.sub(u"\-+$", ur"", entry)

        # Specific strings... for the italian transcription...
        # For the participation at the CLIPS-Evalita 2011 campaign.
        if entry.startswith(u"<") is True and entry.endswith(u">") is True:
            entry = entry[1:-1]

        # No entry! Nothing to do.
        if len(entry) == 0:
            return ""

        # Specific strings used in the CID transcription...
        # CID is Corpus of Interactional Data, http://sldr.org/sldr000720
        if entry.startswith(u"gpd_") is True or entry.startswith(u"gpf_") is True:
            return ""

        # Specific strings used in SPPAS IPU segmentation...
        if entry.find(u"ipu_")>-1:
            return ""

        # Find entry in the dict as it is given
        _strphon = self._pdict.get_pron( entry )

        # OK, the entry is in the dictionary
        if _strphon != self._pdict.unkstamp:
            return _strphon

        # A missing compound word?
        if "-" in entry or "'" in entry or "_" in entry:
            _strphon = ""
            _tabstr = re.split(u"[-'_]",entry)
            # ATTENTION: each part can have variants!
            for w in _tabstr:
                _strphon = _strphon + " " + self._pdict.get_pron( w )

        # OK, finally the entry is in the dictionary?
        if self._pdict.unkstamp in _strphon:
            return self._pdict.unkstamp

        return rutils.ToStrip(_strphon)

    # -----------------------------------------------------------------------

    def get_phon_tokens(self, tokens, phonunk=True):
        """
        Return the phonetization of a list of tokens, with the status.

        @param `tokens` (list) is the list of tokens to phonetize.
        @param `phonunk` (bool) Phonetize unknown words (or not).

        @return A list with the tuple (token, phon, status).

        """
        tab = []

        for entry in tokens:
            phon   = self._pdict.unkstamp
            status = OK_ID

            # Convention TOE: entry is already in SAMPA
            if entry.startswith("/") is True and entry.endswith("/") is True:
                phon = entry.strip("/")
                # Must be converted to our convention (dots to separate phones)
                # TODO

            else:

                if self._pdict.is_unk( entry ) is True:
                    status = ERROR_ID
                    if phonunk is True:
                        try:
                            phon   = self._phonunk.get_phon( entry )
                            status = WARNING_ID
                        except Exception:
                            pass

                else:
                    phon = self.get_phon_entry(entry)

            tab.append( (entry,phon,status) )

        return tab

    # -----------------------------------------------------------------------

    def phonetize(self, utterance, phonunk=True, delimiter=" "):
        """
        Return the phonetization of an utterance.

        @param `utterance` (str) is the utterance to phonetize.
        @param `phonunk` (bool) Phonetize unknown words (or not).
        @param `delimiter` (char) The character to use as tokens separator in `utterance`.

        @return A string with the phonetization of `utterance`.

        """
        if len(delimiter) > 1:
            raise TypeError('Delimiter must be a character.')

        tab = self.get_phon_tokens( utterance.split(delimiter), phonunk)
        tabphon = [t[1] for t in tab]

        return delimiter.join( tabphon ).strip()

    # -----------------------------------------------------------------------
