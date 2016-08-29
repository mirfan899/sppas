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
# import sys
# import os.path
# sys.path.append(  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

import wx

from wxgui.sp_icons import APP_ICON

from wxgui.cutils.imageutils import spBitmap

from wxgui.panels.buttons import ButtonCreator
from wxgui.sp_consts import DIALOG_STYLE
from wxgui.sp_consts import FRAME_TITLE
from wxgui.sp_consts import MAIN_FONTSIZE
from wxgui.sp_consts import BUTTON_ICONSIZE

import wxgui.structs.prefs

# ----------------------------------------------------------------------------
# class BaseDialog
# ----------------------------------------------------------------------------

class spBaseDialog( wx.Dialog ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Base class for dialogs in SPPAS.

    """
    def __init__(self, parent, preferences=None, title=""):
        """
        Constructor.

        @param parent is a wx window.
        @param preferences (Preferences)

        """
        wx.Dialog.__init__(self, parent, -1, title=FRAME_TITLE+title, style=DIALOG_STYLE)

        if preferences is None:
            preferences = wxgui.structs.prefs.Preferences()
        self.preferences = preferences

        # menu and toolbar
        self.toolbar = None
        self.btncreator = ButtonCreator(self.preferences)

        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(APP_ICON) )
        self.SetIcon(_icon)

        # colors
        self.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont( self.preferences.GetValue('M_FONT'))

    # -----------------------------------------------------------------------

    def CreateTitle(self, titleicon=APP_ICON, titletext="It's coffee time!"):
        """
        Create a layout including a nice bold-title with an icon.

        @param titleicon (str) Name of the icon.
        @param titletext (str) The title
        @return wx.Panel

        """
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))

        bitmap = spBitmap(titleicon, BUTTON_ICONSIZE, theme=self.preferences.GetValue('M_ICON_THEME'))
        sBmp = wx.StaticBitmap(panel, wx.ID_ANY, bitmap)

        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)

        paneltext = wx.Panel(self, -1, style=wx.NO_BORDER)
        paneltext.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        sizertext = wx.BoxSizer()
        text = wx.StaticText(paneltext, label=titletext)
        text.SetFont( font )
        text.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        text.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        sizertext.Add(text, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        paneltext.SetSizer( sizertext )

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sBmp, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=4)
        sizer.Add(paneltext, proportion=1, flag=wx.EXPAND|wx.ALL, border=4)
        panel.SetSizer(sizer)
        panel.SetAutoLayout( True )

        return panel

    # -----------------------------------------------------------------------

    def CreateButton(self, icon, text, tooltip="", btnid=None):
        """
        Create a button and return it.

        @param icon (str) Path to the icon file name.
        @param text (str) Short text to print into the button.
        @param tooltip (str) Long text to show when mouse is entering into the button.
        @param btnid (wx.ID) A unique ID assigned to the button.

        """
        return self.btncreator.CreateButton(self, icon, text, tooltip, btnid)

    # -----------------------------------------------------------------------

    def CreateSaveButton(self, tooltip="Save"):
        return self.btncreator.CreateSaveButton(self, tooltip)

    def CreateCancelButton(self, tooltip="Cancel"):
        btn = self.btncreator.CreateCancelButton(self, tooltip)
        self.SetAffirmativeId(wx.ID_CANCEL)
        return btn

    def CreateCloseButton(self, tooltip="Close"):
        btn = self.btncreator.CreateCloseButton(self, tooltip)
        btn.SetDefault()
        btn.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        return btn

    def CreateOkayButton(self, tooltip="Okay"):
        btn = self.btncreator.CreateOkayButton(self, tooltip)
        btn.SetDefault()
        btn.SetFocus()
        self.SetAffirmativeId(wx.ID_OK)
        return btn

    def CreateYesButton(self, tooltip="Yes"):
        btn = self.btncreator.CreateYesButton(self, tooltip)
        btn.SetDefault()
        return btn

    def CreateNoButton(self, tooltip="No"):
        return self.btncreator.CreateNoButton(self, tooltip)

    # -----------------------------------------------------------------------

    def CreateButtonBox(self, leftbuttons=[],rightbuttons=[]):
        """
        Create a button box, with buttons to put at left and others at right.

        @param leftbuttons (list)
        @param rightbuttons (list)
        @return Sizer.

        """
        button_box = wx.BoxSizer(wx.HORIZONTAL)

        if len(leftbuttons)>0:
            for button in leftbuttons:
                button_box.Add(button, flag=wx.LEFT, border=2)

        if len(rightbuttons)>0:
            button_box.AddStretchSpacer()
            for button in rightbuttons:
                button_box.Add(button, flag=wx.RIGHT, border=2)

        return button_box

    # -----------------------------------------------------------------------

    def CreateTextCtrl(self, text, style=wx.TE_MULTILINE|wx.NO_BORDER):
        """
        Return a wx.TextCtrl with appropriate font and style.

        """
        txt = wx.TextCtrl(self, wx.ID_ANY, value=text, style=style)
        font = self.preferences.GetValue('M_FONT')
        txt.SetFont(font)
        txt.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        txt.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )

        return txt

    # -----------------------------------------------------------------------

    def AddToolbar(self, leftobjects,rightobjects):
        """
        Add a toolbar to the dialog.

        @param leftobjects (list)
        @param rightobjects (list)

        """
        if len(leftobjects+rightobjects) == 0: return

        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)

        if len(leftobjects)>0:
            for button in leftobjects:
                self.toolbar.Add(button, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=2)
            if len(rightobjects)>0:
                self.toolbar.AddStretchSpacer()

        if len(rightobjects)>0:
            for button in rightobjects:
                self.toolbar.Add(button, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=2)

    # -----------------------------------------------------------------------

    def LayoutComponents(self, title, content, buttonbox):
        """
        Layout the components of the dialog.
          - title at the top
          - then eventually the toolbar
          - then the content
          - and a button box at the bottom.

        """
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title,     0, flag=wx.ALL|wx.EXPAND, border=2)
        if self.toolbar is not None:
            vbox.Add(self.toolbar, 0, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=2)
        vbox.Add(content,   2, flag=wx.ALL|wx.EXPAND, border=2)
        vbox.Add(buttonbox, 0, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border=2)
        self.SetSizerAndFit(vbox)

# ---------------------------------------------------------------------------

def DemoBaseDialog(parent, preferences=None):

    frame = spBaseDialog(parent, preferences)
    title = frame.CreateTitle(APP_ICON,"This is a BaseDialog frame...")
    btnclose = frame.CreateCloseButton()
    btnbox   = frame.CreateButtonBox( [],[btnclose] )
    frame.AddToolbar([wx.StaticText(frame, label="toolbar is here", style=wx.ALIGN_CENTER)],[])
    frame.LayoutComponents( title, wx.Panel(frame, -1, size=(320,200)), btnbox )
    frame.ShowModal()
    frame.Destroy()

# ---------------------------------------------------------------------------

if __name__ == "__main__":

    app = wx.PySimpleApp()
    DemoBaseDialog(None)
    app.MainLoop()

# ---------------------------------------------------------------------------
