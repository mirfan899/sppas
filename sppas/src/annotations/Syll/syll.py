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
# File: syll.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os
import logging

from annotations.Syll.syllabification import Syllabification
import annotationdata.io

# ----------------------------------------------------------------------------

class sppasSyll:
    """
    SPPAS automatic syllabification annotation.

    For details, see:
    B. Bigi, C. Meunier, I. Nesterenko, R. Bertrand (2010).
    Automatic detection of syllable boundaries in spontaneous speech
    Language Resource and Evaluation Conference,
    pp 3285-3292, La Valetta, Malte.

    The syllabification of phonemes is performed with a rule-based system from
    aligned phonemes. This RBS phoneme-to-syllable segmentation system is based
    on 2 main principles:

        - a syllable contains a vowel, and only one;
        - a pause is a syllable boundary.

    These two principles focus the problem of the task of finding a syllabic
    boundary between two vowels. As in state-of-the-art systems, phonemes were
    grouped into classes and rules established to deal with these classes.

    The rules we propose follow usual phonological statements for most of the
    corpus. A configuration file indicates phonemes, classes and rules.
    This file can be edited and modified to adapt the syllabification.

    The syllable configuration file is a simple ASCII text file that the user
    can change as needed.

    How to use sppasSyll?

    >>> s = sppasSyll( configfilename )
    >>> s.run(inputfilename, outputfilename)

    """

    def __init__(self, config, logfile=None):
        """
        Create a new sppasSyll instance.

        @param config is the configuration (rules) file name,
        @param logfile is a file descriptor of the log file.

        """
        self._merge         = False
        self._usesintervals = False
        self._usesphons     = True
        self._tiername = "TokensAlign"

        try:
            self.syllabifier = Syllabification(config, logfile)
        except Exception as e:
            raise e

    # End __init__
    # ------------------------------------------------------------------------


    def fix_options(self, options):
        """
        Fix all options.

        @param options (dict) Dictionary with key=optionname (string).

        """
        for opt in options:
            if "merge" == opt.get_key():
                self.set_merge( opt.get_value() )
            elif "usesintervals" == opt.get_key():
                self.set_usesintervals( opt.get_value() )
            elif "usesphons" == opt.get_key():
                self.set_usesphons( opt.get_value() )
            elif "tiername" == opt.get_key():
                self.set_tiername(opt.get_value())

    # End fix_options
    # ------------------------------------------------------------------------


    def set_merge(self,merge):
        """
        Fix the merge option.
        If merge is set to True, sppasSyll() will save the input tiers in the output file.

        @param merge is a Boolean

        """
        self._merge = merge

    # End set_merge
    # ----------------------------------------------------------------------


    def set_usesintervals(self, mode):
        """
        Fix the usesintervals option.
        If usesintervals is set to True, the syllabification operates inside
        specific (given) intervals.

        @param mode is a Boolean

        """
        self._usesintervals = mode

    # End set_usesintervals
    # ----------------------------------------------------------------------


    def set_usesphons(self, mode):
        """
        Fix the usesphons option.
        If usesphons is set to True, the syllabification operates by using
        only tier with phonemes.

        @param mode is a Boolean

        """
        self._usesphons = mode

    # End set_usesphons
    # ----------------------------------------------------------------------


    def set_tiername(self, tiername):
        """
        Fix the tiername option.

        @param tiername is a string

        """
        self._tiername = tiername

    # End set_interval_file
    # ----------------------------------------------------------------------


    def save(self, trsinput, inputfilename, syllables, outputfilename):
        """
        Save the syllabification into a file (end of the input or output).
        """

        # An output file name is given
        if outputfilename is not None:
            if self._merge is True:
                for tier in trsinput:
                    syllables.Add(tier)
            trsoutput = syllables
        # the syllable' tiers are added to the input transcription
        else:
            for tier in syllables:
                trsinput.Add(tier)
            trsoutput  = trsinput
            outputfilename = inputfilename

        # Save
        try:
            annotationdata.io.write( outputfilename, trsoutput )
        except Exception as e:
            raise IOError('Syll::syll.py. An error occurred when writing output.\n %s' % e)

    # End save
    # ------------------------------------------------------------------------


    def run(self, inputfilename, outputfilename=None):
        """
        Perform the Syllabification process.

        @param inputfilename (string) annotated file including time-aligned phonemes
        @param outputfilename

        """
        phonemes = None
        trsinput = annotationdata.io.read(inputfilename)

        #find the phoneme tier
        for tier in trsinput:
            if "align" in tier.GetName().lower() and "phon" in tier.GetName().lower():
                phonemes = tier
                break

        if phonemes is None:
            raise IOError("Phoneme tier not found."
                          " The name of a tier must contain both 'align' and 'phon'.")
        if phonemes.IsEmpty() is True:
            raise IOError("Syll::sppasSyll. Empty phoneme tier.\n")

        if self._usesintervals is True:
            intervals = trsinput.Find(self._tiername)
            if not intervals:
                raise IndexError("Interval tier not found: %s" % self._tiername)

        if self._usesintervals and self._usesphons:
            syllables     = self.syllabifier.syllabify(phonemes)
            syllables_seg = self.syllabifier.syllabify2(phonemes, intervals)
            for tier in syllables_seg:
                syllables.Add(tier)
            syll       = syllables.Find("Syllables")
            cls        = syllables.Find("Classes")
            struct     = syllables.Find("Structures")
            syll_seg   = syllables.Find("Syllables-seg")
            cls_seg    = syllables.Find("Classes-seg")
            struct_seg = syllables.Find("Structures-seg")
            #syllables._hierarchy.addLink("TimeAlignment", phonemes, syll) # phonemes are not in this transcription
            syllables._hierarchy.addLink("TimeAssociation", syll, cls)
            syllables._hierarchy.addLink('TimeAssociation', syll, struct)
            #try:
            #    syllables._hierarchy.addLink("TimeAlignment", phonemes, syll_seg) # phonemes are not in this transcription
            #except Exception:
                # it happens when radius was not fixed properly in phonemes
            #    pass
            #try:
            #    syllables._hierarchy.addLink("TimeAlignment", syll_seg, self._tiername) # self._tiername is not in this transcription
            #except Exception:
                # it happens when radius was not fixed properly in self._tiername
            #    pass
            syllables._hierarchy.addLink('TimeAssociation', syll_seg, cls_seg)
            syllables._hierarchy.addLink('TimeAssociation', syll_seg, struct_seg)

        elif self._usesintervals:
            syllables  = self.syllabifier.syllabify2(phonemes, intervals)
            syll_seg   = syllables.Find("Syllables-seg")
            cls_seg    = syllables.Find("Classes-seg")
            struct_seg = syllables.Find("Structures-seg")
            #try:
            #    syllables._hierarchy.addLink("TimeAlignment", phonemes, syll_seg)
            #except Exception:
            #    pass
            #try:
            #    syllables._hierarchy.addLink("TimeAlignment", syll_seg, self._tiername)
            #except Exception:
            #    pass
            syllables._hierarchy.addLink('TimeAssociation', syll_seg, cls_seg)
            syllables._hierarchy.addLink('TimeAssociation', syll_seg, struct_seg)

        else:
            syllables = self.syllabifier.syllabify(phonemes)
            syll      = syllables.Find("Syllables")
            cls       = syllables.Find("Classes")
            struct    = syllables.Find("Structures")
            #syllables._hierarchy.addLink("TimeAlignment", phonemes, syll)
            syllables._hierarchy.addLink('TimeAssociation', syll, cls)
            syllables._hierarchy.addLink('TimeAssociation', syll, struct)


        # Manage results
        self.save(trsinput, inputfilename, syllables, outputfilename)

    # End run
    # ------------------------------------------------------------------------
