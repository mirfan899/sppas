#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Tatsuya Watanabe
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.

import os
import wx
import wx.combo



class ImportPluginDialog(wx.Dialog):

    def __init__(self, *args, **kwargs):
        style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        wx.Dialog.__init__(self, style=style, size=(-1, 160),title="Import plugin", *args, **kwargs)
        self.InitUI()
        self.Center()

    def InitUI(self):
        # Widgets
        self.combo = MyCombo(self)
        self.label_combo = wx.StaticText(self, label='Plugin directory:')
        # Layout
        btnSizer = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.label_combo, flag=wx.EXPAND|wx.ALL^wx.RIGHT, border=5)
        hbox.Add(self.combo, proportion=1, flag=wx.ALIGN_CENTER, border=5)
        sizer.Add(hbox, flag=wx.EXPAND|wx.ALL, border=10)
        sizer.Add((-1, -1), proportion=1, flag=wx.EXPAND)
        sizer.Add(btnSizer, flag=wx.ALIGN_RIGHT|wx.BOTTOM, border=5)
        self.SetSizer(sizer)

    def GetPluginDir(self):
        return self.combo.GetValue()

class MyCombo(wx.combo.ComboCtrl):

    def __init__(self, *args, **kw):
        validator = TextObjectValidator()
        wx.combo.ComboCtrl.__init__(self, validator=validator,*args, **kw)

        # make a custom bitmap showing "..."
        bw, bh = 15, 16
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

    # Overridden from ComboCtrl to avoid assert since there is no ComboPopup
    def DoSetPopupControl(self, popup):
        pass

    def OnButtonClick(self):
        path = ""
        name = ""
        if self.GetValue():
            path, name = os.path.split(self.GetValue())
        dlg = wx.DirDialog(self, message="Select plugin directory: ", defaultPath=path, name=name,
                             style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())
        dlg.Destroy()
        self.SetFocus()



class TextObjectValidator(wx.PyValidator):

     def __init__(self):
         wx.PyValidator.__init__(self)

     def Clone(self):
         return TextObjectValidator()

     def Validate(self, win):
         textCtrl = self.GetWindow()
         text = textCtrl.GetValue()
         cfg = os.path.join(text, 'plugin.cfg')

         if not os.path.exists(cfg):
             wx.MessageBox("Plugin not found in %s" % text, "Error")
             textCtrl.SetFocus()
             textCtrl.Refresh()
             return False
         else:
             textCtrl.SetBackgroundColour(
                 wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
             textCtrl.Refresh()
             return True

     def TransferToWindow(self):
         """ Transfer data from validator to window.

             The default implementation returns False, indicating that an error
             occurred.  We simply return True, as we don't do any data transfer.
         """
         return True # Prevent wxDialog from complaining.


     def TransferFromWindow(self):
         """ Transfer data from window to validator.

             The default implementation returns False, indicating that an error
             occurred.  We simply return True, as we don't do any data transfer.
         """
         return True # Prevent wxDialog from complaining.

if __name__ == '__main__':
    app = wx.App(False)
    dlg = ImportPluginDialog(None)
    dlg.ShowModal()
    print dlg.GetConfigData()
    dlg.Destroy()
    app.MainLoop()
