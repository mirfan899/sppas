# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.
        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
        This banner notice must not be removed.
        ---------------------------------------------------------------------

    src.ui.phoenix.filespck.btntxttoolbar.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Toolbar with button/text buttons.

"""

import logging
import os
import wx

from sppas.src.ui.phoenix.windows.panel import sppasPanel
from sppas.src.ui.phoenix.windows.button import sppasBitmapTextButton  # sub-class GenButton
from sppas.src.ui.phoenix.windows.button import sppasBitmapButton  # sub-class GenButton
from sppas.src.ui.phoenix.windows.button import BitmapTextButton   # custom button


# ----------------------------------------------------------------------------


class BitmapTextToolbar(sppasPanel):
    """Panel imitating the behaviors of a toolbar.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """
    def __init__(self, parent):
        super(BitmapTextToolbar, self).__init__(
            parent, id=wx.ID_ANY,
            pos=wx.DefaultPosition, size=wx.DefaultSize,
            style=wx.NO_BORDER, name=wx.PanelNameStr)

        self.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        self.SetMinSize((-1, 32))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def AddButton(self, icon, text="", tooltip=None, activated=True):
        btn = self.create_button(icon, text)
        # btn.SetToolTip(tooltip)
        btn.Enable(activated)
        self.GetSizer().Add(btn, 2, wx.LEFT | wx.EXPAND, 0)
        return btn

    def AddSpacer(self, proportion=1):
        self.GetSizer().AddStretchSpacer(proportion)

    def AddText(self, text=""):
        st = wx.StaticText(self, label=text)
        self.GetSizer().Add(st, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 8)

    # -----------------------------------------------------------------------

    def create_button(self, icon, text):
        btn = sppasBitmapTextButton(self, label=text, name=icon)
        """btn.FocusStyle = wx.PENSTYLE_SOLID
        btn.FocusWidth = 3
        btn.FocusColour = wx.Colour(220, 220, 120)
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = 12
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()"""
        btn.SetMinSize((64, -1))
        return btn

    # -----------------------------------------------------------------------

    def get_button(self, name):
        for b in self.GetSizer().GetChildren():
            if b.GetName() == name:
                return b

        return None
