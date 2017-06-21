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

    src.annotations.sppasphon.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    SPPAS integration of Phonetization.
    For details, read the following reference:

        | Brigitte Bigi (2016).
        | A phonetization approach for the forced-alignment task in SPPAS.
        | Human Language Technology. Challenges for Computer Science and 
        | Linguistics, LNAI 9561, Springer, pp. 515–526.

"""
from sppas import unk_stamp

import sppas.src.annotationdata.aio
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.resources.dictpron import sppasDictPron
from sppas.src.resources.mapping import sppasMapping

from .. import ERROR_ID, WARNING_ID
from .. import t
from ..annotationsexc import AnnotationOptionError
from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasSearchTier

from .phonetize import sppasDictPhonetizer

# ---------------------------------------------------------------------------

MISSING = ":INFO 1110: "
PHONETIZED = ":INFO 1112: "
NOT_PHONETIZED = ":INFO 1114: "

# ---------------------------------------------------------------------------


class sppasPhon(sppasBaseAnnotation):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS integration of the Phonetization automatic annotation.

    """
    def __init__(self, dict_filename, map_filename=None, logfile=None):
        """ Create a sppasPhon instance.

        :param dict_filename: (str) is the pronunciation dictionary file name
        (HTK-ASCII format, utf8).
        :param map_filename: (str) is the filename of a mapping table. It is used
        to generate new pronunciations by mapping phonemes of the dictionary.
        :param logfile (sppasLog) is a log file utility class member.
        :raises: ValueError if loading the dictionary fails

        """
        sppasBaseAnnotation.__init__(self, logfile)

        # Pronunciation dictionary
        self.maptable = None
        if map_filename is not None:
            self.maptable = sppasMapping(map_filename)

        self.phonetizer = None
        self.set_dict(dict_filename)

        # List of options to configure this automatic annotation
        self._options = dict()
        self._options['phonunk'] = False       # Phonetize missing tokens
        self._options['usestdtokens'] = False  # Phonetize standard spelling

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options. Available options are:

            - unk
            - usesstdtokens

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()

            if key == "unk":
                self.set_unk(opt.get_value())

            elif key == "usestdtokens":
                self.set_usestdtokens(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_unk(self, unk):
        """ Fix the unk option value.

        :param unk: (bool) If unk is set to True, the system will attempt
        to phonetize unknown entries (i.e. tokens missing in the dictionary).
        Otherwise, the phonetization of an unknown entry unit is set to the
        default stamp.

        """
        self._options['phonunk'] = unk

    # -----------------------------------------------------------------------

    def set_usestdtokens(self, stdtokens):
        """ Fix the stdtokens option.

        :param stdtokens: (bool) If it is set to True, the phonetization
        will use the standard transcription as input, instead of the faked
        transcription. This option does make sense only for an Enriched
        Orthographic Transcription.

        """
        self._options['usestdtokens'] = stdtokens

    # -----------------------------------------------------------------------
    # Methods to phonetize series of data
    # -----------------------------------------------------------------------

    def set_dict(self, dict_filename):
        """ Set the pronunciation dictionary.

        :param dict_filename: (str) The pronunciation dictionary in HTK-ASCII
        format with UTF-8 encoding.

        """
        pdict = sppasDictPron(dict_filename, nodump=False)
        self.phonetizer = sppasDictPhonetizer(pdict, self.maptable)

    # -----------------------------------------------------------------------

    def phonetize(self, entry):
        """ Phonetize a text.
        Because we absolutely need to match with the number of tokens, this
        method will always return a string: either the automatic phonetization
        (from dict or from phonunk) or the unk_stamp.

        :param entry: (str) The string to be phonetized.
        :returns: phonetization of the given entry

        """
        tab = self.phonetizer.get_phon_tokens(entry.split(), phonunk=self._options['phonunk'])
        tabphon = list()
        for tex, p, s in tab:
            message = None
            if s == ERROR_ID:
                message = (t.gettext(MISSING)).format(tex) + t.gettext(NOT_PHONETIZED)
                self.print_message(message, indent=3, status=s)
                return unk_stamp
            else:
                if s == WARNING_ID:
                    message = (t.gettext(MISSING)).format(tex)
                    if len(p) > 0:
                        message = message + (t.gettext(PHONETIZED)).format(p)
                    else:
                        message = message + t.gettext(NOT_PHONETIZED)
                        p = unk_stamp
                tabphon.append(p)

            if message:
                self.print_message(message, indent=3, status=s)

        return " ".join(tabphon)

    # -----------------------------------------------------------------------

    def convert(self, tier):
        """ Phonetize all annotation of a tokenized tier.

        :param tier: (Tier) Tier that contains the orthographic transcription
        previously tokenized.
        :returns: A tier with name "Phonetization"

        """
        new_tier = Tier("Phonetization")
        if tier is None:
            return new_tier

        for a in tier:

            af = a.Copy()
            for text in af.GetLabel().GetLabels():

                if text.IsPause() is True:
                    # In case the pronunciation dictionary were not properly fixed.
                    text.SetValue("sil")

                elif text.IsEmpty() is False and text.IsSilence() is False:
                    phon = self.phonetize(text.GetValue())
                    text.SetValue(phon)

            new_tier.Append(af)

        return new_tier

    # ------------------------------------------------------------------------

    def run(self, input_filename, output_filename):
        """ Run the Phonetization process on an input file.

        :param input_filename (str) Name of the file including a tokenization
        :param output_filename (str) Name of the resulting file with phonetization

        """
        self.print_options()
        self.print_diagnosis(input_filename)

        # Get the tier to be phonetized.
        pattern = "faked"
        if self._options['usestdtokens'] is True:
            pattern = "std"
        trs_input = sppas.src.annotationdata.aio.read(input_filename)
        tier_input = sppasSearchTier.tokenization(trs_input, pattern)

        # Phonetize the tier
        tier_phon = self.convert(tier_input)

        # Save
        trs_output = Transcription("SPPAS Phonetization")
        trs_output.Append(tier_phon)

        # Save in a file
        sppas.src.annotationdata.aio.write(output_filename, trs_output)
