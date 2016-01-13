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
import threading
import itertools
import os

import annotationdata.io

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MappingThread(threading.Thread):

    def __init__(self, infiles, outfiles, mappings, dialog=None):
        threading.Thread.__init__(self)
        self.infiles = infiles
        self.outfiles = outfiles
        self.mappings = mappings
        self.dialog = dialog
        self.start()

    def run(self):
        self.dialog.SetGaugeRange(len(self.infiles))
        for pos, inputfile, outputfile in zip(itertools.count(), self.infiles, self.outfiles):
            base = os.path.basename(inputfile)
            wx.CallAfter(self.dialog.Update, pos=pos, top=base)
            try:
                transcription = annotationdata.io.read(inputfile)
            except Exception as e:
                wx.CallAfter(self.dialog.Update,
                             pos=pos,
                             top=base,
                             bottom=u"Error: could not read {0}\n {1}\n".format(inputfile, e)
                             )
                continue
            for mapping in self.mappings:
                source = mapping.GetSourceTier()
                tier = transcription.Find(source)
                if not tier:
                    wx.CallAfter(self.dialog.Update,
                                 pos=pos,
                                 top=base,
                                 bottom=u"Warning: '{0}' not found in {1}\n".format(source, base)
                                 )
                    continue
                name = mapping.GetName()
                new_tier = tier.Copy()
                new_tier.Name = name
                for i, a in enumerate(tier):
                    repl = mapping.get(a.TextValue, "")
                    new_tier[i].TextValue = repl
                transcription.Append(new_tier)

            try:
                annotationdata.io.write(outputfile, transcription)
            except Exception as e:
                wx.CallAfter(self.dialog.Update,
                             pos=pos,
                             top=base,
                             bottom="Error: could not save {0}\n {1}\n".format(base, e)
                             )
                continue

        wx.CallAfter(self.dialog.Update, pos=None)



class ProgressBar(wx.Dialog):

    def __init__(self, parent, message="", title="", range=100):
        style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent,
                           title=title,
                           size=(400, 300),
                           style=style)
        # widgets
        self.top = wx.StaticText(self, label=message)
        self.gauge = wx.Gauge(self, range=range)
        # self.bottom = wx.StaticText(self, label=message)
        self.bottom = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_MULTILINE)
        # Create ok/cancel buttons
        btnSizer = self.CreateStdDialogButtonSizer(wx.OK)
        self.ok = btnSizer.GetAffirmativeButton()
        self.ok.Enable(False)
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.top, flag=wx.EXPAND|wx.ALL, border=10)
        sizer.Add(self.gauge, flag=wx.EXPAND|wx.ALL, border=10)
        sizer.Add(self.bottom, proportion=1, flag=wx.EXPAND|wx.ALL, border=10)
        sizer.Add(btnSizer, flag=wx.EXPAND|wx.ALL, border=10)
        self.SetSizer(sizer)
        self.Center()
        self.Show()
        # bind events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.ok.Bind(wx.EVT_BUTTON, self.OnOk)

    def OnClose(self, event):
        event.Veto()

    def OnOk(self, event):
        self.Destroy()

    def SetGaugeRange(self, value):
        self.gauge.SetRange(value)

    def Pulse(self):
        self.gauge.Pulse()

    def Update(self, pos, top="", bottom="", pulse=False, max_value=None):
        if pos is None:
            max_value = self.gauge.GetRange()
            self.gauge.SetValue(max_value)
            self.top.SetLabel("Process completed")
            self.ok.Enable(True)
            return

        if pulse:
            self.top.SetLabel(top)
            self.gauge.Pulse()
            return

        if max_value:
            self.gauge.SetRange(max_value)

        self.gauge.SetValue(pos)
        self.top.SetLabel(top)
        if bottom:
            self.bottom.AppendText(bottom)
