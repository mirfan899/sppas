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
# File: dataroamerclient.py
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

from wxgui.sp_icons import TIER_RENAME
from wxgui.sp_icons import TIER_DELETE
from wxgui.sp_icons import TIER_CUT
from wxgui.sp_icons import TIER_COPY
from wxgui.sp_icons import TIER_PASTE
from wxgui.sp_icons import TIER_DUPLICATE
from wxgui.sp_icons import TIER_MOVE_UP
from wxgui.sp_icons import TIER_MOVE_DOWN
from wxgui.sp_icons import TIER_PREVIEW
from wxgui.sp_icons import TIER_RADIUS

from wxgui.ui.CustomEvents  import FileWanderEvent, spEVT_FILE_WANDER
from wxgui.ui.CustomEvents  import spEVT_PANEL_SELECTED
from wxgui.ui.CustomEvents  import spEVT_SETTINGS

from baseclient               import BaseClient
from wxgui.panels.trslist     import TrsList
from wxgui.panels.mainbuttons import MainToolbarPanel
from wxgui.structs.files     import xFiles
from wxgui.structs.prefs     import Preferences
from wxgui.structs.themes    import BaseTheme
from wxgui.cutils.imageutils import spBitmap
import wxgui.dialogs.filedialogs as filedialogs
from wxgui.dialogs.msgdialogs import ShowInformation
from wxgui.dialogs.msgdialogs import ShowYesNoQuestion


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

RENAME_ID      = wx.NewId()
DUPLICATE_ID   = wx.NewId()
PREVIEW_ID     = wx.NewId()
TIER_RADIUS_ID = wx.NewId()

# ----------------------------------------------------------------------------
# Main class that manage the notebook
# ----------------------------------------------------------------------------

class DataRoamerClient( BaseClient ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: This class is used to manage the opened files.

    This class manages the pages of a notebook with all opened files.

    Each page (except if empty...) contains an instance of a DataRoamer.

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
        return DataRoamer(parent, prefsIO)

    # ------------------------------------------------------------------------

    def New(self):
        """
        Add a new file into the current page.
        """
        page = self._notebook.GetCurrentPage()
        # Ask for the new file name
        filename = filedialogs.SaveAsAnnotationFile()
        if filename is None:
            return
        # Add the newly created file in the file manager and that's all!
        evt = FileWanderEvent(filename=filename,status=False)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetTopLevelParent(), evt)

    # ------------------------------------------------------------------------

    def Save(self):
        """
        Save the current file(s).
        """
        page = self._notebook.GetCurrentPage()
        for i in range(self._xfiles.GetSize()):
            if self._xfiles.GetOther(i) == page:
                o = self._xfiles.GetObject(i)
                o.Save()

    # ------------------------------------------------------------------------

    def SaveAs(self):
        """
        Save the current file(s).
        """
        page = self._notebook.GetCurrentPage()
        for i in range(self._xfiles.GetSize()):
            if self._xfiles.GetOther(i) == page:
                o = self._xfiles.GetObject(i)
                o.SaveAs()

    # ------------------------------------------------------------------------

    def SaveAll(self):
        """
        Save all files (one per page).
        """
        for i in range(self._xfiles.GetSize()):
            o = self._xfiles.GetObject(i)
            o.Save()

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# The Component is the content of one page of the notebook.
# ----------------------------------------------------------------------------

