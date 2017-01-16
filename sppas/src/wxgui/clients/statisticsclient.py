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

from wxgui.ui.CustomEvents  import FileWanderEvent, spEVT_FILE_WANDER
from wxgui.ui.CustomEvents  import spEVT_PANEL_SELECTED
from wxgui.ui.CustomEvents  import spEVT_SETTINGS

from baseclient              import BaseClient
from wxgui.structs.theme    import sppasTheme
from wxgui.structs.files     import xFiles
from wxgui.structs.prefs     import Preferences
from wxgui.cutils.imageutils import spBitmap

import wxgui.dialogs.filedialogs as filedialogs
from wxgui.dialogs.msgdialogs    import ShowInformation
from wxgui.dialogs.msgdialogs    import ShowYesNoQuestion

from wxgui.panels.trslist         import TrsList
from wxgui.panels.mainbuttons     import MainToolbarPanel
from wxgui.views.descriptivestats import DescriptivesStatsDialog
from wxgui.views.useragreement    import UserAgreementDialog
from wxgui.views.tga              import TGADialog

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

    # ------------------------------------------------------------------------

    def _update_members(self):
        """
        Update members.
        """
        self._multiplefiles = True

        # Quick and dirty solution to communicate to the file manager:
        self._prefsIO.SetValue( 'F_CCB_MULTIPLE', t='bool', v=True, text='')

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
        self.SetBackgroundColour(prefsIO.GetValue('M_BG_COLOUR'))

        # imitate the behavior of a toolbar, with buttons
        self.toolbar = self._create_toolbar()
        sizer.Add(self.toolbar, proportion=0, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=4)

        # sizer
        self._trssizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add(self._trssizer, proportion=1, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border=4)

        # Bind events
        self.Bind(spEVT_PANEL_SELECTED, self.OnPanelSelection)
        self.Bind(spEVT_FILE_WANDER,    self.OnFileWander)
        self.Bind(spEVT_SETTINGS,       self.OnSettings)
        self.Bind(wx.EVT_BUTTON,        self.ProcessEvent)

        self.SetSizer(sizer)
        self.SetAutoLayout( True )
        self.Layout()

        self.SetupScrolling()

    # ----------------------------------------------------------------------

    def _check_prefs(self, prefs):
        """
        Check if preferences are set properly. Set new ones if required.
        Return the new version.
        """
        if prefs is None:
            prefs = Preferences( sppasTheme() )
        else:
            try:
                bg = prefs.GetValue( 'M_BG_COLOUR' )
                fg = prefs.GetValue( 'M_FG_COLOUR' )
                font = prefs.GetValue( 'M_FONT' )
                icons = prefs.GetValue( 'M_ICON_THEME' )
            except Exception:
                self._prefsIO.SetTheme( sppasTheme() )
        return prefs

    #-------------------------------------------------------------------------

    def _create_toolbar(self):
        """ Creates a toolbar panel. """

        toolbar = MainToolbarPanel(self, self._prefsIO)
        toolbar.AddButton( FILTER_CHECK_ID, FILTER_CHECK, 'Check', tooltip="Choose the tier(s) to check.")
        toolbar.AddButton( FILTER_UNCHECK_ID, FILTER_UNCHECK, 'Uncheck', tooltip="Uncheck all the tier(s) of the page.")
        toolbar.AddButton( PREVIEW_ID, TIER_PREVIEW, 'View', tooltip="Preview one checked tier of the selected file.")
        toolbar.AddSpacer()
        toolbar.AddButton( DESCRIPTIVES_ID, SPREADSHEETS, 'Statistics', tooltip="Estimates descriptive statistics of checked tier(s).")
        toolbar.AddButton( TIMEANALYSIS_ID, TIMEANALYSIS, 'TGA', tooltip="Estimates TGA - Time GroupAnalyses of checked tier(s).")
        toolbar.AddButton( USERCHECK_ID, USERCHECK, 'User\nAgreement', tooltip="Estimates Kappa of checked tier(s).")
        toolbar.AddSpacer()
        return toolbar


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
        dlg = wx.TextEntryDialog(self,'What is the name of tier(s) to check?','Tier checker', '')
        case_sensitive=False # TODO: add a check button in the entry dialog
        ret = dlg.ShowModal()

        # Let's check if user clicked OK or pressed ENTER
        if ret == wx.ID_OK:
            tiername = dlg.GetValue()
            for i in range(self._filetrs.GetSize()):
                p = self._filetrs.GetObject(i)
                r = p.Select( tiername, case_sensitive )
                if r: nb = nb+1
        dlg.Destroy()


    def OnUncheck(self, event):
        """ Un-check all tiers in all files. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.Deselect()


    def OnPreview(self, event):
        """ Open a frame to view a tier. """
        # Show the tier which is checked in the selected files
        nb = self._get_nbselectedtiers(inselection=True)
        if nb == 1:
            self._selection.Preview()
        else:
            # show the tier which is checked... even if it's not in a selected file
            nb = self._get_nbselectedtiers(inselection=False)
            if nb == 0:
                ShowInformation(self, self._prefsIO, "One tier must be checked.", wx.ICON_INFORMATION)
            elif nb == 1:
                for i in range(self._filetrs.GetSize()):
                    p = self._filetrs.GetObject(i)
                    if p.tier_list.GetSelectedItemCount()==1:
                        p.Preview()
            else:
                ShowInformation(self, self._prefsIO, "Only one tier must be checked.", wx.ICON_INFORMATION)


    # ----------------------------------------------------------------------

    def OnDescriptivesStats(self, event):
        """ Descriptives Statistics ."""
        nb = self._get_nbselectedtiers(inselection=False)
        logging.debug(' OnDescriptivesStats: %d tier(s) selected'%nb)
        if nb > 0:
            dlg = DescriptivesStatsDialog(self, self._prefsIO, self._get_selectedtiers())
            dlg.ShowModal()
            dlg.Destroy()
        else:
            ShowInformation(self, self._prefsIO, "At least one tier must be checked!", wx.ICON_INFORMATION)

    def OnUserAgreement(self, event):
        """ User agreement ."""
        nb = self._get_nbselectedtiers(inselection=False)
        if nb == 2:
            dlg = UserAgreementDialog(self, self._prefsIO, self._get_selectedtiers())
            dlg.ShowModal()
            dlg.Destroy()
        else:
            ShowInformation(self, self._prefsIO, "Two tiers must be checked!", wx.ICON_WARNING)

    def OnTimeGroupAnalysis(self, event):
        """ Time Group Analysis ."""
        nb = self._get_nbselectedtiers(inselection=False)
        if nb > 0:
            dlg = TGADialog(self, self._prefsIO, self._get_selectedtiers())
            dlg.ShowModal()
            dlg.Destroy()
        else:
            ShowInformation(self, self._prefsIO, "At least one tier must be checked!", wx.ICON_INFORMATION)

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

    # ----------------------------------------------------------------------

    def SetFont(self, font):
        """ Change font of all texts. """

        wx.Window.SetFont( self,font )
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetFont( font )

    # ----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """ Change background of all texts. """

        wx.Window.SetBackgroundColour( self,color )
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetBackgroundColour(color)

    # ----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """ Change foreground of all texts. """

        wx.Window.SetForegroundColour( self,color )
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetForegroundColour(color)

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
            ShowInformation(self, self._prefsIO, 'Error loading: '+filename, style=wx.ICON_ERROR)

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

    # ----------------------------------------------------------------------

    def UnsetData(self, f):
        """ Remove the given file. """

        if self._filetrs.Exists(f):
            i = self._filetrs.GetIndex(f)
            o = self._filetrs.GetObject(i)

            if o._dirty is True:
                # dlg to ask to save or not
                userChoice = ShowYesNoQuestion( None, self._prefsIO, "Do you want to save changes of the file %s?"%f)
                if userChoice == wx.ID_YES:
                    o.Save()

            o.Destroy()
            self._filetrs.Remove(i)
            self._trssizer.Remove(i)

        #self.Layout()
        #self.Refresh()
        self.SendSizeEvent()

    # ----------------------------------------------------------------------

    def UnsetAllData(self):
        """ Clean information and destroy all data. """

        self._filetrs.RemoveAll()
        self._trssizer.DeleteWindows()

        self.Layout()


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

    def _get_selectedtiers(self):
        """ Create a list of selected tiers for each file. """
        data = {}
        for i in range(self._filetrs.GetSize()):
            fname = self._filetrs.GetFilename(i)
            # obj is a TrsList instance
            obj = self._filetrs.GetObject(i)
            trs = obj.GetTranscription()
            for tier in trs:
                if obj.IsSelected(tier.GetName()):
                    if not fname in data.keys():
                        data[fname] = []
                    data[fname].append(tier)
        return data

    def _get_nbselectedtiers(self, inselection=False):
        """ Get the number of selected tiers. """
        nb = 0
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if inselection is False or (inselection is True and p == self._selection):
                nb = nb + p.tier_list.GetSelectedItemCount()
        return nb

# ----------------------------------------------------------------------------

