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

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import logging
import codecs
import pickle
import wx

from option import Option
from themes import Themes, BaseTheme

# ----------------------------------------------------------------------------


class Preferences:
    """
    Manage a dictionary with user's preferences.

    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: This class is used to manage a dictionary of settings.

    """

    def __init__(self, theme=None):
        """
        Constructor.

        Creates a dict of Option() instances, with option id as key.

        """
        self._prefs = {}
        self.SetDefault()

        # Set a default theme to assign values in the dictionary.
        if theme is not None:
            self.SetTheme( theme )
        else:
            self.SetTheme( BaseTheme() )

    # End __init__
    # ------------------------------------------------------------------------



    # ------------------------------------------------------------------------
    # Getters and Setters
    # ------------------------------------------------------------------------


    def SetDefault(self):
        """
        Fix the default settings for SPPAS.
        """
        self.SetValue( 'M_FG_COLOUR',   t='wx.Colour', v=wx.Colour(10,10,10), text='Main frame foreground color')
        self.SetValue( 'M_FONT_COLOUR', t='wx.Colour', v=wx.Colour(10,10,10), text='Main frame foreground color')
        self.SetValue( 'M_BG_COLOUR',   t='wx.Colour', v=wx.Colour(245,245,245), text='Main frame background color')
        self.SetValue( 'M_FONT',        t='wx.Font',   v=wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_SYSTEM), text='Main frame font')

    # End SetDefault
    # ------------------------------------------------------------------------


    def GetValue(self, key):
        """ Return the typed-value of the given key. """

        return self._prefs[key].get_value()

    # End GetValue
    # ------------------------------------------------------------------------


    def SetValue(self, key, t=None, v=None, text=''):
        """ Set a new couple key/(type,typed-value,text). """

        if not key in self._prefs:
            self._prefs[key] = Option(optiontype=t, optionvalue=v, optiontext=text)

        self._prefs[key].set_value(v)

    # End SetValue
    # ------------------------------------------------------------------------


    def SetOption(self, key, option):
        """ Set a new couple key/Option. """

        self._prefs[key] = option

    # End SetOption
    # ------------------------------------------------------------------------


    def GetTheme(self):
        """ Return the the current theme. """

        return self._prefs.get('THEME', None)

    # End GetTheme
    # ------------------------------------------------------------------------


    def SetTheme(self, theme):
        """ Set a new theme. """

        logging.debug('Set to a new theme.')

        self._prefs['THEME'] = theme
        for key in theme.get_keys():
            opt = theme.get_choice(key)
            if opt is not None:
                self.SetOption(key, opt)

    # End SetTheme
    # ------------------------------------------------------------------------


# ----------------------------------------------------------------------------


class Preferences_IO( Preferences ):
    """
    Input/Output preferences.

    @author: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL,v3
    @summary: This class is used to manage a file of settings.

    """

    def __init__(self, filename=None):
        """ Create a new dictionary of preferences. """

        Preferences.__init__(self)
        self._filename = filename

        logging.info('Settings file name is: %s'%self._filename)

    # End __init__
    # ------------------------------------------------------------------------


    def HasFilename(self):
        """
        Return True is a file name was defined.
        """

        if self._filename is None: return False
        return True

    # End HasFilename
    # ------------------------------------------------------------------------


    def Read(self):
        """
        Read user preferences from a file.
        Return True if preferences have been read.
        """

        try:
            with codecs.open(self._filename, mode="rb") as f:
                prefs = pickle.load(f)
        except Exception as e:
            logging.debug('Preferences NOT read, error: %s'%str(e))
            return False

        self._prefs = prefs
        logging.debug('Settings read successfully')
        return True

    # End Read
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
        except Exception as e:
            logging.debug('Preferences NOT saved, error: %s'%str(e))
            return False

        logging.debug('Settings saved successfully.')
        return True

    # End Write
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

    # End Copy
    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------
