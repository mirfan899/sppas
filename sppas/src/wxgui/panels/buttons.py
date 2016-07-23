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
# File: buttons.py
# ----------------------------------------------------------------------------

import wx

from wxgui.cutils.imageutils import spBitmap

# ---------------------------------------------------------------------------

class ImgPanel( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Simple panel with an image.

    """
    def __init__(self, parent, bmpsize, bmpname):
        wx.Panel.__init__(self, parent)

        bitmap = spBitmap( bmpname, size=bmpsize )
        sBmp = wx.StaticBitmap(self, wx.ID_ANY, bitmap)

        sizer = wx.BoxSizer()
        sizer.Add(sBmp, proportion=0, flag=wx.ALL, border=0)
        self.SetBackgroundColour( parent.GetBackgroundColour() )
        self.SetSizerAndFit(sizer)

        sBmp.Bind(wx.EVT_LEFT_UP, self.OnEvent)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEvent)

    def OnEvent(self, evt):
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------

class ButtonPanel( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Panel imitating behaviors of a complex button.

    """
    def __init__(self, parent, idb, preferences, bmp, text, subtext=None):
        wx.Panel.__init__(self, parent, idb, style=wx.NO_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BGD_COLOUR') )
        self.SetFont( preferences.GetValue('M_FONT') )

        self._prefs = preferences

        content = self.create_content(bmp, text, subtext)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(content, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, border=2)
        self.SetSizer(sizer)
        self.SetAutoLayout( True )

    def create_content(self, bmpname, textstr, subtextstr=None):
        panel = wx.Panel(self)
        panel.SetBackgroundColour( self.GetBackgroundColour() )
        sizer = wx.BoxSizer(wx.VERTICAL)

        font = self.GetFont()

        if bmpname is not None:
            bmp = ImgPanel(panel, 32, bmpname)
            sizer.Add(bmp, flag=wx.ALL|wx.ALIGN_CENTER, border=10)

        text = wx.StaticText(panel, -1, textstr)
        font.SetWeight(wx.BOLD)
        text.SetFont( font )
        text.SetBackgroundColour( self.GetBackgroundColour() )
        text.SetForegroundColour( self._prefs.GetValue('M_FONT_COLOUR') )
        text.Bind(wx.EVT_LEFT_UP,     self.OnButtonLeftUp)
        sizer.Add(text, flag=wx.ALL|wx.ALIGN_CENTER, border=0)

        font.SetWeight(wx.NORMAL)
        if subtextstr is not None:
            tabtexts = subtextstr.split(',')
            for i,t in enumerate(tabtexts):
                if (i+1)<len(tabtexts):
                    subtext = wx.StaticText(panel, -1, t+",")
                else:
                    subtext = wx.StaticText(panel, -1, t)
                subtext.SetBackgroundColour( self.GetBackgroundColour() )
                subtext.SetForegroundColour( self._prefs.GetValue('M_FONTD_COLOUR') )
                subtext.SetFont( font )
                subtext.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
                sizer.Add(subtext, flag=wx.ALL|wx.ALIGN_CENTER, border=0)

        panel.SetSizer(sizer)
        panel.SetAutoLayout( True )

        panel.Bind(wx.EVT_LEFT_UP,    self.OnButtonLeftUp)
        panel.Bind(wx.EVT_ENTER_WINDOW, self.OnButtonEnter)
        panel.Bind(wx.EVT_LEAVE_WINDOW, self.OnButtonLeave)
        panel.SetMinSize((116,116))

        return panel


    def OnButtonEnter(self, event):
        self.SetBackgroundColour( self._prefs.GetValue('M_FGD_COLOUR') )

    def OnButtonLeave(self, event):
        self.SetBackgroundColour( self._prefs.GetValue('M_BGD_COLOUR') )

    def OnButtonLeftUp(self, event):
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------

class ButtonMenuPanel( wx.Panel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Panel imitating behaviors of a menu button.

    """
    def __init__(self, parent, idb, preferences, bmpname, textstr):
        wx.Panel.__init__(self, parent, idb, style=wx.NO_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BGM_COLOUR') )

        self._prefs = preferences

        sizer = wx.BoxSizer(wx.VERTICAL)
        if bmpname is not None:
            bmp = ImgPanel(self, 24, bmpname)
            bmp.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
            sizer.Add(bmp, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)

        if textstr is not None:
            text = wx.StaticText(self, -1, textstr)
            text.SetBackgroundColour( self.GetBackgroundColour() )
            text.SetForegroundColour( preferences.GetValue('M_FONTM_COLOUR') )
            text.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
            sizer.Add(text, flag=wx.ALL|wx.ALIGN_CENTER, border=2)

        self.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)

        self.SetSizer(sizer)
        self.SetAutoLayout( True )


    def OnButtonLeftUp(self, event):
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------
