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
# File: src.annotations.Phon.phonetize.py
# ---------------------------------------------------------------------------

import re

from sppas.src.resources.rutils import to_strip
from sppas.src.resources.mapping import Mapping
from sppas.src.resources.dictpron import DictPron
from .. import ERROR_ID, WARNING_ID, OK_ID
from .phonunk import PhonUnk
from .dagphon import DAGPhon

# ---------------------------------------------------------------------------


class DictPhon(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Dictionary-based automatic phonetization.

    Grapheme-to-phoneme conversion is a complex task, for which a number of
    diverse solutions have been proposed. It is a structure prediction task;
    both the input and output are structured, consisting of sequences of
    letters and phonemes, respectively.

    This phonetization system is entirely designed to handle multiple
    languages and/or tasks with the same algorithms and the same tools.
    Only resources are language-specific, and the approach is based on the
    simplest resources as possible:
    this automatic annotation is using a dictionary-based approach.

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

    """
    def __init__(self, pdict, maptable=None):
        """
        Constructor.

        :param pdict: (DictPron) The pronunciation dictionary.
        :param maptable: (Mapping) A mapping table for phones.

        """
        self._pdict = None
        self._phonunk = None
        self._map_table = Mapping()
        self._dag_phon = DAGPhon()

        self.set_dict(pdict)
        self.set_maptable(maptable)

    # -----------------------------------------------------------------------

    def set_dict(self, pdict):
        """
        Set the dictionary.

        :param pdict (DictPron) The pronunciation dictionary.

        """
        if isinstance(pdict, DictPron) is False:
            raise TypeError('Expected a DictPron instance.')

        self._pdict = pdict
        self._phonunk = PhonUnk(self._pdict.get_dict())

    # -----------------------------------------------------------------------

    def set_maptable(self, map_table):
        """
        Set the dictionary.

        :param map_table (Mapping) The mapping table dictionary.

        """
        if map_table is not None:
            if isinstance(map_table, Mapping) is False:
                raise TypeError('Expected a Mapping instance.')
        else:
            map_table = Mapping()

        self._map_table = map_table
        self._map_table.set_keep_miss(False)

    # -----------------------------------------------------------------------

    def get_phon_entry(self, entry):
        """
        Return the phonetization of an entry.
        Unknown entries are not automatically phonetized.
        This is a pure dictionary-based method.

        :param entry: (str) The token to phonetize.
        :returns: A string with the phonetization of the given entry or
        the unknown symbol.

        """
        entry = to_strip(entry)

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
        if entry.startswith(u"ipu_"):
            return ""

        # Find entry in the dict as it is given
        _strphon = self._pdict.get_pron(entry)

        # OK, the entry is properly phonetized.
        if _strphon != self._pdict.get_unkstamp():
            return self._map_phonentry(_strphon)

        return self._pdict.get_unkstamp()

    # -----------------------------------------------------------------------

    def get_phon_tokens(self, tokens, phonunk=True):
        """
        Return the phonetization of a list of tokens, with the status.
        Unknown entries are automatically phonetized if `phonunk` is set to True.

        :param `tokens` (list) is the list of tokens to phonetize.
        :param `phonunk` (bool) Phonetize unknown words (or not).
        @todo EOT is not fully supported.

        @return A list with the tuple (token, phon, status).

        """
        tab = []

        for entry in tokens:
            phon = self._pdict.get_unkstamp()
            status = OK_ID

            # Enriched Orthographic Transcription Convention:
            # entry can be already in SAMPA.
            if entry.startswith("/") is True and entry.endswith("/") is True:
                phon = entry.strip("/")
                # Must use SAMPA (including minus to separate phones)

            else:

                phon = self.get_phon_entry(entry)

                if phon == self._pdict.get_unkstamp():
                    status = ERROR_ID

                    # A missing compound word?
                    if "-" in entry or "'" in entry or "_" in entry:
                        _tabpron = [self.get_phon_entry(w) for w in re.split(u"[-'_]", entry)]

                        # OK, finally the entry is in the dictionary?
                        if self._pdict.get_unkstamp() not in _tabpron:
                            # ATTENTION: each part can have variants! must be decomposed.
                            self._dag_phon.variants = 4
                            phon = to_strip(self._dag_phon.decompose(" ".join(_tabpron)))
                            status = WARNING_ID

                    if phon == self._pdict.get_unkstamp() and phonunk is True:
                        try:
                            phon = self._phonunk.get_phon(entry)
                            status = WARNING_ID
                        except Exception:
                            pass

            tab.append((entry, phon, status))

        return tab

    # -----------------------------------------------------------------------

    def phonetize(self, utterance, phonunk=True, delimiter=" "):
        """
        Return the phonetization of an utterance.

        :param `utterance` (str) is the utterance to phonetize.
        :param `phonunk` (bool) Phonetize unknown words (or not).
        :param `delimiter` (char) The character to use as tokens separator in `utterance`.

        @return A string with the phonetization of `utterance`.

        """
        if len(delimiter) > 1:
            raise TypeError('Delimiter must be a character.')

        tab = self.get_phon_tokens(utterance.split(delimiter), phonunk)
        tab_phon = [t[1] for t in tab]

        return delimiter.join(tab_phon).strip()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _map_phonentry(self, phonentry):
        """
        Map phonemes of a phonetized entry.

        :param phonentry: (str) Phonetization of an entry.

        """
        if self._map_table.is_empty() is True:
            return phonentry

        tab = [self._map_variant(v) for v in phonentry.split(DictPron.VARIANTS_SEPARATOR)]

        return DictPron.VARIANTS_SEPARATOR.join(tab)

    # -----------------------------------------------------------------------

    def _map_variant(self, phonvariant):
        """
        Map phonemes of only one variant of a phonetized entry.

        :param phonvariant: (str) One phonetization variant of an entry.

        """
        phones = self._map_split_variant(phonvariant)
        subs = []
        # Single phonemes
        for p in phones:
            mapped = self._map_table.map_entry(p)
            if len(mapped)>0:
                subs.append(p + DictPron.VARIANTS_SEPARATOR + mapped)
            else:
                subs.append(p)

        self._dag_phon.variants = 0
        phon = to_strip(self._dag_phon.decompose(" ".join(subs)))

        # Remove un-pronounced phonemes!!!
        # By convention, they are represented by an underscore in the
        # mapping table.
        tmp = []
        for p in phon.split(DictPron.VARIANTS_SEPARATOR):
            r = [x for x in p.split(DictPron.PHONEMES_SEPARATOR) if x != "_"]
            tmp.append(DictPron.PHONEMES_SEPARATOR.join(r))

        return DictPron.VARIANTS_SEPARATOR.join(set(tmp))

    # -----------------------------------------------------------------------

    def _map_split_variant(self, phonvariant):
        """
        Return a list of the longest phone sequences.

        :param phonvariant: (str) One phonetization variant of an entry.

        """
        phones = phonvariant.split(DictPron.PHONEMES_SEPARATOR)
        if len(phones) == 1:
            return phones

        tab = []
        idx = 0
        maxidx = len(phones)

        while idx < maxidx:
            # Find the index of the longest phone sequence that can be mapped
            leftindex = self.__longestlr(phones[idx:maxidx])
            # Append such a longest sequence in tab
            s = DictPron.PHONEMES_SEPARATOR
            tab.append(s.join(phones[idx:idx+leftindex]))
            idx += leftindex

        return tab

    # -----------------------------------------------------------------------

    def __longestlr(self, tabentry):
        """
        Select the longest map of an entry.

        """
        i = len(tabentry)
        while i > 0:
            # Find in the map table a substring from 0 to i
            entry = DictPron.PHONEMES_SEPARATOR.join(tabentry[:i])
            if self._map_table.is_key(entry):
                return i
            i -= 1

        # Did not find any map for this entry! Return the shortest.
        return 1

    # -----------------------------------------------------------------------