class DataRoamer( scrolled.ScrolledPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: This component allows to manage annotated files.

    """

    def __init__(self, parent, prefsIO):

        scrolled.ScrolledPanel.__init__(self, parent, -1)
        sizer = wx.BoxSizer( wx.VERTICAL )

        # members
        self._filetrs    = xFiles()
        self._clipboard  = None # Used to cut and paste
        self._selection  = None # the index of the selected trsdata panel

        self._prefsIO = self._check_prefs(prefsIO)
        self.SetBackgroundColour(prefsIO.GetValue('M_BG_COLOUR'))

        # imitate the behavior of a toolbar, with buttons
        toolbar = self._create_toolbar()
        sizer.Add(toolbar, proportion=0, flag=wx.ALL|wx.EXPAND, border=1 )

        # sizer
        self._trssizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add(self._trssizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=1 )

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

        toolbar = MainToolbarPanel(self, self._prefsIO)
        toolbar.AddButton( RENAME_ID,    TIER_RENAME,   'Rename', tooltip="Rename the selected tier.")
        toolbar.AddButton( wx.ID_DELETE, TIER_DELETE,   'Delete', tooltip="Delete the selected tier.")
        toolbar.AddButton( wx.ID_CUT,    TIER_CUT,      'Cut',    tooltip="Cut the selected tier.")
        toolbar.AddButton( wx.ID_COPY,   TIER_COPY,     "Copy",   tooltip="Copy the selected tier.")
        toolbar.AddButton( wx.ID_PASTE,  TIER_PASTE,    "Paste",  tooltip="Paste the selected tier.")
        toolbar.AddButton( DUPLICATE_ID, TIER_DUPLICATE,"Duplicate", tooltip="Duplicate the selected tier.")
        toolbar.AddButton( wx.ID_UP,     TIER_MOVE_UP,  "Move Up",   tooltip="Move up the selected tier.")
        toolbar.AddButton( wx.ID_DOWN,   TIER_MOVE_DOWN,"Move Down", tooltip="Move down the selected tier.")

        toolbar.AddButton( TIER_RADIUS_ID, TIER_RADIUS, "Radius", tooltip="Fix the vagueness of each boundary. Efficient only while saving file in .xra format.")
        toolbar.AddButton( PREVIEW_ID,     TIER_PREVIEW, "View",   tooltip="Preview of the selected tier.")

        return toolbar

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
        ide = event.GetId()

        if ide == RENAME_ID:
            self.OnRename(event)
            return True
        elif ide == wx.ID_DELETE:
            self.OnDelete(event)
            return True
        elif ide == wx.ID_CUT:
            self.OnCut(event)
            return True
        elif ide == wx.ID_COPY:
            self.OnCopy(event)
            return True
        elif ide == wx.ID_PASTE:
            self.OnPaste(event)
            return True
        elif ide == DUPLICATE_ID:
            self.OnDuplicate(event)
            return True
        elif ide == wx.ID_UP:
            self.OnMoveUp(event)
            return True
        elif ide == wx.ID_DOWN:
            self.OnMoveDown(event)
            return True
        elif ide == PREVIEW_ID:
            self.OnPreview(event)
            return True
        elif ide == TIER_RADIUS_ID:
            self.OnRadius(event)
            return True
        return wx.GetApp().ProcessEvent(event)

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
                self.UnsetData( f )
                evt = FileWanderEvent(filename=f, status=False)
                evt.SetEventObject(self)
                wx.PostEvent( self.GetParent().GetParent().GetParent(), evt )

    # ------------------------------------------------------------------------

    def OnPanelSelection(self, event):
        """ Change the current selection (the transcription file that was clicked on). """
        sel = event.panel

        # unselect current selection (even if tier is empty)
        #if self._filetrs.GetSize() == 0:
        #    p.Deselect()
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p != sel:
                p.Deselect()
                p.SetBackgroundColour( self._prefsIO.GetValue('M_BG_COLOUR'))
            else:
                # set the new selection
                self._selection = p
                p.SetBackgroundColour(wx.Colour(215,215,240))

    # -----------------------------------------------------------------------

    def OnRename(self, event):
        """ Rename a tier. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Rename()

    def OnDelete(self, event):
        """ Delete a tier. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Delete()

    def OnCut(self, event):
        """ Cut a tier. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                self._clipboard = p.Cut()

    def OnCopy(self, event):
        """ Copy a tier. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                self._clipboard = p.Copy()

    def OnPaste(self, event):
        """ Paste a tier. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Paste(self._clipboard)

    def OnDuplicate(self, event):
        """ Duplicate a tier. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Duplicate()

    def OnMoveUp(self, event):
        """ Move up a tier. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.MoveUp()

    def OnMoveDown(self, event):
        """ Move down a tier. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.MoveDown()

    def OnPreview(self, event):
        """ Open a frame to view a tier. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Preview()

    def OnRadius(self, event):
        """ Change radius value of all TimePoint instances of the tier. """
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Radius()

    # ----------------------------------------------------------------------
    # Functions...
    # ----------------------------------------------------------------------

    def Save(self):
        """ Save the selected file. """

        if self._selection is None:
            ShowInformation( self, self._prefsIO, "No file selected!\nClick on a tier to select a file...", style=wx.ICON_INFORMATION)
            return

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Save()

    # ----------------------------------------------------------------------

    def SaveAs(self):
        """ Save as... the selected file. """

        if self._selection is None:
            ShowInformation( self, self._prefsIO, "No file selected!\nClick on a tier to select a file...", style=wx.ICON_INFORMATION)
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
                self.__display_text_in_statusbar('File not saved.')
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

    def SaveAll(self):
        """ Save all files. """

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.Save()

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

    # ----------------------------------------------------------------------

    def SetFont(self, font):
        """ Change font of all texts. """

        wx.Window.SetFont( self,font )
        # Apply to all panels
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetFont( font )

    # ----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """ Change background of all texts. """

        wx.Window.SetBackgroundColour( self,color )
        # Apply as background on all panels
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetBackgroundColour(color)

    # ----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """ Change foreground of all texts. """

        wx.Window.SetForegroundColour( self,color )
        # Apply as foreground on all panels
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetForegroundColour(color)

    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Manage the data
    # ----------------------------------------------------------------------

    def SetData(self, filename):
        """ Add a file. """

        # Do not add an already loaded file
        if self._filetrs.Exists( filename ):
            return False

        # Add the file...
        logging.debug('Add file in data roamer: '+filename)
        # create the object
        newtrs = TrsList(self, filename)
        newtrs.SetPreferences( self._prefsIO )
        if newtrs.GetTranscription().GetName() == "IO-Error":
            ShowInformation( self, self._prefsIO, 'Error loading: '+filename, style=wx.ICON_ERROR)

        # put the new trs in a sizer (required to enable sizer.Remove())
        s = wx.BoxSizer( wx.HORIZONTAL )
        s.Add(newtrs, 1, wx.EXPAND)
        self._trssizer.Add(s, proportion=1, flag=wx.EXPAND|wx.TOP, border=4 )
        # add in the list of files
        self._filetrs.Append(filename,newtrs)

        #self.Layout()
        #self.Refresh()
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
        """ Clean information and destroy all data. """

        self._filetrs.RemoveAll()
        self._trssizer.DeleteWindows()

        self.Layout()

    # ----------------------------------------------------------------------

    def GetSelection(self):
        """ Return the current selection (the panel TrsList witch is selected). """

        return self._selection

    # -----------------------------------------------------------------------

# ----------------------------------------------------------------------------
