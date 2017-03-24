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

from .num2letter import sppasNum

# ---------------------------------------------------------------------------


class DictReplUTF8(DictRepl):
    """ Replacement dictionary of UTF8 characters that previously caused problems. """

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


def without_whitespace(lang):
    """ Return true if 'lang' is not using whitespace.
    Mandarin Chinese or Japanese languages return True, but English
    or French language return False.

    :param lang: (str) iso639-3 language code or a string containing
        such code, like "yue" or "yue-chars" for example.
    :returns: (bool)

    """
    lang_list = ["cmn", "jpn", "yue"]  # TODO: add languages
    for l in lang_list:
        if l in lang:
            return True

        return False

# ---------------------------------------------------------------------------


class sppasTranscription(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Manager of orthographic transcription.

    """
    def __init__(self):
        pass

    def __replace(self, obj):
        """
        Callback for clean_toe.

        @param obj (MatchObject)
        @return string
        """
        # Left part
        # Remove parentheses
        left = obj.group(1).replace('(', '')
        left = left.replace(')', '')
        # Replace spaces with underscores
        left = "_".join(left.split())

        # Right part
        # Remove spaces
        right = obj.group(2)
        right = "".join(right.split())
        return " [%s,%s]" % (left, right)

    def clean_toe(self, entry):
        """
        Clean Enriched Orthographic Transcription.
        The convention includes information that must be removed.

        @param entry (string)
        @return string

        """
        # Proper names: $ name ,P\$
        entry = re.sub(u',\s?[PTS]+\s?[\\/\\\]+\s?\\$', ur'', entry, re.UNICODE)
        entry = re.sub(ur'\$', ur'', entry, re.UNICODE)

        entry = re.sub(u'(gpd_[0-9]+)', ur" ", entry, re.UNICODE)
        entry = re.sub(u'(gpf_[0-9]+)', ur" ", entry, re.UNICODE)
        entry = re.sub(u'(ipu_[0-9]+)', ur" ", entry, re.UNICODE)

        # Remove invalid parenthesis content
        entry = re.sub(ur'\s+\([\w\xaa-\xff]+\)\s+', ' ', entry, re.UNICODE)
        entry = re.sub(ur'^\([\w\xaa-\xff]+\)\s+', ' ', entry, re.UNICODE)
        entry = re.sub(ur'\s+\([\w\xaa-\xff]+\)$', ' ', entry, re.UNICODE)

        entry = re.sub(ur'\s*\[([^,]+),([^,]+)\]', self.__replace, entry, re.UNICODE)
        return " ".join(entry.split())

    # ------------------------------------------------------------------

    def toe_spelling(self, entry, std=False):
        """
        Create a specific spelling from an Enriched Orthographic Transcription.

        @param entry (string): the EOT string
        @return a string.

        DevNote: Python’s regular expression engine supports Unicode.
        It can apply the same pattern to either 8-bit (encoded) or
        Unicode strings. To create a regular expression pattern that
        uses Unicode character classes for \w (and \s, and \b), use
        the “(?u)” flag prefix, or the re.UNICODE flag.
        """
        # Ensure all regexp will work!
        _fentry = " " + u(entry) + " "

        if std is False:
            # Stick unregular Liaisons to the previous token
            _fentry = re.sub(u' =([\w]+)=', ur'-\1', _fentry, re.UNICODE)
        else:
            # Remove Liaisons
            _fentry = re.sub(u' =([\w]+)=', ur' ', _fentry, re.UNICODE)

        # Laughing sequences
        _fentry = re.sub(u"\s?@\s?@\s?", u" ", _fentry, re.UNICODE)

        # Laughing
        _fentry = re.sub(u"([\w\xaa-\xff]+)@", ur"\1 @", _fentry, re.UNICODE)
        _fentry = re.sub(u"@([\w\xaa-\xff]+)", ur"@ \1", _fentry, re.UNICODE)

        # Noises
        _fentry = re.sub(u"([\w\xaa-\xff]+)\*", ur"\1 *", _fentry, re.UNICODE)
        _fentry = re.sub(u"\*([\w\xaa-\xff]+)", ur"* \1", _fentry, re.UNICODE)

        # Transcriptor comment's: {comment}
        _fentry = re.sub(u'\\{[\s\w\xaa-\xff\-:]+\\}', ur'', _fentry, re.UNICODE)
        # Transcriptor comment's: [comment]
        _fentry = re.sub(u'\\[[\s\w\xaa-\xff\-:]+\\]', ur'', _fentry, re.UNICODE)
        # Transcription comment's: (comment)
        # _fentry = re.sub(u' \\([\s\w\xaa-\xff\-:]+\\) ', ur'', _fentry, re.UNICODE) # .... warning!

        if std is False:
            # Special elisions (remove parenthesis content)
            _fentry = re.sub(u'\\([\s\w\xaa-\xff\-\']+\\)', ur'', _fentry, re.UNICODE)
        else:
            # Special elisions (keep parenthesis content)
            _fentry = re.sub(u'\\(([\s\w\xaa-\xff\-]+)\\)', ur'\1', _fentry, re.UNICODE)

        # Morphological variants are ignored for phonetization (same pronunciation!)
        _fentry = re.sub(u'\s+\\<([\-\'\s\w\xaa-\xff]+),[\-\'\s\w\xaa-\xff]+\\>', ur' \1', _fentry, re.UNICODE)
        _fentry = re.sub(u'\s+\\{([\-\'\s\w\xaa-\xff]+),[\-\'\s\w\xaa-\xff]+\\}', ur' \1', _fentry, re.UNICODE)
        _fentry = re.sub(u'\s+\\/([\-\'\s\w0-9\xaa-\xff]+),[\-\'\s\w0-9\xaa-\xff]+\\/', ur' \1', _fentry,
                         re.UNICODE)

        if std is False:
            # Special pronunciations (keep right part)
            _fentry = re.sub(u'\s+\\[([\s\w\xaa-\xff/-]+),([\s\w\xaa-\xff/]+)\\]', ur' \2', _fentry, re.UNICODE)
        else:
            # Special pronunciations (keep left part)
            _fentry = re.sub(u'\s+\\[([\s\w\xaa-\xff\\/-]+),[\s\w\xaa-\xff\\/]+\\]', ur' \1', _fentry, re.UNICODE)

        # Proper names: $ name ,P\$
        _fentry = re.sub(u',\s?[PTS]+\s?[\\/\\\]+\s?\\$', ur'', _fentry, re.UNICODE)
        _fentry = re.sub(u'\\$', ur'', _fentry, re.UNICODE)

        # Add a space if some punctuation are sticked to a word
        # TODO: do the same with the whole list of punctuations (in rutils).
        #        _fentry = re.sub(u'([:+^@}\(\){~|=]+)([\xaa-\xff]+)', ur'\1 \2', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+),', ur'\1 ,', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\+', ur'\1 +', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+);', ur'\1 ,', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+):', ur'\1 :', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\(', ur'\1 (', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\)', ur'\1)', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\{', ur'\1 {', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\}', ur'\1 }', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)=', ur'\1 =', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\?', ur'\1 ?', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\!', ur'\1 !', _fentry, re.UNICODE)
        # _fentry = re.sub(u'([\w\xaa-\xff]+)\/', ur'\1 !', _fentry, re.UNICODE) # no: if sampa in special pron.
        _fentry = re.sub(u"\s(?=,[0-9]+)", "", _fentry, re.UNICODE)

        # Correction of errors
        s = ""
        inpron = False
        for c in _fentry:
            if c == "/":
                inpron = not inpron
            else:
                if c == " " and inpron is True:
                    continue
            s += c
        return sppasUnicode(s).to_strip()

# ---------------------------------------------------------------------------


class sppasTokSplitter(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Utterance splitter

    Split an utterance into tokens using whitespace or characters.

    """
    def __init__(self, lang, dict_replace=None, speech=True):
        """ Creates a sppasTokSplitter.

        :param lang: the language code in iso639-3.
        :param dict_replace: Replacement dictionary
        :param speech: (bool) split transcribed speech vs written text

        """
        self.__lang = lang
        self.__speech = speech
        if dict_replace is not None:
            self.__repl = dict_replace
        else:
            self.__repl = DictRepl(None)

    # ------------------------------------------------------------------

    def split_characters(self, utt):
        """ Split an utterance by characters.

        :param utt: (str) the utterance (a transcription, a sentence, ...) in utf-8
        :returns: A string (split character by character, using spaces)

        """
        y = u(utt)
        tmp = " ".join(y)

        # split all characters except numbers and ascii characters
        sstr = re.sub(u"([０-９0-9a-zA-ZＡ-Ｔ\s]+\.?[０-９0-9a-zA-ZＡ-Ｔ\s]+)",
                      lambda o: u" %s " % o.group(0).replace(" ", ""), tmp)
        # and dates...
        if self.__speech is False:
            sstr = re.sub(u"([０-９0-9\s]+\.?[月年日\s]+)", lambda o: u" %s " % o.group(0).replace(" ", ""), sstr)
        # and ・
        sstr = re.sub(u'[\s]*・[\s]*', u"・", sstr)

        return sstr

    # ------------------------------------------------------------------

    def split(self, utt, std=False):
        """ Split an utterance using whitespace.
        If the language is character-based, split each character.

        :param utt: (str) an utterance of a transcription, a sentence, ...
        :param std: (bool)

        :returns: A list (array of string)

        """
        s = utt
        if without_whitespace(self.__lang) is True:
            s = self.split_characters(s)

        toks = []
        for t in s.split():
            # if not a phonetized entry
            if t.startswith("/") is False and t.endswith("/") is False:
                if std is False:
                    if without_whitespace(self.__lang) is False:
                        # Split numbers if sticked to characters
                        # attention: do not replace [a-zA-Z] by [\w] (because \w includes numbers)
                        # and not on Asian languages: it can be a tone!
                        t = re.sub(u'([0-9])([a-zA-Z])', ur'\1 \2', t)
                        t = re.sub(u'([a-zA-Z])([0-9])', ur'\1 \2', t)

                # Split some punctuation
                t = re.sub(u'\\[\\]', ur'\\] \\[', t)

                # Split dots if sticked to a word
                t = re.sub(u' \.([\w-])', ur'. \1', t)
                t = re.sub(u'^\.([\w-])', ur'. \1', t)

                # Split replacement characters
                for r in self.__repl.get_keys():
                    if t.endswith(r):
                        t = t[:-len(r)]
                        t = t + ' ' + r
            toks.append(t.strip())

        s = " ".join(toks)

        # Then split each time there is a space and return result
        s = sppasUnicode(s).to_strip()

        return s.split()

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

        - rock'n roll -> rock'n roll
        - I'm -> I 'm

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

    def __stick_longest_lr(self, phrase):
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
            token = self.separator.join(tab_toks)

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
        :returns: A list of tokens

        """
        new_utt = list()

        idx_start = 0
        while idx_start < len(utt):

            # use a longest matching to aggregate the current token with the next ones
            idx_end = min(len(utt), idx_start+self.aggregate_max+1)
            phrase = " ".join(utt[idx_start:idx_end])
            idx_end, word = self.__stick_longest_lr(sppasUnicode(phrase).to_strip())

            new_utt.append(word)
            idx_start += idx_end + 1

        return new_utt

    # -----------------------------------------------------------------------

    def unbind(self, utt):
        """ Examine tokens containing - or ' and split depending on rules.
        Language independent.

        :param utt: (list) List of tokens of an utterance (a transcription, a sentence, ...)
        :returns: A list of strings

        """
        _utt = list()
        for tok in utt:
            # a missing compound word?
            #   --> an unknown token
            #   --> containing a special character
            #   --> that is not a truncated word!
            if self.__vocab.is_unk(tok.lower().strip()) is True and ("-" in tok or "'" in tok or "." in tok) and not tok.endswith('-'):

                # Split the unknown token into a list
                # KEEP special chars ('-.) in the array!
                _tabtoks = re.split("([-'.])", tok)

                # Explore the list from left to right
                t1 = 0
                while t1 < len(_tabtoks):
                    i = len(_tabtoks)
                    i_ok = 0
                    # Find the longest string in the dict
                    while i >= t1 and i_ok == 0:
                        _token = _tabtoks[t1]
                        if i > (t1+1):
                            for j in range(t1+1, i):
                                _token += _tabtoks[j]
                            if self.__vocab.is_unk(_token) is False:
                                i_ok = j + 1
                        else:
                            i_ok = 1
                            _token = _tabtoks[t1]
                        i -= 1
                    t1 += i_ok
                    t2 = sppasUnicode(_token).to_strip()
                    if len(t2) > 0:
                        _utt.append(t2)

            else:
                _utt.append(sppasUnicode(tok).to_strip())

        return _utt

# ---------------------------------------------------------------------------


class DictTok(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Multilingual text normalization

    From the manual Enriched Orthographic Transcription, two derived ortho.
    transcriptions are generated automatically by the tokenizer: the "standard"
    transcription (the list of orthographic tokens); the "faked spelling" that
    is a specific transcription from which the obtained phonetic tokens are
    used by the phonetization system.

    The following illustrates an utterance text normalization in French:

    - Transcription:   j'ai on a j'ai p- (en)fin j'ai trouvé l(e) meilleur moyen c'était d(e) [loger,locher] chez  des amis
    (English translation is: I've we've I've - well I found the best way was to live in friends' apartment')

    - Resulting Standard tokens:  j' ai on a j' ai p- enfin j' ai trouvé le meilleur moyen c'était de loger  chez  des amis
    - Resulting Faked tokens:     j' ai on a j' ai p-   fin j' ai trouvé l  meilleur moyen c'était d  loche  chez  des amis

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
        self.num2letter = sppasNum(lang)
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

        This method also includes language specific replacements.
        Supported languages are: fra, cmn, jpn, yue, eng, ita, spa, khm, cat, pol.

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

    def lower(self, utt):
        """ Lower a list of strings.

        @param utt (list)

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
        """
        Remove data of an utterance if included in a dictionary.
        Only used to remove punctuation.

        @param entry
        @param wlist (WordList)

        """
        _utt = []
        for tok in utt:
            if wlist.is_unk(tok) is True and "gpd_" not in tok and "ipu_" not in tok:
                _utt.append(tok)

        return _utt


    # ------------------------------------------------------------------
    # The main tokenize is HERE!
    # ------------------------------------------------------------------

    def tokenize_list(self, utt, std=False):
        """
        Tokenize from a list of entries.
        """
        # Step 2: replace
        try:
            utt = self.replace(utt)
        except IOError:
            # repl file not found
            pass
        except Exception as e:
            raise Exception(" *in replace* "+str(e)+'\n')

        tok = sppasTokenizer(self.vocab)

        # Step 3: tokenize
        try:
            # rules for - and '
            utt = tok.unbind(utt)
            # longest matching for whitespace
            if without_whitespace(self.lang):
                tok.separator = ""
                tok.aggregate_max = 15
            utt = tok.bind(utt)
        except Exception as e:
            raise Exception(" *in tokenizer* "+str(e)+'\n')

        # Step 5: num2letter
        try:
            _utt = []
            for i in utt:
                if "/" not in utt:
                    _utt.append(self.num2letter.convert(i))
                else:
                    _utt.append(i)
            utt = _utt
        except Exception as e:
            pass

        # Step 6: lower
        try:
            utt = self.lower(utt)
        except Exception as e:
            raise Exception(" *in lower* "+str(e)+'\n')

        # Step 7: remove (punctuation)
        try:
            utt = self.remove(utt, self.punct)
        except Exception as e:
            raise Exception(" *in remove* "+str(e)+'\n')

        # Finally, prepare the result
        strres = ""
        for s in utt:
            s = sppasUnicode(s).to_strip()
            strres = strres + " " + s.replace(" ", "_")

        strres = sppasUnicode(strres).to_strip()
        if len(strres) == 0:
            return ""  # Nothing valid!

        return strres.replace(" ", self.delimiter)

    # ------------------------------------------------------------------

    def tokenize(self, entry, std=False):
        """
        Tokenize an utterrance.

        @param entry (UTF8-String) is the utterrance (the transcription)
        @param std (Boolean) In case of enriched transcription, std is used
        to fix the output as standard or faked spelling

        @return A string (the tokenized transcription)

        **TODO: disable TOE_CLEAN for written text**

        """
        # THE ENTRY (a transcription, a text...) IS A UTF8-STRING
        # -------------------------------------------------------
        _str = sppasUnicode(entry).to_strip()

        # Remove UTF-8 specific characters that are not in our dictionaries!
        try:
            for key in self.dicoutf.get_keys():
                _str = _str.replace(key, self.dicoutf.replace(key))
        except Exception as e:
            raise UnicodeError('Error during cleaning: %s'%str(e))

        # Enriched Orthographic Transcription
        # Create a faked spelling (default) or a standard spelling
        ortho = sppasTranscription()
        _str = ortho.clean_toe(_str)
        _str = ortho.toe_spelling(_str, std)

        # Step 1: split using spaces (or characters for asian languages)
        try:
            splitter = sppasTokSplitter(self.lang, self.repl)
            utt = splitter.split(_str, std)
        except Exception as e:
            raise Exception(" *in split* "+str(e))

        # THE ENTRY IS NOW A LIST OF STRINGS.
        # ---------------------------------------------------
        return self.tokenize_list(utt, std)
