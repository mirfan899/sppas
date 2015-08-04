#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------
# File: themes.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx

from option import Option
from wxgui.sp_consts import MAIN_FONTSIZE


# ----------------------------------------------------------------------------
# Class to store a set of themes (name/class)
# ----------------------------------------------------------------------------

class Themes:
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to store all themes (name/class).

    """

    def __init__(self):
        """
        Constructor.

        A Theme is a dictionary with key/option.

        """

        self._themes = {}

    # End __init__
    # -----------------------------------------------------------------------


    def get_theme(self, key):
        """ Return a value from its key. """

        if not key in self._themes.keys():
            return None

        return self._themes[key]

    # End get_theme
    # -----------------------------------------------------------------------


    def get_themes(self):
        """ Return the dictionary with all pairs key/value. """

        return self._themes

    # End get_themes
    # -----------------------------------------------------------------------


    def add_theme(self, key, value):
        """ Add a pair key/value. """

        #if not key in self._themes.keys():
        self._themes[key] = value
        #raise KeyError('This theme is already in the set of known themes.')

    # End add_theme
    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Base class for a theme.
# ----------------------------------------------------------------------------

class Theme:
    """
    Base class: A theme store all preferences for the colors, fonts, etc...

    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to store all settings for the colors and fonts.

    """

    def __init__(self):
        """
        Constructor.

        A Theme is a dictionary with key/option.

        """

        self._choice = {}

    # End __init__
    # -----------------------------------------------------------------------


    def get_choice(self, key):
        """ Return a value from its key. """

        if not key in self._choice.keys():
            return None
        return self._choice[key]

    # End get_choice
    # -----------------------------------------------------------------------


    def get_choices(self):
        """ Return the dictionary with all pairs key/value. """

        return self._choice

    # End get_choice
    # -----------------------------------------------------------------------


    def get_keys(self):
        """ Return the list of keys. """

        return self._choice.keys()

    # End get_choice
    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# The BaseTheme (preferences shared by all frames):
# ----------------------------------------------------------------------------


class BaseTheme( Theme ):
    """ Base theme: the minimum required information, with a "classic" look. """

    def __init__(self):

        Theme.__init__(self)

        # For the Main Frame
        # ==================
        self._choice['M_BG_COLOUR']   = Option('wx.Colour', (245,245,245), "Background color")
        self._choice['M_FG_COLOUR']   = Option('wx.Colour', (15,15,15), "Foreground color")
        self._choice['M_FONT']        = Option('wx.Font', (MAIN_FONTSIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_SYSTEM), "Font")
        self._choice['M_FONT_COLOUR'] = Option('wx.Colour', (15,15,15), "Font color")

        self._choice['M_TIPS']        = Option('bool', True, 'Show tips at start-up')
        self._choice['M_OUTPUT_EXT']  = Option('str',  '.xra', "Output file format")
        self._choice['M_ICON_THEME']  = Option('str',  'Default', "Icons theme")

        # For the File Manager
        # ====================
        self._choice['F_SPACING'] = Option('int', 2)

        # wx.FONTFAMILY_DEFAULT     Chooses a default font.
        # wx.FONTFAMILY_DECORATIVE     A decorative font.
        # wx.FONTFAMILY_ROMAN     A formal, serif font.
        # wx.FONTFAMILY_SCRIPT     A handwriting font.
        # wx.FONTFAMILY_SWISS     A sans-serif font.
        # wx.FONTFAMILY_MODERN     Usually a fixed pitch font.
        # wx.FONTFAMILY_TELETYPE     A teletype font.
        #
        # wx.FONTWEIGHT_NORMAL     Normal font.
        # wx.FONTWEIGHT_LIGHT     Light font.
        # wx.FONTWEIGHT_BOLD     Bold font.
        #
        # wx.FONTENCODING_SYSTEM     system default
        # wx.FONTENCODING_DEFAULT     current default encoding
        # wx.FONTENCODING_ISO8859_1     West European (Latin1)
        # ...
        # wx.FONTENCODING_UTF7     UTF-7 Unicode encoding
        # wx.FONTENCODING_UTF8     UTF-8 Unicode encoding

# ----------------------------------------------------------------------------
