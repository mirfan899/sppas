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
import wx.grid

from tiermapping.images import IMG_FIND


class MappingTable(wx.Frame):

    def __init__(self, parent, mapping, *args, **kwargs):
        wx.Frame.__init__(self, parent, *args, **kwargs)
        n_row = len(mapping)
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(n_row, 2)
        self.grid.SetColLabelValue(0, mapping.GetSourceTier())
        self.grid.SetColLabelValue(1, mapping.GetName())
        for i, item in enumerate(mapping.items()):
            self.grid.SetRowLabelValue(i, str(i+1))
            self.grid.SetCellValue(i, 0, item[0])
            self.grid.SetCellValue(i, 1, item[1])

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(IMG_FIND, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle('TierMapping')
