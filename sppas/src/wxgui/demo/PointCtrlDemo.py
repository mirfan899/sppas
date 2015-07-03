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

from wxgui.ui.pointctrl import PointCtrl, spEVT_RESIZING, spEVT_MOVING, spEVT_MOVED, spEVT_POINT_LEFT

# ----------------------------------------------------------------------------

class PointCtrlDemo(wx.Window):

    def __init__(self, parent, id):

        wx.Window.__init__(self, parent, id)
        self.SetBackgroundColour(wx.WHITE)

        wx.StaticText(self, -1, "Click on the following buttons to test Time Point functionalities:", pos=(10,10))

        self.b1 = wx.Button(self, -1, "Color", (10,30))
        self.b2 = wx.Button(self, -1, "Move", (110, 30))
        self.s1 = wx.Button(self, -1, "Small Radius", (210, 30))
        self.s2 = wx.Button(self, -1, "Large Radius", (310, 30))

        self.w1 = PointCtrl(self, id=-1, pos=(80,70), size=wx.Size(10, 40))
        #self.w1.Refresh()
        self.w2 = PointCtrl(self, id=-1)
        self.w2.MoveWindow(pos=(200,70), size=wx.Size(10, 40))
        #self.w2.Refresh()

        wx.StaticText(self, -1, "- Move each point with: LEFT BUTTON + MOUSE MOVING", pos=(20,130))
        wx.StaticText(self, -1, "- Adjust the radius with: SHIFT KEY + LEFT BUTTON + MOUSE MOVING ", pos=(20, 150))
        wx.StaticText(self, -1, "The Radius represents the vagueness of the point. ", pos=(20, 200))

        self.Bind(spEVT_RESIZING,   self.resizing)
        self.Bind(spEVT_MOVING,     self.moving)
        self.Bind(spEVT_MOVED,      self.moved)
        self.Bind(spEVT_POINT_LEFT, self.leftclick)

        self.Bind(wx.EVT_BUTTON, self.repaint1, self.b1)
        self.Bind(wx.EVT_BUTTON, self.repaint2, self.b2)
        self.Bind(wx.EVT_BUTTON, self.repaint3, self.s1)
        self.Bind(wx.EVT_BUTTON, self.repaint4, self.s2)



    def resizing(self,event):
        p = event.GetEventObject()
        (x,y) = event.pos
        (w,h) = event.size
        # accept new size... (then, pos must be changed!)
        p.MoveWindow(event.pos,event.size)
        #p.Refresh()
        if p==self.w1:
            self.GetTopLevelParent().GetStatusBar().SetStatusText('First point is resized: x=%d, w=%d'%(x,w))
        else:
            self.GetTopLevelParent().GetStatusBar().SetStatusText('Second point is resized: x=%d, w=%d'%(x,w))


    def moving(self,event):
        p = event.GetEventObject()
        (x,y) = event.pos
        # accept new pos...
        p.Move(event.pos)
        if p==self.w1:
            self.GetTopLevelParent().GetStatusBar().SetStatusText('First point is moving: %d'%x)
        else:
            self.GetTopLevelParent().GetStatusBar().SetStatusText('Second point is moving: %d'%x)


    def moved(self,event):
        p = event.GetEventObject()
        (x,y) = event.pos
        if p==self.w1:
            self.GetTopLevelParent().GetStatusBar().SetStatusText('First point moved to: %d'%x)
        else:
            self.GetTopLevelParent().GetStatusBar().SetStatusText('Second point moved to: %d'%x)


    def leftclick(self, event):
        p = event.GetEventObject()
        if p==self.w1:
            self.GetTopLevelParent().GetStatusBar().SetStatusText('First point clicked')
        else:
            self.GetTopLevelParent().GetStatusBar().SetStatusText('Second point clicked')


    def repaint1(self, event):
        (r,g,b) = random.sample(range(170,245),  3)
        (a,d,c) = random.sample(range(5,160),  3)
        self.w1.SetColours(wx.Colour(a,d,c),wx.Colour(r,g,b))
        #self.w1.Refresh()
        (r,g,b) = random.sample(range(170,245),  3)
        (a,d,c) = random.sample(range(5,160),  3)
        self.w2.SetColours(wx.Colour(r,g,b),wx.Colour(a,d,c))
        #self.w2.Refresh()
        self.GetTopLevelParent().GetStatusBar().SetStatusText('Color changed successfully.')


    def repaint2(self, event):
        p1,p2 = random.sample(range(20,300),  2)
        self.w1.Move(wx.Point(p1,70))
        self.w2.Move(wx.Point(p2,70))
        #self.w1.Refresh()
        #self.w2.Refresh()
        self.GetTopLevelParent().GetStatusBar().SetStatusText('Points moved successfully.')


    def repaint3(self, event):
        p1,p2 = random.sample(range(1,20),  2)
        self.w1.SetWidth(p1)
        self.w2.SetWidth(p2)
        #self.w1.Refresh()
        #self.w2.Refresh()
        self.GetTopLevelParent().GetStatusBar().SetStatusText('Small radius.')


    def repaint4(self, event):
        p1,p2 = random.sample(range(21,40),  2)
        self.w1.SetWidth(p1)
        self.w2.SetWidth(p2)
        #self.w1.Refresh()
        #self.w2.Refresh()
        self.GetTopLevelParent().GetStatusBar().SetStatusText('Large radius.')


# ----------------------------------------------------------------------------


class PointCtrlFrame(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, pos=wx.DefaultPosition, size=wx.Size(440, 340))

        p = wx.Panel(self, -1)

        hbox = wx.BoxSizer( wx.VERTICAL )
        w = PointCtrlDemo(p, -1)
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


