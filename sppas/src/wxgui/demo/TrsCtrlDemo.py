# coding=UTF8
# Copyright (C) 2014  Brigitte Bigi
#
# This file is part of DataEditor.
#
# DataEditor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DataEditor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DataEditor.  If not, see <http://www.gnu.org/licenses/>.


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import random
import wx
import logging

from wxgui.ui.trsctrl import TranscriptionCtrl
import annotationdata.io

# ----------------------------------------------------------------------------

import os
trs = annotationdata.io.read( os.path.join(os.path.dirname(os.path.abspath(__file__)),"oriana1-merge.TextGrid"))

# ----------------------------------------------------------------------------


class TrsCtrlDemo(wx.Window):

    def __init__(self, parent, id):
        wx.Window.__init__(self, parent, id)
        self.SetBackgroundColour(wx.WHITE)

        wx.StaticText(self, -1, "Click on the following buttons to test functions:", pos=(10,10))

        self.b1 = wx.Button(self, -1, " Pane ", (10,40))
        self.b2 = wx.Button(self, -1, " Scroll ", (110, 40))
        self.b3 = wx.Button(self, -1, " Size ", (210, 40))
        self.b4 = wx.Button(self, -1, " Font ", (310, 40))

        self.trsctrl = TranscriptionCtrl(self, id=-1, pos=(10,80),  size=wx.Size(400,160), trs=trs)
        self.trsctrl.SetTime(0.0,2.0)

        self.Bind(wx.EVT_BUTTON, self.repaint1, self.b1)
        self.Bind(wx.EVT_BUTTON, self.repaint2, self.b2)
        self.Bind(wx.EVT_BUTTON, self.repaint3, self.b3)
        self.Bind(wx.EVT_BUTTON, self.repaint4, self.b4)


    def repaint1(self, event):
        """ Pane. """
        w = random.sample(range(10,200), 1)[0]
        self.trsctrl.SetPaneWidth( w )
        p = random.sample(range(0,3), 1)[0]
        if p==0:
            self.trsctrl.SetPanePosition( wx.ALIGN_LEFT )
        elif p==1:
            self.trsctrl.SetPanePosition( wx.ALIGN_RIGHT )
        else:
            self.trsctrl.SetPanePosition( wx.ALIGN_CENTRE )


    def repaint2(self, event):
        """ Period. """
        s = float(random.sample(range(0,5), 1)[0])
        d = float(random.sample(range(1,20), 1)[0])/10.
        self.GetTopLevelParent().GetStatusBar().SetStatusText('New period: %f,%f'%(s,s+d))
        self.trsctrl.SetTime(s,s+d)


    def repaint3(self, event):
        """ Vertical Zoom. """
        z = random.sample(range(5,50), 1)[0]
        if self.trsctrl.GetSize()[1] > 140:
            z = 1.0 - z/100.0
        else:
            z = 1.0 + z/100.0

        logging.debug('Vertical zoom: %d'%z)
        self.trsctrl.VertZoom( z )


    def repaint4(self, event):
        """ Font. """
        data = wx.FontData()
        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data   = dlg.GetFontData()
            font   = data.GetChosenFont()
            color  = data.GetColour()
            self.trsctrl.SetFont(font)
        dlg.Destroy()


# ---------------------------------------------------------------------------


class TrsCtrlFrame(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, pos=wx.DefaultPosition, size=wx.Size(440, 380))

        p = wx.Panel(self, -1)

        hbox = wx.BoxSizer( wx.VERTICAL )
        w = TrsCtrlDemo(p, -1)
        hbox.Add(w, 1, wx.ALL|wx.EXPAND, border=5)
        hbox.Add(wx.StaticLine(p), 0, wx.ALL|wx.EXPAND, border=1)
        ButtonClose = wx.Button(p, wx.ID_CLOSE)
        hbox.Add(ButtonClose, 0, wx.ALL|wx.ALIGN_RIGHT, border=5)

        p.SetSizer( hbox )

        self.Bind(wx.EVT_BUTTON, self.OnClose,id=wx.ID_CLOSE)

        self.statusbar = self.CreateStatusBar()
        self.Centre()


    def OnClose(self, event):
        self.Destroy()

# ----------------------------------------------------------------------------

