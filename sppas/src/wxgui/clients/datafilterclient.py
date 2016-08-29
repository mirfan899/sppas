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
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os.path
import wx
import wx.lib.scrolledpanel as scrolled
import logging

from wxgui.sp_icons import TIER_DELETE
from wxgui.sp_icons import TIER_PREVIEW
from wxgui.sp_icons import FILTER_CHECK
from wxgui.sp_icons import FILTER_UNCHECK
from wxgui.sp_icons import FILTER_SINGLE
from wxgui.sp_icons import FILTER_RELATION
from wxgui.sp_icons import SAVE_FILE
from wxgui.sp_icons import SAVE_ALL_FILE
from wxgui.sp_icons import SAVE_AS_FILE

from wxgui.ui.CustomEvents  import FileWanderEvent, spEVT_FILE_WANDER
from wxgui.ui.CustomEvents  import spEVT_PANEL_SELECTED
from wxgui.ui.CustomEvents  import spEVT_SETTINGS

from baseclient              import BaseClient
from wxgui.structs.themes    import BaseTheme
from wxgui.structs.files     import xFiles
from wxgui.structs.prefs     import Preferences
from wxgui.cutils.imageutils import spBitmap
import wxgui.dialogs.filedialogs as filedialogs
from wxgui.dialogs.msgdialogs import ShowInformation
from wxgui.dialogs.msgdialogs import ShowYesNoQuestion

from wxgui.panels.trslist        import TrsList
from wxgui.panels.mainbuttons    import MainToolbarPanel
from wxgui.views.singlefilter    import SingleFilterDialog
from wxgui.views.relationfilter  import RelationFilterDialog
from wxgui.process.filterprocess import FilterProcess

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

SAVE_AS_ID    = wx.NewId()
SAVE_ALL_ID   = wx.NewId()
PREVIEW_ID    = wx.NewId()
FILTER_CHECK_ID   = wx.NewId()
FILTER_UNCHECK_ID = wx.NewId()
FILTER_SEL_ID = wx.NewId()
FILTER_REL_ID = wx.NewId()

# ----------------------------------------------------------------------------
# Main class that manage the notebook
# ----------------------------------------------------------------------------

