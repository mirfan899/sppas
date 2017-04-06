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

    src.annotations.Repet.sppasrepet.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import sppas.src.annotationdata.aio
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.tier import Tier
from sppas.src.annotationdata.annotation import Annotation
from sppas.src.annotationdata.ptime.interval import TimeInterval
from sppas.src.annotationdata.label.label import Label
from sppas.src.resources.vocab import Vocabulary
from sppas.src.resources.unigram import Unigram

from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import AnnotationOptionError

from .dictlem import LemmaDict
from .detectrepet import Repetitions
from .datastructs import DataSpeaker

# ---------------------------------------------------------------------------


class sppasRepet(sppasBaseAnnotation):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS Automatic Repetition Detection

    Either detect self-repetitions or other-repetitions with recall=1.

    This annotation is performed on the basis of aligned-tokens.
    The tokens can be lemmatized from a dictionary.

    The output is made of 2 tiers including intervals with sources and echos.

    """
    MAX_SPAN = 20
    MAX_ALPHA = 4.

    # -----------------------------------------------------------------------

    def __init__(self, resource_file="", logfile=None):
        """ Create a new sppasRepetition instance.

        :param resource_file: Either the lemma dictionary or the list of stop-words.

        Attention: the extension of the resource file name is very important:
        must be ".stp" for stop-words and ".lem" for lemmas (case-sensitive)!

        """
        sppasBaseAnnotation.__init__(self, logfile)

        # Members
        self._use_lemmatize = True   # Lemmatize the input
        self._use_stopwords = True   # Add specific stopwords of the input
        self._span = 5               # Detection length (nb of IPUs; 1=current IPU)
        self._alpha = 0.5            # Specific stop-words threshold coefficient
        self.lemmatizer = LemmaDict()
        self.stop_words = Vocabulary()

        # Create the lemmatizer instance
        try:
            lemma_file = resource_file.replace(".stp", ".lem")
            self.lemmatizer.load(lemma_file)
        except:
            self._use_lemmatize = False

        if self._use_lemmatize is False:
            if logfile is not None:
                logfile.print_message("Lemmatization disabled.", indent=2, status=3)
            else:
                print(" ... ... [ INFO ] Lemmatization disabled.")
        else:
            if logfile is not None:
                logfile.print_message("Lemmatization enabled.", indent=2, status=3)
            else:
                print(" ... ... [ INFO ] Lemmatization enabled.")

        # Create the list of stop words (list of non-relevant words)
        try:
            stop_file = resource_file.replace(".lem", ".stp")
            self.stop_words.load_from_ascii(stop_file)
        except:
            pass

        if self._use_stopwords is False:
            if logfile is not None:
                logfile.print_message("StopWords disabled.", indent=2, status=3)
            else:
                print(" ... ... [ INFO ] StopWords disabled.")
        else:
            if logfile is not None:
                logfile.print_message("StopWords: {:d}".format(self.stop_words.get_size()), indent=2, status=3)
            else:
                print(" ... ... [ INFO ] StopWords: {:d}".format(self.stop_words.get_size()))

    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options.

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
        """ Fix the use_lemmatize option.

        If use_lemmatize is set to True, sppasRepetition() will lemmatize the
        input before the repetition automatic detection.

        :param use_lemmatize: (bool)

        """
        self._use_lemmatize = use_lemmatize

    # ----------------------------------------------------------------------

    def set_use_stopwords(self, use_stopwords):
        """ Fix the use_stopwords option.

        If use_stopwords is set to True, sppasRepetition() will add specific
        stopwords to the stopwords list (deducted from the input text).

        :param use_stopwords: (bool)

        """
        self._use_stopwords = use_stopwords

    # ----------------------------------------------------------------------

    def set_span(self, span):
        """ Fix the span option.
        Span is the maximum number of IPUs to find repetitions.

        :param span: (int)

        """
        span = int(span)
        if 0 < span <= sppasRepet.MAX_SPAN:
            self._span = span
        else:
            raise ValueError

    # ----------------------------------------------------------------------

    def set_alpha(self, alpha):
        """ Fix the alpha option.

        :param alpha: (float)

        """
        alpha = float(alpha)
        if 0. < alpha < sppasRepet.MAX_ALPHA:
            self._alpha = alpha
        else:
            raise ValueError

    # ----------------------------------------------------------------------
    # Automatic Detection search parameters                                  #
    # ----------------------------------------------------------------------

    def lemmatize(self, tokens_tier):
        """ Lemmatize a tier.

        :param tokens_tier: (Tier) A tier with aligned tokens.
        :returns: Tier with aligned lemmatization

        """
        if self._use_lemmatize is False:
            return

        lemma_tier = tokens_tier.Copy()
        if self.lemmatizer.get_size() > 0:
            for ann in lemma_tier:
                token = ann.GetLabel().GetValue()
                lemma = self.lemmatizer.get_lem(token)
                ann.GetLabel().SetValue(lemma)

        return lemma_tier

    # -----------------------------------------------------------------------
    # Automatic Detection search 
    # -----------------------------------------------------------------------

    def get_stop_list(self, tier=None):
        """ Return the expected list of stop-words.
        It is either:

            - the loaded list or,
            - the loaded list + un-relevant tokens, estimated on the basis
            of the given tier.

        A token 'w' is relevant for the speaker if its probability is
        less than a threshold:

            | P(w) <= 1 / (alpha * V)

        where 'alpha' is an empirical coefficient and 'V' is the vocabulary
        size of the speaker.

        :param tier: (Tier) A tier with entries to be analyzed.

        """
        if self._use_stopwords is False:
            return Vocabulary()

        if tier is None:
            return self.stop_words

        # Create the Unigram and put data
        u = Unigram()
        for a in tier:
            if a.GetLabel().IsSpeech() is True:
                u.add(a.GetLabel().GetValue())

        # Estimate values for relevance
        _v = float(u.get_size())
        threshold = 1. / (self._alpha * _v)

        # Estimate if a token is relevant; if not: put in the stop-list
        stop_list = self.stop_words.copy()
        for token in u.get_tokens():
            p_w = float(u.get_count(token)) / float(u.get_sum())
            if p_w > threshold:
                stop_list.add(token)
                if self.logfile is not None:
                    self.logfile.print_message('Add in the stop-list: {:s}'.format(token), indent=3)

        return stop_list

    # ------------------------------------------------------------------

    def self_detection(self, tier):
        """ Self-Repetition detection.

        :param tier: (Tier)

        """
        # Use the appropriate stop-list
        stop_words = self.get_stop_list(tier)
        # Create a data structure to detect and store a source and its echos
        repetition = Repetitions(stop_words)
        # Create output data
        src_tier = Tier("SR-Source")
        echo_tier = Tier("SR-Echo")

        # Initialization of tok_start and tok_end
        tok_start = 0
        tok_search = sppasRepet.find_next_break(tier, tok_start+1, span=1)
        tok_end = sppasRepet.find_next_break(tier, tok_start+1, span=self._span)

        # Detection is here:
        while tok_start < tok_end:

            # Build an array with the tokens
            tokens1 = list()
            for i in range(tok_start, tok_end+1):
                tokens1.append(tier[i].GetLabel().GetValue())
            speaker1 = DataSpeaker(tokens1)

            # Detect the first self-repetition in these data
            repetition.detect(speaker1, tok_search-tok_start, None)

            # Save the repetition (if any)
            shift = 1
            if repetition.get_source() is not None:
                sppasRepet.__add_repetition(repetition, tier, tier, tok_start, tok_start, src_tier, echo_tier)
                (src_start, src_end) = repetition.get_source()
                shift = src_end + 1

            # Prepare next search
            tok_start += shift
            tok_search = sppasRepet.find_next_break(tier, tok_start+1, span=1)
            tok_end = sppasRepet.find_next_break(tier, tok_start+1, span=self._span)

        return src_tier, echo_tier

    # ------------------------------------------------------------------------

    def other_detection(self, inputtier1, inputtier2):
        """ Other-Repetition detection.

        :param inputtier1: (Tier)
        :param inputtier2: (Tier)

        """
        inputtier1.SetRadius(0.04)
        inputtier2.SetRadius(0.04)
        # Use the appropriate stop-list: add un-relevant tokens of the echoing speaker
        stop_words = self.get_stop_list(inputtier2)
        # Create repeat objects
        repetition = Repetitions(stop_words)
        # Create output data
        src_tier = Tier("OR-Source")
        echo_tier = Tier("OR-Echo")

        # Initialization of tok_start, and tok_end
        tok_start_src = 0
        tok_end_src = min(20, inputtier1.GetSize()-1)
        tok_start_echo = 0

        tokens1 = list()
        tokens2 = list()
        # Detection is here:
        # detect() is applied work by word, from tok_start to tok_end
        while tok_start_src < tok_end_src:

            # Build an array with the tokens
            tokens1 = list()
            for i in range(tok_start_src, tok_end_src+1):
                tokens1.append(inputtier1[i].GetLabel().GetValue())
            speaker1 = DataSpeaker(tokens1)

            # Create speaker2
            src_begin = inputtier1[tok_start_src].GetLocation().GetBeginMidpoint()
            # re-create only if different of the previous step...
            if len(tokens2) == 0 or inputtier2[tok_start_echo].GetLocation().GetBeginMidpoint() < src_begin:
                tokens2 = list()
                nb_breaks = 0
                old_tok_start_echo = tok_start_echo

                for i in range(old_tok_start_echo, len(inputtier2)):
                    ann = inputtier2[i]
                    if ann.GetLocation().GetBeginMidpoint() >= src_begin:
                        if tok_start_echo == old_tok_start_echo:
                            tok_start_echo = i
                        if ann.GetLabel().IsSilence():
                            nb_breaks += 1
                        if nb_breaks == self._span:
                            break
                        tokens2.append(ann.GetLabel().GetValue())
                speaker2 = DataSpeaker(tokens2)

            # We can't go too further due to the required time-alignment of tokens between src/echo
            # Check only if the first token is the first token of a source!!
            repetition.detect(speaker1, 1, speaker2)

            # Save repeats
            shift = 1
            if repetition.get_source() is not None:
                s, e = repetition.get_source()
                saved = sppasRepet.__add_repetition(repetition, inputtier1, inputtier2, tok_start_src, tok_start_echo, src_tier, echo_tier)
                if saved is True:
                    shift = e + 1

            tok_start_src = min(tok_start_src + shift, inputtier1.GetSize()-1)
            tok_end_src = min(tok_start_src + 20, inputtier1.GetSize()-1)

        return src_tier, echo_tier

    # ------------------------------------------------------------------------

    @staticmethod
    def get_input_tier(trs):
        """ Return the tier with time-aligned tokens or None.

        :param trs: (Transcription)
        :returns: Tier

        """
        for tier in trs:
            if "align" in tier.GetName().lower() and "token" in tier.GetName().lower():
                return tier
        return None

    # ------------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self, input_filename1, input_filename2, output_filename):
        """ Run the Repetition Automatic Detection annotation.

        :param input_filename1: Name of the file with aligned tokens of spkeaker 1 (the source)
        :param input_filename2: Name of the file with aligned tokens of spkeaker 2 (the echo) if OR, or None for SR
        :param output_filename: Name of the file to save the result

        """
        self.print_options()
        self.print_diagnosis(input_filename1)
        if input_filename2 is not None:
            self.print_diagnosis(input_filename2)
        if self.logfile is not None:
            self.logfile.print_message("Span = " + str(self._span), indent=3)
            self.logfile.print_message("Alpha = " + str(self._alpha), indent=3)

        # Get the tiers to be used
        # ---------------------------------------------------------------

        # Tokens of main speaker
        trs_input1 = sppas.src.annotationdata.aio.read(input_filename1)
        tier1 = sppasRepet.get_input_tier(trs_input1)
        if tier1 is None:
            raise Exception("No tier found with time-aligned tokens. "
                            "One of the tier names must contain both 'token' and 'align'.")
        if tier1.IsEmpty() is True:
            raise Exception("Empty tokens tier (main speaker).\n")

        # Tokens of echoing speaker (if any)
        tier2 = None
        if input_filename2 is not None:
            trs_input2 = sppas.src.annotationdata.aio.read(input_filename2)
            tier2 = sppasRepet.get_input_tier(trs_input2)
            if tier2.IsEmpty() is True:
                raise Exception("Empty tokens tier (echoing speaker).\n")

        # Lemmatize input?
        if self._use_lemmatize:
            tier1 = self.lemmatize(tier1)
            if tier2 is not None:
                tier2 = self.lemmatize(tier2)

        # Repetition Automatic Detection
        # ---------------------------------------------------------------
        if tier2 is None:
            (src_tier, echo_tier) = self.self_detection(tier1)
        else:
            (src_tier, echo_tier) = self.other_detection(tier1, tier2)

        # Save results
        # --------------------------------------------------------------
        trs_output = Transcription("Repetitions")
        trs_output.Append(src_tier)
        trs_output.Append(echo_tier)
        sppas.src.annotationdata.aio.write(output_filename, trs_output)

    # ------------------------------------------------------------------

    @staticmethod
    def find_next_break(tier, start, span):
        """ Return the index of the next interval representing a break.
        It depends on the 'span' value.

        :param tier: (Tier)
        :param start: (int) the position of the token where the search will start
        :param span: (int)
        :returns: (int) index of the next interval corresponding to the span

        """
        nb_breaks = 0
        for i in range(start, tier.GetSize()):
            if tier[i].GetLabel().IsSilence():
                nb_breaks += 1
                if nb_breaks == span:
                    return i
        return tier.GetSize() - 1

    # ------------------------------------------------------------------

    @staticmethod
    def __add_repetition(repetition, spk1_tier, spk2_tier, start_spk1, start_spk2, src_tier, echo_tier):
        """ Add a repetition - source and echos - in tiers.

        :param repetition: (DataRepetition)
        :param spk1_tier: (Tier) The tier of speaker 1 (to detect sources)
        :param spk2_tier: (Tier) The tier of speaker 2 (to detect echos)
        :param start_spk1: start index of the interval in spk1_tier
        :param start_spk2: start index of the interval in spk2_tier
        :param src_tier: (Tier) The resulting tier with sources
        :param echo_tier: (Tier) The resulting tier with echos
        :returns: (bool) the repetition was added or not

        """
        index = len(src_tier)
        # Source
        s, e = repetition.get_source()
        src_begin = spk1_tier[start_spk1+s].GetLocation().GetBegin()
        src_end = spk1_tier[start_spk1+e].GetLocation().GetEnd()
        time = TimeInterval(src_begin.Copy(), src_end.Copy())
        src_ann = Annotation(time, Label("S"+str(index+1)))
        try:
            src_tier.Add(src_ann)
        except Exception:
            return False

        # Echos
        for (s, e) in repetition.get_echos():
            rep_begin = spk2_tier[start_spk2+s].GetLocation().GetBegin()
            rep_end = spk2_tier[start_spk2+e].GetLocation().GetEnd()
            time = TimeInterval(rep_begin.Copy(), rep_end.Copy())
            rep_ann = Annotation(time, Label("R"+str(index+1)))
            echo_tier.Add(rep_ann)

        return True
