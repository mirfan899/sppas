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
import webbrowser

import annotationdata
import audiodata

from wxgui.cutils.imageutils import spBitmap
from wxgui.sp_icons import APP_ICON
import wxgui.structs.prefs

from wxgui.sp_consts import MIN_FRAME_W, MIN_PANEL_W, PANEL_W
from wxgui.sp_consts import MIN_FRAME_H, MIN_PANEL_H, FRAME_H
from wxgui.sp_consts import FRAME_STYLE
from wxgui.sp_consts import FRAME_TITLE

from wxgui.sp_consts          import ID_ANNOTATIONS
from wxgui.sp_consts          import ID_COMPONENTS
from wxgui.sp_consts          import ID_PLUGINS
from wxgui.sp_consts          import ID_ACTIONS
from wxgui.sp_consts          import ID_EXT_BUG
from wxgui.sp_consts          import ID_EXT_HOME
from wxgui.sp_consts          import ID_FEEDBACK
from wxgui.sp_consts          import ID_FRAME_DATAROAMER
from wxgui.sp_consts          import ID_FRAME_SNDROAMER
from wxgui.sp_consts          import ID_FRAME_IPUSCRIBE
from wxgui.sp_consts          import ID_FRAME_SPPASEDIT
from wxgui.sp_consts          import ID_FRAME_STATISTICS
from wxgui.sp_consts          import ID_FRAME_DATAFILTER

from wxgui.panels.filetree         import FiletreePanel
from wxgui.panels.mainbuttons      import MainActionsPanel, MainMenuPanel, MainActionsMenuPanel, MainTitlePanel
from wxgui.panels.components       import AnalyzePanel
from wxgui.panels.aannotations     import AnnotationsPanel
from wxgui.panels.plugins          import PluginPanel
from wxgui.panels.about            import AboutSPPAS

