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
# File: basedialog.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------
import sys
import os
import os.path
sys.path.append(  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

import wx

from wxgui.sp_icons import APP_ICON
from wxgui.sp_icons import CLOSE_ICON
from wxgui.sp_icons import APPLY_ICON
from wxgui.sp_icons import CANCEL_ICON
from wxgui.sp_icons import SAVE_FILE

from wxgui.cutils.ctrlutils  import CreateGenButton
from wxgui.cutils.imageutils import spBitmap

from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE
from wxgui.sp_consts import MAIN_FONTSIZE
from wxgui.sp_consts import BUTTON_ICONSIZE

import wxgui.structs.prefs

# ----------------------------------------------------------------------------
# class BaseDialog
# ----------------------------------------------------------------------------

class spBaseDialog( wx.Dialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Base class for dialogs in SPPAS.

    """

    def __init__(self, parent, preferences=None, title=""):
        """
        Constructor.

        @param parent is a wx window.
        @param preferences (Preferences)

        """
        wx.Dialog.__init__(self, parent, -1, title=FRAME_TITLE+title, style=FRAME_STYLE)

        if preferences is None:
            preferences = wxgui.structs.prefs.Preferences()
        self.preferences = preferences

        # menu and toolbar
        self.toolbar = None

        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(APP_ICON) )
        self.SetIcon(_icon)

        # colors
        self.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont( self.preferences.GetValue('M_FONT'))


    def CreateTitle(self, titleicon, titletext):
        """
        Create a layout including a nice bold-title with an icon.
        """
        title_layout = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.BitmapButton(self, bitmap=spBitmap(titleicon, BUTTON_ICONSIZE, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label = wx.StaticText(self, label=titletext, style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)
        title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)
        return title_layout

    def CreateButton(self, icon, text, tooltip="", btnid=None):
        """
        Create a button and return it.

        @param icon (str) Path to the icon file name.
        @param text (str) Short text to print into the button.
        @param tooltip (str) Long text to show when mouse is entering into the button.
        @param btnid (wx.ID) A unique ID assigned to the button.

        """
        if btnid is None:
            btnid = wx.NewId()
        bmp = spBitmap(icon, theme=self.preferences.GetValue('M_ICON_THEME'))
        btn = CreateGenButton(self, btnid, bmp, text=text, tooltip=tooltip, colour=None)
        btn.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        btn.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        btn.SetFont( self.preferences.GetValue('M_FONT') )
        return btn

    def CreateSaveButton(self, tooltip=""):
        return self.CreateButton(SAVE_FILE, "Save", tooltip)

    def CreateCancelButton(self, tooltip=""):
        btn = self.CreateButton(CANCEL_ICON, "Cancel", tooltip, wx.ID_CANCEL)
        self.SetAffirmativeId(wx.ID_CANCEL)
        return btn

    def CreateCloseButton(self, tooltip=""):
        btn = self.CreateButton(CLOSE_ICON, "Close", tooltip, wx.ID_CLOSE)
        btn.SetDefault()
        btn.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        return btn

    def CreateOkayButton(self, tooltip=""):
        btn = self.CreateButton(APPLY_ICON, " OK ", tooltip, wx.ID_OK)
        btn.SetDefault()
        btn.SetFocus()
        self.SetAffirmativeId(wx.ID_OK)
        return btn

    def CreateButtonBox(self, leftbuttons,rightbuttons):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        if len(leftbuttons)>0:
            for button in leftbuttons:
                button_box.Add(button, flag=wx.LEFT, border=2)
        if len(rightbuttons)>0:
            button_box.AddStretchSpacer()
            for button in rightbuttons:
                button_box.Add(button, flag=wx.RIGHT, border=2)
        return button_box

    def AddToolbar(self, leftobjects,rightobjects):
        if len(leftobjects+rightobjects)==0:
            return
        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)
        if len(leftobjects)>0:
            for button in leftobjects:
                self.toolbar.Add(button, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=2)
            if len(rightobjects)>0:
                self.toolbar.AddStretchSpacer()
        if len(rightobjects)>0:
            for button in rightobjects:
                self.toolbar.Add(button, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=2)


    def LayoutComponents(self, title, content, buttonbox):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title,     0, flag=wx.ALL|wx.EXPAND, border=4)
        if self.toolbar is not None:
            vbox.Add(self.toolbar, 0, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=4)
        vbox.Add(content,   1, flag=wx.ALL|wx.EXPAND, border=4)
        vbox.Add(buttonbox, 0, flag=wx.ALL|wx.EXPAND, border=4)
        self.SetSizerAndFit(vbox)


# ---------------------------------------------------------------------------

def ShowBaseDialog(parent, preferences=None):
    frame = spBaseDialog(parent, preferences)
    title = frame.CreateTitle(APP_ICON,"This is a BaseDialog frame...")
    btnsave  = frame.CreateButton(SAVE_FILE,"Save button", "Save something!")
    btnclose = frame.CreateCloseButton()
    btnbox   = frame.CreateButtonBox( [btnsave],[btnclose] )
    frame.AddToolbar([wx.StaticText(frame, label="toolbar is here", style=wx.ALIGN_CENTER)],[])
    frame.LayoutComponents( title, wx.Panel(frame, -1, size=(320,200)), btnbox )
    frame.ShowModal()
    frame.Destroy()

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.PySimpleApp()
    ShowBaseDialog(None)
    app.MainLoop()

# ---------------------------------------------------------------------------
