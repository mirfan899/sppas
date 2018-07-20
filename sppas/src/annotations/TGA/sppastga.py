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

    src.annotations.TGA.sppastga.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Integration of TGA into SPPAS.

"""
from sppas import PHONE_SYMBOLS

from sppas.src.utils.makeunicode import sppasUnicode
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel

from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyOutputError

from .timegroupanalysis import TimeGroupAnalysis

# ----------------------------------------------------------------------------


class sppasTGA(sppasBaseAnnotation):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Estimates TGA on a tier.

    Create time groups then map them into a dictionary where:

        - key is a label assigned to the time group;
        - value is the list of observed durations of segments in this time group.

    """
    def __init__(self, logfile=None):
        """ Create a new sppasTGA instance.

        :param logfile: (sppasLog)

        """
        sppasBaseAnnotation.__init__(self, logfile, "Syllabification")

        # List of the symbols used to create the time groups
        self._tg_separators = list(PHONE_SYMBOLS.keys())

        # List of options to configure this automatic annotation
        self._options = dict()
        self._options['with_radius'] = 0
        self._options['original'] = False
        self._options['annotationpro'] = True
        self._options['tg_prefix_label'] = "tg_"

        # for backward compatibility, we can't simply use PHONE_SYMBOLS...
        self._tg_separators.append('#')
        self._tg_separators.append('@@')
        self._tg_separators.append('+')
        self._tg_separators.append('gb')
        self._tg_separators.append('lg')
        self._tg_separators.append('_')

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options. Available options are:

            - with_radius

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "with_radius" == key:
                self.set_with_radius(opt.get_value())

            elif "original" == key:
                self.set_intercept_slope_original(opt.get_value())

            elif "annotationpro" == key:
                self.set_intercept_slope_annotationpro(opt.get_value())

            elif "tg_prefix_label" == key:
                self.set_tg_prefix_label(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # ------------------------------------------------------------------

    def set_tg_prefix_label(self, prefix):
        """ Fix the prefix to add to each TG.

        :param prefix: (str) Default is 'tg_'

        """
        sp = sppasUnicode(prefix)
        tg = sp.to_strip()
        if len(tg) > 0:
            self._options['tg_prefix_label'] = tg

    # ------------------------------------------------------------------

    def set_with_radius(self, with_radius):
        """ Set the with_radius option, used to estimate the duration.

        :param with_radius: (int)
            - 0 means to use Midpoint;
            - negative value means to use R-;
            - positive radius means to use R+.

        """
        try:
            w = int(with_radius)
            self._options['with_radius'] = w
        except ValueError:
            raise

    # ------------------------------------------------------------------

    def set_intercept_slope_original(self, value):
        """ Estimate intercepts and slopes with the original method.
        Default is False.

        :param value: (boolean)

        """
        self._options['original'] = value

    # ------------------------------------------------------------------

    def set_intercept_slope_annotationpro(self, value):
        """ Estimate intercepts and slopes with the method of annotationpro.
        Default is True.

        :param value: (boolean)

        """
        self._options['annotationpro'] = value

    # ------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------

    def syllables_to_timegroups(self, syllables):
        """ Create the time group intervals.

        :param syllables: (sppasTier)
        :returns: (sppasTier) Time groups

        """
        intervals = syllables.export_to_intervals(self._tg_separators)
        intervals.set_name("TGA-TimeGroups")

        for i, tg in enumerate(intervals):
            tag_str = self._options['tg_prefix_label']
            tag_str += str(i+1)
            tg.append_label(sppasLabel(sppasTag(tag_str)))

        return intervals

    # ----------------------------------------------------------------------

    def syllables_to_timesegments(self, syllables):
        """ Create the time segments intervals.

        Time segments are time groups with serialized syllables.

        :param syllables:
        :returns: (sppasTier) Time segments

        """
        intervals = syllables.export_to_intervals(self._tg_separators)
        intervals.set_name("TGA-TimeSegments")

        for i, tg in enumerate(intervals):
            syll_anns = syllables.find(tg.get_lowest_localization(), tg.get_highest_localization())
            tag_str = ""
            for ann in syll_anns:
                tag_str += ann.serialize_labels(separator=" ")
                tag_str += " "
            tg.append_label(sppasLabel(sppasTag(tag_str)))

        return intervals

    # ----------------------------------------------------------------------

    def timegroups_to_durations(self, syllables, timegroups):
        """ Return a dict with timegroups and the syllable durations.

        :param syllables: (sppasTier) Syllables
        :param timegroups: (sppasTier) Time groups
        :returns: (dict)

        """
        tg_dur = dict()
        for tg_ann in timegroups:
            tg_label = tg_ann.serialize_labels()
            tg_dur[tg_label] = list()
            syll_anns = syllables.find(tg_ann.get_lowest_localization(),
                                       tg_ann.get_highest_localization())
            for syll_ann in syll_anns:
                loc = syll_ann.get_location().get_best()

                # Fix the duration value of this syllable
                dur = loc.duration()
                value = dur.get_value()
                if self._options['with_radius'] < 0:
                    value -= dur.get_margin()
                if self._options['with_radius'] > 0:
                    value += dur.get_margin()

                # Append in the list of values of this TG
                tg_dur[tg_label].append(value)

        return tg_dur

    # ----------------------------------------------------------------------

    def tga_to_tier(self, tga_result, timegroups, tier_name, tag_type="float"):
        """ Create a tier from one of the TGA result.

        :param tga_result: One of the results of TGA
        :param timegroups: (sppasTier) Time groups
        :param tier_name: (str) Name of the output tier
        :param tag_type: (str) Type of the sppasTag to be included

        :returns: (sppasTier)

        """
        tier = sppasTier(tier_name)

        for tg_ann in timegroups:
            tg_label = tg_ann.serialize_labels()
            tag_value = tga_result[tg_label]
            if tag_type == "float":
                tag_value = round(tag_value, 5)

            tier.create_annotation(
                tg_ann.get_location().copy(),
                sppasLabel(sppasTag(tag_value, tag_type)))

        return tier

    # ----------------------------------------------------------------------

    def tga_to_tier_reglin(self, tga_result, timegroups, intercept=True):
        """ Create tiers of intercept,slope from one of the TGA result.

        :param tga_result: One of the results of TGA
        :param timegroups: (sppasTier) Time groups
        :param intercept: (boolean) Export the intercept. If False, export Slope.

        :returns: (sppasTier)

        """
        if intercept is True:
            tier = sppasTier('TGA-Intercept')
        else:
            tier = sppasTier('TGA-Slope')

        for tg_ann in timegroups:
            tg_label = tg_ann.serialize_labels()
            loc = tg_ann.get_location().copy()
            if intercept is True:
                tag_value = tga_result[tg_label][0]
            else:
                tag_value = tga_result[tg_label][1]

            tag_value = round(tag_value, 5)
            tier.create_annotation(loc, sppasLabel(sppasTag(tag_value, "float")))

        return tier

    # ----------------------------------------------------------------------

    def convert(self, syllables):
        """ Estimates TGA on the given syllables.

        :param syllables: (sppasTier)
        :returns: (sppasTranscription)

        """
        trs_out = sppasTranscription("TimeGroupAnalyser")

        # Create the time groups: intervals of consecutive syllables
        timegroups = self.syllables_to_timegroups(syllables)
        timegroups.set_meta('timegroups_of_tier', syllables.get_name())
        trs_out.append(timegroups)

        # Create the time segments
        timesegs = self.syllables_to_timesegments(syllables)
        trs_out.append(timesegs)
        trs_out.add_hierarchy_link("TimeAssociation", timegroups, timesegs)

        # Get the duration of each syllable, grouped into the timegroups
        tg_dur = self.timegroups_to_durations(syllables, timegroups)
        # here, we could add an option to add durations and
        # delta durations into the transcription output

        # Estimate TGA
        ts = TimeGroupAnalysis(tg_dur)

        # Put TGA non-optional results into tiers
        tier = self.tga_to_tier(ts.len(), timegroups, "TGA-Occurrences", "int")
        trs_out.append(tier)
        trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        tier = self.tga_to_tier(ts.total(), timegroups, "TGA-Total", "int")
        trs_out.append(tier)
        trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        tier = self.tga_to_tier(ts.mean(), timegroups, "TGA-Mean")
        trs_out.append(tier)
        trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        tier = self.tga_to_tier(ts.median(), timegroups, "TGA-Median")
        trs_out.append(tier)
        trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        tier = self.tga_to_tier(ts.stdev(), timegroups, "TGA-StdDev")
        trs_out.append(tier)
        trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        tier = self.tga_to_tier(ts.nPVI(), timegroups, "TGA-nPVI")
        trs_out.append(tier)
        trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        # Put TGA Intercept/Slope results
        if self._options['original'] is True:
            tier = self.tga_to_tier_reglin(ts.intercept_slope_original(), timegroups, True)
            tier.set_name('TGA-Intercept_original')
            trs_out.append(tier)
            trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

            tier = self.tga_to_tier_reglin(ts.intercept_slope_original(), timegroups, False)
            tier.set_name('TGA-slope_original')
            trs_out.append(tier)
            trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        if self._options['annotationpro'] is True:
            tier = self.tga_to_tier_reglin(ts.intercept_slope(), timegroups, True)
            tier.set_name('TGA-Intercept_timestamps')
            trs_out.append(tier)
            trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

            tier = self.tga_to_tier_reglin(ts.intercept_slope(), timegroups, False)
            tier.set_name('TGA-slope_timestamps')
            trs_out.append(tier)
            trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        return trs_out

    # ----------------------------------------------------------------------

    def run(self, input_filename, output_filename=None):
        """ Perform the TGA estimation process.

        :param input_filename: (str) Name of the input file with the aligned syllables
        :param output_filename: (str) Name of the resulting file with TGA

        """
        self.print_filename(input_filename)
        self.print_options()
        self.print_diagnosis(input_filename)

        # Get the tier to syllabify
        parser = sppasRW(input_filename)
        trs_input = parser.read()
        tier_input = sppasFindTier.aligned_syllables(trs_input)

        # Create the transcription result
        trs_output = sppasTranscription("Time Group Analyzer")
        trs_output.set_meta('tga_result_of', input_filename)

        # Estimate TGA on the tier
        trs_output = self.convert(tier_input)

        # Save in a file
        if output_filename is not None:
            if len(trs_output) > 0:
                parser = sppasRW(output_filename)
                parser.write(trs_output)
                self.print_filename(output_filename, status=0)
            else:
                raise EmptyOutputError

        return trs_output

