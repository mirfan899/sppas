#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: tokenize.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import re

from num2letter         import sppasNum
from resources.wordslst import WordsList
from resources.dictrepl import DictRepl

import resources.rutils as rutils

# ---------------------------------------------------------------------------

class DictReplUTF8( DictRepl ):
    """
    Replacement dictionary of UTF8 characters that cause problems.
    """

    def __init__(self):
        DictRepl.__init__(self, dictfilename=None, nodump=True)

        self.add(u"æ",u"ae")
        self.add(u"œ",u"oe")
        self.add(u"，",u", ")
        self.add(u"”",u'"')
        self.add(u"“",u'"')
        self.add(u"。",u". ")
        self.add(u"》",u'"')
        self.add(u"《",u'"')
        self.add(u"«",u'"')
        self.add(u"»",u'"')
        self.add(u"’",u"'")

# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# DictTok main class
# ---------------------------------------------------------------------------


class DictTok:
    """
    @authors: Brigitte Bigi, Tatsuya Watanabe
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Tokenization automatic annotation.

    The creation of text corpora requires a sequence of processing steps in
    order to constitute, normalize, and then to directly exploit it by a given
    application. This class implements a generic approach for text normalization
    and concentrates on the aspects of methodology and linguistic engineering,
    which serve to develop a multi-purpose multilingual text corpus.
    This approach consists in splitting the text normalization problem in a set
    of minor sub-problems as language-independent as possible.

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

    See the whole description of the algorithm in the following reference:
        Brigitte Bigi (2011).
        A Multilingual Text Normalization Approach.
        2nd Less-Resourced Languages workshop,
        5th Language & Technology Conference, Poznan (Poland).

    """

    # ------------------------------------------------------------------


    def __init__(self, vocab=None, lang="und"):
        """
        Create a new DictTok instance.

        @param vocab (WordsList)
        @param lang is the language code in iso639-3.

        """
        # resources
        self.dicoutf = DictReplUTF8()
        self.repl    = DictRepl(None)
        self.punct   = WordsList(None)
        self.vocab   = vocab
        self.speech  = True   # transcribed speech (and not written text) is to be tokenized
        if vocab is None:
            self.vocab = WordsList(None)

        # members
        self.lang = lang
        self.num2letter = sppasNum( lang )
        self.delimiter = u' '

    # End __init__
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # Options
    # ------------------------------------------------------------------

    def set_delim(self, delim):
        """
        Set the delimiter, used to separate tokens.

        @param delim is a unicode character.

        """
        self.delimiter = delim

    # End set_delim
    # -------------------------------------------------------------------------


    def set_vocab(self,vocab):
        """
        Set the lexicon.

        @param vocab is a WordsList().

        """
        self.vocab = vocab

    # -------------------------------------------------------------------------


    def set_repl(self,repl):
        """
        Set the dictionary of replacements.

        @param repl (ReplDict)

        """
        self.repl = repl

    # -------------------------------------------------------------------------


    def set_punct(self,punct):
        """
        Set the list of punctuation.

        @param punct (WordsList)

        """
        self.punct = punct

    # -------------------------------------------------------------------------


    def set_lang(self,lang):
        """
        Set the language.

        @param lang is the language code in iso639-3 (fra, eng, vie, cmn...).

        """
        self.lang = lang

    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # Language independent modules
    # -------------------------------------------------------------------------

    def split_characters(self,utt):
        """
        Split an utterance by characters.

        @param utt is the utterance (a transcription, a sentence, ...) in utf-8
        @return A string (split character by character, using spaces)

        """
        try:
            y = unicode(utt, 'utf-8')
        except Exception:
            y = utt
        tmp =  " ".join( y )

        # split all characters except numbers and ascii characters
        sstr = re.sub(u"([０-９0-9a-zA-ZＡ-Ｔ\s]+\.?[０-９0-9a-zA-ZＡ-Ｔ\s]+)", lambda o: u" %s " % o.group(0).replace(" ",""), tmp)
        # and dates...
        if not self.speech:
            sstr = re.sub(u"([０-９0-9\s]+\.?[月年日\s]+)", lambda o: u" %s " % o.group(0).replace(" ",""), sstr)
        # and ・
        sstr = re.sub(u'[\s]*・[\s]*', u"・", sstr)
        return sstr


    def split(self, utt, std=False):
        """
        Split an utterance using spaces or split each character, depending
        on the language.

        @param utt (string): the utterance (a transcription, a sentence, ...)
        @param std (Boolean)

        @return A list (array of string)

        """

        s = utt
        if self.lang == "cmn" or self.lang == "jpn" or self.lang == "yue":
            s = self.split_characters( s )

        toks = s.split()
        s = ""
        for t in toks:
            if not "/" in t: #if not a phonetized entry
                if std is False:
                    if self.lang != "cmn" and self.lang != "jpn" and self.lang != "yue":
                        # Split numbers if sticked to characters
                        # attention: do not replace [a-zA-Z] by [\w] (because \w includes numbers)
                        # and not on asian languages: it can be a tone!
                        s = re.sub(u'([0-9])([a-zA-Z])', ur'\1 \2', s)
                        s = re.sub(u'([a-zA-Z])([0-9])', ur'\1 \2', s)

                # Split some punctuation
                s = re.sub(u'\\[\\]', ur'\\] \\[', s)

                # Split dots if sticked to a word
                s = re.sub(u' \.([\w-])', ur'. \1', s)
                s = re.sub(u'^\.([\w-])', ur'. \1', s)

        s = " ".join(toks)

        # Then split each time there is a space and return result
        s = rutils.ToStrip( s )

        return s.split()

    # End split
    # ------------------------------------------------------------------


    def __stick_longest(self, utt, attachement = "_"):
        """ Longest matching algorithm. """
        tabtoks = utt.split(" ")
        i = len(tabtoks)
        while i>0:
            # try to stick all tokens
            _token = attachement.join(tabtoks)
            if self.vocab.is_unk(_token) is False:
                return (i,_token)
            tabtoks.pop()
            i -= 1
        return (1,utt.split(" ")[0])


    def stick(self, utt, attachement = "_"):
        """
        Stick tokens of an utterance using '_'.
        Language independent.

        @param utt (list) the utterance (a transcription, a sentence, ...)
        @return A list of strings

        """
        _utt = []
        t1 = 0
        while t1<len(utt):
            sl = utt[t1] # longest string ... in theory!
            lmax = t1+7
            if lmax>len(utt):
                lmax = len(utt)
            for t2 in range(t1+1,lmax):
                sl = sl + " " + utt[t2]
            (i,tok) = self.__stick_longest( rutils.ToStrip( sl ), attachement) # real longest string!
            t1 += i
            _utt.append( rutils.ToStrip( tok ) )

        return _utt

    # End stick
    # ------------------------------------------------------------------


    def replace(self, utt):
        """
        Examine tokens and performs some replacements.
        A dictionary with symbols contains the replacements to operate.

        This method also includes language specific replacements.
        Supported languages are: fra, cmn, jpn, yue, eng, ita, spa, khm, cat, pol.

        @param utt (list) the utterance

        @return A list of strings

        """
        # Specific case of float numbers
        sent = ' '.join(utt)
        sent = re.sub(u'([0-9])\.([0-9])', ur'\1 NUMBER_SEP_POINT \2', sent)
        sent = re.sub(u'([0-9])\,([0-9])', ur'\1 NUMBER_SEP \2', sent)
        sent = rutils.ToStrip( sent )
        _utt = sent.split()

        # Other generic replacements
        _result = []
        for s in _utt:
            if self.repl.is_key( s ):
                s = s.replace(s, self.repl.replace(s))
            _result.append(rutils.ToStrip( s ))

        return _result

    # End replace
    # -----------------------------------------------------------------------


    def compound(self, utt):
        """
        Examine tokens containing - or ' and split depending on rules.
        Language independent.

        @param utt (list) the utterance
        @return A list of strings

        """
        _utt = []
        for tok in utt:
            # a missing compound word?
            #   --> an unknown token
            #   --> containing a special character
            #   --> that is not a truncated word!
            if self.vocab.is_unk(tok.lower().strip()) is True and (tok.find("-")>-1 or tok.find("'")>-1 or tok.find(".")>-1) and not tok.endswith('-'):
                # Split the unknown token into a list
                # KEEP special chars ('-.) in the array!
                _tabtoks = re.split("([-'.])",tok)

                # Explore the list from left to right
                t1 = 0
                while t1<len(_tabtoks):
                    i = len(_tabtoks)
                    i_ok = 0
                    # Find the longest string in the dict
                    while i>=t1 and i_ok==0:
                        _token = _tabtoks[t1]
                        if i > (t1+1):
                            for j in range(t1+1,i):
                                _token += _tabtoks[j]
                            if self.vocab.is_unk(_token) is False:
                                i_ok = j+1
                        else:
                            i_ok = 1
                            _token = _tabtoks[t1]
                        i -= 1
                    t1 += i_ok
                    _utt.append( rutils.ToStrip( _token ))

            else:
                _utt.append( rutils.ToStrip( tok ))

        return _utt

    # End compound
    # ------------------------------------------------------------------


    def lower(self, utt ):
        """
        Lower a list of strings.

        @param utt (list)

        """
        _utt = []
        for tok in utt:
            if "/" not in tok:
                _utt.append( rutils.ToLower( tok ))
            else:
                _utt.append( tok )

        return _utt

    # End lower
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
                _utt.append( tok )

        return _utt

    # End remove
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # EOT specific modules
    # ------------------------------------------------------------------

    def __repl(self, obj):
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

        entry = re.sub(ur'\s*\[([^,]+),([^,]+)\]', self.__repl, entry, re.UNICODE)
        return " ".join(entry.split())

    # End clean_toe and __repl
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
        _fentry = " " + unicode(entry) + " "

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
        _fentry = re.sub(u' \\([\s\w\xaa-\xff\-:]+\\) ', ur'', _fentry, re.UNICODE) # .... warning!

        if std is False:
            # Special elisions (remove parenthesis content)
            _fentry = re.sub(u'\\([\s\w\xaa-\xff\-\']+\\)', ur'', _fentry, re.UNICODE)
        else:
            # Special elisions (keep parenthesis content)
            _fentry = re.sub(u'\\(([\s\w\xaa-\xff\-]+)\\)', ur'\1', _fentry, re.UNICODE)

        # Morphological variants are ignored for phonetization (same pronunciation!)
        _fentry = re.sub(u'\s+\\<([\-\'\s\w\xaa-\xff]+),[\-\'\s\w\xaa-\xff]+\\>', ur' \1', _fentry, re.UNICODE)
        _fentry = re.sub(u'\s+\\{([\-\'\s\w\xaa-\xff]+),[\-\'\s\w\xaa-\xff]+\\}', ur' \1', _fentry, re.UNICODE)
        _fentry = re.sub(u'\s+\\/([\-\'\s\w0-9\xaa-\xff]+),[\-\'\s\w0-9\xaa-\xff]+\\/', ur' \1', _fentry, re.UNICODE)

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
        _fentry = re.sub(u'([\w\xaa-\xff]+)\)', ur'\1 )', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\{', ur'\1 {', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\}', ur'\1 }', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)=', ur'\1 =', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\?', ur'\1 ?', _fentry, re.UNICODE)
        _fentry = re.sub(u'([\w\xaa-\xff]+)\!', ur'\1 !', _fentry, re.UNICODE)
        #_fentry = re.sub(u'([\w\xaa-\xff]+)\/', ur'\1 !', _fentry, re.UNICODE) # no: if sampa in special pron.
        _fentry = re.sub(u"\s(?=,[0-9]+)", "" , _fentry, re.UNICODE)

        # Correction of errors
        s = ""
        inpron=False
        for c in _fentry:
            if c == "/":
                inpron = not inpron
            else:
                if c == " " and inpron is True:
                    continue
            s += c
        return rutils.ToStrip(s)

    # End toe_spelling
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # The main tokenize is HERE!
    # ------------------------------------------------------------------

    def tokenize_list(self, utt, std=False):
        """
        Tokenize from a list of entries.
        """
        # Step 2: replace
        try:
            utt = self.replace( utt )
        except IOError:
            # repl file not found
            pass
        except Exception as e:
            raise Exception(" *in replace* "+str(e)+'\n')

        # Step 3: compound
        try:
            utt = self.compound( utt )
        except Exception as e:
            raise Exception(" *in compound* "+str(e)+'\n')

        # Step 4: stick (using the dictionary)
        try:
            attachement = "_"
            if (self.lang=="cmn" or self.lang == "jpn" or self.lang == "yue"):
                attachement = ""
            utt = self.stick( utt,attachement )
        except Exception as e:
            raise Exception(" *in stick* "+str(e)+'\n')


        # Step 5: num2letter
        try:
            _utt = []
            for i in utt:
                if not "/" in utt:
                    _utt.append( self.num2letter.convert( i ) )
                else:
                    _utt.append( i )
            utt = _utt
        except Exception as e:
            pass

        # Step 6: lower
        try:
            utt = self.lower( utt )
        except Exception as e:
            raise Exception(" *in lower* "+str(e)+'\n')

        # Step 7: remove (punctuation)
        try:
            utt = self.remove( utt,self.punct )
        except Exception as e:
            raise Exception(" *in remove* "+str(e)+'\n')

        # Finally, prepare the result
        strres = ""
        for s in utt:
            s = rutils.ToStrip( s )
            strres = strres + u" " + s.replace(u" ",u"_")

        strres = rutils.ToStrip(strres)
        if len(strres)==0:
            return "#"   # or "dummy" ???

        return strres.replace(u" ", self.delimiter)




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
        _str = rutils.ToStrip( entry )

        # Remove UTF-8 specific characters that are not in our dictionaries!
        try:
            for key in self.dicoutf.get_keys():
                _str = _str.replace( key, self.dicoutf.replace(key) )
        except Exception as e:
            raise UnicodeError('Error during cleaning: %s'%str(e))

        # Enriched Orthographic Transcription
        # Create a faked spelling (default) or a standard spelling
        _str = self.clean_toe(_str)
        _str = self.toe_spelling(_str, std)

        # Step 1: split using spaces (or characters for asian languages)
        try:
            utt = self.split( _str, std )
        except Exception as e:
            raise Exception(" *in split* "+str(e))

        # THE ENTRY IS NOW A LIST OF STRINGS.
        # ---------------------------------------------------
        return self.tokenize_list(utt, std)

    # End tokenize
    # ------------------------------------------------------------------------

# End DictTok
# ---------------------------------------------------------------------------
