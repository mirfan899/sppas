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

    Multilingual text normalization system.

"""
import re

from sppas.src.utils.makeunicode import u, sppasUnicode
from sppas.src.resources.vocab import Vocabulary
from sppas.src.resources.dictrepl import DictRepl

from .transcription import sppasTranscription
from .tokenize import sppasTokenizer
from .num2letter import sppasNum
from .language import without_whitespace
from .splitter import sppasTokSplitter

# ---------------------------------------------------------------------------


class DictReplUTF8(DictRepl):
    """ Replacement dictionary of UTF8 characters that caused problems. """

    def __init__(self):
        DictRepl.__init__(self, None, nodump=True)

        self.add(u"æ", u"ae")
        self.add(u"œ", u"oe")
        self.add(u"，", u", ")
        self.add(u"”", u'"')
        self.add(u"“", u'"')
        self.add(u"。", u". ")
        self.add(u"》", u'"')
        self.add(u"《", u'"')
        self.add(u"«", u'"')
        self.add(u"»", u'"')
        self.add(u"’", u"'")

# ---------------------------------------------------------------------------


class TextNormalizer(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Multilingual text normalization

    """
    def __init__(self, vocab=None, lang="und"):
        """ Create a new DictTok instance.

        :param vocab: (Vocabulary)
        :param lang: the language code in iso639-3.

        """
        # resources
        self.dicoutf = DictReplUTF8()
        self.repl = DictRepl(None)
        self.punct = Vocabulary()
        self.vocab = vocab
        if vocab is None:
            self.vocab = Vocabulary()

        # members
        self.lang = lang
        self.delimiter = ' '

    # ------------------------------------------------------------------
    # Options
    # ------------------------------------------------------------------

    def set_delim(self, delim):
        """ Set the delimiter, used to separate tokens.

        :param delim: (str) a unicode character.

        """
        self.delimiter = delim

    # -------------------------------------------------------------------------

    def set_vocab(self, vocab):
        """ Set the lexicon.

        :param vocab: (Vocabulary).

        """
        # TODO: test instance

        self.vocab = vocab

    # -------------------------------------------------------------------------

    def set_repl(self, repl):
        """ Set the dictionary of replacements.

        :param repl: (DictRepl)

        """
        # TODO: test instance

        self.repl = repl

    # -------------------------------------------------------------------------

    def set_punct(self, punct):
        """ Set the list of punctuation.

        :param punct: (Vocabulary)

        """
        # TODO: test instance

        self.punct = punct

    # -------------------------------------------------------------------------

    def set_lang(self, lang):
        """ Set the language.

        :param lang: (str) the language code in iso639-3 (fra, eng, vie, cmn...).

        """
        self.lang = lang

    # -------------------------------------------------------------------------
    # Language independent modules
    # -------------------------------------------------------------------------

    def replace(self, utt):
        """ Examine tokens and performs some replacements.
        A dictionary with symbols contains the replacements to operate.

        :param utt: (list) the utterance
        :returns: A list of strings

        """
        # Specific case of float numbers
        sent = ' '.join(utt)
        sent = re.sub('([0-9])\.([0-9])', r'\1 NUMBER_SEP_POINT \2', sent)
        sent = re.sub('([0-9])\,([0-9])', r'\1 NUMBER_SEP \2', sent)
        sent = sppasUnicode(sent).to_strip()
        _utt = sent.split()

        # Other generic replacements
        _result = []
        for s in _utt:
            if self.repl.is_key(s):
                s = s.replace(s, self.repl.replace(s))
            _result.append(sppasUnicode(s).to_strip())

        return _result

    # ------------------------------------------------------------------

    def tokenize(self, utt):
        """ Tokenize.

        :param utt: (list)
        :returns: (list)

        """
        tok = sppasTokenizer(self.vocab)

        # rules for - ' .
        unbind_result = tok.unbind(utt)

        # longest matching for whitespace
        if without_whitespace(self.lang):
            tok.separator = ""
            tok.aggregate_max = 15

        bind_result = tok.bind(unbind_result)

        return bind_result

    # ------------------------------------------------------------------

    def numbers(self, utt):
        """ Convert numbers to their written form.

        :param utt: (list)
        :returns: (list)

        """
        num2letter = sppasNum(self.lang)
        _result = []
        for i in utt:
            if "/" not in i:
                _result.append(num2letter.convert(i))
            else:
                _result.append(i)

        return _result

    # ------------------------------------------------------------------

    def lower(self, utt):
        """ Lower a list of strings.

        :param utt: (list)

        """
        _utt = []
        for tok in utt:
            if "/" not in tok:
                _utt.append(sppasUnicode(tok).to_lower())
            else:
                _utt.append(tok)

        return _utt

    # ------------------------------------------------------------------

    def remove(self, utt, wlist):
        """ Remove data of an utterance if included in a dictionary.
        Only used to remove punctuation.

        :param entry:
        :param wlist: (WordList)

        """
        _utt = []
        for tok in utt:
            if wlist.is_unk(tok) is True and "gpd_" not in tok and "ipu_" not in tok:
                _utt.append(tok)

        return _utt

    # ------------------------------------------------------------------
    # The main tokenize is HERE!
    # ------------------------------------------------------------------

    def normalize(self, entry, actions=[]):
        """ Tokenize an utterance.

        :param entry: (str) the string to normalize
        :param actions: (list) the modules/options to enable.

            - "std": generated the standard orthography instead of the faked one
            - "replace": use a replacement dictionary
            - "tokenize": tokenize the entry
            - "numbers": convert numbers to their written form
            - "lower": change case of characters to lower
            - "punct": remove punctuation

        :returns: (str) the normalized entry

        Important:
        An empty actions list or a list containing only "std" means to
        enable all actions.

        """
        _str = sppasUnicode(entry).to_strip()

        # Remove UTF-8 specific characters that are not in our dictionaries!
        for key in self.dicoutf.get_keys():
            _str = _str.replace(key, self.dicoutf.replace(key))

        # Clean the Enriched Orthographic Transcription
        ortho = sppasTranscription()
        _str = ortho.clean_toe(_str)
        if "std" in actions:
            _str = ortho.toe_spelling(_str, True)
        else:
            _str = ortho.toe_spelling(_str, False)

        # Split using whitespace or characters.
        splitter = sppasTokSplitter(self.lang, self.repl)
        utt = splitter.split(_str)

        # The entry is now a list of strings on which we'll perform actions
        # -----------------------------------------------------------------
        if len(actions) == 0 or (len(actions) == 1 and "std" in actions):
            actions.append("replace")
            actions.append("tokenize")
            actions.append("numbers")
            actions.append("lower")
            actions.append("punct")

        if "replace" in actions:
            utt = self.replace(utt)

        if "tokenize" in actions:
            utt = self.tokenize(utt)

        if "numbers" in actions:
            utt = self.numbers(utt)

        if "lower" in actions:
            utt = self.lower(utt)

        if "punct" in actions:
            utt = self.remove(utt, self.punct)

        # Finally, prepare the result
        result = ""
        for s in utt:
            s = sppasUnicode(s).to_strip()
            result = result + " " + s.replace(" ", "_")

        result = sppasUnicode(result).to_strip()
        if len(result) == 0:
            return ""  # Nothing valid!

        return result.replace(" ", self.delimiter)
