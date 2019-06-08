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

from .num_europ_lang import sppasNumEuropeanType

# ---------------------------------------------------------------------------


class sppasNumSpanish(sppasNumEuropeanType):
    """Return an instance of sppasNumSpanish

    :returns: (sppasNumSpanish)

    """
    def __init__(self, dictionary):
        NUMBER_LIST = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                       11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                       21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                       40, 50, 60, 70, 80, 90, 100, 1000, 1000000, 1000000000)
        super(sppasNumSpanish, self).__init__('spa', dictionary)
        self.separator = "-"

    # ---------------------------------------------------------------------------

    def _tenth(self, number):
        """Return the "wordified" version of a tenth number.

        Returns the word corresponding to the given tenth within the current
        language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if 30 < number < 100:
            if int(str(number)[1:]) == 0:
                return self._lang_dict[str(number)]
            else:
                return self._lang_dict[str(int(number / 10) * 10)] \
                       + self.separator \
                       + 'y' \
                       + self.separator \
                       + self._units(number % 10)

        return super(sppasNumSpanish, self)._tenth(number)

    # ---------------------------------------------------------------------------

    def _hundreds(self, number):
        """Return the "wordified" version of a hundred number.

        Returns the word corresponding to the given hundred number within the
        current language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number < 100:
            return self._tenth(number)
        else:
            mult = None
            if int(str(number)[0])*100 != 100:
                mult = self._units(int(number/100))

            if mult is not None:
                return mult + self._lang_dict['100'] \
                       + 's' \
                       + self.separator \
                       + self._tenth(number % 100)

        return super(sppasNumSpanish, self)._hundreds(number)

    # ---------------------------------------------------------------------------

    def _thousands(self, number):
        """Return the "wordified" version of a thousand number.

        Returns the word corresponding to the given thousand number within the
        current language dictionary

        :param number: (int) number to convert in word
        :returns: (str)

        """
        if number < 1000:
            return self._tenth(number)
        else:
            mult = None
            if number / 1000 * 1000 != 1000:
                mult = self._hundreds(int(number / 1000))

            if mult is not None:
                return mult + 'milliones' \
                       + self.separator \
                       + self._tenth(number % 1000)

        return super(sppasNumSpanish, self)._thousands(number)

# ---------------------------------------------------------------------------
