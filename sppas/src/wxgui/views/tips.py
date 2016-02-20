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
# File: tips.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import codecs
import wx
import random

from wxgui.cutils.imageutils import ScaleBitmap
from wxgui.cutils.imageutils import spBitmap
from wxgui.cutils.imageutils import GetBitmap

from wxgui.cutils.ctrlutils import CreateGenButton

from sp_glob import TIPS_ICON_PATH
from sp_glob import TIPS_FILE
from wxgui.sp_icons import APP_ICON
from wxgui.sp_icons import TIPS_ICON
from wxgui.sp_icons import FORWARD_ICON
from wxgui.sp_icons import CANCEL_ICON

from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE
from wxgui.sp_consts import MAIN_FONTSIZE

# ----------------------------------------------------------------------------
# class TipsDialog
# ----------------------------------------------------------------------------

class TipsDialog( wx.Dialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: A class to show tips at start-up.

    This class implements a frame including a bitmap and a message.

    """

    def __init__(self, parent, prefsIO):

        wx.Dialog.__init__(self, parent, title=FRAME_TITLE+" - Tips", style=FRAME_STYLE)

        self.preferences = prefsIO
        self._create_gui()

    # End __init__
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------


    def _create_gui(self):
        self._init_infos()
        self._create_title_label()
        self._create_content()
        self._create_next_button()
        self._create_close_button()
        self._layout_components()
        self._set_focus_component()


    def _init_infos( self ):
        wx.GetApp().SetAppName( "tips" )
        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(APP_ICON) )
        self.SetIcon(_icon)
        # colors
        self.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont( self.preferences.GetValue('M_FONT'))


    def _create_title_label(self):
        self.title_layout = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.BitmapButton(self, bitmap=spBitmap(TIPS_ICON, 32, theme=self.preferences.GetValue('M_ICON_THEME')), style=wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() + 2)
        self.title_label = wx.StaticText(self, label="Tips and tricks", style=wx.ALIGN_CENTER)
        self.title_label.SetFont( font )
        self.title_layout.Add(bmp,  flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)
        self.title_layout.Add(self.title_label, flag=wx.EXPAND|wx.ALL|wx.wx.ALIGN_CENTER_VERTICAL, border=5)


    def _create_content(self):
        # bitmap
        bmpinput = GetBitmap(TIPS_ICON_PATH, "tips-", "png")
        bmp = wx.Bitmap( bmpinput )
        bmp = ScaleBitmap(bmp, 96, 96)
        bitmap = wx.StaticBitmap(self, -1, bmp)
        # text
        text = self.GetTip()
        self.txt = wx.TextCtrl(self, value=text, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.NO_BORDER)
        font = wx.Font(MAIN_FONTSIZE, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL)
        self.txt.SetFont(font)
        self.txt.SetForegroundColour( wx.Colour(50,0,100) )
        self.txt.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        # sizer
        self.content_layout = wx.BoxSizer( wx.HORIZONTAL )
        self.content_layout.Add(bitmap, 0, wx.ALL, 5)
        self.content_layout.Add(self.txt, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5)


    def _create_next_button(self):
        bmp = spBitmap(FORWARD_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_next = CreateGenButton(self, wx.ID_FORWARD, bmp, text=" Next tip", tooltip="Show a random tip", colour=color)
        self.btn_next.SetFont( self.preferences.GetValue('M_FONT'))
        self.Bind(wx.EVT_BUTTON, self.onShowNextTip, self.btn_next, wx.ID_FORWARD)


    def _create_close_button(self):
        bmp = spBitmap(CANCEL_ICON, theme=self.preferences.GetValue('M_ICON_THEME'))
        color = self.preferences.GetValue('M_BG_COLOUR')
        self.btn_close = CreateGenButton(self, wx.ID_CLOSE, bmp, text=" Close", tooltip="Close this frame", colour=color)
        self.btn_close.SetFont( self.preferences.GetValue('M_FONT'))
        self.btn_close.SetDefault()
        self.btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)


    def _create_button_box(self):
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.AddStretchSpacer()
        button_box.Add(self.btn_next,  flag=wx.RIGHT, border=5)
        button_box.Add(self.btn_close, flag=wx.RIGHT, border=5)
        return button_box


    def _layout_components(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.title_layout,   0, flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(self.content_layout, 1, flag=wx.ALL|wx.EXPAND, border=0)
        vbox.Add(self._create_button_box(), 0, flag=wx.ALL|wx.EXPAND, border=5)
        self.SetMinSize((380,240))
        self.SetSize((420,280))
        self.SetSizer( vbox )


    def _set_focus_component(self):
        self.btn_close.SetFocus()


    #-------------------------------------------------------------------------
    # Callbacks
    #-------------------------------------------------------------------------


    def GetTip(self):
        """ Return a message. """
        try:
            with codecs.open(TIPS_FILE, 'r', 'utf-8') as f:
                lines = f.readlines()
            return random.choice(lines)
        except Exception:
            return "Thanks for using SPPAS."

    # End GetTip
    # ------------------------------------------------------------------------


    def onShowNextTip(self,event):
        """ Change the message (pick randomly)."""
        text = self.GetTip()
        self.txt.SetValue(text)

    # End NextTip
    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

def ShowTipsDialog(parent, preferences=None):
    dialog = TipsDialog(parent, preferences)
    dialog.ShowModal()
    dialog.Destroy()

# ----------------------------------------------------------------------------
