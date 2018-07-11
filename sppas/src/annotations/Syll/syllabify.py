# -*- coding: UTF-8 -*-
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

    src.annotations.syllabify.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from .rules import Rules

# ----------------------------------------------------------------------------


class Syllabifier(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Syllabification of a sequence of phonemes.

    """
    def __init__(self, rules_filename):
        """ Create a new syllabification instance.

        Load rules from a text file, depending on the language and phonemes
        encoding. See documentation for details about this file.

        :param rules_filename: (str) Name of the file with the list of rules.

        """
        self.rules = Rules(rules_filename)

    # ------------------------------------------------------------------

    def annotate(self, phonemes):
        """ Return the syllable boundaries of a sequence of phonemes.

        :param phonemes: (list)
        :returns: list of tuples (begin index, end index)

        """
        # Convert a list of phonemes into a list of classes.
        classes = [self.rules.get_class(p) for p in phonemes]
        syllables = list()

        # Find the first vowel = first nucleus
        nucleus = Syllabifier._fix_nucleus(classes, 0)
        if nucleus == -1:
            return list()

        end_syll = -1
        while nucleus != -1:
            start_syll = self._fix_start_syll(classes, end_syll, nucleus)
            next_nucleus = Syllabifier._find_next_vowel(classes, nucleus+1)
            next_break = Syllabifier._find_next_break(classes, nucleus)

            # no rule to apply if the next event is a break.
            if next_break != -1 and next_break < next_nucleus:
                syllables.append((start_syll, next_break-1))
                nucleus = Syllabifier._find_next_vowel(classes, next_break)
            else:
                # apply the exception rule or the general one
                end_syll = self._apply_class_rules(classes, nucleus, next_nucleus)
                # apply the specific rules on phonemes to shift the end
                end_syll = self._apply_phon_rules(phonemes, end_syll, nucleus, next_nucleus)
                syllables.append((start_syll, end_syll))
                nucleus = next_nucleus

        return syllables

    # ------------------------------------------------------------------

    @staticmethod
    def _fix_nucleus(classes, from_index):
        """ Search for the next nucleus of a syllable. """

        next_nucleus = -1
        next_break = -1
        while next_break <= next_nucleus:
            next_nucleus = Syllabifier._find_next_vowel(classes, from_index)
            next_break = Syllabifier._find_next_break(classes, from_index)
            if next_nucleus == -1:
                return -1
            if next_break == -1:
                return next_nucleus
            from_index = next_nucleus
        return next_nucleus

    # ------------------------------------------------------------------

    @staticmethod
    def _fix_start_syll(classes, end_previous, nucleus):
        """ Search for the index of the first phoneme of the syllable. """

        # should not occur
        if end_previous == nucleus:
            return nucleus

        for i in reversed(range(end_previous, nucleus)):
            if i == -1:
                return 0
            if classes[i] in ("V", "W", Rules.BREAK_SYMBOL):
                return i+1

        # no break nor vowel between the end of the previous syllable
        # and the current nucleus
        return end_previous+1

    # ------------------------------------------------------------------

    def _apply_class_rules(self, classes, v1, v2):
        """ Apply the syllabification rules between v1 and v2. """

        sequence = "".join(classes[v1:v2+1])
        return v1 + self.rules.get_class_rules_boundary(sequence)

    # ------------------------------------------------------------------

    def _apply_phon_rules(self, phonemes, end_syll, v1, v2):
        """ Apply the specific phoneme-based syllabification rules between v1 and v2. """

        _str = ""
        nb = v2-v1
        if nb > 1:
            # specific rules are sequences of 5 consonants max
            if nb == 5:
                _str = "V "
            if nb < 5:
                _str = "ANY "*(5-nb) + "V "
            for i in range(1, nb):
                _str = _str + phonemes[v1+i] + " "
        _str = _str.strip()

        if len(_str) > 0:
            d = self.rules.get_gap(_str)
            if d != 0:
                # check validity before assigning...
                new_end = end_syll + d
                if v2 >= new_end >= v1:
                    end_syll = new_end

        return end_syll

    # ------------------------------------------------------------------

    @staticmethod
    def _find_next_vowel(classes, from_index):
        """ Find the index of the next vowel.

        -1 is returned if no longer vowel is existing.

        :param classes: (list) List of phoneme classes
        :param from_index: (int) the position where the search will begin
        (this from index is included in).
        :returns: the position of the next vowel or -1

        """
        for i in range(from_index, len(classes)):
            if classes[i] in ("V", "W"):
                return i
        return -1

    # ------------------------------------------------------------------

    @staticmethod
    def _find_next_break(classes, from_index):
        """ Find the index of the next break.

        -1 is returned if no longer break is existing.

        :param classes: (list) List of phoneme classes
        :param from_index: (int) the position where the search will begin
        :returns: the position of the next break or -1

        """
        for i in range(from_index, len(classes)):
            if classes[i] == Rules.BREAK_SYMBOL:
                return i
        return -1
