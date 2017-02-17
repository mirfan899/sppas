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

    makeunicode is useful for the compatibility of strings
    between python 2.7 and python > 3.2.

"""
from __future__ import unicode_literals
import sys
import codecs
import re

from sppas.src.sp_glob import encoding

# ---------------------------------------------------------------------------

""" Unicode conversion for python 2.7. """

if sys.version_info < (3,):

    text_type = unicode
    binary_type = str

    def u(x):
        return x.decode(encoding)
        # return codecs.unicode_escape_decode(x)[0]

    def b(x):
        return x.encode(encoding)

else:
    """ Unicode conversion for python > 3. """

    text_type = str
    binary_type = bytes

    def u(x):
        return x

    def b(x):
        return codecs.encode(x, encoding, errors='strict')
        #return codecs.utf_8_encode(x)[0]

# ---------------------------------------------------------------------------


class sppasUnicode(object):

    def __init__(self, entry):
        """ Unicode maker for SPPAS.

        :param entry: (str or unicode or bytes)

        """
        self._entry = entry

    # -----------------------------------------------------------------------

    def to_lower(self):
        """ Return the unicode string with lower case.

        :returns: unicode

        """
        e = self._entry
        if isinstance(self._entry, binary_type):
            e = u(self._entry)

        self._entry = e.lower()
        return self._entry

    # -----------------------------------------------------------------------

    def to_strip(self):
        """ Strip the string.
        Remove also multiple spaces inside the string.

        :returns: unicode

        """
        e = self._entry
        if isinstance(self._entry, binary_type):
            e = u(self._entry)

        # Remove multiple spaces
        __str = re.sub("[\s]+", r" ", e)
        # Remove spaces at beginning and end
        __str = re.sub("^[ ]+", r"", __str)
        __str = re.sub("[ ]+$", r"", __str)
        __str = re.sub("\ufeff", r"", __str)

        self._entry = __str
        return self._entry

    # ----------------------------------------------------------------------------

    def clear_whitespace(self):
        """ Replace the whitespace by underscores.

        :returns: unicode

        """
        e = self.to_strip()
        # Replace spaces by underscores
        e = re.sub('\s', r'_', e)
        self._entry = e
        return self._entry

    # ------------------------------------------------------------------------

    def to_ascii(self):
        """ Replace the non-ASCII characters by underscores.

        :returns: unicode

        """
        e = self._entry
        if isinstance(self._entry, binary_type):
            e = u(self._entry)

        e = re.sub(r'[^\x00-\x7F]', "_", e)
        self._entry = e
        return self._entry

    # ------------------------------------------------------------------------
