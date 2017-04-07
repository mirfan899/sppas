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

    src.annotations.rules.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import re

from sppas.src.utils.makeunicode import sppasUnicode

# ----------------------------------------------------------------------------


class Rules(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS syllabification set of rules.
    """

    def __init__(self, filename=None):
        """ Create a new Rules instance.

        :param filename: (str) Name of the file with the syllabification rules.
        """
        self.general = dict()    # list of general rules
        self.exception = dict()  # list of exception rules
        self.gap = dict()        # list of gap rules
        self.phonclass = dict()  # list of couples phoneme/classe

        if filename is not None:
            self.load(filename)

    # ------------------------------------------------------------------------

    def load(self, filename):
        """ Load the rules using the file "filename".

        :param filename: (str) Name of the file with the syllabification rules.

        """
        self.general = dict()    # list of general rules
        self.exception = dict()  # list of exception rules
        self.gap = dict()        # list of gap rules
        self.phonclass = dict()  # list of couples phoneme/classe
        with open(filename, "r") as file_in:

            for line_nb, line in enumerate(file_in, 1):
                sp = sppasUnicode(line)
                line = sp.to_strip()

                wds = line.split()
                if len(wds) == 3:
                    if wds[0] == "PHONCLASS":
                        self.phonclass[wds[1]] = wds[2]
                    elif wds[0] == "GENRULE":
                        self.general[wds[1]] = int(wds[2])
                    elif wds[0] == "EXCRULE":
                        self.exception[wds[1]] = int(wds[2])
                if len(wds) == 7:
                    if wds[0] == "OTHRULE":
                        s = " ".join(wds[1:6])
                        self.gap[s] = int(wds[6])

        if len(self.general) < 4:
            raise IOError('Syllabification rules file corrupted. '
                          'Got {:d} general rules, {:d} exceptions '
                          'and {:d} other rules.'.format(len(self.general), len(self.exception), len(self.gap)))

        if "UNK" not in self.phonclass:
            self.phonclass["UNK"] = "#"

    # ------------------------------------------------------------------------

    def get_class(self, phoneme):
        """ Return the class identifier of the phoneme.

        :param phoneme: (str)
        :returns: class of the phoneme

        """
        if phoneme in self.phonclass:
            return self.phonclass[phoneme]

        return self.phonclass["UNK"]

    # ------------------------------------------------------------------------

    def is_exception(self, rule):
        """ Return True if the rule is an exception rule.

        :param rule:

        """
        return rule in self.exception

    # ------------------------------------------------------------------------

    def get_boundary(self, phonemes):
        """ Get the index of the syllable boundary (EXCRULES or GENRULES).

        :param phonemes: (str) Phonemes to syllabify
        :returns: (int) boundary index or -1 if phonemes does not match any rule.

        """
        sp = sppasUnicode(phonemes)
        phonemes = sp.to_strip()
        phon_list = phonemes.split(" ")
        classes = ""
        for phon in phon_list:
            classes += self.get_class(phon)

        # search into exception
        if classes in self.exception:
            return self.exception[classes]

        # search into general
        for key, val in self.general.items():
            if len(key) == len(phon_list):
                return val

        return -1

    # ------------------------------------------------------------------------

    def get_gap(self, phonemes):
        """ Return the shift to apply (OTHRULES).

        :param phonemes: (str) Phonemes to syllabify
        :returns: (int) boundary shift

        """
        for gp in self.gap:
            if gp == phonemes:
                return self.gap[gp]

            # Search by replacing a phoneme by "ANY"
            if gp.find("ANY") > -1:
                r = gp.split()
                phons = phonemes.split()
                new_phonemes = ""
                if len(r) == len(phons):
                    # For each phoneme, replace the ANY
                    for ph in range(len(r)):
                        if r[ph] == "ANY":
                            new_phonemes += "ANY "
                        else:
                            new_phonemes += phons[ph] + " "
                    new_phonemes = new_phonemes.strip()

                if gp == new_phonemes:
                    return self.gap[gp]

        return 0
