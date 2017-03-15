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
# File: sppasyll.py
# ----------------------------------------------------------------------------

from sppas.src.annotations.Syll.syllabification import Syllabification
import sppas.src.annotationdata.aio
from sppas.src.annotationdata.transcription import Transcription
from .. import WARNING_ID
from ..baseannot import sppasBaseAnnotation

# ----------------------------------------------------------------------------


class sppasSyll( sppasBaseAnnotation ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS automatic syllabification annotation.

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
        @param logfile (sppasLog)

        """
        sppasBaseAnnotation.__init__(self, logfile)

        self.syllabifier = Syllabification(config, logfile)

        # List of options to configure this automatic annotation
        self._options = {}
        self._options['usesintervals'] = False #
        self._options['usesphons']     = True #
        self._options['tiername']      = "TokensAlign" #

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        Available options are:
            - usesintervals
            - usesphons
            - tiername

        @param options (option)

        """
        for opt in options:

            key = opt.get_key()

            if "usesintervals" == key:
                self.set_usesintervals( opt.get_value() )

            elif "usesphons" == key:
                self.set_usesphons( opt.get_value() )

            elif "tiername" == key:
                self.set_tiername( opt.get_value() )

            else:
                raise Exception('Unknown key option: %s'%key)

    # ------------------------------------------------------------------------

    def set_usesintervals(self, mode):
        """
        Fix the usesintervals option.
        If usesintervals is set to True, the syllabification operates inside
        specific (given) intervals.

        @param mode is a Boolean

        """
        self._options['usesintervals'] = mode

    # ----------------------------------------------------------------------

    def set_usesphons(self, mode):
        """
        Fix the usesphons option.
        If usesphons is set to True, the syllabification operates by using
        only tier with phonemes.

        @param mode is a Boolean

        """
        self._options['usesphons'] = mode

    # ----------------------------------------------------------------------

    def set_tiername(self, tiername):
        """
        Fix the tiername option.

        @param tiername is a string

        """
        self._options['tiername'] = tiername

    # ------------------------------------------------------------------------

    def get_input_tier(self, trsinput):
        """
        Return the tier with time-aligned phonemes or None.

        """
        for tier in trsinput:
            if "align" in tier.GetName().lower() and "phon" in tier.GetName().lower():
                return tier

        for tier in trsinput:
            if "phon" in tier.GetName().lower():
                return tier

        return None

    # ------------------------------------------------------------------------

    def convert(self, phonemes, intervals=None):
        """
        Syllabify labels of a time-aligned phones tier.

        @param phonemes (Tier) time-aligned phones tier
        @return Transcription

        """
        syllables = Transcription("sppasSyll")
        if self._options['usesphons'] is True:
            syllables = self.syllabifier.syllabify(phonemes)

        if intervals is not None:
            syllables_seg = self.syllabifier.syllabify2(phonemes, intervals)
            for tier in syllables_seg:
                syllables.Add(tier)

        return syllables

    # ------------------------------------------------------------------------

    def run(self, inputfilename, outputfilename=None):
        """
        Perform the Syllabification process.

        @param inputfilename (string) annotated file including time-aligned phonemes
        @param outputfilename

        """
        self.print_options()
        self.print_diagnosis(inputfilename)

        # Get the tier to syllabify
        trsinput = sppas.src.annotationdata.aio.read(inputfilename)
        phonemes = self.get_input_tier(trsinput)
        if phonemes is None:
            raise Exception("No tier found with time-aligned phonemes. "
                            "One of the tier names must contain both 'phon' and align.")

        intervals = None
        if self._options['usesintervals'] is True:
            intervals = trsinput.Find(self._options['tiername'])
            if intervals is None and self.logfile:
                self.logfile.print_message("The use of %s is disabled. Tier not found."%(self._options['tiername']), indent=2, status=WARNING_ID)

        syllables = self.convert( phonemes, intervals )

        # Save in a file
        sppas.src.annotationdata.aio.write( outputfilename,syllables )

    # ------------------------------------------------------------------------
