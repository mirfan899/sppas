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
# File: sndroamerclient.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import logging
import wx.lib.scrolledpanel as scrolled

from wxgui.ui.CustomEvents  import NotebookClosePageEvent
from wxgui.ui.CustomEvents  import FileWanderEvent, spEVT_FILE_WANDER
from wxgui.ui.CustomEvents  import spEVT_SETTINGS

from baseclient        import BaseClient
from wxgui.panels.sndplayer     import SndPlayer
from wxgui.panels.sndproperty   import SndProperty
from wxgui.structs.prefs        import Preferences
from wxgui.structs.themes       import BaseTheme


# ----------------------------------------------------------------------------
# Main class that manage the notebook
# ----------------------------------------------------------------------------

class SndRoamerClient( BaseClient ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to manage the opened files.

    This class manages the pages of a notebook with all opened files.

    Each page (except if empty...) contains an instance of a SndRoamer.

    """

    def __init__( self, parent, prefsIO ):
        BaseClient.__init__( self, parent, prefsIO )

    def CreateComponent(self, parent, prefsIO ):
        return SndRoamer(parent, prefsIO)


# ----------------------------------------------------------------------------
# The Component is the content of one page of the notebook.
# ----------------------------------------------------------------------------


class SndRoamer( scrolled.ScrolledPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This component allows to manage speech files.

    The current version allows to print information and play the file.

    """

    def __init__(self, parent, prefsIO):
        """
        SndRoamer Component.
        """
        scrolled.ScrolledPanel.__init__(self, parent, -1)
        sizer = wx.BoxSizer( wx.VERTICAL )

        # members
        self._prefsIO = self._check_prefs(prefsIO)
        self._filename = None

        # create the panels
        self._propertyPanel = SndProperty(self)
        self._propertyPanel.SetPreferences(self._prefsIO)
        self._playerPanel   = SndPlayer(self, prefsIO=self._prefsIO)

        sizer.Add(self._propertyPanel, proportion=0, flag=wx.LEFT|wx.TOP|wx.EXPAND, border=5 )
        sizer.Add(self._playerPanel,   proportion=0, flag=wx.CENTRE|wx.TOP, border=5 )

        # Bind events
        self.Bind(spEVT_FILE_WANDER, self.OnFileWander)
        self.Bind(spEVT_SETTINGS,    self.OnSettings)

        self.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR'))
        self.SetSizer(sizer)
        self.SetAutoLayout( True )
        self.Layout()
        self.SetupScrolling()

    # End __init__
    # ----------------------------------------------------------------------


    def _check_prefs(self, prefs):
        """
        Check if preferences are set properly. Set new ones if required.
        Return the new version.
        """
        if prefs is None:
            prefs = Preferences( BaseTheme() )
        else:
            try:
                prefs.GetValue( 'M_BG_COLOUR' )
                prefs.GetValue( 'M_FG_COLOUR' )
                prefs.GetValue( 'M_FONT' )
                prefs.GetValue( 'M_ICON_THEME' )
            except Exception:
                self._prefsIO.SetTheme( BaseTheme() )
                prefs = self._prefsIO

        prefs.SetValue('SND_INFO',       'bool', False)
        prefs.SetValue('SND_PLAY',       'bool', True)
        prefs.SetValue('SND_AUTOREPLAY', 'bool', False)
        prefs.SetValue('SND_PAUSE',      'bool', True)
        prefs.SetValue('SND_STOP',       'bool', True)
        prefs.SetValue('SND_NEXT',       'bool', True)
        prefs.SetValue('SND_REWIND',     'bool', True)
        prefs.SetValue('SND_EJECT',      'bool', True)

        return prefs

    #-----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # GUI
    # ----------------------------------------------------------------------


    def OnSettings(self, event):
        """
        Set new preferences, then apply them.
        """

        self._prefsIO = event.prefsIO

        # Apply the changes on self
        self.SetBackgroundColour( self._prefsIO.GetValue( 'M_BG_COLOUR' ) )
        self.SetForegroundColour( self._prefsIO.GetValue( 'M_FG_COLOUR' ) )
        self.SetFont( self._prefsIO.GetValue( 'M_FONT' ) )

        self.Layout()
        self.Refresh()

    # End OnSettings
    # ----------------------------------------------------------------------


    def SetFont(self, font):
        """ Change font of all texts. """

        wx.Window.SetFont( self,font )
        self._propertyPanel.SetFont( font )
        self._playerPanel.SetFont( font )

    # End ChangeFont
    # ----------------------------------------------------------------------


    def SetBackgroundColour(self, color):
        """ Change background of all texts. """

        wx.Window.SetBackgroundColour( self,color )
        self._propertyPanel.SetBackgroundColour( color )
        self._playerPanel.SetBackgroundColour( color )

    # End SetBackgroundColour
    # ----------------------------------------------------------------------


    def SetForegroundColour(self, color):
        """ Change foreground of all texts. """

        wx.Window.SetForegroundColour( self,color )
        self._propertyPanel.SetForegroundColour( color )
        self._playerPanel.SetForegroundColour( color )

    # End SetForegroundColour
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Callbacks
    # ----------------------------------------------------------------------


    def OnFileWander(self, event):
        """
        A file was checked/unchecked/ejected somewhere else.

        """
        logging.debug(' sndroamerclient. OnFileWander. received event.')
        o = event.GetEventObject()
        if o == self._playerPanel:
            evt = NotebookClosePageEvent()
            evt.SetEventObject(self)
            wx.PostEvent( self.GetParent().GetParent().GetParent(),evt )
            self._propertyPanel.FileDeSelected()
            return

        f = event.filename
        s = event.status

        if s is True:
            self._propertyPanel.FileSelected( f )
            self._playerPanel.FileSelected( f )
            self._filename = f
        else:
            self._propertyPanel.FileDeSelected()
            self._playerPanel.FileDeSelected()
            evt = FileWanderEvent(filename=self._filename, status=False)
            evt.SetEventObject(self)
            wx.PostEvent( self.GetParent().GetParent().GetParent(), evt )
            self._filename = None

    # End OnFileWander
    # ------------------------------------------------------------------------


# ----------------------------------------------------------------------------

