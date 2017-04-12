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

    src.annotations.tokenize.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tokenization module for the multilingual text normalization system.

"""
import re

from sppas.src.utils.makeunicode import sppasUnicode

# ---------------------------------------------------------------------------


class sppasTokenizer(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Create words from tokens on the basis of a lexicon.

    This is a totally language independent method, based on a longest
    matching algorithm to aggregate tokens into words. Words of a lexicon
    are found and:

     1/ unbind or not if they contain a separator character:

        - rock'n'roll -> rock'n'roll
        - I'm -> I 'm
        - it's -> it 's

     2/ bind using a character separator like for example, with '_':

        - parce que -> parce_que
        - rock'n roll -> rock'n_roll

    """
    SEPARATOR = "_"
    STICK_MAX = 7

    # -------------------------------------------------------------------------

    def __init__(self, vocab=None):
        """ Create a new sppasTokenizer instance.

        :param vocab: (Vocabulary)

        """
        self.__vocab = vocab
        self.separator = sppasTokenizer.SEPARATOR
        self.aggregate_max = sppasTokenizer.STICK_MAX

    # -------------------------------------------------------------------------

    def __stick_longest_lr(self, phrase, separator):
        """ Return the longest first word of a phrase.
        A longest matching algorithm is applied from left to right.

        :param phrase: (str)
        :returns: tuple of (index of the first longest token, the longest token)

        """
        tab_toks = phrase.split(" ")
        token = tab_toks[0]
        i = len(tab_toks)

        if self.__vocab is None:
            return 1, token

        while i > 0:
            # try to aggregate all tokens
            token = separator.join(tab_toks)

            # next round will try without the last token
            tab_toks.pop()
            i -= 1

            # find if this is a word in the vocabulary
            if self.__vocab.is_unk(token) is False:
                break

        # the first real token is the first given token
        return i, sppasUnicode(token).to_strip()

    # -------------------------------------------------------------------------

    def bind(self, utt):
        """ Bind tokens of an utterance using a specific character.

        :param utt: (list) List of tokens of an utterance (a transcription, a sentence, ...)
        :returns: A list of strings

        """
        new_utt = list()

        idx_start = 0
        while idx_start < len(utt):

            # use a longest matching to aggregate the current token with the next ones
            idx_end = min(len(utt), idx_start+self.aggregate_max+1)
            phrase = " ".join(utt[idx_start:idx_end])
            idx_end, word = self.__stick_longest_lr(sppasUnicode(phrase).to_strip(), self.separator)

            new_utt.append(word)
            idx_start += idx_end + 1

        return new_utt

    # -----------------------------------------------------------------------

    def unbind(self, utt):
        """ Unbind tokens containing - or ' or . depending on rules.

        :param utt: (list) List of tokens of an utterance (a transcription, a sentence, ...)
        :returns: A list of strings

        """
        new_utt = list()
        for tok in utt:
            # a missing compound word?
            #   --> an unknown token
            #   --> containing a special character
            #   --> that is not a truncated word!
            if self.__vocab.is_unk(tok.lower().strip()) is True and ("-" in tok or "'" in tok or "." in tok) and not tok.endswith('-'):

                # KEEP special chars in the array!
                tab_split = re.split("([-'.])", tok)
                tab_tok = list(entry for entry in tab_split if len(entry) > 0)
                idx_start = 0
                while idx_start < len(tab_tok):

                    # use a longest matching to aggregate the current token with the next ones
                    idx_end = min(len(tab_tok), idx_start + 5)
                    phrase = " ".join(tab_tok[idx_start:idx_end])
                    idx_end, word = self.__stick_longest_lr(sppasUnicode(phrase).to_strip(), "")

                    new_utt.append(word)
                    idx_start += idx_end + 1

            else:
                new_utt.append(sppasUnicode(tok).to_strip())

        return new_utt
