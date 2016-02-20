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
# File: components.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
from wx.lib.buttons import GenBitmapButton, GenBitmapTextButton

from wxgui.frames.dataroamerframe import DataRoamerFrame
from wxgui.frames.sndroamerframe  import SndRoamerFrame
from wxgui.frames.ipuscribeframe  import IPUscribeFrame
from wxgui.frames.sppaseditframe  import SppasEditFrame
from wxgui.frames.datafilterframe import DataFilterFrame
from wxgui.frames.statisticsframe import StatisticsFrame

from wxgui.cutils.imageutils import spBitmap
from wxgui.cutils.ctrlutils import CreateGenButton

from wxgui.sp_icons import SNDROAMER_APP_ICON
from wxgui.sp_icons import DATAROAMER_APP_ICON
from wxgui.sp_icons import IPUSCRIBE_APP_ICON
from wxgui.sp_icons import SPPASEDIT_APP_ICON
from wxgui.sp_icons import STATISTICS_APP_ICON
from wxgui.sp_icons import DATAFILTER_APP_ICON

from wxgui.sp_consts import BUTTON_ICONSIZE


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

ID_FRAME_DATAROAMER  = wx.NewId()
ID_FRAME_SNDROAMER   = wx.NewId()
ID_FRAME_IPUSCRIBE   = wx.NewId()
ID_FRAME_SPPASEDIT   = wx.NewId()
ID_FRAME_STATISTICS  = wx.NewId()
ID_FRAME_DATAFILTER  = wx.NewId()


# ----------------------------------------------------------------------------
# class componentsPanel
# ----------------------------------------------------------------------------

