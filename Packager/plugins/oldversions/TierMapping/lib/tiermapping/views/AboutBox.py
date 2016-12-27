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


class AboutBox( wx.AboutDialogInfo ):

    def __init__(self):

        wx.AboutDialogInfo.__init__(self)
        description = """"""

        licence = """TierMapping is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.

TierMapping is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA"""

#         _icon = wx.EmptyIcon()
#         _icon.CopyFromBitmap(wx.Bitmap(APP_ICON, wx.BITMAP_TYPE_ANY))
#         self.SetIcon(_icon)
        self.SetName('TierMapping')
        self.SetVersion('0.1')
        self.SetDescription(description)
        self.SetCopyright('(C) 2014 - Tatsuya Watanabe')
        self.SetLicence(licence)
        self.AddDeveloper('Tatsuya Watanabe')
        self.AddDocWriter('Tatsuya Watanabe')
        self.AddArtist('Oxygen icon set,\nGimp')
