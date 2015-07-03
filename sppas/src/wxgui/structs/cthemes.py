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
# File: cthemes.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# -------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------

import wx

from wxgui.structs.option import Option
from wxgui.structs.themes import Theme, Themes

# ----------------------------------------------------------------------------
# Specific themes for SppasEdit component
# ----------------------------------------------------------------------------
#

class ThemeDefault( Theme ):
    """ The theme which assign all required options, with default values. """

    def __init__(self):

        Theme.__init__(self)

        # Display
        self._choice['D_TIME_MIN']      = Option('float', 0.0,  'Minimum time value (in seconds) of the displayed period at start-up')
        self._choice['D_TIME_MAX']      = Option('float', 2.0,  'Maximum time value (in seconds) of the displayed period at start-up')
        self._choice['D_TIME_ZOOM_MIN'] = Option('float', 0.2, 'Minimum duration (in seconds) of the displayed period')
        self._choice['D_TIME_ZOOM_MAX'] = Option('float', 300.0, 'Maximum duration (in seconds) of the displayed period')

        self._choice['D_H_ZOOM'] = Option('float', 50.0, 'Time zoom (percentage)')
        self._choice['D_SCROLL'] = Option('float', 75.0, 'Time scroll (percentage)')
        self._choice['D_V_ZOOM'] = Option('float', 10.0, 'Vertical zoom (percentage)')

        # spControl
        self._choice['O_PEN_WIDTH']   = Option('int', 1)
        self._choice['O_PEN_STYLE']   = Option('int', wx.SOLID)
        self._choice['O_BRUSH_STYLE'] = Option('int', wx.SOLID)
        self._choice['O_MARGIN']      = Option('int', 2, 'Margin around objects')

        # Ruler
        self._choice['R_BG_COLOUR']      = Option('wx.Colour', (255,255,255), 'Ruler background color')
        self._choice['R_FG_COLOUR']      = Option('wx.Colour', (10,10,140))
        self._choice['R_HANDLES_COLOUR'] = Option('wx.Colour', (10,10,140))
        self._choice['R_FONT']           = Option('wx.Font', (8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))
        self._choice['R_FONT_COLOUR']    = Option('wx.Colour', (10, 10, 140))
        self._choice['R_HEIGHT']         = Option('int', 30, 'Initial height of the ruler')

        # Separator
        self._choice['S_COLOUR']         = Option('wx.Colour', (123,15,28))
        self._choice['S_PEN_WIDTH']      = Option('int', 4)

        # Tier
        self._choice['T_BG_COLOUR']      = Option('wx.Colour', None, 'Tier background color') # Pick randomly
        self._choice['T_FG_COLOUR']      = Option('wx.Colour', (10,60,10), 'Tier foreground color')
        self._choice['T_RADIUS_COLOUR']  = Option('wx.Colour', (20,20,80), 'Color for the radius of points')
        self._choice['T_HANDLES_COLOUR'] = Option('wx.Colour', (140,10,10), 'Color of the handles of a transcription')
        self._choice['T_FONT']           = Option('wx.Font', (9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))
        self._choice['T_FONT_COLOUR']    = Option('wx.Colour', (140, 10, 10), 'Font color')
        self._choice['T_LABEL_ALIGN']    = Option('wx.ALIGN', 'center', 'Text alignment for labels')
        self._choice['T_HEIGHT']         = Option('int', 30, 'Initial height of a tier')

        # Wave
        self._choice['W_BG_COLOUR']      = Option('wx.Colour', (255,255,255), 'Wave background color')
        self._choice['W_FG_COLOUR']      = Option('wx.Colour', (10,140,10), 'Wave foreground color')
        self._choice['W_BG_GRADIENT_COLOUR'] = Option('wx.Colour', (228,228,228), 'Wave background gradient color')
        self._choice['W_HANDLES_COLOUR'] = Option('wx.Colour', (10,140,10), 'Color of the handles of a wave')
        self._choice['W_FONT']           = Option('wx.Font', (9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))
        self._choice['W_FONT_COLOUR']    = Option('wx.Colour', (10, 140, 10), 'Font color')
        self._choice['W_FG_DISCO']       = Option('bool', False, 'Foreground in a Disco style')
        self._choice['W_AUTOSCROLL']     = Option('bool', True, 'Automatic vertical scroll of speech')
        self._choice['W_HEIGHT']         = Option('int', 100, 'Initial height of a wave')


# ----------------------------------------------------------------------------


