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
import wx.lib.mixins.listctrl as listmix


class MyList(wx.ListCtrl, listmix.CheckListCtrlMixin):

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('style'):
            kwargs['style'] = kwargs['style'] | wx.LC_REPORT
        else:
            kwargs['style'] = wx.LC_REPORT
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.CheckListCtrlMixin.__init__(self)

    def AppendItem(self, row, check=True):
        """
        Append row to the list.
        Args:
            row (tuple)
        """
        index = self.Append(row)
        self.CheckItem(index, check)

    def GetCheckedItems(self):
        """
        Returs:
            (list)
        """
        return [i for i in range(self.GetItemCount()) if self.IsChecked(i)]

    def GetSelectedItems(self):
        """
        Returs:
            (list)
        """
        selection = []
        for i in range(self.GetItemCount()):
            item = self.GetItem(i)
            if item.GetState() & wx.LIST_STATE_SELECTED:
                selection.append(i)
        return selection
