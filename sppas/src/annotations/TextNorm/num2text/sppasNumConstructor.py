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
"""
from sppasNumJapanese import sppasNumJapanese
from sppasNumFrench import sppasNumFrench
from sppasNumEnglish import sppasNumEnglish
from sppasNumSpanish import sppasNumSpanish
from sppasNumPolish import sppasNumPolish
from sppasNumItalian import sppasNumItalian
from sppasNumKhmer import sppasNumKhmer
from sppasNumPortuguese import sppasNumPortuguese
from sppasNumVietnamese import sppasNumVietnamese
from sppasNumAsianType import sppasNumAsianType
from sppasNumUnd import sppasNumUnd

from sppas import sppasValueError, sppasTypeError


# ---------------------------------------------------------------------------


class sppasNumConstructor(object):

    def __init__(self):
        pass

    # ---------------------------------------------------------------------------

    @staticmethod
    def construct(lang=None, dictionary=None):
        """Return an instance of the correct object regarding the given language

        :returns: (sppasNumBase)

        """
        if lang is not None and not isinstance(lang, str):
            raise sppasTypeError(lang, str)

        ASIAN_TYPED_LANGUAGES = ("yue", "cmn", "pcm")

        LANGUAGES_DICT = {
                          "und": sppasNumUnd,
                          "yue": sppasNumAsianType,
                          "cmn": sppasNumAsianType,
                          "fra": sppasNumFrench,
                          "ita": sppasNumItalian,
                          "eng": sppasNumEnglish,
                          "spa": sppasNumSpanish,
                          "khm": sppasNumKhmer,
                          "vie": sppasNumVietnamese,
                          "jpn": sppasNumJapanese,
                          "pol": sppasNumPolish,
                          "por": sppasNumPortuguese,
                          "pcm": sppasNumAsianType
                          }

        if lang is None or lang.lower() in LANGUAGES_DICT.keys():
            if lang is None:
                return sppasNumUnd()
            elif lang not in ASIAN_TYPED_LANGUAGES:
                return LANGUAGES_DICT[lang](dictionary)
            else:
                return LANGUAGES_DICT[lang](lang, dictionary)
        else:
            raise sppasValueError(lang, LANGUAGES_DICT.keys())

# ---------------------------------------------------------------------------
