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

    src.annotations.sppastok.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    SPPAS integration of Text Normalization.
    For details, read the following reference:

        | Brigitte Bigi (2011).
        | A Multilingual Text Normalization Approach.
        | 2nd Less-Resourced Languages workshop,
        | 5th Language & Technology Conference, Poznan (Poland).

"""
import os.path

from sppas import RESOURCES_PATH
from sppas.src.resources.vocab import Vocabulary
from sppas.src.resources.dictrepl import DictRepl
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.tier import Tier
import sppas.src.annotationdata.aio

from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyInputError
from ..annotationsexc import NoInputError

from .normalize import TextNormalizer

# ---------------------------------------------------------------------------


class sppasTok(sppasBaseAnnotation):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Text normalization automatic annotation.

    """
    def __init__(self, vocab, lang="und", logfile=None):
        """ Create a sppasTok instance.

        :param vocab: (str) name of the file with the orthographic transcription
        :param lang: (str) the language code
        :param logfile: (sppasLog)

        """
        sppasBaseAnnotation.__init__(self, logfile)

        self.normalizer = None
        voc = Vocabulary(vocab)
        self.normalizer = TextNormalizer(voc, lang)

        # Replacement dictionary
        replace_filename = os.path.join(RESOURCES_PATH, "repl", lang + ".repl")
        if os.path.exists(replace_filename):
            dict_replace = DictRepl(replace_filename, nodump=True)
        else:
            dict_replace = DictRepl()
        self.normalizer.set_repl(dict_replace)

        # Punctuations dictionary
        punct_filename = os.path.join(RESOURCES_PATH, "vocab", "Punctuations.txt")
        if os.path.exists(replace_filename):
            vocab_punct = Vocabulary(punct_filename, nodump=True)
        else:
            vocab_punct = Vocabulary()
        self.normalizer.set_punct(vocab_punct)

        # List of options to configure this automatic annotation
        self._options['faked'] = True
        self._options['std'] = False
        self._options['custom'] = False

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options. Available options are:

            - faked
            - std
            - custom

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if key == "faked":
                self.set_faked(opt.get_value())
            elif key == "std":
                self.set_std(opt.get_value())
            elif key == "custom":
                self.set_custom(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_faked(self, value):
        """ Fix the faked option.

        :param value: (bool) Create a faked tokenization

        """
        self._options['faked'] = value

    # -----------------------------------------------------------------------

    def set_std(self, value):
        """ Fix the std option.

        :param value: (bool) Create a standard tokenization

        """
        self._options['std'] = value

    # -----------------------------------------------------------------------

    def set_custom(self, value):
        """ Fix the custom option.

        :param value: (bool) Create a customized tokenization

        """
        self._options['custom'] = value

    # -----------------------------------------------------------------------
    # Methods to tokenize series of data
    # -----------------------------------------------------------------------

    def convert(self, tier):
        """ Tokenization of all labels of a tier.

        :param tier: (Tier) contains the orthographic transcription
        :returns: A tuple with 3 tiers named "Tokens-Faked", "Tokens-Std" and "Tokens-Custom"

        """
        if tier.IsEmpty() is True:
            raise EmptyInputError(name=tier.GetName())

        tokens_faked = None
        if self._options['faked'] is True:
            tokens_faked = self.__convert(tier, [])
            tokens_faked.SetName("Tokens")

        tokens_std = None
        if self._options['std'] is True:
            actions = ['std']
            tokens_std = self.__convert(tier, actions)
            tokens_std.SetName("Tokens-Std")

        tokens_custom = None
        if self._options['custom'] is True:
            actions = ['std', 'tokenize']
            tokens_custom = self.__convert(tier, actions)
            tokens_custom.SetName("Tokens-Custom")

        # Align Faked and Standard
        if tokens_faked is not None and tokens_std is not None:
            self.align_tiers(tokens_std, tokens_faked)

        return tokens_faked, tokens_std, tokens_custom

    # ------------------------------------------------------------------------

    def align_tiers(self, std_tier, faked_tier):
        """ Force standard spelling and faked spelling to share the same
        number of tokens.

        :param std_tier: (Tier)
        :param faked_tier: (Tier)

        """
        if self._options['std'] is False:
            return

        i = 0
        for astd, afaked in zip(std_tier, faked_tier):
                i += 1

                for text_std, text_faked in zip(astd.GetLabel().GetLabels(),afaked.GetLabel().GetLabels()):

                    try:
                        texts, textf = self.__align_tiers(text_std.GetValue(), text_faked.GetValue())
                        text_std.SetValue(texts)
                        text_faked.SetValue(textf)

                    except Exception:
                        self.print_message("Standard/Faked tokens matching error, at interval {:d}\n".format(i), indent=2, status=1)
                        self.print_message(astd.GetLabel().GetValue(), indent=3)
                        self.print_message(afaked.GetLabel().GetValue(), indent=3)
                        self.print_message("Fall back on faked.", indent=3, status=3)
                        text_std.SetValue(textf)

    # ------------------------------------------------------------------------

    def get_trans_tier(self, trs_input):
        """ Return the tier with transcription, or None.

        :param trs_input: (Transcription)
        :returns: (tier)

        """
        for tier in trs_input:
            tier_name = tier.GetName().lower()
            if "transcription" in tier_name:
                return tier

        for tier in trs_input:
            tier_name = tier.GetName().lower()
            if "trans" in tier_name:
                return tier
            elif "trs" in tier_name:
                return tier
            elif "ipu" in tier_name:
                return tier
            elif "ortho" in tier_name:
                return tier
            elif "toe" in tier_name:
                return tier

        return None

    # ------------------------------------------------------------------------

    def run(self, input_filename, output_filename):
        """ Run the Text Normalization process on an input file.

        :param input_filename: (str) Name of the input file with the transcription
        :param output_filename: (str) Name of the resulting file with normalization

        """
        self.print_options()
        self.print_diagnosis(input_filename)

        # Get input tier to tokenize
        trs_input = sppas.src.annotationdata.aio.read(input_filename)
        tier_input = self.get_trans_tier(trs_input)
        if tier_input is None:
            raise NoInputError

        # Tokenize the tier
        tier_faked_tokens, tier_std_tokens, tier_custom = self.convert(tier_input)

        # Save
        trs_output = Transcription("SPPAS Text Normalization")
        if tier_faked_tokens is not None:
            trs_output.Add(tier_faked_tokens)
        if tier_std_tokens is not None:
            trs_output.Add(tier_std_tokens)
        if tier_custom is not None:
            trs_output.Add(tier_custom)

        # Save in a file
        if len(trs_output) > 0:
            sppas.src.annotationdata.aio.write(output_filename, trs_output)
        else:
            raise IOError("No resulting tier. No file created.")    

    # ------------------------------------------------------------------------
    # Private: some workers...
    # ------------------------------------------------------------------------

    def __convert(self, tier, actions):
        """ Normalize all labels of an annotation.
        (normalize not only the one with the best score!).

        """
        tokens = Tier("Tokens")
        for i, ann in enumerate(tier):
            af = ann.Copy()
            for text in af.GetLabel().GetLabels():
                # Do not tokenize an empty label, noises, laughter...
                if text.IsSpeech() is True:
                    try:
                        normalized = self.normalizer.normalize(text.GetValue(), actions)
                    except Exception as e:
                        normalized = ""
                        if self.logfile is not None:
                            self.logfile.print_message("Error while normalizing interval {:d}: {:s}".format(i, str(e)), indent=3)
                        else:
                            print("Error while normalizing interval {:d}: {:s}".format(i, str(e)))
                    text.SetValue(normalized)
            tokens.Append(af)

        return tokens

    # -----------------------------------------------------------------------

    def __align_tiers(self, std, faked):
        """ Align standard spelling tokens with faked spelling tokens.

        :param std: (str)
        :param faked: (str)
        :returns: a tuple of std and faked

        """
        stds = std.split()
        fakeds = faked.split()
        if len(stds) == len(fakeds):
            return std,faked

        tmp = []
        for f in fakeds:
            toks = f.split('_')
            for t in toks:
                tmp.append(t)
        fakeds = tmp[:]

        num_tokens = len(stds)
        i = 0
        while i < num_tokens:
            if "'" in stds[i]:
                if not stds[i].endswith("'") and fakeds[i].endswith("'"):
                    fakeds[i] = fakeds[i] + fakeds[i+1]
                    del fakeds[i+1]

            if "-" in stds[i]:
                if not stds[i].endswith("-") and "-" not in fakeds[i]:

                    fakeds[i] = fakeds[i] + fakeds[i+1]
                    del fakeds[i+1]

            num_underscores = stds[i].count('_')
            if num_underscores > 0:
                if not self.normalizer.vocab.is_unk(stds[i]):
                    n = num_underscores + 1
                    fakeds[i] = "_".join(fakeds[i:i+n])
                    del fakeds[i+1:i+n]

            i += 1

        if len(stds) != len(fakeds):
            raise
        return std, " ".join(fakeds)
