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

    src.anndata.metadata.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
from collections import OrderedDict

from sppas.src.utils.makeunicode import sppasUnicode

# ---------------------------------------------------------------------------


class sppasMetaData(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Dictionary of meta data.

    Meta data keys and values are unicode strings.

    """
    def __init__(self):
        self.__metadata = OrderedDict()

    # ------------------------------------------------------------------------

    def is_meta_key(self, entry):
        """ Check if an entry is a key in the list of metadata.

        :param entry: (str) Entry to check
        :return: (Boolean)

        """
        return entry in self.__metadata

    # ------------------------------------------------------------------------

    def get_meta(self, key):
        """ Return the value of the given key.
        Return an empty string if key if not a key of metadata.

        :param key: (str)

        """
        return self.__metadata.get(key, "")

    # ------------------------------------------------------------------------

    def get_meta_keys(self):
        """ Return the list of metadata keys. """

        return self.__metadata.keys()

    # ------------------------------------------------------------------------

    def set_meta(self, key, value):
        """ Set or update a tuple key/value of metadata.

        :param key: (str)
        :param value: (str)

        """
        su = sppasUnicode(key)
        key = su.to_strip()

        su = sppasUnicode(value)
        value = su.to_strip()

        self.__metadata[key] = value

    # ------------------------------------------------------------------------

    def pop_meta(self, key):
        """ Remove a metadata from its key.

        :param key: (str)

        """
        if key in self.__metadata:
            del self.__metadata[key]
