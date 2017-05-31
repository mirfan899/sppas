#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
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
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------

# ----------------------------------------------------------------------------

import logging
import random
import wx

from sppas.src.wxgui.ui.timerulerctrl import TimeRulerCtrl
from sppas.src.wxgui.ui.spControl import spEVT_CTRL_SELECTED

# ----------------------------------------------------------------------------


class RulerCtrlDemo(wx.Window):

    def __init__(self, parent, id):
        wx.Window.__init__(self, parent, id)
        self.SetBackgroundColour(wx.WHITE)

        wx.StaticText(self, -1, "Click on the following buttons to test ruler functionalities:", pos=(10,10))
        self.b1 = wx.Button(self, -1, " Colors ", (10,40))
        self.b2 = wx.Button(self, -1, "Zoom/Scroll", (110, 40))
        self.b3 = wx.Button(self, -1, " Size ", (210, 40))
        self.b4 = wx.Button(self, -1, " Flip ", (310, 40))

        logging.debug(" ... ruler: Init")
        self.rulerctrl = TimeRulerCtrl(self, id=-1, pos=(10,80),  size=wx.Size(400,28))
        # indicators on the ruler:
        logging.debug(" ... ruler: SetTime")
        self.rulerctrl.SetTime( 0.0,2.0 )
        logging.debug(" ... ruler: SetPlayerIndicatorValue")
        self.rulerctrl.SetPlayerIndicatorValue( 0.0 )
        logging.debug(" ... ruler: SetSelectionIndicatorValues")
        self.rulerctrl.SetSelectionIndicatorValues( 0.5, 1.5 )
        logging.debug(" ... ruler: SetDrawingParent")
        self.rulerctrl.SetDrawingParent(self)
        self.rulerctrl.SetBackgroundColour( wx.Colour(250,250,125) )
        self.rulerctrl.RequestRedraw()

        wx.StaticText(self, -1, "- A green arrow indicates the player position", pos=(20,170))
        wx.StaticText(self, -1, "- Two blue arrows indicate a time selection", pos=(20,190))

        self.Bind(wx.EVT_BUTTON, self.repaint1, self.b1)
        self.Bind(wx.EVT_BUTTON, self.repaint2, self.b2)
        self.Bind(wx.EVT_BUTTON, self.repaint3, self.b3)
        self.Bind(wx.EVT_BUTTON, self.repaint4, self.b4)

        self.Bind(spEVT_CTRL_SELECTED, self.OnSelect)


    def repaint1(self, event):
        """ Color. """
        (r,g,b) = random.sample(range(170,250),  3)
        self.rulerctrl.SetBackgroundColour( wx.Colour(r, g, b))
        self.rulerctrl.SetTicksColour( wx.Colour(r-100, g-100, b-100))
        self.rulerctrl.SetTextColour( wx.Colour(r-150, g-150, b-150))

    def repaint2(self, event):
        """ Zoom/Scroll. """
        s,e = random.sample(range(0,1000), 2)
        s = float(s)/100.0
        e = float(e)/100.0
        if s > e:
            t = s
            s = e
            e = t
        self.rulerctrl.SetTime(s,e)
        self.rulerctrl.SetPlayerIndicatorValue( s )
        self.rulerctrl.SetSelectionIndicatorValues( s+0.1, e-0.1 )

    def repaint3(self, event):
        """ Size. """
        h = random.sample(range(15,60),  1)[0]
        self.rulerctrl.MoveWindow( self.rulerctrl.GetPosition() , wx.Size(400,h))

    def repaint4(self, event):
        """ Flip. """
        self.rulerctrl.SetFlip( not self.rulerctrl.GetFlip() )

    def OnSelect(self, event):
        ctrl = event.GetEventObject()
        selected = event.value

# ---------------------------------------------------------------------------


class RulerCtrlFrame(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, pos=wx.DefaultPosition, size=wx.Size(440, 340))

        p = wx.Panel(self, -1)

        hbox = wx.BoxSizer( wx.VERTICAL )
        w = RulerCtrlDemo(p, -1)
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

