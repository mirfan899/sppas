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

import re
import codecs

import signals
from basealigner  import BaseAligner
from sp_glob import encoding

# ----------------------------------------------------------------------------

class BasicAligner( BaseAligner ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Basic automatic alignment system.

    This segmentation assign the same duration to each phoneme.
    In case of phonetic variants, the shortest phonetization is selected.

    """
    def __init__(self, modelfilename, mapping=None):
        """
        Constructor.

        BasicAlign aligns one inter-pausal unit with the same duration
        for each phoneme. It selects the shortest in case of variants.

        @param modelfilename (str) the acoustic model file name
        @param mapping (Mapping) a mapping table to convert the phone set

        """
        BaseAligner.__init__(self, modelfilename, mapping)
        self._outext = "palign"

    # -----------------------------------------------------------------------

    def run_alignment(self, inputwav, basename, outputalign):
        """
        Perform the speech segmentation.

        Assign the same duration to each phoneme.

        @param inputwav (str or float) the audio input file name, of type PCM-WAV 16000 Hz, 16 bits; or its duration
        @param basename (str or None) the base name of the grammar file and of the dictionary file
        @param outputalign (str) the output file name

        @return Empty string.

        """
        if isinstance(inputwav, float) is True:
            duration = inputwav
        else:
            try:
                wavspeech = signals.open( inputwav )
                duration  = wavspeech.get_duration()
            except Exception:
                duration = 0.

        phones = ""
        if basename is not None:
            with codecs.open(basename, 'r', encoding) as fp:
                # Get the phoneme sequence and Remove multiple spaces
                phones = fp.readline()
                phones = re.sub("[ ]+", " ", phones)

        self.run_basic(duration, phones, outputalign)

        return ""

    # ------------------------------------------------------------------------

    def run_basic(self, duration, phones, outputalign=None):
        """
        Perform the speech segmentation.

        Assign the same duration to each phoneme.

        @param duration (float) the duration of the audio input
        @param phones (str) the phonetization to time-align
        @param outputalign (str) the output file name

        @return the List of tuples (begin, end, phone)

        """
        # Remove variants: Select the first-shorter pronunciation of each token
        phoneslist = []
        tokenslist = phones.strip().split(" ")
        selecttokenslist = []
        delta = 0.
        for pron in tokenslist:
            token = self.__select(pron)
            phoneslist.extend( token.split() )
            selecttokenslist.append( token.replace("."," ") )

        # Estimate the duration of a phone (in centi-seconds)
        if len(phoneslist) > 0:
            delta = ( duration / float(len(phoneslist)) ) * 100.

        # Generate the result
        if delta < 1. or len(selecttokenslist) == 0:
            return self.gen_alignment([], [], int(duration*100.), outputalign)

        return self.gen_alignment(selecttokenslist, phoneslist, int(delta), outputalign)

    # ------------------------------------------------------------------------

    def gen_alignment(self, tokenslist, phoneslist, phonesdur, outputalign=None):
        """
        Write an alignment in an output file.

        @param tokenslist (list) phonetization of each token
        @param phoneslist (list) each phone
        @param phonesdur (int) the duration of each phone in centi-seconds
        @param outputalign (str) the output file name

        """
        timeval = 0
        alignments = []
        for phon in phoneslist:
            tv1 = timeval
            tv2 = timeval + phonesdur - 1
            alignments.append( (tv1, tv2, phon) )
            timeval = tv2 + 1

        if len(alignments) == 0:
            alignments = [(0, int(phonesdur), "")]

        if outputalign is not None:
            if outputalign.endswith('palign'):
                self.write_palign(tokenslist, alignments, outputalign)

        return alignments

    # ------------------------------------------------------------------------

    def write_palign(self, tokenslist, alignments, outputfilename):
        """
        Write an alignment output file.

        @param tokenslist (list) List with the phonetization of each token
        @param alignments (list) List of tuples: (start-time end-time phoneme)
        @param outputfilename (str) The output file name (a Julius-like output).

        """
        with codecs.open(outputfilename, 'w', encoding) as fp:

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
            for tv1,tv2,phon in alignments:
                fp.write("[ %d " % tv1)
                fp.write(" %d]" % tv2)
                fp.write(" -30.000000 "+str(phon)+"\n")
            fp.write("=== end forced alignment ===\n")

            fp.close()

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __select(self, pron):
        """
        Select the first-shorter phonetization of an entry.

        """
        tab = pron.split("|")
        i = 0
        m = len(tab[0])

        for n,p in enumerate(tab):
            if len(p) < m:
                i = n
                m = len(p)
        return tab[i].strip()

    # ------------------------------------------------------------------------
