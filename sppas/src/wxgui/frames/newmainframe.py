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
# File: mainframe.py
# ----------------------------------------------------------------------------
import sys
import os.path
sys.path.append(  os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )

import wx
import logging
import annotationdata
import audiodata

from sp_glob import program, title
from wxgui.sp_icons import APP_ICON
from wxgui.sp_icons import EXIT_ICON

from wxgui.sp_consts import MIN_FRAME_W, MIN_PANEL_W, PANEL_W
from wxgui.sp_consts import MIN_FRAME_H, MIN_PANEL_H, FRAME_H
from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE

from wxgui.cutils.imageutils import spBitmap

from wxgui.panels.filetree    import FiletreePanel
from wxgui.panels.buttons     import ButtonMenuPanel, ImgPanel
from wxgui.panels.mainbuttons import MainButtonsPanel
from wxgui.panels.mainbuttons import ID_ANNOTATE, ID_COMPONENTS, ID_PLUGINS
import wxgui.structs.prefs

from wxgui.views.settings      import SettingsDialog
from wxgui.views.about         import AboutBox
from wxgui.views.settings      import SettingsDialog
from wxgui.frames.helpbrowser  import HelpBrowser
from wxgui.panels.components   import ComponentsPanel
from wxgui.panels.aannotations import AnnotationsPanel
from wxgui.panels.plugins      import PluginPanel

# -----------------------------------------------------------------------
# S P P A S  Graphical User Interface... is here!
# -----------------------------------------------------------------------

