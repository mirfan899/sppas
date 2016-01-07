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
import logging
import random
import wx

from wxgui.ui.annotationctrl import AnnotationCtrl
import annotationdata.io

# ----------------------------------------------------------------------------

import os
trs = annotationdata.io.read( os.path.join(os.path.dirname(os.path.abspath(__file__)),"oriana1-merge.TextGrid"))

# ----------------------------------------------------------------------------


class AnnCtrlDemo(wx.Window):

    def __init__(self, parent, id):
        wx.Window.__init__(self, parent, id)
        self.SetBackgroundColour(wx.WHITE)

        wx.StaticText(self, -1, "Click on the buttons to test Annotation functionalities:", pos=(10,10))

        self.b1 = wx.Button(self, -1, " Color ", (10,40))
        self.b2 = wx.Button(self, -1, " Move ", (110, 40))
        self.b3 = wx.Button(self, -1, " Size ", (210, 40))
        self.b4 = wx.Button(self, -1, " Font ", (310, 40))

        tier = trs[2]
        tier.SetRadius(0.005)

        logging.debug('Create annotation controls')
        pxsec = 800

        self._anns = []
        a0 = trs[1][0] # a long silence first... not interesting for that demo!
        time0 = a0.GetLocation().GetEnd().GetMidpoint() - a0.GetLocation().GetEnd().GetRadius()
        for i in range(1,7):
            ann = trs[1][i]
            logging.debug('  New annotation: %s'%(ann))

            time1 = ann.GetLocation().GetBegin().GetMidpoint() - ann.GetLocation().GetBegin().GetRadius()
            time2 = ann.GetLocation().GetEnd().GetMidpoint()   + ann.GetLocation().GetEnd().GetRadius()
            logging.debug('  --> time0=%f, time1=%f, time2=%f '%(time0,time1,time2))
            x = round( (time1-time0) * float(pxsec)) + 10
            y = 80
            h = 30
            duration = time2 - time1
            w = round( duration * float(pxsec))
            logging.debug('  ==> x=%d,w=%d'%(x,w))
            if (x+w) > 400:
                w = w + (400-x-w)
                logging.debug('  -> w was adjusted!')
                logging.debug('  -> New annotation: %s / x=%d,w=%d'%(ann,x,w))
            a = AnnotationCtrl(self, id=-1, pos=(x,y),  size=wx.Size(w,h), ann=trs[1][i])
            a.SetPxSec( pxsec )
            self._anns.append(a)

        self.Bind(wx.EVT_BUTTON, self.repaint1, self.b1)
        self.Bind(wx.EVT_BUTTON, self.repaint2, self.b2)
        self.Bind(wx.EVT_BUTTON, self.repaint3, self.b3)
        self.Bind(wx.EVT_BUTTON, self.repaint4, self.b4)


    def repaint1(self, event):
        """ Color. """
        (a,b,c) = random.sample(range(160,250),  3)
        (q,r,s) = random.sample(range(0,150),  3)
        for ann in self._anns:
            ann.SetLabelColours(bgcolour=wx.Colour(a,b,c),fontnormalcolour=wx.Colour(q,r,s))

    def repaint2(self, event):
        """ Move. """
        y1 = random.sample(range(70,120), 2)[0]
        for a in self._anns:
            x,y=a.GetPosition()
            a.MoveWindow(pos=(x,y1), size=a.GetSize())
        self.GetTopLevelParent().GetStatusBar().SetStatusText('Annotations re-sized: %d'%y1)

    def repaint3(self, event):
        """ Size. """
        h1 = random.sample(range(20,60),  2)[0]
        for a in self._anns:
            a.MoveWindow(pos=a.GetPosition(), size=wx.Size(a.GetSize().width,h1))
        self.GetTopLevelParent().GetStatusBar().SetStatusText('Annotations re-sized: %d'%h1)

    def repaint4(self, event):
        """ Font. """
        data = wx.FontData()
        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data   = dlg.GetFontData()
            font   = data.GetChosenFont()
            for a in self._anns:
                a.SetLabelFont(font)
        dlg.Destroy()


# ---------------------------------------------------------------------------


class AnnCtrlFrame(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, pos=wx.DefaultPosition, size=wx.Size(440, 340))

        p = wx.Panel(self, -1)

        hbox = wx.BoxSizer( wx.VERTICAL )
        w = AnnCtrlDemo(p, -1)
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
