#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------
# File: datafilterclient.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os.path
import wx
import wx.lib.scrolledpanel as scrolled
import logging

from wxgui.sp_icons import TIMEANALYSIS
from wxgui.sp_icons import USERCHECK
from wxgui.sp_icons import SPREADSHEETS
from wxgui.sp_icons import FILTER_CHECK
from wxgui.sp_icons import FILTER_UNCHECK
from wxgui.sp_icons import TIER_PREVIEW

from wxgui.sp_consts import TB_ICONSIZE
from wxgui.sp_consts import TB_FONTSIZE

from wxgui.ui.CustomEvents  import FileWanderEvent, spEVT_FILE_WANDER
from wxgui.ui.CustomEvents  import spEVT_PANEL_SELECTED
from wxgui.ui.CustomEvents  import spEVT_SETTINGS

from baseclient              import BaseClient
from wxgui.structs.themes    import BaseTheme
from wxgui.structs.files     import xFiles
from wxgui.structs.prefs     import Preferences
from wxgui.cutils.imageutils import spBitmap
import wxgui.dialogs.filedialogs as filedialogs

from wxgui.panels.trslist        import TrsList
from wxgui.views.descriptivestats import DescriptivesStatsDialog

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

FILTER_CHECK_ID   = wx.NewId()
FILTER_UNCHECK_ID = wx.NewId()
DESCRIPTIVES_ID   = wx.NewId()
USERCHECK_ID      = wx.NewId()
TIMEANALYSIS_ID   = wx.NewId()
PREVIEW_ID        = wx.NewId()

# ----------------------------------------------------------------------------
# Main class that manage the notebook
# ----------------------------------------------------------------------------


