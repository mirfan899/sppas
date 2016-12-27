#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Tatsuya Watanabe
#
# This file is part of MarsaTagPlugin.
#
# MarsaTagPlugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MarsaTagPlugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MarsaTagPlugin.  If not, see <http://www.gnu.org/licenses/>.


import os
import json

import wx
import wx.combo

from MarsaTagProcess import MarsaTagProcess



class MarsaTagFrame(wx.Frame):

    def __init__(self, inputfiles=None, cfgfile="", *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.inputfiles = inputfiles
        self.cfgfile = cfgfile
        self.process = None
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

        ok = self.InitProcess()
        if not ok:
            wx.MessageBox("MarsaTag not found", "Error")
            self.Destroy()
        else:
            self.RunMarsaTag()
            self.timer.Start(2000)

    def InitProcess(self):
        if not os.path.exists(self.cfgfile):
            command = self.ShowImportDialog()
        else:
            try:
                command = self.LoadCommand()
            except:
                wx.MessageBox("MarsaTag not found", "Error")
                command = self.ShowImportDialog()

        if not command:
            return False

        try:
            process = MarsaTagProcess(command)
        except:
            return False
        else:
            self.SaveCommand({'command':command})
            self.process = process
            return True


    def SaveCommand(self, command):
        with open(self.cfgfile, "w") as fp:
            try:
                json.dump(command, fp, encoding="utf-8")
            except Exception as e:
                pass


    def LoadCommand(self):
        with open(self.cfgfile, "r") as fp:
            tmp = json.load(fp, encoding="utf-8")
        return tmp['command']


    def ShowImportDialog(self):
        dialog = ImportDialog(self)
        command = None
        if dialog.ShowModal() == wx.ID_OK:
            command = dialog.GetConfigData()
        dialog.Destroy()
        return command


    def RunMarsaTag(self):
        if self.process:
            self.process.Run(self.inputfiles)


    def OnDestroy(self, event):
        if self.process:
            self.process.Terminate()
            event.Skip()


    def OnTimer(self, event):
        if not self.process.IsRunning():
            self.Destroy()



class ImportDialog(wx.Dialog):

    def __init__(self, *args, **kwargs):
        style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        wx.Dialog.__init__(self, style=style,
                                 size=(-1, 160),
                                 title="Import MarsaTag",
                                 *args, **kwargs)
        self.InitUI()
        self.Center()

    def InitUI(self):
        # Widgets
        self.combo = MyCombo(self)
        self.label_combo = wx.StaticText(self, label='Select MarsaTag installation directory: ')
        # Layout
        btnSizer = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.label_combo, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(self.combo, flag=wx.EXPAND|wx.ALL, border=5)
        sizer.Add(vbox, flag=wx.EXPAND|wx.ALL, border=10)
        sizer.Add((-1, -1), proportion=1, flag=wx.EXPAND)
        sizer.Add(btnSizer, flag=wx.ALIGN_RIGHT|wx.BOTTOM, border=5)
        self.SetSizer(sizer)

    def GetConfigData(self):
        plugin_dir = self.combo.GetValue()
        jar = os.path.join(plugin_dir, 'lib', 'MarsaTag-UI.jar')
        return (
                'java -Xms300M -Xmx600M -Dortolang.home="{0}" '
                '-jar "{1}" '
                '-g -pt TokensAlign -r praat-textgrid -e UTF8 -w praat-textgrid '
                '-oe UTF8 -rm-ext -ox .pos.TextGrid'.format(plugin_dir, jar)
                )



class MyCombo(wx.combo.ComboCtrl):

    def __init__(self, *args, **kw):
        wx.combo.ComboCtrl.__init__(self,
                                    validator=MarsaTagInstallationValidator(),
                                    *args, **kw)
        bw, bh = 15, 16
        bmp = wx.EmptyBitmap(bw,bh)
        dc = wx.MemoryDC(bmp)

        bgcolor = wx.Colour(255,254,255)
        dc.SetBackground(wx.Brush(bgcolor))
        dc.Clear()

        label = "..."
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        tw,th = dc.GetTextExtent(label)
        dc.DrawText(label, (bw-tw)/2, (bw-tw)/2)
        del dc

        bmp.SetMaskColour(bgcolor)
        self.SetButtonBitmaps(bmp, True)

    def DoSetPopupControl(self, popup):
        pass

    def OnButtonClick(self):
        path = ""
        name = ""
        if self.GetValue():
            path, name = os.path.split(self.GetValue())
        dlg = wx.DirDialog(self,
                           message="MarsaTag installation directory",
                           defaultPath=path,
                           name=name,
                           style=wx.DD_DEFAULT_STYLE
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())
        dlg.Destroy()
        self.SetFocus()



class MarsaTagInstallationValidator(wx.PyValidator):

     def __init__(self):
         wx.PyValidator.__init__(self)

     def Clone(self):
         return MarsaTagInstallationValidator()

     def Validate(self, win):
         textCtrl = self.GetWindow()
         text = textCtrl.GetValue()
         jar = os.path.join(text, 'lib', 'MarsaTag-UI.jar')
         if not os.path.exists(jar):
             wx.MessageBox("MarsaTag not found", "Error")
             textCtrl.SetFocus()
             textCtrl.Refresh()
             return False
         else:
             textCtrl.SetBackgroundColour(
                 wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
             textCtrl.Refresh()
             return True

     def TransferToWindow(self):
         return True

     def TransferFromWindow(self):
         return True
