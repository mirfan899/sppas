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
#


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import random
import wx

from wxgui.ui.tierctrl import TierCtrl
import annotationdata.io

# ----------------------------------------------------------------------------

import os
trs = annotationdata.io.read( os.path.join(os.path.dirname(os.path.abspath(__file__)),"oriana1-merge.TextGrid"))

# ----------------------------------------------------------------------------


class TierCtrlDemo(wx.Window):

    def __init__(self, parent, id):
        wx.Window.__init__(self, parent, id)
        self.SetBackgroundColour(wx.WHITE)

        wx.StaticText(self, -1, "Click on the following buttons to test Tier functionalities:", pos=(10,10))

        self.b1 = wx.Button(self, -1, " Color ", (10,40))
        self.b2 = wx.Button(self, -1, "Zoom/Scroll", (110, 40))
        self.b3 = wx.Button(self, -1, " Tier Size ", (210, 40))
        self.b4 = wx.Button(self, -1, " Font ", (310, 40))

        tier = trs[2]
        tier.SetRadius(0.005)
        self.t1 = TierCtrl(self, id=-1, pos=(10,80),  size=wx.Size(400,30), tier=trs[2])
        self.t1.SetTime(1.5,2.5)
        self.t2 = TierCtrl(self, id=-1, pos=(10,115), size=wx.Size(400,30), tier=trs[3])
        self.t2.SetTime(1.5,2.5)

        self.Bind(wx.EVT_BUTTON, self.repaint1, self.b1)
        self.Bind(wx.EVT_BUTTON, self.repaint2, self.b2)
        self.Bind(wx.EVT_BUTTON, self.repaint3, self.b3)
        self.Bind(wx.EVT_BUTTON, self.repaint4, self.b4)


    def repaint1(self, event):
        """ Color. """
        (a,b,c) = random.sample(range(160,250),  3)
        (q,r,s) = random.sample(range(0,150),  3)
        self.t1.SetLabelColours(bgcolour=wx.Colour(a,b,c),fontnormalcolour=wx.Colour(q,r,s))
        self.t1.SetForegroundColour(wx.Colour(a,b,c))

        (a,b,c) = random.sample(range(120,220),  3)
        self.t2.SetLabelColours(bgcolour=wx.Colour(a,b,c))
        self.t2.SetForegroundColour(wx.Colour(a,b,c))


    def repaint2(self, event):
        """ Period. """
        s = float(random.sample(range(0,5), 1)[0])
        d = float(random.sample(range(1,20), 1)[0])/10.
        self.GetTopLevelParent().GetStatusBar().SetStatusText('New period: %f,%f'%(s,s+d))
        self.t1.SetTime(s,s+d)
        self.t2.SetTime(s,s+d)

    def repaint3(self, event):
        """ Size. """
        y1,y2 = random.sample(range(15,30),  2)
        self.t1.MoveWindow(self.t1.GetPosition(), wx.Size(400,y1))
        self.t2.MoveWindow(self.t2.GetPosition(), wx.Size(400,y2))
        self.GetTopLevelParent().GetStatusBar().SetStatusText('Tiers re-sized: %d'%y1)


    def repaint4(self, event):
        """ Font. """
        data = wx.FontData()
        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data   = dlg.GetFontData()
            font   = data.GetChosenFont()
            color  = data.GetColour()
            self.t1.SetFont(font)
            self.t2.SetFont(font)
        dlg.Destroy()


# ---------------------------------------------------------------------------


class TierCtrlFrame(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, pos=wx.DefaultPosition, size=wx.Size(440, 340))

        p = wx.Panel(self, -1)

        hbox = wx.BoxSizer( wx.VERTICAL )
        w = TierCtrlDemo(p, -1)
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