class ComponentsPanel( wx.Panel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: A panel with buttons to execute components.

    """

    def __init__(self, parent, preferences):

        wx.Panel.__init__(self, parent, -1, style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))

        self.opened_frames = {}
        self._prefsIO = preferences

        self._title = wx.StaticText(self, -1, 'Components: ')
        self._title.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        font = self._prefsIO.GetValue('M_FONT')
        font.SetWeight( wx.BOLD )
        self._title.SetFont(font)

        _buttonbox = self.__create_buttons( )

        _vbox = wx.BoxSizer(wx.VERTICAL)
        _vbox.Add(self._title, proportion=0, flag=wx.EXPAND | wx.ALL, border=4)
        _vbox.Add(_buttonbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=4)

        self.SetSizer(_vbox)


    def __create_buttons(self):
        """ Create buttons to call components. """

        FONT = self._prefsIO.GetValue('M_FONT')
        bmproamer = spBitmap(DATAROAMER_APP_ICON, theme=self._prefsIO.GetValue('M_ICON_THEME'))
        bmpplayer = spBitmap(SNDROAMER_APP_ICON,  theme=self._prefsIO.GetValue('M_ICON_THEME'))
        bmpscribe = spBitmap(IPUSCRIBE_APP_ICON,  theme=self._prefsIO.GetValue('M_ICON_THEME'))
        bmpedit   = spBitmap(SPPASEDIT_APP_ICON,  theme=self._prefsIO.GetValue('M_ICON_THEME'))
        bmpfilter = spBitmap(DATAFILTER_APP_ICON, theme=self._prefsIO.GetValue('M_ICON_THEME'))
        bmpstats  = spBitmap(STATISTICS_APP_ICON, theme=self._prefsIO.GetValue('M_ICON_THEME'))

        roamerButton     = CreateGenButton(self, ID_FRAME_DATAROAMER, bmproamer, text="DataRoamer", tooltip="DataRoamer: Explore annotated files.", colour=wx.Colour(220,120,180), SIZE=BUTTON_ICONSIZE, font=FONT)
        waveButton       = CreateGenButton(self, ID_FRAME_SNDROAMER,  bmpplayer, text="SndPlayer",  tooltip="SndRoamer: Play your speech files.",  colour=wx.Colour(110,210,210), SIZE=BUTTON_ICONSIZE, font=FONT)
        transcribeButton = CreateGenButton(self, ID_FRAME_IPUSCRIBE,  bmpscribe, text="IPUscribe",  tooltip="IPUscribe: Manual orthographic transcription based on IPUs segmentation.", colour=wx.Colour(120,240,120), SIZE=BUTTON_ICONSIZE, font=FONT)
        editorButton     = CreateGenButton(self, ID_FRAME_SPPASEDIT,  bmpedit,   text="SppasEdit",  tooltip="SppasEdit: View speech and annotated files.", colour=wx.Colour(100,120,230), SIZE=BUTTON_ICONSIZE, font=FONT)
        filterButton     = CreateGenButton(self, ID_FRAME_DATAFILTER, bmpfilter, text="DataFilter", tooltip="DataFilter: Extract/Request annotated files.", colour=wx.Colour(250,250,150), SIZE=BUTTON_ICONSIZE, font=FONT)
        statsButton      = CreateGenButton(self, ID_FRAME_STATISTICS, bmpstats,  text="Statistics", tooltip="Statistics: Estimates frequencies/durations of annotations.", colour=wx.Colour(245,190,150), SIZE=BUTTON_ICONSIZE, font=FONT)

        _box = wx.GridBagSizer()
        _box.Add( roamerButton,     pos=(0, 0), flag=wx.EXPAND|wx.ALL, border=2)
        _box.Add( waveButton,       pos=(1, 0), flag=wx.EXPAND|wx.ALL, border=2)
        _box.Add( editorButton,     pos=(0, 1), flag=wx.EXPAND|wx.ALL, border=2)
        _box.Add( transcribeButton, pos=(1, 1), flag=wx.EXPAND|wx.ALL, border=2)
        _box.Add( statsButton,      pos=(1, 2), flag=wx.EXPAND|wx.ALL, border=2)
        _box.Add( filterButton,     pos=(0, 2), flag=wx.EXPAND|wx.ALL, border=2)

        _box.AddGrowableCol(0)
        _box.AddGrowableCol(1)
        _box.AddGrowableCol(2)
        _box.AddGrowableRow(0)
        _box.AddGrowableRow(1)

        self.Bind(wx.EVT_BUTTON, self.OnDataRoamer,  roamerButton, ID_FRAME_DATAROAMER)
        self.Bind(wx.EVT_BUTTON, self.OnSndRoamer,   waveButton,   ID_FRAME_SNDROAMER)
        self.Bind(wx.EVT_BUTTON, self.OnIPUscribe,   transcribeButton, ID_FRAME_IPUSCRIBE)
        self.Bind(wx.EVT_BUTTON, self.OnSppasEdit,   editorButton, ID_FRAME_SPPASEDIT)
        self.Bind(wx.EVT_BUTTON, self.OnDataFilter,  filterButton, ID_FRAME_DATAFILTER)
        self.Bind(wx.EVT_BUTTON, self.OnStatistics,  statsButton,  ID_FRAME_STATISTICS)

        self.buttons = [ roamerButton, waveButton, transcribeButton, editorButton, filterButton, statsButton ]
        return _box

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------


    def OnDataRoamer(self, evt):
        """
        Open the DataRoamer component.
        """
        selection = self.GetTopLevelParent().GetTrsSelection()
        if not len(selection):
            dial = wx.MessageDialog(None, 'No annotated file selected.', 'Information', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            return

        arguments = {}
        arguments['title'] = 'SPPAS - Data Roamer'
        arguments['icon']  = DATAROAMER_APP_ICON
        arguments['type']  = "DATAFILES"
        arguments['prefs'] = self._prefsIO

        # DataRoamer Frame already opened or not...
        try:
            if ID_FRAME_DATAROAMER in self.opened_frames.keys():
                self.opened_frames[ID_FRAME_DATAROAMER].SetFocus()
                self.opened_frames[ID_FRAME_DATAROAMER].Raise()
        except Exception:
            del self.opened_frames[ID_FRAME_DATAROAMER]

        # Create (or not) and Add files. Give the focus to this frame.
        if ID_FRAME_DATAROAMER not in self.opened_frames.keys():
            self.opened_frames[ID_FRAME_DATAROAMER] = DataRoamerFrame(self.GetTopLevelParent(), ID_FRAME_IPUSCRIBE, arguments)

        self.opened_frames[ID_FRAME_DATAROAMER].AddFiles( selection )
        self.opened_frames[ID_FRAME_DATAROAMER].SetFocus()
        self.opened_frames[ID_FRAME_DATAROAMER].Raise()

    # End OnDataRoamer
    # -----------------------------------------------------------------------


    def OnSndRoamer(self, evt):
        """
        Open the SndRoamer component.
        """
        selection = self.GetTopLevelParent().GetAudioSelection()
        if not len(selection):
            dial = wx.MessageDialog(None, 'No sound file selected.', 'Information', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            return

        arguments = {}
        arguments['title'] = 'SPPAS - SndRoamer'
        arguments['icon']  = SNDROAMER_APP_ICON
        arguments['type']  = "SOUNDFILES"
        arguments['prefs'] = self._prefsIO

        # Frame already opened or not...
        try:
            if ID_FRAME_SNDROAMER in self.opened_frames.keys():
                self.opened_frames[ID_FRAME_SNDROAMER].SetFocus()
        except Exception:
            del self.opened_frames[ID_FRAME_SNDROAMER]

        # Create (or not) and Add files. Give the focus to this frame.
        if ID_FRAME_SNDROAMER not in self.opened_frames.keys():
            self.opened_frames[ID_FRAME_SNDROAMER] = SndRoamerFrame(self.GetTopLevelParent(), ID_FRAME_IPUSCRIBE, arguments)

        self.opened_frames[ID_FRAME_SNDROAMER].AddFiles( selection )
        self.opened_frames[ID_FRAME_SNDROAMER].SetFocus()
        self.opened_frames[ID_FRAME_SNDROAMER].Raise()

    # End OnWavPlayer
    # -----------------------------------------------------------------------


    def OnSppasEdit(self, evt):
        """
        Open the SPPASEditor component.
        """
        selection = self.GetTopLevelParent().GetTrsSelection()
        selection += self.GetTopLevelParent().GetAudioSelection()
        if not len(selection):
            dial = wx.MessageDialog(None, 'No file selected.', 'Information', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            return

        arguments = {}
        arguments['title'] = 'SPPAS - SppasEdit'
        arguments['icon']  = SPPASEDIT_APP_ICON
        arguments['type']  = "ANYFILES"
        arguments['prefs'] = self._prefsIO

        # Editor Frame already opened or not...
        try:
            if ID_FRAME_SPPASEDIT in self.opened_frames.keys():
                self.opened_frames[ID_FRAME_SPPASEDIT].SetFocus()
        except Exception as e:
            del self.opened_frames[ID_FRAME_SPPASEDIT]

        # Create (or not) and Add files. Give the focus to this frame.
        if ID_FRAME_SPPASEDIT not in self.opened_frames.keys():
            self.opened_frames[ID_FRAME_SPPASEDIT] = SppasEditFrame(self.GetTopLevelParent(), ID_FRAME_IPUSCRIBE, arguments)

        self.opened_frames[ID_FRAME_SPPASEDIT].AddFiles( selection )
        self.opened_frames[ID_FRAME_SPPASEDIT].SetFocus()
        self.opened_frames[ID_FRAME_SPPASEDIT].Raise()

    # End OnSppasEdit
    # -----------------------------------------------------------------------


    def OnIPUscribe(self, evt):
        """
        Open the IPU Transcriber component.
        """
        selection = self.GetTopLevelParent().GetAudioSelection()
        if not len(selection):
            dial = wx.MessageDialog(None, 'No sound file selected.', 'Information', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            return

        arguments = {}
        arguments['title'] = 'SPPAS - IPUscribe'
        arguments['icon']  = IPUSCRIBE_APP_ICON
        arguments['type']  = "SOUNDFILES"
        arguments['prefs'] = self._prefsIO

        # IPU Transcriber Frame already opened or not...
        try:
            if ID_FRAME_IPUSCRIBE in self.opened_frames.keys():
                self.opened_frames[ID_FRAME_IPUSCRIBE].SetFocus()
        except Exception:
            del self.opened_frames[ID_FRAME_IPUSCRIBE]

        # Create (or not) and Add files. Give the focus to this frame.
        if ID_FRAME_IPUSCRIBE not in self.opened_frames.keys():
            self.opened_frames[ID_FRAME_IPUSCRIBE] = IPUscribeFrame(self.GetTopLevelParent(), ID_FRAME_IPUSCRIBE, arguments)

        self.opened_frames[ID_FRAME_IPUSCRIBE].AddFiles( selection )
        self.opened_frames[ID_FRAME_IPUSCRIBE].SetFocus()
        self.opened_frames[ID_FRAME_IPUSCRIBE].Raise()

    # End OnIPUScribe
    # -----------------------------------------------------------------------


    def OnDataFilter(self, evt):
        """
        Open the DataFilter component.
        """
        selection = self.GetTopLevelParent().GetTrsSelection()
        if not len(selection):
            dial = wx.MessageDialog(None, 'No file selected.', 'Information', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            return

        arguments = {}
        arguments['title'] = 'SPPAS - DataFilter'
        arguments['icon']  = DATAFILTER_APP_ICON
        arguments['type']  = "DATAFILES"
        arguments['prefs'] = self._prefsIO

        # IPU Transcriber Frame already opened or not...
        try:
            if ID_FRAME_DATAFILTER in self.opened_frames.keys():
                self.opened_frames[ID_FRAME_DATAFILTER].SetFocus()
        except Exception:
            del self.opened_frames[ID_FRAME_DATAFILTER]

        # Create (or not) and Add files. Give the focus to this frame.
        if ID_FRAME_DATAFILTER not in self.opened_frames.keys():
            self.opened_frames[ID_FRAME_DATAFILTER] = DataFilterFrame(self.GetTopLevelParent(), ID_FRAME_DATAFILTER, arguments)

        self.opened_frames[ID_FRAME_DATAFILTER].AddFiles( selection )
        self.opened_frames[ID_FRAME_DATAFILTER].SetFocus()
        self.opened_frames[ID_FRAME_DATAFILTER].Raise()

    # End OnDataFilter
    # -----------------------------------------------------------------------


    def OnStatistics(self, evt):
        """
        Open the Statistics component.
        """
        selection = self.GetTopLevelParent().GetTrsSelection()
        if not len(selection):
            dial = wx.MessageDialog(None, 'No file selected.', 'Information', wx.OK | wx.ICON_ERROR)
            dial.ShowModal()
            return

        arguments = {}
        arguments['title'] = 'SPPAS - Statistics'
        arguments['icon']  = STATISTICS_APP_ICON
        arguments['type']  = "DATAFILES"
        arguments['prefs'] = self._prefsIO

        # IPU Transcriber Frame already opened or not...
        try:
            if ID_FRAME_STATISTICS in self.opened_frames.keys():
                self.opened_frames[ID_FRAME_STATISTICS].SetFocus()
        except Exception:
            del self.opened_frames[ID_FRAME_STATISTICS]

        # Create (or not) and Add files. Give the focus to this frame.
        if ID_FRAME_STATISTICS not in self.opened_frames.keys():
            self.opened_frames[ID_FRAME_STATISTICS] = StatisticsFrame(self.GetTopLevelParent(), ID_FRAME_STATISTICS, arguments)

        self.opened_frames[ID_FRAME_STATISTICS].AddFiles( selection )
        self.opened_frames[ID_FRAME_STATISTICS].SetFocus()
        self.opened_frames[ID_FRAME_STATISTICS].Raise()

    # End OnStatistics
    # -----------------------------------------------------------------------


    def SetPrefs(self, prefs):
        """
        Fix new preferences.
        """
        self._prefsIO = prefs
        self.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR') )
        self.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )
        self.SetFont( self._prefsIO.GetValue('M_FONT') )

        font = self._prefsIO.GetValue('M_FONT')
        font.SetWeight( wx.BOLD )
        self._title.SetFont( font )
        self._title.SetForegroundColour( self._prefsIO.GetValue('M_FG_COLOUR') )

        for b in self.buttons:
            b.SetFont( self._prefsIO.GetValue('M_FONT') )

        for f in self.opened_frames.keys():
            try:
                self.opened_frames[f].SetPrefs( self._prefsIO )
            except Exception as e:
                import logging
                logging.debug('SetPrefs error: %s'%str(e))
                pass
        self.Refresh()

    # End SetPrefs
    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------
