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
# File: prefs.py
# ----------------------------------------------------------------------------

import logging
import codecs
import pickle

from option import Option
from themes import BaseTheme

# ----------------------------------------------------------------------------

class Preferences:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      This class is used to manage a dictionary of settings.

    """
    def __init__(self, theme=None):
        """
        Constructor.

        Creates a dict of Option() instances, with option id as key.

        """
        self._prefs = {}

        # Set the requested theme.
        if theme is None:
            self.SetTheme( BaseTheme() )
        else:
            self.SetTheme( theme )

    # ------------------------------------------------------------------------
    # Getters and Setters
    # ------------------------------------------------------------------------

    def GetValue(self, key):
        """ Return the typed-value of the given key. """

        return self._prefs[key].get_value()

    # ------------------------------------------------------------------------

    def SetValue(self, key, t=None, v=None, text=''):
        """ Set a new couple key/(type,typed-value,text). """

        if not key in self._prefs:
            self._prefs[key] = Option(optiontype=t, optionvalue=v, optiontext=text)

        self._prefs[key].set_value(v)

    # ------------------------------------------------------------------------

    def SetOption(self, key, option):
        """ Set a new couple key/Option. """

        self._prefs[key] = option

    # ------------------------------------------------------------------------

    def GetTheme(self):
        """ Return the the current theme. """

        return self._prefs.get('THEME', None)

    # ------------------------------------------------------------------------

    def SetTheme(self, theme):
        """ Set a new theme. """

        self._prefs['THEME'] = theme
        for key in theme.get_keys():
            opt = theme.get_choice(key)
            if opt is not None:
                self.SetOption(key, opt)

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class Preferences_IO( Preferences ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Input/Output preferences.

    """
    def __init__(self, filename=None):
        """ Create a new dictionary of preferences. """

        Preferences.__init__(self)
        self._filename = filename

    # ------------------------------------------------------------------------

    def HasFilename(self):
        """
        Return True is a file name was defined.

        """
        if self._filename is None: return False
        return True

    # ------------------------------------------------------------------------

    def Read(self):
        """
        Read user preferences from a file.
        Return True if preferences have been read.

        """
        try:
            with codecs.open(self._filename, mode="rb") as f:
                prefs = pickle.load(f)
        except Exception:
            return False

        self._prefs = prefs
        return True

    # ------------------------------------------------------------------------

    def Write(self):
        """
        Save user preferences into a file.
        Return True if preferences have been saved.

        """
        if self._filename is None:
            return False

        try:
            with codecs.open(self._filename, mode="wb") as f:
                pickle.dump(self._prefs, f, pickle.HIGHEST_PROTOCOL)
        except Exception:
            return False

        return True

    # ------------------------------------------------------------------------

    def Copy(self):
        """
        Return a deep copy of self.

        """
        #import copy
        #return copy.deepcopy( self._prefs ) -->
        #BUG: TypeError: object.__new__(PySwigObject) is not safe, use PySwigObject.__new__()

        cpref = Preferences_IO()

        for key in self._prefs.keys():
            if key == 'THEME':
                cpref.SetTheme( self._prefs[key] )
            else:
                t   = self._prefs[key].get_type()
                v   = self._prefs[key].get_untypedvalue()
                txt = self._prefs[key].get_text()
                opt = Option(t,v,txt)
                cpref.SetOption(key, opt)

        return cpref

# ----------------------------------------------------------------------------
