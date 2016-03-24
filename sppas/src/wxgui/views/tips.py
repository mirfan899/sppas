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
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import codecs
import wx
import random

from wxgui.dialogs.basedialog import spBaseDialog

from wxgui.cutils.imageutils import ScaleBitmap
from wxgui.cutils.imageutils import GetBitmap
from wxgui.cutils.imageutils  import spBitmap

from sp_glob import TIPS_ICON_PATH
from sp_glob import TIPS_FILE

from wxgui.sp_icons import MESSAGE_ICON
from wxgui.sp_icons import FORWARD_ICON

from wxgui.sp_consts import MAIN_FONTSIZE

# ----------------------------------------------------------------------------
# class TipsDialog
# ----------------------------------------------------------------------------

class TipsDialog( spBaseDialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: A class to show tips at start-up.

    This class implements a frame including a bitmap and a message.

    """
    def __init__(self, parent, preferences):
        """"
        Constructor.

        """
        spBaseDialog.__init__(self, parent, preferences, title="Tips")
        wx.GetApp().SetAppName( "tips" )

        titlebox   = self.CreateTitle(MESSAGE_ICON,"Tips and tricks")
        contentbox = self._create_content()
        buttonbox  = self._create_buttons()

        self.LayoutComponents( titlebox,
                               contentbox,
                               buttonbox )

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_next  = self.CreateButton( FORWARD_ICON, " Next tip", tooltip="Show a random tip")
        btn_close = self.CreateOkayButton( )
        self.Bind(wx.EVT_BUTTON, self._on_show_next, btn_next)
        return self.CreateButtonBox( [btn_next],[btn_close] )


    def _create_content(self):
        # bitmap
        bmpinput = GetBitmap(TIPS_ICON_PATH, "tips-", "png")
        bmp = spBitmap(bmpinput, 64, theme=self.preferences.GetValue('M_ICON_THEME'))
        pan = wx.Panel(self,-1)
        pic = wx.StaticBitmap(pan)
        pic.SetBitmap(bmp)
        # text
        text = self.GetTip()
        self.txt = self.CreateTextCtrl( text, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.NO_BORDER )
        self.txt.SetMinSize((280,-1))
        # sizer
        content_layout = wx.BoxSizer( wx.HORIZONTAL )
        content_layout.Add(pan,      0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        content_layout.Add(self.txt, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 0)
        return content_layout

    #-------------------------------------------------------------------------
    # Callbacks
    #-------------------------------------------------------------------------

    def _on_show_next(self,event):
        """
        Change the message (pick a new one randomly).

        """
        pround = 0
        current = self.txt.GetValue()
        text = self.GetTip()
        while text == current and pround<3:
            text = self.GetTip()
            pround = pround + 1
        self.txt.SetValue(text)

    # ------------------------------------------------------------------------
    # Functions
    # ------------------------------------------------------------------------

    def GetTip(self):
        """
        Return a message.

        """
        try:
            with codecs.open(TIPS_FILE, 'r', 'utf-8') as f:
                lines = f.readlines()
            return random.choice(lines)
        except Exception:
            return "Thanks for using SPPAS."

# ----------------------------------------------------------------------------

def ShowTipsDialog(parent, preferences=None):
    dialog = TipsDialog(parent, preferences)
    dialog.ShowModal()
    dialog.Destroy()

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.PySimpleApp()
    ShowTipsDialog(None)
    app.MainLoop()

# ---------------------------------------------------------------------------
