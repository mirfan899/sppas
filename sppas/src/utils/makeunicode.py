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

    makeunicode is useful for the compatibility of strings between
    Python 2.7 and Python > 3.2.

"""
from __future__ import unicode_literals
import sys
import codecs
import re

from sppas import encoding

# ---------------------------------------------------------------------------

""" Unicode conversion for Python 2.7. """

if sys.version_info < (3,):

    text_type = unicode
    binary_type = str

    def u(x):
        return x.decode(encoding)
        # return codecs.unicode_escape_decode(x)[0]

    def b(x):
        return x

else:
    """ Unicode conversion for Python > 3.2 """

    text_type = str
    binary_type = bytes

    def u(x):
        return x

    def b(x):
        return codecs.encode(x, encoding, errors='strict')
        # return codecs.utf_8_encode(x)[0]

# ---------------------------------------------------------------------------


class sppasUnicode(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Make unicode strings.

    """
    def __init__(self, entry):
        """ Unicode maker for SPPAS.

        :param entry: (str or unicode or bytes)

        """
        self._entry = entry

    # -----------------------------------------------------------------------

    def unicode(self):
        """ Return the unicode string of the given entry.

        :returns: unicode

        """
        e = self._entry
        if isinstance(self._entry, binary_type):
            e = u(self._entry)
        return e

    # -----------------------------------------------------------------------

    def to_lower(self):
        """ Return the unicode string with lower case.

        :returns: unicode

        """
        e = self.unicode()
        self._entry = e.lower()

        return self._entry

    # -----------------------------------------------------------------------

    def to_strip(self):
        """ Strip the string.
        Remove also multiple whitespace, tab and CR inside the string.

        :returns: unicode

        """
        # Remove multiple whitespace
        e = self.unicode()
        __str = re.sub("[\s]+", r" ", e)

        # Remove whitespace at beginning and end
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
        e = re.sub('\s', r'_', e)
        self._entry = e

        return self._entry

    # ------------------------------------------------------------------------

    def to_ascii(self):
        """ Replace the non-ASCII characters by underscores.

        :returns: unicode

        """
        e = self.unicode()
        e = re.sub(r'[^\x00-\x7F]', "_", e)
        self._entry = e

        return self._entry
