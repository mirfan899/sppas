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
# File: sp_consts.py
# ----------------------------------------------------------------------------

import os.path
import wx

from sp_glob import BASE_PATH
from sp_glob import program, version

# ---------------------------------------------------------------------------
# Define all paths (relatively to SPPAS base path)
# ---------------------------------------------------------------------------

PREFS_FILE = os.path.join( BASE_PATH , "etc", "sppas.prefs")

HELP_PATH     = os.path.join( BASE_PATH, "doc" )
HELP_IMG_PATH = os.path.join( HELP_PATH, "img" )
DOC_IDX       = os.path.join( HELP_PATH, "markdown.idx" )
HELP_IDX_EXT  = ".idx"


# ---------------------------------------------------------------------------
# Base components:

FRAME_STYLE = wx.DEFAULT_FRAME_STYLE|wx.CLOSE_BOX
FRAME_TITLE = " " + program + " " + version + " "
DIALOG_STYLE = wx.CAPTION|wx.RESIZE_BORDER|wx.THICK_FRAME

DEFAULT_APP_NAME = program + "Component"


# ---------------------------------------------------------------------------
# GUI design.

ERROR_COLOUR   = wx.Colour( 220,  30,  10 )  # red
INFO_COLOUR    = wx.Colour(  55,  30, 200 )  # blue
IGNORE_COLOUR  = wx.Colour( 140, 100, 160 )  # gray-violet
WARNING_COLOUR = wx.Colour( 240, 190,  45 )  # orange
OK_COLOUR      = wx.Colour(  25, 160,  50 )  # green

# ---------------------------------------------------------------------------
# GUI design.

MIN_PANEL_W = 180
MIN_PANEL_H = 220

MIN_FRAME_W=640
MIN_FRAME_H=440

if wx.Platform == "__WXMSW__":
    FRAME_H  = 600   # expected "good" height
    PANEL_W  = 320   # Left/Right panel (FLP)
else:
    FRAME_H  = 540   # expected "good" height
    PANEL_W  = 380

TREE_ICONSIZE   = 16
MENU_ICONSIZE   = 16
TB_ICONSIZE     = 24
BUTTON_ICONSIZE = 32

# ---------------------------------------------------------------------------

if wx.Platform == '__WXMAC__':
    MAIN_FONTSIZE = 12
elif wx.Platform == '__WXGTK__':
    MAIN_FONTSIZE = 8
else:
    MAIN_FONTSIZE = 9

TB_FONTSIZE     = MAIN_FONTSIZE - 2
HEADER_FONTSIZE = MAIN_FONTSIZE + 4

# ---------------------------------------------------------------------------

# ----------------------------------------------------------------------------

ID_ANNOTATIONS = wx.NewId()
ID_COMPONENTS  = wx.NewId()
ID_PLUGINS     = wx.NewId()
ID_ACTIONS     = wx.NewId()

ID_EXT_BUG     = wx.NewId()
ID_EXT_HOME    = wx.NewId()
ID_FEEDBACK    = wx.NewId()

ID_FRAME_DATAROAMER  = wx.NewId()
ID_FRAME_SNDROAMER   = wx.NewId()
ID_FRAME_IPUSCRIBE   = wx.NewId()
ID_FRAME_SPPASEDIT   = wx.NewId()
ID_FRAME_STATISTICS  = wx.NewId()
ID_FRAME_DATAFILTER  = wx.NewId()

# ---------------------------------------------------------------------------

