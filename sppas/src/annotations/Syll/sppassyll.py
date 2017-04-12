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

    src.annotations.sppassyll.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    SPPAS integration of Syllabification.
    For details, read the following reference:

        | Brigitte Bigi, Christine Meunier, Irina Nesterenko, Roxane Bertrand (2010).
        | Automatic detection of syllable boundaries in spontaneous speech.
        | In Language Resource and Evaluation Conference, pp. 3285–3292,
        | La Valetta, Malta.

"""
from sppas.src.annotations.Syll.syllabification import Syllabification
import sppas.src.annotationdata.aio
from sppas.src.annotationdata.transcription import Transcription
from .. import WARNING_ID
from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import AnnotationOptionError, NoInputError

# ----------------------------------------------------------------------------


class sppasSyll(sppasBaseAnnotation):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS automatic syllabification annotation.

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

    """
    def __init__(self, config_filename, logfile=None):
        """ Create a new sppasSyll instance.

        :param config_filename: Name of the configuration (rules) file name,
        :param logfile: (sppasLog)

        """
        sppasBaseAnnotation.__init__(self, logfile)

        self.syllabifier = Syllabification(config_filename, logfile)

        # List of options to configure this automatic annotation
        self._options = dict()
        self._options['usesintervals'] = False
        self._options['usesphons'] = True
        self._options['tiername'] = "TokensAlign"

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options. Available options are:

            - usesintervals
            - usesphons
            - tiername

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "usesintervals" == key:
                self.set_usesintervals(opt.get_value())
            elif "usesphons" == key:
                self.set_usesphons(opt.get_value())
            elif "tiername" == key:
                self.set_tiername(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # ------------------------------------------------------------------------

    def set_usesintervals(self, mode):
        """ Fix the usesintervals option.

        :param mode: (bool) If mode is set to True, the syllabification operates
        inside specific (given) intervals.

        """
        self._options['usesintervals'] = mode

    # ----------------------------------------------------------------------

    def set_usesphons(self, mode):
        """ Fix the usesphons option.

        :param mode: (str) If mode is set to True, the syllabification operates
        by using only tier with phonemes.

        """
        self._options['usesphons'] = mode

    # ----------------------------------------------------------------------

    def set_tiername(self, tier_name):
        """ Fix the tiername option.

        :param tier_name: (str)

        """
        self._options['tiername'] = tier_name

    # ------------------------------------------------------------------------

    def get_input_tier(self, trs_input):
        """ Return the tier with time-aligned phonemes or None.

        :param trs_input: (Transcription)

        """
        for tier in trs_input:
            if "align" in tier.GetName().lower() and "phon" in tier.GetName().lower():
                return tier

        for tier in trs_input:
            if "phon" in tier.GetName().lower():
                return tier

        return None

    # ------------------------------------------------------------------------

    def convert(self, phonemes, intervals=None):
        """ Syllabify labels of a time-aligned phones tier.

        :param phonemes: (Tier) time-aligned phones tier
        :param intervals: (Tier)
        :returns: Transcription

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

    def run(self, input_filename, output_filename):
        """ Perform the Syllabification process.

        :param input_filename: (str) Name of the input file with the aligned phonemes
        :param output_filename: (str) Name of the resulting file with syllabification

        """
        self.print_options()
        self.print_diagnosis(input_filename)

        # Get the tier to syllabify
        trs_input = sppas.src.annotationdata.aio.read(input_filename)
        phonemes = self.get_input_tier(trs_input)
        if phonemes is None:
            raise NoInputError

        intervals = None
        if self._options['usesintervals'] is True:
            intervals = trs_input.Find(self._options['tiername'])
            if intervals is None and self.logfile:
                message = "The use of %s is disabled. Tier not found."%(self._options['tiername'])
                self.logfile.print_message(message, indent=2, status=WARNING_ID)

        syllables = self.convert(phonemes, intervals)

        # Save in a file
        sppas.src.annotationdata.aio.write(output_filename, syllables)
