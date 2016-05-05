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

import wx


class CSVImportDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)
        self.InitUI()
        self.Center()

    def InitUI(self):
        # Widgets
        label_encoding = wx.StaticText(self, label='Text Encoding:')
        self.encoding = wx.ComboBox(self , choices=('utf-8',), style=wx.CB_READONLY)
        self.encoding.SetStringSelection('utf-8')
        self.from_row = wx.SpinCtrl(self, min=1)
        # cancel/ok btn
        btnSizer = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
