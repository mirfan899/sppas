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

"""
from sppas import PHONE_SYMBOLS
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel

from .. import WARNING_ID
from .. import t
from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyOutputError

from .syllabify import Syllabifier

# ----------------------------------------------------------------------------

MSG_TRACK = t.gettext(":INFO 1220: ")

# ----------------------------------------------------------------------------


class sppasSyll(sppasBaseAnnotation):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS automatic syllabification annotation.

    """
    def __init__(self, config_filename, logfile=None):
        """ Create a new sppasSyll instance.

        :param config_filename: Name of the configuration file with the rules
        :param logfile: (sppasLog)

        """
        sppasBaseAnnotation.__init__(self, logfile, "Syllabification")

        self.syllabifier = Syllabifier(config_filename)

        # List of options to configure this automatic annotation
        self._options = dict()
        self._options['usesintervals'] = False
        self._options['usesphons'] = True
        self._options['tiername'] = "TokensAlign"
        self._options['createclasses'] = True
        self._options['createstructures'] = True

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options. Available options are:

            - usesintervals
            - usesphons
            - tiername
            - createclasses
            - createstructures

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

            elif "createclasses" == key:
                self.set_create_tier_classes(opt.get_value())

            elif "createstructures" == key:
                self.set_create_tier_strctures(opt.get_value())

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

    # ----------------------------------------------------------------------

    def set_create_tier_classes(self, create=True):
        """ Fix the createclasses option.

        :param create: (bool)

        """
        self._options['createclasses'] = create

    # ----------------------------------------------------------------------

    def set_create_tier_strctures(self, create=True):
        """ Fix the createstructures option.

        :param create: (bool)

        """
        self._options['createstructures'] = create

    # ----------------------------------------------------------------------
    # Syllabification of time-aligned phonemes stored into a tier
    # ----------------------------------------------------------------------

    def convert(self, phonemes, intervals=None):
        """ Syllabify labels of a time-aligned phones tier.

        :param phonemes: (sppasTier) time-aligned phonemes tier
        :param intervals: (sppasTier)
        :returns: (sppasTier)

        """
        if intervals is None:
            intervals = sppasSyll._phon_to_intervals(phonemes)

        syllables = sppasTier("Syllables")

        for interval in intervals:

            # get the index of the phonemes containing the begin of the interval
            start_phon_idx = phonemes.lindex(interval.get_lowest_localization())
            if start_phon_idx == -1:
                start_phon_idx = phonemes.mindex(interval.get_lowest_localization(), bound=-1)

            # get the index of the phonemes containing the end of the interval
            end_phon_idx = phonemes.rindex(interval.get_highest_localization())
            if end_phon_idx == -1:
                end_phon_idx = phonemes.mindex(interval.get_highest_localization(),
                                               bound=1)

            # syllabify within the interval
            if start_phon_idx != -1 and end_phon_idx != -1:
                self.syllabify_interval(phonemes,
                                        start_phon_idx,
                                        end_phon_idx,
                                        syllables)
            else:
                self.print_message("Invalid interval")

        return syllables

    # ----------------------------------------------------------------------

    def syllabify_interval(self, phonemes, from_p, to_p, syllables):
        """ Perform the syllabification of one interval.

        :param phonemes: (sppasTier)
        :param from_p: (int) index of the first phoneme to be syllabified
        :param to_p: (int) index of the last phoneme to be syllabified
        :param syllables: (sppasTier)

        """
        # create the sequence of phonemes to syllabify
        p = list()
        for ann in phonemes[from_p:to_p+1]:
            tag = ann.get_best_tag()
            p.append(tag.get_typed_content())

        # create the sequence of syllables
        s = self.syllabifier.annotate(p)

        # add the syllables into the tier
        for i, syll in enumerate(s):
            start_idx, end_idx = syll

            # create the location
            begin = phonemes[start_idx+from_p].get_lowest_localization().copy()
            end = phonemes[end_idx+from_p].get_highest_localization().copy()
            location = sppasLocation(sppasInterval(begin, end))

            # create the label
            syll_string = Syllabifier.phonetize_syllables(p, [syll])
            label = sppasLabel(sppasTag(syll_string))

            # add the syllable
            syllables.create_annotation(location, label)

    # ----------------------------------------------------------------------

    def run(self, input_filename, output_filename=None):
        """ Perform the Syllabification process.

        :param input_filename: (str) Name of the input file with the aligned phonemes
        :param output_filename: (str) Name of the resulting file with syllabification

        """
        self.print_filename(input_filename)
        self.print_options()
        self.print_diagnosis(input_filename)

        # Get the tier to syllabify
        parser = sppasRW(input_filename)
        trs_input = parser.read()
        tier_input = sppasFindTier.aligned_phones(trs_input)

        # Create the transcription result
        trs_output = sppasTranscription("Syllabification")
        trs_output.set_meta('syllabification_result_of', input_filename)

        # Syllabify the tier
        if self._options['usesphons'] is True:
            tier_syll = self.convert(tier_input)
            trs_output.append(tier_syll)
            if self._options['createclasses']:
                pass
            if self._options['createstructures']:
                pass

        # Extra tier: syllabify between given intervals
        if self._options['usesintervals'] is True:
            intervals = trs_input.find(self._options['tiername'])
            if intervals is None:
                message = "The use of {:s} is disabled. " \
                          "Tier not found.".format(self._options['tiername'])
                self.print_message(message, indent=2, status=WARNING_ID)
            else:
                tier_syll_int = self.convert(tier_input, intervals)
                tier_syll_int.set_name("Syllables-Intervals")
                tier_syll_int.set_meta('syll_used_intervals', intervals.get_name())
                trs_output.append(tier_syll_int)
                if self._options['createclasses']:
                    pass
                if self._options['createstructures']:
                    pass

        # Save in a file
        if output_filename is not None:
            if len(trs_output) > 0:
                parser = sppasRW(output_filename)
                parser.write(trs_output)
                self.print_filename(output_filename, status=0)
            else:
                raise EmptyOutputError

        return trs_output

    # ----------------------------------------------------------------------

    @staticmethod
    def _phon_to_intervals(phonemes):
        """ Create the intervals to be syllabified. """

        # for backward compatibility
        stop = list(PHONE_SYMBOLS.keys())
        stop.append('#')
        stop.append('@@')
        stop.append('+')
        stop.append('gb')
        stop.append('lg')

        intervals = sppasTier("intervals")
        begin = phonemes.get_first_point()
        end = begin
        prev_ann = None

        for ann in phonemes:
            tag = None
            if ann.label_is_filled():
                tag = ann.get_best_tag()

            if prev_ann is not None:
                # if no tag or stop tag or hole between prev_ann and ann
                if tag is None or \
                   tag.get_typed_content() in stop or \
                   prev_ann.get_highest_localization() < ann.get_lowest_localization():
                    if end > begin:
                        intervals.create_annotation(sppasLocation(
                              sppasInterval(begin,
                                            prev_ann.get_highest_localization())))

                    if tag is None or tag.get_typed_content() in stop:
                        begin = ann.get_highest_localization()
                    else:
                        begin = ann.get_lowest_localization()
            else:
                # phonemes can start with a non-labelled interval!
                if tag is None or tag.get_typed_content() in stop:
                    begin = ann.get_highest_localization()

            end = ann.get_highest_localization()
            prev_ann = ann

        if end > begin:
            ann = phonemes[-1]
            end = ann.get_highest_localization()
            a = intervals.create_annotation(sppasLocation(sppasInterval(begin, end)))

        return intervals
