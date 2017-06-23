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
# Imports
# ----------------------------------------------------------------------------

import random
import logging
import wx

from sppas.src.wxgui.ui.wavectrl import WaveCtrl
import sppas.src.audiodata.aio

# ----------------------------------------------------------------------------

import os
wavef = sppas.src.audiodata.aio.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"oriana1.wav"))

# ----------------------------------------------------------------------------


class WaveCtrlDemo(wx.Window):

    def __init__(self, parent, id):
        wx.Window.__init__(self, parent, id)
        self.SetBackgroundColour(wx.WHITE)

        wx.StaticText(self, -1, "Click on the following buttons to test functions:", pos=(10,10))

        self.b1 = wx.Button(self, -1, " Pane ", (10,40))
        self.b2 = wx.Button(self, -1, " Scroll ", (110, 40))
        self.b3 = wx.Button(self, -1, " Size ", (210, 40))

        self.wavectrl = WaveCtrl(self, id=-1, pos=(10,80),  size=wx.Size(400,100), audio=wavef)
        self.wavectrl.SetGradientBackground( True ) # Gradient bg
        self.wavectrl.SetTime(2.0,4.0)
        self.wavectrl.SetHandlesColour( wx.Colour(200, 100, 100) )

        self.Bind(wx.EVT_BUTTON, self.repaint1, self.b1)
        self.Bind(wx.EVT_BUTTON, self.repaint2, self.b2)
        self.Bind(wx.EVT_BUTTON, self.repaint3, self.b3)


    def repaint1(self, event):
        """ Pane. """
        p = random.sample(range(0,3),  1)[0]
        if p==0:
            self.wavectrl.SetPanePosition( wx.ALIGN_LEFT )
        elif p==1:
            self.wavectrl.SetPanePosition( wx.ALIGN_RIGHT )
        else:
            self.wavectrl.SetPanePosition( wx.ALIGN_CENTRE )


    def repaint2(self, event):
        """ Period. """
        s = float(random.sample(range(0,5), 1)[0])
        d = float(random.sample(range(1,20), 1)[0])/10.
        self.GetTopLevelParent().GetStatusBar().SetStatusText('New period: %f,%f'%(s,s+d))
        self.wavectrl.SetTime(s,s+d)


    def repaint3(self, event):
        """ Vertical Zoom. """
        z = random.sample(range(5,50), 1)[0]
        if self.wavectrl.GetSize()[1] > 140:
            z = 1.0 - z/100.0
        else:
            z = 1.0 + z/100.0

        logging.debug('Vertical zoom: %d'%z)
        self.wavectrl.VertZoom( z )


# ---------------------------------------------------------------------------


class WaveCtrlFrame(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, pos=wx.DefaultPosition, size=wx.Size(440, 340))

        p = wx.Panel(self, -1)

        hbox = wx.BoxSizer( wx.VERTICAL )
        w = WaveCtrlDemo(p, -1)
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

