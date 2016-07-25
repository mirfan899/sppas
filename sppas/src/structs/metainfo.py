#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: metainfo.py
# ----------------------------------------------------------------------------

import collections

# ----------------------------------------------------------------------------

class MetaInfo( object ):
    """
    @authors:      Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Meta information manager.

    Manage meta information of type (key,value) and allow to enable/disable
    each one.

    """
    def __init__(self):
        """
        Creates a new MetaInfo instance.

        """
        super(MetaInfo, self).__init__()
        self._metainfo = collections.OrderedDict()

    # ------------------------------------------------------------------------

    def is_active_metainfo(self, key):
        """
        Return the status of a given key or raise a KeyError exception.

        @param key (str)

        """
        if not str(key) in self._metainfo.keys():
            raise KeyError('%s is not a known meta information.'%key)

        return self._metainfo[key][0]

    # ------------------------------------------------------------------------

    def get_metainfo(self, key):
        """
        Return the value of a given key or raise a KeyError exception.

        @param key (str)

        """
        if not str(key) in self._metainfo.keys():
            raise KeyError('%s is not a known meta information.'%key)

        return self._metainfo[key][1]

    # ------------------------------------------------------------------------

    def activate_metainfo(self, key, value):
        """
        Activate/Disable a meta information or raise a KeyError exception.

        @param key (str)
        @param value (bool)

        """
        if not str(key) in self._metainfo.keys():
            raise KeyError('%s is not a known meta information.'%key)

        self._metainfo[str(key)][0] = bool(value)

    # ------------------------------------------------------------------------

    def add_metainfo(self, key, strv):
        """
        Fix a meta information or raise a KeyError exception.

        @param key (str)
        @param strv (str)

        """
        if str(key) in self._metainfo.keys():
            raise KeyError('%s is already a known meta information.'%key)

        self._metainfo[str(key)] = [True,strv]

    # ------------------------------------------------------------------------

    def pop_metainfo(self, key):
        """
        Pop a meta information or raise a KeyError exception.

        @param key (str)

        """
        if not str(key) in self._metainfo.keys():
            raise KeyError('%s is not a known meta information.'%key)

        del self._metainfo[str(key)]

    # ------------------------------------------------------------------------

    def keys_activated(self):
        """
        Return a list of the keys of activated meta information.

        """
        return [key for key in self._metainfo.keys() if self._metainfo[key][0] is True]

    # ------------------------------------------------------------------------