class StatisticsClient( BaseClient ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to manage the opened files.

    This class manages the pages of a notebook with all opened files.

    Each page (except if empty...) contains an instance of a Statistics panel.

    """

    def __init__( self, parent, prefsIO ):
        BaseClient.__init__( self, parent, prefsIO )
        self._update_members()

    # End __init__
    # ------------------------------------------------------------------------


    def _update_members(self):
        """
        Update members.
        """
        self._multiplefiles = True

        # Quick and dirty solution to communicate to the file manager:
        self._prefsIO.SetValue( 'F_CCB_MULTIPLE', t='bool', v=True, text='')

    # End _update_members
    # ------------------------------------------------------------------------


    def CreateComponent(self, parent, prefsIO ):
        return Statistics(parent, prefsIO)

    # ------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# The Component is the content of one page of the notebook.
# ----------------------------------------------------------------------------


class Statistics( scrolled.ScrolledPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: This component allows to manage annotated files.

    It is used to select which tiers will be estimated.

    """

    def __init__(self, parent, prefsIO):

        scrolled.ScrolledPanel.__init__(self, parent, -1)
        sizer = wx.BoxSizer( wx.VERTICAL )

        # members
        self._filetrs    = xFiles()
        self._selection  = None # the index of the selected trsdata panel

        self._prefsIO = self._check_prefs(prefsIO)

        # imitate the behavior of a toolbar, with buttons
        self.toolbar = self._create_toolbar()
        sizer.Add(self.toolbar, proportion=0, flag=wx.EXPAND|wx.ALL, border=1 )

        # sizer
        self._trssizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add(self._trssizer, proportion=1, flag=wx.EXPAND|wx.ALL, border=1 )

        # Bind events
        self.Bind(spEVT_PANEL_SELECTED, self.OnPanelSelection)
        self.Bind(spEVT_FILE_WANDER,    self.OnFileWander)
        self.Bind(spEVT_SETTINGS,       self.OnSettings)

        self.SetSizer(sizer)
        self.SetAutoLayout( True )
        self.Layout()

        self.SetupScrolling()

    # End __init__
    # ----------------------------------------------------------------------


    def __display_text_in_statusbar(self, text):
        wx.GetTopLevelParent(self).SetStatusText(text,0)

    def __reset_text_in_statusbar(self):
        wx.GetTopLevelParent(self).SetStatusText('', 0)


    #-------------------------------------------------------------------------


    def _check_prefs(self, prefs):
        """
        Check if preferences are set properly. Set new ones if required.
        Return the new version.
        """
        if prefs is None:
            prefs = Preferences( BaseTheme() )
        else:
            try:
                bg = prefs.GetValue( 'M_BG_COLOUR' )
                fg = prefs.GetValue( 'M_FG_COLOUR' )
                font = prefs.GetValue( 'M_FONT' )
                icons = prefs.GetValue( 'M_ICON_THEME' )
            except Exception:
                self._prefsIO.SetTheme( BaseTheme() )
        return prefs

    #-------------------------------------------------------------------------


    def _create_toolbar(self):
        """ Creates a toolbar panel. """
        # Define the size of the icons and buttons
        iconSize = (TB_ICONSIZE, TB_ICONSIZE)

        toolbar = wx.ToolBar( self, -1, style=wx.TB_TEXT )
        # Set the size of the buttons
        toolbar.SetToolBitmapSize(iconSize)
        toolbar.SetFont( self._prefsIO.GetValue('M_FONT') )

        toolbar.AddLabelTool(FILTER_CHECK_ID,'Check tiers',
                             spBitmap(FILTER_CHECK,TB_ICONSIZE,theme=self._prefsIO.GetValue('M_ICON_THEME')),
                             shortHelp="Choose the tier(s) to check")
        toolbar.AddLabelTool(FILTER_UNCHECK_ID, 'Uncheck tiers',
                             spBitmap(FILTER_UNCHECK,TB_ICONSIZE,theme=self._prefsIO.GetValue('M_ICON_THEME')),
                             shortHelp="Uncheck all")
        toolbar.AddLabelTool(PREVIEW_ID,   'View',
                             spBitmap(TIER_PREVIEW,TB_ICONSIZE,theme=self._prefsIO.GetValue('M_ICON_THEME')),
                             shortHelp="Preview one checked tier of the selected file")

        toolbar.AddSeparator()

        toolbar.AddLabelTool(DESCRIPTIVES_ID, 'Descriptive\nStatistics',
                             spBitmap(SPREADSHEETS,TB_ICONSIZE,theme=self._prefsIO.GetValue('M_ICON_THEME')),
                             shortHelp="Estimates descriptive statistics of checked tier(s).")
        toolbar.AddLabelTool(USERCHECK_ID, 'User\nAgreement',
                             spBitmap(USERCHECK,TB_ICONSIZE,theme=self._prefsIO.GetValue('M_ICON_THEME')),
                             shortHelp="Estimates Kappa of checked tier(s).")
        toolbar.AddLabelTool(TIMEANALYSIS_ID, 'TimeGroup\nAnalysis',
                             spBitmap(TIMEANALYSIS,TB_ICONSIZE,theme=self._prefsIO.GetValue('M_ICON_THEME')),
                             shortHelp="Estimates TGA - Time GroupAnalyses of checked tier(s).")

        toolbar.Realize()

        # events
        eventslist = [ FILTER_CHECK_ID, FILTER_UNCHECK_ID, PREVIEW_ID, DESCRIPTIVES_ID, USERCHECK_ID, TIMEANALYSIS_ID ]
        for event in eventslist:
            wx.EVT_TOOL(self, event, self.ProcessEvent)

        return toolbar

    # End _create_toolbar
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Callbacks to any kind of event
    # ------------------------------------------------------------------------


    def ProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.
        """
        id = event.GetId()
        logging.debug('Statistics. Event received %d' % id)

        if id == FILTER_CHECK_ID:
            self.OnCheck(event)
            return True
        elif id == FILTER_UNCHECK_ID:
            self.OnUncheck(event)
            return True
        elif id == PREVIEW_ID:
            self.OnPreview(event)
            return True

        elif id == TIMEANALYSIS_ID:
            self.OnTimeGroupAnalysis(event)
            return True
        elif id == USERCHECK_ID:
            self.OnUserAgreement(event)
            return True
        elif id == DESCRIPTIVES_ID:
            self.OnDescriptivesStats(event)
            return True

        return wx.GetApp().ProcessEvent(event)

    # End ProcessEvent
    # ------------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Callbacks
    # ----------------------------------------------------------------------


    def OnFileWander(self, event):
        """
        A file was checked/unchecked somewhere else, then, set/unset the data.

        """
        f = event.filename
        s = event.status

        if s is True:
            r = self.SetData( f )
            if r is False:
                evt = FileWanderEvent(filename=f, status=False)
                evt.SetEventObject(self)
                wx.PostEvent( self.GetParent().GetParent().GetParent(), evt )

        else:
            if f is None:
                self.UnsetAllData( )

            else:
                try:
                    self.UnsetData( f )
                    evt = FileWanderEvent(filename=f, status=False)
                    evt.SetEventObject(self)
                    wx.PostEvent( self.GetParent().GetParent().GetParent(), evt )
                except Exception:
                    pass

    # End OnFileWander
    # ------------------------------------------------------------------------


    def OnPanelSelection(self, event):
        """ Change the current selection (the transcription file that was clicked on). """
        self._selection = event.panel
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.SetBackgroundColour(wx.Colour(245,235,210))
            else:
                p.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR'))

    # End OnPanelSelection
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Toolbar actions...
    # -----------------------------------------------------------------------

    def OnCheck(self, event):
        """ Choose tiers to check. """

        nb = 0
        dlg = wx.TextEntryDialog(self,'What is name of tier(s) to check?','Tier checker', '')
        ret = dlg.ShowModal()
        # Let's check if user clicked OK or pressed ENTER
        if ret == wx.ID_OK:
            tiername = dlg.GetValue()
            for i in range(self._filetrs.GetSize()):
                p = self._filetrs.GetObject(i)
                r = p.Select( tiername )
                if r:
                    nb = nb+1
        dlg.Destroy()

        if nb == 0:
            self.__display_text_in_statusbar("No tier selected.")
        else:
            self.__display_text_in_statusbar("%d tier(s) selected."%nb)


    def OnUncheck(self, event):
        """ Un-check all tiers in all files. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            d = p.Deselect()


    def OnPreview(self, event):
        """ Open a frame to view a tier. """
        nb = 0
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                nb = p.tier_list.GetSelectedItemCount()

        if nb == 1:
            for i in range(self._filetrs.GetSize()):
                p = self._filetrs.GetObject(i)
                if p == self._selection:
                    p.Preview()

        elif nb == 0:
            self.__display_text_in_statusbar("Nothing to view: one tier must be selected.")

        else:
            wx.MessageBox('You must check only one tier to view...', 'Warning', wx.OK | wx.ICON_INFORMATION)


    # ----------------------------------------------------------------------

    def OnDescriptivesStats(self, event):
        """ Descriptives Statistics ."""
        logging.debug('Descriptives statistics')

        dlg = DescriptivesStatsDialog(self, self._prefsIO, self._filetrs)
        dlg.ShowModal()
        dlg.Destroy()


    def OnTimeGroupAnalysis(self, event):
        """ Time Group Analysis ."""
        logging.debug('Time Group Analysis')
        dlg = wx.MessageBox("TGA will come soon in SPPAS!\nTGA is available here: http://wwwhomes.uni-bielefeld.de/gibbon/TGA/.", "Not Implemented (yet!)", wx.OK| wx.ICON_INFORMATION)


    def OnUserAgreement(self, event):
        """ User agreement ."""
        logging.debug('User agreement')

        dlg = wx.MessageBox("User agreement estimations will come soon in SPPAS!", "Not Implemented (yet!)", wx.OK| wx.ICON_INFORMATION)

    # ----------------------------------------------------------------------


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

        for i in range(self._filetrs.GetSize()):
            obj = self._filetrs.GetObject(i)
            obj.SetPreferences( self._prefsIO )

        self.Layout()
        self.Refresh()

    # End OnSettings
    # ----------------------------------------------------------------------


    def SetFont(self, font):
        """ Change font of all texts. """

        wx.Window.SetFont( self,font )
        self.toolbar.SetFont( font )

        # Apply to all panels
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetFont( font )

    # End SetFont
    # ----------------------------------------------------------------------


    def SetBackgroundColour(self, color):
        """ Change background of all texts. """

        wx.Window.SetBackgroundColour( self,color )
        self.toolbar.SetBackgroundColour( color )

        # Apply as background on all panels
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetBackgroundColour(color)

    # End SetBackgroundColour
    # ----------------------------------------------------------------------


    def SetForegroundColour(self, color):
        """ Change foreground of all texts. """

        wx.Window.SetForegroundColour( self,color )
        self.toolbar.SetForegroundColour( color )

        # Apply as foreground on all panels
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetForegroundColour(color)

    # End SetForegroundColour
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Manage the data
    # ----------------------------------------------------------------------


    def SetData(self, filename):
        """ Add a file. """

        # Do not add an existing file
        if self._filetrs.Exists( filename ):
            return False

        # Add the file...

        # create the object
        newtrs = TrsList(self, filename, multiple=self._prefsIO.GetValue('F_CCB_MULTIPLE'))
        newtrs.SetPreferences( self._prefsIO )
        newtrs.Protect()
        if newtrs.GetTranscription().GetName() == "IO-Error":
            wx.MessageBox('Error loading: '+filename, 'Info', wx.OK | wx.ICON_INFORMATION)

        # put the new trs in a sizer (required to enable sizer.Remove())
        s = wx.BoxSizer( wx.HORIZONTAL )
        s.Add(newtrs, 1, wx.EXPAND)
        self._trssizer.Add(s, proportion=1, flag=wx.EXPAND|wx.TOP, border=4 )
        # add in the list of files
        self._filetrs.Append(filename,newtrs)

        self.Layout()
        self.Refresh()
        self.SendSizeEvent()

        return True

    # End SetData
    # ----------------------------------------------------------------------


    def UnsetData(self, f):
        """ Remove the given file. """

        if self._filetrs.Exists(f):
            i = self._filetrs.GetIndex(f)
            o = self._filetrs.GetObject(i)

            if o._dirty is True:
                # dlg to ask to save or not
                dial = wx.MessageDialog(None, 'Do you want to save changes on the transcription of\n%s?'%f, 'Question', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                userChoice = dial.ShowModal()
                if userChoice == wx.ID_YES:
                    o.Save()

            o.Destroy()
            self._filetrs.Remove(i)
            self._trssizer.Remove(i)

        #self.Layout()
        #self.Refresh()
        self.SendSizeEvent()

    # End UnsetData
    # ----------------------------------------------------------------------


    def UnsetAllData(self):
        """ Clean information and destroy all data. """

        self._filetrs.RemoveAll()
        self._trssizer.DeleteWindows()

        self.Layout()

    # End UnsetAllData
    # ----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _get_tiernames(self):
        """ Create a list of selected tier names, and the whole list of tier names."""
        tiersX = []
        tiersY = []

        for i in range(self._filetrs.GetSize()):
            obj = self._filetrs.GetObject(i)
            trs = obj.GetTranscription()
            for tier in trs:
                name = tier.GetName()
                if obj.IsSelected(name):
                    if not name in tiersX:
                        tiersX.append(name)
                if not name in tiersY:
                    tiersY.append(name)

        return (sorted(tiersX),sorted(tiersY))

# ----------------------------------------------------------------------------

