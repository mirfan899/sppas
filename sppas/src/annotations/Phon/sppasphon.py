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

"""
from sppas.src.config import unk_stamp
from sppas.src.config import PHONE_SYMBOLS, ORTHO_SYMBOLS
from sppas.src.config import separators

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from sppas.src.resources.dictpron import sppasDictPron
from sppas.src.resources.mapping import sppasMapping

from .. import ERROR_ID, WARNING_ID
from .. import t
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyInputError
from ..annotationsexc import EmptyOutputError
from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier

from .phonetize import sppasDictPhonetizer

# ---------------------------------------------------------------------------

MSG_MISSING = (t.gettext(":INFO 1110: "))
MSG_PHONETIZED = (t.gettext(":INFO 1112: "))
MSG_NOT_PHONETIZED = (t.gettext(":INFO 1114: "))
MSG_TRACK = (t.gettext(":INFO 1220: "))

SIL = list(PHONE_SYMBOLS.keys())[list(PHONE_SYMBOLS.values()).index("silence")]
SIL_ORTHO = list(ORTHO_SYMBOLS.keys())[list(ORTHO_SYMBOLS.values()).index("silence")]

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
        sppasBaseAnnotation.__init__(self, logfile, "Phonetization")

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

        :param unk: (bool) If unk is set to True, the system attempts
        to phonetize unknown entries (i.e. tokens missing in the dictionary).
        Otherwise, the phonetization of an unknown entry unit is set to the
        default stamp.

        """
        self._options['phonunk'] = unk

    # -----------------------------------------------------------------------

    def set_usestdtokens(self, stdtokens):
        """ Fix the stdtokens option.

        :param stdtokens: (bool) If it is set to True, the phonetization
        uses the standard transcription as input, instead of the faked
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

    def phonetize(self, entry, idx=0):
        """ Phonetize a text.

        Because we absolutely need to match with the number of tokens, this
        method will always return a string: either the automatic phonetization
        (from dict or from phonunk) or the unk_stamp.

        :param entry: (str) The string to be phonetized.
        :param idx: (int) number to communicate in the error/warning message. 0=disabled
        :returns: phonetization of the given entry

        """
        tab = self.phonetizer.get_phon_tokens(entry.split(),
                                              phonunk=self._options['phonunk'])
        tab_phones = list()
        for tex, p, s in tab:
            message = None
            if s == ERROR_ID:
                message = MSG_MISSING.format(tex) + MSG_NOT_PHONETIZED
                self.print_message(message, indent=3, status=s)
                return unk_stamp
            else:
                if s == WARNING_ID:
                    message = MSG_MISSING.format(tex)
                    if len(p) > 0:
                        message = message + MSG_PHONETIZED.format(p)
                    else:
                        message = message + MSG_NOT_PHONETIZED
                        p = unk_stamp
                tab_phones.append(p)

            if message:
                self.print_message(message, indent=3, status=s)

        return tab_phones

    # -----------------------------------------------------------------------

    def convert(self, tier):
        """ Phonetize annotations of a tokenized tier.

        :param tier: (Tier) the orthographic transcription previously tokenized.
        :returns: (Tier) phonetized tier with name "Phones"

        """
        if tier.is_empty() is True:
            raise EmptyInputError(name=tier.get_name())

        phones_tier = sppasTier("Phones")
        for i, ann in enumerate(tier):
            self.print_message(MSG_TRACK.format(number=i+1), indent=2)

            location = ann.get_location().copy()
            labels = list()

            # Normalize all labels of the orthographic transcription
            for label in ann.get_labels():

                phonetizations = list()
                for text, score in label:
                    if text.is_pause() or text.is_silence():
                        # It's in case the pronunciation dictionary
                        # were not properly fixed.
                        phonetizations.append(SIL)

                    elif text.is_empty() is False:
                        phones = self.phonetize(text.get_content(), i)
                        for p in phones:
                            phonetizations.extend(p.split(separators.variants))

                # New in SPPAS 1.9.6.
                #  - The result is a sequence of labels.
                #  - Variants are alternative tags.
                tags = [sppasTag(p) for p in set(phonetizations)]
                labels.append(sppasLabel(tags))

            phones_tier.create_annotation(location, labels)

        return phones_tier

    # ------------------------------------------------------------------------

    def run(self, input_filename, output_filename=None):
        """ Run the Phonetization process on an input file.

        :param input_filename (str) Name of the file including a tokenization
        :param output_filename (str) Name of the resulting file with phonetization
        :returns: (sppasTranscription)

        """
        self.print_filename(input_filename)
        self.print_options()
        self.print_diagnosis(input_filename)

        # Get the tier to be phonetized.
        pattern = ""
        if self._options['usestdtokens'] is True:
            pattern = "std"
        parser = sppasRW(input_filename)
        trs_input = parser.read()
        tier_input = sppasFindTier.tokenization(trs_input, pattern)

        # Phonetize the tier
        tier_phon = self.convert(tier_input)

        # Create the transcription result
        trs_output = sppasTranscription("Phonetization")
        if tier_phon is not None:
            trs_output.append(tier_phon)

        trs_output.set_meta('text_phonetization_result_of', input_filename)
        trs_output.set_meta('text_phonetization_dict', self.phonetizer.get_dict_filename())

        # Save in a file
        if output_filename is not None:
            if len(trs_output) > 0:
                parser = sppasRW(output_filename)
                parser.write(trs_output)
                self.print_filename(output_filename, status=0)
            else:
                raise EmptyOutputError

        return trs_output
