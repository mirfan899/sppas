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

DEBUG = False

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

    How to use sppasRepetition?

    >>> p = sppasRepetition(dictpath, lang)
    >>> p.run(inputtrsname, outputfilename)

    """
    MAX_SPAN = 20
    MAX_ALPHA = 4.

    # -----------------------------------------------------------------------

    def __init__(self, resource_file, logfile=None):
        """ Create a new sppasRepetition instance.

        :param resource_file: Either the lemma dictionary or the list of stop-words.

        Attention: the extension of the resource file name is very important:
        must be ".stp" for stop-words and ".lem" for lemmas (case-sensitive)!

        """
        sppasBaseAnnotation.__init__(self, logfile)

        # Members
        self._use_lemmatize = True   # Lemmatize the input
        self._use_stopwords = True   # Add specific stopwords of the input
        self._empan = 5              # Detection length (nb of IPUs; 1=current IPU)
        self._alpha = 0.5            # Specific stop-words threshold coefficient
        self.logfile = logfile
        self.lemmatizer = None
        self.__stop_words = None

        # Create the lemmatizer instance
        try:
            lemma_file = resource_file.replace(".stp", ".lem")
            self.lemmatizer = LemmaDict(lemma_file)
        except Exception:
            self._use_lemmatize = False

        if (self._use_lemmatize is True and self.lemmatizer.get_size() == 0) or self._use_lemmatize is False:
            if logfile is not None:
                logfile.print_message("Lemmatization disabled.", indent=2, status=3)
            else:
                print(" ... ... [ INFO ] Lemmatization disabled.")
            self._use_lemmatize = False

        # Create the list of stop words (list of non-relevant words)
        try:
            stop_file = resource_file.replace(".lem", ".stp")
            self.__stop_words = Vocabulary(filename=stop_file, nodump=True)
            if self.__stop_words.get_size() == 0:
                self._use_stopwords = False
        except Exception:
            self.__stop_words = Vocabulary()

        if self._use_stopwords is False:
            if logfile is not None:
                logfile.print_message("StopWords disabled.",indent=2,status=3)
            else:
                print(" ... ... [ INFO ] StopWords disabled.")

    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options.

        :param options: list of sppsOption instances

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
            self._empan = span
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

    # ------------------------------------------------------------------

    def relevancy(self, tier):
        """ Add very frequent tokens in a copy of the stopwords list.

        Estimate the relevance of each term by using the number of
        occurrences of this term in the input and compare this value
        to a threshold, to add the term (or not) in the stopwords list.

        :param tier: (Tier)
        :returns: a Vocabulary instance

        """
        l = self.__stop_words.copy()
        if tier is None:
            return l

        # Create the Unigram and put data
        u = Unigram()
        for a in tier:
            if a.GetLabel().IsSpeech() is True:
                u.add(a.GetLabel().GetValue())

        # Estimate if a token is relevant, put in the stoplist
        for token in u.get_tokens():
            freq = u.get_count(token)
            proba = float(freq) / float(u.get_sum())
            relevant = 1.0 / (float(u.get_size())*float(self._alpha))
            if proba > relevant:
                l.add(token)
                if self.logfile is not None:
                    self.logfile.print_message('Add in the stoplist: {:s}'.format(token), indent=3)

        return l

    # ------------------------------------------------------------------
    # Automatic Detection search 
    # ------------------------------------------------------------------
    
    def get_stop_list(self, tier=None):
        """ Return the expected list of stop-words. 
        
        :param tier: (Tier) A tier with entries to be analyzed.
        
        """
        if self._use_stopwords is True:
            return self.relevancy(tier)

        return self.__stop_words.copy()

    # ------------------------------------------------------------------

    def _addrepetition(self, repeatobj, nb_repets, inputtier1, inputtier2, tokstartsrc, tokstartrep, src_tier, echo_tier):
        """ Add sources and repetitions from repeatobj to the tiers.

        """
        n = 0
        for i in range(len(repeatobj)):

            # Source
            s, e = repeatobj.get_source(i)
            srcbegin = inputtier1[tokstartsrc+s].GetLocation().GetBegin()
            srcend = inputtier1[tokstartsrc+e].GetLocation().GetEnd()
            time = TimeInterval(srcbegin.Copy(), srcend.Copy())
            srcann = Annotation(time, Label("S"+str(nb_repets+n)))
            try:
                src_tier.Add(srcann)
            except Exception:
                continue

            # Repetition
            rep = repeatobj.get_echos(i)
            for r in rep:
                (s, e) = r
                repbegin = inputtier2[tokstartrep+s].GetLocation().GetBegin()
                repend   = inputtier2[tokstartrep+e].GetLocation().GetEnd()
                r = echo_tier.Lindex(repbegin)
                l = echo_tier.Rindex(repend)

                # all other cases (no repetition, overlap)
                time = TimeInterval(repbegin.Copy(), repend.Copy())
                repann = Annotation(time, Label("R"+str(nb_repets+n)))
                echo_tier.Add(repann)

            n += 1

        return n

    # ------------------------------------------------------------------

    def self_detection(self, tier):
        """ Self-Repetition detection.

        :param tier: (Tier)

        """
        # Use the appropriate stop-list
        stop_words = self.get_stop_list(tier)

        # Create repeat objects (a data structure to store sources and echos)
        repeatobj = Repetitions()

        # Create output data
        src_tier = Tier("Sources")
        echo_tier = Tier("Repetitions")
        nb_repets = 1

        # Initialization of tokstart and tokend
        tokstart = 0
        if tier[0].GetLabel().IsDummy():
            tokstart = 1
        toksearch = self.find_next_break(tier, tokstart+1, span=1)
        tokend = self.find_next_break(tier, tokstart+1, span=self._empan)

        # Detection is here:
        while tokstart < tokend:

            # Build an array with the tokens
            tokens1 = list()
            for i in range(tokstart, tokend+1):
                tokens1.append(tier[i].GetLabel().GetValue())
            speaker1 = DataSpeaker(tokens1, stop_words)

            # Detect repeats in these data
            repeatobj.detect(speaker1, toksearch-tokstart, None)

            # Save repeats
            if len(repeatobj) > 0:
                n = self._addrepetition(repeatobj, nb_repets, tier, tier, tokstart, tokstart, src_tier, echo_tier)
                nb_repets += n

            # Prepare next search
            tokstart = toksearch
            toksearch = sppasRepet.find_next_break(tier, tokstart+1, span=1)
            tokend = sppasRepet.find_next_break(tier, tokstart+1, span=self._empan)

        return src_tier, echo_tier

    # ------------------------------------------------------------------------

    def other_detection(self, inputtier1, inputtier2):
        """ Other-Repetition detection.

        :param inputtier1: (Tier)
        :param inputtier2: (Tier)

        """
        # Update the stoplist
        if self._use_stopwords is True:
            # other-repetition: relevance of the echoing-speaker
            stop_words = self.relevancy(inputtier2)
        else:
            stop_words = self.__stop_words

        # Create repeat objects
        repeatobj = Repetitions()

        # Create output data
        src_tier = Tier("OR-Source")
        echo_tier = Tier("OR-Repetition")

        nb_repets = 1

        # Initialization of tokstart, and tokend
        tokstartsrc = 0
        if inputtier1[0].GetLabel().IsDummy():
            tokstartsrc = 1
        tokendsrc = min(20, inputtier1.GetSize()-1)

        # Detection is here:
        # detect() is applied work by word, from tokstart to tokend
        while tokstartsrc < tokendsrc:

            # Build an array with the tokens
            tokens1 = list()
            for i in range(tokstartsrc, tokendsrc):
                tokens1.append(inputtier1[i].GetLabel().GetValue())
            speaker1 = DataSpeaker(tokens1, stop_words)

            # Create speaker2
            tokens2 = list()
            nbbreaks = 0
            tokstartrep = -1
            a = inputtier1[tokstartsrc]

            for (r,b) in enumerate(inputtier2):
                if b.GetLocation().GetBeginMidpoint() >= a.GetLocation().GetBeginMidpoint():
                    if tokstartrep == -1:
                        tokstartrep = r
                    if b.GetLabel().IsSilence():
                        nbbreaks += 1
                    if nbbreaks == self._empan:
                        break
                    tokens2.append(b.GetLabel().GetValue())
            speaker2 = DataSpeaker(tokens2, stop_words)

            # Detect repeats in these data: search if the first token of spk1
            # is the first token of a source.
            repeatobj.detect(speaker1, 1, speaker2)

            # Save repeats
            shift = 1
            if len(repeatobj) > 0:
                s, e = repeatobj.get_source(0)
                n = self._addrepetition(repeatobj, nb_repets, inputtier1, inputtier2, tokstartsrc, tokstartrep, src_tier, echo_tier)
                if n > 0:
                    nb_repets +=n
                shift = e + 1

            while speaker1.is_token(speaker1.get_token(shift)) is False and shift < 20:
                shift += 1

            tokstartsrc = tokstartsrc + shift
            tokstartsrc = min(tokstartsrc, inputtier1.GetSize()-1)
            tokendsrc = min(tokstartsrc + 20, inputtier1.GetSize()-1)

        return (src_tier,echo_tier)

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

    def run(self, input_filename1, input_filename2=None, output_filename=None):
        """ Run the Repetition Automatic Detection annotation.

        :param input_filename1:
        :param input_filename2:
        :param output_filename:

        """
        self.print_options()
        self.print_diagnosis(input_filename1)
        if input_filename2 is not None:
            self.print_diagnosis(input_filename2)
        if self.logfile is not None:
            self.logfile.print_message("Span = " + str(self._empan), indent=3)
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
