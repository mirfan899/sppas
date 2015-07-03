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

import wx
import random

from wxgui.ui.labelctrl import LabelCtrl, spEVT_LABEL_LEFT, spEVT_LABEL_RIGHT
from annotationdata.label.label import Label
from annotationdata.label.text import Text

# ----------------------------------------------------------------------------


class LabelCtrlDemo(wx.Window):

    def __init__(self, parent, id):
        wx.Window.__init__(self, parent, id)
        self.SetBackgroundColour(wx.WHITE)

        wx.StaticText(self, -1, "Click on the following buttons to test Label functionalities:", pos=(10,10))

        self.b1 = wx.Button(self, -1, " Color ", (10,30))
        self.b2 = wx.Button(self, -1, "Position", (110, 30))
        self.b3 = wx.Button(self, -1, " Size ", (210, 30))
        self.b4 = wx.Button(self, -1, " Text", (10, 70))
        self.b5 = wx.Button(self, -1, " Font ", (110, 70))
        self.b6 = wx.Button(self, -1, " Align ", (210, 70))

        t1 = Text("Ambiguous", 0.6)
        t2 = Text("Alternative", 0.4)
        l = Label()
        l.AddValue(t1)
        l.AddValue(t2)

        self.l1 = LabelCtrl(self, id=-1, pos=(10,120),  size=wx.Size(100,40), label=l)
        self.l1.SetAlign(wx.ALIGN_CENTRE)
        self.l1.Refresh()
        self.l2 = LabelCtrl(self, id=-1, label=Label("label 2 is a long long label."))
        self.l2.MoveWindow(pos=(150,110), size=wx.Size(100,40))
        self.l2.Refresh()

        self.Bind(spEVT_LABEL_LEFT, self.OnLabelLeftClick)

        self.Bind(wx.EVT_BUTTON, self.repaint1, self.b1)
        self.Bind(wx.EVT_BUTTON, self.repaint2, self.b2)
        self.Bind(wx.EVT_BUTTON, self.repaint3, self.b3)
        self.Bind(wx.EVT_BUTTON, self.repaint4, self.b4)
        self.Bind(wx.EVT_BUTTON, self.repaint5, self.b5)
        self.Bind(wx.EVT_BUTTON, self.repaint6, self.b6)



    def OnLabelLeftClick(self, event):
        l = event.GetEventObject()
        self.GetTopLevelParent().GetStatusBar().SetStatusText('Label clicked: %s'%l.GetValue())


    def repaint1(self, event):
        """ Color. """
        (r,g,b) = random.sample(range(170,245),  3)
        (a,d,c) = random.sample(range(5,160),  3)
        self.l1.SetColours(wx.Colour(r,g,b),wx.Colour(a,d,c))
        self.l2.SetColours(wx.Colour(r,g,b),wx.Colour(a,d,c))
        self.l1.Refresh()
        self.l2.Refresh()


    def repaint2(self, event):
        """ Position. """
        x1,x2 = random.sample(range(20,300),  2)
        y1,y2 = random.sample(range(100,180),  2)
        self.l1.MoveWindow(wx.Point(x1,y1),self.l1.GetSize())
        self.l2.MoveWindow(wx.Point(x2,y2),self.l2.GetSize())
        self.l1.Refresh()
        self.l2.Refresh()
        self.GetTopLevelParent().GetStatusBar().SetStatusText('Move ok.')


    def repaint3(self, event):
        """ Size. """
        x1,x2 = random.sample(range(40,140),  2)
        y1,y2 = random.sample(range(10,40),  2)
        self.l1.MoveWindow(self.l1.GetPosition(),wx.Size(x1,y1))
        self.l2.MoveWindow(self.l2.GetPosition(),wx.Size(x2,y2))
        self.l1.Refresh()
        self.l2.Refresh()
        self.GetTopLevelParent().GetStatusBar().SetStatusText('re-Size.')


    def repaint4(self, event):
        """ Text. """
        text = ['blah blah 1', 'blah blah 2', 'blah blah 3', 'toto 1', 'toto 2', 'toto 3', 'label 1', 'label 2', 'label 3', 'label rouge']
        i,j = random.sample(range(0,9),2)#[0]
        self.l1.SetValue(Label(text[i]))
        self.l2.SetValue(Label(text[j]))
        self.l1.Refresh()
        self.l2.Refresh()


    def repaint5(self, event):
        """ Font. """
        data = wx.FontData()
        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data   = dlg.GetFontData()
            font   = data.GetChosenFont()
            color  = data.GetColour()
            self.l1.SetFont(font)
            self.l2.SetFont(font)
        dlg.Destroy()
        self.l1.Refresh()
        self.l2.Refresh()


    def repaint6(self, event):
        """ Align. """
        a = random.sample(range(0,3),  1)[0]
        if a == 0:
            self.l1.SetAlign( wx.ALIGN_LEFT )
            self.l2.SetAlign( wx.ALIGN_LEFT )
            self.GetTopLevelParent().GetStatusBar().SetStatusText('Left alignment.')
        elif a == 1:
            self.l1.SetAlign( wx.ALIGN_RIGHT )
            self.l2.SetAlign( wx.ALIGN_RIGHT )
            self.GetTopLevelParent().GetStatusBar().SetStatusText('Right alignment.')
        else:
            self.l1.SetAlign( wx.ALIGN_CENTRE )
            self.l2.SetAlign( wx.ALIGN_CENTRE )
            self.GetTopLevelParent().GetStatusBar().SetStatusText('Center alignment.')
        self.l1.Refresh()
        self.l2.Refresh()

# ----------------------------------------------------------------------------


class LabelCtrlFrame(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, pos=wx.DefaultPosition, size=wx.Size(440, 340))

        p = wx.Panel(self, -1)

        hbox = wx.BoxSizer( wx.VERTICAL )
        w = LabelCtrlDemo(p, -1)
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


