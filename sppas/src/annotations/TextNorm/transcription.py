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

    src.annotations.transcription.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Module managing the orthographic transcription for the multilingual text
    normalization system.

"""
import re

from sppas.src.utils.makeunicode import u, sppasUnicode

# ---------------------------------------------------------------------------


class sppasTranscription(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Manager of orthographic transcription.

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
        return " [{:s},{:s}]".format(left, right)

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
