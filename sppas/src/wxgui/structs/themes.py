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
# File: themes.py
# ----------------------------------------------------------------------------

import wx

from wxgui.structs.wxoption import wxOption
from wxgui.sp_consts import MAIN_FONTSIZE


# ----------------------------------------------------------------------------
# Class to store a set of themes (name/class)
# ----------------------------------------------------------------------------

class Themes:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:     This class is used to store all themes (name/class).

    """
    def __init__(self):
        """
        Constructor.

        A Theme is a dictionary with key/option.

        """
        self._themes = {}

    # -----------------------------------------------------------------------

    def get_theme(self, key):
        """ Return a value from its key. """

        if not key in self._themes.keys():
            return None

        return self._themes[key]

    # -----------------------------------------------------------------------

    def get_themes(self):
        """ Return the dictionary with all pairs key/value. """

        return self._themes

    # -----------------------------------------------------------------------

    def add_theme(self, key, value):
        """ Add a pair key/value. """

        #if not key in self._themes.keys():
        self._themes[key] = value
        #raise KeyError('This theme is already in the set of known themes.')

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Base class for a theme.
# ----------------------------------------------------------------------------

class Theme:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:     Base class: A theme store all preferences for the colors, fonts, etc...

    """

    def __init__(self):
        """ A Theme is a dictionary with key/option. """
        self._choice = {}

    # -----------------------------------------------------------------------

    def get_choice(self, key):
        """ Return a value from its key. """

        if not key in self._choice.keys():
            return None
        return self._choice[key]

    # -----------------------------------------------------------------------

    def get_choices(self):
        """ Return the dictionary with all pairs key/value. """

        return self._choice

    # -----------------------------------------------------------------------

    def get_keys(self):
        """ Return the list of keys. """

        return self._choice.keys()

# ---------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# The BaseTheme (preferences shared by all frames):
# ----------------------------------------------------------------------------

class BaseTheme( Theme ):
    """ Base theme: the minimum required information, with a "classic" look. """

    def __init__(self):

        Theme.__init__(self)

        self._choice['M_BG_COLOUR']   = wxOption('wx.Colour', (240,240,230), "Main background color")
        self._choice['M_FG_COLOUR']   = wxOption('wx.Colour', (128,122,122), "Main foreground color")
        self._choice['M_FONT']        = wxOption('wx.Font', (MAIN_FONTSIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_SYSTEM), "Font")
        self._choice['M_FONT_COLOUR'] = wxOption('wx.Colour', (30,30,30), "Main font color")

        self._choice['M_TIPS']        = wxOption('bool', True, 'Show tips at start-up')
        self._choice['M_OUTPUT_EXT']  = wxOption('str',  '.xra', "Output file format")
        self._choice['M_ICON_THEME']  = wxOption('str',  'Default', "Icons theme")

        self._choice['M_BGD_COLOUR']   = wxOption('wx.Colour', (240,235,215), "Secondary main background color")
        self._choice['M_FGD_COLOUR']   = wxOption('wx.Colour', (128,122,122), "Secondary main foreground color")
        self._choice['M_FONTD_COLOUR'] = wxOption('wx.Colour', (108,102,102), "Secondary main font color")

        # Menu
        self._choice['M_BGM_COLOUR']   = wxOption('wx.Colour', (128,122,122), "Menu background color")
        self._choice['M_FONTM_COLOUR'] = wxOption('wx.Colour', (240,240,230), "Menu font color")

        self._choice['F_SPACING'] = wxOption('int', 2)


# (100,110,125)

# ----------------------------------------------------------------------------

class OldBaseTheme( Theme ):
    """ Base theme for SPPAS before 1.8.0 """

    def __init__(self):

        Theme.__init__(self)

        # For the Main Frame
        # ==================

        self._choice['M_BG_COLOUR']   = wxOption('wx.Colour', (245,245,245), "Main background color")
        self._choice['M_FG_COLOUR']   = wxOption('wx.Colour', (15,15,15), "Main foreground color")
        self._choice['M_FONT']        = wxOption('wx.Font', (MAIN_FONTSIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_SYSTEM), "Font")
        self._choice['M_FONT_COLOUR'] = wxOption('wx.Colour', (15,15,15), "Main font color")

        self._choice['M_TIPS']        = wxOption('bool', True, 'Show tips at start-up')
        self._choice['M_OUTPUT_EXT']  = wxOption('str',  '.xra', "Output file format")
        self._choice['M_ICON_THEME']  = wxOption('str',  'Default', "Icons theme")

        # For the File Manager
        # ====================
        self._choice['F_SPACING'] = wxOption('int', 2)

# ----------------------------------------------------------------------------
