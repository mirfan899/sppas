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
# File: basicalign.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------


import sys
import os
import re
import codecs
import logging

import signals
from basealigner  import baseAligner


# ----------------------------------------------------------------------------


class basicAligner( baseAligner ):
    """
    Basic Alignment annotation (also called phonetic segmentation).

    This segmentation assign the same duration at each phoneme.
    In case of phonetic variants, the shortest possibility is selected.
    """

    def __init__(self, model, mapping, logfile=None):
        """
        Create a BasicAlign instance.

        BasicAlign aligns one inter-pausal unit with the same duration
        for each phoneme. Select the shortest in case of variants.

        """
        baseAligner.__init__(self, model, mapping, logfile)

    # End __init__
    # -----------------------------------------------------------------------


    def run_alignment(self, inputwav, basename, outputalign):
        """
        Execute the external program julius to align.

        @param inputwav is the wav input file name.
        @param basename is the name of the phon file
        @param outputalign is the output file name.

        """
        try:
            wavspeech = signals.open(inputwav)
            duration  = wavspeech.get_duration()
        except Exception:
            duration = 0.

        self.run_basic(duration, basename, outputalign)

    # End run_alignment
    # ------------------------------------------------------------------------


    def run_basic(self, duration, basename, outputalign):

        with codecs.open(basename, 'r', self._encoding) as fp:
            # Get the phoneme sequence
            phones = fp.readline()
            # Remove multiple spaces
            phones = re.sub("[ ]+", " ", phones)

        # Remove variants
        phoneslist = []
        tokenslist = phones.strip().split(" ")
        if len(tokenslist) == 0 or duration < 0.01:
            alignments = [(0., duration, "")]
            self.write_palign([], alignments, outputalign)
            return

        selecttokenslist = [] # selected pronunciation of each token
        i = 0
        for pron in tokenslist:
            token = self.__select(tokenslist[i])
            selecttokenslist.append( token.strip().replace("."," ") )
            phones = token.split(".")
            i = i + 1
            for p in phones:
                phoneslist.append(p)

        # Estimate the duration of a phone (in centiseconds)
        delta = ( duration / float(len(phoneslist)) ) * 100.0
        if delta < 1.:
            #raise Exception('Segmentation error: phones shorter than 10ms.')
            if self._logfile:
                self._logfile.print_message('Phones shorter than 10ms.', indent=3, status=-1)
            alignments = [(0., duration, "")]
            self.write_palign([], alignments, outputalign)
            return

        timeval = 0.0
        alignments = []
        for i in range(len(phoneslist)):
            tv1 = int(timeval)
            timeval = timeval + delta - 1
            tv2 = int(timeval)
            timeval = timeval + 1
            alignments.append( (tv1, tv2, phoneslist[i]) )

        # Write this result in a file
        self.write_palign(selecttokenslist, alignments, outputalign)

    # End run_basic
    # ------------------------------------------------------------------------


    def write_palign(self,tokenslist,alignments,outputfile):
        """
        Write an alignment file.

        @param tokenslist: is a list with the phonetization of each token
        @param alignments: is a list of tuples: (start-time end-time phoneme)
        @param outputfile: is the output file name (a Julius-like output).

        @raise IOError

        """

        with codecs.open(outputfile, 'w', self._encoding)as fp:

            fp.write("----------------------- System Information begin ---------------------\n")
            fp.write("\n")
            fp.write("                         SPPAS Basic Alignment\n")
            fp.write("\n")
            fp.write("----------------------- System Information end -----------------------\n")
            fp.write("### Recognition: 1st pass\n")
            fp.write("pass1_best_wordseq: ")
            for i in range(len(tokenslist)):
                fp.write(str(i)+" ")
            fp.write("\n")
            fp.write("pass1_best_phonemeseq: ")
            for i in range(len(tokenslist)-1):
                fp.write(str(tokenslist[i])+" | ")
            if len(tokenslist) > 0:
                fp.write(str(tokenslist[len(tokenslist)-1]))
            fp.write("\n")
            fp.write("### Recognition: 2nd pass\n")
            fp.write("ALIGN: === phoneme alignment begin ===\n")
            fp.write("wseq1: ")
            for i in range(len(tokenslist)):
                fp.write(str(i)+" ")
            fp.write("\n")
            fp.write("phseq1: ")
            for i in range(len(tokenslist)-1):
                fp.write(str(tokenslist[i])+" | ")
            if len(tokenslist) > 0:
                fp.write(str(tokenslist[len(tokenslist)-1]))
            fp.write("\n")
            fp.write("=== begin forced alignment ===\n")
            fp.write("-- phoneme alignment --\n")
            fp.write(" id: from  to    n_score    unit\n")
            fp.write(" ----------------------------------------\n")
            for i in range(len(alignments)):
                tv1,tv2,phon = alignments[i]
                fp.write("[ %d " % tv1)
                fp.write(" %d]" % tv2)
                fp.write(" -30.000000 "+str(phon)+"\n")
            fp.write("=== end forced alignment ===\n")
            fp.close()

    # End write_palign
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __select(self, pron):
        """ Select the shorter phonetization of an entry. """
        tab = pron.split("|")
        i=0
        m=len(tab[0])

        for n,p in enumerate(tab):
            if len(p)<m:
                i = n
                m = len(p)
        return tab[i]

    # End __select
    # ------------------------------------------------------------------------
