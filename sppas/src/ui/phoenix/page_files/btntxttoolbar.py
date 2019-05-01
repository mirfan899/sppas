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
from sppas.src.ui.phoenix.windows.button import BitmapTextButton

# ----------------------------------------------------------------------------


class BitmapTextToolbar(sppasPanel):
    """Panel imitating the behaviors of a toolbar.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """
    def __init__(self, parent, orient=wx.HORIZONTAL):
        super(BitmapTextToolbar, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.NO_BORDER | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=wx.PanelNameStr)

        # Focus Color&Style
        self._fs = wx.PENSTYLE_SOLID
        self._fw = 3
        self._fc = wx.Colour(128, 128, 128, 128)

        self.SetSizer(wx.BoxSizer(orient))
        #self.SetMinSize((-1, 32))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def get_button(self, name):
        for b in self.GetSizer().GetChildren():
            if b.GetName() == name:
                return b

        return None

    # -----------------------------------------------------------------------

    def AddButton(self, icon, text="", tooltip=None, activated=True):
        btn = self.create_button(text, icon)
        # btn.SetToolTip(tooltip)
        btn.Enable(activated)
        if self.GetSizer().GetOrientation() == wx.HORIZONTAL:
            self.GetSizer().Add(btn, 1, wx.LEFT | wx.EXPAND, 0)
        else:
            self.GetSizer().Add(btn, 0, wx.LEFT | wx.EXPAND, 0)
        return btn

    def AddSpacer(self, proportion=1):
        self.GetSizer().AddStretchSpacer(proportion)

    def AddText(self, text=""):
        st = wx.StaticText(self, label=text)
        self.GetSizer().Add(st, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 6)

    # -----------------------------------------------------------------------

    def set_focus_color(self, value):
        self._fc = value

    def set_focus_penstyle(self, value):
        self._fs = value

    def set_focus_width(self, value):
        self._fw = value

    # -----------------------------------------------------------------------

    def create_button(self, text, icon):
        btn = BitmapTextButton(self, label=text, name=icon)
        btn.FocusStyle = self._fs
        btn.FocusWidth = self._fw
        btn.FocusColour = self._fc
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = 12
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize((32, 32))

        return btn

