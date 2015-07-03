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
# File: wavpitch.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import sys
import re

# ######################################################################### #

class Rules:
    """ SPPAS syllabification set of rules.
    """

    def __init__(self, filename):
        """ Create a new rules instance.
            Parameters:
                - filename is the file indicating syllabification rules.
        """
        self.load( filename )

    # End __init__
    # ------------------------------------------------------------------------


    def __initialize( self ):
        self.general   = {} # list of general rules
        self.exception = {} # list of exception rules
        self.gap       = {} # list of gap rules
        self.phonclass = {} # list of couples phoneme/classe


    def load (self, filename):
        """ Load the rules using the file "filename".
            Parameters:
                - filename is the name of the file where the rules are
            Return:      none
        """
        self.__initialize()
        with open(filename, "r") as file_in:

            for line_nb, line in enumerate(file_in, 1):
                line = re.sub("[ ]+", " ", line)
                line = line.strip()
                wds = line.split()
                if len(wds) > 2:
                    if wds[0] == "PHONCLASS":
                        if len(wds) != 3:
                            raise IOError('Syll::rules.py. Error: rule file corrupted at line number %d\n' % line_nb)
                        else:
                            self.phonclass[wds[1]] = wds[2]
                    elif wds[0] == "GENRULE":
                        if len(wds) != 3:
                            raise IOError('Syll::rules.py. Error: rule file corrupted at line number %d\n' % line_nb)
                        else:
                            self.general[wds[1]] = int(wds[2])
                    elif wds[0] == "EXCRULE":
                        if len(wds) != 3:
                            raise IOError('Syll::rules.py. Error: rule file corrupted at line number %d\n' % line_nb)
                        else:
                            self.exception[wds[1]] = int(wds[2])
                    elif wds[0] == "OTHRULE":
                        if len(wds) != 7:
                            raise IOError('Syll::rules.py. Error: rule file corrupted at line number %d\n' % line_nb)
                        else:
                            s = wds[1] + " " + wds[2] + " " + wds[3] + " " + wds[4] + " " + wds[5]
                            self.gap[s] = int(wds[6])
            if len(self.general) == 0:
                raise IOError('Syll::rules.py. Error: rule file corrupted: No rules found.\n')

    # End load
    # ------------------------------------------------------------------------


    def get_class(self, phoneme):
        """ Return the value of "phoneme" in phonclass.
            Parameters:  phoneme (string)
            Return:      the value of "phoneme" in phonclass
        """
        for key in self.phonclass.keys():
            if  key == phoneme:
                return self.phonclass[key]

        # If phoneme is not in phonclass
        #sys.stderr.write("Unknown phoneme: " + phoneme)
        return self.phonclass["UNK"]


    # End get_class
    # ------------------------------------------------------------------------


    def is_exception(self, rule):
        """ Return True if the rule is an exception rule.
            Parameters:  rule
            Return:      boolean
        """
        for exc in self.exception.keys():
            if exc == rule:
                return True
        return False

    # End is_exception
    # ------------------------------------------------------------------------


    def get_boundary(self, phonemes):
        """ Get the index of the syllable boundary (EXCRULES or GENRULES).
            Parameters:
                - phonemes to syllabify
            Return: boundary index (int value)
        """
        #sys.stderr.write("getting boundaries...\n") #c%
        classes = ""
        phonemes = phonemes.strip()
        phonList = phonemes.split(" ")
        for phon in phonList:
            classes += self.get_class(phon)

        #search into exception
        for key, val in self.exception.iteritems():
            if key == classes:
                return int(val)

        #search into general
        for key, val in self.general.iteritems():
            if len(key) == len(phonList):
                return int(val)

        return -1

    # End get_boundary
    # ------------------------------------------------------------------------


    def get_gap(self, phonemes):
        """ Return the shift to apply (OTHRULES).
            Parameters:
                - phonemes to syllabify
            Return: the boundary shift (int value)
        """
        for gp in self.gap.keys():
            if gp == phonemes:
                return self.gap[gp]

            # Search by replacing a phoneme by "ANY"
            if gp.find("ANY") > -1:
                r = gp.split(" ")
                phons = phonemes.split(" ")
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

    # End get_gap
    # ------------------------------------------------------------------------


    def print_rules(self):
        """ Used to debug!.
        """
        print("Association phonemes/classes: \n")
        for phon in self.phonclass.keys():
            print("Phoneme " + phon + ", Class %d\n" % self.phonclass[phon])
        print("General rules: ")
        for gen in self.general.keys():
            print(gen + " %d" % self.general[gen] + " %r" % self.is_exception(gen))
        for exc in self.exception.keys():
            print(exc + " %d" % self.exception[exc] + " %r" % self.is_exception(exc))
        for gp in self.gap.keys():
            print(gp + " %d" % self.gap[gp] + " %r" % self.is_exception(gp))

    # End get_gap
    # ------------------------------------------------------------------------