from wxgui.frames.dataroamerframe  import DataRoamerFrame
from wxgui.frames.audioroamerframe import AudioRoamerFrame
from wxgui.frames.ipuscribeframe   import IPUscribeFrame
from wxgui.frames.sppaseditframe   import SppasEditFrame
from wxgui.frames.datafilterframe  import DataFilterFrame
from wxgui.frames.statisticsframe  import StatisticsFrame
from wxgui.frames.helpbrowser      import HelpBrowser
from wxgui.views.settings          import SettingsDialog
from wxgui.views.settings          import SettingsDialog
from wxgui.views.feedback          import ShowFeedbackDialog

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
            preferencesIO = wxgui.structs.prefs.Preferences_IO()
        self.preferences = preferencesIO

        # Create GUI
        self._init_infos()
        self.actions = None
        self.flp     = None

        self._mainmenu  = MainMenuPanel(self,  self.preferences)
        self._maintitle = MainTitlePanel(self, self.preferences)
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
        """  Set the title and the icon. """

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

    def _create_content(self):
        """ Create the frame content. """

        splitpanel = wx.SplitterWindow(self, -1, style=wx.SP_NOBORDER)
        splitpanel.SetBackgroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        splitpanel.SetForegroundColour( self.preferences.GetValue('M_BG_COLOUR') )

        # Left: File explorer
        self.flp   = FiletreePanel(splitpanel, self.preferences)

        # Right: Actions to perform on selected files
        self._rightpanel = wx.Panel(splitpanel,-1)
        self._contentsizer = wx.BoxSizer( wx.VERTICAL )
        self.actionsmenu = MainActionsMenuPanel(self._rightpanel, self.preferences)
        self.actionsmenu.ShowBack(False)
        self.actions     = MainActionsPanel(self._rightpanel, self.preferences)
        self._contentsizer.Add( self.actionsmenu, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)
        self._contentsizer.Add( self.actions,     proportion=1, flag=wx.ALL|wx.EXPAND, border=0)
        self._rightpanel.SetSizer(self._contentsizer)

        splitpanel.SplitVertically( self.flp , self._rightpanel, sashPosition=0 )
        splitpanel.SetSashGravity(0.5)
        splitpanel.SetMinimumPaneSize( MIN_PANEL_W )

        return splitpanel

    # ------------------------------------------------------------------------

    def _frame_properties(self):
        """ Fix frame size (adjust size depending on screen capabilities). """

        self._mainmenu.SetMinSize((32,MIN_FRAME_H))
        self._maintitle.SetMinSize((-1,32))
        self.flp.SetMinSize((MIN_PANEL_W,MIN_PANEL_H))
        self.actions.SetMinSize((MIN_PANEL_W,MIN_PANEL_H))

        self.SetMinSize( (MIN_FRAME_W,MIN_FRAME_H) )
        self.Centre()
        self.Enable()
        self.SetFocus()

    # ------------------------------------------------------------------------

    def fix_actioncontent( self, ide ):
        """ Fix the action panel content. """

        # Remove current actions panel
        if self.actions is not None:
            self._contentsizer.Detach( self.actions )
            self.actions.Destroy()

        # Create the new one:
        if ide == ID_ACTIONS:
            self.actions = MainActionsPanel(self._rightpanel, self.preferences)
            self.actionsmenu.ShowBack(False, "")

        elif ide == ID_COMPONENTS:
            self.actions = AnalyzePanel(self._rightpanel, self.preferences)
            self.actionsmenu.ShowBack(True, "   A N A L Y Z E ")

        elif ide == ID_ANNOTATIONS:
            self.actions = AnnotationsPanel(self._rightpanel, self.preferences)
            self.actionsmenu.ShowBack(True, "   A N N O T A T E ")

        elif ide == wx.ID_ABOUT:
            self.actions = AboutSPPAS(self._rightpanel, self.preferences)
            self.actionsmenu.ShowBack(True, "   A B O U T ")

        self._contentsizer.Add( self.actions, proportion=1, flag=wx.ALL|wx.EXPAND, border=0)
        self.Refresh()
        self.Layout()

    # -----------------------------------------------------------------------

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

        elif ide == wx.ID_PREFERENCES:
            self.OnSettings(event)

        elif ide == wx.ID_HELP:
            self.OnHelp(event)

        elif ide == ID_PLUGINS:
            pass
            #self.ppp.Import()

        elif ide == wx.ID_ABOUT:
            self.fix_actioncontent( wx.ID_ABOUT )

        elif ide == ID_ANNOTATIONS:
            self.fix_actioncontent( ID_ANNOTATIONS )

        elif ide == ID_COMPONENTS:
            self.fix_actioncontent( ID_COMPONENTS )

        elif ide == ID_ACTIONS:
            self.fix_actioncontent( ID_ACTIONS )

        elif ide == ID_EXT_HOME or ide == ID_EXT_BUG:
            self.OnExternalLink(event)

        elif ide == ID_FEEDBACK:
            ShowFeedbackDialog(self, preferences=self.preferences)

        elif ide == ID_FRAME_DATAROAMER or ide == ID_FRAME_SNDROAMER or ide == ID_FRAME_IPUSCRIBE or ide == ID_FRAME_SPPASEDIT or ide == ID_FRAME_DATAFILTER or ide == ID_FRAME_STATISTICS:
            self.OnAnalyzer(event)

        return True

    # -----------------------------------------------------------------------

    def OnExit(self, evt):
        """
        Close the frame.

        """
        self.Destroy()

    # -----------------------------------------------------------------------

    def OnSettings(self, event):
        """ Open the Settings dialog. """

        import copy
        p = copy.deepcopy( self.preferences )
        #p = self._prefsIO.Copy() # does not work!

        prefdlg = SettingsDialog( self, p )
        res = prefdlg.ShowModal()
        if res == wx.ID_OK:
            self.SetPrefs( prefdlg.GetPreferences() )

        prefdlg.Destroy()

    # -----------------------------------------------------------------------

    def OnHelp(self, evt):
        """ Open the help frame. """

        for c in self.GetChildren():
            if isinstance(c,HelpBrowser):
                c.SetFocus()
                c.Raise()
                return True
        HelpBrowser( self, self.preferences )

    # -----------------------------------------------------------------------

    def OnExternalLink(self, evt):
        """ Open the web browser, go to a specific location. """

        eid = evt.GetId()

        if eid == ID_EXT_HOME:
            url="http://www.sppas.org/"

        elif eid == ID_EXT_BUG:
            url="https://github.com/brigittebigi/sppas/issues/"

        else:
            evt.Skip()
            return

        # It seems under some cases when running under windows the call to
        # subprocess in webbrowser will fail and raise an exception here. So
        # simply trap and ignore it.
        wx.BeginBusyCursor()
        try:
            webbrowser.open(url,1)
        except:
            pass
        wx.EndBusyCursor()

    # -----------------------------------------------------------------------

    def __create_component(self, instance, idc):
        """ Create or raise a component frame and return it. """

        for c in self.GetChildren():
            if isinstance(c,instance):
                c.SetFocus()
                c.Raise()
                return c
        return instance(self, idc, self.preferences)

    # -----------------------------------------------------------------------

    def OnAnalyzer(self, evt):
        """ Open a component. """

        eid = evt.GetId()
        selection = []

        if eid == ID_FRAME_DATAROAMER:
            selection = self.GetTrsSelection()
            analyzer = self.__create_component(DataRoamerFrame, ID_FRAME_DATAROAMER)

        elif eid == ID_FRAME_SNDROAMER:
            selection = self.GetAudioSelection()
            analyzer = self.__create_component(AudioRoamerFrame, ID_FRAME_SNDROAMER)

        elif eid == ID_FRAME_SPPASEDIT:
            selection = self.GetTrsSelection() + self.GetAudioSelection()
            analyzer = self.__create_component(SppasEditFrame, ID_FRAME_SPPASEDIT)

        elif eid == ID_FRAME_IPUSCRIBE:
            selection = self.GetAudioSelection()
            analyzer = self.__create_component(IPUscribeFrame, ID_FRAME_IPUSCRIBE)

        elif eid == ID_FRAME_DATAFILTER:
            selection = self.GetTrsSelection()
            analyzer = self.__create_component(DataFilterFrame, ID_FRAME_DATAFILTER)

        elif eid == ID_FRAME_STATISTICS:
            selection = self.GetTrsSelection()
            analyzer = self.__create_component(StatisticsFrame, ID_FRAME_STATISTICS)

        if len(selection) > 0:
            analyzer.AddFiles( selection )

    # -----------------------------------------------------------------------
    # Functions
    # -----------------------------------------------------------------------

    def SetPrefs(self, prefs):
        """ Set new preferences. """

        self.preferences = prefs
        self.flp.SetPrefs( self.preferences )

        self._contentsizer.Detach(self.actions)
        self.actions.Destroy()
        self.actions = MainActionsPanel(self._rightpanel, self.preferences)
        self._contentsizer.Add( self.actions, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)

        self.Refresh()
        self.Layout()

    # -----------------------------------------------------------------------

    def GetSelected(self, extension):
        """ Return the list of selected files in FLP. """

        return self.flp.GetSelected(extension)

    # -----------------------------------------------------------------------

    def GetTrsSelection(self):
        """ Return the list of annotated files selected in the FLP. """

        selection = []
        for ext in annotationdata.io.extensions:
            selection.extend(self.flp.GetSelected(ext))
        return selection

    # -----------------------------------------------------------------------

    def GetAudioSelection(self):
        """ Return the list of audio files selected in the FLP. """

        selection = []
        for ext in audiodata.io.extensions:
            selection.extend( self.flp.GetSelected(ext) )
        return selection

    # -----------------------------------------------------------------------

    def RefreshTree(self, filelist=None):
        """ Refresh the tree of the FLP. """

        self.flp.RefreshTree(filelist)

    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------

if __name__ == "__main__":

    app = wx.PySimpleApp()
    frame = FrameSPPAS(None)
    frame.Show()
    app.MainLoop()

# ---------------------------------------------------------------------------
