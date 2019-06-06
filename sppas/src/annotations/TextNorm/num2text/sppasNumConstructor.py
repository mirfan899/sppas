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

from sppas import sppasValueError, sppasTypeError

from .sppasNumJapanese import sppasNumJapanese
from .sppasNumFrench import sppasNumFrench
from .sppasNumSpanish import sppasNumSpanish
from .sppasNumItalian import sppasNumItalian
from .sppasNumKhmer import sppasNumKhmer
from .sppasNumVietnamese import sppasNumVietnamese

from .sppasNumAsianType import sppasNumAsianType
from .sppasNumUnd import sppasNumUnd
from .sppasNumEuropeanType import sppasNumEuropeanType

# ---------------------------------------------------------------------------


class sppasNumConstructor(object):

    ASIAN_TYPED_LANGUAGES = ("yue", "cmn", "pcm")

    LANGUAGES_DICT = {
        "und": sppasNumUnd,
        "fra": sppasNumFrench,
        "ita": sppasNumItalian,
        "spa": sppasNumSpanish,
        "khm": sppasNumKhmer,
        "vie": sppasNumVietnamese,
        "jpn": sppasNumJapanese,
        "yue": sppasNumAsianType,
        "cmn": sppasNumAsianType,
        "pcm": sppasNumAsianType,
        "eng": sppasNumEuropeanType,
        "pol": sppasNumEuropeanType,
        "por": sppasNumEuropeanType
    }

    # ---------------------------------------------------------------------------

    @staticmethod
    def construct(lang=None, dictionary=None):
        """Return an instance of the correct object regarding the given language

        :returns: (sppasNumBase)

        """
        if lang is not None and isinstance(lang, str) is False:  # basestring, str, unicode
            raise sppasTypeError(lang, "string")

        if lang is None:
            return sppasNumUnd()

        if lang.lower() in sppasNumConstructor.LANGUAGES_DICT.keys():
            constructor = sppasNumConstructor.LANGUAGES_DICT[lang]
            try:
                instance = constructor(dictionary)
            except:
                instance = constructor(lang, dictionary)
            return instance

        raise sppasValueError(lang, sppasNumConstructor.LANGUAGES_DICT.keys())
