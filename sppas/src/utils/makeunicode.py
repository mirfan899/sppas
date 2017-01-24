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

    src.utils.makeunicode
    ~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    makeunicode is useful for the compatibility of the code between python 2.7
    and python > 3.

"""
from __future__ import unicode_literals
import sys
import codecs

# ---------------------------------------------------------------------------

""" Unicode conversion for python 2.7. """

if sys.version_info < (3,):

    text_type = unicode
    binary_type = str

    def u(x):
        return codecs.unicode_escape_decode(x)[0]

    def b(x):
        return x

else:
    """ Unicode conversion for python > 3. """

    text_type = str
    binary_type = bytes

    def u(x):
        return x

    def b(x):
        return codecs.latin_1_encode(x)[0]
