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

    src.structs.metainfo.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    Meta-information is a sorted collection of pairs (key, value) where
    value is a tuple with first argument of type boolean to indicate the
    state of the key: enabled/disabled.

"""
import collections

# ----------------------------------------------------------------------------


class sppasMetaInfo(object):
    """
    :authors:      Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Meta information manager.

    Manage meta information of type (key,value) and allow to enable/disable
    each one.

    >>> m = sppasMetaInfo()
    >>> m.add_metainfo('author', 'Brigitte Bigi')
    >>> m.add_metainfo('version', (1,8,2))

    """
    def __init__(self):
        """ Creates a new MetaInfo instance. """

        super(sppasMetaInfo, self).__init__()
        self._metainfo = collections.OrderedDict()

    # ------------------------------------------------------------------------

    def is_active_metainfo(self, key):
        """ Return the status of a given key or raise a KeyError exception.

        :param key (str)

        """
        if str(key) not in self._metainfo:
            raise KeyError('%s is not a known meta information.' % key)

        return self._metainfo[key][0]

    # ------------------------------------------------------------------------

    def get_metainfo(self, key):
        """ Return the value of a given key or raise a KeyError exception.

        :param key (str)

        """
        if str(key) not in self._metainfo:
            raise KeyError('%s is not a known meta information.' % key)

        return self._metainfo[key][1]

    # ------------------------------------------------------------------------

    def activate_metainfo(self, key, value=True):
        """ Activate/Disable a meta information or raise a KeyError exception.

        :param key (str)
        :param value (bool)

        """
        if str(key) not in self._metainfo.keys():
            raise KeyError('%s is not a known meta information.' % key)

        self._metainfo[str(key)][0] = bool(value)

    # ------------------------------------------------------------------------

    def add_metainfo(self, key, strv):
        """ Fix a meta information or raise a KeyError exception.
        The meta information is then activated.

        :param key (str)
        :param strv (str)

        """
        if str(key) in self._metainfo.keys():
            raise KeyError('%s is already a known meta information.' % key)

        self._metainfo[str(key)] = [True, strv]

    # ------------------------------------------------------------------------

    def pop_metainfo(self, key):
        """ Pop a meta information or raise a KeyError exception.

        :param key (str)

        """
        if str(key) not in self._metainfo.keys():
            raise KeyError('%s is not a known meta information.' % key)

        del self._metainfo[str(key)]

    # ------------------------------------------------------------------------

    def keys_activated(self):
        """ Return a list of the keys of activated meta information.

        :returns: list of str

        """
        return [key for key in self._metainfo.keys() if self._metainfo[key][0] is True]

    # ------------------------------------------------------------------------

    def __len__(self):
        return len(self._metainfo)

    # ------------------------------------------------------------------------
