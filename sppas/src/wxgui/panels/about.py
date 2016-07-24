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
# File: about.py
# ----------------------------------------------------------------------------

import wx
import wx.lib.scrolledpanel
import webbrowser

from sp_glob import program, version, author, copyright, brief, url, license_text

from wxgui.sp_icons import APP_ICON
from wxgui.cutils.imageutils import spBitmap


class AboutSPPAS( wx.lib.scrolledpanel.ScrolledPanel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      About SPPAS.

    """
    def __init__(self, parent, preferences):

        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, size=wx.DefaultSize, style=wx.NO_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BG_COLOUR') )
        self.SetForegroundColour( preferences.GetValue('M_FG_COLOUR') )

        # Logo
        bitmap = spBitmap( APP_ICON, size=48 )
        logo = wx.StaticBitmap(self, wx.ID_ANY, bitmap)

        # Program name
        font = preferences.GetValue('M_FONT')
        fontsize = font.GetPointSize()
        font.SetPointSize( fontsize+4 )
        font.SetWeight( wx.BOLD )
        textprogramversion = wx.StaticText(self, -1, program + " "+version)
        textprogramversion.SetFont( font )
        textprogramversion.SetBackgroundColour( preferences.GetValue('M_BG_COLOUR') )
        textprogramversion.SetForegroundColour( preferences.GetValue('M_FONT_COLOUR') )

        # Description
        font.SetPointSize( fontsize )
        font.SetWeight( wx.NORMAL )
        textdescr = wx.StaticText(self, -1, brief)
        textdescr.SetFont( font )
        textdescr.SetBackgroundColour( preferences.GetValue('M_BG_COLOUR') )
        textdescr.SetForegroundColour( preferences.GetValue('M_FONT_COLOUR') )

        # Copyright
        font.SetWeight( wx.BOLD )
        textcopy = wx.StaticText(self, -1, copyright)
        textcopy.SetFont( font )
        textcopy.SetBackgroundColour( preferences.GetValue('M_BG_COLOUR') )
        textcopy.SetForegroundColour( preferences.GetValue('M_FONT_COLOUR') )

        # URL
        font.SetWeight( wx.NORMAL )
        font.SetUnderlined( True )
        texturl = wx.StaticText(self, -1, url)
        texturl.SetFont( font )
        texturl.SetBackgroundColour( preferences.GetValue('M_BG_COLOUR') )
        texturl.SetForegroundColour( wx.Colour(80,108,216) )
        texturl.Bind( wx.EVT_LEFT_UP, self.OnLink )

        # License
        font.SetUnderlined( False )
        textgpl = wx.StaticText(self, -1, license_text)
        textgpl.SetFont( font )
        textgpl.SetBackgroundColour( preferences.GetValue('M_BG_COLOUR') )
        textgpl.SetForegroundColour( preferences.GetValue('M_FONT_COLOUR') )

        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add(logo,               proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=8)
        sizer.Add(textprogramversion, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=2)
        sizer.Add(textdescr,          proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=2)
        sizer.Add(textcopy,           proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=8)
        sizer.Add(texturl,            proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=2)
        sizer.Add(textgpl,            proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=2)
        self.SetSizer(sizer)

        self.FitInside()
        self.SetupScrolling(scroll_x=True, scroll_y=True)


    def OnLink(self, event):
        try:
            webbrowser.open(url,1)
        except:
            pass

