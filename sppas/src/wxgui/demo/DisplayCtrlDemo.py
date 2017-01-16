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
import wx
import logging
import wave

import annotationdata.aio

from wxgui.ui.displayctrl import DisplayCtrl

from wxgui.structs.prefs import Preferences_IO
from wxgui.structs.cthemes import all_themes


# ----------------------------------------------------------------------------

import os
trsf  = os.path.join(os.path.dirname(os.path.abspath(__file__)),"oriana1-merge.TextGrid")
wavef = os.path.join(os.path.dirname(os.path.abspath(__file__)),"oriana1.wav")

# ----------------------------------------------------------------------------


class DisplayCtrlDemo( wx.Window ):

    def __init__(self, parent, id):
        wx.Window.__init__(self, parent, id)
        self.SetBackgroundColour(wx.WHITE)

        wx.StaticText(self, -1, "Click on the following buttons to test functions:", pos=(10,10))

        self.b1 = wx.Button(self, -1, " Theme ",  (10,40))
        self.b2 = wx.Button(self, -1, " Scroll ", (110, 40))
        self.b3 = wx.Button(self, -1, " Font ",   (210, 40))

        self._init_prefs()
        self.displayctrl = DisplayCtrl(self, id=-1, pos=(10,80),  size=wx.Size(400,160), prefsIO=self._prefsIO)
        self.displayctrl.SetPeriodValues(1.0,3.0)
        self.displayctrl.SetData( wavef )
        self.displayctrl.SetData( trsf )

        self.Bind(wx.EVT_BUTTON, self.repaint1, self.b1)
        self.Bind(wx.EVT_BUTTON, self.repaint2, self.b2)
        self.Bind(wx.EVT_BUTTON, self.repaint3, self.b3)


    def _init_prefs( self ):
        """
        Set the Editor settings.
        """

        self._prefsIO = Preferences_IO()

        # Panel: Display
        self._prefsIO.SetValue( 'D_TIME_MIN', t='float', v=0.0,  text='Minimum time value (in seconds) of the displayed period at start-up')
        self._prefsIO.SetValue( 'D_TIME_MAX', t='float', v=2.0,  text='Maximum time value (in seconds) of the displayed period at start-up')
        self._prefsIO.SetValue( 'D_TIME_ZOOM_MIN', t='float', v=0.2,   text='Minimum duration (in seconds) of the displayed period')
        self._prefsIO.SetValue( 'D_TIME_ZOOM_MAX', t='float', v=300.0, text='Maximum duration (in seconds) of the displayed period')

        self._prefsIO.SetValue( 'D_H_ZOOM',   t='float', v=50.0, text='Time zoom (percentage)')
        self._prefsIO.SetValue( 'D_SCROLL',   t='float', v=75.0, text='Time scroll (percentage)')
        self._prefsIO.SetValue( 'D_V_ZOOM',   t='float', v=10.0, text='Vertical zoom (percentage)')

        # Panel: Objects
        self._prefsIO.SetValue( 'O_PEN_WIDTH',   t='int', v=1,        text='')
        self._prefsIO.SetValue( 'O_PEN_STYLE',   t='int', v=wx.SOLID, text='')
        self._prefsIO.SetValue( 'O_BRUSH_STYLE', t='int', v=wx.SOLID, text='')
        self._prefsIO.SetValue( 'O_MARGIN',      t='int', v=6,        text='Margins (for handles)')

        # Ruler
        self._prefsIO.SetValue( 'R_BG_COLOUR',     t='wx.Colour', v=wx.Colour(255,255,255))
        self._prefsIO.SetValue( 'R_FG_COLOUR',     t='wx.Colour', v=wx.Colour(40,40,10))
        self._prefsIO.SetValue( 'R_HANDLES_COLOUR',t='wx.Colour', v=wx.Colour(0,0,200))
        self._prefsIO.SetValue( 'R_FONT',          t='wx.Font',   v=wx.Font(8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8))
        self._prefsIO.SetValue( 'R_FONT_COLOUR',   t='wx.Colour', v=wx.Colour(0, 0, 200))

        # Tier
        self._prefsIO.SetValue( 'T_BG_COLOUR',     t='wx.Colour', v=wx.Colour(200,200,200), text='Tier background color')
        self._prefsIO.SetValue( 'T_FG_COLOUR',     t='wx.Colour', v=wx.Colour(20,20,20), text='Tier foreground color')
        self._prefsIO.SetValue( 'T_HANDLES_COLOUR',t='wx.Colour', v=wx.Colour(200,0,0), text='Main frame handles color')
        self._prefsIO.SetValue( 'T_FONT',          t='wx.Font',   v=wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8), text='Font for tiers')
        self._prefsIO.SetValue( 'T_FONT_COLOUR',   t='wx.Colour', v=wx.Colour(200,0,0), text='Main frame foreground color')
        self._prefsIO.SetValue( 'T_HEIGHT',        t='int',       v=30, text='Tier height')
        self._prefsIO.SetValue( 'T_RADIUS_COLOUR', t='wx.Colour', v=wx.Colour(200,0,0), text='Main frame radius color for points')
        self._prefsIO.SetValue( 'T_LABEL_ALIGN',   t='wx.ALIGN',  v=wx.ALIGN_CENTRE, text='Text alignment for labels')

        # Wave
        self._prefsIO.SetValue( 'W_BG_COLOUR',     t='wx.Colour', v=wx.Colour(240,240,240), text='Wave background')
        self._prefsIO.SetValue( 'W_FG_COLOUR',     t='wx.Colour', v=wx.Colour(0,200,0), text='Wave foreground')
        self._prefsIO.SetValue( 'W_HANDLES_COLOUR',t='wx.Colour', v=wx.Colour(0,200,0), text='Main frame foreground color')
        self._prefsIO.SetValue( 'W_FONT',          t='wx.Font',   v=wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, '', wx.FONTENCODING_UTF8), text='Font for wave')
        self._prefsIO.SetValue( 'W_FONT_COLOUR',   t='wx.Colour', v=wx.Colour(200, 0, 0))
        self._prefsIO.SetValue( 'W_HEIGHT',        t='int',       v=120,   text='Wave height')
        self._prefsIO.SetValue( 'W_FG_DISCO',      t='bool',      v=False, text='Wave disco style')
        self._prefsIO.SetValue( 'W_BG_GRADIENT_COLOUR', t='wx.Colour', v=wx.Colour(200,200,200), text='Wave background gradient')
        self._prefsIO.SetValue( 'W_AUTOSCROLL',    t='bool',      v=True,  text='Wave auto-scrolling')

        self._prefsIO.SetTheme( all_themes.get_theme(u'Default') )



    def repaint1(self, event):
        """ Theme. """
        themes = [u'Default', u'Brigitte', u'Paul', u'Léa']
        p = random.sample(range(0,4),1)[0]
        # set the theme to prefsIO
        self._prefsIO.SetTheme( all_themes.get_theme(themes[p]) )

        # set prefsIO to the display
        self.displayctrl.SetPreferences( self._prefsIO )


    def repaint2(self, event):
        """ Period. """
        s = float(random.sample(range(0,5), 1)[0])
        d = float(random.sample(range(1,20), 1)[0])/10.
        self.GetTopLevelParent().GetStatusBar().SetStatusText('New period: %f,%f'%(s,s+d))
        self.displayctrl.SetPeriodValues(s,s+d)


    def repaint3(self, event):
        """ Font. """
        data = wx.FontData()
        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data   = dlg.GetFontData()
            font   = data.GetChosenFont()
            color  = data.GetColour()
            # set this new font to prefsIO
            # set prefsIO to the display
            self.displayctrl.SetPreferences( self._prefsIO )
        dlg.Destroy()

# ---------------------------------------------------------------------------


class DisplayCtrlFrame(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, pos=wx.DefaultPosition, size=wx.Size(440, 380))

        p = wx.Panel(self, -1)

        hbox = wx.BoxSizer( wx.VERTICAL )
        w = DisplayCtrlDemo(p, -1)
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

