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

    src.annotations.SelfRepet.sppasrepet.py
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

from .detectrepet import SelfRepetition
from .datastructs import DataSpeaker

# ---------------------------------------------------------------------------

SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]

# ---------------------------------------------------------------------------


class sppasSelfRepet(sppasBaseAnnotation):
    """SPPAS Automatic Self-Repetition Detection.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Detect self-repetitions. The result has never been validated by an expert.
    This annotation is performed on the basis of time-aligned tokens or lemmas.
    The output is made of 2 tiers with sources and echos.

    """

    MAX_SPAN = 20
    MAX_ALPHA = 4.

    # -----------------------------------------------------------------------

    def __init__(self, resource_file=None, logfile=None):
        """Create a new sppasRepetition instance.

        :param resource_file: (str) File with the list of stop-words.

        """
        super(sppasSelfRepet, self).__init__(logfile, "SelfRepetitions")

        # List of options to configure this automatic annotation
        self._options = dict()
        self._options['lemmas'] = True
        self._options['stopwords'] = True
        self._options['span'] = 5
        self._options['alpha'] = 0.5

        self.__stop_filename = resource_file
        self.__stop_words = sppasVocabulary()
        self.set_use_stopwords(True)

    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        :param options: list of sppasOption instances

        """
        for opt in options:

            key = opt.get_key()

            if "stopwords" == key:
                self.set_use_stopwords(opt.get_value())

            elif "lemmatize" == key:
                self.set_use_lemmatize(opt.get_value())

            elif "empan" == key:
                self.set_span(opt.get_value())

            elif "alpha" == key:
                self.set_alpha(opt.get_value())

            else:
                raise AnnotationOptionError(key)

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

        If use_stopwords is set to True, sppasRepetition() will add specific
        stopwords to the stopwords list (deducted from the input text).

        :param use_stopwords: (bool)

        """
        self._options['stopwords'] = bool(use_stopwords)

        # Load the list of stop words from a file
        if self._options['stopwords'] is True:
            try:
                self.__stop_filename.load_from_ascii(self.__stop_filename)
                self.print_message("The initial list contains {:d} stop-words"
                                   "".format(len(self.__stop_words)),
                                   indent=2, status=3)
            except Exception as e:
                self._options['stopwords'] = False
                self.print_message("No stop-words loaded: {:s}"
                                   "".format(str(e)), indent=2, status=1)

        if self._options['stopwords'] is False:
            self.__stop_words = sppasVocabulary()

    # -----------------------------------------------------------------------

    def set_span(self, span):
        """Fix the span option.

        Span is the maximum number of IPUs to search for repetitions.
        A value of 1 means to search only in the current IPU.

        :param span: (int)

        """
        span = int(span)
        if 0 < span <= sppasSelfRepet.MAX_SPAN:
            self._options['span'] = span
        else:
            raise IndexRangeException(span, 0, sppasSelfRepet.MAX_SPAN)

    # -----------------------------------------------------------------------

    def set_alpha(self, alpha):
        """Fix the alpha option.

        Alpha is a coefficient to add specific stop-words in the list.

        :param alpha: (float)

        """
        alpha = float(alpha)
        if 0. < alpha < sppasSelfRepet.MAX_ALPHA:
            self._options['alpha'] = alpha
        else:
            raise IndexRangeException(alpha, 0, sppasSelfRepet.MAX_ALPHA)

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

    @staticmethod
    def __find_next_break(tier, start, span):
        """Return the index of the next interval representing a break.

        It depends on the 'span' value.

        :param tier: (sppasTier)
        :param start: (int) the position of the token where the search will start
        :param span: (int)
        :returns: (int) index of the next interval corresponding to the span

        """
        nb_breaks = 0
        for i in range(start, len(tier)):
            if tier[i].serialize_labels() == SIL_ORTHO:
                nb_breaks += 1
                if nb_breaks == span:
                    return i
        return len(tier) - 1

    # -----------------------------------------------------------------------

    def __fix_indexes(self, tier, tok_start, shift):
        tok_start += shift
        tok_search = sppasSelfRepet.__find_next_break(
            tier, tok_start + 1, span=1)
        tok_end = sppasSelfRepet.__find_next_break(
            tier, tok_start + 1, span=self._options['span'])

        return tok_start, tok_search, tok_end

    # -----------------------------------------------------------------------

    def self_detection(self, tier):
        """Self-Repetition detection.

        :param tier: (sppasTier)

        """
        # Use the appropriate stop-list
        stop_words = self.fix_stop_list(tier)
        # Create a data structure to detect and store a source/echos
        repetition = SelfRepetition(stop_words)
        # Create output data
        src_tier = sppasTier("SR-Source")
        echo_tier = sppasTier("SR-Echo")

        # Initialization of the indexes to work with tokens
        tok_start, tok_search, tok_end = self.__fix_indexes(tier, 0, 0)

        # Detection is here:
        while tok_start < tok_end:

            # Build an array with the tokens
            tokens = [tier[i].serialize_labels()
                      for i in range(tok_start, tok_end+1)]
            speaker = DataSpeaker(tokens)

            # Detect the first self-repetition in these data
            limit = tok_search - tok_start
            repetition.detect(speaker, limit, None)

            # Save the repetition (if any)
            shift = 1
            if repetition.get_source() is not None:
                sppasSelfRepet.__add_repetition(repetition, tier, tok_start,
                                                src_tier, echo_tier)
                (src_start, src_end) = repetition.get_source()
                shift = src_end + 1

            # Fix indexes for the next search
            tok_start, tok_search, tok_end = self.__fix_indexes(
                tier, tok_start, shift)

        return src_tier, echo_tier

    # -----------------------------------------------------------------------
    # Run
    # -----------------------------------------------------------------------

    def run(self, input_filename, output_filename=None):
        """Run the Repetition Automatic Detection annotation.

        :param input_filename: (str) File with time-aligned tokens or lemmas
        :param output_filename:(str) Name of the file to save the result

        """
        self.print_filename(input_filename)
        self.print_options()
        self.print_diagnosis(input_filename)

        # Get the tier to be used
        parser = sppasRW(input_filename)
        trs_input = parser.read()

        if self._options['lemmas'] is True:
            tier_input = sppasFindTier.aligned_lemmas(trs_input)
        else:
            tier_input = sppasFindTier.aligned_tokens(trs_input)

        # Repetition Automatic Detection
        (src_tier, echo_tier) = self.self_detection(tier_input)

        # Create the transcription result
        trs_output = sppasTranscription("SelfRepetition")
        trs_output.set_meta('self_repetition_result_of', input_filename)
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
    def __add_repetition(repetition, spk_tier, start_idx, src_tier, echo_tier):
        """Add a repetition - source and echos - in tiers.

        :param repetition: (DataRepetition)
        :param spk_tier: (sppasTier) The tier of the speaker (to detect sources)
        :param start_idx: (int) start index of the interval in spk_tier
        :param src_tier: (sppasTier) The resulting tier with sources
        :param echo_tier: (sppasTier) The resulting tier with echos
        :returns: (bool) the repetition was added or not

        """
        index = len(src_tier)

        # Source
        s, e = repetition.get_source()
        src_begin = spk_tier[start_idx + s].get_lowest_localization()
        src_end = spk_tier[start_idx + e].get_highest_localization()
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
            rep_begin = spk_tier[start_idx + s].get_lowest_localization()
            rep_end = spk_tier[start_idx + e].get_highest_localization()
            time = sppasInterval(rep_begin.copy(), rep_end.copy())
            a = echo_tier.create_annotation(
                sppasLocation(time),
                sppasLabel(sppasTag("R" + str(index + 1))))
            a.set_meta('is_self_repetition_of', src_id)

        return True
