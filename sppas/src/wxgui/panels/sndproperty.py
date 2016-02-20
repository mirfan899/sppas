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
# File: sndproperty.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import logging

import signals

from wxgui.structs.prefs  import Preferences
from wxgui.structs.themes import BaseTheme

from wxgui.sp_consts import ERROR_COLOUR
from wxgui.sp_consts import WARNING_COLOUR
from wxgui.sp_consts import OK_COLOUR


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LABEL_LIST = [ "File name: ",
               "Duration (in sec.): ",
               "Frame rate: ",
               "Sample width: ",
               "Channels: ",
               "Volume min: ",
               "Volume mean: ",
               "Volume max: " ]

NO_INFO_LABEL = " ... "


# ---------------------------------------------------------------------------

class SndProperty( wx.Panel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Display information about a sound file.

    Information has a different colour depending on level of acceptability
    in SPPAS.

    """

    def __init__(self, parent):
        """ Create a new WavProperty instance. """

        wx.Panel.__init__(self, parent)

        # members
        self._prefs = Preferences( BaseTheme() )
        self._values = []
        self._labels = []

        # GUI design
        gbs = wx.GridBagSizer(len(LABEL_LIST), 2)
        self._create_property_labels(gbs)
        self._create_property_values(gbs)
        gbs.AddGrowableCol(1)

        self.SetBackgroundColour( self._prefs.GetValue("M_BG_COLOUR") )
        self.SetForegroundColour( self._prefs.GetValue("M_FG_COLOUR") )
        self.SetFont( self._prefs.GetValue("M_FONT") )

        self.SetSizer(gbs)
        self.SetAutoLayout( True )
        self.Layout()

    # End __init__
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # -----------------------------------------------------------------------


    def _create_property_labels(self, sizer):
        for line,label in enumerate(LABEL_LIST):
            static_tx = wx.StaticText(self, -1, label, size=(100,-1),style=wx.TE_READONLY|wx.NO_BORDER)
            #static_tx.SetFont( self.GetFont() )
            #static_tx.SetForegroundColour( self.GetForegroundColour() )
            #static_tx.SetBackgroundColour( self.GetBackgroundColour() )
            self._labels.append( static_tx )
            sizer.Add(static_tx, (line,0), flag=wx.ALL, border=5)

    # End create_property_labels
    # -----------------------------------------------------------------------


    def _create_property_values(self, sizer):
        for line,label in enumerate(LABEL_LIST):
            tx = wx.TextCtrl(self, -1, NO_INFO_LABEL, style=wx.TE_READONLY)
            #static_tx.SetFont( self.GetFont() )
            #static_tx.SetBackgroundColour( self.GetBackgroundColour() )
            #static_tx.SetForegroundColour( self.GetForegroundColour() )
            self._values.append( tx )
            sizer.Add(tx, (line,1), flag=wx.EXPAND|wx.RIGHT, border=5)

    # End create_property_values
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # GUI
    # -----------------------------------------------------------------------


    def SetPreferences(self, prefs):
        """ Set new preferences. """

        self._prefs = prefs
        self.SetBackgroundColour( self._prefs.GetValue("M_BG_COLOUR") )
        self.SetForegroundColour( self._prefs.GetValue("M_FG_COLOUR") )
        self.SetFont( self._prefs.GetValue("M_FONT") )

    #-------------------------------------------------------------------------


    def SetFont(self, font):
        """ Change font of all texts. """

        wx.Window.SetFont( self,font )
        for p in self._values:
            p.SetFont( font )
        for l in self._labels:
            l.SetFont( font )
        self.Refresh()

    # End SetFont
    # -----------------------------------------------------------------------


    def SetBackgroundColour(self, colour):
        """ Change the background color of all objects. """

        wx.Window.SetBackgroundColour( self,colour )

        for p in self._values:
            p.SetBackgroundColour( colour )
        for l in self._labels:
            l.SetBackgroundColour( colour )
        self.Refresh()

    # End SetForegroundColour
    # -----------------------------------------------------------------------


    def SetForegroundColour(self, colour):
        """ Change the foreground color of all objects. """

        wx.Window.SetForegroundColour( self,colour )

        for i,p in enumerate(self._values):
            p.SetForegroundColour( colour )
            if i == 2:
                if p.GetValue() in ["16000","32000","48000"]:
                    p.SetForegroundColour( OK_COLOUR )
                else:
                    p.SetForegroundColour( WARNING_COLOUR )
            elif i == 3:
                if p.GetValue() == "2":
                    p.SetForegroundColour( OK_COLOUR )
                else:
                    p.SetForegroundColour( ERROR_COLOUR )
            elif i == 4:
                if p.GetValue() == "1":
                    p.SetForegroundColour( OK_COLOUR )
                else:
                    p.SetForegroundColour( ERROR_COLOUR )

        for l in self._labels:
            l.SetForegroundColour( colour )
        self.Refresh()

    # End SetForegroundColour
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------


    def FileSelected(self, filename):
        """
        Show information of a sound file.
        """
        try:
            logging.info('PropertyPanel. File: '+filename)
            #_wav  = wave.Wave_read( filename )
            _audio = signals.open( filename )
            duration = float(_audio.get_duration() )
            value_list = [ filename,
                           '%.2f' % duration,
                           str(_audio.get_framerate()),
                           str(_audio.get_sampwidth()),
                           str(_audio.get_nchannels()),
                           str(_audio.get_minvolume()),
                           str(_audio.get_meanvolume()),
                           str(_audio.get_maxvolume()) ]
        except Exception as e:
            value_list = [ NO_INFO_LABEL ] * len(LABEL_LIST)
            logging.info(" ... Error reading %s: %s" % (filename,e))

        for i,value in enumerate(value_list):
            #self._values[i].SetLabel(value) # deprecated. (now, only works on windows)
            self._values[i].ChangeValue(value)  # linux

        self.SetForegroundColour( self._prefs.GetValue('M_FG_COLOUR') )
        #self.Refresh()

    # End OnFileSelected
    #------------------------------------------------------------------------


    def FileDeSelected(self):
        """
        Reset information.
        """

        for i in range(len(self._values)):
            self._values[i].SetValue( NO_INFO_LABEL )

        self.Refresh()

    # End OnFileDeSelected
    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------
