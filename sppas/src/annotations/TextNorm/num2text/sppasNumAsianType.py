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

from sppasNumBase import sppasNumBase

from sppas import sppasValueError


class sppasNumAsianType(sppasNumBase):

    ASIAN_TYPED_LANGUAGES = ("yue", "cmn", "jpn", "pcm")

    def __init__(self, lang=None, dictionary=None):
        """Return an instance of sppasNumAsianType

        :param lang: (str) name of the language

        """
        if lang in self.ASIAN_TYPED_LANGUAGES:
            super(sppasNumAsianType, self).__init__(lang, dictionary)
        else:
            raise sppasValueError(lang, sppasNumAsianType.ASIAN_TYPED_LANGUAGES)

    def _tenth_of_thousands(self, number):
        """Return the "wordified" version of a tenth of a thousand number

        Returns the word corresponding to the given tenth of a thousand number
        within the current language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number < 10000:
            return self._thousands(number)
        else:
            mult = None
            if int(number/10000)*10000 != 10000:
                mult = self._thousands(int(number/10000))

            for item in self._lang_dict:
                if item[0] == 10000:
                    if mult is None:
                        if int(str(number)[1:]) == 0:
                            return item[1]
                        else:
                            return item[1] + self._thousands(number % 10000)
                    else:
                        if int(str(number)[1:]) == 0:
                            return mult + item[1]
                        else:
                            return mult + item[1] + self._thousands(number % 10000)

    def _billions(self, number):
        """Return the "wordified" version of a billion number

        Returns the word corresponding to the given billion number within the
        current language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number < 100000000:
            return self._tenth_of_thousands(number)
        else:
            mult = None
            if int(number/100000000)*100000000 != 100000000:
                mult = self._thousands(int(number/100000000))

            for item in self._lang_dict:
                if item[0] == 100000000:
                    if mult is None:
                        if int(str(number)[1:]) == 0:
                            return item[1]
                        else:
                            return item[1] \
                                   + self._tenth_of_thousands(number % 100000000)
                    else:
                        if int(str(number)[1:]) == 0:
                            return mult + item[1]
                        else:
                            return mult + item[1] \
                                   + self._tenth_of_thousands(number % 100000000)