class FrameSPPAS( wx.Frame ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS main frame based on wx library.

    """
    def __init__( self, preferencesIO ):
        """
        Constructor of the SPPAS main frame.

        @param preferences (Preferences_IO)

        """
        wx.Frame.__init__(self, None, -1, title=FRAME_TITLE, style=FRAME_STYLE)

        # Members
        if preferencesIO is None:
            preferences = wxgui.structs.prefs.Preferences()
        self.preferences = preferences

        # Set title and icon of the frame
        self._init_infos()
        self._mainmenu  = self._create_menu()
        self._maintitle = self._create_title()
        self._mainpanel = self._create_content()

        contentsizer = wx.BoxSizer( wx.VERTICAL )
        contentsizer.Add( self._maintitle, proportion=0, flag=wx.ALL|wx.EXPAND, border=0 )
        contentsizer.Add( self._mainpanel, proportion=1, flag=wx.ALL|wx.EXPAND, border=0 )

        sizer = wx.BoxSizer( wx.HORIZONTAL )
        sizer.Add( self._mainmenu, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)
        sizer.Add( contentsizer,   proportion=2, flag=wx.ALL|wx.EXPAND, border=0)
        self.SetSizer( sizer )

        # Frame properties
        self._frame_properties()

        # Events of this frame
        self.Bind(wx.EVT_CLOSE,  self.ProcessEvent)
        self.Bind(wx.EVT_BUTTON, self.ProcessEvent)

        self.Show( True )

    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # ------------------------------------------------------------------------

    def _init_infos( self ):
        """
        Set the title and the icon.

        """
        wx.GetApp().SetAppName( "sppas" )

        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap( spBitmap(APP_ICON) )
        self.SetIcon(_icon)

        # colors
        self.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont( self.preferences.GetValue('M_FONT'))

    # ------------------------------------------------------------------------

    def _create_menu(self):
        """
        Create a menu and return it.

        """
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour( self.preferences.GetValue('M_BGM_COLOUR'))

        exitButton = ButtonMenuPanel(panel, wx.ID_EXIT, self.preferences, EXIT_ICON, None)

        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( exitButton, proportion=0, flag=wx.ALL, border=0)
        panel.SetSizer( sizer )
        panel.Bind( wx.EVT_BUTTON, self.OnExit )

        return panel

    # ------------------------------------------------------------------------

    def _create_title(self):
        """
        Create a layout including a nice bold-title with an icon.

        @param titleicon Name of the icon (see sp_icons)
        @param titletext String of the title
        @return Sizer

        """
        paneltitle = wx.Panel(self, -1)
        paneltitle.SetBackgroundColour( self.preferences.GetValue('M_BGD_COLOUR') )

        panelimage = ImgPanel(paneltitle, 32, APP_ICON)
        panelimage.SetBackgroundColour( self.preferences.GetValue('M_BGD_COLOUR') )

        font = self.preferences.GetValue('M_FONT')
        font.SetWeight(wx.BOLD)

        paneltext = wx.Panel(paneltitle, -1)
        paneltext.SetBackgroundColour( self.preferences.GetValue('M_BGD_COLOUR') )
        s = wx.BoxSizer()
        text = wx.StaticText(paneltext, label=program+" - "+title, style=wx.ALIGN_CENTER)
        text.SetFont( font )
        s.Add(text, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL)
        paneltext.SetSizer(s)

        title_layout = wx.BoxSizer(wx.HORIZONTAL)
        title_layout.Add(panelimage, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=4)
        title_layout.Add(paneltext,  proportion=1, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=4)
        paneltitle.SetSizer( title_layout )

        return paneltitle

    # ------------------------------------------------------------------------

    def _create_content(self):
        """
        Create the frame content.

        """
        splitpanel = wx.SplitterWindow(self, -1, style=wx.SP_NOBORDER)
        self.flp   = FiletreePanel(splitpanel, self.preferences)

        self._rightpanel = wx.Panel(splitpanel,-1)
        self._contentsizer = wx.BoxSizer()
        self.actions = MainButtonsPanel(self._rightpanel, self.preferences)
        self._contentsizer.Add(self.actions, proportion=1, flag=wx.EXPAND)
        self._rightpanel.SetSizer(self._contentsizer)

        splitpanel.SplitVertically( self.flp , self._rightpanel, sashPosition=0 )
        splitpanel.SetSashGravity(0.5)
        splitpanel.SetMinimumPaneSize( MIN_PANEL_W )

        return splitpanel

    # ------------------------------------------------------------------------

    def _frame_properties(self):
        """
        Fix frame size (adjust size depending on screen capabilities).

        """
        self._mainmenu.SetMinSize((-1,MIN_FRAME_H))
        self._maintitle.SetMinSize((MIN_PANEL_H,-1))
        self.flp.SetMinSize((MIN_PANEL_W,MIN_PANEL_H))
        self.actions.SetMinSize((MIN_PANEL_W,MIN_PANEL_H))

        self.SetMinSize( (MIN_FRAME_W,MIN_FRAME_H) )
        self.Centre()
        self.Enable()
        self.SetFocus()

    # ------------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def ProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.

        """
        ide = event.GetId()
        logging.debug('Event id: %d'%ide)

        if ide == wx.ID_EXIT:
            self.OnExit(event)
            return True
        elif ide == wx.ID_PREFERENCES:
            self.OnSettings(event)
            return True
        elif ide == wx.ID_ABOUT:
            wx.AboutBox( AboutBox() )
            return True
        elif ide == wx.ID_HELP:
            HelpBrowser( self, self.preferences )
            return True
        elif ide == ID_PLUGINS:
            #self.ppp.Import()
            return True
        elif ide == ID_ANNOTATE:
            self._contentsizer.Detach( self.actions )
            self.actions.Destroy()
            self.actions = AnnotationsPanel(self._rightpanel, self.preferences)
            self._contentsizer.Add( self.actions, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)
            self.Refresh()
            self.Layout()
            return True
        elif ide == ID_COMPONENTS:
            self._contentsizer.Detach( self.actions )
            self.actions.Destroy()
            self.actions = ComponentsPanel(self._rightpanel, self.preferences)
            self._contentsizer.Add( self.actions, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)
            self.Refresh()
            self.Layout()
            return True

    # -----------------------------------------------------------------------

    def OnExit(self, evt):
        """
        Close the frame.

        """
        logging.info("Good bye... Hope to see you soon!")
        self.Destroy()

    # -----------------------------------------------------------------------

    def OnSettings(self, event):
        """
        Open the Settings dialog.

        """
        import copy
        p = copy.deepcopy( self.preferences )
        #p = self._prefsIO.Copy() # does not work!

        prefdlg = SettingsDialog( self, p )
        res = prefdlg.ShowModal()
        if res == wx.ID_OK:
            self.SetPrefs( prefdlg.GetPreferences() )

        prefdlg.Destroy()

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Functions
    # -----------------------------------------------------------------------

    def SetPrefs(self, prefs):
        """
        Set new preferences.

        """
        self.preferences = prefs
        self.flp.SetPrefs( self.preferences )

        self._contentsizer.Detach(self.actions)
        self.actions.Destroy()
        self.actions = MainButtonsPanel(self._rightpanel, self.preferences)
        self._contentsizer.Add( self.actions, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)

        self.Refresh()
        self.Layout()

    # -----------------------------------------------------------------------

    def GetSelected(self, extension):
        """
        Return the list of selected files in FLP.

        """
        return self.flp.GetSelected(extension)

    # -----------------------------------------------------------------------

    def GetTrsSelection(self):
        """
        Return the list of annotated files selected in the FLP.

        """
        selection = []
        for ext in annotationdata.io.extensions:
            selection.extend(self.flp.GetSelected(ext))
        return selection

    # -----------------------------------------------------------------------

    def GetAudioSelection(self):
        """
        Return the list of audio files selected in the FLP.

        """
        selection = []
        for ext in audiodata.io.extensions:
            selection.extend( self.flp.GetSelected(ext) )
        return selection

    # -----------------------------------------------------------------------

    def RefreshTree(self, filelist=None):
        """
        Refresh the tree of the FLP.

        """
        self.flp.RefreshTree(filelist)

    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------

if __name__ == "__main__":

    app = wx.PySimpleApp()
    frame = FrameSPPAS(None)
    frame.Show()
    app.MainLoop()

# ---------------------------------------------------------------------------
