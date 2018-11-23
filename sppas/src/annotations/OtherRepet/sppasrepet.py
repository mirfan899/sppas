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

    src.annotations.OtherRepet.sppasrepet.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sppas import IndexRangeException
from sppas import symbols
from sppas import sppasRW
from sppas import sppasTranscription
from sppas import sppasTier
from sppas import sppasInterval
from sppas import sppasLocation
from sppas import sppasLabel
from sppas import sppasTag
from sppas import sppasVocabulary
from sppas import sppasUnigram

from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyOutputError

from ..SelfRepet.datastructs import DataSpeaker

from .detectrepet import OtherRepetition

# ---------------------------------------------------------------------------

SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]

# ---------------------------------------------------------------------------


class sppasOtherRepet(sppasBaseAnnotation):
    """SPPAS Automatic Other-Repetition Detection.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Detect automatically other-repetitions. Result must be re-filtered by an
    expert. This annotation is performed on the basis of time-aligned tokens
    or lemmas. The output is made of 2 tiers with sources and echos.

    """

    MAX_SPAN = 12
    MAX_ALPHA = 4.

    # -----------------------------------------------------------------------

    def __init__(self, resource_file=None, logfile=None):
        """Create a new sppasOtherRepet instance.

        :param resource_file: (str) File with the list of stop-words.

        """
        super(sppasOtherRepet, self).__init__(logfile, "OtherRepetitions")

        # List of options to configure this automatic annotation
        self._options = dict()
        self._options['lemmas'] = False    # is better but not produced by SPPAS
        self._options['span'] = 5          # never tested if it's appropriate
        self._options['stopwords'] = True  #
        self._options['alpha'] = 0.5       #

        self.__stop_words = sppasVocabulary()
        if resource_file is not None:
            self.load_stop_words(resource_file)

    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        :param options: list of sppasOption instances

        """
        for opt in options:

            key = opt.get_key()

            if "stopwords" == key:
                self.set_use_stopwords(opt.get_value())

            elif "lemmas" == key:
                self.set_use_lemmatize(opt.get_value())

            elif "span" == key:
                self.set_span(opt.get_value())

            elif "alpha" == key:
                self.set_alpha(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def load_stop_words(self, filename):
        """Load or re-load a list of stop-words from a file.

        Erase the existing list...

        :param filename: (str) File with 1 column.

        """
        self.__stop_words = sppasVocabulary()

        try:
            self.__stop_words.load_from_ascii(filename)
            self.print_message("The initial list contains {:d} stop-words"
                               "".format(len(self.__stop_words)),
                               indent=2, status=3)
        except Exception as e:
            self.__stop_words = sppasVocabulary()
            self.print_message("No stop-words loaded: {:s}"
                               "".format(str(e)), indent=2, status=1)

    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------

    def set_use_lemmatize(self, use_lemmatize):
        """Fix the use_lemmatize option.

        If use_lemmatize is set to True, sppasRepetition() will use a tier
        with lemmas. Instead, it uses a tier with tokens.

        :param use_lemmatize: (bool)

        """
        self._options['lemmas'] = bool(use_lemmatize)

    # -----------------------------------------------------------------------

    def set_use_stopwords(self, use_stopwords):
        """Fix the use_stopwords option.

        If use_stopwords is set to True, sppasOtherRepet() will add specific
        stopwords to the stopwords list (deducted from the input text).

        :param use_stopwords: (bool)

        """
        self._options['stopwords'] = bool(use_stopwords)

    # -----------------------------------------------------------------------

    def set_span(self, span):
        """Fix the span option.

        Span is the maximum number of IPUs to search for repetitions.
        A value of 1 means to search only in the current IPU.

        :param span: (int)

        """
        span = int(span)
        if 0 < span <= sppasOtherRepet.MAX_SPAN:
            self._options['span'] = span
        else:
            raise IndexRangeException(span, 0, sppasOtherRepet.MAX_SPAN)

    # -----------------------------------------------------------------------

    def set_alpha(self, alpha):
        """Fix the alpha option.

        Alpha is a coefficient to add specific stop-words in the list.

        :param alpha: (float)

        """
        alpha = float(alpha)
        if 0. < alpha < sppasOtherRepet.MAX_ALPHA:
            self._options['alpha'] = alpha
        else:
            raise IndexRangeException(alpha, 0, sppasOtherRepet.MAX_ALPHA)

    # -----------------------------------------------------------------------

    def fix_stop_list(self, tier=None):
        """Return the expected list of stop-words.

        It is either:

            - the current stop-list or,
            - this list + un-relevant tokens, estimated on the given tier.

        A token 'w' is relevant for the speaker if its probability is
        less than a threshold:

            | P(w) <= 1 / (alpha * V)

        where 'alpha' is an empirical coefficient and 'V' is the vocabulary
        size of the speaker.

        :param tier: (sppasTier) A tier with entries to be analyzed.
        :returns: (sppasVocabulary) List of stop-words

        """
        if self._options['stopwords'] is False:
            return sppasVocabulary()

        if tier is None or len(tier) < 5:
            return self.__stop_words.copy()

        # Create the sppasUnigram and put data
        u = sppasUnigram()
        for a in tier:
            content = a.serialize_labels()
            if content not in symbols.all:
                u.add(content)

        # Estimate values for relevance
        _v = float(len(u))
        threshold = 1. / (self._options["alpha"] * _v)

        # Estimate if a token is relevant; if not: put it in the stop-list
        stop_list = self.__stop_words.copy()
        for token in u.get_tokens():
            p_w = float(u.get_count(token)) / float(u.get_sum())
            if p_w > threshold:
                stop_list.add(token)
                self.print_message('Add in the stop-list: {:s}'
                                   ''.format(token), indent=3)

        return stop_list

    # -----------------------------------------------------------------------
    # Automatic Detection search
    # -----------------------------------------------------------------------

    def other_detection(self, inputtier1, inputtier2):
        """Other-Repetition detection.

        :param inputtier1: (Tier)
        :param inputtier2: (Tier)

        """
        inputtier1.set_radius(0.04)
        inputtier2.set_radius(0.04)
        # Use the appropriate stop-list: add un-relevant tokens of the echoing speaker
        stop_words = self.fix_stop_list(inputtier2)
        # Create repeat objects
        repetition = OtherRepetition(stop_words)
        # Create output data
        src_tier = sppasTier("OR-Source")
        echo_tier = sppasTier("OR-Echo")

        # Initialization of tok_start, and tok_end
        tok_start_src = 0
        tok_end_src = min(20, len(inputtier1)-1)  # 20 is the max nb of tokens in a src
        tok_start_echo = 0

        tokens2 = list()
        speaker2 = DataSpeaker(tokens2)
        # Detection is here:
        # detect() is applied work by word, from tok_start to tok_end
        while tok_start_src < tok_end_src:

            # Build an array with the tokens
            print(tok_start_src)
            print(tok_end_src)
            tokens1 = [inputtier1[i].serialize_labels()
                       for i in range(tok_start_src, tok_end_src+1)]
            speaker1 = DataSpeaker(tokens1)

            # Create speaker2
            # re-create only if different of the previous step...
            src_begin = inputtier1[tok_start_src].get_lowest_localization().get_midpoint()
            echo_begin = inputtier2[tok_start_echo].get_lowest_localization().get_midpoint()
            if len(tokens2) == 0 or echo_begin < src_begin:
                tokens2 = list()
                nb_breaks = 0
                old_tok_start_echo = tok_start_echo

                for i in range(old_tok_start_echo, len(inputtier2)):
                    ann = inputtier2[i]
                    label = ann.serialize_labels()
                    if ann.get_lowest_localization().get_midpoint() >= src_begin:
                        if tok_start_echo == old_tok_start_echo:
                            tok_start_echo = i
                        if label == SIL_ORTHO:
                            nb_breaks += 1
                        if nb_breaks == self._options['span']:
                            break
                        tokens2.append(label)
                speaker2 = DataSpeaker(tokens2)

            # We can't go too further due to the required time-alignment of
            # tokens between src/echo
            # Check only if the first token is the first token of a source!!
            repetition.detect(speaker1, speaker2, 1)

            # Save repeats
            shift = 1
            if repetition.get_source() is not None:
                s, e = repetition.get_source()
                saved = sppasOtherRepet.__add_repetition(
                    repetition, inputtier1, inputtier2, tok_start_src,
                    tok_start_echo, src_tier, echo_tier)
                if saved is True:
                    shift = e + 1

            tok_start_src = min(tok_start_src + shift, len(inputtier1)-1)
            tok_end_src = min(tok_start_src + 20, len(inputtier1)-1)

        return src_tier, echo_tier

    # -----------------------------------------------------------------------
    # Run
    # -----------------------------------------------------------------------

    def run(self, input_filename1, input_filename2, output_filename=None):
        """Run the Repetition Automatic Detection annotation.

        :param input_filename1: (str) File with time-aligned tokens or lemmas
        :param input_filename2: (str) File with time-aligned tokens or lemmas
        :param output_filename:(str) Name of the file to save the result

        """
        self.print_filename(input_filename1)
        self.print_filename(input_filename2)
        self.print_options()
        self.print_diagnosis(input_filename1)
        self.print_diagnosis(input_filename2)

        # Get the tier to be used
        parser = sppasRW(input_filename1)
        trs_input1 = parser.read()

        if self._options['lemmas'] is True:
            tier_input1 = sppasFindTier.aligned_lemmas(trs_input1)
        else:
            tier_input1 = sppasFindTier.aligned_tokens(trs_input1)

        # Get the tier to be used
        parser = sppasRW(input_filename2)
        trs_input2 = parser.read()

        if self._options['lemmas'] is True:
            tier_input2 = sppasFindTier.aligned_lemmas(trs_input2)
        else:
            tier_input2 = sppasFindTier.aligned_tokens(trs_input2)

        # Repetition Automatic Detection
        (src_tier, echo_tier) = self.other_detection(tier_input1, tier_input2)

        # Create the transcription result
        trs_output = sppasTranscription("OtherRepetition")
        trs_output.set_meta('other_repetition_result_of_src', input_filename1)
        trs_output.set_meta('other_repetition_result_of_echo', input_filename2)
        trs_output.append(src_tier)
        trs_output.append(echo_tier)

        # Save in a file
        if output_filename is not None:
            if len(trs_output) > 0:
                parser = sppasRW(output_filename)
                parser.write(trs_output)
                self.print_filename(output_filename, status=0)
            else:
                raise EmptyOutputError

        return trs_output

    # -----------------------------------------------------------------------

    @staticmethod
    def __add_repetition(repetition, spk1_tier, spk2_tier, start_idx1, start_idx2, src_tier, echo_tier):
        """Add a repetition - source and echos - in tiers.

        :param repetition: (DataRepetition)
        :param spk1_tier: (Tier) The tier of speaker 1 (to detect sources)
        :param spk2_tier: (Tier) The tier of speaker 2 (to detect echos)
        :param start_idx1: start index of the interval in spk1_tier
        :param start_idx2: start index of the interval in spk2_tier
        :param src_tier: (Tier) The resulting tier with sources
        :param echo_tier: (Tier) The resulting tier with echos
        :returns: (bool) the repetition was added or not


        """
        index = len(src_tier)

        # Source
        s, e = repetition.get_source()
        src_begin = spk1_tier[start_idx1 + s].get_lowest_localization()
        src_end = spk1_tier[start_idx1 + e].get_highest_localization()
        time = sppasInterval(src_begin.copy(), src_end.copy())
        try:
            a = src_tier.create_annotation(
                    sppasLocation(time),
                    sppasLabel(sppasTag("S" + str(index + 1))))
            src_id = a.get_meta('id')
        except:
            return False

        # Echos
        for (s, e) in repetition.get_echos():
            rep_begin = spk2_tier[start_idx2 + s].get_lowest_localization()
            rep_end = spk2_tier[start_idx2 + e].get_highest_localization()
            time = sppasInterval(rep_begin.copy(), rep_end.copy())
            a = echo_tier.create_annotation(
                sppasLocation(time),
                sppasLabel(sppasTag("R" + str(index + 1))))
            a.set_meta('is_other_repetition_of', src_id)

        return True
