#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Tatsuya Watanabe
#
# This file is part of TierMapping.
#
# TierMapping is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TierMapping is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TierMapping.  If not, see <http://www.gnu.org/licenses/>.

import os

import wx
import wx.combo


class OutputDir(wx.combo.ComboCtrl):
    def __init__(self, *args, **kw):
        wx.combo.ComboCtrl.__init__(self, *args, **kw)

        # make a custom bitmap showing "..."
        bw, bh = 14, 16
        bmp = wx.EmptyBitmap(bw,bh)
        dc = wx.MemoryDC(bmp)

        # clear to a specific background colour
        bgcolor = wx.Colour(255,254,255)
        dc.SetBackground(wx.Brush(bgcolor))
        dc.Clear()

        # draw the label onto the bitmap
        label = "..."
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        tw,th = dc.GetTextExtent(label)
        dc.DrawText(label, (bw-tw)/2, (bw-tw)/2)
        del dc

        # now apply a mask using the bgcolor
        bmp.SetMaskColour(bgcolor)

        # and tell the ComboCtrl to use it
        self.SetButtonBitmaps(bmp, True)
        default = os.path.expanduser('~')
        self.SetValue(default)

    def OnButtonClick(self):
        path = ""
        name = ""
        if self.GetValue():
            path, name = os.path.split(self.GetValue())
        dlg = wx.DirDialog(self, message="Choose Output directory", defaultPath=path, name=name,
                             style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())
        dlg.Destroy()
        self.SetFocus()

    # Overridden from ComboCtrl to avoid assert since there is no ComboPopup
    def DoSetPopupControl(self, popup):
        pass