class ThemeBrigitte( ThemeDefault ):
    """ SppasEdit author' theme. """

    def __init__(self):

        ThemeDefault.__init__(self)

        # Ruler
        self._choice['R_BG_COLOUR'] = Option('wx.Colour', (235,238,233))
        self._choice['R_FG_COLOUR'] = Option('wx.Colour', (123,15,28))
        self._choice['R_HANDLES_COLOUR'] = Option('wx.Colour', (130,40,10))
        self._choice['R_FONT'] = Option('wx.Font', (10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))
        self._choice['R_FONT_COLOUR'] = Option('wx.Colour', (130,130,130))

        # Separator
        self._choice['S_COLOUR'] = Option('wx.Colour', (123,15,28))
        self._choice['S_PEN_WIDTH'] = Option('int', 2)

        # Tier
        self._choice['T_BG_COLOUR'] = Option('wx.Colour', (135,138,133))
        self._choice['T_RADIUS_COLOUR'] = Option('wx.Colour', (252,175,62))
        self._choice['T_FG_COLOUR'] = Option('wx.Colour', (252,175,62))
        self._choice['T_FONT'] = Option('wx.Font', (10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))
        self._choice['T_FONT_COLOUR'] = Option('wx.Colour', (50, 50, 50))

        # Wave
        self._choice['W_FG_DISCO']   = Option('bool', False)
        self._choice['W_BG_COLOUR'] = Option('wx.Colour', (135,138,133))
        self._choice['W_FG_COLOUR'] = Option('wx.Colour', (252,175,62))
        self._choice['W_BG_GRADIENT_COLOUR'] = Option('wx.Colour', (86, 88, 84))
        self._choice['T_FONT'] = Option('wx.Font', (8, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))



# ----------------------------------------------------------------------------


class ThemePaul( ThemeDefault ):
    """ Theme looking like Praat (more or less...). """

    def __init__(self):

        ThemeDefault.__init__(self)

        # Ruler
        self._choice['R_BG_COLOUR'] = Option('wx.Colour', (166,166,166))
        self._choice['R_FG_COLOUR'] = Option('wx.Colour', (20,20,20))
        self._choice['R_HANDLES_COLOUR'] = Option('wx.Colour', (0,0,211))
        self._choice['R_FONT'] = Option('wx.Font', (10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))
        self._choice['R_FONT_COLOUR'] = Option('wx.Colour', (20, 20, 20))

        # Separator
        self._choice['S_COLOUR']    = Option('wx.Colour', (166,216,246))
        self._choice['S_PEN_WIDTH'] = Option('int', 2)

        # Tiers:
        self._choice['T_BG_COLOUR'] = Option('wx.Colour', (225,225,225))
        self._choice['T_RADIUS_COLOUR'] = Option('wx.Colour', (0,0,211))
        self._choice['T_FG_COLOUR'] = Option('wx.Colour', (10,10,10))
        self._choice['T_FONT'] = Option('wx.Font', (10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))
        self._choice['T_FONT_COLOUR'] = Option('wx.Colour', (0, 0, 0))

        # Wave
        self._choice['W_FG_DISCO'] = Option('bool', False)
        self._choice['W_BG_GRADIENT_COLOUR'] = Option('wx.Colour', (255,255,255))
        self._choice['W_FG_COLOUR'] = Option('wx.Colour', (10,10,10))
        self._choice['W_BG_COLOUR'] = Option('wx.Colour', (225,225,225))
        self._choice['W_FONT'] = Option('wx.Font', (8, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))



# ----------------------------------------------------------------------------

class ThemeLea( ThemeDefault ):
    """ SppasEdit author' daughter theme. """

    def __init__(self):

        ThemeDefault.__init__(self)

        # Ruler
        self._choice['R_BG_COLOUR'] = Option('wx.Colour', (255,255,255))
        self._choice['R_FG_COLOUR'] = Option('wx.Colour', (105,105,205))
        self._choice['R_HANDLES_COLOUR'] = Option('wx.Colour', (167,42,152))
        self._choice['R_FONT'] = Option('wx.Font', (10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))
        self._choice['R_FONT_COLOUR'] = Option('wx.Colour', (105, 105, 205))

        # Separator
        self._choice['S_COLOUR'] = Option('wx.Colour', (123,15,28))
        self._choice['S_PEN_WIDTH'] = Option('int', 4)

        # Tiers:
        self._choice['T_BG_COLOUR'] = Option('wx.Colour', (232,185,229))
        self._choice['T_RADIUS_COLOUR'] = Option('wx.Colour', (167,42,152))
        self._choice['T_FG_COLOUR'] = Option('wx.Colour', (167,42,152))
        self._choice['T_FONT'] = Option('wx.Font', (9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))
        self._choice['T_FONT_COLOUR'] = Option('wx.Colour', (10, 20, 10))

        # Wave
        self._choice['W_FG_DISCO'] = Option('bool', True)
        self._choice['W_BG_GRADIENT_COLOUR'] = Option('wx.Colour', (232,185,229))
        self._choice['W_FG_COLOUR'] = Option('wx.Colour', (167,42,152))
        self._choice['W_BG_COLOUR'] = Option('wx.Colour', (255,255,255))
        self._choice['W_FONT'] = Option('wx.Font', (8, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))

# ----------------------------------------------------------------------------

all_themes = Themes()
all_themes.add_theme(u'Default',  ThemeDefault())
all_themes.add_theme(u'Brigitte', ThemeBrigitte())
all_themes.add_theme(u'Léa',      ThemeLea())
all_themes.add_theme(u'Paul',     ThemePaul())

# ----------------------------------------------------------------------------
