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
import os

import sppas
from sppas import sppasValueError, u

# ---------------------------------------------------------------------------


class Dictionary(object):
    """Return an instance of a Dictionary

    :returns: (Dictionary)

    """

    def __init__(self, lang=None):
        super(Dictionary, self).__init__()

        if not isinstance(lang, str):
            raise sppasValueError(lang, str)

        if lang is not None:
            self._lang_dict = list()
            with open(os.path.join(sppas.paths.resources, 'num', lang + '_num.repl')) as language_dict:
                self._lang_dict = language_dict.readlines()

            for i in range(len(self._lang_dict)):
                number, word = self._lang_dict[i].split()
                self._lang_dict[i] = (int(number), u(word))

    # ---------------------------------------------------------------------------
    # Override
    # ---------------------------------------------------------------------------

    def __iter__(self):
        for item in self._lang_dict:
            yield item

    def __getitem__(self, i):
        return self._lang_dict[i]