class DataFilterClient( BaseClient ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to manage the opened files.

    This class manages the pages of a notebook with all opened files.

    Each page (except if empty...) contains an instance of a DataFilter.

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
        return DataFilter(parent, prefsIO)


# ----------------------------------------------------------------------------
# The Component is the content of one page of the notebook.
# ----------------------------------------------------------------------------

class DataFilter( scrolled.ScrolledPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: This component allows to manage annotated files.

    It is used to select which tiers will be filtered.

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
        sizer.Add(self._trssizer, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=4)

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
        """
        Creates a toolbar panel.

        """
        toolbar = MainToolbarPanel(self, self._prefsIO)
        toolbar.AddButton( wx.ID_SAVE,    SAVE_FILE,    'Save', tooltip="Save the selected file.")
        toolbar.AddButton( SAVE_AS_ID,    SAVE_AS_FILE, 'Save As', tooltip="Save as... the selected file.")
        toolbar.AddButton( SAVE_ALL_ID,   SAVE_ALL_FILE, 'Save All', tooltip="Save all files of the page.")
        toolbar.AddSpacer()

        toolbar.AddButton( FILTER_CHECK_ID, FILTER_CHECK, 'Check', tooltip="Choose the tier(s) to check.")
        toolbar.AddButton( FILTER_UNCHECK_ID, FILTER_UNCHECK, 'Uncheck', tooltip="Uncheck all the tier(s) of the page.")
        toolbar.AddButton( wx.ID_DELETE, TIER_DELETE, 'Delete', tooltip="Delete all the checked tier(s) of the page.")
        toolbar.AddButton( PREVIEW_ID, TIER_PREVIEW, 'View', tooltip="Preview one checked tier of the selected file.")
        toolbar.AddSpacer()

        toolbar.AddButton( FILTER_SEL_ID, FILTER_SINGLE, 'Single', tooltip="Filter checked tier(s) depending on its annotations.")
        toolbar.AddButton( FILTER_REL_ID, FILTER_RELATION, 'Relation', tooltip="Filter checked tier(s) depending on time-relations of its annotation with annotations of another tier.")
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
        ide = event.GetId()

        if ide == wx.ID_SAVE:
            self.OnSave(event)
            return True
        elif ide == SAVE_AS_ID:
            self.OnSaveAs(event)
            return True
        elif ide == SAVE_ALL_ID:
            self.OnSaveAll(event)
            return True

        elif ide == wx.ID_DELETE:
            self.OnDelete(event)
            return True
        elif ide == PREVIEW_ID:
            self.OnPreview(event)
            return True

        elif ide == FILTER_CHECK_ID:
            self.OnCheck(event)
            return True
        elif ide == FILTER_UNCHECK_ID:
            self.OnUncheck(event)
            return True

        elif ide == FILTER_SEL_ID:
            self.OnSingleFilter(event)
            return True
        elif ide == FILTER_REL_ID:
            self.OnRelationFilter(event)
            return True

        return wx.GetApp().ProcessEvent(event)

    # ------------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

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

    # ------------------------------------------------------------------------

    def OnPanelSelection(self, event):
        """
        Change the current selection (the transcription file that was clicked on).

        """
        self._selection = event.panel
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.SetBackgroundColour(wx.Colour(245,235,210))
            else:
                p.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR'))


    # -----------------------------------------------------------------------
    # Toolbar actions...
    # -----------------------------------------------------------------------

    def OnCheck(self, event):
        """
        Choose tiers to check.

        """
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


    def OnUncheck(self, event):
        """
        Un-check all tiers in all files.

        """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.Deselect()


    def OnDelete(self, event):
        """
        Delete all checked tiers of all panels.

        """
        delete = 0
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            d = p.Delete()
            delete = delete + d


    def OnPreview(self, event):
        """
        Open a frame to view a tier.

        """
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
            pass

        else:
            ShowInformation( self, self._prefsIO, "You must check only one tier to view...", style=wx.ICON_WARNING)

    # ----------------------------------------------------------------------

    def OnSave(self, event):
        """
        Save the selected file.

        """

        if self._selection is None:
            ShowInformation( self, self._prefsIO, "No file selected!\nClick on a tier to select a file...", style=wx.ICON_INFORMATION)
            return

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Save()

    # ----------------------------------------------------------------------

    def OnSaveAs(self, event):
        """
        Save as... the selected file.

        """
        if self._selection is None:
            ShowInformation( self, self._prefsIO, 'No file selected!\nClick on a tier to select a file...', style=wx.ICON_INFORMATION)
            return

        found = -1
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                found = i
                break

        if found > -1:
            f = self._filetrs.GetFilename(i)
            p = self._filetrs.GetObject(i)

            # Ask for the new file name
            filename = filedialogs.SaveAsAnnotationFile()

            if filename is None:
                return

            # do not erase the file if it is already existing!
            if os.path.exists( filename ) and f != filename:
                ShowInformation( self, self._prefsIO, "File not saved: this file name is already existing!", style=wx.ICON_INFORMATION)
            elif f == filename :
                p.Save()
            else:
                p.SaveAs( filename )
                # Add the newly created file in the file manager
                evt = FileWanderEvent(filename=filename,status=True)
                evt.SetEventObject(self)
                wx.PostEvent(self.GetTopLevelParent(), evt)

                evt = FileWanderEvent(filename=filename, status=True)
                evt.SetEventObject(self)
                wx.PostEvent( self.GetParent().GetParent().GetParent(), evt )

    # ----------------------------------------------------------------------

    def OnSaveAll(self, event):
        """
        Save all files.

        """
        for i in range(self._filetrs.GetSize()):
            o = self._filetrs.GetObject(i)
            o.Save()

    # ----------------------------------------------------------------------

    def OnSingleFilter(self, event):
        """
        Filter selected tiers with Sel predicate.

        """
        dlg = SingleFilterDialog(self, self._prefsIO)
        if dlg.ShowModal() == wx.ID_OK:

            # Match all or match any of the predicates
            match_all = dlg.GetMatchAll()
            # Output tier name
            tiername = dlg.GetFiltererdTierName()
            # List of SinglePredicates
            psel = dlg.GetPredicates()
            # OK, go...
            if len(psel):
                process = FilterProcess(psel, [], match_all, tiername, self._filetrs)
                process.RunSingleFilter()

        dlg.Destroy()


    def OnRelationFilter(self, event):
        """
        Filter selected tiers with Rel predicate.

        """
        (tiersX,tiersY) = self._get_tiernames()
        dlg = RelationFilterDialog(self, self._prefsIO, tiersX, tiersY)

        if dlg.ShowModal() == wx.ID_OK:
            # Output tier name
            tiername = dlg.GetFiltererdTierName()
            # Relation Tier name
            reltiername = dlg.GetRelationTierName()
            # The RelationPredicate to be applied
            prel = dlg.GetPredicate()
            annotformat = dlg.GetAnnotationFormat()

            # OK, go...
            if prel:
                process = FilterProcess([], prel, False, tiername, self._filetrs)
                process.RunRelationFilter( self, reltiername, annotformat )

        dlg.Destroy()


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
        """
        Change font of all texts.

        """
        wx.Window.SetFont( self,font )
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetFont( font )

    # ----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """
        Change background of all texts.

        """
        wx.Window.SetBackgroundColour( self,color )
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetBackgroundColour(color)

    # ----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """
        Change foreground of all texts.

        """
        wx.Window.SetForegroundColour( self,color )
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetForegroundColour(color)

    # ----------------------------------------------------------------------
    # Manage the data
    # ----------------------------------------------------------------------

    def SetData(self, filename):
        """
        Add a file.

        """
        # Do not add an existing file
        if self._filetrs.Exists( filename ):
            return False

        # Add the file...

        # create the object
        newtrs = TrsList(self, filename, multiple=self._prefsIO.GetValue('F_CCB_MULTIPLE'))
        newtrs.SetPreferences( self._prefsIO )
        newtrs.Protect()
        if newtrs.GetTranscription().GetName() == "IO-Error":
            ShowInformation( self, self._prefsIO, 'Error loading: '+filename, style=wx.ICON_ERROR)

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
        """
        Remove the given file.

        """
        if self._filetrs.Exists(f):
            i = self._filetrs.GetIndex(f)
            o = self._filetrs.GetObject(i)

            if o._dirty is True:
                # dlg to ask to save or not
                userChoice = ShowYesNoQuestion( None, self._prefsIO, "Do you want to save changes on the transcription of\n%s?"%f)
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
        """
        Clean information and destroy all data.

        """
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

# ----------------------------------------------------------------------------
