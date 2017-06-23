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

    src.annotations.language.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


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
